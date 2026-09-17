from __future__ import annotations

import json

import ifcopenshell
import ifcopenshell.api.project
import ifcopenshell.api.pset
import ifcopenshell.api.root
import pytest
from ornek_model import iyi_model, kaydet

from ifc_ruhsat import ek9, veri
from ifc_ruhsat.cli import main
from ifc_ruhsat.kontrol import kontrol_et, ozet
from ifc_ruhsat.kurallar.isim import DOSYA_ADI, VARLIK_ADI


def kodlar(rapor, seviye=None):
    return {b.kod for b in rapor.bulgular if seviye is None or b.seviye == seviye}


def test_iyi_model_hatasiz(iyi_dosya):
    rapor = kontrol_et(iyi_dosya)
    assert rapor.schema == "IFC4X3"
    assert rapor.hatalar() == []
    assert rapor.uyarilar() == []
    kararlar = {r["no"]: r["karar"] for r in ek9.satirlar(rapor)}
    for no in (2, 3, 5, 6, 8, 9, 11, 12, 16, 18, 19):
        assert kararlar[no] == "Evet", no
    for no in (10, 15):
        assert kararlar[no] == "Kısmen (elle tamamlanacak)", no
    for no in (1, 7, 13, 14, 17, 21):
        assert kararlar[no] == "Elle", no


def test_kotu_model_bilinen_hatalari_yakalar(kotu_dosya):
    rapor = kontrol_et(kotu_dosya)
    hata = kodlar(rapor, "hata")
    assert {
        "sinif-proxy",
        "isim-bicim",
        "isim-kategori",
        "koordinat-epsg",
        "ek6-malzeme",
        "ek6-ozellik",
        "kat-bagi",
    } <= hata
    uyari = kodlar(rapor, "uyari")
    assert {"yinelenen-eleman", "on-tanimli-tip", "dosya-adi"} <= uyari
    # Duvarın kaldırılan Pset_WallCommon'ı iki ayrı özellik bulgusu üretir, ikisi de EK-9 m.9'a gider.
    duvar_bulgulari = [b for b in rapor.bulgular if b.kod == "ek6-ozellik" and "IfcWall" in b.mesaj]
    assert {b.ek9 for b in duvar_bulgulari} == {9}
    assert all(b.varliklar for b in duvar_bulgulari)
    kararlar = {r["no"]: r["karar"] for r in ek9.satirlar(rapor)}
    assert kararlar[5] == "Hayır" and kararlar[6] == "Hayır" and kararlar[9] == "Hayır"
    assert kararlar[15] == "Hayır" and kararlar[17] == "Hayır"
    assert kararlar[16] == "Evet (uyarıyla)"


def test_yanlis_sette_ozellik_ek9_madde_20(tmp_path):
    m = iyi_model()
    duvar = m.by_type("IfcWall")[0]
    pset = ifcopenshell.util.element.get_pset(duvar, "Pset_WallCommon")
    ifcopenshell.api.pset.remove_pset(m, product=duvar, pset=m.by_id(pset["id"]))
    p = ifcopenshell.api.pset.add_pset(m, product=duvar, name="Ofis_Ozel")
    ifcopenshell.api.pset.edit_pset(
        m, pset=p, properties={"IsExternal": True, "FireRating": "REI 60"}
    )
    rapor = kontrol_et(kaydet(m, tmp_path))
    yanlis = [b for b in rapor.bulgular if b.kod == "ek6-ozellik-set"]
    assert len(yanlis) == 2
    assert all(b.ek9 == 20 and "Ofis_Ozel" in b.mesaj for b in yanlis)


def test_emsal_kaks_asimi(tmp_path):
    m = iyi_model()
    zon = m.by_type("IfcSpatialZone")[0]
    qto = ifcopenshell.util.element.get_pset(zon, "Qto_SpatialZoneBaseQuantities")
    ifcopenshell.api.pset.edit_qto(m, qto=m.by_id(qto["id"]), properties={"GrossFloorArea": 1600.0})
    rapor = kontrol_et(kaydet(m, tmp_path))
    kaks = next(b for b in rapor.bulgular if b.kod == "emsal-kaks")
    assert kaks.seviye == "hata" and "aşıyor" in kaks.mesaj


def test_ifc4_dosya_surum_hatasi(tmp_path):
    m = ifcopenshell.api.project.create_file(version="IFC4")
    ifcopenshell.api.root.create_entity(m, ifc_class="IfcProject", name="123456")
    yol = kaydet(m, tmp_path, "eski.ifc")
    rapor = kontrol_et(yol)
    surum = next(b for b in rapor.bulgular if b.kod == "surum")
    assert surum.seviye == "hata" and "IFC4" in surum.mesaj
    assert "iskelet" in kodlar(rapor, "hata")


@pytest.mark.parametrize(
    "ad, uygun",
    [
        ("MM-DVR-dis_20cm", True),
        ("ST-KLN-k1", True),
        ("MM-DVR", True),
        ("MM-DVR-dis-20cm", False),  # açıklamada orta tire
        ("MM-DVR-dis 20cm", False),  # boşluk
        ("mm-DVR-dis", False),  # küçük harf disiplin
        ("MM_DVR_dis", False),  # alt tire ayırıcı
        ("Duvar 1", False),
    ],
)
def test_varlik_adi_sablonu(ad, uygun):
    assert bool(VARLIK_ADI.match(ad)) is uygun


@pytest.mark.parametrize(
    "ad, uygun",
    [
        ("123456_00_MM_GNEL_MD_BIM_000_01_000", True),
        ("123456_00_MM_GNEL_MD_BIM_000_01", False),
        ("123456-00-MM-GNEL-MD-BIM-000-01-000", False),
        ("kotu model", False),
    ],
)
def test_dosya_adi_sablonu(ad, uygun):
    assert bool(DOSYA_ADI.match(ad)) is uygun


def test_veri_dosyalari_tutarli():
    assert len(veri.zorunlu_siniflar()) == 69
    assert len(veri.istege_bagli_siniflar()) == 67
    assert set(veri.ek6_tablolar()) <= set(veri.zorunlu_siniflar())
    assert veri.kategori_kodlari()["DVR"] == "IfcWall"
    assert veri.ek2_disiplinler()["MM"] == "Mimari"
    assert len(veri.ek9_maddeler()) == 21
    for k in veri.kaynaklar().values():
        assert "33331" in k


def test_cli_json_ve_ek9(iyi_dosya, kotu_dosya, tmp_path, capsys):
    form = tmp_path / "ek9.md"
    assert main(["kontrol", str(kotu_dosya), "--json", "--ek9", str(form)]) == 1
    cikti = json.loads(capsys.readouterr().out)
    assert cikti["ozet"]["hata"] > 0
    assert all({"kod", "seviye", "mesaj", "madde"} <= set(b) for b in cikti["bulgular"])
    metin = form.read_text(encoding="utf-8")
    assert metin.count("\n| ") >= 21 + 5  # 21 satır + bölüm başlıkları
    assert "Hayır" in metin and "ek5_siniflar.json" in metin
    assert main(["kontrol", str(iyi_dosya)]) == 0
    assert "0 hata" in capsys.readouterr().out
    assert main(["kontrol", str(tmp_path / "yok.ifc")]) == 2


def test_ozet(iyi_dosya):
    o = ozet(iyi_dosya)
    assert o["schema"] == "IFC4X3" and o["proje"] == "123456"
    assert o["katlar"] == ["MM-BNK-zemin"] and o["mahalSayisi"] == 1
    assert o["sinifSayilari"]["IfcWall"] == 1
