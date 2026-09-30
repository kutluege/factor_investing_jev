# Faktör açıklama raporu — themes_v1 (`themes_v1_20260930`)

Bu rapor **tanımlayıcıdır**; faktör seçimi veya ağırlık öğrenmesi için kullanılmaz (THEMES_SPEC §7.9).

- Ön kayıt: `research/preregistration/themes_v1.yaml`, SHA256 `b3f5ab188a3002aaf058c356277042023f70a55057de60883657277098072c4b`
- Veri: 2011-07-29 → 2026-09-30, 183 ay; uygun satır 54412
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
| biotech | 143.6 | 27 | 259 | 0 |
| energy | 142.9 | 91 | 180 | 0 |
| robotics | 10.9 | 2 | 23 | 116 |

## §7.9 Karar tablosu (126 seans)

Çalışıyor = IC > 0 ve NW t ≥ 2 **ve** FM katsayısı aynı işaretli **ve** alt dönemlerin ≥ 2/3'ünde IC > 0 **ve** bağımlı sıralama farkı > 0. Çalışmayanlar bir sonraki sürümde gerekçeyle çıkarılabilir; sonuçlara bakıp yeni faktör eklenmez.

| Kapsam | Faktör | IC | NW t | IC>0,t≥2 | FM | Alt dönem | Bağımlı | Çalışıyor |
|---|---|---|---|---|---|---|---|---|
| havuz | asset_growth | 0.033 | 2.25 | ✔ | ✔ | ✔ | ✔ | ✔ |
| havuz | capex_at | -0.024 | -1.59 | ✘ | ✘ | ✘ | ✔ | ✘ |
| havuz | cash_runway_years | 0.008 | 0.46 | ✘ | ✘ | ✔ | ✘ | ✘ |
| havuz | cop_at | -0.033 | -1.14 | ✘ | ✔ | ✘ | ✘ | ✘ |
| havuz | dist_52w_high | 0.087 | 3.37 | ✔ | ✔ | ✔ | ✔ | ✔ |
| havuz | droe | -0.017 | -0.94 | ✘ | ✘ | ✘ | ✘ | ✘ |
| havuz | ear_3d | -0.001 | -0.05 | ✘ | ✘ | ✘ | ✘ | ✘ |
| havuz | ebit_ev | -0.020 | -0.57 | ✘ | ✔ | ✘ | ✘ | ✘ |
| havuz | gross_profitability | -0.007 | -0.25 | ✘ | ✔ | ✔ | ✘ | ✘ |
| havuz | idio_vol_60d | 0.115 | 3.89 | ✔ | ✔ | ✔ | ✘ | ✘ |
| havuz | max_ret_21d | 0.094 | 3.46 | ✔ | ✔ | ✔ | ✘ | ✘ |
| havuz | mom_12_1 | 0.016 | 0.77 | ✘ | ✔ | ✔ | ✔ | ✘ |
| havuz | net_debt_ebitda | -0.053 | -1.55 | ✘ | ✘ | ✘ | ✘ | ✘ |
| havuz | ocf_ev | 0.009 | 0.21 | ✘ | ✔ | ✘ | ✔ | ✘ |
| havuz | oil_beta_trend | -0.015 | -0.41 | ✘ | ✔ | ✔ | ✔ | ✘ |
| havuz | profitable_growth | — | — | ✘ | ✘ | ✘ | ✘ | ✘ |
| havuz | share_issuance | 0.070 | 4.84 | ✔ | ✔ | ✔ | ✘ | ✘ |
| havuz | sue | 0.001 | 0.07 | ✘ | ✔ | ✘ | ✘ | ✘ |
| havuz | sue_announce | 0.039 | 2.54 | ✔ | ✔ | ✔ | ✔ | ✔ |
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
| biotech | asset_growth | 0.013 | 0.76 | ✘ | ✔ | ✔ | ✔ | ✘ |
| biotech | capex_at | -0.016 | -0.98 | ✘ | ✘ | ✘ | ✔ | ✘ |
| biotech | cash_runway_years | 0.017 | 0.99 | ✘ | ✘ | ✔ | ✘ | ✘ |
| biotech | cop_at | 0.003 | 0.13 | ✘ | ✘ | ✘ | ✘ | ✘ |
| biotech | dist_52w_high | 0.098 | 5.02 | ✔ | ✔ | ✔ | ✔ | ✔ |
| biotech | droe | -0.021 | -1.01 | ✘ | ✘ | ✘ | ✘ | ✘ |
| biotech | ear_3d | -0.012 | -1.12 | ✘ | ✔ | ✘ | ✘ | ✘ |
| biotech | gross_profitability | -0.014 | -0.46 | ✘ | ✔ | ✔ | ✘ | ✘ |
| biotech | idio_vol_60d | 0.134 | 6.05 | ✔ | ✔ | ✔ | ✔ | ✔ |
| biotech | max_ret_21d | 0.105 | 5.13 | ✔ | ✔ | ✔ | ✔ | ✔ |
| biotech | mom_12_1 | 0.007 | 0.38 | ✘ | ✔ | ✔ | ✔ | ✘ |
| biotech | share_issuance | 0.073 | 3.05 | ✔ | ✘ | ✔ | ✘ | ✘ |
| biotech | sue | 0.001 | 0.05 | ✘ | ✔ | ✘ | ✘ | ✘ |
| biotech | sue_announce | 0.059 | 2.89 | ✔ | ✔ | ✔ | ✔ | ✔ |
| energy | asset_growth | 0.071 | 2.73 | ✔ | ✔ | ✔ | ✔ | ✔ |
| energy | capex_at | 0.047 | 1.56 | ✘ | ✔ | ✔ | ✔ | ✘ |
| energy | cash_runway_years | -0.339 | -6.03 | ✘ | ✔ | ✘ | ✘ | ✘ |
| energy | cop_at | -0.049 | -1.23 | ✘ | ✔ | ✘ | ✘ | ✘ |
| energy | dist_52w_high | 0.052 | 1.02 | ✘ | ✔ | ✔ | ✘ | ✘ |
| energy | ear_3d | 0.022 | 1.37 | ✘ | ✔ | ✔ | ✔ | ✘ |
| energy | ebit_ev | -0.020 | -0.57 | ✘ | ✔ | ✘ | ✘ | ✘ |
| energy | gross_profitability | -0.023 | -0.82 | ✘ | ✔ | ✘ | ✔ | ✘ |
| energy | idio_vol_60d | 0.076 | 1.33 | ✘ | ✘ | ✔ | ✘ | ✘ |
| energy | max_ret_21d | 0.055 | 1.14 | ✘ | ✘ | ✔ | ✘ | ✘ |
| energy | mom_12_1 | 0.033 | 0.76 | ✘ | ✔ | ✔ | ✔ | ✘ |
| energy | net_debt_ebitda | -0.053 | -1.55 | ✘ | ✘ | ✘ | ✘ | ✘ |
| energy | ocf_ev | 0.009 | 0.21 | ✘ | ✔ | ✘ | ✔ | ✘ |
| energy | oil_beta_trend | -0.015 | -0.41 | ✘ | ✔ | ✔ | ✔ | ✘ |
| energy | share_issuance | 0.041 | 1.95 | ✘ | ✔ | ✔ | ✔ | ✘ |
| energy | sue_announce | 0.024 | 0.98 | ✘ | ✔ | ✔ | ✔ | ✘ |

## Kapsam: havuz

### 7.7 Rank IC

| Faktör | Ufuk | IC | NW t | Örtüşmesiz t | IC>0 oranı | Ay |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 0.014 | 1.73 | 1.76 | 51.10% | 182 |
| asset_growth | 63 | 0.018 | 1.51 | 1.18 | 57.78% | 180 |
| asset_growth | 126 | 0.033 | 2.25 | 1.75 | 62.71% | 177 |
| capex_at | 21 | -0.013 | -1.67 | -1.79 | 43.41% | 182 |
| capex_at | 63 | -0.021 | -1.78 | -0.90 | 41.67% | 180 |
| capex_at | 126 | -0.024 | -1.59 | -1.10 | 40.68% | 177 |
| cash_runway_years | 21 | 0.007 | 0.74 | 0.80 | 52.30% | 174 |
| cash_runway_years | 63 | 0.002 | 0.18 | -0.23 | 50.00% | 172 |
| cash_runway_years | 126 | 0.008 | 0.46 | 0.33 | 54.44% | 169 |
| cop_at | 21 | -0.005 | -0.34 | -0.34 | 47.80% | 182 |
| cop_at | 63 | -0.021 | -1.02 | -1.18 | 47.78% | 180 |
| cop_at | 126 | -0.033 | -1.14 | -1.17 | 44.63% | 177 |
| dist_52w_high | 21 | 0.043 | 2.55 | 2.55 | 57.69% | 182 |
| dist_52w_high | 63 | 0.063 | 3.25 | 2.74 | 63.33% | 180 |
| dist_52w_high | 126 | 0.087 | 3.37 | 3.33 | 74.58% | 177 |
| droe | 21 | -0.001 | -0.06 | -0.06 | 50.28% | 181 |
| droe | 63 | -0.005 | -0.35 | 0.38 | 48.60% | 179 |
| droe | 126 | -0.017 | -0.94 | -0.69 | 46.02% | 176 |
| ear_3d | 21 | 0.002 | 0.31 | 0.30 | 48.90% | 182 |
| ear_3d | 63 | -0.001 | -0.13 | 0.06 | 51.67% | 180 |
| ear_3d | 126 | -0.001 | -0.05 | 0.40 | 49.72% | 177 |
| ebit_ev | 21 | 0.003 | 0.13 | 0.14 | 50.00% | 182 |
| ebit_ev | 63 | -0.017 | -0.65 | -0.97 | 46.11% | 180 |
| ebit_ev | 126 | -0.020 | -0.57 | -0.45 | 49.15% | 177 |
| gross_profitability | 21 | 0.001 | 0.08 | 0.08 | 52.20% | 182 |
| gross_profitability | 63 | -0.016 | -0.81 | -0.47 | 38.89% | 180 |
| gross_profitability | 126 | -0.007 | -0.25 | -0.25 | 42.94% | 177 |
| idio_vol_60d | 21 | 0.055 | 3.05 | 3.07 | 60.44% | 182 |
| idio_vol_60d | 63 | 0.079 | 3.52 | 2.84 | 65.00% | 180 |
| idio_vol_60d | 126 | 0.115 | 3.89 | 3.46 | 74.01% | 177 |
| max_ret_21d | 21 | 0.044 | 2.74 | 2.74 | 58.79% | 182 |
| max_ret_21d | 63 | 0.069 | 3.41 | 2.40 | 61.11% | 180 |
| max_ret_21d | 126 | 0.094 | 3.46 | 2.62 | 71.75% | 177 |
| mom_12_1 | 21 | 0.007 | 0.56 | 0.57 | 49.45% | 182 |
| mom_12_1 | 63 | 0.011 | 0.75 | 0.92 | 54.44% | 180 |
| mom_12_1 | 126 | 0.016 | 0.77 | 0.84 | 57.63% | 177 |
| net_debt_ebitda | 21 | -0.013 | -0.67 | -0.72 | 50.55% | 182 |
| net_debt_ebitda | 63 | -0.034 | -1.29 | -1.26 | 48.33% | 180 |
| net_debt_ebitda | 126 | -0.053 | -1.55 | -1.29 | 44.63% | 177 |
| ocf_ev | 21 | 0.013 | 0.63 | 0.68 | 51.10% | 182 |
| ocf_ev | 63 | 0.008 | 0.27 | -0.26 | 51.67% | 180 |
| ocf_ev | 126 | 0.009 | 0.21 | 0.02 | 55.93% | 177 |
| oil_beta_trend | 21 | 0.008 | 0.34 | 0.34 | 54.40% | 182 |
| oil_beta_trend | 63 | -0.019 | -0.57 | -0.01 | 48.33% | 180 |
| oil_beta_trend | 126 | -0.015 | -0.41 | -0.66 | 48.02% | 177 |
| profitable_growth | 21 | — | — | -0.44 | 40.00% | 5 |
| profitable_growth | 63 | — | — | — | 40.00% | 5 |
| profitable_growth | 126 | — | — | — | 20.00% | 5 |
| share_issuance | 21 | 0.037 | 4.00 | 4.01 | 58.79% | 182 |
| share_issuance | 63 | 0.051 | 4.16 | 2.82 | 65.56% | 180 |
| share_issuance | 126 | 0.070 | 4.84 | 3.22 | 77.40% | 177 |
| sue | 21 | 0.000 | 0.01 | 0.01 | 50.56% | 178 |
| sue | 63 | -0.004 | -0.34 | 0.45 | 49.43% | 176 |
| sue | 126 | 0.001 | 0.07 | 0.57 | 48.55% | 173 |
| sue_announce | 21 | 0.019 | 1.88 | 1.84 | 55.49% | 182 |
| sue_announce | 63 | 0.029 | 2.28 | 1.71 | 57.22% | 180 |
| sue_announce | 126 | 0.039 | 2.54 | 2.39 | 64.41% | 177 |

### 7.4 Tek değişkenli sıralama (EW; üst − alt = `mimic_`)

| Faktör | Ufuk | Port. | mimic EW | t | mimic VW | Üst − ort. | t | Monoton |
|---|---|---|---|---|---|---|---|---|
| asset_growth | 21 | 5 | -0.27% | -0.26 | -0.18% | 0.22% | 0.61 | ✘ |
| asset_growth | 63 | 5 | -0.97% | -0.48 | 0.12% | 0.20% | 0.28 | ✘ |
| asset_growth | 126 | 5 | 1.56% | 1.18 | 1.87% | 0.30% | 0.32 | ✘ |
| capex_at | 21 | 5 | 1.32% | 1.80 | -0.41% | 0.82% | 1.20 | ✘ |
| capex_at | 63 | 5 | 3.63% | 2.55 | 0.43% | 2.10% | 1.68 | ✘ |
| capex_at | 126 | 5 | 5.49% | 2.74 | 1.88% | 2.28% | 1.51 | ✘ |
| cash_runway_years | 21 | 5 | 1.85% | 0.65 | 0.50% | 2.24% | 0.99 | ✘ |
| cash_runway_years | 63 | 5 | 3.16% | 0.56 | 0.04% | 4.50% | 1.02 | ✘ |
| cash_runway_years | 126 | 5 | -10.08% | -1.43 | -8.26% | -2.01% | -1.02 | ✘ |
| cop_at | 21 | 5 | -0.13% | -0.41 | 0.05% | -0.15% | -0.85 | ✘ |
| cop_at | 63 | 5 | -0.85% | -1.05 | -0.21% | -0.74% | -1.66 | ✘ |
| cop_at | 126 | 5 | -1.78% | -1.06 | 0.63% | -1.49% | -1.67 | ✘ |
| dist_52w_high | 21 | 5 | 0.32% | 0.53 | 0.39% | -0.20% | -0.61 | ✘ |
| dist_52w_high | 63 | 5 | 0.72% | 0.56 | 1.21% | -0.52% | -0.77 | ✘ |
| dist_52w_high | 126 | 5 | 1.63% | 0.66 | 1.13% | 0.19% | 0.18 | ✘ |
| droe | 21 | 5 | -0.22% | -0.47 | -0.02% | -0.21% | -0.65 | ✘ |
| droe | 63 | 5 | -0.57% | -0.47 | -0.15% | -0.34% | -0.43 | ✘ |
| droe | 126 | 5 | -0.57% | -0.23 | -1.85% | 0.51% | 0.33 | ✘ |
| ear_3d | 21 | 5 | -0.30% | -1.05 | -0.73% | -0.13% | -0.81 | ✘ |
| ear_3d | 63 | 5 | -0.41% | -0.75 | -1.81% | -0.40% | -0.91 | ✘ |
| ear_3d | 126 | 5 | -2.03% | -0.84 | 0.87% | -0.22% | -0.30 | ✘ |
| ebit_ev | 21 | 5 | -0.42% | -0.73 | -0.34% | -0.06% | -0.17 | ✘ |
| ebit_ev | 63 | 5 | -2.05% | -1.44 | -1.50% | -1.01% | -1.39 | ✘ |
| ebit_ev | 126 | 5 | -4.45% | -1.69 | -3.67% | -2.08% | -1.49 | ✘ |
| gross_profitability | 21 | 5 | -0.17% | -0.35 | -0.41% | -0.13% | -0.55 | ✘ |
| gross_profitability | 63 | 5 | -0.65% | -0.54 | -0.96% | -0.46% | -0.75 | ✘ |
| gross_profitability | 126 | 5 | -0.23% | -0.11 | -0.15% | -0.49% | -0.45 | ✘ |
| idio_vol_60d | 21 | 5 | -1.00% | -0.97 | 0.32% | 0.03% | 0.08 | ✘ |
| idio_vol_60d | 63 | 5 | -2.53% | -1.12 | 0.40% | -0.11% | -0.13 | ✘ |
| idio_vol_60d | 126 | 5 | 0.40% | 0.15 | 0.26% | 0.05% | 0.03 | ✘ |
| max_ret_21d | 21 | 5 | 0.89% | 0.68 | 0.49% | 0.96% | 0.99 | ✘ |
| max_ret_21d | 63 | 5 | -0.54% | -0.35 | 1.28% | 0.82% | 0.73 | ✘ |
| max_ret_21d | 126 | 5 | -0.58% | -0.24 | -0.24% | -0.44% | -0.29 | ✘ |
| mom_12_1 | 21 | 5 | 1.18% | 1.27 | 0.15% | 0.58% | 0.86 | ✔ |
| mom_12_1 | 63 | 5 | 1.85% | 1.54 | 0.06% | 0.77% | 1.16 | ✘ |
| mom_12_1 | 126 | 5 | 2.57% | 1.26 | -0.51% | 1.36% | 1.26 | ✘ |
| net_debt_ebitda | 21 | 5 | 0.24% | 0.53 | 0.21% | 0.15% | 0.49 | ✘ |
| net_debt_ebitda | 63 | 5 | 0.26% | 0.23 | -0.16% | 0.19% | 0.25 | ✘ |
| net_debt_ebitda | 126 | 5 | 0.17% | 0.08 | -1.02% | 0.19% | 0.13 | ✘ |
| ocf_ev | 21 | 5 | 0.46% | 0.71 | 0.57% | 0.08% | 0.19 | ✘ |
| ocf_ev | 63 | 5 | 0.60% | 0.39 | 0.85% | -0.28% | -0.29 | ✘ |
| ocf_ev | 126 | 5 | 0.41% | 0.12 | 1.13% | -0.99% | -0.46 | ✘ |
| oil_beta_trend | 21 | 5 | 0.45% | 0.58 | 0.73% | 0.35% | 0.88 | ✘ |
| oil_beta_trend | 63 | 5 | -0.53% | -0.29 | 0.33% | 0.22% | 0.21 | ✘ |
| oil_beta_trend | 126 | 5 | 0.06% | 0.02 | 1.40% | 0.59% | 0.32 | ✘ |
| profitable_growth | 21 | 3 | — | — | — | — | — | ✘ |
| profitable_growth | 63 | 3 | — | — | — | — | — | ✘ |
| profitable_growth | 126 | 3 | — | — | — | — | — | ✘ |
| share_issuance | 21 | 5 | -0.77% | -0.86 | 0.43% | -0.05% | -0.27 | ✘ |
| share_issuance | 63 | 5 | -2.24% | -1.27 | 0.76% | -0.23% | -0.57 | ✘ |
| share_issuance | 126 | 5 | -1.96% | -0.80 | 1.19% | 0.19% | 0.27 | ✘ |
| sue | 21 | 5 | -0.34% | -0.80 | -0.32% | -0.07% | -0.25 | ✘ |
| sue | 63 | 5 | -0.78% | -0.83 | -1.17% | -0.18% | -0.34 | ✘ |
| sue | 126 | 5 | -0.19% | -0.11 | -2.48% | 0.97% | 1.23 | ✘ |
| sue_announce | 21 | 5 | 0.30% | 0.82 | 0.11% | 0.15% | 0.78 | ✘ |
| sue_announce | 63 | 5 | 1.25% | 1.55 | 0.53% | 0.28% | 0.59 | ✘ |
| sue_announce | 126 | 5 | 1.84% | 1.49 | -0.91% | 0.68% | 0.96 | ✘ |

### 7.4 Alfalar (21 seans, aylık; NW t)

Üst portföy RF üzeri; `mimic_ew` ham fark.

| Faktör | Seri | capm t | ff3 t | carhart4 t | ff5_mom t |
|---|---|---|---|---|---|
| asset_growth | mimic_ew | -0.27 | -0.23 | -0.56 | -0.24 |
| asset_growth | top_ew | 0.42 | 1.00 | 1.07 | 1.21 |
| capex_at | mimic_ew | 1.51 | 1.90 | 1.66 | 1.96 |
| capex_at | top_ew | 0.95 | 1.23 | 1.27 | 1.36 |
| cash_runway_years | mimic_ew | 0.65 | 0.58 | 0.87 | 0.73 |
| cash_runway_years | top_ew | 0.95 | 1.07 | 1.16 | 1.19 |
| cop_at | mimic_ew | -0.57 | -0.80 | -0.30 | -0.52 |
| cop_at | top_ew | -0.48 | -0.49 | -0.33 | -0.50 |
| dist_52w_high | mimic_ew | 2.14 | 1.81 | 1.42 | 1.13 |
| dist_52w_high | top_ew | 1.28 | 1.45 | 1.02 | 0.92 |
| droe | mimic_ew | -0.30 | -0.20 | -0.25 | -0.39 |
| droe | top_ew | 0.47 | 0.89 | 0.76 | 0.85 |
| ear_3d | mimic_ew | -0.71 | -0.70 | -0.52 | -0.68 |
| ear_3d | top_ew | -0.78 | -0.30 | -0.26 | -0.11 |
| ebit_ev | mimic_ew | -0.69 | -0.86 | -0.50 | -1.03 |
| ebit_ev | top_ew | -0.80 | -1.05 | -0.83 | -1.30 |
| gross_profitability | mimic_ew | 1.54 | 1.74 | 1.76 | 1.83 |
| gross_profitability | top_ew | 0.72 | 0.93 | 0.96 | 0.92 |
| idio_vol_60d | mimic_ew | -0.32 | -0.66 | -0.93 | -1.01 |
| idio_vol_60d | top_ew | 1.91 | 1.70 | 1.56 | 1.14 |
| max_ret_21d | mimic_ew | 1.15 | 0.82 | 1.00 | 0.57 |
| max_ret_21d | top_ew | 1.18 | 1.15 | 1.16 | 1.05 |
| mom_12_1 | mimic_ew | 1.59 | 1.54 | 1.15 | 1.14 |
| mom_12_1 | top_ew | 0.73 | 0.89 | 0.89 | 0.84 |
| net_debt_ebitda | mimic_ew | -0.56 | -0.47 | -0.64 | -0.84 |
| net_debt_ebitda | top_ew | -0.66 | -0.78 | -0.90 | -1.12 |
| ocf_ev | mimic_ew | -0.04 | -0.17 | 0.23 | -0.07 |
| ocf_ev | top_ew | -0.57 | -0.77 | -0.60 | -0.85 |
| oil_beta_trend | mimic_ew | 1.98 | 2.04 | 1.75 | 1.84 |
| oil_beta_trend | top_ew | 0.57 | 0.71 | 0.69 | 0.53 |
| share_issuance | mimic_ew | -0.64 | -0.92 | -1.03 | -1.09 |
| share_issuance | top_ew | 0.25 | 0.26 | 0.32 | -0.02 |
| sue | mimic_ew | -1.45 | -1.47 | -1.27 | -1.39 |
| sue | top_ew | 0.12 | 0.53 | 0.38 | 0.35 |
| sue_announce | mimic_ew | 0.99 | 0.83 | 0.32 | 0.35 |
| sue_announce | top_ew | 0.48 | 0.75 | 0.45 | 0.34 |

### 7.5 Bağımlı iki değişkenli sıralama (tema skoru terciliyle kontrol)

| Faktör | Ufuk | Ort. fark | NW t |
|---|---|---|---|
| asset_growth | 21 | -0.10% | -0.16 |
| asset_growth | 63 | -0.33% | -0.28 |
| asset_growth | 126 | 0.09% | 0.06 |
| capex_at | 21 | 0.54% | 1.52 |
| capex_at | 63 | 1.86% | 2.63 |
| capex_at | 126 | 3.01% | 2.36 |
| cash_runway_years | 21 | 0.76% | 0.51 |
| cash_runway_years | 63 | -0.76% | -0.24 |
| cash_runway_years | 126 | -8.36% | -2.09 |
| cop_at | 21 | -0.12% | -0.29 |
| cop_at | 63 | -0.77% | -0.79 |
| cop_at | 126 | -1.42% | -0.69 |
| dist_52w_high | 21 | -0.09% | -0.14 |
| dist_52w_high | 63 | 0.21% | 0.22 |
| dist_52w_high | 126 | 1.13% | 0.75 |
| droe | 21 | 0.00% | 0.00 |
| droe | 63 | -0.10% | -0.14 |
| droe | 126 | -0.87% | -0.68 |
| ear_3d | 21 | -0.07% | -0.34 |
| ear_3d | 63 | -0.24% | -0.59 |
| ear_3d | 126 | -1.50% | -1.01 |
| ebit_ev | 21 | -0.42% | -0.95 |
| ebit_ev | 63 | -1.51% | -1.38 |
| ebit_ev | 126 | -2.92% | -1.37 |
| gross_profitability | 21 | -0.27% | -0.83 |
| gross_profitability | 63 | -0.97% | -1.25 |
| gross_profitability | 126 | -0.32% | -0.26 |
| idio_vol_60d | 21 | -0.63% | -1.05 |
| idio_vol_60d | 63 | -1.73% | -1.30 |
| idio_vol_60d | 126 | -0.50% | -0.27 |
| max_ret_21d | 21 | 0.49% | 0.61 |
| max_ret_21d | 63 | -0.31% | -0.31 |
| max_ret_21d | 126 | -0.40% | -0.26 |
| mom_12_1 | 21 | 0.82% | 1.55 |
| mom_12_1 | 63 | 2.14% | 1.71 |
| mom_12_1 | 126 | 2.53% | 1.51 |
| net_debt_ebitda | 21 | 0.06% | 0.12 |
| net_debt_ebitda | 63 | -0.31% | -0.28 |
| net_debt_ebitda | 126 | -0.42% | -0.19 |
| ocf_ev | 21 | 0.54% | 0.94 |
| ocf_ev | 63 | 1.05% | 0.74 |
| ocf_ev | 126 | 1.56% | 0.53 |
| oil_beta_trend | 21 | 0.41% | 0.77 |
| oil_beta_trend | 63 | 0.20% | 0.15 |
| oil_beta_trend | 126 | 1.18% | 0.52 |
| share_issuance | 21 | -0.36% | -0.71 |
| share_issuance | 63 | -1.21% | -1.16 |
| share_issuance | 126 | -1.40% | -0.92 |
| sue | 21 | -0.18% | -0.66 |
| sue | 63 | -0.25% | -0.38 |
| sue | 126 | -0.24% | -0.19 |
| sue_announce | 21 | 0.45% | 1.81 |
| sue_announce | 63 | 1.07% | 1.93 |
| sue_announce | 126 | 2.22% | 2.30 |

### 7.6 Fama-MacBeth (tek faktör + β, ln(MktCap); NW t)

| Faktör | Ufuk | OLS rank-normal t | OLS ham t | WLS √MktCap t | 1 std etkisi | Ort. R² |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 1.96 | 1.43 | 0.44 | 0.19% | 7.76% |
| asset_growth | 63 | 1.08 | 1.62 | 0.01 | 0.27% | 6.25% |
| asset_growth | 126 | 0.89 | 1.57 | 0.29 | 0.40% | 5.59% |
| capex_at | 21 | 0.11 | -0.03 | -0.16 | 0.02% | 7.32% |
| capex_at | 63 | 1.13 | 0.99 | 0.55 | 0.37% | 5.92% |
| capex_at | 126 | 1.84 | 1.75 | 1.36 | 0.95% | 5.19% |
| cash_runway_years | 21 | -1.58 | -1.01 | -0.24 | -0.27% | 5.13% |
| cash_runway_years | 63 | -1.92 | -1.16 | -0.65 | -0.93% | 5.01% |
| cash_runway_years | 126 | -1.92 | -0.84 | -1.00 | -1.53% | 4.78% |
| cop_at | 21 | -0.25 | -0.74 | 0.55 | -0.03% | 12.32% |
| cop_at | 63 | -0.81 | -1.27 | 0.13 | -0.23% | 10.85% |
| cop_at | 126 | -0.87 | -1.38 | 0.00 | -0.52% | 10.43% |
| dist_52w_high | 21 | 0.83 | 1.40 | 0.23 | 0.14% | 8.11% |
| dist_52w_high | 63 | 1.19 | 1.82 | 0.64 | 0.41% | 6.35% |
| dist_52w_high | 126 | 1.55 | 1.97 | 1.06 | 0.96% | 5.48% |
| droe | 21 | 0.28 | -0.88 | -0.37 | 0.03% | 11.12% |
| droe | 63 | 0.32 | -0.78 | -0.62 | 0.09% | 11.05% |
| droe | 126 | 0.01 | -1.36 | -0.79 | 0.00% | 10.74% |
| ear_3d | 21 | -0.71 | -0.73 | -0.62 | -0.06% | 7.33% |
| ear_3d | 63 | -0.66 | -0.88 | -0.64 | -0.11% | 5.80% |
| ear_3d | 126 | 0.09 | 0.37 | 0.38 | 0.03% | 5.04% |
| ebit_ev | 21 | -0.15 | -0.14 | 0.33 | -0.02% | 20.12% |
| ebit_ev | 63 | -0.46 | -0.50 | -0.17 | -0.18% | 18.77% |
| ebit_ev | 126 | -0.49 | -0.84 | -0.15 | -0.33% | 18.44% |
| gross_profitability | 21 | -0.09 | -0.65 | -0.22 | -0.01% | 9.89% |
| gross_profitability | 63 | -0.39 | -0.78 | -0.46 | -0.15% | 9.15% |
| gross_profitability | 126 | -0.10 | -0.51 | -0.15 | -0.06% | 8.34% |
| idio_vol_60d | 21 | 0.07 | -0.43 | 0.07 | 0.01% | 7.65% |
| idio_vol_60d | 63 | -0.35 | -0.70 | -0.25 | -0.15% | 6.15% |
| idio_vol_60d | 126 | 0.70 | 0.38 | 0.26 | 0.53% | 5.47% |
| max_ret_21d | 21 | 0.20 | -0.02 | 0.61 | 0.03% | 7.38% |
| max_ret_21d | 63 | -0.09 | -0.83 | 0.24 | -0.03% | 5.90% |
| max_ret_21d | 126 | 0.15 | -0.17 | -0.28 | 0.07% | 5.19% |
| mom_12_1 | 21 | 1.75 | 0.87 | 1.51 | 0.19% | 7.75% |
| mom_12_1 | 63 | 2.20 | 1.66 | 2.29 | 0.57% | 6.12% |
| mom_12_1 | 126 | 1.68 | 1.49 | 1.56 | 0.92% | 5.49% |
| net_debt_ebitda | 21 | 0.53 | 0.92 | 0.48 | 0.07% | 19.38% |
| net_debt_ebitda | 63 | 0.38 | 0.74 | -0.15 | 0.13% | 17.89% |
| net_debt_ebitda | 126 | 0.59 | 0.50 | -0.28 | 0.33% | 17.48% |
| ocf_ev | 21 | 0.86 | 1.17 | 1.28 | 0.14% | 20.18% |
| ocf_ev | 63 | 0.39 | 0.56 | 0.71 | 0.16% | 18.50% |
| ocf_ev | 126 | 0.22 | 0.20 | 0.60 | 0.19% | 18.18% |
| oil_beta_trend | 21 | -0.11 | 0.19 | 0.38 | -0.03% | 15.88% |
| oil_beta_trend | 63 | -0.59 | -0.16 | -0.35 | -0.32% | 15.83% |
| oil_beta_trend | 126 | -0.23 | 0.21 | -0.19 | -0.23% | 16.04% |
| share_issuance | 21 | 1.44 | 0.75 | 1.27 | 0.13% | 7.46% |
| share_issuance | 63 | 0.38 | -0.07 | 0.60 | 0.09% | 6.00% |
| share_issuance | 126 | 0.19 | -0.16 | 0.69 | 0.09% | 5.37% |
| sue | 21 | -0.24 | -0.35 | -0.55 | -0.03% | 10.23% |
| sue | 63 | 0.32 | 0.05 | -0.51 | 0.08% | 9.89% |
| sue | 126 | 0.37 | 0.24 | -0.67 | 0.18% | 9.88% |
| sue_announce | 21 | 1.71 | 1.45 | 2.09 | 0.15% | 10.73% |
| sue_announce | 63 | 2.23 | 1.90 | 2.22 | 0.48% | 8.58% |
| sue_announce | 126 | 2.03 | 1.92 | 1.57 | 0.77% | 7.84% |

Tüm faktörlü model (kapsama ≥ %50, eksiksiz satırlar):

| Ufuk | Faktör | Katsayı | NW t | Ort. düz. R² |
|---|---|---|---|---|
| 21 | asset_growth | -0.27% | -1.68 | 20.22% |
| 21 | capex_at | 0.11% | 0.57 | 20.22% |
| 21 | cash_runway_years | -0.00% | -0.02 | 20.22% |
| 21 | cop_at | 0.24% | 1.03 | 20.22% |
| 21 | dist_52w_high | -0.32% | -1.42 | 20.22% |
| 21 | droe | 0.16% | 0.93 | 20.22% |
| 21 | ear_3d | -0.03% | -0.22 | 20.22% |
| 21 | ebit_ev | -0.33% | -1.74 | 20.22% |
| 21 | gross_profitability | -0.24% | -1.33 | 20.22% |
| 21 | idio_vol_60d | -0.10% | -0.43 | 20.22% |
| 21 | max_ret_21d | 0.29% | 1.87 | 20.22% |
| 21 | mom_12_1 | 0.43% | 2.15 | 20.22% |
| 21 | net_debt_ebitda | 0.16% | 1.15 | 20.22% |
| 21 | ocf_ev | 0.18% | 0.79 | 20.22% |
| 21 | profitable_growth | -0.09% | -0.50 | 20.22% |
| 21 | share_issuance | 0.14% | 0.95 | 20.22% |
| 21 | sue | -0.16% | -1.01 | 20.22% |
| 63 | asset_growth | -0.62% | -1.53 | 18.15% |
| 63 | capex_at | 0.42% | 0.96 | 18.15% |
| 63 | cash_runway_years | 0.13% | 0.21 | 18.15% |
| 63 | cop_at | 0.24% | 0.46 | 18.15% |
| 63 | dist_52w_high | -0.39% | -0.95 | 18.15% |
| 63 | droe | -0.06% | -0.16 | 18.15% |
| 63 | ear_3d | 0.20% | 0.75 | 18.15% |
| 63 | ebit_ev | -0.83% | -2.18 | 18.15% |
| 63 | gross_profitability | -0.52% | -1.22 | 18.15% |
| 63 | idio_vol_60d | -0.43% | -0.78 | 18.15% |
| 63 | max_ret_21d | 0.46% | 1.45 | 18.15% |
| 63 | mom_12_1 | 0.97% | 2.00 | 18.15% |
| 63 | net_debt_ebitda | 0.33% | 0.95 | 18.15% |
| 63 | ocf_ev | 0.52% | 0.96 | 18.15% |
| 63 | profitable_growth | -0.21% | -0.46 | 18.15% |
| 63 | share_issuance | 0.27% | 0.79 | 18.15% |
| 63 | sue | -0.11% | -0.32 | 18.15% |
| 126 | asset_growth | -1.06% | -1.37 | 16.76% |
| 126 | capex_at | 0.77% | 0.96 | 16.76% |
| 126 | cash_runway_years | 1.13% | 1.01 | 16.76% |
| 126 | cop_at | 0.33% | 0.33 | 16.76% |
| 126 | dist_52w_high | -1.65% | -2.06 | 16.76% |
| 126 | droe | -0.53% | -0.87 | 16.76% |
| 126 | ear_3d | 0.49% | 1.35 | 16.76% |
| 126 | ebit_ev | -1.24% | -1.94 | 16.76% |
| 126 | gross_profitability | -0.95% | -1.49 | 16.76% |
| 126 | idio_vol_60d | 0.21% | 0.21 | 16.76% |
| 126 | max_ret_21d | 0.44% | 0.94 | 16.76% |
| 126 | mom_12_1 | 2.03% | 2.01 | 16.76% |
| 126 | net_debt_ebitda | 0.26% | 0.44 | 16.76% |
| 126 | ocf_ev | 0.79% | 0.76 | 16.76% |
| 126 | profitable_growth | -0.40% | -0.44 | 16.76% |
| 126 | share_issuance | 0.08% | 0.14 | 16.76% |
| 126 | sue | 0.16% | 0.24 | 16.76% |

### 7.1 Tanımlayıcı istatistikler (winsorize %0,5/%99,5; aylık değerlerin zaman ortalaması)

| Faktör | Ort. | Std | Çarp. | Bas. | P5 | Medyan | P95 | n | Ort. kayması |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.253 | 0.617 | 3.59 | 16.86 | -0.207 | 0.074 | 1.285 | 291 | 0.15 |
| capex_at | 0.051 | 0.057 | 1.98 | 5.04 | 0.001 | 0.032 | 0.168 | 275 | 0.28 |
| cash_runway_years | 6.347 | 4.167 | -0.39 | -1.66 | 0.139 | 9.618 | 10.000 | 292 | 0.08 |
| cop_at | -0.009 | 0.223 | -1.69 | 4.05 | -0.444 | 0.063 | 0.224 | 292 | 0.19 |
| dist_52w_high | -0.230 | 0.182 | -0.95 | 0.38 | -0.583 | -0.186 | -0.022 | 297 | 0.37 |
| droe | -0.004 | 0.191 | -0.02 | 12.76 | -0.235 | -0.001 | 0.214 | 263 | 0.11 |
| ear_3d | 0.005 | 0.083 | 0.34 | 2.86 | -0.122 | 0.002 | 0.142 | 272 | 0.08 |
| ebit_ev | -0.025 | 0.222 | -2.04 | 22.02 | -0.307 | 0.021 | 0.145 | 268 | 0.25 |
| gross_profitability | 0.249 | 0.198 | 0.75 | 2.69 | 0.025 | 0.208 | 0.617 | 151 | 0.16 |
| idio_vol_60d | 0.442 | 0.285 | 2.35 | 9.93 | 0.160 | 0.382 | 0.913 | 297 | 0.38 |
| max_ret_21d | 0.065 | 0.063 | 3.68 | 20.36 | 0.018 | 0.049 | 0.158 | 297 | 0.30 |
| mom_12_1 | 0.290 | 0.813 | 2.79 | 13.36 | -0.439 | 0.111 | 1.572 | 297 | 0.35 |
| net_debt_ebitda | 2.733 | 6.342 | 1.62 | 12.47 | -4.443 | 2.476 | 9.690 | 164 | 0.10 |
| ocf_ev | 0.025 | 0.165 | -1.47 | 11.34 | -0.209 | 0.050 | 0.214 | 291 | 0.23 |
| oil_beta_trend | -0.024 | 0.378 | -0.36 | 8.22 | -0.443 | -0.024 | 0.409 | 90 | 1.21 |
| profitable_growth | 1.034 | 0.412 | 0.07 | -0.58 | 0.370 | 1.019 | 1.721 | 183 | 0.04 |
| share_issuance | 0.076 | 0.204 | 3.04 | 20.27 | -0.050 | 0.016 | 0.364 | 282 | 0.16 |
| sue | -0.069 | 1.286 | -0.27 | 0.57 | -2.330 | -0.008 | 1.972 | 284 | 0.17 |
| sue_announce | 0.268 | 1.308 | 0.40 | 0.78 | -1.725 | 0.179 | 2.451 | 140 | 0.20 |

### 7.2 Korelasyon ve çoklu doğrusallık

Tam matris (alt üçgen Pearson, üst üçgen Spearman): `corr.csv`. |ρ| > 0,7 çiftleri:

| A | B | Pearson | Spearman | Not |
|---|---|---|---|---|
| cop_at | ocf_ev | 0.68 | 0.78 |  |
| ebit_ev | ocf_ev | 0.71 | 0.74 |  |
| idio_vol_60d | max_ret_21d | 0.68 | 0.79 |  |

VIF > 5: yok

Ortogonalize (tema skoru + alt tema kuklaları sonrası artık) IC:

| Faktör | Ufuk | Artık IC | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.015 | 2.09 |
| asset_growth | 63 | 0.016 | 1.56 |
| asset_growth | 126 | 0.026 | 1.95 |
| capex_at | 21 | 0.003 | 0.37 |
| capex_at | 63 | 0.006 | 0.50 |
| capex_at | 126 | 0.007 | 0.44 |
| cash_runway_years | 21 | -0.022 | -2.22 |
| cash_runway_years | 63 | -0.034 | -2.52 |
| cash_runway_years | 126 | -0.034 | -1.91 |
| cop_at | 21 | -0.012 | -1.50 |
| cop_at | 63 | -0.029 | -2.36 |
| cop_at | 126 | -0.044 | -2.30 |
| dist_52w_high | 21 | 0.021 | 2.16 |
| dist_52w_high | 63 | 0.036 | 2.94 |
| dist_52w_high | 126 | 0.045 | 2.84 |
| droe | 21 | 0.003 | 0.27 |
| droe | 63 | -0.008 | -0.49 |
| droe | 126 | -0.045 | -2.46 |
| ear_3d | 21 | 0.001 | 0.23 |
| ear_3d | 63 | -0.001 | -0.25 |
| ear_3d | 126 | -0.003 | -0.28 |
| ebit_ev | 21 | -0.014 | -1.15 |
| ebit_ev | 63 | -0.025 | -1.43 |
| ebit_ev | 126 | -0.028 | -1.30 |
| gross_profitability | 21 | -0.009 | -1.04 |
| gross_profitability | 63 | -0.031 | -2.32 |
| gross_profitability | 126 | -0.034 | -1.75 |
| idio_vol_60d | 21 | 0.029 | 2.76 |
| idio_vol_60d | 63 | 0.047 | 3.38 |
| idio_vol_60d | 126 | 0.074 | 4.22 |
| max_ret_21d | 21 | 0.018 | 1.99 |
| max_ret_21d | 63 | 0.034 | 2.98 |
| max_ret_21d | 126 | 0.052 | 3.42 |
| mom_12_1 | 21 | 0.005 | 0.55 |
| mom_12_1 | 63 | 0.002 | 0.20 |
| mom_12_1 | 126 | -0.007 | -0.41 |
| net_debt_ebitda | 21 | -0.024 | -1.66 |
| net_debt_ebitda | 63 | -0.041 | -2.18 |
| net_debt_ebitda | 126 | -0.057 | -2.26 |
| ocf_ev | 21 | 0.001 | 0.05 |
| ocf_ev | 63 | -0.000 | -0.00 |
| ocf_ev | 126 | -0.002 | -0.07 |
| oil_beta_trend | 21 | 0.002 | 0.08 |
| oil_beta_trend | 63 | -0.015 | -0.47 |
| oil_beta_trend | 126 | -0.009 | -0.25 |
| profitable_growth | 21 | — | — |
| profitable_growth | 63 | — | — |
| profitable_growth | 126 | — | — |
| share_issuance | 21 | 0.017 | 2.37 |
| share_issuance | 63 | 0.026 | 2.88 |
| share_issuance | 126 | 0.036 | 3.36 |
| sue | 21 | -0.012 | -1.00 |
| sue | 63 | -0.027 | -1.94 |
| sue | 126 | -0.039 | -2.50 |
| sue_announce | 21 | 0.013 | 1.75 |
| sue_announce | 63 | 0.020 | 2.23 |
| sue_announce | 126 | 0.024 | 2.64 |

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
| mom_12_1 | 0.89 | 0.69 | 0.42 | -0.00 |
| net_debt_ebitda | 0.98 | 0.95 | 0.91 | 0.85 |
| ocf_ev | 0.98 | 0.94 | 0.89 | 0.78 |
| oil_beta_trend | 0.65 | 0.18 | 0.01 | -0.14 |
| profitable_growth | 0.96 | 0.89 | 0.76 | 0.50 |
| share_issuance | 0.95 | 0.86 | 0.75 | 0.53 |
| sue | 0.79 | 0.40 | 0.29 | -0.07 |
| sue_announce | 0.82 | 0.47 | 0.34 | 0.03 |

### 7.8 İstikrar (126 seans IC ortalaması) ve ekonomik gerekçe

| Faktör | 2011-07..2015-12 | 2016-01..2020-12 | 2021-01..2026-09 | bull | bear | vix_high | vix_low | Neden çalışmalı | Kaynak |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.045 | 0.019 | 0.034 | 0.033 | 0.028 | 0.043 | 0.021 | aşırı yatırım / q-teorisi (−) | Cooper, Gulen & Schill (2008); Hou, Xue & Zhang (2015) |
| capex_at | -0.024 | -0.022 | -0.027 | -0.030 | 0.028 | -0.006 | -0.044 | yatırım faktörü (−) | Titman, Wei & Xie (2004); Fama & French (2015) CMA |
| cash_runway_years | -0.027 | 0.022 | 0.021 | 0.009 | -0.000 | -0.001 | 0.017 | finansal kısıt / seyreltme riski | Hadlock & Pierce (2010) — tema uyarlaması |
| cop_at | -0.056 | -0.068 | 0.021 | -0.030 | -0.055 | -0.007 | -0.060 | kalite (tahakkuksuz kârlılık) | Ball, Gerakos, Linnainmaa & Nikolaev (2016) |
| dist_52w_high | 0.087 | 0.062 | 0.110 | 0.092 | 0.037 | 0.047 | 0.128 | davranışsal (çıpalama) | George & Hwang (2004) |
| droe | -0.039 | -0.020 | 0.005 | -0.022 | 0.034 | -0.036 | 0.003 | temel momentum | Hou, Xue & Zhang (2015) q-faktör ROE |
| ear_3d | -0.007 | 0.008 | -0.004 | 0.001 | -0.016 | -0.014 | 0.013 | davranışsal (duyuru getirisi sürüklenmesi) | Chan, Jegadeesh & Lakonishok (1996) |
| ebit_ev | 0.026 | -0.075 | -0.006 | -0.017 | -0.042 | -0.034 | -0.005 | değer (risk + davranışsal) | Loughran & Wellman (2011) |
| gross_profitability | 0.020 | -0.040 | 0.002 | -0.004 | -0.031 | -0.008 | -0.006 | risk/kalite | Novy-Marx (2013) |
| idio_vol_60d | 0.118 | 0.099 | 0.129 | 0.119 | 0.083 | 0.069 | 0.163 | sınırlı arbitraj / piyango tercihi (−) | Ang, Hodrick, Xing & Zhang (2006) |
| max_ret_21d | 0.103 | 0.078 | 0.101 | 0.094 | 0.086 | 0.057 | 0.132 | piyango tercihi (−) | Bali, Cakici & Whitelaw (2011) |
| mom_12_1 | 0.038 | -0.008 | 0.020 | 0.011 | 0.064 | 0.021 | 0.011 | davranışsal (yetersiz tepki) + risk | Jegadeesh & Titman (1993); Carhart (1997) |
| net_debt_ebitda | -0.055 | -0.078 | -0.029 | -0.055 | -0.042 | -0.029 | -0.078 | kaldıraç / sıkıntı riski (−) | Campbell, Hilscher & Szilagyi (2008) |
| ocf_ev | -0.014 | -0.020 | 0.057 | 0.012 | -0.019 | 0.053 | -0.036 | değer (nakit akışı) | Lakonishok, Shleifer & Vishny (1994) |
| oil_beta_trend | 0.009 | -0.085 | 0.031 | -0.018 | 0.008 | 0.040 | -0.073 | emtia risk primi + trend | Moskowitz, Ooi & Pedersen (2012) — tema uyarlaması |
| profitable_growth | — | — | -0.196 | -0.196 | — | 0.182 | -0.291 | kalite + büyüme | Mohanram (2005) GSCORE ruhunda |
| share_issuance | 0.069 | 0.037 | 0.103 | 0.074 | 0.035 | 0.059 | 0.083 | piyasa zamanlaması (−) | Pontiff & Woodgate (2008); Daniel & Titman (2006) |
| sue | -0.031 | -0.004 | 0.032 | -0.002 | 0.029 | -0.014 | 0.016 | davranışsal (kazanç sonrası sürüklenme) | Bernard & Thomas (1989) |
| sue_announce | 0.060 | 0.034 | 0.026 | 0.042 | 0.008 | 0.022 | 0.056 | davranışsal (PEAD, duyuru tarihli) | Bernard & Thomas (1989); Livnat & Mendenhall (2006) |

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
| asset_growth | 21 | 0.006 | 0.67 | 0.67 | 50.28% | 181 |
| asset_growth | 63 | 0.004 | 0.27 | 0.50 | 50.84% | 179 |
| asset_growth | 126 | 0.013 | 0.76 | 1.10 | 47.16% | 176 |
| capex_at | 21 | -0.003 | -0.34 | -0.33 | 53.85% | 182 |
| capex_at | 63 | 0.001 | 0.08 | 0.12 | 51.67% | 180 |
| capex_at | 126 | -0.016 | -0.98 | -0.96 | 45.20% | 177 |
| cash_runway_years | 21 | 0.006 | 0.59 | 0.62 | 53.80% | 171 |
| cash_runway_years | 63 | 0.011 | 0.77 | -0.00 | 55.03% | 169 |
| cash_runway_years | 126 | 0.017 | 0.99 | 0.29 | 57.23% | 166 |
| cop_at | 21 | 0.003 | 0.27 | 0.27 | 48.90% | 182 |
| cop_at | 63 | -0.007 | -0.41 | -0.48 | 45.56% | 180 |
| cop_at | 126 | 0.003 | 0.13 | -0.45 | 48.02% | 177 |
| dist_52w_high | 21 | 0.042 | 2.97 | 2.85 | 60.99% | 182 |
| dist_52w_high | 63 | 0.070 | 4.11 | 3.69 | 63.33% | 180 |
| dist_52w_high | 126 | 0.098 | 5.02 | 5.69 | 76.27% | 177 |
| droe | 21 | 0.001 | 0.11 | 0.11 | 49.72% | 181 |
| droe | 63 | 0.000 | 0.01 | 0.55 | 49.72% | 179 |
| droe | 126 | -0.021 | -1.01 | -0.67 | 50.00% | 176 |
| ear_3d | 21 | -0.014 | -1.56 | -1.59 | 46.15% | 182 |
| ear_3d | 63 | -0.019 | -1.85 | -0.80 | 45.00% | 180 |
| ear_3d | 126 | -0.012 | -1.12 | 0.39 | 44.07% | 177 |
| gross_profitability | 21 | -0.010 | -0.78 | -0.76 | 47.80% | 182 |
| gross_profitability | 63 | -0.025 | -1.27 | -1.29 | 42.78% | 180 |
| gross_profitability | 126 | -0.014 | -0.46 | -0.38 | 42.94% | 177 |
| idio_vol_60d | 21 | 0.055 | 3.75 | 3.67 | 57.69% | 182 |
| idio_vol_60d | 63 | 0.087 | 4.74 | 3.72 | 68.33% | 180 |
| idio_vol_60d | 126 | 0.134 | 6.05 | 5.70 | 79.66% | 177 |
| max_ret_21d | 21 | 0.040 | 2.99 | 2.96 | 57.14% | 182 |
| max_ret_21d | 63 | 0.069 | 3.93 | 2.53 | 63.33% | 180 |
| max_ret_21d | 126 | 0.105 | 5.13 | 3.75 | 72.32% | 177 |
| mom_12_1 | 21 | 0.008 | 0.72 | 0.75 | 48.90% | 182 |
| mom_12_1 | 63 | 0.005 | 0.34 | 0.37 | 47.78% | 180 |
| mom_12_1 | 126 | 0.007 | 0.38 | 0.58 | 49.72% | 177 |
| share_issuance | 21 | 0.037 | 2.63 | 2.60 | 55.25% | 181 |
| share_issuance | 63 | 0.051 | 2.79 | 2.56 | 59.78% | 179 |
| share_issuance | 126 | 0.073 | 3.05 | 2.24 | 60.23% | 176 |
| sue | 21 | 0.000 | 0.01 | 0.01 | 47.19% | 178 |
| sue | 63 | -0.003 | -0.21 | 0.42 | 46.59% | 176 |
| sue | 126 | 0.001 | 0.05 | 0.39 | 53.18% | 173 |
| sue_announce | 21 | 0.017 | 1.37 | 1.25 | 52.20% | 182 |
| sue_announce | 63 | 0.038 | 2.40 | 2.17 | 56.11% | 180 |
| sue_announce | 126 | 0.059 | 2.89 | 1.57 | 67.23% | 177 |

### 7.4 Tek değişkenli sıralama (EW; üst − alt = `mimic_`)

| Faktör | Ufuk | Port. | mimic EW | t | mimic VW | Üst − ort. | t | Monoton |
|---|---|---|---|---|---|---|---|---|
| asset_growth | 21 | 5 | 0.74% | 1.57 | -0.04% | 0.12% | 0.23 | ✘ |
| asset_growth | 63 | 5 | 0.47% | 0.38 | 0.72% | -0.13% | -0.12 | ✘ |
| asset_growth | 126 | 5 | 1.39% | 0.68 | 3.03% | 0.24% | 0.16 | ✘ |
| capex_at | 21 | 5 | 2.61% | 1.21 | 0.03% | 2.00% | 1.18 | ✘ |
| capex_at | 63 | 5 | 7.16% | 1.75 | 1.22% | 5.05% | 1.55 | ✘ |
| capex_at | 126 | 5 | 8.18% | 1.60 | 1.91% | 6.03% | 1.56 | ✘ |
| cash_runway_years | 21 | 5 | 2.37% | 0.70 | 0.66% | 2.71% | 1.02 | ✘ |
| cash_runway_years | 63 | 5 | 4.53% | 0.69 | 1.34% | 5.49% | 1.06 | ✘ |
| cash_runway_years | 126 | 5 | -10.68% | -1.37 | -5.17% | -1.94% | -0.94 | ✘ |
| cop_at | 21 | 5 | -0.31% | -0.52 | 0.52% | -0.40% | -1.24 | ✘ |
| cop_at | 63 | 5 | -1.37% | -0.99 | 1.26% | -1.21% | -1.53 | ✘ |
| cop_at | 126 | 5 | -3.23% | -1.27 | 1.00% | -2.66% | -1.85 | ✘ |
| dist_52w_high | 21 | 5 | 1.02% | 1.60 | 1.05% | -0.14% | -0.33 | ✘ |
| dist_52w_high | 63 | 5 | 2.42% | 1.75 | 2.59% | -0.33% | -0.30 | ✘ |
| dist_52w_high | 126 | 5 | 4.19% | 1.84 | 4.88% | 0.60% | 0.43 | ✘ |
| droe | 21 | 3 | 0.23% | 0.60 | 0.08% | 0.04% | 0.16 | ✘ |
| droe | 63 | 3 | 0.37% | 0.44 | 0.15% | 0.08% | 0.14 | ✘ |
| droe | 126 | 3 | -0.34% | -0.29 | -1.72% | 0.47% | 0.55 | ✘ |
| ear_3d | 21 | 5 | -0.75% | -1.59 | -0.73% | -0.47% | -1.75 | ✘ |
| ear_3d | 63 | 5 | -1.31% | -1.39 | -0.63% | -1.42% | -2.04 | ✘ |
| ear_3d | 126 | 5 | -5.18% | -1.08 | 1.02% | -2.18% | -1.87 | ✘ |
| gross_profitability | 21 | 3 | -0.29% | -0.85 | 0.07% | -0.02% | -0.13 | ✘ |
| gross_profitability | 63 | 3 | -0.88% | -0.91 | 0.36% | -0.22% | -0.46 | ✘ |
| gross_profitability | 126 | 3 | -1.57% | -0.77 | 1.04% | -0.57% | -0.57 | ✘ |
| idio_vol_60d | 21 | 5 | -1.84% | -0.86 | -0.03% | -0.16% | -0.28 | ✘ |
| idio_vol_60d | 63 | 5 | -3.59% | -0.84 | 1.67% | -0.49% | -0.37 | ✘ |
| idio_vol_60d | 126 | 5 | 3.63% | 1.47 | 4.90% | 1.11% | 0.55 | ✘ |
| max_ret_21d | 21 | 5 | 1.87% | 0.98 | 1.06% | 1.70% | 1.10 | ✘ |
| max_ret_21d | 63 | 5 | 0.41% | 0.20 | 1.60% | 1.59% | 1.08 | ✘ |
| max_ret_21d | 126 | 5 | 2.19% | 0.93 | 3.80% | 0.88% | 0.48 | ✘ |
| mom_12_1 | 21 | 5 | 2.60% | 1.31 | 1.35% | 1.43% | 0.93 | ✘ |
| mom_12_1 | 63 | 5 | 3.92% | 1.71 | 2.49% | 1.63% | 1.16 | ✔ |
| mom_12_1 | 126 | 5 | 1.79% | 0.78 | 0.98% | -0.54% | -0.30 | ✘ |
| share_issuance | 21 | 5 | 0.55% | 0.88 | 0.68% | 0.00% | 0.01 | ✘ |
| share_issuance | 63 | 5 | -0.31% | -0.19 | 1.23% | -0.55% | -0.49 | ✘ |
| share_issuance | 126 | 5 | -0.60% | -0.19 | 2.64% | -0.16% | -0.09 | ✘ |
| sue | 21 | 5 | -0.33% | -0.66 | -0.20% | 0.02% | 0.07 | ✘ |
| sue | 63 | 5 | -0.47% | -0.44 | -0.60% | 0.18% | 0.28 | ✘ |
| sue | 126 | 5 | 0.23% | 0.13 | -1.08% | 1.43% | 1.49 | ✘ |
| sue_announce | 21 | 5 | 0.13% | 0.16 | -0.66% | 0.61% | 1.41 | ✘ |
| sue_announce | 63 | 5 | 1.20% | 0.81 | -0.04% | 0.48% | 0.53 | ✘ |
| sue_announce | 126 | 5 | 4.52% | 2.02 | 1.78% | 2.01% | 1.45 | ✘ |

### 7.4 Alfalar (21 seans, aylık; NW t)

Üst portföy RF üzeri; `mimic_ew` ham fark.

| Faktör | Seri | capm t | ff3 t | carhart4 t | ff5_mom t |
|---|---|---|---|---|---|
| asset_growth | mimic_ew | 1.31 | 1.41 | 1.47 | 1.33 |
| asset_growth | top_ew | 0.68 | 1.61 | 1.63 | 1.86 |
| capex_at | mimic_ew | 1.22 | 1.25 | 1.32 | 1.42 |
| capex_at | top_ew | 1.16 | 1.35 | 1.36 | 1.51 |
| cash_runway_years | mimic_ew | 0.80 | 0.73 | 0.96 | 0.82 |
| cash_runway_years | top_ew | 0.98 | 1.10 | 1.18 | 1.20 |
| cop_at | mimic_ew | 0.10 | -0.10 | 0.22 | 0.20 |
| cop_at | top_ew | 0.05 | 0.44 | 0.47 | 0.67 |
| dist_52w_high | mimic_ew | 1.99 | 1.68 | 2.04 | 1.87 |
| dist_52w_high | top_ew | 1.05 | 1.54 | 1.61 | 1.79 |
| droe | mimic_ew | 0.05 | 0.12 | 0.19 | 0.19 |
| droe | top_ew | 0.43 | 0.83 | 0.78 | 0.90 |
| ear_3d | mimic_ew | -2.10 | -2.14 | -2.06 | -1.96 |
| ear_3d | top_ew | -0.86 | -0.23 | -0.27 | 0.06 |
| gross_profitability | mimic_ew | 0.49 | 0.30 | 0.52 | 0.59 |
| gross_profitability | top_ew | 0.72 | 1.12 | 1.20 | 1.26 |
| idio_vol_60d | mimic_ew | -0.62 | -0.79 | -0.96 | -0.93 |
| idio_vol_60d | top_ew | 2.21 | 2.51 | 2.59 | 2.61 |
| max_ret_21d | mimic_ew | 1.28 | 1.13 | 1.20 | 1.01 |
| max_ret_21d | top_ew | 1.26 | 1.36 | 1.33 | 1.39 |
| mom_12_1 | mimic_ew | 1.34 | 1.36 | 1.32 | 1.35 |
| mom_12_1 | top_ew | 0.88 | 1.07 | 1.15 | 1.20 |
| share_issuance | mimic_ew | 1.19 | 0.70 | 0.88 | 0.58 |
| share_issuance | top_ew | 1.66 | 2.09 | 2.12 | 2.18 |
| sue | mimic_ew | -0.17 | -0.13 | 0.15 | 0.10 |
| sue | top_ew | 0.77 | 1.21 | 1.21 | 1.23 |
| sue_announce | mimic_ew | 0.04 | -0.27 | -0.41 | -0.43 |
| sue_announce | top_ew | 1.43 | 2.01 | 1.72 | 1.93 |

### 7.5 Bağımlı iki değişkenli sıralama (tema skoru terciliyle kontrol)

| Faktör | Ufuk | Ort. fark | NW t |
|---|---|---|---|
| asset_growth | 21 | -0.60% | -0.54 |
| asset_growth | 63 | -1.87% | -0.84 |
| asset_growth | 126 | 0.69% | 0.42 |
| capex_at | 21 | 1.30% | 1.15 |
| capex_at | 63 | 3.88% | 1.84 |
| capex_at | 126 | 3.99% | 1.37 |
| cash_runway_years | 21 | 0.51% | 0.29 |
| cash_runway_years | 63 | 0.14% | 0.04 |
| cash_runway_years | 126 | -8.95% | -2.04 |
| cop_at | 21 | -0.52% | -1.73 |
| cop_at | 63 | -1.28% | -1.71 |
| cop_at | 126 | -1.97% | -1.45 |
| dist_52w_high | 21 | -0.31% | -0.29 |
| dist_52w_high | 63 | 0.64% | 0.48 |
| dist_52w_high | 126 | 2.71% | 2.09 |
| droe | 21 | 0.02% | 0.06 |
| droe | 63 | -0.18% | -0.23 |
| droe | 126 | -1.71% | -1.30 |
| ear_3d | 21 | -0.45% | -1.37 |
| ear_3d | 63 | -1.66% | -1.39 |
| ear_3d | 126 | -2.68% | -1.07 |
| gross_profitability | 21 | -0.31% | -1.13 |
| gross_profitability | 63 | -1.05% | -1.48 |
| gross_profitability | 126 | -1.41% | -0.97 |
| idio_vol_60d | 21 | -0.76% | -0.65 |
| idio_vol_60d | 63 | -2.34% | -0.97 |
| idio_vol_60d | 126 | 2.19% | 1.49 |
| max_ret_21d | 21 | 0.94% | 0.94 |
| max_ret_21d | 63 | -0.67% | -0.66 |
| max_ret_21d | 126 | 0.32% | 0.27 |
| mom_12_1 | 21 | 1.20% | 1.11 |
| mom_12_1 | 63 | 2.33% | 1.63 |
| mom_12_1 | 126 | 2.41% | 1.20 |
| share_issuance | 21 | -0.99% | -0.86 |
| share_issuance | 63 | -3.26% | -1.45 |
| share_issuance | 126 | -4.24% | -1.38 |
| sue | 21 | -0.09% | -0.31 |
| sue | 63 | -0.19% | -0.26 |
| sue | 126 | -0.88% | -0.67 |
| sue_announce | 21 | 0.10% | 0.24 |
| sue_announce | 63 | 0.73% | 0.76 |
| sue_announce | 126 | 1.82% | 1.20 |

### 7.6 Fama-MacBeth (tek faktör + β, ln(MktCap); NW t)

| Faktör | Ufuk | OLS rank-normal t | OLS ham t | WLS √MktCap t | 1 std etkisi | Ort. R² |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 1.65 | 1.50 | 0.49 | 0.23% | 6.95% |
| asset_growth | 63 | 0.76 | 1.34 | -0.00 | 0.28% | 5.93% |
| asset_growth | 126 | 0.76 | 1.28 | 0.34 | 0.48% | 5.45% |
| capex_at | 21 | 0.53 | -0.48 | -0.55 | 0.08% | 6.99% |
| capex_at | 63 | 1.99 | 0.86 | 0.64 | 0.75% | 5.97% |
| capex_at | 126 | 1.03 | -0.11 | 0.03 | 0.78% | 5.37% |
| cash_runway_years | 21 | -0.51 | -0.13 | -0.02 | -0.13% | 5.61% |
| cash_runway_years | 63 | -0.91 | -0.29 | -0.40 | -0.53% | 5.14% |
| cash_runway_years | 126 | -2.02 | -1.00 | -1.39 | -1.58% | 4.87% |
| cop_at | 21 | -0.39 | -1.22 | 0.18 | -0.05% | 11.50% |
| cop_at | 63 | -0.49 | -1.61 | 0.50 | -0.15% | 10.79% |
| cop_at | 126 | -0.38 | -1.37 | 0.82 | -0.20% | 10.86% |
| dist_52w_high | 21 | 0.70 | 1.46 | 0.83 | 0.15% | 7.45% |
| dist_52w_high | 63 | 1.66 | 2.34 | 1.66 | 0.75% | 6.39% |
| dist_52w_high | 126 | 1.74 | 2.28 | 1.34 | 1.33% | 6.02% |
| droe | 21 | 0.52 | -0.37 | -0.18 | 0.07% | 12.05% |
| droe | 63 | 0.74 | -0.31 | -0.08 | 0.24% | 11.85% |
| droe | 126 | 0.05 | -1.14 | -0.88 | 0.03% | 11.59% |
| ear_3d | 21 | -1.86 | -1.86 | -1.02 | -0.25% | 6.83% |
| ear_3d | 63 | -2.13 | -2.17 | -1.60 | -0.57% | 5.92% |
| ear_3d | 126 | -0.91 | -0.22 | -0.58 | -0.41% | 5.42% |
| gross_profitability | 21 | -0.99 | -1.16 | -0.44 | -0.14% | 12.69% |
| gross_profitability | 63 | -0.90 | -1.25 | 0.02 | -0.31% | 12.33% |
| gross_profitability | 126 | -0.51 | -0.87 | 0.44 | -0.39% | 12.33% |
| idio_vol_60d | 21 | 0.06 | 0.16 | 0.67 | 0.01% | 6.66% |
| idio_vol_60d | 63 | -0.53 | -0.66 | 0.49 | -0.28% | 5.92% |
| idio_vol_60d | 126 | 1.12 | 0.12 | 1.10 | 0.98% | 6.07% |
| max_ret_21d | 21 | 0.38 | 0.69 | 1.45 | 0.06% | 6.39% |
| max_ret_21d | 63 | -0.07 | -0.77 | 0.90 | -0.03% | 5.68% |
| max_ret_21d | 126 | 0.57 | -0.71 | 1.09 | 0.35% | 5.58% |
| mom_12_1 | 21 | 1.11 | 1.20 | 0.90 | 0.19% | 6.87% |
| mom_12_1 | 63 | 1.87 | 1.90 | 1.54 | 0.78% | 5.87% |
| mom_12_1 | 126 | 1.44 | 1.63 | 0.98 | 1.02% | 5.35% |
| share_issuance | 21 | 0.83 | -0.38 | 1.16 | 0.14% | 6.80% |
| share_issuance | 63 | -0.39 | -0.93 | 0.20 | -0.18% | 5.92% |
| share_issuance | 126 | -0.33 | -0.60 | 0.17 | -0.29% | 5.71% |
| sue | 21 | -0.12 | -0.42 | -0.37 | -0.01% | 10.87% |
| sue | 63 | 0.53 | 0.12 | 0.00 | 0.14% | 10.29% |
| sue | 126 | 0.49 | 0.23 | -0.41 | 0.24% | 10.43% |
| sue_announce | 21 | 0.47 | 0.63 | 0.52 | 0.08% | 11.96% |
| sue_announce | 63 | 1.24 | 1.44 | 1.23 | 0.52% | 10.79% |
| sue_announce | 126 | 1.28 | 1.86 | 0.73 | 1.00% | 11.66% |

Tüm faktörlü model (kapsama ≥ %50, eksiksiz satırlar):

| Ufuk | Faktör | Katsayı | NW t | Ort. düz. R² |
|---|---|---|---|---|
| 21 | asset_growth | -0.25% | -0.80 | 15.72% |
| 21 | capex_at | 0.34% | 1.64 | 15.72% |
| 21 | cash_runway_years | -0.35% | -0.85 | 15.72% |
| 21 | cop_at | 0.04% | 0.11 | 15.72% |
| 21 | dist_52w_high | 0.54% | 1.68 | 15.72% |
| 21 | droe | 0.19% | 0.68 | 15.72% |
| 21 | ear_3d | -0.04% | -0.20 | 15.72% |
| 21 | ebit_ev | -0.28% | -0.66 | 15.72% |
| 21 | gross_profitability | 0.21% | 0.83 | 15.72% |
| 21 | idio_vol_60d | -0.21% | -0.60 | 15.72% |
| 21 | max_ret_21d | 0.25% | 0.99 | 15.72% |
| 21 | mom_12_1 | 0.19% | 0.63 | 15.72% |
| 21 | ocf_ev | 0.28% | 0.62 | 15.72% |
| 21 | share_issuance | 0.43% | 1.70 | 15.72% |
| 21 | sue | -0.15% | -0.54 | 15.72% |
| 63 | asset_growth | -0.69% | -0.97 | 13.68% |
| 63 | capex_at | 1.01% | 2.03 | 13.68% |
| 63 | cash_runway_years | -0.27% | -0.28 | 13.68% |
| 63 | cop_at | -0.16% | -0.13 | 13.68% |
| 63 | dist_52w_high | 0.41% | 0.56 | 13.68% |
| 63 | droe | 0.29% | 0.45 | 13.68% |
| 63 | ear_3d | 0.39% | 0.81 | 13.68% |
| 63 | ebit_ev | -0.53% | -0.54 | 13.68% |
| 63 | gross_profitability | 0.42% | 0.53 | 13.68% |
| 63 | idio_vol_60d | 0.56% | 0.90 | 13.68% |
| 63 | max_ret_21d | 0.33% | 0.60 | 13.68% |
| 63 | mom_12_1 | 0.25% | 0.38 | 13.68% |
| 63 | ocf_ev | 0.52% | 0.49 | 13.68% |
| 63 | share_issuance | 0.30% | 0.51 | 13.68% |
| 63 | sue | -0.12% | -0.20 | 13.68% |
| 126 | asset_growth | -1.87% | -1.60 | 11.57% |
| 126 | capex_at | 1.39% | 1.52 | 11.57% |
| 126 | cash_runway_years | -0.75% | -0.39 | 11.57% |
| 126 | cop_at | 0.15% | 0.07 | 11.57% |
| 126 | dist_52w_high | 0.09% | 0.06 | 11.57% |
| 126 | droe | 1.55% | 0.87 | 11.57% |
| 126 | ear_3d | -0.04% | -0.05 | 11.57% |
| 126 | ebit_ev | -2.68% | -1.56 | 11.57% |
| 126 | gross_profitability | 0.88% | 0.49 | 11.57% |
| 126 | idio_vol_60d | 3.42% | 2.65 | 11.57% |
| 126 | max_ret_21d | 0.36% | 0.55 | 11.57% |
| 126 | mom_12_1 | 0.90% | 0.92 | 11.57% |
| 126 | ocf_ev | 3.48% | 1.84 | 11.57% |
| 126 | share_issuance | -0.22% | -0.19 | 11.57% |
| 126 | sue | -0.82% | -0.72 | 11.57% |

### 7.1 Tanımlayıcı istatistikler (winsorize %0,5/%99,5; aylık değerlerin zaman ortalaması)

| Faktör | Ort. | Std | Çarp. | Bas. | P5 | Medyan | P95 | n | Ort. kayması |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.392 | 0.780 | 2.74 | 9.83 | -0.248 | 0.151 | 1.890 | 140 | 0.24 |
| capex_at | 0.017 | 0.020 | 2.28 | 6.77 | 0.001 | 0.010 | 0.056 | 134 | 0.20 |
| cash_runway_years | 6.018 | 3.784 | -0.14 | -1.38 | 0.853 | 6.095 | 10.000 | 142 | 0.21 |
| cop_at | -0.122 | 0.278 | -0.94 | 1.53 | -0.607 | -0.085 | 0.220 | 142 | 0.23 |
| dist_52w_high | -0.268 | 0.185 | -0.72 | -0.02 | -0.607 | -0.238 | -0.033 | 144 | 0.46 |
| droe | -0.006 | 0.242 | -0.05 | 7.34 | -0.358 | -0.003 | 0.336 | 125 | 0.12 |
| ear_3d | 0.007 | 0.099 | 0.46 | 3.54 | -0.136 | 0.002 | 0.165 | 131 | 0.10 |
| ebit_ev | -0.101 | 0.294 | -2.83 | 18.13 | -0.414 | -0.048 | 0.090 | 133 | 0.30 |
| gross_profitability | 0.313 | 0.209 | 0.83 | 0.95 | 0.041 | 0.281 | 0.684 | 75 | 0.21 |
| idio_vol_60d | 0.546 | 0.372 | 2.51 | 11.29 | 0.193 | 0.479 | 1.096 | 144 | 0.30 |
| max_ret_21d | 0.083 | 0.093 | 3.83 | 20.88 | 0.023 | 0.060 | 0.199 | 144 | 0.23 |
| mom_12_1 | 0.436 | 1.111 | 2.82 | 13.55 | -0.454 | 0.169 | 2.094 | 144 | 0.36 |
| net_debt_ebitda | 0.461 | 8.309 | 1.01 | 6.93 | -11.357 | 0.040 | 12.170 | 43 | 0.16 |
| ocf_ev | -0.059 | 0.233 | -2.41 | 15.58 | -0.316 | -0.021 | 0.106 | 141 | 0.28 |
| profitable_growth | 1.076 | 0.417 | 0.08 | -0.52 | 0.431 | 1.062 | 1.765 | 53 | 0.05 |
| share_issuance | 0.105 | 0.191 | 2.74 | 13.14 | -0.034 | 0.045 | 0.395 | 138 | 0.25 |
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
| asset_growth | 21 | 0.007 | 0.80 |
| asset_growth | 63 | 0.003 | 0.19 |
| asset_growth | 126 | 0.012 | 0.76 |
| capex_at | 21 | -0.006 | -0.63 |
| capex_at | 63 | -0.004 | -0.35 |
| capex_at | 126 | -0.021 | -1.37 |
| cash_runway_years | 21 | -0.022 | -2.01 |
| cash_runway_years | 63 | -0.028 | -2.11 |
| cash_runway_years | 126 | -0.033 | -1.71 |
| cop_at | 21 | -0.011 | -0.94 |
| cop_at | 63 | -0.029 | -1.97 |
| cop_at | 126 | -0.032 | -1.44 |
| dist_52w_high | 21 | 0.020 | 1.87 |
| dist_52w_high | 63 | 0.040 | 3.00 |
| dist_52w_high | 126 | 0.049 | 3.26 |
| droe | 21 | -0.003 | -0.27 |
| droe | 63 | -0.015 | -0.89 |
| droe | 126 | -0.058 | -3.03 |
| ear_3d | 21 | -0.013 | -1.52 |
| ear_3d | 63 | -0.020 | -1.94 |
| ear_3d | 126 | -0.013 | -1.38 |
| gross_profitability | 21 | -0.019 | -1.56 |
| gross_profitability | 63 | -0.040 | -2.30 |
| gross_profitability | 126 | -0.045 | -1.64 |
| idio_vol_60d | 21 | 0.036 | 3.12 |
| idio_vol_60d | 63 | 0.060 | 4.15 |
| idio_vol_60d | 126 | 0.093 | 5.58 |
| max_ret_21d | 21 | 0.021 | 1.95 |
| max_ret_21d | 63 | 0.039 | 2.88 |
| max_ret_21d | 126 | 0.062 | 4.23 |
| mom_12_1 | 21 | -0.008 | -0.74 |
| mom_12_1 | 63 | -0.018 | -1.24 |
| mom_12_1 | 126 | -0.029 | -1.56 |
| share_issuance | 21 | 0.024 | 2.01 |
| share_issuance | 63 | 0.029 | 1.88 |
| share_issuance | 126 | 0.039 | 2.06 |
| sue | 21 | -0.016 | -1.24 |
| sue | 63 | -0.031 | -1.96 |
| sue | 126 | -0.044 | -2.31 |
| sue_announce | 21 | 0.005 | 0.45 |
| sue_announce | 63 | 0.021 | 1.52 |
| sue_announce | 126 | 0.027 | 1.59 |

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
| asset_growth | 0.035 | 0.003 | 0.004 | 0.014 | 0.003 | 0.013 | 0.012 | aşırı yatırım / q-teorisi (−) | Cooper, Gulen & Schill (2008); Hou, Xue & Zhang (2015) |
| capex_at | -0.057 | -0.040 | 0.041 | -0.023 | 0.047 | -0.007 | -0.026 | yatırım faktörü (−) | Titman, Wei & Xie (2004); Fama & French (2015) CMA |
| cash_runway_years | -0.042 | 0.029 | 0.046 | 0.019 | -0.004 | 0.016 | 0.017 | finansal kısıt / seyreltme riski | Hadlock & Pierce (2010) — tema uyarlaması |
| cop_at | -0.001 | -0.023 | 0.031 | 0.005 | -0.018 | -0.009 | 0.015 | kalite (tahakkuksuz kârlılık) | Ball, Gerakos, Linnainmaa & Nikolaev (2016) |
| dist_52w_high | 0.094 | 0.065 | 0.132 | 0.097 | 0.104 | 0.091 | 0.104 | davranışsal (çıpalama) | George & Hwang (2004) |
| droe | -0.041 | -0.029 | 0.005 | -0.028 | 0.051 | -0.045 | 0.004 | temel momentum | Hou, Xue & Zhang (2015) q-faktör ROE |
| ear_3d | -0.020 | 0.001 | -0.017 | -0.007 | -0.062 | -0.019 | -0.005 | davranışsal (duyuru getirisi sürüklenmesi) | Chan, Jegadeesh & Lakonishok (1996) |
| gross_profitability | -0.090 | 0.006 | 0.031 | -0.019 | 0.030 | -0.028 | 0.000 | risk/kalite | Novy-Marx (2013) |
| idio_vol_60d | 0.142 | 0.092 | 0.166 | 0.133 | 0.141 | 0.130 | 0.137 | sınırlı arbitraj / piyango tercihi (−) | Ang, Hodrick, Xing & Zhang (2006) |
| max_ret_21d | 0.120 | 0.064 | 0.130 | 0.102 | 0.132 | 0.105 | 0.105 | piyango tercihi (−) | Bali, Cakici & Whitelaw (2011) |
| mom_12_1 | 0.000 | 0.021 | -0.001 | -0.005 | 0.118 | 0.018 | -0.005 | davranışsal (yetersiz tepki) + risk | Jegadeesh & Titman (1993); Carhart (1997) |
| share_issuance | 0.103 | 0.036 | 0.082 | 0.080 | 0.003 | 0.063 | 0.083 | piyasa zamanlaması (−) | Pontiff & Woodgate (2008); Daniel & Titman (2006) |
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
| dist_52w_high | 63 | 0.042 | 1.19 | 1.05 | 52.22% | 180 |
| dist_52w_high | 126 | 0.052 | 1.02 | 0.89 | 53.67% | 177 |
| ear_3d | 21 | 0.024 | 2.42 | 2.32 | 56.04% | 182 |
| ear_3d | 63 | 0.019 | 1.52 | 0.76 | 60.00% | 180 |
| ear_3d | 126 | 0.022 | 1.37 | 0.94 | 55.93% | 177 |
| ebit_ev | 21 | 0.003 | 0.13 | 0.14 | 50.00% | 182 |
| ebit_ev | 63 | -0.017 | -0.65 | -0.97 | 46.11% | 180 |
| ebit_ev | 126 | -0.020 | -0.57 | -0.45 | 49.15% | 177 |
| gross_profitability | 21 | -0.000 | -0.03 | -0.03 | 48.35% | 182 |
| gross_profitability | 63 | -0.020 | -0.84 | -0.72 | 47.22% | 180 |
| gross_profitability | 126 | -0.023 | -0.82 | -0.90 | 38.98% | 177 |
| idio_vol_60d | 21 | 0.040 | 1.33 | 1.37 | 52.75% | 182 |
| idio_vol_60d | 63 | 0.052 | 1.29 | 1.19 | 54.44% | 180 |
| idio_vol_60d | 126 | 0.076 | 1.33 | 1.11 | 51.41% | 177 |
| max_ret_21d | 21 | 0.031 | 1.15 | 1.17 | 53.85% | 182 |
| max_ret_21d | 63 | 0.047 | 1.37 | 1.29 | 52.22% | 180 |
| max_ret_21d | 126 | 0.055 | 1.14 | 0.85 | 53.67% | 177 |
| mom_12_1 | 21 | 0.013 | 0.56 | 0.56 | 50.55% | 182 |
| mom_12_1 | 63 | 0.027 | 0.91 | 0.80 | 52.22% | 180 |
| mom_12_1 | 126 | 0.033 | 0.76 | 0.75 | 54.24% | 177 |
| net_debt_ebitda | 21 | -0.013 | -0.67 | -0.72 | 50.55% | 182 |
| net_debt_ebitda | 63 | -0.034 | -1.29 | -1.26 | 48.33% | 180 |
| net_debt_ebitda | 126 | -0.053 | -1.55 | -1.29 | 44.63% | 177 |
| ocf_ev | 21 | 0.013 | 0.63 | 0.68 | 51.10% | 182 |
| ocf_ev | 63 | 0.008 | 0.27 | -0.26 | 51.67% | 180 |
| ocf_ev | 126 | 0.009 | 0.21 | 0.02 | 55.93% | 177 |
| oil_beta_trend | 21 | 0.008 | 0.34 | 0.34 | 54.40% | 182 |
| oil_beta_trend | 63 | -0.019 | -0.57 | -0.01 | 48.33% | 180 |
| oil_beta_trend | 126 | -0.015 | -0.41 | -0.66 | 48.02% | 177 |
| share_issuance | 21 | 0.022 | 2.03 | 2.08 | 58.24% | 182 |
| share_issuance | 63 | 0.028 | 1.83 | 1.17 | 62.78% | 180 |
| share_issuance | 126 | 0.041 | 1.95 | 0.94 | 66.10% | 177 |
| sue_announce | 21 | 0.021 | 1.49 | 1.47 | 52.20% | 182 |
| sue_announce | 63 | 0.024 | 1.18 | 0.61 | 51.11% | 180 |
| sue_announce | 126 | 0.024 | 0.98 | 1.29 | 56.50% | 177 |

### 7.4 Tek değişkenli sıralama (EW; üst − alt = `mimic_`)

| Faktör | Ufuk | Port. | mimic EW | t | mimic VW | Üst − ort. | t | Monoton |
|---|---|---|---|---|---|---|---|---|
| asset_growth | 21 | 5 | 0.82% | 1.72 | 0.26% | 0.47% | 1.43 | ✘ |
| asset_growth | 63 | 5 | 2.22% | 1.91 | 0.87% | 1.35% | 1.86 | ✘ |
| asset_growth | 126 | 5 | 4.64% | 1.93 | 1.39% | 2.84% | 1.78 | ✘ |
| capex_at | 21 | 5 | 0.39% | 0.82 | 0.16% | 0.16% | 0.63 | ✘ |
| capex_at | 63 | 5 | 1.95% | 1.57 | 0.98% | 0.88% | 1.21 | ✘ |
| capex_at | 126 | 5 | 4.91% | 1.79 | 1.93% | 1.89% | 1.25 | ✘ |
| cash_runway_years | 21 | 3 | -4.44% | -1.07 | -8.67% | -3.45% | -2.77 | ✘ |
| cash_runway_years | 63 | 3 | -10.11% | -3.04 | -22.23% | -2.21% | -0.77 | ✘ |
| cash_runway_years | 126 | 3 | -25.24% | -8.70 | -43.74% | -9.06% | -8.77 | ✘ |
| cop_at | 21 | 5 | 0.05% | 0.10 | 0.22% | 0.02% | 0.07 | ✘ |
| cop_at | 63 | 5 | -0.53% | -0.43 | -0.08% | -0.40% | -0.54 | ✘ |
| cop_at | 126 | 5 | -1.84% | -0.71 | -1.06% | -1.19% | -0.76 | ✘ |
| dist_52w_high | 21 | 5 | -0.01% | -0.01 | 0.37% | 0.01% | 0.02 | ✘ |
| dist_52w_high | 63 | 5 | -0.82% | -0.40 | 0.71% | -0.25% | -0.28 | ✘ |
| dist_52w_high | 126 | 5 | -1.21% | -0.29 | 0.64% | -0.32% | -0.18 | ✘ |
| ear_3d | 21 | 5 | 0.39% | 1.04 | 0.10% | 0.24% | 1.10 | ✘ |
| ear_3d | 63 | 5 | 0.52% | 0.68 | -0.29% | 0.40% | 0.79 | ✘ |
| ear_3d | 126 | 5 | 1.74% | 1.41 | 1.99% | 1.24% | 1.33 | ✘ |
| ebit_ev | 21 | 5 | -0.42% | -0.73 | -0.34% | -0.06% | -0.17 | ✘ |
| ebit_ev | 63 | 5 | -2.05% | -1.44 | -1.50% | -1.01% | -1.39 | ✘ |
| ebit_ev | 126 | 5 | -4.45% | -1.69 | -3.67% | -2.08% | -1.49 | ✘ |
| gross_profitability | 21 | 5 | -0.12% | -0.21 | -0.97% | -0.09% | -0.23 | ✘ |
| gross_profitability | 63 | 5 | -0.17% | -0.11 | -2.64% | -0.50% | -0.52 | ✘ |
| gross_profitability | 126 | 5 | 0.23% | 0.09 | -4.02% | 0.11% | 0.06 | ✘ |
| idio_vol_60d | 21 | 5 | -0.48% | -0.47 | 0.04% | -0.15% | -0.31 | ✘ |
| idio_vol_60d | 63 | 5 | -1.76% | -0.69 | -0.58% | -0.43% | -0.39 | ✘ |
| idio_vol_60d | 126 | 5 | -2.51% | -0.51 | -0.49% | -0.78% | -0.35 | ✘ |
| max_ret_21d | 21 | 5 | -0.56% | -0.64 | -0.20% | -0.23% | -0.55 | ✘ |
| max_ret_21d | 63 | 5 | -1.61% | -0.75 | -0.08% | -0.58% | -0.60 | ✘ |
| max_ret_21d | 126 | 5 | -3.14% | -0.77 | -1.64% | -1.34% | -0.70 | ✘ |
| mom_12_1 | 21 | 5 | 0.45% | 0.60 | -0.13% | 0.49% | 1.37 | ✘ |
| mom_12_1 | 63 | 5 | 1.39% | 0.86 | 0.06% | 1.40% | 1.80 | ✘ |
| mom_12_1 | 126 | 5 | 1.64% | 0.48 | -1.42% | 2.09% | 1.45 | ✘ |
| net_debt_ebitda | 21 | 5 | 0.24% | 0.53 | 0.21% | 0.15% | 0.49 | ✘ |
| net_debt_ebitda | 63 | 5 | 0.26% | 0.23 | -0.16% | 0.19% | 0.25 | ✘ |
| net_debt_ebitda | 126 | 5 | 0.17% | 0.08 | -1.02% | 0.19% | 0.13 | ✘ |
| ocf_ev | 21 | 5 | 0.46% | 0.71 | 0.57% | 0.08% | 0.19 | ✘ |
| ocf_ev | 63 | 5 | 0.60% | 0.39 | 0.85% | -0.28% | -0.29 | ✘ |
| ocf_ev | 126 | 5 | 0.41% | 0.12 | 1.13% | -0.99% | -0.46 | ✘ |
| oil_beta_trend | 21 | 5 | 0.45% | 0.58 | 0.73% | 0.35% | 0.88 | ✘ |
| oil_beta_trend | 63 | 5 | -0.53% | -0.29 | 0.33% | 0.22% | 0.21 | ✘ |
| oil_beta_trend | 126 | 5 | 0.06% | 0.02 | 1.40% | 0.59% | 0.32 | ✘ |
| share_issuance | 21 | 5 | -0.04% | -0.11 | 0.09% | 0.11% | 0.49 | ✘ |
| share_issuance | 63 | 5 | -0.07% | -0.07 | 0.34% | 0.07% | 0.13 | ✘ |
| share_issuance | 126 | 5 | 0.85% | 0.47 | 1.32% | 0.24% | 0.23 | ✘ |
| sue_announce | 21 | 5 | 0.26% | 0.58 | 0.29% | -0.01% | -0.06 | ✘ |
| sue_announce | 63 | 5 | 0.45% | 0.48 | 1.03% | -0.29% | -0.57 | ✘ |
| sue_announce | 126 | 5 | 0.55% | 0.35 | 0.89% | 0.03% | 0.03 | ✘ |

### 7.4 Alfalar (21 seans, aylık; NW t)

Üst portföy RF üzeri; `mimic_ew` ham fark.

| Faktör | Seri | capm t | ff3 t | carhart4 t | ff5_mom t |
|---|---|---|---|---|---|
| asset_growth | mimic_ew | 1.70 | 1.68 | 1.65 | 1.67 |
| asset_growth | top_ew | 0.15 | 0.12 | 0.11 | -0.09 |
| capex_at | mimic_ew | 1.04 | 1.36 | 0.74 | 0.94 |
| capex_at | top_ew | -0.27 | -0.22 | -0.40 | -0.42 |
| cash_runway_years | mimic_ew | -1.35 | — | — | — |
| cash_runway_years | top_ew | -2.46 | — | — | — |
| cop_at | mimic_ew | -0.65 | -0.83 | -0.56 | -0.77 |
| cop_at | top_ew | -0.52 | -0.73 | -0.62 | -0.86 |
| dist_52w_high | mimic_ew | 1.56 | 1.66 | 1.21 | 1.14 |
| dist_52w_high | top_ew | 1.39 | 1.32 | 0.74 | 0.40 |
| ear_3d | mimic_ew | 1.46 | 1.46 | 1.52 | 1.16 |
| ear_3d | top_ew | -0.10 | -0.10 | -0.10 | -0.34 |
| ebit_ev | mimic_ew | -0.69 | -0.86 | -0.50 | -1.03 |
| ebit_ev | top_ew | -0.80 | -1.05 | -0.83 | -1.30 |
| gross_profitability | mimic_ew | 0.18 | -0.04 | 0.12 | -0.01 |
| gross_profitability | top_ew | -0.48 | -0.75 | -0.68 | -0.92 |
| idio_vol_60d | mimic_ew | 0.83 | 0.74 | 0.59 | 0.50 |
| idio_vol_60d | top_ew | 1.06 | 0.74 | 0.54 | 0.27 |
| max_ret_21d | mimic_ew | 0.57 | 0.39 | 0.29 | 0.15 |
| max_ret_21d | top_ew | 0.50 | 0.13 | -0.03 | -0.34 |
| mom_12_1 | mimic_ew | 1.42 | 1.26 | 0.28 | 0.59 |
| mom_12_1 | top_ew | 0.66 | 0.71 | 0.05 | 0.18 |
| net_debt_ebitda | mimic_ew | -0.56 | -0.47 | -0.64 | -0.84 |
| net_debt_ebitda | top_ew | -0.66 | -0.78 | -0.90 | -1.12 |
| ocf_ev | mimic_ew | -0.04 | -0.17 | 0.23 | -0.07 |
| ocf_ev | top_ew | -0.57 | -0.77 | -0.60 | -0.85 |
| oil_beta_trend | mimic_ew | 1.98 | 2.04 | 1.75 | 1.84 |
| oil_beta_trend | top_ew | 0.57 | 0.71 | 0.69 | 0.53 |
| share_issuance | mimic_ew | -0.01 | -0.23 | -0.08 | -0.63 |
| share_issuance | top_ew | -0.20 | -0.39 | -0.24 | -0.73 |
| sue_announce | mimic_ew | 1.26 | 1.15 | 0.71 | 0.84 |
| sue_announce | top_ew | -0.11 | -0.26 | -0.51 | -0.75 |

### 7.5 Bağımlı iki değişkenli sıralama (tema skoru terciliyle kontrol)

| Faktör | Ufuk | Ort. fark | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.68% | 1.71 |
| asset_growth | 63 | 1.90% | 2.12 |
| asset_growth | 126 | 4.31% | 2.31 |
| capex_at | 21 | 0.54% | 1.58 |
| capex_at | 63 | 2.02% | 2.24 |
| capex_at | 126 | 4.14% | 2.17 |
| cop_at | 21 | 0.01% | 0.01 |
| cop_at | 63 | -0.46% | -0.34 |
| cop_at | 126 | -1.46% | -0.52 |
| dist_52w_high | 21 | -0.16% | -0.26 |
| dist_52w_high | 63 | -0.60% | -0.42 |
| dist_52w_high | 126 | -0.62% | -0.21 |
| ear_3d | 21 | 0.30% | 1.15 |
| ear_3d | 63 | 0.37% | 0.71 |
| ear_3d | 126 | 1.27% | 1.39 |
| ebit_ev | 21 | -0.42% | -0.95 |
| ebit_ev | 63 | -1.51% | -1.38 |
| ebit_ev | 126 | -2.92% | -1.37 |
| gross_profitability | 21 | 0.22% | 0.67 |
| gross_profitability | 63 | 0.22% | 0.25 |
| gross_profitability | 126 | 1.45% | 0.83 |
| idio_vol_60d | 21 | -0.47% | -0.65 |
| idio_vol_60d | 63 | -1.30% | -0.73 |
| idio_vol_60d | 126 | -1.79% | -0.49 |
| max_ret_21d | 21 | -0.49% | -0.82 |
| max_ret_21d | 63 | -1.02% | -0.70 |
| max_ret_21d | 126 | -1.68% | -0.58 |
| mom_12_1 | 21 | 0.19% | 0.37 |
| mom_12_1 | 63 | 0.75% | 0.66 |
| mom_12_1 | 126 | 1.37% | 0.55 |
| net_debt_ebitda | 21 | 0.06% | 0.12 |
| net_debt_ebitda | 63 | -0.31% | -0.28 |
| net_debt_ebitda | 126 | -0.42% | -0.19 |
| ocf_ev | 21 | 0.54% | 0.94 |
| ocf_ev | 63 | 1.05% | 0.74 |
| ocf_ev | 126 | 1.56% | 0.53 |
| oil_beta_trend | 21 | 0.41% | 0.77 |
| oil_beta_trend | 63 | 0.20% | 0.15 |
| oil_beta_trend | 126 | 1.18% | 0.52 |
| share_issuance | 21 | -0.10% | -0.36 |
| share_issuance | 63 | -0.14% | -0.20 |
| share_issuance | 126 | 0.00% | 0.00 |
| sue_announce | 21 | 0.42% | 1.28 |
| sue_announce | 63 | 1.11% | 1.54 |
| sue_announce | 126 | 1.72% | 1.35 |

### 7.6 Fama-MacBeth (tek faktör + β, ln(MktCap); NW t)

| Faktör | Ufuk | OLS rank-normal t | OLS ham t | WLS √MktCap t | 1 std etkisi | Ort. R² |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 2.07 | 1.45 | 1.59 | 0.26% | 17.85% |
| asset_growth | 63 | 1.95 | 1.33 | 1.69 | 0.60% | 15.78% |
| asset_growth | 126 | 1.77 | 1.27 | 1.56 | 1.15% | 15.60% |
| capex_at | 21 | 0.92 | 0.31 | 1.16 | 0.13% | 18.17% |
| capex_at | 63 | 1.46 | 0.92 | 1.49 | 0.58% | 16.13% |
| capex_at | 126 | 1.46 | 1.14 | 1.34 | 1.21% | 15.89% |
| cash_runway_years | 21 | -0.79 | -1.13 | -1.51 | -1.29% | 29.59% |
| cash_runway_years | 63 | -1.64 | -2.72 | -2.76 | -3.51% | 28.99% |
| cash_runway_years | 126 | -10.59 | -3.47 | -11.83 | -10.31% | 28.97% |
| cop_at | 21 | 0.02 | 0.05 | 0.36 | 0.00% | 19.35% |
| cop_at | 63 | -0.73 | -0.89 | -0.38 | -0.26% | 17.73% |
| cop_at | 126 | -0.99 | -1.35 | -0.72 | -0.68% | 17.15% |
| dist_52w_high | 21 | 0.61 | 1.01 | 0.68 | 0.16% | 19.27% |
| dist_52w_high | 63 | 0.25 | 0.55 | 0.67 | 0.14% | 17.33% |
| dist_52w_high | 126 | 0.03 | 0.46 | 0.35 | 0.02% | 16.02% |
| ear_3d | 21 | 0.73 | 0.79 | 0.33 | 0.09% | 17.92% |
| ear_3d | 63 | 0.75 | 0.65 | 0.83 | 0.19% | 16.07% |
| ear_3d | 126 | 1.09 | 1.14 | 1.43 | 0.46% | 15.31% |
| ebit_ev | 21 | -0.15 | -0.14 | 0.33 | -0.02% | 20.12% |
| ebit_ev | 63 | -0.46 | -0.50 | -0.17 | -0.18% | 18.77% |
| ebit_ev | 126 | -0.49 | -0.84 | -0.15 | -0.33% | 18.44% |
| gross_profitability | 21 | 0.44 | -0.92 | -0.12 | 0.06% | 16.53% |
| gross_profitability | 63 | -0.19 | -1.13 | -0.61 | -0.07% | 15.44% |
| gross_profitability | 126 | -0.18 | -1.25 | -0.61 | -0.13% | 14.52% |
| idio_vol_60d | 21 | -0.67 | -1.09 | -0.17 | -0.20% | 19.18% |
| idio_vol_60d | 63 | -1.02 | -1.30 | -0.63 | -0.77% | 17.03% |
| idio_vol_60d | 126 | -1.01 | -1.17 | -0.66 | -1.32% | 16.03% |
| max_ret_21d | 21 | -0.29 | -0.95 | -0.07 | -0.06% | 18.26% |
| max_ret_21d | 63 | -0.46 | -0.81 | 0.04 | -0.20% | 15.90% |
| max_ret_21d | 126 | -1.30 | -1.31 | -0.90 | -0.92% | 15.16% |
| mom_12_1 | 21 | 1.39 | 2.06 | 1.41 | 0.30% | 20.32% |
| mom_12_1 | 63 | 1.90 | 1.90 | 2.16 | 0.95% | 18.06% |
| mom_12_1 | 126 | 1.63 | 1.85 | 1.81 | 1.47% | 16.97% |
| net_debt_ebitda | 21 | 0.53 | 0.92 | 0.48 | 0.07% | 19.38% |
| net_debt_ebitda | 63 | 0.38 | 0.74 | -0.15 | 0.13% | 17.89% |
| net_debt_ebitda | 126 | 0.59 | 0.50 | -0.28 | 0.33% | 17.48% |
| ocf_ev | 21 | 0.86 | 1.17 | 1.28 | 0.14% | 20.18% |
| ocf_ev | 63 | 0.39 | 0.56 | 0.71 | 0.16% | 18.50% |
| ocf_ev | 126 | 0.22 | 0.20 | 0.60 | 0.19% | 18.18% |
| oil_beta_trend | 21 | -0.11 | 0.19 | 0.38 | -0.03% | 15.88% |
| oil_beta_trend | 63 | -0.59 | -0.16 | -0.35 | -0.32% | 15.83% |
| oil_beta_trend | 126 | -0.23 | 0.21 | -0.19 | -0.23% | 16.04% |
| share_issuance | 21 | 0.73 | 0.14 | 0.98 | 0.08% | 17.94% |
| share_issuance | 63 | 0.57 | -0.27 | 0.85 | 0.15% | 15.67% |
| share_issuance | 126 | 0.53 | -0.21 | 0.73 | 0.28% | 15.40% |
| sue_announce | 21 | 1.66 | 1.51 | 2.08 | 0.17% | 20.05% |
| sue_announce | 63 | 1.56 | 1.60 | 2.09 | 0.37% | 18.00% |
| sue_announce | 126 | 1.48 | 1.65 | 2.02 | 0.66% | 16.97% |

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
| dist_52w_high | -0.193 | 0.159 | -1.20 | 1.32 | -0.504 | -0.150 | -0.024 | 142 | 0.47 |
| droe | -0.003 | 0.129 | -0.68 | 14.18 | -0.150 | -0.000 | 0.142 | 127 | 0.30 |
| ear_3d | 0.002 | 0.066 | 0.19 | 3.09 | -0.099 | 0.001 | 0.106 | 132 | 0.13 |
| ebit_ev | 0.051 | 0.200 | -0.96 | 19.04 | -0.110 | 0.052 | 0.171 | 124 | 0.31 |
| gross_profitability | 0.172 | 0.176 | 0.11 | 7.91 | 0.014 | 0.148 | 0.447 | 66 | 0.21 |
| idio_vol_60d | 0.357 | 0.246 | 1.68 | 6.51 | 0.155 | 0.313 | 0.703 | 143 | 0.48 |
| max_ret_21d | 0.050 | 0.036 | 2.24 | 8.22 | 0.017 | 0.040 | 0.114 | 143 | 0.57 |
| mom_12_1 | 0.201 | 0.711 | 2.25 | 14.76 | -0.352 | 0.088 | 0.993 | 143 | 0.55 |
| net_debt_ebitda | 3.833 | 4.730 | 2.41 | 13.20 | -0.837 | 3.337 | 9.809 | 112 | 0.20 |
| ocf_ev | 0.104 | 0.087 | 1.29 | 6.98 | 0.006 | 0.083 | 0.253 | 139 | 0.20 |
| oil_beta_trend | -0.024 | 0.378 | -0.36 | 8.22 | -0.443 | -0.024 | 0.409 | 90 | 1.21 |
| profitable_growth | 1.008 | 0.407 | 0.07 | -0.63 | 0.364 | 0.998 | 1.675 | 122 | 0.06 |
| share_issuance | 0.047 | 0.191 | 2.67 | 19.20 | -0.060 | 0.005 | 0.307 | 133 | 0.13 |
| sue | 0.108 | 1.068 | 0.05 | 0.43 | -1.653 | 0.076 | 1.878 | 136 | 0.29 |
| sue_announce | 0.199 | 1.154 | 0.21 | 0.26 | -1.556 | 0.151 | 2.072 | 82 | 0.31 |

### 7.2 Korelasyon ve çoklu doğrusallık

Tam matris (alt üçgen Pearson, üst üçgen Spearman): `corr.csv`. |ρ| > 0,7 çiftleri:

| A | B | Pearson | Spearman | Not |
|---|---|---|---|---|
| droe | sue | 0.49 | 0.81 | Spearman >> Pearson: doğrusal olmayan monoton ilişki |
| idio_vol_60d | max_ret_21d | 0.76 | 0.82 |  |

VIF > 5: `capex_at` (7.0), `cop_at` (6.2), `dist_52w_high` (6.6), `droe` (6.0), `idio_vol_60d` (11.1), `max_ret_21d` (7.2), `mom_12_1` (5.2), `ocf_ev` (6.5), `oil_beta_trend` (6.5), `sue` (8.7), `sue_announce` (5.4)

Ortogonalize (tema skoru + alt tema kuklaları sonrası artık) IC:

| Faktör | Ufuk | Artık IC | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.021 | 2.21 |
| asset_growth | 63 | 0.036 | 2.72 |
| asset_growth | 126 | 0.056 | 3.18 |
| capex_at | 21 | 0.013 | 1.29 |
| capex_at | 63 | 0.020 | 1.25 |
| capex_at | 126 | 0.035 | 1.44 |
| cash_runway_years | 21 | -0.125 | -1.38 |
| cash_runway_years | 63 | -0.133 | -2.70 |
| cash_runway_years | 126 | -0.198 | -3.74 |
| cop_at | 21 | -0.019 | -1.75 |
| cop_at | 63 | -0.032 | -1.95 |
| cop_at | 126 | -0.047 | -1.85 |
| dist_52w_high | 21 | 0.018 | 1.25 |
| dist_52w_high | 63 | 0.030 | 1.43 |
| dist_52w_high | 126 | 0.038 | 1.30 |
| ear_3d | 21 | 0.018 | 2.11 |
| ear_3d | 63 | 0.017 | 1.73 |
| ear_3d | 126 | 0.018 | 1.25 |
| ebit_ev | 21 | -0.014 | -1.15 |
| ebit_ev | 63 | -0.025 | -1.43 |
| ebit_ev | 126 | -0.028 | -1.30 |
| gross_profitability | 21 | -0.011 | -0.77 |
| gross_profitability | 63 | -0.033 | -1.56 |
| gross_profitability | 126 | -0.036 | -1.30 |
| idio_vol_60d | 21 | 0.023 | 1.45 |
| idio_vol_60d | 63 | 0.037 | 1.69 |
| idio_vol_60d | 126 | 0.055 | 1.77 |
| max_ret_21d | 21 | 0.020 | 1.39 |
| max_ret_21d | 63 | 0.031 | 1.82 |
| max_ret_21d | 126 | 0.039 | 1.65 |
| mom_12_1 | 21 | 0.016 | 1.17 |
| mom_12_1 | 63 | 0.023 | 1.29 |
| mom_12_1 | 126 | 0.017 | 0.64 |
| net_debt_ebitda | 21 | -0.024 | -1.66 |
| net_debt_ebitda | 63 | -0.041 | -2.18 |
| net_debt_ebitda | 126 | -0.057 | -2.26 |
| ocf_ev | 21 | 0.001 | 0.05 |
| ocf_ev | 63 | -0.000 | -0.00 |
| ocf_ev | 126 | -0.002 | -0.07 |
| oil_beta_trend | 21 | 0.002 | 0.08 |
| oil_beta_trend | 63 | -0.015 | -0.47 |
| oil_beta_trend | 126 | -0.009 | -0.25 |
| share_issuance | 21 | 0.010 | 1.23 |
| share_issuance | 63 | 0.025 | 2.09 |
| share_issuance | 126 | 0.040 | 2.41 |
| sue_announce | 21 | 0.011 | 1.23 |
| sue_announce | 63 | 0.009 | 0.67 |
| sue_announce | 126 | 0.004 | 0.24 |

### 7.3 Süreklilik (ρτ, aylık kesitsel sıra korelasyonu)

| Faktör | τ=1 | τ=3 | τ=6 | τ=12 |
|---|---|---|---|---|
| asset_growth | 0.93 | 0.81 | 0.63 | 0.28 |
| capex_at | 0.99 | 0.96 | 0.92 | 0.83 |
| cash_runway_years | 0.95 | 0.86 | 0.76 | 0.60 |
| cop_at | 0.97 | 0.92 | 0.84 | 0.69 |
| dist_52w_high | 0.83 | 0.66 | 0.50 | 0.33 |
| droe | 0.74 | 0.27 | 0.17 | -0.25 |
| ear_3d | 0.64 | 0.00 | 0.03 | 0.01 |
| ebit_ev | 0.95 | 0.87 | 0.73 | 0.46 |
| gross_profitability | 0.99 | 0.96 | 0.92 | 0.84 |
| idio_vol_60d | 0.96 | 0.88 | 0.85 | 0.82 |
| max_ret_21d | 0.66 | 0.65 | 0.63 | 0.60 |
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
| capex_at | 0.030 | 0.072 | 0.037 | 0.039 | 0.126 | 0.052 | 0.042 | yatırım faktörü (−) | Titman, Wei & Xie (2004); Fama & French (2015) CMA |
| cash_runway_years | — | — | -0.339 | -0.339 | — | -0.212 | -0.508 | finansal kısıt / seyreltme riski | Hadlock & Pierce (2010) — tema uyarlaması |
| cop_at | -0.072 | -0.091 | 0.011 | -0.046 | -0.071 | -0.005 | -0.094 | kalite (tahakkuksuz kârlılık) | Ball, Gerakos, Linnainmaa & Nikolaev (2016) |
| dist_52w_high | 0.103 | 0.041 | 0.019 | 0.066 | -0.078 | -0.043 | 0.150 | davranışsal (çıpalama) | George & Hwang (2004) |
| ear_3d | 0.012 | 0.032 | 0.021 | 0.019 | 0.053 | 0.007 | 0.038 | davranışsal (duyuru getirisi sürüklenmesi) | Chan, Jegadeesh & Lakonishok (1996) |
| ebit_ev | 0.026 | -0.075 | -0.006 | -0.017 | -0.042 | -0.034 | -0.005 | değer (risk + davranışsal) | Loughran & Wellman (2011) |
| gross_profitability | 0.027 | -0.057 | -0.034 | -0.022 | -0.038 | -0.015 | -0.032 | risk/kalite | Novy-Marx (2013) |
| idio_vol_60d | 0.112 | 0.092 | 0.029 | 0.087 | -0.028 | -0.038 | 0.194 | sınırlı arbitraj / piyango tercihi (−) | Ang, Hodrick, Xing & Zhang (2006) |
| max_ret_21d | 0.091 | 0.069 | 0.011 | 0.062 | -0.005 | -0.033 | 0.147 | piyango tercihi (−) | Bali, Cakici & Whitelaw (2011) |
| mom_12_1 | 0.107 | -0.055 | 0.054 | 0.040 | -0.034 | 0.013 | 0.054 | davranışsal (yetersiz tepki) + risk | Jegadeesh & Titman (1993); Carhart (1997) |
| net_debt_ebitda | -0.055 | -0.078 | -0.029 | -0.055 | -0.042 | -0.029 | -0.078 | kaldıraç / sıkıntı riski (−) | Campbell, Hilscher & Szilagyi (2008) |
| ocf_ev | -0.014 | -0.020 | 0.057 | 0.012 | -0.019 | 0.053 | -0.036 | değer (nakit akışı) | Lakonishok, Shleifer & Vishny (1994) |
| oil_beta_trend | 0.009 | -0.085 | 0.031 | -0.018 | 0.008 | 0.040 | -0.073 | emtia risk primi + trend | Moskowitz, Ooi & Pedersen (2012) — tema uyarlaması |
| share_issuance | 0.027 | 0.008 | 0.084 | 0.042 | 0.027 | 0.032 | 0.050 | piyasa zamanlaması (−) | Pontiff & Woodgate (2008); Daniel & Titman (2006) |
| sue_announce | 0.074 | -0.001 | 0.003 | 0.036 | -0.093 | -0.007 | 0.055 | davranışsal (PEAD, duyuru tarihli) | Bernard & Thomas (1989); Livnat & Mendenhall (2006) |

## Dosyalar

Tüm tablolar (alt temalar dahil): `alphas.csv`, `corr.csv`, `counts.csv`, `decision.csv`, `dependent.csv`, `descriptive.csv`, `fm.csv`, `ic.csv`, `orth.csv`, `persistence.csv`, `redundant.csv`, `sorts.csv`, `stability.csv`, `vif.csv`
