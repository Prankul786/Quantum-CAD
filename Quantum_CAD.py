import re, os

def reed_muller_expression_multiple(TTs):
    """Takes multiple Truth Tables (lists) as input and returns the Reed-Muller expressions for each in the desired format."""
    # Determine the maximum number of inputs based on the size of the largest TT
    max_inputs = max(len(TT) for TT in TTs)
    num_inputs = {4: 2, 8: 3, 16: 4}.get(max_inputs, None)
    if num_inputs is None:
        raise ValueError("Unsupported Truth Table size. Only 4 (2 inputs), 8 (3 inputs), or 16 (4 inputs) are supported.")
    # Generate the input variable names
    inputs = [chr(97 + i) for i in range(num_inputs)]  # ['a', 'b'], ['a', 'b', 'c'], ['a', 'b', 'c', 'd']
    # Generate the output variable names 
    outputs = [f"{chr(97 + i)}0" for i in range(len(TTs))]  # ['a0', 'b0', 'c0', ...]
    equations = []
    for TT in TTs:
        n = len(TT)
        
        if n == 4:  # Case for 2 inputs
            rm_values = [
                TT[0],
                TT[0] ^ TT[2],
                TT[0] ^ TT[1],
                TT[0] ^ TT[1] ^ TT[2] ^ TT[3]
            ]
            terms = ["1", inputs[0], inputs[1], f"{inputs[0]}{inputs[1]}"]
        
        elif n == 8:  # Case for 3 inputs
            rm_values = [
                TT[0],
                TT[0] ^ TT[4],
                TT[0] ^ TT[2],
                TT[0] ^ TT[1],
                TT[0] ^ TT[4] ^ TT[2] ^ TT[6],
                TT[0] ^ TT[2] ^ TT[1] ^ TT[3],
                TT[0] ^ TT[1] ^ TT[4] ^ TT[5],
                TT[0] ^ TT[1] ^ TT[2] ^ TT[3] ^ TT[4] ^ TT[5] ^ TT[6] ^ TT[7]
            ]
            terms = ["1", inputs[0], inputs[1], inputs[2], 
                     f"{inputs[0]}{inputs[1]}", f"{inputs[1]}{inputs[2]}", 
                     f"{inputs[0]}{inputs[2]}", f"{inputs[0]}{inputs[1]}{inputs[2]}"]
            print(terms)
            print(rm_values)
        elif n == 16:  # Case for 4 inputs
            rm_values = [
                TT[0],
                TT[0] ^ TT[8],
                TT[0] ^ TT[4],
                TT[0] ^ TT[2],
                TT[0] ^ TT[1],
                TT[0] ^ TT[8] ^ TT[4] ^ TT[12],
                TT[0] ^ TT[4] ^ TT[2] ^ TT[6],
                TT[0] ^ TT[2] ^ TT[1] ^ TT[3],
                TT[0] ^ TT[8] ^ TT[2] ^ TT[10],
                TT[0] ^ TT[4] ^ TT[1] ^ TT[5],
                TT[0] ^ TT[8] ^ TT[1] ^ TT[9],
                TT[0] ^ TT[2] ^ TT[4] ^ TT[6] ^ TT[8] ^ TT[10] ^ TT[12] ^ TT[14],
                TT[0] ^ TT[1] ^ TT[2] ^ TT[3] ^ TT[4] ^ TT[5] ^ TT[6] ^ TT[7],
                TT[0] ^ TT[1] ^ TT[2] ^ TT[3] ^ TT[8] ^ TT[9] ^ TT[10] ^ TT[11],
                TT[0] ^ TT[1] ^ TT[4] ^ TT[5] ^ TT[8] ^ TT[9] ^ TT[12] ^ TT[13],
                TT[0] ^ TT[1] ^ TT[2] ^ TT[3] ^ TT[4] ^ TT[5] ^ TT[6] ^ TT[7] ^
                TT[8] ^ TT[9] ^ TT[10] ^ TT[11] ^ TT[12] ^ TT[13] ^ TT[14] ^ TT[15]
            ]
            terms = ["1", inputs[0], inputs[1], inputs[2], inputs[3],
                     f"{inputs[0]}{inputs[1]}", f"{inputs[1]}{inputs[2]}", 
                     f"{inputs[2]}{inputs[3]}", f"{inputs[0]}{inputs[2]}", 
                     f"{inputs[1]}{inputs[3]}", f"{inputs[0]}{inputs[3]}", 
                     f"{inputs[0]}{inputs[1]}{inputs[2]}", 
                     f"{inputs[1]}{inputs[2]}{inputs[3]}", 
                     f"{inputs[0]}{inputs[2]}{inputs[3]}", 
                     f"{inputs[0]}{inputs[1]}{inputs[3]}", 
                     f"{inputs[0]}{inputs[1]}{inputs[2]}{inputs[3]}"]
            print(terms)
        else:
            raise ValueError("Unsupported Truth Table size.")
        
        # Generate Reed-Muller expression
        rm_expr = " ⊕ ".join(terms[i] for i in range(len(rm_values)) if rm_values[i] == 1)
        equations.append(rm_expr)
    
    return inputs, outputs, equations


class QuantumCircuitSynthesizer:
    def __init__(self, equations, inputs, outputs):
        """Initialize relevent variables"""
        self.equations = equations
        self.inputs = inputs
        self.outputs = outputs
        self.num_inputs = len(self.inputs)
        self.num_outputs = len(self.outputs)
        self.num_qubits = self.num_inputs + self.num_outputs
        self.qubits = [{"input": "0" if i >= self.num_inputs else None, "output": None, "description": None} for i in range(self.num_qubits)]
        self.gate_circuit_description = []
        # Initializing the first n Qubits as raw input Qubits
        for i, inp in enumerate(self.inputs):
            self.qubits[i]["input"] = inp
            self.qubits[i]["output"] = inp
            self.qubits[i]["description"] = "-"

    def parse_term(self, term):
        return list(term)  

    def apply_toffoli(self, target_qubit, controls):
        if controls:
            control_str = ",".join(controls)
            gate_description = f"TOF{target_qubit + 1}({control_str})"
        else:
            gate_description = f"TOF{target_qubit + 1}()"
        self.qubits[target_qubit]["description"] = (self.qubits[target_qubit]["description"] or "") + gate_description
        self.gate_circuit_description.append(gate_description)

    def synthesize(self):
        """Main code to synthesize the ckt"""
        for i, (equation, output) in enumerate(zip(self.equations, self.outputs), start=self.num_inputs):
            terms = equation.split('⊕')  
            target_qubit = i
            self.qubits[target_qubit]["output"] = output
            # Check if the equation includes '1' and toggle the target qubit
            if "1" in [term.strip() for term in terms]:
                self.apply_toffoli(target_qubit, [])  
            # Apply Toffoli gates for other terms
            for term in terms:
                term = term.strip()
                if term == "1":
                    continue  
                controls = self.parse_term(term)
                self.apply_toffoli(target_qubit, controls)

    def print_circuit(self):
        # Print the gate circuit description
        print("Toffoli gates description (sequencial): ")
        print(" ".join(self.gate_circuit_description))
        print("where TOFi(x1,x2,...,xn) means input of toffoli gate is ith Qubit while x1*x2*...*xn is controlling bit")
        # Print the detailed circuit description
        print("\nQubit             Input   Output  Description")
        for i, qubit in enumerate(self.qubits, start=1):
            print(f"{i:<18}{qubit['input'] or '-':<8}{qubit['output'] or '-':<8}{qubit['description'] or '-'}")




def load_truth_tables_from_file(filename):
    """
    Reads Truth Tables from a text file. Each line is expected to contain a single truth table.
    Empty lines in the file will be ignored.
    """
    with open(filename, "r") as file:
        TTs = [
            list(map(int, line.strip().split())) 
            for line in file.readlines() 
            if line.strip()  # Ignore empty lines
        ]
    return TTs


# Getting folder where we are running tests
script_dir = os.path.dirname(os.path.abspath(__file__))
#getting test file from the folder
filename = os.path.join(script_dir,'input.txt')

TTs = load_truth_tables_from_file(filename)

# Generate Reed-Muller expressions for all input Truth Tables
inputs, outputs, equations = reed_muller_expression_multiple(TTs)
print(f"Inputs: {inputs}")
print(f"Outputs: {outputs}")
print(f"Equations: {equations}")
synthesizer = QuantumCircuitSynthesizer(equations, inputs, outputs)
synthesizer.synthesize()
synthesizer.print_circuit()

