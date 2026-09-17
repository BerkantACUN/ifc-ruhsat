"""Mahaller (IfcSpace): numara şablonu Kat_Bölüm_SıraNo (m.10, EK-3 Tablo 3.1, kat kodları
EK-2 Tablo 2.14 — EK-9 m.4); her mahalin kapalı bir gövdesi olması (m.14) ve aynı kattaki
mahallerin birbirine girmemesi (m.13). Geometri IfcOpenShell ile hesaplanır; hesaplanamazsa
satır "elle" bırakılır, uydurulmaz."""

from __future__ import annotations

import re
from itertools import combinations
from typing import Any

from ifc_ruhsat.bulgu import Bulgu, varlik_listesi
from ifc_ruhsat.kurallar.geometri import hacim, kesisim, sinir_kutulari
from ifc_ruhsat.kurallar.ortak import Baglam, kati, oznitelik

# EK-3 Tablo 3.1: Kat(3) _ Bölüm/Fonksiyon(3) _ Sıra No(3); kat kodu EK-2 Tablo 2.14
# (B01… bodrum, K00 zemin, K01… kat, NNN kattan bağımsız).
MAHAL_NO = re.compile(r"^(B\d{2}|K\d{2}|NNN)_([A-Z0-9]{3})_(\d{3})$")
ORTUSME_ORANI = 0.10  # küçük hacim oranına göre; komşu duvar payı için tolerans


def kontrol(b: Baglam) -> list[Bulgu]:
    mahaller = b.sinif("IfcSpace")
    if not mahaller:
        return []
    out: list[Bulgu] = []
    out += _numaralar(mahaller)
    out += _geometri(mahaller)
    return out


def _numaralar(mahaller: list[Any]) -> list[Bulgu]:
    bos, bicim, isimsiz = [], [], []
    for m in mahaller:
        ad = oznitelik(m, "Name")
        if ad is None:
            bos.append(m)
        elif not MAHAL_NO.match(ad.strip()):
            bicim.append(m)
        if oznitelik(m, "LongName") is None:
            isimsiz.append(m)
    out = []
    if bos:
        out.append(
            Bulgu(
                "mahal-no-bos",
                "hata",
                f"{len(bos)} mahalin numarası (Name) boş.",
                "m.10, EK-3 3.2",
                4,
                varlik_listesi(bos),
                len(bos),
            )
        )
    if bicim:
        out.append(
            Bulgu(
                "mahal-no-bicim",
                "hata",
                f"{len(bicim)} mahalin numarası EK-3 şablonuna uymuyor. Beklenen Kat_Bölüm_SıraNo, "
                "alt tire ile: kat kodu B01/B02… (bodrum), K00 (zemin), K01… ya da NNN; bölüm üç "
                "karakter; sıra no üç basamak — örn. K00_DAI_001.",
                "m.10, EK-3 Tablo 3.1, EK-2 Tablo 2.14",
                4,
                varlik_listesi(bicim),
                len(bicim),
            )
        )
    if isimsiz:
        out.append(
            Bulgu(
                "mahal-isim-bos",
                "hata",
                f"{len(isimsiz)} mahalin ismi (LongName) boş; mahal ismi EK-3 Tablo 3.2'deki adlarla "
                "ya da kısaltmalarıyla verilir.",
                "m.10, EK-3 3.3",
                4,
                varlik_listesi(isimsiz),
                len(isimsiz),
            )
        )
    if not out:
        out.append(
            Bulgu(
                "mahal-no", "bilgi", "Mahal numaraları ve isimleri EK-3'e uygun.", "m.10, EK-3", 4
            )
        )
    return out


def _geometri(mahaller: list[Any]) -> list[Bulgu]:
    kutular = sinir_kutulari(mahaller)
    if kutular is None:
        return [
            Bulgu(
                "mahal-geometri",
                "elle",
                "Geometri motoru yüklenemedi; mahallerin kapalılığı ve örtüşmesi elle kontrol edilmeli.",
                "EK-9 madde 13–14",
                13,
            )
        ]
    out: list[Bulgu] = []
    govdesiz = [m for m in mahaller if m.id() not in kutular or hacim(kutular[m.id()]) <= 1e-6]
    if govdesiz:
        out.append(
            Bulgu(
                "mahal-govde",
                "hata",
                f"{len(govdesiz)} mahalin kapalı bir 3B gövdesi yok (hacim sıfır ya da gösterim eksik); "
                "mahaller kapalı hacim olarak, üst sınırı tanımlı modellenmeli.",
                "EK-9 madde 14",
                14,
                varlik_listesi(govdesiz),
                len(govdesiz),
            )
        )
    else:
        out.append(
            Bulgu(
                "mahal-govde",
                "bilgi",
                "Her mahalin hacimli bir 3B gövdesi var.",
                "EK-9 madde 14",
                14,
            )
        )
    # Örtüşme: aynı kattaki mahal çiftleri; küçük hacmin %10'undan fazlası ortaksa uyarı.
    kat_gruplari: dict[int | None, list[Any]] = {}
    for m in mahaller:
        if m.id() in kutular:
            k = kati(m)
            kat_gruplari.setdefault(k.id() if k else None, []).append(m)
    ortusen: list[Any] = []
    for grup in kat_gruplari.values():
        for a, b in combinations(grup, 2):
            ka, kb = kutular[a.id()], kutular[b.id()]
            ortak = kesisim(ka, kb)
            kucuk = min(hacim(ka), hacim(kb))
            if kucuk > 1e-6 and ortak / kucuk > ORTUSME_ORANI:
                ortusen.extend([a, b])
    if ortusen:
        out.append(
            Bulgu(
                "mahal-ortusme",
                "uyari",
                f"{len(ortusen) // 2} mahal çifti aynı katta birbirine giriyor (sınır kutuları küçük "
                f"hacmin %{int(ORTUSME_ORANI * 100)}'undan fazla örtüşüyor); sınırları düzeltin. "
                "Kutu tabanlı kaba kontroldür, L biçimli mahallerde yanlış alarm verebilir.",
                "EK-9 madde 13",
                13,
                varlik_listesi(ortusen),
                len(ortusen),
            )
        )
    else:
        out.append(
            Bulgu(
                "mahal-ortusme",
                "bilgi",
                "Aynı kattaki mahaller örtüşmüyor (sınır kutusu kontrolü).",
                "EK-9 madde 13",
                13,
            )
        )
    return out
