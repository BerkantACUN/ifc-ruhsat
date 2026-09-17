"""Tek giriş: bir IFC dosyasını aç, bütün kural modüllerini çalıştır, rapor döndür."""

from __future__ import annotations

from pathlib import Path

import ifcopenshell

from ifc_ruhsat.bulgu import Bulgu, Rapor
from ifc_ruhsat.kurallar import emsal, isim, kot, mahal, ortak, ozellik, sinif, yapi

MODULLER = (yapi, sinif, isim, ozellik, emsal, mahal, kot)

# EK-9'un bu sürümde makinece hiç denetlenemeyen satırları: rapor bunları "elle" olarak
# açıkça bırakır, "uygun" demez.
ELLE = {
    1: "Bakanlığın dosya boyutu sınırı henüz yayımlanmadı; dosya {boyut}, karar idarenin.",
    7: "Gelişim seviyesi (LOD 300) geometrinin ayrıntısına bakılarak elle değerlendirilir.",
    21: "PDF paftaların modelden üretildiği yalnızca teslim sürecinden anlaşılır.",
}


def modeli_ac(yol: str | Path) -> ifcopenshell.file:
    yol = Path(yol)
    if not yol.exists():
        raise FileNotFoundError(f"dosya yok: {yol}")
    return ifcopenshell.open(str(yol))


def disiplini_sec(yol: Path, verilen: str | None) -> str:
    """Verilmemişse EK-2 biçimindeki dosya adının üçüncü alanından; o da yoksa mimari (MM)."""
    if verilen:
        return verilen.upper()
    from ifc_ruhsat.kurallar.isim import DOSYA_ADI

    m = DOSYA_ADI.match(yol.stem)
    return m.group(3) if m else "MM"


def kontrol_et(yol: str | Path, disiplin: str | None = None) -> Rapor:
    yol = Path(yol)
    model = modeli_ac(yol)
    b = ortak.Baglam(model=model, dosya_adi=yol.name, disiplin=disiplini_sec(yol, disiplin))
    rapor = Rapor(dosya=str(yol), schema=model.schema)
    boyut = _boyut(yol.stat().st_size)
    for modul in MODULLER:
        rapor.ekle(*modul.kontrol(b))
    for no, mesaj in ELLE.items():
        if not any(bu.ek9 == no and bu.seviye == "elle" for bu in rapor.bulgular):
            rapor.ekle(
                Bulgu(f"elle-{no}", "elle", mesaj.format(boyut=boyut), f"EK-9 madde {no}", no)
            )
    rapor.bulgular.sort(key=lambda bu: (bu.ek9 or 99, _sira(bu.seviye)))
    return rapor


def _boyut(bayt: int) -> str:
    return f"{bayt / (1024 * 1024):,.1f} MB" if bayt >= 1024 * 1024 else f"{bayt / 1024:,.0f} KB"


def _sira(seviye: str) -> int:
    return {"hata": 0, "uyari": 1, "elle": 2, "bilgi": 3}[seviye]


def ozet(yol: str | Path) -> dict:
    """Modelin kimliği: şema, yazılım, proje/saha/bina, kat sayısı, sınıf sayıları."""
    yol = Path(yol)
    model = modeli_ac(yol)
    b = ortak.Baglam(model=model, dosya_adi=yol.name)
    proje = next(iter(model.by_type("IfcProject")), None)
    uygulama = next(iter(model.by_type("IfcApplication")), None)
    return {
        "dosya": str(yol),
        "boyutMB": round(yol.stat().st_size / (1024 * 1024), 2),
        "schema": model.schema,
        "yazilim": f"{uygulama.ApplicationFullName} {uygulama.Version}" if uygulama else None,
        "proje": proje.Name if proje else None,
        "saha": [s.Name for s in model.by_type("IfcSite")],
        "bina": [s.Name for s in model.by_type("IfcBuilding")],
        "katlar": [s.Name for s in model.by_type("IfcBuildingStorey")],
        "mahalSayisi": len(model.by_type("IfcSpace")),
        "varlikSayisi": len(b.varliklar),
        "sinifSayilari": b.sinif_sayilari,
    }
