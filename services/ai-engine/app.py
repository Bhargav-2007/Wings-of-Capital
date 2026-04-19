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

app = FastAPI(title="Wings of Capital - AI Engine")


@app.get("/health")
def health() -> dict:
    return {"service": "ai-engine", "status": "ok"}


@app.post("/predict/price-direction")
def predict_price_direction(payload: dict) -> dict:
    # Placeholder model response until PyTorch pipeline is wired.
    return {"direction": "neutral", "confidence": 0.5, "input": payload}
