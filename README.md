# ifc-ruhsat

**Yapı ruhsatı IFC modelini yönetmeliğe göre kontrol eder.** Türkiye'de 1 Eylül 2027'de yürürlüğe giren *Mimarlık ve Mühendislik Projelerinin Dijital Olarak Hazırlanması Hakkında Yönetmelik* (Resmî Gazete 5.8.2026, sayı 33331) her ruhsat projesinin IFC modelini 241 sayfalık eklere uydurmayı ve her teslimde EK-9 Model Kalite Kontrol Formu düzenlemeyi zorunlu kılıyor. Bu araç o ekleri makine kuralına çevirir: modeli okur, eksikleri **madde numarasıyla** söyler, EK-9 formunu doldurur. Komut satırından ya da Claude / Cursor gibi istemcilerden (MCP) kullanılır; yazılımdan bağımsızdır — Revit, Archicad, Allplan, Bonsai, hepsi IFC verir.

> Otomatik **ön kontrol**dür. Yönetmeliğin bazı satırları (LOD, mahal geometrisi, PDF–IFC uyumu) makinece denetlenemez; araç bunları "elle" diye açıkça bırakır, uygun saymaz. Nihai değerlendirme proje müellifi ile ilgili idareye aittir; bu araç hukuki görüş değildir.

```
uvx ifc-ruhsat kontrol 123456_00_MM_GNEL_MD_BIM_000_01_000.ifc
```

```
ornekler\hatali_ornek.ifc — IFC4X3
10 hata, 3 uyarı, 8 elle kontrol, 7 bilgi

X [m.11, EK-5 5.5 ve Tablo 5.3 · EK-9 m.5] 1 varlığın adı şablona uymuyor. Beklenen: iki harf disiplin,
  üç harf kategori kodu ve açıklama, orta tire ile (örn. MM-DVR-dis_20cm) …
    3U9N2MO4vDDA4Hfy2J54b4
X [EK-7 Tablo 7.6 · EK-9 m.6] IfcProjectedCRS.Name 'EPSG:3857'; TUREF 3° dilimlerinden biri olmalı:
  EPSG:5253 … EPSG:5259.
X [EK-6 Tablo 6.66 · EK-9 m.9] IfcWall: Pset_WallCommon.FireRating (Yangın Dayanım Sınıfı) 1 varlıkta yok ya da boş.
    3U9N2MO4vDDA4Hfy2J54b4
X [EK-6 6.1.3 · EK-9 m.17] 1 varlık IfcProxy/IfcBuildingElementProxy ile modellenmiş; yönetmelik vekil sınıfa izin vermez …
? [EK-9 madde 7] Gelişim seviyesi (LOD 300) geometrinin ayrıntısına bakılarak elle değerlendirilir.
```

Tam örnek: [`ornekler/hatali_ornek.EK-9.md`](ornekler/hatali_ornek.EK-9.md) — 21 satırlık EK-9 formu, her satırda Evet / Hayır / Kısmen / Elle ve dayanağı.

## Kurulum

Python 3.10+ yeterli. [uv](https://docs.astral.sh/uv/) varsa kurulum gerekmez, `uvx ifc-ruhsat …` yeter. Kalıcı kurulum:

```
pip install ifc-ruhsat
```

## Komutlar

| Komut | Ne yapar |
|---|---|
| `ifc-ruhsat kontrol model.ifc` | Bütün kuralları çalıştırır; hata varsa çıkış kodu 1 (CI'da kullanılabilir). `--json` makine çıktısı, `--ek9 form.md` EK-9 formunu dosyaya yazar, `--disiplin ST` EK-2 disiplin kodu |
| `ifc-ruhsat ek9 model.ifc` | EK-9 Model Kalite Kontrol Formu (Tablo 9.1), Markdown |
| `ifc-ruhsat ozet model.ifc` | Şema, üreten yazılım, proje/saha/bina/katlar, sınıf sayıları |
| `ifc-ruhsat ids` | EK-6 ve EK-7'yi buildingSMART **IDS** dosyası olarak yazar ([`ids/`](ids/)) — Solibri, BIMcollab Zoom, usBIM.IDS, ifctester okur |
| `ifc-ruhsat mcp` | MCP sunucusu (stdio) |

## MCP ile kullanım

Claude Desktop, Claude Code, Cursor ve MCP konuşan her istemci:

```json
{
  "mcpServers": {
    "ifc-ruhsat": { "command": "uvx", "args": ["ifc-ruhsat", "mcp"] }
  }
}
```

Sonra asistanınıza sorun: *"C:\proje\A_blok.ifc yönetmeliğe uyuyor mu, EK-9 formunu çıkar"*, *"IfcSlab için hangi özellikler zorunlu?"*, *"Kolonlarda neden hata var, hangi maddeye göre?"*

| Araç | Ne yapar |
|---|---|
| `yonetmelik_kontrolu` | Modeli denetler; her bulgu seviye, madde, EK-9 satırı ve GlobalId listesiyle |
| `ek9_formu` | EK-9 formunu Markdown üretir |
| `model_ozeti` | Şema, yazılım, iskelet, sınıf sayıları |
| `ek5_siniflar` | Zorunlu / isteğe bağlı IFC sınıfları, Türkçe adları ve kategori kodları |
| `ek6_gerekenler` | Bir sınıf için zorunlu öznitelik ve özellik setleri (EK-6 / EK-7) |
| `yonetmelik_bilgisi` | Dayanak, kademeli takvim, veri kaynakları |

Sunucu yalnızca verilen dosyayı okur; ağa hiçbir şey göndermez, hiçbir şey yazmaz.

## Ne denetleniyor

| EK-9 satırı | Kontrol | Durum |
|---|---|---|
| 2 Proje bilgileri | IfcProject, IfcPerson, IfcOrganization, IfcPersonAndOrganization öznitelikleri (EK-7 Tablo 7.1–7.5) | otomatik |
| 3 Dosya/proje adı | EK-2 Tablo 2.1 dokuz alan; IfcProject.Name | otomatik (alt disiplin/dosya türü kodları listeyle karşılaştırılmıyor) |
| 4 Mahal no/ismi | IfcSpace.Name `Kat_Bölüm_SıraNo` (EK-3 Tablo 3.1, kat kodları EK-2 Tablo 2.14), LongName dolu | otomatik |
| 5 Varlık adları | `Disiplin-Kategori-Açıklama`; disiplin EK-2, kategori kodu EK-5 ve sınıfla uyumu | otomatik |
| 6 Koordinat | IfcProjectedCRS (EPSG:5253–5259, datum, zon, birim) + IfcMapConversion (EK-7 Tablo 7.6–7.7) | otomatik |
| 7 LOD 300 | — | **elle** |
| 8 / 17 Sınıflar | EK-5 zorunlu + isteğe bağlı liste; IfcProxy / IfcBuildingElementProxy yasak; üst sınıf yerine alt sınıf | otomatik + elle (anlam) |
| 9 / 20 Öznitelik ve özellikler | EK-6'nın **68 zorunlu sınıf tablosunun tamamı**: Name, Tag, malzeme (Ad_Dayanım), IfcSystem bağı, katman, Pset_/Qto_/TREpys_ özellikleri, veri tipi, izinli değerler; yanlış sette bulunan özellik ayrıca | otomatik |
| 10 Emsal | IfcSpatialZone alanları EmsalDurumu'na (DAHIL/HARIC/DIGER) göre toplanır, KAKS × parsel alanıyla karşılaştırılır | kısmen (pafta tablosuyla karşılaştırma elle) |
| 11 İskelet | Proje, Saha, Bina, ≥1 Kat; tek IfcProject | otomatik |
| 12 Mahal var mı | mimari disiplinde IfcSpace | otomatik |
| 13–14 Mahal geometrisi | her mahalin hacimli 3B gövdesi var; aynı kattaki mahallerin sınır kutuları %10'dan fazla örtüşmüyor | otomatik (kutu tabanlı, kaba) |
| 15 Kata bağlılık ve kot | her eleman bir kata bağlı; gövdesi katın kotu ile üst katın kotu arasında (±1,5 m) | otomatik |
| 16 Yinelenen | tekrar eden GlobalId; aynı sınıf+ad+yerleşim | otomatik |
| 18 IFC sürümü | IFC4X3, `.ifc` uzantısı | otomatik |
| 19 Ön Tanımlı Tip | boş / NOTDEFINED; USERDEFINED ise ObjectType | otomatik |
| 1, 21 | dosya boyutu sınırı yayımlanmadı; PDF–IFC uyumu | **elle** |

EK-6'nın 68 zorunlu sınıf tablosunun tamamı nihai Resmî Gazete ekinden sayfa sayfa okunup kodlandı; her öznitelik IFC 4.3 şemasına, her özellik buildingSMART'ın resmî Pset şablonlarına karşı testle doğrulanır. Hangi tablonun hangi sayfadan geldiği: [KAYNAKLAR.md](KAYNAKLAR.md). Geometri kontrolleri (mahal gövdesi, örtüşme, kot) sınır kutusu tabanlıdır — hızlı ve kaba; L biçimli mahallerde yanlış alarm verebilir, bunu bulgu metni de söyler.

## Yönetmelik ne diyor, kısaca

- Ruhsat eki projeler BIM tabanlı hazırlanır, **IFC 4.3** (TS EN ISO 16739-1) teslim edilir; 2B paftalar modelden üretilip PDF/A verilir (m.4, m.9).
- Varlıklar EK-5'teki sınıflarla, `Disiplin-KategoriKodu-Açıklama` adıyla modellenir (m.11, EK-5); vekil sınıf yasak (EK-6 6.1.3).
- Her sınıf için EK-6'daki öznitelik ve özellik setleri, projeler için EK-7 (Türkiye'ye özel `TREpys_` setleri dahil) doldurulur (m.12–13).
- Model LOD 300'dür (EK-8); her teslimde EK-9 formu düzenlenir (m.15).
- Takvim (Geçici m.1): yürürlük 1.9.2027; IFC teslimi 1.9.2029'dan itibaren büyükşehirlerdeki >10.000 m² projelerle başlar, 1.9.2032'de bütün binalar, 1.9.2033'te konut dışı.

Metin: [Resmî Gazete 20260805-2](https://www.resmigazete.gov.tr/eskiler/2026/08/20260805-2.htm) · Ekler (241 s.): [20260805-2-1.pdf](https://www.resmigazete.gov.tr/eskiler/2026/08/20260805-2-1.pdf)

## Kendi kurallarınız

Yönetmelik verisi `src/ifc_ruhsat/ekler/*.json` içinde, her dosya kaynağını kendi `kaynak` alanında söyler. Bir EK-6 tablosu eklemek: ilgili Resmî Gazete sayfasını okuyup `ek6_ozellikler.json`'a satırı ve sayfa numarasını yazın, testleri çalıştırın. Kural eklemek: `src/ifc_ruhsat/kurallar/` altına `kontrol(baglam) -> list[Bulgu]` imzasıyla bir modül, `kontrol.py`'daki `MODULLER`'e bir satır. Her bulgu bir maddeye ve bir EK-9 satırına bağlanmak zorundadır; dayanağı olmayan kural eklenmez.

```
uv sync && uv run pytest && uv run ruff check .
```

## English

**ifc-ruhsat** checks an IFC model against Türkiye's building-permit BIM regulation (Official Gazette 5 Aug 2026, no. 33331; in force 1 Sep 2027; IFC delivery phased in from Sep 2029). It encodes the regulation's annexes — mandatory IFC 4.3 classes and 3-letter category codes (Annex 5), per-class attribute and property-set requirements including the Turkish `TREpys_` sets (Annex 6), project/person/organisation and TUREF coordinate requirements (Annex 7) — and fills in the 21-row model quality-control form (Annex 9). Findings cite the article and annex table and list GlobalIds. Vendor-neutral (IfcOpenShell), usable as a CLI, as an MCP server for Claude/Cursor, and as buildingSMART IDS files for Solibri/BIMcollab/usBIM. It is an automated pre-check, not legal advice; rows that cannot be verified by machine are reported as manual, never as passed.

## Lisans

MIT. Yönetmelik metni ve ekleri kamu belgesidir; buradaki JSON dosyaları o eklerin makine biçimidir, hangi sayfadan alındığı her birinde yazılıdır.

<!-- MCP Registry doğrulaması için -->
mcp-name: io.github.BerkantACUN/ifc-ruhsat
