# T6 — Tema portföyü backtest (themes_v1, tek sabit yapılandırma)

Ön kayıt SHA256 `b3f5ab188a3002aaf058c356277042023f70a55057de60883657277098072c4b`. Dönem 2011-06-30 → 2026-09-30 (184 ay). Jev ağırlığı 0. Parametre taraması yok; yapılandırma hiçbir parametre tahmin etmediği için tüm dönem örneklem dışıdır ve ön kayıtlı alt dönemler walk-forward katmanlarının yerini tutar.
Maliyetler: mevcut model (komisyon, kayma, işlem maliyeti, Abdi–Ranaldo yarım spread); delist: son kapanış eksi sembol bazlı kesinti (sıkıntılı delist %30, diğerleri yapılandırılmış oran; portföy ve endeks aynı kuralı kullanır). Tema endeksleri maliyetsiz, aylık yeniden dengelenen eşit ağırlıklıdır.

## §8 Başarı ölçütü (ön kayıtlı; CAGR hedefi değil)

| Ölçüt | Değer | Sonuç |
|---|---|---|
| Seçim katkısı > 0 alt dönemlerin ≥ 2/3'ünde | 0/3 | ✘ |
| Maks. düşüş, tema endeksinden en fazla 5 puan kötü | portföy -18.2% / endeks -30.1% | ✔ |
| 2× maliyette seçim katkısı ≥ 0 | -1.60%/yıl | ✘ |
| **Sonuç** | seçim katkısı (tüm dönem) -0.68%/yıl | **GEÇMEDİ** |

## Alt dönemler

| Alt dönem | Ay | Portföy (yıllık) | Tema endeksi (yıllık) | Seçim katkısı |
|---|---|---|---|---|
| 2011-07..2015-12 | 54 | 9.52% | 10.47% | -0.95% |
| 2016-01..2020-12 | 60 | 19.28% | 19.58% | -0.30% |
| 2021-01..2026-09 | 69 | 13.73% | 14.51% | -0.78% |

## Karşılaştırma (aylık getirilerden; ETF'ler kendi başlangıç tarihlerinden)

| Seri | Başlangıç | Yıllık getiri | Yıllık oynaklık | Maks. düşüş |
|---|---|---|---|---|
| Portföy (1× maliyet) | 2011-07-29 | 14.24% | 15.70% | -18.23% |
| Portföy (2× maliyet) | 2011-07-29 | 13.33% | 15.75% | -18.56% |
| Bileşik tema endeksi | 2011-07-29 | 14.92% | 21.89% | -30.12% |
| Tema endeksi: robotics | 2011-07-29 | 16.87% | 27.44% | -45.60% |
| Tema endeksi: biotech | 2011-07-29 | 13.73% | 29.40% | -52.65% |
| Tema endeksi: energy | 2011-07-29 | 7.98% | 24.16% | -59.69% |
| BOTZ | 2016-10-31 | 9.15% | 24.26% | -51.90% |
| IBB | 2011-07-29 | 12.63% | 20.56% | -33.61% |
| ICLN | 2011-07-29 | 2.46% | 27.47% | -60.79% |
| QQQ | 2011-07-29 | 19.34% | 17.50% | -32.58% |
| ROBO | 2013-11-29 | 9.69% | 21.46% | -41.05% |
| SPY | 2011-07-29 | 14.21% | 14.21% | -23.93% |
| XBI | 2011-07-29 | 13.29% | 28.29% | -56.67% |
| XLE | 2011-07-29 | 6.90% | 27.07% | -64.00% |
| XLU | 2011-07-29 | 9.41% | 14.55% | -18.81% |

## Tema kolları (brüt) vs tema endeksi

| Tema | Kol (yıllık) | Endeks (yıllık) | Fark |
|---|---|---|---|
| robotics | 21.44% | 16.52% | +4.91% |
| biotech | 14.94% | 13.73% | +1.21% |
| energy | 9.35% | 7.98% | +1.37% |


## Tanı: başarısızlık nereden geliyor? (ölçüt değişmez, yalnızca açıklama)

- Tema kollarının brüt getirisi her temada kendi endeksini geçiyor (robotik +4,9, biotech +1,2, enerji +1,4 puan/yıl);
  yani yatırılan dolar başına seçim pozitif.
- Buna karşın portföy ortalamada yalnızca **%90,9 yatırımda**: robotik bütçesi %40 iken ortalama %31,5 dolu (8 slotun
  ortalama 6,4'ü; 183 ayın 16'sında hiç uygun robotik hisse yok). Ön kayıtlı kural gereği boş slotlar nakitte ve
  backtest nakde faiz işletmez. ~%9 nakit × endeksin ~%15/yıl getirisi ≈ **−1,3 puan/yıl** sürüklenme; bu, ölçülen
  −0,68 puanlık açıktan büyüktür. Maliyetler ayrıca ~0,9 puan/yıl (1× ile 2× farkı).
- Portföyün oynaklığı (%15,7) ve maks. düşüşü (−%18) endeksten (%21,9, −%30) belirgin düşük; düşük risk faktörleri ve
  nakit bunun kaynağı.
- Sebep yapısaldır: robotik teması 10-K anahtar kelime + likidite filtreleriyle ayda ortalama ~11 uygun firmaya iner.

**Karar değişmez: themes_v1 ön kayıtlı ölçütü GEÇMEDİ.** Boş bütçenin diğer temalara dağıtılması, nakde RF işletilmesi
veya robotik kapsamının genişletilmesi ancak yeni bir sürüm (themes_v2) olarak, bu sonuç gerekçe gösterilerek
`docs/CHANGELOG_THEMES.md`'ye yazılıp yeniden ön kayıtla denenebilir — bu kullanıcı kararıdır.

## Karar

Faktör seçimi temayı geçemedi: tema içinde geniş eşit ağırlıklı sepet (veya tema ETF'i) tutulur; yalnızca nakit ömrü/sulandırma elemeleri korunur, TA zamanlama için kullanılır (ROADMAP Adım 7).

İşlem sayısı: 961; dosyalar: `T6_period_returns.csv`, `T6_trades.csv`.
