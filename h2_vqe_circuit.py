import cirq
import sympy
import numpy as np

def create_h2_ansatz(qubits, num_layers=2):
    """
    Creates a 4-qubit Hardware Efficient Ansatz for H2.
    Structure: 
    Initial RY/RZ rotations (8 params)
    Layer 1: Ring CNOTs + RY/RZ rotations (8 params)
    Layer 2: Ring CNOTs + RY/RZ rotations (8 params)
    Total: 24 parameters.
    """
    circuit = cirq.Circuit()
    params = []
    num_qubits = len(qubits)
    
    # Initial rotation layer (Layer 0)
    for i in range(num_qubits):
        ry_sym = sympy.Symbol(f'p{len(params)}')
        rz_sym = sympy.Symbol(f'p{len(params)+1}')
        circuit.append(cirq.ry(ry_sym)(qubits[i]))
        circuit.append(cirq.rz(rz_sym)(qubits[i]))
        params.extend([ry_sym, rz_sym])
        
    for layer in range(1, num_layers + 1):
        # Entanglement (Ring pattern: 0-1, 1-2, 2-3, 3-0)
        for i in range(num_qubits):
            control = qubits[i]
            target = qubits[(i + 1) % num_qubits]
            circuit.append(cirq.CNOT(control, target))
            
        # Subsequent rotation layers
        for i in range(num_qubits):
            ry_sym = sympy.Symbol(f'p{len(params)}')
            rz_sym = sympy.Symbol(f'p{len(params)+1}')
            circuit.append(cirq.ry(ry_sym)(qubits[i]))
            circuit.append(cirq.rz(rz_sym)(qubits[i]))
            params.extend([ry_sym, rz_sym])
            
    return circuit, params

if __name__ == "__main__":
    # Define 4 qubits
    qubits = cirq.LineQubit.range(4)
    
    # Create the H2 ansatz
    ansatz, parameters = create_h2_ansatz(qubits, num_layers=2)
    
    print("--- H2 Hardware Efficient Ansatz (4 Qubits, 2 Layers) ---")
    print(ansatz)
    print(f"\nTotal parameters: {len(parameters)}")
    
    # Verify parameter count
    assert len(parameters) == 24, f"Expected 24 parameters, got {len(parameters)}"
