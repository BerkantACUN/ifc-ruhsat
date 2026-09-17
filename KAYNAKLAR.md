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
| `ek6_ozellikler.json` | Tablo 6.1–6.68, **68 tablonun tamamı** (aşağıda) | tabloda | görsel, 2026-09-17; öznitelikler IFC4X3_ADD2 şemasına, özellikler resmî Pset şablonlarına karşı testle doğrulanır |
| `ek7_proje.json` | Tablo 7.1 IfcProject, 7.2 IfcPerson, 7.3 IfcPersonAndOrganization, 7.4 IfcOrganization, 7.5 IfcActorRole, 7.6 IfcProjectedCRS, 7.7 IfcMapConversion | ek s.222–230 | görsel, 2026-09-17 |
| `ek9_form.json` | Tablo 9.1 — 21 kontrol satırı (mimari) | ek s.238–239 | görsel, 2026-09-17 |

### EK-6: kodlanmış tablolar

68 zorunlu sınıfın tamamı: Tablo 6.1–6.68, ek sayfa 36–109; sıra Tablo 5.1 ile aynıdır (Tablo 6.n ↔ Tablo 5.1 satır n), her tablonun sayfası `ek6_ozellikler.json` içindeki `sayfa` alanındadır. İki turda okundu: 23 mimari tablo (6.1, 6.3, 6.7, 6.8, 6.16, 6.20, 6.21, 6.25, 6.34, 6.35, 6.40, 6.41, 6.48, 6.49, 6.52, 6.55, 6.56, 6.58, 6.60, 6.61, 6.66, 6.67, 6.68) ve kalan 45 tesisat/altyapı tablosu. Tesisat tablolarında Ön Tanımlı Tip listesi tablodan değil IFC4X3_ADD2 şemasından alınmıştır (EK-5 5.4 "IFC 4.3 esas alınarak" — liste aynıdır, yazım hataları hariç).

Tesisat tablolarının ortak deseni: PredefinedType, Name, Tag, `IfcRelAssignsToGroup>IfcSystem` bağı (sistem cihazlarında) ve sınıfa özel bir-iki Pset özelliği (ör. `Pset_FanTypeCommon.NominalAirFlowRate`, `Pset_ElectricalDeviceCommon.NominalPowerConsumption`). Köprü/yol/kazık gibi altyapı sınıflarında Tag yerine malzeme istenir.

### Kodlanmamış ekler

- **EK-1** proje kodu yapısı: IfcProject.Name yalnızca boş olmamasıyla denetlenir. **EK-3** mahal numarası şablonu (Tablo 3.1) ve kat kodları (Tablo 2.14) kodlandı; Tablo 3.2'deki mahal ismi kısaltmaları listesi (yaklaşık 150 ad, s.14–19) kodlanmadı — LongName yalnızca boş olmamasıyla denetlenir.
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
5. **IfcGroup için "Attribute: Tag"** (Tablo 6.37): IfcGroup'un IFC şemasında Tag özniteliği yoktur; araç yalnızca Name'i denetler.
6. **Ön Tanımlı Tip listelerinde yazım**: tablolarda "AIR COOLED", "BACKWARD INCLINED CURVED" gibi boşluklu yazımlar şemada "AIRCOOLED", "CENTRIFUGALBACKWARDINCLINEDCURVED" biçimindedir; araç şemayı esas alır.

## Yönetmelik listesinin gerçek modellerle sınandığı yerler

- **IfcPlate** (giydirme cephe panelleri, saclar) EK-5 Tablo 5.1 ve 5.2'de yok; Revit her giydirme cephe panelini IfcPlate olarak dışa aktarır (örnek Revit modelinde 44 adet). Araç bunu "listede yok" uyarısıyla bildirir; ilgili idare EK-2 2.5'teki gibi ek tanım yapana kadar çözüm IfcCurtainWall altında birleştirmek ya da idareyle teyittir.
- **IfcFlowTerminal / IfcSystem** gibi üst sınıflar: Revit, tipi belirsiz tesisat elemanlarını üst sınıfla dışa aktarır; yönetmelik alt sınıf ister (EK-6 6.1.2). Araç uygun alt sınıfları önerir.
- **IfcWallStandardCase, IfcSlabElementedCase** vb. IFC4 sınıfları IFC 4.3'te kaldırıldı; IFC4 dosyalarda "listede yok" olarak görünür, IFC 4.3 dışa aktarımıyla kendiliğinden düzelir.
- **Kat olmayan Revit seviyeleri** (tavan, çatı çizgisi) IfcBuildingStorey olarak çıkarsa kot kontrolü yanlış alarm verir; Revit'te o seviyelerde "Building Story" işareti kaldırılmalı.

## Doğrulama yöntemi ve sınırı

Ekler taranmış görüntü olduğundan tablolar OCR ile değil, sayfa görüntüsü okunarak elle geçirildi ve şemayla çapraz kontrol edildi (sınıf adları, enum değerleri). Bir yazım hatası gözden kaçmış olabilir; bulursanız sayfa numarasıyla issue açın. Ekler değişirse (Bakanlık düzeltme yayımlarsa) JSON'daki `kaynak` satırı ve bu dosya güncellenir.
