"""EK-6 (sınıf başına zorunlu öznitelik ve özellik setleri) ve EK-7 (proje, kişi,
kuruluş) kontrolleri — EK-9 madde 2, 9 ve 20. Her (sınıf, gereklilik) çifti için
tek bulgu üretilir; başarısız varlıklar GlobalId ile listelenir."""

from __future__ import annotations

from typing import Any

from ifc_ruhsat import veri
from ifc_ruhsat.bulgu import Bulgu, varlik_listesi
from ifc_ruhsat.kurallar.ortak import (
    Baglam,
    malzeme_adi,
    mantiksal_mi,
    metin_mi,
    ozellik,
    ozellik_setleri,
    oznitelik,
    sayisal_mi,
)

TIP_ADI = {"M": "metin", "S": "sayı", "B": "mantıksal (DOĞRU/YANLIŞ)", "SM": "sayı ya da metin"}


def kontrol(b: Baglam) -> list[Bulgu]:
    out: list[Bulgu] = []
    out += _ek6(b)
    out += _ek7(b)
    return out


def _tip_uygun(deger: Any, tip: str) -> bool:
    # İlişki değerleri (Roles, Addresses, ThePerson…): dolu bir liste ya da nesne yeter.
    if isinstance(deger, tuple):
        return len(deger) > 0
    if hasattr(deger, "is_a"):
        return True
    if tip == "S":
        # IFC'de metin tutulan kimlik alanları (vergi no gibi) rakam dizisi olarak da geçer.
        return sayisal_mi(deger) or (isinstance(deger, str) and deger.strip().isdigit())
    if tip == "B":
        return mantiksal_mi(deger)
    if tip == "M":
        return metin_mi(deger)
    return sayisal_mi(deger) or metin_mi(deger)


def _ek6(b: Baglam) -> list[Bulgu]:
    out: list[Bulgu] = []
    tablolar = veri.ek6_tablolar()
    dogrulanmamis: list[str] = []
    for sinif in veri.zorunlu_siniflar():
        varliklar = b.sinif(sinif)
        if not varliklar:
            continue
        tablo = tablolar.get(sinif)
        if tablo is None:
            dogrulanmamis.append(sinif)
            out += _yalniz_isim(sinif, varliklar)
            continue
        out += _tablo_kontrol(b, tablo, varliklar)
    if dogrulanmamis:
        out.append(
            Bulgu(
                "ek6-kapsam",
                "bilgi",
                f"Modelde bulunan {len(dogrulanmamis)} zorunlu sınıfın EK-6 tablosu bu sürümde henüz "
                f"kodlanmadı, yalnızca İsim denetlendi: {', '.join(dogrulanmamis)}. (KAYNAKLAR.md)",
                "EK-6",
                9,
            )
        )
    if not any(bu.seviye == "hata" and bu.ek9 == 9 for bu in out):
        out.append(
            Bulgu(
                "ek6",
                "bilgi",
                f"Kodlanmış {len(tablolar)} EK-6 tablosundaki zorunlu öznitelik ve özellikler tam.",
                "m.13, EK-6",
                9,
            )
        )
    return out


def _yalniz_isim(sinif: str, varliklar: list[Any]) -> list[Bulgu]:
    bos = [e for e in varliklar if oznitelik(e, "Name") is None]
    if not bos:
        return []
    return [
        Bulgu(
            "ek6-isim",
            "hata",
            f"{sinif}: {len(bos)} varlıkta İsim (Name) boş.",
            "EK-6 (İsim her tabloda zorunlu)",
            9,
            varlik_listesi(bos),
            len(bos),
        )
    ]


def _tablo_kontrol(b: Baglam, tablo: dict[str, Any], varliklar: list[Any]) -> list[Bulgu]:
    out: list[Bulgu] = []
    sinif, ref = tablo["ifc"], f"EK-6 Tablo {tablo['tablo']}"
    out += _eksik_setler(sinif, ref, tablo, varliklar)
    for g in tablo["gerekenler"]:
        tur = g["tur"]
        if tur == "oznitelik":
            if g["ad"] == "PredefinedType":
                continue  # sinif.py ayrıca ve daha ayrıntılı bakıyor (EK-9 m.19)
            out += _oznitelik_kontrol(sinif, ref, g, varliklar)
        elif tur == "ozellik":
            out += _ozellik_kontrol(sinif, ref, g, varliklar)
        elif tur == "malzeme":
            out += _malzeme_kontrol(sinif, ref, g, varliklar)
        elif tur == "iliski":
            out += _sistem_kontrol(sinif, ref, varliklar)
        elif tur == "katman":
            pass  # IfcCovering katmanları: _kaplama_kontrol tek seferde bakar
    if sinif == "IfcCovering":
        out += _kaplama_kontrol(b, ref, varliklar)
    elif any(g["tur"] == "katman" for g in tablo["gerekenler"]):
        out += _katman_kontrol(sinif, ref, varliklar)
    if sinif == "IfcSpace":
        out = _mahal_kaplama_gevset(b, out)
    return out


def _oznitelik_kontrol(sinif: str, ref: str, g: dict, varliklar: list[Any]) -> list[Bulgu]:
    bos, tip_yanlis, deger_yanlis = [], [], []
    izinli = g.get("degerler")
    if varliklar and not _semada_var(varliklar[0], g["ad"]):
        return []  # tablo şemada olmayan bir öznitelik sayıyor (IfcGroup.Tag gibi) — KAYNAKLAR.md
    for e in varliklar:
        d = oznitelik(e, g["ad"])
        if d is None:
            bos.append(e)
        elif not _tip_uygun(d, g["veriTipi"]):
            tip_yanlis.append(e)
        elif izinli and str(d).strip().upper() not in izinli:
            deger_yanlis.append(e)
    out = []
    if bos:
        out.append(
            Bulgu(
                "ek6-oznitelik",
                "hata",
                f"{sinif}.{g['ad']} ({g['turkce']}) {len(bos)} varlıkta boş.",
                ref,
                9,
                varlik_listesi(bos),
                len(bos),
            )
        )
    if tip_yanlis:
        out.append(
            Bulgu(
                "ek6-oznitelik-tip",
                "uyari",
                f"{sinif}.{g['ad']} {len(tip_yanlis)} varlıkta {TIP_ADI[g['veriTipi']]} değil.",
                ref,
                9,
                varlik_listesi(tip_yanlis),
                len(tip_yanlis),
            )
        )
    if deger_yanlis:
        out.append(
            Bulgu(
                "ek6-oznitelik-deger",
                "hata",
                f"{sinif}.{g['ad']} {len(deger_yanlis)} varlıkta izinli değerlerden biri değil "
                f"({', '.join(izinli)}).",
                ref,
                9,
                varlik_listesi(deger_yanlis),
                len(deger_yanlis),
            )
        )
    return out


def _semada_var(e: Any, ad: str) -> bool:
    try:
        getattr(e, ad)
    except AttributeError:
        return False
    return True


def _baska_sette(e: Any, set_adi: str, ad: str) -> str | None:
    """Aynı adlı özellik başka bir sette varsa o setin adı — 'yanlış Pset' bulgusu için."""
    for aday, ozellikler in ozellik_setleri(e).items():
        if aday != set_adi and ad in ozellikler:
            return aday
    return None


def _eksik_setler(sinif: str, ref: str, tablo: dict[str, Any], varliklar: list[Any]) -> list[Bulgu]:
    """Bir özellik seti varlıkta hiç yoksa özellik özellik değil, set olarak tek bulgu: gerçek
    modellerde en sık durum budur (Pset_BuildingCommon tamamen boş gibi) ve 12 satır yerine 1 satır."""
    out = []
    setler: dict[str, list[str]] = {}
    for g in tablo["gerekenler"]:
        if g["tur"] == "ozellik":
            setler.setdefault(g["set"], []).append(g["ad"])
    for set_adi, adlar in setler.items():
        # Set yok ama özellikleri başka bir sette duruyorsa o "yanlış set" bulgusudur, burada sayılmaz.
        yok = [
            e
            for e in varliklar
            if set_adi not in ozellik_setleri(e)
            and not any(_baska_sette(e, set_adi, ad) for ad in adlar)
        ]
        if not yok:
            continue
        out.append(
            Bulgu(
                "ek6-set",
                "hata",
                f"{sinif}: {set_adi} özellik seti {len(yok)} varlıkta hiç yok; zorunlu özellikler: "
                f"{', '.join(adlar)}.",
                ref,
                9,
                varlik_listesi(yok),
                len(yok),
            )
        )
    return out


def _ozellik_kontrol(sinif: str, ref: str, g: dict, varliklar: list[Any]) -> list[Bulgu]:
    bos, yanlis_set, tip_yanlis, deger_yanlis = [], {}, [], []
    izinli = g.get("degerler")
    for e in varliklar:
        d = ozellik(e, g["set"], g["ad"])
        if (
            d is None
            and g["set"] not in ozellik_setleri(e)
            and not _baska_sette(e, g["set"], g["ad"])
        ):
            continue  # set bütünüyle yok: _eksik_setler tek bulguyla raporladı
        if d is None:
            baska = _baska_sette(e, g["set"], g["ad"])
            if baska:
                yanlis_set.setdefault(baska, []).append(e)
            else:
                bos.append(e)
        elif not _tip_uygun(d, g["veriTipi"]):
            tip_yanlis.append(e)
        elif izinli and str(d).strip().upper() not in izinli:
            deger_yanlis.append(e)
    out = []
    etiket = f"{g['set']}.{g['ad']} ({g['turkce']})"
    if bos:
        out.append(
            Bulgu(
                "ek6-ozellik",
                "hata",
                f"{sinif}: {etiket} {len(bos)} varlıkta yok ya da boş.",
                ref,
                9,
                varlik_listesi(bos),
                len(bos),
            )
        )
    for baska, liste in yanlis_set.items():
        out.append(
            Bulgu(
                "ek6-ozellik-set",
                "hata",
                f"{sinif}: {g['ad']} özelliği {len(liste)} varlıkta '{baska}' setinde; "
                f"yönetmelik {g['set']} altında ister.",
                ref,
                20,
                varlik_listesi(liste),
                len(liste),
            )
        )
    if tip_yanlis:
        out.append(
            Bulgu(
                "ek6-ozellik-tip",
                "uyari",
                f"{sinif}: {etiket} {len(tip_yanlis)} varlıkta {TIP_ADI[g['veriTipi']]} değil.",
                ref,
                20,
                varlik_listesi(tip_yanlis),
                len(tip_yanlis),
            )
        )
    if deger_yanlis:
        out.append(
            Bulgu(
                "ek6-ozellik-deger",
                "hata",
                f"{sinif}: {etiket} {len(deger_yanlis)} varlıkta {', '.join(izinli)} dışında bir değer.",
                ref,
                9,
                varlik_listesi(deger_yanlis),
                len(deger_yanlis),
            )
        )
    return out


def _malzeme_kontrol(sinif: str, ref: str, g: dict, varliklar: list[Any]) -> list[Bulgu]:
    yok, bicim = [], []
    for e in varliklar:
        ad = malzeme_adi(e)
        if not ad:
            yok.append(e)
        elif "_" not in ad:
            bicim.append(e)
    out = []
    if yok:
        out.append(
            Bulgu(
                "ek6-malzeme",
                "hata",
                f"{sinif}: {len(yok)} varlığa malzeme atanmamış (IfcRelAssociatesMaterial).",
                ref,
                9,
                varlik_listesi(yok),
                len(yok),
            )
        )
    if bicim:
        out.append(
            Bulgu(
                "ek6-malzeme-bicim",
                "uyari",
                f"{sinif}: {len(bicim)} varlıkta malzeme adı 'Malzeme İsmi_Dayanım' biçiminde değil "
                "(örn. Beton_C25, Çelik_S355).",
                ref,
                9,
                varlik_listesi(bicim),
                len(bicim),
            )
        )
    return out


def _sistem_kontrol(sinif: str, ref: str, varliklar: list[Any]) -> list[Bulgu]:
    bagsiz = [
        e
        for e in varliklar
        if not any(
            r.is_a("IfcRelAssignsToGroup") and r.RelatingGroup.is_a("IfcSystem")
            for r in (getattr(e, "HasAssignments", None) or [])
        )
    ]
    if not bagsiz:
        return []
    return [
        Bulgu(
            "ek6-sistem",
            "hata",
            f"{sinif}: {len(bagsiz)} varlık bir sisteme (IfcSystem, IfcRelAssignsToGroup) bağlı değil.",
            ref,
            9,
            varlik_listesi(bagsiz),
            len(bagsiz),
        )
    ]


def _katmanli(e: Any) -> bool:
    """IfcCovering'de kalınlığı olan bir malzeme katman seti var mı?"""
    for r in getattr(e, "HasAssociations", None) or []:
        if not r.is_a("IfcRelAssociatesMaterial"):
            continue
        m = r.RelatingMaterial
        if m.is_a("IfcMaterialLayerSetUsage"):
            m = m.ForLayerSet
        if m.is_a("IfcMaterialLayerSet") and any(
            k.Material is not None and k.LayerThickness for k in m.MaterialLayers
        ):
            return True
    return False


def _mahalde_kaplama_var(b: Baglam) -> bool:
    return any(
        any(
            ozellik(s, "Pset_SpaceCoveringRequirements", a) is not None
            for a in ("FloorCovering", "WallCovering", "CeilingCovering")
        )
        for s in b.sinif("IfcSpace")
    )


def _kaplama_kontrol(b: Baglam, ref: str, kaplamalar: list[Any]) -> list[Bulgu]:
    """Tablo 6.20/6.58 dipnotu: kaplama bilgisi ya IfcSpace'te ya IfcCovering katmanında — biri yeter."""
    if _mahalde_kaplama_var(b):
        return []
    katmansiz = [e for e in kaplamalar if not _katmanli(e)]
    if not katmansiz:
        return []
    return [
        Bulgu(
            "ek6-kaplama",
            "uyari",
            f"IfcCovering: {len(katmansiz)} kaplamada malzeme katmanı/kalınlığı yok ve mahallerde de "
            "Pset_SpaceCoveringRequirements tanımlı değil; iki yöntemden biri zorunlu.",
            ref,
            9,
            varlik_listesi(katmansiz),
            len(katmansiz),
        )
    ]


def _katman_kontrol(sinif: str, ref: str, varliklar: list[Any]) -> list[Bulgu]:
    """Katman malzemesi ve kalınlığı isteyen tablolar (IfcPavement): katmanlı malzeme seti zorunlu."""
    katmansiz = [e for e in varliklar if not _katmanli(e)]
    if not katmansiz:
        return []
    return [
        Bulgu(
            "ek6-katman",
            "hata",
            f"{sinif}: {len(katmansiz)} varlıkta katman malzemesi/kalınlığı yok "
            "(IfcMaterialLayerSet, her katmanda Material ve LayerThickness).",
            ref,
            9,
            varlik_listesi(katmansiz),
            len(katmansiz),
        )
    ]


def _mahal_kaplama_gevset(b: Baglam, bulgular: list[Bulgu]) -> list[Bulgu]:
    """Kaplama bilgisi IfcCovering katmanlarında verilmişse mahaldeki set zorunlu değildir."""
    kaplamalar = b.sinif("IfcCovering")
    if kaplamalar and all(_katmanli(k) for k in kaplamalar):
        return [
            bu
            for bu in bulgular
            if not (bu.kod == "ek6-ozellik" and "Pset_SpaceCoveringRequirements" in bu.mesaj)
        ]
    return bulgular


def _ek7(b: Baglam) -> list[Bulgu]:
    out: list[Bulgu] = []
    tablolar = veri.ek7_tablolar()
    for sinif in ("IfcProject", "IfcPerson", "IfcOrganization", "IfcPersonAndOrganization"):
        varliklar = b.sinif(sinif)
        tablo = tablolar[sinif]
        ref = f"EK-7 Tablo {tablo['tablo']}"
        if not varliklar:
            out.append(
                Bulgu(
                    "ek7-yok",
                    "hata" if sinif == "IfcProject" else "uyari",
                    f"{sinif} modelde yok; proje müellifi/kuruluş bilgisi {ref} uyarınca tanımlanmalı.",
                    ref,
                    2,
                )
            )
            continue
        for g in tablo["gerekenler"]:
            if g["tur"] == "oznitelik":
                out += [
                    Bulgu(
                        bu.kod.replace("ek6", "ek7"),
                        bu.seviye,
                        bu.mesaj,
                        bu.madde,
                        2,
                        bu.varliklar,
                        bu.sayi,
                    )
                    for bu in _oznitelik_kontrol(sinif, ref, g, varliklar)
                ]
            elif g["tur"] == "ozellik":
                out += [
                    Bulgu(
                        bu.kod.replace("ek6", "ek7"),
                        bu.seviye,
                        bu.mesaj,
                        bu.madde,
                        2,
                        bu.varliklar,
                        bu.sayi,
                    )
                    for bu in _ozellik_kontrol(sinif, ref, g, varliklar)
                ]
    if not any(bu.seviye == "hata" for bu in out):
        out.append(Bulgu("ek7", "bilgi", "Proje bilgileri (EK-7) tanımlı.", "m.13, EK-7", 2))
    return out
