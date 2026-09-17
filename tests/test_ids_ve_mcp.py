from __future__ import annotations

import asyncio

import ifcopenshell
from ifctester import ids as ids_mod

from ifc_ruhsat import ids_uret, mcp_server


def test_ids_dosyalari_uretilir_ve_geri_okunur(tmp_path):
    yollar = ids_uret.yaz(tmp_path)
    assert [y.name for y in yollar] == ["tr-ruhsat-ek6.ids", "tr-ruhsat-ek7.ids"]
    ek6 = ids_mod.open(str(yollar[0]))
    assert len(ek6.specifications) == 68
    duvar = next(s for s in ek6.specifications if "IfcWall" in s.name)
    assert any(getattr(r, "propertySet", None) == "Pset_WallCommon" for r in duvar.requirements)
    assert any(isinstance(r, ids_mod.Material) for r in duvar.requirements)


def test_ids_iyi_modeli_gecirir_kotuyu_gecirmez(iyi_dosya, kotu_dosya, tmp_path):
    ek6 = ids_uret.uret("EK-6")
    ek6.validate(ifcopenshell.open(str(iyi_dosya)))
    duvar = next(s for s in ek6.specifications if "IfcWall" in s.name)
    assert duvar.status is True
    ek6 = ids_uret.uret("EK-6")
    ek6.validate(ifcopenshell.open(str(kotu_dosya)))
    duvar = next(s for s in ek6.specifications if "IfcWall" in s.name)
    assert duvar.status is False


def test_mcp_araclari_listelenir_ve_calisir(iyi_dosya):
    araclar = asyncio.run(mcp_server.mcp.list_tools())
    adlar = {a.name for a in araclar}
    assert {
        "model_ozeti",
        "yonetmelik_kontrolu",
        "ek9_formu",
        "ek5_siniflar",
        "ek6_gerekenler",
        "yonetmelik_bilgisi",
    } <= adlar
    assert all(a.description and ("IFC" in a.description or "EK" in a.description) for a in araclar)
    sonuc = mcp_server.yonetmelik_kontrolu(str(iyi_dosya))
    assert sonuc["ozet"]["hata"] == 0
    assert mcp_server.ek6_gerekenler("ifcwall")["tablo"] == "6.66"
    assert mcp_server.ek6_gerekenler("IfcBoiler")["tablo"] == "6.4"
    assert "değil" in mcp_server.ek6_gerekenler("IfcSensor")["durum"]
    assert mcp_server.ek5_siniflar("duvar")["zorunlu"][0]["kod"] == "DVR"
    assert "33331" in mcp_server.yonetmelik_bilgisi()["resmiGazete"]
    assert mcp_server.ek9_formu(str(iyi_dosya)).startswith("# EK-9")
