/*
Copyright 2026 Bhargav (Wings of Capital)
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

const services = [
  { name: "Core Ledger", url: "http://localhost:8001/health" },
  { name: "AI Engine", url: "http://localhost:8002/health" },
  { name: "On-Chain Analytics", url: "http://localhost:8003/health" },
  { name: "Payment Gateway", url: "http://localhost:8004/health" },
  { name: "Fraud Detection", url: "http://localhost:8005/health" },
  { name: "KYC Service", url: "http://localhost:8006/health" }
];

async function fetchHealth(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) return "unhealthy";
    const data = await response.json();
    return data.status || "unknown";
  } catch {
    return "offline";
  }
}

async function render() {
  const grid = document.getElementById("service-grid");
  for (const service of services) {
    const status = await fetchHealth(service.url);
    const card = document.createElement("article");
    card.className = "card";
    card.innerHTML = `<h2>${service.name}</h2><p class="status">${status}</p>`;
    grid.appendChild(card);
  }
}

render();
