# Katkı

Bir kural eklemek için önce dayanağı bul: yönetmeliğin maddesi ya da ekin tablosu ve sayfası. Dayanağı olmayan kural kabul edilmez; "sektörde böyle yapılır" dayanak değildir.

1. Veri: `src/ifc_ruhsat/ekler/*.json` — ilgili tabloyu Resmî Gazete ekinden okuyup sayfa numarasıyla ekle.
2. Kural: `src/ifc_ruhsat/kurallar/` altında `kontrol(baglam) -> list[Bulgu]`; her bulguda `madde` ve `ek9` dolu.
3. Test: `tests/ornek_model.py`'de iyi modele gerekliliği ekle, bozulmuş bir çeşidiyle kuralın yakaladığını göster.
4. `uv run pytest && uv run ruff check . && uv run ruff format .` yeşil; IDS değiştiyse `uv run ifc-ruhsat ids`.

Yönetmelik metnindeki bir çelişkiyi ya da yazım hatasını fark edersen KAYNAKLAR.md'deki listeye ekle; araç hangi yorumu uyguladığını orada söyler.
