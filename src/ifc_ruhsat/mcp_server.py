"""MCP sunucusu: Claude, Cursor ve benzeri istemciler için beş araç. Dosya yolları
istemcinin çalıştığı makinedeki yerel yollardır; sunucu hiçbir şeyi ağa göndermez."""

from __future__ import annotations

from typing import Any

from mcp.types import ToolAnnotations

from ifc_ruhsat import SURUM, YONETMELIK, veri

try:  # mcp 2.x
    from mcp.server.mcpserver import MCPServer
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as MCPServer

SALT_OKUR = ToolAnnotations(readOnlyHint=True, openWorldHint=False)

mcp = MCPServer(
    "ifc-ruhsat",
    version=SURUM,
    instructions=(
        "Yapı ruhsatı IFC modellerini Türkiye'nin dijital proje yönetmeliğine "
        f"({YONETMELIK['ad']}, RG {YONETMELIK['resmiGazete']}) göre kontrol eder. "
        "Her bulgu yönetmelik maddesi ve EK-9 satırıyla gelir; 'elle' seviyesi makinece "
        "denetlenemeyen satırdır, uygun sayma. Sonuçları kullanıcıya madde numarasıyla aktar, "
        "hukuki değerlendirme yapma."
    ),
)


@mcp.tool(annotations=SALT_OKUR)
def model_ozeti(dosya: str) -> dict[str, Any]:
    """IFC dosyasının kimliği: şema (IFC4X3 olmalı), üreten yazılım, proje/saha/bina/kat adları,
    mahal sayısı ve sınıf başına varlık sayıları. Summary of an IFC file: schema, authoring
    software, spatial structure and entity counts by class."""
    from ifc_ruhsat.kontrol import ozet

    return ozet(dosya)


@mcp.tool(annotations=SALT_OKUR)
def yonetmelik_kontrolu(dosya: str, disiplin: str = "MM") -> dict[str, Any]:
    """Modeli yönetmeliğe göre denetler: IFC sürümü, Proje/Saha/Bina/Kat iskeleti, EK-5 sınıf
    listesi ve yasak vekil sınıflar, EK-5 isimlendirme (Disiplin-Kategori-Açıklama), EK-6/EK-7
    zorunlu öznitelik ve özellik setleri (TREpys_ dahil), koordinat sistemi (TUREF EPSG:5253–5259),
    kat bağı, yinelenen varlıklar, emsal toplamları. Her bulgu: seviye (hata/uyari/elle/bilgi),
    madde, EK-9 satırı, GlobalId listesi. Checks an IFC model against the Turkish building-permit
    BIM regulation and returns findings with article references. `disiplin`: EK-2 kodu (MM mimari)."""
    from ifc_ruhsat.kontrol import kontrol_et

    return kontrol_et(dosya, disiplin).sozluk()


@mcp.tool(annotations=SALT_OKUR)
def ek9_formu(dosya: str, disiplin: str = "MM") -> str:
    """EK-9 Model Kalite Kontrol Formu'nu (Tablo 9.1, 21 satır) Markdown olarak üretir; her satır
    Evet / Hayır / Elle ve dayanağıyla. Renders the regulation's model quality-control form
    (Annex 9) for the model as Markdown."""
    from ifc_ruhsat import ek9
    from ifc_ruhsat.kontrol import kontrol_et

    return ek9.markdown(kontrol_et(dosya, disiplin))


@mcp.tool(annotations=SALT_OKUR)
def ek5_siniflar(ara: str | None = None) -> dict[str, Any]:
    """EK-5'teki zorunlu (Tablo 5.1) ve isteğe bağlı (Tablo 5.2) IFC sınıfları, Türkçe adı ve üç
    harfli kategori koduyla; `ara` ile sınıf/Türkçe ad filtresi. Lists the regulation's mandatory
    and optional IFC classes with their Turkish names and 3-letter category codes."""
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


@mcp.tool(annotations=SALT_OKUR)
def ek6_gerekenler(ifc_sinifi: str) -> dict[str, Any]:
    """Bir IFC sınıfı için yönetmeliğin istediği zorunlu öznitelikler, özellik setleri
    (Pset_/Qto_/TREpys_) ve Ön Tanımlı Tip listesi — EK-6 (yapı elemanları) ya da EK-7 (proje,
    kişi, kuruluş, koordinat). Kodlanmamış bir sınıf için bunu açıkça söyler. Required attributes
    and property sets for one IFC class per Annex 6/7."""
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


@mcp.tool(annotations=SALT_OKUR)
def yonetmelik_bilgisi() -> dict[str, Any]:
    """Aracın dayandığı yönetmelik, Resmî Gazete tarihi/sayısı, yürürlük ve kademeli IFC takvimi,
    veri dosyalarının kaynak satırları ve araç sürümü. Which regulation this tool encodes, with
    the phased deadlines."""
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


def calistir() -> None:
    mcp.run()


if __name__ == "__main__":
    calistir()
