# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Celery worker entrypoint for background jobs."""

from __future__ import annotations

import datetime as dt
import logging
import os
import statistics
from decimal import Decimal
from typing import Iterable, List, Optional

from celery import Celery
from celery.schedules import crontab
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import ProgrammingError

from crypto_service.market import fetch_market_chart, fetch_prices
from crypto_service.models.ai_model import AIModel
from crypto_service.models.ai_model_metric import AIModelMetric
from crypto_service.models.enums import AIModelStatus, PriceAlertCondition
from crypto_service.models.market_price import MarketPrice
from crypto_service.models.price_alert import PriceAlert
from crypto_service.notifications import send_email_notification, send_webhook_notification
from shared.database import SessionLocal, TimescaleSessionLocal
from shared.exceptions import ValidationError

broker_url = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
backend_url = os.getenv("CELERY_RESULT_BACKEND")

celery_app = Celery("woc", broker=broker_url, backend=backend_url)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "refresh-prices-5m": {
            "task": "woc.refresh_prices",
            "schedule": 300.0,
        },
        "evaluate-alerts-1m": {
            "task": "woc.evaluate_alerts",
            "schedule": 60.0,
        },
        "sync-market-history-daily": {
            "task": "woc.sync_market_history",
            "schedule": crontab(hour=2, minute=0),
        },
        "train-baseline-model-weekly": {
            "task": "woc.train_baseline_model",
            "schedule": crontab(hour=3, minute=0, day_of_week="sun"),
        },
    },
)

app = celery_app
logger = logging.getLogger(__name__)


def _default_symbols() -> List[str]:
    env_symbols = os.getenv("CRYPTO_REFRESH_SYMBOLS", "BTC,ETH,SOL,USDT")
    return [symbol.strip().upper() for symbol in env_symbols.split(",") if symbol.strip()]


def _store_market_prices(quotes: Iterable[dict], currency: str) -> int:
    if currency.lower() != "usd":
        return 0

    session_factories = [TimescaleSessionLocal, SessionLocal]
    inserted = 0

    for factory in session_factories:
        if factory is None:
            continue
        session = factory()
        try:
            for quote in quotes:
                session.add(
                    MarketPrice(
                        symbol=quote["symbol"],
                        price_usd=Decimal(str(quote["price"])),
                        volume_24h=Decimal(str(quote["volume_24h"] or 0)),
                        market_cap=Decimal(str(quote["market_cap"] or 0)),
                        timestamp=quote["last_updated"],
                    )
                )
                inserted += 1
            session.commit()
            return inserted
        except ProgrammingError:
            session.rollback()
            inserted = 0
        finally:
            session.close()
    return inserted


def _should_trigger(condition: PriceAlertCondition, price: Decimal, target: Decimal) -> bool:
    if condition == PriceAlertCondition.ABOVE:
        return price >= target
    return price <= target


def _load_training_prices(session: Session, symbol: str, days: int = 90) -> list[MarketPrice]:
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    return (
        session.execute(
            select(MarketPrice)
            .where(MarketPrice.symbol == symbol, MarketPrice.timestamp >= cutoff)
            .order_by(MarketPrice.timestamp.asc())
        )
        .scalars()
        .all()
    )


def _calculate_metrics(prices: list[MarketPrice]) -> dict:
    series = [float(item.price_usd) for item in prices]
    if len(series) < 5:
        return {}

    returns = []
    for idx in range(1, len(series)):
        prev = series[idx - 1]
        current = series[idx]
        if prev <= 0:
            continue
        returns.append((current - prev) / prev)

    if len(returns) < 2:
        return {}

    mean_return = statistics.mean(returns)
    volatility = statistics.pstdev(returns)
    mae = statistics.mean([abs(ret - mean_return) for ret in returns])

    return {
        "mean_return": mean_return,
        "volatility": volatility,
        "mae": mae,
    }


def _record_metric(
    session: Session,
    model_id: object,
    name: str,
    value: float,
    dataset_symbol: Optional[str],
    dataset_start: Optional[dt.datetime],
    dataset_end: Optional[dt.datetime],
    dataset_size: int,
) -> None:
    session.add(
        AIModelMetric(
            model_id=model_id,
            metric_name=name,
            metric_value=Decimal(str(value)),
            dataset_symbol=dataset_symbol,
            dataset_start=dataset_start,
            dataset_end=dataset_end,
            dataset_size=dataset_size,
        )
    )


@celery_app.task(name="woc.ping")
def ping() -> str:
    return "pong"


@celery_app.task(name="woc.refresh_prices")
def refresh_prices(symbols: Optional[List[str]] = None, vs_currency: str = "usd") -> dict:
    symbol_list = symbols or _default_symbols()
    if not symbol_list:
        return {"symbols": [], "inserted": 0}

    try:
        quotes = fetch_prices(symbol_list, vs_currency)
    except ValidationError as exc:
        return {"error": str(exc)}

    inserted = _store_market_prices(quotes, vs_currency)
    return {"symbols": symbol_list, "inserted": inserted}


@celery_app.task(name="woc.evaluate_alerts")
def evaluate_alerts() -> dict:
    session = SessionLocal()
    try:
        alerts = (
            session.execute(
                select(PriceAlert).where(PriceAlert.enabled.is_(True))
            )
            .scalars()
            .all()
        )

        if not alerts:
            return {"checked": 0, "triggered": 0}

        symbols = sorted({alert.symbol.upper() for alert in alerts})
        try:
            quotes = fetch_prices(symbols)
        except ValidationError as exc:
            return {"error": str(exc)}

        price_map = {quote["symbol"].upper(): Decimal(str(quote["price"])) for quote in quotes}

        triggered = 0
        now = dt.datetime.now(dt.timezone.utc)
        for alert in alerts:
            price = price_map.get(alert.symbol.upper())
            if price is None:
                continue
            if _should_trigger(alert.condition, price, Decimal(alert.target_price)):
                alert.triggered_at = now
                alert.enabled = False
                notified = False

                if alert.notify_on_trigger:
                    if alert.notify_email:
                        try:
                            send_email_notification(
                                to_address=alert.notify_email,
                                subject=f"Price alert triggered for {alert.symbol}",
                                body=(
                                    f"Symbol: {alert.symbol}\n"
                                    f"Condition: {alert.condition}\n"
                                    f"Target: {alert.target_price}\n"
                                    f"Price: {price}\n"
                                    f"Triggered at: {now.isoformat()}\n"
                                ),
                            )
                            notified = True
                        except Exception:
                            logger.warning("Alert email failed", exc_info=True)

                    if alert.webhook_url:
                        try:
                            send_webhook_notification(
                                alert.webhook_url,
                                payload={
                                    "alert_id": str(alert.id),
                                    "user_id": str(alert.user_id),
                                    "symbol": alert.symbol,
                                    "condition": alert.condition,
                                    "target_price": str(alert.target_price),
                                    "price": str(price),
                                    "triggered_at": now.isoformat(),
                                },
                            )
                            notified = True
                        except Exception:
                            logger.warning("Alert webhook failed", exc_info=True)

                if notified:
                    alert.last_notified_at = now
                triggered += 1

        session.commit()
        return {"checked": len(alerts), "triggered": triggered}
    finally:
        session.close()


@celery_app.task(name="woc.sync_market_history")
def sync_market_history(symbol: Optional[str] = None, days: int = 30) -> dict:
    symbols = [symbol.upper()] if symbol else _default_symbols()
    if not symbols:
        return {"symbols": [], "inserted": 0}

    session = TimescaleSessionLocal() if TimescaleSessionLocal is not None else SessionLocal()
    inserted = 0
    try:
        for symbol_item in symbols:
            series = fetch_market_chart(symbol_item, days=days)
            existing_ts = session.execute(
                select(MarketPrice.timestamp).where(MarketPrice.symbol == symbol_item)
            ).scalars().all()
            existing_set = {ts for ts in existing_ts}

            for item in series:
                if item["timestamp"] in existing_set:
                    continue
                session.add(
                    MarketPrice(
                        symbol=symbol_item,
                        price_usd=Decimal(str(item["price"])),
                        volume_24h=Decimal(str(item["volume_24h"] or 0)),
                        market_cap=Decimal(str(item["market_cap"] or 0)),
                        timestamp=item["timestamp"],
                    )
                )
                inserted += 1
        session.commit()
    finally:
        session.close()
    return {"symbols": symbols, "inserted": inserted}


@celery_app.task(name="woc.train_baseline_model")
def train_baseline_model(model_name: str = "baseline-returns", version: str = "baseline-returns-v1") -> dict:
    session = SessionLocal()
    try:
        existing = (
            session.execute(
                select(AIModel).where(
                    AIModel.model_name == model_name,
                    AIModel.version == version,
                    AIModel.status == AIModelStatus.ACTIVE,
                )
            )
            .scalars()
            .first()
        )
        if existing:
            return {"status": "exists", "model_id": str(existing.id)}

        session.query(AIModel).filter(
            AIModel.model_name == model_name,
            AIModel.status == AIModelStatus.ACTIVE,
        ).update({"status": AIModelStatus.ARCHIVED}, synchronize_session=False)

        model = AIModel(
            model_name=model_name,
            version=version,
            accuracy=Decimal("0"),
            deployment_date=dt.datetime.now(dt.timezone.utc),
            status=AIModelStatus.ACTIVE,
        )
        session.add(model)
        session.flush()

        metrics = {}
        dataset_symbol = None
        dataset_start = None
        dataset_end = None
        dataset_size = 0

        symbols = _default_symbols()
        if symbols:
            dataset_symbol = symbols[0]
            prices = []
            for factory in [TimescaleSessionLocal, None]:
                data_session = session if factory is None else factory()
                try:
                    prices = _load_training_prices(data_session, dataset_symbol, days=90)
                    break
                except ProgrammingError:
                    prices = []
                finally:
                    if data_session is not session:
                        data_session.close()

            if prices:
                dataset_start = prices[0].timestamp
                dataset_end = prices[-1].timestamp
                dataset_size = len(prices)
                metrics = _calculate_metrics(prices)

        for name, value in metrics.items():
            _record_metric(
                session,
                model_id=model.id,
                name=name,
                value=value,
                dataset_symbol=dataset_symbol,
                dataset_start=dataset_start,
                dataset_end=dataset_end,
                dataset_size=dataset_size,
            )

        if "mae" in metrics:
            accuracy = Decimal("1") - Decimal(str(metrics["mae"]))
            model.accuracy = max(Decimal("0"), accuracy)

        session.commit()
        session.refresh(model)
        return {"status": "trained", "model_id": str(model.id)}
    finally:
        session.close()
