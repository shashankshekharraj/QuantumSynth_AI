import json
import pickle
import numpy as np
import cirq
import os
import sys

# Use absolute package imports for Reasoning Engine compatibility
from quantum_agent.h2_vqe_engine import run_vqe
from quantum_agent.h2_vqe_circuit import create_h2_ansatz

def run_quantum_vqe(molecule_name: str, bond_length: float):
    """
    Runs a VQE calculation for a given molecule and bond length.
    
    Args:
        molecule_name (str): The name of the molecule (only 'H2' is supported).
        bond_length (float): The bond length in Angstroms (0.3 to 2.5).
        
    Returns:
        str: A JSON string containing the calculation results or an error message.
    """
    try:
        # Validate molecule name
        if molecule_name.upper() != "H2":
            return json.dumps({
                "error": f"Molecule '{molecule_name}' not supported. Only 'H2' is supported.",
                "status": "failed"
            })
            
        # Validate bond length
        if not (0.3 <= bond_length <= 2.5):
            return json.dumps({
                "error": f"Bond length {bond_length} out of range (0.3-2.5 A).",
                "status": "failed"
            })
            
        # Load Hamiltonians - file is now in the quantum_agent directory
        pickle_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../h2_hamiltonians.pkl'))
        if not os.path.exists(pickle_path):
            return json.dumps({
                "error": "Hamiltonian database (h2_hamiltonians.pkl) not found.",
                "status": "failed"
            })
            
        with open(pickle_path, 'rb') as f:
            h2_data = pickle.load(f)
            
        # Find the closest bond length in the database
        distances = sorted(h2_data.keys())
        closest_dist = min(distances, key=lambda x: abs(float(x) - bond_length))
        
        # Check if the closest distance is within a reasonable threshold (e.g., 0.1 A)
        if abs(closest_dist - bond_length) > 0.1:
            return json.dumps({
                "error": f"No pre-calculated Hamiltonian found near bond length {bond_length} A.",
                "status": "failed"
            })
            
        hamiltonian = h2_data[closest_dist]['qubit_hamiltonian']
        
        # Setup Qubits and Ansatz
        qubits = cirq.LineQubit.range(4)
        ansatz, parameters = create_h2_ansatz(qubits, num_layers=2)
        
        # Run VQE
        vqe_energy, _ = run_vqe(hamiltonian, ansatz, qubits, parameters, max_iter=1000, restarts=3)
        
        # Prepare Result
        result = {
            "molecule": "H2",
            "bond_length": float(closest_dist),
            "vqe_energy": float(vqe_energy),
            "method": "VQE (COBYLA)",
            "qubits_used": 4,
            "status": "success"
        }
        
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "failed"
        })

if __name__ == "__main__":
    # Example usage for testing
    if len(sys.argv) > 2:
        mol = sys.argv[1]
        dist = float(sys.argv[2])
        print(run_quantum_vqe(mol, dist))
    else:
        # Default test
        print(run_quantum_vqe("H2", 0.7414))
