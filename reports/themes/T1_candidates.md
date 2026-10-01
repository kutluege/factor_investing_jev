# T1 — Tema aday havuzu (aşama A)

Aşama A yalnızca 10-K metni puanlanacak firmaları belirler; üyelik kararı vermez (THEMES_SPEC §3-A).
FMP sanayi ve EDGAR SIC bugünkü değerlerdir (PIT değildir); filtre bilerek geniş tutulmuştur.

- Borsalar: NASDAQ, NYSE (NYSE American hariç)
- Aday firma: **3712** (aktif 2303, delist 1409); 10-K metni gereken: 2452; yabancı dosyalayan (20-F/40-F) çıkarılan: 727; fiyatı olan: 3106

| Tema | Alt tema | Aday | NASDAQ | NYSE | Delist | Sadece SIC ile |
|---|---|---|---|---|---|---|
| ai | ai_compute | 342 | 273 | 69 | 107 | 49 |
| ai | ai_infrastructure | 755 | 383 | 372 | 254 | 264 |
| ai | ai_software | 860 | 657 | 203 | 353 | 155 |
| biotech | biotech_all | 1040 | 997 | 43 | 433 | 100 |
| biotech | biotech_tools | 112 | 96 | 16 | 40 | 53 |
| cyber_cloud | cloud_saas | 823 | 628 | 195 | 336 | 182 |
| cyber_cloud | cybersecurity | 807 | 605 | 202 | 319 | 165 |
| defense_space | defense | 323 | 198 | 125 | 94 | 19 |
| defense_space | quantum | 783 | 602 | 181 | 287 | 296 |
| defense_space | space | 412 | 263 | 149 | 143 | 27 |
| energy | grid_equipment | 60 | 37 | 23 | 7 | 5 |
| energy | nuclear_uranium | 74 | 17 | 57 | 18 | 70 |
| energy | oil_gas | 267 | 79 | 188 | 107 | 29 |
| energy | power_utilities | 122 | 32 | 90 | 36 | 37 |
| energy | renewables | 205 | 130 | 75 | 64 | 168 |
| robotics | autonomous_drone | 803 | 556 | 247 | 298 | 109 |
| robotics | components | 333 | 253 | 80 | 89 | 44 |
| robotics | industrial_automation | 466 | 290 | 176 | 145 | 65 |
| robotics | surgical_medical | 302 | 251 | 51 | 122 | 47 |
| semiconductors | semi_equipment | 278 | 163 | 115 | 65 | 42 |
| semiconductors | semis_all | 145 | 131 | 14 | 44 | 25 |

Not: bir firma birden çok alt temanın aday havuzunda olabilir; birincil alt tema T3'te 10-K ile belirlenir.

Veri yükleme özeti: `{}`
