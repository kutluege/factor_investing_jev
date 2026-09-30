# Kapı (gate) kararları — themes_v1

Kullanıcı kararı (2026-09-30): yol haritasındaki kullanıcı girdileri FMP verisiyle yanıtlanır. Hiçbir karar
getiri sonucuna bakılarak verilmez. Her karar burada gerekçesiyle kayıtlıdır.

## Kapı 1 — T0: `fmp_industries` doğrulaması (2026-09-30)

Kaynak: FMP `company-screener` (NASDAQ + NYSE, aktif, ETF/fon hariç; 5.821 firma, 152 sanayi) ve
`available-industries` (159 ad). Çıktılar: `research/themes/fmp_industries.csv`,
`research/themes/fmp_industries_mapping.csv`, `research/themes/sic_counts.csv` (393 SIC kodu).

**Sonuç:** `config/themes.yaml` içindeki 27 sanayi adının **27'si FMP'de birebir mevcut** ve hepsi FMP'nin resmi
sanayi listesinde. Hiçbir ad değiştirilmedi; yalnızca `# VERIFY` işaretleri kaldırıldı.

| Tema / alt tema | Sanayi (firma sayısı, NASDAQ+NYSE, aktif) |
|---|---|
| robotics / industrial_automation | Industrial - Machinery (93), Electrical Equipment & Parts (60), Industrial - Specialties (4) |
| robotics / surgical_medical | Medical - Devices (114), Medical - Instruments & Supplies (43) |
| robotics / autonomous_drone | Auto - Manufacturers (33), Auto - Parts (46), Aerospace & Defense (88), Software - Application (273), Software - Infrastructure (142) |
| robotics / components | Semiconductors (110), Hardware, Equipment & Parts (63), Electrical Equipment & Parts (60) |
| biotech / biotech_all | Biotechnology (584), Drug Manufacturers - Specialty & Generic (64) |
| energy / oil_gas | E&P (68), Integrated (16), Midstream (47), Equipment & Services (49), Refining & Marketing (18) |
| energy / power_utilities | Regulated Electric (66), Independent Power Producers (12), Diversified Utilities (9) |
| energy / nuclear_uranium | Uranium (8) |
| energy / grid_equipment | Electrical Equipment & Parts (60) |
| energy / renewables | Solar (20), Renewable Utilities (20) |

**Notlar:**
- Anahtar kelimeli alt temalarda geniş sanayiler (ör. Software - Application, 273 firma) bilinçli olarak kalır:
  aşama A sadece 10-K indirilecek firmaları belirler, üyelik kararını 10-K anahtar kelimeleri verir.
- SIC 1094 (uranyum cevheri), 3612 (transformatör) ve 3625 (röle) kodlarında bugün listeli firma yok; kodlar
  korunur (geçmişte listeli/delist firmaları yakalayabilir, maliyeti yok).
- FMP `country` alanı yabancı firmaları gösteriyor (ör. Auto - Manufacturers: 33 firmanın 14'ü ABD); yabancı
  dosyalayanlar (20-F/40-F) T1'de `include_foreign_filers: false` ile SEC form türüne göre çıkarılır.

## Veri kararı — `oil_beta_trend` petrol serisi (2026-09-30, sonuç görülmeden)

FMP `commodities-list` WTI'yi `CLUSD` ve Brent'i `BZUSD` olarak listeliyor. `historical-price-eod/full?symbol=CLUSD`
Starter planda **HTTP 402** (Premium) döndü; `BZUSD` açık ve 2007-07'den bu yana günlük veri içeriyor.
Karar: `oil_beta_trend` hesabında WTI yerine **Brent (BZUSD)** kullanılır. Haftalık Brent ve WTI getirileri çok
yüksek korelasyonludur; regresyon (β_oil) ve trend işareti (126 seans) için ekonomik anlamı aynıdır. Bu, ön kayıt
öncesi bir veri erişim kararıdır (themes_v2 gerektirmez); `src/features/theme_features.py` içinde belgelenmiştir.

## Kapı 5 — T4b: FMP duyuru tarihleri (2026-09-30, sonuç görülmeden)

20 rastgele firma-çeyrekte FMP `earnings` tarihi ile EDGAR 8-K Item 2.02 kabul tarihi (ET) aynı günde **16/20 = %80**
uyuştu (±1 gün: %90). Eşik ≥ %90 aynı gün → karşılanmadı. Karar: `ear_3d` ve `sue_announce` zamanlaması **8-K
tarihlerinden**; FMP yalnızca gerçekleşen EPS değeri için (±3 gün eşleşme). Ayrıntı: `T4b_earnings_dates.md`.
Aynı çalışmada EDGAR `acceptanceDateTime` alanının UTC olduğu doğrulandı ve üyelik seans kuralı düzeltildi.

## Uygulama yorumu — alt tema tavanı (2026-09-30, sonuç görülmeden)

`max_share_per_subtheme: 0.5` kuralı iki durumda tanımsız kalıyordu: (1) tek alt temalı bir tema (biotech yalnızca
`biotech_all`) seçimlerinin yarısıyla sınırlanırdı; (2) tek sayılı `n_picks` (biotech 7) iki alt temayla
doldurulamazdı (⌊3,5⌋ = 3 + 3 = 6). Yorum: tavan = ⌈0,5 × n_picks⌉ ve yalnızca sıralamada en az iki alt tema
varsa uygulanır. Kod: `src/portfolio/rebalance.py::select_theme`; testler `tests/test_theme_backtest.py`.
Bu, ön kayıttan önce yapılan bir uygulama netleştirmesidir; yapılandırma değeri değişmedi.

## Kapı 2 — T3r: sınıflandırma isabeti (2026-09-30, sonuç görülmeden)

Otomatik inceleme: güncel üyelerden alt tema tabakalı 120 firma; etiket = FMP şirket açıklaması + sanayisinin alt temayı
bağımsız olarak doğrulaması (FMP açıklaması yalnızca doğrulama etiketi, backtest üyeliğinde kullanılmaz).

| Koşu | İsabet | En zayıf alt temalar |
|---|---|---|
| İlk (themes_v1 taslağı) | **%83,3** (< %85) | autonomous_drone %41,7, surgical_medical %70, industrial_automation %75 |
| Tek revizyon sonrası | **%91,7** (≥ %85, geçti) | surgical_medical %71,4, autonomous_drone %75 |

Hataların incelemesi (`research/themes/membership_review_labeled.csv`): (a) 6 hata SPAC'lerdi; bunların 4'ü aslında
birleşme sonrası şirketle aynı CIK'i paylaşan emekli SPAC sembolleriydi (PSAC→FFIE, CLAQ→Nauticus Robotics,
SVFC→Symbotic, DEH→Vicarious Surgical) — üyelik metni doğru şirketi anlatıyor, doğrulayıcı ise eski sembolün
"Shell Companies" profiline bakıyordu; (b) autonomous_drone'da düşük isabetli yanlış pozitifler (otonom sürüşten
geçerken bahseden EV üreticileri vb.); (c) doğrulayıcının kendi hataları (ör. Globus Medical gerçekten cerrahi robot
satıyor).

**Tek revizyon (THEMES_SPEC §3; getiriye bakılmadan):**
1. SPAC kuralı: 10-K'nın kendi Item 1 metni şirketi "blank check company" olarak tanımlıyorsa o dosyadan üyelik yok
   (metin tabanlı → PIT). 13.623 metnin 211'i kurala takıldı.
2. `autonomous_drone.min_hits`: 5 → 10 (anahtar kelimeler değişmedi).
3. İnceleme örneklemi düzeltmesi (sınıflandırma değişikliği değil): yalnızca hâlâ işlem gören semboller incelenir;
   emekli SPAC sembolleri CIK üzerinden birleşme sonrası 10-K'ları devralıyordu. Backtest etkilenmez (o sembollerin
   birleşme sonrası fiyatı yok).

İsabet artışının bir kısmı (3) numaralı örneklem düzeltmesinden gelir; bu açıkça not edilir.

**Kapsam uyarısı (getiri değil, sayı):** robotik teması incedir — güncel 46 üye; components, surgical_medical ve
grid_equipment alt temaları hiçbir ayda 15 firmaya ulaşmıyor; bu alt temalar araştırma modülünde ayrı kapsam olarak
raporlanmaz (n < 15), tema düzeyinde kalır.
