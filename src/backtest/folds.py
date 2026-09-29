"""Expanding-window walk-forward folds over monthly rebalance dates, with embargo and label purge metadata."""
from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd


@dataclass(frozen=True)
class Fold:
    fold_id: int
    train_start: pd.Timestamp
    train_end: pd.Timestamp      # last training rebalance date
    test_start: pd.Timestamp     # first test rebalance date
    test_end: pd.Timestamp       # end of the last test holding period (next rebalance or last session)
    embargo_dates: tuple         # rebalance dates skipped between train and test
    purge_label_days: int        # training labels ending on/after test_start must be dropped

    def to_dict(self) -> dict:
        d = asdict(self)
        return {k: (str(v.date()) if isinstance(v, pd.Timestamp) else
                    [str(x.date()) for x in v] if isinstance(v, tuple) else v) for k, v in d.items()}


def walk_forward_folds(dates: list[pd.Timestamp], last_session: pd.Timestamp, min_train_months: int,
                       test_months: int, embargo_months: int, purge_label_days: int) -> list[Fold]:
    dates = sorted(dates)
    folds = []
    train_end_i = min_train_months - 1
    k = 0
    while True:
        test_start_i = train_end_i + embargo_months + 1
        if test_start_i >= len(dates):
            break
        test_end_i = min(test_start_i + test_months - 1, len(dates) - 1)
        test_end = dates[test_end_i + 1] if test_end_i + 1 < len(dates) else last_session
        folds.append(Fold(k, dates[0], dates[train_end_i], dates[test_start_i], test_end,
                          tuple(dates[train_end_i + 1:test_start_i]), purge_label_days))
        k += 1
        train_end_i = test_end_i  # expanding window: next fold trains through this test block
        if test_end_i >= len(dates) - 1:
            break
    return folds


def purge_labels(labels: pd.DataFrame, fold: Fold) -> pd.DataFrame:
    """Training labels usable for ``fold``: rebalance <= train_end AND label window ends before test_start."""
    return labels[(labels["rebalance_date"] <= fold.train_end) & (labels["label_end_date"] < fold.test_start)]
