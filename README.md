# Immunotherapy Response Agent

Deterministic Python audit utilities and a standalone browser demonstration for synthetic oncology-oriented inputs. The current algorithms are **not clinically validated** as TMB/MSI/PD-L1 interpretations or predictors of anti-PD-1/PD-L1 response.

## What works

- **Browser demonstration:** three local JavaScript worker rules, input validation, human-readable JSON output and JSON export, without sending entries to a server.
- **Operations CLI/API:** Pydantic payload validation, three configurable fixed worker checks, CSV batch processing, mock chat, and in-memory HMAC-SHA256 audit entries.
- **Legacy prototypes:** `immuno_mind.py` and `immunotherapy_response_agent/` expose separate rule sets and CLI/API interfaces. They are not interoperable models and are not validated treatment recommendation engines.

### Demonstration rules

| Worker | Trigger | Output |
| --- | --- | --- |
| InvariantQCWorker | Primary metric > 25 | Elevated |
| SafetyEscalationWorker | Secondary metric > 12 or explicit critical flag | Elevated, or critical when flagged |
| ProtocolConformanceWorker | Status contains DISCORDANT, ANOMALY, MUTANT, VIOLATION, FAIL or REJECT | Elevated |

Thresholds are illustrative software behavior only; they are **not clinical reference ranges, guideline cutoffs, or biomarker response estimates**. Results must not be used for diagnosis, triage, or treatment decisions.

## Browser demonstration

Open `web/index.html` from a static HTTP server:

```bash
python -m http.server 8080 --directory web
```

Visit `http://localhost:8080/`. The browser runs a local JavaScript port of the three operations worker rules. Python is **not** executed in the browser; a backend and Pyodide are unnecessary for this demonstration. GitHub Pages deployment is provided through `.github/workflows/pages.yml`, subject to repository Pages being enabled and configured for GitHub Actions.

## Python setup

Requires Python 3.10 or newer.

```bash
python -m pip install -e ".[api,test]"
python -m pytest -q
node --test web/app.test.cjs  # Node.js 22 recommended for the browser checks
```

Operations CLI:

```bash
python cli.py audit --task-id DEMO-01 --target SPECIMEN-01 --primary 28 --secondary 13
python cli.py batch --input sample.csv --output results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

Use `python -m immunotherapy_response_agent.cli audit` for the separate clinical-prototype rule set, or `python immuno_mind.py audit` for the standalone legacy version. Sample CSV fields `case_id`, `patient_synthetic_id`, `metric_primary`, `metric_secondary`, `is_stat`, and `status_flag` are accepted by the operations batch CLI as aliases. Invalid boolean tokens are skipped with a warning.

The operations API includes `GET /health`, `POST /api/audit`, `POST /api/chat`, `GET /api/audit/logs`, `GET /metrics` (JSON counters), and generated OpenAPI docs at `/docs`. The mock chat adapter does not call any language model. The development server also serves the static demonstration at `/` when the `web/` directory is present.

## Docker

```bash
export AUDIT_SECRET_KEY="$(openssl rand -hex 32)"
docker compose up --build
```

Do not commit the secret or use an identical key across deployments. Without an explicit key, the CLI generates an ephemeral random key on process startup; the Compose configuration requires a key.

## Privacy, limitations, and security

**Only synthetic, non-identifying inputs are appropriate.** The Python identifier guard checks selected patterns such as MRNs, emails, phone numbers and SSNs. It is **not a comprehensive PHI detector, HIPAA Safe Harbor de-identification mechanism, or proof of regulatory compliance**. Input files and API calls must be managed by the operator. The API has no authentication: bind it to localhost or protect it behind a trusted authenticated gateway, not the public internet.

Browser demonstration inputs stay in the current tab (unless the user explicitly exports JSON); no server calls, analytics, or browser storage are used. The Python services keep case and audit information in **process memory only**. Audit-chain integrity is verified with HMAC-SHA256 over each entry, but persistence, rotation, identity management and full regulatory audit controls are not implemented. The repository includes no external clinical model integration or prospective clinical validation.

## Development and testing

Python CI runs on 3.10, 3.11 and 3.12. Browser rules have Node.js regression tests. `web/` uses standards-based HTML, CSS and JavaScript without dependencies. The API uses FastAPI/Pydantic v2; the core utilities use Python.

## License

MIT. See [LICENSE](LICENSE).
