# Tema katmanı değişiklik günlüğü

Kural (CLAUDE.md §3): ön kayıttan (`research/preregistration/<sürüm>.yaml` + SHA256) sonra yapılandırmada yapılan her
değişiklik yeni bir sürüm (`themes_v2`, …) gerektirir ve burada **gerekçe + sebep olan sonuç** ile kaydedilir. Sonuca
bakılarak yeni faktör eklenmez; parametre taraması yapılmaz.

## themes_v1 — ön kayıt öncesi kararlar (2026-09-30)

Bunlar ön kayıttan ÖNCE, hiçbir getiri sonucu görülmeden verilen veri/uygulama kararlarıdır (ayrıntı:
`reports/themes/gate_decisions.md`):

- Kapı 1 (T0): 27 FMP sanayi adının 27'si birebir doğrulandı; `# VERIFY` işaretleri kaldırıldı, ad değişmedi.
- `oil_beta_trend`: WTI (CLUSD) Starter planda 402 → Brent (BZUSD) kullanılır.
- Kapı 5 (T4b): FMP duyuru tarihleri 8-K Item 2.02 ile aynı günde %80 (< %90) uyuştu → `ear_3d` / `sue_announce`
  zamanlaması 8-K'dan, EPS değeri FMP `epsActual`'dan.
- EDGAR `acceptanceDateTime` UTC'dir (doğrulandı); seans kuralı ET'ye dönüştürülerek uygulanır.
- `max_share_per_subtheme`: tavan ⌈0,5 × n_picks⌉, yalnızca ≥ 2 alt tema sıralandığında (tek alt temalı biotech için
  kural anlamsızdı).

- Kapı 2 (T3r): ilk isabet %83,3 < %85 → tek revizyon: SPAC ("blank check company") 10-K'ları üyelik vermez;
  `autonomous_drone.min_hits` 5 → 10; inceleme yalnızca işlem gören sembollerde. Revizyon sonrası %91,7.
  Sebep olan sonuç: sınıflandırma hataları (getiri değil). Ayrıntı: `reports/themes/gate_decisions.md`.

## themes_v1 — ön kayıt (2026-09-30)

`research/preregistration/themes_v1.yaml`, SHA256 `b3f5ab188a3002aaf058c356277042023f70a55057de60883657277098072c4b`. Bu tarihten sonra themes_v1 yapılandırması değiştirilmez; T5 araştırma ve T6 backtest bu dosyayla koşar.
