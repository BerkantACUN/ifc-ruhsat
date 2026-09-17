# EK-9 Model Kalite Kontrol Formu (Tablo 9.1, mimari disiplin)

**Model:** `ornekler\hatali_ornek.ifc` · **Şema:** IFC4X3 · **Tarih:** 17.09.2026 13:48  
**Dayanak:** Mimarlık ve Mühendislik Projelerinin Dijital Olarak Hazırlanması Hakkında Yönetmelik (RG 5.8.2026, sayı 33331)  
**Araç:** ifc-ruhsat 0.1.0 — otomatik ön kontrol; formun imzalanması ve nihai değerlendirme proje müellifi ile ilgili idareye aittir.  
**Özet:** 10 hata, 3 uyarı, 8 elle kontrol.

| No | Kategori | Kontrol Başlığı | Açıklama | Evet / Hayır | Bulgu |
|---|---|---|---|---|---|
| | **GENEL KONTROL** | | | | |
| 1 | Genel | Dosya Boyutu | Dosya boyutu, Bakanlıkça belirlenen kısıtlamalara uygun mu? | Elle | Bakanlığın dosya boyutu sınırı henüz yayımlanmadı; dosya 0.0 MB, karar idarenin. |
| 2 | Genel | Proje Bilgileri | Proje bilgileri Yönetmeliğin 13 üncü maddesinde belirtilen esaslara göre dolduruldu mu? | Evet | Proje bilgileri (EK-7) tanımlı. |
| | **İSİMLENDİRME** | | | | |
| 3 | Genel | Proje ve Dosya İsimlendirmesi | Proje ve dosya isimlendirmesi Yönetmeliğin 6 ncı maddesine uygun mu? | Evet (uyarıyla) | UYARI: Dosya adı 'hatali_ornek' EK-2 Tablo 2.1 şablonuna uymuyor: ProjeKodu(6)_BinaKodu(2)_Disiplin(2)_AltDisiplin(4)_DosyaTürü(2)_DosyaTipi(3)_KatKonum(3)_SıraNo(2)_RevizyonNo(3), örn. 123456_00_MM_GNEL_MD_BIM_000_01_000. |
| 4 | Mimari | Mahal No ve Mahal İsmi | Mahal numaraları ve mahal isimlendirmesi Yönetmeliğin 10 uncu maddesine uygun mu? | Elle | Mahal numarası ve mahal ismi (EK-3: kat, bölüm/fonksiyon, sıra no) bu sürümde denetlenmiyor; mahal listesinden kontrol edin. |
| 5 | Genel | Varlıklar | Varlıkların isimlendirmesi Yönetmeliğin 11 inci maddesine uygun mu? | Hayır | HATA: 1 varlığın adı şablona uymuyor. Beklenen: iki harf disiplin, üç harf kategori kodu ve açıklama, orta tire ile (örn. MM-DVR-dis_20cm); açıklama içinde alt tire kullanılır, orta tire ve boşluk kullanılmaz.<br>HATA: 1 varlıkta kategori kodu EK-5 Tablo 5.1/5.2'de yok. |
| | **MODEL YAPILANMASI** | | | | |
| 6 | Genel | Koordinat Sistemi | Model doğru koordinat sisteminde konumlandırıldı mı? Bu koordinat verileri Yönetmeliğin 13 üncü maddesinde verilen ilgili proje özniteliklerini kullanılarak atandı mı? | Hayır | HATA: IfcProjectedCRS.Name 'EPSG:3857'; TUREF 3° dilimlerinden biri olmalı: EPSG:5253, EPSG:5254, EPSG:5255, EPSG:5256, EPSG:5257, EPSG:5258, EPSG:5259. |
| 7 | Genel | Gelişim seviyesi | Modelde yer alan varlıklar Yönetmeliğin 14 üncü maddesinde verilen gelişim seviyesine uygun olarak modellendi mi? | Elle | Gelişim seviyesi (LOD 300) geometrinin ayrıntısına bakılarak elle değerlendirilir. |
| 8 | Genel | IFC Sınıfları | Modelde yer alan varlıklar Yönetmeliğin 12 inci maddesinde tanımlanan "Zorunlu IFC Sınıfları" listesindeki doğru sınıflar kullanılarak tanımlandı mı? | Elle |  |
| 9 | Genel | IFC Sınıfları | Yönetmeliğin 13 üncü maddesinde belirtilen projedeki mevcut "Zorunlu IFC Sınıfları" için zorunlu öznitelikler ve özellikler tanımlandı mı? | Hayır | HATA: IfcColumn: 1 varlığa malzeme atanmamış (IfcRelAssociatesMaterial).<br>HATA: IfcColumn: Pset_ColumnCommon.FireRating (Yangın Dayanım Sınıfı) 1 varlıkta yok ya da boş.<br>HATA: IfcColumn: Pset_ColumnCommon.LoadBearing (Taşıyıcı) 1 varlıkta yok ya da boş.<br>HATA: IfcWall: Pset_WallCommon.IsExternal (Dışarıda) 1 varlıkta yok ya da boş.<br>HATA: IfcWall: Pset_WallCommon.FireRating (Yangın Dayanım Sınıfı) 1 varlıkta yok ya da boş. |
| 10 | Genel | Emsal hesabı | Mahal (IfcSpace) ve Mekansal Zon (IfcSpatialZone) alanları emsal hesap tablolarıyla uyumlu mu? | Kısmen (elle tamamlanacak) | Emsal alanları — DAHIL: 300.00 m².<br>Emsale dahil alan 300.00 m²; KAKS 1.5 × parsel 1,000.00 m² = 1,500.00 m² sınırının içinde. |
| 11 | Genel | IFC Sınıfları | Modelde "Proje", "Saha", "Bina" ve en az bir "Bina Katı" ile ilgili IFC Sınıfları bulunuyor mu? | Evet | Proje, Saha, Bina ve 1 kat mevcut. |
| | **DİSİPLİN KONTROLLERİ** | | | | |
| 12 | Mimari | Mahal | Mimari modelde "Mahal" (IfcSpace) IFC Kategorisi yer alıyor mu? | Evet | 1 mahal (IfcSpace) tanımlı. |
| 13 | Mimari | Mahal | Mahaller diğer mahallerle örtüşmeyecek şekilde ve doğru katta modellendi mi? | Elle | Mahallerin örtüşmesi bu sürümde geometrik olarak denetlenmiyor (kat ataması denetleniyor). |
| 14 | Mimari | Mahal | Mahaller kapalı olarak ve üst sınırları doğru tanımlandı mı? | Elle | Mahallerin kapalı olması ve üst sınırı bu sürümde geometrik olarak denetlenmiyor. |
| 15 | Genel | Varlıklar | Varlıklar doğru katta veya doğru kotta modellendi mi? | Hayır | HATA: 1 yapı elemanı hiçbir bina katına bağlı değil (IfcRelContainedInSpatialStructure). Her eleman bir kata atanmalı. |
| 16 | Genel | Varlıklar | Modelden yinelenen varlıklar kaldırıldı mı? | Evet (uyarıyla) | UYARI: 1 yerde aynı sınıf, isim ve yerleşimle birden fazla eleman var; üst üste kopyalanmış olabilir. |
| | **TESLİM VE FORMAT** | | | | |
| 17 | Genel | IFC Sınıfları | Model IFC'ye uygun olarak oluşturuldu mu (IfcWall, IfcSlab, IfcWindow vb. sınıflar doğru atandı mı)? | Hayır | HATA: 1 varlık IfcProxy/IfcBuildingElementProxy ile modellenmiş; yönetmelik genel/vekil sınıfa izin vermez, her eleman gerçek IFC sınıfıyla temsil edilmeli. |
| 18 | Genel | IFC Versiyonu | Model dosyası, teslime ilişkin kısıtlamalarda tanımlanan IFC versiyonunda teslim edildi mi? Dosya uzantısı IFC mi? | Evet | Şema IFC4X3 — IFC 4.3. |
| 19 | Genel | Ön Tanımlı Tip | Varlıklar IFC'de doğru Ön Tanımlı Tip (Predefined Type) kullanılarak temsil edildi mi? | Evet (uyarıyla) | UYARI: 2 elemanda Ön Tanımlı Tip boş ya da NOTDEFINED; tipi seçin (IfcWall için SOLIDWALL/PARTITIONING…, IfcSlab için FLOOR/ROOF…). |
| 20 | Genel | Özellikler | Özellikler doğru P_set'ler altında listelendi mi? | Elle |  |
| 21 | Genel | PDF ve IFC uyumu | Teslim edilen PDF paftaları BIM modelinden üretildi mi? | Elle | PDF paftaların modelden üretildiği yalnızca teslim sürecinden anlaşılır. |

## Bulgu ayrıntısı

- **ELLE** [EK-9 madde 1]: Bakanlığın dosya boyutu sınırı henüz yayımlanmadı; dosya 0.0 MB, karar idarenin.
- **UYARI** [m.6, EK-2 Tablo 2.1] (EK-9 m.3): Dosya adı 'hatali_ornek' EK-2 Tablo 2.1 şablonuna uymuyor: ProjeKodu(6)_BinaKodu(2)_Disiplin(2)_AltDisiplin(4)_DosyaTürü(2)_DosyaTipi(3)_KatKonum(3)_SıraNo(2)_RevizyonNo(3), örn. 123456_00_MM_GNEL_MD_BIM_000_01_000.
- **ELLE** [m.10, EK-3] (EK-9 m.4): Mahal numarası ve mahal ismi (EK-3: kat, bölüm/fonksiyon, sıra no) bu sürümde denetlenmiyor; mahal listesinden kontrol edin.
- **HATA** [m.11, EK-5 5.5 ve Tablo 5.3] (EK-9 m.5): 1 varlığın adı şablona uymuyor. Beklenen: iki harf disiplin, üç harf kategori kodu ve açıklama, orta tire ile (örn. MM-DVR-dis_20cm); açıklama içinde alt tire kullanılır, orta tire ve boşluk kullanılmaz.
  - varlıklar: `3U9N2MO4vDDA4Hfy2J54b4`
- **HATA** [EK-5 Tablo 5.1–5.2] (EK-9 m.5): 1 varlıkta kategori kodu EK-5 Tablo 5.1/5.2'de yok.
  - varlıklar: `0SLvzPoqz5Y9IPBz79Q$N6`
- **HATA** [EK-7 Tablo 7.6] (EK-9 m.6): IfcProjectedCRS.Name 'EPSG:3857'; TUREF 3° dilimlerinden biri olmalı: EPSG:5253, EPSG:5254, EPSG:5255, EPSG:5256, EPSG:5257, EPSG:5258, EPSG:5259.
  - varlıklar: `20`
- **ELLE** [EK-9 madde 7]: Gelişim seviyesi (LOD 300) geometrinin ayrıntısına bakılarak elle değerlendirilir.
- **HATA** [EK-6 Tablo 6.16] (EK-9 m.9): IfcColumn: 1 varlığa malzeme atanmamış (IfcRelAssociatesMaterial).
  - varlıklar: `3w8TKxv_5FbO6qlPthxVLY`
- **HATA** [EK-6 Tablo 6.16] (EK-9 m.9): IfcColumn: Pset_ColumnCommon.FireRating (Yangın Dayanım Sınıfı) 1 varlıkta yok ya da boş.
  - varlıklar: `3w8TKxv_5FbO6qlPthxVLY`
- **HATA** [EK-6 Tablo 6.16] (EK-9 m.9): IfcColumn: Pset_ColumnCommon.LoadBearing (Taşıyıcı) 1 varlıkta yok ya da boş.
  - varlıklar: `3w8TKxv_5FbO6qlPthxVLY`
- **HATA** [EK-6 Tablo 6.66] (EK-9 m.9): IfcWall: Pset_WallCommon.IsExternal (Dışarıda) 1 varlıkta yok ya da boş.
  - varlıklar: `3U9N2MO4vDDA4Hfy2J54b4`
- **HATA** [EK-6 Tablo 6.66] (EK-9 m.9): IfcWall: Pset_WallCommon.FireRating (Yangın Dayanım Sınıfı) 1 varlıkta yok ya da boş.
  - varlıklar: `3U9N2MO4vDDA4Hfy2J54b4`
- **ELLE** [EK-9 madde 10]: Hesaplanan toplamlar projedeki emsal hesap tablosuyla (pafta) karşılaştırılmalı.
- **ELLE** [EK-9 madde 13]: Mahallerin örtüşmesi bu sürümde geometrik olarak denetlenmiyor (kat ataması denetleniyor).
- **ELLE** [EK-9 madde 14]: Mahallerin kapalı olması ve üst sınırı bu sürümde geometrik olarak denetlenmiyor.
- **HATA** [EK-9 madde 15]: 1 yapı elemanı hiçbir bina katına bağlı değil (IfcRelContainedInSpatialStructure). Her eleman bir kata atanmalı.
  - varlıklar: `3w8TKxv_5FbO6qlPthxVLY`
- **UYARI** [EK-9 madde 16]: 1 yerde aynı sınıf, isim ve yerleşimle birden fazla eleman var; üst üste kopyalanmış olabilir.
  - varlıklar: `1lVYUINYTEou$R3v2bI54X`, `1Tr7aMYGv6V8pOapYErJHj`
- **HATA** [EK-6 6.1.3] (EK-9 m.17): 1 varlık IfcProxy/IfcBuildingElementProxy ile modellenmiş; yönetmelik genel/vekil sınıfa izin vermez, her eleman gerçek IFC sınıfıyla temsil edilmeli.
  - varlıklar: `0SLvzPoqz5Y9IPBz79Q$N6`
- **ELLE** [EK-9 madde 17]: Sınıfın doğru seçilip seçilmediği (bir döşemenin IfcSlab, duvarın IfcWall olması) geometriden anlaşılmaz; model görünümünde göz kontrolü gerekir.
- **UYARI** [EK-9 madde 19, EK-6]: 2 elemanda Ön Tanımlı Tip boş ya da NOTDEFINED; tipi seçin (IfcWall için SOLIDWALL/PARTITIONING…, IfcSlab için FLOOR/ROOF…).
  - varlıklar: `0SLvzPoqz5Y9IPBz79Q$N6`, `3U9N2MO4vDDA4Hfy2J54b4`
- **ELLE** [EK-9 madde 21]: PDF paftaların modelden üretildiği yalnızca teslim sürecinden anlaşılır.

## Veri kaynakları

- `ek2_disiplinler.json`: RG 5.8.2026 sayı 33331, ek EK-2 Tablo 2.2 (s.3), görsel doğrulama 2026-09-17
- `ek5_siniflar.json`: RG 5.8.2026 sayı 33331, ek EK-5 Tablo 5.1 (zorunlu, s.29–31) ve Tablo 5.2 (isteğe bağlı, s.31–33); IFC 4.3 (EK-5 5.4); görsel doğrulama 2026-09-17
- `ek6_ozellikler.json`: RG 5.8.2026 sayı 33331, ek EK-6 Tablo 6.1–6.68 (zorunlu sınıflar); listelenen tablolar nihai metnin sayfalarından görsel olarak doğrulandı (2026-09-17). Doğrulanmamış zorunlu sınıflar için yalnızca Name aranır (KAYNAKLAR.md).
- `ek7_proje.json`: RG 5.8.2026 sayı 33331, ek EK-7 Tablo 7.1–7.7 (s.221–230), görsel doğrulama 2026-09-17
- `ek9_form.json`: RG 5.8.2026 sayı 33331, ek EK-9 Tablo 9.1 Model Kalite Kontrol Formu (mimari disiplin), s.238–239, görsel doğrulama 2026-09-17
