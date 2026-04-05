# QuantumSynth AI
### Quantum Molecular Simulation Agent for Drug Discovery

![Python 3.10](https://img.shields.io/badge/Python-3.10-blue.svg)
![Vertex AI](https://img.shields.io/badge/Google%20Cloud-Vertex%20AI-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🧪 Overview
**QuantumSynth AI** is a specialized Variational Quantum Eigensolver (VQE) agent designed to accelerate drug discovery by providing high-precision molecular ground state energy calculations. The agent is deployed as a **Vertex AI Reasoning Engine**, leveraging Google Cloud's enterprise-grade infrastructure to serve quantum chemistry simulations at scale.

This project focuses on the **H2 molecule**, calculating ground state energies across varying atomic bond lengths to map the molecular potential energy surface with chemical accuracy.

## ✨ Features
- **4-Qubit VQE Simulation**: Utilizes a Hardware Efficient Ansatz (HEA) with 4 qubits to simulate the H2 molecule.
- **Pre-computed Quantum Dataset**: High-fidelity dataset covering 30 distinct bond lengths (0.3Å to 2.5Å) for rapid inference.
- **Vertex AI Reasoning Engine**: Fully deployed and active reasoning engine instance (**ID: 3890741191896989696**).
- **Multi-layer Safety Guardrails**: 
    - Domain validation for chemistry-specific queries.
    - Physical boundary enforcement for atomic bond lengths.
    - Grounding and uncertainty metadata included in every response.

## 🚀 Quick Start
To run the agent locally for verification:

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Execute Safety Tests**:
   ```bash
   python agent.py
   ```

## 🏗️ Architecture

```mermaid
flowchart TB
    subgraph USER["👤 User"]
        Q[/"What is H2 energy<br/>at 0.74 Angstrom?"/]
    end

    subgraph GCP["☁️ Google Cloud Platform"]
        subgraph VERTEX["Vertex AI Reasoning Engine"]
            RE["🧠 Reasoning Engine<br/>ID: 3890741191896989696"]

            subgraph AGENT["QuantumSynth_AI Agent"]
                GEMINI["🤖 Gemini 2.5 Flash"]
                SAFETY["🛡️ Safety Guardrails<br/>• Domain Validation<br/>• Range Check (0.3-2.5Å)<br/>• Grounding Enforcement"]
            end

            subgraph TOOLS["🔧 Tools"]
                LOOKUP["h2_energy_lookup()"]
            end
        end

        subgraph DATA["📊 Quantum Data"]
            CSV["h2_quantum_dataset.csv<br/>30 Pre-computed VQE Energies"]
            VQE["⚛️ VQE Results<br/>4-Qubit Circuit<br/>Hardware Efficient Ansatz"]
        end
    end

    subgraph RESPONSE["📤 Response"]
        R["Energy: -1.1342 Ha<br/>Method: VQE 4-qubit<br/>Uncertainty: ±0.002 Ha"]
    end

    Q --> RE
    RE --> GEMINI
    GEMINI --> SAFETY
    SAFETY --> LOOKUP
    LOOKUP --> CSV
    CSV --> VQE
    VQE --> LOOKUP
    LOOKUP --> GEMINI
    GEMINI --> R

    style GCP fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    style VERTEX fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    style AGENT fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    style DATA fill:#fce4ec,stroke:#e91e63,stroke-width:2px
    style SAFETY fill:#ffebee,stroke:#f44336,stroke-width:2px
```

### Component Details

| Component | File | Description |
|-----------|------|-------------|
| **Agent Core** | `agent.py` | Defines `QuantumSynth_AI` class with Gemini 2.5 Flash model and tool-calling logic |
| **Energy Lookup Tool** | `h2_energy_lookup()` | Retrieves pre-computed VQE energies with safety validation |
| **Quantum Dataset** | `h2_quantum_dataset.csv` | 30 bond lengths with VQE, FCI, and HF energies |
| **System Prompt** | `prompts/system_prompt.txt` | Agent persona and response guidelines |

### Data Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant R as 🧠 Reasoning Engine
    participant G as 🤖 Gemini
    participant S as 🛡️ Safety Check
    participant T as 🔧 Tool
    participant D as 📊 Dataset

    U->>R: "H2 energy at 0.74Å?"
    R->>G: Process Query
    G->>S: Validate Input

    alt Invalid Domain
        S-->>G: Redirect to molecules
    else Out of Range
        S-->>G: Range error (0.3-2.5Å)
    else Valid Query
        S->>T: h2_energy_lookup(0.74)
        T->>D: Find closest bond length
        D-->>T: VQE: -1.1342 Ha
        T-->>G: Result + Grounding
    end

    G-->>R: Formatted Response
    R-->>U: Energy with uncertainty
```

## 📸 Visual Audit & Screenshots
The repository includes a comprehensive visual audit of the system's performance and deployment status:

- `screenshot_1_code_architecture.png`: Shows the core agent logic and safety guardrails.
- `screenshot_2_local_execution.png`: Verification of precise JSON output for H2 at 0.74Å.
- `screenshot_3_deployment_status.png`: Confirmation of ACTIVE status on Vertex AI.
- `screenshot_4_remote_test.png`: Successful query to the deployed reasoning engine.
- `screenshot_5_regression_tests.png`: Dataset comparison showing chemical accuracy.
- `screenshot_6_performance_summary.png`: Final success metrics and 100% safety compliance.

## 🏆 Hackathon
This project was developed for the **TCS Google AI Ekata Hackathon**.
- **Track**: Track 2 - Build with Vertex AI.
- **Objective**: Demonstrating the power of Vertex AI Reasoning Engines in solving complex scientific problems.

---
**Audit Status**: 100% SUCCESSFUL | **Submission Ready**: YES
