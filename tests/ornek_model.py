"""Testler için sentetik IFC4X3 modeller: yönetmeliğe uyan küçük bir bina ("iyi") ve
bilinen hataları olan çeşitleri. Gerçek bir yazılımdan çıkmış dosya değil; her
gereklilik bilerek doldurulur ki bir kuralın neyi yakaladığı belli olsun."""

from __future__ import annotations

from pathlib import Path

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.georeference
import ifcopenshell.api.material
import ifcopenshell.api.owner
import ifcopenshell.api.project
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.util.element as ue


def _pset(m, e, ad, **ozellikler):
    p = ifcopenshell.api.pset.add_pset(m, product=e, name=ad)
    ifcopenshell.api.pset.edit_pset(m, pset=p, properties=ozellikler)
    return p


def _qto(m, e, ad, **nicelikler):
    q = ifcopenshell.api.pset.add_qto(m, product=e, name=ad)
    ifcopenshell.api.pset.edit_qto(m, qto=q, properties=nicelikler)
    return q


def _malzeme(m, e, ad):
    mat = ifcopenshell.api.material.add_material(m, name=ad)
    ifcopenshell.api.material.assign_material(m, products=[e], type="IfcMaterial", material=mat)
    return mat


def _yerlestir(m, e, x=0.0, y=0.0, z=0.0):
    matris = [[1.0, 0.0, 0.0, x], [0.0, 1.0, 0.0, y], [0.0, 0.0, 1.0, z], [0.0, 0.0, 0.0, 1.0]]
    ifcopenshell.api.geometry.edit_object_placement(m, product=e, matrix=matris)


def iyi_model() -> ifcopenshell.file:
    m = ifcopenshell.api.project.create_file(version="IFC4X3")
    proje = ifcopenshell.api.root.create_entity(m, ifc_class="IfcProject", name="123456")
    proje.Description = "Konut, 4 kat"
    ifcopenshell.api.unit.assign_unit(m)
    ifcopenshell.api.context.add_context(m, context_type="Model")
    _pset(m, proje, "Pset_ProjectCommon", ProjectType="Yeni yapı")

    # EK-7: kişi ve kuruluş
    kisi = ifcopenshell.api.owner.add_person(
        m, identification="12345", family_name="Yılmaz", given_name="Ayşe"
    )
    rol = m.createIfcActorRole("ARCHITECT")
    kisi.Roles = [rol]
    kurulus = ifcopenshell.api.owner.add_organisation(
        m, identification="1234567890", name="Örnek Mimarlık"
    )
    kurulus.Roles = [m.createIfcActorRole("ARCHITECT")]
    kurulus.Addresses = [m.createIfcPostalAddress(AddressLines=["Örnek Cad. 1"], Town="Ankara")]
    ifcopenshell.api.owner.add_person_and_organisation(m, person=kisi, organisation=kurulus)

    # EK-7 Tablo 7.6–7.7: koordinat sistemi
    ifcopenshell.api.georeference.add_georeferencing(m)
    ifcopenshell.api.georeference.edit_georeferencing(
        m,
        projected_crs={
            "Name": "EPSG:5256",
            "Description": "TUREF / TM33",
            "GeodeticDatum": "ITRF96",
            "VerticalDatum": "TUDKA99",
            "MapProjection": "Transverse Mercator",
            "MapZone": "33",
        },
        coordinate_operation={
            "Eastings": 500000.0,
            "Northings": 4400000.0,
            "OrthogonalHeight": 850.0,
            "Scale": 1.0,
        },
    )
    m.by_type("IfcProjectedCRS")[0].MapUnit = m.createIfcSIUnit(UnitType="LENGTHUNIT", Name="METRE")

    saha = ifcopenshell.api.root.create_entity(m, ifc_class="IfcSite", name="MM-SAH-parsel")
    saha.LongName = "Ada 100 Parsel 5"
    saha.ObjectType = "Parsel"
    saha.RefElevation = 850.0
    _pset(m, saha, "Pset_SiteCommon", FloorAreaRatio=1.5, SiteCoverageRatio=0.4, TotalArea=1000.0)
    _pset(
        m,
        saha,
        "Pset_Address",
        AddressLines="Örnek Mah. Örnek Sok.",
        Town="Ankara",
        Region="Çankaya",
    )
    _pset(m, saha, "Pset_LandRegistration", LandID="100/5", LandTitleID="T-0001")
    _pset(
        m,
        saha,
        "TREpys_ParselOzellikSeti",
        TAKS=0.4,
        KAKS=1.5,
        CekmeOn=5.0,
        CekmeYan=3.0,
        CekmeArka=3.0,
    )

    bina = ifcopenshell.api.root.create_entity(m, ifc_class="IfcBuilding", name="MM-BNA-A")
    bina.LongName = "A Blok"
    _pset(
        m,
        bina,
        "Pset_BuildingCommon",
        BuildingID="A",
        IsPermanentID=True,
        ConstructionMethod="Betonarme",
        FireProtectionClass="A",
        OccupancyType="Konut",
        GrossPlannedArea=1500.0,
        NetPlannedArea=1200.0,
        NumberOfStoreys=4,
    )
    _pset(
        m,
        bina,
        "Pset_Address",
        AddressLines="Örnek Mah. Örnek Sok. 1",
        Town="Ankara",
        Region="Çankaya",
        PostalBox="06000",
    )
    _qto(
        m,
        bina,
        "Qto_BuildingBaseQuantities",
        Height=13.0,
        EavesHeight=12.5,
        FootPrintArea=400.0,
        GrossFloorArea=1500.0,
        NetFloorArea=1200.0,
    )

    kat = ifcopenshell.api.root.create_entity(m, ifc_class="IfcBuildingStorey", name="MM-BNK-zemin")
    kat.Elevation = 0.0
    _qto(m, kat, "Qto_BuildingStoreyBaseQuantities", NetFloorArea=300.0)
    _pset(m, kat, "Pset_BuildingStoreyCommon", ElevationOfSSLRelative=0.0)

    ifcopenshell.api.aggregate.assign_object(m, relating_object=proje, products=[saha])
    ifcopenshell.api.aggregate.assign_object(m, relating_object=saha, products=[bina])
    ifcopenshell.api.aggregate.assign_object(m, relating_object=bina, products=[kat])

    duvar = ifcopenshell.api.root.create_entity(
        m, ifc_class="IfcWall", name="MM-DVR-dis_20cm", predefined_type="SOLIDWALL"
    )
    duvar.Tag = "D-01"
    _malzeme(m, duvar, "Beton_C25")
    _pset(m, duvar, "Pset_WallCommon", IsExternal=True, FireRating="REI 60")
    _yerlestir(m, duvar, 0.0, 0.0, 0.0)

    doseme = ifcopenshell.api.root.create_entity(
        m, ifc_class="IfcSlab", name="MM-DSM-zemin", predefined_type="FLOOR"
    )
    doseme.Tag = "S-01"
    _malzeme(m, doseme, "Beton_C25")
    _pset(m, doseme, "Pset_SlabCommon", IsExternal=False, FireRating="REI 60")
    _yerlestir(m, doseme, 0.0, 0.0, 0.0)

    kapi = ifcopenshell.api.root.create_entity(
        m, ifc_class="IfcDoor", name="MM-KAP-giris", predefined_type="DOOR"
    )
    kapi.Tag = "K-01"
    _pset(m, kapi, "Pset_DoorCommon", IsExternal=True, FireRating="EI 30", FireExit=True)
    _yerlestir(m, kapi, 2.0, 0.0, 0.0)

    mahal = ifcopenshell.api.root.create_entity(
        m, ifc_class="IfcSpace", name="Z01", predefined_type="INTERNAL"
    )
    mahal.LongName = "Salon"
    _pset(
        m,
        mahal,
        "Pset_SpaceCoveringRequirements",
        FloorCovering="Seramik",
        FloorCoveringThickness=0.01,
        WallCovering="Alçı sıva",
        WallCoveringThickness=0.02,
        CeilingCovering="Alçıpan",
        CeilingCoveringThickness=0.0125,
    )
    _yerlestir(m, mahal, 0.0, 0.0, 0.0)

    zon = ifcopenshell.api.root.create_entity(
        m, ifc_class="IfcSpatialZone", name="MM-MZN-emsal_dahil"
    )
    zon.LongName = "Emsale dahil alan"
    zon.Description = "Zemin kat konut alanı"
    _pset(m, zon, "TREpys_EmsalOzellikSeti", EmsalDurumu="DAHIL")
    _qto(m, zon, "Qto_SpatialZoneBaseQuantities", GrossFloorArea=300.0)

    ifcopenshell.api.aggregate.assign_object(m, relating_object=kat, products=[mahal])
    ifcopenshell.api.aggregate.assign_object(m, relating_object=bina, products=[zon])
    ifcopenshell.api.spatial.assign_container(
        m, relating_structure=kat, products=[duvar, doseme, kapi]
    )
    return m


def kaydet(
    m: ifcopenshell.file, klasor: Path, ad: str = "123456_00_MM_GNEL_MD_BIM_000_01_000.ifc"
) -> Path:
    yol = klasor / ad
    m.write(str(yol))
    return yol


def kotu_model() -> ifcopenshell.file:
    """İyi modelin bozulmuş hâli: vekil sınıf, adsız/şablonsuz varlıklar, eksik pset, yanlış EPSG,
    kata bağlı olmayan eleman, yinelenen eleman, NOTDEFINED tip."""
    m = iyi_model()
    kat = m.by_type("IfcBuildingStorey")[0]
    duvar = m.by_type("IfcWall")[0]
    duvar.Name = "Duvar 1"  # şablon dışı
    duvar.PredefinedType = "NOTDEFINED"
    pset_id = ue.get_pset(duvar, "Pset_WallCommon")["id"]
    ifcopenshell.api.pset.remove_pset(m, product=duvar, pset=m.by_id(pset_id))
    proxy = ifcopenshell.api.root.create_entity(
        m, ifc_class="IfcBuildingElementProxy", name="MM-XXX-bilinmez"
    )
    ifcopenshell.api.spatial.assign_container(m, relating_structure=kat, products=[proxy])
    kopya = ifcopenshell.api.root.create_entity(
        m, ifc_class="IfcDoor", name="MM-KAP-giris", predefined_type="DOOR"
    )
    kopya.Tag = "K-01"
    _pset(m, kopya, "Pset_DoorCommon", IsExternal=True, FireRating="EI 30", FireExit=True)
    _yerlestir(m, kopya, 2.0, 0.0, 0.0)  # aynı yer: yinelenen
    ifcopenshell.api.spatial.assign_container(m, relating_structure=kat, products=[kopya])
    serbest = ifcopenshell.api.root.create_entity(
        m, ifc_class="IfcColumn", name="ST-KLN-k1", predefined_type="COLUMN"
    )
    serbest.Tag = "C-01"  # kata bağlanmadı, malzemesi yok
    crs = m.by_type("IfcProjectedCRS")[0]
    crs.Name = "EPSG:3857"
    return m
