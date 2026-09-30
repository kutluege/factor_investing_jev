"""Turkish report for the theme research run (THEMES_SPEC §7.9) and the pre-registration guard (CLAUDE.md §3)."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import PROJECT_ROOT
from src.themes.config import THEMES_PATH, file_sha256
from src.themes.research.run import WHY

PREREG_DIR = PROJECT_ROOT / "research" / "preregistration"


class PreregistrationError(RuntimeError):
    pass


def preregister(version: str, src: Path = THEMES_PATH) -> tuple[Path, str]:
    """Copy the config to research/preregistration/<version>.yaml and record its SHA256 (commit before running)."""
    PREREG_DIR.mkdir(parents=True, exist_ok=True)
    dst = PREREG_DIR / f"{version}.yaml"
    if dst.exists() and file_sha256(dst) != file_sha256(src):
        raise PreregistrationError(f"{dst} exists with different content; a changed config needs a new version")
    shutil.copyfile(src, dst)
    sha = file_sha256(dst)
    (PREREG_DIR / f"{version}.sha256").write_text(f"{sha}  {version}.yaml\n", encoding="utf-8")
    return dst, sha


def check_preregistration(version: str, src: Path = THEMES_PATH, require_committed: bool = True) -> str:
    """The research run refuses to start unless the live config equals the committed pre-registered copy."""
    dst = PREREG_DIR / f"{version}.yaml"
    if not dst.exists():
        raise PreregistrationError(f"missing {dst}; run t5-preregister and commit it first")
    sha = file_sha256(dst)
    recorded = (PREREG_DIR / f"{version}.sha256").read_text(encoding="utf-8").split()[0]
    if sha != recorded or file_sha256(src) != sha:
        raise PreregistrationError("config/themes.yaml differs from the pre-registered copy (new version required, "
                                   "docs/CHANGELOG_THEMES.md)")
    if require_committed:
        rel = dst.relative_to(PROJECT_ROOT).as_posix()
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=PROJECT_ROOT, capture_output=True)
        dirty = subprocess.run(["git", "status", "--porcelain", "--", rel, rel.replace(".yaml", ".sha256")],
                               cwd=PROJECT_ROOT, capture_output=True, text=True).stdout.strip()
        if tracked.returncode != 0 or dirty:
            raise PreregistrationError(f"{rel} must be committed before the research run")
    return sha


def _f(x, pct=False, d=3) -> str:
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "—"
    if isinstance(x, (bool, np.bool_)):
        return "✔" if x else "✘"
    if pct:
        return f"{x * 100:.2f}%"
    return f"{x:.{d}f}" if isinstance(x, (float, np.floating)) else str(x)


def _table(df: pd.DataFrame, cols: list[tuple[str, str, dict]]) -> list[str]:
    if df is None or df.empty:
        return ["_(veri yok)_", ""]
    head = "| " + " | ".join(c[1] for c in cols) + " |"
    sep = "|" + "---|" * len(cols)
    lines = [head, sep]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(_f(r.get(c[0]), **c[2]) for c in cols) + " |")
    return lines + [""]


def write_report(tables: dict[str, pd.DataFrame], out_dir: Path, run_id: str, prereg_sha: str, audit: dict,
                 consistency: dict | None, meta: dict) -> Path:
    md = [f"# Faktör açıklama raporu — themes_v1 (`{run_id}`)", "",
          "Bu rapor **tanımlayıcıdır**; faktör seçimi veya ağırlık öğrenmesi için kullanılmaz (THEMES_SPEC §7.9).",
          "", f"- Ön kayıt: `research/preregistration/themes_v1.yaml`, SHA256 `{prereg_sha}`",
          f"- Veri: {meta.get('start')} → {meta.get('end')}, {meta.get('dates')} ay; uygun satır {meta.get('rows')}",
          f"- Sızıntı denetimi: {audit}",
          "- Hedef: tema endeksinden arındırılmış ileri getiri (`label_fwd_<h>_theme`, maliyetsiz EW tema endeksi).",
          "- Faktörler yön işaretlidir (pozitif = beklenen yön). Faktörler yalnızca kullanıldıkları aşamadaki firmalarda "
          "incelenir; `ear_3d`, `sue_announce` hiçbir sette değildir (aday), tüm firmalarda incelenir.", "",
          "## Otomatik uyarılar", "",
          "- Örtüşen ufuklar (63/126 seans, aylık gözlem) t'yi şişirir: NW gecikmesi = ufuk/21 ve örtüşmeyen alt örnek "
          "t'si birlikte raporlanır.",
          "- Tek hisse getirisinde kesitsel R²'nin yüzde birkaç olması normaldir (kitap örneği: β, Size, BM ile R² ≈ %2,4).",
          "- Küçük temalar (aylık n < 15) gürültülüdür; bu aylar analiz dışıdır, sayılar aşağıda.",
          "- Yüksek t-istatistiği para kazandırmak demek değildir: ekonomik büyüklüğe ve maliyetlere bakın.", ""]
    if consistency:
        md += ["## Tutarlılık testi (`mom_12_1`, NASDAQ paneli, 21 seans)", "",
               f"Bu modülün IC fonksiyonu mevcut NASDAQ panelinde `mom_12_1` için IC = {_f(consistency['ic'])} "
               f"(t = {_f(consistency['t'], d=1)}, {consistency['months']} ay) verdi; `docs/FACTOR_IC.md`: "
               f"IC = {consistency['doc_ic']} (t = {consistency['doc_t']}). Fark {_f(consistency['diff'], d=4)} → "
               f"**{'tutarlı' if consistency['ok'] else 'TUTARSIZ'}**.", ""]
    counts = tables.get("counts")
    if counts is not None and not counts.empty:
        c = counts.set_index("rebalance_date")
        md += ["## Tema-tarih firma sayıları (uygun)", "", "| Tema | Ortalama | Min | Maks | n<15 ay |",
               "|---|---|---|---|---|"]
        md += [f"| {t} | {c[t].mean():.1f} | {c[t].min()} | {c[t].max()} | {(c[t] < 15).sum()} |" for t in c.columns]
        md += [""]
    dec = tables.get("decision", pd.DataFrame())
    md += ["## §7.9 Karar tablosu (126 seans)", "",
           "Çalışıyor = IC > 0 ve NW t ≥ 2 **ve** FM katsayısı aynı işaretli **ve** alt dönemlerin ≥ 2/3'ünde IC > 0 "
           "**ve** bağımlı sıralama farkı > 0. Çalışmayanlar bir sonraki sürümde gerekçeyle çıkarılabilir; sonuçlara "
           "bakıp yeni faktör eklenmez.", ""]
    md += _table(dec[dec["scope"].isin(["havuz", "robotics", "biotech", "energy"])] if not dec.empty else dec,
                 [("scope", "Kapsam", {}), ("factor", "Faktör", {}), ("ic_126", "IC", {}),
                  ("ic_126_nw_t", "NW t", {"d": 2}), ("ic_pozitif_t2", "IC>0,t≥2", {}), ("fm_ayni_isaret", "FM", {}),
                  ("altdonem_2_3", "Alt dönem", {}), ("bagimli_siralama_pozitif", "Bağımlı", {}),
                  ("calisiyor", "Çalışıyor", {})])
    ic = tables.get("ic", pd.DataFrame())
    for scope in [s for s in ["havuz", "robotics", "biotech", "energy"] if not ic.empty and s in set(ic["scope"])]:
        md += [f"## Kapsam: {scope}", ""]
        md += ["### 7.7 Rank IC", ""]
        md += _table(ic[ic["scope"] == scope].sort_values(["factor", "horizon"]),
                     [("factor", "Faktör", {}), ("horizon", "Ufuk", {}), ("ic_mean", "IC", {}),
                      ("ic_nw_t", "NW t", {"d": 2}), ("ic_nonoverlap_t", "Örtüşmesiz t", {"d": 2}),
                      ("ic_hit_rate", "IC>0 oranı", {"pct": True}), ("months", "Ay", {})])
        so = tables.get("sorts", pd.DataFrame())
        md += ["### 7.4 Tek değişkenli sıralama (EW; üst − alt = `mimic_`)", ""]
        md += _table(so[so["scope"] == scope].sort_values(["factor", "horizon"]) if not so.empty else so,
                     [("factor", "Faktör", {}), ("horizon", "Ufuk", {}), ("n_ports", "Port.", {}),
                      ("mimic_ew", "mimic EW", {"pct": True}), ("mimic_ew_t", "t", {"d": 2}),
                      ("mimic_vw", "mimic VW", {"pct": True}), ("top_minus_mean_ew", "Üst − ort.", {"pct": True}),
                      ("top_minus_mean_ew_t", "t", {"d": 2}), ("monotonic", "Monoton", {})])
        al = tables.get("alphas", pd.DataFrame())
        if not al.empty:
            a = al[(al["scope"] == scope)].pivot_table(index=["factor", "series"], columns="model",
                                                      values="alpha_t").reset_index()
            md += ["### 7.4 Alfalar (21 seans, aylık; NW t)", "", "Üst portföy RF üzeri; `mimic_ew` ham fark.", ""]
            md += _table(a, [("factor", "Faktör", {}), ("series", "Seri", {})] +
                         [(m, f"{m} t", {"d": 2}) for m in ("capm", "ff3", "carhart4", "ff5_mom") if m in a])
        dp = tables.get("dependent", pd.DataFrame())
        md += ["### 7.5 Bağımlı iki değişkenli sıralama (tema skoru terciliyle kontrol)", ""]
        md += _table(dp[dp["scope"] == scope].sort_values(["factor", "horizon"]) if not dp.empty else dp,
                     [("factor", "Faktör", {}), ("horizon", "Ufuk", {}), ("avg_diff", "Ort. fark", {"pct": True}),
                      ("nw_t", "NW t", {"d": 2})])
        fm = tables.get("fm", pd.DataFrame())
        if not fm.empty:
            f1 = fm[(fm["scope"] == scope) & (fm["target"] == "tema_arındırılmış") &
                    fm["variant"].isin(["ols_rank_normal", "ols_winsorized_raw", "wls_sqrt_mcap"])]
            wide = f1.pivot_table(index=["factor", "horizon"], columns="variant", values="nw_t").reset_index()
            eco = f1[f1["variant"] == "ols_rank_normal"][["factor", "horizon", "economic_magnitude", "avg_r2"]]
            wide = wide.merge(eco, on=["factor", "horizon"], how="left")
            md += ["### 7.6 Fama-MacBeth (tek faktör + β, ln(MktCap); NW t)", ""]
            md += _table(wide.sort_values(["factor", "horizon"]),
                         [("factor", "Faktör", {}), ("horizon", "Ufuk", {}),
                          ("ols_rank_normal", "OLS rank-normal t", {"d": 2}),
                          ("ols_winsorized_raw", "OLS ham t", {"d": 2}), ("wls_sqrt_mcap", "WLS √MktCap t", {"d": 2}),
                          ("economic_magnitude", "1 std etkisi", {"pct": True}), ("avg_r2", "Ort. R²", {"pct": True})])
            fa = fm[(fm["scope"] == scope) & (fm["variant"] == "ols_rank_normal_all")]
            if not fa.empty:
                md += ["Tüm faktörlü model (kapsama ≥ %50, eksiksiz satırlar):", ""]
                md += _table(fa.sort_values(["horizon", "factor"]),
                             [("horizon", "Ufuk", {}), ("factor", "Faktör", {}), ("coef", "Katsayı", {"pct": True}),
                              ("nw_t", "NW t", {"d": 2}), ("avg_adj_r2", "Ort. düz. R²", {"pct": True})])
        de = tables.get("descriptive", pd.DataFrame())
        md += ["### 7.1 Tanımlayıcı istatistikler (winsorize %0,5/%99,5; aylık değerlerin zaman ortalaması)", ""]
        md += _table(de[de["scope"] == scope] if not de.empty else de,
                     [("factor", "Faktör", {}), ("mean", "Ort.", {}), ("std", "Std", {}), ("skew", "Çarp.", {"d": 2}),
                      ("kurt", "Bas.", {"d": 2}), ("p5", "P5", {}), ("median", "Medyan", {}), ("p95", "P95", {}),
                      ("n", "n", {"d": 0}), ("mean_drift", "Ort. kayması", {"d": 2})])
        rd = tables.get("redundant", pd.DataFrame())
        vf = tables.get("vif", pd.DataFrame())
        md += ["### 7.2 Korelasyon ve çoklu doğrusallık", "",
               "Tam matris (alt üçgen Pearson, üst üçgen Spearman): `corr.csv`. |ρ| > 0,7 çiftleri:", ""]
        md += _table(rd[rd["scope"] == scope] if not rd.empty else rd,
                     [("a", "A", {}), ("b", "B", {}), ("pearson", "Pearson", {"d": 2}),
                      ("spearman", "Spearman", {"d": 2}), ("note", "Not", {})])
        v = vf[(vf["scope"] == scope) & (vf["vif"] > 5)] if not vf.empty else vf
        md += ["VIF > 5: " + (", ".join(f"`{r.factor}` ({r.vif:.1f})" for r in v.itertuples()) if not v.empty
                              else "yok"), ""]
        oc = tables.get("orth", pd.DataFrame())
        md += ["Ortogonalize (tema skoru + alt tema kuklaları sonrası artık) IC:", ""]
        md += _table(oc[(oc["scope"] == scope)].sort_values(["factor", "horizon"]) if not oc.empty else oc,
                     [("factor", "Faktör", {}), ("horizon", "Ufuk", {}), ("ic_mean", "Artık IC", {}),
                      ("ic_nw_t", "NW t", {"d": 2})])
        pe = tables.get("persistence", pd.DataFrame())
        md += ["### 7.3 Süreklilik (ρτ, aylık kesitsel sıra korelasyonu)", ""]
        md += _table(pe[pe["scope"] == scope] if not pe.empty else pe,
                     [("factor", "Faktör", {})] + [(f"rho_{L}", f"τ={L}", {"d": 2}) for L in (1, 3, 6, 12)])
        st = tables.get("stability", pd.DataFrame())
        if not st.empty:
            s = st[(st["scope"] == scope) & (st["horizon"] == 126)]
            bcols = [c for c in s.columns if c not in ("scope", "factor", "horizon")]
            md += ["### 7.8 İstikrar (126 seans IC ortalaması) ve ekonomik gerekçe", ""]
            s = s.assign(why=s["factor"].map(lambda f: WHY.get(f, ("", ""))[0]),
                         src=s["factor"].map(lambda f: WHY.get(f, ("", ""))[1]))
            md += _table(s, [("factor", "Faktör", {})] + [(c, c, {}) for c in bcols] +
                         [("why", "Neden çalışmalı", {}), ("src", "Kaynak", {})])
    md += ["## Dosyalar", "", "Tüm tablolar (alt temalar dahil): " +
           ", ".join(f"`{p.name}`" for p in sorted(out_dir.glob("*.csv")))]
    path = out_dir / "factor_explain.md"
    path.write_text("\n".join(md) + "\n", encoding="utf-8")
    return path
