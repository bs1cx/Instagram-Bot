# 🔍 Instagram Hunter Pro

**Instagram Profil Analiz ve Keşif Aracı**  
Python ile geliştirilen bu GUI uygulaması, Instagram'da detaylı profil analizi ve hedef kitle keşfi yapar.

## ✨ Temel Özellikler
- **Akıllı Arama:** Kullanıcı adı, bio, lokasyon ve takipçi sayısına göre filtreleme
- **Detaylı Analiz:**
  - Takipçi/takip oranları
  - Ortalama beğeni sayıları
  - Lokasyon bilgileri
- **Veri Görselleştirme:** Takipçi dağılım grafikleri
- **Excel Entegrasyonu:** Tüm verileri tek tıkla dışa aktarma

## 🛠 Teknik Detaylar
```python
# Örnek API Kullanımı
user_info = client.user_info(user_id)
print(f"@{user_info.username}: {user_info.follower_count} takipçi")
```
## 📦 Kurulum

Gereksinimler:

bash
pip install instagrapi pandas matplotlib tkinter

Çalıştırma:

bash
python acc_finder.py

## 🎯 Kullanım Senaryoları
Pazarlamacılar: Influencer araştırması

İçerik Üreticiler: Rekabet analizi

Kişisel Kullanım: Yeni hesaplar keşfetme

## ⚠️ Önemli Uyarılar

Instagram'ın API kullanım politikalarına dikkat edin

Dakikada 20'den fazla istek göndermeyin

Resmi Instagram API'ı için geliştirici izni almayı unutmayın

## 📊 Örnek Çıktı

Kullanıcı	Takipçi	Ort. Beğeni	Lokasyon

@dogukankardas	15.7k	1.2k	İstanbul
@techworld	89.3k	4.5k	San Francisco

## 🌟 Proje Geliştirme

Katkıda bulunmak için:

Repoyu fork edin

Yeni özellik ekleyin (Örn: Hashtag analizi)

Pull request açın

## 🔧 Gelişmiş Kurulum
Instagram API erişimi için:
1. [Instagram Geliştirici Portalı](https://developers.facebook.com/docs/instagram/)'na kaydolun
2. `config.json` dosyasına kimlik bilgilerinizi ekleyin

## 📦 Bağımlılıklar

graph TD
  A[Instagram Hunter] --> B[instagrapi]
  A --> C[pandas]
  A --> D[matplotlib]
   
