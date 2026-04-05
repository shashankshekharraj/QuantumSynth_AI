import os
import pandas as pd
from typing import Dict, Any
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
        return "You are QuantumSynth AI, an expert in quantum chemistry."

    def h2_energy_lookup(self, bond_length: float) -> Dict[str, Any]:
        """
        Looks up the pre-computed VQE ground state energy for the H2 molecule at a specific bond length.
        
        Args:
            bond_length: The distance between the two Hydrogen nuclei in Angstroms (e.g., 0.74).
            
        Returns:
            A dictionary with the molecule, bond_length, VQE energy, and simulation metadata.
        """
        import os
        # Robust path search
        possible_paths = [
            self.data_file,
            os.path.join(os.getcwd(), "h2_quantum_dataset.csv"),
            os.path.join(os.getcwd(), "quantum_agent", "h2_quantum_dataset.csv"),
            "/opt/python/lib/python3.9/site-packages/quantum_agent/h2_quantum_dataset.csv",
            "/home/jupyter/quantum_agent/h2_quantum_dataset.csv"
        ]
        
        actual_path = None
        for p in possible_paths:
            if os.path.exists(p):
                actual_path = p
                break
        
        if not actual_path:
            return {
                "error": f"Dataset file not found. Checked: {possible_paths}",
                "cwd": os.getcwd(),
                "pkg_dir": os.path.dirname(__file__),
                "pkg_listdir": os.listdir(os.path.dirname(__file__)) if os.path.exists(os.path.dirname(__file__)) else "NOT_FOUND"
            }
        
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
            "qubits_used": 4,
            "note": "Pre-computed using COBYLA optimizer"
        }

    def set_up(self):
        """Standard setup for Vertex Reasoning Engine."""
        vertexai.init(project=self.project_id, location=self.location)
        self.model = GenerativeModel(
            self.model_name,
            system_instruction=[self._system_instruction]
        )
        # Define the tool using from_func for simplicity
        self.tool = Tool(
            function_declarations=[
                FunctionDeclaration.from_func(self.h2_energy_lookup)
            ]
        )

    def query(self, input: str) -> str:
        """
        Processes a user query using the lookup tool and Vertex AI Gemini.
        """
        # Start a chat session
        chat = self.model.start_chat()
        
        # Initial request
        response = chat.send_message(input, tools=[self.tool])
        
        # Check for function call
        if response.candidates[0].function_calls:
            function_call = response.candidates[0].function_calls[0]
            if function_call.name == "h2_energy_lookup":
                # Execute the tool locally
                args = {k: v for k, v in function_call.args.items()}
                tool_result = self.h2_energy_lookup(**args)
                
                # Send the tool result back to the model
                response = chat.send_message(
                    Part.from_function_response(
                        name="h2_energy_lookup",
                        response={"result": tool_result}
                    )
                )
                
        return response.text

# Instance for deployment
root_agent = QuantumSynth_AI()
