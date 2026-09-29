"""DuckDB schema. Tables are append-oriented: historical decisions are versioned, never overwritten."""
from __future__ import annotations

from pathlib import Path

import duckdb

from src.config import database_path

SCHEMA_VERSION = 1

DDL = [
    """CREATE TABLE IF NOT EXISTS schema_info (key VARCHAR PRIMARY KEY, value VARCHAR)""",
    # --- reference / market data -------------------------------------------------------------------------
    """CREATE TABLE IF NOT EXISTS securities (
        symbol VARCHAR PRIMARY KEY,
        cik VARCHAR,
        name VARCHAR,
        exchange VARCHAR,
        sector VARCHAR,
        industry VARCHAR,
        sic INTEGER,
        sic_description VARCHAR,
        sector_group VARCHAR,
        classification_source VARCHAR,
        is_etf BOOLEAN,
        is_fund BOOLEAN,
        is_active BOOLEAN,
        ipo_date DATE,
        delisted_date DATE,
        first_price_date DATE,
        last_price_date DATE,
        reference_source VARCHAR,
        updated_at TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS daily_prices (
        symbol VARCHAR,
        date DATE,
        open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE,
        adj_close DOUBLE,
        volume DOUBLE,
        source VARCHAR,
        loaded_at TIMESTAMP,
        PRIMARY KEY (symbol, date)
    )""",
    """CREATE TABLE IF NOT EXISTS stock_splits (
        symbol VARCHAR,
        date DATE,
        ratio DOUBLE,
        source VARCHAR,
        PRIMARY KEY (symbol, date)
    )""",
    """CREATE TABLE IF NOT EXISTS data_load_status (
        item VARCHAR,
        key VARCHAR,
        status VARCHAR,
        detail VARCHAR,
        updated_at TIMESTAMP,
        PRIMARY KEY (item, key)
    )""",
    # PIT fundamental snapshots: one per company per filing-availability date.
    """CREATE TABLE IF NOT EXISTS fundamental_snapshots (
        cik VARCHAR,
        snapshot_date DATE,
        availability_date DATE,
        period_end DATE,
        payload JSON,
        facts_version VARCHAR,
        PRIMARY KEY (cik, snapshot_date)
    )""",
    # Normalized XBRL facts. availability_date = first date the fact may be used by the strategy.
    """CREATE TABLE IF NOT EXISTS financial_facts (
        cik VARCHAR,
        metric VARCHAR,
        concept VARCHAR,
        unit VARCHAR,
        period_start DATE,
        period_end DATE,
        duration_days INTEGER,
        fiscal_year INTEGER,
        fiscal_period VARCHAR,
        form VARCHAR,
        accn VARCHAR,
        filed_date DATE,
        availability_date DATE,
        value DOUBLE,
        loaded_at TIMESTAMP,
        PRIMARY KEY (cik, concept, unit, period_start, period_end, accn)
    )""",
    # --- research features --------------------------------------------------------------------------------
    """CREATE TABLE IF NOT EXISTS rebalance_universe (
        rebalance_date DATE,
        symbol VARCHAR,
        sector_group VARCHAR,
        base_eligible BOOLEAN,
        exclusion_reason VARCHAR,
        market_cap DOUBLE,
        adv20 DOUBLE,
        close DOUBLE,
        history_days INTEGER,
        shares_source VARCHAR,
        computed_at TIMESTAMP,
        PRIMARY KEY (rebalance_date, symbol)
    )""",
    """CREATE TABLE IF NOT EXISTS factor_values (
        rebalance_date DATE,
        symbol VARCHAR,
        feature VARCHAR,
        family VARCHAR,
        value DOUBLE,
        observation_period_end DATE,
        availability_date DATE,
        computed_at TIMESTAMP,
        PRIMARY KEY (rebalance_date, symbol, feature)
    )""",
    """CREATE TABLE IF NOT EXISTS technical_values (
        rebalance_date DATE,
        symbol VARCHAR,
        indicator VARCHAR,
        value DOUBLE,
        as_of_price_date DATE,
        computed_at TIMESTAMP,
        PRIMARY KEY (rebalance_date, symbol, indicator)
    )""",
    """CREATE TABLE IF NOT EXISTS forward_returns (
        rebalance_date DATE,
        symbol VARCHAR,
        horizon_days INTEGER,
        fwd_return DOUBLE,
        label_end_date DATE,
        PRIMARY KEY (rebalance_date, symbol, horizon_days)
    )""",
    # --- Jev ----------------------------------------------------------------------------------------------
    """CREATE TABLE IF NOT EXISTS jev_feature_sets (
        jev_feature_set_id VARCHAR PRIMARY KEY,
        provider VARCHAR,
        model_requested VARCHAR,
        resolved_model VARCHAR,
        state_schema_version VARCHAR,
        question_schema_version VARCHAR,
        questions_payload JSON,
        created_at TIMESTAMP,
        window_start DATE,
        window_end DATE,
        notes VARCHAR
    )""",
    """CREATE TABLE IF NOT EXISTS jev_decisions (
        decision_id VARCHAR PRIMARY KEY,
        cache_key VARCHAR,
        jev_feature_set_id VARCHAR,
        symbol VARCHAR,
        rebalance_date DATE,
        purpose VARCHAR,
        provider VARCHAR,
        model_requested VARCHAR,
        model_returned VARCHAR,
        resolved_model_version VARCHAR,
        state_schema_version VARCHAR,
        question_schema_version VARCHAR,
        state_hash VARCHAR,
        state_payload VARCHAR,
        questions_payload JSON,
        answers_payload JSON,
        probabilities_payload JSON,
        confidence_payload JSON,
        usage_payload JSON,
        input_tokens INTEGER,
        output_tokens INTEGER,
        cost_usd DOUBLE,
        market_cost_usd DOUBLE,
        latency_ms DOUBLE,
        provider_request_id VARCHAR,
        created_at TIMESTAMP,
        status VARCHAR,
        retry_count INTEGER,
        error_type VARCHAR,
        error_message VARCHAR
    )""",
    # Links (symbol, rebalance_date) states to cached evaluations; one state may serve many rows.
    """CREATE TABLE IF NOT EXISTS jev_state_index (
        jev_feature_set_id VARCHAR,
        symbol VARCHAR,
        rebalance_date DATE,
        purpose VARCHAR,
        cache_key VARCHAR,
        state_hash VARCHAR,
        created_at TIMESTAMP,
        PRIMARY KEY (jev_feature_set_id, symbol, rebalance_date, purpose)
    )""",
    """CREATE TABLE IF NOT EXISTS jev_candidate_sets (
        rebalance_date DATE,
        jev_feature_set_id VARCHAR,
        definition JSON,
        symbols JSON,
        created_at TIMESTAMP,
        PRIMARY KEY (rebalance_date, jev_feature_set_id)
    )""",
    # --- models & backtests -------------------------------------------------------------------------------
    """CREATE TABLE IF NOT EXISTS factor_models (
        model_id VARCHAR PRIMARY KEY,
        config JSON,
        description VARCHAR,
        created_at TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS model_versions (
        version_id VARCHAR PRIMARY KEY,
        model_id VARCHAR,
        role VARCHAR,
        as_of_date DATE,
        backtest_run_id VARCHAR,
        objective DOUBLE,
        decision JSON,
        created_at TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS promotion_decisions (
        decision_id VARCHAR PRIMARY KEY,
        as_of_date DATE,
        incumbent_version_id VARCHAR,
        challenger_version_id VARCHAR,
        promoted BOOLEAN,
        criteria JSON,
        evidence JSON,
        created_at TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS backtest_runs (
        run_id VARCHAR PRIMARY KEY,
        kind VARCHAR,
        created_at TIMESTAMP,
        git_commit VARCHAR,
        data_snapshot JSON,
        config JSON,
        jev_feature_set_id VARCHAR,
        seed INTEGER,
        folds JSON,
        metrics JSON,
        diagnostics JSON,
        status VARCHAR,
        notes VARCHAR
    )""",
    """CREATE TABLE IF NOT EXISTS backtest_fold_results (
        run_id VARCHAR,
        model_id VARCHAR,
        fold_id INTEGER,
        train_start DATE, train_end DATE, test_start DATE, test_end DATE,
        metrics JSON,
        PRIMARY KEY (run_id, model_id, fold_id)
    )""",
    """CREATE TABLE IF NOT EXISTS backtest_model_results (
        run_id VARCHAR,
        model_id VARCHAR,
        stage VARCHAR,
        objective DOUBLE,
        summary JSON,
        PRIMARY KEY (run_id, model_id)
    )""",
    """CREATE TABLE IF NOT EXISTS backtest_equity (
        run_id VARCHAR,
        series VARCHAR,
        date DATE,
        equity DOUBLE,
        PRIMARY KEY (run_id, series, date)
    )""",
    # --- production decisions -----------------------------------------------------------------------------
    """CREATE TABLE IF NOT EXISTS production_runs (
        run_key VARCHAR PRIMARY KEY,
        portfolio_id VARCHAR,
        rebalance_date DATE,
        model_version_id VARCHAR,
        status VARCHAR,
        started_at TIMESTAMP,
        finished_at TIMESTAMP,
        steps JSON,
        summary JSON
    )""",
    """CREATE TABLE IF NOT EXISTS monthly_rankings (
        run_key VARCHAR,
        rebalance_date DATE,
        model_version_id VARCHAR,
        symbol VARCHAR,
        rank INTEGER,
        previous_rank INTEGER,
        quant_score DOUBLE,
        jev_score DOUBLE,
        jev_confidence DOUBLE,
        final_score DOUBLE,
        family_scores JSON,
        family_percentiles JSON,
        in_jev_pool BOOLEAN,
        created_at TIMESTAMP,
        PRIMARY KEY (run_key, symbol)
    )""",
    """CREATE TABLE IF NOT EXISTS signal_history (
        run_key VARCHAR,
        portfolio_id VARCHAR,
        rebalance_date DATE,
        symbol VARCHAR,
        signal VARCHAR,
        reason_codes JSON,
        explanation JSON,
        rank INTEGER,
        previous_rank INTEGER,
        final_score DOUBLE,
        model_version_id VARCHAR,
        created_at TIMESTAMP,
        PRIMARY KEY (run_key, symbol)
    )""",
    """CREATE TABLE IF NOT EXISTS portfolio_positions (
        portfolio_id VARCHAR,
        as_of_date DATE,
        symbol VARCHAR,
        shares DOUBLE,
        entry_date DATE,
        entry_price DOUBLE,
        cost_basis DOUBLE,
        last_price DOUBLE,
        market_value DOUBLE,
        run_key VARCHAR,
        PRIMARY KEY (portfolio_id, as_of_date, symbol)
    )""",
    """CREATE TABLE IF NOT EXISTS portfolio_cash (
        portfolio_id VARCHAR,
        as_of_date DATE,
        cash DOUBLE,
        equity DOUBLE,
        run_key VARCHAR,
        PRIMARY KEY (portfolio_id, as_of_date)
    )""",
    """CREATE TABLE IF NOT EXISTS portfolio_transactions (
        txn_id VARCHAR PRIMARY KEY,
        portfolio_id VARCHAR,
        run_key VARCHAR,
        rebalance_date DATE,
        trade_date DATE,
        symbol VARCHAR,
        side VARCHAR,
        shares DOUBLE,
        price DOUBLE,
        gross_amount DOUBLE,
        commission DOUBLE,
        slippage_cost DOUBLE,
        transaction_cost DOUBLE,
        reason VARCHAR,
        status VARCHAR,
        created_at TIMESTAMP
    )""",
    # --- observability ------------------------------------------------------------------------------------
    """CREATE TABLE IF NOT EXISTS api_requests (
        ts TIMESTAMP,
        provider VARCHAR,
        endpoint VARCHAR,
        status_code INTEGER,
        from_cache BOOLEAN,
        latency_ms DOUBLE,
        error VARCHAR
    )""",
]


def connect(path: str | Path | None = None, read_only: bool = False) -> duckdb.DuckDBPyConnection:
    """Open (and initialize) the database. ':memory:' is supported for tests."""
    target = str(path) if path is not None else str(database_path())
    if target != ":memory:":
        Path(target).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(target, read_only=read_only)
    if not read_only:
        init_schema(con)
    return con


MIGRATIONS = [
    # reference market cap (screener snapshot) is used only to prioritize price downloads, never as a feature
    "ALTER TABLE securities ADD COLUMN IF NOT EXISTS reference_market_cap DOUBLE",
]


def init_schema(con: duckdb.DuckDBPyConnection) -> None:
    for stmt in DDL + MIGRATIONS:
        con.execute(stmt)
    con.execute(
        "INSERT INTO schema_info VALUES ('schema_version', ?) ON CONFLICT (key) DO UPDATE SET value = excluded.value",
        [str(SCHEMA_VERSION)],
    )


def upsert_df(con: duckdb.DuckDBPyConnection, table: str, df, key_cols: list[str], replace: bool = True) -> int:
    """Insert a DataFrame; on key conflict either replace (reference data) or keep the existing row."""
    if df is None or len(df) == 0:
        return 0
    cols = list(df.columns)
    col_list = ", ".join(cols)
    con.register("_upsert_src", df)
    try:
        if replace:
            updates = ", ".join(f"{c} = excluded.{c}" for c in cols if c not in key_cols)
            conflict = f"ON CONFLICT ({', '.join(key_cols)}) DO UPDATE SET {updates}" if updates else \
                f"ON CONFLICT ({', '.join(key_cols)}) DO NOTHING"
        else:
            conflict = f"ON CONFLICT ({', '.join(key_cols)}) DO NOTHING"
        con.execute(f"INSERT INTO {table} ({col_list}) SELECT {col_list} FROM _upsert_src {conflict}")
    finally:
        con.unregister("_upsert_src")
    return len(df)
