from __future__ import annotations

import asyncio
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

import pytest

from ifc_ruhsat import cli, mcp_server

ARACLAR = {
    "model_ozeti",
    "yonetmelik_kontrolu",
    "ek9_formu",
    "ek5_siniflar",
    "ek6_gerekenler",
    "yonetmelik_bilgisi",
}


def _istek(port: int, govde: dict, anahtar: str | None = None) -> tuple[int, str]:
    basliklar = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if anahtar is not None:
        basliklar["X-API-Key"] = anahtar
    r = urllib.request.Request(
        f"http://127.0.0.1:{port}/mcp",
        data=json.dumps(govde).encode(),
        headers=basliklar,
        method="POST",
    )
    try:
        with urllib.request.urlopen(r, timeout=60) as yanit:
            return yanit.status, yanit.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


BASLAT = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "0"},
    },
}


@pytest.fixture
def sunucu():
    acik = []

    def baslat(anahtar: str | None = None) -> int:
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        ortam = {k: v for k, v in os.environ.items() if not k.startswith("IFC_RUHSAT_")}
        ortam.update({"IFC_RUHSAT_HOST": "127.0.0.1", "IFC_RUHSAT_PORT": str(port)})
        if anahtar:
            ortam["IFC_RUHSAT_API_KEY"] = anahtar
        p = subprocess.Popen(
            [sys.executable, "-m", "ifc_ruhsat.cli", "mcp", "--http"],
            env=ortam,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        acik.append(p)
        son = time.monotonic() + 60
        while time.monotonic() < son:
            assert p.poll() is None, "sunucu erken kapandı"
            try:
                socket.create_connection(("127.0.0.1", port), timeout=0.5).close()
                return port
            except OSError:
                time.sleep(0.2)
        pytest.fail("sunucu zamanında açılmadı")

    yield baslat
    for p in acik:
        p.terminate()
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            p.kill()


def test_http_anahtarsiz_acik_ve_arac_calisir(sunucu, iyi_dosya):
    port = sunucu()
    durum, govde = _istek(port, BASLAT)
    assert durum == 200 and '"serverInfo"' in govde and "ifc-ruhsat" in govde
    cagri = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "model_ozeti",
            "arguments": {
                "ifc_metni": iyi_dosya.read_text(encoding="utf-8"),
                "dosya_adi": iyi_dosya.name,
            },
        },
    }
    durum, govde = _istek(port, cagri)
    assert durum == 200 and "IFC4X3" in govde and iyi_dosya.name in govde


def test_http_anahtar_zorunlu(sunucu):
    port = sunucu("gizli-anahtar")
    assert _istek(port, BASLAT)[0] == 401
    durum, govde = _istek(port, BASLAT, "yanlis")
    assert durum == 401 and json.loads(govde)["hata"] == "yetkisiz"
    durum, govde = _istek(port, BASLAT, "gizli-anahtar")
    assert durum == 200 and '"serverInfo"' in govde


def test_anahtar_kapisi_lifespan_gecirir():
    cagrilar = []

    async def uygulama(scope, receive, send):
        cagrilar.append(scope["type"])

    kapi = mcp_server._AnahtarKapisi(uygulama, "k")
    asyncio.run(kapi({"type": "lifespan"}, None, None))
    asyncio.run(kapi({"type": "http", "headers": [(b"x-api-key", b"k")]}, None, None))
    assert cagrilar == ["lifespan", "http"]


def test_http_varsayilanlari_ve_ortam(monkeypatch):
    import uvicorn

    goruldu = {}
    monkeypatch.setattr(
        mcp_server, "_UZAK_MOD", False
    )  # http_uygulamasi() açar; test sonrası geri al
    monkeypatch.setattr(uvicorn, "run", lambda uygulama, **kw: goruldu.update(kw, app=uygulama))
    for k in ("IFC_RUHSAT_HOST", "IFC_RUHSAT_PORT", "IFC_RUHSAT_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    assert cli.main(["mcp", "--http"]) == 0
    assert (goruldu["host"], goruldu["port"]) == ("0.0.0.0", 8080)
    assert not isinstance(goruldu["app"], mcp_server._AnahtarKapisi)

    monkeypatch.setenv("IFC_RUHSAT_HOST", "127.0.0.1")
    monkeypatch.setenv("IFC_RUHSAT_PORT", "9000")
    monkeypatch.setenv("IFC_RUHSAT_API_KEY", "k")
    assert cli.main(["mcp", "--http"]) == 0
    assert (goruldu["host"], goruldu["port"]) == ("127.0.0.1", 9000)
    assert isinstance(goruldu["app"], mcp_server._AnahtarKapisi)
    assert cli.main(["mcp", "--http", "--host", "::", "--port", "1234"]) == 0
    assert (goruldu["host"], goruldu["port"]) == ("::", 1234)


def test_arac_tanimlari_eksiksiz():
    araclar = asyncio.run(mcp_server.mcp.list_tools())
    assert {a.name for a in araclar} == ARACLAR
    for a in araclar:
        d = a.description
        assert len(d) > 400, a.name
        for bolum in ("Ne zaman:", "Dönüş (", "English:"):
            assert bolum in d, (a.name, bolum)
        assert "örne" in d.lower(), a.name  # girdi örneği
        assert a.title
        n = a.annotations.model_dump(by_alias=True)
        assert n["title"] and n["readOnlyHint"] is True and n["destructiveHint"] is False, a.name
        assert n["idempotentHint"] is True and n["openWorldHint"] is False, a.name
        sema = a.inputSchema if hasattr(a, "inputSchema") else a.input_schema
        for ad, ozellik in sema.get("properties", {}).items():
            assert ozellik.get("description") and ozellik.get("examples"), (a.name, ad)


def test_ifc_metni_ile_kontrol(iyi_dosya, kotu_dosya):
    metin = iyi_dosya.read_text(encoding="utf-8")
    ozet = mcp_server.model_ozeti(ifc_metni=metin, dosya_adi=iyi_dosya.name)
    assert ozet["dosya"] == iyi_dosya.name and ozet["schema"] == "IFC4X3"
    yoldan = mcp_server.yonetmelik_kontrolu(str(kotu_dosya))
    metinden = mcp_server.yonetmelik_kontrolu(
        ifc_metni=kotu_dosya.read_text(encoding="utf-8"), dosya_adi=kotu_dosya.name
    )
    assert metinden["dosya"] == kotu_dosya.name
    assert metinden["ozet"] == yoldan["ozet"]
    form = mcp_server.ek9_formu(ifc_metni=metin, dosya_adi="../../gizli/ad.ifc")
    assert form.startswith("# EK-9") and "`ad.ifc`" in form
    with pytest.raises(ValueError):
        mcp_server.model_ozeti()


def _arac_cagir(port: int, ad: str, argumanlar: dict) -> dict:
    durum, govde = _istek(
        port,
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": ad, "arguments": argumanlar},
        },
    )
    assert durum == 200, govde
    veri = next(s[5:] for s in govde.splitlines() if s.startswith("data:"))
    return json.loads(veri)["result"]


@pytest.mark.parametrize("arac", ["model_ozeti", "yonetmelik_kontrolu", "ek9_formu"])
def test_http_dosya_yolu_kapali(sunucu, iyi_dosya, arac):
    port = sunucu()
    # Sunucunun diskinde gerçekten var olan, okunabilir bir IFC dosyası: yine de okunmamalı
    sonuc = _arac_cagir(port, arac, {"dosya": str(iyi_dosya)})
    metin = json.dumps(sonuc, ensure_ascii=False)
    assert sonuc.get("isError") is True, metin
    assert "uzak-dosya-kapali" in metin and "ifc_metni kullanın" in metin
    assert "IFC4X3" not in metin and "EK-9" not in metin.split("uzak-dosya-kapali")[0]
    # ifc_metni ile birlikte verilse de yol kabul edilmez
    sonuc = _arac_cagir(
        port,
        arac,
        {"dosya": "/etc/passwd", "ifc_metni": iyi_dosya.read_text(encoding="utf-8")},
    )
    assert sonuc.get("isError") is True
    # ifc_metni tek başına çalışmaya devam eder
    sonuc = _arac_cagir(port, arac, {"ifc_metni": iyi_dosya.read_text(encoding="utf-8")})
    assert not sonuc.get("isError"), json.dumps(sonuc, ensure_ascii=False)[:500]


def test_uzak_modda_yol_reddi_ve_yerelde_yol(monkeypatch, iyi_dosya):
    assert mcp_server.model_ozeti(str(iyi_dosya))["schema"] == "IFC4X3"  # yerel (stdio)
    monkeypatch.setattr(mcp_server, "_UZAK_MOD", True)
    for cagri in (
        lambda: mcp_server.model_ozeti(str(iyi_dosya)),
        lambda: mcp_server.yonetmelik_kontrolu(str(iyi_dosya)),
        lambda: mcp_server.ek9_formu(dosya=str(iyi_dosya), ifc_metni="ISO-10303-21;"),
    ):
        with pytest.raises(mcp_server.UzakDosyaHatasi, match="Uzak modda dosya yolu kapalı"):
            cagri()
    metin = iyi_dosya.read_text(encoding="utf-8")
    assert mcp_server.model_ozeti(ifc_metni=metin)["schema"] == "IFC4X3"


def test_http_uygulamasi_uzak_modu_acar(monkeypatch):
    monkeypatch.setattr(mcp_server, "_UZAK_MOD", False)
    mcp_server.http_uygulamasi()
    assert mcp_server._UZAK_MOD is True
