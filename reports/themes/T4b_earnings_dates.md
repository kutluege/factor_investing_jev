# T4b — Kazanç duyuru tarihleri: FMP vs EDGAR 8-K Item 2.02

Tarih: 2026-09-30. Komut: `python -m src.pipeline.themes t4b-verify` (tohum 20260930, tekrar üretilebilir).
Örnek: `research/themes/T4b_earnings_dates_sample.csv`.

## Endpoint doğrulaması (Starter plan)

| Endpoint | Durum | Not |
|---|---|---|
| `earnings?symbol=` | 200, açık | Alanlar: `symbol, date, epsActual, epsEstimated, revenueActual, revenueEstimated, lastUpdated`. Geçmiş derin (ISRG 2000'den, XOM/AMGN 1985'ten). İlk kayıt gelecekteki planlı tarih (gerçekleşenler boş) — filtrelenir. |
| `earnings-calendar?from=<geçmiş>` | **402** (Premium Query Parameter) | Kullanılmıyor. |
| `historical-price-eod/full?symbol=BZUSD` | 200 | Brent, 2007-07'den itibaren. |
| `historical-price-eod/full?symbol=CLUSD` | **402** | WTI yerine Brent (bkz. `gate_decisions.md`). |

`epsEstimated` / `revenueEstimated` (analist tahminleri) **kullanılmaz** (CLAUDE.md §1).

## Karşılaştırma yöntemi

Havuz: T0 envanterindeki tema sanayilerinde, ülkesi US olan ve SEC CIK'i bulunan 1.581 firma. Firmalar rastgele
sıralanır; her firmada 2012 sonrası FMP duyurularından biri rastgele seçilir; en yakın 8-K (Item 2.02) kabul zamanı
ile karşılaştırılır. 20 firma-çeyreğe ulaşınca durulur. **Uyuşma = aynı takvim günü** (ear_3d penceresi ve
`sue_announce` kullanılabilirliği tam güne bağlı olduğu için sıkı tanım).

## Sonuç

| Ölçüt | Değer |
|---|---|
| Aynı gün uyuşma | **16/20 = %80** |
| ±1 gün içinde | 18/20 = %90 |
| Karar eşiği (ROADMAP kapı 5) | ≥ %90 aynı gün |
| **Karar** | **8-K tarihleri kullanılır** (FMP yalnızca gerçekleşen EPS değeri için) |

Uyuşmayan 4 durum:

| Sembol | FMP tarihi | 8-K kabulü (ET) | Fark | Yorum |
|---|---|---|---|---|
| VTOL | 2023-11-02 | 2023-11-01 16:25 | −1 | FMP tepki gününü vermiş; duyuru bir önceki akşam. |
| THRM | 2012-11-01 | 2012-11-02 15:35 | +1 | 8-K ertesi gün dosyalanmış olabilir; hangisinin doğru olduğu kesin değil. |
| NXXT | 2023-08-22 | 2023-08-24 16:01 | +2 | FMP tarihi 8-K'dan 2 gün önce. |
| CSW | 2014-09-30 | 2015-11-16 16:09 | +412 | FMP tarihi çeyrek sonu (firma 2015'te ayrıldı); duyuru tarihi değil. |

## Önemli PIT düzeltmesi: EDGAR `acceptanceDateTime` UTC'dir

Bu karşılaştırma sırasında, submissions JSON'daki `acceptanceDateTime` alanının ("Z" ekli) **gerçekten UTC**
olduğu doğrulandı: dosyalama indeks sayfaları "Accepted 2024-02-01 16:12:25" (ET) gösterirken JSON
`2024-02-01T21:12:25Z` veriyor (3 dosyada birebir). Önceki kod bu değeri ET duvar saati sayıyordu; bu, 11:00–16:00 ET
arası kabul edilen dosyaları yanlışlıkla "kapanış sonrası" sayıp bir seans **geç** kullanılabilir yapıyordu (yani
sızıntı yok, gereğinden muhafazakâr) ve 20:00 ET sonrası dosyaları ertesi güne kaydırıyordu. Düzeltme:
`src/themes/membership.py::eastern_time` UTC → America/New_York dönüşümü (yaz saati dahil); T3 üyelik tablosu henüz
oluşturulmadığı için hiçbir sonuç etkilenmedi. Testler: `test_eastern_time_handles_dst`, gece yarısı sınırı testi.

## Uygulama (`src/features/earnings_events.py`, `src/themes/earnings.py`)

- Olay: her 8-K Item 2.02 (5 gün içindeki 8-K/A tekrarları aynı duyuru sayılır). `t0` = kabul günü (seans ve
  16:00 ET öncesiyse), aksi hâlde sonraki seans. `available_from` = `t0` + 1 seans.
- EPS: FMP `epsActual`, 8-K tarihine ±3 takvim günü içindeki en yakın FMP kaydı (her kayıt bir kez); eşleşme yoksa
  EPS boş (olay `ear_3d` için yine kullanılır).
- `sue_announce` = (EPS_q − EPS_{q−4}) / son 8 mevsimsel değişimin std'si; mevcut `sue` ile aynı kural (12 olay,
  ≥6 geçerli değişim, ±10 kırpma); q−4 eşleşmesi 300–430 gün aralığıyla denetlenir.
- `ear_3d` = Σ_{t0−1..t0+1}(r_i − r_ETF); son 90 gün içindeki en son olay, pencere yeniden dengeleme tarihinde
  tamamlanmış olmalı.
- Tablo: `earnings_events` (`python -m src.pipeline.themes t4b-events`, T1 bittikten sonra çalıştırılır).
- Bilinen sınırlama: 8-K, basın bülteninden sonra (4 iş gününe kadar) dosyalanabilir; 8-K tarihi bu durumda geç
  kalır — sızıntı yaratmaz ama `ear_3d` penceresi tepkiyi kaçırabilir. Item kodları 2004-08-23 reformundan beri var.

## Testler

`tests/test_earnings_events.py` (7): seans kuralları (açılış öncesi, kapanış sonrası, Cuma, hafta sonu), 8-K/A
tekrar birleştirme ve FMP ±3 gün eşleşmesi, `sue_announce` tanımı, `sue_announce` sızıntı enjeksiyonu, `ear_3d`
değeri + pencere tamamlanma + 90 gün sınırı, `ear_3d` sızıntı enjeksiyonu (gelecek fiyatlar ve gelecek olay),
Item 2.02 filtresi + UTC dönüşümü.
