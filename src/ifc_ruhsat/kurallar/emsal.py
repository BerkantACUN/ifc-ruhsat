"""Emsal (EK-9 madde 10): IfcSpatialZone'lar TREpys_EmsalOzellikSeti.EmsalDurumu ile
DAHIL/HARIC/DIGER diye işaretlenir; alanları toplanıp sahadaki KAKS ve parsel
alanıyla karşılaştırılır. Alan, nesnenin nicelik setlerindeki ilk alan değerinden
okunur (Qto_*BaseQuantities: NetFloorArea, GrossFloorArea, NetArea, GrossArea)."""

from __future__ import annotations

from typing import Any

from ifc_ruhsat.bulgu import Bulgu, varlik_listesi
from ifc_ruhsat.kurallar.ortak import Baglam, ozellik, ozellik_setleri, sayisal_mi

ALAN_ADLARI = ("NetFloorArea", "GrossFloorArea", "NetArea", "GrossArea", "Area")


def alan(e: Any) -> float | None:
    for set_adi, ozellikler in ozellik_setleri(e).items():
        if not set_adi.startswith("Qto_"):
            continue
        for ad in ALAN_ADLARI:
            d = ozellikler.get(ad)
            if sayisal_mi(d):
                return float(d)
    return None


def kontrol(b: Baglam) -> list[Bulgu]:
    zonlar = b.sinif("IfcSpatialZone")
    if not zonlar:
        return [
            Bulgu(
                "emsal",
                "elle",
                "Modelde IfcSpatialZone yok; emsal hesabı için emsale dahil/hariç alanlar mekânsal zon "
                "olarak modellenip TREpys_EmsalOzellikSeti.EmsalDurumu ile işaretlenmeli.",
                "EK-6 Tablo 6.60, EK-9 madde 10",
                10,
            )
        ]
    toplam: dict[str, float] = {"DAHIL": 0.0, "HARIC": 0.0, "DIGER": 0.0}
    alansiz, isaretsiz = [], []
    for z in zonlar:
        durum = ozellik(z, "TREpys_EmsalOzellikSeti", "EmsalDurumu")
        a = alan(z)
        if durum is None:
            isaretsiz.append(z)
            continue
        if a is None:
            alansiz.append(z)
            continue
        toplam[str(durum).strip().upper()] = toplam.get(str(durum).strip().upper(), 0.0) + a
    out: list[Bulgu] = []
    if isaretsiz:
        out.append(
            Bulgu(
                "emsal-isaret",
                "hata",
                f"{len(isaretsiz)} mekânsal zonda EmsalDurumu (DAHIL/HARIC/DIGER) yok.",
                "EK-6 Tablo 6.60",
                10,
                varlik_listesi(isaretsiz),
                len(isaretsiz),
            )
        )
    if alansiz:
        out.append(
            Bulgu(
                "emsal-alan",
                "uyari",
                f"{len(alansiz)} mekânsal zonun nicelik setinde alan yok; emsal toplamına giremedi.",
                "EK-9 madde 10",
                10,
                varlik_listesi(alansiz),
                len(alansiz),
            )
        )
    ozet = ", ".join(f"{k}: {v:,.2f} m²" for k, v in toplam.items() if v)
    out.append(
        Bulgu(
            "emsal-toplam",
            "bilgi",
            f"Emsal alanları — {ozet or 'hesaplanamadı'}.",
            "EK-9 madde 10",
            10,
        )
    )
    out += _kaks_karsilastir(b, toplam["DAHIL"])
    out.append(
        Bulgu(
            "emsal-tablo",
            "elle",
            "Hesaplanan toplamlar projedeki emsal hesap tablosuyla (pafta) karşılaştırılmalı.",
            "EK-9 madde 10",
            10,
        )
    )
    return out


def _kaks_karsilastir(b: Baglam, dahil: float) -> list[Bulgu]:
    for saha in b.sinif("IfcSite"):
        kaks = ozellik(saha, "TREpys_ParselOzellikSeti", "KAKS")
        parsel = ozellik(saha, "Pset_SiteCommon", "TotalArea")
        if sayisal_mi(kaks) and sayisal_mi(parsel) and parsel > 0 and dahil > 0:
            izin = float(kaks) * float(parsel)
            durum = "aşıyor" if dahil > izin + 1e-6 else "içinde"
            return [
                Bulgu(
                    "emsal-kaks",
                    "hata" if durum == "aşıyor" else "bilgi",
                    f"Emsale dahil alan {dahil:,.2f} m²; KAKS {kaks} × parsel {parsel:,.2f} m² = "
                    f"{izin:,.2f} m² sınırının {durum}.",
                    "EK-6 Tablo 6.55, EK-9 madde 10",
                    10,
                )
            ]
    return []
