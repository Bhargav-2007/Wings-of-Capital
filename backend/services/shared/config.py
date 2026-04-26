# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Shared configuration settings for Wings of Capital services."""

from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        extra="allow",
    )

    # Core service configuration
    service_name: str = Field(default="wings-of-capital", validation_alias="SERVICE_NAME")
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    debug: bool = Field(default=False, validation_alias="DEBUG")
    api_host: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")

    # CORS configuration
    allowed_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:8080"],
        validation_alias="ALLOWED_ORIGINS",
    )
    cors_allow_credentials: bool = Field(default=True, validation_alias="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: str = Field(default="GET,POST,PUT,DELETE,OPTIONS", validation_alias="CORS_ALLOW_METHODS")
    cors_allow_headers: str = Field(default="Content-Type,Authorization", validation_alias="CORS_ALLOW_HEADERS")

    # Database configuration
    database_url: str = Field(..., validation_alias="DATABASE_URL")
    timescale_url: Optional[str] = Field(default=None, validation_alias="TIMESCALE_URL")
    database_pool_size: int = Field(default=20, validation_alias="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=10, validation_alias="DATABASE_MAX_OVERFLOW")

    # Redis configuration
    redis_url: str = Field(default="redis://redis:6379/0", validation_alias="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, validation_alias="REDIS_PASSWORD")
    redis_ssl: bool = Field(default=False, validation_alias="REDIS_SSL")

    # Authentication and security
    jwt_secret_key: str = Field(..., validation_alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    jwt_expiry_minutes: int = Field(default=60, validation_alias="JWT_EXPIRY_MINUTES")
    jwt_refresh_expiry_days: int = Field(default=7, validation_alias="JWT_REFRESH_EXPIRY_DAYS")
    jwt_private_key: Optional[str] = Field(default=None, validation_alias="JWT_PRIVATE_KEY")
    jwt_public_key: Optional[str] = Field(default=None, validation_alias="JWT_PUBLIC_KEY")
    password_min_length: int = Field(default=12, validation_alias="PASSWORD_MIN_LENGTH")
    bcrypt_rounds: int = Field(default=12, validation_alias="BCRYPT_ROUNDS")

    # Vault configuration
    vault_addr: Optional[str] = Field(default=None, validation_alias="VAULT_ADDR")
    vault_token: Optional[str] = Field(default=None, validation_alias="VAULT_TOKEN")
    vault_path: str = Field(default="secret/wings", validation_alias="VAULT_PATH")

    # Logging configuration
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    log_format: str = Field(default="json", validation_alias="LOG_FORMAT")
    log_output: str = Field(default="stdout", validation_alias="LOG_OUTPUT")

    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, validation_alias="RATE_LIMIT_ENABLED")
    rate_limit_per_ip: int = Field(default=100, validation_alias="RATE_LIMIT_PER_IP")
    rate_limit_window_seconds: int = Field(default=60, validation_alias="RATE_LIMIT_WINDOW_SECONDS")

    # External services
    coingecko_api_key: Optional[str] = Field(default=None, validation_alias="COINGECKO_API_KEY")
    ethereum_rpc_url: Optional[str] = Field(default=None, validation_alias="ETHEREUM_RPC_URL")

    # Email configuration
    smtp_host: str = Field(default="smtp.gmail.com", validation_alias="SMTP_HOST")
    smtp_port: int = Field(default=587, validation_alias="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, validation_alias="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, validation_alias="SMTP_PASSWORD")
    smtp_from: Optional[str] = Field(default=None, validation_alias="SMTP_FROM")
    smtp_use_tls: bool = Field(default=True, validation_alias="SMTP_USE_TLS")

    # Frontend
    frontend_url: str = Field(default="http://localhost:8080", validation_alias="FRONTEND_URL")

    # MFA
    mfa_encryption_key: Optional[str] = Field(default=None, validation_alias="MFA_ENCRYPTION_KEY")

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: object) -> List[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            origins = [item.strip() for item in value.split(",") if item.strip()]
            return origins or ["http://localhost:8080"]
        return ["http://localhost:8080"]

    @field_validator("cors_allow_methods", "cors_allow_headers", mode="before")
    @classmethod
    def normalize_csv(cls, value: object) -> str:
        if isinstance(value, str):
            return ",".join([item.strip() for item in value.split(",") if item.strip()])
        return ""

    @property
    def cors_methods_list(self) -> List[str]:
        return [item for item in self.cors_allow_methods.split(",") if item]

    @property
    def cors_headers_list(self) -> List[str]:
        return [item for item in self.cors_allow_headers.split(",") if item]

    def __init__(self, **values: object) -> None:
        # Capture explicitly-provided constructor values so they can override
        # environment-derived defaults which BaseSettings may load.
        explicit_jwt = values.get("jwt_secret_key")
        super().__init__(**values)
        if explicit_jwt is not None:
            object.__setattr__(self, "jwt_secret_key", explicit_jwt)

    @property
    def jwt_signing_key(self) -> str:
        if self.jwt_algorithm.upper().startswith("RS"):
            if not self.jwt_private_key:
                raise ValueError("JWT_PRIVATE_KEY is required for RS algorithms")
            return self.jwt_private_key
        return self.jwt_secret_key

    @property
    def jwt_verification_key(self) -> str:
        if self.jwt_algorithm.upper().startswith("RS"):
            if not self.jwt_public_key:
                raise ValueError("JWT_PUBLIC_KEY is required for RS algorithms")
            return self.jwt_public_key
        return self.jwt_secret_key


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
