"""Bir kontrolün sonucu. Her bulgu yönetmeliğin hangi maddesine dayandığını ve EK-9
formunun hangi satırına gittiğini taşır; varlıklar GlobalId ile verilir ki BIM
yazılımında bulunabilsin."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

Seviye = Literal["hata", "uyari", "bilgi", "elle"]


@dataclass(frozen=True)
class Bulgu:
    kod: str
    seviye: Seviye
    mesaj: str
    madde: str
    ek9: int | None = None
    varliklar: tuple[str, ...] = ()
    sayi: int | None = None

    def sozluk(self) -> dict:
        d = asdict(self)
        d["varliklar"] = list(self.varliklar)
        return d


@dataclass
class Rapor:
    dosya: str
    schema: str
    bulgular: list[Bulgu] = field(default_factory=list)

    def ekle(self, *b: Bulgu) -> None:
        self.bulgular.extend(b)

    def hatalar(self) -> list[Bulgu]:
        return [b for b in self.bulgular if b.seviye == "hata"]

    def uyarilar(self) -> list[Bulgu]:
        return [b for b in self.bulgular if b.seviye == "uyari"]

    def madde_bulgulari(self, ek9_no: int) -> list[Bulgu]:
        return [b for b in self.bulgular if b.ek9 == ek9_no]

    def ozet(self) -> dict[str, int]:
        return {
            "hata": len(self.hatalar()),
            "uyari": len(self.uyarilar()),
            "bilgi": len([b for b in self.bulgular if b.seviye == "bilgi"]),
            "elle": len([b for b in self.bulgular if b.seviye == "elle"]),
        }

    def sozluk(self) -> dict:
        return {
            "dosya": self.dosya,
            "schema": self.schema,
            "ozet": self.ozet(),
            "bulgular": [b.sozluk() for b in self.bulgular],
        }


def varlik_listesi(entities, sinir: int = 20) -> tuple[str, ...]:
    """GlobalId listesi; uzun listeler kırpılır, sayı ayrıca ``sayi`` alanında verilir."""
    return tuple(_kimlik(e) for e in list(entities)[:sinir])


def _kimlik(e) -> str:
    kimlik = getattr(e, "GlobalId", None)
    if kimlik:
        return str(kimlik)
    try:
        return f"#{e.id()}"
    except AttributeError:
        return str(e)
