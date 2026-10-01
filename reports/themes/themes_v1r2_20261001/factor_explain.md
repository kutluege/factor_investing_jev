# Faktör açıklama raporu — themes_v1 (`themes_v1r2_20261001`)

Bu rapor **tanımlayıcıdır**; faktör seçimi veya ağırlık öğrenmesi için kullanılmaz (THEMES_SPEC §7.9).

- Ön kayıt: `research/preregistration/themes_v1.yaml`, SHA256 `b3f5ab188a3002aaf058c356277042023f70a55057de60883657277098072c4b`
- Veri: 2011-07-29 → 2026-09-30, 183 ay; uygun satır 54267
- Sızıntı denetimi: {'future_fundamentals': 0, 'future_membership': 0, 'future_snapshots': 0, 'events_available_before_announcement': 0, 'passed': True}
- Hedef: tema endeksinden arındırılmış ileri getiri (`label_fwd_<h>_theme`, maliyetsiz EW tema endeksi).
- Faktörler yön işaretlidir (pozitif = beklenen yön). Faktörler yalnızca kullanıldıkları aşamadaki firmalarda incelenir; `ear_3d`, `sue_announce` hiçbir sette değildir (aday), tüm firmalarda incelenir.

## Otomatik uyarılar

- Örtüşen ufuklar (63/126 seans, aylık gözlem) t'yi şişirir: NW gecikmesi = ufuk/21 ve örtüşmeyen alt örnek t'si birlikte raporlanır.
- Tek hisse getirisinde kesitsel R²'nin yüzde birkaç olması normaldir (kitap örneği: β, Size, BM ile R² ≈ %2,4).
- Küçük temalar (aylık n < 15) gürültülüdür; bu aylar analiz dışıdır, sayılar aşağıda.
- Yüksek t-istatistiği para kazandırmak demek değildir: ekonomik büyüklüğe ve maliyetlere bakın.

## Tutarlılık testi (`mom_12_1`, NASDAQ paneli, 21 seans)

Bu modülün IC fonksiyonu mevcut NASDAQ panelinde `mom_12_1` için IC = 0.012 (t = 1.2, 182 ay) verdi; `docs/FACTOR_IC.md`: IC = 0.012 (t = 1.2). Fark 0.0002 → **tutarlı**.

## Tema-tarih firma sayıları (uygun)

| Tema | Ortalama | Min | Maks | n<15 ay |
|---|---|---|---|---|
| biotech | 143.4 | 27 | 258 | 0 |
| energy | 142.3 | 89 | 179 | 0 |
| robotics | 10.9 | 2 | 23 | 116 |

## §7.9 Karar tablosu (126 seans)

Çalışıyor = IC > 0 ve NW t ≥ 2 **ve** FM katsayısı aynı işaretli **ve** alt dönemlerin ≥ 2/3'ünde IC > 0 **ve** bağımlı sıralama farkı > 0. Çalışmayanlar bir sonraki sürümde gerekçeyle çıkarılabilir; sonuçlara bakıp yeni faktör eklenmez.

| Kapsam | Faktör | IC | NW t | IC>0,t≥2 | FM | Alt dönem | Bağımlı | Çalışıyor |
|---|---|---|---|---|---|---|---|---|
| havuz | asset_growth | 0.033 | 2.28 | ✔ | ✔ | ✔ | ✔ | ✔ |
| havuz | capex_at | -0.020 | -1.38 | ✘ | ✘ | ✘ | ✔ | ✘ |
| havuz | cash_runway_years | 0.008 | 0.44 | ✘ | ✘ | ✔ | ✘ | ✘ |
| havuz | cop_at | -0.032 | -1.10 | ✘ | ✔ | ✘ | ✘ | ✘ |
| havuz | dist_52w_high | 0.084 | 3.26 | ✔ | ✔ | ✔ | ✔ | ✔ |
| havuz | droe | -0.017 | -0.92 | ✘ | ✔ | ✘ | ✘ | ✘ |
| havuz | ear_3d | -0.001 | -0.06 | ✘ | ✘ | ✘ | ✘ | ✘ |
| havuz | ebit_ev | -0.020 | -0.57 | ✘ | ✔ | ✘ | ✘ | ✘ |
| havuz | gross_profitability | -0.004 | -0.14 | ✘ | ✘ | ✔ | ✔ | ✘ |
| havuz | idio_vol_60d | 0.113 | 3.80 | ✔ | ✔ | ✔ | ✘ | ✘ |
| havuz | max_ret_21d | 0.092 | 3.40 | ✔ | ✘ | ✔ | ✘ | ✘ |
| havuz | mom_12_1 | 0.017 | 0.83 | ✘ | ✔ | ✔ | ✔ | ✘ |
| havuz | net_debt_ebitda | -0.053 | -1.56 | ✘ | ✘ | ✘ | ✘ | ✘ |
| havuz | ocf_ev | 0.009 | 0.21 | ✘ | ✔ | ✘ | ✔ | ✘ |
| havuz | oil_beta_trend | -0.015 | -0.41 | ✘ | ✔ | ✔ | ✔ | ✘ |
| havuz | profitable_growth | — | — | ✘ | ✘ | ✘ | ✘ | ✘ |
| havuz | share_issuance | 0.070 | 4.81 | ✔ | ✔ | ✔ | ✘ | ✘ |
| havuz | sue | 0.001 | 0.06 | ✘ | ✔ | ✘ | ✘ | ✘ |
| havuz | sue_announce | 0.039 | 2.55 | ✔ | ✔ | ✔ | ✔ | ✔ |
| robotics | asset_growth | 0.056 | 0.93 | ✘ | ✘ | ✔ | ✔ | ✘ |
| robotics | capex_at | -0.151 | -2.08 | ✘ | ✔ | ✘ | ✘ | ✘ |
| robotics | cop_at | — | — | ✘ | ✘ | ✔ | ✘ | ✘ |
| robotics | dist_52w_high | 0.049 | 0.99 | ✘ | ✔ | ✘ | ✘ | ✘ |
| robotics | droe | — | — | ✘ | ✘ | ✔ | ✘ | ✘ |
| robotics | ear_3d | 0.012 | 0.29 | ✘ | ✔ | ✘ | ✘ | ✘ |
| robotics | gross_profitability | — | — | ✘ | ✘ | ✔ | ✘ | ✘ |
| robotics | idio_vol_60d | 0.125 | 2.16 | ✔ | ✔ | ✘ | ✘ | ✘ |
| robotics | max_ret_21d | 0.096 | 1.89 | ✘ | ✘ | ✘ | ✘ | ✘ |
| robotics | mom_12_1 | 0.041 | 0.78 | ✘ | ✔ | ✘ | ✘ | ✘ |
| robotics | profitable_growth | — | — | ✘ | ✘ | ✘ | ✘ | ✘ |
| robotics | share_issuance | 0.133 | 1.85 | ✘ | ✔ | ✘ | ✔ | ✘ |
| robotics | sue | — | — | ✘ | ✘ | ✔ | ✘ | ✘ |
| biotech | asset_growth | 0.013 | 0.75 | ✘ | ✔ | ✔ | ✔ | ✘ |
| biotech | capex_at | -0.017 | -1.00 | ✘ | ✘ | ✘ | ✔ | ✘ |
| biotech | cash_runway_years | 0.017 | 1.00 | ✘ | ✘ | ✔ | ✘ | ✘ |
| biotech | cop_at | 0.003 | 0.13 | ✘ | ✘ | ✘ | ✘ | ✘ |
| biotech | dist_52w_high | 0.097 | 5.03 | ✔ | ✔ | ✔ | ✔ | ✔ |
| biotech | droe | -0.021 | -1.01 | ✘ | ✔ | ✘ | ✘ | ✘ |
| biotech | ear_3d | -0.011 | -1.06 | ✘ | ✔ | ✘ | ✘ | ✘ |
| biotech | gross_profitability | -0.014 | -0.46 | ✘ | ✔ | ✔ | ✘ | ✘ |
| biotech | idio_vol_60d | 0.133 | 6.06 | ✔ | ✔ | ✔ | ✔ | ✔ |
| biotech | max_ret_21d | 0.105 | 5.14 | ✔ | ✔ | ✔ | ✔ | ✔ |
| biotech | mom_12_1 | 0.006 | 0.34 | ✘ | ✔ | ✔ | ✔ | ✘ |
| biotech | share_issuance | 0.072 | 3.03 | ✔ | ✘ | ✔ | ✘ | ✘ |
| biotech | sue | 0.001 | 0.05 | ✘ | ✔ | ✘ | ✘ | ✘ |
| biotech | sue_announce | 0.059 | 2.87 | ✔ | ✔ | ✔ | ✔ | ✔ |
| energy | asset_growth | 0.071 | 2.73 | ✔ | ✔ | ✔ | ✔ | ✔ |
| energy | capex_at | 0.047 | 1.56 | ✘ | ✔ | ✔ | ✔ | ✘ |
| energy | cash_runway_years | -0.339 | -6.03 | ✘ | ✔ | ✘ | ✘ | ✘ |
| energy | cop_at | -0.049 | -1.23 | ✘ | ✔ | ✘ | ✘ | ✘ |
| energy | dist_52w_high | 0.052 | 1.03 | ✘ | ✔ | ✔ | ✘ | ✘ |
| energy | ear_3d | 0.022 | 1.34 | ✘ | ✔ | ✔ | ✔ | ✘ |
| energy | ebit_ev | -0.020 | -0.57 | ✘ | ✔ | ✘ | ✘ | ✘ |
| energy | gross_profitability | -0.023 | -0.82 | ✘ | ✔ | ✘ | ✔ | ✘ |
| energy | idio_vol_60d | 0.076 | 1.33 | ✘ | ✘ | ✔ | ✘ | ✘ |
| energy | max_ret_21d | 0.055 | 1.14 | ✘ | ✘ | ✔ | ✘ | ✘ |
| energy | mom_12_1 | 0.033 | 0.75 | ✘ | ✔ | ✔ | ✔ | ✘ |
| energy | net_debt_ebitda | -0.053 | -1.56 | ✘ | ✘ | ✘ | ✘ | ✘ |
| energy | ocf_ev | 0.009 | 0.21 | ✘ | ✔ | ✘ | ✔ | ✘ |
| energy | oil_beta_trend | -0.015 | -0.41 | ✘ | ✔ | ✔ | ✔ | ✘ |
| energy | share_issuance | 0.042 | 2.01 | ✔ | ✔ | ✔ | ✔ | ✔ |
| energy | sue_announce | 0.024 | 0.99 | ✘ | ✔ | ✔ | ✔ | ✘ |

## Kapsam: havuz

### 7.7 Rank IC

| Faktör | Ufuk | IC | NW t | Örtüşmesiz t | IC>0 oranı | Ay |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 0.014 | 1.71 | 1.74 | 50.55% | 182 |
| asset_growth | 63 | 0.018 | 1.52 | 1.19 | 57.22% | 180 |
| asset_growth | 126 | 0.033 | 2.28 | 1.87 | 62.71% | 177 |
| capex_at | 21 | -0.009 | -1.40 | -1.46 | 43.96% | 182 |
| capex_at | 63 | -0.016 | -1.56 | -0.92 | 41.67% | 180 |
| capex_at | 126 | -0.020 | -1.38 | -0.62 | 41.24% | 177 |
| cash_runway_years | 21 | 0.007 | 0.74 | 0.80 | 52.30% | 174 |
| cash_runway_years | 63 | 0.003 | 0.20 | -0.20 | 50.00% | 172 |
| cash_runway_years | 126 | 0.008 | 0.44 | 0.33 | 53.85% | 169 |
| cop_at | 21 | -0.003 | -0.24 | -0.24 | 48.35% | 182 |
| cop_at | 63 | -0.019 | -0.93 | -1.18 | 47.78% | 180 |
| cop_at | 126 | -0.032 | -1.10 | -1.07 | 45.20% | 177 |
| dist_52w_high | 21 | 0.042 | 2.54 | 2.53 | 57.69% | 182 |
| dist_52w_high | 63 | 0.062 | 3.19 | 2.73 | 63.89% | 180 |
| dist_52w_high | 126 | 0.084 | 3.26 | 3.19 | 75.14% | 177 |
| droe | 21 | -0.000 | -0.03 | -0.03 | 50.28% | 181 |
| droe | 63 | -0.005 | -0.34 | 0.38 | 48.60% | 179 |
| droe | 126 | -0.017 | -0.92 | -0.69 | 46.02% | 176 |
| ear_3d | 21 | 0.002 | 0.31 | 0.30 | 49.45% | 182 |
| ear_3d | 63 | -0.001 | -0.12 | 0.08 | 52.22% | 180 |
| ear_3d | 126 | -0.001 | -0.06 | 0.38 | 49.72% | 177 |
| ebit_ev | 21 | 0.003 | 0.14 | 0.15 | 50.00% | 182 |
| ebit_ev | 63 | -0.017 | -0.65 | -0.97 | 46.11% | 180 |
| ebit_ev | 126 | -0.020 | -0.57 | -0.45 | 49.15% | 177 |
| gross_profitability | 21 | 0.004 | 0.36 | 0.36 | 52.75% | 182 |
| gross_profitability | 63 | -0.011 | -0.61 | -0.49 | 40.00% | 180 |
| gross_profitability | 126 | -0.004 | -0.14 | 0.05 | 42.37% | 177 |
| idio_vol_60d | 21 | 0.053 | 2.96 | 2.98 | 59.89% | 182 |
| idio_vol_60d | 63 | 0.077 | 3.44 | 2.82 | 64.44% | 180 |
| idio_vol_60d | 126 | 0.113 | 3.80 | 3.31 | 74.58% | 177 |
| max_ret_21d | 21 | 0.042 | 2.64 | 2.64 | 58.79% | 182 |
| max_ret_21d | 63 | 0.067 | 3.33 | 2.39 | 60.56% | 180 |
| max_ret_21d | 126 | 0.092 | 3.40 | 2.49 | 70.62% | 177 |
| mom_12_1 | 21 | 0.008 | 0.65 | 0.67 | 49.45% | 182 |
| mom_12_1 | 63 | 0.012 | 0.83 | 0.91 | 55.00% | 180 |
| mom_12_1 | 126 | 0.017 | 0.83 | 0.99 | 57.06% | 177 |
| net_debt_ebitda | 21 | -0.013 | -0.67 | -0.72 | 50.55% | 182 |
| net_debt_ebitda | 63 | -0.034 | -1.29 | -1.26 | 48.33% | 180 |
| net_debt_ebitda | 126 | -0.053 | -1.56 | -1.29 | 44.63% | 177 |
| ocf_ev | 21 | 0.013 | 0.63 | 0.68 | 51.10% | 182 |
| ocf_ev | 63 | 0.008 | 0.27 | -0.26 | 51.67% | 180 |
| ocf_ev | 126 | 0.009 | 0.21 | 0.02 | 55.93% | 177 |
| oil_beta_trend | 21 | 0.008 | 0.33 | 0.33 | 53.85% | 182 |
| oil_beta_trend | 63 | -0.019 | -0.58 | -0.02 | 47.78% | 180 |
| oil_beta_trend | 126 | -0.015 | -0.41 | -0.66 | 48.02% | 177 |
| profitable_growth | 21 | — | — | -0.44 | 40.00% | 5 |
| profitable_growth | 63 | — | — | — | 40.00% | 5 |
| profitable_growth | 126 | — | — | — | 20.00% | 5 |
| share_issuance | 21 | 0.035 | 3.92 | 3.92 | 58.79% | 182 |
| share_issuance | 63 | 0.049 | 4.15 | 2.83 | 66.11% | 180 |
| share_issuance | 126 | 0.070 | 4.81 | 3.15 | 77.40% | 177 |
| sue | 21 | -0.000 | -0.00 | -0.00 | 50.56% | 178 |
| sue | 63 | -0.005 | -0.36 | 0.43 | 49.43% | 176 |
| sue | 126 | 0.001 | 0.06 | 0.56 | 46.82% | 173 |
| sue_announce | 21 | 0.018 | 1.83 | 1.79 | 54.95% | 182 |
| sue_announce | 63 | 0.029 | 2.26 | 1.72 | 57.78% | 180 |
| sue_announce | 126 | 0.039 | 2.55 | 2.37 | 64.41% | 177 |

### 7.4 Tek değişkenli sıralama (EW; üst − alt = `mimic_`)

| Faktör | Ufuk | Port. | mimic EW | t | mimic VW | Üst − ort. | t | Monoton |
|---|---|---|---|---|---|---|---|---|
| asset_growth | 21 | 5 | 0.70% | 2.12 | -0.08% | 0.47% | 2.04 | ✔ |
| asset_growth | 63 | 5 | 1.02% | 1.26 | 0.42% | 0.73% | 1.59 | ✘ |
| asset_growth | 126 | 5 | 1.77% | 1.35 | 1.79% | 0.93% | 1.28 | ✘ |
| capex_at | 21 | 5 | 0.61% | 2.43 | -0.34% | 0.13% | 0.80 | ✘ |
| capex_at | 63 | 5 | 2.21% | 3.11 | 0.86% | 0.71% | 1.75 | ✘ |
| capex_at | 126 | 5 | 3.96% | 2.92 | 1.88% | 0.88% | 1.28 | ✘ |
| cash_runway_years | 21 | 5 | -0.89% | -1.51 | -0.01% | 0.02% | 0.06 | ✘ |
| cash_runway_years | 63 | 5 | -2.52% | -1.67 | -1.18% | -0.09% | -0.11 | ✘ |
| cash_runway_years | 126 | 5 | -3.39% | -1.48 | -5.58% | -0.65% | -0.51 | ✘ |
| cop_at | 21 | 5 | -0.06% | -0.17 | 0.30% | -0.08% | -0.49 | ✘ |
| cop_at | 63 | 5 | -0.69% | -0.86 | 0.26% | -0.59% | -1.40 | ✘ |
| cop_at | 126 | 5 | -1.69% | -1.00 | 0.96% | -1.37% | -1.53 | ✘ |
| dist_52w_high | 21 | 5 | 0.19% | 0.32 | 0.44% | -0.06% | -0.22 | ✘ |
| dist_52w_high | 63 | 5 | 0.53% | 0.41 | 1.15% | -0.10% | -0.19 | ✘ |
| dist_52w_high | 126 | 5 | 1.39% | 0.56 | 1.17% | 0.39% | 0.38 | ✘ |
| droe | 21 | 5 | -0.19% | -0.41 | -0.04% | -0.16% | -0.50 | ✘ |
| droe | 63 | 5 | -0.49% | -0.41 | -0.20% | -0.23% | -0.29 | ✘ |
| droe | 126 | 5 | -0.47% | -0.19 | -1.35% | 0.65% | 0.42 | ✘ |
| ear_3d | 21 | 5 | -0.29% | -1.01 | -0.63% | -0.09% | -0.54 | ✘ |
| ear_3d | 63 | 5 | -0.36% | -0.67 | -1.50% | -0.06% | -0.19 | ✘ |
| ear_3d | 126 | 5 | 0.55% | 0.59 | 1.07% | 0.40% | 0.67 | ✘ |
| ebit_ev | 21 | 5 | -0.41% | -0.73 | -0.34% | -0.05% | -0.17 | ✘ |
| ebit_ev | 63 | 5 | -2.05% | -1.44 | -1.50% | -1.01% | -1.39 | ✘ |
| ebit_ev | 126 | 5 | -4.45% | -1.69 | -3.67% | -2.08% | -1.49 | ✘ |
| gross_profitability | 21 | 5 | 0.13% | 0.33 | -0.09% | 0.03% | 0.17 | ✘ |
| gross_profitability | 63 | 5 | -0.01% | -0.01 | -0.27% | -0.11% | -0.21 | ✘ |
| gross_profitability | 126 | 5 | 0.35% | 0.19 | 0.48% | -0.16% | -0.16 | ✘ |
| idio_vol_60d | 21 | 5 | -0.17% | -0.25 | 0.57% | 0.11% | 0.29 | ✘ |
| idio_vol_60d | 63 | 5 | -0.78% | -0.51 | 0.48% | 0.04% | 0.05 | ✘ |
| idio_vol_60d | 126 | 5 | 0.00% | 0.00 | 0.29% | 0.23% | 0.14 | ✘ |
| max_ret_21d | 21 | 5 | -0.21% | -0.36 | 0.26% | 0.05% | 0.15 | ✘ |
| max_ret_21d | 63 | 5 | -0.78% | -0.58 | 0.95% | -0.00% | -0.00 | ✘ |
| max_ret_21d | 126 | 5 | -0.58% | -0.25 | -0.52% | -0.18% | -0.12 | ✘ |
| mom_12_1 | 21 | 5 | 0.29% | 0.73 | 0.04% | -0.10% | -0.46 | ✘ |
| mom_12_1 | 63 | 5 | 1.07% | 1.16 | -0.02% | 0.42% | 0.80 | ✘ |
| mom_12_1 | 126 | 5 | 1.53% | 0.80 | -0.47% | 0.73% | 0.75 | ✘ |
| net_debt_ebitda | 21 | 5 | 0.24% | 0.53 | 0.21% | 0.15% | 0.49 | ✘ |
| net_debt_ebitda | 63 | 5 | 0.26% | 0.23 | -0.16% | 0.19% | 0.25 | ✘ |
| net_debt_ebitda | 126 | 5 | 0.17% | 0.08 | -1.02% | 0.18% | 0.13 | ✘ |
| ocf_ev | 21 | 5 | 0.46% | 0.71 | 0.57% | 0.08% | 0.19 | ✘ |
| ocf_ev | 63 | 5 | 0.60% | 0.39 | 0.85% | -0.28% | -0.29 | ✘ |
| ocf_ev | 126 | 5 | 0.41% | 0.12 | 1.13% | -0.99% | -0.46 | ✘ |
| oil_beta_trend | 21 | 5 | 0.44% | 0.57 | 0.71% | 0.32% | 0.80 | ✘ |
| oil_beta_trend | 63 | 5 | -0.45% | -0.25 | 0.46% | 0.17% | 0.16 | ✘ |
| oil_beta_trend | 126 | 5 | 0.14% | 0.05 | 1.49% | 0.55% | 0.30 | ✘ |
| profitable_growth | 21 | 3 | — | — | — | — | — | ✘ |
| profitable_growth | 63 | 3 | — | — | — | — | — | ✘ |
| profitable_growth | 126 | 3 | — | — | — | — | — | ✘ |
| share_issuance | 21 | 5 | 0.08% | 0.23 | 0.72% | 0.07% | 0.41 | ✘ |
| share_issuance | 63 | 5 | -0.43% | -0.47 | 0.99% | 0.03% | 0.07 | ✘ |
| share_issuance | 126 | 5 | -0.09% | -0.06 | 1.88% | 0.45% | 0.67 | ✘ |
| sue | 21 | 5 | -0.40% | -0.93 | -0.39% | -0.10% | -0.39 | ✘ |
| sue | 63 | 5 | -0.89% | -0.95 | -1.31% | -0.26% | -0.48 | ✘ |
| sue | 126 | 5 | -0.10% | -0.07 | -1.81% | 0.94% | 1.18 | ✘ |
| sue_announce | 21 | 5 | 0.28% | 0.75 | -0.01% | 0.15% | 0.81 | ✘ |
| sue_announce | 63 | 5 | 1.17% | 1.48 | 0.27% | 0.26% | 0.57 | ✘ |
| sue_announce | 126 | 5 | 1.85% | 1.50 | -0.67% | 0.74% | 1.04 | ✘ |

### 7.4 Alfalar (21 seans, aylık; NW t)

Üst portföy RF üzeri; `mimic_ew` ham fark.

| Faktör | Seri | capm t | ff3 t | carhart4 t | ff5_mom t |
|---|---|---|---|---|---|
| asset_growth | mimic_ew | 1.79 | 1.84 | 1.96 | 1.89 |
| asset_growth | top_ew | 0.41 | 0.99 | 1.06 | 1.20 |
| capex_at | mimic_ew | 1.31 | 2.24 | 1.99 | 2.43 |
| capex_at | top_ew | 0.12 | 0.79 | 0.77 | 1.04 |
| cash_runway_years | mimic_ew | -1.52 | -1.68 | -1.50 | -1.42 |
| cash_runway_years | top_ew | -0.05 | 0.46 | 0.44 | 0.73 |
| cop_at | mimic_ew | -0.57 | -0.80 | -0.30 | -0.52 |
| cop_at | top_ew | -0.48 | -0.49 | -0.33 | -0.50 |
| dist_52w_high | mimic_ew | 1.98 | 1.63 | 1.21 | 0.90 |
| dist_52w_high | top_ew | 1.09 | 1.28 | 0.78 | 0.60 |
| droe | mimic_ew | -0.30 | -0.20 | -0.25 | -0.39 |
| droe | top_ew | 0.47 | 0.89 | 0.76 | 0.85 |
| ear_3d | mimic_ew | -0.67 | -0.67 | -0.48 | -0.62 |
| ear_3d | top_ew | -0.76 | -0.28 | -0.24 | -0.09 |
| ebit_ev | mimic_ew | -0.69 | -0.86 | -0.50 | -1.03 |
| ebit_ev | top_ew | -0.80 | -1.05 | -0.83 | -1.30 |
| gross_profitability | mimic_ew | 1.54 | 1.74 | 1.76 | 1.83 |
| gross_profitability | top_ew | 0.72 | 0.93 | 0.96 | 0.92 |
| idio_vol_60d | mimic_ew | 0.94 | 0.39 | 0.34 | -0.12 |
| idio_vol_60d | top_ew | 1.92 | 1.72 | 1.58 | 1.17 |
| max_ret_21d | mimic_ew | 0.67 | -0.02 | 0.03 | -0.53 |
| max_ret_21d | top_ew | 0.91 | 0.69 | 0.54 | 0.12 |
| mom_12_1 | mimic_ew | 1.31 | 1.18 | 0.40 | 0.58 |
| mom_12_1 | top_ew | -0.32 | 0.01 | -0.43 | -0.12 |
| net_debt_ebitda | mimic_ew | -0.56 | -0.47 | -0.64 | -0.84 |
| net_debt_ebitda | top_ew | -0.66 | -0.78 | -0.90 | -1.12 |
| ocf_ev | mimic_ew | -0.04 | -0.17 | 0.23 | -0.07 |
| ocf_ev | top_ew | -0.57 | -0.77 | -0.60 | -0.85 |
| oil_beta_trend | mimic_ew | 1.96 | 2.03 | 1.74 | 1.82 |
| oil_beta_trend | top_ew | 0.52 | 0.65 | 0.64 | 0.47 |
| share_issuance | mimic_ew | 0.68 | 0.03 | 0.21 | -0.36 |
| share_issuance | top_ew | 0.22 | 0.23 | 0.30 | -0.04 |
| sue | mimic_ew | -1.45 | -1.47 | -1.27 | -1.39 |
| sue | top_ew | 0.12 | 0.53 | 0.38 | 0.35 |
| sue_announce | mimic_ew | 1.00 | 0.82 | 0.32 | 0.35 |
| sue_announce | top_ew | 0.48 | 0.75 | 0.45 | 0.34 |

### 7.5 Bağımlı iki değişkenli sıralama (tema skoru terciliyle kontrol)

| Faktör | Ufuk | Ort. fark | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.46% | 1.94 |
| asset_growth | 63 | 0.82% | 1.41 |
| asset_growth | 126 | 1.32% | 1.31 |
| capex_at | 21 | 0.23% | 1.24 |
| capex_at | 63 | 1.25% | 2.40 |
| capex_at | 126 | 2.34% | 2.14 |
| cash_runway_years | 21 | -0.65% | -1.51 |
| cash_runway_years | 63 | -3.68% | -3.02 |
| cash_runway_years | 126 | -5.01% | -2.34 |
| cop_at | 21 | -0.06% | -0.14 |
| cop_at | 63 | -0.64% | -0.67 |
| cop_at | 126 | -1.32% | -0.64 |
| dist_52w_high | 21 | 0.44% | 1.16 |
| dist_52w_high | 63 | 0.67% | 0.84 |
| dist_52w_high | 126 | 1.43% | 0.97 |
| droe | 21 | 0.03% | 0.12 |
| droe | 63 | -0.04% | -0.05 |
| droe | 126 | -0.83% | -0.65 |
| ear_3d | 21 | -0.14% | -0.68 |
| ear_3d | 63 | -0.42% | -1.04 |
| ear_3d | 126 | -0.05% | -0.08 |
| ebit_ev | 21 | -0.43% | -0.96 |
| ebit_ev | 63 | -1.48% | -1.36 |
| ebit_ev | 126 | -2.88% | -1.36 |
| gross_profitability | 21 | -0.02% | -0.08 |
| gross_profitability | 63 | -0.43% | -0.73 |
| gross_profitability | 126 | 0.05% | 0.04 |
| idio_vol_60d | 21 | -0.17% | -0.40 |
| idio_vol_60d | 63 | -0.80% | -0.81 |
| idio_vol_60d | 126 | -0.22% | -0.12 |
| max_ret_21d | 21 | -0.22% | -0.61 |
| max_ret_21d | 63 | -0.66% | -0.76 |
| max_ret_21d | 126 | -0.45% | -0.29 |
| mom_12_1 | 21 | 0.34% | 1.18 |
| mom_12_1 | 63 | 1.00% | 1.44 |
| mom_12_1 | 126 | 1.42% | 0.99 |
| net_debt_ebitda | 21 | 0.06% | 0.13 |
| net_debt_ebitda | 63 | -0.28% | -0.26 |
| net_debt_ebitda | 126 | -0.38% | -0.18 |
| ocf_ev | 21 | 0.53% | 0.92 |
| ocf_ev | 63 | 1.04% | 0.74 |
| ocf_ev | 126 | 1.54% | 0.52 |
| oil_beta_trend | 21 | 0.37% | 0.70 |
| oil_beta_trend | 63 | 0.09% | 0.07 |
| oil_beta_trend | 126 | 1.04% | 0.46 |
| share_issuance | 21 | 0.09% | 0.40 |
| share_issuance | 63 | -0.25% | -0.41 |
| share_issuance | 126 | -0.41% | -0.36 |
| sue | 21 | -0.19% | -0.71 |
| sue | 63 | -0.27% | -0.40 |
| sue | 126 | -0.28% | -0.22 |
| sue_announce | 21 | 0.43% | 1.75 |
| sue_announce | 63 | 1.03% | 1.91 |
| sue_announce | 126 | 2.25% | 2.38 |

### 7.6 Fama-MacBeth (tek faktör + β, ln(MktCap); NW t)

| Faktör | Ufuk | OLS rank-normal t | OLS ham t | WLS √MktCap t | 1 std etkisi | Ort. R² |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 1.94 | 1.37 | 0.48 | 0.19% | 7.71% |
| asset_growth | 63 | 1.07 | 1.58 | 0.09 | 0.27% | 6.12% |
| asset_growth | 126 | 0.91 | 1.57 | 0.29 | 0.41% | 5.55% |
| capex_at | 21 | 1.44 | 1.06 | 1.38 | 0.13% | 7.17% |
| capex_at | 63 | 2.52 | 2.00 | 2.23 | 0.62% | 5.61% |
| capex_at | 126 | 2.49 | 2.33 | 2.32 | 1.16% | 5.06% |
| cash_runway_years | 21 | -1.78 | -1.37 | -0.34 | -0.30% | 5.16% |
| cash_runway_years | 63 | -2.13 | -1.53 | -0.78 | -1.01% | 4.99% |
| cash_runway_years | 126 | -1.78 | -0.68 | -0.90 | -1.34% | 4.77% |
| cop_at | 21 | 0.01 | -0.43 | 0.99 | 0.00% | 12.28% |
| cop_at | 63 | -0.61 | -1.05 | 0.48 | -0.17% | 10.72% |
| cop_at | 126 | -0.82 | -1.30 | 0.18 | -0.48% | 10.36% |
| dist_52w_high | 21 | 0.94 | 1.50 | 0.45 | 0.15% | 8.06% |
| dist_52w_high | 63 | 1.22 | 1.80 | 0.73 | 0.42% | 6.22% |
| dist_52w_high | 126 | 1.35 | 1.80 | 0.85 | 0.81% | 5.37% |
| droe | 21 | 0.41 | -0.77 | -0.12 | 0.05% | 10.93% |
| droe | 63 | 0.40 | -0.72 | -0.43 | 0.12% | 10.74% |
| droe | 126 | -0.01 | -1.36 | -0.72 | -0.00% | 10.63% |
| ear_3d | 21 | -0.66 | -0.68 | -0.49 | -0.05% | 7.28% |
| ear_3d | 63 | -0.57 | -0.80 | -0.51 | -0.09% | 5.66% |
| ear_3d | 126 | 0.21 | 0.46 | 0.40 | 0.06% | 5.00% |
| ebit_ev | 21 | -0.15 | -0.15 | 0.33 | -0.02% | 20.10% |
| ebit_ev | 63 | -0.45 | -0.50 | -0.17 | -0.18% | 18.78% |
| ebit_ev | 126 | -0.49 | -0.84 | -0.15 | -0.33% | 18.43% |
| gross_profitability | 21 | 0.75 | 0.04 | 0.59 | 0.08% | 9.81% |
| gross_profitability | 63 | 0.17 | -0.29 | 0.11 | 0.05% | 8.88% |
| gross_profitability | 126 | 0.17 | -0.28 | 0.13 | 0.10% | 8.10% |
| idio_vol_60d | 21 | -0.19 | -0.41 | -0.28 | -0.03% | 7.58% |
| idio_vol_60d | 63 | -0.53 | -0.72 | -0.46 | -0.22% | 6.02% |
| idio_vol_60d | 126 | 0.43 | 0.18 | -0.05 | 0.30% | 5.31% |
| max_ret_21d | 21 | -0.15 | -0.32 | 0.12 | -0.02% | 7.31% |
| max_ret_21d | 63 | -0.35 | -1.03 | -0.15 | -0.11% | 5.75% |
| max_ret_21d | 126 | -0.06 | -0.32 | -0.53 | -0.03% | 5.13% |
| mom_12_1 | 21 | 1.98 | 0.95 | 1.72 | 0.21% | 7.69% |
| mom_12_1 | 63 | 2.36 | 1.75 | 2.35 | 0.61% | 6.00% |
| mom_12_1 | 126 | 1.80 | 1.55 | 1.76 | 0.97% | 5.43% |
| net_debt_ebitda | 21 | 0.49 | 0.91 | 0.46 | 0.06% | 19.39% |
| net_debt_ebitda | 63 | 0.37 | 0.74 | -0.16 | 0.12% | 17.90% |
| net_debt_ebitda | 126 | 0.56 | 0.50 | -0.29 | 0.32% | 17.49% |
| ocf_ev | 21 | 0.85 | 1.17 | 1.28 | 0.14% | 20.17% |
| ocf_ev | 63 | 0.39 | 0.56 | 0.71 | 0.16% | 18.51% |
| ocf_ev | 126 | 0.22 | 0.20 | 0.60 | 0.18% | 18.18% |
| oil_beta_trend | 21 | -0.11 | 0.21 | 0.36 | -0.03% | 15.78% |
| oil_beta_trend | 63 | -0.58 | -0.15 | -0.37 | -0.32% | 15.76% |
| oil_beta_trend | 126 | -0.23 | 0.21 | -0.21 | -0.23% | 15.91% |
| share_issuance | 21 | 1.19 | 0.61 | 1.24 | 0.11% | 7.38% |
| share_issuance | 63 | 0.22 | -0.14 | 0.58 | 0.05% | 5.84% |
| share_issuance | 126 | 0.03 | -0.23 | 0.68 | 0.02% | 5.30% |
| sue | 21 | -0.24 | -0.37 | -0.46 | -0.03% | 10.06% |
| sue | 63 | 0.25 | -0.03 | -0.45 | 0.06% | 9.59% |
| sue | 126 | 0.31 | 0.20 | -0.66 | 0.15% | 9.77% |
| sue_announce | 21 | 1.58 | 1.34 | 1.79 | 0.14% | 10.66% |
| sue_announce | 63 | 2.16 | 1.83 | 1.97 | 0.45% | 8.40% |
| sue_announce | 126 | 2.03 | 1.93 | 1.66 | 0.78% | 7.82% |

Tüm faktörlü model (kapsama ≥ %50, eksiksiz satırlar):

| Ufuk | Faktör | Katsayı | NW t | Ort. düz. R² |
|---|---|---|---|---|
| 21 | asset_growth | -0.28% | -1.75 | 20.01% |
| 21 | capex_at | 0.24% | 1.38 | 20.01% |
| 21 | cash_runway_years | -0.00% | -0.00 | 20.01% |
| 21 | cop_at | 0.33% | 1.43 | 20.01% |
| 21 | dist_52w_high | -0.32% | -1.40 | 20.01% |
| 21 | droe | 0.20% | 1.15 | 20.01% |
| 21 | ear_3d | -0.04% | -0.30 | 20.01% |
| 21 | ebit_ev | -0.32% | -1.70 | 20.01% |
| 21 | gross_profitability | -0.20% | -1.19 | 20.01% |
| 21 | idio_vol_60d | -0.10% | -0.42 | 20.01% |
| 21 | max_ret_21d | 0.29% | 1.81 | 20.01% |
| 21 | mom_12_1 | 0.40% | 2.02 | 20.01% |
| 21 | net_debt_ebitda | 0.15% | 1.06 | 20.01% |
| 21 | ocf_ev | 0.15% | 0.66 | 20.01% |
| 21 | profitable_growth | -0.16% | -0.86 | 20.01% |
| 21 | share_issuance | 0.12% | 0.82 | 20.01% |
| 21 | sue | -0.18% | -1.15 | 20.01% |
| 63 | asset_growth | -0.66% | -1.61 | 17.78% |
| 63 | capex_at | 0.67% | 1.56 | 17.78% |
| 63 | cash_runway_years | 0.16% | 0.25 | 17.78% |
| 63 | cop_at | 0.40% | 0.78 | 17.78% |
| 63 | dist_52w_high | -0.41% | -1.00 | 17.78% |
| 63 | droe | 0.02% | 0.05 | 17.78% |
| 63 | ear_3d | 0.19% | 0.72 | 17.78% |
| 63 | ebit_ev | -0.83% | -2.17 | 17.78% |
| 63 | gross_profitability | -0.45% | -1.09 | 17.78% |
| 63 | idio_vol_60d | -0.39% | -0.73 | 17.78% |
| 63 | max_ret_21d | 0.45% | 1.44 | 17.78% |
| 63 | mom_12_1 | 0.92% | 1.90 | 17.78% |
| 63 | net_debt_ebitda | 0.30% | 0.86 | 17.78% |
| 63 | ocf_ev | 0.45% | 0.83 | 17.78% |
| 63 | profitable_growth | -0.34% | -0.75 | 17.78% |
| 63 | share_issuance | 0.23% | 0.70 | 17.78% |
| 63 | sue | -0.15% | -0.45 | 17.78% |
| 126 | asset_growth | -1.09% | -1.40 | 16.36% |
| 126 | capex_at | 0.93% | 1.16 | 16.36% |
| 126 | cash_runway_years | 1.29% | 1.17 | 16.36% |
| 126 | cop_at | 0.46% | 0.46 | 16.36% |
| 126 | dist_52w_high | -1.69% | -2.11 | 16.36% |
| 126 | droe | -0.48% | -0.78 | 16.36% |
| 126 | ear_3d | 0.49% | 1.35 | 16.36% |
| 126 | ebit_ev | -1.29% | -2.03 | 16.36% |
| 126 | gross_profitability | -0.88% | -1.43 | 16.36% |
| 126 | idio_vol_60d | 0.24% | 0.24 | 16.36% |
| 126 | max_ret_21d | 0.49% | 1.10 | 16.36% |
| 126 | mom_12_1 | 2.05% | 2.03 | 16.36% |
| 126 | net_debt_ebitda | 0.24% | 0.40 | 16.36% |
| 126 | ocf_ev | 0.76% | 0.74 | 16.36% |
| 126 | profitable_growth | -0.49% | -0.54 | 16.36% |
| 126 | share_issuance | 0.08% | 0.13 | 16.36% |
| 126 | sue | 0.14% | 0.22 | 16.36% |

### 7.1 Tanımlayıcı istatistikler (winsorize %0,5/%99,5; aylık değerlerin zaman ortalaması)

| Faktör | Ort. | Std | Çarp. | Bas. | P5 | Medyan | P95 | n | Ort. kayması |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.253 | 0.617 | 3.59 | 16.86 | -0.207 | 0.074 | 1.285 | 291 | 0.15 |
| capex_at | 0.051 | 0.057 | 1.98 | 5.04 | 0.001 | 0.032 | 0.168 | 275 | 0.28 |
| cash_runway_years | 6.347 | 4.167 | -0.39 | -1.66 | 0.139 | 9.618 | 10.000 | 292 | 0.08 |
| cop_at | -0.009 | 0.223 | -1.69 | 4.05 | -0.444 | 0.063 | 0.224 | 292 | 0.19 |
| dist_52w_high | -0.230 | 0.181 | -0.94 | 0.37 | -0.582 | -0.186 | -0.022 | 296 | 0.37 |
| droe | -0.004 | 0.191 | -0.02 | 12.76 | -0.235 | -0.001 | 0.214 | 263 | 0.11 |
| ear_3d | 0.005 | 0.084 | 0.34 | 2.86 | -0.122 | 0.002 | 0.142 | 272 | 0.08 |
| ebit_ev | -0.025 | 0.222 | -2.04 | 22.02 | -0.307 | 0.021 | 0.145 | 268 | 0.25 |
| gross_profitability | 0.249 | 0.198 | 0.75 | 2.69 | 0.025 | 0.208 | 0.617 | 151 | 0.16 |
| idio_vol_60d | 0.441 | 0.282 | 2.23 | 8.77 | 0.160 | 0.383 | 0.912 | 296 | 0.39 |
| max_ret_21d | 0.065 | 0.062 | 3.61 | 19.50 | 0.018 | 0.049 | 0.158 | 296 | 0.31 |
| mom_12_1 | 0.290 | 0.813 | 2.78 | 13.28 | -0.439 | 0.112 | 1.574 | 296 | 0.35 |
| net_debt_ebitda | 2.733 | 6.342 | 1.62 | 12.47 | -4.443 | 2.476 | 9.690 | 164 | 0.10 |
| ocf_ev | 0.025 | 0.165 | -1.47 | 11.34 | -0.209 | 0.050 | 0.214 | 291 | 0.23 |
| oil_beta_trend | -0.025 | 0.379 | -0.36 | 8.19 | -0.441 | -0.024 | 0.406 | 89 | 1.22 |
| profitable_growth | 1.034 | 0.412 | 0.07 | -0.58 | 0.370 | 1.019 | 1.721 | 183 | 0.04 |
| share_issuance | 0.076 | 0.204 | 3.04 | 20.27 | -0.050 | 0.016 | 0.364 | 281 | 0.16 |
| sue | -0.069 | 1.286 | -0.27 | 0.57 | -2.330 | -0.008 | 1.972 | 284 | 0.17 |
| sue_announce | 0.268 | 1.309 | 0.40 | 0.78 | -1.725 | 0.179 | 2.453 | 140 | 0.20 |

### 7.2 Korelasyon ve çoklu doğrusallık

Tam matris (alt üçgen Pearson, üst üçgen Spearman): `corr.csv`. |ρ| > 0,7 çiftleri:

| A | B | Pearson | Spearman | Not |
|---|---|---|---|---|
| cop_at | ocf_ev | 0.68 | 0.78 |  |
| ebit_ev | ocf_ev | 0.71 | 0.74 |  |
| idio_vol_60d | max_ret_21d | 0.69 | 0.79 |  |

VIF > 5: yok

Ortogonalize (tema skoru + alt tema kuklaları sonrası artık) IC:

| Faktör | Ufuk | Artık IC | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.014 | 2.05 |
| asset_growth | 63 | 0.016 | 1.56 |
| asset_growth | 126 | 0.026 | 1.95 |
| capex_at | 21 | 0.002 | 0.34 |
| capex_at | 63 | 0.005 | 0.45 |
| capex_at | 126 | 0.007 | 0.43 |
| cash_runway_years | 21 | -0.022 | -2.23 |
| cash_runway_years | 63 | -0.033 | -2.48 |
| cash_runway_years | 126 | -0.033 | -1.89 |
| cop_at | 21 | -0.012 | -1.49 |
| cop_at | 63 | -0.029 | -2.36 |
| cop_at | 126 | -0.044 | -2.29 |
| dist_52w_high | 21 | 0.021 | 2.14 |
| dist_52w_high | 63 | 0.036 | 2.89 |
| dist_52w_high | 126 | 0.045 | 2.82 |
| droe | 21 | 0.003 | 0.29 |
| droe | 63 | -0.008 | -0.49 |
| droe | 126 | -0.045 | -2.46 |
| ear_3d | 21 | 0.001 | 0.22 |
| ear_3d | 63 | -0.002 | -0.26 |
| ear_3d | 126 | -0.003 | -0.31 |
| ebit_ev | 21 | -0.014 | -1.12 |
| ebit_ev | 63 | -0.025 | -1.42 |
| ebit_ev | 126 | -0.028 | -1.29 |
| gross_profitability | 21 | -0.009 | -1.04 |
| gross_profitability | 63 | -0.032 | -2.37 |
| gross_profitability | 126 | -0.034 | -1.76 |
| idio_vol_60d | 21 | 0.029 | 2.80 |
| idio_vol_60d | 63 | 0.047 | 3.43 |
| idio_vol_60d | 126 | 0.075 | 4.31 |
| max_ret_21d | 21 | 0.018 | 1.99 |
| max_ret_21d | 63 | 0.034 | 3.02 |
| max_ret_21d | 126 | 0.052 | 3.48 |
| mom_12_1 | 21 | 0.004 | 0.50 |
| mom_12_1 | 63 | 0.001 | 0.13 |
| mom_12_1 | 126 | -0.008 | -0.47 |
| net_debt_ebitda | 21 | -0.024 | -1.65 |
| net_debt_ebitda | 63 | -0.041 | -2.18 |
| net_debt_ebitda | 126 | -0.057 | -2.26 |
| ocf_ev | 21 | 0.001 | 0.06 |
| ocf_ev | 63 | 0.000 | 0.00 |
| ocf_ev | 126 | -0.002 | -0.07 |
| oil_beta_trend | 21 | 0.001 | 0.06 |
| oil_beta_trend | 63 | -0.016 | -0.50 |
| oil_beta_trend | 126 | -0.010 | -0.28 |
| profitable_growth | 21 | — | — |
| profitable_growth | 63 | — | — |
| profitable_growth | 126 | — | — |
| share_issuance | 21 | 0.018 | 2.39 |
| share_issuance | 63 | 0.026 | 2.98 |
| share_issuance | 126 | 0.037 | 3.50 |
| sue | 21 | -0.011 | -0.97 |
| sue | 63 | -0.027 | -1.91 |
| sue | 126 | -0.039 | -2.50 |
| sue_announce | 21 | 0.013 | 1.71 |
| sue_announce | 63 | 0.019 | 2.19 |
| sue_announce | 126 | 0.023 | 2.55 |

### 7.3 Süreklilik (ρτ, aylık kesitsel sıra korelasyonu)

| Faktör | τ=1 | τ=3 | τ=6 | τ=12 |
|---|---|---|---|---|
| asset_growth | 0.91 | 0.75 | 0.55 | 0.18 |
| capex_at | 0.99 | 0.97 | 0.94 | 0.89 |
| cash_runway_years | 0.96 | 0.88 | 0.79 | 0.64 |
| cop_at | 0.98 | 0.94 | 0.89 | 0.77 |
| dist_52w_high | 0.84 | 0.66 | 0.49 | 0.30 |
| droe | 0.76 | 0.32 | 0.18 | -0.24 |
| ear_3d | 0.63 | -0.01 | 0.02 | 0.00 |
| ebit_ev | 0.97 | 0.93 | 0.84 | 0.68 |
| gross_profitability | 0.99 | 0.96 | 0.93 | 0.86 |
| idio_vol_60d | 0.94 | 0.83 | 0.81 | 0.77 |
| max_ret_21d | 0.61 | 0.60 | 0.58 | 0.56 |
| mom_12_1 | 0.89 | 0.69 | 0.43 | -0.00 |
| net_debt_ebitda | 0.98 | 0.95 | 0.91 | 0.85 |
| ocf_ev | 0.98 | 0.94 | 0.89 | 0.78 |
| oil_beta_trend | 0.65 | 0.18 | 0.01 | -0.14 |
| profitable_growth | 0.96 | 0.89 | 0.76 | 0.50 |
| share_issuance | 0.95 | 0.86 | 0.75 | 0.53 |
| sue | 0.79 | 0.40 | 0.29 | -0.07 |
| sue_announce | 0.82 | 0.47 | 0.35 | 0.03 |

### 7.8 İstikrar (126 seans IC ortalaması) ve ekonomik gerekçe

| Faktör | 2011-07..2015-12 | 2016-01..2020-12 | 2021-01..2026-09 | bull | bear | vix_high | vix_low | Neden çalışmalı | Kaynak |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.045 | 0.019 | 0.035 | 0.033 | 0.028 | 0.044 | 0.021 | aşırı yatırım / q-teorisi (−) | Cooper, Gulen & Schill (2008); Hou, Xue & Zhang (2015) |
| capex_at | -0.024 | -0.022 | -0.015 | -0.025 | 0.027 | 0.003 | -0.044 | yatırım faktörü (−) | Titman, Wei & Xie (2004); Fama & French (2015) CMA |
| cash_runway_years | -0.027 | 0.022 | 0.020 | 0.009 | -0.000 | -0.002 | 0.017 | finansal kısıt / seyreltme riski | Hadlock & Pierce (2010) — tema uyarlaması |
| cop_at | -0.056 | -0.068 | 0.025 | -0.029 | -0.055 | -0.004 | -0.060 | kalite (tahakkuksuz kârlılık) | Ball, Gerakos, Linnainmaa & Nikolaev (2016) |
| dist_52w_high | 0.086 | 0.063 | 0.102 | 0.089 | 0.036 | 0.042 | 0.127 | davranışsal (çıpalama) | George & Hwang (2004) |
| droe | -0.039 | -0.020 | 0.006 | -0.022 | 0.033 | -0.035 | 0.002 | temel momentum | Hou, Xue & Zhang (2015) q-faktör ROE |
| ear_3d | -0.007 | 0.008 | -0.004 | 0.001 | -0.015 | -0.013 | 0.013 | davranışsal (duyuru getirisi sürüklenmesi) | Chan, Jegadeesh & Lakonishok (1996) |
| ebit_ev | 0.027 | -0.075 | -0.006 | -0.017 | -0.042 | -0.034 | -0.005 | değer (risk + davranışsal) | Loughran & Wellman (2011) |
| gross_profitability | 0.020 | -0.040 | 0.011 | -0.001 | -0.031 | -0.001 | -0.006 | risk/kalite | Novy-Marx (2013) |
| idio_vol_60d | 0.118 | 0.098 | 0.123 | 0.116 | 0.083 | 0.064 | 0.163 | sınırlı arbitraj / piyango tercihi (−) | Ang, Hodrick, Xing & Zhang (2006) |
| max_ret_21d | 0.102 | 0.077 | 0.097 | 0.093 | 0.086 | 0.054 | 0.132 | piyango tercihi (−) | Bali, Cakici & Whitelaw (2011) |
| mom_12_1 | 0.037 | -0.007 | 0.022 | 0.012 | 0.063 | 0.022 | 0.011 | davranışsal (yetersiz tepki) + risk | Jegadeesh & Titman (1993); Carhart (1997) |
| net_debt_ebitda | -0.055 | -0.078 | -0.029 | -0.055 | -0.042 | -0.029 | -0.078 | kaldıraç / sıkıntı riski (−) | Campbell, Hilscher & Szilagyi (2008) |
| ocf_ev | -0.014 | -0.020 | 0.057 | 0.012 | -0.019 | 0.053 | -0.036 | değer (nakit akışı) | Lakonishok, Shleifer & Vishny (1994) |
| oil_beta_trend | 0.009 | -0.085 | 0.030 | -0.018 | 0.008 | 0.039 | -0.072 | emtia risk primi + trend | Moskowitz, Ooi & Pedersen (2012) — tema uyarlaması |
| profitable_growth | — | — | -0.196 | -0.196 | — | 0.182 | -0.291 | kalite + büyüme | Mohanram (2005) GSCORE ruhunda |
| share_issuance | 0.069 | 0.038 | 0.100 | 0.073 | 0.034 | 0.056 | 0.083 | piyasa zamanlaması (−) | Pontiff & Woodgate (2008); Daniel & Titman (2006) |
| sue | -0.031 | -0.004 | 0.031 | -0.002 | 0.029 | -0.014 | 0.016 | davranışsal (kazanç sonrası sürüklenme) | Bernard & Thomas (1989) |
| sue_announce | 0.060 | 0.034 | 0.026 | 0.042 | 0.009 | 0.022 | 0.056 | davranışsal (PEAD, duyuru tarihli) | Bernard & Thomas (1989); Livnat & Mendenhall (2006) |

## Kapsam: robotics

### 7.7 Rank IC

| Faktör | Ufuk | IC | NW t | Örtüşmesiz t | IC>0 oranı | Ay |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 0.002 | 0.04 | 0.04 | 52.38% | 63 |
| asset_growth | 63 | 0.024 | 0.51 | -0.01 | 55.74% | 61 |
| asset_growth | 126 | 0.056 | 0.93 | 0.18 | 62.07% | 58 |
| capex_at | 21 | -0.074 | -2.17 | -2.17 | 35.19% | 54 |
| capex_at | 63 | -0.113 | -1.97 | -1.97 | 30.77% | 52 |
| capex_at | 126 | -0.151 | -2.08 | -1.21 | 32.65% | 49 |
| cop_at | 21 | — | — | 3.36 | 100.00% | 5 |
| cop_at | 63 | — | — | — | 100.00% | 5 |
| cop_at | 126 | — | — | — | 80.00% | 5 |
| dist_52w_high | 21 | 0.027 | 0.69 | 0.73 | 57.58% | 66 |
| dist_52w_high | 63 | 0.009 | 0.19 | 0.78 | 54.69% | 64 |
| dist_52w_high | 126 | 0.049 | 0.99 | 0.17 | 67.21% | 61 |
| droe | 21 | — | — | 0.94 | 80.00% | 5 |
| droe | 63 | — | — | — | 80.00% | 5 |
| droe | 126 | — | — | — | 100.00% | 5 |
| ear_3d | 21 | 0.018 | 0.43 | 0.50 | 51.02% | 49 |
| ear_3d | 63 | 0.002 | 0.04 | 0.08 | 44.68% | 47 |
| ear_3d | 126 | 0.012 | 0.29 | -0.19 | 54.55% | 44 |
| gross_profitability | 21 | — | — | 2.49 | 100.00% | 5 |
| gross_profitability | 63 | — | — | — | 100.00% | 5 |
| gross_profitability | 126 | — | — | — | 80.00% | 5 |
| idio_vol_60d | 21 | 0.049 | 1.36 | 1.38 | 60.61% | 66 |
| idio_vol_60d | 63 | 0.082 | 1.70 | 2.09 | 65.62% | 64 |
| idio_vol_60d | 126 | 0.125 | 2.16 | 0.93 | 70.49% | 61 |
| max_ret_21d | 21 | 0.034 | 0.91 | 0.96 | 50.00% | 66 |
| max_ret_21d | 63 | 0.087 | 1.83 | 1.77 | 59.38% | 64 |
| max_ret_21d | 126 | 0.096 | 1.89 | 0.24 | 65.57% | 61 |
| mom_12_1 | 21 | 0.032 | 0.80 | 0.82 | 60.61% | 66 |
| mom_12_1 | 63 | 0.015 | 0.35 | -0.46 | 56.25% | 64 |
| mom_12_1 | 126 | 0.041 | 0.78 | 0.23 | 57.38% | 61 |
| profitable_growth | 21 | — | — | -0.44 | 40.00% | 5 |
| profitable_growth | 63 | — | — | — | 40.00% | 5 |
| profitable_growth | 126 | — | — | — | 20.00% | 5 |
| share_issuance | 21 | 0.098 | 2.31 | 2.51 | 61.67% | 60 |
| share_issuance | 63 | 0.128 | 2.33 | 2.29 | 70.69% | 58 |
| share_issuance | 126 | 0.133 | 1.85 | 0.70 | 67.27% | 55 |
| sue | 21 | — | — | 0.62 | 60.00% | 5 |
| sue | 63 | — | — | — | 60.00% | 5 |
| sue | 126 | — | — | — | 80.00% | 5 |

### 7.4 Tek değişkenli sıralama (EW; üst − alt = `mimic_`)

| Faktör | Ufuk | Port. | mimic EW | t | mimic VW | Üst − ort. | t | Monoton |
|---|---|---|---|---|---|---|---|---|
| asset_growth | 21 | 3 | -0.53% | -0.48 | -0.83% | -0.16% | -0.24 | ✘ |
| asset_growth | 63 | 3 | -0.03% | -0.01 | -1.45% | 0.22% | 0.15 | ✘ |
| asset_growth | 126 | 3 | 1.26% | 0.26 | -4.16% | 0.39% | 0.15 | ✘ |
| capex_at | 21 | 3 | -2.35% | -1.77 | -2.29% | -1.16% | -1.75 | ✘ |
| capex_at | 63 | 3 | -7.17% | -2.01 | -5.08% | -3.74% | -1.75 | ✘ |
| capex_at | 126 | 3 | -13.44% | -2.08 | -11.42% | -6.33% | -1.52 | ✘ |
| cop_at | 21 | 3 | — | — | — | — | — | ✘ |
| cop_at | 63 | 3 | — | — | — | — | — | ✘ |
| cop_at | 126 | 3 | — | — | — | — | — | ✘ |
| dist_52w_high | 21 | 3 | -0.19% | -0.19 | -2.47% | -0.00% | -0.00 | ✘ |
| dist_52w_high | 63 | 3 | -2.64% | -1.06 | -8.20% | -1.29% | -1.27 | ✘ |
| dist_52w_high | 126 | 3 | -2.68% | -0.60 | -16.12% | -0.64% | -0.42 | ✘ |
| droe | 21 | 3 | — | — | — | — | — | ✘ |
| droe | 63 | 3 | — | — | — | — | — | ✘ |
| droe | 126 | 3 | — | — | — | — | — | ✘ |
| ear_3d | 21 | 3 | 0.25% | 0.24 | 2.92% | 0.22% | 0.32 | ✘ |
| ear_3d | 63 | 3 | 2.12% | 0.94 | 3.95% | 1.94% | 1.26 | ✘ |
| ear_3d | 126 | 3 | 0.68% | 0.24 | 0.46% | 1.40% | 1.07 | ✘ |
| gross_profitability | 21 | 3 | — | — | — | — | — | ✘ |
| gross_profitability | 63 | 3 | — | — | — | — | — | ✘ |
| gross_profitability | 126 | 3 | — | — | — | — | — | ✘ |
| idio_vol_60d | 21 | 3 | 0.47% | 0.34 | -0.21% | 0.00% | 0.00 | ✘ |
| idio_vol_60d | 63 | 3 | -0.73% | -0.20 | -3.26% | -1.02% | -0.62 | ✘ |
| idio_vol_60d | 126 | 3 | 1.46% | 0.24 | -4.14% | -0.14% | -0.04 | ✘ |
| max_ret_21d | 21 | 3 | -0.06% | -0.05 | -2.10% | -0.60% | -0.93 | ✘ |
| max_ret_21d | 63 | 3 | 0.00% | 0.00 | -0.93% | -0.32% | -0.22 | ✘ |
| max_ret_21d | 126 | 3 | 1.79% | 0.41 | -8.62% | -0.03% | -0.01 | ✘ |
| mom_12_1 | 21 | 3 | 0.99% | 0.75 | -1.52% | 0.49% | 0.65 | ✔ |
| mom_12_1 | 63 | 3 | 1.60% | 0.62 | -5.23% | 1.30% | 0.92 | ✘ |
| mom_12_1 | 126 | 3 | 2.87% | 0.68 | -11.40% | 2.56% | 1.26 | ✘ |
| profitable_growth | 21 | 3 | — | — | — | — | — | ✘ |
| profitable_growth | 63 | 3 | — | — | — | — | — | ✘ |
| profitable_growth | 126 | 3 | — | — | — | — | — | ✘ |
| share_issuance | 21 | 3 | 1.15% | 0.80 | 1.12% | 0.72% | 1.11 | ✔ |
| share_issuance | 63 | 3 | 1.12% | 0.32 | 3.77% | 0.42% | 0.25 | ✘ |
| share_issuance | 126 | 3 | 3.34% | 0.60 | 7.44% | 1.16% | 0.33 | ✔ |
| sue | 21 | 3 | — | — | — | — | — | ✘ |
| sue | 63 | 3 | — | — | — | — | — | ✘ |
| sue | 126 | 3 | — | — | — | — | — | ✘ |

### 7.4 Alfalar (21 seans, aylık; NW t)

Üst portföy RF üzeri; `mimic_ew` ham fark.

| Faktör | Seri | capm t | ff3 t | carhart4 t | ff5_mom t |
|---|---|---|---|---|---|
| asset_growth | mimic_ew | -0.38 | -0.54 | -0.39 | -0.54 |
| asset_growth | top_ew | -0.00 | 0.40 | -0.07 | -0.10 |
| capex_at | mimic_ew | -1.88 | -1.95 | -1.85 | -1.74 |
| capex_at | top_ew | -2.22 | -1.03 | -2.32 | -2.28 |
| dist_52w_high | mimic_ew | -0.30 | -0.20 | -0.46 | -0.53 |
| dist_52w_high | top_ew | 0.08 | 0.94 | 0.18 | 0.21 |
| ear_3d | mimic_ew | 0.14 | 0.05 | 0.06 | -0.10 |
| ear_3d | top_ew | -0.25 | 0.31 | -0.26 | -0.01 |
| idio_vol_60d | mimic_ew | 0.67 | 0.08 | 0.23 | 0.18 |
| idio_vol_60d | top_ew | 0.29 | 0.79 | 0.17 | 0.23 |
| max_ret_21d | mimic_ew | 0.36 | -0.08 | 0.26 | 0.18 |
| max_ret_21d | top_ew | -0.31 | -0.13 | -0.61 | -0.62 |
| mom_12_1 | mimic_ew | 0.47 | 0.75 | 0.38 | 0.36 |
| mom_12_1 | top_ew | 0.30 | 1.02 | 0.24 | 0.32 |
| share_issuance | mimic_ew | 1.10 | 0.20 | 0.65 | 0.63 |
| share_issuance | top_ew | 1.01 | 1.83 | 1.09 | 1.04 |

### 7.5 Bağımlı iki değişkenli sıralama (tema skoru terciliyle kontrol)

| Faktör | Ufuk | Ort. fark | NW t |
|---|---|---|---|
| asset_growth | 21 | -1.49% | -0.71 |
| asset_growth | 63 | 4.24% | 1.33 |
| asset_growth | 126 | 9.78% | 1.59 |
| capex_at | 21 | -2.28% | -1.06 |
| capex_at | 63 | -3.68% | -0.40 |
| capex_at | 126 | -11.99% | -0.62 |
| dist_52w_high | 21 | 3.32% | 1.95 |
| dist_52w_high | 63 | -0.91% | -0.25 |
| dist_52w_high | 126 | -12.13% | -1.70 |
| ear_3d | 21 | -0.28% | -0.12 |
| ear_3d | 63 | 2.75% | 0.67 |
| ear_3d | 126 | -6.87% | -1.04 |
| idio_vol_60d | 21 | -2.04% | -0.62 |
| idio_vol_60d | 63 | -8.50% | -1.14 |
| idio_vol_60d | 126 | -10.09% | -0.86 |
| max_ret_21d | 21 | -1.18% | -0.45 |
| max_ret_21d | 63 | -8.37% | -1.94 |
| max_ret_21d | 126 | -6.04% | -1.95 |
| mom_12_1 | 21 | 0.43% | 0.20 |
| mom_12_1 | 63 | -2.11% | -0.50 |
| mom_12_1 | 126 | -8.11% | -0.98 |
| share_issuance | 21 | -2.00% | -0.72 |
| share_issuance | 63 | -1.68% | -0.22 |
| share_issuance | 126 | 1.02% | 0.10 |

### 7.6 Fama-MacBeth (tek faktör + β, ln(MktCap); NW t)

| Faktör | Ufuk | OLS rank-normal t | OLS ham t | WLS √MktCap t | 1 std etkisi | Ort. R² |
|---|---|---|---|---|---|---|
| asset_growth | 21 | -0.31 | -0.15 | -0.08 | -0.15% | 27.67% |
| asset_growth | 63 | 0.10 | 0.36 | -0.05 | 0.11% | 26.55% |
| asset_growth | 126 | -0.06 | 0.11 | -0.09 | -0.14% | 25.43% |
| capex_at | 21 | -1.43 | -1.47 | -1.85 | -0.95% | 25.90% |
| capex_at | 63 | -1.39 | -1.41 | -2.11 | -2.26% | 28.02% |
| capex_at | 126 | -1.55 | -1.59 | -2.34 | -5.41% | 30.05% |
| dist_52w_high | 21 | 0.47 | -0.16 | -1.23 | 0.32% | 26.10% |
| dist_52w_high | 63 | 0.03 | -0.33 | -1.20 | 0.05% | 28.20% |
| dist_52w_high | 126 | 0.25 | -0.09 | -0.75 | 0.36% | 25.13% |
| ear_3d | 21 | -0.43 | -1.64 | -0.56 | -0.24% | 26.42% |
| ear_3d | 63 | 0.40 | -0.60 | -0.33 | 0.51% | 27.69% |
| ear_3d | 126 | 0.02 | -0.31 | -0.12 | 0.04% | 24.12% |
| idio_vol_60d | 21 | -0.35 | -0.02 | -0.54 | -0.22% | 25.78% |
| idio_vol_60d | 63 | -0.39 | 0.19 | -0.92 | -0.53% | 25.86% |
| idio_vol_60d | 126 | 0.03 | 1.43 | -0.55 | 0.06% | 24.69% |
| max_ret_21d | 21 | -0.65 | -0.27 | -1.88 | -0.49% | 25.51% |
| max_ret_21d | 63 | -0.67 | 0.27 | -1.30 | -1.10% | 26.14% |
| max_ret_21d | 126 | -0.49 | 1.15 | -1.67 | -0.86% | 25.65% |
| mom_12_1 | 21 | 0.13 | 0.72 | -0.90 | 0.07% | 27.15% |
| mom_12_1 | 63 | 0.08 | 0.83 | -0.31 | 0.09% | 26.58% |
| mom_12_1 | 126 | 0.24 | 1.01 | -0.68 | 0.45% | 25.22% |
| share_issuance | 21 | 1.35 | 0.47 | 1.24 | 0.79% | 27.33% |
| share_issuance | 63 | 1.17 | 0.71 | 1.46 | 1.99% | 27.62% |
| share_issuance | 126 | 0.72 | 0.04 | 0.77 | 2.61% | 28.02% |

### 7.1 Tanımlayıcı istatistikler (winsorize %0,5/%99,5; aylık değerlerin zaman ortalaması)

| Faktör | Ort. | Std | Çarp. | Bas. | P5 | Medyan | P95 | n | Ort. kayması |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.187 | 0.387 | 1.46 | 3.84 | -0.083 | 0.080 | 0.801 | 13 | 0.42 |
| capex_at | 0.027 | 0.021 | 1.23 | 1.37 | 0.009 | 0.019 | 0.064 | 12 | 0.31 |
| cash_runway_years | 8.974 | 2.065 | -1.44 | 2.63 | 5.172 | 10.000 | 10.000 | 12 | 0.44 |
| cop_at | 0.062 | 0.116 | -0.80 | 1.34 | -0.124 | 0.083 | 0.178 | 12 | 0.46 |
| dist_52w_high | -0.203 | 0.136 | -0.73 | 0.29 | -0.413 | -0.180 | -0.052 | 13 | 0.76 |
| droe | 0.004 | 0.086 | 0.06 | 4.88 | -0.089 | 0.001 | 0.096 | 12 | 0.41 |
| ear_3d | 0.014 | 0.106 | 0.45 | 0.59 | -0.112 | 0.003 | 0.169 | 12 | 0.33 |
| ebit_ev | -0.033 | 0.238 | -1.70 | 5.10 | -0.165 | 0.023 | 0.063 | 12 | 0.84 |
| gross_profitability | 0.243 | 0.117 | 0.08 | 0.60 | 0.087 | 0.236 | 0.402 | 13 | 0.38 |
| idio_vol_60d | 0.383 | 0.175 | 0.81 | 0.62 | 0.200 | 0.344 | 0.656 | 13 | 0.71 |
| max_ret_21d | 0.061 | 0.040 | 1.26 | 2.38 | 0.026 | 0.050 | 0.127 | 13 | 0.65 |
| mom_12_1 | 0.307 | 0.567 | 0.98 | 2.54 | -0.214 | 0.198 | 1.066 | 13 | 0.60 |
| net_debt_ebitda | -0.351 | 4.557 | -0.30 | 1.60 | -6.230 | -0.358 | 5.167 | 9 | 0.37 |
| ocf_ev | 0.029 | 0.120 | -0.88 | 4.62 | -0.086 | 0.030 | 0.083 | 12 | 0.85 |
| profitable_growth | 1.155 | 0.418 | -0.25 | -0.35 | 0.588 | 1.169 | 1.676 | 10 | 0.20 |
| share_issuance | 0.040 | 0.133 | 0.67 | 5.19 | -0.056 | 0.012 | 0.221 | 12 | 0.45 |
| sue | 0.312 | 1.327 | 0.30 | 0.83 | -1.385 | 0.213 | 2.162 | 12 | 0.46 |
| sue_announce | 0.444 | 1.285 | 0.39 | 0.29 | -1.074 | 0.327 | 2.240 | 9 | 0.31 |

### 7.2 Korelasyon ve çoklu doğrusallık

Tam matris (alt üçgen Pearson, üst üçgen Spearman): `corr.csv`. |ρ| > 0,7 çiftleri:

| A | B | Pearson | Spearman | Not |
|---|---|---|---|---|
| cash_runway_years | cop_at | 0.81 | 0.68 |  |
| cash_runway_years | ebit_ev | 0.71 | 0.63 |  |
| cash_runway_years | ocf_ev | 0.75 | 0.68 |  |
| droe | sue | 0.55 | 0.74 | Spearman >> Pearson: doğrusal olmayan monoton ilişki |
| ebit_ev | ocf_ev | 0.82 | 0.85 |  |

VIF > 5: yok

Ortogonalize (tema skoru + alt tema kuklaları sonrası artık) IC:

| Faktör | Ufuk | Artık IC | NW t |
|---|---|---|---|
| asset_growth | 21 | -0.015 | -0.51 |
| asset_growth | 63 | 0.013 | 0.33 |
| asset_growth | 126 | 0.019 | 0.36 |
| capex_at | 21 | -0.048 | -1.28 |
| capex_at | 63 | -0.074 | -1.25 |
| capex_at | 126 | -0.113 | -1.82 |
| cop_at | 21 | — | — |
| cop_at | 63 | — | — |
| cop_at | 126 | — | — |
| dist_52w_high | 21 | 0.015 | 0.45 |
| dist_52w_high | 63 | 0.009 | 0.21 |
| dist_52w_high | 126 | 0.029 | 0.62 |
| droe | 21 | — | — |
| droe | 63 | — | — |
| droe | 126 | — | — |
| ear_3d | 21 | -0.004 | -0.09 |
| ear_3d | 63 | -0.028 | -0.55 |
| ear_3d | 126 | -0.013 | -0.32 |
| gross_profitability | 21 | — | — |
| gross_profitability | 63 | — | — |
| gross_profitability | 126 | — | — |
| idio_vol_60d | 21 | 0.034 | 1.02 |
| idio_vol_60d | 63 | 0.025 | 0.62 |
| idio_vol_60d | 126 | 0.035 | 0.74 |
| max_ret_21d | 21 | 0.009 | 0.29 |
| max_ret_21d | 63 | 0.062 | 1.74 |
| max_ret_21d | 126 | 0.048 | 1.05 |
| mom_12_1 | 21 | 0.018 | 0.56 |
| mom_12_1 | 63 | 0.006 | 0.17 |
| mom_12_1 | 126 | 0.033 | 0.67 |
| profitable_growth | 21 | — | — |
| profitable_growth | 63 | — | — |
| profitable_growth | 126 | — | — |
| share_issuance | 21 | 0.088 | 2.50 |
| share_issuance | 63 | 0.108 | 2.41 |
| share_issuance | 126 | 0.140 | 2.34 |
| sue | 21 | — | — |
| sue | 63 | — | — |
| sue | 126 | — | — |

### 7.3 Süreklilik (ρτ, aylık kesitsel sıra korelasyonu)

| Faktör | τ=1 | τ=3 | τ=6 | τ=12 |
|---|---|---|---|---|
| asset_growth | 0.93 | 0.78 | 0.62 | 0.35 |
| capex_at | 0.98 | 0.94 | 0.86 | 0.78 |
| cash_runway_years | 0.97 | 0.93 | 0.92 | 0.86 |
| cop_at | 0.98 | 0.95 | 0.90 | 0.81 |
| dist_52w_high | 0.76 | 0.55 | 0.43 | 0.21 |
| droe | 0.78 | 0.39 | 0.24 | 0.04 |
| ear_3d | 0.68 | -0.05 | 0.02 | -0.05 |
| ebit_ev | 0.99 | 0.98 | 0.96 | 0.95 |
| gross_profitability | 0.99 | 0.96 | 0.92 | 0.84 |
| idio_vol_60d | 0.87 | 0.69 | 0.69 | 0.64 |
| max_ret_21d | 0.41 | 0.42 | 0.36 | 0.37 |
| mom_12_1 | 0.85 | 0.65 | 0.43 | -0.06 |
| net_debt_ebitda | — | — | — | — |
| ocf_ev | 0.98 | 0.94 | 0.91 | 0.83 |
| profitable_growth | 0.85 | 0.40 | — | — |
| share_issuance | 0.96 | 0.88 | 0.76 | 0.60 |
| sue | 0.81 | 0.43 | 0.30 | 0.14 |
| sue_announce | — | — | — | — |

### 7.8 İstikrar (126 seans IC ortalaması) ve ekonomik gerekçe

| Faktör | 2011-07..2015-12 | 2016-01..2020-12 | 2021-01..2026-09 | bull | bear | vix_high | vix_low | Neden çalışmalı | Kaynak |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | — | 0.334 | 0.029 | 0.060 | 0.023 | 0.082 | 0.006 | aşırı yatırım / q-teorisi (−) | Cooper, Gulen & Schill (2008); Hou, Xue & Zhang (2015) |
| capex_at | — | 0.084 | -0.161 | -0.158 | 0.186 | -0.099 | -0.226 | yatırım faktörü (−) | Titman, Wei & Xie (2004); Fama & French (2015) CMA |
| cop_at | — | — | 0.117 | 0.117 | — | 0.314 | 0.068 | kalite (tahakkuksuz kârlılık) | Ball, Gerakos, Linnainmaa & Nikolaev (2016) |
| dist_52w_high | — | -0.401 | 0.090 | 0.056 | 0.005 | 0.010 | 0.131 | davranışsal (çıpalama) | George & Hwang (2004) |
| droe | — | — | 0.116 | 0.116 | — | 0.121 | 0.114 | temel momentum | Hou, Xue & Zhang (2015) q-faktör ROE |
| ear_3d | — | -0.144 | 0.028 | 0.017 | -0.062 | -0.049 | 0.119 | davranışsal (duyuru getirisi sürüklenmesi) | Chan, Jegadeesh & Lakonishok (1996) |
| gross_profitability | — | — | 0.185 | 0.185 | — | 0.336 | 0.147 | risk/kalite | Novy-Marx (2013) |
| idio_vol_60d | — | -0.191 | 0.153 | 0.095 | 0.319 | 0.133 | 0.107 | sınırlı arbitraj / piyango tercihi (−) | Ang, Hodrick, Xing & Zhang (2006) |
| max_ret_21d | — | -0.003 | 0.105 | 0.078 | 0.215 | 0.118 | 0.050 | piyango tercihi (−) | Bali, Cakici & Whitelaw (2011) |
| mom_12_1 | — | -0.264 | 0.069 | 0.057 | -0.061 | 0.015 | 0.096 | davranışsal (yetersiz tepki) + risk | Jegadeesh & Titman (1993); Carhart (1997) |
| profitable_growth | — | — | -0.196 | -0.196 | — | 0.182 | -0.291 | kalite + büyüme | Mohanram (2005) GSCORE ruhunda |
| share_issuance | — | -0.051 | 0.152 | 0.120 | 0.307 | 0.157 | 0.088 | piyasa zamanlaması (−) | Pontiff & Woodgate (2008); Daniel & Titman (2006) |
| sue | — | — | 0.176 | 0.176 | — | 0.189 | 0.172 | davranışsal (kazanç sonrası sürüklenme) | Bernard & Thomas (1989) |

## Kapsam: biotech

### 7.7 Rank IC

| Faktör | Ufuk | IC | NW t | Örtüşmesiz t | IC>0 oranı | Ay |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 0.006 | 0.66 | 0.66 | 50.28% | 181 |
| asset_growth | 63 | 0.004 | 0.26 | 0.48 | 50.84% | 179 |
| asset_growth | 126 | 0.013 | 0.75 | 1.08 | 47.16% | 176 |
| capex_at | 21 | -0.003 | -0.35 | -0.34 | 53.85% | 182 |
| capex_at | 63 | 0.001 | 0.06 | 0.12 | 51.67% | 180 |
| capex_at | 126 | -0.017 | -1.00 | -0.99 | 44.63% | 177 |
| cash_runway_years | 21 | 0.006 | 0.58 | 0.61 | 53.80% | 171 |
| cash_runway_years | 63 | 0.011 | 0.76 | -0.01 | 55.03% | 169 |
| cash_runway_years | 126 | 0.017 | 1.00 | 0.29 | 57.83% | 166 |
| cop_at | 21 | 0.003 | 0.27 | 0.27 | 48.90% | 182 |
| cop_at | 63 | -0.007 | -0.41 | -0.48 | 45.56% | 180 |
| cop_at | 126 | 0.003 | 0.13 | -0.45 | 48.02% | 177 |
| dist_52w_high | 21 | 0.041 | 2.91 | 2.80 | 60.99% | 182 |
| dist_52w_high | 63 | 0.070 | 4.08 | 3.65 | 63.33% | 180 |
| dist_52w_high | 126 | 0.097 | 5.03 | 5.73 | 75.71% | 177 |
| droe | 21 | 0.001 | 0.11 | 0.11 | 49.72% | 181 |
| droe | 63 | 0.000 | 0.01 | 0.55 | 49.72% | 179 |
| droe | 126 | -0.021 | -1.01 | -0.67 | 50.00% | 176 |
| ear_3d | 21 | -0.014 | -1.54 | -1.57 | 46.70% | 182 |
| ear_3d | 63 | -0.019 | -1.83 | -0.75 | 44.44% | 180 |
| ear_3d | 126 | -0.011 | -1.06 | 0.46 | 44.07% | 177 |
| gross_profitability | 21 | -0.010 | -0.78 | -0.76 | 47.80% | 182 |
| gross_profitability | 63 | -0.025 | -1.27 | -1.29 | 42.78% | 180 |
| gross_profitability | 126 | -0.014 | -0.46 | -0.38 | 42.94% | 177 |
| idio_vol_60d | 21 | 0.055 | 3.73 | 3.65 | 57.69% | 182 |
| idio_vol_60d | 63 | 0.087 | 4.74 | 3.70 | 67.78% | 180 |
| idio_vol_60d | 126 | 0.133 | 6.06 | 5.75 | 79.66% | 177 |
| max_ret_21d | 21 | 0.040 | 2.97 | 2.93 | 57.14% | 182 |
| max_ret_21d | 63 | 0.068 | 3.93 | 2.51 | 63.33% | 180 |
| max_ret_21d | 126 | 0.105 | 5.14 | 3.76 | 72.32% | 177 |
| mom_12_1 | 21 | 0.008 | 0.67 | 0.69 | 48.90% | 182 |
| mom_12_1 | 63 | 0.005 | 0.31 | 0.33 | 47.22% | 180 |
| mom_12_1 | 126 | 0.006 | 0.34 | 0.57 | 50.28% | 177 |
| share_issuance | 21 | 0.037 | 2.59 | 2.57 | 55.25% | 181 |
| share_issuance | 63 | 0.050 | 2.78 | 2.53 | 59.78% | 179 |
| share_issuance | 126 | 0.072 | 3.03 | 2.23 | 60.23% | 176 |
| sue | 21 | 0.000 | 0.01 | 0.01 | 47.19% | 178 |
| sue | 63 | -0.003 | -0.21 | 0.42 | 46.59% | 176 |
| sue | 126 | 0.001 | 0.05 | 0.39 | 53.18% | 173 |
| sue_announce | 21 | 0.017 | 1.35 | 1.23 | 52.20% | 182 |
| sue_announce | 63 | 0.038 | 2.37 | 2.16 | 56.11% | 180 |
| sue_announce | 126 | 0.059 | 2.87 | 1.57 | 67.23% | 177 |

### 7.4 Tek değişkenli sıralama (EW; üst − alt = `mimic_`)

| Faktör | Ufuk | Port. | mimic EW | t | mimic VW | Üst − ort. | t | Monoton |
|---|---|---|---|---|---|---|---|---|
| asset_growth | 21 | 5 | 0.72% | 1.52 | -0.05% | 0.49% | 1.64 | ✘ |
| asset_growth | 63 | 5 | 0.46% | 0.37 | 0.71% | 0.66% | 0.94 | ✘ |
| asset_growth | 126 | 5 | 1.71% | 0.85 | 3.19% | 1.09% | 0.91 | ✘ |
| capex_at | 21 | 5 | 0.49% | 0.89 | -0.58% | 0.31% | 0.96 | ✘ |
| capex_at | 63 | 5 | 2.81% | 2.31 | 0.55% | 1.58% | 2.02 | ✘ |
| capex_at | 126 | 5 | 3.70% | 1.72 | 0.35% | 2.54% | 2.05 | ✘ |
| cash_runway_years | 21 | 5 | -0.92% | -1.58 | 0.04% | 0.08% | 0.26 | ✘ |
| cash_runway_years | 63 | 5 | -2.29% | -1.59 | -0.05% | 0.05% | 0.06 | ✘ |
| cash_runway_years | 126 | 5 | -2.81% | -1.26 | -1.58% | -0.36% | -0.27 | ✘ |
| cop_at | 21 | 5 | -0.31% | -0.52 | 0.52% | -0.40% | -1.24 | ✘ |
| cop_at | 63 | 5 | -1.37% | -0.99 | 1.26% | -1.21% | -1.53 | ✘ |
| cop_at | 126 | 5 | -3.23% | -1.27 | 1.00% | -2.66% | -1.85 | ✘ |
| dist_52w_high | 21 | 5 | 0.79% | 1.28 | 0.98% | 0.08% | 0.27 | ✘ |
| dist_52w_high | 63 | 5 | 2.34% | 1.69 | 2.45% | 0.53% | 0.74 | ✘ |
| dist_52w_high | 126 | 5 | 4.42% | 1.99 | 5.01% | 1.41% | 1.26 | ✘ |
| droe | 21 | 3 | 0.23% | 0.60 | 0.08% | 0.04% | 0.16 | ✘ |
| droe | 63 | 3 | 0.37% | 0.44 | 0.15% | 0.08% | 0.14 | ✘ |
| droe | 126 | 3 | -0.34% | -0.29 | -1.72% | 0.47% | 0.55 | ✘ |
| ear_3d | 21 | 5 | -0.74% | -1.57 | -0.75% | -0.43% | -1.59 | ✘ |
| ear_3d | 63 | 5 | -1.28% | -1.35 | -0.66% | -0.85% | -1.56 | ✘ |
| ear_3d | 126 | 5 | -0.04% | -0.02 | 1.26% | -1.05% | -1.17 | ✘ |
| gross_profitability | 21 | 3 | -0.29% | -0.85 | 0.07% | -0.02% | -0.13 | ✘ |
| gross_profitability | 63 | 3 | -0.88% | -0.91 | 0.36% | -0.22% | -0.46 | ✘ |
| gross_profitability | 126 | 3 | -1.57% | -0.77 | 1.04% | -0.57% | -0.57 | ✘ |
| idio_vol_60d | 21 | 5 | 0.22% | 0.34 | 0.68% | 0.25% | 0.64 | ✘ |
| idio_vol_60d | 63 | 5 | 0.63% | 0.41 | 2.38% | 0.39% | 0.40 | ✘ |
| idio_vol_60d | 126 | 5 | 3.61% | 1.47 | 4.87% | 1.98% | 1.20 | ✔ |
| max_ret_21d | 21 | 5 | 0.14% | 0.22 | 1.09% | 0.21% | 0.59 | ✘ |
| max_ret_21d | 63 | 5 | 0.75% | 0.54 | 1.76% | 0.54% | 0.64 | ✘ |
| max_ret_21d | 126 | 5 | 2.51% | 1.11 | 3.92% | 1.72% | 1.18 | ✘ |
| mom_12_1 | 21 | 5 | 0.63% | 1.06 | 0.96% | -0.10% | -0.33 | ✘ |
| mom_12_1 | 63 | 5 | 1.98% | 1.40 | 2.16% | 0.57% | 0.65 | ✘ |
| mom_12_1 | 126 | 5 | 1.71% | 0.75 | 1.05% | 0.29% | 0.20 | ✘ |
| share_issuance | 21 | 5 | 0.49% | 0.79 | 0.67% | 0.38% | 1.13 | ✘ |
| share_issuance | 63 | 5 | -0.32% | -0.19 | 1.22% | 0.23% | 0.29 | ✘ |
| share_issuance | 126 | 5 | -0.73% | -0.23 | 2.59% | 0.60% | 0.39 | ✘ |
| sue | 21 | 5 | -0.33% | -0.66 | -0.20% | 0.02% | 0.07 | ✘ |
| sue | 63 | 5 | -0.47% | -0.44 | -0.60% | 0.18% | 0.28 | ✘ |
| sue | 126 | 5 | 0.23% | 0.13 | -1.08% | 1.43% | 1.49 | ✘ |
| sue_announce | 21 | 5 | 0.11% | 0.13 | -0.67% | 0.61% | 1.39 | ✘ |
| sue_announce | 63 | 5 | 1.17% | 0.79 | -0.03% | 0.46% | 0.51 | ✘ |
| sue_announce | 126 | 5 | 4.49% | 2.00 | 1.79% | 1.99% | 1.43 | ✘ |

### 7.4 Alfalar (21 seans, aylık; NW t)

Üst portföy RF üzeri; `mimic_ew` ham fark.

| Faktör | Seri | capm t | ff3 t | carhart4 t | ff5_mom t |
|---|---|---|---|---|---|
| asset_growth | mimic_ew | 1.27 | 1.38 | 1.45 | 1.30 |
| asset_growth | top_ew | 0.65 | 1.58 | 1.61 | 1.83 |
| capex_at | mimic_ew | 0.98 | 0.99 | 1.18 | 1.48 |
| capex_at | top_ew | 0.68 | 1.29 | 1.37 | 1.72 |
| cash_runway_years | mimic_ew | -0.96 | -1.26 | -1.13 | -1.28 |
| cash_runway_years | top_ew | 0.07 | 0.63 | 0.63 | 0.89 |
| cop_at | mimic_ew | 0.10 | -0.10 | 0.22 | 0.20 |
| cop_at | top_ew | 0.05 | 0.44 | 0.47 | 0.67 |
| dist_52w_high | mimic_ew | 1.71 | 1.36 | 1.63 | 1.42 |
| dist_52w_high | top_ew | 0.78 | 1.30 | 1.33 | 1.51 |
| droe | mimic_ew | 0.05 | 0.12 | 0.19 | 0.19 |
| droe | top_ew | 0.43 | 0.83 | 0.78 | 0.90 |
| ear_3d | mimic_ew | -2.07 | -2.12 | -2.03 | -1.94 |
| ear_3d | top_ew | -0.83 | -0.19 | -0.24 | 0.09 |
| gross_profitability | mimic_ew | 0.49 | 0.30 | 0.52 | 0.59 |
| gross_profitability | top_ew | 0.72 | 1.12 | 1.20 | 1.26 |
| idio_vol_60d | mimic_ew | 1.25 | 0.69 | 0.85 | 0.48 |
| idio_vol_60d | top_ew | 2.21 | 2.50 | 2.58 | 2.60 |
| max_ret_21d | mimic_ew | 1.20 | 0.71 | 0.80 | 0.31 |
| max_ret_21d | top_ew | 1.60 | 2.05 | 2.07 | 2.06 |
| mom_12_1 | mimic_ew | 1.25 | 1.22 | 1.10 | 1.11 |
| mom_12_1 | top_ew | -0.19 | 0.41 | 0.38 | 0.71 |
| share_issuance | mimic_ew | 1.11 | 0.61 | 0.80 | 0.50 |
| share_issuance | top_ew | 1.62 | 2.06 | 2.10 | 2.15 |
| sue | mimic_ew | -0.17 | -0.13 | 0.15 | 0.10 |
| sue | top_ew | 0.77 | 1.21 | 1.21 | 1.23 |
| sue_announce | mimic_ew | 0.02 | -0.29 | -0.42 | -0.45 |
| sue_announce | top_ew | 1.43 | 2.01 | 1.72 | 1.93 |

### 7.5 Bağımlı iki değişkenli sıralama (tema skoru terciliyle kontrol)

| Faktör | Ufuk | Ort. fark | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.44% | 1.22 |
| asset_growth | 63 | 0.29% | 0.31 |
| asset_growth | 126 | 0.84% | 0.53 |
| capex_at | 21 | 0.20% | 0.50 |
| capex_at | 63 | 1.62% | 1.90 |
| capex_at | 126 | 1.63% | 1.00 |
| cash_runway_years | 21 | -1.14% | -2.46 |
| cash_runway_years | 63 | -3.31% | -3.05 |
| cash_runway_years | 126 | -4.87% | -2.45 |
| cop_at | 21 | -0.51% | -1.69 |
| cop_at | 63 | -1.28% | -1.70 |
| cop_at | 126 | -1.93% | -1.42 |
| dist_52w_high | 21 | 0.60% | 1.50 |
| dist_52w_high | 63 | 1.65% | 2.02 |
| dist_52w_high | 126 | 2.57% | 1.98 |
| droe | 21 | 0.01% | 0.04 |
| droe | 63 | -0.17% | -0.22 |
| droe | 126 | -1.71% | -1.31 |
| ear_3d | 21 | -0.59% | -1.81 |
| ear_3d | 63 | -0.85% | -1.28 |
| ear_3d | 126 | -0.25% | -0.26 |
| gross_profitability | 21 | -0.31% | -1.12 |
| gross_profitability | 63 | -1.04% | -1.47 |
| gross_profitability | 126 | -1.37% | -0.94 |
| idio_vol_60d | 21 | 0.35% | 0.90 |
| idio_vol_60d | 63 | 0.04% | 0.05 |
| idio_vol_60d | 126 | 1.99% | 1.51 |
| max_ret_21d | 21 | 0.02% | 0.06 |
| max_ret_21d | 63 | -0.59% | -0.83 |
| max_ret_21d | 126 | 0.55% | 0.49 |
| mom_12_1 | 21 | 0.19% | 0.47 |
| mom_12_1 | 63 | 1.23% | 1.28 |
| mom_12_1 | 126 | 1.18% | 0.69 |
| share_issuance | 21 | 0.05% | 0.11 |
| share_issuance | 63 | -1.04% | -0.99 |
| share_issuance | 126 | -2.00% | -1.03 |
| sue | 21 | -0.10% | -0.35 |
| sue | 63 | -0.21% | -0.28 |
| sue | 126 | -0.92% | -0.69 |
| sue_announce | 21 | 0.11% | 0.25 |
| sue_announce | 63 | 0.67% | 0.71 |
| sue_announce | 126 | 1.76% | 1.15 |

### 7.6 Fama-MacBeth (tek faktör + β, ln(MktCap); NW t)

| Faktör | Ufuk | OLS rank-normal t | OLS ham t | WLS √MktCap t | 1 std etkisi | Ort. R² |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 1.65 | 1.48 | 0.48 | 0.23% | 6.96% |
| asset_growth | 63 | 0.78 | 1.34 | 0.00 | 0.29% | 5.90% |
| asset_growth | 126 | 0.78 | 1.29 | 0.35 | 0.49% | 5.44% |
| capex_at | 21 | 0.50 | -0.53 | -0.55 | 0.08% | 7.02% |
| capex_at | 63 | 1.96 | 0.83 | 0.65 | 0.74% | 5.97% |
| capex_at | 126 | 1.01 | -0.12 | 0.03 | 0.76% | 5.35% |
| cash_runway_years | 21 | -1.65 | -1.46 | -0.53 | -0.29% | 5.65% |
| cash_runway_years | 63 | -2.02 | -1.59 | -0.87 | -0.90% | 5.16% |
| cash_runway_years | 126 | -1.74 | -0.67 | -1.12 | -1.18% | 4.88% |
| cop_at | 21 | -0.39 | -1.22 | 0.18 | -0.05% | 11.54% |
| cop_at | 63 | -0.50 | -1.62 | 0.49 | -0.15% | 10.80% |
| cop_at | 126 | -0.36 | -1.34 | 0.82 | -0.19% | 10.90% |
| dist_52w_high | 21 | 0.59 | 1.39 | 0.79 | 0.13% | 7.49% |
| dist_52w_high | 63 | 1.71 | 2.35 | 1.69 | 0.77% | 6.39% |
| dist_52w_high | 126 | 1.71 | 2.25 | 1.35 | 1.29% | 5.98% |
| droe | 21 | 0.57 | -0.30 | -0.18 | 0.07% | 12.12% |
| droe | 63 | 0.72 | -0.33 | -0.09 | 0.23% | 11.87% |
| droe | 126 | -0.00 | -1.19 | -0.88 | -0.00% | 11.66% |
| ear_3d | 21 | -1.87 | -1.86 | -1.02 | -0.25% | 6.85% |
| ear_3d | 63 | -2.10 | -2.13 | -1.57 | -0.57% | 5.93% |
| ear_3d | 126 | -0.60 | -0.05 | -0.38 | -0.27% | 5.42% |
| gross_profitability | 21 | -0.98 | -1.16 | -0.43 | -0.13% | 12.73% |
| gross_profitability | 63 | -0.93 | -1.28 | 0.01 | -0.32% | 12.35% |
| gross_profitability | 126 | -0.52 | -0.89 | 0.44 | -0.40% | 12.37% |
| idio_vol_60d | 21 | 0.05 | 0.19 | 0.71 | 0.01% | 6.68% |
| idio_vol_60d | 63 | -0.23 | -0.40 | 0.61 | -0.11% | 5.91% |
| idio_vol_60d | 126 | 1.10 | 0.11 | 1.09 | 0.96% | 6.05% |
| max_ret_21d | 21 | 0.39 | 0.64 | 1.49 | 0.06% | 6.41% |
| max_ret_21d | 63 | -0.10 | -0.48 | 0.90 | -0.04% | 5.69% |
| max_ret_21d | 126 | 0.57 | -0.71 | 1.09 | 0.35% | 5.56% |
| mom_12_1 | 21 | 1.04 | 1.10 | 0.86 | 0.18% | 6.90% |
| mom_12_1 | 63 | 1.72 | 1.79 | 1.46 | 0.73% | 5.89% |
| mom_12_1 | 126 | 1.38 | 1.46 | 0.94 | 0.98% | 5.33% |
| share_issuance | 21 | 0.75 | -0.41 | 1.13 | 0.12% | 6.82% |
| share_issuance | 63 | -0.39 | -0.92 | 0.20 | -0.18% | 5.89% |
| share_issuance | 126 | -0.35 | -0.59 | 0.17 | -0.30% | 5.70% |
| sue | 21 | -0.05 | -0.35 | -0.35 | -0.01% | 10.94% |
| sue | 63 | 0.48 | 0.08 | -0.00 | 0.13% | 10.29% |
| sue | 126 | 0.39 | 0.14 | -0.44 | 0.19% | 10.50% |
| sue_announce | 21 | 0.47 | 0.62 | 0.52 | 0.08% | 11.95% |
| sue_announce | 63 | 1.23 | 1.43 | 1.22 | 0.51% | 10.76% |
| sue_announce | 126 | 1.28 | 1.86 | 0.73 | 1.00% | 11.63% |

Tüm faktörlü model (kapsama ≥ %50, eksiksiz satırlar):

| Ufuk | Faktör | Katsayı | NW t | Ort. düz. R² |
|---|---|---|---|---|
| 21 | asset_growth | -0.22% | -0.71 | 15.78% |
| 21 | capex_at | 0.32% | 1.52 | 15.78% |
| 21 | cash_runway_years | -0.32% | -0.79 | 15.78% |
| 21 | cop_at | 0.07% | 0.17 | 15.78% |
| 21 | dist_52w_high | 0.53% | 1.65 | 15.78% |
| 21 | droe | 0.19% | 0.67 | 15.78% |
| 21 | ear_3d | -0.03% | -0.16 | 15.78% |
| 21 | ebit_ev | -0.27% | -0.62 | 15.78% |
| 21 | gross_profitability | 0.19% | 0.77 | 15.78% |
| 21 | idio_vol_60d | -0.23% | -0.65 | 15.78% |
| 21 | max_ret_21d | 0.26% | 1.05 | 15.78% |
| 21 | mom_12_1 | 0.20% | 0.66 | 15.78% |
| 21 | ocf_ev | 0.24% | 0.55 | 15.78% |
| 21 | share_issuance | 0.40% | 1.60 | 15.78% |
| 21 | sue | -0.15% | -0.53 | 15.78% |
| 63 | asset_growth | -0.67% | -0.96 | 13.66% |
| 63 | capex_at | 0.97% | 1.98 | 13.66% |
| 63 | cash_runway_years | -0.22% | -0.23 | 13.66% |
| 63 | cop_at | -0.19% | -0.16 | 13.66% |
| 63 | dist_52w_high | 0.43% | 0.59 | 13.66% |
| 63 | droe | 0.29% | 0.45 | 13.66% |
| 63 | ear_3d | 0.40% | 0.84 | 13.66% |
| 63 | ebit_ev | -0.53% | -0.54 | 13.66% |
| 63 | gross_profitability | 0.42% | 0.52 | 13.66% |
| 63 | idio_vol_60d | 0.52% | 0.81 | 13.66% |
| 63 | max_ret_21d | 0.37% | 0.67 | 13.66% |
| 63 | mom_12_1 | 0.28% | 0.42 | 13.66% |
| 63 | ocf_ev | 0.52% | 0.50 | 13.66% |
| 63 | share_issuance | 0.28% | 0.48 | 13.66% |
| 63 | sue | -0.12% | -0.20 | 13.66% |
| 126 | asset_growth | -1.93% | -1.66 | 11.63% |
| 126 | capex_at | 1.44% | 1.61 | 11.63% |
| 126 | cash_runway_years | -0.85% | -0.44 | 11.63% |
| 126 | cop_at | 0.08% | 0.04 | 11.63% |
| 126 | dist_52w_high | 0.08% | 0.05 | 11.63% |
| 126 | droe | 1.57% | 0.88 | 11.63% |
| 126 | ear_3d | -0.03% | -0.03 | 11.63% |
| 126 | ebit_ev | -2.71% | -1.59 | 11.63% |
| 126 | gross_profitability | 0.90% | 0.50 | 11.63% |
| 126 | idio_vol_60d | 3.51% | 2.73 | 11.63% |
| 126 | max_ret_21d | 0.36% | 0.55 | 11.63% |
| 126 | mom_12_1 | 0.93% | 0.95 | 11.63% |
| 126 | ocf_ev | 3.55% | 1.88 | 11.63% |
| 126 | share_issuance | -0.14% | -0.12 | 11.63% |
| 126 | sue | -0.83% | -0.73 | 11.63% |

### 7.1 Tanımlayıcı istatistikler (winsorize %0,5/%99,5; aylık değerlerin zaman ortalaması)

| Faktör | Ort. | Std | Çarp. | Bas. | P5 | Medyan | P95 | n | Ort. kayması |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.392 | 0.780 | 2.74 | 9.83 | -0.248 | 0.151 | 1.890 | 140 | 0.24 |
| capex_at | 0.017 | 0.020 | 2.28 | 6.77 | 0.001 | 0.010 | 0.056 | 134 | 0.20 |
| cash_runway_years | 6.018 | 3.784 | -0.14 | -1.38 | 0.853 | 6.095 | 10.000 | 142 | 0.21 |
| cop_at | -0.122 | 0.278 | -0.94 | 1.53 | -0.607 | -0.085 | 0.220 | 142 | 0.23 |
| dist_52w_high | -0.268 | 0.185 | -0.72 | -0.02 | -0.607 | -0.237 | -0.033 | 143 | 0.46 |
| droe | -0.006 | 0.242 | -0.05 | 7.34 | -0.358 | -0.003 | 0.336 | 125 | 0.12 |
| ear_3d | 0.007 | 0.099 | 0.46 | 3.55 | -0.136 | 0.002 | 0.165 | 130 | 0.10 |
| ebit_ev | -0.101 | 0.294 | -2.83 | 18.13 | -0.414 | -0.048 | 0.090 | 133 | 0.30 |
| gross_profitability | 0.313 | 0.209 | 0.83 | 0.95 | 0.041 | 0.281 | 0.684 | 75 | 0.21 |
| idio_vol_60d | 0.543 | 0.348 | 2.45 | 10.54 | 0.193 | 0.479 | 1.093 | 143 | 0.30 |
| max_ret_21d | 0.082 | 0.088 | 3.80 | 20.52 | 0.023 | 0.060 | 0.199 | 143 | 0.23 |
| mom_12_1 | 0.422 | 0.993 | 2.57 | 10.48 | -0.453 | 0.169 | 2.094 | 143 | 0.38 |
| net_debt_ebitda | 0.461 | 8.309 | 1.01 | 6.93 | -11.357 | 0.040 | 12.170 | 43 | 0.16 |
| ocf_ev | -0.059 | 0.233 | -2.41 | 15.58 | -0.316 | -0.021 | 0.106 | 141 | 0.28 |
| profitable_growth | 1.076 | 0.417 | 0.08 | -0.52 | 0.431 | 1.062 | 1.765 | 53 | 0.05 |
| share_issuance | 0.105 | 0.191 | 2.74 | 13.15 | -0.034 | 0.045 | 0.395 | 138 | 0.25 |
| sue | -0.269 | 1.415 | -0.29 | 0.30 | -2.721 | -0.140 | 1.960 | 138 | 0.16 |
| sue_announce | 0.378 | 1.489 | 0.26 | 0.52 | -1.839 | 0.243 | 2.815 | 52 | 0.22 |

### 7.2 Korelasyon ve çoklu doğrusallık

Tam matris (alt üçgen Pearson, üst üçgen Spearman): `corr.csv`. |ρ| > 0,7 çiftleri:

| A | B | Pearson | Spearman | Not |
|---|---|---|---|---|
| cash_runway_years | cop_at | 0.85 | 0.87 |  |
| cash_runway_years | ocf_ev | 0.62 | 0.80 | Spearman >> Pearson: doğrusal olmayan monoton ilişki |
| cop_at | ebit_ev | 0.52 | 0.76 | Spearman >> Pearson: doğrusal olmayan monoton ilişki |
| cop_at | ocf_ev | 0.63 | 0.85 | Spearman >> Pearson: doğrusal olmayan monoton ilişki |
| ebit_ev | ocf_ev | 0.87 | 0.87 |  |

VIF > 5: `cop_at` (7.4), `ebit_ev` (8.9), `ocf_ev` (11.1)

Ortogonalize (tema skoru + alt tema kuklaları sonrası artık) IC:

| Faktör | Ufuk | Artık IC | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.007 | 0.79 |
| asset_growth | 63 | 0.002 | 0.19 |
| asset_growth | 126 | 0.012 | 0.75 |
| capex_at | 21 | -0.006 | -0.64 |
| capex_at | 63 | -0.005 | -0.37 |
| capex_at | 126 | -0.022 | -1.39 |
| cash_runway_years | 21 | -0.022 | -1.99 |
| cash_runway_years | 63 | -0.028 | -2.11 |
| cash_runway_years | 126 | -0.033 | -1.68 |
| cop_at | 21 | -0.011 | -0.94 |
| cop_at | 63 | -0.029 | -1.98 |
| cop_at | 126 | -0.032 | -1.45 |
| dist_52w_high | 21 | 0.020 | 1.84 |
| dist_52w_high | 63 | 0.039 | 2.96 |
| dist_52w_high | 126 | 0.048 | 3.23 |
| droe | 21 | -0.003 | -0.27 |
| droe | 63 | -0.015 | -0.89 |
| droe | 126 | -0.058 | -3.03 |
| ear_3d | 21 | -0.013 | -1.50 |
| ear_3d | 63 | -0.019 | -1.91 |
| ear_3d | 126 | -0.013 | -1.32 |
| gross_profitability | 21 | -0.019 | -1.57 |
| gross_profitability | 63 | -0.040 | -2.31 |
| gross_profitability | 126 | -0.045 | -1.64 |
| idio_vol_60d | 21 | 0.036 | 3.14 |
| idio_vol_60d | 63 | 0.060 | 4.15 |
| idio_vol_60d | 126 | 0.093 | 5.58 |
| max_ret_21d | 21 | 0.021 | 1.97 |
| max_ret_21d | 63 | 0.039 | 2.90 |
| max_ret_21d | 126 | 0.063 | 4.25 |
| mom_12_1 | 21 | -0.008 | -0.76 |
| mom_12_1 | 63 | -0.018 | -1.25 |
| mom_12_1 | 126 | -0.030 | -1.57 |
| share_issuance | 21 | 0.024 | 2.01 |
| share_issuance | 63 | 0.029 | 1.89 |
| share_issuance | 126 | 0.039 | 2.06 |
| sue | 21 | -0.015 | -1.23 |
| sue | 63 | -0.032 | -1.96 |
| sue | 126 | -0.044 | -2.31 |
| sue_announce | 21 | 0.005 | 0.45 |
| sue_announce | 63 | 0.020 | 1.51 |
| sue_announce | 126 | 0.027 | 1.58 |

### 7.3 Süreklilik (ρτ, aylık kesitsel sıra korelasyonu)

| Faktör | τ=1 | τ=3 | τ=6 | τ=12 |
|---|---|---|---|---|
| asset_growth | 0.89 | 0.69 | 0.46 | 0.05 |
| capex_at | 0.98 | 0.95 | 0.89 | 0.78 |
| cash_runway_years | 0.96 | 0.89 | 0.81 | 0.70 |
| cop_at | 0.98 | 0.93 | 0.87 | 0.76 |
| dist_52w_high | 0.83 | 0.64 | 0.47 | 0.28 |
| droe | 0.79 | 0.37 | 0.19 | -0.26 |
| ear_3d | 0.63 | -0.03 | 0.01 | 0.01 |
| ebit_ev | 0.98 | 0.93 | 0.87 | 0.75 |
| gross_profitability | 0.98 | 0.95 | 0.90 | 0.83 |
| idio_vol_60d | 0.89 | 0.71 | 0.70 | 0.68 |
| max_ret_21d | 0.46 | 0.45 | 0.44 | 0.44 |
| mom_12_1 | 0.88 | 0.68 | 0.41 | -0.03 |
| net_debt_ebitda | 0.98 | 0.94 | 0.90 | 0.84 |
| ocf_ev | 0.98 | 0.93 | 0.87 | 0.75 |
| profitable_growth | 0.97 | 0.90 | 0.79 | 0.61 |
| share_issuance | 0.95 | 0.87 | 0.76 | 0.58 |
| sue | 0.82 | 0.48 | 0.38 | 0.04 |
| sue_announce | 0.85 | 0.56 | 0.45 | 0.19 |

### 7.8 İstikrar (126 seans IC ortalaması) ve ekonomik gerekçe

| Faktör | 2011-07..2015-12 | 2016-01..2020-12 | 2021-01..2026-09 | bull | bear | vix_high | vix_low | Neden çalışmalı | Kaynak |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.035 | 0.003 | 0.003 | 0.014 | 0.003 | 0.013 | 0.012 | aşırı yatırım / q-teorisi (−) | Cooper, Gulen & Schill (2008); Hou, Xue & Zhang (2015) |
| capex_at | -0.057 | -0.040 | 0.041 | -0.023 | 0.047 | -0.007 | -0.026 | yatırım faktörü (−) | Titman, Wei & Xie (2004); Fama & French (2015) CMA |
| cash_runway_years | -0.042 | 0.029 | 0.046 | 0.020 | -0.004 | 0.017 | 0.017 | finansal kısıt / seyreltme riski | Hadlock & Pierce (2010) — tema uyarlaması |
| cop_at | -0.001 | -0.023 | 0.031 | 0.005 | -0.018 | -0.009 | 0.015 | kalite (tahakkuksuz kârlılık) | Ball, Gerakos, Linnainmaa & Nikolaev (2016) |
| dist_52w_high | 0.094 | 0.065 | 0.129 | 0.096 | 0.101 | 0.090 | 0.103 | davranışsal (çıpalama) | George & Hwang (2004) |
| droe | -0.041 | -0.029 | 0.005 | -0.028 | 0.051 | -0.045 | 0.004 | temel momentum | Hou, Xue & Zhang (2015) q-faktör ROE |
| ear_3d | -0.020 | 0.001 | -0.016 | -0.006 | -0.060 | -0.017 | -0.005 | davranışsal (duyuru getirisi sürüklenmesi) | Chan, Jegadeesh & Lakonishok (1996) |
| gross_profitability | -0.090 | 0.006 | 0.031 | -0.019 | 0.030 | -0.028 | 0.000 | risk/kalite | Novy-Marx (2013) |
| idio_vol_60d | 0.143 | 0.092 | 0.164 | 0.133 | 0.139 | 0.130 | 0.137 | sınırlı arbitraj / piyango tercihi (−) | Ang, Hodrick, Xing & Zhang (2006) |
| max_ret_21d | 0.120 | 0.064 | 0.129 | 0.102 | 0.130 | 0.105 | 0.105 | piyango tercihi (−) | Bali, Cakici & Whitelaw (2011) |
| mom_12_1 | 0.000 | 0.022 | -0.004 | -0.006 | 0.115 | 0.017 | -0.005 | davranışsal (yetersiz tepki) + risk | Jegadeesh & Titman (1993); Carhart (1997) |
| share_issuance | 0.103 | 0.036 | 0.081 | 0.080 | 0.001 | 0.062 | 0.082 | piyasa zamanlaması (−) | Pontiff & Woodgate (2008); Daniel & Titman (2006) |
| sue | -0.021 | -0.008 | 0.026 | -0.003 | 0.034 | -0.020 | 0.021 | davranışsal (kazanç sonrası sürüklenme) | Bernard & Thomas (1989) |
| sue_announce | 0.032 | 0.100 | 0.043 | 0.057 | 0.077 | 0.045 | 0.074 | davranışsal (PEAD, duyuru tarihli) | Bernard & Thomas (1989); Livnat & Mendenhall (2006) |

## Kapsam: energy

### 7.7 Rank IC

| Faktör | Ufuk | IC | NW t | Örtüşmesiz t | IC>0 oranı | Ay |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 0.024 | 1.60 | 1.67 | 54.95% | 182 |
| asset_growth | 63 | 0.044 | 2.17 | 2.21 | 62.22% | 180 |
| asset_growth | 126 | 0.071 | 2.73 | 2.32 | 68.36% | 177 |
| capex_at | 21 | 0.018 | 1.39 | 1.41 | 50.00% | 182 |
| capex_at | 63 | 0.026 | 1.29 | 1.56 | 55.00% | 180 |
| capex_at | 126 | 0.047 | 1.56 | 1.57 | 63.28% | 177 |
| cash_runway_years | 21 | -0.170 | -1.28 | -1.27 | 22.22% | 9 |
| cash_runway_years | 63 | -0.139 | -2.32 | -2.14 | 25.00% | 8 |
| cash_runway_years | 126 | -0.339 | -6.03 | — | 14.29% | 7 |
| cop_at | 21 | -0.011 | -0.53 | -0.55 | 50.00% | 182 |
| cop_at | 63 | -0.028 | -1.00 | -1.23 | 48.33% | 180 |
| cop_at | 126 | -0.049 | -1.23 | -1.20 | 45.76% | 177 |
| dist_52w_high | 21 | 0.039 | 1.49 | 1.52 | 57.14% | 182 |
| dist_52w_high | 63 | 0.042 | 1.20 | 1.06 | 53.33% | 180 |
| dist_52w_high | 126 | 0.052 | 1.03 | 0.89 | 53.67% | 177 |
| ear_3d | 21 | 0.024 | 2.39 | 2.30 | 55.49% | 182 |
| ear_3d | 63 | 0.019 | 1.50 | 0.73 | 60.00% | 180 |
| ear_3d | 126 | 0.022 | 1.34 | 0.92 | 55.93% | 177 |
| ebit_ev | 21 | 0.003 | 0.14 | 0.15 | 50.00% | 182 |
| ebit_ev | 63 | -0.017 | -0.65 | -0.97 | 46.11% | 180 |
| ebit_ev | 126 | -0.020 | -0.57 | -0.45 | 49.15% | 177 |
| gross_profitability | 21 | -0.000 | -0.03 | -0.03 | 48.35% | 182 |
| gross_profitability | 63 | -0.020 | -0.84 | -0.71 | 47.22% | 180 |
| gross_profitability | 126 | -0.023 | -0.82 | -0.90 | 38.98% | 177 |
| idio_vol_60d | 21 | 0.040 | 1.33 | 1.36 | 52.75% | 182 |
| idio_vol_60d | 63 | 0.052 | 1.29 | 1.19 | 54.44% | 180 |
| idio_vol_60d | 126 | 0.076 | 1.33 | 1.11 | 51.41% | 177 |
| max_ret_21d | 21 | 0.031 | 1.15 | 1.17 | 53.85% | 182 |
| max_ret_21d | 63 | 0.047 | 1.36 | 1.29 | 52.78% | 180 |
| max_ret_21d | 126 | 0.055 | 1.14 | 0.85 | 54.24% | 177 |
| mom_12_1 | 21 | 0.013 | 0.56 | 0.56 | 50.00% | 182 |
| mom_12_1 | 63 | 0.027 | 0.92 | 0.81 | 52.22% | 180 |
| mom_12_1 | 126 | 0.033 | 0.75 | 0.74 | 54.80% | 177 |
| net_debt_ebitda | 21 | -0.013 | -0.67 | -0.72 | 50.55% | 182 |
| net_debt_ebitda | 63 | -0.034 | -1.29 | -1.26 | 48.33% | 180 |
| net_debt_ebitda | 126 | -0.053 | -1.56 | -1.29 | 44.63% | 177 |
| ocf_ev | 21 | 0.013 | 0.63 | 0.68 | 51.10% | 182 |
| ocf_ev | 63 | 0.008 | 0.27 | -0.26 | 51.67% | 180 |
| ocf_ev | 126 | 0.009 | 0.21 | 0.02 | 55.93% | 177 |
| oil_beta_trend | 21 | 0.008 | 0.33 | 0.33 | 53.85% | 182 |
| oil_beta_trend | 63 | -0.019 | -0.58 | -0.02 | 47.78% | 180 |
| oil_beta_trend | 126 | -0.015 | -0.41 | -0.66 | 48.02% | 177 |
| share_issuance | 21 | 0.022 | 2.05 | 2.10 | 58.79% | 182 |
| share_issuance | 63 | 0.029 | 1.88 | 1.24 | 63.89% | 180 |
| share_issuance | 126 | 0.042 | 2.01 | 0.99 | 66.67% | 177 |
| sue_announce | 21 | 0.021 | 1.50 | 1.48 | 52.75% | 182 |
| sue_announce | 63 | 0.024 | 1.18 | 0.62 | 51.67% | 180 |
| sue_announce | 126 | 0.024 | 0.99 | 1.30 | 57.06% | 177 |

### 7.4 Tek değişkenli sıralama (EW; üst − alt = `mimic_`)

| Faktör | Ufuk | Port. | mimic EW | t | mimic VW | Üst − ort. | t | Monoton |
|---|---|---|---|---|---|---|---|---|
| asset_growth | 21 | 5 | 0.82% | 1.73 | 0.26% | 0.47% | 1.44 | ✘ |
| asset_growth | 63 | 5 | 2.22% | 1.92 | 0.88% | 1.35% | 1.86 | ✘ |
| asset_growth | 126 | 5 | 4.44% | 1.89 | 1.39% | 2.68% | 1.72 | ✘ |
| capex_at | 21 | 5 | 0.39% | 0.82 | 0.16% | 0.16% | 0.63 | ✘ |
| capex_at | 63 | 5 | 1.95% | 1.57 | 0.98% | 0.88% | 1.20 | ✘ |
| capex_at | 126 | 5 | 4.68% | 1.72 | 1.92% | 1.71% | 1.16 | ✘ |
| cash_runway_years | 21 | 3 | -4.44% | -1.07 | -8.67% | -3.45% | -2.77 | ✘ |
| cash_runway_years | 63 | 3 | -10.11% | -3.04 | -22.23% | -2.21% | -0.77 | ✘ |
| cash_runway_years | 126 | 3 | -25.24% | -8.70 | -43.74% | -9.06% | -8.77 | ✘ |
| cop_at | 21 | 5 | 0.05% | 0.10 | 0.22% | 0.02% | 0.07 | ✘ |
| cop_at | 63 | 5 | -0.53% | -0.43 | -0.08% | -0.40% | -0.54 | ✘ |
| cop_at | 126 | 5 | -1.84% | -0.71 | -1.06% | -1.19% | -0.76 | ✘ |
| dist_52w_high | 21 | 5 | -0.05% | -0.05 | 0.34% | 0.00% | 0.01 | ✘ |
| dist_52w_high | 63 | 5 | -0.85% | -0.42 | 0.77% | -0.27% | -0.30 | ✘ |
| dist_52w_high | 126 | 5 | -1.28% | -0.30 | 0.71% | -0.34% | -0.19 | ✘ |
| ear_3d | 21 | 5 | 0.37% | 0.98 | 0.06% | 0.23% | 1.06 | ✘ |
| ear_3d | 63 | 5 | 0.46% | 0.60 | -0.31% | 0.39% | 0.77 | ✘ |
| ear_3d | 126 | 5 | 1.65% | 1.33 | 1.98% | 1.22% | 1.30 | ✘ |
| ebit_ev | 21 | 5 | -0.41% | -0.73 | -0.34% | -0.05% | -0.17 | ✘ |
| ebit_ev | 63 | 5 | -2.05% | -1.44 | -1.50% | -1.01% | -1.39 | ✘ |
| ebit_ev | 126 | 5 | -4.45% | -1.69 | -3.67% | -2.08% | -1.49 | ✘ |
| gross_profitability | 21 | 5 | -0.12% | -0.21 | -0.97% | -0.09% | -0.23 | ✘ |
| gross_profitability | 63 | 5 | -0.17% | -0.11 | -2.64% | -0.50% | -0.52 | ✘ |
| gross_profitability | 126 | 5 | 0.23% | 0.09 | -4.02% | 0.11% | 0.06 | ✘ |
| idio_vol_60d | 21 | 5 | -0.49% | -0.48 | 0.03% | -0.14% | -0.29 | ✘ |
| idio_vol_60d | 63 | 5 | -1.76% | -0.69 | -0.55% | -0.42% | -0.37 | ✘ |
| idio_vol_60d | 126 | 5 | -2.36% | -0.48 | -0.51% | -0.76% | -0.34 | ✘ |
| max_ret_21d | 21 | 5 | -0.55% | -0.63 | -0.17% | -0.23% | -0.55 | ✘ |
| max_ret_21d | 63 | 5 | -1.67% | -0.78 | -0.09% | -0.60% | -0.61 | ✘ |
| max_ret_21d | 126 | 5 | -2.94% | -0.73 | -1.66% | -1.29% | -0.67 | ✘ |
| mom_12_1 | 21 | 5 | 0.43% | 0.58 | -0.10% | 0.50% | 1.39 | ✘ |
| mom_12_1 | 63 | 5 | 1.39% | 0.86 | 0.11% | 1.42% | 1.82 | ✘ |
| mom_12_1 | 126 | 5 | 1.44% | 0.42 | -1.37% | 1.95% | 1.34 | ✘ |
| net_debt_ebitda | 21 | 5 | 0.24% | 0.53 | 0.21% | 0.15% | 0.49 | ✘ |
| net_debt_ebitda | 63 | 5 | 0.26% | 0.23 | -0.16% | 0.19% | 0.25 | ✘ |
| net_debt_ebitda | 126 | 5 | 0.17% | 0.08 | -1.02% | 0.18% | 0.13 | ✘ |
| ocf_ev | 21 | 5 | 0.46% | 0.71 | 0.57% | 0.08% | 0.19 | ✘ |
| ocf_ev | 63 | 5 | 0.60% | 0.39 | 0.85% | -0.28% | -0.29 | ✘ |
| ocf_ev | 126 | 5 | 0.41% | 0.12 | 1.13% | -0.99% | -0.46 | ✘ |
| oil_beta_trend | 21 | 5 | 0.44% | 0.57 | 0.71% | 0.32% | 0.80 | ✘ |
| oil_beta_trend | 63 | 5 | -0.45% | -0.25 | 0.46% | 0.17% | 0.16 | ✘ |
| oil_beta_trend | 126 | 5 | 0.14% | 0.05 | 1.49% | 0.55% | 0.30 | ✘ |
| share_issuance | 21 | 5 | -0.03% | -0.08 | 0.08% | 0.11% | 0.48 | ✘ |
| share_issuance | 63 | 5 | -0.06% | -0.06 | 0.42% | 0.07% | 0.14 | ✘ |
| share_issuance | 126 | 5 | 0.87% | 0.47 | 1.44% | 0.31% | 0.29 | ✘ |
| sue_announce | 21 | 5 | 0.27% | 0.60 | 0.25% | 0.01% | 0.02 | ✘ |
| sue_announce | 63 | 5 | 0.48% | 0.51 | 0.99% | -0.26% | -0.52 | ✘ |
| sue_announce | 126 | 5 | 0.64% | 0.40 | 0.96% | 0.09% | 0.11 | ✘ |

### 7.4 Alfalar (21 seans, aylık; NW t)

Üst portföy RF üzeri; `mimic_ew` ham fark.

| Faktör | Seri | capm t | ff3 t | carhart4 t | ff5_mom t |
|---|---|---|---|---|---|
| asset_growth | mimic_ew | 1.71 | 1.69 | 1.66 | 1.67 |
| asset_growth | top_ew | 0.15 | 0.12 | 0.12 | -0.09 |
| capex_at | mimic_ew | 1.04 | 1.36 | 0.74 | 0.94 |
| capex_at | top_ew | -0.27 | -0.22 | -0.40 | -0.42 |
| cash_runway_years | mimic_ew | -1.35 | — | — | — |
| cash_runway_years | top_ew | -2.46 | — | — | — |
| cop_at | mimic_ew | -0.65 | -0.83 | -0.56 | -0.77 |
| cop_at | top_ew | -0.52 | -0.73 | -0.62 | -0.86 |
| dist_52w_high | mimic_ew | 1.54 | 1.63 | 1.18 | 1.11 |
| dist_52w_high | top_ew | 1.32 | 1.24 | 0.66 | 0.32 |
| ear_3d | mimic_ew | 1.42 | 1.41 | 1.46 | 1.11 |
| ear_3d | top_ew | -0.12 | -0.12 | -0.12 | -0.36 |
| ebit_ev | mimic_ew | -0.69 | -0.86 | -0.50 | -1.03 |
| ebit_ev | top_ew | -0.80 | -1.05 | -0.83 | -1.30 |
| gross_profitability | mimic_ew | 0.19 | -0.03 | 0.13 | -0.01 |
| gross_profitability | top_ew | -0.48 | -0.74 | -0.68 | -0.92 |
| idio_vol_60d | mimic_ew | 0.83 | 0.74 | 0.59 | 0.50 |
| idio_vol_60d | top_ew | 1.08 | 0.76 | 0.57 | 0.32 |
| max_ret_21d | mimic_ew | 0.57 | 0.39 | 0.30 | 0.16 |
| max_ret_21d | top_ew | 0.48 | 0.12 | -0.03 | -0.34 |
| mom_12_1 | mimic_ew | 1.41 | 1.24 | 0.27 | 0.58 |
| mom_12_1 | top_ew | 0.67 | 0.72 | 0.06 | 0.20 |
| net_debt_ebitda | mimic_ew | -0.56 | -0.47 | -0.64 | -0.84 |
| net_debt_ebitda | top_ew | -0.66 | -0.78 | -0.90 | -1.12 |
| ocf_ev | mimic_ew | -0.04 | -0.17 | 0.23 | -0.07 |
| ocf_ev | top_ew | -0.57 | -0.77 | -0.60 | -0.85 |
| oil_beta_trend | mimic_ew | 1.96 | 2.03 | 1.74 | 1.82 |
| oil_beta_trend | top_ew | 0.52 | 0.65 | 0.64 | 0.47 |
| share_issuance | mimic_ew | 0.01 | -0.21 | -0.05 | -0.59 |
| share_issuance | top_ew | -0.20 | -0.39 | -0.24 | -0.73 |
| sue_announce | mimic_ew | 1.27 | 1.16 | 0.73 | 0.87 |
| sue_announce | top_ew | -0.09 | -0.23 | -0.47 | -0.70 |

### 7.5 Bağımlı iki değişkenli sıralama (tema skoru terciliyle kontrol)

| Faktör | Ufuk | Ort. fark | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.68% | 1.72 |
| asset_growth | 63 | 1.93% | 2.16 |
| asset_growth | 126 | 4.20% | 2.30 |
| capex_at | 21 | 0.54% | 1.59 |
| capex_at | 63 | 2.01% | 2.23 |
| capex_at | 126 | 3.97% | 2.11 |
| cop_at | 21 | 0.01% | 0.01 |
| cop_at | 63 | -0.42% | -0.31 |
| cop_at | 126 | -1.42% | -0.50 |
| dist_52w_high | 21 | -0.18% | -0.29 |
| dist_52w_high | 63 | -0.66% | -0.46 |
| dist_52w_high | 126 | -0.74% | -0.25 |
| ear_3d | 21 | 0.31% | 1.16 |
| ear_3d | 63 | 0.37% | 0.69 |
| ear_3d | 126 | 1.26% | 1.35 |
| ebit_ev | 21 | -0.43% | -0.96 |
| ebit_ev | 63 | -1.48% | -1.36 |
| ebit_ev | 126 | -2.88% | -1.36 |
| gross_profitability | 21 | 0.21% | 0.65 |
| gross_profitability | 63 | 0.26% | 0.29 |
| gross_profitability | 126 | 1.53% | 0.89 |
| idio_vol_60d | 21 | -0.45% | -0.62 |
| idio_vol_60d | 63 | -1.33% | -0.74 |
| idio_vol_60d | 126 | -1.69% | -0.47 |
| max_ret_21d | 21 | -0.48% | -0.79 |
| max_ret_21d | 63 | -1.06% | -0.72 |
| max_ret_21d | 126 | -1.61% | -0.55 |
| mom_12_1 | 21 | 0.21% | 0.40 |
| mom_12_1 | 63 | 0.77% | 0.68 |
| mom_12_1 | 126 | 1.29% | 0.52 |
| net_debt_ebitda | 21 | 0.06% | 0.13 |
| net_debt_ebitda | 63 | -0.28% | -0.26 |
| net_debt_ebitda | 126 | -0.38% | -0.18 |
| ocf_ev | 21 | 0.53% | 0.92 |
| ocf_ev | 63 | 1.04% | 0.74 |
| ocf_ev | 126 | 1.54% | 0.52 |
| oil_beta_trend | 21 | 0.37% | 0.70 |
| oil_beta_trend | 63 | 0.09% | 0.07 |
| oil_beta_trend | 126 | 1.04% | 0.46 |
| share_issuance | 21 | -0.09% | -0.32 |
| share_issuance | 63 | -0.08% | -0.11 |
| share_issuance | 126 | 0.16% | 0.11 |
| sue_announce | 21 | 0.42% | 1.28 |
| sue_announce | 63 | 1.06% | 1.48 |
| sue_announce | 126 | 1.75% | 1.36 |

### 7.6 Fama-MacBeth (tek faktör + β, ln(MktCap); NW t)

| Faktör | Ufuk | OLS rank-normal t | OLS ham t | WLS √MktCap t | 1 std etkisi | Ort. R² |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 2.08 | 1.46 | 1.60 | 0.26% | 17.83% |
| asset_growth | 63 | 1.96 | 1.34 | 1.69 | 0.60% | 15.80% |
| asset_growth | 126 | 1.76 | 1.27 | 1.56 | 1.14% | 15.59% |
| capex_at | 21 | 0.93 | 0.32 | 1.17 | 0.13% | 18.15% |
| capex_at | 63 | 1.47 | 0.92 | 1.49 | 0.58% | 16.14% |
| capex_at | 126 | 1.44 | 1.12 | 1.34 | 1.19% | 15.92% |
| cash_runway_years | 21 | -0.79 | -1.13 | -1.51 | -1.29% | 29.59% |
| cash_runway_years | 63 | -1.64 | -2.72 | -2.76 | -3.51% | 28.99% |
| cash_runway_years | 126 | -10.59 | -3.47 | -11.83 | -10.31% | 28.97% |
| cop_at | 21 | -0.01 | 0.04 | 0.34 | -0.00% | 19.36% |
| cop_at | 63 | -0.74 | -0.89 | -0.40 | -0.27% | 17.74% |
| cop_at | 126 | -1.00 | -1.36 | -0.73 | -0.69% | 17.15% |
| dist_52w_high | 21 | 0.61 | 1.00 | 0.71 | 0.16% | 19.28% |
| dist_52w_high | 63 | 0.25 | 0.55 | 0.70 | 0.14% | 17.33% |
| dist_52w_high | 126 | 0.02 | 0.43 | 0.37 | 0.02% | 16.01% |
| ear_3d | 21 | 0.73 | 0.80 | 0.34 | 0.09% | 17.90% |
| ear_3d | 63 | 0.76 | 0.66 | 0.84 | 0.20% | 16.08% |
| ear_3d | 126 | 1.09 | 1.15 | 1.42 | 0.46% | 15.30% |
| ebit_ev | 21 | -0.15 | -0.15 | 0.33 | -0.02% | 20.10% |
| ebit_ev | 63 | -0.45 | -0.50 | -0.17 | -0.18% | 18.78% |
| ebit_ev | 126 | -0.49 | -0.84 | -0.15 | -0.33% | 18.43% |
| gross_profitability | 21 | 0.45 | -0.91 | -0.10 | 0.06% | 16.57% |
| gross_profitability | 63 | -0.18 | -1.11 | -0.60 | -0.07% | 15.47% |
| gross_profitability | 126 | -0.16 | -1.24 | -0.60 | -0.12% | 14.57% |
| idio_vol_60d | 21 | -0.67 | -0.94 | -0.17 | -0.20% | 19.19% |
| idio_vol_60d | 63 | -1.04 | -1.19 | -0.62 | -0.79% | 17.03% |
| idio_vol_60d | 126 | -1.01 | -1.06 | -0.69 | -1.33% | 16.03% |
| max_ret_21d | 21 | -0.28 | -1.07 | -0.09 | -0.05% | 18.26% |
| max_ret_21d | 63 | -0.51 | -0.88 | -0.02 | -0.22% | 15.90% |
| max_ret_21d | 126 | -1.29 | -1.28 | -0.92 | -0.92% | 15.15% |
| mom_12_1 | 21 | 1.39 | 2.06 | 1.44 | 0.30% | 20.30% |
| mom_12_1 | 63 | 1.90 | 1.91 | 2.18 | 0.95% | 18.04% |
| mom_12_1 | 126 | 1.60 | 1.85 | 1.83 | 1.46% | 16.98% |
| net_debt_ebitda | 21 | 0.49 | 0.91 | 0.46 | 0.06% | 19.39% |
| net_debt_ebitda | 63 | 0.37 | 0.74 | -0.16 | 0.12% | 17.90% |
| net_debt_ebitda | 126 | 0.56 | 0.50 | -0.29 | 0.32% | 17.49% |
| ocf_ev | 21 | 0.85 | 1.17 | 1.28 | 0.14% | 20.17% |
| ocf_ev | 63 | 0.39 | 0.56 | 0.71 | 0.16% | 18.51% |
| ocf_ev | 126 | 0.22 | 0.20 | 0.60 | 0.18% | 18.18% |
| oil_beta_trend | 21 | -0.11 | 0.21 | 0.36 | -0.03% | 15.78% |
| oil_beta_trend | 63 | -0.58 | -0.15 | -0.37 | -0.32% | 15.76% |
| oil_beta_trend | 126 | -0.23 | 0.21 | -0.21 | -0.23% | 15.91% |
| share_issuance | 21 | 0.73 | 0.15 | 0.98 | 0.08% | 17.92% |
| share_issuance | 63 | 0.61 | -0.25 | 0.89 | 0.15% | 15.67% |
| share_issuance | 126 | 0.57 | -0.21 | 0.78 | 0.30% | 15.39% |
| sue_announce | 21 | 1.66 | 1.50 | 2.07 | 0.17% | 20.05% |
| sue_announce | 63 | 1.56 | 1.61 | 2.11 | 0.37% | 18.01% |
| sue_announce | 126 | 1.49 | 1.67 | 2.07 | 0.67% | 16.97% |

Tüm faktörlü model (kapsama ≥ %50, eksiksiz satırlar):

| Ufuk | Faktör | Katsayı | NW t | Ort. düz. R² |
|---|---|---|---|---|
| 21 | asset_growth | -0.49% | -1.46 | 44.48% |
| 21 | capex_at | 0.42% | 0.81 | 44.48% |
| 21 | cash_runway_years | 0.91% | 1.25 | 44.48% |
| 21 | cop_at | -0.79% | -1.76 | 44.48% |
| 21 | dist_52w_high | 0.34% | 0.39 | 44.48% |
| 21 | droe | -0.09% | -0.18 | 44.48% |
| 21 | ear_3d | -0.15% | -0.45 | 44.48% |
| 21 | ebit_ev | 0.09% | 0.19 | 44.48% |
| 21 | idio_vol_60d | -0.99% | -1.05 | 44.48% |
| 21 | max_ret_21d | 0.53% | 0.76 | 44.48% |
| 21 | mom_12_1 | 0.15% | 0.25 | 44.48% |
| 21 | net_debt_ebitda | 0.34% | 0.95 | 44.48% |
| 21 | ocf_ev | 0.52% | 1.02 | 44.48% |
| 21 | oil_beta_trend | -0.96% | -1.28 | 44.48% |
| 21 | profitable_growth | -0.25% | -0.52 | 44.48% |
| 21 | share_issuance | -0.11% | -0.30 | 44.48% |
| 21 | sue | -0.07% | -0.12 | 44.48% |
| 21 | sue_announce | -0.06% | -0.19 | 44.48% |
| 63 | asset_growth | -0.54% | -0.85 | 36.25% |
| 63 | capex_at | 1.94% | 1.80 | 36.25% |
| 63 | cash_runway_years | 1.38% | 1.03 | 36.25% |
| 63 | cop_at | -0.96% | -0.80 | 36.25% |
| 63 | dist_52w_high | 0.08% | 0.07 | 36.25% |
| 63 | droe | -0.46% | -0.45 | 36.25% |
| 63 | ear_3d | -1.11% | -1.78 | 36.25% |
| 63 | ebit_ev | 0.76% | 0.87 | 36.25% |
| 63 | idio_vol_60d | -0.78% | -0.52 | 36.25% |
| 63 | max_ret_21d | 0.56% | 0.45 | 36.25% |
| 63 | mom_12_1 | 0.05% | 0.03 | 36.25% |
| 63 | net_debt_ebitda | 0.56% | 0.81 | 36.25% |
| 63 | ocf_ev | 0.27% | 0.22 | 36.25% |
| 63 | oil_beta_trend | -2.39% | -1.36 | 36.25% |
| 63 | profitable_growth | -1.37% | -1.24 | 36.25% |
| 63 | share_issuance | 0.66% | 0.92 | 36.25% |
| 63 | sue | 0.32% | 0.23 | 36.25% |
| 63 | sue_announce | -0.00% | -0.00 | 36.25% |
| 126 | asset_growth | -1.61% | -1.05 | 35.39% |
| 126 | capex_at | 2.96% | 2.51 | 35.39% |
| 126 | cash_runway_years | 2.38% | 1.12 | 35.39% |
| 126 | cop_at | -0.02% | -0.01 | 35.39% |
| 126 | dist_52w_high | 0.11% | 0.08 | 35.39% |
| 126 | droe | 0.86% | 0.55 | 35.39% |
| 126 | ear_3d | -2.37% | -1.97 | 35.39% |
| 126 | ebit_ev | 0.21% | 0.17 | 35.39% |
| 126 | idio_vol_60d | -0.88% | -0.29 | 35.39% |
| 126 | max_ret_21d | 1.44% | 0.93 | 35.39% |
| 126 | mom_12_1 | -0.86% | -0.41 | 35.39% |
| 126 | net_debt_ebitda | 1.96% | 2.50 | 35.39% |
| 126 | ocf_ev | -0.64% | -0.37 | 35.39% |
| 126 | oil_beta_trend | -4.39% | -2.00 | 35.39% |
| 126 | profitable_growth | -3.30% | -2.22 | 35.39% |
| 126 | share_issuance | 2.07% | 1.45 | 35.39% |
| 126 | sue | 0.18% | 0.09 | 35.39% |
| 126 | sue_announce | -0.86% | -0.99 | 35.39% |

### 7.1 Tanımlayıcı istatistikler (winsorize %0,5/%99,5; aylık değerlerin zaman ortalaması)

| Faktör | Ort. | Std | Çarp. | Bas. | P5 | Medyan | P95 | n | Ort. kayması |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.127 | 0.342 | 3.70 | 19.97 | -0.134 | 0.055 | 0.628 | 140 | 0.17 |
| capex_at | 0.082 | 0.065 | 1.66 | 3.99 | 0.007 | 0.069 | 0.206 | 131 | 0.26 |
| cash_runway_years | 6.649 | 4.420 | -0.64 | -1.48 | 0.051 | 10.000 | 10.000 | 139 | 0.11 |
| cop_at | 0.097 | 0.072 | 0.51 | 5.11 | 0.003 | 0.082 | 0.221 | 139 | 0.18 |
| dist_52w_high | -0.194 | 0.158 | -1.19 | 1.30 | -0.504 | -0.151 | -0.024 | 142 | 0.47 |
| droe | -0.003 | 0.129 | -0.68 | 14.18 | -0.150 | -0.000 | 0.142 | 127 | 0.30 |
| ear_3d | 0.002 | 0.066 | 0.19 | 3.08 | -0.099 | 0.002 | 0.106 | 131 | 0.13 |
| ebit_ev | 0.051 | 0.200 | -0.96 | 19.04 | -0.110 | 0.052 | 0.171 | 124 | 0.31 |
| gross_profitability | 0.172 | 0.176 | 0.11 | 7.91 | 0.014 | 0.148 | 0.447 | 66 | 0.21 |
| idio_vol_60d | 0.357 | 0.241 | 1.54 | 4.99 | 0.156 | 0.315 | 0.703 | 142 | 0.49 |
| max_ret_21d | 0.050 | 0.035 | 2.17 | 7.45 | 0.017 | 0.040 | 0.114 | 142 | 0.58 |
| mom_12_1 | 0.201 | 0.715 | 2.25 | 14.78 | -0.352 | 0.088 | 0.996 | 142 | 0.55 |
| net_debt_ebitda | 3.833 | 4.730 | 2.41 | 13.20 | -0.837 | 3.337 | 9.809 | 112 | 0.20 |
| ocf_ev | 0.104 | 0.087 | 1.29 | 6.98 | 0.006 | 0.083 | 0.253 | 139 | 0.20 |
| oil_beta_trend | -0.025 | 0.379 | -0.36 | 8.19 | -0.441 | -0.024 | 0.406 | 89 | 1.22 |
| profitable_growth | 1.008 | 0.407 | 0.07 | -0.63 | 0.364 | 0.998 | 1.675 | 122 | 0.06 |
| share_issuance | 0.047 | 0.191 | 2.67 | 19.20 | -0.060 | 0.005 | 0.307 | 133 | 0.13 |
| sue | 0.108 | 1.068 | 0.05 | 0.43 | -1.653 | 0.076 | 1.878 | 136 | 0.29 |
| sue_announce | 0.200 | 1.155 | 0.21 | 0.26 | -1.556 | 0.151 | 2.074 | 82 | 0.31 |

### 7.2 Korelasyon ve çoklu doğrusallık

Tam matris (alt üçgen Pearson, üst üçgen Spearman): `corr.csv`. |ρ| > 0,7 çiftleri:

| A | B | Pearson | Spearman | Not |
|---|---|---|---|---|
| droe | sue | 0.49 | 0.81 | Spearman >> Pearson: doğrusal olmayan monoton ilişki |
| idio_vol_60d | max_ret_21d | 0.76 | 0.82 |  |

VIF > 5: `capex_at` (7.0), `cop_at` (6.2), `dist_52w_high` (6.6), `droe` (6.0), `idio_vol_60d` (11.2), `max_ret_21d` (7.1), `mom_12_1` (5.2), `ocf_ev` (6.5), `oil_beta_trend` (6.5), `sue` (8.7), `sue_announce` (5.4)

Ortogonalize (tema skoru + alt tema kuklaları sonrası artık) IC:

| Faktör | Ufuk | Artık IC | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.021 | 2.21 |
| asset_growth | 63 | 0.036 | 2.72 |
| asset_growth | 126 | 0.055 | 3.17 |
| capex_at | 21 | 0.013 | 1.28 |
| capex_at | 63 | 0.020 | 1.24 |
| capex_at | 126 | 0.034 | 1.43 |
| cash_runway_years | 21 | -0.112 | -1.18 |
| cash_runway_years | 63 | -0.128 | -2.72 |
| cash_runway_years | 126 | -0.193 | -3.59 |
| cop_at | 21 | -0.019 | -1.75 |
| cop_at | 63 | -0.032 | -1.96 |
| cop_at | 126 | -0.047 | -1.85 |
| dist_52w_high | 21 | 0.018 | 1.25 |
| dist_52w_high | 63 | 0.030 | 1.44 |
| dist_52w_high | 126 | 0.038 | 1.31 |
| ear_3d | 21 | 0.018 | 2.08 |
| ear_3d | 63 | 0.017 | 1.70 |
| ear_3d | 126 | 0.018 | 1.22 |
| ebit_ev | 21 | -0.014 | -1.12 |
| ebit_ev | 63 | -0.025 | -1.42 |
| ebit_ev | 126 | -0.028 | -1.29 |
| gross_profitability | 21 | -0.011 | -0.80 |
| gross_profitability | 63 | -0.033 | -1.57 |
| gross_profitability | 126 | -0.036 | -1.30 |
| idio_vol_60d | 21 | 0.023 | 1.44 |
| idio_vol_60d | 63 | 0.037 | 1.70 |
| idio_vol_60d | 126 | 0.055 | 1.77 |
| max_ret_21d | 21 | 0.019 | 1.35 |
| max_ret_21d | 63 | 0.030 | 1.80 |
| max_ret_21d | 126 | 0.038 | 1.64 |
| mom_12_1 | 21 | 0.015 | 1.14 |
| mom_12_1 | 63 | 0.023 | 1.27 |
| mom_12_1 | 126 | 0.016 | 0.62 |
| net_debt_ebitda | 21 | -0.024 | -1.65 |
| net_debt_ebitda | 63 | -0.041 | -2.18 |
| net_debt_ebitda | 126 | -0.057 | -2.26 |
| ocf_ev | 21 | 0.001 | 0.06 |
| ocf_ev | 63 | 0.000 | 0.00 |
| ocf_ev | 126 | -0.002 | -0.07 |
| oil_beta_trend | 21 | 0.001 | 0.06 |
| oil_beta_trend | 63 | -0.016 | -0.50 |
| oil_beta_trend | 126 | -0.010 | -0.28 |
| share_issuance | 21 | 0.011 | 1.26 |
| share_issuance | 63 | 0.026 | 2.18 |
| share_issuance | 126 | 0.042 | 2.54 |
| sue_announce | 21 | 0.011 | 1.21 |
| sue_announce | 63 | 0.008 | 0.62 |
| sue_announce | 126 | 0.003 | 0.20 |

### 7.3 Süreklilik (ρτ, aylık kesitsel sıra korelasyonu)

| Faktör | τ=1 | τ=3 | τ=6 | τ=12 |
|---|---|---|---|---|
| asset_growth | 0.93 | 0.81 | 0.63 | 0.28 |
| capex_at | 0.99 | 0.96 | 0.92 | 0.83 |
| cash_runway_years | 0.95 | 0.86 | 0.76 | 0.60 |
| cop_at | 0.97 | 0.92 | 0.84 | 0.69 |
| dist_52w_high | 0.83 | 0.66 | 0.49 | 0.33 |
| droe | 0.74 | 0.27 | 0.17 | -0.25 |
| ear_3d | 0.64 | 0.00 | 0.03 | 0.01 |
| ebit_ev | 0.95 | 0.87 | 0.73 | 0.46 |
| gross_profitability | 0.99 | 0.96 | 0.92 | 0.84 |
| idio_vol_60d | 0.96 | 0.88 | 0.85 | 0.82 |
| max_ret_21d | 0.66 | 0.65 | 0.63 | 0.59 |
| mom_12_1 | 0.89 | 0.70 | 0.43 | 0.01 |
| net_debt_ebitda | 0.97 | 0.93 | 0.89 | 0.81 |
| ocf_ev | 0.97 | 0.90 | 0.81 | 0.63 |
| oil_beta_trend | 0.65 | 0.18 | 0.01 | -0.14 |
| profitable_growth | 0.96 | 0.88 | 0.74 | 0.44 |
| share_issuance | 0.94 | 0.83 | 0.68 | 0.41 |
| sue | 0.74 | 0.27 | 0.16 | -0.23 |
| sue_announce | 0.79 | 0.40 | 0.26 | -0.07 |

### 7.8 İstikrar (126 seans IC ortalaması) ve ekonomik gerekçe

| Faktör | 2011-07..2015-12 | 2016-01..2020-12 | 2021-01..2026-09 | bull | bear | vix_high | vix_low | Neden çalışmalı | Kaynak |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.037 | 0.040 | 0.131 | 0.067 | 0.112 | 0.110 | 0.032 | aşırı yatırım / q-teorisi (−) | Cooper, Gulen & Schill (2008); Hou, Xue & Zhang (2015) |
| capex_at | 0.030 | 0.072 | 0.037 | 0.038 | 0.126 | 0.052 | 0.042 | yatırım faktörü (−) | Titman, Wei & Xie (2004); Fama & French (2015) CMA |
| cash_runway_years | — | — | -0.339 | -0.339 | — | -0.212 | -0.508 | finansal kısıt / seyreltme riski | Hadlock & Pierce (2010) — tema uyarlaması |
| cop_at | -0.072 | -0.091 | 0.011 | -0.046 | -0.071 | -0.005 | -0.094 | kalite (tahakkuksuz kârlılık) | Ball, Gerakos, Linnainmaa & Nikolaev (2016) |
| dist_52w_high | 0.103 | 0.042 | 0.019 | 0.066 | -0.077 | -0.043 | 0.150 | davranışsal (çıpalama) | George & Hwang (2004) |
| ear_3d | 0.012 | 0.031 | 0.021 | 0.018 | 0.053 | 0.007 | 0.037 | davranışsal (duyuru getirisi sürüklenmesi) | Chan, Jegadeesh & Lakonishok (1996) |
| ebit_ev | 0.027 | -0.075 | -0.006 | -0.017 | -0.042 | -0.034 | -0.005 | değer (risk + davranışsal) | Loughran & Wellman (2011) |
| gross_profitability | 0.027 | -0.057 | -0.034 | -0.022 | -0.038 | -0.015 | -0.032 | risk/kalite | Novy-Marx (2013) |
| idio_vol_60d | 0.112 | 0.092 | 0.029 | 0.086 | -0.026 | -0.038 | 0.193 | sınırlı arbitraj / piyango tercihi (−) | Ang, Hodrick, Xing & Zhang (2006) |
| max_ret_21d | 0.090 | 0.069 | 0.012 | 0.061 | -0.003 | -0.033 | 0.147 | piyango tercihi (−) | Bali, Cakici & Whitelaw (2011) |
| mom_12_1 | 0.107 | -0.054 | 0.053 | 0.040 | -0.035 | 0.013 | 0.054 | davranışsal (yetersiz tepki) + risk | Jegadeesh & Titman (1993); Carhart (1997) |
| net_debt_ebitda | -0.055 | -0.078 | -0.029 | -0.055 | -0.042 | -0.029 | -0.078 | kaldıraç / sıkıntı riski (−) | Campbell, Hilscher & Szilagyi (2008) |
| ocf_ev | -0.014 | -0.020 | 0.057 | 0.012 | -0.019 | 0.053 | -0.036 | değer (nakit akışı) | Lakonishok, Shleifer & Vishny (1994) |
| oil_beta_trend | 0.009 | -0.085 | 0.030 | -0.018 | 0.008 | 0.039 | -0.072 | emtia risk primi + trend | Moskowitz, Ooi & Pedersen (2012) — tema uyarlaması |
| share_issuance | 0.027 | 0.010 | 0.086 | 0.044 | 0.029 | 0.033 | 0.052 | piyasa zamanlaması (−) | Pontiff & Woodgate (2008); Daniel & Titman (2006) |
| sue_announce | 0.074 | -0.001 | 0.004 | 0.037 | -0.095 | -0.006 | 0.055 | davranışsal (PEAD, duyuru tarihli) | Bernard & Thomas (1989); Livnat & Mendenhall (2006) |

## Dosyalar

Tüm tablolar (alt temalar dahil): `alphas.csv`, `corr.csv`, `counts.csv`, `decision.csv`, `dependent.csv`, `descriptive.csv`, `fm.csv`, `ic.csv`, `orth.csv`, `persistence.csv`, `redundant.csv`, `sorts.csv`, `stability.csv`, `vif.csv`
