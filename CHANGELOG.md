# Changelog

Biçim [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), sürümleme [SemVer](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `ifc-ruhsat mcp --http`: MCP Python SDK'nın streamable HTTP taşımasıyla uzak sunucu (yol `/mcp`, durumsuz). Adres/port `--host`/`--port` ya da `IFC_RUHSAT_HOST`/`IFC_RUHSAT_PORT` (varsayılan `0.0.0.0:8080`); `IFC_RUHSAT_API_KEY` verilirse `X-API-Key` başlığı zorunlu.
- Model araçlarına `ifc_metni` ve `dosya_adi` parametreleri: uzak sunucuya model yol yerine metin olarak gönderilir. Uzak (HTTP) modda `dosya` kapalıdır: sunucu kendi diskinden yol okumaz, araç `uzak-dosya-kapali` hatası (isError) döner.
- Dockerfile (Python 3.12 slim, çok aşamalı, root olmayan kullanıcı, IfcOpenShell dahil) ve `ghcr.io/berkantacun/ifc-ruhsat` imajını `v*` etiketlerinde yayınlayan Docker iş akışı.
- `llms-install.md`: Cline gibi ajanların sunucuyu kendi başına kurması için adım adım rehber.

### Changed

- Araç açıklamaları yeniden yazıldı: ne yaptığı, ne zaman kullanılacağı, girdi örnekleri ve dönüş biçimi; her parametrenin şemada açıklaması ve örnekleri var. Bütün araçlara başlık ve eksiksiz ToolAnnotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`).

### Fixed

- Alt komut verilmeden çalıştırıldığında (stdin bir boruysa) doğrudan MCP sunucusu olarak başlar; bazı barındırıcılar paketi `ifc-ruhsat` diye çağırıyor. Terminalde davranış değişmedi.

## [0.2.1] — 2026-09-17

Halka açık gerçek modellerle (buildingSMART IFC 4.3 örneği, Revit 2021 konut, IfcOpenShell örnek evi) ilk tur; rapor okunurluğu ve hız.

### Changed

- Bir özellik seti varlıkta hiç yoksa özellik özellik değil set olarak tek bulgu (`ek6-set`); Revit modelinde 17 satır 3 satıra indi. Yanlış sette duran özellik yine ayrı bildirilir.
- Kot kontrolü (EK-9 m.15) gövde geometrisi yerine yerleşim kotuyla: 13 MB Revit modeli 64 s → 1,7 s. Revit'in kat olmayan seviyeleri için uyarı metni.
- Sahaya (IfcSite) bağlı elemanlar "kata bağlı değil" hatası yerine uyarı.
- Disiplin verilmezse EK-2 biçimindeki dosya adından okunur (üçüncü alan), yoksa MM.
- `--json` çıktısı Windows'ta da UTF-8.

### Added

- README: üç halka açık modelde sonuç tablosu. KAYNAKLAR: yönetmelik listesinde olmayan yaygın sınıflar (IfcPlate) ve Revit üst sınıf/seviye notları.

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
