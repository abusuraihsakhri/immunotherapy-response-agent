# Immunotherapy Response Agent

> **Domain:** Clinical Decision Support & Biomedical Computing
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Immunotherapy Response Agent** is an advanced analytical and computational platform implementing TMB, MSI-H, PD-L1 & HLA-I Loss of Heterozygosity Predictor. It synthesizes TMB (mut/Mb), MSI-H/dMMR status, PD-L1 TPS/CPS, and HLA-I loss of heterozygosity to predict anti-PD-1/PD-L1 clinical response.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`Severity`** — dedicated module for severity evaluation and state verification.
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks.
- **`AgentAlert`** — dedicated module for agent alert evaluation and state verification.
- **`TMBScoreEvaluatorAgent`**: Specialized Sub-Agent 1 for immunotherapy-response-agent
- **`MSIStatusValidatorAgent`**: Specialized Sub-Agent 2 for immunotherapy-response-agent
- **`PDL1ExpressionHarmonizerAgent`**: Specialized Sub-Agent 3 for immunotherapy-response-agent

### 🏗️ Architecture

The project contains two parallel implementations:

- **`agents/`** — Enterprise package with Pydantic models, FastAPI REST API, HMAC-SHA256 audit trail, and Zero-PHI outbound guard
- **`immunotherapy_response_agent/`** — Clinical package with dataclass models and AMP/ASCO/CAP Somatic Variant Tiers standards
- **`immuno_mind.py`** — Standalone script for direct evaluation

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/immunotherapy-response-agent.git
cd immunotherapy-response-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

---

## 💻 CLI Quickstart & Usage

### 1. Single Case Audit
```bash
python cli.py audit --task-id TASK-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Air-Gapped Chat
```bash
python cli.py chat "What are the guidelines?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task / case identifier
- `--target`: Entity, patient key, or genomic target
- `--primary`: Primary domain measurement or score (float)
- `--secondary`: Secondary kinetic or confidence score (float)
- `--status`: Status code or phenotype descriptor
- `--critical`: Emergency escalation flag

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `case_id` | Parameter / observation metric | Required |
| `patient_synthetic_id` | Parameter / observation metric | Required |
| `metric_primary` | Parameter / observation metric | Required |
| `metric_secondary` | Parameter / observation metric | Required |
| `is_stat` | Parameter / observation metric | Required |
| `status_flag` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Security Configuration

Set the `AUDIT_SECRET_KEY` environment variable to a secure random value for production deployments:

```bash
export AUDIT_SECRET_KEY="your-secure-random-key-here"
```

If not set, a random key is generated at runtime (suitable for development/testing).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t immunotherapy-response-agent .
docker run -p 8000:8000 immunotherapy-response-agent
```

---

## 📁 Project Structure

```
immunotherapy-response-agent/
├── agents/                          # Enterprise package
│   ├── api.py                       # FastAPI REST endpoints
│   ├── base.py                      # Security, PHI guard, HMAC audit
│   ├── learning.py                  # Bayesian calibration engine
│   ├── llm_factory.py               # LLM provider factory
│   ├── metrics.py                   # Prometheus metrics collector
│   ├── models.py                    # Pydantic data models
│   ├── streamer.py                  # WebSocket telemetry
│   ├── supervisor.py                # Master orchestrator
│   └── workers.py                   # Specialized worker agents
├── immunotherapy_response_agent/    # Clinical package
│   ├── agents.py                    # Clinical sub-agents
│   ├── cli.py                       # Clinical CLI
│   ├── engine.py                    # Clinical algorithmic engine
│   ├── models.py                    # Clinical data models
│   └── server.py                    # Clinical FastAPI server
├── tests/                           # Test suite
│   ├── test_enrichment.py           # Enrichment module tests
│   └── test_immunotherapy_response_agent.py  # Core security & functionality tests
├── cli.py                           # Main CLI entry point
├── immuno_mind.py                   # Standalone evaluation script
├── enrichment.py                    # Enrichment feature suite
├── simulator.py                     # High-throughput stress simulator
├── web/index.html                   # Operations console UI
├── sample.csv                       # Sample batch input
├── sample_payload.json              # Sample API payload
├── benchmark_dataset.json           # Golden benchmark test suite
├── openapi_spec.json                # OpenAPI 3.1 specification
├── Dockerfile                       # Container build
├── docker-compose.yml               # Multi-container orchestration
└── pyproject.toml                   # Project metadata & dependencies
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
