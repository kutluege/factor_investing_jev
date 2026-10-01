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

## themes_v2 / arama izi — kullanıcı kararı (2026-10-01)

**Kullanıcı kararı:** "Free optimization on full history" — kullanıcı, CLAUDE.md §3'ü (parametre taraması yok) bu iş
için açıkça geçersiz kıldı. Bu nedenle ayrı ve açıkça etiketlenmiş bir **arama izi** (`themes search`) açılır;
themes_v1 kaydı (ön kayıt dosyası, SHA256 `b3f5ab18…`, raporlar) dondurulmuş kalır. Diğer kararlar: faktör listesi
değişmez (yalnızca ağırlıklar, portföy kurulumu ve evren aranabilir); robotik evreni genişletilir; ölçülen portföy
geniş, skora göre eğimli (tilt) bir sepettir; kullanıcının TA'sı için ilk-N seçim listesi korunur.

**Sebep olan sonuçlar (themes_v1, `reports/themes/T6_backtest.md`):** seçim katkısı −0,68 puan/yıl geometrik
(−1,76 aritmetik, t −0,58), 0/3 alt dönem; takip hatası %11,8/yıl; ortalama yatırım oranı %90,9 (robotik
bütçesi dolmuyor); biotech'te skorun rank IC'si anlamlı (21g 0,043, t 3,3) ama ilk-7 eşit ağırlıklı kol bunu
paraya çeviremiyor (getiri çarpıklığı 151). Veri hataları: 48 adayda bozuk temettü düzeltmeli fiyat serisi (ör. ESPR),
USD dışı XBRL raporlayanlar (ör. Enbridge).

**Aşırı uyum ölçümü (gizlenmez):** tasarım penceresi 2011-07→2020-12'de seçim, 2021-01→2026-09 dokunulmamış
tutma dönemi, yıllık iç içe walk-forward yeniden seçim, tüm denemeler üzerinde CSCV PBO, deneme sayısıyla deflated
Sharpe; tüm denemeler kaydedilir. Tek temiz örneklem dışı kanıt 2026-10'dan itibaren ileri (gölge) takip olacaktır.
