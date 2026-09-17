# Changelog

Biçim [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), sürümleme [SemVer](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2026-09-17

EK-6'nın tamamı ve geometri kontrolleri.

### Added

- **EK-6:** kalan 45 tesisat/altyapı tablosu (6.2–6.65) nihai ekten okunup kodlandı; 68 zorunlu sınıfın tamamı denetleniyor. IfcSystem bağı ve katman (IfcPavement) kuralları. Her öznitelik/özellik adı IFC4X3 şeması ve resmî Pset şablonlarına karşı testle doğrulanıyor.
- **EK-3 / EK-9 m.4:** mahal numarası `Kat_Bölüm_SıraNo` (kat kodları EK-2 Tablo 2.14) ve mahal ismi (LongName) kontrolü.
- **EK-9 m.13–14:** mahallerin hacimli 3B gövdesi ve aynı kattaki mahallerin örtüşmesi (sınır kutusu, %10 eşik).
- **EK-9 m.15:** elemanların gövdesi bağlı olduğu katın kot aralığında mı (±1,5 m tolerans; 20.000 elemanın üstünde atlanır).
- IDS dosyaları 68 tabloyu kapsıyor.

### Fixed

- Mahallerin katı IfcRelAggregates üzerinden bulunuyor (önceden yalnızca IfcRelContainedInSpatialStructure).
- IfcGridAxis gibi GlobalId'siz varlıklar yinelenen kontrolünü düşürmüyor.

## [0.1.0] — 2026-09-17

İlk sürüm. Yönetmelik (RG 5.8.2026, 33331) eklerinden EK-2 Tablo 2.2, EK-5 Tablo 5.1–5.3, EK-6'nın 23 mimari tablosu, EK-7 Tablo 7.1–7.7 ve EK-9 Tablo 9.1 nihai metinden okunarak koda geçirildi.

### Added

- `ifc-ruhsat kontrol` — IFC sürümü, iskelet, EK-5 sınıf listesi ve vekil sınıf yasağı, isimlendirme, EK-6/EK-7 zorunlu öznitelik ve özellik setleri (TREpys_ dahil), TUREF koordinat sistemi, kata bağlılık, yinelenen varlıklar, emsal toplamları; her bulgu madde + EK-9 satırı + GlobalId ile. Hata varsa çıkış kodu 1.
- `ifc-ruhsat ek9` — EK-9 Model Kalite Kontrol Formu, Markdown; satır başına Evet / Hayır / Kısmen / Elle.
- `ifc-ruhsat ids` — EK-6 ve EK-7'nin buildingSMART IDS 1.0 karşılığı (`ids/`).
- `ifc-ruhsat mcp` — MCP sunucusu: `yonetmelik_kontrolu`, `ek9_formu`, `model_ozeti`, `ek5_siniflar`, `ek6_gerekenler`, `yonetmelik_bilgisi`.
- `ornekler/` — yönetmeliğe uyan ve bilerek bozulmuş iki IFC4X3 örnek model ve üretilen EK-9 formu.
