"""EK-6 ve EK-7'yi buildingSMART IDS (Information Delivery Specification 1.0) olarak
yazar. IDS'i Solibri, BIMcollab Zoom, usBIM.IDS ve ifctester okur — yani bu aracı
kullanmayan bir ofis de yönetmeliği kendi yazılımında denetleyebilir.

IDS'in anlatamadığı kurallar (malzeme adı biçimi, sistem ilişkisi, kaplama seçeneği,
koordinat EPSG listesi dışındaki alanlar) Python kurallarında kalır; IDS dosyası
bunu başlığında söyler."""

from __future__ import annotations

from pathlib import Path

from ifctester import ids

from ifc_ruhsat import SURUM, YONETMELIK, veri

VERI_TIPI = {"M": "IFCLABEL", "S": "IFCREAL", "B": "IFCBOOLEAN"}


def _ozellik(g: dict) -> ids.Property:
    p = ids.Property(
        propertySet=g["set"],
        baseName=g["ad"],
        cardinality="required",
        instructions=g.get("turkce"),
    )
    tip = VERI_TIPI.get(g["veriTipi"])
    if tip:
        p.dataType = tip
    if g.get("degerler"):
        kisit = ids.Restriction(options={"enumeration": g["degerler"]})
        p.value = kisit
    return p


def _oznitelik(g: dict) -> ids.Attribute:
    a = ids.Attribute(name=g["ad"], cardinality="required", instructions=g.get("turkce"))
    if g.get("degerler"):
        a.value = ids.Restriction(options={"enumeration": g["degerler"]})
    return a


def _spec(tablo: dict, ek: str) -> ids.Specification:
    s = ids.Specification(
        name=f"{ek} Tablo {tablo['tablo']} — {tablo['ifc']}",
        ifcVersion=["IFC4X3_ADD2"],
        identifier=f"{ek}-{tablo['tablo']}",
        description=f"RG {YONETMELIK['resmiGazete']} ek s.{tablo.get('sayfa', '?')}",
    )
    s.applicability.append(ids.Entity(name=tablo["ifc"].upper()))
    for g in tablo["gerekenler"]:
        if g["tur"] == "oznitelik":
            s.requirements.append(_oznitelik(g))
        elif g["tur"] == "ozellik":
            s.requirements.append(_ozellik(g))
        elif g["tur"] == "malzeme":
            s.requirements.append(ids.Material(cardinality="required", instructions=g.get("not")))
    return s


def uret(ek: str) -> ids.Ids:
    tablolar = veri.ek6_tablolar() if ek == "EK-6" else veri.ek7_tablolar()
    belge = ids.Ids(
        title=f"{YONETMELIK['ad']} — {ek}",
        description=(
            f"RG {YONETMELIK['resmiGazete']} {ek} tablolarının IDS karşılığı; ifc-ruhsat {SURUM} "
            "tarafından üretildi. Kapsam: kodlanmış tablolar (KAYNAKLAR.md). Malzeme adı biçimi, "
            "IfcSystem ilişkisi, kaplama seçeneği ve koordinat dönüşümü IDS dışında, araçta denetlenir."
        ),
        author="ifc-ruhsat",
        version=SURUM,
        purpose="Yapı ruhsatı teslim öncesi model kontrolü",
        milestone="Ruhsat",
    )
    for t in tablolar.values():
        belge.specifications.append(_spec(t, ek))
    return belge


def yaz(klasor: Path) -> list[Path]:
    klasor.mkdir(parents=True, exist_ok=True)
    yollar = []
    for ek, dosya in (("EK-6", "tr-ruhsat-ek6.ids"), ("EK-7", "tr-ruhsat-ek7.ids")):
        yol = klasor / dosya
        uret(ek).to_xml(str(yol))
        yollar.append(yol)
    return yollar
