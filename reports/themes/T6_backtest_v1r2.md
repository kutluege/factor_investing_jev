# T6 — Tema portföyü backtest (themes_v1, tek sabit yapılandırma) — v1r2

Ön kayıt SHA256 `b3f5ab188a3002aaf058c356277042023f70a55057de60883657277098072c4b`. Dönem 2011-06-30 → 2026-09-30 (184 ay). Jev ağırlığı 0. Parametre taraması yok; yapılandırma hiçbir parametre tahmin etmediği için tüm dönem örneklem dışıdır ve ön kayıtlı alt dönemler walk-forward katmanlarının yerini tutar.
Maliyetler: mevcut model (komisyon, kayma, işlem maliyeti, Abdi–Ranaldo yarım spread); delist: son kapanış eksi sembol bazlı kesinti (sıkıntılı delist %30, diğerleri yapılandırılmış oran; portföy ve endeks aynı kuralı kullanır). Tema endeksleri maliyetsiz, aylık yeniden dengelenen eşit ağırlıklıdır.

## §8 Başarı ölçütü (ön kayıtlı; CAGR hedefi değil)

| Ölçüt | Değer | Sonuç |
|---|---|---|
| Seçim katkısı > 0 alt dönemlerin ≥ 2/3'ünde | 1/3 | ✘ |
| Maks. düşüş, tema endeksinden en fazla 5 puan kötü | portföy -18.2% / endeks -30.1% | ✔ |
| 2× maliyette seçim katkısı ≥ 0 | -0.09%/yıl | ✘ |
| **Sonuç** | seçim katkısı (tüm dönem) +0.84%/yıl | **GEÇMEDİ** |

## Seçim katkısının istatistiği (aylık, aritmetik)

Aritmetik katkı -0.36%/yıl, takip hatası 10.48%, bilgi oranı -0.03, NW t -0.14; gözlenen bilgi oranının %95 güvenle anlamlı olması için gereken en kısa süre (MinTRL): inf ay. Nakit: risksiz faiz (French RF) işler.

## Alt dönemler

| Alt dönem | Ay | Portföy (yıllık) | Tema endeksi (yıllık) | Seçim katkısı |
|---|---|---|---|---|
| 2011-07..2015-12 | 54 | 9.47% | 10.47% | -1.00% |
| 2016-01..2020-12 | 60 | 19.46% | 19.55% | -0.09% |
| 2021-01..2026-09 | 69 | 13.14% | 10.08% | +3.06% |

## Karşılaştırma (aylık getirilerden; ETF'ler kendi başlangıç tarihlerinden)

| Seri | Başlangıç | Yıllık getiri | Yıllık oynaklık | Maks. düşüş |
|---|---|---|---|---|
| Portföy (1× maliyet) | 2011-07-29 | 14.06% | 15.77% | -18.22% |
| Portföy (2× maliyet) | 2011-07-29 | 13.12% | 15.84% | -18.55% |
| Bileşik tema endeksi | 2011-07-29 | 13.22% | 21.71% | -30.12% |
| Tema endeksi: robotics | 2011-07-29 | 16.87% | 27.44% | -45.60% |
| Tema endeksi: biotech | 2011-07-29 | 9.73% | 25.38% | -52.12% |
| Tema endeksi: energy | 2011-07-29 | 7.97% | 24.23% | -59.90% |
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

Geometrik fark oynaklık sürüklenmesinden etkilenir (düşük oynaklıklı kol lehine); asıl ölçü aritmetik farktır.

| Tema | Kol (geom.) | Endeks (geom.) | Geom. fark | Aritm. fark | t |
|---|---|---|---|---|---|
| robotics | 21.44% | 16.52% | +4.91% | +3.84% | +1.49 |
| biotech | 14.75% | 9.73% | +5.02% | +3.10% | +0.71 |
| energy | 9.36% | 7.97% | +1.39% | -0.39% | -0.09 |

## Karar

Faktör seçimi temayı geçemedi: tema içinde geniş eşit ağırlıklı sepet (veya tema ETF'i) tutulur; yalnızca nakit ömrü/sulandırma elemeleri korunur, TA zamanlama için kullanılır (ROADMAP Adım 7).

İşlem sayısı: 958; dosyalar: `T6_period_returns_v1r2.csv`, `T6_trades_v1r2.csv`.
