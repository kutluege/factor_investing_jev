# T1 — Tema aday havuzu (aşama A)

Aşama A yalnızca 10-K metni puanlanacak firmaları belirler; üyelik kararı vermez (THEMES_SPEC §3-A).
FMP sanayi ve EDGAR SIC bugünkü değerlerdir (PIT değildir); filtre bilerek geniş tutulmuştur.

- Borsalar: NASDAQ, NYSE (NYSE American hariç)
- Aday firma: **2839** (aktif 1786, delist 1053); 10-K metni gereken: 1530; yabancı dosyalayan (20-F/40-F) çıkarılan: 541; fiyatı olan: 2834

| Tema | Alt tema | Aday | NASDAQ | NYSE | Delist | Sadece SIC ile |
|---|---|---|---|---|---|---|
| biotech | biotech_all | 1032 | 990 | 42 | 428 | 134 |
| energy | grid_equipment | 60 | 37 | 23 | 7 | 5 |
| energy | nuclear_uranium | 74 | 17 | 57 | 18 | 70 |
| energy | oil_gas | 267 | 79 | 188 | 107 | 29 |
| energy | power_utilities | 122 | 32 | 90 | 36 | 37 |
| energy | renewables | 205 | 130 | 75 | 64 | 168 |
| robotics | autonomous_drone | 770 | 543 | 227 | 289 | 118 |
| robotics | components | 288 | 223 | 65 | 74 | 44 |
| robotics | industrial_automation | 214 | 117 | 97 | 48 | 54 |
| robotics | surgical_medical | 285 | 238 | 47 | 108 | 65 |

Not: bir firma birden çok alt temanın aday havuzunda olabilir; birincil alt tema T3'te 10-K ile belirlenir.

Veri yükleme özeti: `{"prices": {"requested": 2848, "loaded": 2254, "up_to_date": 0, "stopped_reason": null, "dividend_adjusted": true, "rebased": ["ONMD", "CDT"], "failed": 0}, "splits": {"loaded": 1165, "stopped_reason": null, "available": true}, "fundamentals": {"requested": 2525, "loaded": 2493, "no_facts": 32, "snapshots_rebuilt": 978}}`
