"""IFC sınıfı kuralları: her varlık EK-5'teki zorunlu ya da isteğe bağlı listeden bir
sınıfta olmalı (m.12, EK-9 m.8/17); IfcProxy ve IfcBuildingElementProxy yasak
(EK-6 6.1.3); üst sınıf yerine alt sınıf kullanılmalı (EK-6 6.1.2); Ön Tanımlı Tip
doğru ve boş değil (EK-9 m.19)."""

from __future__ import annotations

from ifcopenshell import ifcopenshell_wrapper as w

from ifc_ruhsat import veri
from ifc_ruhsat.bulgu import Bulgu, varlik_listesi
from ifc_ruhsat.kurallar.ortak import Baglam, oznitelik

YASAK = ("IfcProxy", "IfcBuildingElementProxy")
# Yönetmeliğin listesinde olmayan ama modelde bulunması olağan, kontrol dışı sınıflar:
# mekânsal iskelet EK-9 m.11'de ayrıca denetlenir.
KONTROL_DISI = ("IfcProject",)


def kontrol(b: Baglam) -> list[Bulgu]:
    out: list[Bulgu] = []
    zorunlu = veri.zorunlu_siniflar()
    istege = veri.istege_bagli_siniflar()
    yasak, disarida = [], {}
    for e in b.varliklar:
        ad = e.is_a()
        if ad in YASAK:
            yasak.append(e)
        elif ad not in zorunlu and ad not in istege and ad not in KONTROL_DISI:
            disarida.setdefault(ad, []).append(e)
    if yasak:
        out.append(
            Bulgu(
                "sinif-proxy",
                "hata",
                f"{len(yasak)} varlık IfcProxy/IfcBuildingElementProxy ile modellenmiş; yönetmelik "
                "genel/vekil sınıfa izin vermez, her eleman gerçek IFC sınıfıyla temsil edilmeli.",
                "EK-6 6.1.3",
                17,
                varlik_listesi(yasak),
                len(yasak),
            )
        )
    for ad, liste in sorted(disarida.items()):
        altlar = _listedeki_alt_siniflar(ad, {*zorunlu, *istege})
        if altlar:
            # EK-6 6.1.2: alt sınıfı olan üst sınıf kullanılmaz — IfcFlowController yerine IfcValve.
            mesaj = (
                f"{ad} ({len(liste)} varlık) bir üst sınıf; yönetmelik alt sınıfı ister. "
                f"Uygun alt sınıflar: {', '.join(altlar[:6])}{'…' if len(altlar) > 6 else ''}."
            )
            madde = "EK-6 6.1.2, EK-5"
        else:
            mesaj = (
                f"{ad} ({len(liste)} varlık) EK-5'teki zorunlu ya da isteğe bağlı sınıf listesinde yok. "
                "Listedeki bir sınıfa dönüştürün ya da ilgili idareyle teyit edin."
            )
            madde = "m.12, EK-5 Tablo 5.1–5.2"
        out.append(
            Bulgu("sinif-liste-disi", "uyari", mesaj, madde, 8, varlik_listesi(liste), len(liste))
        )
    if not yasak and not disarida:
        out.append(
            Bulgu(
                "sinif",
                "bilgi",
                f"{len(b.varliklar)} varlığın tümü EK-5 listelerindeki sınıflarda "
                f"({len(b.sinif_sayilari)} farklı sınıf).",
                "m.12, EK-5",
                8,
            )
        )
    out += _on_tanimli_tip(b)
    out.append(
        Bulgu(
            "sinif-anlam",
            "elle",
            "Sınıfın doğru seçilip seçilmediği (bir döşemenin IfcSlab, duvarın IfcWall olması) "
            "geometriden anlaşılmaz; model görünümünde göz kontrolü gerekir.",
            "EK-9 madde 17",
            17,
        )
    )
    return out


def _listedeki_alt_siniflar(ad: str, listedekiler: set[str]) -> list[str]:
    """Bu sınıfın EK-5 listesinde yer alan (dolaylı) alt sınıfları — öneri için."""
    try:
        decl = w.schema_by_name("IFC4X3_ADD2").declaration_by_name(ad)
    except RuntimeError:
        return []
    sonuc: list[str] = []
    yigin = list(decl.subtypes())
    while yigin:
        alt = yigin.pop()
        if alt.name() in listedekiler:
            sonuc.append(alt.name())
        yigin.extend(alt.subtypes())
    return sorted(set(sonuc))


def _on_tanimli_tip(b: Baglam) -> list[Bulgu]:
    """PredefinedType olan her sınıfta değer atanmış ve NOTDEFINED değil; USERDEFINED ise ObjectType dolu."""
    out = []
    bos, kullanici = [], []
    for e in b.varliklar:
        if not hasattr(e, "PredefinedType") or not e.is_a("IfcElement"):
            continue
        tip = oznitelik(e, "PredefinedType")
        if tip is None or tip == "NOTDEFINED":
            bos.append(e)
        elif tip == "USERDEFINED" and oznitelik(e, "ObjectType") is None:
            kullanici.append(e)
    if bos:
        out.append(
            Bulgu(
                "on-tanimli-tip",
                "uyari",
                f"{len(bos)} elemanda Ön Tanımlı Tip boş ya da NOTDEFINED; tipi seçin "
                "(IfcWall için SOLIDWALL/PARTITIONING…, IfcSlab için FLOOR/ROOF…).",
                "EK-9 madde 19, EK-6",
                19,
                varlik_listesi(bos),
                len(bos),
            )
        )
    if kullanici:
        out.append(
            Bulgu(
                "on-tanimli-tip-userdefined",
                "uyari",
                f"{len(kullanici)} elemanda Ön Tanımlı Tip USERDEFINED ama ObjectType boş; "
                "USERDEFINED seçildiğinde tip adı ObjectType'a yazılır.",
                "EK-6 (ObjectType açıklaması)",
                19,
                varlik_listesi(kullanici),
                len(kullanici),
            )
        )
    if not out:
        out.append(
            Bulgu("on-tanimli-tip", "bilgi", "Ön Tanımlı Tipler atanmış.", "EK-9 madde 19", 19)
        )
    return out
