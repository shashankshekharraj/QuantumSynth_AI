import pickle
import numpy as np
import cirq
import sympy
from scipy.optimize import minimize
from h2_vqe_circuit import create_h2_ansatz

def qubit_operator_to_cirq(qubit_op, qubits):
    """Converts an OpenFermion QubitOperator to a cirq.PauliSum."""
    pauli_sum = cirq.PauliSum()
    for term, coefficient in qubit_op.terms.items():
        coeff = complex(coefficient)
        if not term: # Constant term
            pauli_sum += coeff
            continue
            
        ops = []
        for index, pauli_str in term:
            if pauli_str == 'X':
                ops.append(cirq.X(qubits[index]))
            elif pauli_str == 'Y':
                ops.append(cirq.Y(qubits[index]))
            elif pauli_str == 'Z':
                ops.append(cirq.Z(qubits[index]))
        
        pauli_sum += coeff * cirq.PauliString(ops)
    return pauli_sum

def get_energy_function(ansatz, pauli_sum, qubits, parameters):
    """Returns a function that calculates the expectation value for a given set of parameter values."""
    simulator = cirq.Simulator()
    
    def energy_func(param_values):
        param_dict = {p: v for p, v in zip(parameters, param_values)}
        resolved_circuit = cirq.resolve_parameters(ansatz, param_dict)
        
        # Calculate expectation value
        # Note: For efficiency in a real loop, we'd use a more direct method if available
        # but for 4 qubits, simulating the state vector is fine.
        result = simulator.simulate(resolved_circuit)
        expectation_value = pauli_sum.expectation_from_state_vector(result.final_state_vector, {q: i for i, q in enumerate(qubits)})
        return expectation_value.real

    return energy_func

def run_vqe(hamiltonian, ansatz, qubits, parameters, max_iter=200, tol=1e-6, restarts=2):
    """Runs VQE with restarts and returns the best result."""
    pauli_sum = qubit_operator_to_cirq(hamiltonian, qubits)
    energy_func = get_energy_function(ansatz, pauli_sum, qubits, parameters)
    
    best_energy = float('inf')
    best_params = None
    
    for i in range(restarts + 1):
        print(f"\n--- Restart {i} ---")
        initial_params = np.random.uniform(0, 2 * np.pi, len(parameters))
        
        iteration_count = 0
        def callback(xk):
            nonlocal iteration_count
            iteration_count += 1
            if iteration_count % 20 == 0:
                current_energy = energy_func(xk)
                print(f"Iteration {iteration_count:3d}: Energy = {current_energy:.6f} Hartree")

        res = minimize(
            energy_func, 
            initial_params, 
            method='COBYLA', 
            options={'maxiter': max_iter, 'tol': tol},
            callback=callback
        )
        
        if res.fun < best_energy:
            best_energy = res.fun
            best_params = res.x
            
        print(f"Restart {i} finished. Final Energy: {res.fun:.6f}")
        
    return best_energy, best_params

if __name__ == "__main__":
    # Load Hamiltonians
    with open('h2_hamiltonians.pkl', 'rb') as f:
        h2_data = pickle.load(f)
    
    # Target 0.74 Angstrom (equilibrium)
    # The keys in the pickle are likely rounded or strings, let's find the closest one
    target_dist = 0.74
    distances = sorted(h2_data.keys())
    closest_dist = min(distances, key=lambda x: abs(float(x) - target_dist))
    
    print(f"Targeting Bond Length: {closest_dist} Angstroms")
    hamiltonian = h2_data[closest_dist]['qubit_hamiltonian']
    fci_energy = h2_data[closest_dist]['fci_energy']
    hf_energy = h2_data[closest_dist]['hf_energy']
    
    # Setup Ansatz
    qubits = cirq.LineQubit.range(4)
    ansatz, parameters = create_h2_ansatz(qubits, num_layers=2)
    
    # Run VQE
    vqe_energy, vqe_params = run_vqe(hamiltonian, ansatz, qubits, parameters)
    
    print("\n" + "="*40)
    print(f"VQE Final Results for {closest_dist} A")
    print(f"VQE Energy: {vqe_energy:.6f} Hartree")
    print(f"HF Energy:  {hf_energy:.6f} Hartree")
    print(f"FCI Energy: {fci_energy:.6f} Hartree (Target)")
    print(f"Error:      {abs(vqe_energy - fci_energy):.6f} Hartree")
    print("="*40)
