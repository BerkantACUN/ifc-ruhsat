"""Geometri yardımcıları: IfcOpenShell ile dünya koordinatlarında sınır kutuları (metre).
Motor yüklenemez ya da bir gövde hesaplanamazsa o nesne atlanır; kural bunu bilerek
"elle" ya da kısmi raporlar."""

from __future__ import annotations

from typing import Any

Kutu = tuple[float, float, float, float, float, float]

# Çok büyük modellerde her elemanın gövdesini üretmek dakikalar alır; bu sınırın üstünde
# kot kontrolü yapılmaz, satır "elle" kalır.
ELEMAN_SINIRI = 20_000


def sinir_kutulari(nesneler: list[Any]) -> dict[int, Kutu] | None:
    """{ifc id: (xmin, ymin, zmin, xmax, ymax, zmax)}; geometri motoru yoksa None."""
    try:
        import ifcopenshell.geom
    except ImportError:
        return None
    ayar = ifcopenshell.geom.settings()
    ayar.set("use-world-coords", True)
    kutular: dict[int, Kutu] = {}
    for n in nesneler:
        if not getattr(n, "Representation", None):
            continue
        try:
            sekil = ifcopenshell.geom.create_shape(ayar, n)
        except Exception:  # noqa: BLE001 — bozuk geometri kuralı düşürmesin
            continue
        v = sekil.geometry.verts
        if len(v) < 12:
            continue
        xs, ys, zs = v[0::3], v[1::3], v[2::3]
        kutular[n.id()] = (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))
    return kutular


def hacim(k: Kutu) -> float:
    return max(k[3] - k[0], 0) * max(k[4] - k[1], 0) * max(k[5] - k[2], 0)


def kesisim(a: Kutu, b: Kutu) -> float:
    return hacim(
        (
            max(a[0], b[0]),
            max(a[1], b[1]),
            max(a[2], b[2]),
            min(a[3], b[3]),
            min(a[4], b[4]),
            min(a[5], b[5]),
        )
    )
