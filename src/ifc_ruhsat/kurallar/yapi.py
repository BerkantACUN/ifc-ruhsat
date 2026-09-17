"""Modelin iskeleti: IFC sürümü ve uzantı (EK-9 m.18), Proje/Saha/Bina/Kat (m.11),
mahal varlığı (m.12), kata bağlılık (m.15), yinelenen varlıklar (m.16),
koordinat sistemi (m.6 — EK-7 Tablo 7.6/7.7)."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from ifc_ruhsat import veri
from ifc_ruhsat.bulgu import Bulgu, varlik_listesi
from ifc_ruhsat.kurallar.ortak import Baglam, kati, oznitelik

IFC_SURUMU = "IFC4X3"


def kontrol(b: Baglam) -> list[Bulgu]:
    out: list[Bulgu] = []
    out += _surum(b)
    out += _iskelet(b)
    out += _kat_bagi(b)
    out += _yinelenen(b)
    out += _koordinat(b)
    return out


def _surum(b: Baglam) -> list[Bulgu]:
    out = []
    schema = b.model.schema
    if not schema.upper().startswith(IFC_SURUMU):
        out.append(
            Bulgu(
                "surum",
                "hata",
                f"Model şeması {schema}; yönetmelik IFC 4.3 ister (EK-5 5.4, EK-6 6.1.1). "
                "Yazılımınızın IFC 4.3 dışa aktarımını kullanın.",
                "m.4(5), EK-5 5.4",
                18,
            )
        )
    else:
        out.append(Bulgu("surum", "bilgi", f"Şema {schema} — IFC 4.3.", "m.4(5), EK-5 5.4", 18))
    if Path(b.dosya_adi).suffix.lower() != ".ifc":
        out.append(
            Bulgu(
                "uzanti",
                "hata",
                f"Dosya uzantısı '{Path(b.dosya_adi).suffix}'; teslim dosyası .ifc olmalı.",
                "m.4(5)",
                18,
            )
        )
    return out


def _iskelet(b: Baglam) -> list[Bulgu]:
    out = []
    eksik = [
        ad
        for ad, sinif in (
            ("Proje", "IfcProject"),
            ("Saha", "IfcSite"),
            ("Bina", "IfcBuilding"),
            ("Bina Katı", "IfcBuildingStorey"),
        )
        if not b.sinif(sinif)
    ]
    if eksik:
        out.append(
            Bulgu(
                "iskelet",
                "hata",
                f"Modelde bulunması zorunlu mekânsal yapı eksik: {', '.join(eksik)}.",
                "EK-9 madde 11",
                11,
            )
        )
    else:
        out.append(
            Bulgu(
                "iskelet",
                "bilgi",
                f"Proje, Saha, Bina ve {len(b.sinif('IfcBuildingStorey'))} kat mevcut.",
                "EK-9 madde 11",
                11,
            )
        )
    projeler = b.sinif("IfcProject")
    if len(projeler) > 1:
        out.append(
            Bulgu(
                "iskelet",
                "hata",
                f"Modelde {len(projeler)} IfcProject var; tek olmalı.",
                "EK-7 7.2",
                11,
            )
        )
    if b.disiplin == "MM":
        mahaller = b.sinif("IfcSpace")
        if mahaller:
            out.append(
                Bulgu(
                    "mahal-var",
                    "bilgi",
                    f"{len(mahaller)} mahal (IfcSpace) tanımlı.",
                    "EK-9 madde 12",
                    12,
                )
            )
        else:
            out.append(
                Bulgu(
                    "mahal-var",
                    "hata",
                    "Mimari modelde hiç mahal (IfcSpace) yok; emsal ve mahal kontrolleri yapılamaz.",
                    "EK-9 madde 12",
                    12,
                )
            )
    return out


def _kat_bagi(b: Baglam) -> list[Bulgu]:
    """Her yapı elemanı bir kata (ya da katın içindeki bir mekâna) bağlı olmalı."""
    bagsiz = [
        e
        for e in b.varliklar
        if e.is_a("IfcElement")
        and not e.is_a("IfcOpeningElement")
        and not e.is_a("IfcFeatureElement")
        and kati(e) is None
    ]
    if bagsiz:
        return [
            Bulgu(
                "kat-bagi",
                "hata",
                f"{len(bagsiz)} yapı elemanı hiçbir bina katına bağlı değil "
                "(IfcRelContainedInSpatialStructure). Her eleman bir kata atanmalı.",
                "EK-9 madde 15",
                15,
                varlik_listesi(bagsiz),
                len(bagsiz),
            )
        ]
    return [
        Bulgu("kat-bagi", "bilgi", "Her yapı elemanı bir kata bağlı.", "EK-9 madde 15", 15),
        Bulgu(
            "kat-kotu",
            "elle",
            "Elemanların doğru kotta olup olmadığı (kat yüksekliğiyle uyum) bu sürümde "
            "geometrik olarak denetlenmiyor; yazılımda kat görünümlerinden kontrol edin.",
            "EK-9 madde 15",
            15,
        ),
    ]


def _yinelenen(b: Baglam) -> list[Bulgu]:
    """Aynı GlobalId iki kez; ya da aynı sınıf + isim + yerleşim (aynı yere iki kez konmuş eleman)."""
    out = []
    guid_sayisi = Counter(e.GlobalId for e in b.varliklar)
    tekrar = [g for g, n in guid_sayisi.items() if n > 1]
    if tekrar:
        out.append(
            Bulgu(
                "yinelenen-guid",
                "hata",
                f"{len(tekrar)} GlobalId birden fazla varlıkta kullanılmış; GlobalId tekil olmalı.",
                "EK-9 madde 16",
                16,
                tuple(tekrar[:20]),
                len(tekrar),
            )
        )
    imza: dict[tuple, list] = {}
    for e in b.varliklar:
        if not e.is_a("IfcElement"):
            continue
        yer = getattr(e, "ObjectPlacement", None)
        rel = getattr(yer, "RelativePlacement", None) if yer else None
        konum = getattr(getattr(rel, "Location", None), "Coordinates", None) if rel else None
        if konum is None:
            continue
        imza.setdefault((e.is_a(), e.Name, tuple(round(c, 3) for c in konum)), []).append(e)
    kopyalar = [grup for grup in imza.values() if len(grup) > 1]
    if kopyalar:
        duz = [e for grup in kopyalar for e in grup]
        out.append(
            Bulgu(
                "yinelenen-eleman",
                "uyari",
                f"{len(kopyalar)} yerde aynı sınıf, isim ve yerleşimle birden fazla eleman var; "
                "üst üste kopyalanmış olabilir.",
                "EK-9 madde 16",
                16,
                varlik_listesi(duz),
                len(duz),
            )
        )
    if not out:
        out.append(
            Bulgu(
                "yinelenen",
                "bilgi",
                "Yinelenen GlobalId ya da üst üste eleman yok.",
                "EK-9 madde 16",
                16,
            )
        )
    return out


def _koordinat(b: Baglam) -> list[Bulgu]:
    """IfcProjectedCRS + IfcMapConversion; EPSG kodu TUREF dilimlerinden biri (EK-7 Tablo 7.6)."""
    out = []
    crs = b.sinif("IfcProjectedCRS")
    donusum = b.sinif("IfcMapConversion")
    if not crs or not donusum:
        out.append(
            Bulgu(
                "koordinat",
                "hata",
                "Harita koordinat sistemi tanımlı değil: IfcProjectedCRS ve IfcMapConversion "
                "birlikte bulunmalı (TUREF/ITRF96 TM 3°, EPSG:5253–5259).",
                "m.13, EK-7 Tablo 7.6–7.7",
                6,
            )
        )
        return out
    tablo = veri.ek7_tablolar()["IfcProjectedCRS"]
    izinli = next(g["degerler"] for g in tablo["gerekenler"] if g["ad"] == "Name")
    for c in crs:
        ad = (oznitelik(c, "Name") or "").strip().upper()
        if ad not in izinli:
            out.append(
                Bulgu(
                    "koordinat-epsg",
                    "hata",
                    f"IfcProjectedCRS.Name '{oznitelik(c, 'Name')}'; TUREF 3° dilimlerinden biri olmalı: "
                    f"{', '.join(izinli)}.",
                    "EK-7 Tablo 7.6",
                    6,
                    (f"#{c.id()}",),
                )
            )
        for alan in ("GeodeticDatum", "VerticalDatum", "MapProjection", "MapZone", "MapUnit"):
            if oznitelik(c, alan) is None:
                out.append(
                    Bulgu(
                        "koordinat-alan",
                        "uyari",
                        f"IfcProjectedCRS.{alan} boş (EK-7 Tablo 7.6 zorunlu sayar).",
                        "EK-7 Tablo 7.6",
                        6,
                    )
                )
    for d in donusum:
        for alan in ("Eastings", "Northings", "OrthogonalHeight"):
            if oznitelik(d, alan) is None:
                out.append(
                    Bulgu(
                        "koordinat-alan",
                        "uyari",
                        f"IfcMapConversion.{alan} boş (EK-7 Tablo 7.7 zorunlu sayar).",
                        "EK-7 Tablo 7.7",
                        6,
                    )
                )
    if not out:
        out.append(
            Bulgu(
                "koordinat",
                "bilgi",
                f"Koordinat sistemi {oznitelik(crs[0], 'Name')}; harita dönüşümü tanımlı.",
                "EK-7 Tablo 7.6–7.7",
                6,
            )
        )
    return out
