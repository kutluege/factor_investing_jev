# Adım 0 — Tasarım özeti, çakışmalar ve açık sorular (themes_v1)

## Tasarım (10 madde)
1. Tema katmanı: robotik (%40), biotech (%35), enerji (%25); NASDAQ + NYSE ortak hisseleri, long-only.
2. Üyelik kararı yalnızca 10-K Item 1 metninden (PIT: kabul zamanı + 1 seans, sonraki 10-K veya 18 ay).
   FMP sanayi / SIC sadece aday havuzunu daraltır (bugünkü değerler, PIT değil).
3. Aşama: TTM faaliyet nakit akışı ≤ 0 → `pre_profit`; biotech: `clinical` / `commercial` ($50M gelir eşiği).
4. Faktör setleri aşamaya ve temaya göre sabit (`theme_factor_map`); gruplar eşit ağırlıklı; ağırlık öğrenme yok.
5. Yeni faktörler: `capex_at`, `fcf_margin`, `profitable_growth`, `net_debt_ebitda`, `oil_beta_trend`
   (+ doğrulanırsa `ear_3d`, `sue_announce`).
6. Skorlama: tarih bazında tema içinde rank → normal; muhasebe oranları alt tema (≥ 8 firma) içinde.
7. Araştırma modülü (§7): tanımlayıcı istatistik, korelasyon/VIF, süreklilik, tek ve iki değişkenli sıralama,
   `mimic_` portföyler, CAPM/FF3/Carhart/FF5+MOM alfaları, Fama-MacBeth (3 varyant), rank IC, istikrar.
8. Tek sabit konfigürasyonla backtest; başarı ölçütü CAGR değil, tema eşit ağırlık endeksine karşı seçim katkısı.
9. Aylık seçim listesi + 2 günde bir TA tablosu + işlem günlüğü ve değerlendirme betiği (otomatik işlem yok).
10. Disiplin: ön kayıt (SHA256), parametre taraması yok, her yeni özellik için sızıntı enjeksiyon testi, NW t.

## Mevcut kodla çakışmalar ve çözüm
| Konu | Çakışma | Çözüm |
|---|---|---|
| Evren | `config/universe.yaml` + `securities` tablosu yalnız NASDAQ ve eski sektör gruplarını içerir | Tema aday havuzu ayrı `theme_candidates` tablosunda tutulur; eski model (NASDAQ) bozulmaz. Fiyatlar ortak `daily_prices` tablosuna yazılır |
| Özellik deposu | `feature_panel` eski evren için kurulur | Aynı fonksiyonlar tema aday listesiyle çağrılır, sonuç `theme_feature_panel` tablosuna yazılır |
| Rebalance | Tema bütçesi ve alt tema tavanı yok | Tema ağırlıkları/alt tema tavanı `src/portfolio/rebalance.py` içine eklenir (tek rebalance modülü kuralı korunur) |
| "FMP" adı | Ders notlarında Factor Mimicking Portfolio | Kodda `mimic_` öneki; `fmp_` sadece API |
| METHODOLOGY | CLAUDE.md `docs/METHODOLOGY.md` bekliyor | `docs/METHODOLOGY_SUMMARY.md` → `docs/METHODOLOGY.md` olarak taşındı |
| Jev | Tema koşularında ağırlık 0 | Tema backtest'i Jev kullanmaz |

## Kapı (gate) kararları
Kullanıcı kararı: kapılar FMP verisiyle yanıtlanır. Her karar `reports/themes/gate_decisions.md` dosyasına yazılır.
Hiçbir kapı kararı getiri sonucuna bakılarak verilmez.

## Açık riskler
- Kenneth French veri kütüphanesi kurum ağında (Cisco Umbrella) engelli olabilir → T5a'da doğrulanacak.
- FMP earnings ve emtia (WTI) endpoint'lerinin Starter planda açık olup olmadığı → T4/T4b'de doğrulanacak.
- NYSE fiyat geçmişi FMP bant genişliğini (20 GB/30 gün) kullanır → sadece aday havuzu için çekilir.
