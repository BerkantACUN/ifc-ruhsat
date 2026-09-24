"""MCP sunucusu: Claude, Cursor ve benzeri istemciler için altı salt-okur araç.

stdio modunda `dosya` istemcinin makinesindeki yerel yoldur. Uzak (streamable HTTP) modda
sunucu istemcinin diskini göremez; model `ifc_metni` ile IFC (STEP) metni olarak gönderilir.
Sunucu hiçbir şeyi ağa göndermez, kalıcı bir şey yazmaz."""

from __future__ import annotations

import hmac
import json
import os
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated, Any

from mcp.types import ToolAnnotations
from pydantic import Field

from ifc_ruhsat import SURUM, YONETMELIK, veri

try:  # mcp 2.x
    from mcp.server.mcpserver import MCPServer
    from mcp.server.mcpserver.exceptions import ToolError
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as MCPServer
    from mcp.server.fastmcp.exceptions import ToolError

UZAK_DOSYA_MESAJI = "Uzak modda dosya yolu kapalı, ifc_metni kullanın"
_UZAK_MOD = False  # http_uygulamasi() kurulduğunda True: sunucu kendi diskinden okumaz


class UzakDosyaHatasi(ToolError):
    """Uzak (HTTP) modda yol parametresi verildi; istemciye isError olarak döner."""


def _salt_okur(baslik: str) -> ToolAnnotations:
    """Bütün araçlar yalnız okur, aynı girdiye aynı sonucu verir, dış dünyaya çıkmaz."""
    return ToolAnnotations(
        title=baslik,
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )


mcp = MCPServer(
    "ifc-ruhsat",
    version=SURUM,
    instructions=(
        "Yapı ruhsatı IFC modellerini Türkiye'nin dijital proje yönetmeliğine "
        f"({YONETMELIK['ad']}, RG {YONETMELIK['resmiGazete']}) göre kontrol eder. "
        "Model için önce `model_ozeti` (hızlı kimlik), sonra `yonetmelik_kontrolu` (bulgular) ya da "
        "`ek9_formu` (resmî form) çağır. Model yoksa `ek5_siniflar`, `ek6_gerekenler` ve "
        "`yonetmelik_bilgisi` yönetmeliğin kendisini anlatır. Yerel sunucuda `dosya` yol alır; "
        "uzak sunucuda `dosya` kapalıdır (uzak-dosya-kapali hatası), modeli `ifc_metni` ile gönder. Her bulgu yönetmelik maddesi ve EK-9 "
        "satırıyla gelir; 'elle' seviyesi makinece denetlenemeyen satırdır, uygun sayma. "
        "Sonuçları kullanıcıya madde numarasıyla aktar, hukuki değerlendirme yapma."
    ),
)

Dosya = Annotated[
    str | None,
    Field(
        description=(
            "Yerel (stdio) sunucuda .ifc dosyasının yolu (istemcinin diskindeki yol). Uzak "
            "(HTTP) sunucuda kapalıdır: verilirse `uzak-dosya-kapali` hatası döner, `ifc_metni` "
            "kullanın. Yerelde `ifc_metni` verilirse yok sayılır."
        ),
        examples=["C:/proje/123456_00_MM_GNEL_MD_BIM_000_01_000.ifc", "/home/ali/A_blok.ifc"],
    ),
]
IfcMetni = Annotated[
    str | None,
    Field(
        description=(
            "IFC dosyasının tam metni (ISO-10303-21 / STEP, 'ISO-10303-21;' ile başlar). Uzak "
            "sunucuda dosya yolu yerine bunu gönderin."
        ),
        examples=["ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('ViewDefinition [...]'),'2;1');\n..."],
    ),
]
DosyaAdi = Annotated[
    str | None,
    Field(
        description=(
            "`ifc_metni` ile gönderilen modelin özgün dosya adı. EK-2 dosya adı kontrolü ve "
            "disiplinin dosya adından okunması için kullanılır; verilmezse 'model.ifc'."
        ),
        examples=["123456_00_MM_GNEL_MD_BIM_000_01_000.ifc"],
    ),
]
Disiplin = Annotated[
    str | None,
    Field(
        description=(
            "EK-2 disiplin kodu: MM mimari, ST statik, MK mekanik, EE elektrik… Verilmezse EK-2 "
            "biçimindeki dosya adının üçüncü alanından, o da yoksa MM."
        ),
        examples=["MM", "ST", "MK", "EE"],
    ),
]


@contextmanager
def _model_yolu(
    dosya: str | None, ifc_metni: str | None, dosya_adi: str | None
) -> Iterator[tuple[Path, str]]:
    """(okunacak yol, raporda görünecek ad). Metin geldiyse geçici klasöre özgün adıyla yazar.
    Uzak modda `dosya` hiç kabul edilmez (ifc_metni ile birlikte verilse de): uzaktaki bir
    çağıran kapsayıcıdaki herhangi bir dosyayı okutamasın."""
    if dosya and _UZAK_MOD:
        raise UzakDosyaHatasi(f"uzak-dosya-kapali: {UZAK_DOSYA_MESAJI}")
    if ifc_metni:
        ad = Path(dosya_adi or "model.ifc").name or "model.ifc"
        with tempfile.TemporaryDirectory(prefix="ifc-ruhsat-") as klasor:
            yol = Path(klasor) / ad
            yol.write_text(ifc_metni, encoding="utf-8", newline="")
            yield yol, ad
        return
    if not dosya:
        raise ValueError("`dosya` (yol) ya da `ifc_metni` (IFC metni) verilmeli")
    yield Path(dosya), dosya


@mcp.tool(title="IFC model özeti", annotations=_salt_okur("IFC model özeti"))
def model_ozeti(
    dosya: Dosya = None, ifc_metni: IfcMetni = None, dosya_adi: DosyaAdi = None
) -> dict[str, Any]:
    """Bir IFC modelinin kimliğini hızlıca çıkarır; kural denetimi yapmaz.

    Ne zaman: kullanıcı bir model verdiğinde ilk adım olarak ("bu dosyada ne var?", "hangi IFC
    sürümü?", "kaç kat var?") ya da uzun `yonetmelik_kontrolu` öncesinde doğru dosya olduğunu
    teyit etmek için. Yönetmeliğe uygunluk soruluyorsa `yonetmelik_kontrolu` kullanın.

    Girdi: `dosya` (yol) ya da `ifc_metni` (+ isteğe bağlı `dosya_adi`). Örnek:
    `{"dosya": "C:/proje/A_blok.ifc"}`.

    Dönüş (JSON nesne): `dosya`, `boyutMB`, `schema` (yönetmelik IFC4X3 ister), `yazilim`
    (üreten program ve sürümü), `proje`, `saha[]`, `bina[]`, `katlar[]` (kat adları),
    `mahalSayisi`, `varlikSayisi` ve `sinifSayilari` (IFC sınıfı → varlık sayısı).

    Uzak (HTTP) sunucuda `dosya` kapalıdır: verilirse araç `uzak-dosya-kapali` hatası (isError)
    döner; modeli `ifc_metni` ile gönderin.

    English: identity of an IFC file — schema, authoring software, project/site/building/storey
    names and entity counts per class. Read-only, no rule checks.
    """
    from ifc_ruhsat.kontrol import ozet

    with _model_yolu(dosya, ifc_metni, dosya_adi) as (yol, ad):
        return {**ozet(yol), "dosya": ad}


@mcp.tool(title="Yönetmelik kontrolü", annotations=_salt_okur("Yönetmelik kontrolü"))
def yonetmelik_kontrolu(
    dosya: Dosya = None,
    ifc_metni: IfcMetni = None,
    dosya_adi: DosyaAdi = None,
    disiplin: Disiplin = None,
) -> dict[str, Any]:
    """IFC modelini Türkiye dijital proje yönetmeliğine (RG 5.8.2026, 33331) göre denetler ve
    madde numaralı bulgu listesi döndürür.

    Ne zaman: "model yönetmeliğe uyuyor mu?", "ruhsata hazır mı?", "hangi elemanlarda eksik
    var?", "duvarlarda neden hata var?" gibi sorularda. Resmî EK-9 formu isteniyorsa
    `ek9_formu`; tek bir sınıfın gereksinimi soruluyorsa `ek6_gerekenler` daha uygundur.

    Denetlenenler: IFC sürümü (IFC4X3), Proje/Saha/Bina/Kat iskeleti, EK-5 sınıf listesi ve
    yasak vekil sınıflar (IfcBuildingElementProxy), EK-5 isimlendirme (Disiplin-Kategori-Açıklama),
    EK-6/EK-7 zorunlu öznitelik ve özellik setleri (TREpys_ dahil), koordinat sistemi (TUREF
    EPSG:5253–5259), mahal numarası ve geometrisi, kata bağlılık ve kot, yinelenen varlıklar,
    emsal toplamları.

    Girdi örnekleri: `{"dosya": "C:/proje/123456_00_MM_GNEL_MD_BIM_000_01_000.ifc"}`,
    `{"dosya": "statik.ifc", "disiplin": "ST"}`,
    `{"ifc_metni": "ISO-10303-21;...", "dosya_adi": "A_blok.ifc"}`.

    Dönüş (JSON nesne): `dosya`, `schema`, `ozet` ({hata, uyari, elle, bilgi} sayıları) ve
    `bulgular[]`; her bulgu `kod`, `seviye` (hata = yönetmeliğe aykırı, uyari = muhtemel sorun,
    elle = makinece denetlenemez, uygun sayılmaz; bilgi), `mesaj` (Türkçe), `madde` (ör.
    "EK-6 Tablo 6.66"), `ek9` (EK-9 satır no), `varliklar` (GlobalId listesi, kısaltılmış) ve
    `sayi` (etkilenen varlık sayısı). Büyük modellerde birkaç saniye sürebilir.

    Uzak (HTTP) sunucuda `dosya` kapalıdır: verilirse araç `uzak-dosya-kapali` hatası (isError)
    döner; modeli `ifc_metni` ile gönderin.

    English: checks an IFC model against the Turkish building-permit BIM regulation; returns
    findings with severity, article reference, Annex 9 row and affected GlobalIds.
    """
    from ifc_ruhsat.kontrol import kontrol_et

    with _model_yolu(dosya, ifc_metni, dosya_adi) as (yol, ad):
        rapor = kontrol_et(yol, disiplin)
        rapor.dosya = ad
        return rapor.sozluk()


@mcp.tool(title="EK-9 kalite kontrol formu", annotations=_salt_okur("EK-9 kalite kontrol formu"))
def ek9_formu(
    dosya: Dosya = None,
    ifc_metni: IfcMetni = None,
    dosya_adi: DosyaAdi = None,
    disiplin: Disiplin = None,
) -> str:
    """Yönetmeliğin EK-9 Model Kalite Kontrol Formu'nu (Tablo 9.1, 21 satır) modele göre doldurur.

    Ne zaman: kullanıcı teslim için formun kendisini istediğinde ("EK-9 formunu çıkar", "kalite
    kontrol formunu doldur"). Bulguları ayrıntılı incelemek, GlobalId almak ya da programatik
    işlemek için `yonetmelik_kontrolu` kullanın; bu araç aynı denetimi çalıştırıp özetler.

    Girdi örnekleri: `{"dosya": "C:/proje/A_blok.ifc"}`,
    `{"dosya": "A_blok.ifc", "disiplin": "MM"}`, `{"ifc_metni": "ISO-10303-21;..."}`.

    Dönüş (Markdown metin): başlık, model/şema/tarih satırı, 21 satırlık tablo (her satır
    Evet / Hayır / Kısmen / Elle ve dayanağı olan madde) ve veri kaynakları. Olduğu gibi
    kullanıcıya gösterilebilir ya da .md dosyasına yazılabilir.

    Uzak (HTTP) sunucuda `dosya` kapalıdır: verilirse araç `uzak-dosya-kapali` hatası (isError)
    döner; modeli `ifc_metni` ile gönderin.

    English: renders the regulation's Annex 9 model quality-control form for the model as
    Markdown (21 rows, Yes / No / Partial / Manual with the legal basis).
    """
    from ifc_ruhsat import ek9
    from ifc_ruhsat.kontrol import kontrol_et

    with _model_yolu(dosya, ifc_metni, dosya_adi) as (yol, ad):
        rapor = kontrol_et(yol, disiplin)
        rapor.dosya = ad
        return ek9.markdown(rapor)


@mcp.tool(title="EK-5 IFC sınıf listesi", annotations=_salt_okur("EK-5 IFC sınıf listesi"))
def ek5_siniflar(
    ara: Annotated[
        str | None,
        Field(
            description=(
                "IFC sınıf adında ya da Türkçe adda geçen alt dize (büyük/küçük harf duyarsız). "
                "Boş bırakılırsa bütün liste döner."
            ),
            examples=["duvar", "IfcSlab", "merdiven", "pompa"],
        ),
    ] = None,
) -> dict[str, Any]:
    """Yönetmeliğin EK-5 listesindeki IFC sınıflarını Türkçe adları ve üç harfli kategori
    kodlarıyla verir; model gerektirmez.

    Ne zaman: "duvar hangi IFC sınıfıyla modellenir?", "IfcCovering'in kategori kodu ne?",
    "IfcPlate listede var mı?", "varlık adı nasıl olmalı?" gibi sorularda. Bir sınıfın zorunlu
    özellik setleri için `ek6_gerekenler` kullanın.

    Girdi örnekleri: `{}` (tüm liste), `{"ara": "duvar"}`, `{"ara": "IfcDoor"}`.

    Dönüş (JSON nesne): `kaynak` (Resmî Gazete ek sayfası), `isimlendirme` (varlık adı şablonu,
    ör. MM-DVR-dis_20cm), `zorunlu[]` (Tablo 5.1) ve `istegeBagli[]` (Tablo 5.2); her öğe
    `ifc` (sınıf adı), `turkce` (Türkçe adı) ve `kod` (kategori kodu, ör. DVR).

    English: lists the regulation's mandatory and optional IFC classes with Turkish names and
    3-letter category codes, optionally filtered.
    """
    e = veri.ek5()
    a = (ara or "").strip().lower()

    def sec(liste):
        return [s for s in liste if not a or a in s["ifc"].lower() or a in s["turkce"].lower()]

    return {
        "kaynak": e["kaynak"],
        "isimlendirme": e["isimlendirme"],
        "zorunlu": sec(e["zorunlu"]),
        "istegeBagli": sec(e["istege_bagli"]),
    }


@mcp.tool(
    title="EK-6/EK-7 sınıf gereksinimleri", annotations=_salt_okur("EK-6/EK-7 sınıf gereksinimleri")
)
def ek6_gerekenler(
    ifc_sinifi: Annotated[
        str,
        Field(
            description="IFC sınıf adı (büyük/küçük harf duyarsız).",
            examples=["IfcWall", "IfcSlab", "IfcBoiler", "IfcProject", "IfcProjectedCRS"],
        ),
    ],
) -> dict[str, Any]:
    """Tek bir IFC sınıfı için yönetmeliğin istediği zorunlu öznitelikleri, özellik setlerini
    (Pset_/Qto_/TREpys_) ve izinli Ön Tanımlı Tip değerlerini verir; model gerektirmez.

    Ne zaman: "IfcSlab için hangi özellikler zorunlu?", "duvara FireRating gerekiyor mu?",
    "IfcProject'te hangi alanlar dolu olmalı?" gibi sorularda ya da `yonetmelik_kontrolu`
    bulgusunu açıklarken. Yapı elemanları EK-6'dan, proje/kişi/kuruluş/koordinat sınıfları
    EK-7'den gelir.

    Girdi örnekleri: `{"ifc_sinifi": "IfcWall"}`, `{"ifc_sinifi": "ifcboiler"}`,
    `{"ifc_sinifi": "IfcProjectedCRS"}`.

    Dönüş (JSON nesne): kodlanmış sınıfta `ek` ("EK-6" ya da "EK-7"), `ifc`, `tablo` (ör.
    "6.66"), `sayfa` (Resmî Gazete ekindeki sayfa), `gerekenler[]` (her öğe `tur`: oznitelik /
    ozellik / malzeme…, `ad`, `turkce`, `veriTipi`, özelliklerde set adı ve izinli değerler) ve
    varsa `onTanimliTipler[]` (izinli PredefinedType değerleri). EK-5'te zorunlu olup tablosu
    kodlanmamış sınıfta `durum` ve `kategoriKodu`; listede olmayan sınıfta yalnız `ifc` ve
    `durum`.

    English: required attributes, property sets and predefined types for one IFC class per
    Annex 6 (building elements) or Annex 7 (project, actors, coordinates).
    """
    ad = ifc_sinifi.strip()
    for tablolar, ek in ((veri.ek6_tablolar(), "EK-6"), (veri.ek7_tablolar(), "EK-7")):
        for k, t in tablolar.items():
            if k.lower() == ad.lower():
                return {"ek": ek, **t}
    zorunlu = veri.zorunlu_siniflar()
    for k in zorunlu:
        if k.lower() == ad.lower():
            return {
                "ifc": k,
                "durum": "EK-5'te zorunlu sınıf; EK-6 tablosu bu sürümde henüz kodlanmadı "
                "(yalnızca Name denetlenir). Bkz. KAYNAKLAR.md.",
                "kategoriKodu": zorunlu[k]["kod"],
            }
    return {"ifc": ad, "durum": "EK-5 zorunlu listesinde değil."}


@mcp.tool(title="Yönetmelik ve takvim bilgisi", annotations=_salt_okur("Yönetmelik bilgisi"))
def yonetmelik_bilgisi() -> dict[str, Any]:
    """Aracın dayandığı yönetmeliği, yürürlük ve kademeli IFC zorunluluğu takvimini, veri
    dosyalarının kaynaklarını ve araç sürümünü verir; parametre almaz, model gerektirmez.

    Ne zaman: "bu yönetmelik ne zaman yürürlüğe giriyor?", "IFC teslimi benim projem için ne
    zaman zorunlu?", "hangi Resmî Gazete?", "kurallar nereden alındı?" gibi sorularda ya da
    sonuçları aktarırken dayanak göstermek için.

    Girdi örneği: `{}`.

    Dönüş (JSON nesne): `arac` (ör. "ifc-ruhsat 0.2.1"), `ad`, `resmiGazete` (tarih ve sayı),
    `yururluk`, `metin` ve `ekler` (Resmî Gazete bağlantıları), `takvim` (`yururluk`, `ifcZorunlu`: tarih → kapsam, `kaynak`:
    Geçici m.1) ve `veriKaynaklari` (veri dosyası → ekin sayfaları).

    English: which regulation this tool encodes (Official Gazette no. 33331), its entry into
    force and phased IFC deadlines, and the provenance of the encoded data.
    """
    return {
        "arac": f"ifc-ruhsat {SURUM}",
        **YONETMELIK,
        "takvim": {
            "yururluk": "2027-09-01 (m.16)",
            "ifcZorunlu": {
                "2029-09-01": "nüfusu 2 milyonu geçen illerde 600 bin+ belediyeler, >10.000 m²",
                "2030-09-01": "aynı iller, 400 bin+ belediyeler, >10.000 m²",
                "2031-09-01": "nüfusu 1 milyonu geçen iller, 300 bin+ belediyeler, >10.000 m²",
                "2032-09-01": "diğer tüm binalar",
                "2033-09-01": "konut ve konut+ticaret dışı binalar",
            },
            "kaynak": "Geçici m.1",
        },
        "veriKaynaklari": veri.kaynaklar(),
    }


VARSAYILAN_HOST = "0.0.0.0"  # Azure Container Apps'te IPv6 yok; "::" dinlemek başlamayı bozar
VARSAYILAN_PORT = 8080


class _AnahtarKapisi:
    """IFC_RUHSAT_API_KEY verildiğinde her HTTP isteğinde X-API-Key başlığını zorunlu kılar."""

    def __init__(self, uygulama, anahtar: str) -> None:
        self.uygulama = uygulama
        self.anahtar = anahtar.encode("utf-8")

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] == "http":
            verilen = dict(scope.get("headers") or []).get(b"x-api-key", b"")
            if not hmac.compare_digest(verilen, self.anahtar):
                govde = json.dumps(
                    {"hata": "yetkisiz", "mesaj": "Geçerli bir X-API-Key başlığı gerekli"},
                    ensure_ascii=False,
                ).encode("utf-8")
                await send(
                    {
                        "type": "http.response.start",
                        "status": 401,
                        "headers": [
                            (b"content-type", b"application/json; charset=utf-8"),
                            (b"content-length", str(len(govde)).encode()),
                        ],
                    }
                )
                await send({"type": "http.response.body", "body": govde})
                return
        await self.uygulama(scope, receive, send)


def http_uygulamasi(api_anahtari: str | None = None, host: str = VARSAYILAN_HOST):
    """Streamable HTTP ASGI uygulaması (yol: /mcp). Durumsuz: her istek bağımsız, böylece
    birden çok kopya yük dengeleyici arkasında oturum yapışkanlığı olmadan çalışır. Bu süreçte
    `dosya` parametresi kapanır: uzaktaki bir çağıran sunucunun diskindeki dosyaları okuyamasın."""
    global _UZAK_MOD
    _UZAK_MOD = True
    uygulama = mcp.streamable_http_app(stateless_http=True, host=host)
    return _AnahtarKapisi(uygulama, api_anahtari) if api_anahtari else uygulama


def http_calistir(host: str | None = None, port: int | None = None) -> None:
    import uvicorn

    host = host or os.environ.get("IFC_RUHSAT_HOST") or VARSAYILAN_HOST
    port = port or int(os.environ.get("IFC_RUHSAT_PORT") or VARSAYILAN_PORT)
    uygulama = http_uygulamasi(os.environ.get("IFC_RUHSAT_API_KEY") or None, host)
    uvicorn.run(uygulama, host=host, port=port, proxy_headers=True, forwarded_allow_ips="*")


def calistir() -> None:
    mcp.run()


if __name__ == "__main__":
    calistir()
