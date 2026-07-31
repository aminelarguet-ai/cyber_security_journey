# 🚀 Building in Public: Road to AI Security Engineer (2026–2030)

A public, artifact-first build log toward becoming an **EU-remote AI Security Engineer**, following a **21-module roadmap across four years**.

Every module ships a **real, working artifact** — not just notes.

---

## Background

Second-year engineering prepa student in Tunisia, concours-bound (**Sept 2026 – June 2027**), heading into **SUP'COM's CySed track (2027–2030).**

No EU work visa, so this repository is the portfolio that has to speak for itself.

---

## Rules I Hold Myself To

- Every module ends with a **shippable artifact. No exceptions.**
- Total certification spending is capped at **$600.**
- The concours year (**Sept 2026 – June 2027**) is protected: only **one low-hour module** runs during it.

---

# 📍 Where Things Stand

| Phase | Window | Modules | Status |
|:------:|---------|---------|:------:|
| **0** | Summer 2026 | **01** Python Security Fundamentals | ✅ Done |
| **0** | Summer 2026 | **02** Linux Hardening & Shell Automation | 🔧 In Progress |
| **0** | Summer 2026 | **03** Packet-Level Network Literacy | ⏳ Not Started |
| **1** | Concours Year (Sep 2026 – Jun 2027) | **04** AI Governance & Risk Classification I | ⏳ Not Started |
| **2** | Summer 2027 | **05–07** Cloud IAM · LLM Security · STRIDE for AI | ⏳ Not Started |
| **3** | SUP'COM Year 1 | **08–10** DevSecOps · Applied Crypto · SOC Fundamentals | ⏳ Not Started |
| **4** | Summer 2028 | **11–12** Cloud Security (Azure) · MLOps Supply-Chain Security | ⏳ Not Started |
| **5** | SUP'COM Year 2 | **13–15** Zero Trust · Detection Engineering · AI-Augmented SOC | ⏳ Not Started |
| **6** | Summer 2029 | **16–17** Agentic AI Security · AI Governance II | ⏳ Not Started |
| **7** | SUP'COM Year 3 (CySed) | **18–20** IR for AI · Vendor Risk / EU AI Act · Offensive AI | ⏳ Not Started |
| **8** | Summer 2030 | **21** PFE Capstone — AI Security Architecture | ⏳ Not Started |

---

# 📚 Modules

| # | Module | Artifact | Repository |
|---:|---------|----------|------------|
| **01** | Python Security Fundamentals | Secrets hygiene, structured logging with redaction, CI pipeline (gitleaks + pip-audit + bandit) | `mod01` |
| **02** | Linux Hardening & Shell Automation | A hardened VM plus a script that gets it through CIS benchmarks without me clicking through menus | *In Progress* |
| **03** | Packet-Level Network Literacy | A Scapy-based traffic analyzer that actually parses things I care about | — |
| **04** | AI Governance & Risk Classification I | A blog series mapping the EU AI Act and NIST AI RMF classifications to real products | — |
| **05** | Cloud IAM Foundations | Azure Entra ID + AWS IAM policy-as-code that I can explain to an auditor | — |
| **06** | LLM Security Engineering | A RAG app plus a prompt-injection attack/defense suite I can demo | — |
| **07** | STRIDE Threat Modeling for AI Systems | A published threat model for an AI system I didn't build | — |
| **08** | DevSecOps Pipelines for AI Code | A reusable GitHub Actions security template I actually use | — |
| **09** | Applied Cryptography for AI Pipelines | A model-integrity verifier (SHA-256/GPG) for supply-chain paranoia | — |
| **10** | SOC Fundamentals & SIEM Basics | A homelab SIEM with detection rules that fire on real (lab) attacks | — |
| **11** | Cloud Security Engineering (Azure) | An IaC security baseline in Bicep or Terraform | — |
| **12** | MLOps & Model Supply-Chain Security | A model-registry security checklist + model card template | — |
| **13** | Network Security Automation & Zero Trust | A Python ACL/segmentation generator because clicking in GUIs doesn't scale | — |
| **14** | Linux Detection Engineering | An eBPF/auditd detection rule pack that catches things I used to miss | — |
| **15** | AI-Augmented SOC | An LLM alert-triage pipeline that hopefully doesn't hallucinate severity | — |
| **16** | Agentic AI Security | A sandboxed agent + tool-call-injection test suite | — |
| **17** | AI Governance II — Audit & Resilience | A NIST AI RMF audit-evidence checklist mapped to DORA | — |
| **18** | Incident Response for AI Systems | An IR playbook + a tabletop exercise I run with friends | — |
| **19** | AI Vendor Risk & EU AI Act Compliance | A vendor-risk assessment template with a worked example | — |
| **20** | Offensive Security for AI | An automated red-teaming harness I can point at my own stuff | — |
| **21** | PFE Capstone — AI Security Architecture | The full thesis: STRIDE + Zero Trust + AI-pipeline security + EU AI Act mapping | — |

> Each module's README covers the deliverable, estimated hours, prerequisites, and what I had to learn to get there.

---

# 🎓 Certification Ledger *(Hard Cap: $600)*

| Certification | Cost | Why I'm Taking It |
|--------------|-----:|-------------------|
| (ISC)² Certified in Cybersecurity | **$199** | Baseline credibility for governance/risk work (Module 4) |
| Microsoft SC-900 | **$99** | Cloud identity vocabulary for IAM foundations (Module 5) |
| Microsoft AZ-500 | **$165** | The Azure security depth I'll need in Module 11 |
| **Spent** | **$463** | |
| **Reserve** | **$137** | AWS CCP voucher first; cash only if the voucher path fails |

> CCNA and LPI-1/2 are school-funded through **SUP'COM**, so they don't touch this budget.

---

# 🎯 Why This Exists

Most **AI security** portfolios stop at the LLM layer with Python scripts that call an API.

This one is built to cover the **systems layer** — Linux internals, embedded systems, firmware, and RF/telecom — because that's the differentiated path available from an engineering-prepa background, not a bootcamp shortcut.

I want to understand AI security at the layer where the **model meets the kernel**, not just where the **model meets the prompt.**

---

If you're reading this because you're on a similar path—or because you're hiring and wondering whether the person behind this repository can actually think—the module READMEs are where the real work lives.

**This page is just the map.**
