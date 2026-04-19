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

import pytest

from schemas import PostingRequest


def test_posting_request_accepts_balanced_lines() -> None:
    payload = PostingRequest(
        reference="UNIT-001",
        lines=[
            {"account_id": "cash", "direction": "debit", "amount": "125.00", "currency": "usd"},
            {"account_id": "liability", "direction": "credit", "amount": "125.00", "currency": "USD"},
        ],
    )

    assert payload.lines[0].currency == "USD"
    assert payload.lines[1].currency == "USD"


def test_posting_request_rejects_imbalanced_lines() -> None:
    with pytest.raises(ValueError, match="Double-entry imbalance"):
        PostingRequest(
            reference="UNIT-002",
            lines=[
                {"account_id": "cash", "direction": "debit", "amount": "125.00", "currency": "USD"},
                {"account_id": "liability", "direction": "credit", "amount": "120.00", "currency": "USD"},
            ],
        )


def test_posting_request_rejects_mixed_currency() -> None:
    with pytest.raises(ValueError, match="same currency"):
        PostingRequest(
            reference="UNIT-003",
            lines=[
                {"account_id": "cash", "direction": "debit", "amount": "50.00", "currency": "USD"},
                {"account_id": "liability", "direction": "credit", "amount": "50.00", "currency": "EUR"},
            ],
        )
