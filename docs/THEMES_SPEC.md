# Tema Bazlı Faktör Sistemi — Tasarım ve Görev Listesi (themes_v1)

Bu belge, mevcut `jev-factor-investor` sistemine eklenecek **tema katmanını** tanımlar:
robotik, biotech ve enerji temaları; tema bazlı faktör setleri; faktörlerin getiriyi ne kadar
açıkladığını ölçen araştırma modülü; aylık seçim listesi ve teknik analiz günlüğü.
Tüm parametreler `config/themes.yaml` içindedir. Proje kuralları `CLAUDE.md` içindedir.
Uygulama sırası ve hazır Claude Code komutları: `docs/ROADMAP.md`.

**Terim notu (isim çakışması):** Ders notlarında "FMP" = *Factor Mimicking Portfolio*
(faktör taklit portföyü). Bu projede "FMP" = *Financial Modeling Prep* API. Karışıklığı önlemek için:
kodda `fmp_` öneki **sadece API** için kullanılır; faktör taklit portföyleri `mimic_` önekiyle
adlandırılır ve belgelerde **"mimic portföy"** denir.

**Durum:** NİHAİ (2026-09-30). **Sürüm:** themes_v1.1 — ders notlarındaki (EC 581, Bali–Engle–Murray *Empirical Asset Pricing*)
analiz yöntemleri §7'ye ve TA değerlendirmesi §9'a eklendi.

---

## 1. Amaç ve ayrım

Getiri iki karardan gelir; sistem bunları **ayrı ayrı** ölçer:

1. **Tema seçimi** (kullanıcının kararı): hangi temada, hangi ağırlıkla. Getirinin seviyesini belirler.
2. **Tema içi hisse seçimi** (faktörlerin işi): temanın içinden daha iyileri seçmek.

Bu yüzden her tema için bir **tema eşit ağırlık endeksi** (tüm tema üyeleri, aylık, maliyetsiz)
benchmark olarak hesaplanır. Portföy getirisi = tema getirisi + seçim katkısı. Faktörler ancak
tema endeksini geçiyorsa işe yarıyor demektir.

---

## 2. Evren

- NASDAQ + NYSE ortak hisseler (NYSE American, ADR ve 20-F/40-F dosyalayan yabancılar hariç — parametre).
- Mevcut filtreler: traded fiyat ≥ $3, piyasa değeri ≥ $300M, ADV20 ≥ $5M, ≥ 252 seans geçmiş.
- NYSE delist kurtarma: mevcut yöntemle aynı (FMP tam liste − aktif liste → profil → borsa filtresi).
- **FMP bant genişliği:** fiyat geçmişi sadece tema aday evreni (bkz. §3 aşama A) için çekilir.

---

## 3. Tema sınıflandırma (PIT)

Üç aşama:

**A. Kaba filtre (aday havuzu).** FMP sanayi adı `fmp_industries` içinde **veya** EDGAR SIC kodu
`sic` içinde olan firmalar. Bu aşama sadece hangi firmaların 10-K metninin indirileceğini belirler;
**üyelik kararı vermez.** Filtre bilerek geniş tutulur, çünkü FMP sanayi ve EDGAR SIC bugünkü
değerlerdir (PIT değil).

**B. 10-K metin skoru (üyelik kararı, PIT).**
- Kaynak: `https://data.sec.gov/submissions/CIK##########.json` → `filings.recent` (ve eski yıllar için
  `filings.files`) içinden form ∈ {10-K, 10-K405, 10-KT}; `accessionNumber`, `acceptanceDateTime`,
  `primaryDocument`. Belge: `https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no_dashes}/{primaryDocument}`.
  *Alan adlarını önce birkaç örnek CIK ile doğrula.*
- Metin: HTML → düz metin; **Item 1 (Business)** bölümü, "Item 1A" (yoksa "Item 2") başlığına kadar.
  İçindekiler tablosundaki kopya başlıkları atlamak için en uzun eşleşen bölüm alınır.
- Skor: her alt tema için anahtar kelime eşleşme sayısı (büyük/küçük harf duyarsız, alt dize).
  Üyelik: `hits ≥ min_hits`. Anahtar kelimesi boş alt temalarda aşama A yeterlidir.
- Geçerlilik: `acceptanceDateTime` + 1 seans (16:00 ET sonrası ise ertesi seans) → bir sonraki 10-K'ya
  kadar, en fazla 18 ay.
- Birden çok alt temaya uyan firma: en yüksek eşleşme yoğunluğu (hits / 10.000 kelime) → birincil alt tema.
  Tema çakışmasında `theme_tie_priority`.
- Çıktı tablosu: `theme_membership(cik, symbol, theme, subtheme, valid_from, valid_to, hits, density, filing_accession, method)`.

**C. İnceleme ve elle düzeltme.** `research/themes/membership_review.csv`: bugünkü üyeler + her biri için
eşleşen kelimeler ve 10-K'dan 1–2 cümlelik kanıt. Kullanıcı `correct / wrong` işaretler.
`include/exclude` **sadece canlı listede** uygulanır, backtest'te asla.

**Kalite ölçütü (ön kayıtlı):** kullanıcının incelediği güncel üyelerde isabet ≥ %85. Altındaysa
anahtar kelimeler/eşikler bir kez revize edilir → `themes_v2` + CHANGELOG.

---

## 4. Aşama (stage) ayrımı

Her firma-tarih için, PIT XBRL verisiyle:

- `pre_profit`: TTM faaliyet nakit akışı ≤ 0 (tüm temalarda).
- Biotech: `clinical` = pre_profit **veya** TTM gelir < $50M; aksi hâlde `commercial`.

Mantık: kârsız firmalarda kârlılık/değer oranları anlamsızdır; hayatta kalma (nakit ömrü),
sulandırma, oynaklık ve momentum belirleyicidir. Klinik biotech, otonom araç girişimleri ve
erken aşama yenilenebilir aynı ekonomik gruptadır.

---

## 5. Faktörler

### 5.1 Mevcut (yeniden kullanılır)
`mom_12_1`, `dist_52w_high`, `idio_vol_60d`, `max_ret_21d`, `share_issuance`, `asset_growth`,
`gross_profitability`, `cop_at`, `ebit_ev`, `ocf_ev`, `sue`, `droe`, `cash_runway_years`.
Biotech'te negatif çıkan `cash_to_mcap` ve `rd_intensity` **kullanılmaz** (işaret ters çevrilmez).
Değer teması genel evrende sıfır çıktı; sadece enerjide (ekonomik gerekçeyle) kullanılır.

### 5.2 Yeni (T4)
Tüm girdiler PIT (`filed + 1`). Payda ≤ 0 → NaN.

| Faktör | Tanım | Kullanım |
|---|---|---|
| `capex_at` | Capex_TTM / Toplam varlık | yatırım (−) |
| `fcf_margin` | (OCF_TTM − Capex_TTM) / Gelir_TTM | ara değişken |
| `profitable_growth` | rank(revenue_yoy) + rank(fcf_margin), sadece `profitable` aşamada | kârlı büyüme |
| `net_debt_ebitda` | (Toplam borç − Nakit ve kısa vadeli yatırımlar) / EBITDA_TTM | kaldıraç (−), enerji |
| `oil_beta_trend` | β_oil × sign(WTI 126 günlük getiri). β_oil: son 104 haftalık getirilerde r_i = a + b_m·r_SPY + b_oil·r_WTI regresyonu | sadece `oil_gas` |
| `ear_3d` (T4b) | Duyuru günü t0 için Σ_{d=t0−1}^{t0+1}(r_i,d − r_ETF,d); son 90 gün içindeki en son duyuru | kazanç olayı |
| `sue_announce` (T4b) | (EPS_q − EPS_{q−4}) / son 8 mevsimsel değişimin std'si; EPS FMP earnings verisinden (gerçekleşen), kullanılabilirlik = duyuru t0 + 1 seans. Mevcut filing tarihli `sue`'nun duyuru tarihli versiyonu | kazanç olayı |

**T4b koşulu:** FMP earnings endpoint'inin (tarih, gerçekleşen/beklenen EPS ve gelir) Starter planda
açık olduğu ve tarihlerinin doğru olduğu doğrulanmalı: 20 rastgele firma-çeyrek, EDGAR 8-K Item 2.02
`acceptanceDateTime` ile karşılaştırılır. Uyuşma < %90 ise 8-K tarihleri kullanılır.
WTI ve emtia serileri için FMP emtia endpoint'i doğrulanmalı (alan adları, geçmiş uzunluğu).

---

## 6. Skorlama

1. Tarih bazında, tema içinde rank → normal skor. Muhasebe oranları alt tema içinde (≥ 8 firma), yoksa tema içinde.
2. Firma aşamasına göre faktör seti (`theme_factor_map`).
3. Grup skoru = gruptaki mevcut faktörlerin ortalaması; tema skoru = grupların **eşit ağırlıklı** ortalaması → robust z.
4. Kapsama < %30 olan faktör o tarihte düşer; toplam ağırlığın < %50'si mevcutsa firma skorlanmaz.
5. Ağırlıklar sabittir. IC'ye göre ağırlık öğrenme, parametre taraması yok.

---

## 7. Araştırma modülü: "Faktörler getiriyi ne kadar açıklıyor?"

Ders notlarındaki sırayla (Bali–Engle–Murray): önce faktörü tanı, sonra ilişkileri, sonra getiriyi test et.
Her analiz **iki adımlıdır**: (1) her ay kesitsel olarak hesaplanır, (2) aylık değerlerin zaman ortalaması
alınır ("ortalama ayın dağılımı" — faktör sağlamlığı). Hepsi her tema için ayrı, alt temalar için (n ≥ 15)
ve tüm temalar birlikte (havuz) raporlanır. Parametreler: `themes.yaml → research`.

### 7.1 Tanımlayıcı istatistikler
Her faktör için her ay: ortalama, std, çarpıklık, basıklık, min, P5, P25, medyan, P75, P95, maks, firma sayısı.
Sonra zaman ortalaması. Ham değerler %0,5/%99,5 winsorize edilir. Amaç: aşırı çarpık faktörleri ve zamanla
ortalaması kayan faktörleri görmek. (Skorlamada rank → normal kullanıldığı için uç değerler seçimi bozmaz.)

### 7.2 Korelasyon, çoklu doğrusallık, ortogonalizasyon
- Korelasyon matrisi: **alt üçgen Pearson, üst üçgen Spearman**; aylık kesitsel korelasyonların zaman ortalaması.
- |ρ| > 0,7 olan çiftler işaretlenir (aynı ekonomik mekanizma olabilir → biri gereksiz).
  Spearman ≫ Pearson: doğrusal olmayan monoton ilişki. Pearson ≫ Spearman: uç değer sorunu.
- VIF (> 5 işaretlenir).
- Ek bilgi testi için ortogonalizasyon: yeni faktör her ay mevcut tema skoruna (ve sektör kuklalarına)
  regress edilir, **artık** kullanılır.

### 7.3 Süreklilik (persistence)
ρ_τ = faktörün t ile t+τ aylarındaki kesitsel korelasyonunun zaman ortalaması, τ ∈ {1, 3, 6, 12}.
Yüksek süreklilik → düşük işlem devri, daha ucuz uygulama (JKMP 2026 ile uyumlu). Düşük süreklilik → pahalı sinyal.

### 7.4 Tek değişkenli portföy analizi
- Her ay **dinamik kırılma noktaları** (statik eşik yok): n ≥ 50 ise 5 portföy, değilse 3.
- Eşit ağırlıklı ve piyasa değeri ağırlıklı portföy getirileri (ileri 21/63/126 seans).
- Çıktılar: portföy başına ortalama getiri, **monotonluk** kontrolü, üst − alt (mimic portföy) ve
  üst − tema ortalaması (long-only için asıl ölçü), Newey-West t.
- **Alfa:** üst portföy ve üst − alt farkının CAPM, FF3, Carhart-4 ve FF5+MOM alfaları
  (faktörler ve risksiz faiz: Kenneth French veri kütüphanesi, ücretsiz). Alfa, bilinen faktörlerin
  açıklayamadığı getiridir; tema portföyünün getirisi zaten momentum ya da piyasa betası ise burada görünür.

### 7.5 İki değişkenli bağımlı sıralama (ek bilgi testi)
Önce mevcut tema skoruna göre 3 grup, sonra **her grubun içinde** yeni faktöre göre 3 grup (bağımlı sıralama).
Rapor: her tema-skoru grubunda yeni faktörün üst − alt farkı ve bunların ortalaması. Tema skoru sabitken yeni
faktör hâlâ getiri farkı yaratıyorsa ek bilgi vardır. (Bağımsız sıralama sadece etkileşimi görmek için ikincil.)

### 7.6 Fama-MacBeth regresyonları
Her ay kesitsel regresyon: r_{i,t→t+h} = a_t + b_t·faktör_{i,t} + c_t·β_i + d_t·ln(MktCap_i) + e_{i,t}.
Kontroller: beta (günlük veri, 252 gün, en az 200 gözlem) ve büyüklük. Üç varyant:
1. OLS, rank → normal değişkenler (ana sonuç; katsayı doğrudan "1 std'lik fark" etkisidir),
2. OLS, winsorize edilmiş ham değişkenler (ders/kitap formatı),
3. WLS, ağırlık = √MktCap (küçük firmaların gürültüsü tahmini bozmasın diye). *Not: ders notunda
   "market cap'in karesi" yazıyor; yaygın uygulama √MktCap'tir — hocanla teyit et.*

Çıktılar: b_t'lerin ortalaması, Newey-West t (lag = ufuk/21), **ekonomik büyüklük** =
katsayı × faktörün ortalama kesitsel std'si (varyant 1'de katsayının kendisi), ortalama kesitsel R² ve düzeltilmiş R².
Tek faktörlü ve tüm faktörlü modeller ayrı raporlanır.

### 7.7 Rank IC
Aylık Spearman(faktör_t, ileri getiri); ortalama, NW t, örtüşmeyen alt örnek t, IC > 0 olan ayların oranı.

### 7.8 İstikrar ve ekonomik gerekçe
- Alt dönemler (2011–15 / 2016–20 / 2021–26), boğa/ayı, yüksek/düşük VIX.
- Rapor her faktör için bir **"neden çalışmalı"** satırı içerir (risk mi, davranışsal yanılgı mı, sınırlı
  arbitraj mı; kaynak makale). İstatistik ile ekonomik gerekçe uyuşmuyorsa işaretlenir.

### 7.9 Rapor ve karar kuralı
- `reports/themes/<run_id>/factor_explain.md` (Türkçe) + CSV'ler. Otomatik uyarılar: örtüşen ufuklar
  t'yi şişirir; tek hisse getirisinde R²'nin yüzde birkaç olması normaldir (kitaptaki örnek: β, Size, BM
  birlikte R² ≈ %2,4); küçük temalar gürültülüdür; t-stat yüksekliği para kazandırdığı anlamına gelmez
  (ekonomik büyüklüğe bak).
- Hedef değişken: tema endeksinden arındırılmış ileri getiri (FM varyantlarında ham fazla getiri de raporlanır).
- Bu modül **seçim için kullanılmaz**. Bir faktör "bu temada çalışıyor" sayılırsa: havuz 126g IC > 0 ve
  NW t ≥ 2; FM katsayısı aynı işaretli; alt dönemlerin en az 2/3'ünde IC > 0; bağımlı sıralamada farkın
  ortalaması > 0. Çalışmayanlar bir sonraki sürümde gerekçeli çıkarılabilir; sonuçlara bakıp yeni faktör eklenmez.

---

## 8. Portföy ve seçim listesi

- Aylık: her açık temadan `n_picks` hisse, tema ağırlığı / n_picks eşit ağırlık; alt tema başına en fazla %50;
  pozisyon tavanı %8; mevcut histerezis (`hold_buffer`) ve maliyet modeli; en oynak %3 girişte bloklu.
- Çıktı: `reports/themes/shortlist_<tarih>.md` ve `.csv` — tema, alt tema, aşama, skor, grup katkıları,
  BUY/HOLD/WAIT/SELL, WAIT yedek listesi, 10-K eşleşme kanıtı.
- Backtest: 2011-06 → bugün, mevcut walk-forward katmanları, **tek sabit konfigürasyon** (themes_v1).
  Karşılaştırma: her tema eşit ağırlık endeksi, tema ETF'leri (başlangıç tarihlerine dikkat), QQQ, SPY.

**Başarı ölçütü (ön kayıtlı, CAGR hedefi değil):**
seçim katkısı (portföy − tema endeksi) > 0 alt dönemlerin en az 2/3'ünde; maksimum düşüş tema endeksinden
5 puandan fazla kötü değil; maliyet çarpanı 2× iken seçim katkısı hâlâ ≥ 0.

---

## 9. Teknik analiz katmanı ve işlem günlüğü

- Her `interval_days` günde bir: aylık listedeki hisseler için göstergeler (SMA 50/200, EMA, RSI, MACD, ADX,
  ATR, Bollinger, kırılımlar) tablosu. **Otomatik işlem yok**; TA listeyi değiştirmez, sadece zamanlama yapar.
- Kurallar önceden yazılır: `research/ta/rules.yaml`. Örnek kurallar (dersteki gibi): `golden_cross_50_200`,
  `pullback_to_50d`, `trailing_stop_atr`. **Parametreler optimize edilmez** (statik optimizasyon tüm veriye
  uyar ve gerçekte bozulur). Değişiklik gerekirse yeni kural sürümü + tarih.
- Günlük: `trade_journal.csv` — tarih, sembol, işlem, fiyat, adet, rule_id, stop seviyesi, gerekçe.
- **Değerlendirme betiği** (derste geçen ölçütlerle):
  - Her işlem, aynı hissenin ay başı rebalance fiyatıyla alınmış hâliyle karşılaştırılır (maliyetler dahil).
  - **İsabet oranı taban oranla karşılaştırılır**: aynı hisseleri aynı sürede rastgele günlerde tutsaydın
    kazanma oranı ne olurdu? (%56 isabet, taban oran %60 ise kural kötüdür.)
  - Kâr faktörü (brüt kâr / brüt zarar), kâr / maksimum düşüş, ortalama kazanç / ortalama kayıp.
  - 50+ işlem ve 3–6 ay sonra: TA'nın ortalama katkısı ve güven aralığı.

---

## 10. Görev listesi (Claude Code için, sırayla)

Her görev: kod + test + kısa rapor. Bir görev bitmeden sonrakine geçilmez.

| Görev | İçerik | Teslim / test |
|---|---|---|
| **T0** | FMP'deki tüm benzersiz `sector`/`industry` değerlerini ve EDGAR SIC dağılımını dök | `research/themes/fmp_industries.csv`, `sic_counts.csv`. Kullanıcı ile `fmp_industries` listeleri kesinleştirilir, `# VERIFY` kaldırılır |
| **T1** | Evreni NYSE'ye genişlet (borsa parametresi, NYSE delist kurtarma, yabancı dosyalayan bayrağı) | Mevcut testler geçer; borsa filtresi testi; aday havuzu firma sayısı raporu |
| **T2** | EDGAR 10-K Item 1 indirme + metin çıkarma + önbellek | 10 örnek firmada Item 1 çıkarım doğruluğu; oran sınırı ≤ 8 istek/sn; tekrar çalıştırmada ağ çağrısı yok |
| **T3** | Anahtar kelime skoru + `theme_membership` tablosu (PIT geçerlilik) + inceleme CSV'si | Sızıntı testi: gelecekte dosyalanan 10-K geçmiş üyeliği değiştirmez; tema-tarih firma sayısı raporu |
| **T3r** | *Kullanıcı incelemesi* (isabet ≥ %85) | İşaretlenmiş CSV |
| **T4** | Aşama bayrağı + `capex_at`, `fcf_margin`, `profitable_growth`, `net_debt_ebitda`, `oil_beta_trend` | Her faktör için sızıntı enjeksiyon testi ve birim testi |
| **T4b** | FMP earnings + emtia endpoint doğrulama; geçerse `ear_3d`, `sue_announce` | 20 örnek 8-K karşılaştırması raporu |
| **T5a** | Kenneth French veri kütüphanesinden FF3, FF5, MOM ve RF aylık serilerini indir + önbellekle; beta_252d ve size_ln_mcap kontrollerini hesapla | Tarih hizalama testi (ay sonu), serilerin başlangıç/bitiş raporu |
| **T5** | Ön kayıt dosyası + araştırma modülü (§7.1–7.9) | `research/preregistration/themes_v1.yaml` + SHA256; `factor_explain.md` + CSV'ler; bilinen bir faktörle (ör. `mom_12_1`) sonuçların mevcut `FACTOR_IC.md` ile tutarlılık testi |
| **T6** | Tema portföyü backtest + seçim listesi (§8) | Walk-forward sonuçları, seçim katkısı, başarı ölçütü tablosu, güncel `shortlist` |
| **T7** | TA tablosu + işlem günlüğü + değerlendirme betiği (§9) | Örnek günlükle uçtan uca test |

---

## 11. Bilinen riskler

- **Küçük temalar:** robotiğin bazı alt temalarında tarih başına 10–30 firma olabilir; sonuçlar gürültülü, havuz sonuçları esas alınır.
- **Metin sınıflandırma hataları:** "robot" kelimesi alakasız bağlamda geçebilir; eşikler ve inceleme bunu sınırlar, sıfırlamaz.
- **Kaba filtre PIT değil:** sanayi/SIC bugünkü değerler. Filtreyi geniş tutmak riski azaltır; kalan etki raporda belirtilir.
- **ADR/yabancı hariç:** büyük robotik firmalarının bir kısmı (Japonya, İsviçre) kapsam dışında kalır.
- **Hayatta kalma:** NYSE delist kapsaması FMP'nin sunduğu kadardır.
- **Tema endeksini geçmek zordur:** faktörlerin gerçekçi katkısı yılda birkaç puan; getirinin seviyesini tema belirler.
- **Size faktörü:** ders notları size primini vurgular, ama $300M altı hariç tutulan bu evrende ve 1980 sonrası
  verilerde küçük firma primi zayıftır ve çoğunlukla mikro şirketlerdedir. Bu yüzden büyüklük **seçim faktörü
  değil, FM regresyonunda kontrol** olarak kullanılır.

---

## 12. Kapsam dışı (bilinçli olarak)

- **Pairs trading, kointegrasyon, ARMA/ARIMA** (ders notlarının istatistiksel arbitraj bölümü): piyasa nötr,
  açığa satış gerektiren, kısa vadeli ayrı bir strateji ailesi. Bu sistemin 3–6 aylık long-only yapısına uymaz;
  istenirse ayrı bir proje olarak ele alınır.
- **Kaldıraç:** varyans sürüklenmesi (variance drag) nedeniyle mevcut Sharpe seviyesinde getiriyi artırmaz;
  forward sonuçlar ön kayıtlı kuralı geçmeden kullanılmaz.
- **Makro faktör taklit portföyleri** (dolar, büyüme, enflasyon sürprizleri): sadece `oil_beta_trend` dahil;
  diğerleri themes_v2 adayı.

### themes_v2 adayları (v1 sonuçları görüldükten sonra, ön kayıtla, birer birer)
Önceki araştırmadaki (bkz. yüksek getiri raporu, E1–E5) deneylerden tema sistemine taşınabilecekler:
- **FINRA açığa satış oranı** (ücretsiz, ayda iki kez; yayın tarihi = settlement + 7 iş günü): özellikle biotech.
- **Form 4 fırsatçı içeriden alımları** (ücretsiz EDGAR; kabul zaman damgası).
- **Kısmi işlem (partial trading):** her ay hedef ağırlığa farkın %50'si kadar yaklaş; işlem maliyetini düşürür.
- **ETF ile beta hedge** (QQQ/sektör ETF'i, tam hisse): düşüşü azaltır, getiri yaratmaz.
- **Jev'in 8-K olay sınıflandırıcısı** olarak yeniden kullanımı: sadece ileriye dönük (forward) doğrulamayla.
Her biri ayrı ön kayıt, "mevcut skora ek bilgi" testi ve ablation ile eklenir; aynı anda birden fazla eklenmez.

