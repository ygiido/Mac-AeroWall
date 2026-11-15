# ✦ macOS 4K/8K Wallpaper Downloader & Plugin

Antigravity asistanı ve macOS için geliştirilmiş, dilediğiniz konu, kişi, estetik, sahne veya detay içeren metinlerden internetteki en kaliteli **4K / 5K / 8K** çözünürlüklü ve **macOS Retina (16:10), Standart (16:9) veya Geniş Ekran (21:9/32:9)** uyumlu duvar kağıtlarını otomatik bulan ve belirlediğiniz klasöre indiren hepsi-bir-arada eklenti ve CLI aracı.

---

## ✨ Özellikler

* **🌐 Hibrit Çoklu Kaynak Desteği:**
  * **Wallhaven API:** 4K/8K sanatsal, anime, cyberpunk, doğa ve soyut duvar kağıtları.
  * **Unsplash API:** Ultra-HD gerçekçi fotoğrafçılık, şehir manzaraları ve minimal kareler.
  * **Reddit:** `r/wallpapers`, `r/WQHD_Wallpaper`, `r/MultiWall`, `r/EarthPorn` gibi popüler topluluklar.
  * **Bing UHD Archive:** Günlük resmi 4K Ultra-HD doğa ve mimari arşivleri.

* **🧠 Akıllı Doğal Dil ve Türkçe Çözümleme (Smart Prompt Engine):**
  * Türkçe yazdığınız cümleleri (örn: *"yağmurlu bir tokyo gecesi neon ışıklar"* veya *"kara delik derin uzay"*) otomatik analiz eder.
  * Gereksiz dolgu kelimelerini ayıklar, estetik anahtar kelimelere ve arama terimlerine dönüştürür.
  * Metin içindeki *"8k"*, *"ultrawide"*, *"retina"* gibi istekleri otomatik filtre parametresine bağlar.

* **🖥️ macOS Ekran Formatlarıyla Tam Uyum:**
  * **16:10:** MacBook Pro / MacBook Air Retina ekranlar (2560x1600, 3024x1964, 3456x2234).
  * **16:9:** Harici 4K UHD (3840x2160) ve 8K (7680x4320) monitörler.
  * **21:9 & 32:9:** Ultrawide ve Super Ultrawide monitörler.

* **📁 Güvenli ve Düzenli İndirme:**
  * İndirilen görseller doğrudan `~/Pictures/Wallpapers` klasörüne (veya belirlediğiniz özel bir klasöre) düzenli isimlendirmeyle kaydedilir.
  * Daha önce indirilen aynı görseller tespit edilir, gereksiz kota/zaman harcanmaz.

* **⚡ Sıfır Harici Bağımlılık (Zero-Dependency):**
  * Tamamen Python standart kütüphaneleri (`urllib`, `ssl`, `json`) ile yazılmıştır; `pip install` ihtiyacı olmadan her Mac'te anında çalışır.

* **🔄 İki Yönlü Kullanım:**
  * **Antigravity Chat:** Asistanla konuşurken *"bana 8k uzay wallpaper'ı indir"* diyerek sohbet içinden çalıştırma.
  * **macOS Terminal CLI:** Terminalden `wallpaper "steve jobs minimalist"` şeklinde tek komutla çalıştırma.

---

## 🚀 Kurulum

Tek bir komutla kurulumu tamamlayabilirsiniz:

```bash
chmod +x install.sh
./install.sh
```

Bu işlem:
1. `~/Pictures/Wallpapers` klasörünü hazırlar.
2. `wallpaper` komutunu `~/.local/bin/wallpaper` altına bağlar.
3. Antigravity eklentisini `~/.gemini/config/plugins/macos-wallpaper` altına yükler.

> **İpucu:** Eğer `wallpaper` komutu terminalde tanınmıyorsa, `~/.zshrc` dosyanıza `export PATH="$HOME/.local/bin:$PATH"` ekleyin.

---

## 💻 Terminalden Kullanım Örnekleri

```bash
# 1. Temel Arama ve İndirme (Varsayılan 4K)
wallpaper "yağmurlu tokyo gecesi neon"

# 2. Tüm Resmi macOS Stock Duvar Kağıtlarını (6K) Senkronize Etme ve Güncelleme
wallpaper --macos-stock

# 3. 8K Çözünürlük ve Belirli Sayıda İndirme
wallpaper "steve jobs minimalist siyah beyaz" --res 8k -n 2

# 3. Ultrawide (21:9) Monitör İçin Arama
wallpaper "kara delik derin uzay" --ratio 21:9

# 4. MacBook Retina (16:10) Ekran Formatı
wallpaper "bmw m3 sonbahar dağ yolu" --ratio 16:10

# 5. İndirmeden Sadece Sonuçları Listeleme
wallpaper "cyberpunk 2077" --list

# 6. Özel Bir Klasöre İndirme
wallpaper "interstellar gargantua" --dir ~/Desktop/MyWallpapers

# 7. Varsayılan İndirme Klasörünü Kalıcı Olarak Değiştirme
wallpaper --set-dir ~/Downloads/Wallpapers
```

---

## 🤖 Antigravity İçinden Kullanım

Plugin yüklendikten sonra Antigravity sohbetinde doğrudan doğal dille isteğinizi söyleyebilirsiniz:

* *"Bana yağmurlu bir tokyo gecesi neon 4k wallpaper indir"*
* *"Steve Jobs minimalist siyah beyaz 8k masaüstü arka planı bul ve indir"*
* *"MacBook ekranıma uygun 3 adet lofi tarzı wallpaper indirir misin?"*

Antigravity aracı arka planda çalıştıracak, görselleri `~/Pictures/Wallpapers` klasörüne indirecek ve sohbette size tıklanabilir dosya bağlantıları sunacaktır.

---

## ⚙️ Komut Parametreleri

| Parametre | Kısa Yol | Açıklama | Varsayılan |
| :--- | :--- | :--- | :--- |
| `prompt` | - | Arama konusu, kişi, tema veya detaylı metin | - |
| `-n`, `--count` | `-n` | İndirilecek görsel adedi | `1` |
| `-r`, `--res` | `-r` | Minimum çözünürlük: `4k`, `5k`, `8k`, `retina` | `4k` (3840x2160) |
| `--ratio` | - | Ekran oranı: `16:9`, `16:10`, `21:9`, `32:9`, `all` | `all` |
| `-s`, `--source` | `-s` | Kaynak sağlayıcı: `all`, `wallhaven`, `unsplash`, `reddit`, `bing` | `all` |
| `-o`, `--dir` | `-o` | İndirilecek özel hedef klasör | `~/Pictures/Wallpapers` |
| `--list` | - | İndirmeden sadece bulunan görselleri listeler | `false` |
| `--json` | - | Çıktıyı JSON formatında döndürür | `false` |
| `--set-dir` | - | Varsayılan indirme klasörünü kalıcı günceller | - |

---

## 📂 Proje Yapısı

```text
wallpaper plugin/
├── .agents/
│   └── skills/
│       └── wallpaper/
│           └── SKILL.md            # Antigravity skill tanımı
├── bin/
│   └── wallpaper                   # Çalıştırılabilir CLI binary
├── wallpaper_engine/               # Çekirdek Python paketi
│   ├── __init__.py
│   ├── cli.py                      # CLI arayüzü ve argüman yönetimi
│   ├── config.py                   # Ayarlar ve klasör yönetimi
│   ├── downloader.py               # Akış indirme ve doğrulama motoru
│   ├── query_parser.py             # Türkçe & doğal dil analiz motoru
│   └── sources/                    # Duvar kağıdı sağlayıcıları
│       ├── __init__.py             # Çoklu kaynak birleştirici
│       ├── base.py                 # Temel kaynak arayüzü
│       ├── bing.py                 # Bing UHD sağlayıcısı
│       ├── reddit.py               # Reddit toplulukları sağlayıcısı
│       ├── unsplash.py             # Unsplash sağlayıcısı
│       └── wallhaven.py            # Wallhaven 4K/8K sağlayıcısı
├── install.sh                      # Tek tıkla kurulum betiği
├── plugin.json                     # Antigravity plugin manifestosu
└── README.md                       # Detaylı dokümantasyon
```
