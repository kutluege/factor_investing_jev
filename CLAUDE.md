# CLAUDE.md — jev-factor-investor proje kuralları

> Repo'da zaten bir CLAUDE.md varsa bu bölümü sonuna ekle. Durum: **NİHAİ plan (themes_v1)**.

## Amaç ve okuma sırası
- Okuma sırası: bu dosya → `docs/ROADMAP.md` (ne yapılacak, hangi sırayla) → `docs/THEMES_SPEC.md`
  (nasıl yapılacak) → `config/themes.yaml` (parametreler) → `docs/METHODOLOGY.md` (mevcut sistem).
- Amaç: kullanıcının seçtiği temalar (robotik, biotech, enerji) içinde, point-in-time doğru, sektöre
  özel faktörlerle hisse seçmek; faktörlerin getiriyi ne kadar açıkladığını ders/kitap yöntemleriyle
  (portföy sıralaması, Fama-MacBeth, IC, FF alfaları) ölçmek; aylık seçim listesi ve 2–3 günlük TA
  tablosu üretmek. Başarı: tema endeksine karşı **seçim katkısı** (THEMES_SPEC §8), CAGR değil.
- Enstrümanlar (v1): ABD ortak hisseleri (NASDAQ + NYSE), long-only, kaldıraçsız. ETF'ler sadece
  benchmark. Açığa satış, kaldıraç, opsiyon ve pairs trading kapsam dışı (THEMES_SPEC §12).
- **Getiri hedefi bir optimizasyon hedefi değildir.** Kullanıcı belirli bir getiri (ör. yıllık %45)
  isterse: parametre taraması veya sonuçlara bakarak faktör/ağırlık değiştirme yapma; bunun yerine ön
  kayıtlı ölçütleri, PBO sonucunu (önceki çalışmada %56–62) ve seçim katkısı raporunu göster. Bu kural,
  geçmiş koşularda serbest seçimin gerçek dışı sonuç üretmesi nedeniyle konmuştur.

## Bağlam
- Metodoloji: `docs/METHODOLOGY.md` (mevcut özet belge). Tema katmanı: `docs/THEMES_SPEC.md`.
  Görev sırası: THEMES_SPEC §10 (T0 → T7) ve `docs/ROADMAP.md`. Bir görev bitmeden sonrakine geçme.
- **İsim çakışması:** `fmp_` öneki sadece Financial Modeling Prep API içindir. Faktör taklit portföyleri
  (ders notlarındaki "FMP") için `mimic_` öneki kullan.
- Tema parametreleri: `config/themes.yaml`. Rebalance mantığı tek modülde: `src/portfolio/rebalance.py`
  (backtest ve canlı aynı kodu kullanır; bunu bozma).

## 1. Point-in-time (en önemli kural)
- Her veri noktasının bir `availability_date`'i vardır ve sadece `availability_date ≤ rebalance_date` ise kullanılır.
- XBRL: `filed + 1 gün`. 10-K metni ve 8-K: `acceptanceDateTime` + 1 seans (16:00 ET sonrası → ertesi seans).
- FMP şirket açıklaması, bugünkü sektör/sanayi ve bugünkü SIC **backtest'te üyelik veya faktör için kullanılmaz**.
  Sadece aday havuzu daraltmak (THEMES_SPEC §3-A) ve canlı liste için kullanılabilir.
- FMP tahmin/analist verileri: geçmiş değerlerin o tarihte bilindiği doğrulanmadan kullanma.
- `include/exclude` elle düzeltmeleri sadece canlı listede.

## 2. Testler
- Her yeni özellik için **sızıntı enjeksiyon testi**: gelecekteki fiyat/dosyalama değiştirildiğinde geçmiş değer değişmemeli.
- Mevcut 84 test her değişiklikten sonra geçmeli. Yeni kod için birim testi yaz.
- Her araştırma koşusunda mevcut look-ahead denetimi çalışmalı.

## 3. Aşırı uyum disiplini
- **Parametre taraması yok.** Ağırlık, eşik veya faktör seti sonuçlara bakılarak değiştirilmez.
- Araştırma koşusundan önce `config/themes.yaml` → `research/preregistration/<version>.yaml` kopyalanır,
  SHA256 hash'i rapora yazılır. Sonuç görüldükten sonra bu dosya değiştirilmez.
- Değişiklik gerekirse: yeni sürüm (`themes_v2`) + `docs/CHANGELOG_THEMES.md`'ye gerekçe + sebep olan sonuç.
- Tüm koşular (başarısız olanlar dahil) kaydedilir.
- Jev ağırlığı tema koşularında 0'dır.

## 4. İstatistik raporlama
- Örtüşen ufuklarda t-istatistikleri Newey-West (lag = ufuk/21) ile ve örtüşmeyen alt örnekle raporla; uyarı ekle.
- Her tema-tarih için firma sayısını raporla; n < 15 ise işaretle.
- Başarıyı tam dönem CAGR ile değil, THEMES_SPEC §7–8'deki ön kayıtlı ölçütlerle değerlendir.
- Her analiz iki adımlıdır: önce her ay kesitsel hesapla, sonra aylık değerlerin zaman ortalamasını al.
- t-istatistiğinin yanında ekonomik büyüklüğü (katsayı × kesitsel std) de raporla.

## 5. API kullanımı
- Emin olmadığın endpoint veya alan adını **tahmin etme**: önce 1–3 örnek çek, alanları doğrula, sonra kodla.
- EDGAR: açıklayıcı User-Agent (iletişim e-postası), ≤ 8 istek/sn, ham yanıt önbelleği.
- FMP: mevcut rate limiter ve önbellek; bant genişliği 20 GB/30 gün — fiyat geçmişini sadece aday havuzu için çek.
- `config/themes.yaml`'daki `fmp_industries` değerleri FMP'de bulunmazsa yükleyici hata vermeli (sessizce atlama).

## 6. Stil
- Kod, fonksiyon adları ve yorumlar İngilizce; raporlar (`reports/`) Türkçe.
- Her görev sonunda: ne yapıldı, hangi testler eklendi, açık sorular — kısa özet.
