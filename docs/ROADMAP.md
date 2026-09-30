# Uygulama Yol Haritası — Adım Adım (themes_v1) — NİHAİ

Bu belge **ne yapacağını, hangi sırayla** yapacağını söyler. Tasarım detayları `docs/THEMES_SPEC.md`,
kurallar `CLAUDE.md`, parametreler `config/themes.yaml` içindedir.

Toplam süre: yarı zamanlı çalışmayla **8–10 hafta**. Her adımın sonunda "Bitti sayılır" koşulu sağlanmadan
sonrakine geçme. Kod bloklarındaki metinleri Claude Code'a olduğu gibi yapıştırabilirsin.

---

## Adım 0 — Hazırlık (yarım gün)

**Sen:**
1. Dosyaları repo'ya koy: `CLAUDE.md` (kök; varsa sonuna ekle), `config/themes.yaml`, `docs/THEMES_SPEC.md`, `docs/ROADMAP.md`.
2. Yeni dal aç: `git checkout -b themes-v1`
3. Mevcut testleri çalıştır; hepsi geçmeli.

**Claude Code:**
```
CLAUDE.md, docs/THEMES_SPEC.md, docs/ROADMAP.md ve config/themes.yaml dosyalarını oku. Kod yazma.
Tasarımı 10 maddede özetle; mevcut kodla çakışan yerleri (özellikle src/data, src/features,
src/portfolio/rebalance.py) ve açık soruları listele.
```

**Bitti sayılır:** Claude Code'un özeti doğru, açık sorular cevaplandı.

---

## Adım 1 — Sanayi dökümü (T0) — 1 gün

**Claude Code:**
```
THEMES_SPEC §10'daki T0 görevini yap. FMP'den NASDAQ ve NYSE ortak hisselerinin tüm benzersiz
sector/industry değerlerini, her birindeki firma sayısıyla dök. EDGAR SIC kodu dağılımını da çıkar.
Önce 3 örnek istekle alan adlarını doğrula. Çıktılar: research/themes/fmp_industries.csv ve sic_counts.csv.
```

**Bana gönder:** `fmp_industries.csv`. Birlikte `themes.yaml` içindeki `fmp_industries` listelerini kesinleştirir,
`# VERIFY` işaretlerini kaldırırız.

**Bitti sayılır:** `themes.yaml`'da `# VERIFY` kalmadı; yükleyici her sanayi adını FMP'de buluyor.

---

## Adım 2 — Evreni NYSE'ye genişlet (T1) — 2–3 gün

**Claude Code:**
```
T1 görevini yap: universe.exchanges parametresini ekle, NYSE delist kurtarmayı mevcut yöntemle yap,
include_foreign_filers bayrağını uygula. Fiyat geçmişini sadece aday havuzu (§3-A) için çek.
Mevcut testler geçmeli; borsa filtresi için yeni test yaz. Tema başına aday firma sayısı raporu üret.
```

**Kontrol et:** Tema başına aday sayıları makul mü? Tanıdığın büyük NYSE enerji ve otomasyon şirketleri aday
havuzunda mı? (Bu sadece veri kontrolü; üyelik kararı Adım 3'te 10-K'dan verilir.)

**Bitti sayılır:** Testler geçiyor, aday havuzu raporu var.

---

## Adım 3 — 10-K metinleriyle tema sınıflandırma (T2 + T3) — 1 hafta

**Claude Code (iki ayrı görev olarak ver):**
```
T2 görevini yap: aday havuzundaki firmaların 10-K belgelerini EDGAR'dan indir, Item 1 (Business)
bölümünü çıkar, önbellekle. Önce 10 örnek firmada Item 1 çıkarımını doğrula ve bana göster.
```
```
T3 görevini yap: anahtar kelime skorlarını hesapla, theme_membership tablosunu PIT geçerlilik
tarihleriyle kur, research/themes/membership_review.csv dosyasını üret (eşleşen kelimeler + 10-K'dan
1-2 cümle kanıt). Sızıntı testini yaz. Tema-tarih firma sayısı raporunu üret.
```

**Bitti sayılır:** Testler geçiyor; inceleme CSV'si hazır.

---

## Adım 4 — Sınıflandırma incelemesi (T3r) — senin işin, 2–3 saat

**Sen:** `membership_review.csv`'de güncel üyelerin her birini `correct / wrong` olarak işaretle. En az 100
firma incele; her alt temadan örnek olsun.

- İsabet **≥ %85** → devam.
- İsabet < %85 → anahtar kelimeleri ve eşikleri **bir kez** revize et, T3'ü tekrar çalıştır.

Henüz getiri sonucu görülmediği için bu revizyon serbesttir. Ön kayıt Adım 6'da yapılır.

**Bana gönder:** İsabet oranı ve yanlış sınıflanan örnekler. Eşikleri birlikte ayarlarız.

**Bitti sayılır:** İsabet ≥ %85.

---

## Adım 5 — Yeni faktörler (T4 + T4b) — 1 hafta

**Claude Code:**
```
T4 görevini yap: aşama bayrağı (pre_profit / profitable; biotech için clinical / commercial) ve
capex_at, fcf_margin, profitable_growth, net_debt_ebitda, oil_beta_trend faktörlerini THEMES_SPEC §5.2
tanımlarıyla ekle. Her faktör için sızıntı enjeksiyon testi ve birim testi yaz.
```
```
T4b görevini yap: FMP earnings ve emtia endpoint'lerinin Starter planda açık olup olmadığını ve
alan adlarını doğrula. 20 rastgele firma-çeyrekte FMP duyuru tarihini EDGAR 8-K Item 2.02
acceptanceDateTime ile karşılaştır. Uyuşma ≥ %90 ise ear_3d ve sue_announce'u ekle, değilse 8-K
tarihlerini kullan. Raporu göster.
```

**Bitti sayılır:** Tüm faktörler testli; T4b raporu var.

---

## Adım 6 — Ön kayıt + araştırma raporu (T5a + T5) — 1 hafta ⚠️ kritik adım

**Sen, çalıştırmadan önce:** `themes.yaml`'ı son kez gözden geçir. Bu noktadan sonra faktör setleri, ağırlıklar ve
eşikler sonuçlara bakılarak **değiştirilmez**.

**Claude Code:**
```
T5a görevini yap: Kenneth French veri kütüphanesinden FF3, FF5, MOM ve RF aylık serilerini indir,
önbellekle, ay sonuna hizala. beta_252d ve size_ln_mcap kontrollerini hesapla.
```
```
T5 görevini yap: önce config/themes.yaml'ı research/preregistration/themes_v1.yaml olarak kopyala,
SHA256'sını kaydet ve commit et. Sonra THEMES_SPEC §7.1–7.9'daki araştırma modülünü çalıştır ve
reports/themes/<run_id>/factor_explain.md raporunu üret. Tutarlılık testi olarak mom_12_1 sonuçlarını
mevcut docs/FACTOR_IC.md ile karşılaştır.
```

**Bana gönder:** `factor_explain.md`. Birlikte şunları ayırırız:
- Hangi faktör hangi temada §7.9 kuralına göre çalışıyor, hangisi gürültü?
- Hangi faktörler aynı şeyi ölçüyor (korelasyon > 0,7)?
- Ekonomik büyüklük anlamlı mı?

Çıkarılacak faktör olursa bu `themes_v2` + CHANGELOG demektir.

**Ders projesi bağlantısı:** EC 581 projesi "faktör modeli kur, skorla, backtest et, faktörlerin neden çalıştığını
açıkla" istiyor. Bu rapor (tanımlayıcı istatistikler, korelasyon matrisi, portföy sıralamaları, mimic portföyler,
Fama-MacBeth, IC, "neden çalışmalı" satırları) ve Adım 7'nin backtest'i projenin gövdesini oluşturur.

**Bitti sayılır:** Ön kayıt hash'i commit'te; rapor birlikte yorumlandı.

---

## Adım 7 — Tema portföyü backtest + ilk seçim listesi (T6) — 3–5 gün

**Claude Code:**
```
T6 görevini yap: themes_v1 (veya onaylanan themes_v2) ile tema portföyünün walk-forward backtest'ini
TEK sabit konfigürasyonla çalıştır. Her temanın eşit ağırlık endeksini, tema ETF'lerini, QQQ ve SPY'ı
benchmark al. Seçim katkısını (portföy − tema endeksi) alt dönemlerle raporla, THEMES_SPEC §8'deki
başarı ölçütü tablosunu doldur. Güncel ay için reports/themes/shortlist_<tarih>.md üret.
```

**Karar noktası:**
- **Başarı ölçütü geçti:** Faktör seçimi canlı kullanıma girer (Adım 8–9).
- **Geçmedi:** Faktör seçimi temayı geçemiyor demektir. Bu durumda tema içinde geniş, eşit ağırlıklı bir sepet
  tut (veya tema ETF'i), sadece nakit ömrü ve sulandırma gibi elemeleri koru; TA'yı yine zamanlama için kullan.
  Bu da dürüst ve geçerli bir sonuçtur.

**Bitti sayılır:** Başarı ölçütü tablosu dolu; karar verildi.

---

## Adım 8 — Teknik analiz katmanı (T7) — 3–4 gün

**Sen:** `research/ta/rules.yaml`'a kullanacağın **2–3 kuralı** yaz: giriş koşulu, çıkış/stop ve takip eden stop.
Parametreleri sen belirle; optimize edilmeyecek.

**Claude Code:**
```
T7 görevini yap: her interval_days günde bir shortlist hisseleri için gösterge tablosu üret; işlem
günlüğü şablonunu ve değerlendirme betiğini THEMES_SPEC §9'a göre yaz (taban oranla isabet
karşılaştırması, kâr faktörü, kâr/maks düşüş, ay başı girişine göre katkı). Örnek günlükle uçtan uca test et.
```

**Bitti sayılır:** TA tablosu tek komutla üretiliyor; değerlendirme betiği örnek günlükte çalışıyor.

---

## Adım 9 — Canlı döngü (sürekli)

| Ne zaman | Ne yapılır |
|---|---|
| Ayın ilk işlem günü | Seçim listesini üret (BUY/HOLD/WAIT/SELL) |
| Her 2–3 günde | TA tablosunu üret; al/sat kararlarını ver; **her işlemi günlüğe yaz** |
| Her ay sonu | Forward sonuçları kaydet (seçim katkısı, TA katkısı) |
| Her çeyrek | Forward raporu buraya gönder; birlikte bakarız |
| 6 ay sonra | İlk ciddi karar: TA taban oranı geçiyor mu, seçim katkısı pozitif mi? |
| Yılda bir | Tema ağırlıkları (senin kararın) ve gerekirse themes_v2 |

Gerçek parayla büyük pozisyona geçmeden önce en az 3 ay forward/paper sonucu gör; sonra küçük başla.

---

## Karar noktaları özeti

| Adım | Koşul | Geçerse | Geçmezse |
|---|---|---|---|
| 4 | Sınıflandırma isabeti ≥ %85 | Devam | Bir kez revize |
| 5 | FMP duyuru tarihleri ≥ %90 doğru | FMP earnings kullan | 8-K tarihleri kullan |
| 6 | Faktör §7.9 kuralını geçiyor | Sette kalır | themes_v2'de çıkar (gerekçeli) |
| 7 | Seçim katkısı ölçütü | Faktör seçimi canlıya | Geniş tema sepeti + eleme + TA |
| 9 | 6 ay forward, TA > taban oran | TA kuralları kalır | TA'yı sadece stop/risk için kullan |

## Beklenti

Bu sistemin amacı her yıl sabit bir getiri değil. Seçtiğin temaların içinde daha iyi hisseleri seçmek ve kötüleri
elemek hedefleniyor; gerçekçi katkı yılda birkaç puan. Getirinin seviyesini temaların kendisi belirler. Sistem,
hangi kısmın senin tema seçiminden, hangi kısmın faktörlerden, hangi kısmın TA'dan geldiğini ayrı ayrı gösterir.

## Adım 10 — Sonraki sürüm (themes_v2)

6 aylık forward sonuçlardan sonra, THEMES_SPEC §12'deki v2 adaylarından **birini** seç (öneri sırası: FINRA
açığa satış → Form 4 → kısmi işlem → ETF hedge). Her biri için: ön kayıt → ek bilgi testi → ablation →
sadece geçerse ekle. Aynı anda birden fazla değişiklik yapma.

