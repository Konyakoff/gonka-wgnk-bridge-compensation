"""Пути исследования и запись файлов — без сетевых и прикладных зависимостей.

Вынесено из common.py, чтобы расчётные модули (модель взлома моста, варианты компенсаций, самопроверка) запускались
с одним pandas — например, сторонним проверяющим на опубликованных данных.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class Paths:
    root: Path

    @property
    def raw(self) -> Path:
        return self.root / "raw"

    @property
    def model(self) -> Path:
        return self.root / "model"

    @property
    def charts(self) -> Path:
        return self.root / "charts"

    @property
    def report(self) -> Path:
        return self.root / "report"

    def ensure(self) -> "Paths":
        for p in (self.raw, self.model / "parquet", self.charts, self.report):
            p.mkdir(parents=True, exist_ok=True)
        return self


def _jsonable(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def save_json(obj, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1, default=_jsonable))
    tmp.replace(path)
    return path


def save_parquet(df: pd.DataFrame, path: Path) -> Path:
    """Пишет таблицу атомарно: сначала во временный файл, потом подменяет."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.parquet")
    df.to_parquet(tmp, index=False)
    tmp.replace(path)
    return path
