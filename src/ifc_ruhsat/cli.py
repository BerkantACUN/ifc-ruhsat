"""Komut satırı: `ifc-ruhsat kontrol model.ifc`, `ozet`, `ek9`, `ids`, `mcp`."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ifc_ruhsat import SURUM, YONETMELIK


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="ifc-ruhsat",
        description=(
            "Yapı ruhsatı IFC modelini yönetmeliğe göre kontrol eder "
            f"({YONETMELIK['ad']}, RG {YONETMELIK['resmiGazete']})."
        ),
    )
    p.add_argument("--version", action="version", version=f"ifc-ruhsat {SURUM}")
    alt = p.add_subparsers(dest="komut", required=True)

    k = alt.add_parser("kontrol", help="modeli denetle, bulguları yaz")
    k.add_argument("dosya")
    k.add_argument("--disiplin", default="MM", help="EK-2 disiplin kodu, varsayılan MM (mimari)")
    k.add_argument("--json", action="store_true", help="JSON çıktı")
    k.add_argument("--ek9", metavar="DOSYA.md", help="EK-9 formunu Markdown olarak buraya yaz")

    o = alt.add_parser("ozet", help="modelin kimliği: şema, yazılım, katlar, sınıf sayıları")
    o.add_argument("dosya")

    e = alt.add_parser("ek9", help="EK-9 formunu Markdown olarak yaz (stdout)")
    e.add_argument("dosya")
    e.add_argument("--disiplin", default="MM")

    i = alt.add_parser("ids", help="EK-6/EK-7'yi buildingSMART IDS dosyaları olarak üret")
    i.add_argument("--klasor", default="ids")

    alt.add_parser("mcp", help="MCP sunucusunu (stdio) başlat")

    a = p.parse_args(argv)
    if a.komut == "kontrol":
        return _kontrol(a)
    if a.komut == "ozet":
        from ifc_ruhsat.kontrol import ozet

        print(json.dumps(ozet(a.dosya), ensure_ascii=False, indent=2))
        return 0
    if a.komut == "ek9":
        from ifc_ruhsat import ek9
        from ifc_ruhsat.kontrol import kontrol_et

        print(ek9.markdown(kontrol_et(a.dosya, a.disiplin)))
        return 0
    if a.komut == "ids":
        from ifc_ruhsat.ids_uret import yaz

        for yol in yaz(Path(a.klasor)):
            print(yol)
        return 0
    if a.komut == "mcp":
        from ifc_ruhsat.mcp_server import calistir

        calistir()
        return 0
    return 2


def _kontrol(a: argparse.Namespace) -> int:
    from ifc_ruhsat import ek9
    from ifc_ruhsat.kontrol import kontrol_et

    try:
        rapor = kontrol_et(a.dosya, a.disiplin)
    except FileNotFoundError as hata:
        print(f"ifc-ruhsat: {hata}", file=sys.stderr)
        return 2
    if a.ek9:
        Path(a.ek9).write_text(ek9.markdown(rapor), encoding="utf-8", newline="\n")
    if a.json:
        print(json.dumps(rapor.sozluk(), ensure_ascii=False, indent=2))
    else:
        _yazdir(rapor)
    return 1 if rapor.hatalar() else 0


def _yazdir(rapor) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    o = rapor.ozet()
    print(f"{rapor.dosya} — {rapor.schema}")
    print(f"{o['hata']} hata, {o['uyari']} uyarı, {o['elle']} elle kontrol, {o['bilgi']} bilgi\n")
    for b in rapor.bulgular:
        if b.seviye == "bilgi":
            continue
        isaret = {"hata": "X", "uyari": "!", "elle": "?"}[b.seviye]
        ek = f" · EK-9 m.{b.ek9}" if b.ek9 and "EK-9" not in b.madde else ""
        print(f"{isaret} [{b.madde}{ek}] {b.mesaj}")
        if b.varliklar:
            kalan = (
                f" ... +{b.sayi - len(b.varliklar)}" if b.sayi and b.sayi > len(b.varliklar) else ""
            )
            print(
                f"    {', '.join(b.varliklar[:5])}{' ...' if len(b.varliklar) > 5 else ''}{kalan}"
            )


if __name__ == "__main__":
    sys.exit(main())
