# @ya_da_psikoloji • İçerik Keşfi & Karosel Üretim Stüdyosu

Bu proje; 7.600+ bilimsel psikoloji makalesini yapay zeka ile analiz eden, Türkçe sosyal medya kurgularına (Instagram Karoselleri ve Reels senaryoları) dönüştüren ve tek tıkla 1080x1350 yüksek çözünürlüklü görseller üreten profesyonel bir içerik fabrikasıdır.

---

## ⚡ Hızlı Başlangıç (Herhangi Bir Bilgisayarda)

### 1. Gereksinimler
- **Python 3.10 veya üzeri** (Kurulum sırasında *"Add python.exe to PATH"* seçeneğini işaretleyin).
- İnternet bağlantısı ve Google Chrome veya Microsoft Edge tarayıcısı.
- Windows'ta `py` komutunun kullanılabilir olması gerekir. Python kurulumu sırasında Python Launcher seçili değilse `BASLAT.bat` çalışmaz.

### 2. Tek Tıkla Başlatma
Proje klasöründeki **`BASLAT.bat`** dosyasına çift tıklayın.
- Gerekli tüm kütüphaneler otomatik olarak kontrol edilir ve yüklenir.
- Projeye özel `.venv` sanal ortamı oluşturulur; sistemdeki Python paketleri değiştirilmez.
- İlk çalıştırmada Playwright Chromium tarayıcısı da kurulur.
- Web Stüdyosu varsayılan tarayıcınızda açılır: **http://localhost:8000**

> Başlatma sırasında `.env` dosyası yoksa `.env.example` üzerinden oluşturulur. Oluşan `.env` dosyasına kendi Gemini anahtarlarınızı ekleyin; bu dosya Git'e eklenmemelidir.

---

## 🔑 API Yapılandırması (`.env`)

Proje kök dizininde `.env` adında bir dosya oluşturun (veya `.env.example` dosyasını kopyalayın):

```env
# Gemini API Anahtarlarınızı virgülle ayırarak girin:
GEMINI_API_KEYS=AIzaSy...1,AIzaSy...2,AIzaSy...3
```
*Sistem birden fazla anahtar girildiğinde kota aşımını (15 RPM / 1500 RPD) önlemek için anahtarları otomatik olarak dönüştürür ve dinlendirir.*

---

## 🎨 Web Stüdyosu Özellikleri

1. **Keşfet (Discovery):**
   - Yapay zeka tarafından 100 üzerinden katı kriterlerle puanlanmış makaleler kart formatında akar.
   - Kart içi çoklu görünüm: **Özet & Kanca**, **Slayt Başlıkları (6)**, **Reels Senaryosu** ve **Orijinal Makale & Link**.
   - Dokunarak veya fareyle sürükleyerek: Sağa çekince **Havuza Ekle**, sola çekince **Pas Geç**.

2. **Havuz (Pool):**
   - Beğendiğiniz ve onayladığınız konular burada birikir.
   - Anlık arama ve kategori filtreleme ile konular taranabilir.
   - Tek tıkla stüdyoya aktarılır.

3. **Karosel & Reels Stüdyosu:**
   - **Canlı 4:5 Önizleme:** Instagram akışında nasıl görüneceğini gerçek zamanlı gösterir.
   - **Görsel Seçici & Karartma:** Konuya özel 4 alternatif telifsiz fotoğraf arasından seçim ve arka plan opaklık ayarı.
   - **Canlı Metin Düzenleme:** Başlık, gövde ve vurgu kutularını anında değiştirme.
   - **Reels Kurgusu:** 30-60 saniyelik konuşma metnini tek tıkla kopyalama.
   - **Hızlı Render (1.5 - 2 saniye):** 1080x1350 piksel baskı kalitesinde PNG çıktısı.
   - **İndirme & Klasör:** Tek tıkla **ZIP Olarak İndir** veya **Klasörü Aç**.

4. **Arşiv (Archive):**
   - Daha önce üretilmiş tüm karosellerin kapak önizlemeleri ve indirme bağlantıları.

5. **Süreç & Ayarlar:**
   - 11 motorlu arka plan analizini başlatma ve duraklatma.
   - Arşivi güncelleme ve yeni kaynaklardan (Simply Psychology, Psychology Today) makale çekme.

---

## 📁 Dizin Mimarisi

```text
├── BASLAT.bat                 # Tek tıkla sistemi başlatan dosya
├── launcher.py                # Konsol ve web başlatıcı motoru
├── requirements.txt           # Gerekli Python kütüphaneleri listesi
├── .env.example               # Örnek yapılandırma dosyası
├── web/                       # FastAPI web sunucusu ve Vue arayüzü
│   ├── server.py              # REST API ve dosya servisleri
│   └── templates/index.html   # Sezgisel, mobil uyumlu stüdyo arayüzü
├── analyzer/                  # Editoryal yapay zeka & render motoru
│   ├── carousel_renderer.py   # Playwright 1080x1350 yüksek çözünürlüklü render
│   ├── editorial_ai.py        # Gemini editoryal paket üreticisi
│   ├── batch_processor.py     # 11 anahtar rotasyonlu toplu analiz motoru
│   └── gemini_client.py       # Hız limitli akıllı API istemcisi
└── data/                      # Veri deposu
    ├── makaleler/             # 7.600+ İngilizce bilimsel makale
    ├── ai_catalog.json        # AI tarafından Türkçeleştirilmiş ve puanlanmış katalog
    ├── liked_articles.json    # Havuzdaki konular
    └── carousels/             # Üretilen 1080x1350 PNG ve caption paketleri
```

## GitHub'a Yükleme

`.env`, sanal ortam, ham makaleler ve üretilmiş dosyalar `.gitignore` ile otomatik olarak dışarıda bırakılır. Bu nedenle depoyu başka bir bilgisayara alan kişi:

1. Python 3.10+ kurar.
2. `.env.example` dosyasını `.env` olarak kopyalayıp Gemini anahtarını ekler.
3. `BASLAT.bat` dosyasını çalıştırır.

Ham makale arşivi veya mevcut karoseller paylaşılacaksa bunları Git'e koymak yerine ayrıca ZIP olarak iletin; GitHub tek dosyada 100 MB sınırına sahiptir.
