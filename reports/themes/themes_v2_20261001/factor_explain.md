# Faktör açıklama raporu — themes_v1 (`themes_v2_20261001`)

Bu rapor **tanımlayıcıdır**; faktör seçimi veya ağırlık öğrenmesi için kullanılmaz (THEMES_SPEC §7.9).

- Ön kayıt: `research/preregistration/themes_v1.yaml`, SHA256 `62db03649c07ac71a4f5f95a0085f2a5c685bf57e0f2dc09e66b33b9f69bf6e5`
- Veri: 2011-07-29 → 2026-09-30, 183 ay; uygun satır 117307
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
| ai | 109.3 | 16 | 324 | 0 |
| biotech | 162.8 | 39 | 286 | 0 |
| cyber_cloud | 92.8 | 14 | 156 | 1 |
| defense_space | 56.6 | 35 | 77 | 0 |
| energy | 142.3 | 89 | 179 | 0 |
| robotics | 17.0 | 3 | 35 | 91 |
| semiconductors | 60.2 | 36 | 88 | 0 |

## §7.9 Karar tablosu (126 seans)

Çalışıyor = IC > 0 ve NW t ≥ 2 **ve** FM katsayısı aynı işaretli **ve** alt dönemlerin ≥ 2/3'ünde IC > 0 **ve** bağımlı sıralama farkı > 0. Çalışmayanlar bir sonraki sürümde gerekçeyle çıkarılabilir; sonuçlara bakıp yeni faktör eklenmez.

| Kapsam | Faktör | IC | NW t | IC>0,t≥2 | FM | Alt dönem | Bağımlı | Çalışıyor |
|---|---|---|---|---|---|---|---|---|
| havuz | asset_growth | 0.010 | 0.72 | ✘ | ✘ | ✔ | ✘ | ✘ |
| havuz | capex_at | -0.016 | -1.75 | ✘ | ✘ | ✘ | ✘ | ✘ |
| havuz | cash_runway_years | 0.013 | 0.74 | ✘ | ✘ | ✔ | ✘ | ✘ |
| havuz | cop_at | 0.000 | 0.01 | ✘ | ✘ | ✘ | ✘ | ✘ |
| havuz | dist_52w_high | 0.082 | 4.15 | ✔ | ✔ | ✔ | ✔ | ✔ |
| havuz | droe | 0.012 | 1.25 | ✘ | ✔ | ✔ | ✔ | ✘ |
| havuz | ear_3d | 0.008 | 1.02 | ✘ | ✔ | ✔ | ✔ | ✘ |
| havuz | ebit_ev | -0.018 | -0.54 | ✘ | ✔ | ✘ | ✘ | ✘ |
| havuz | gross_profitability | 0.006 | 0.45 | ✘ | ✔ | ✔ | ✘ | ✘ |
| havuz | idio_vol_60d | 0.097 | 4.10 | ✔ | ✔ | ✔ | ✘ | ✘ |
| havuz | max_ret_21d | 0.073 | 3.43 | ✔ | ✔ | ✔ | ✘ | ✘ |
| havuz | mom_12_1 | 0.027 | 1.71 | ✘ | ✔ | ✔ | ✔ | ✘ |
| havuz | net_debt_ebitda | -0.058 | -1.64 | ✘ | ✔ | ✘ | ✘ | ✘ |
| havuz | ocf_ev | 0.006 | 0.14 | ✘ | ✔ | ✘ | ✔ | ✘ |
| havuz | oil_beta_trend | -0.015 | -0.41 | ✘ | ✔ | ✔ | ✔ | ✘ |
| havuz | profitable_growth | 0.026 | 1.16 | ✘ | ✔ | ✔ | ✔ | ✘ |
| havuz | share_issuance | 0.059 | 3.92 | ✔ | ✔ | ✔ | ✘ | ✘ |
| havuz | sue | 0.020 | 1.84 | ✘ | ✔ | ✔ | ✔ | ✘ |
| havuz | sue_announce | 0.041 | 3.67 | ✔ | ✔ | ✔ | ✔ | ✔ |
| robotics | asset_growth | 0.086 | 2.11 | ✔ | ✔ | ✔ | ✔ | ✔ |
| robotics | capex_at | -0.105 | -2.57 | ✘ | ✔ | ✘ | ✘ | ✘ |
| robotics | cop_at | 0.018 | 0.44 | ✘ | ✘ | ✘ | ✔ | ✘ |
| robotics | dist_52w_high | 0.018 | 0.32 | ✘ | ✘ | ✘ | ✔ | ✘ |
| robotics | droe | 0.074 | 2.35 | ✔ | ✔ | ✔ | ✔ | ✔ |
| robotics | ear_3d | 0.018 | 0.58 | ✘ | ✘ | ✔ | ✔ | ✘ |
| robotics | gross_profitability | 0.010 | 0.19 | ✘ | ✘ | ✘ | ✔ | ✘ |
| robotics | idio_vol_60d | 0.016 | 0.30 | ✘ | ✘ | ✘ | ✘ | ✘ |
| robotics | max_ret_21d | 0.015 | 0.37 | ✘ | ✘ | ✘ | ✘ | ✘ |
| robotics | mom_12_1 | 0.039 | 0.76 | ✘ | ✔ | ✘ | ✔ | ✘ |
| robotics | profitable_growth | -0.109 | -2.19 | ✘ | ✔ | ✘ | ✘ | ✘ |
| robotics | share_issuance | 0.129 | 2.90 | ✔ | ✔ | ✔ | ✔ | ✔ |
| robotics | sue | 0.067 | 1.76 | ✘ | ✔ | ✔ | ✔ | ✘ |
| robotics | sue_announce | -0.001 | -0.01 | ✘ | ✔ | ✘ | ✘ | ✘ |
| biotech | asset_growth | 0.018 | 0.98 | ✘ | ✔ | ✔ | ✔ | ✘ |
| biotech | capex_at | -0.027 | -1.65 | ✘ | ✘ | ✘ | ✔ | ✘ |
| biotech | cash_runway_years | 0.015 | 0.85 | ✘ | ✘ | ✔ | ✘ | ✘ |
| biotech | cop_at | 0.005 | 0.22 | ✘ | ✘ | ✘ | ✘ | ✘ |
| biotech | dist_52w_high | 0.098 | 4.80 | ✔ | ✔ | ✔ | ✔ | ✔ |
| biotech | droe | -0.004 | -0.25 | ✘ | ✘ | ✘ | ✘ | ✘ |
| biotech | ear_3d | -0.002 | -0.25 | ✘ | ✔ | ✔ | ✔ | ✘ |
| biotech | gross_profitability | -0.010 | -0.35 | ✘ | ✔ | ✘ | ✘ | ✘ |
| biotech | idio_vol_60d | 0.128 | 5.12 | ✔ | ✔ | ✔ | ✔ | ✔ |
| biotech | max_ret_21d | 0.104 | 4.64 | ✔ | ✔ | ✔ | ✔ | ✔ |
| biotech | mom_12_1 | 0.005 | 0.26 | ✘ | ✔ | ✘ | ✔ | ✘ |
| biotech | share_issuance | 0.080 | 3.08 | ✔ | ✘ | ✔ | ✘ | ✘ |
| biotech | sue | 0.009 | 0.53 | ✘ | ✔ | ✔ | ✘ | ✘ |
| biotech | sue_announce | 0.070 | 3.19 | ✔ | ✔ | ✔ | ✔ | ✔ |
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
| asset_growth | 21 | 0.004 | 0.52 | 0.54 | 47.80% | 182 |
| asset_growth | 63 | 0.000 | 0.02 | 0.06 | 44.44% | 180 |
| asset_growth | 126 | 0.010 | 0.72 | 0.91 | 51.41% | 177 |
| capex_at | 21 | -0.006 | -1.32 | -1.38 | 48.90% | 182 |
| capex_at | 63 | -0.011 | -1.44 | -1.06 | 41.11% | 180 |
| capex_at | 126 | -0.016 | -1.75 | -0.85 | 40.11% | 177 |
| cash_runway_years | 21 | 0.009 | 1.01 | 1.06 | 57.47% | 174 |
| cash_runway_years | 63 | 0.009 | 0.72 | 0.16 | 52.91% | 172 |
| cash_runway_years | 126 | 0.013 | 0.74 | 0.51 | 52.66% | 169 |
| cop_at | 21 | 0.004 | 0.51 | 0.52 | 50.00% | 182 |
| cop_at | 63 | 0.001 | 0.08 | -0.51 | 48.89% | 180 |
| cop_at | 126 | 0.000 | 0.01 | -0.03 | 49.15% | 177 |
| dist_52w_high | 21 | 0.034 | 2.44 | 2.41 | 58.24% | 182 |
| dist_52w_high | 63 | 0.055 | 3.56 | 2.78 | 63.33% | 180 |
| dist_52w_high | 126 | 0.082 | 4.15 | 3.50 | 76.27% | 177 |
| droe | 21 | 0.007 | 1.22 | 1.31 | 54.40% | 182 |
| droe | 63 | 0.011 | 1.40 | 1.22 | 54.44% | 180 |
| droe | 126 | 0.012 | 1.25 | 1.50 | 54.80% | 177 |
| ear_3d | 21 | 0.003 | 0.61 | 0.57 | 46.70% | 182 |
| ear_3d | 63 | 0.001 | 0.13 | -0.36 | 51.11% | 180 |
| ear_3d | 126 | 0.008 | 1.02 | -0.08 | 55.93% | 177 |
| ebit_ev | 21 | 0.005 | 0.27 | 0.29 | 51.65% | 182 |
| ebit_ev | 63 | -0.013 | -0.50 | -0.78 | 48.33% | 180 |
| ebit_ev | 126 | -0.018 | -0.54 | -0.49 | 48.59% | 177 |
| gross_profitability | 21 | 0.008 | 1.22 | 1.26 | 57.69% | 182 |
| gross_profitability | 63 | 0.006 | 0.62 | 0.33 | 55.56% | 180 |
| gross_profitability | 126 | 0.006 | 0.45 | 0.60 | 54.24% | 177 |
| idio_vol_60d | 21 | 0.044 | 2.97 | 2.96 | 56.04% | 182 |
| idio_vol_60d | 63 | 0.067 | 3.79 | 2.97 | 63.89% | 180 |
| idio_vol_60d | 126 | 0.097 | 4.10 | 3.72 | 74.58% | 177 |
| max_ret_21d | 21 | 0.034 | 2.57 | 2.57 | 56.04% | 182 |
| max_ret_21d | 63 | 0.054 | 3.44 | 2.80 | 61.67% | 180 |
| max_ret_21d | 126 | 0.073 | 3.43 | 3.19 | 72.32% | 177 |
| mom_12_1 | 21 | 0.012 | 1.21 | 1.22 | 54.95% | 182 |
| mom_12_1 | 63 | 0.019 | 1.69 | 1.44 | 56.11% | 180 |
| mom_12_1 | 126 | 0.027 | 1.71 | 1.32 | 58.19% | 177 |
| net_debt_ebitda | 21 | -0.015 | -0.76 | -0.81 | 50.55% | 182 |
| net_debt_ebitda | 63 | -0.038 | -1.43 | -1.42 | 45.56% | 180 |
| net_debt_ebitda | 126 | -0.058 | -1.64 | -1.29 | 44.63% | 177 |
| ocf_ev | 21 | 0.012 | 0.58 | 0.62 | 48.35% | 182 |
| ocf_ev | 63 | 0.007 | 0.24 | -0.25 | 52.78% | 180 |
| ocf_ev | 126 | 0.006 | 0.14 | -0.09 | 55.37% | 177 |
| oil_beta_trend | 21 | 0.008 | 0.33 | 0.33 | 53.85% | 182 |
| oil_beta_trend | 63 | -0.019 | -0.58 | -0.02 | 47.78% | 180 |
| oil_beta_trend | 126 | -0.015 | -0.41 | -0.66 | 48.02% | 177 |
| profitable_growth | 21 | 0.013 | 1.47 | 1.49 | 54.40% | 182 |
| profitable_growth | 63 | 0.025 | 1.49 | 1.32 | 60.56% | 180 |
| profitable_growth | 126 | 0.026 | 1.16 | 1.03 | 58.76% | 177 |
| share_issuance | 21 | 0.028 | 3.13 | 3.20 | 54.40% | 182 |
| share_issuance | 63 | 0.041 | 3.58 | 2.26 | 53.89% | 180 |
| share_issuance | 126 | 0.059 | 3.92 | 2.81 | 67.23% | 177 |
| sue | 21 | 0.011 | 1.85 | 1.90 | 56.59% | 182 |
| sue | 63 | 0.012 | 1.48 | 1.18 | 54.44% | 180 |
| sue | 126 | 0.020 | 1.84 | 2.09 | 62.15% | 177 |
| sue_announce | 21 | 0.021 | 3.25 | 3.18 | 62.09% | 182 |
| sue_announce | 63 | 0.032 | 3.54 | 3.07 | 67.78% | 180 |
| sue_announce | 126 | 0.041 | 3.67 | 2.73 | 68.36% | 177 |

### 7.4 Tek değişkenli sıralama (EW; üst − alt = `mimic_`)

| Faktör | Ufuk | Port. | mimic EW | t | mimic VW | Üst − ort. | t | Monoton |
|---|---|---|---|---|---|---|---|---|
| asset_growth | 21 | 5 | 0.32% | 1.35 | 0.16% | 0.26% | 1.72 | ✘ |
| asset_growth | 63 | 5 | 0.43% | 0.65 | 0.04% | 0.35% | 0.99 | ✘ |
| asset_growth | 126 | 5 | 0.94% | 0.75 | 0.14% | 0.59% | 0.93 | ✘ |
| capex_at | 21 | 5 | 0.09% | 0.52 | -0.26% | -0.04% | -0.35 | ✘ |
| capex_at | 63 | 5 | 0.52% | 1.12 | 0.15% | 0.10% | 0.36 | ✘ |
| capex_at | 126 | 5 | 0.84% | 0.89 | 0.26% | 0.10% | 0.18 | ✘ |
| cash_runway_years | 21 | 5 | -0.94% | -1.86 | 0.08% | -0.12% | -0.44 | ✘ |
| cash_runway_years | 63 | 5 | -2.24% | -1.71 | 0.25% | -0.30% | -0.37 | ✘ |
| cash_runway_years | 126 | 5 | -2.53% | -1.14 | -1.02% | 0.07% | 0.05 | ✘ |
| cop_at | 21 | 5 | 0.02% | 0.10 | 1.06% | 0.06% | 0.67 | ✘ |
| cop_at | 63 | 5 | 0.04% | 0.08 | 3.27% | 0.15% | 0.64 | ✘ |
| cop_at | 126 | 5 | -0.09% | -0.08 | 5.29% | 0.17% | 0.38 | ✘ |
| dist_52w_high | 21 | 5 | 0.24% | 0.52 | 0.37% | -0.02% | -0.11 | ✘ |
| dist_52w_high | 63 | 5 | 0.73% | 0.73 | 1.21% | -0.08% | -0.21 | ✘ |
| dist_52w_high | 126 | 5 | 1.67% | 0.87 | 1.58% | 0.43% | 0.62 | ✘ |
| droe | 21 | 5 | 0.36% | 2.03 | 0.41% | 0.34% | 2.95 | ✘ |
| droe | 63 | 5 | 1.14% | 2.45 | 1.10% | 0.89% | 3.00 | ✘ |
| droe | 126 | 5 | 2.20% | 2.27 | 0.72% | 1.77% | 2.71 | ✘ |
| ear_3d | 21 | 5 | -0.09% | -0.49 | 0.10% | -0.01% | -0.08 | ✘ |
| ear_3d | 63 | 5 | -0.11% | -0.33 | 0.00% | 0.06% | 0.28 | ✘ |
| ear_3d | 126 | 5 | 1.18% | 2.05 | 2.24% | 0.76% | 1.59 | ✘ |
| ebit_ev | 21 | 5 | -0.23% | -0.41 | -0.23% | -0.03% | -0.08 | ✘ |
| ebit_ev | 63 | 5 | -1.61% | -1.14 | -1.43% | -0.96% | -1.31 | ✘ |
| ebit_ev | 126 | 5 | -3.66% | -1.40 | -3.38% | -2.07% | -1.50 | ✘ |
| gross_profitability | 21 | 5 | 0.10% | 0.51 | 0.30% | 0.09% | 0.79 | ✘ |
| gross_profitability | 63 | 5 | 0.04% | 0.07 | 0.79% | 0.16% | 0.50 | ✘ |
| gross_profitability | 126 | 5 | 0.00% | 0.00 | 2.55% | 0.21% | 0.31 | ✘ |
| idio_vol_60d | 21 | 5 | -0.13% | -0.25 | -0.02% | 0.06% | 0.24 | ✘ |
| idio_vol_60d | 63 | 5 | -0.66% | -0.55 | -0.68% | 0.03% | 0.06 | ✘ |
| idio_vol_60d | 126 | 5 | -0.47% | -0.20 | -1.81% | 0.01% | 0.01 | ✘ |
| max_ret_21d | 21 | 5 | -0.19% | -0.41 | -0.17% | 0.02% | 0.09 | ✘ |
| max_ret_21d | 63 | 5 | -0.79% | -0.74 | -0.48% | -0.14% | -0.26 | ✘ |
| max_ret_21d | 126 | 5 | -1.26% | -0.63 | -2.45% | -0.57% | -0.55 | ✘ |
| mom_12_1 | 21 | 5 | 0.41% | 1.27 | 0.10% | 0.14% | 0.73 | ✘ |
| mom_12_1 | 63 | 5 | 1.52% | 2.18 | 0.72% | 0.84% | 2.09 | ✔ |
| mom_12_1 | 126 | 5 | 2.74% | 2.02 | 2.64% | 1.55% | 2.20 | ✔ |
| net_debt_ebitda | 21 | 5 | 0.09% | 0.19 | 0.19% | 0.07% | 0.21 | ✘ |
| net_debt_ebitda | 63 | 5 | -0.20% | -0.18 | -0.37% | -0.17% | -0.23 | ✘ |
| net_debt_ebitda | 126 | 5 | -0.72% | -0.37 | -1.50% | -0.44% | -0.32 | ✘ |
| ocf_ev | 21 | 5 | 0.52% | 0.80 | 0.63% | 0.09% | 0.21 | ✘ |
| ocf_ev | 63 | 5 | 0.93% | 0.61 | 0.85% | -0.31% | -0.32 | ✘ |
| ocf_ev | 126 | 5 | 1.15% | 0.34 | 1.12% | -1.01% | -0.47 | ✘ |
| oil_beta_trend | 21 | 5 | 0.44% | 0.57 | 0.71% | 0.32% | 0.80 | ✘ |
| oil_beta_trend | 63 | 5 | -0.45% | -0.25 | 0.46% | 0.17% | 0.16 | ✘ |
| oil_beta_trend | 126 | 5 | 0.14% | 0.05 | 1.49% | 0.55% | 0.30 | ✘ |
| profitable_growth | 21 | 5 | 0.15% | 0.57 | 0.71% | 0.17% | 1.23 | ✘ |
| profitable_growth | 63 | 5 | 0.82% | 0.99 | 2.19% | 0.51% | 1.17 | ✘ |
| profitable_growth | 126 | 5 | 1.14% | 0.66 | 3.40% | 0.91% | 1.03 | ✘ |
| share_issuance | 21 | 5 | 0.10% | 0.32 | 0.15% | 0.09% | 0.66 | ✘ |
| share_issuance | 63 | 5 | -0.04% | -0.06 | 0.71% | 0.17% | 0.53 | ✘ |
| share_issuance | 126 | 5 | 0.14% | 0.10 | 3.32% | 0.35% | 0.59 | ✘ |
| sue | 21 | 5 | 0.21% | 1.23 | -0.22% | 0.14% | 1.36 | ✘ |
| sue | 63 | 5 | 0.63% | 1.35 | -0.50% | 0.32% | 1.26 | ✘ |
| sue | 126 | 5 | 1.72% | 1.87 | -0.40% | 1.07% | 2.15 | ✘ |
| sue_announce | 21 | 5 | 0.33% | 1.62 | 0.24% | 0.09% | 0.85 | ✘ |
| sue_announce | 63 | 5 | 1.19% | 2.61 | 1.21% | 0.19% | 0.77 | ✘ |
| sue_announce | 126 | 5 | 2.17% | 2.83 | 1.64% | 0.45% | 1.03 | ✘ |

### 7.4 Alfalar (21 seans, aylık; NW t)

Üst portföy RF üzeri; `mimic_ew` ham fark.

| Faktör | Seri | capm t | ff3 t | carhart4 t | ff5_mom t |
|---|---|---|---|---|---|
| asset_growth | mimic_ew | 1.51 | 1.57 | 1.87 | 1.67 |
| asset_growth | top_ew | 0.45 | 0.98 | 0.89 | 0.95 |
| capex_at | mimic_ew | 0.60 | 1.33 | 1.41 | 1.80 |
| capex_at | top_ew | -0.16 | 0.43 | 0.42 | 0.68 |
| cash_runway_years | mimic_ew | -1.53 | -1.85 | -1.71 | -1.55 |
| cash_runway_years | top_ew | -0.30 | 0.14 | -0.07 | 0.25 |
| cop_at | mimic_ew | 0.64 | 0.31 | 1.00 | 0.82 |
| cop_at | top_ew | 0.43 | 0.66 | 0.70 | 0.61 |
| dist_52w_high | mimic_ew | 1.97 | 1.65 | 1.18 | 0.97 |
| dist_52w_high | top_ew | 1.15 | 1.43 | 0.86 | 0.77 |
| droe | mimic_ew | 2.08 | 2.29 | 1.94 | 1.91 |
| droe | top_ew | 1.38 | 1.93 | 1.64 | 1.69 |
| ear_3d | mimic_ew | -0.67 | -0.54 | -0.84 | -0.88 |
| ear_3d | top_ew | -0.31 | 0.22 | -0.08 | 0.10 |
| ebit_ev | mimic_ew | -0.41 | -0.53 | -0.22 | -0.68 |
| ebit_ev | top_ew | -0.82 | -1.08 | -0.86 | -1.33 |
| gross_profitability | mimic_ew | 1.44 | 1.91 | 2.16 | 2.25 |
| gross_profitability | top_ew | 1.01 | 1.36 | 1.35 | 1.37 |
| idio_vol_60d | mimic_ew | 1.28 | 0.77 | 0.96 | 0.36 |
| idio_vol_60d | top_ew | 1.89 | 1.83 | 1.62 | 1.19 |
| max_ret_21d | mimic_ew | 0.96 | 0.31 | 0.62 | -0.04 |
| max_ret_21d | top_ew | 1.16 | 1.09 | 0.98 | 0.60 |
| mom_12_1 | mimic_ew | 1.32 | 1.29 | 0.13 | 0.37 |
| mom_12_1 | top_ew | 0.07 | 0.55 | -0.23 | 0.12 |
| net_debt_ebitda | mimic_ew | -0.99 | -1.00 | -1.06 | -1.30 |
| net_debt_ebitda | top_ew | -0.79 | -0.98 | -1.02 | -1.24 |
| ocf_ev | mimic_ew | -0.02 | -0.10 | 0.29 | -0.01 |
| ocf_ev | top_ew | -0.59 | -0.78 | -0.60 | -0.85 |
| oil_beta_trend | mimic_ew | 1.96 | 2.03 | 1.74 | 1.82 |
| oil_beta_trend | top_ew | 0.52 | 0.65 | 0.64 | 0.47 |
| profitable_growth | mimic_ew | 0.65 | 0.71 | 1.11 | 1.29 |
| profitable_growth | top_ew | 0.95 | 1.28 | 1.09 | 1.25 |
| share_issuance | mimic_ew | 1.52 | 0.94 | 1.31 | 0.76 |
| share_issuance | top_ew | 1.02 | 1.17 | 1.17 | 0.96 |
| sue | mimic_ew | 1.02 | 1.03 | 0.85 | 0.86 |
| sue | top_ew | 1.09 | 1.55 | 1.27 | 1.22 |
| sue_announce | mimic_ew | 2.12 | 2.08 | 1.66 | 1.77 |
| sue_announce | top_ew | 0.83 | 1.12 | 0.87 | 0.84 |

### 7.5 Bağımlı iki değişkenli sıralama (tema skoru terciliyle kontrol)

| Faktör | Ufuk | Ort. fark | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.10% | 0.55 |
| asset_growth | 63 | -0.03% | -0.05 |
| asset_growth | 126 | -0.21% | -0.24 |
| capex_at | 21 | 0.00% | 0.00 |
| capex_at | 63 | 0.16% | 0.48 |
| capex_at | 126 | -0.03% | -0.04 |
| cash_runway_years | 21 | -0.71% | -1.82 |
| cash_runway_years | 63 | -2.54% | -2.39 |
| cash_runway_years | 126 | -3.52% | -1.89 |
| cop_at | 21 | -0.00% | -0.01 |
| cop_at | 63 | -0.34% | -0.65 |
| cop_at | 126 | -0.83% | -0.73 |
| dist_52w_high | 21 | 0.28% | 1.06 |
| dist_52w_high | 63 | 0.63% | 1.12 |
| dist_52w_high | 126 | 1.33% | 1.24 |
| droe | 21 | 0.16% | 1.09 |
| droe | 63 | 0.56% | 1.39 |
| droe | 126 | 1.18% | 1.34 |
| ear_3d | 21 | -0.08% | -0.61 |
| ear_3d | 63 | -0.21% | -0.72 |
| ear_3d | 126 | 0.38% | 0.81 |
| ebit_ev | 21 | -0.24% | -0.55 |
| ebit_ev | 63 | -1.13% | -1.06 |
| ebit_ev | 126 | -2.33% | -1.12 |
| gross_profitability | 21 | 0.02% | 0.17 |
| gross_profitability | 63 | -0.11% | -0.31 |
| gross_profitability | 126 | -0.24% | -0.30 |
| idio_vol_60d | 21 | -0.06% | -0.19 |
| idio_vol_60d | 63 | -0.53% | -0.69 |
| idio_vol_60d | 126 | -0.72% | -0.49 |
| max_ret_21d | 21 | -0.16% | -0.55 |
| max_ret_21d | 63 | -0.69% | -1.02 |
| max_ret_21d | 126 | -1.21% | -0.91 |
| mom_12_1 | 21 | 0.38% | 1.68 |
| mom_12_1 | 63 | 1.15% | 2.40 |
| mom_12_1 | 126 | 2.07% | 2.41 |
| net_debt_ebitda | 21 | -0.07% | -0.14 |
| net_debt_ebitda | 63 | -0.51% | -0.45 |
| net_debt_ebitda | 126 | -0.95% | -0.42 |
| ocf_ev | 21 | 0.57% | 0.97 |
| ocf_ev | 63 | 1.19% | 0.85 |
| ocf_ev | 126 | 1.90% | 0.64 |
| oil_beta_trend | 21 | 0.37% | 0.70 |
| oil_beta_trend | 63 | 0.09% | 0.07 |
| oil_beta_trend | 126 | 1.04% | 0.46 |
| profitable_growth | 21 | -0.04% | -0.17 |
| profitable_growth | 63 | 0.07% | 0.11 |
| profitable_growth | 126 | 0.19% | 0.15 |
| share_issuance | 21 | -0.05% | -0.22 |
| share_issuance | 63 | -0.37% | -0.70 |
| share_issuance | 126 | -0.72% | -0.71 |
| sue | 21 | 0.16% | 1.10 |
| sue | 63 | 0.35% | 0.92 |
| sue | 126 | 1.26% | 1.36 |
| sue_announce | 21 | 0.14% | 1.06 |
| sue_announce | 63 | 0.53% | 1.82 |
| sue_announce | 126 | 1.33% | 2.39 |

### 7.6 Fama-MacBeth (tek faktör + β, ln(MktCap); NW t)

| Faktör | Ufuk | OLS rank-normal t | OLS ham t | WLS √MktCap t | 1 std etkisi | Ort. R² |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 0.79 | 0.05 | -0.28 | 0.06% | 6.08% |
| asset_growth | 63 | -0.02 | 0.07 | -0.66 | -0.00% | 4.78% |
| asset_growth | 126 | -0.06 | 0.40 | -0.29 | -0.02% | 4.18% |
| capex_at | 21 | 0.29 | 0.58 | -0.85 | 0.02% | 5.73% |
| capex_at | 63 | 1.01 | 1.09 | -0.58 | 0.16% | 4.42% |
| capex_at | 126 | 0.67 | 1.03 | -0.72 | 0.23% | 3.78% |
| cash_runway_years | 21 | -1.54 | -0.48 | 0.33 | -0.24% | 4.70% |
| cash_runway_years | 63 | -1.81 | -0.75 | 0.09 | -0.73% | 4.58% |
| cash_runway_years | 126 | -1.34 | -0.32 | 0.11 | -0.96% | 4.45% |
| cop_at | 21 | 0.28 | 0.20 | 2.26 | 0.02% | 7.50% |
| cop_at | 63 | -0.08 | -0.33 | 2.09 | -0.01% | 6.30% |
| cop_at | 126 | -0.30 | -0.61 | 1.67 | -0.12% | 5.58% |
| dist_52w_high | 21 | 1.37 | 1.82 | 1.38 | 0.16% | 6.50% |
| dist_52w_high | 63 | 2.30 | 2.72 | 2.14 | 0.55% | 4.91% |
| dist_52w_high | 126 | 2.72 | 2.97 | 2.87 | 1.13% | 4.04% |
| droe | 21 | 1.62 | 0.84 | 0.25 | 0.09% | 5.43% |
| droe | 63 | 2.32 | 1.55 | 1.00 | 0.31% | 4.91% |
| droe | 126 | 2.36 | 0.50 | 1.01 | 0.66% | 4.35% |
| ear_3d | 21 | -0.04 | -0.08 | 1.37 | -0.00% | 5.88% |
| ear_3d | 63 | -0.02 | -0.22 | 1.53 | -0.00% | 4.47% |
| ear_3d | 126 | 1.34 | 1.50 | 2.41 | 0.26% | 3.70% |
| ebit_ev | 21 | 0.11 | 0.32 | 0.57 | 0.02% | 21.00% |
| ebit_ev | 63 | -0.21 | -0.10 | 0.09 | -0.08% | 19.79% |
| ebit_ev | 126 | -0.30 | -0.64 | 0.08 | -0.20% | 19.73% |
| gross_profitability | 21 | 1.03 | 1.25 | 0.47 | 0.07% | 5.89% |
| gross_profitability | 63 | 0.77 | 0.97 | 0.58 | 0.14% | 5.05% |
| gross_profitability | 126 | 0.32 | 0.49 | 0.52 | 0.13% | 4.48% |
| idio_vol_60d | 21 | 0.31 | 0.17 | 0.71 | 0.04% | 6.18% |
| idio_vol_60d | 63 | 0.15 | 0.19 | 0.58 | 0.05% | 4.82% |
| idio_vol_60d | 126 | 0.81 | 1.08 | 1.09 | 0.45% | 4.08% |
| max_ret_21d | 21 | 0.44 | 0.32 | 1.07 | 0.04% | 5.88% |
| max_ret_21d | 63 | 0.14 | 0.03 | 0.61 | 0.03% | 4.55% |
| max_ret_21d | 126 | 0.21 | 0.82 | 0.31 | 0.08% | 3.85% |
| mom_12_1 | 21 | 2.22 | 1.41 | 2.73 | 0.19% | 6.32% |
| mom_12_1 | 63 | 3.25 | 2.59 | 3.77 | 0.61% | 4.75% |
| mom_12_1 | 126 | 3.23 | 2.77 | 3.96 | 1.10% | 4.02% |
| net_debt_ebitda | 21 | 0.04 | 0.72 | 0.24 | 0.00% | 20.30% |
| net_debt_ebitda | 63 | -0.20 | 0.50 | -0.48 | -0.06% | 18.78% |
| net_debt_ebitda | 126 | -0.25 | 0.04 | -0.75 | -0.11% | 18.72% |
| ocf_ev | 21 | 1.24 | 1.34 | 1.67 | 0.19% | 20.69% |
| ocf_ev | 63 | 0.81 | 0.68 | 1.12 | 0.32% | 19.20% |
| ocf_ev | 126 | 0.70 | 0.33 | 0.95 | 0.54% | 19.18% |
| oil_beta_trend | 21 | -0.11 | 0.21 | 0.36 | -0.03% | 15.78% |
| oil_beta_trend | 63 | -0.58 | -0.15 | -0.37 | -0.32% | 15.76% |
| oil_beta_trend | 126 | -0.23 | 0.21 | -0.21 | -0.23% | 15.91% |
| profitable_growth | 21 | 0.02 | 0.04 | 0.79 | 0.00% | 6.48% |
| profitable_growth | 63 | 0.61 | 0.67 | 1.04 | 0.16% | 5.97% |
| profitable_growth | 126 | 0.24 | 0.30 | 0.59 | 0.13% | 5.89% |
| share_issuance | 21 | 0.80 | 0.39 | 1.26 | 0.06% | 6.21% |
| share_issuance | 63 | 0.25 | -0.09 | 1.03 | 0.05% | 4.85% |
| share_issuance | 126 | 0.17 | 0.23 | 1.93 | 0.07% | 4.20% |
| sue | 21 | 2.07 | 1.57 | 0.00 | 0.11% | 5.79% |
| sue | 63 | 2.43 | 2.08 | 0.49 | 0.33% | 5.20% |
| sue | 126 | 2.85 | 2.67 | 0.80 | 0.84% | 4.64% |
| sue_announce | 21 | 2.57 | 2.26 | 3.24 | 0.13% | 7.34% |
| sue_announce | 63 | 3.62 | 3.13 | 4.03 | 0.46% | 5.74% |
| sue_announce | 126 | 3.96 | 3.48 | 3.92 | 0.87% | 5.07% |

Tüm faktörlü model (kapsama ≥ %50, eksiksiz satırlar):

| Ufuk | Faktör | Katsayı | NW t | Ort. düz. R² |
|---|---|---|---|---|
| 21 | asset_growth | -0.22% | -2.58 | 13.27% |
| 21 | capex_at | 0.02% | 0.27 | 13.27% |
| 21 | cash_runway_years | 0.51% | 1.93 | 13.27% |
| 21 | cop_at | 0.10% | 0.70 | 13.27% |
| 21 | dist_52w_high | -0.20% | -1.68 | 13.27% |
| 21 | droe | 0.00% | 0.01 | 13.27% |
| 21 | ear_3d | -0.00% | -0.05 | 13.27% |
| 21 | ebit_ev | 0.01% | 0.07 | 13.27% |
| 21 | gross_profitability | -0.05% | -0.49 | 13.27% |
| 21 | idio_vol_60d | 0.23% | 2.25 | 13.27% |
| 21 | max_ret_21d | 0.06% | 0.68 | 13.27% |
| 21 | mom_12_1 | 0.19% | 1.72 | 13.27% |
| 21 | net_debt_ebitda | -0.08% | -0.91 | 13.27% |
| 21 | ocf_ev | -0.07% | -0.47 | 13.27% |
| 21 | profitable_growth | -0.13% | -1.30 | 13.27% |
| 21 | share_issuance | 0.01% | 0.06 | 13.27% |
| 21 | sue | 0.05% | 0.47 | 13.27% |
| 21 | sue_announce | -0.07% | -0.90 | 13.27% |
| 63 | asset_growth | -0.46% | -2.35 | 12.07% |
| 63 | capex_at | 0.11% | 0.49 | 12.07% |
| 63 | cash_runway_years | 1.21% | 2.05 | 12.07% |
| 63 | cop_at | 0.10% | 0.27 | 12.07% |
| 63 | dist_52w_high | -0.31% | -1.34 | 12.07% |
| 63 | droe | 0.12% | 0.41 | 12.07% |
| 63 | ear_3d | -0.17% | -0.89 | 12.07% |
| 63 | ebit_ev | -0.05% | -0.19 | 12.07% |
| 63 | gross_profitability | -0.12% | -0.45 | 12.07% |
| 63 | idio_vol_60d | 0.21% | 0.95 | 12.07% |
| 63 | max_ret_21d | 0.19% | 1.21 | 12.07% |
| 63 | mom_12_1 | 0.51% | 1.83 | 12.07% |
| 63 | net_debt_ebitda | -0.31% | -1.41 | 12.07% |
| 63 | ocf_ev | -0.09% | -0.24 | 12.07% |
| 63 | profitable_growth | -0.31% | -1.29 | 12.07% |
| 63 | share_issuance | 0.04% | 0.19 | 12.07% |
| 63 | sue | -0.01% | -0.04 | 12.07% |
| 63 | sue_announce | -0.14% | -0.71 | 12.07% |
| 126 | asset_growth | -0.63% | -2.06 | 11.66% |
| 126 | capex_at | 0.08% | 0.15 | 11.66% |
| 126 | cash_runway_years | 1.83% | 1.92 | 11.66% |
| 126 | cop_at | 0.17% | 0.22 | 11.66% |
| 126 | dist_52w_high | -0.39% | -0.89 | 11.66% |
| 126 | droe | 0.12% | 0.26 | 11.66% |
| 126 | ear_3d | 0.02% | 0.07 | 11.66% |
| 126 | ebit_ev | -0.18% | -0.43 | 11.66% |
| 126 | gross_profitability | -0.52% | -1.06 | 11.66% |
| 126 | idio_vol_60d | 0.22% | 0.59 | 11.66% |
| 126 | max_ret_21d | -0.11% | -0.47 | 11.66% |
| 126 | mom_12_1 | 1.02% | 2.02 | 11.66% |
| 126 | net_debt_ebitda | -0.27% | -0.67 | 11.66% |
| 126 | ocf_ev | 0.06% | 0.09 | 11.66% |
| 126 | profitable_growth | -0.84% | -1.83 | 11.66% |
| 126 | share_issuance | -0.05% | -0.13 | 11.66% |
| 126 | sue | 0.31% | 0.71 | 11.66% |
| 126 | sue_announce | -0.11% | -0.32 | 11.66% |

### 7.1 Tanımlayıcı istatistikler (winsorize %0,5/%99,5; aylık değerlerin zaman ortalaması)

| Faktör | Ort. | Std | Çarp. | Bas. | P5 | Medyan | P95 | n | Ort. kayması |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.220 | 0.536 | 3.94 | 20.47 | -0.165 | 0.075 | 1.063 | 558 | 0.14 |
| capex_at | 0.041 | 0.047 | 2.38 | 7.13 | 0.002 | 0.024 | 0.134 | 533 | 0.22 |
| cash_runway_years | 7.780 | 3.670 | -1.19 | -0.37 | 0.363 | 10.000 | 10.000 | 559 | 0.06 |
| cop_at | 0.041 | 0.178 | -2.11 | 6.61 | -0.328 | 0.078 | 0.230 | 559 | 0.15 |
| dist_52w_high | -0.210 | 0.170 | -1.07 | 0.73 | -0.552 | -0.164 | -0.019 | 566 | 0.37 |
| droe | -0.002 | 0.169 | -0.12 | 16.86 | -0.179 | -0.000 | 0.169 | 512 | 0.08 |
| ear_3d | 0.005 | 0.091 | 0.23 | 2.25 | -0.138 | 0.003 | 0.157 | 522 | 0.06 |
| ebit_ev | 0.003 | 0.137 | -2.32 | 14.07 | -0.208 | 0.030 | 0.134 | 524 | 0.25 |
| gross_profitability | 0.292 | 0.184 | 1.04 | 2.01 | 0.049 | 0.267 | 0.629 | 400 | 0.12 |
| idio_vol_60d | 0.389 | 0.236 | 2.10 | 7.05 | 0.154 | 0.329 | 0.816 | 566 | 0.40 |
| max_ret_21d | 0.059 | 0.052 | 3.31 | 16.32 | 0.018 | 0.045 | 0.145 | 567 | 0.34 |
| mom_12_1 | 0.255 | 0.679 | 2.73 | 13.43 | -0.409 | 0.124 | 1.319 | 566 | 0.36 |
| net_debt_ebitda | 1.387 | 6.295 | 1.08 | 12.23 | -6.571 | 1.255 | 8.279 | 368 | 0.08 |
| ocf_ev | 0.043 | 0.115 | -1.04 | 9.70 | -0.129 | 0.051 | 0.190 | 558 | 0.22 |
| oil_beta_trend | -0.025 | 0.379 | -0.36 | 8.19 | -0.441 | -0.024 | 0.406 | 89 | 1.22 |
| profitable_growth | 1.056 | 0.403 | -0.03 | -0.55 | 0.374 | 1.052 | 1.725 | 421 | 0.04 |
| share_issuance | 0.049 | 0.188 | 3.26 | 25.61 | -0.065 | 0.010 | 0.283 | 523 | 0.11 |
| sue | 0.063 | 1.272 | -0.10 | 0.58 | -2.149 | 0.065 | 2.159 | 545 | 0.13 |
| sue_announce | 0.574 | 1.457 | 0.54 | 0.83 | -1.617 | 0.431 | 3.081 | 292 | 0.16 |

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
| asset_growth | 21 | 0.003 | 0.57 |
| asset_growth | 63 | -0.002 | -0.21 |
| asset_growth | 126 | 0.002 | 0.17 |
| capex_at | 21 | -0.002 | -0.31 |
| capex_at | 63 | -0.002 | -0.29 |
| capex_at | 126 | -0.004 | -0.36 |
| cash_runway_years | 21 | -0.016 | -1.75 |
| cash_runway_years | 63 | -0.027 | -2.13 |
| cash_runway_years | 126 | -0.028 | -1.53 |
| cop_at | 21 | -0.006 | -1.25 |
| cop_at | 63 | -0.012 | -1.45 |
| cop_at | 126 | -0.016 | -1.28 |
| dist_52w_high | 21 | 0.013 | 1.57 |
| dist_52w_high | 63 | 0.025 | 2.53 |
| dist_52w_high | 126 | 0.038 | 2.84 |
| droe | 21 | 0.002 | 0.37 |
| droe | 63 | 0.002 | 0.19 |
| droe | 126 | -0.007 | -0.65 |
| ear_3d | 21 | 0.001 | 0.28 |
| ear_3d | 63 | -0.001 | -0.21 |
| ear_3d | 126 | 0.004 | 0.57 |
| ebit_ev | 21 | -0.011 | -0.88 |
| ebit_ev | 63 | -0.020 | -1.14 |
| ebit_ev | 126 | -0.026 | -1.22 |
| gross_profitability | 21 | -0.000 | -0.07 |
| gross_profitability | 63 | -0.007 | -0.79 |
| gross_profitability | 126 | -0.008 | -0.63 |
| idio_vol_60d | 21 | 0.021 | 2.24 |
| idio_vol_60d | 63 | 0.034 | 2.94 |
| idio_vol_60d | 126 | 0.053 | 3.63 |
| max_ret_21d | 21 | 0.014 | 1.70 |
| max_ret_21d | 63 | 0.023 | 2.40 |
| max_ret_21d | 126 | 0.031 | 2.47 |
| mom_12_1 | 21 | 0.004 | 0.48 |
| mom_12_1 | 63 | 0.003 | 0.35 |
| mom_12_1 | 126 | -0.000 | -0.04 |
| net_debt_ebitda | 21 | -0.025 | -1.80 |
| net_debt_ebitda | 63 | -0.041 | -2.28 |
| net_debt_ebitda | 126 | -0.055 | -2.36 |
| ocf_ev | 21 | -0.000 | -0.01 |
| ocf_ev | 63 | -0.001 | -0.03 |
| ocf_ev | 126 | -0.004 | -0.13 |
| oil_beta_trend | 21 | 0.001 | 0.06 |
| oil_beta_trend | 63 | -0.016 | -0.50 |
| oil_beta_trend | 126 | -0.010 | -0.28 |
| profitable_growth | 21 | -0.000 | -0.00 |
| profitable_growth | 63 | 0.004 | 0.26 |
| profitable_growth | 126 | 0.000 | 0.01 |
| share_issuance | 21 | 0.011 | 1.48 |
| share_issuance | 63 | 0.016 | 1.68 |
| share_issuance | 126 | 0.024 | 2.00 |
| sue | 21 | 0.000 | 0.03 |
| sue | 63 | -0.007 | -0.79 |
| sue | 126 | -0.014 | -1.31 |
| sue_announce | 21 | 0.011 | 2.08 |
| sue_announce | 63 | 0.017 | 2.59 |
| sue_announce | 126 | 0.018 | 2.27 |

### 7.3 Süreklilik (ρτ, aylık kesitsel sıra korelasyonu)

| Faktör | τ=1 | τ=3 | τ=6 | τ=12 |
|---|---|---|---|---|
| asset_growth | 0.92 | 0.77 | 0.58 | 0.22 |
| capex_at | 0.99 | 0.97 | 0.94 | 0.88 |
| cash_runway_years | 0.96 | 0.88 | 0.81 | 0.68 |
| cop_at | 0.98 | 0.94 | 0.89 | 0.77 |
| dist_52w_high | 0.83 | 0.64 | 0.47 | 0.27 |
| droe | 0.78 | 0.36 | 0.21 | -0.21 |
| ear_3d | 0.65 | -0.01 | 0.01 | -0.01 |
| ebit_ev | 0.98 | 0.94 | 0.86 | 0.72 |
| gross_profitability | 0.99 | 0.97 | 0.94 | 0.89 |
| idio_vol_60d | 0.93 | 0.80 | 0.78 | 0.74 |
| max_ret_21d | 0.54 | 0.54 | 0.52 | 0.50 |
| mom_12_1 | 0.89 | 0.70 | 0.44 | 0.01 |
| net_debt_ebitda | 0.99 | 0.97 | 0.94 | 0.89 |
| ocf_ev | 0.98 | 0.94 | 0.88 | 0.76 |
| oil_beta_trend | 0.65 | 0.18 | 0.01 | -0.14 |
| profitable_growth | 0.97 | 0.90 | 0.79 | 0.56 |
| share_issuance | 0.96 | 0.88 | 0.78 | 0.58 |
| sue | 0.80 | 0.42 | 0.30 | -0.06 |
| sue_announce | 0.86 | 0.59 | 0.45 | 0.17 |

### 7.8 İstikrar (126 seans IC ortalaması) ve ekonomik gerekçe

| Faktör | 2011-07..2015-12 | 2016-01..2020-12 | 2021-01..2026-09 | bull | bear | vix_high | vix_low | Neden çalışmalı | Kaynak |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.017 | -0.013 | 0.026 | 0.009 | 0.013 | 0.021 | -0.002 | aşırı yatırım / q-teorisi (−) | Cooper, Gulen & Schill (2008); Hou, Xue & Zhang (2015) |
| capex_at | -0.017 | -0.005 | -0.027 | -0.022 | 0.038 | 0.000 | -0.034 | yatırım faktörü (−) | Titman, Wei & Xie (2004); Fama & French (2015) CMA |
| cash_runway_years | -0.029 | 0.054 | 0.005 | 0.015 | -0.002 | 0.002 | 0.024 | finansal kısıt / seyreltme riski | Hadlock & Pierce (2010) — tema uyarlaması |
| cop_at | -0.032 | -0.039 | 0.064 | 0.002 | -0.017 | 0.010 | -0.010 | kalite (tahakkuksuz kârlılık) | Ball, Gerakos, Linnainmaa & Nikolaev (2016) |
| dist_52w_high | 0.068 | 0.056 | 0.119 | 0.085 | 0.057 | 0.054 | 0.112 | davranışsal (çıpalama) | George & Hwang (2004) |
| droe | 0.016 | 0.006 | 0.015 | 0.010 | 0.036 | 0.014 | 0.010 | temel momentum | Hou, Xue & Zhang (2015) q-faktör ROE |
| ear_3d | 0.002 | 0.010 | 0.011 | 0.012 | -0.031 | -0.002 | 0.019 | davranışsal (duyuru getirisi sürüklenmesi) | Chan, Jegadeesh & Lakonishok (1996) |
| ebit_ev | 0.030 | -0.072 | -0.009 | -0.016 | -0.039 | -0.030 | -0.006 | değer (risk + davranışsal) | Loughran & Wellman (2011) |
| gross_profitability | 0.000 | 0.006 | 0.011 | 0.006 | 0.012 | 0.006 | 0.006 | risk/kalite | Novy-Marx (2013) |
| idio_vol_60d | 0.095 | 0.080 | 0.115 | 0.096 | 0.106 | 0.067 | 0.128 | sınırlı arbitraj / piyango tercihi (−) | Ang, Hodrick, Xing & Zhang (2006) |
| max_ret_21d | 0.077 | 0.054 | 0.087 | 0.071 | 0.093 | 0.052 | 0.094 | piyango tercihi (−) | Bali, Cakici & Whitelaw (2011) |
| mom_12_1 | 0.024 | 0.001 | 0.054 | 0.022 | 0.067 | 0.032 | 0.021 | davranışsal (yetersiz tepki) + risk | Jegadeesh & Titman (1993); Carhart (1997) |
| net_debt_ebitda | -0.057 | -0.104 | -0.016 | -0.058 | -0.060 | -0.032 | -0.085 | kaldıraç / sıkıntı riski (−) | Campbell, Hilscher & Szilagyi (2008) |
| ocf_ev | -0.022 | -0.017 | 0.053 | 0.009 | -0.018 | 0.054 | -0.044 | değer (nakit akışı) | Lakonishok, Shleifer & Vishny (1994) |
| oil_beta_trend | 0.009 | -0.085 | 0.030 | -0.018 | 0.008 | 0.039 | -0.072 | emtia risk primi + trend | Moskowitz, Ooi & Pedersen (2012) — tema uyarlaması |
| profitable_growth | 0.039 | 0.043 | -0.000 | 0.026 | 0.033 | 0.021 | 0.032 | kalite + büyüme | Mohanram (2005) GSCORE ruhunda |
| share_issuance | 0.046 | 0.030 | 0.098 | 0.061 | 0.040 | 0.054 | 0.063 | piyasa zamanlaması (−) | Pontiff & Woodgate (2008); Daniel & Titman (2006) |
| sue | 0.012 | -0.007 | 0.054 | 0.019 | 0.030 | 0.023 | 0.018 | davranışsal (kazanç sonrası sürüklenme) | Bernard & Thomas (1989) |
| sue_announce | 0.034 | 0.043 | 0.046 | 0.044 | 0.009 | 0.027 | 0.055 | davranışsal (PEAD, duyuru tarihli) | Bernard & Thomas (1989); Livnat & Mendenhall (2006) |

## Kapsam: robotics

### 7.7 Rank IC

| Faktör | Ufuk | IC | NW t | Örtüşmesiz t | IC>0 oranı | Ay |
|---|---|---|---|---|---|---|
| asset_growth | 21 | -0.001 | -0.03 | -0.02 | 55.06% | 89 |
| asset_growth | 63 | 0.031 | 1.03 | 1.24 | 56.32% | 87 |
| asset_growth | 126 | 0.086 | 2.11 | 2.67 | 75.00% | 84 |
| capex_at | 21 | -0.049 | -2.06 | -2.03 | 42.17% | 83 |
| capex_at | 63 | -0.068 | -2.00 | -2.04 | 37.04% | 81 |
| capex_at | 126 | -0.105 | -2.57 | -2.54 | 33.33% | 78 |
| cop_at | 21 | 0.026 | 0.98 | 0.95 | 56.10% | 82 |
| cop_at | 63 | 0.033 | 0.88 | 0.53 | 55.00% | 80 |
| cop_at | 126 | 0.018 | 0.44 | -0.07 | 49.35% | 77 |
| dist_52w_high | 21 | 0.021 | 0.69 | 0.71 | 52.75% | 91 |
| dist_52w_high | 63 | 0.008 | 0.21 | 0.15 | 53.93% | 89 |
| dist_52w_high | 126 | 0.018 | 0.32 | 0.10 | 56.98% | 86 |
| droe | 21 | 0.028 | 1.12 | 1.07 | 53.41% | 88 |
| droe | 63 | 0.049 | 1.83 | 1.45 | 60.47% | 86 |
| droe | 126 | 0.074 | 2.35 | 0.24 | 65.06% | 83 |
| ear_3d | 21 | 0.010 | 0.38 | 0.39 | 57.95% | 88 |
| ear_3d | 63 | -0.006 | -0.18 | -0.20 | 50.00% | 86 |
| ear_3d | 126 | 0.018 | 0.58 | 0.67 | 50.60% | 83 |
| gross_profitability | 21 | 0.026 | 0.96 | 0.94 | 55.95% | 84 |
| gross_profitability | 63 | -0.002 | -0.06 | -0.13 | 53.66% | 82 |
| gross_profitability | 126 | 0.010 | 0.19 | 0.19 | 50.63% | 79 |
| idio_vol_60d | 21 | 0.028 | 0.98 | 1.02 | 52.75% | 91 |
| idio_vol_60d | 63 | 0.031 | 0.81 | 1.55 | 58.43% | 89 |
| idio_vol_60d | 126 | 0.016 | 0.30 | -0.04 | 55.81% | 86 |
| max_ret_21d | 21 | 0.020 | 0.76 | 0.75 | 51.65% | 91 |
| max_ret_21d | 63 | 0.039 | 1.22 | 1.90 | 57.30% | 89 |
| max_ret_21d | 126 | 0.015 | 0.37 | -0.34 | 53.49% | 86 |
| mom_12_1 | 21 | 0.034 | 0.99 | 1.09 | 57.14% | 91 |
| mom_12_1 | 63 | 0.039 | 0.93 | 0.37 | 58.43% | 89 |
| mom_12_1 | 126 | 0.039 | 0.76 | 1.31 | 56.98% | 86 |
| profitable_growth | 21 | -0.053 | -1.86 | -1.91 | 42.68% | 82 |
| profitable_growth | 63 | -0.066 | -1.74 | -1.77 | 41.25% | 80 |
| profitable_growth | 126 | -0.109 | -2.19 | -1.58 | 36.36% | 77 |
| share_issuance | 21 | 0.088 | 3.01 | 2.95 | 61.80% | 89 |
| share_issuance | 63 | 0.121 | 3.48 | 2.73 | 71.26% | 87 |
| share_issuance | 126 | 0.129 | 2.90 | 1.40 | 69.05% | 84 |
| sue | 21 | 0.027 | 0.95 | 0.99 | 54.65% | 86 |
| sue | 63 | 0.039 | 1.20 | 0.28 | 57.14% | 84 |
| sue | 126 | 0.067 | 1.76 | 1.97 | 64.20% | 81 |
| sue_announce | 21 | 0.014 | 0.33 | 0.32 | 48.48% | 33 |
| sue_announce | 63 | -0.032 | -0.46 | -0.01 | 41.94% | 31 |
| sue_announce | 126 | -0.001 | -0.01 | -0.67 | 57.14% | 28 |

### 7.4 Tek değişkenli sıralama (EW; üst − alt = `mimic_`)

| Faktör | Ufuk | Port. | mimic EW | t | mimic VW | Üst − ort. | t | Monoton |
|---|---|---|---|---|---|---|---|---|
| asset_growth | 21 | 3 | 0.15% | 0.20 | -1.09% | 0.24% | 0.60 | ✘ |
| asset_growth | 63 | 3 | 1.17% | 0.74 | -3.85% | 0.69% | 0.79 | ✔ |
| asset_growth | 126 | 3 | 3.36% | 0.99 | -8.23% | 1.14% | 0.68 | ✔ |
| capex_at | 21 | 3 | -2.53% | -2.96 | -3.51% | -1.06% | -2.91 | ✘ |
| capex_at | 63 | 3 | -5.84% | -2.75 | -8.83% | -2.55% | -2.48 | ✘ |
| capex_at | 126 | 3 | -12.42% | -3.08 | -16.70% | -5.02% | -2.55 | ✘ |
| cop_at | 21 | 3 | 0.18% | 0.26 | 1.20% | -0.20% | -0.54 | ✘ |
| cop_at | 63 | 3 | 0.88% | 0.53 | 1.34% | -0.27% | -0.27 | ✘ |
| cop_at | 126 | 3 | 0.39% | 0.15 | -0.30% | -1.73% | -0.88 | ✘ |
| dist_52w_high | 21 | 3 | -0.62% | -0.78 | -2.35% | -0.54% | -1.41 | ✘ |
| dist_52w_high | 63 | 3 | -2.37% | -1.18 | -6.73% | -1.56% | -1.60 | ✘ |
| dist_52w_high | 126 | 3 | -4.62% | -1.11 | -13.13% | -2.42% | -1.29 | ✘ |
| droe | 21 | 3 | 0.70% | 0.89 | 1.14% | 0.31% | 0.76 | ✔ |
| droe | 63 | 3 | 1.68% | 1.02 | 0.65% | 1.26% | 1.52 | ✘ |
| droe | 126 | 3 | 5.89% | 2.61 | 5.51% | 4.95% | 3.79 | ✘ |
| ear_3d | 21 | 3 | -0.26% | -0.37 | -0.71% | 0.26% | 0.63 | ✘ |
| ear_3d | 63 | 3 | 1.05% | 0.63 | -0.84% | 1.38% | 1.62 | ✘ |
| ear_3d | 126 | 3 | -0.36% | -0.15 | 2.06% | 0.95% | 0.92 | ✘ |
| gross_profitability | 21 | 3 | -0.64% | -0.91 | -2.38% | -0.35% | -0.96 | ✘ |
| gross_profitability | 63 | 3 | -2.63% | -1.37 | -7.45% | -0.91% | -0.87 | ✘ |
| gross_profitability | 126 | 3 | -6.37% | -1.37 | -17.35% | -1.97% | -0.91 | ✘ |
| idio_vol_60d | 21 | 3 | -0.71% | -0.72 | -3.11% | -0.33% | -0.79 | ✘ |
| idio_vol_60d | 63 | 3 | -3.82% | -1.49 | -11.21% | -1.39% | -1.28 | ✘ |
| idio_vol_60d | 126 | 3 | -6.83% | -1.36 | -20.32% | -2.80% | -1.33 | ✘ |
| max_ret_21d | 21 | 3 | -0.78% | -0.87 | -3.07% | -0.44% | -0.97 | ✘ |
| max_ret_21d | 63 | 3 | -2.72% | -1.41 | -4.39% | -1.10% | -1.09 | ✘ |
| max_ret_21d | 126 | 3 | -4.84% | -1.41 | -13.87% | -2.59% | -1.41 | ✘ |
| mom_12_1 | 21 | 3 | 0.65% | 0.68 | 0.13% | 0.41% | 0.81 | ✔ |
| mom_12_1 | 63 | 3 | 1.24% | 0.53 | -1.02% | 1.27% | 1.05 | ✘ |
| mom_12_1 | 126 | 3 | 1.43% | 0.37 | 1.20% | 2.10% | 1.11 | ✘ |
| profitable_growth | 21 | 3 | -1.44% | -1.86 | -1.17% | -0.56% | -1.40 | ✘ |
| profitable_growth | 63 | 3 | -3.75% | -2.33 | -5.10% | -1.78% | -2.12 | ✘ |
| profitable_growth | 126 | 3 | -7.62% | -2.67 | -13.29% | -4.05% | -2.71 | ✘ |
| share_issuance | 21 | 3 | 0.77% | 0.78 | -1.00% | 0.28% | 0.73 | ✔ |
| share_issuance | 63 | 3 | 0.33% | 0.15 | -4.46% | -0.26% | -0.28 | ✘ |
| share_issuance | 126 | 3 | -1.60% | -0.33 | -12.21% | -1.33% | -0.64 | ✘ |
| sue | 21 | 3 | 0.31% | 0.46 | -0.11% | -0.29% | -0.75 | ✘ |
| sue | 63 | 3 | 1.26% | 0.78 | -0.33% | -0.27% | -0.30 | ✘ |
| sue | 126 | 3 | 5.09% | 2.14 | -1.66% | 1.57% | 1.09 | ✘ |
| sue_announce | 21 | 3 | -0.30% | -0.28 | -1.06% | -0.21% | -0.32 | ✘ |
| sue_announce | 63 | 3 | -1.78% | -0.65 | -5.36% | -1.42% | -0.93 | ✘ |
| sue_announce | 126 | 3 | -1.55% | -0.22 | -5.46% | -0.29% | -0.06 | ✘ |

### 7.4 Alfalar (21 seans, aylık; NW t)

Üst portföy RF üzeri; `mimic_ew` ham fark.

| Faktör | Seri | capm t | ff3 t | carhart4 t | ff5_mom t |
|---|---|---|---|---|---|
| asset_growth | mimic_ew | 0.26 | 0.03 | -0.04 | -0.11 |
| asset_growth | top_ew | 0.31 | 0.47 | -0.07 | -0.03 |
| capex_at | mimic_ew | -2.85 | -3.06 | -2.88 | -3.06 |
| capex_at | top_ew | -1.23 | -1.25 | -1.84 | -1.78 |
| cop_at | mimic_ew | 0.10 | -0.02 | 0.40 | 0.25 |
| cop_at | top_ew | -0.12 | 0.05 | -0.33 | -0.36 |
| dist_52w_high | mimic_ew | -0.66 | -0.93 | -1.01 | -1.33 |
| dist_52w_high | top_ew | -0.48 | -0.18 | -0.84 | -0.80 |
| droe | mimic_ew | 0.17 | 0.08 | 0.22 | -0.26 |
| droe | top_ew | 0.25 | 0.47 | 0.01 | -0.15 |
| ear_3d | mimic_ew | -0.83 | -0.77 | -0.96 | -1.46 |
| ear_3d | top_ew | 0.10 | 0.51 | -0.16 | -0.20 |
| gross_profitability | mimic_ew | -0.79 | -0.64 | -0.74 | -0.44 |
| gross_profitability | top_ew | -0.45 | -0.20 | -0.74 | -0.57 |
| idio_vol_60d | mimic_ew | -0.05 | -0.50 | -0.34 | -0.72 |
| idio_vol_60d | top_ew | 0.12 | 0.22 | -0.12 | -0.21 |
| max_ret_21d | mimic_ew | 0.03 | -0.22 | 0.28 | 0.11 |
| max_ret_21d | top_ew | 0.06 | 0.21 | -0.12 | -0.23 |
| mom_12_1 | mimic_ew | 0.20 | 0.27 | -0.04 | -0.19 |
| mom_12_1 | top_ew | 0.25 | 0.62 | -0.02 | 0.02 |
| profitable_growth | mimic_ew | -1.78 | -1.74 | -1.49 | -1.34 |
| profitable_growth | top_ew | -0.48 | -0.40 | -0.75 | -0.58 |
| share_issuance | mimic_ew | 1.18 | 0.76 | 1.22 | 0.87 |
| share_issuance | top_ew | 0.53 | 0.75 | 0.37 | 0.35 |
| sue | mimic_ew | -0.20 | -0.33 | 0.14 | -0.34 |
| sue | top_ew | -0.22 | 0.01 | -0.33 | -0.47 |
| sue_announce | mimic_ew | -0.78 | -0.41 | -0.39 | -0.12 |
| sue_announce | top_ew | -0.98 | -0.68 | -1.50 | -1.03 |

### 7.5 Bağımlı iki değişkenli sıralama (tema skoru terciliyle kontrol)

| Faktör | Ufuk | Ort. fark | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.26% | 0.31 |
| asset_growth | 63 | 1.33% | 0.78 |
| asset_growth | 126 | 3.75% | 1.11 |
| capex_at | 21 | -2.32% | -2.99 |
| capex_at | 63 | -3.89% | -2.02 |
| capex_at | 126 | -8.21% | -2.27 |
| cop_at | 21 | 0.65% | 0.97 |
| cop_at | 63 | 1.28% | 0.91 |
| cop_at | 126 | 1.58% | 0.62 |
| dist_52w_high | 21 | 0.56% | 0.65 |
| dist_52w_high | 63 | 1.67% | 0.79 |
| dist_52w_high | 126 | 1.91% | 0.48 |
| droe | 21 | 0.82% | 1.14 |
| droe | 63 | 0.90% | 0.50 |
| droe | 126 | 3.35% | 1.71 |
| ear_3d | 21 | -0.27% | -0.33 |
| ear_3d | 63 | 1.81% | 1.17 |
| ear_3d | 126 | 2.18% | 1.25 |
| gross_profitability | 21 | 0.65% | 0.90 |
| gross_profitability | 63 | 1.44% | 0.88 |
| gross_profitability | 126 | 3.29% | 1.01 |
| idio_vol_60d | 21 | -0.05% | -0.05 |
| idio_vol_60d | 63 | -2.80% | -1.22 |
| idio_vol_60d | 126 | -5.59% | -1.17 |
| max_ret_21d | 21 | -0.26% | -0.30 |
| max_ret_21d | 63 | -0.66% | -0.32 |
| max_ret_21d | 126 | -4.43% | -1.32 |
| mom_12_1 | 21 | 2.75% | 3.04 |
| mom_12_1 | 63 | 5.16% | 2.66 |
| mom_12_1 | 126 | 8.10% | 2.52 |
| profitable_growth | 21 | -0.91% | -1.26 |
| profitable_growth | 63 | -2.87% | -1.53 |
| profitable_growth | 126 | -4.79% | -1.40 |
| share_issuance | 21 | 1.60% | 1.58 |
| share_issuance | 63 | 3.12% | 1.47 |
| share_issuance | 126 | 4.24% | 1.13 |
| sue | 21 | 0.83% | 1.38 |
| sue | 63 | 1.46% | 1.18 |
| sue | 126 | 5.19% | 2.21 |
| sue_announce | 21 | -2.15% | -1.03 |
| sue_announce | 63 | -5.87% | -2.00 |
| sue_announce | 126 | -11.94% | -3.03 |

### 7.6 Fama-MacBeth (tek faktör + β, ln(MktCap); NW t)

| Faktör | Ufuk | OLS rank-normal t | OLS ham t | WLS √MktCap t | 1 std etkisi | Ort. R² |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 0.26 | 0.54 | 0.71 | 0.09% | 22.32% |
| asset_growth | 63 | 1.08 | 1.46 | 0.82 | 0.74% | 20.04% |
| asset_growth | 126 | 1.33 | 1.50 | 1.19 | 1.96% | 19.06% |
| capex_at | 21 | -2.29 | -1.36 | -2.91 | -0.87% | 21.18% |
| capex_at | 63 | -2.47 | -1.56 | -3.06 | -2.09% | 20.70% |
| capex_at | 126 | -2.50 | -1.68 | -3.06 | -4.43% | 20.33% |
| cop_at | 21 | -0.02 | -0.20 | -0.62 | -0.01% | 23.77% |
| cop_at | 63 | -0.37 | -0.40 | -0.79 | -0.38% | 20.94% |
| cop_at | 126 | -0.50 | -0.52 | -0.93 | -1.37% | 21.03% |
| dist_52w_high | 21 | -0.14 | 0.12 | -2.19 | -0.06% | 21.99% |
| dist_52w_high | 63 | -0.64 | 0.17 | -2.21 | -0.79% | 22.24% |
| dist_52w_high | 126 | -0.80 | 0.00 | -2.06 | -1.88% | 21.33% |
| droe | 21 | 0.22 | 0.47 | -0.04 | 0.06% | 22.78% |
| droe | 63 | 0.01 | 0.36 | -0.38 | 0.01% | 19.66% |
| droe | 126 | 1.56 | 0.98 | 0.55 | 1.40% | 18.31% |
| ear_3d | 21 | 0.03 | 0.07 | -0.45 | 0.01% | 22.32% |
| ear_3d | 63 | 0.62 | 0.79 | -0.23 | 0.46% | 21.09% |
| ear_3d | 126 | -0.68 | 0.49 | -0.44 | -0.76% | 20.43% |
| gross_profitability | 21 | -0.32 | 0.14 | -1.33 | -0.11% | 24.43% |
| gross_profitability | 63 | -0.54 | -0.18 | -1.37 | -0.57% | 21.33% |
| gross_profitability | 126 | -0.54 | -0.33 | -1.15 | -1.53% | 21.85% |
| idio_vol_60d | 21 | -1.21 | -0.89 | -1.85 | -0.57% | 21.71% |
| idio_vol_60d | 63 | -1.70 | -0.71 | -2.15 | -2.06% | 21.42% |
| idio_vol_60d | 126 | -1.33 | -0.56 | -1.75 | -4.00% | 21.97% |
| max_ret_21d | 21 | -1.35 | -1.33 | -2.78 | -0.65% | 20.78% |
| max_ret_21d | 63 | -1.79 | -1.68 | -2.25 | -1.98% | 20.59% |
| max_ret_21d | 126 | -1.81 | -1.31 | -2.01 | -3.54% | 20.27% |
| mom_12_1 | 21 | 0.98 | 1.56 | 0.34 | 0.39% | 23.24% |
| mom_12_1 | 63 | 0.80 | 1.42 | 0.41 | 0.78% | 21.92% |
| mom_12_1 | 126 | 0.43 | 1.32 | 0.16 | 0.78% | 21.81% |
| profitable_growth | 21 | -2.97 | -2.73 | -2.64 | -1.03% | 23.19% |
| profitable_growth | 63 | -3.29 | -3.23 | -2.61 | -2.58% | 21.08% |
| profitable_growth | 126 | -3.56 | -3.79 | -2.22 | -5.99% | 22.01% |
| share_issuance | 21 | 1.46 | 0.52 | 0.28 | 0.53% | 23.14% |
| share_issuance | 63 | 1.11 | 0.35 | 0.11 | 0.98% | 20.91% |
| share_issuance | 126 | 0.68 | -0.07 | -0.10 | 1.32% | 20.01% |
| sue | 21 | 0.62 | 0.07 | -0.29 | 0.16% | 23.67% |
| sue | 63 | 0.74 | 0.33 | -0.02 | 0.49% | 19.76% |
| sue | 126 | 1.37 | 1.36 | -0.04 | 1.56% | 19.59% |
| sue_announce | 21 | -0.64 | -0.64 | -0.56 | -0.33% | 22.37% |
| sue_announce | 63 | -1.18 | -0.83 | -1.01 | -1.39% | 24.19% |
| sue_announce | 126 | -1.12 | -1.25 | -0.98 | -3.43% | 24.97% |

### 7.1 Tanımlayıcı istatistikler (winsorize %0,5/%99,5; aylık değerlerin zaman ortalaması)

| Faktör | Ort. | Std | Çarp. | Bas. | P5 | Medyan | P95 | n | Ort. kayması |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.166 | 0.356 | 1.68 | 4.94 | -0.079 | 0.067 | 0.792 | 18 | 0.42 |
| capex_at | 0.025 | 0.017 | 1.28 | 2.05 | 0.009 | 0.020 | 0.056 | 17 | 0.25 |
| cash_runway_years | 9.273 | 1.747 | -1.78 | 4.45 | 5.734 | 10.000 | 10.000 | 18 | 0.39 |
| cop_at | 0.076 | 0.094 | -0.82 | 2.06 | -0.085 | 0.088 | 0.176 | 18 | 0.44 |
| dist_52w_high | -0.183 | 0.130 | -0.95 | 0.82 | -0.403 | -0.155 | -0.040 | 18 | 0.73 |
| droe | 0.004 | 0.081 | 0.05 | 6.14 | -0.081 | -0.000 | 0.098 | 18 | 0.31 |
| ear_3d | 0.010 | 0.095 | 0.40 | 0.96 | -0.110 | 0.001 | 0.152 | 17 | 0.26 |
| ebit_ev | -0.004 | 0.191 | -1.22 | 6.88 | -0.085 | 0.026 | 0.070 | 17 | 0.65 |
| gross_profitability | 0.276 | 0.109 | -0.14 | -0.19 | 0.125 | 0.283 | 0.429 | 17 | 0.47 |
| idio_vol_60d | 0.344 | 0.165 | 1.24 | 1.95 | 0.180 | 0.301 | 0.618 | 18 | 0.70 |
| max_ret_21d | 0.055 | 0.038 | 1.60 | 3.47 | 0.023 | 0.044 | 0.117 | 18 | 0.60 |
| mom_12_1 | 0.257 | 0.503 | 1.07 | 3.43 | -0.220 | 0.157 | 0.923 | 18 | 0.57 |
| net_debt_ebitda | 0.608 | 5.060 | -0.35 | 2.57 | -5.537 | 0.574 | 6.952 | 14 | 0.29 |
| ocf_ev | 0.045 | 0.111 | -0.14 | 6.43 | -0.038 | 0.040 | 0.090 | 18 | 0.55 |
| profitable_growth | 1.132 | 0.414 | -0.01 | -0.35 | 0.554 | 1.137 | 1.711 | 15 | 0.22 |
| share_issuance | 0.031 | 0.124 | 1.22 | 7.48 | -0.041 | 0.005 | 0.195 | 18 | 0.40 |
| sue | 0.268 | 1.329 | 0.29 | 0.93 | -1.515 | 0.188 | 2.236 | 18 | 0.33 |
| sue_announce | 0.558 | 1.313 | 0.40 | 0.48 | -1.031 | 0.486 | 2.448 | 11 | 0.34 |

### 7.2 Korelasyon ve çoklu doğrusallık

Tam matris (alt üçgen Pearson, üst üçgen Spearman): `corr.csv`. |ρ| > 0,7 çiftleri:

| A | B | Pearson | Spearman | Not |
|---|---|---|---|---|
| cash_runway_years | cop_at | 0.73 | 0.58 |  |
| droe | sue | 0.52 | 0.73 | Spearman >> Pearson: doğrusal olmayan monoton ilişki |
| ebit_ev | ocf_ev | 0.76 | 0.74 |  |

VIF > 5: yok

Ortogonalize (tema skoru + alt tema kuklaları sonrası artık) IC:

| Faktör | Ufuk | Artık IC | NW t |
|---|---|---|---|
| asset_growth | 21 | -0.008 | -0.39 |
| asset_growth | 63 | 0.014 | 0.57 |
| asset_growth | 126 | 0.059 | 1.92 |
| capex_at | 21 | -0.043 | -1.73 |
| capex_at | 63 | -0.055 | -1.73 |
| capex_at | 126 | -0.090 | -2.13 |
| cop_at | 21 | 0.031 | 1.38 |
| cop_at | 63 | 0.042 | 1.37 |
| cop_at | 126 | 0.059 | 1.94 |
| dist_52w_high | 21 | 0.002 | 0.07 |
| dist_52w_high | 63 | -0.020 | -0.51 |
| dist_52w_high | 126 | -0.010 | -0.18 |
| droe | 21 | 0.032 | 1.49 |
| droe | 63 | 0.050 | 1.92 |
| droe | 126 | 0.056 | 1.50 |
| ear_3d | 21 | 0.006 | 0.22 |
| ear_3d | 63 | -0.015 | -0.45 |
| ear_3d | 126 | 0.010 | 0.31 |
| gross_profitability | 21 | 0.033 | 1.25 |
| gross_profitability | 63 | -0.002 | -0.07 |
| gross_profitability | 126 | 0.032 | 0.62 |
| idio_vol_60d | 21 | -0.027 | -1.03 |
| idio_vol_60d | 63 | -0.057 | -1.42 |
| idio_vol_60d | 126 | -0.058 | -1.02 |
| max_ret_21d | 21 | -0.005 | -0.22 |
| max_ret_21d | 63 | -0.008 | -0.29 |
| max_ret_21d | 126 | -0.029 | -0.71 |
| mom_12_1 | 21 | 0.029 | 0.86 |
| mom_12_1 | 63 | 0.011 | 0.26 |
| mom_12_1 | 126 | 0.007 | 0.14 |
| profitable_growth | 21 | -0.067 | -2.35 |
| profitable_growth | 63 | -0.098 | -2.57 |
| profitable_growth | 126 | -0.136 | -2.74 |
| share_issuance | 21 | 0.059 | 2.53 |
| share_issuance | 63 | 0.078 | 2.90 |
| share_issuance | 126 | 0.110 | 2.99 |
| sue | 21 | 0.014 | 0.69 |
| sue | 63 | 0.040 | 1.35 |
| sue | 126 | 0.059 | 1.46 |
| sue_announce | 21 | -0.016 | -0.42 |
| sue_announce | 63 | -0.034 | -0.69 |
| sue_announce | 126 | -0.029 | -0.66 |

### 7.3 Süreklilik (ρτ, aylık kesitsel sıra korelasyonu)

| Faktör | τ=1 | τ=3 | τ=6 | τ=12 |
|---|---|---|---|---|
| asset_growth | 0.91 | 0.77 | 0.57 | 0.21 |
| capex_at | 0.98 | 0.95 | 0.90 | 0.82 |
| cash_runway_years | 0.96 | — | — | — |
| cop_at | 0.98 | 0.93 | 0.86 | 0.71 |
| dist_52w_high | 0.79 | 0.59 | 0.43 | 0.31 |
| droe | 0.77 | 0.36 | 0.19 | -0.14 |
| ear_3d | 0.66 | -0.04 | 0.02 | -0.06 |
| ebit_ev | 0.97 | 0.95 | 0.90 | 0.81 |
| gross_profitability | 0.99 | 0.97 | 0.93 | 0.84 |
| idio_vol_60d | 0.87 | 0.69 | 0.66 | 0.61 |
| max_ret_21d | 0.42 | 0.42 | 0.38 | 0.32 |
| mom_12_1 | 0.86 | 0.67 | 0.40 | -0.00 |
| net_debt_ebitda | 0.98 | 0.93 | 0.87 | 0.74 |
| ocf_ev | 0.97 | 0.92 | 0.87 | 0.78 |
| profitable_growth | 0.94 | 0.83 | 0.65 | 0.33 |
| share_issuance | 0.96 | 0.90 | 0.77 | 0.55 |
| sue | 0.78 | 0.40 | 0.27 | -0.11 |
| sue_announce | 0.81 | 0.42 | 0.25 | -0.08 |

### 7.8 İstikrar (126 seans IC ortalaması) ve ekonomik gerekçe

| Faktör | 2011-07..2015-12 | 2016-01..2020-12 | 2021-01..2026-09 | bull | bear | vix_high | vix_low | Neden çalışmalı | Kaynak |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | — | 0.136 | 0.069 | 0.080 | 0.125 | 0.105 | 0.051 | aşırı yatırım / q-teorisi (−) | Cooper, Gulen & Schill (2008); Hou, Xue & Zhang (2015) |
| capex_at | — | -0.136 | -0.097 | -0.106 | -0.100 | -0.077 | -0.163 | yatırım faktörü (−) | Titman, Wei & Xie (2004); Fama & French (2015) CMA |
| cop_at | — | -0.192 | 0.065 | 0.011 | 0.054 | -0.008 | 0.074 | kalite (tahakkuksuz kârlılık) | Ball, Gerakos, Linnainmaa & Nikolaev (2016) |
| dist_52w_high | — | -0.264 | 0.122 | 0.009 | 0.075 | 0.003 | 0.045 | davranışsal (çıpalama) | George & Hwang (2004) |
| droe | — | 0.045 | 0.083 | 0.060 | 0.159 | 0.080 | 0.063 | temel momentum | Hou, Xue & Zhang (2015) q-faktör ROE |
| ear_3d | — | 0.012 | 0.019 | -0.004 | 0.144 | -0.018 | 0.083 | davranışsal (duyuru getirisi sürüklenmesi) | Chan, Jegadeesh & Lakonishok (1996) |
| gross_profitability | — | -0.174 | 0.057 | 0.004 | 0.043 | -0.043 | 0.119 | risk/kalite | Novy-Marx (2013) |
| idio_vol_60d | — | -0.221 | 0.103 | 0.006 | 0.075 | 0.033 | -0.015 | sınırlı arbitraj / piyango tercihi (−) | Ang, Hodrick, Xing & Zhang (2006) |
| max_ret_21d | — | -0.133 | 0.069 | 0.017 | 0.000 | 0.061 | -0.066 | piyango tercihi (−) | Bali, Cakici & Whitelaw (2011) |
| mom_12_1 | — | -0.087 | 0.085 | 0.026 | 0.118 | 0.028 | 0.057 | davranışsal (yetersiz tepki) + risk | Jegadeesh & Titman (1993); Carhart (1997) |
| profitable_growth | — | -0.123 | -0.106 | -0.134 | 0.026 | -0.089 | -0.155 | kalite + büyüme | Mohanram (2005) GSCORE ruhunda |
| share_issuance | — | 0.012 | 0.169 | 0.135 | 0.097 | 0.144 | 0.103 | piyasa zamanlaması (−) | Pontiff & Woodgate (2008); Daniel & Titman (2006) |
| sue | — | 0.002 | 0.086 | 0.044 | 0.200 | 0.088 | 0.026 | davranışsal (kazanç sonrası sürüklenme) | Bernard & Thomas (1989) |
| sue_announce | — | — | -0.001 | -0.007 | 0.150 | -0.014 | 0.013 | davranışsal (PEAD, duyuru tarihli) | Bernard & Thomas (1989); Livnat & Mendenhall (2006) |

## Kapsam: biotech

### 7.7 Rank IC

| Faktör | Ufuk | IC | NW t | Örtüşmesiz t | IC>0 oranı | Ay |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 0.010 | 1.09 | 1.11 | 50.00% | 182 |
| asset_growth | 63 | 0.007 | 0.53 | 0.26 | 50.56% | 180 |
| asset_growth | 126 | 0.018 | 0.98 | 1.24 | 50.28% | 177 |
| capex_at | 21 | -0.009 | -0.94 | -0.91 | 47.25% | 182 |
| capex_at | 63 | -0.009 | -0.75 | -0.38 | 46.11% | 180 |
| capex_at | 126 | -0.027 | -1.65 | -1.88 | 42.37% | 177 |
| cash_runway_years | 21 | 0.004 | 0.43 | 0.45 | 53.80% | 171 |
| cash_runway_years | 63 | 0.011 | 0.79 | -0.03 | 54.44% | 169 |
| cash_runway_years | 126 | 0.015 | 0.85 | 0.23 | 53.61% | 166 |
| cop_at | 21 | 0.009 | 0.71 | 0.74 | 51.65% | 182 |
| cop_at | 63 | -0.005 | -0.29 | -0.49 | 45.56% | 180 |
| cop_at | 126 | 0.005 | 0.22 | 0.05 | 50.28% | 177 |
| dist_52w_high | 21 | 0.041 | 2.85 | 2.74 | 58.24% | 182 |
| dist_52w_high | 63 | 0.069 | 3.86 | 3.84 | 63.33% | 180 |
| dist_52w_high | 126 | 0.098 | 4.80 | 5.80 | 77.40% | 177 |
| droe | 21 | 0.005 | 0.48 | 0.46 | 53.85% | 182 |
| droe | 63 | 0.006 | 0.44 | -0.36 | 51.11% | 180 |
| droe | 126 | -0.004 | -0.25 | -0.04 | 49.72% | 177 |
| ear_3d | 21 | -0.007 | -0.91 | -0.91 | 51.10% | 182 |
| ear_3d | 63 | -0.013 | -1.43 | -0.18 | 41.11% | 180 |
| ear_3d | 126 | -0.002 | -0.25 | 0.74 | 46.33% | 177 |
| gross_profitability | 21 | -0.005 | -0.45 | -0.43 | 49.45% | 182 |
| gross_profitability | 63 | -0.021 | -1.18 | -1.06 | 45.00% | 180 |
| gross_profitability | 126 | -0.010 | -0.35 | 0.28 | 50.85% | 177 |
| idio_vol_60d | 21 | 0.052 | 3.39 | 3.29 | 57.14% | 182 |
| idio_vol_60d | 63 | 0.084 | 4.22 | 3.43 | 65.00% | 180 |
| idio_vol_60d | 126 | 0.128 | 5.12 | 5.27 | 77.97% | 177 |
| max_ret_21d | 21 | 0.039 | 2.76 | 2.72 | 58.24% | 182 |
| max_ret_21d | 63 | 0.068 | 3.75 | 2.54 | 62.22% | 180 |
| max_ret_21d | 126 | 0.104 | 4.64 | 3.76 | 71.75% | 177 |
| mom_12_1 | 21 | 0.009 | 0.77 | 0.80 | 50.00% | 182 |
| mom_12_1 | 63 | 0.004 | 0.25 | 0.30 | 47.78% | 180 |
| mom_12_1 | 126 | 0.005 | 0.26 | 0.53 | 50.28% | 177 |
| share_issuance | 21 | 0.038 | 2.56 | 2.54 | 53.85% | 182 |
| share_issuance | 63 | 0.055 | 2.80 | 2.08 | 58.33% | 180 |
| share_issuance | 126 | 0.080 | 3.08 | 2.29 | 62.15% | 177 |
| sue | 21 | -0.002 | -0.17 | -0.17 | 47.80% | 182 |
| sue | 63 | -0.004 | -0.26 | -0.28 | 50.56% | 180 |
| sue | 126 | 0.009 | 0.53 | 0.24 | 52.54% | 177 |
| sue_announce | 21 | 0.020 | 1.62 | 1.49 | 54.95% | 182 |
| sue_announce | 63 | 0.043 | 2.80 | 2.17 | 61.67% | 180 |
| sue_announce | 126 | 0.070 | 3.19 | 1.64 | 68.36% | 177 |

### 7.4 Tek değişkenli sıralama (EW; üst − alt = `mimic_`)

| Faktör | Ufuk | Port. | mimic EW | t | mimic VW | Üst − ort. | t | Monoton |
|---|---|---|---|---|---|---|---|---|
| asset_growth | 21 | 5 | 0.74% | 1.67 | -0.15% | 0.55% | 2.01 | ✘ |
| asset_growth | 63 | 5 | 1.33% | 1.16 | 0.29% | 1.15% | 1.76 | ✘ |
| asset_growth | 126 | 5 | 3.07% | 1.55 | 2.19% | 1.82% | 1.61 | ✘ |
| capex_at | 21 | 5 | 0.31% | 0.62 | -0.60% | 0.22% | 0.74 | ✘ |
| capex_at | 63 | 5 | 2.23% | 1.99 | 0.01% | 1.23% | 1.76 | ✘ |
| capex_at | 126 | 5 | 2.86% | 1.45 | -0.49% | 1.94% | 1.58 | ✘ |
| cash_runway_years | 21 | 5 | -0.91% | -1.56 | 0.16% | 0.04% | 0.13 | ✘ |
| cash_runway_years | 63 | 5 | -2.45% | -1.76 | -0.36% | -0.06% | -0.07 | ✘ |
| cash_runway_years | 126 | 5 | -3.15% | -1.32 | -2.07% | -0.35% | -0.22 | ✘ |
| cop_at | 21 | 5 | -0.22% | -0.48 | 0.35% | -0.48% | -1.90 | ✘ |
| cop_at | 63 | 5 | -0.98% | -0.85 | 1.32% | -1.38% | -2.14 | ✘ |
| cop_at | 126 | 5 | -1.58% | -0.81 | 2.96% | -2.55% | -2.23 | ✘ |
| dist_52w_high | 21 | 5 | 0.66% | 1.18 | 0.64% | 0.08% | 0.27 | ✘ |
| dist_52w_high | 63 | 5 | 1.68% | 1.34 | 1.36% | 0.25% | 0.39 | ✘ |
| dist_52w_high | 126 | 5 | 3.64% | 1.82 | 2.89% | 1.30% | 1.23 | ✔ |
| droe | 21 | 5 | 0.26% | 0.67 | -0.57% | 0.03% | 0.11 | ✘ |
| droe | 63 | 5 | 0.70% | 0.72 | -1.05% | 0.11% | 0.16 | ✘ |
| droe | 126 | 5 | 0.42% | 0.22 | -3.38% | 0.11% | 0.08 | ✘ |
| ear_3d | 21 | 5 | -0.74% | -1.86 | -0.56% | -0.35% | -1.46 | ✘ |
| ear_3d | 63 | 5 | -1.23% | -1.67 | -0.80% | -0.55% | -1.21 | ✘ |
| ear_3d | 126 | 5 | 0.33% | 0.29 | 1.67% | -0.32% | -0.43 | ✘ |
| gross_profitability | 21 | 5 | -0.01% | -0.01 | 0.10% | -0.14% | -0.62 | ✘ |
| gross_profitability | 63 | 5 | 0.63% | 0.59 | 1.39% | -0.26% | -0.51 | ✘ |
| gross_profitability | 126 | 5 | 2.42% | 1.06 | 4.30% | -0.38% | -0.35 | ✘ |
| idio_vol_60d | 21 | 5 | 0.09% | 0.15 | 0.76% | 0.16% | 0.45 | ✘ |
| idio_vol_60d | 63 | 5 | -0.52% | -0.35 | 1.62% | 0.05% | 0.05 | ✘ |
| idio_vol_60d | 126 | 5 | 1.69% | 0.69 | 3.69% | 1.03% | 0.62 | ✘ |
| max_ret_21d | 21 | 5 | -0.03% | -0.05 | 0.92% | 0.18% | 0.58 | ✘ |
| max_ret_21d | 63 | 5 | -0.47% | -0.36 | 0.93% | 0.15% | 0.19 | ✘ |
| max_ret_21d | 126 | 5 | 0.98% | 0.42 | 2.31% | 0.84% | 0.57 | ✘ |
| mom_12_1 | 21 | 5 | 0.60% | 1.18 | 0.78% | 0.05% | 0.18 | ✘ |
| mom_12_1 | 63 | 5 | 1.65% | 1.39 | 1.42% | 0.71% | 0.94 | ✘ |
| mom_12_1 | 126 | 5 | 1.78% | 0.89 | 0.54% | 0.69% | 0.52 | ✘ |
| share_issuance | 21 | 5 | 0.46% | 0.73 | 1.04% | 0.21% | 0.65 | ✘ |
| share_issuance | 63 | 5 | -0.20% | -0.13 | 1.31% | 0.13% | 0.16 | ✘ |
| share_issuance | 126 | 5 | -0.22% | -0.07 | 1.95% | 0.44% | 0.28 | ✘ |
| sue | 21 | 5 | -0.13% | -0.31 | -0.37% | 0.02% | 0.09 | ✘ |
| sue | 63 | 5 | -0.07% | -0.08 | -0.45% | -0.10% | -0.18 | ✘ |
| sue | 126 | 5 | 0.54% | 0.44 | -1.15% | 0.91% | 1.22 | ✘ |
| sue_announce | 21 | 5 | 0.55% | 0.80 | 0.11% | 0.51% | 1.36 | ✘ |
| sue_announce | 63 | 5 | 2.48% | 1.66 | 1.34% | 1.23% | 1.11 | ✘ |
| sue_announce | 126 | 5 | 5.68% | 2.52 | 4.01% | 3.09% | 1.94 | ✔ |

### 7.4 Alfalar (21 seans, aylık; NW t)

Üst portföy RF üzeri; `mimic_ew` ham fark.

| Faktör | Seri | capm t | ff3 t | carhart4 t | ff5_mom t |
|---|---|---|---|---|---|
| asset_growth | mimic_ew | 1.50 | 1.54 | 1.73 | 1.60 |
| asset_growth | top_ew | 0.85 | 1.83 | 1.85 | 2.14 |
| capex_at | mimic_ew | 0.81 | 0.87 | 1.01 | 1.32 |
| capex_at | top_ew | 0.57 | 1.22 | 1.28 | 1.61 |
| cash_runway_years | mimic_ew | -1.18 | -1.53 | -1.34 | -1.41 |
| cash_runway_years | top_ew | 0.07 | 0.61 | 0.60 | 0.87 |
| cop_at | mimic_ew | 0.25 | 0.03 | 0.18 | 0.11 |
| cop_at | top_ew | 0.01 | 0.39 | 0.43 | 0.57 |
| dist_52w_high | mimic_ew | 1.71 | 1.35 | 1.62 | 1.38 |
| dist_52w_high | top_ew | 0.90 | 1.40 | 1.49 | 1.63 |
| droe | mimic_ew | 0.29 | 0.37 | 0.33 | 0.26 |
| droe | top_ew | 0.58 | 1.07 | 1.02 | 1.14 |
| ear_3d | mimic_ew | -1.87 | -1.96 | -1.91 | -1.86 |
| ear_3d | top_ew | -0.51 | 0.16 | 0.12 | 0.44 |
| gross_profitability | mimic_ew | 0.61 | 0.44 | 0.73 | 0.59 |
| gross_profitability | top_ew | 0.71 | 1.15 | 1.34 | 1.33 |
| idio_vol_60d | mimic_ew | 0.90 | 0.25 | 0.46 | 0.03 |
| idio_vol_60d | top_ew | 1.70 | 1.89 | 1.96 | 1.90 |
| max_ret_21d | mimic_ew | 0.86 | 0.23 | 0.35 | -0.07 |
| max_ret_21d | top_ew | 1.66 | 2.06 | 2.08 | 2.16 |
| mom_12_1 | mimic_ew | 1.16 | 1.14 | 0.96 | 0.99 |
| mom_12_1 | top_ew | 0.01 | 0.66 | 0.58 | 0.89 |
| share_issuance | mimic_ew | 1.14 | 0.59 | 0.82 | 0.46 |
| share_issuance | top_ew | 1.50 | 1.86 | 1.88 | 1.94 |
| sue | mimic_ew | -0.35 | -0.32 | -0.13 | -0.15 |
| sue | top_ew | 0.67 | 1.16 | 1.14 | 1.20 |
| sue_announce | mimic_ew | 0.92 | 0.65 | 0.45 | 0.42 |
| sue_announce | top_ew | 1.56 | 2.18 | 1.96 | 2.18 |

### 7.5 Bağımlı iki değişkenli sıralama (tema skoru terciliyle kontrol)

| Faktör | Ufuk | Ort. fark | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.38% | 1.17 |
| asset_growth | 63 | 0.34% | 0.40 |
| asset_growth | 126 | 1.01% | 0.62 |
| capex_at | 21 | 0.22% | 0.60 |
| capex_at | 63 | 1.14% | 1.41 |
| capex_at | 126 | 0.82% | 0.53 |
| cash_runway_years | 21 | -1.12% | -2.63 |
| cash_runway_years | 63 | -3.18% | -3.16 |
| cash_runway_years | 126 | -5.36% | -2.57 |
| cop_at | 21 | -0.02% | -0.06 |
| cop_at | 63 | -0.31% | -0.55 |
| cop_at | 126 | -0.44% | -0.41 |
| dist_52w_high | 21 | 0.52% | 1.48 |
| dist_52w_high | 63 | 1.22% | 1.66 |
| dist_52w_high | 126 | 2.38% | 1.95 |
| droe | 21 | 0.09% | 0.32 |
| droe | 63 | 0.49% | 0.73 |
| droe | 126 | -0.46% | -0.41 |
| ear_3d | 21 | -0.49% | -1.76 |
| ear_3d | 63 | -0.85% | -1.53 |
| ear_3d | 126 | 0.02% | 0.02 |
| gross_profitability | 21 | -0.20% | -0.83 |
| gross_profitability | 63 | -0.60% | -0.93 |
| gross_profitability | 126 | -0.56% | -0.44 |
| idio_vol_60d | 21 | 0.17% | 0.47 |
| idio_vol_60d | 63 | 0.08% | 0.10 |
| idio_vol_60d | 126 | 1.62% | 1.18 |
| max_ret_21d | 21 | -0.23% | -0.69 |
| max_ret_21d | 63 | -0.52% | -0.74 |
| max_ret_21d | 126 | 0.29% | 0.24 |
| mom_12_1 | 21 | 0.21% | 0.56 |
| mom_12_1 | 63 | 0.91% | 1.00 |
| mom_12_1 | 126 | 1.01% | 0.62 |
| share_issuance | 21 | -0.03% | -0.07 |
| share_issuance | 63 | -0.86% | -0.84 |
| share_issuance | 126 | -1.55% | -0.82 |
| sue | 21 | 0.01% | 0.03 |
| sue | 63 | -0.10% | -0.15 |
| sue | 126 | -0.54% | -0.47 |
| sue_announce | 21 | 0.48% | 1.26 |
| sue_announce | 63 | 1.60% | 1.97 |
| sue_announce | 126 | 3.28% | 2.13 |

### 7.6 Fama-MacBeth (tek faktör + β, ln(MktCap); NW t)

| Faktör | Ufuk | OLS rank-normal t | OLS ham t | WLS √MktCap t | 1 std etkisi | Ort. R² |
|---|---|---|---|---|---|---|
| asset_growth | 21 | 1.59 | 1.49 | 0.36 | 0.21% | 6.95% |
| asset_growth | 63 | 0.68 | 1.24 | -0.15 | 0.23% | 6.06% |
| asset_growth | 126 | 0.68 | 1.17 | 0.19 | 0.42% | 5.71% |
| capex_at | 21 | -0.02 | -0.82 | -1.02 | -0.00% | 6.78% |
| capex_at | 63 | 1.26 | 0.35 | 0.04 | 0.45% | 5.89% |
| capex_at | 126 | 0.52 | -0.41 | -0.44 | 0.36% | 5.37% |
| cash_runway_years | 21 | -1.74 | -1.46 | -0.64 | -0.31% | 5.57% |
| cash_runway_years | 63 | -1.94 | -1.51 | -0.87 | -0.87% | 5.14% |
| cash_runway_years | 126 | -1.65 | -0.62 | -1.13 | -1.20% | 4.89% |
| cop_at | 21 | 0.06 | -0.92 | 0.92 | 0.01% | 10.33% |
| cop_at | 63 | -0.17 | -1.31 | 1.15 | -0.05% | 10.13% |
| cop_at | 126 | -0.20 | -1.09 | 1.47 | -0.10% | 9.83% |
| dist_52w_high | 21 | 0.64 | 1.52 | 0.22 | 0.12% | 7.29% |
| dist_52w_high | 63 | 1.72 | 2.40 | 1.34 | 0.69% | 6.29% |
| dist_52w_high | 126 | 1.96 | 2.60 | 1.33 | 1.23% | 5.74% |
| droe | 21 | 0.75 | -0.94 | 0.14 | 0.08% | 11.11% |
| droe | 63 | 1.07 | -0.64 | 0.11 | 0.28% | 11.04% |
| droe | 126 | 0.48 | -1.15 | -0.37 | 0.24% | 10.63% |
| ear_3d | 21 | -1.61 | -1.54 | -0.75 | -0.18% | 6.49% |
| ear_3d | 63 | -1.80 | -1.90 | -1.18 | -0.42% | 5.70% |
| ear_3d | 126 | -0.04 | 0.39 | 0.12 | -0.01% | 5.39% |
| gross_profitability | 21 | -0.82 | -0.78 | -0.08 | -0.10% | 11.55% |
| gross_profitability | 63 | -0.82 | -1.12 | 0.19 | -0.24% | 11.31% |
| gross_profitability | 126 | -0.42 | -0.85 | 0.68 | -0.25% | 10.79% |
| idio_vol_60d | 21 | -0.17 | -0.28 | 0.40 | -0.03% | 6.65% |
| idio_vol_60d | 63 | -0.21 | -0.35 | 0.36 | -0.10% | 6.01% |
| idio_vol_60d | 126 | 1.15 | 0.54 | 0.88 | 0.94% | 5.92% |
| max_ret_21d | 21 | 0.00 | -0.12 | 1.13 | 0.00% | 6.38% |
| max_ret_21d | 63 | -0.17 | -0.63 | 0.66 | -0.06% | 5.60% |
| max_ret_21d | 126 | 0.68 | -0.64 | 0.97 | 0.40% | 5.50% |
| mom_12_1 | 21 | 1.00 | 0.82 | 0.80 | 0.16% | 6.85% |
| mom_12_1 | 63 | 1.62 | 1.74 | 1.40 | 0.62% | 5.97% |
| mom_12_1 | 126 | 1.38 | 1.67 | 1.16 | 0.87% | 5.39% |
| share_issuance | 21 | 0.80 | -0.40 | 0.89 | 0.13% | 6.92% |
| share_issuance | 63 | -0.19 | -0.95 | 0.11 | -0.09% | 6.31% |
| share_issuance | 126 | -0.20 | -0.61 | 0.12 | -0.17% | 6.20% |
| sue | 21 | 0.12 | -0.36 | -0.12 | 0.01% | 10.85% |
| sue | 63 | 0.52 | 0.09 | 0.10 | 0.12% | 10.14% |
| sue | 126 | 0.66 | 0.23 | 0.06 | 0.28% | 9.67% |
| sue_announce | 21 | 0.96 | 1.10 | 1.02 | 0.14% | 11.11% |
| sue_announce | 63 | 2.12 | 2.22 | 1.75 | 0.78% | 10.18% |
| sue_announce | 126 | 2.14 | 2.61 | 1.41 | 1.64% | 10.76% |

Tüm faktörlü model (kapsama ≥ %50, eksiksiz satırlar):

| Ufuk | Faktör | Katsayı | NW t | Ort. düz. R² |
|---|---|---|---|---|
| 21 | asset_growth | -0.17% | -0.78 | 18.21% |
| 21 | capex_at | 0.29% | 1.45 | 18.21% |
| 21 | cash_runway_years | -0.08% | -0.23 | 18.21% |
| 21 | cop_at | 0.11% | 0.34 | 18.21% |
| 21 | dist_52w_high | 0.29% | 1.19 | 18.21% |
| 21 | droe | 0.06% | 0.23 | 18.21% |
| 21 | ear_3d | 0.01% | 0.09 | 18.21% |
| 21 | ebit_ev | -0.39% | -1.11 | 18.21% |
| 21 | gross_profitability | 0.32% | 1.46 | 18.21% |
| 21 | idio_vol_60d | -0.47% | -1.67 | 18.21% |
| 21 | max_ret_21d | 0.19% | 0.84 | 18.21% |
| 21 | mom_12_1 | 0.16% | 0.69 | 18.21% |
| 21 | ocf_ev | 0.17% | 0.48 | 18.21% |
| 21 | share_issuance | 0.25% | 1.23 | 18.21% |
| 21 | sue | 0.11% | 0.46 | 18.21% |
| 63 | asset_growth | -0.59% | -1.10 | 15.35% |
| 63 | capex_at | 0.85% | 1.66 | 15.35% |
| 63 | cash_runway_years | 0.33% | 0.40 | 15.35% |
| 63 | cop_at | -0.23% | -0.26 | 15.35% |
| 63 | dist_52w_high | 0.04% | 0.06 | 15.35% |
| 63 | droe | -0.02% | -0.04 | 15.35% |
| 63 | ear_3d | 0.18% | 0.43 | 15.35% |
| 63 | ebit_ev | -1.01% | -1.27 | 15.35% |
| 63 | gross_profitability | 0.77% | 1.31 | 15.35% |
| 63 | idio_vol_60d | -0.07% | -0.12 | 15.35% |
| 63 | max_ret_21d | -0.04% | -0.10 | 15.35% |
| 63 | mom_12_1 | 0.59% | 1.07 | 15.35% |
| 63 | ocf_ev | 0.56% | 0.74 | 15.35% |
| 63 | share_issuance | 0.24% | 0.47 | 15.35% |
| 63 | sue | 0.40% | 0.75 | 15.35% |
| 126 | asset_growth | -1.34% | -1.35 | 13.92% |
| 126 | capex_at | 1.01% | 1.10 | 13.92% |
| 126 | cash_runway_years | -0.30% | -0.21 | 13.92% |
| 126 | cop_at | -0.07% | -0.06 | 13.92% |
| 126 | dist_52w_high | -0.32% | -0.28 | 13.92% |
| 126 | droe | 0.13% | 0.14 | 13.92% |
| 126 | ear_3d | -0.10% | -0.15 | 13.92% |
| 126 | ebit_ev | -2.61% | -1.76 | 13.92% |
| 126 | gross_profitability | 1.22% | 1.19 | 13.92% |
| 126 | idio_vol_60d | 1.95% | 1.60 | 13.92% |
| 126 | max_ret_21d | -0.24% | -0.50 | 13.92% |
| 126 | mom_12_1 | 1.30% | 1.66 | 13.92% |
| 126 | ocf_ev | 2.22% | 1.47 | 13.92% |
| 126 | share_issuance | 0.21% | 0.23 | 13.92% |
| 126 | sue | 0.42% | 0.52 | 13.92% |

### 7.1 Tanımlayıcı istatistikler (winsorize %0,5/%99,5; aylık değerlerin zaman ortalaması)

| Faktör | Ort. | Std | Çarp. | Bas. | P5 | Medyan | P95 | n | Ort. kayması |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.365 | 0.746 | 2.89 | 11.02 | -0.237 | 0.134 | 1.797 | 160 | 0.24 |
| capex_at | 0.018 | 0.020 | 2.19 | 6.43 | 0.001 | 0.011 | 0.055 | 152 | 0.18 |
| cash_runway_years | 6.414 | 3.752 | -0.36 | -1.12 | 0.951 | 7.377 | 10.000 | 161 | 0.22 |
| cop_at | -0.100 | 0.268 | -1.07 | 1.80 | -0.575 | -0.047 | 0.217 | 161 | 0.22 |
| dist_52w_high | -0.256 | 0.183 | -0.79 | 0.13 | -0.596 | -0.223 | -0.029 | 163 | 0.46 |
| droe | -0.004 | 0.229 | 0.01 | 8.68 | -0.321 | -0.002 | 0.306 | 144 | 0.12 |
| ear_3d | 0.007 | 0.098 | 0.43 | 3.25 | -0.137 | 0.002 | 0.164 | 149 | 0.09 |
| ebit_ev | -0.085 | 0.258 | -2.87 | 17.43 | -0.389 | -0.034 | 0.088 | 151 | 0.31 |
| gross_profitability | 0.306 | 0.199 | 0.93 | 1.19 | 0.042 | 0.272 | 0.670 | 94 | 0.19 |
| idio_vol_60d | 0.515 | 0.337 | 2.41 | 10.17 | 0.179 | 0.453 | 1.050 | 163 | 0.32 |
| max_ret_21d | 0.078 | 0.083 | 3.82 | 20.94 | 0.021 | 0.057 | 0.191 | 163 | 0.24 |
| mom_12_1 | 0.398 | 0.958 | 2.67 | 11.19 | -0.439 | 0.156 | 2.002 | 163 | 0.38 |
| net_debt_ebitda | 0.575 | 7.407 | 0.91 | 8.01 | -10.398 | 0.409 | 9.680 | 56 | 0.15 |
| ocf_ev | -0.047 | 0.204 | -2.50 | 15.42 | -0.295 | -0.008 | 0.104 | 160 | 0.28 |
| profitable_growth | 1.063 | 0.419 | 0.13 | -0.55 | 0.411 | 1.029 | 1.773 | 68 | 0.05 |
| share_issuance | 0.095 | 0.187 | 2.93 | 14.51 | -0.041 | 0.035 | 0.379 | 156 | 0.25 |
| sue | -0.222 | 1.395 | -0.29 | 0.35 | -2.664 | -0.104 | 1.994 | 157 | 0.15 |
| sue_announce | 0.469 | 1.530 | 0.30 | 0.47 | -1.827 | 0.317 | 3.031 | 59 | 0.26 |

### 7.2 Korelasyon ve çoklu doğrusallık

Tam matris (alt üçgen Pearson, üst üçgen Spearman): `corr.csv`. |ρ| > 0,7 çiftleri:

| A | B | Pearson | Spearman | Not |
|---|---|---|---|---|
| cash_runway_years | cop_at | 0.85 | 0.86 |  |
| cash_runway_years | ebit_ev | 0.53 | 0.71 | Spearman >> Pearson: doğrusal olmayan monoton ilişki |
| cash_runway_years | ocf_ev | 0.64 | 0.81 | Spearman >> Pearson: doğrusal olmayan monoton ilişki |
| cop_at | ebit_ev | 0.54 | 0.76 | Spearman >> Pearson: doğrusal olmayan monoton ilişki |
| cop_at | ocf_ev | 0.65 | 0.85 | Spearman >> Pearson: doğrusal olmayan monoton ilişki |
| ebit_ev | ocf_ev | 0.87 | 0.87 |  |
| idio_vol_60d | max_ret_21d | 0.64 | 0.72 |  |

VIF > 5: `cop_at` (6.6), `ebit_ev` (7.9), `ocf_ev` (9.4)

Ortogonalize (tema skoru + alt tema kuklaları sonrası artık) IC:

| Faktör | Ufuk | Artık IC | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.009 | 1.08 |
| asset_growth | 63 | 0.004 | 0.34 |
| asset_growth | 126 | 0.013 | 0.79 |
| capex_at | 21 | -0.007 | -0.80 |
| capex_at | 63 | -0.007 | -0.63 |
| capex_at | 126 | -0.021 | -1.56 |
| cash_runway_years | 21 | -0.020 | -1.86 |
| cash_runway_years | 63 | -0.027 | -2.11 |
| cash_runway_years | 126 | -0.029 | -1.54 |
| cop_at | 21 | 0.000 | 0.04 |
| cop_at | 63 | -0.014 | -1.03 |
| cop_at | 126 | -0.015 | -0.80 |
| dist_52w_high | 21 | 0.016 | 1.53 |
| dist_52w_high | 63 | 0.032 | 2.69 |
| dist_52w_high | 126 | 0.042 | 3.02 |
| droe | 21 | 0.001 | 0.06 |
| droe | 63 | 0.000 | 0.00 |
| droe | 126 | -0.024 | -1.27 |
| ear_3d | 21 | -0.008 | -1.09 |
| ear_3d | 63 | -0.013 | -1.56 |
| ear_3d | 126 | -0.002 | -0.31 |
| gross_profitability | 21 | -0.008 | -0.75 |
| gross_profitability | 63 | -0.028 | -1.79 |
| gross_profitability | 126 | -0.027 | -1.10 |
| idio_vol_60d | 21 | 0.031 | 2.79 |
| idio_vol_60d | 63 | 0.051 | 3.61 |
| idio_vol_60d | 126 | 0.078 | 4.58 |
| max_ret_21d | 21 | 0.017 | 1.67 |
| max_ret_21d | 63 | 0.035 | 2.83 |
| max_ret_21d | 126 | 0.055 | 3.78 |
| mom_12_1 | 21 | -0.005 | -0.45 |
| mom_12_1 | 63 | -0.015 | -1.02 |
| mom_12_1 | 126 | -0.026 | -1.36 |
| share_issuance | 21 | 0.020 | 1.79 |
| share_issuance | 63 | 0.025 | 1.68 |
| share_issuance | 126 | 0.037 | 1.92 |
| sue | 21 | -0.015 | -1.23 |
| sue | 63 | -0.025 | -1.55 |
| sue | 126 | -0.029 | -1.48 |
| sue_announce | 21 | 0.006 | 0.53 |
| sue_announce | 63 | 0.021 | 1.71 |
| sue_announce | 126 | 0.028 | 1.63 |

### 7.3 Süreklilik (ρτ, aylık kesitsel sıra korelasyonu)

| Faktör | τ=1 | τ=3 | τ=6 | τ=12 |
|---|---|---|---|---|
| asset_growth | 0.90 | 0.69 | 0.47 | 0.07 |
| capex_at | 0.98 | 0.95 | 0.90 | 0.78 |
| cash_runway_years | 0.97 | 0.90 | 0.83 | 0.72 |
| cop_at | 0.98 | 0.94 | 0.89 | 0.78 |
| dist_52w_high | 0.83 | 0.65 | 0.48 | 0.31 |
| droe | 0.78 | 0.37 | 0.20 | -0.24 |
| ear_3d | 0.63 | -0.02 | 0.01 | 0.01 |
| ebit_ev | 0.98 | 0.94 | 0.89 | 0.78 |
| gross_profitability | 0.98 | 0.95 | 0.91 | 0.84 |
| idio_vol_60d | 0.91 | 0.75 | 0.74 | 0.72 |
| max_ret_21d | 0.50 | 0.50 | 0.48 | 0.49 |
| mom_12_1 | 0.88 | 0.68 | 0.41 | -0.03 |
| net_debt_ebitda | 0.98 | 0.95 | 0.91 | 0.85 |
| ocf_ev | 0.98 | 0.93 | 0.88 | 0.77 |
| profitable_growth | 0.97 | 0.91 | 0.81 | 0.63 |
| share_issuance | 0.96 | 0.88 | 0.78 | 0.61 |
| sue | 0.82 | 0.48 | 0.37 | 0.03 |
| sue_announce | 0.86 | 0.58 | 0.47 | 0.23 |

### 7.8 İstikrar (126 seans IC ortalaması) ve ekonomik gerekçe

| Faktör | 2011-07..2015-12 | 2016-01..2020-12 | 2021-01..2026-09 | bull | bear | vix_high | vix_low | Neden çalışmalı | Kaynak |
|---|---|---|---|---|---|---|---|---|---|
| asset_growth | 0.042 | -0.001 | 0.017 | 0.019 | 0.007 | 0.022 | 0.014 | aşırı yatırım / q-teorisi (−) | Cooper, Gulen & Schill (2008); Hou, Xue & Zhang (2015) |
| capex_at | -0.058 | -0.056 | 0.027 | -0.032 | 0.024 | -0.020 | -0.035 | yatırım faktörü (−) | Titman, Wei & Xie (2004); Fama & French (2015) CMA |
| cash_runway_years | -0.043 | 0.038 | 0.033 | 0.018 | -0.013 | 0.014 | 0.016 | finansal kısıt / seyreltme riski | Hadlock & Pierce (2010) — tema uyarlaması |
| cop_at | -0.019 | -0.046 | 0.074 | 0.007 | -0.018 | -0.013 | 0.023 | kalite (tahakkuksuz kârlılık) | Ball, Gerakos, Linnainmaa & Nikolaev (2016) |
| dist_52w_high | 0.080 | 0.081 | 0.128 | 0.098 | 0.092 | 0.090 | 0.106 | davranışsal (çıpalama) | George & Hwang (2004) |
| droe | -0.010 | -0.010 | 0.006 | -0.012 | 0.071 | -0.016 | 0.008 | temel momentum | Hou, Xue & Zhang (2015) q-faktör ROE |
| ear_3d | 0.003 | 0.002 | -0.011 | 0.002 | -0.046 | -0.004 | -0.001 | davranışsal (duyuru getirisi sürüklenmesi) | Chan, Jegadeesh & Lakonishok (1996) |
| gross_profitability | -0.064 | -0.019 | 0.045 | -0.013 | 0.023 | -0.024 | 0.005 | risk/kalite | Novy-Marx (2013) |
| idio_vol_60d | 0.120 | 0.104 | 0.158 | 0.126 | 0.142 | 0.126 | 0.130 | sınırlı arbitraj / piyango tercihi (−) | Ang, Hodrick, Xing & Zhang (2006) |
| max_ret_21d | 0.108 | 0.072 | 0.132 | 0.102 | 0.125 | 0.106 | 0.103 | piyango tercihi (−) | Bali, Cakici & Whitelaw (2011) |
| mom_12_1 | -0.004 | 0.023 | -0.006 | -0.005 | 0.093 | 0.013 | -0.004 | davranışsal (yetersiz tepki) + risk | Jegadeesh & Titman (1993); Carhart (1997) |
| share_issuance | 0.101 | 0.051 | 0.090 | 0.087 | 0.015 | 0.076 | 0.085 | piyasa zamanlaması (−) | Pontiff & Woodgate (2008); Daniel & Titman (2006) |
| sue | 0.008 | -0.008 | 0.025 | 0.004 | 0.056 | -0.004 | 0.022 | davranışsal (kazanç sonrası sürüklenme) | Bernard & Thomas (1989) |
| sue_announce | 0.028 | 0.132 | 0.047 | 0.067 | 0.097 | 0.057 | 0.084 | davranışsal (PEAD, duyuru tarihli) | Bernard & Thomas (1989); Livnat & Mendenhall (2006) |

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
| asset_growth | 21 | 5 | 0.82% | 1.74 | 0.27% | 0.47% | 1.44 | ✘ |
| asset_growth | 63 | 5 | 2.23% | 1.92 | 0.88% | 1.35% | 1.86 | ✘ |
| asset_growth | 126 | 5 | 4.44% | 1.89 | 1.40% | 2.68% | 1.72 | ✘ |
| capex_at | 21 | 5 | 0.39% | 0.82 | 0.17% | 0.16% | 0.63 | ✘ |
| capex_at | 63 | 5 | 1.96% | 1.58 | 0.99% | 0.88% | 1.20 | ✘ |
| capex_at | 126 | 5 | 4.69% | 1.72 | 1.93% | 1.71% | 1.16 | ✘ |
| cash_runway_years | 21 | 3 | -4.44% | -1.07 | -8.67% | -3.45% | -2.77 | ✘ |
| cash_runway_years | 63 | 3 | -10.11% | -3.04 | -22.23% | -2.21% | -0.77 | ✘ |
| cash_runway_years | 126 | 3 | -25.24% | -8.70 | -43.74% | -9.06% | -8.77 | ✘ |
| cop_at | 21 | 5 | 0.06% | 0.11 | 0.22% | 0.02% | 0.07 | ✘ |
| cop_at | 63 | 5 | -0.51% | -0.42 | -0.08% | -0.40% | -0.54 | ✘ |
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
| net_debt_ebitda | 21 | 5 | 0.23% | 0.52 | 0.20% | 0.15% | 0.49 | ✘ |
| net_debt_ebitda | 63 | 5 | 0.26% | 0.22 | -0.16% | 0.19% | 0.25 | ✘ |
| net_debt_ebitda | 126 | 5 | 0.17% | 0.08 | -1.01% | 0.18% | 0.13 | ✘ |
| ocf_ev | 21 | 5 | 0.46% | 0.71 | 0.57% | 0.08% | 0.19 | ✘ |
| ocf_ev | 63 | 5 | 0.60% | 0.39 | 0.85% | -0.28% | -0.29 | ✘ |
| ocf_ev | 126 | 5 | 0.40% | 0.12 | 1.13% | -0.99% | -0.46 | ✘ |
| oil_beta_trend | 21 | 5 | 0.44% | 0.57 | 0.71% | 0.32% | 0.80 | ✘ |
| oil_beta_trend | 63 | 5 | -0.45% | -0.25 | 0.46% | 0.17% | 0.16 | ✘ |
| oil_beta_trend | 126 | 5 | 0.14% | 0.05 | 1.49% | 0.55% | 0.30 | ✘ |
| share_issuance | 21 | 5 | -0.03% | -0.08 | 0.09% | 0.12% | 0.51 | ✘ |
| share_issuance | 63 | 5 | 0.00% | 0.00 | 0.44% | 0.13% | 0.24 | ✘ |
| share_issuance | 126 | 5 | 0.91% | 0.50 | 1.47% | 0.34% | 0.32 | ✘ |
| sue_announce | 21 | 5 | 0.27% | 0.60 | 0.25% | 0.01% | 0.02 | ✘ |
| sue_announce | 63 | 5 | 0.48% | 0.51 | 0.99% | -0.26% | -0.52 | ✘ |
| sue_announce | 126 | 5 | 0.64% | 0.40 | 0.96% | 0.09% | 0.11 | ✘ |

### 7.4 Alfalar (21 seans, aylık; NW t)

Üst portföy RF üzeri; `mimic_ew` ham fark.

| Faktör | Seri | capm t | ff3 t | carhart4 t | ff5_mom t |
|---|---|---|---|---|---|
| asset_growth | mimic_ew | 1.71 | 1.69 | 1.66 | 1.68 |
| asset_growth | top_ew | 0.15 | 0.12 | 0.12 | -0.09 |
| capex_at | mimic_ew | 1.05 | 1.37 | 0.75 | 0.94 |
| capex_at | top_ew | -0.27 | -0.22 | -0.40 | -0.42 |
| cash_runway_years | mimic_ew | -1.35 | — | — | — |
| cash_runway_years | top_ew | -2.46 | — | — | — |
| cop_at | mimic_ew | -0.64 | -0.82 | -0.55 | -0.76 |
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
| net_debt_ebitda | mimic_ew | -0.56 | -0.47 | -0.65 | -0.84 |
| net_debt_ebitda | top_ew | -0.66 | -0.78 | -0.90 | -1.12 |
| ocf_ev | mimic_ew | -0.04 | -0.17 | 0.23 | -0.07 |
| ocf_ev | top_ew | -0.57 | -0.77 | -0.60 | -0.85 |
| oil_beta_trend | mimic_ew | 1.96 | 2.03 | 1.74 | 1.82 |
| oil_beta_trend | top_ew | 0.52 | 0.65 | 0.64 | 0.47 |
| share_issuance | mimic_ew | 0.01 | -0.20 | -0.03 | -0.58 |
| share_issuance | top_ew | -0.19 | -0.37 | -0.22 | -0.72 |
| sue_announce | mimic_ew | 1.27 | 1.16 | 0.73 | 0.87 |
| sue_announce | top_ew | -0.09 | -0.23 | -0.47 | -0.69 |

### 7.5 Bağımlı iki değişkenli sıralama (tema skoru terciliyle kontrol)

| Faktör | Ufuk | Ort. fark | NW t |
|---|---|---|---|
| asset_growth | 21 | 0.69% | 1.72 |
| asset_growth | 63 | 1.94% | 2.16 |
| asset_growth | 126 | 4.21% | 2.30 |
| capex_at | 21 | 0.54% | 1.58 |
| capex_at | 63 | 2.01% | 2.23 |
| capex_at | 126 | 3.97% | 2.11 |
| cop_at | 21 | 0.00% | 0.00 |
| cop_at | 63 | -0.42% | -0.31 |
| cop_at | 126 | -1.43% | -0.50 |
| dist_52w_high | 21 | -0.18% | -0.29 |
| dist_52w_high | 63 | -0.66% | -0.46 |
| dist_52w_high | 126 | -0.74% | -0.25 |
| ear_3d | 21 | 0.31% | 1.16 |
| ear_3d | 63 | 0.37% | 0.69 |
| ear_3d | 126 | 1.26% | 1.35 |
| ebit_ev | 21 | -0.43% | -0.96 |
| ebit_ev | 63 | -1.48% | -1.36 |
| ebit_ev | 126 | -2.88% | -1.36 |
| gross_profitability | 21 | 0.22% | 0.67 |
| gross_profitability | 63 | 0.28% | 0.32 |
| gross_profitability | 126 | 1.54% | 0.89 |
| idio_vol_60d | 21 | -0.45% | -0.62 |
| idio_vol_60d | 63 | -1.33% | -0.74 |
| idio_vol_60d | 126 | -1.69% | -0.47 |
| max_ret_21d | 21 | -0.48% | -0.79 |
| max_ret_21d | 63 | -1.06% | -0.72 |
| max_ret_21d | 126 | -1.61% | -0.55 |
| mom_12_1 | 21 | 0.21% | 0.39 |
| mom_12_1 | 63 | 0.77% | 0.68 |
| mom_12_1 | 126 | 1.29% | 0.52 |
| net_debt_ebitda | 21 | 0.05% | 0.11 |
| net_debt_ebitda | 63 | -0.29% | -0.27 |
| net_debt_ebitda | 126 | -0.39% | -0.18 |
| ocf_ev | 21 | 0.53% | 0.92 |
| ocf_ev | 63 | 1.04% | 0.74 |
| ocf_ev | 126 | 1.54% | 0.52 |
| oil_beta_trend | 21 | 0.37% | 0.70 |
| oil_beta_trend | 63 | 0.09% | 0.07 |
| oil_beta_trend | 126 | 1.04% | 0.46 |
| share_issuance | 21 | -0.09% | -0.32 |
| share_issuance | 63 | -0.09% | -0.14 |
| share_issuance | 126 | 0.20% | 0.13 |
| sue_announce | 21 | 0.43% | 1.31 |
| sue_announce | 63 | 1.08% | 1.50 |
| sue_announce | 126 | 1.76% | 1.37 |

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
| capex_at | 63 | 0.020 | 1.25 |
| capex_at | 126 | 0.035 | 1.43 |
| cash_runway_years | 21 | -0.114 | -1.20 |
| cash_runway_years | 63 | -0.127 | -2.61 |
| cash_runway_years | 126 | -0.196 | -3.67 |
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
| max_ret_21d | 21 | 0.019 | 1.34 |
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
