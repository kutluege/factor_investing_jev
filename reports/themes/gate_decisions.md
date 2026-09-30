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
