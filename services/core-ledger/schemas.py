# Copyright 2026 Bhargav (Wings of Capital)
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

Direction = Literal["debit", "credit"]


class PostingLine(BaseModel):
    account_id: str = Field(min_length=2, max_length=64)
    direction: Direction
    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=8)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class PostingRequest(BaseModel):
    reference: str | None = Field(default=None, max_length=128)
    lines: list[PostingLine] = Field(min_length=2)

    @model_validator(mode="after")
    def validate_balanced(self) -> "PostingRequest":
        debit_total = sum(line.amount for line in self.lines if line.direction == "debit")
        credit_total = sum(line.amount for line in self.lines if line.direction == "credit")

        if debit_total != credit_total:
            raise ValueError("Double-entry imbalance: total debits must equal total credits")

        currencies = {line.currency for line in self.lines}
        if len(currencies) != 1:
            raise ValueError("All lines in a journal entry must use the same currency")

        return self


class PostingResponse(BaseModel):
    accepted: bool
    entry_id: str
    reference: str
    total_debits: Decimal
    total_credits: Decimal
    currency: str
    line_count: int
    reconciliation_task_id: str | None


class LedgerLineResponse(BaseModel):
    account_id: str
    direction: Direction
    amount: Decimal
    currency: str


class JournalEntryResponse(BaseModel):
    entry_id: str
    reference: str
    currency: str
    created_at: str
    lines: list[LedgerLineResponse]


class JournalListResponse(BaseModel):
    items: list[JournalEntryResponse]
    count: int


class AccountBalanceResponse(BaseModel):
    account_id: str
    currency: str
    debits: Decimal
    credits: Decimal
    net_balance: Decimal
