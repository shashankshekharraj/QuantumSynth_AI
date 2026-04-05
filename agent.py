import os
import pandas as pd
import json
from typing import Dict, Any, Union
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, Part

class QuantumSynth_AI:
    def __init__(self):
        self.project_id = "tcs-1770741140578"
        self.location = "us-central1"
        self.model_name = "gemini-2.5-flash"
        self.data_file = os.path.join(os.path.dirname(__file__), "h2_quantum_dataset.csv")
        self._system_instruction = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r") as f:
                return f.read()
        return "You are QuantumSynth AI, an expert in quantum chemistry molecular simulations."

    def h2_energy_lookup(self, bond_length: float, query: str = "") -> Dict[str, Any]:
        """
        Looks up the pre-computed VQE ground state energy for the H2 molecule at a specific bond length.
        
        Args:
            bond_length: The atomic bond length in Angstroms.
            query: The original user query for safety validation.
        """
        # 1. Safety Check: Molecule-related keywords
        keywords = ["h2", "hydrogen", "energy", "bond", "angstrom"]
        query_lower = query.lower()
        if query and not any(k in query_lower for k in keywords):
            return {
                "error": "I specialize in quantum molecular simulations. Please ask about H2 ground state energy."
            }

        # 2. Safety Check: Bond length range
        if bond_length < 0.3 or bond_length > 2.5:
            return {
                "error": f"Bond length {bond_length} is outside simulation range. Supported range: 0.3 to 2.5 Angstroms."
            }

        # Lookup logic
        possible_paths = [
            self.data_file,
            os.path.join(os.getcwd(), "h2_quantum_dataset.csv"),
            os.path.join(os.getcwd(), "quantum_agent", "h2_quantum_dataset.csv"),
            "/home/jupyter/quantum_agent/h2_quantum_dataset.csv"
        ]
        
        actual_path = None
        for p in possible_paths:
            if os.path.exists(p):
                actual_path = p
                break
        
        if not actual_path:
            return {"error": "Dataset file not found."}
        
        df = pd.read_csv(actual_path)
        # Find the closest bond length in the dataset
        idx = (df['bond_length'] - bond_length).abs().idxmin()
        closest_match = df.iloc[idx]
        
        return {
            "molecule": "H2",
            "requested_bond_length": float(bond_length),
            "matched_bond_length": float(closest_match['bond_length']),
            "vqe_energy": float(closest_match['vqe_energy']),
            "method": "VQE with 4-qubit Hardware Efficient Ansatz",
            "grounding": "Calculated using Variational Quantum Eigensolver VQE with 4-qubit quantum circuit",
            "uncertainty": "plus minus 0.002 Hartree chemical accuracy",
            "status": "SUCCESS"
        }

    def set_up(self):
        """Standard setup for Vertex Reasoning Engine."""
        vertexai.init(project=self.project_id, location=self.location)
        self.model = GenerativeModel(
            self.model_name,
            system_instruction=[self._system_instruction]
        )
        self.tool = Tool(
            function_declarations=[
                FunctionDeclaration.from_func(self.h2_energy_lookup)
            ]
        )

    def query(self, input_text: str) -> str:
        """
        Processes a user query using the lookup tool and Vertex AI Gemini.
        """
        chat = self.model.start_chat()
        response = chat.send_message(input_text, tools=[self.tool])
        
        if response.candidates[0].function_calls:
            function_call = response.candidates[0].function_calls[0]
            if function_call.name == "h2_energy_lookup":
                args = {k: v for k, v in function_call.args.items()}
                # Pass the original query for safety validation
                args["query"] = input_text
                tool_result = self.h2_energy_lookup(**args)
                
                response = chat.send_message(
                    Part.from_function_response(
                        name="h2_energy_lookup",
                        response={"result": tool_result}
                    )
                )
                
        return response.text

root_agent = QuantumSynth_AI()

if __name__ == "__main__":
    import sys
    
    print("--- RUNNING LOCAL SAFETY TESTS ---")
    
    # Test 1: Out-of-domain query
    q1 = "What is the weather?"
    print(f"\nQUERY 1: {q1}")
    res1 = root_agent.h2_energy_lookup(0.0, query=q1)
    print(json.dumps(res1, indent=4))
    
    # Test 2: Valid query
    q2 = "H2 at 0.74 Angstrom"
    print(f"\nQUERY 2: {q2}")
    res2 = root_agent.h2_energy_lookup(0.74, query=q2)
    print(json.dumps(res2, indent=4))
    
    # Test 3: Out of range
    q3 = "H2 at 5.0 Angstrom"
    print(f"\nQUERY 3: {q3}")
    res3 = root_agent.h2_energy_lookup(5.0, query=q3)
    print(json.dumps(res3, indent=4))
