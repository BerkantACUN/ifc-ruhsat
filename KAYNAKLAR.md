# Kaynaklar ve doğrulama durumu

Bu araçtaki her kural yönetmeliğin bir maddesine ya da ekinin bir tablosuna dayanır. Aşağıda hangi verinin nereden, nasıl alındığı ve neyin henüz alınmadığı yazılıdır. Kural: **birincil metne bağlanamayan gereklilik eklenmez.**

## Birincil metin

| Belge | Yer | Not |
|---|---|---|
| Mimarlık ve Mühendislik Projelerinin Dijital Olarak Hazırlanması Hakkında Yönetmelik | [RG 5.8.2026 sayı 33331, 20260805-2.htm](https://www.resmigazete.gov.tr/eskiler/2026/08/20260805-2.htm) | Madde metinleri buradan. Yürürlük 1.9.2027 (m.16). |
| Yönetmeliğin ekleri (EK-1 … EK-9, 241 sayfa) | [20260805-2-1.pdf](https://www.resmigazete.gov.tr/eskiler/2026/08/20260805-2-1.pdf) | **Taranmış görüntü**, metin katmanı yok. Tablolar sayfa sayfa okunarak JSON'a geçirildi; her JSON dosyası ve her EK-6 tablosu sayfa numarasını taşır. |
| Mimarlık ve Mühendislik Projelerinin Elektronik Ortamda Teslimi ve Yönetilmesi Hakkında Yönetmelik (e-PYS) | [20260805-3.htm](https://www.resmigazete.gov.tr/eskiler/2026/08/20260805-3.htm) | Yürürlük 1.9.2028. Bu araç teslim sürecine değil, teslim edilecek modele bakar. |
| Bakanlık taslağı (Kasım 2025, metin katmanlı) | [csb.gov.tr, taslak dokümanlar](https://webdosya.csb.gov.tr/db/meslekihizmetler/icerikler/cal-stay-taslak-dokumanlar--20251107085546-20251110130354.pdf) | **Kullanılmadı.** Nihai metinden farklı (tablo numaraları, ayırıcılar, zorunlu/isteğe bağlı ayrımı). Yalnızca nihai ekler esas alındı. |

## Veri dosyaları (`src/ifc_ruhsat/ekler/`)

| Dosya | İçerik | Kaynak sayfa | Doğrulama |
|---|---|---|---|
| `ek2_disiplinler.json` | Tablo 2.2 — 12 disiplin kodu | ek s.3 | görsel, 2026-09-17 |
| `ek5_siniflar.json` | Tablo 5.1 — 69 zorunlu sınıf + kategori kodu; Tablo 5.2 — 67 isteğe bağlı; Tablo 5.3 isimlendirme şablonu | ek s.29–34 | görsel, 2026-09-17; sınıf adları IFC4X3_ADD2 şemasına karşı doğrulandı |
| `ek6_ozellikler.json` | Tablo 6.1–6.68'den **23 tablo** (aşağıda) | tabloda | görsel, 2026-09-17 |
| `ek7_proje.json` | Tablo 7.1 IfcProject, 7.2 IfcPerson, 7.3 IfcPersonAndOrganization, 7.4 IfcOrganization, 7.5 IfcActorRole, 7.6 IfcProjectedCRS, 7.7 IfcMapConversion | ek s.222–230 | görsel, 2026-09-17 |
| `ek9_form.json` | Tablo 9.1 — 21 kontrol satırı (mimari) | ek s.238–239 | görsel, 2026-09-17 |

### EK-6: kodlanmış tablolar

| Tablo | Sınıf | Sayfa | Tablo | Sınıf | Sayfa |
|---|---|---|---|---|---|
| 6.1 | IfcAirTerminal | 36 | 6.41 | IfcOpeningElement | 80 |
| 6.3 | IfcBeam | 38 | 6.48 | IfcRailing | 87 |
| 6.7 | IfcBuilding | 42–44 | 6.49 | IfcRamp | 88 |
| 6.8 | IfcBuildingStorey | 45 | 6.52 | IfcRoof | 91 |
| 6.16 | IfcColumn | 53–54 | 6.55 | IfcSite | 94–95 |
| 6.20 | IfcCovering | 58–59 | 6.56 | IfcSlab | 96 |
| 6.21 | IfcCurtainWall | 60 | 6.58 | IfcSpace | 98–99 |
| 6.25 | IfcDoor | 64 | 6.60 | IfcSpatialZone | 101 |
| 6.34 | IfcFooting | 73 | 6.61 | IfcStair | 102 |
| 6.35 | IfcFurniture | 74 | 6.66 | IfcWall | 107 |
| 6.40 | IfcMember | 79 | 6.67 | IfcWindow | 108 |
| | | | 6.68 | IfcZone | 109 |

### EK-6: henüz kodlanmamış zorunlu sınıflar (45)

Modelde bulunduklarında yalnızca `Name` denetlenir ve rapor bunu "ek6-kapsam" bulgusuyla söyler. Sayfa aralığı 37–106; sıra Tablo 5.1 ile aynıdır (Tablo 6.n ↔ Tablo 5.1 satır n).

IfcAudioVisualAppliance, IfcBoiler, IfcBridge, IfcBridgePart, IfcBurner, IfcCableCarrierFitting, IfcCableCarrierSegment, IfcCaissonFoundation, IfcChiller, IfcChimney, IfcCoil, IfcCommunicationsAppliance, IfcCondenser, IfcCoolingTower, IfcDamper, IfcDistributionBoard, IfcDistributionSystem, IfcDuctFitting, IfcDuctSegment, IfcDuctSilencer, IfcElectricAppliance, IfcElectricGenerator, IfcEvaporator, IfcFan, IfcFireSuppressionTerminal, IfcGridAxis, IfcGroup, IfcHeatExchanger, IfcLightFixture, IfcOutlet, IfcPavement, IfcPile, IfcPipeFitting, IfcPipeSegment, IfcPump, IfcRoad, IfcRoadPart, IfcSanitaryTerminal, IfcSign, IfcSolarDevice, IfcSpaceHeater, IfcTank, IfcTransformer, IfcTransportElement, IfcValve.

Katkı: ilgili sayfayı okuyup `ek6_ozellikler.json`'a tabloyu sayfa numarasıyla ekleyin; `tests/` içindeki şema tutarlılık testi sınıf ve enum adlarını denetler.

### Kodlanmamış ekler

- **EK-1** proje kodu yapısı ve **EK-3** mahal numaralama/isimlendirme: v0.1'de yok (EK-9 m.4 "elle").
- **EK-2** Tablo 2.3–2.14 (alt disiplin/öğe, dosya türü, dosya tipi, kat kodları): dosya adı yalnızca alan sayısı/uzunluğu ve disiplin koduyla denetlenir.
- **EK-4** CAD katman esasları: kapsam dışı (IFC değil).
- **EK-6** Tablo 6.69–6.135 (isteğe bağlı öznitelikler): idare istemedikçe zorunlu değil, kodlanmadı.
- **EK-7** Tablo 7.8 IfcGeometricRepresentationContext, 7.9 IfcAnnotation, 7.10–7.12 (isteğe bağlı): kodlanmadı.
- **EK-8** LOD 300: makinece denetlenemez.

## Metindeki tutarsızlıklar (araç ne yapıyor)

1. **Açıklama alanındaki ayırıcı.** m.11(2): "Açıklama alanında yer alacak bilgiler boşluk bırakılmaksızın orta tire '-' kullanılarak ayrılır." EK-5 5.5 ve 5.5.3: bilgi alanları orta tire ile ayrılır, açıklama içindeki alt bilgiler **alt tire** ile ayrılır, "açıklama kısmında orta tire kullanılmaz". Araç EK-5'i (özel ve ayrıntılı kural) uygular: `MM-DVR-dis_20cm` geçer, `MM-DVR-dis-20cm` geçmez.
2. **Ön Tanımlı Tip yazımları.** EK-6 tablolarında bazı tipler boşluklu yazılmış (SKIRTING BOARD, FILE CABINET, TECHNICAL CABINET); IFC 4.3 şemasındaki gerçek değerler SKIRTINGBOARD, FILECABINET, TECHNICALCABINET. Araç şemadaki değerleri kullanır.
3. **Özel özellik seti öneki.** EK-6 6.5 metninde "TREpys_" ile başlayan setler kullanıcı tarafından oluşturulur denir; Tablo 6.55 ve 6.60'ta setler `TREpys_ParselOzellikSeti` ve `TREpys_EmsalOzellikSeti` olarak geçer. Araç bu iki adı birebir kullanır.
4. **IfcOrganization.Identification** için EK-7 "Sayı" der (vergi no) ama IFC'de bu alan metindir; araç rakamlardan oluşan metni kabul eder.

## Doğrulama yöntemi ve sınırı

Ekler taranmış görüntü olduğundan tablolar OCR ile değil, sayfa görüntüsü okunarak elle geçirildi ve şemayla çapraz kontrol edildi (sınıf adları, enum değerleri). Bir yazım hatası gözden kaçmış olabilir; bulursanız sayfa numarasıyla issue açın. Ekler değişirse (Bakanlık düzeltme yayımlarsa) JSON'daki `kaynak` satırı ve bu dosya güncellenir.
