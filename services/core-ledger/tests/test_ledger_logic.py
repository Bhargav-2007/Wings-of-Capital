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

from ledger import get_account_balance


class FakeQuery:
    def __init__(self, result):
        self._result = result

    def filter(self, *args, **kwargs):
        return self

    def scalar(self):
        return self._result


class FakeSession:
    def __init__(self, debit, credit):
        self._values = [debit, credit]

    def query(self, *args, **kwargs):
        return FakeQuery(self._values.pop(0))


def test_get_account_balance_calculates_net() -> None:
    session = FakeSession(debit=Decimal("300.00"), credit=Decimal("125.00"))
    result = get_account_balance(session=session, account_id="cash", currency="USD")

    assert result["debits"] == Decimal("300.00")
    assert result["credits"] == Decimal("125.00")
    assert result["net_balance"] == Decimal("175.00")
