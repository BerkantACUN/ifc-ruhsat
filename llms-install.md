# ifc-ruhsat — kurulum rehberi (Cline ve diğer yapay zekâ ajanları için)

Bu dosya, bir yapay zekâ ajanının (Cline vb.) ifc-ruhsat MCP sunucusunu kullanıcıya soru sormadan kurabilmesi için yazıldı. *This file lets an AI agent such as Cline install the ifc-ruhsat MCP server without asking the user anything; steps are below, in Turkish, with English notes.*

ifc-ruhsat, yapı ruhsatı IFC modellerini Türkiye'nin dijital proje yönetmeliğine (Resmî Gazete 5.8.2026, sayı 33331) göre denetler. Altı salt-okur araç sunar; API anahtarı, hesap ya da ortam değişkeni **gerekmez**, ağa hiçbir şey göndermez.

## 1. Ön koşul: uv

Sunucu PyPI'deki `ifc-ruhsat` paketinden `uvx` ile çalışır (Python 3.10+ ve IfcOpenShell'i uv kendisi getirir). `uvx --version` çalışmıyorsa uv'yi kurun:

- macOS / Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

Kurulumdan sonra yeni bir terminal açın ya da uv'nin yazdığı PATH talimatını uygulayın. uv kurulamıyorsa yedek yol: `pip install ifc-ruhsat` ve aşağıdaki yapılandırmada `"command": "ifc-ruhsat", "args": ["mcp"]`.

## 2. Paketi önceden indirin (isteğe bağlı ama önerilir)

İlk çalıştırmada IfcOpenShell (~40–50 MB) iner; MCP istemcisinin zaman aşımına düşmemesi için bir kez elle çalıştırın:

```bash
uvx ifc-ruhsat --version
```

Çıktı `ifc-ruhsat 0.x.y` olmalı.

## 3. MCP yapılandırması

Cline'ın `cline_mcp_settings.json` dosyasındaki `mcpServers` nesnesine ekleyin:

```json
{
  "mcpServers": {
    "ifc-ruhsat": {
      "command": "uvx",
      "args": ["ifc-ruhsat", "mcp"],
      "disabled": false,
      "autoApprove": [
        "model_ozeti",
        "yonetmelik_kontrolu",
        "ek9_formu",
        "ek5_siniflar",
        "ek6_gerekenler",
        "yonetmelik_bilgisi"
      ]
    }
  }
}
```

Bütün araçlar salt okurdur (dosya yazmaz, silmez, ağa çıkmaz); bu yüzden `autoApprove` güvenlidir. Kullanıcı istemezse listeyi boş bırakın.

Windows'ta `uvx` PATH'te bulunamazsa `"command"` alanına tam yolu yazın (ör. `C:\\Users\\<ad>\\.local\\bin\\uvx.exe`).

### Uzak sunucu (isteğe bağlı)

Kullanıcı kendi barındırdığı bir sunucu adresi verdiyse (bkz. README, "Uzak sunucu (Docker)"), yerel komut yerine:

```json
{
  "mcpServers": {
    "ifc-ruhsat": {
      "type": "streamableHttp",
      "url": "https://<sunucu>/mcp",
      "headers": { "X-API-Key": "<anahtar>" }
    }
  }
}
```

Uzak sunucuda `dosya` parametresi güvenlik gereği kapalıdır (verilirse `uzak-dosya-kapali` hatası döner): modeli `ifc_metni` (dosyanın metni) ve `dosya_adi` ile gönderin.

## 4. Doğrulama

Sunucu listede yeşil görünmeli ve altı araç sunmalı. Model gerektirmeyen bir araçla deneyin:

- `yonetmelik_bilgisi` → `{}` : yanıtta `"resmiGazete"` alanında `33331` geçmeli.
- `ek6_gerekenler` → `{"ifc_sinifi": "IfcWall"}` : yanıtta `"tablo": "6.66"` olmalı.

Kullanıcının bir IFC dosyası varsa: `yonetmelik_kontrolu` → `{"dosya": "<tam yol>.ifc"}`.

## Sorun giderme

| Belirti | Çözüm |
|---|---|
| `uvx: command not found` | 1. adım; ya da `command` alanına uvx'in tam yolu |
| İlk çağrıda zaman aşımı | 2. adımdaki `uvx ifc-ruhsat --version` ile paketi önceden indirin |
| `dosya yok: …` | `dosya` tam (mutlak) yol olmalı |
| `uzak-dosya-kapali` | Uzak sunucudasınız; modeli `ifc_metni` ile gönderin |
| Python sürüm hatası | uv kendi Python'unu indirir; `pip` yolu seçildiyse Python ≥ 3.10 gerekir |
