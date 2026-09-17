"""Kuralların ortak yardımcıları: modeli bir kez tarayıp sınıf, kat ve özellik
bilgisini hazır tutan bağlam, ve IFC'nin dolaylı ilişkilerini (kat, malzeme,
özellik seti) düz sorulara çeviren küçük fonksiyonlar."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

import ifcopenshell
import ifcopenshell.util.element as ue

# Kontrol edilecek nesneler: yapı elemanları, mekânsal elemanlar ve grup benzerleri.
# IfcRoot altındaki ilişki/özellik nesneleri değil.
KOK_SINIFLAR = ("IfcElement", "IfcSpatialElement", "IfcGroup", "IfcGridAxis")


@dataclass
class Baglam:
    model: ifcopenshell.file
    dosya_adi: str
    disiplin: str = "MM"
    ek: dict[str, Any] = field(default_factory=dict)

    @cached_property
    def varliklar(self) -> list[Any]:
        """Modeldeki kontrol edilecek her nesne, sınıf adına göre sıralı."""
        gorulen: dict[int, Any] = {}
        for kok in KOK_SINIFLAR:
            try:
                for e in self.model.by_type(kok):
                    gorulen[e.id()] = e
            except RuntimeError:
                continue
        return sorted(gorulen.values(), key=lambda e: (e.is_a(), e.id()))

    @cached_property
    def sinif_sayilari(self) -> dict[str, int]:
        sayi: dict[str, int] = {}
        for e in self.varliklar:
            sayi[e.is_a()] = sayi.get(e.is_a(), 0) + 1
        return dict(sorted(sayi.items()))

    def sinif(self, ad: str) -> list[Any]:
        try:
            return [e for e in self.model.by_type(ad) if e.is_a() == ad]
        except RuntimeError:
            return []


def ozellik_setleri(e: Any) -> dict[str, dict[str, Any]]:
    """Nesnenin (ve tipinin) özellik + nicelik setleri: {set adı: {özellik: değer}}."""
    try:
        return ue.get_psets(e, should_inherit=True)
    except Exception:  # noqa: BLE001 — bozuk bir set tüm kontrolü düşürmesin
        return {}


def ozellik(e: Any, set_adi: str, ad: str) -> Any:
    """Bir özelliğin değeri; set ya da özellik yoksa None. Boş metin de None sayılır."""
    deger = ozellik_setleri(e).get(set_adi, {}).get(ad)
    if isinstance(deger, str) and not deger.strip():
        return None
    return deger


def oznitelik(e: Any, ad: str) -> Any:
    """Öznitelik değeri; şemada yoksa ya da boşsa None."""
    try:
        deger = getattr(e, ad)
    except AttributeError:
        return None
    if isinstance(deger, str) and not deger.strip():
        return None
    return deger


def malzeme_adi(e: Any) -> str | None:
    """IfcRelAssociatesMaterial ile bağlı malzemenin adı; katmanlı/profilli setlerde ilk katman."""
    m = ue.get_material(e, should_skip_usage=True)
    if m is None:
        return None
    if m.is_a("IfcMaterial"):
        return m.Name
    for alan in ("MaterialLayers", "MaterialProfiles", "MaterialConstituents", "Materials"):
        parcalar = getattr(m, alan, None)
        if parcalar:
            ilk = parcalar[0]
            mat = getattr(ilk, "Material", ilk)
            return getattr(mat, "Name", None)
    return getattr(m, "Name", None)


def kati(e: Any) -> Any | None:
    """Nesnenin içinde bulunduğu IfcBuildingStorey (IfcRelContainedInSpatialStructure), yoksa None."""
    kap = ue.get_container(e)
    while kap is not None and not kap.is_a("IfcBuildingStorey"):
        kap = ue.get_aggregate(kap) if not kap.is_a("IfcProject") else None
    return kap


def sayisal_mi(deger: Any) -> bool:
    return isinstance(deger, (int, float)) and not isinstance(deger, bool)


def mantiksal_mi(deger: Any) -> bool:
    return isinstance(deger, bool)


def metin_mi(deger: Any) -> bool:
    return isinstance(deger, str) and bool(deger.strip())
