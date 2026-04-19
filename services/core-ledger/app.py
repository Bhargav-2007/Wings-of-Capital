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

from fastapi import FastAPI

app = FastAPI(title="Wings of Capital - Core Ledger")


@app.get("/health")
def health() -> dict:
    return {"service": "core-ledger", "status": "ok"}


@app.post("/ledger/posting")
def post_ledger_entry(payload: dict) -> dict:
    # Placeholder for double-entry validation and journal posting.
    return {"accepted": True, "payload": payload}
