"""Elemanların kotu (EK-9 m.15): her yapı elemanının yerleşim noktası, bağlı olduğu katın
kotu ile bir üstteki katın kotu arasında olmalı. Temel ve subasman için kat kotunun
altına, çatı ve parapet için üst katın üstüne tolerans tanınır.

Gövde geometrisi değil, IfcObjectPlacement'ın dünya koordinatındaki kotu kullanılır:
saniyeler değil milisaniyeler sürer ve "yanlış kata atanmış eleman" için yeterli bir
göstergedir. Kat kotları IfcBuildingStorey.Elevation'dan, proje birimi metreye
çevrilerek okunur."""

from __future__ import annotations

from typing import Any

import ifcopenshell.util.placement as up
import ifcopenshell.util.unit as uu

from ifc_ruhsat.bulgu import Bulgu, varlik_listesi
from ifc_ruhsat.kurallar.ortak import Baglam, kati

ALT_TOLERANS_M = 1.5  # temel, subasman, düşük döşeme
UST_TOLERANS_M = 1.5  # çatı, parapet, saçak


def yerlesim_kotu(e: Any, olcek: float) -> float | None:
    """Elemanın yerleşim orijininin dünya kotu (metre); yerleşimi yoksa None."""
    yer = getattr(e, "ObjectPlacement", None)
    if yer is None:
        return None
    try:
        return float(up.get_local_placement(yer)[2][3]) * olcek
    except Exception:  # noqa: BLE001 — bozuk yerleşim kuralı düşürmesin
        return None


def kontrol(b: Baglam) -> list[Bulgu]:
    elemanlar = [
        e
        for e in b.varliklar
        if e.is_a("IfcElement") and not e.is_a("IfcFeatureElement") and kati(e) is not None
    ]
    if not elemanlar:
        return []
    olcek = uu.calculate_unit_scale(b.model)  # proje birimi → metre
    katlar = sorted(
        (float(k.Elevation or 0.0) * olcek, k) for k in b.model.by_type("IfcBuildingStorey")
    )
    kot = {k.id(): z for z, k in katlar}
    ust_kot: dict[int, float | None] = {
        k.id(): (katlar[i + 1][0] if i + 1 < len(katlar) else None)
        for i, (_, k) in enumerate(katlar)
    }
    yanlis: list[Any] = []
    for e in elemanlar:
        k = kati(e)
        z = yerlesim_kotu(e, olcek)
        if z is None or k is None or k.id() not in kot:
            continue
        alt, ust = kot[k.id()], ust_kot[k.id()]
        if z < alt - ALT_TOLERANS_M or (ust is not None and z > ust + UST_TOLERANS_M):
            yanlis.append(e)
    if yanlis:
        return [
            Bulgu(
                "kat-kotu",
                "uyari",
                f"{len(yanlis)} elemanın yerleşim kotu bağlı olduğu katın aralığının dışında (kat "
                f"kotunun {ALT_TOLERANS_M:g} m altı ile üst katın {UST_TOLERANS_M:g} m üstü dışında); "
                "yanlış kata atanmış ya da yanlış kota çizilmiş olabilir. Revit'te kat olmayan "
                "seviyeler (tavan, çatı çizgisi) IfcBuildingStorey olarak dışa aktarılmışsa yanlış "
                "alarm verir; o seviyelerde 'Building Story' işaretini kaldırın.",
                "EK-9 madde 15",
                15,
                varlik_listesi(yanlis),
                len(yanlis),
            )
        ]
    return [
        Bulgu(
            "kat-kotu",
            "bilgi",
            "Elemanların yerleşim kotları bağlı oldukları katın aralığında.",
            "EK-9 madde 15",
            15,
        )
    ]
