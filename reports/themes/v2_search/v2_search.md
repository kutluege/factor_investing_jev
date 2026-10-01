# themes v2 — serbest arama, ölçülen aşırı uyum

**Durum: ARAMA İZİ (örneklem içi).** Kullanıcı kararıyla (2026-10-01) CLAUDE.md §3 bu iz için geçersiz kılındı; themes_v1 kaydı dondurulmuştur. Faktör listesi değişmedi; grup ağırlıkları, tilt kurulumu, tema bütçeleri, yeniden dengeleme hızı/sıklığı ve oynaklık bloğu arandı. Ölçüt: kompozit tema endeksine karşı net seçim katkısının bilgi oranı (IR).

## Aşırı uyum ölçümü (asıl sonuç)

| Ölçü | Değer | Yorum |
|---|---|---|
| Deneme sayısı | 500 | hepsi `trials.csv` içinde |
| Tasarım penceresi (2011-07→2020-12) IR, seçilen | -0.02 | seçim burada yapıldı (iyimser) |
| **Tutma dönemi (2021-01→) IR, seçilen** | **+0.36** | seçimde hiç kullanılmadı |
| Tutma dönemi katkı (aritm., yıllık) | +2.87% | 67 ay |
| Seçilenin tutma dönemindeki yüzdelik sırası | %100 | %50 = tesadüf |
| İç içe walk-forward IR (yıllık yeniden seçim) | -0.19 | gerçekçi tahmin, 127 ay |
| İç içe walk-forward katkı (yıllık) | -1.68% | |
| PBO (CSCV, tüm denemeler) | 19% | > %50: seçim kalıcı değil |
| Deflated Sharpe (tam örneklem en iyisi) | 0.10 | < 0,95: anlamlı değil |

## Seçilen yapılandırma (tasarım penceresinde en yüksek IR)

- Grup ağırlık çarpanları: fundamental_mom ×0.5, growth_quality ×0.5, investment ×0.5, low_risk ×1, momentum ×0.5, quality ×4, survival ×0.25, commodity ×0.25, leverage ×0.25, value ×2
- Tilt gücü λ = 0.74; tutulan üst dilim = %20
- Tema bütçeleri: ai %23, biotech %12, cyber_cloud %16, defense_space %11, energy %10, robotics %10, semiconductors %17
- Yeniden dengeleme: her 3 ayda bir, hız 1
- Oynaklık bloğu: en oynak %10

## Seçilenin tam (exact) backtest'i — sonraki açılışta işlem, tüm maliyet modeli, nakit RF

| Ölçü | Değer |
|---|---|
| §8 ölçütü (alt dönem, düşüş, 2× maliyet) | 3/3, ✔, ✔ → **GEÇTİ** |
| Seçim katkısı (aritm., tüm dönem) | +1.49%/yıl, NW t +0.76 |
| Takip hatası / IR | 7.65% / +0.19 |
| 2× maliyette katkı (geom.) | +1.51%/yıl |
| Maks. düşüş portföy / endeks | -24.5% / -28.5% |
| Tutma dönemi (exact) katkı / IR | +2.52% / +0.32 |
| Portföy yıllık getiri / endeks | 17.22% / 14.62% |
| İşlem sayısı | 4866 |

## Karşılaştırma: themes_v1-r2 (veri düzeltmeli v1, ilk-N)

Aritmetik katkı -0.36%/yıl, IR -0.03, takip hatası 10.48% (bkz. `T6_backtest_v1r2.md`).

## Deneme dağılımı

Tasarım IR yüzdelikleri (10/50/90): -0.78 / -0.56 / -0.33; tutma dönemi: -0.48 / -0.30 / -0.05. Tasarım ve tutma IR'ı arasındaki sıra korelasyonu: +0.26 (yakın 0 → tasarımda iyi görünen, sonra iyi kalmıyor).

## Yorum kuralları

- Tek temiz örneklem dışı kanıt ileri (gölge) takiptir (`themes forward`).
- Tasarım IR'ı seçim yanlılığı içerir; karar için tutma dönemi, walk-forward, PBO ve DSR birlikte okunur.
- Bu iz CLAUDE.md §3'ün kullanıcı tarafından geçersiz kılınmasıyla yürütülmüştür (`docs/CHANGELOG_THEMES.md`).
