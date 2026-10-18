# Third-party components, data formats and datasets

Disclosed in full. Nothing here is a pre-built solution; all are libraries, public data or file formats.

## Libraries — backend
| Component | Licence | Use |
|---|---|---|
| FastAPI, Starlette, Pydantic, Uvicorn | MIT / BSD | API, validation, server |
| NumPy, SciPy | BSD | Monte Carlo, PERT sampling |
| NetworkX | BSD | Attack-path enumeration |
| PuLP | BSD | Integer-program modelling |
| HiGHS (`highspy`) | MIT | MIP solver |
| PyJWT | MIT | Session tokens |
| defusedxml | PSF | XXE-safe XML parsing |
| httpx | BSD | Optional Claude API calls |

## Libraries — frontend
| Component | Licence | Use |
|---|---|---|
| React, React DOM, React Router | MIT | UI |
| Vite, TypeScript | MIT / Apache-2.0 | Build |
| Tailwind CSS | MIT | Styling |
| @xyflow/react (React Flow) | MIT | Attack-path map |
| Recharts | MIT | Charts |
| lucide-react | ISC | Icons |
| @fontsource IBM Plex Sans, Space Grotesk | OFL-1.1 | Self-hosted fonts |

## Tooling
| Component | Licence | Use |
|---|---|---|
| Playwright | Apache-2.0 | Screenshots and walkthrough recording |
| ffmpeg | LGPL/GPL | Video conversion |
| pytest | MIT | Tests |

## Optional service
| Service | Use |
|---|---|
| Anthropic Claude API | Copilot phrasing and tool planning when `ANTHROPIC_API_KEY` is set; never computes figures |

## Data formats replayed (synthetic content)
Nmap XML · ProjectDiscovery Nuclei JSONL · Aqua Trivy JSON · Gitleaks JSON · Suricata EVE JSON · CISA KEV JSON · FIRST EPSS JSON.
All evidence content is synthetic and describes a fictional organisation.

## Public references used for calibration and mapping
IBM Cost of a Data Breach 2025 (India) · Cyentia IRIS 2025 · DPDP Act 2023 and Rules 2025 · CERT-In Directions 2022 ·
ISO/IEC 27001:2022 · NIST CSF 2.0 · CIS Controls v8.1 · RBI IT governance directions 2023 · MITRE ATT&CK.
See [research/references.md](research/references.md).
