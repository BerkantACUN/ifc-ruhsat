"""Yönetmelik eklerinin makine biçimi. Her dosya hangi sayfadan, ne zaman doğrulandığını
kendi ``kaynak`` alanında söyler; buradaki hiçbir sayı ya da ad koddan gelmez, ekten gelir."""

from __future__ import annotations

import json
from functools import cache
from importlib import resources
from typing import Any


@cache
def _yukle(ad: str) -> dict[str, Any]:
    return json.loads(resources.files("ifc_ruhsat.ekler").joinpath(ad).read_text(encoding="utf-8"))


def ek2_disiplinler() -> dict[str, str]:
    """EK-2 Tablo 2.2: iki harfli disiplin kodu → ad."""
    return _yukle("ek2_disiplinler.json")["disiplinler"]


def ek5() -> dict[str, Any]:
    return _yukle("ek5_siniflar.json")


@cache
def zorunlu_siniflar() -> dict[str, dict[str, Any]]:
    """EK-5 Tablo 5.1: IFC sınıfı → {turkce, kod}."""
    return {s["ifc"]: s for s in ek5()["zorunlu"]}


@cache
def istege_bagli_siniflar() -> dict[str, dict[str, Any]]:
    """EK-5 Tablo 5.2."""
    return {s["ifc"]: s for s in ek5()["istege_bagli"]}


@cache
def kategori_kodlari() -> dict[str, str]:
    """Üç harfli kategori kodu → IFC sınıfı (her iki tablo)."""
    out: dict[str, str] = {}
    for s in [*ek5()["zorunlu"], *ek5()["istege_bagli"]]:
        if s["kod"]:
            out[s["kod"]] = s["ifc"]
    return out


@cache
def ek6_tablolar() -> dict[str, dict[str, Any]]:
    """EK-6: doğrulanmış sınıf tabloları, IFC sınıfı → tablo."""
    return {t["ifc"]: t for t in _yukle("ek6_ozellikler.json")["tablolar"]}


@cache
def ek7_tablolar() -> dict[str, dict[str, Any]]:
    return {t["ifc"]: t for t in _yukle("ek7_proje.json")["tablolar"]}


def ek9_maddeler() -> list[dict[str, Any]]:
    return _yukle("ek9_form.json")["maddeler"]


def kaynaklar() -> dict[str, str]:
    """Her veri dosyasının kendi kaynak satırı — rapora ve README'ye girer."""
    return {
        ad: _yukle(ad)["kaynak"]
        for ad in (
            "ek2_disiplinler.json",
            "ek5_siniflar.json",
            "ek6_ozellikler.json",
            "ek7_proje.json",
            "ek9_form.json",
        )
    }
