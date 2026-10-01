# Faktör açıklama raporu — themes_v1 (`themes_v2_20261001b`)

Bu rapor **tanımlayıcıdır**; faktör seçimi veya ağırlık öğrenmesi için kullanılmaz (THEMES_SPEC §7.9).

- Ön kayıt: `research/preregistration/themes_v1.yaml`, SHA256 `62db03649c07ac71a4f5f95a0085f2a5c685bf57e0f2dc09e66b33b9f69bf6e5`
- Veri: 2011-07-29 → 2026-09-30, 183 ay; uygun satır 114927
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
| ai | 107.0 | 16 | 320 | 0 |
| biotech | 160.4 | 38 | 279 | 0 |
| cyber_cloud | 91.4 | 14 | 152 | 1 |
| defense_space | 54.1 | 35 | 75 | 0 |
| energy | 138.7 | 86 | 177 | 0 |
| robotics | 16.7 | 3 | 35 | 96 |
| semiconductors | 59.8 | 36 | 88 | 0 |

## §7.9 Karar tablosu (126 seans)

Çalışıyor = IC > 0 ve NW t ≥ 2 **ve** FM katsayısı aynı işaretli **ve** alt dönemlerin ≥ 2/3'ünde IC > 0 **ve** bağımlı sıralama farkı > 0. Çalışmayanlar bir sonraki sürümde gerekçeyle çıkarılabilir; sonuçlara bakıp yeni faktör eklenmez.

| Kapsam | Faktör | IC | NW t | IC>0,t≥2 | FM | Alt dönem | Bağımlı | Çalışıyor |
|---|---|---|---|---|---|---|---|---|
| havuz | asset_growth | 0.010 | 0.75 | ✘ | ✘ | ✔ | ✘ | ✘ |
| havuz | capex_at | -0.017 | -1.77 | ✘ | ✘ | ✘ | ✘ | ✘ |
| havuz | cash_runway_years | 0.012 | 0.64 | ✘ | ✘ | ✔ | ✘ | ✘ |
| havuz | cop_at | 0.001 | 0.08 | ✘ | ✘ | ✘ | ✘ | ✘ |
| havuz | dist_52w_high | 0.083 | 4.23 | ✔ | ✔ | ✔ | ✔ | ✔ |
| havuz | droe | 0.011 | 1.16 | ✘ | ✔ | ✔ | ✔ | ✘ |
| havuz | ear_3d | 0.008 | 0.98 | ✘ | ✔ | ✔ | ✔ | ✘ |
| havuz | ebit_ev | -0.017 | -0.48 | ✘ | ✔ | ✘ | ✘ | ✘ |
| havuz | gross_profitability | 0.006 | 0.44 | ✘ | ✔ | ✔ | ✘ | ✘ |
| havuz | idio_vol_60d | 0.097 | 4.16 | ✔ | ✔ | ✔ | ✘ | ✘ |
| havuz | max_ret_21d | 0.072 | 3.45 | ✔ | ✔ | ✔ | ✘ | ✘ |
| havuz | mom_12_1 | 0.027 | 1.69 | ✘ | ✔ | ✔ | ✔ | ✘ |
| havuz | net_debt_ebitda | -0.058 | -1.64 | ✘ | ✔ | ✘ | ✘ | ✘ |
| havuz | ocf_ev | 0.007 | 0.17 | ✘ | ✔ | ✘ | ✔ | ✘ |
| havuz | oil_beta_trend | -0.016 | -0.43 | ✘ | ✔ | ✔ | ✔ | ✘ |
| havuz | profitable_growth | 0.024 | 1.06 | ✘ | ✔ | ✔ | ✔ | ✘ |
| havuz | share_issuance | 0.059 | 3.80 | ✔ | ✔ | ✔ | ✘ | ✘ |
| havuz | sue | 0.019 | 1.70 | ✘ | ✔ | ✔ | ✔ | ✘ |
| havuz | sue_announce | 0.042 | 3.72 | ✔ | ✔ | ✔ | ✔ | ✔ |
| robotics | asset_growth | 0.083 | 1.92 | ✘ | ✔ | ✔ | ✔ | ✘ |
| robotics | capex_at | -0.101 | -2.36 | ✘ | ✔ | ✘ | ✘ | ✘ |
| robotics | cop_at | 0.028 | 0.72 | ✘ | ✘ | ✘ | ✔ | ✘ |
| robotics | dist_52w_high | 0.039 | 0.70 | ✘ | ✘ | ✘ | ✔ | ✘ |
| robotics | droe | 0.073 | 2.26 | ✔ | ✔ | ✔ | ✔ | ✔ |
| robotics | ear_3d | 0.019 | 0.58 | ✘ | ✘ | ✔ | ✔ | ✘ |
| robotics | gross_profitability | 0.017 | 0.33 | ✘ | ✘ | ✘ | ✔ | ✘ |
| robotics | idio_vol_60d | 0.030 | 0.53 | ✘ | ✘ | ✘ | ✘ | ✘ |
| robotics | max_ret_21d | 0.030 | 0.71 | ✘ | ✘ | ✘ | ✘ | ✘ |
| robotics | mom_12_1 | 0.038 | 0.74 | ✘ | ✔ | ✘ | ✔ | ✘ |
| robotics | profitable_growth | -0.107 | -2.15 | ✘ | ✔ | ✘ | ✘ | ✘ |
| robotics | share_issuance | 0.153 | 3.49 | ✔ | ✔ | ✔ | ✔ | ✔ |
| robotics | sue | 0.069 | 1.76 | ✘ | ✔ | ✔ | ✔ | ✘ |
| robotics | sue_announce | -0.001 | -0.01 | ✘ | ✔ | ✘ | ✘ | ✘ |
| biotech | asset_growth | 0.020 | 1.08 | ✘ | ✔ | ✔ | ✔ | ✘ |
| biotech | capex_at | -0.028 | -1.65 | ✘ | ✘ | ✘ | ✔ | ✘ |
| biotech | cash_runway_years | 0.013 | 0.74 | ✘ | ✘ | ✔ | ✘ | ✘ |
| biotech | cop_at | 0.008 | 0.32 | ✘ | ✘ | ✘ | ✘ | ✘ |
| biotech | dist_52w_high | 0.098 | 4.83 | ✔ | ✔ | ✔ | ✔ | ✔ |
| biotech | droe | -0.006 | -0.33 | ✘ | ✘ | ✘ | ✘ | ✘ |
| biotech | ear_3d | -0.004 | -0.36 | ✘ | ✔ | ✘ | ✘ | ✘ |
| biotech | gross_profitability | -0.008 | -0.30 | ✘ | ✔ | ✘ | ✘ | ✘ |
| biotech | idio_vol_60d | 0.125 | 5.04 | ✔ | ✔ | ✔ | ✔ | ✔ |
| biotech | max_ret_21d | 0.102 | 4.49 | ✔ | ✔ | ✔ | ✘ | ✘ |
| biotech | mom_12_1 | 0.007 | 0.38 | ✘ | ✔ | ✔ | ✔ | ✘ |
| biotech | share_issuance | 0.078 | 2.95 | ✔ | ✘ | ✔ | ✘ | ✘ |
| biotech | sue | 0.008 | 0.50 | ✘ | ✔ | ✔ | ✘ | ✘ |
| biotech | sue_announce | 0.071 | 3.23 | ✔ | ✔ | ✔ | ✔ | ✔ |
| energy | asset_growth | 0.066 | 2.52 | ✔ | ✔ | ✔ | ✔ | ✔ |
| energy | capex_at | 0.043 | 1.43 | ✘ | ✔ | ✔ | ✔ | ✘ |
| energy | cash_runway_years | -0.311 | -6.30 | ✘ | ✔ | ✘ | ✘ | ✘ |
| energy | cop_at | -0.046 | -1.18 | ✘ | ✔ | ✘ | ✘ | ✘ |
| energy | dist_52w_high | 0.053 | 1.05 | ✘ | ✔ | ✔ | ✘ | ✘ |
| energy | ear_3d | 0.019 | 1.17 | ✘ | ✔ | ✔ | ✔ | ✘ |
| energy | ebit_ev | -0.018 | -0.51 | ✘ | ✔ | ✘ | ✘ | ✘ |
| energy | gross_profitability | -0.026 | -0.91 | ✘ | ✔ | ✘ | ✔ | ✘ |
| energy | idio_vol_60d | 0.074 | 1.31 | ✘ | ✘ | ✔ | ✘ | ✘ |
| energy | max_ret_21d | 0.053 | 1.11 | ✘ | ✘ | ✔ | ✘ | ✘ |
| energy | mom_12_1 | 0.033 | 0.75 | ✘ | ✔ | ✔ | ✔ | ✘ |
| energy | net_debt_ebitda | -0.053 | -1.54 | ✘ | ✘ | ✘ | ✘ | ✘ |
| energy | ocf_ev | 0.011 | 0.25 | ✘ | ✔ | ✘ | ✔ | ✘ |
| energy | oil_beta_trend | -0.016 | -0.43 | ✘ | ✔ | ✔ | ✔ | ✘ |
| energy | share_issuance | 0.042 | 2.01 | ✔ | ✔ | ✔ | ✔ | ✔ |
| energy | sue_announce | 0.027 | 1.14 | ✘ | ✔ | ✔ | ✔ | ✘ |

## Kapsam: havuz

### 7.7 Rank IC

| Faktör | Ufuk | IC | NW t | Örtüşmesiz t | IC>0 oranı | Ay |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 0.004 | 0.52 | 0.54 | 48.90% | 182 |
| asset_growth | 63 | 0.000 | 0.01 | 0.03 | 45.56% | 180 |
| asset_growth | 126 | 0.010 | 0.75 | 0.86 | 51.98% | 177 |
| capex_at | 21 | -0.007 | -1.36 | -1.43 | 48.90% | 182 |
| capex_at | 63 | -0.011 | -1.49 | -1.14 | 41.11% | 180 |
| capex_at | 126 | -0.017 | -1.77 | -0.82 | 42.94% | 177 |
| cash_runway_years | 21 | 0.009 | 1.04 | 1.09 | 57.47% | 174 |
| cash_runway_years | 63 | 0.009 | 0.66 | 0.18 | 52.33% | 172 |
| cash_runway_years | 126 | 0.012 | 0.64 | 0.52 | 50.89% | 169 |
| cop_at | 21 | 0.004 | 0.53 | 0.55 | 51.10% | 182 |
| cop_at | 63 | 0.002 | 0.13 | -0.41 | 48.33% | 180 |
| cop_at | 126 | 0.001 | 0.08 | 0.02 | 48.02% | 177 |
| dist_52w_high | 21 | 0.034 | 2.46 | 2.43 | 58.24% | 182 |
| dist_52w_high | 63 | 0.056 | 3.62 | 2.84 | 63.89% | 180 |
| dist_52w_high | 126 | 0.083 | 4.23 | 3.54 | 76.27% | 177 |
| droe | 21 | 0.007 | 1.23 | 1.33 | 53.30% | 182 |
| droe | 63 | 0.010 | 1.33 | 1.18 | 55.00% | 180 |
| droe | 126 | 0.011 | 1.16 | 1.41 | 56.50% | 177 |
| ear_3d | 21 | 0.003 | 0.58 | 0.54 | 47.25% | 182 |
| ear_3d | 63 | 0.001 | 0.13 | -0.48 | 53.33% | 180 |
| ear_3d | 126 | 0.008 | 0.98 | -0.19 | 56.50% | 177 |
| ebit_ev | 21 | 0.006 | 0.30 | 0.33 | 52.20% | 182 |
| ebit_ev | 63 | -0.012 | -0.44 | -0.69 | 49.44% | 180 |
| ebit_ev | 126 | -0.017 | -0.48 | -0.47 | 48.59% | 177 |
| gross_profitability | 21 | 0.007 | 1.13 | 1.16 | 58.24% | 182 |
| gross_profitability | 63 | 0.005 | 0.59 | 0.39 | 54.44% | 180 |
| gross_profitability | 126 | 0.006 | 0.44 | 0.66 | 51.41% | 177 |
| idio_vol_60d | 21 | 0.044 | 2.98 | 2.99 | 56.04% | 182 |
| idio_vol_60d | 63 | 0.067 | 3.82 | 2.97 | 66.11% | 180 |
| idio_vol_60d | 126 | 0.097 | 4.16 | 3.74 | 74.58% | 177 |
| max_ret_21d | 21 | 0.034 | 2.59 | 2.60 | 57.14% | 182 |
| max_ret_21d | 63 | 0.054 | 3.45 | 2.75 | 61.67% | 180 |
| max_ret_21d | 126 | 0.072 | 3.45 | 3.21 | 72.88% | 177 |
| mom_12_1 | 21 | 0.012 | 1.22 | 1.23 | 54.40% | 182 |
| mom_12_1 | 63 | 0.019 | 1.67 | 1.43 | 55.56% | 180 |
| mom_12_1 | 126 | 0.027 | 1.69 | 1.28 | 58.76% | 177 |
| net_debt_ebitda | 21 | -0.016 | -0.79 | -0.85 | 50.00% | 182 |
| net_debt_ebitda | 63 | -0.039 | -1.47 | -1.46 | 46.67% | 180 |
| net_debt_ebitda | 126 | -0.058 | -1.64 | -1.41 | 46.33% | 177 |
| ocf_ev | 21 | 0.013 | 0.63 | 0.67 | 51.10% | 182 |
| ocf_ev | 63 | 0.007 | 0.26 | -0.22 | 53.89% | 180 |
| ocf_ev | 126 | 0.007 | 0.17 | -0.11 | 54.80% | 177 |
| oil_beta_trend | 21 | 0.006 | 0.25 | 0.25 | 54.95% | 182 |
| oil_beta_trend | 63 | -0.023 | -0.69 | -0.16 | 46.67% | 180 |
| oil_beta_trend | 126 | -0.016 | -0.43 | -0.77 | 48.59% | 177 |
| profitable_growth | 21 | 0.013 | 1.47 | 1.49 | 54.40% | 182 |
| profitable_growth | 63 | 0.024 | 1.45 | 1.35 | 60.00% | 180 |
| profitable_growth | 126 | 0.024 | 1.06 | 1.01 | 55.93% | 177 |
| share_issuance | 21 | 0.027 | 3.08 | 3.16 | 53.30% | 182 |
| share_issuance | 63 | 0.041 | 3.52 | 2.27 | 53.89% | 180 |
| share_issuance | 126 | 0.059 | 3.80 | 2.74 | 66.67% | 177 |
| sue | 21 | 0.010 | 1.84 | 1.89 | 54.40% | 182 |
| sue | 63 | 0.011 | 1.38 | 1.05 | 55.56% | 180 |
| sue | 126 | 0.019 | 1.70 | 1.99 | 62.15% | 177 |
| sue_announce | 21 | 0.021 | 3.22 | 3.16 | 60.99% | 182 |
| sue_announce | 63 | 0.032 | 3.51 | 3.05 | 66.11% | 180 |
| sue_announce | 126 | 0.042 | 3.72 | 2.73 | 70.06% | 177 |

### 7.4 Tek değişkenli sıralama (EW; üst − alt = `mimic_`)

| Faktör | Ufuk | Port. | mimic EW | t | mimic VW | Üst − ort. | t | Monoton |
|---|---|---|---|---|---|---|---|---|
| asset_growth | 21 | 5 | 0.33% | 1.36 | 0.17% | 0.27% | 1.78 | ✘ |
| asset_growth | 63 | 5 | 0.43% | 0.65 | 0.01% | 0.37% | 1.03 | ✘ |
| asset_growth | 126 | 5 | 1.06% | 0.83 | 0.16% | 0.69% | 1.09 | ✘ |
| capex_at | 21 | 5 | 0.11% | 0.61 | -0.28% | -0.03% | -0.22 | ✘ |
| capex_at | 63 | 5 | 0.49% | 1.07 | 0.06% | 0.13% | 0.46 | ✘ |
| capex_at | 126 | 5 | 0.78% | 0.81 | 0.13% | 0.10% | 0.20 | ✘ |
| cash_runway_years | 21 | 5 | -1.01% | -1.95 | 0.05% | -0.09% | -0.36 | ✘ |
| cash_runway_years | 63 | 5 | -2.29% | -1.66 | 0.45% | -0.26% | -0.32 | ✘ |
| cash_runway_years | 126 | 5 | -2.61% | -1.11 | -1.32% | 0.16% | 0.11 | ✘ |
| cop_at | 21 | 5 | 0.02% | 0.13 | 1.06% | 0.05% | 0.60 | ✘ |
| cop_at | 63 | 5 | 0.05% | 0.09 | 3.28% | 0.12% | 0.53 | ✘ |
| cop_at | 126 | 5 | -0.02% | -0.02 | 5.34% | 0.13% | 0.32 | ✘ |
| dist_52w_high | 21 | 5 | 0.22% | 0.49 | 0.38% | -0.03% | -0.16 | ✘ |
| dist_52w_high | 63 | 5 | 0.70% | 0.71 | 1.16% | -0.08% | -0.22 | ✘ |
| dist_52w_high | 126 | 5 | 1.60% | 0.84 | 1.46% | 0.40% | 0.59 | ✘ |
| droe | 21 | 5 | 0.37% | 2.07 | 0.43% | 0.34% | 2.90 | ✘ |
| droe | 63 | 5 | 1.10% | 2.32 | 1.14% | 0.87% | 2.86 | ✘ |
| droe | 126 | 5 | 2.09% | 2.21 | 0.80% | 1.68% | 2.68 | ✘ |
| ear_3d | 21 | 5 | -0.12% | -0.69 | 0.07% | -0.04% | -0.35 | ✘ |
| ear_3d | 63 | 5 | -0.18% | -0.54 | -0.02% | -0.02% | -0.07 | ✘ |
| ear_3d | 126 | 5 | 1.06% | 1.84 | 2.19% | 0.63% | 1.35 | ✘ |
| ebit_ev | 21 | 5 | -0.21% | -0.39 | -0.11% | -0.06% | -0.19 | ✘ |
| ebit_ev | 63 | 5 | -1.52% | -1.07 | -1.12% | -0.97% | -1.31 | ✘ |
| ebit_ev | 126 | 5 | -3.56% | -1.34 | -3.07% | -2.11% | -1.50 | ✘ |
| gross_profitability | 21 | 5 | 0.09% | 0.44 | 0.26% | 0.07% | 0.62 | ✘ |
| gross_profitability | 63 | 5 | 0.01% | 0.02 | 0.74% | 0.12% | 0.38 | ✘ |
| gross_profitability | 126 | 5 | -0.07% | -0.06 | 2.50% | 0.15% | 0.22 | ✘ |
| idio_vol_60d | 21 | 5 | -0.12% | -0.23 | -0.04% | 0.06% | 0.25 | ✘ |
| idio_vol_60d | 63 | 5 | -0.71% | -0.59 | -0.83% | 0.03% | 0.05 | ✘ |
| idio_vol_60d | 126 | 5 | -0.52% | -0.23 | -2.05% | -0.01% | -0.01 | ✘ |
| max_ret_21d | 21 | 5 | -0.19% | -0.43 | -0.18% | 0.02% | 0.07 | ✘ |
| max_ret_21d | 63 | 5 | -0.82% | -0.77 | -0.48% | -0.15% | -0.28 | ✘ |
| max_ret_21d | 126 | 5 | -1.36% | -0.69 | -2.38% | -0.61% | -0.59 | ✘ |
| mom_12_1 | 21 | 5 | 0.42% | 1.30 | 0.13% | 0.15% | 0.79 | ✘ |
| mom_12_1 | 63 | 5 | 1.54% | 2.20 | 0.75% | 0.87% | 2.16 | ✔ |
| mom_12_1 | 126 | 5 | 2.74% | 2.00 | 2.57% | 1.61% | 2.25 | ✔ |
| net_debt_ebitda | 21 | 5 | 0.14% | 0.30 | 0.25% | 0.08% | 0.24 | ✘ |
| net_debt_ebitda | 63 | 5 | -0.19% | -0.17 | -0.08% | -0.19% | -0.25 | ✘ |
| net_debt_ebitda | 126 | 5 | -0.68% | -0.35 | -0.84% | -0.55% | -0.39 | ✘ |
| ocf_ev | 21 | 5 | 0.46% | 0.72 | 0.61% | 0.05% | 0.11 | ✘ |
| ocf_ev | 63 | 5 | 0.89% | 0.60 | 1.08% | -0.35% | -0.36 | ✘ |
| ocf_ev | 126 | 5 | 1.24% | 0.37 | 1.52% | -1.01% | -0.48 | ✘ |
| oil_beta_trend | 21 | 5 | 0.42% | 0.57 | 0.76% | 0.28% | 0.74 | ✘ |
| oil_beta_trend | 63 | 5 | -0.50% | -0.28 | 0.46% | 0.10% | 0.10 | ✘ |
| oil_beta_trend | 126 | 5 | 0.08% | 0.03 | 1.50% | 0.55% | 0.31 | ✘ |
| profitable_growth | 21 | 5 | 0.15% | 0.60 | 0.85% | 0.17% | 1.18 | ✘ |
| profitable_growth | 63 | 5 | 0.76% | 0.93 | 2.15% | 0.48% | 1.13 | ✘ |
| profitable_growth | 126 | 5 | 1.00% | 0.60 | 3.64% | 0.80% | 0.92 | ✘ |
| share_issuance | 21 | 5 | 0.08% | 0.23 | 0.19% | 0.11% | 0.75 | ✘ |
| share_issuance | 63 | 5 | -0.07% | -0.08 | 0.82% | 0.20% | 0.63 | ✘ |
| share_issuance | 126 | 5 | 0.07% | 0.05 | 3.31% | 0.40% | 0.65 | ✘ |
| sue | 21 | 5 | 0.20% | 1.15 | -0.27% | 0.13% | 1.31 | ✘ |
| sue | 63 | 5 | 0.54% | 1.18 | -0.59% | 0.31% | 1.27 | ✘ |
| sue | 126 | 5 | 1.55% | 1.73 | -0.48% | 1.05% | 2.15 | ✘ |
| sue_announce | 21 | 5 | 0.33% | 1.65 | 0.23% | 0.09% | 0.88 | ✘ |
| sue_announce | 63 | 5 | 1.23% | 2.68 | 1.11% | 0.20% | 0.82 | ✘ |
| sue_announce | 126 | 5 | 2.17% | 2.86 | 1.50% | 0.44% | 1.00 | ✘ |

### 7.4 Alfalar (21 seans, aylık; NW t)

Üst portföy RF üzeri; `mimic_ew` ham fark.

| Faktör | Seri | capm t | ff3 t | carhart4 t | ff5_mom t |
|---|---|---|---|---|---|
| asset_growth | mimic_ew | 1.50 | 1.55 | 1.84 | 1.63 |
| asset_growth | top_ew | 0.48 | 1.03 | 0.94 | 1.00 |
| capex_at | mimic_ew | 0.71 | 1.46 | 1.53 | 1.95 |
| capex_at | top_ew | -0.09 | 0.52 | 0.51 | 0.78 |
| cash_runway_years | mimic_ew | -1.66 | -1.98 | -1.84 | -1.66 |
| cash_runway_years | top_ew | -0.23 | 0.24 | 0.01 | 0.35 |
| cop_at | mimic_ew | 0.65 | 0.31 | 0.98 | 0.81 |
| cop_at | top_ew | 0.37 | 0.58 | 0.61 | 0.51 |
| dist_52w_high | mimic_ew | 1.92 | 1.59 | 1.12 | 0.91 |
| dist_52w_high | top_ew | 1.15 | 1.43 | 0.86 | 0.75 |
| droe | mimic_ew | 2.13 | 2.34 | 2.00 | 1.97 |
| droe | top_ew | 1.39 | 1.96 | 1.68 | 1.73 |
| ear_3d | mimic_ew | -0.90 | -0.79 | -1.06 | -1.09 |
| ear_3d | top_ew | -0.38 | 0.14 | -0.16 | 0.03 |
| ebit_ev | mimic_ew | -0.48 | -0.63 | -0.33 | -0.81 |
| ebit_ev | top_ew | -0.90 | -1.15 | -0.95 | -1.41 |
| gross_profitability | mimic_ew | 1.40 | 1.85 | 2.12 | 2.22 |
| gross_profitability | top_ew | 0.98 | 1.32 | 1.32 | 1.35 |
| idio_vol_60d | mimic_ew | 1.28 | 0.77 | 0.97 | 0.35 |
| idio_vol_60d | top_ew | 1.96 | 1.91 | 1.70 | 1.26 |
| max_ret_21d | mimic_ew | 0.92 | 0.24 | 0.57 | -0.11 |
| max_ret_21d | top_ew | 1.16 | 1.09 | 0.98 | 0.60 |
| mom_12_1 | mimic_ew | 1.32 | 1.29 | 0.13 | 0.35 |
| mom_12_1 | top_ew | 0.10 | 0.59 | -0.18 | 0.16 |
| net_debt_ebitda | mimic_ew | -0.86 | -0.88 | -0.92 | -1.15 |
| net_debt_ebitda | top_ew | -0.80 | -0.96 | -0.99 | -1.21 |
| ocf_ev | mimic_ew | -0.13 | -0.24 | 0.15 | -0.14 |
| ocf_ev | top_ew | -0.64 | -0.84 | -0.65 | -0.90 |
| oil_beta_trend | mimic_ew | 1.99 | 2.05 | 1.78 | 1.88 |
| oil_beta_trend | top_ew | 0.43 | 0.52 | 0.50 | 0.33 |
| profitable_growth | mimic_ew | 0.66 | 0.69 | 1.12 | 1.29 |
| profitable_growth | top_ew | 0.92 | 1.23 | 1.04 | 1.21 |
| share_issuance | mimic_ew | 1.43 | 0.83 | 1.19 | 0.63 |
| share_issuance | top_ew | 1.04 | 1.20 | 1.20 | 0.98 |
| sue | mimic_ew | 0.98 | 0.99 | 0.79 | 0.79 |
| sue | top_ew | 1.07 | 1.53 | 1.24 | 1.20 |
| sue_announce | mimic_ew | 2.06 | 2.01 | 1.59 | 1.68 |
| sue_announce | top_ew | 0.81 | 1.10 | 0.85 | 0.82 |

### 7.5 Bağımlı iki değişkenli sıralama (tema skoru terciliyle kontrol)

| Faktör | Ufuk | Ort. fark | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.10% | 0.54 |
| asset_growth | 63 | -0.02% | -0.04 |
| asset_growth | 126 | -0.15% | -0.17 |
| capex_at | 21 | -0.02% | -0.18 |
| capex_at | 63 | 0.14% | 0.40 |
| capex_at | 126 | -0.05% | -0.07 |
| cash_runway_years | 21 | -0.91% | -2.46 |
| cash_runway_years | 63 | -2.81% | -2.70 |
| cash_runway_years | 126 | -4.00% | -2.15 |
| cop_at | 21 | -0.02% | -0.08 |
| cop_at | 63 | -0.34% | -0.66 |
| cop_at | 126 | -0.80% | -0.71 |
| dist_52w_high | 21 | 0.27% | 1.02 |
| dist_52w_high | 63 | 0.69% | 1.23 |
| dist_52w_high | 126 | 1.40% | 1.32 |
| droe | 21 | 0.17% | 1.12 |
| droe | 63 | 0.57% | 1.39 |
| droe | 126 | 1.19% | 1.36 |
| ear_3d | 21 | -0.09% | -0.66 |
| ear_3d | 63 | -0.22% | -0.75 |
| ear_3d | 126 | 0.32% | 0.68 |
| ebit_ev | 21 | -0.25% | -0.56 |
| ebit_ev | 63 | -1.10% | -1.01 |
| ebit_ev | 126 | -2.24% | -1.05 |
| gross_profitability | 21 | 0.00% | 0.00 |
| gross_profitability | 63 | -0.15% | -0.43 |
| gross_profitability | 126 | -0.27% | -0.35 |
| idio_vol_60d | 21 | -0.07% | -0.22 |
| idio_vol_60d | 63 | -0.56% | -0.73 |
| idio_vol_60d | 126 | -0.76% | -0.53 |
| max_ret_21d | 21 | -0.12% | -0.41 |
| max_ret_21d | 63 | -0.67% | -1.01 |
| max_ret_21d | 126 | -1.27% | -0.97 |
| mom_12_1 | 21 | 0.40% | 1.77 |
| mom_12_1 | 63 | 1.19% | 2.48 |
| mom_12_1 | 126 | 2.03% | 2.36 |
| net_debt_ebitda | 21 | 0.02% | 0.05 |
| net_debt_ebitda | 63 | -0.49% | -0.44 |
| net_debt_ebitda | 126 | -0.98% | -0.44 |
| ocf_ev | 21 | 0.60% | 1.04 |
| ocf_ev | 63 | 1.13% | 0.82 |
| ocf_ev | 126 | 1.92% | 0.65 |
| oil_beta_trend | 21 | 0.39% | 0.75 |
| oil_beta_trend | 63 | 0.16% | 0.12 |
| oil_beta_trend | 126 | 1.29% | 0.57 |
| profitable_growth | 21 | -0.01% | -0.06 |
| profitable_growth | 63 | 0.07% | 0.11 |
| profitable_growth | 126 | 0.15% | 0.12 |
| share_issuance | 21 | -0.04% | -0.19 |
| share_issuance | 63 | -0.36% | -0.68 |
| share_issuance | 126 | -0.72% | -0.70 |
| sue | 21 | 0.15% | 1.05 |
| sue | 63 | 0.34% | 0.91 |
| sue | 126 | 1.25% | 1.43 |
| sue_announce | 21 | 0.14% | 1.06 |
| sue_announce | 63 | 0.51% | 1.77 |
| sue_announce | 126 | 1.26% | 2.32 |

### 7.6 Fama-MacBeth (tek faktör + β, ln(MktCap); NW t)

| Faktör | Ufuk | OLS rank-normal t | OLS ham t | WLS √MktCap t | 1 std etkisi | Ort. R² |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 0.78 | 0.11 | -0.23 | 0.06% | 6.08% |
| asset_growth | 63 | -0.02 | 0.02 | -0.59 | -0.00% | 4.81% |
| asset_growth | 126 | -0.01 | 0.36 | -0.24 | -0.00% | 4.17% |
| capex_at | 21 | 0.31 | 0.60 | -0.94 | 0.02% | 5.71% |
| capex_at | 63 | 0.95 | 1.04 | -0.69 | 0.15% | 4.44% |
| capex_at | 126 | 0.62 | 1.00 | -0.81 | 0.21% | 3.77% |
| cash_runway_years | 21 | -1.48 | -0.44 | 0.36 | -0.23% | 4.65% |
| cash_runway_years | 63 | -1.75 | -0.73 | 0.13 | -0.71% | 4.54% |
| cash_runway_years | 126 | -1.28 | -0.28 | 0.13 | -0.93% | 4.45% |
| cop_at | 21 | 0.30 | 0.17 | 2.20 | 0.02% | 7.43% |
| cop_at | 63 | -0.06 | -0.34 | 2.08 | -0.01% | 6.25% |
| cop_at | 126 | -0.25 | -0.61 | 1.70 | -0.10% | 5.52% |
| dist_52w_high | 21 | 1.40 | 1.83 | 1.41 | 0.16% | 6.47% |
| dist_52w_high | 63 | 2.40 | 2.82 | 2.21 | 0.57% | 4.90% |
| dist_52w_high | 126 | 2.78 | 3.05 | 2.91 | 1.15% | 4.00% |
| droe | 21 | 1.70 | 0.85 | 0.25 | 0.09% | 5.45% |
| droe | 63 | 2.24 | 1.49 | 0.98 | 0.31% | 4.93% |
| droe | 126 | 2.32 | 0.46 | 0.99 | 0.65% | 4.32% |
| ear_3d | 21 | -0.09 | -0.16 | 1.38 | -0.01% | 5.86% |
| ear_3d | 63 | -0.05 | -0.31 | 1.56 | -0.01% | 4.45% |
| ear_3d | 126 | 1.26 | 1.37 | 2.38 | 0.25% | 3.66% |
| ebit_ev | 21 | 0.21 | 0.58 | 0.65 | 0.03% | 21.03% |
| ebit_ev | 63 | -0.14 | 0.16 | 0.15 | -0.05% | 20.03% |
| ebit_ev | 126 | -0.25 | -0.46 | 0.14 | -0.17% | 20.04% |
| gross_profitability | 21 | 0.98 | 1.19 | 0.42 | 0.06% | 5.84% |
| gross_profitability | 63 | 0.71 | 0.89 | 0.55 | 0.12% | 5.01% |
| gross_profitability | 126 | 0.29 | 0.45 | 0.49 | 0.12% | 4.43% |
| idio_vol_60d | 21 | 0.34 | 0.09 | 0.66 | 0.04% | 6.16% |
| idio_vol_60d | 63 | 0.09 | 0.06 | 0.50 | 0.03% | 4.81% |
| idio_vol_60d | 126 | 0.77 | 0.96 | 1.03 | 0.43% | 4.03% |
| max_ret_21d | 21 | 0.51 | 0.38 | 1.11 | 0.05% | 5.86% |
| max_ret_21d | 63 | 0.09 | -0.06 | 0.57 | 0.02% | 4.53% |
| max_ret_21d | 126 | 0.14 | 0.64 | 0.24 | 0.05% | 3.80% |
| mom_12_1 | 21 | 2.25 | 1.55 | 2.72 | 0.20% | 6.31% |
| mom_12_1 | 63 | 3.31 | 2.71 | 3.77 | 0.63% | 4.74% |
| mom_12_1 | 126 | 3.17 | 2.74 | 3.92 | 1.11% | 3.98% |
| net_debt_ebitda | 21 | 0.03 | 0.86 | 0.30 | 0.00% | 20.37% |
| net_debt_ebitda | 63 | -0.18 | 0.71 | -0.34 | -0.05% | 19.00% |
| net_debt_ebitda | 126 | -0.23 | 0.21 | -0.61 | -0.11% | 19.00% |
| ocf_ev | 21 | 1.25 | 1.39 | 1.69 | 0.19% | 20.74% |
| ocf_ev | 63 | 0.82 | 0.73 | 1.18 | 0.31% | 19.31% |
| ocf_ev | 126 | 0.72 | 0.37 | 1.02 | 0.55% | 19.31% |
| oil_beta_trend | 21 | -0.24 | 0.05 | 0.25 | -0.06% | 15.75% |
| oil_beta_trend | 63 | -0.71 | -0.32 | -0.53 | -0.39% | 15.83% |
| oil_beta_trend | 126 | -0.32 | 0.06 | -0.28 | -0.32% | 15.96% |
| profitable_growth | 21 | 0.09 | 0.09 | 0.81 | 0.01% | 6.47% |
| profitable_growth | 63 | 0.62 | 0.65 | 1.02 | 0.16% | 5.92% |
| profitable_growth | 126 | 0.21 | 0.25 | 0.55 | 0.11% | 5.76% |
| share_issuance | 21 | 0.75 | 0.39 | 1.23 | 0.06% | 6.22% |
| share_issuance | 63 | 0.24 | -0.06 | 1.07 | 0.05% | 4.89% |
| share_issuance | 126 | 0.16 | 0.22 | 1.98 | 0.07% | 4.23% |
| sue | 21 | 2.02 | 1.54 | -0.06 | 0.11% | 5.81% |
| sue | 63 | 2.30 | 1.98 | 0.42 | 0.31% | 5.20% |
| sue | 126 | 2.77 | 2.58 | 0.74 | 0.79% | 4.59% |
| sue_announce | 21 | 2.60 | 2.27 | 3.16 | 0.13% | 7.27% |
| sue_announce | 63 | 3.67 | 3.12 | 3.94 | 0.47% | 5.75% |
| sue_announce | 126 | 4.02 | 3.45 | 3.88 | 0.88% | 5.06% |

Tüm faktörlü model (kapsama ≥ %50, eksiksiz satırlar):

| Ufuk | Faktör | Katsayı | NW t | Ort. düz. R² |
|---|---|---|---|---|
| 21 | asset_growth | -0.23% | -2.74 | 12.94% |
| 21 | capex_at | 0.03% | 0.38 | 12.94% |
| 21 | cash_runway_years | 0.51% | 1.87 | 12.94% |
| 21 | cop_at | 0.11% | 0.77 | 12.94% |
| 21 | dist_52w_high | -0.21% | -1.82 | 12.94% |
| 21 | droe | 0.00% | 0.03 | 12.94% |
| 21 | ear_3d | -0.00% | -0.01 | 12.94% |
| 21 | ebit_ev | 0.01% | 0.09 | 12.94% |
| 21 | gross_profitability | -0.04% | -0.39 | 12.94% |
| 21 | idio_vol_60d | 0.23% | 2.30 | 12.94% |
| 21 | max_ret_21d | 0.06% | 0.66 | 12.94% |
| 21 | mom_12_1 | 0.21% | 1.92 | 12.94% |
| 21 | net_debt_ebitda | -0.08% | -0.97 | 12.94% |
| 21 | ocf_ev | -0.09% | -0.55 | 12.94% |
| 21 | profitable_growth | -0.12% | -1.27 | 12.94% |
| 21 | share_issuance | 0.01% | 0.11 | 12.94% |
| 21 | sue | 0.04% | 0.42 | 12.94% |
| 21 | sue_announce | -0.06% | -0.84 | 12.94% |
| 63 | asset_growth | -0.46% | -2.30 | 12.06% |
| 63 | capex_at | 0.10% | 0.46 | 12.06% |
| 63 | cash_runway_years | 1.15% | 1.95 | 12.06% |
| 63 | cop_at | 0.13% | 0.32 | 12.06% |
| 63 | dist_52w_high | -0.33% | -1.47 | 12.06% |
| 63 | droe | 0.14% | 0.48 | 12.06% |
| 63 | ear_3d | -0.14% | -0.76 | 12.06% |
| 63 | ebit_ev | -0.06% | -0.25 | 12.06% |
| 63 | gross_profitability | -0.12% | -0.45 | 12.06% |
| 63 | idio_vol_60d | 0.21% | 0.94 | 12.06% |
| 63 | max_ret_21d | 0.20% | 1.27 | 12.06% |
| 63 | mom_12_1 | 0.56% | 1.99 | 12.06% |
| 63 | net_debt_ebitda | -0.30% | -1.40 | 12.06% |
| 63 | ocf_ev | -0.10% | -0.27 | 12.06% |
| 63 | profitable_growth | -0.27% | -1.14 | 12.06% |
| 63 | share_issuance | 0.07% | 0.33 | 12.06% |
| 63 | sue | -0.05% | -0.19 | 12.06% |
| 63 | sue_announce | -0.12% | -0.63 | 12.06% |
| 126 | asset_growth | -0.63% | -2.03 | 11.72% |
| 126 | capex_at | 0.09% | 0.18 | 11.72% |
| 126 | cash_runway_years | 1.73% | 1.81 | 11.72% |
| 126 | cop_at | 0.20% | 0.26 | 11.72% |
| 126 | dist_52w_high | -0.46% | -1.06 | 11.72% |
| 126 | droe | 0.15% | 0.31 | 11.72% |
| 126 | ear_3d | 0.06% | 0.22 | 11.72% |
| 126 | ebit_ev | -0.19% | -0.46 | 11.72% |
| 126 | gross_profitability | -0.50% | -0.98 | 11.72% |
| 126 | idio_vol_60d | 0.22% | 0.59 | 11.72% |
| 126 | max_ret_21d | -0.12% | -0.51 | 11.72% |
| 126 | mom_12_1 | 1.09% | 2.21 | 11.72% |
| 126 | net_debt_ebitda | -0.27% | -0.64 | 11.72% |
| 126 | ocf_ev | 0.04% | 0.06 | 11.72% |
| 126 | profitable_growth | -0.83% | -1.77 | 11.72% |
| 126 | share_issuance | -0.00% | -0.00 | 11.72% |
| 126 | sue | 0.26% | 0.59 | 11.72% |
| 126 | sue_announce | -0.09% | -0.28 | 11.72% |

### 7.1 Tanımlayıcı istatistikler (winsorize %0,5/%99,5; aylık değerlerin zaman ortalaması)

| Faktör | Ort. | Std | Çarp. | Bas. | P5 | Medyan | P95 | n | Ort. kayması |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.220 | 0.535 | 3.94 | 20.50 | -0.165 | 0.076 | 1.063 | 546 | 0.14 |
| capex_at | 0.040 | 0.047 | 2.36 | 6.99 | 0.002 | 0.023 | 0.131 | 522 | 0.22 |
| cash_runway_years | 7.794 | 3.660 | -1.19 | -0.34 | 0.379 | 10.000 | 10.000 | 548 | 0.07 |
| cop_at | 0.041 | 0.178 | -2.10 | 6.53 | -0.329 | 0.078 | 0.231 | 548 | 0.15 |
| dist_52w_high | -0.209 | 0.170 | -1.07 | 0.72 | -0.551 | -0.164 | -0.019 | 555 | 0.37 |
| droe | -0.001 | 0.169 | -0.12 | 16.93 | -0.177 | -0.000 | 0.169 | 501 | 0.08 |
| ear_3d | 0.005 | 0.090 | 0.23 | 2.26 | -0.137 | 0.003 | 0.156 | 512 | 0.06 |
| ebit_ev | 0.003 | 0.137 | -2.35 | 14.35 | -0.207 | 0.031 | 0.134 | 512 | 0.25 |
| gross_profitability | 0.293 | 0.184 | 1.04 | 2.01 | 0.050 | 0.268 | 0.630 | 392 | 0.12 |
| idio_vol_60d | 0.389 | 0.235 | 2.10 | 7.09 | 0.154 | 0.328 | 0.815 | 555 | 0.40 |
| max_ret_21d | 0.059 | 0.051 | 3.31 | 16.30 | 0.018 | 0.045 | 0.145 | 555 | 0.35 |
| mom_12_1 | 0.255 | 0.681 | 2.76 | 13.66 | -0.407 | 0.125 | 1.315 | 555 | 0.36 |
| net_debt_ebitda | 1.345 | 6.286 | 1.08 | 12.33 | -6.629 | 1.215 | 8.144 | 359 | 0.08 |
| ocf_ev | 0.043 | 0.116 | -1.10 | 9.91 | -0.131 | 0.051 | 0.190 | 547 | 0.23 |
| oil_beta_trend | -0.025 | 0.379 | -0.30 | 7.68 | -0.434 | -0.025 | 0.402 | 87 | 1.21 |
| profitable_growth | 1.058 | 0.402 | -0.03 | -0.54 | 0.377 | 1.054 | 1.724 | 412 | 0.04 |
| share_issuance | 0.048 | 0.186 | 3.18 | 25.26 | -0.065 | 0.010 | 0.282 | 513 | 0.11 |
| sue | 0.063 | 1.275 | -0.10 | 0.57 | -2.153 | 0.066 | 2.165 | 533 | 0.13 |
| sue_announce | 0.577 | 1.461 | 0.54 | 0.83 | -1.619 | 0.434 | 3.091 | 288 | 0.16 |

### 7.2 Korelasyon ve çoklu doğrusallık

Tam matris (alt üçgen Pearson, üst üçgen Spearman): `corr.csv`. |ρ| > 0,7 çiftleri:

| A | B | Pearson | Spearman | Not |
|---|---|---|---|---|
| droe | sue | 0.36 | 0.71 | Spearman >> Pearson: doğrusal olmayan monoton ilişki |
| ebit_ev | ocf_ev | 0.72 | 0.71 |  |
| idio_vol_60d | max_ret_21d | 0.67 | 0.74 |  |

VIF > 5: yok

Ortogonalize (tema skoru + alt tema kuklaları sonrası artık) IC:

| Faktör | Ufuk | Artık IC | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.003 | 0.49 |
| asset_growth | 63 | -0.003 | -0.27 |
| asset_growth | 126 | 0.002 | 0.18 |
| capex_at | 21 | -0.002 | -0.38 |
| capex_at | 63 | -0.003 | -0.37 |
| capex_at | 126 | -0.005 | -0.45 |
| cash_runway_years | 21 | -0.015 | -1.67 |
| cash_runway_years | 63 | -0.026 | -2.17 |
| cash_runway_years | 126 | -0.029 | -1.63 |
| cop_at | 21 | -0.006 | -1.10 |
| cop_at | 63 | -0.011 | -1.33 |
| cop_at | 126 | -0.014 | -1.12 |
| dist_52w_high | 21 | 0.014 | 1.59 |
| dist_52w_high | 63 | 0.027 | 2.68 |
| dist_52w_high | 126 | 0.039 | 2.94 |
| droe | 21 | 0.002 | 0.38 |
| droe | 63 | 0.001 | 0.16 |
| droe | 126 | -0.008 | -0.69 |
| ear_3d | 21 | 0.001 | 0.29 |
| ear_3d | 63 | -0.001 | -0.12 |
| ear_3d | 126 | 0.004 | 0.59 |
| ebit_ev | 21 | -0.010 | -0.82 |
| ebit_ev | 63 | -0.019 | -1.06 |
| ebit_ev | 126 | -0.024 | -1.12 |
| gross_profitability | 21 | -0.000 | -0.07 |
| gross_profitability | 63 | -0.007 | -0.80 |
| gross_profitability | 126 | -0.007 | -0.58 |
| idio_vol_60d | 21 | 0.021 | 2.26 |
| idio_vol_60d | 63 | 0.034 | 2.97 |
| idio_vol_60d | 126 | 0.052 | 3.64 |
| max_ret_21d | 21 | 0.014 | 1.75 |
| max_ret_21d | 63 | 0.023 | 2.40 |
| max_ret_21d | 126 | 0.029 | 2.43 |
| mom_12_1 | 21 | 0.005 | 0.57 |
| mom_12_1 | 63 | 0.004 | 0.45 |
| mom_12_1 | 126 | 0.000 | 0.02 |
| net_debt_ebitda | 21 | -0.027 | -1.92 |
| net_debt_ebitda | 63 | -0.043 | -2.37 |
| net_debt_ebitda | 126 | -0.057 | -2.40 |
| ocf_ev | 21 | -0.000 | -0.00 |
| ocf_ev | 63 | -0.000 | -0.03 |
| ocf_ev | 126 | -0.004 | -0.14 |
| oil_beta_trend | 21 | 0.001 | 0.03 |
| oil_beta_trend | 63 | -0.019 | -0.60 |
| oil_beta_trend | 126 | -0.009 | -0.27 |
| profitable_growth | 21 | 0.000 | 0.05 |
| profitable_growth | 63 | 0.004 | 0.30 |
| profitable_growth | 126 | -0.000 | -0.02 |
| share_issuance | 21 | 0.010 | 1.40 |
| share_issuance | 63 | 0.015 | 1.61 |
| share_issuance | 126 | 0.023 | 1.87 |
| sue | 21 | -0.000 | -0.06 |
| sue | 63 | -0.008 | -0.89 |
| sue | 126 | -0.016 | -1.44 |
| sue_announce | 21 | 0.010 | 1.99 |
| sue_announce | 63 | 0.017 | 2.58 |
| sue_announce | 126 | 0.018 | 2.38 |

### 7.3 Süreklilik (ρτ, aylık kesitsel sıra korelasyonu)

| Faktör | τ=1 | τ=3 | τ=6 | τ=12 |
|---|---|---|---|---|
| asset_growth | 0.92 | 0.77 | 0.58 | 0.23 |
| capex_at | 0.99 | 0.97 | 0.94 | 0.88 |
| cash_runway_years | 0.96 | 0.88 | 0.81 | 0.68 |
| cop_at | 0.98 | 0.94 | 0.89 | 0.77 |
| dist_52w_high | 0.83 | 0.64 | 0.47 | 0.27 |
| droe | 0.78 | 0.37 | 0.22 | -0.21 |
| ear_3d | 0.65 | -0.01 | 0.01 | -0.01 |
| ebit_ev | 0.98 | 0.94 | 0.86 | 0.72 |
| gross_profitability | 0.99 | 0.97 | 0.94 | 0.89 |
| idio_vol_60d | 0.93 | 0.80 | 0.78 | 0.74 |
| max_ret_21d | 0.54 | 0.54 | 0.52 | 0.50 |
| mom_12_1 | 0.89 | 0.70 | 0.44 | 0.01 |
| net_debt_ebitda | 0.99 | 0.97 | 0.94 | 0.90 |
| ocf_ev | 0.98 | 0.94 | 0.88 | 0.76 |
| oil_beta_trend | 0.65 | 0.18 | 0.00 | -0.15 |
| profitable_growth | 0.97 | 0.90 | 0.79 | 0.56 |
| share_issuance | 0.96 | 0.88 | 0.78 | 0.59 |
| sue | 0.80 | 0.42 | 0.30 | -0.06 |
| sue_announce | 0.86 | 0.59 | 0.45 | 0.17 |

### 7.8 İstikrar (126 seans IC ortalaması) ve ekonomik gerekçe

| Faktör | 2011-07..2015-12 | 2016-01..2020-12 | 2021-01..2026-09 | bull | bear | vix_high | vix_low | Neden çalışmalı | Kaynak |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.016 | -0.014 | 0.028 | 0.010 | 0.013 | 0.022 | -0.002 | aşırı yatırım / q-teorisi (−) | Cooper, Gulen & Schill (2008); Hou, Xue & Zhang (2015) |
| capex_at | -0.017 | -0.005 | -0.027 | -0.023 | 0.037 | -0.000 | -0.034 | yatırım faktörü (−) | Titman, Wei & Xie (2004); Fama & French (2015) CMA |
| cash_runway_years | -0.025 | 0.051 | 0.002 | 0.013 | -0.001 | 0.001 | 0.022 | finansal kısıt / seyreltme riski | Hadlock & Pierce (2010) — tema uyarlaması |
| cop_at | -0.031 | -0.036 | 0.065 | 0.003 | -0.012 | 0.011 | -0.009 | kalite (tahakkuksuz kârlılık) | Ball, Gerakos, Linnainmaa & Nikolaev (2016) |
| dist_52w_high | 0.072 | 0.054 | 0.120 | 0.086 | 0.053 | 0.055 | 0.112 | davranışsal (çıpalama) | George & Hwang (2004) |
| droe | 0.018 | 0.003 | 0.014 | 0.009 | 0.033 | 0.014 | 0.009 | temel momentum | Hou, Xue & Zhang (2015) q-faktör ROE |
| ear_3d | 0.001 | 0.011 | 0.010 | 0.012 | -0.032 | -0.003 | 0.019 | davranışsal (duyuru getirisi sürüklenmesi) | Chan, Jegadeesh & Lakonishok (1996) |
| ebit_ev | 0.028 | -0.069 | -0.006 | -0.016 | -0.026 | -0.027 | -0.006 | değer (risk + davranışsal) | Loughran & Wellman (2011) |
| gross_profitability | 0.000 | 0.007 | 0.010 | 0.005 | 0.015 | 0.007 | 0.005 | risk/kalite | Novy-Marx (2013) |
| idio_vol_60d | 0.097 | 0.077 | 0.115 | 0.096 | 0.100 | 0.068 | 0.127 | sınırlı arbitraj / piyango tercihi (−) | Ang, Hodrick, Xing & Zhang (2006) |
| max_ret_21d | 0.078 | 0.051 | 0.088 | 0.070 | 0.086 | 0.052 | 0.093 | piyango tercihi (−) | Bali, Cakici & Whitelaw (2011) |
| mom_12_1 | 0.027 | -0.000 | 0.051 | 0.022 | 0.065 | 0.031 | 0.022 | davranışsal (yetersiz tepki) + risk | Jegadeesh & Titman (1993); Carhart (1997) |
| net_debt_ebitda | -0.055 | -0.101 | -0.020 | -0.059 | -0.051 | -0.033 | -0.083 | kaldıraç / sıkıntı riski (−) | Campbell, Hilscher & Szilagyi (2008) |
| ocf_ev | -0.027 | -0.011 | 0.054 | 0.009 | -0.008 | 0.054 | -0.041 | değer (nakit akışı) | Lakonishok, Shleifer & Vishny (1994) |
| oil_beta_trend | 0.007 | -0.085 | 0.031 | -0.018 | 0.006 | 0.038 | -0.071 | emtia risk primi + trend | Moskowitz, Ooi & Pedersen (2012) — tema uyarlaması |
| profitable_growth | 0.037 | 0.038 | -0.000 | 0.024 | 0.025 | 0.018 | 0.031 | kalite + büyüme | Mohanram (2005) GSCORE ruhunda |
| share_issuance | 0.042 | 0.029 | 0.100 | 0.061 | 0.039 | 0.055 | 0.063 | piyasa zamanlaması (−) | Pontiff & Woodgate (2008); Daniel & Titman (2006) |
| sue | 0.015 | -0.011 | 0.050 | 0.018 | 0.026 | 0.021 | 0.016 | davranışsal (kazanç sonrası sürüklenme) | Bernard & Thomas (1989) |
| sue_announce | 0.036 | 0.044 | 0.045 | 0.046 | 0.009 | 0.029 | 0.056 | davranışsal (PEAD, duyuru tarihli) | Bernard & Thomas (1989); Livnat & Mendenhall (2006) |

## Kapsam: robotics

### 7.7 Rank IC

| Faktör | Ufuk | IC | NW t | Örtüşmesiz t | IC>0 oranı | Ay |
|---|---|---|---|---|---|---|
| asset_growth | 21 | -0.006 | -0.25 | -0.23 | 54.76% | 84 |
| asset_growth | 63 | 0.026 | 0.82 | 0.63 | 54.88% | 82 |
| asset_growth | 126 | 0.083 | 1.92 | 3.09 | 75.95% | 79 |
| capex_at | 21 | -0.048 | -2.03 | -1.99 | 41.98% | 81 |
| capex_at | 63 | -0.067 | -1.90 | -1.83 | 36.71% | 79 |
| capex_at | 126 | -0.101 | -2.36 | -1.38 | 34.21% | 76 |
| cop_at | 21 | 0.022 | 0.84 | 0.82 | 56.10% | 82 |
| cop_at | 63 | 0.041 | 1.11 | 0.75 | 55.00% | 80 |
| cop_at | 126 | 0.028 | 0.72 | 0.09 | 51.95% | 77 |
| dist_52w_high | 21 | 0.021 | 0.67 | 0.71 | 51.16% | 86 |
| dist_52w_high | 63 | 0.015 | 0.36 | 0.46 | 55.95% | 84 |
| dist_52w_high | 126 | 0.039 | 0.70 | 1.02 | 61.73% | 81 |
| droe | 21 | 0.030 | 1.14 | 1.11 | 52.38% | 84 |
| droe | 63 | 0.048 | 1.72 | 1.87 | 59.76% | 82 |
| droe | 126 | 0.073 | 2.26 | 1.98 | 65.82% | 79 |
| ear_3d | 21 | 0.012 | 0.45 | 0.47 | 59.52% | 84 |
| ear_3d | 63 | -0.000 | -0.00 | 0.98 | 47.56% | 82 |
| ear_3d | 126 | 0.019 | 0.58 | 0.74 | 50.63% | 79 |
| gross_profitability | 21 | 0.016 | 0.55 | 0.56 | 56.41% | 78 |
| gross_profitability | 63 | 0.002 | 0.04 | 0.12 | 52.63% | 76 |
| gross_profitability | 126 | 0.017 | 0.33 | 0.62 | 52.05% | 73 |
| idio_vol_60d | 21 | 0.026 | 0.83 | 0.88 | 53.49% | 86 |
| idio_vol_60d | 63 | 0.023 | 0.55 | 0.31 | 55.95% | 84 |
| idio_vol_60d | 126 | 0.030 | 0.53 | 0.76 | 59.26% | 81 |
| max_ret_21d | 21 | 0.017 | 0.61 | 0.60 | 50.00% | 86 |
| max_ret_21d | 63 | 0.037 | 1.07 | 1.36 | 55.95% | 84 |
| max_ret_21d | 126 | 0.030 | 0.71 | 1.33 | 55.56% | 81 |
| mom_12_1 | 21 | 0.043 | 1.20 | 1.33 | 56.98% | 86 |
| mom_12_1 | 63 | 0.034 | 0.79 | 1.15 | 54.76% | 84 |
| mom_12_1 | 126 | 0.038 | 0.74 | 0.74 | 55.56% | 81 |
| profitable_growth | 21 | -0.053 | -1.87 | -1.91 | 41.46% | 82 |
| profitable_growth | 63 | -0.064 | -1.68 | -1.62 | 38.75% | 80 |
| profitable_growth | 126 | -0.107 | -2.15 | -1.54 | 36.36% | 77 |
| share_issuance | 21 | 0.089 | 3.02 | 2.94 | 61.90% | 84 |
| share_issuance | 63 | 0.138 | 3.85 | 2.74 | 73.17% | 82 |
| share_issuance | 126 | 0.153 | 3.49 | 2.01 | 73.42% | 79 |
| sue | 21 | 0.036 | 1.27 | 1.32 | 55.42% | 83 |
| sue | 63 | 0.047 | 1.44 | 0.42 | 58.02% | 81 |
| sue | 126 | 0.069 | 1.76 | -0.01 | 62.82% | 78 |
| sue_announce | 21 | 0.014 | 0.33 | 0.32 | 48.48% | 33 |
| sue_announce | 63 | -0.032 | -0.46 | -0.01 | 41.94% | 31 |
| sue_announce | 126 | -0.001 | -0.01 | -0.67 | 57.14% | 28 |

### 7.4 Tek değişkenli sıralama (EW; üst − alt = `mimic_`)

| Faktör | Ufuk | Port. | mimic EW | t | mimic VW | Üst − ort. | t | Monoton |
|---|---|---|---|---|---|---|---|---|
| asset_growth | 21 | 3 | 0.02% | 0.02 | -1.11% | 0.22% | 0.54 | ✘ |
| asset_growth | 63 | 3 | 0.70% | 0.41 | -3.99% | 0.78% | 0.91 | ✘ |
| asset_growth | 126 | 3 | 2.50% | 0.69 | -8.54% | 1.26% | 0.76 | ✔ |
| capex_at | 21 | 3 | -2.53% | -2.92 | -3.74% | -1.01% | -2.71 | ✘ |
| capex_at | 63 | 3 | -5.97% | -2.74 | -9.10% | -2.33% | -2.27 | ✘ |
| capex_at | 126 | 3 | -12.35% | -3.01 | -16.96% | -4.33% | -2.42 | ✘ |
| cop_at | 21 | 3 | 0.21% | 0.30 | 1.03% | -0.13% | -0.33 | ✘ |
| cop_at | 63 | 3 | 0.89% | 0.54 | -0.10% | -0.11% | -0.12 | ✘ |
| cop_at | 126 | 3 | 0.63% | 0.23 | -2.00% | -1.53% | -0.80 | ✘ |
| dist_52w_high | 21 | 3 | -0.65% | -0.81 | -2.46% | -0.47% | -1.17 | ✘ |
| dist_52w_high | 63 | 3 | -2.36% | -1.15 | -7.72% | -1.29% | -1.33 | ✘ |
| dist_52w_high | 126 | 3 | -3.92% | -0.91 | -15.34% | -1.70% | -0.93 | ✘ |
| droe | 21 | 3 | 0.75% | 0.93 | 1.17% | 0.35% | 0.86 | ✔ |
| droe | 63 | 3 | 2.16% | 1.22 | 1.93% | 1.50% | 1.68 | ✘ |
| droe | 126 | 3 | 6.31% | 2.79 | 5.18% | 5.10% | 3.83 | ✘ |
| ear_3d | 21 | 3 | -0.27% | -0.37 | -0.70% | 0.13% | 0.33 | ✘ |
| ear_3d | 63 | 3 | 1.26% | 0.73 | -0.58% | 1.32% | 1.48 | ✘ |
| ear_3d | 126 | 3 | -0.44% | -0.18 | 1.55% | 0.86% | 0.74 | ✘ |
| gross_profitability | 21 | 3 | -0.88% | -1.15 | -2.50% | -0.45% | -1.17 | ✘ |
| gross_profitability | 63 | 3 | -1.80% | -0.95 | -5.36% | -0.60% | -0.55 | ✘ |
| gross_profitability | 126 | 3 | -4.41% | -1.04 | -12.75% | -1.32% | -0.61 | ✘ |
| idio_vol_60d | 21 | 3 | -0.87% | -0.80 | -2.82% | -0.45% | -1.01 | ✘ |
| idio_vol_60d | 63 | 3 | -3.91% | -1.48 | -10.36% | -1.71% | -1.42 | ✘ |
| idio_vol_60d | 126 | 3 | -5.93% | -1.13 | -18.71% | -3.12% | -1.33 | ✘ |
| max_ret_21d | 21 | 3 | -1.10% | -1.15 | -3.66% | -0.54% | -1.14 | ✘ |
| max_ret_21d | 63 | 3 | -3.18% | -1.57 | -4.52% | -1.35% | -1.28 | ✘ |
| max_ret_21d | 126 | 3 | -4.40% | -1.18 | -13.88% | -2.52% | -1.22 | ✘ |
| mom_12_1 | 21 | 3 | 0.73% | 0.73 | -0.42% | 0.51% | 0.94 | ✘ |
| mom_12_1 | 63 | 3 | 0.71% | 0.29 | -2.28% | 1.00% | 0.79 | ✘ |
| mom_12_1 | 126 | 3 | 0.87% | 0.22 | -0.61% | 1.83% | 0.97 | ✘ |
| profitable_growth | 21 | 3 | -1.49% | -1.94 | -1.16% | -0.59% | -1.47 | ✘ |
| profitable_growth | 63 | 3 | -3.84% | -2.39 | -5.11% | -1.76% | -2.06 | ✘ |
| profitable_growth | 126 | 3 | -7.76% | -2.72 | -13.28% | -4.08% | -2.69 | ✘ |
| share_issuance | 21 | 3 | 0.58% | 0.57 | -1.25% | 0.18% | 0.42 | ✘ |
| share_issuance | 63 | 3 | 0.75% | 0.34 | -4.93% | -0.06% | -0.06 | ✘ |
| share_issuance | 126 | 3 | -0.29% | -0.06 | -12.82% | -0.94% | -0.44 | ✘ |
| sue | 21 | 3 | 0.30% | 0.44 | 0.14% | -0.27% | -0.69 | ✘ |
| sue | 63 | 3 | 1.44% | 0.88 | 0.46% | -0.15% | -0.16 | ✘ |
| sue | 126 | 3 | 4.18% | 1.65 | -1.61% | 1.24% | 0.84 | ✘ |
| sue_announce | 21 | 3 | -0.30% | -0.28 | -1.06% | -0.21% | -0.32 | ✘ |
| sue_announce | 63 | 3 | -1.78% | -0.65 | -5.36% | -1.42% | -0.93 | ✘ |
| sue_announce | 126 | 3 | -1.55% | -0.22 | -5.46% | -0.29% | -0.06 | ✘ |

### 7.4 Alfalar (21 seans, aylık; NW t)

Üst portföy RF üzeri; `mimic_ew` ham fark.

| Faktör | Seri | capm t | ff3 t | carhart4 t | ff5_mom t |
|---|---|---|---|---|---|
| asset_growth | mimic_ew | 0.08 | -0.28 | -0.36 | -0.46 |
| asset_growth | top_ew | 0.11 | 0.18 | -0.35 | -0.35 |
| capex_at | mimic_ew | -2.79 | -3.10 | -2.94 | -3.09 |
| capex_at | top_ew | -0.86 | -0.72 | -1.32 | -1.30 |
| cop_at | mimic_ew | 0.21 | 0.06 | 0.50 | 0.29 |
| cop_at | top_ew | -0.04 | 0.18 | -0.20 | -0.24 |
| dist_52w_high | mimic_ew | -0.62 | -0.84 | -0.95 | -1.25 |
| dist_52w_high | top_ew | -0.40 | -0.10 | -0.83 | -0.80 |
| droe | mimic_ew | 0.25 | 0.12 | 0.26 | -0.28 |
| droe | top_ew | 0.23 | 0.43 | -0.02 | -0.19 |
| ear_3d | mimic_ew | -0.79 | -0.68 | -0.86 | -1.32 |
| ear_3d | top_ew | -0.03 | 0.35 | -0.31 | -0.34 |
| gross_profitability | mimic_ew | -1.31 | -1.27 | -1.40 | -1.08 |
| gross_profitability | top_ew | -0.40 | 0.01 | -0.52 | -0.37 |
| idio_vol_60d | mimic_ew | -0.29 | -0.67 | -0.52 | -0.84 |
| idio_vol_60d | top_ew | -0.09 | 0.03 | -0.40 | -0.50 |
| max_ret_21d | mimic_ew | -0.31 | -0.54 | -0.10 | -0.27 |
| max_ret_21d | top_ew | -0.10 | 0.05 | -0.32 | -0.46 |
| mom_12_1 | mimic_ew | 0.24 | 0.31 | 0.01 | -0.11 |
| mom_12_1 | top_ew | 0.29 | 0.66 | -0.01 | 0.04 |
| profitable_growth | mimic_ew | -1.88 | -1.83 | -1.58 | -1.44 |
| profitable_growth | top_ew | -0.52 | -0.44 | -0.79 | -0.62 |
| share_issuance | mimic_ew | 0.98 | 0.54 | 1.02 | 0.70 |
| share_issuance | top_ew | 0.25 | 0.36 | 0.01 | -0.04 |
| sue | mimic_ew | -0.14 | -0.28 | 0.01 | -0.53 |
| sue | top_ew | -0.20 | 0.00 | -0.34 | -0.49 |
| sue_announce | mimic_ew | -0.78 | -0.41 | -0.39 | -0.12 |
| sue_announce | top_ew | -0.98 | -0.68 | -1.50 | -1.03 |

### 7.5 Bağımlı iki değişkenli sıralama (tema skoru terciliyle kontrol)

| Faktör | Ufuk | Ort. fark | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.44% | 0.49 |
| asset_growth | 63 | 1.90% | 1.07 |
| asset_growth | 126 | 4.71% | 1.35 |
| capex_at | 21 | -1.77% | -2.29 |
| capex_at | 63 | -3.67% | -1.89 |
| capex_at | 126 | -7.93% | -2.16 |
| cop_at | 21 | 0.63% | 0.90 |
| cop_at | 63 | 1.12% | 0.81 |
| cop_at | 126 | 2.90% | 1.18 |
| dist_52w_high | 21 | 0.68% | 0.76 |
| dist_52w_high | 63 | 1.56% | 0.68 |
| dist_52w_high | 126 | 2.56% | 0.59 |
| droe | 21 | 0.75% | 1.02 |
| droe | 63 | 0.64% | 0.35 |
| droe | 126 | 3.25% | 1.61 |
| ear_3d | 21 | -0.44% | -0.52 |
| ear_3d | 63 | 1.23% | 0.84 |
| ear_3d | 126 | 1.16% | 0.68 |
| gross_profitability | 21 | 0.80% | 1.09 |
| gross_profitability | 63 | 1.84% | 1.12 |
| gross_profitability | 126 | 3.68% | 1.13 |
| idio_vol_60d | 21 | -0.15% | -0.13 |
| idio_vol_60d | 63 | -2.32% | -0.96 |
| idio_vol_60d | 126 | -3.86% | -0.87 |
| max_ret_21d | 21 | -0.66% | -0.73 |
| max_ret_21d | 63 | -1.03% | -0.49 |
| max_ret_21d | 126 | -4.50% | -1.32 |
| mom_12_1 | 21 | 2.65% | 2.82 |
| mom_12_1 | 63 | 4.72% | 2.54 |
| mom_12_1 | 126 | 8.23% | 2.43 |
| profitable_growth | 21 | -1.16% | -1.56 |
| profitable_growth | 63 | -3.40% | -1.73 |
| profitable_growth | 126 | -5.84% | -1.71 |
| share_issuance | 21 | 1.80% | 1.73 |
| share_issuance | 63 | 3.51% | 1.61 |
| share_issuance | 126 | 4.67% | 1.25 |
| sue | 21 | 0.85% | 1.37 |
| sue | 63 | 1.30% | 1.10 |
| sue | 126 | 4.25% | 1.65 |
| sue_announce | 21 | -2.15% | -1.03 |
| sue_announce | 63 | -5.87% | -2.00 |
| sue_announce | 126 | -11.94% | -3.03 |

### 7.6 Fama-MacBeth (tek faktör + β, ln(MktCap); NW t)

| Faktör | Ufuk | OLS rank-normal t | OLS ham t | WLS √MktCap t | 1 std etkisi | Ort. R² |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 0.13 | 0.41 | 0.68 | 0.05% | 22.18% |
| asset_growth | 63 | 0.94 | 1.16 | 0.68 | 0.69% | 20.34% |
| asset_growth | 126 | 1.35 | 1.32 | 1.11 | 2.14% | 18.77% |
| capex_at | 21 | -2.38 | -1.53 | -2.96 | -0.92% | 20.99% |
| capex_at | 63 | -2.43 | -1.61 | -2.93 | -2.13% | 20.30% |
| capex_at | 126 | -2.40 | -1.65 | -2.89 | -4.42% | 20.47% |
| cop_at | 21 | -0.02 | -0.18 | -0.63 | -0.01% | 23.77% |
| cop_at | 63 | -0.31 | -0.36 | -0.79 | -0.32% | 20.96% |
| cop_at | 126 | -0.45 | -0.50 | -0.93 | -1.22% | 20.98% |
| dist_52w_high | 21 | -0.15 | -0.15 | -2.26 | -0.07% | 21.60% |
| dist_52w_high | 63 | -0.66 | -0.26 | -2.29 | -0.89% | 22.48% |
| dist_52w_high | 126 | -0.69 | -0.08 | -1.91 | -1.72% | 19.77% |
| droe | 21 | 0.07 | 0.27 | -0.32 | 0.02% | 22.16% |
| droe | 63 | 0.30 | 0.18 | 0.03 | 0.20% | 19.95% |
| droe | 126 | 1.62 | 0.78 | 0.54 | 1.38% | 18.14% |
| ear_3d | 21 | -0.00 | 0.02 | -0.28 | -0.00% | 22.03% |
| ear_3d | 63 | 0.64 | 0.75 | -0.06 | 0.49% | 21.29% |
| ear_3d | 126 | -0.59 | 0.44 | -0.31 | -0.69% | 20.02% |
| gross_profitability | 21 | -0.45 | -0.13 | -1.29 | -0.17% | 23.82% |
| gross_profitability | 63 | 0.11 | 0.31 | -0.86 | 0.10% | 20.25% |
| gross_profitability | 126 | -0.01 | 0.13 | -0.80 | -0.02% | 20.56% |
| idio_vol_60d | 21 | -1.32 | -1.08 | -1.95 | -0.66% | 21.69% |
| idio_vol_60d | 63 | -1.88 | -0.98 | -2.31 | -2.42% | 22.15% |
| idio_vol_60d | 126 | -1.23 | -0.34 | -1.68 | -4.01% | 21.67% |
| max_ret_21d | 21 | -1.46 | -1.36 | -3.04 | -0.74% | 21.01% |
| max_ret_21d | 63 | -1.81 | -1.58 | -2.41 | -2.12% | 21.03% |
| max_ret_21d | 126 | -1.63 | -1.00 | -1.95 | -3.39% | 19.67% |
| mom_12_1 | 21 | 0.96 | 1.60 | 0.32 | 0.41% | 23.51% |
| mom_12_1 | 63 | 0.63 | 1.26 | 0.30 | 0.66% | 22.39% |
| mom_12_1 | 126 | 0.44 | 1.34 | 0.17 | 0.80% | 20.48% |
| profitable_growth | 21 | -2.98 | -2.74 | -2.65 | -1.04% | 23.27% |
| profitable_growth | 63 | -3.27 | -3.19 | -2.60 | -2.62% | 21.25% |
| profitable_growth | 126 | -3.49 | -3.76 | -2.21 | -6.14% | 22.31% |
| share_issuance | 21 | 1.48 | 0.71 | 0.27 | 0.56% | 22.75% |
| share_issuance | 63 | 1.32 | 0.80 | 0.22 | 1.21% | 21.17% |
| share_issuance | 126 | 0.90 | 0.39 | -0.01 | 1.82% | 19.53% |
| sue | 21 | 0.88 | 0.32 | -0.12 | 0.23% | 22.89% |
| sue | 63 | 1.09 | 1.07 | 0.42 | 0.71% | 19.79% |
| sue | 126 | 1.45 | 1.50 | 0.18 | 1.69% | 20.02% |
| sue_announce | 21 | -0.64 | -0.64 | -0.56 | -0.33% | 22.37% |
| sue_announce | 63 | -1.18 | -0.83 | -1.01 | -1.39% | 24.19% |
| sue_announce | 126 | -1.12 | -1.25 | -0.98 | -3.43% | 24.97% |

### 7.1 Tanımlayıcı istatistikler (winsorize %0,5/%99,5; aylık değerlerin zaman ortalaması)

| Faktör | Ort. | Std | Çarp. | Bas. | P5 | Medyan | P95 | n | Ort. kayması |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.164 | 0.358 | 1.68 | 4.92 | -0.080 | 0.065 | 0.797 | 18 | 0.42 |
| capex_at | 0.025 | 0.017 | 1.25 | 1.96 | 0.009 | 0.020 | 0.056 | 17 | 0.27 |
| cash_runway_years | 9.260 | 1.768 | -1.74 | 4.21 | 5.664 | 10.000 | 10.000 | 18 | 0.39 |
| cop_at | 0.077 | 0.095 | -0.83 | 2.02 | -0.087 | 0.088 | 0.177 | 18 | 0.44 |
| dist_52w_high | -0.184 | 0.131 | -0.96 | 0.83 | -0.404 | -0.155 | -0.040 | 18 | 0.72 |
| droe | 0.004 | 0.080 | 0.06 | 6.20 | -0.077 | -0.000 | 0.097 | 17 | 0.31 |
| ear_3d | 0.010 | 0.095 | 0.41 | 1.04 | -0.110 | 0.001 | 0.152 | 17 | 0.25 |
| ebit_ev | -0.005 | 0.191 | -1.21 | 6.73 | -0.089 | 0.026 | 0.071 | 16 | 0.65 |
| gross_profitability | 0.276 | 0.110 | -0.14 | -0.26 | 0.124 | 0.284 | 0.430 | 17 | 0.46 |
| idio_vol_60d | 0.343 | 0.167 | 1.27 | 2.01 | 0.179 | 0.298 | 0.621 | 18 | 0.70 |
| max_ret_21d | 0.055 | 0.038 | 1.63 | 3.56 | 0.023 | 0.043 | 0.116 | 18 | 0.60 |
| mom_12_1 | 0.253 | 0.506 | 1.09 | 3.46 | -0.223 | 0.154 | 0.931 | 18 | 0.56 |
| net_debt_ebitda | 0.640 | 5.140 | -0.37 | 2.48 | -5.666 | 0.751 | 7.098 | 13 | 0.29 |
| ocf_ev | 0.045 | 0.112 | -0.14 | 6.32 | -0.040 | 0.040 | 0.091 | 17 | 0.54 |
| profitable_growth | 1.128 | 0.418 | 0.01 | -0.39 | 0.552 | 1.127 | 1.714 | 15 | 0.22 |
| share_issuance | 0.031 | 0.126 | 1.21 | 7.24 | -0.043 | 0.004 | 0.202 | 18 | 0.40 |
| sue | 0.268 | 1.333 | 0.28 | 0.93 | -1.512 | 0.183 | 2.229 | 17 | 0.33 |
| sue_announce | 0.575 | 1.310 | 0.40 | 0.48 | -1.012 | 0.501 | 2.459 | 11 | 0.35 |

### 7.2 Korelasyon ve çoklu doğrusallık

Tam matris (alt üçgen Pearson, üst üçgen Spearman): `corr.csv`. |ρ| > 0,7 çiftleri:

| A | B | Pearson | Spearman | Not |
|---|---|---|---|---|
| cash_runway_years | cop_at | 0.73 | 0.59 |  |
| droe | sue | 0.51 | 0.73 | Spearman >> Pearson: doğrusal olmayan monoton ilişki |
| ebit_ev | ocf_ev | 0.76 | 0.75 |  |

VIF > 5: yok

Ortogonalize (tema skoru + alt tema kuklaları sonrası artık) IC:

| Faktör | Ufuk | Artık IC | NW t |
|---|---|---|---|
| asset_growth | 21 | -0.013 | -0.57 |
| asset_growth | 63 | 0.008 | 0.29 |
| asset_growth | 126 | 0.049 | 1.44 |
| capex_at | 21 | -0.045 | -1.86 |
| capex_at | 63 | -0.060 | -1.80 |
| capex_at | 126 | -0.086 | -1.94 |
| cop_at | 21 | 0.029 | 1.34 |
| cop_at | 63 | 0.046 | 1.57 |
| cop_at | 126 | 0.065 | 2.16 |
| dist_52w_high | 21 | 0.004 | 0.15 |
| dist_52w_high | 63 | -0.012 | -0.30 |
| dist_52w_high | 126 | 0.014 | 0.27 |
| droe | 21 | 0.031 | 1.34 |
| droe | 63 | 0.048 | 1.79 |
| droe | 126 | 0.047 | 1.19 |
| ear_3d | 21 | 0.011 | 0.42 |
| ear_3d | 63 | -0.004 | -0.14 |
| ear_3d | 126 | 0.012 | 0.38 |
| gross_profitability | 21 | 0.025 | 0.92 |
| gross_profitability | 63 | 0.006 | 0.18 |
| gross_profitability | 126 | 0.041 | 0.84 |
| idio_vol_60d | 21 | -0.028 | -1.03 |
| idio_vol_60d | 63 | -0.071 | -1.57 |
| idio_vol_60d | 126 | -0.058 | -0.94 |
| max_ret_21d | 21 | -0.010 | -0.42 |
| max_ret_21d | 63 | -0.007 | -0.25 |
| max_ret_21d | 126 | -0.017 | -0.40 |
| mom_12_1 | 21 | 0.035 | 1.08 |
| mom_12_1 | 63 | 0.015 | 0.35 |
| mom_12_1 | 126 | 0.009 | 0.18 |
| profitable_growth | 21 | -0.066 | -2.25 |
| profitable_growth | 63 | -0.101 | -2.64 |
| profitable_growth | 126 | -0.139 | -2.84 |
| share_issuance | 21 | 0.072 | 3.01 |
| share_issuance | 63 | 0.094 | 3.51 |
| share_issuance | 126 | 0.127 | 3.59 |
| sue | 21 | 0.028 | 1.44 |
| sue | 63 | 0.040 | 1.33 |
| sue | 126 | 0.058 | 1.39 |
| sue_announce | 21 | -0.016 | -0.42 |
| sue_announce | 63 | -0.034 | -0.69 |
| sue_announce | 126 | -0.029 | -0.66 |

### 7.3 Süreklilik (ρτ, aylık kesitsel sıra korelasyonu)

| Faktör | τ=1 | τ=3 | τ=6 | τ=12 |
|---|---|---|---|---|
| asset_growth | 0.92 | 0.76 | 0.58 | 0.22 |
| capex_at | 0.98 | 0.95 | 0.90 | 0.82 |
| cash_runway_years | 0.96 | — | — | — |
| cop_at | 0.98 | 0.93 | 0.86 | 0.71 |
| dist_52w_high | 0.79 | 0.60 | 0.45 | 0.32 |
| droe | 0.77 | 0.38 | 0.21 | -0.16 |
| ear_3d | 0.65 | -0.03 | 0.03 | -0.05 |
| ebit_ev | 0.98 | 0.95 | 0.91 | 0.81 |
| gross_profitability | 0.99 | 0.96 | 0.93 | 0.84 |
| idio_vol_60d | 0.88 | 0.70 | 0.68 | 0.62 |
| max_ret_21d | 0.43 | 0.42 | 0.38 | 0.33 |
| mom_12_1 | 0.86 | 0.68 | 0.42 | 0.01 |
| net_debt_ebitda | 0.98 | 0.93 | 0.87 | 0.75 |
| ocf_ev | 0.98 | 0.94 | 0.88 | 0.78 |
| profitable_growth | 0.94 | 0.83 | 0.65 | 0.33 |
| share_issuance | 0.96 | 0.89 | 0.79 | 0.58 |
| sue | 0.79 | 0.42 | 0.27 | -0.09 |
| sue_announce | 0.81 | 0.42 | 0.25 | -0.08 |

### 7.8 İstikrar (126 seans IC ortalaması) ve ekonomik gerekçe

| Faktör | 2011-07..2015-12 | 2016-01..2020-12 | 2021-01..2026-09 | bull | bear | vix_high | vix_low | Neden çalışmalı | Kaynak |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | — | 0.133 | 0.070 | 0.076 | 0.121 | 0.102 | 0.044 | aşırı yatırım / q-teorisi (−) | Cooper, Gulen & Schill (2008); Hou, Xue & Zhang (2015) |
| capex_at | — | -0.122 | -0.096 | -0.101 | -0.097 | -0.074 | -0.158 | yatırım faktörü (−) | Titman, Wei & Xie (2004); Fama & French (2015) CMA |
| cop_at | — | -0.148 | 0.067 | 0.023 | 0.059 | 0.008 | 0.074 | kalite (tahakkuksuz kârlılık) | Ball, Gerakos, Linnainmaa & Nikolaev (2016) |
| dist_52w_high | — | -0.257 | 0.123 | 0.032 | 0.077 | 0.017 | 0.083 | davranışsal (çıpalama) | George & Hwang (2004) |
| droe | — | 0.037 | 0.082 | 0.057 | 0.162 | 0.076 | 0.067 | temel momentum | Hou, Xue & Zhang (2015) q-faktör ROE |
| ear_3d | — | 0.016 | 0.019 | -0.004 | 0.144 | -0.016 | 0.089 | davranışsal (duyuru getirisi sürüklenmesi) | Chan, Jegadeesh & Lakonishok (1996) |
| gross_profitability | — | -0.242 | 0.058 | 0.011 | 0.051 | -0.022 | 0.102 | risk/kalite | Novy-Marx (2013) |
| idio_vol_60d | — | -0.228 | 0.103 | 0.023 | 0.069 | 0.037 | 0.015 | sınırlı arbitraj / piyango tercihi (−) | Ang, Hodrick, Xing & Zhang (2006) |
| max_ret_21d | — | -0.107 | 0.069 | 0.035 | 0.001 | 0.057 | -0.024 | piyango tercihi (−) | Bali, Cakici & Whitelaw (2011) |
| mom_12_1 | — | -0.126 | 0.085 | 0.025 | 0.116 | 0.035 | 0.044 | davranışsal (yetersiz tepki) + risk | Jegadeesh & Titman (1993); Carhart (1997) |
| profitable_growth | — | -0.109 | -0.107 | -0.131 | 0.024 | -0.086 | -0.154 | kalite + büyüme | Mohanram (2005) GSCORE ruhunda |
| share_issuance | — | 0.093 | 0.169 | 0.163 | 0.099 | 0.149 | 0.162 | piyasa zamanlaması (−) | Pontiff & Woodgate (2008); Daniel & Titman (2006) |
| sue | — | 0.002 | 0.085 | 0.045 | 0.203 | 0.088 | 0.029 | davranışsal (kazanç sonrası sürüklenme) | Bernard & Thomas (1989) |
| sue_announce | — | — | -0.001 | -0.007 | 0.150 | -0.014 | 0.013 | davranışsal (PEAD, duyuru tarihli) | Bernard & Thomas (1989); Livnat & Mendenhall (2006) |

## Kapsam: biotech

### 7.7 Rank IC

| Faktör | Ufuk | IC | NW t | Örtüşmesiz t | IC>0 oranı | Ay |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 0.011 | 1.10 | 1.13 | 48.35% | 182 |
| asset_growth | 63 | 0.008 | 0.53 | 0.26 | 50.00% | 180 |
| asset_growth | 126 | 0.020 | 1.08 | 1.26 | 50.28% | 177 |
| capex_at | 21 | -0.009 | -0.98 | -0.95 | 47.25% | 182 |
| capex_at | 63 | -0.009 | -0.71 | -0.43 | 45.56% | 180 |
| capex_at | 126 | -0.028 | -1.65 | -1.85 | 42.37% | 177 |
| cash_runway_years | 21 | 0.004 | 0.41 | 0.43 | 55.56% | 171 |
| cash_runway_years | 63 | 0.010 | 0.71 | -0.00 | 52.07% | 169 |
| cash_runway_years | 126 | 0.013 | 0.74 | 0.09 | 51.20% | 166 |
| cop_at | 21 | 0.008 | 0.65 | 0.68 | 50.00% | 182 |
| cop_at | 63 | -0.005 | -0.28 | -0.43 | 45.00% | 180 |
| cop_at | 126 | 0.008 | 0.32 | 0.04 | 51.41% | 177 |
| dist_52w_high | 21 | 0.041 | 2.86 | 2.75 | 58.24% | 182 |
| dist_52w_high | 63 | 0.069 | 3.87 | 3.83 | 63.33% | 180 |
| dist_52w_high | 126 | 0.098 | 4.83 | 5.59 | 76.84% | 177 |
| droe | 21 | 0.004 | 0.39 | 0.39 | 53.85% | 182 |
| droe | 63 | 0.005 | 0.33 | -0.42 | 50.56% | 180 |
| droe | 126 | -0.006 | -0.33 | -0.08 | 50.85% | 177 |
| ear_3d | 21 | -0.008 | -1.05 | -1.04 | 50.55% | 182 |
| ear_3d | 63 | -0.015 | -1.61 | -0.52 | 41.67% | 180 |
| ear_3d | 126 | -0.004 | -0.36 | 0.60 | 44.07% | 177 |
| gross_profitability | 21 | -0.005 | -0.45 | -0.44 | 48.90% | 182 |
| gross_profitability | 63 | -0.021 | -1.19 | -1.02 | 43.89% | 180 |
| gross_profitability | 126 | -0.008 | -0.30 | 0.24 | 50.85% | 177 |
| idio_vol_60d | 21 | 0.051 | 3.37 | 3.27 | 57.69% | 182 |
| idio_vol_60d | 63 | 0.082 | 4.14 | 3.40 | 65.56% | 180 |
| idio_vol_60d | 126 | 0.125 | 5.04 | 5.26 | 77.97% | 177 |
| max_ret_21d | 21 | 0.038 | 2.72 | 2.67 | 59.34% | 182 |
| max_ret_21d | 63 | 0.067 | 3.67 | 2.46 | 60.00% | 180 |
| max_ret_21d | 126 | 0.102 | 4.49 | 3.62 | 72.32% | 177 |
| mom_12_1 | 21 | 0.010 | 0.83 | 0.87 | 50.00% | 182 |
| mom_12_1 | 63 | 0.006 | 0.40 | 0.47 | 47.22% | 180 |
| mom_12_1 | 126 | 0.007 | 0.38 | 0.58 | 51.98% | 177 |
| share_issuance | 21 | 0.037 | 2.49 | 2.47 | 53.85% | 182 |
| share_issuance | 63 | 0.052 | 2.67 | 1.94 | 57.22% | 180 |
| share_issuance | 126 | 0.078 | 2.95 | 2.21 | 62.15% | 177 |
| sue | 21 | -0.003 | -0.24 | -0.25 | 47.80% | 182 |
| sue | 63 | -0.005 | -0.34 | -0.38 | 50.00% | 180 |
| sue | 126 | 0.008 | 0.50 | 0.23 | 53.67% | 177 |
| sue_announce | 21 | 0.020 | 1.63 | 1.49 | 55.49% | 182 |
| sue_announce | 63 | 0.044 | 2.85 | 2.28 | 61.11% | 180 |
| sue_announce | 126 | 0.071 | 3.23 | 1.60 | 68.36% | 177 |

### 7.4 Tek değişkenli sıralama (EW; üst − alt = `mimic_`)

| Faktör | Ufuk | Port. | mimic EW | t | mimic VW | Üst − ort. | t | Monoton |
|---|---|---|---|---|---|---|---|---|
| asset_growth | 21 | 5 | 0.81% | 1.80 | -0.10% | 0.61% | 2.21 | ✘ |
| asset_growth | 63 | 5 | 1.36% | 1.15 | 0.27% | 1.22% | 1.82 | ✘ |
| asset_growth | 126 | 5 | 3.07% | 1.54 | 2.10% | 2.04% | 1.82 | ✘ |
| capex_at | 21 | 5 | 0.39% | 0.80 | -0.58% | 0.21% | 0.70 | ✘ |
| capex_at | 63 | 5 | 2.11% | 1.88 | 0.10% | 1.10% | 1.59 | ✘ |
| capex_at | 126 | 5 | 2.78% | 1.39 | -0.73% | 1.80% | 1.44 | ✘ |
| cash_runway_years | 21 | 5 | -1.22% | -2.11 | -0.24% | -0.07% | -0.26 | ✘ |
| cash_runway_years | 63 | 5 | -2.79% | -2.02 | -0.69% | -0.10% | -0.12 | ✘ |
| cash_runway_years | 126 | 5 | -3.25% | -1.31 | -2.85% | -0.32% | -0.20 | ✘ |
| cop_at | 21 | 5 | -0.13% | -0.26 | 0.51% | -0.42% | -1.61 | ✘ |
| cop_at | 63 | 5 | -0.85% | -0.71 | 1.64% | -1.38% | -2.09 | ✘ |
| cop_at | 126 | 5 | -1.39% | -0.68 | 3.41% | -2.60% | -2.21 | ✘ |
| dist_52w_high | 21 | 5 | 0.54% | 0.96 | 0.50% | 0.05% | 0.16 | ✘ |
| dist_52w_high | 63 | 5 | 1.60% | 1.26 | 1.35% | 0.23% | 0.34 | ✘ |
| dist_52w_high | 126 | 5 | 3.72% | 1.82 | 2.87% | 1.33% | 1.24 | ✔ |
| droe | 21 | 5 | 0.27% | 0.69 | -0.57% | 0.05% | 0.19 | ✘ |
| droe | 63 | 5 | 0.75% | 0.76 | -1.00% | 0.11% | 0.15 | ✘ |
| droe | 126 | 5 | 0.38% | 0.20 | -3.52% | 0.03% | 0.02 | ✘ |
| ear_3d | 21 | 5 | -0.75% | -1.90 | -0.50% | -0.36% | -1.55 | ✘ |
| ear_3d | 63 | 5 | -1.46% | -2.00 | -0.85% | -0.74% | -1.65 | ✘ |
| ear_3d | 126 | 5 | 0.20% | 0.17 | 1.78% | -0.42% | -0.56 | ✘ |
| gross_profitability | 21 | 5 | 0.11% | 0.25 | 0.13% | -0.12% | -0.53 | ✘ |
| gross_profitability | 63 | 5 | 0.79% | 0.74 | 1.19% | -0.24% | -0.47 | ✘ |
| gross_profitability | 126 | 5 | 2.51% | 1.10 | 3.94% | -0.41% | -0.37 | ✘ |
| idio_vol_60d | 21 | 5 | -0.14% | -0.22 | 0.71% | 0.10% | 0.28 | ✘ |
| idio_vol_60d | 63 | 5 | -0.72% | -0.49 | 1.50% | -0.01% | -0.02 | ✘ |
| idio_vol_60d | 126 | 5 | 1.52% | 0.60 | 3.68% | 0.85% | 0.51 | ✘ |
| max_ret_21d | 21 | 5 | -0.15% | -0.25 | 1.03% | 0.11% | 0.36 | ✘ |
| max_ret_21d | 63 | 5 | -0.75% | -0.56 | 0.93% | 0.04% | 0.05 | ✘ |
| max_ret_21d | 126 | 5 | 0.33% | 0.14 | 1.89% | 0.55% | 0.37 | ✘ |
| mom_12_1 | 21 | 5 | 0.56% | 1.10 | 0.94% | 0.01% | 0.05 | ✘ |
| mom_12_1 | 63 | 5 | 1.74% | 1.42 | 1.73% | 0.76% | 0.97 | ✘ |
| mom_12_1 | 126 | 5 | 1.83% | 0.86 | 0.75% | 0.85% | 0.59 | ✘ |
| share_issuance | 21 | 5 | 0.35% | 0.56 | 1.01% | 0.17% | 0.51 | ✘ |
| share_issuance | 63 | 5 | -0.43% | -0.26 | 0.98% | 0.06% | 0.07 | ✘ |
| share_issuance | 126 | 5 | -0.62% | -0.19 | 1.51% | 0.32% | 0.20 | ✘ |
| sue | 21 | 5 | -0.09% | -0.21 | -0.24% | 0.03% | 0.12 | ✘ |
| sue | 63 | 5 | -0.11% | -0.13 | -0.42% | -0.17% | -0.28 | ✘ |
| sue | 126 | 5 | 0.50% | 0.39 | -1.09% | 0.85% | 1.10 | ✘ |
| sue_announce | 21 | 5 | 0.20% | 0.31 | 0.08% | 0.29% | 0.86 | ✘ |
| sue_announce | 63 | 5 | 1.79% | 1.43 | 1.46% | 0.74% | 0.85 | ✘ |
| sue_announce | 126 | 5 | 5.04% | 2.50 | 3.98% | 2.75% | 1.93 | ✘ |

### 7.4 Alfalar (21 seans, aylık; NW t)

Üst portföy RF üzeri; `mimic_ew` ham fark.

| Faktör | Seri | capm t | ff3 t | carhart4 t | ff5_mom t |
|---|---|---|---|---|---|
| asset_growth | mimic_ew | 1.60 | 1.62 | 1.80 | 1.65 |
| asset_growth | top_ew | 1.00 | 2.03 | 2.05 | 2.35 |
| capex_at | mimic_ew | 0.95 | 1.01 | 1.15 | 1.51 |
| capex_at | top_ew | 0.61 | 1.26 | 1.31 | 1.67 |
| cash_runway_years | mimic_ew | -1.78 | -2.13 | -1.97 | -2.14 |
| cash_runway_years | top_ew | -0.16 | 0.39 | 0.36 | 0.65 |
| cop_at | mimic_ew | 0.32 | 0.09 | 0.24 | 0.18 |
| cop_at | top_ew | 0.10 | 0.50 | 0.53 | 0.69 |
| dist_52w_high | mimic_ew | 1.59 | 1.21 | 1.48 | 1.24 |
| dist_52w_high | top_ew | 0.94 | 1.46 | 1.52 | 1.65 |
| droe | mimic_ew | 0.20 | 0.30 | 0.24 | 0.20 |
| droe | top_ew | 0.64 | 1.14 | 1.08 | 1.20 |
| ear_3d | mimic_ew | -2.03 | -2.12 | -2.05 | -1.99 |
| ear_3d | top_ew | -0.53 | 0.16 | 0.12 | 0.45 |
| gross_profitability | mimic_ew | 0.93 | 0.76 | 1.04 | 0.91 |
| gross_profitability | top_ew | 0.76 | 1.20 | 1.38 | 1.37 |
| idio_vol_60d | mimic_ew | 0.61 | -0.14 | 0.08 | -0.38 |
| idio_vol_60d | top_ew | 1.71 | 1.91 | 1.99 | 1.92 |
| max_ret_21d | mimic_ew | 0.75 | 0.07 | 0.20 | -0.24 |
| max_ret_21d | top_ew | 1.65 | 2.05 | 2.07 | 2.16 |
| mom_12_1 | mimic_ew | 1.13 | 1.10 | 0.92 | 0.97 |
| mom_12_1 | top_ew | 0.04 | 0.69 | 0.62 | 0.94 |
| share_issuance | mimic_ew | 0.96 | 0.37 | 0.59 | 0.23 |
| share_issuance | top_ew | 1.47 | 1.83 | 1.85 | 1.93 |
| sue | mimic_ew | -0.28 | -0.24 | -0.06 | -0.09 |
| sue | top_ew | 0.69 | 1.19 | 1.15 | 1.22 |
| sue_announce | mimic_ew | 0.64 | 0.33 | 0.16 | 0.15 |
| sue_announce | top_ew | 1.43 | 2.02 | 1.80 | 2.03 |

### 7.5 Bağımlı iki değişkenli sıralama (tema skoru terciliyle kontrol)

| Faktör | Ufuk | Ort. fark | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.42% | 1.27 |
| asset_growth | 63 | 0.40% | 0.45 |
| asset_growth | 126 | 1.15% | 0.72 |
| capex_at | 21 | 0.26% | 0.74 |
| capex_at | 63 | 1.28% | 1.60 |
| capex_at | 126 | 0.98% | 0.63 |
| cash_runway_years | 21 | -1.26% | -3.04 |
| cash_runway_years | 63 | -3.84% | -3.82 |
| cash_runway_years | 126 | -5.63% | -2.65 |
| cop_at | 21 | -0.05% | -0.20 |
| cop_at | 63 | -0.36% | -0.62 |
| cop_at | 126 | -0.56% | -0.51 |
| dist_52w_high | 21 | 0.58% | 1.62 |
| dist_52w_high | 63 | 1.22% | 1.63 |
| dist_52w_high | 126 | 2.44% | 1.98 |
| droe | 21 | 0.12% | 0.42 |
| droe | 63 | 0.40% | 0.59 |
| droe | 126 | -0.51% | -0.45 |
| ear_3d | 21 | -0.53% | -1.91 |
| ear_3d | 63 | -1.02% | -1.86 |
| ear_3d | 126 | -0.01% | -0.01 |
| gross_profitability | 21 | -0.19% | -0.79 |
| gross_profitability | 63 | -0.71% | -1.10 |
| gross_profitability | 126 | -0.56% | -0.45 |
| idio_vol_60d | 21 | 0.11% | 0.31 |
| idio_vol_60d | 63 | -0.06% | -0.08 |
| idio_vol_60d | 126 | 1.31% | 0.99 |
| max_ret_21d | 21 | -0.33% | -0.96 |
| max_ret_21d | 63 | -0.60% | -0.84 |
| max_ret_21d | 126 | -0.02% | -0.02 |
| mom_12_1 | 21 | 0.21% | 0.57 |
| mom_12_1 | 63 | 1.14% | 1.24 |
| mom_12_1 | 126 | 1.26% | 0.75 |
| share_issuance | 21 | 0.01% | 0.03 |
| share_issuance | 63 | -0.94% | -0.92 |
| share_issuance | 126 | -1.81% | -0.96 |
| sue | 21 | -0.02% | -0.08 |
| sue | 63 | -0.14% | -0.21 |
| sue | 126 | -0.48% | -0.42 |
| sue_announce | 21 | 0.37% | 0.94 |
| sue_announce | 63 | 1.42% | 1.66 |
| sue_announce | 126 | 2.99% | 1.83 |

### 7.6 Fama-MacBeth (tek faktör + β, ln(MktCap); NW t)

| Faktör | Ufuk | OLS rank-normal t | OLS ham t | WLS √MktCap t | 1 std etkisi | Ort. R² |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 1.68 | 1.49 | 0.42 | 0.22% | 6.92% |
| asset_growth | 63 | 0.70 | 1.22 | -0.12 | 0.25% | 6.09% |
| asset_growth | 126 | 0.78 | 1.22 | 0.26 | 0.48% | 5.69% |
| capex_at | 21 | -0.08 | -0.77 | -0.99 | -0.01% | 6.73% |
| capex_at | 63 | 1.25 | 0.39 | 0.07 | 0.45% | 5.91% |
| capex_at | 126 | 0.49 | -0.40 | -0.44 | 0.35% | 5.39% |
| cash_runway_years | 21 | -1.73 | -1.52 | -0.63 | -0.30% | 5.51% |
| cash_runway_years | 63 | -1.94 | -1.59 | -0.86 | -0.86% | 5.08% |
| cash_runway_years | 126 | -1.61 | -0.69 | -1.08 | -1.18% | 4.86% |
| cop_at | 21 | -0.02 | -1.00 | 0.85 | -0.00% | 10.35% |
| cop_at | 63 | -0.22 | -1.32 | 1.10 | -0.06% | 10.14% |
| cop_at | 126 | -0.15 | -1.00 | 1.46 | -0.08% | 9.87% |
| dist_52w_high | 21 | 0.72 | 1.60 | 0.27 | 0.14% | 7.26% |
| dist_52w_high | 63 | 1.84 | 2.54 | 1.40 | 0.74% | 6.26% |
| dist_52w_high | 126 | 2.12 | 2.75 | 1.42 | 1.33% | 5.71% |
| droe | 21 | 0.73 | -0.97 | 0.11 | 0.08% | 11.13% |
| droe | 63 | 0.97 | -0.72 | 0.07 | 0.26% | 11.08% |
| droe | 126 | 0.38 | -1.24 | -0.43 | 0.19% | 10.69% |
| ear_3d | 21 | -1.73 | -1.70 | -0.79 | -0.19% | 6.49% |
| ear_3d | 63 | -2.03 | -2.18 | -1.27 | -0.46% | 5.65% |
| ear_3d | 126 | -0.14 | 0.27 | 0.07 | -0.06% | 5.37% |
| gross_profitability | 21 | -0.79 | -0.75 | -0.06 | -0.09% | 11.53% |
| gross_profitability | 63 | -0.84 | -1.13 | 0.21 | -0.25% | 11.30% |
| gross_profitability | 126 | -0.42 | -0.85 | 0.71 | -0.25% | 10.81% |
| idio_vol_60d | 21 | -0.10 | -0.28 | 0.43 | -0.02% | 6.60% |
| idio_vol_60d | 63 | -0.24 | -0.37 | 0.34 | -0.11% | 5.97% |
| idio_vol_60d | 126 | 1.12 | 0.46 | 0.86 | 0.92% | 5.90% |
| max_ret_21d | 21 | -0.01 | -0.28 | 1.14 | -0.00% | 6.34% |
| max_ret_21d | 63 | -0.20 | -0.63 | 0.65 | -0.07% | 5.56% |
| max_ret_21d | 126 | 0.53 | -0.69 | 0.90 | 0.31% | 5.49% |
| mom_12_1 | 21 | 1.09 | 0.85 | 0.85 | 0.17% | 6.82% |
| mom_12_1 | 63 | 1.76 | 1.78 | 1.49 | 0.68% | 5.95% |
| mom_12_1 | 126 | 1.45 | 1.66 | 1.22 | 0.95% | 5.42% |
| share_issuance | 21 | 0.84 | -0.33 | 0.89 | 0.13% | 6.86% |
| share_issuance | 63 | -0.24 | -0.98 | 0.07 | -0.11% | 6.29% |
| share_issuance | 126 | -0.26 | -0.68 | 0.08 | -0.22% | 6.21% |
| sue | 21 | 0.09 | -0.39 | -0.19 | 0.01% | 10.88% |
| sue | 63 | 0.44 | 0.02 | 0.03 | 0.11% | 10.12% |
| sue | 126 | 0.58 | 0.16 | -0.01 | 0.25% | 9.70% |
| sue_announce | 21 | 1.01 | 1.17 | 1.03 | 0.15% | 11.09% |
| sue_announce | 63 | 2.18 | 2.28 | 1.78 | 0.81% | 10.23% |
| sue_announce | 126 | 2.18 | 2.65 | 1.42 | 1.68% | 10.82% |

Tüm faktörlü model (kapsama ≥ %50, eksiksiz satırlar):

| Ufuk | Faktör | Katsayı | NW t | Ort. düz. R² |
|---|---|---|---|---|
| 21 | asset_growth | -0.14% | -0.64 | 16.49% |
| 21 | capex_at | 0.28% | 1.44 | 16.49% |
| 21 | cash_runway_years | -0.00% | -0.01 | 16.49% |
| 21 | cop_at | 0.17% | 0.54 | 16.49% |
| 21 | dist_52w_high | 0.31% | 1.26 | 16.49% |
| 21 | droe | 0.17% | 0.76 | 16.49% |
| 21 | ear_3d | 0.05% | 0.30 | 16.49% |
| 21 | ebit_ev | -0.30% | -0.88 | 16.49% |
| 21 | gross_profitability | 0.26% | 1.29 | 16.49% |
| 21 | idio_vol_60d | -0.47% | -1.63 | 16.49% |
| 21 | max_ret_21d | 0.32% | 1.58 | 16.49% |
| 21 | mom_12_1 | 0.19% | 0.84 | 16.49% |
| 21 | ocf_ev | 0.07% | 0.21 | 16.49% |
| 21 | share_issuance | 0.22% | 1.08 | 16.49% |
| 21 | sue | -0.02% | -0.09 | 16.49% |
| 63 | asset_growth | -0.58% | -1.06 | 14.26% |
| 63 | capex_at | 0.65% | 1.41 | 14.26% |
| 63 | cash_runway_years | 0.47% | 0.57 | 14.26% |
| 63 | cop_at | -0.06% | -0.07 | 14.26% |
| 63 | dist_52w_high | 0.17% | 0.28 | 14.26% |
| 63 | droe | 0.21% | 0.44 | 14.26% |
| 63 | ear_3d | 0.27% | 0.68 | 14.26% |
| 63 | ebit_ev | -0.84% | -1.08 | 14.26% |
| 63 | gross_profitability | 0.57% | 1.12 | 14.26% |
| 63 | idio_vol_60d | 0.02% | 0.04 | 14.26% |
| 63 | max_ret_21d | 0.20% | 0.60 | 14.26% |
| 63 | mom_12_1 | 0.54% | 0.97 | 14.26% |
| 63 | ocf_ev | 0.24% | 0.32 | 14.26% |
| 63 | share_issuance | 0.24% | 0.48 | 14.26% |
| 63 | sue | 0.19% | 0.37 | 14.26% |
| 126 | asset_growth | -1.36% | -1.36 | 12.55% |
| 126 | capex_at | 0.71% | 0.82 | 12.55% |
| 126 | cash_runway_years | -0.23% | -0.16 | 12.55% |
| 126 | cop_at | -0.00% | -0.00 | 12.55% |
| 126 | dist_52w_high | -0.26% | -0.22 | 12.55% |
| 126 | droe | 0.38% | 0.45 | 12.55% |
| 126 | ear_3d | 0.04% | 0.07 | 12.55% |
| 126 | ebit_ev | -2.52% | -1.70 | 12.55% |
| 126 | gross_profitability | 1.07% | 1.07 | 12.55% |
| 126 | idio_vol_60d | 2.15% | 1.79 | 12.55% |
| 126 | max_ret_21d | -0.16% | -0.34 | 12.55% |
| 126 | mom_12_1 | 1.26% | 1.58 | 12.55% |
| 126 | ocf_ev | 2.03% | 1.35 | 12.55% |
| 126 | share_issuance | 0.27% | 0.29 | 12.55% |
| 126 | sue | 0.23% | 0.30 | 12.55% |

### 7.1 Tanımlayıcı istatistikler (winsorize %0,5/%99,5; aylık değerlerin zaman ortalaması)

| Faktör | Ort. | Std | Çarp. | Bas. | P5 | Medyan | P95 | n | Ort. kayması |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.366 | 0.747 | 2.90 | 11.05 | -0.237 | 0.135 | 1.780 | 157 | 0.24 |
| capex_at | 0.018 | 0.020 | 2.17 | 6.35 | 0.001 | 0.012 | 0.055 | 150 | 0.18 |
| cash_runway_years | 6.405 | 3.759 | -0.36 | -1.14 | 0.942 | 7.419 | 10.000 | 159 | 0.22 |
| cop_at | -0.100 | 0.269 | -1.06 | 1.77 | -0.574 | -0.046 | 0.218 | 159 | 0.22 |
| dist_52w_high | -0.257 | 0.183 | -0.79 | 0.13 | -0.597 | -0.223 | -0.030 | 160 | 0.46 |
| droe | -0.003 | 0.229 | 0.01 | 8.66 | -0.315 | -0.002 | 0.308 | 142 | 0.12 |
| ear_3d | 0.007 | 0.098 | 0.44 | 3.31 | -0.137 | 0.002 | 0.163 | 147 | 0.09 |
| ebit_ev | -0.085 | 0.259 | -2.87 | 17.50 | -0.390 | -0.033 | 0.089 | 149 | 0.31 |
| gross_profitability | 0.307 | 0.200 | 0.92 | 1.16 | 0.041 | 0.273 | 0.671 | 92 | 0.20 |
| idio_vol_60d | 0.515 | 0.338 | 2.42 | 10.25 | 0.179 | 0.453 | 1.049 | 160 | 0.32 |
| max_ret_21d | 0.078 | 0.083 | 3.82 | 20.88 | 0.021 | 0.057 | 0.190 | 160 | 0.24 |
| mom_12_1 | 0.400 | 0.964 | 2.67 | 11.20 | -0.439 | 0.156 | 2.013 | 160 | 0.38 |
| net_debt_ebitda | 0.549 | 7.449 | 0.92 | 7.99 | -10.478 | 0.359 | 9.783 | 55 | 0.16 |
| ocf_ev | -0.047 | 0.205 | -2.50 | 15.43 | -0.296 | -0.008 | 0.104 | 158 | 0.28 |
| profitable_growth | 1.067 | 0.420 | 0.11 | -0.55 | 0.411 | 1.034 | 1.775 | 67 | 0.05 |
| share_issuance | 0.095 | 0.187 | 2.94 | 14.64 | -0.041 | 0.035 | 0.375 | 154 | 0.25 |
| sue | -0.221 | 1.398 | -0.28 | 0.34 | -2.667 | -0.105 | 1.996 | 154 | 0.15 |
| sue_announce | 0.473 | 1.535 | 0.30 | 0.45 | -1.824 | 0.324 | 3.038 | 59 | 0.26 |

### 7.2 Korelasyon ve çoklu doğrusallık

Tam matris (alt üçgen Pearson, üst üçgen Spearman): `corr.csv`. |ρ| > 0,7 çiftleri:

| A | B | Pearson | Spearman | Not |
|---|---|---|---|---|
| cash_runway_years | cop_at | 0.85 | 0.86 |  |
| cash_runway_years | ebit_ev | 0.53 | 0.71 | Spearman >> Pearson: doğrusal olmayan monoton ilişki |
| cash_runway_years | ocf_ev | 0.63 | 0.81 | Spearman >> Pearson: doğrusal olmayan monoton ilişki |
| cop_at | ebit_ev | 0.54 | 0.76 | Spearman >> Pearson: doğrusal olmayan monoton ilişki |
| cop_at | ocf_ev | 0.65 | 0.85 | Spearman >> Pearson: doğrusal olmayan monoton ilişki |
| ebit_ev | ocf_ev | 0.87 | 0.87 |  |
| idio_vol_60d | max_ret_21d | 0.64 | 0.72 |  |

VIF > 5: `cop_at` (6.6), `ebit_ev` (7.9), `ocf_ev` (9.4)

Ortogonalize (tema skoru + alt tema kuklaları sonrası artık) IC:

| Faktör | Ufuk | Artık IC | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.010 | 1.10 |
| asset_growth | 63 | 0.004 | 0.32 |
| asset_growth | 126 | 0.014 | 0.83 |
| capex_at | 21 | -0.007 | -0.83 |
| capex_at | 63 | -0.006 | -0.57 |
| capex_at | 126 | -0.022 | -1.55 |
| cash_runway_years | 21 | -0.020 | -1.88 |
| cash_runway_years | 63 | -0.028 | -2.23 |
| cash_runway_years | 126 | -0.032 | -1.68 |
| cop_at | 21 | -0.001 | -0.08 |
| cop_at | 63 | -0.015 | -1.14 |
| cop_at | 126 | -0.015 | -0.76 |
| dist_52w_high | 21 | 0.016 | 1.55 |
| dist_52w_high | 63 | 0.032 | 2.68 |
| dist_52w_high | 126 | 0.042 | 3.02 |
| droe | 21 | 0.001 | 0.07 |
| droe | 63 | -0.001 | -0.08 |
| droe | 126 | -0.026 | -1.37 |
| ear_3d | 21 | -0.009 | -1.23 |
| ear_3d | 63 | -0.015 | -1.80 |
| ear_3d | 126 | -0.004 | -0.46 |
| gross_profitability | 21 | -0.008 | -0.74 |
| gross_profitability | 63 | -0.029 | -1.86 |
| gross_profitability | 126 | -0.027 | -1.11 |
| idio_vol_60d | 21 | 0.031 | 2.79 |
| idio_vol_60d | 63 | 0.049 | 3.51 |
| idio_vol_60d | 126 | 0.075 | 4.50 |
| max_ret_21d | 21 | 0.016 | 1.62 |
| max_ret_21d | 63 | 0.033 | 2.70 |
| max_ret_21d | 126 | 0.051 | 3.60 |
| mom_12_1 | 21 | -0.004 | -0.36 |
| mom_12_1 | 63 | -0.013 | -0.88 |
| mom_12_1 | 126 | -0.025 | -1.25 |
| share_issuance | 21 | 0.020 | 1.74 |
| share_issuance | 63 | 0.023 | 1.54 |
| share_issuance | 126 | 0.035 | 1.80 |
| sue | 21 | -0.014 | -1.15 |
| sue | 63 | -0.025 | -1.58 |
| sue | 126 | -0.030 | -1.49 |
| sue_announce | 21 | 0.006 | 0.52 |
| sue_announce | 63 | 0.022 | 1.81 |
| sue_announce | 126 | 0.029 | 1.71 |

### 7.3 Süreklilik (ρτ, aylık kesitsel sıra korelasyonu)

| Faktör | τ=1 | τ=3 | τ=6 | τ=12 |
|---|---|---|---|---|
| asset_growth | 0.90 | 0.70 | 0.47 | 0.07 |
| capex_at | 0.98 | 0.95 | 0.90 | 0.78 |
| cash_runway_years | 0.97 | 0.90 | 0.83 | 0.72 |
| cop_at | 0.98 | 0.94 | 0.88 | 0.78 |
| dist_52w_high | 0.83 | 0.65 | 0.48 | 0.31 |
| droe | 0.79 | 0.38 | 0.20 | -0.24 |
| ear_3d | 0.63 | -0.02 | 0.01 | 0.01 |
| ebit_ev | 0.98 | 0.94 | 0.89 | 0.78 |
| gross_profitability | 0.98 | 0.95 | 0.91 | 0.84 |
| idio_vol_60d | 0.91 | 0.75 | 0.74 | 0.72 |
| max_ret_21d | 0.50 | 0.50 | 0.48 | 0.48 |
| mom_12_1 | 0.88 | 0.69 | 0.41 | -0.03 |
| net_debt_ebitda | 0.98 | 0.95 | 0.91 | 0.85 |
| ocf_ev | 0.98 | 0.93 | 0.88 | 0.77 |
| profitable_growth | 0.97 | 0.91 | 0.81 | 0.63 |
| share_issuance | 0.96 | 0.88 | 0.79 | 0.62 |
| sue | 0.82 | 0.48 | 0.38 | 0.03 |
| sue_announce | 0.86 | 0.59 | 0.47 | 0.23 |

### 7.8 İstikrar (126 seans IC ortalaması) ve ekonomik gerekçe

| Faktör | 2011-07..2015-12 | 2016-01..2020-12 | 2021-01..2026-09 | bull | bear | vix_high | vix_low | Neden çalışmalı | Kaynak |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.042 | 0.000 | 0.020 | 0.022 | 0.005 | 0.024 | 0.016 | aşırı yatırım / q-teorisi (−) | Cooper, Gulen & Schill (2008); Hou, Xue & Zhang (2015) |
| capex_at | -0.064 | -0.053 | 0.028 | -0.033 | 0.026 | -0.020 | -0.035 | yatırım faktörü (−) | Titman, Wei & Xie (2004); Fama & French (2015) CMA |
| cash_runway_years | -0.039 | 0.034 | 0.029 | 0.016 | -0.011 | 0.012 | 0.015 | finansal kısıt / seyreltme riski | Hadlock & Pierce (2010) — tema uyarlaması |
| cop_at | -0.013 | -0.042 | 0.073 | 0.010 | -0.018 | -0.010 | 0.026 | kalite (tahakkuksuz kârlılık) | Ball, Gerakos, Linnainmaa & Nikolaev (2016) |
| dist_52w_high | 0.082 | 0.079 | 0.131 | 0.099 | 0.091 | 0.091 | 0.106 | davranışsal (çıpalama) | George & Hwang (2004) |
| droe | -0.009 | -0.013 | 0.005 | -0.014 | 0.071 | -0.016 | 0.005 | temel momentum | Hou, Xue & Zhang (2015) q-faktör ROE |
| ear_3d | -0.001 | 0.002 | -0.012 | 0.001 | -0.047 | -0.007 | -0.001 | davranışsal (duyuru getirisi sürüklenmesi) | Chan, Jegadeesh & Lakonishok (1996) |
| gross_profitability | -0.061 | -0.017 | 0.045 | -0.011 | 0.022 | -0.020 | 0.004 | risk/kalite | Novy-Marx (2013) |
| idio_vol_60d | 0.117 | 0.098 | 0.158 | 0.124 | 0.139 | 0.124 | 0.127 | sınırlı arbitraj / piyango tercihi (−) | Ang, Hodrick, Xing & Zhang (2006) |
| max_ret_21d | 0.105 | 0.067 | 0.131 | 0.099 | 0.122 | 0.103 | 0.100 | piyango tercihi (−) | Bali, Cakici & Whitelaw (2011) |
| mom_12_1 | 0.000 | 0.026 | -0.005 | -0.002 | 0.093 | 0.015 | -0.001 | davranışsal (yetersiz tepki) + risk | Jegadeesh & Titman (1993); Carhart (1997) |
| share_issuance | 0.095 | 0.048 | 0.092 | 0.085 | 0.011 | 0.073 | 0.083 | piyasa zamanlaması (−) | Pontiff & Woodgate (2008); Daniel & Titman (2006) |
| sue | 0.008 | -0.007 | 0.023 | 0.003 | 0.057 | -0.005 | 0.022 | davranışsal (kazanç sonrası sürüklenme) | Bernard & Thomas (1989) |
| sue_announce | 0.028 | 0.132 | 0.049 | 0.068 | 0.094 | 0.058 | 0.084 | davranışsal (PEAD, duyuru tarihli) | Bernard & Thomas (1989); Livnat & Mendenhall (2006) |

## Kapsam: energy

### 7.7 Rank IC

| Faktör | Ufuk | IC | NW t | Örtüşmesiz t | IC>0 oranı | Ay |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 0.023 | 1.50 | 1.57 | 52.20% | 182 |
| asset_growth | 63 | 0.040 | 1.97 | 2.02 | 62.22% | 180 |
| asset_growth | 126 | 0.066 | 2.52 | 2.11 | 67.23% | 177 |
| capex_at | 21 | 0.016 | 1.23 | 1.25 | 52.75% | 182 |
| capex_at | 63 | 0.023 | 1.12 | 1.34 | 55.00% | 180 |
| capex_at | 126 | 0.043 | 1.43 | 1.47 | 63.28% | 177 |
| cash_runway_years | 21 | -0.101 | -0.86 | -0.78 | 25.00% | 8 |
| cash_runway_years | 63 | -0.125 | -2.07 | -0.18 | 28.57% | 7 |
| cash_runway_years | 126 | -0.311 | -6.30 | — | 16.67% | 6 |
| cop_at | 21 | -0.009 | -0.46 | -0.49 | 51.10% | 182 |
| cop_at | 63 | -0.027 | -0.97 | -1.16 | 48.89% | 180 |
| cop_at | 126 | -0.046 | -1.18 | -1.18 | 47.46% | 177 |
| dist_52w_high | 21 | 0.038 | 1.47 | 1.50 | 56.59% | 182 |
| dist_52w_high | 63 | 0.044 | 1.26 | 1.13 | 52.22% | 180 |
| dist_52w_high | 126 | 0.053 | 1.05 | 0.99 | 54.80% | 177 |
| ear_3d | 21 | 0.023 | 2.29 | 2.21 | 56.04% | 182 |
| ear_3d | 63 | 0.017 | 1.33 | 0.66 | 60.56% | 180 |
| ear_3d | 126 | 0.019 | 1.17 | 0.95 | 56.50% | 177 |
| ebit_ev | 21 | 0.003 | 0.16 | 0.18 | 52.20% | 182 |
| ebit_ev | 63 | -0.016 | -0.60 | -0.89 | 48.89% | 180 |
| ebit_ev | 126 | -0.018 | -0.51 | -0.43 | 48.59% | 177 |
| gross_profitability | 21 | -0.002 | -0.10 | -0.12 | 47.25% | 182 |
| gross_profitability | 63 | -0.022 | -0.90 | -0.75 | 46.11% | 180 |
| gross_profitability | 126 | -0.026 | -0.91 | -0.84 | 37.29% | 177 |
| idio_vol_60d | 21 | 0.040 | 1.32 | 1.35 | 52.20% | 182 |
| idio_vol_60d | 63 | 0.053 | 1.30 | 1.22 | 55.00% | 180 |
| idio_vol_60d | 126 | 0.074 | 1.31 | 1.13 | 51.98% | 177 |
| max_ret_21d | 21 | 0.031 | 1.14 | 1.16 | 53.85% | 182 |
| max_ret_21d | 63 | 0.047 | 1.37 | 1.29 | 52.78% | 180 |
| max_ret_21d | 126 | 0.053 | 1.11 | 0.85 | 52.54% | 177 |
| mom_12_1 | 21 | 0.011 | 0.51 | 0.51 | 50.00% | 182 |
| mom_12_1 | 63 | 0.027 | 0.89 | 0.81 | 53.33% | 180 |
| mom_12_1 | 126 | 0.033 | 0.75 | 0.73 | 55.93% | 177 |
| net_debt_ebitda | 21 | -0.014 | -0.69 | -0.75 | 50.00% | 182 |
| net_debt_ebitda | 63 | -0.035 | -1.32 | -1.30 | 47.78% | 180 |
| net_debt_ebitda | 126 | -0.053 | -1.54 | -1.40 | 45.76% | 177 |
| ocf_ev | 21 | 0.014 | 0.69 | 0.74 | 52.75% | 182 |
| ocf_ev | 63 | 0.008 | 0.30 | -0.23 | 54.44% | 180 |
| ocf_ev | 126 | 0.011 | 0.25 | 0.00 | 54.80% | 177 |
| oil_beta_trend | 21 | 0.006 | 0.25 | 0.25 | 54.95% | 182 |
| oil_beta_trend | 63 | -0.023 | -0.69 | -0.16 | 46.67% | 180 |
| oil_beta_trend | 126 | -0.016 | -0.43 | -0.77 | 48.59% | 177 |
| share_issuance | 21 | 0.022 | 2.09 | 2.13 | 57.69% | 182 |
| share_issuance | 63 | 0.029 | 1.91 | 1.32 | 64.44% | 180 |
| share_issuance | 126 | 0.042 | 2.01 | 0.94 | 64.41% | 177 |
| sue_announce | 21 | 0.020 | 1.43 | 1.41 | 53.30% | 182 |
| sue_announce | 63 | 0.025 | 1.25 | 0.65 | 52.22% | 180 |
| sue_announce | 126 | 0.027 | 1.14 | 1.47 | 55.93% | 177 |

### 7.4 Tek değişkenli sıralama (EW; üst − alt = `mimic_`)

| Faktör | Ufuk | Port. | mimic EW | t | mimic VW | Üst − ort. | t | Monoton |
|---|---|---|---|---|---|---|---|---|
| asset_growth | 21 | 5 | 0.75% | 1.62 | 0.19% | 0.41% | 1.29 | ✘ |
| asset_growth | 63 | 5 | 1.99% | 1.76 | 0.64% | 1.20% | 1.69 | ✘ |
| asset_growth | 126 | 5 | 4.23% | 1.81 | 1.33% | 2.65% | 1.72 | ✘ |
| capex_at | 21 | 5 | 0.41% | 0.87 | 0.22% | 0.17% | 0.66 | ✘ |
| capex_at | 63 | 5 | 1.98% | 1.59 | 1.04% | 0.95% | 1.28 | ✘ |
| capex_at | 126 | 5 | 4.52% | 1.67 | 1.83% | 1.80% | 1.19 | ✘ |
| cash_runway_years | 21 | 3 | -3.75% | -0.85 | -8.96% | -3.41% | -2.59 | ✘ |
| cash_runway_years | 63 | 3 | -10.43% | -2.79 | -24.11% | -2.78% | -0.87 | ✘ |
| cash_runway_years | 126 | 3 | -21.56% | -8.15 | -38.21% | -8.22% | -6.67 | ✘ |
| cop_at | 21 | 5 | 0.06% | 0.12 | 0.23% | 0.04% | 0.12 | ✘ |
| cop_at | 63 | 5 | -0.49% | -0.40 | 0.01% | -0.39% | -0.52 | ✘ |
| cop_at | 126 | 5 | -1.66% | -0.64 | -0.60% | -1.19% | -0.75 | ✘ |
| dist_52w_high | 21 | 5 | 0.00% | 0.00 | 0.43% | 0.03% | 0.08 | ✘ |
| dist_52w_high | 63 | 5 | -0.75% | -0.37 | 1.04% | -0.18% | -0.20 | ✘ |
| dist_52w_high | 126 | 5 | -1.18% | -0.28 | 1.04% | -0.22% | -0.13 | ✘ |
| ear_3d | 21 | 5 | 0.38% | 1.03 | 0.13% | 0.23% | 1.04 | ✘ |
| ear_3d | 63 | 5 | 0.39% | 0.51 | -0.32% | 0.31% | 0.59 | ✘ |
| ear_3d | 126 | 5 | 1.45% | 1.15 | 1.85% | 1.01% | 1.05 | ✘ |
| ebit_ev | 21 | 5 | -0.38% | -0.68 | -0.25% | -0.08% | -0.25 | ✘ |
| ebit_ev | 63 | 5 | -1.92% | -1.33 | -1.27% | -1.04% | -1.40 | ✘ |
| ebit_ev | 126 | 5 | -4.23% | -1.57 | -3.29% | -2.11% | -1.49 | ✘ |
| gross_profitability | 21 | 5 | -0.20% | -0.36 | -1.00% | -0.13% | -0.34 | ✘ |
| gross_profitability | 63 | 5 | -0.47% | -0.29 | -2.88% | -0.65% | -0.66 | ✘ |
| gross_profitability | 126 | 5 | 0.11% | 0.04 | -4.42% | 0.01% | 0.01 | ✘ |
| idio_vol_60d | 21 | 5 | -0.52% | -0.51 | -0.01% | -0.13% | -0.27 | ✘ |
| idio_vol_60d | 63 | 5 | -1.82% | -0.72 | -0.63% | -0.42% | -0.37 | ✘ |
| idio_vol_60d | 126 | 5 | -2.58% | -0.53 | -0.68% | -0.81% | -0.36 | ✘ |
| max_ret_21d | 21 | 5 | -0.55% | -0.64 | -0.27% | -0.22% | -0.53 | ✘ |
| max_ret_21d | 63 | 5 | -1.74% | -0.81 | -0.27% | -0.61% | -0.62 | ✘ |
| max_ret_21d | 126 | 5 | -3.17% | -0.80 | -1.97% | -1.36% | -0.72 | ✘ |
| mom_12_1 | 21 | 5 | 0.38% | 0.51 | -0.04% | 0.50% | 1.38 | ✘ |
| mom_12_1 | 63 | 5 | 1.31% | 0.80 | 0.31% | 1.46% | 1.84 | ✘ |
| mom_12_1 | 126 | 5 | 1.36% | 0.39 | -1.18% | 2.04% | 1.39 | ✘ |
| net_debt_ebitda | 21 | 5 | 0.25% | 0.56 | 0.20% | 0.15% | 0.48 | ✘ |
| net_debt_ebitda | 63 | 5 | 0.21% | 0.18 | -0.18% | 0.10% | 0.13 | ✘ |
| net_debt_ebitda | 126 | 5 | 0.11% | 0.05 | -1.04% | 0.03% | 0.02 | ✘ |
| ocf_ev | 21 | 5 | 0.46% | 0.71 | 0.57% | 0.06% | 0.14 | ✘ |
| ocf_ev | 63 | 5 | 0.56% | 0.37 | 1.04% | -0.33% | -0.35 | ✘ |
| ocf_ev | 126 | 5 | 0.53% | 0.16 | 1.60% | -0.99% | -0.47 | ✘ |
| oil_beta_trend | 21 | 5 | 0.42% | 0.57 | 0.76% | 0.28% | 0.74 | ✘ |
| oil_beta_trend | 63 | 5 | -0.50% | -0.28 | 0.46% | 0.10% | 0.10 | ✘ |
| oil_beta_trend | 126 | 5 | 0.08% | 0.03 | 1.50% | 0.55% | 0.31 | ✘ |
| share_issuance | 21 | 5 | -0.02% | -0.06 | 0.07% | 0.16% | 0.69 | ✘ |
| share_issuance | 63 | 5 | 0.04% | 0.04 | 0.46% | 0.25% | 0.47 | ✘ |
| share_issuance | 126 | 5 | 0.75% | 0.40 | 1.45% | 0.50% | 0.46 | ✘ |
| sue_announce | 21 | 5 | 0.32% | 0.73 | 0.34% | 0.03% | 0.12 | ✘ |
| sue_announce | 63 | 5 | 0.54% | 0.58 | 1.06% | -0.23% | -0.46 | ✘ |
| sue_announce | 126 | 5 | 0.83% | 0.52 | 1.27% | 0.23% | 0.30 | ✘ |

### 7.4 Alfalar (21 seans, aylık; NW t)

Üst portföy RF üzeri; `mimic_ew` ham fark.

| Faktör | Seri | capm t | ff3 t | carhart4 t | ff5_mom t |
|---|---|---|---|---|---|
| asset_growth | mimic_ew | 1.62 | 1.59 | 1.56 | 1.57 |
| asset_growth | top_ew | 0.10 | 0.06 | 0.06 | -0.15 |
| capex_at | mimic_ew | 1.16 | 1.44 | 0.86 | 1.07 |
| capex_at | top_ew | -0.24 | -0.20 | -0.37 | -0.40 |
| cash_runway_years | mimic_ew | -1.08 | — | — | — |
| cash_runway_years | top_ew | -2.12 | — | — | — |
| cop_at | mimic_ew | -0.65 | -0.81 | -0.56 | -0.77 |
| cop_at | top_ew | -0.52 | -0.71 | -0.59 | -0.84 |
| dist_52w_high | mimic_ew | 1.59 | 1.69 | 1.24 | 1.17 |
| dist_52w_high | top_ew | 1.47 | 1.41 | 0.84 | 0.49 |
| ear_3d | mimic_ew | 1.48 | 1.49 | 1.56 | 1.19 |
| ear_3d | top_ew | -0.14 | -0.13 | -0.15 | -0.41 |
| ebit_ev | mimic_ew | -0.67 | -0.84 | -0.50 | -1.04 |
| ebit_ev | top_ew | -0.85 | -1.10 | -0.90 | -1.36 |
| gross_profitability | mimic_ew | 0.15 | -0.07 | 0.09 | -0.04 |
| gross_profitability | top_ew | -0.51 | -0.78 | -0.71 | -0.95 |
| idio_vol_60d | mimic_ew | 0.81 | 0.71 | 0.57 | 0.48 |
| idio_vol_60d | top_ew | 1.13 | 0.81 | 0.63 | 0.38 |
| max_ret_21d | mimic_ew | 0.56 | 0.38 | 0.27 | 0.13 |
| max_ret_21d | top_ew | 0.53 | 0.17 | -0.01 | -0.30 |
| mom_12_1 | mimic_ew | 1.35 | 1.19 | 0.26 | 0.57 |
| mom_12_1 | top_ew | 0.68 | 0.73 | 0.09 | 0.22 |
| net_debt_ebitda | mimic_ew | -0.55 | -0.48 | -0.61 | -0.81 |
| net_debt_ebitda | top_ew | -0.70 | -0.82 | -0.92 | -1.15 |
| ocf_ev | mimic_ew | -0.07 | -0.20 | 0.20 | -0.09 |
| ocf_ev | top_ew | -0.61 | -0.80 | -0.62 | -0.87 |
| oil_beta_trend | mimic_ew | 1.99 | 2.05 | 1.78 | 1.88 |
| oil_beta_trend | top_ew | 0.43 | 0.52 | 0.50 | 0.33 |
| share_issuance | mimic_ew | -0.01 | -0.23 | -0.07 | -0.63 |
| share_issuance | top_ew | -0.15 | -0.31 | -0.18 | -0.65 |
| sue_announce | mimic_ew | 1.39 | 1.28 | 0.84 | 0.98 |
| sue_announce | top_ew | -0.05 | -0.17 | -0.40 | -0.63 |

### 7.5 Bağımlı iki değişkenli sıralama (tema skoru terciliyle kontrol)

| Faktör | Ufuk | Ort. fark | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.66% | 1.67 |
| asset_growth | 63 | 1.87% | 2.10 |
| asset_growth | 126 | 4.12% | 2.27 |
| capex_at | 21 | 0.55% | 1.68 |
| capex_at | 63 | 1.94% | 2.23 |
| capex_at | 126 | 3.91% | 2.11 |
| cop_at | 21 | -0.02% | -0.04 |
| cop_at | 63 | -0.52% | -0.39 |
| cop_at | 126 | -1.50% | -0.54 |
| dist_52w_high | 21 | -0.12% | -0.18 |
| dist_52w_high | 63 | -0.50% | -0.34 |
| dist_52w_high | 126 | -0.55% | -0.19 |
| ear_3d | 21 | 0.30% | 1.15 |
| ear_3d | 63 | 0.41% | 0.78 |
| ear_3d | 126 | 1.28% | 1.34 |
| ebit_ev | 21 | -0.39% | -0.87 |
| ebit_ev | 63 | -1.43% | -1.30 |
| ebit_ev | 126 | -2.74% | -1.26 |
| gross_profitability | 21 | 0.10% | 0.31 |
| gross_profitability | 63 | 0.03% | 0.04 |
| gross_profitability | 126 | 1.21% | 0.71 |
| idio_vol_60d | 21 | -0.42% | -0.58 |
| idio_vol_60d | 63 | -1.26% | -0.70 |
| idio_vol_60d | 126 | -1.81% | -0.50 |
| max_ret_21d | 21 | -0.39% | -0.64 |
| max_ret_21d | 63 | -0.89% | -0.61 |
| max_ret_21d | 126 | -1.57% | -0.55 |
| mom_12_1 | 21 | 0.17% | 0.33 |
| mom_12_1 | 63 | 0.66% | 0.57 |
| mom_12_1 | 126 | 1.20% | 0.47 |
| net_debt_ebitda | 21 | 0.05% | 0.11 |
| net_debt_ebitda | 63 | -0.44% | -0.41 |
| net_debt_ebitda | 126 | -0.59% | -0.27 |
| ocf_ev | 21 | 0.55% | 0.97 |
| ocf_ev | 63 | 1.00% | 0.71 |
| ocf_ev | 126 | 1.61% | 0.54 |
| oil_beta_trend | 21 | 0.39% | 0.75 |
| oil_beta_trend | 63 | 0.16% | 0.12 |
| oil_beta_trend | 126 | 1.29% | 0.57 |
| share_issuance | 21 | -0.10% | -0.37 |
| share_issuance | 63 | -0.18% | -0.26 |
| share_issuance | 126 | 0.13% | 0.08 |
| sue_announce | 21 | 0.43% | 1.35 |
| sue_announce | 63 | 1.12% | 1.61 |
| sue_announce | 126 | 1.85% | 1.46 |

### 7.6 Fama-MacBeth (tek faktör + β, ln(MktCap); NW t)

| Faktör | Ufuk | OLS rank-normal t | OLS ham t | WLS √MktCap t | 1 std etkisi | Ort. R² |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 1.99 | 1.43 | 1.56 | 0.25% | 17.79% |
| asset_growth | 63 | 1.87 | 1.46 | 1.61 | 0.56% | 15.87% |
| asset_growth | 126 | 1.65 | 1.31 | 1.43 | 1.06% | 15.61% |
| capex_at | 21 | 0.96 | 0.29 | 1.10 | 0.13% | 18.07% |
| capex_at | 63 | 1.42 | 0.89 | 1.38 | 0.54% | 16.21% |
| capex_at | 126 | 1.34 | 1.01 | 1.22 | 1.10% | 15.95% |
| cash_runway_years | 21 | -0.67 | -1.04 | -1.34 | -1.19% | 28.14% |
| cash_runway_years | 63 | -1.70 | -2.91 | -2.70 | -4.13% | 25.22% |
| cash_runway_years | 126 | -8.59 | -2.81 | -8.95 | -9.58% | 29.46% |
| cop_at | 21 | -0.03 | 0.07 | 0.35 | -0.00% | 19.31% |
| cop_at | 63 | -0.78 | -0.94 | -0.35 | -0.28% | 17.86% |
| cop_at | 126 | -1.00 | -1.30 | -0.66 | -0.68% | 17.25% |
| dist_52w_high | 21 | 0.63 | 0.98 | 0.91 | 0.16% | 19.30% |
| dist_52w_high | 63 | 0.34 | 0.62 | 0.93 | 0.19% | 17.45% |
| dist_52w_high | 126 | 0.07 | 0.48 | 0.51 | 0.07% | 16.07% |
| ear_3d | 21 | 0.70 | 0.76 | 0.49 | 0.08% | 17.87% |
| ear_3d | 63 | 0.79 | 0.69 | 0.96 | 0.20% | 16.14% |
| ear_3d | 126 | 1.00 | 1.06 | 1.39 | 0.43% | 15.35% |
| ebit_ev | 21 | -0.08 | 0.08 | 0.40 | -0.01% | 20.10% |
| ebit_ev | 63 | -0.39 | -0.26 | -0.11 | -0.15% | 18.99% |
| ebit_ev | 126 | -0.44 | -0.66 | -0.10 | -0.31% | 18.70% |
| gross_profitability | 21 | 0.41 | -0.98 | -0.13 | 0.05% | 16.69% |
| gross_profitability | 63 | -0.22 | -1.17 | -0.61 | -0.08% | 15.66% |
| gross_profitability | 126 | -0.25 | -1.33 | -0.65 | -0.18% | 14.66% |
| idio_vol_60d | 21 | -0.61 | -1.00 | -0.20 | -0.18% | 19.24% |
| idio_vol_60d | 63 | -1.04 | -1.22 | -0.64 | -0.80% | 17.18% |
| idio_vol_60d | 126 | -1.05 | -1.18 | -0.75 | -1.37% | 16.04% |
| max_ret_21d | 21 | -0.15 | -1.08 | 0.07 | -0.03% | 18.28% |
| max_ret_21d | 63 | -0.49 | -0.95 | 0.01 | -0.21% | 15.98% |
| max_ret_21d | 126 | -1.31 | -1.42 | -0.99 | -0.93% | 15.14% |
| mom_12_1 | 21 | 1.40 | 2.16 | 1.52 | 0.30% | 20.34% |
| mom_12_1 | 63 | 1.88 | 1.99 | 2.25 | 0.95% | 18.19% |
| mom_12_1 | 126 | 1.57 | 1.83 | 1.88 | 1.47% | 17.13% |
| net_debt_ebitda | 21 | 0.50 | 1.05 | 0.53 | 0.06% | 19.42% |
| net_debt_ebitda | 63 | 0.40 | 0.95 | -0.04 | 0.13% | 18.12% |
| net_debt_ebitda | 126 | 0.58 | 0.63 | -0.16 | 0.33% | 17.76% |
| ocf_ev | 21 | 0.84 | 1.20 | 1.29 | 0.14% | 20.21% |
| ocf_ev | 63 | 0.38 | 0.59 | 0.76 | 0.16% | 18.60% |
| ocf_ev | 126 | 0.22 | 0.24 | 0.65 | 0.19% | 18.28% |
| oil_beta_trend | 21 | -0.24 | 0.05 | 0.25 | -0.06% | 15.75% |
| oil_beta_trend | 63 | -0.71 | -0.32 | -0.53 | -0.39% | 15.83% |
| oil_beta_trend | 126 | -0.32 | 0.06 | -0.28 | -0.32% | 15.96% |
| share_issuance | 21 | 0.73 | 0.34 | 0.94 | 0.08% | 17.95% |
| share_issuance | 63 | 0.65 | 0.02 | 0.98 | 0.17% | 15.84% |
| share_issuance | 126 | 0.58 | 0.04 | 0.88 | 0.31% | 15.49% |
| sue_announce | 21 | 1.58 | 1.45 | 2.03 | 0.16% | 20.12% |
| sue_announce | 63 | 1.56 | 1.59 | 2.14 | 0.37% | 18.18% |
| sue_announce | 126 | 1.57 | 1.73 | 2.19 | 0.70% | 17.13% |

Tüm faktörlü model (kapsama ≥ %50, eksiksiz satırlar):

| Ufuk | Faktör | Katsayı | NW t | Ort. düz. R² |
|---|---|---|---|---|
| 21 | asset_growth | -0.43% | -1.26 | 42.91% |
| 21 | capex_at | 0.56% | 1.09 | 42.91% |
| 21 | cash_runway_years | 0.87% | 1.21 | 42.91% |
| 21 | cop_at | -0.78% | -1.84 | 42.91% |
| 21 | dist_52w_high | 0.48% | 0.62 | 42.91% |
| 21 | droe | -0.25% | -0.48 | 42.91% |
| 21 | ear_3d | -0.20% | -0.57 | 42.91% |
| 21 | ebit_ev | 0.31% | 0.74 | 42.91% |
| 21 | idio_vol_60d | -1.03% | -1.02 | 42.91% |
| 21 | max_ret_21d | 0.52% | 0.75 | 42.91% |
| 21 | mom_12_1 | 0.43% | 0.75 | 42.91% |
| 21 | net_debt_ebitda | 0.30% | 0.82 | 42.91% |
| 21 | ocf_ev | 0.36% | 0.71 | 42.91% |
| 21 | oil_beta_trend | -0.99% | -1.26 | 42.91% |
| 21 | profitable_growth | -0.34% | -0.78 | 42.91% |
| 21 | share_issuance | -0.01% | -0.03 | 42.91% |
| 21 | sue | 0.02% | 0.03 | 42.91% |
| 21 | sue_announce | -0.11% | -0.32 | 42.91% |
| 63 | asset_growth | -0.34% | -0.56 | 35.08% |
| 63 | capex_at | 1.95% | 1.78 | 35.08% |
| 63 | cash_runway_years | 1.93% | 1.39 | 35.08% |
| 63 | cop_at | -0.83% | -0.68 | 35.08% |
| 63 | dist_52w_high | 0.11% | 0.11 | 35.08% |
| 63 | droe | -0.64% | -0.60 | 35.08% |
| 63 | ear_3d | -1.19% | -1.78 | 35.08% |
| 63 | ebit_ev | 1.23% | 1.55 | 35.08% |
| 63 | idio_vol_60d | -0.92% | -0.59 | 35.08% |
| 63 | max_ret_21d | 0.36% | 0.27 | 35.08% |
| 63 | mom_12_1 | 0.42% | 0.28 | 35.08% |
| 63 | net_debt_ebitda | 0.35% | 0.55 | 35.08% |
| 63 | ocf_ev | 0.07% | 0.05 | 35.08% |
| 63 | oil_beta_trend | -2.47% | -1.34 | 35.08% |
| 63 | profitable_growth | -1.40% | -1.26 | 35.08% |
| 63 | share_issuance | 0.64% | 0.86 | 35.08% |
| 63 | sue | 0.29% | 0.22 | 35.08% |
| 63 | sue_announce | -0.06% | -0.10 | 35.08% |
| 126 | asset_growth | -1.27% | -0.85 | 33.35% |
| 126 | capex_at | 2.49% | 1.75 | 33.35% |
| 126 | cash_runway_years | 3.03% | 1.38 | 33.35% |
| 126 | cop_at | -0.83% | -0.37 | 33.35% |
| 126 | dist_52w_high | 0.19% | 0.15 | 33.35% |
| 126 | droe | 0.66% | 0.39 | 33.35% |
| 126 | ear_3d | -2.21% | -1.86 | 33.35% |
| 126 | ebit_ev | 0.47% | 0.40 | 33.35% |
| 126 | idio_vol_60d | -0.47% | -0.16 | 33.35% |
| 126 | max_ret_21d | 1.55% | 0.92 | 33.35% |
| 126 | mom_12_1 | -0.64% | -0.31 | 33.35% |
| 126 | net_debt_ebitda | 2.24% | 2.97 | 33.35% |
| 126 | ocf_ev | -0.83% | -0.46 | 33.35% |
| 126 | oil_beta_trend | -4.27% | -1.92 | 33.35% |
| 126 | profitable_growth | -2.85% | -1.68 | 33.35% |
| 126 | share_issuance | 2.00% | 1.32 | 33.35% |
| 126 | sue | 0.18% | 0.09 | 33.35% |
| 126 | sue_announce | -1.42% | -1.68 | 33.35% |

### 7.1 Tanımlayıcı istatistikler (winsorize %0,5/%99,5; aylık değerlerin zaman ortalaması)

| Faktör | Ort. | Std | Çarp. | Bas. | P5 | Medyan | P95 | n | Ort. kayması |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.127 | 0.338 | 3.70 | 19.93 | -0.132 | 0.055 | 0.638 | 137 | 0.17 |
| capex_at | 0.080 | 0.064 | 1.70 | 4.33 | 0.007 | 0.068 | 0.204 | 128 | 0.27 |
| cash_runway_years | 6.696 | 4.406 | -0.66 | -1.45 | 0.053 | 10.000 | 10.000 | 136 | 0.11 |
| cop_at | 0.096 | 0.072 | 0.53 | 5.53 | 0.003 | 0.082 | 0.219 | 136 | 0.18 |
| dist_52w_high | -0.193 | 0.158 | -1.19 | 1.29 | -0.501 | -0.151 | -0.024 | 138 | 0.47 |
| droe | -0.003 | 0.126 | -0.63 | 14.25 | -0.148 | -0.000 | 0.139 | 123 | 0.29 |
| ear_3d | 0.002 | 0.066 | 0.18 | 3.15 | -0.099 | 0.002 | 0.106 | 128 | 0.13 |
| ebit_ev | 0.052 | 0.206 | -0.99 | 18.90 | -0.107 | 0.052 | 0.170 | 121 | 0.31 |
| gross_profitability | 0.173 | 0.177 | 0.10 | 7.96 | 0.019 | 0.149 | 0.449 | 65 | 0.22 |
| idio_vol_60d | 0.357 | 0.244 | 1.55 | 5.01 | 0.156 | 0.314 | 0.700 | 138 | 0.49 |
| max_ret_21d | 0.049 | 0.035 | 2.21 | 7.67 | 0.017 | 0.040 | 0.113 | 138 | 0.59 |
| mom_12_1 | 0.203 | 0.733 | 2.25 | 14.66 | -0.349 | 0.088 | 0.973 | 138 | 0.54 |
| net_debt_ebitda | 3.820 | 4.740 | 2.42 | 13.33 | -0.876 | 3.334 | 9.656 | 109 | 0.18 |
| ocf_ev | 0.104 | 0.088 | 1.31 | 6.97 | 0.006 | 0.084 | 0.253 | 136 | 0.20 |
| oil_beta_trend | -0.025 | 0.379 | -0.30 | 7.68 | -0.434 | -0.025 | 0.402 | 87 | 1.21 |
| profitable_growth | 1.009 | 0.405 | 0.07 | -0.62 | 0.365 | 1.000 | 1.674 | 119 | 0.06 |
| share_issuance | 0.046 | 0.180 | 2.70 | 18.10 | -0.061 | 0.005 | 0.301 | 129 | 0.12 |
| sue | 0.109 | 1.072 | 0.05 | 0.42 | -1.659 | 0.079 | 1.872 | 132 | 0.29 |
| sue_announce | 0.199 | 1.159 | 0.21 | 0.27 | -1.562 | 0.154 | 2.079 | 80 | 0.30 |

### 7.2 Korelasyon ve çoklu doğrusallık

Tam matris (alt üçgen Pearson, üst üçgen Spearman): `corr.csv`. |ρ| > 0,7 çiftleri:

| A | B | Pearson | Spearman | Not |
|---|---|---|---|---|
| droe | sue | 0.50 | 0.81 | Spearman >> Pearson: doğrusal olmayan monoton ilişki |
| idio_vol_60d | max_ret_21d | 0.76 | 0.82 |  |

VIF > 5: `capex_at` (6.7), `cop_at` (6.0), `dist_52w_high` (6.7), `droe` (5.8), `idio_vol_60d` (11.1), `max_ret_21d` (6.9), `mom_12_1` (5.3), `ocf_ev` (6.4), `oil_beta_trend` (6.5), `sue` (8.1), `sue_announce` (5.4)

Ortogonalize (tema skoru + alt tema kuklaları sonrası artık) IC:

| Faktör | Ufuk | Artık IC | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.019 | 1.97 |
| asset_growth | 63 | 0.032 | 2.46 |
| asset_growth | 126 | 0.051 | 2.97 |
| capex_at | 21 | 0.011 | 1.07 |
| capex_at | 63 | 0.016 | 1.03 |
| capex_at | 126 | 0.030 | 1.26 |
| cash_runway_years | 21 | -0.124 | -1.23 |
| cash_runway_years | 63 | -0.160 | -4.42 |
| cash_runway_years | 126 | -0.231 | -4.59 |
| cop_at | 21 | -0.017 | -1.55 |
| cop_at | 63 | -0.029 | -1.82 |
| cop_at | 126 | -0.044 | -1.77 |
| dist_52w_high | 21 | 0.018 | 1.27 |
| dist_52w_high | 63 | 0.033 | 1.57 |
| dist_52w_high | 126 | 0.040 | 1.37 |
| ear_3d | 21 | 0.017 | 2.02 |
| ear_3d | 63 | 0.016 | 1.68 |
| ear_3d | 126 | 0.016 | 1.14 |
| ebit_ev | 21 | -0.014 | -1.10 |
| ebit_ev | 63 | -0.023 | -1.35 |
| ebit_ev | 126 | -0.026 | -1.19 |
| gross_profitability | 21 | -0.010 | -0.73 |
| gross_profitability | 63 | -0.032 | -1.54 |
| gross_profitability | 126 | -0.035 | -1.25 |
| idio_vol_60d | 21 | 0.024 | 1.50 |
| idio_vol_60d | 63 | 0.038 | 1.76 |
| idio_vol_60d | 126 | 0.054 | 1.77 |
| max_ret_21d | 21 | 0.020 | 1.40 |
| max_ret_21d | 63 | 0.031 | 1.82 |
| max_ret_21d | 126 | 0.037 | 1.59 |
| mom_12_1 | 21 | 0.015 | 1.10 |
| mom_12_1 | 63 | 0.023 | 1.25 |
| mom_12_1 | 126 | 0.017 | 0.63 |
| net_debt_ebitda | 21 | -0.025 | -1.73 |
| net_debt_ebitda | 63 | -0.042 | -2.25 |
| net_debt_ebitda | 126 | -0.058 | -2.28 |
| ocf_ev | 21 | 0.001 | 0.06 |
| ocf_ev | 63 | -0.000 | -0.00 |
| ocf_ev | 126 | -0.002 | -0.07 |
| oil_beta_trend | 21 | 0.001 | 0.03 |
| oil_beta_trend | 63 | -0.019 | -0.60 |
| oil_beta_trend | 126 | -0.009 | -0.27 |
| share_issuance | 21 | 0.010 | 1.18 |
| share_issuance | 63 | 0.025 | 2.11 |
| share_issuance | 126 | 0.040 | 2.45 |
| sue_announce | 21 | 0.009 | 0.99 |
| sue_announce | 63 | 0.008 | 0.57 |
| sue_announce | 126 | 0.004 | 0.27 |

### 7.3 Süreklilik (ρτ, aylık kesitsel sıra korelasyonu)

| Faktör | τ=1 | τ=3 | τ=6 | τ=12 |
|---|---|---|---|---|
| asset_growth | 0.93 | 0.81 | 0.63 | 0.29 |
| capex_at | 0.99 | 0.96 | 0.92 | 0.83 |
| cash_runway_years | 0.95 | 0.86 | 0.76 | 0.60 |
| cop_at | 0.97 | 0.92 | 0.84 | 0.68 |
| dist_52w_high | 0.83 | 0.66 | 0.49 | 0.33 |
| droe | 0.74 | 0.27 | 0.17 | -0.25 |
| ear_3d | 0.64 | 0.00 | 0.03 | 0.01 |
| ebit_ev | 0.95 | 0.87 | 0.73 | 0.46 |
| gross_profitability | 0.99 | 0.96 | 0.92 | 0.84 |
| idio_vol_60d | 0.96 | 0.88 | 0.85 | 0.81 |
| max_ret_21d | 0.66 | 0.65 | 0.62 | 0.59 |
| mom_12_1 | 0.89 | 0.70 | 0.43 | 0.01 |
| net_debt_ebitda | 0.98 | 0.93 | 0.89 | 0.82 |
| ocf_ev | 0.97 | 0.91 | 0.81 | 0.64 |
| oil_beta_trend | 0.65 | 0.18 | 0.00 | -0.15 |
| profitable_growth | 0.96 | 0.89 | 0.74 | 0.45 |
| share_issuance | 0.94 | 0.84 | 0.69 | 0.42 |
| sue | 0.74 | 0.27 | 0.16 | -0.23 |
| sue_announce | 0.79 | 0.40 | 0.27 | -0.07 |

### 7.8 İstikrar (126 seans IC ortalaması) ve ekonomik gerekçe

| Faktör | 2011-07..2015-12 | 2016-01..2020-12 | 2021-01..2026-09 | bull | bear | vix_high | vix_low | Neden çalışmalı | Kaynak |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.029 | 0.034 | 0.128 | 0.062 | 0.103 | 0.103 | 0.027 | aşırı yatırım / q-teorisi (−) | Cooper, Gulen & Schill (2008); Hou, Xue & Zhang (2015) |
| capex_at | 0.032 | 0.061 | 0.035 | 0.035 | 0.120 | 0.048 | 0.037 | yatırım faktörü (−) | Titman, Wei & Xie (2004); Fama & French (2015) CMA |
| cash_runway_years | — | — | -0.311 | -0.311 | — | -0.113 | -0.508 | finansal kısıt / seyreltme riski | Hadlock & Pierce (2010) — tema uyarlaması |
| cop_at | -0.072 | -0.085 | 0.013 | -0.045 | -0.061 | -0.002 | -0.092 | kalite (tahakkuksuz kârlılık) | Ball, Gerakos, Linnainmaa & Nikolaev (2016) |
| dist_52w_high | 0.108 | 0.036 | 0.023 | 0.067 | -0.082 | -0.039 | 0.149 | davranışsal (çıpalama) | George & Hwang (2004) |
| ear_3d | 0.008 | 0.030 | 0.018 | 0.016 | 0.048 | 0.004 | 0.035 | davranışsal (duyuru getirisi sürüklenmesi) | Chan, Jegadeesh & Lakonishok (1996) |
| ebit_ev | 0.025 | -0.072 | -0.003 | -0.017 | -0.029 | -0.031 | -0.004 | değer (risk + davranışsal) | Loughran & Wellman (2011) |
| gross_profitability | 0.032 | -0.065 | -0.038 | -0.024 | -0.038 | -0.012 | -0.040 | risk/kalite | Novy-Marx (2013) |
| idio_vol_60d | 0.114 | 0.082 | 0.032 | 0.086 | -0.036 | -0.037 | 0.189 | sınırlı arbitraj / piyango tercihi (−) | Ang, Hodrick, Xing & Zhang (2006) |
| max_ret_21d | 0.090 | 0.061 | 0.014 | 0.060 | -0.010 | -0.032 | 0.142 | piyango tercihi (−) | Bali, Cakici & Whitelaw (2011) |
| mom_12_1 | 0.112 | -0.061 | 0.056 | 0.041 | -0.035 | 0.015 | 0.053 | davranışsal (yetersiz tepki) + risk | Jegadeesh & Titman (1993); Carhart (1997) |
| net_debt_ebitda | -0.053 | -0.075 | -0.033 | -0.055 | -0.032 | -0.031 | -0.076 | kaldıraç / sıkıntı riski (−) | Campbell, Hilscher & Szilagyi (2008) |
| ocf_ev | -0.018 | -0.014 | 0.058 | 0.013 | -0.009 | 0.053 | -0.034 | değer (nakit akışı) | Lakonishok, Shleifer & Vishny (1994) |
| oil_beta_trend | 0.007 | -0.085 | 0.031 | -0.018 | 0.006 | 0.038 | -0.071 | emtia risk primi + trend | Moskowitz, Ooi & Pedersen (2012) — tema uyarlaması |
| share_issuance | 0.021 | 0.012 | 0.088 | 0.043 | 0.029 | 0.036 | 0.048 | piyasa zamanlaması (−) | Pontiff & Woodgate (2008); Daniel & Titman (2006) |
| sue_announce | 0.082 | 0.001 | 0.005 | 0.040 | -0.094 | -0.003 | 0.059 | davranışsal (PEAD, duyuru tarihli) | Bernard & Thomas (1989); Livnat & Mendenhall (2006) |

## Dosyalar

Tüm tablolar (alt temalar dahil): `alphas.csv`, `corr.csv`, `counts.csv`, `decision.csv`, `dependent.csv`, `descriptive.csv`, `fm.csv`, `ic.csv`, `orth.csv`, `persistence.csv`, `redundant.csv`, `sorts.csv`, `stability.csv`, `vif.csv`
