"""İsimlendirme: varlık adı ``Disiplin-KategoriKodu-Açıklama`` (m.11, EK-5 5.5, EK-9 m.5);
dosya adı EK-2 Tablo 2.1'in dokuz alanı (m.6, EK-9 m.3); proje adı boş değil (EK-1)."""

from __future__ import annotations

import re
from pathlib import Path

from ifc_ruhsat import veri
from ifc_ruhsat.bulgu import Bulgu, varlik_listesi
from ifc_ruhsat.kurallar.ortak import Baglam, oznitelik

# Disiplin (2 harf) - Kategori (3 harf) - Açıklama (alt tire ile ayrılmış, orta tire yok)
VARLIK_ADI = re.compile(r"^([A-Z]{2})-([A-Z]{3})(?:-([^\s-]+))?$")

# EK-2 Tablo 2.1: ProjeKodu(6) BinaKodu(2) Disiplin(2) AltDisiplin(4) DosyaTürü(2)
# DosyaTipi(3) Kat/Konum(3) SıraNo(2) RevizyonNo(3), alt tire ile.
DOSYA_ADI = re.compile(
    r"^([A-Za-z0-9]{6})_([A-Za-z0-9]{2})_([A-Z]{2})_([A-Z0-9]{4})_([A-Z0-9]{2})_"
    r"([A-Z0-9]{3})_([A-Za-z0-9]{3})_(\d{2})_(\d{3})$"
)

# İsimlendirme şablonu yapı elemanları ve mekânsal elemanlar içindir; iskelet ve
# proje bilgileri EK-1/EK-3'e göre ayrı adlandırılır.
SABLON_DISI = (
    "IfcProject",
    "IfcSite",
    "IfcBuilding",
    "IfcBuildingStorey",
    "IfcSpace",
    "IfcGridAxis",
)


def kontrol(b: Baglam) -> list[Bulgu]:
    out: list[Bulgu] = []
    out += _varlik_adlari(b)
    out += _dosya_adi(b)
    out += _proje_adi(b)
    out.append(
        Bulgu(
            "mahal-adi",
            "elle",
            "Mahal numarası ve mahal ismi (EK-3: kat, bölüm/fonksiyon, sıra no) bu sürümde "
            "denetlenmiyor; mahal listesinden kontrol edin.",
            "m.10, EK-3",
            4,
        )
    )
    return out


def _varlik_adlari(b: Baglam) -> list[Bulgu]:
    out = []
    disiplinler = veri.ek2_disiplinler()
    kodlar = veri.kategori_kodlari()
    bos, bicim, disiplin_yanlis, kod_yanlis, kod_sinif = [], [], [], [], []
    for e in b.varliklar:
        if e.is_a() in SABLON_DISI:
            continue
        ad = oznitelik(e, "Name")
        if ad is None:
            bos.append(e)
            continue
        m = VARLIK_ADI.match(ad.strip())
        if not m:
            bicim.append(e)
            continue
        disiplin, kod = m.group(1), m.group(2)
        if disiplin not in disiplinler:
            disiplin_yanlis.append(e)
        if kod not in kodlar:
            kod_yanlis.append(e)
        elif kodlar[kod] != e.is_a():
            kod_sinif.append(e)
    if bos:
        out.append(
            Bulgu(
                "isim-bos",
                "hata",
                f"{len(bos)} varlığın adı (Name) boş; her varlık Disiplin-Kategori-Açıklama ile adlandırılır.",
                "m.11, EK-5 5.5",
                5,
                varlik_listesi(bos),
                len(bos),
            )
        )
    if bicim:
        out.append(
            Bulgu(
                "isim-bicim",
                "hata",
                f"{len(bicim)} varlığın adı şablona uymuyor. Beklenen: iki harf disiplin, üç harf "
                "kategori kodu ve açıklama, orta tire ile (örn. MM-DVR-dis_20cm); açıklama içinde "
                "alt tire kullanılır, orta tire ve boşluk kullanılmaz.",
                "m.11, EK-5 5.5 ve Tablo 5.3",
                5,
                varlik_listesi(bicim),
                len(bicim),
            )
        )
    if disiplin_yanlis:
        out.append(
            Bulgu(
                "isim-disiplin",
                "hata",
                f"{len(disiplin_yanlis)} varlıkta disiplin kodu EK-2 Tablo 2.2'de yok "
                f"(geçerli: {', '.join(disiplinler)}).",
                "EK-2 Tablo 2.2",
                5,
                varlik_listesi(disiplin_yanlis),
                len(disiplin_yanlis),
            )
        )
    if kod_yanlis:
        out.append(
            Bulgu(
                "isim-kategori",
                "hata",
                f"{len(kod_yanlis)} varlıkta kategori kodu EK-5 Tablo 5.1/5.2'de yok.",
                "EK-5 Tablo 5.1–5.2",
                5,
                varlik_listesi(kod_yanlis),
                len(kod_yanlis),
            )
        )
    if kod_sinif:
        ornek = kod_sinif[0]
        out.append(
            Bulgu(
                "isim-kategori-sinif",
                "hata",
                f"{len(kod_sinif)} varlıkta kategori kodu varlığın IFC sınıfına ait değil "
                f"(örn. {ornek.Name} adlı varlık {ornek.is_a()}; bu sınıfın kodu "
                f"{veri.zorunlu_siniflar().get(ornek.is_a(), veri.istege_bagli_siniflar().get(ornek.is_a(), {})).get('kod', '?')}).",
                "EK-5 5.5.2",
                5,
                varlik_listesi(kod_sinif),
                len(kod_sinif),
            )
        )
    if not out:
        out.append(
            Bulgu("isim", "bilgi", "Varlık adları EK-5 şablonuna uygun.", "m.11, EK-5 5.5", 5)
        )
    return out


def _dosya_adi(b: Baglam) -> list[Bulgu]:
    govde = Path(b.dosya_adi).stem
    m = DOSYA_ADI.match(govde)
    if not m:
        return [
            Bulgu(
                "dosya-adi",
                "uyari",
                f"Dosya adı '{govde}' EK-2 Tablo 2.1 şablonuna uymuyor: "
                "ProjeKodu(6)_BinaKodu(2)_Disiplin(2)_AltDisiplin(4)_DosyaTürü(2)_DosyaTipi(3)_"
                "KatKonum(3)_SıraNo(2)_RevizyonNo(3), örn. 123456_00_MM_GNEL_MD_BIM_000_01_000.",
                "m.6, EK-2 Tablo 2.1",
                3,
            )
        ]
    disiplin = m.group(3)
    if disiplin not in veri.ek2_disiplinler():
        return [
            Bulgu(
                "dosya-adi-disiplin",
                "uyari",
                f"Dosya adındaki disiplin kodu '{disiplin}' EK-2 Tablo 2.2'de yok.",
                "EK-2 Tablo 2.2",
                3,
            )
        ]
    return [
        Bulgu(
            "dosya-adi",
            "bilgi",
            "Dosya adı EK-2 şablonunun dokuz alanına uyuyor (alt disiplin, dosya türü ve tipi "
            "kodları bu sürümde listeyle karşılaştırılmıyor).",
            "m.6, EK-2 Tablo 2.1",
            3,
        )
    ]


def _proje_adi(b: Baglam) -> list[Bulgu]:
    for p in b.sinif("IfcProject"):
        if oznitelik(p, "Name") is None:
            return [
                Bulgu(
                    "proje-adi",
                    "hata",
                    "IfcProject.Name boş; EK-1'e göre proje kodu yazılmalı.",
                    "m.6, EK-1, EK-7 Tablo 7.1",
                    3,
                )
            ]
    return []
