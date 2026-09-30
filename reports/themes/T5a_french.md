# T5a — Kenneth French veri kütüphanesi

Kaynak: F-F_Research_Data_Factors_CSV.zip, F-F_Research_Data_5_Factors_2x3_CSV.zip, F-F_Momentum_Factor_CSV.zip (aylık tablo; yüzde → ondalık; ay sonu indeks).
Önbellek: `data/external/french/` (30 gün; ağ yoksa eski önbellek ya da elle indirilen zip kullanılır).

| Seri | Başlangıç | Bitiş | Ay |
|---|---|---|---|
| `ff_mkt_rf` | 1926-07-31 | 2026-08-31 | 1202 |
| `ff_smb` | 1926-07-31 | 2026-08-31 | 1202 |
| `ff_hml` | 1926-07-31 | 2026-08-31 | 1202 |
| `ff_rf` | 1926-07-31 | 2026-08-31 | 1202 |
| `ff5_smb` | 1963-07-31 | 2026-08-31 | 758 |
| `ff5_hml` | 1963-07-31 | 2026-08-31 | 758 |
| `ff_rmw` | 1963-07-31 | 2026-08-31 | 758 |
| `ff_cma` | 1963-07-31 | 2026-08-31 | 758 |
| `ff_mom` | 1927-01-31 | 2026-08-31 | 1196 |

Adlandırma: dış kıyas faktörleri `ff_`/`ff5_` önekli; `mimic_` yalnızca projenin kendi faktör-taklit portföyleri, `fmp_` yalnızca FMP alanları içindir.
Kontroller (`src/features/theme_features.py`): `beta_252d` = SPY'a karşı günlük CAPM betası (son 252 seans, en az 200 gözlem); `size_ln_mcap` = ln(piyasa değeri, USD).
Hizalama: portföy getirileri ay içindeki son işlem gününde damgalanır ve `to_month_end` ile takvim ay sonuna taşınır (test: `tests/test_french.py`).
