"""Renders the Streamlit app headlessly against the synthetic end-to-end database."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

from tests.test_pipeline_e2e import e2e, env  # noqa: F401  (module fixtures)

APP = str(Path(__file__).resolve().parent.parent / "app" / "streamlit_app.py")


def test_dashboard_renders_all_views(e2e):  # noqa: F811
    from src.pipeline.common import open_context
    from src.pipeline.monthly_run import run_monthly
    run_monthly(open_context(), clients=e2e["clients"])  # ensure a completed production run exists
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    assert not at.exception, at.exception
    labels = [b.label for b in at.button]
    assert "RUN MONTHLY ANALYSIS" in labels
    assert len(at.tabs) == 7
    # every view rendered data rather than the empty-state message
    info_text = " ".join(i.value for i in at.info)
    assert "No completed monthly run yet" not in info_text
    assert "No backtest runs yet" not in info_text
    assert len(at.dataframe) >= 5


def test_dashboard_button_is_idempotent(e2e):  # noqa: F811
    at = AppTest.from_file(APP, default_timeout=300)
    at.run()
    at.checkbox[0].uncheck()  # do not refresh data inside the test
    at.button[0].click()
    at.run()
    assert not at.exception, at.exception
    from src.pipeline.common import open_context
    con = open_context().con
    runs = con.execute("SELECT count(*) FROM production_runs WHERE status = 'completed'").fetchone()[0]
    assert runs == 1  # the button returned the stored run instead of creating a duplicate
