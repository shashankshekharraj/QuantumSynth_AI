import pandas as pd
import numpy as np
import os
from pydantic import BaseModel, Field

# Constants
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "h2_quantum_dataset.csv")

class QuantumLookupInput(BaseModel):
    bond_length: float = Field(..., description="The distance between the two H nuclei in Angstroms.")

def get_h2_vqe_energy(bond_length: float):
    """
    Retrieves the pre-computed VQE energy for H2 at a given bond length from a dataset.
    
    Args:
        bond_length: The bond length of the H2 molecule in Angstroms.
        
    Returns:
        A dictionary containing the VQE energy and simulation metadata.
    """
    if not os.path.exists(DATA_FILE):
        return {"error": f"Dataset file not found at {DATA_FILE}"}
    
    df = pd.read_csv(DATA_FILE)
    
    # Find the closest bond length in the dataset
    idx = (df['bond_length'] - bond_length).abs().idxmin()
    closest_match = df.iloc[idx]
    
    return {
        "molecule": "H2",
        "requested_bond_length": bond_length,
        "matched_bond_length": float(closest_match['bond_length']),
        "vqe_energy": float(closest_match['vqe_energy']),
        "method": "VQE with 4-qubit Hardware Efficient Ansatz",
        "qubits_used": 4,
        "note": "Pre-computed using COBYLA optimizer (Hardware-Efficient Ansatz on simulator)"
    }
