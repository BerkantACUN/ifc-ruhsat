"""Elemanların kotu (EK-9 m.15): her yapı elemanının gövdesi, bağlı olduğu katın kotu ile
bir üstteki katın kotu arasında olmalı. Temel ve döşeme için kat kotunun biraz altına,
çatı ve parapet için üst katın biraz üstüne tolerans tanınır. Kaba bir kontroldür: kat
kotları IfcBuildingStorey.Elevation'dan, gövdeler sınır kutusundan okunur."""

from __future__ import annotations

from typing import Any

import ifcopenshell.util.unit as uu

from ifc_ruhsat.bulgu import Bulgu, varlik_listesi
from ifc_ruhsat.kurallar.geometri import ELEMAN_SINIRI, sinir_kutulari
from ifc_ruhsat.kurallar.ortak import Baglam, kati

ALT_TOLERANS_M = 1.5  # temel, subasman, düşük döşeme
UST_TOLERANS_M = 1.5  # çatı, parapet, saçak


def kontrol(b: Baglam) -> list[Bulgu]:
    elemanlar = [
        e
        for e in b.varliklar
        if e.is_a("IfcElement") and not e.is_a("IfcFeatureElement") and kati(e) is not None
    ]
    if not elemanlar:
        return []
    if len(elemanlar) > ELEMAN_SINIRI:
        return [
            Bulgu(
                "kat-kotu",
                "elle",
                f"{len(elemanlar)} eleman var; kot kontrolü {ELEMAN_SINIRI} elemanın üstünde "
                "çalıştırılmıyor, yazılımda kat görünümlerinden bakın.",
                "EK-9 madde 15",
                15,
            )
        ]
    kutular = sinir_kutulari(elemanlar)
    if kutular is None:
        return [
            Bulgu(
                "kat-kotu",
                "elle",
                "Geometri motoru yüklenemedi; elemanların kotu elle kontrol edilmeli.",
                "EK-9 madde 15",
                15,
            )
        ]
    olcek = uu.calculate_unit_scale(b.model)  # proje birimi → metre
    katlar = sorted(
        (float(k.Elevation or 0.0) * olcek, k) for k in b.model.by_type("IfcBuildingStorey")
    )
    ust_kot: dict[int, float | None] = {}
    for i, (_, k) in enumerate(katlar):
        ust_kot[k.id()] = katlar[i + 1][0] if i + 1 < len(katlar) else None
    kot = {k.id(): z for z, k in katlar}
    yanlis: list[Any] = []
    for e in elemanlar:
        kutu = kutular.get(e.id())
        k = kati(e)
        if kutu is None or k is None or k.id() not in kot:
            continue
        alt, ust = kot[k.id()], ust_kot[k.id()]
        zmin, zmax = kutu[2], kutu[5]
        if zmax < alt - ALT_TOLERANS_M or (ust is not None and zmin > ust + UST_TOLERANS_M):
            yanlis.append(e)
    if yanlis:
        return [
            Bulgu(
                "kat-kotu",
                "uyari",
                f"{len(yanlis)} eleman bağlı olduğu katın kot aralığının dışında (kat kotunun "
                f"{ALT_TOLERANS_M:g} m altı ile üst katın {UST_TOLERANS_M:g} m üstü dışında); yanlış "
                "kata atanmış ya da yanlış kota çizilmiş olabilir.",
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
            "Elemanların gövdeleri bağlı oldukları katın kot aralığında.",
            "EK-9 madde 15",
            15,
        )
    ]
