# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""AI model registry routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from crypto_service.models.ai_model import AIModel
from crypto_service.models.ai_model_metric import AIModelMetric
from crypto_service.models.enums import AIModelStatus
from crypto_service.schemas.ai_models import AIModelMetricOut, AIModelOut
from shared.database import get_db
from shared.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/api/v1/crypto/ai/models", tags=["crypto-ai-models"])


@router.get("", response_model=list[AIModelOut])
def list_models(db: Session = Depends(get_db)) -> list[AIModelOut]:
    models = db.execute(
        select(AIModel).order_by(AIModel.deployment_date.desc())
    ).scalars().all()
    return [AIModelOut.model_validate(model) for model in models]


@router.get("/active", response_model=AIModelOut)
def get_active_model(db: Session = Depends(get_db)) -> AIModelOut:
    model = db.execute(
        select(AIModel)
        .where(AIModel.status == AIModelStatus.ACTIVE)
        .order_by(AIModel.deployment_date.desc())
    ).scalars().first()
    if not model:
        raise NotFoundError("No active model found")
    return AIModelOut.model_validate(model)


@router.get("/{model_id}/metrics", response_model=list[AIModelMetricOut])
def get_model_metrics(model_id: str, db: Session = Depends(get_db)) -> list[AIModelMetricOut]:
    try:
        model_uuid = UUID(model_id)
    except ValueError as exc:
        raise ValidationError("Invalid model id") from exc

    metrics = db.execute(
        select(AIModelMetric)
        .where(AIModelMetric.model_id == model_uuid)
        .order_by(AIModelMetric.created_at.desc())
    ).scalars().all()
    return [AIModelMetricOut.model_validate(metric) for metric in metrics]
