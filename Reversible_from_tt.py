import math

class ReversibleFunction:
    def __init__(self, f, num_inputs, num_outputs):
        self.f = f
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.reversible_function = {}
        self.reversible_function_bits = {}
        self.make_reversible()

    def make_reversible(self):
        # Identify the maximum repetitions of output values
        output_counts = {}
        for output in self.f.values():
            if output not in output_counts:
                output_counts[output] = 0
            output_counts[output] += 1
        max_reps = max(output_counts.values())  
        num_garbage_outputs = math.ceil(math.log2(max_reps))  
        garbage_output_values = [bin(i)[2:].zfill(num_garbage_outputs) for i in range(2**num_garbage_outputs)]
        total_outputs = self.num_outputs + num_garbage_outputs
        # Add garbage outputs to make outputs unique
        unique_outputs = {}
        output_repeats = {}
        for key, output in self.f.items():
            if output not in output_repeats:
                output_repeats[output] = 0
            garbage_output = garbage_output_values[output_repeats[output]]
            padded_output = bin(output)[2:].zfill(self.num_outputs) + garbage_output
            unique_outputs[key] = int(padded_output, 2)
            output_repeats[output] += 1
        # Add garbage inputs to balance the input and output sizes
        num_garbage_inputs = max(0, total_outputs - self.num_inputs)
        garbage_input_values = [bin(i)[2:].zfill(num_garbage_inputs) for i in range(2**num_garbage_inputs)]
        total_inputs = self.num_inputs + num_garbage_inputs
        # Assign minterms for garbage inputs
        minterms = [i for i in range(2**total_inputs)]
        used_minterms = list(unique_outputs.keys())
        remaining_minterms = list(set(minterms) - set(used_minterms))
        for i in range(2**total_inputs):
            if i in unique_outputs:
                self.reversible_function[i] = unique_outputs[i]
            else:
                self.reversible_function[i] = remaining_minterms.pop(0)
        # Convert to bitstring representation
        self.reversible_function_bits = {
            bin(key)[2:].zfill(total_inputs): bin(value)[2:].zfill(total_outputs)
            for key, value in self.reversible_function.items()
        }

    def print_reversible_function(self):
        print("Reversible Function:")
        for input_bits, output_bits in sorted(self.reversible_function_bits.items()):
            print(f"{input_bits} -> {output_bits}")

    def print_as_output_lists(self):
        total_outputs = len(next(iter(self.reversible_function_bits.values())))
        output_lists = [[] for _ in range(total_outputs)]
        for output_bits in self.reversible_function_bits.values():
            for i, bit in enumerate(output_bits):
                output_lists[i].append(int(bit))
        print("\nOutput Lists:")
        for i, output_list in enumerate(output_lists):
            print(f"List {i + 1}: {output_list}")


f = {
    0b00: 0b1,
    0b01: 0b0,
    0b10: 0b1,
    0b11: 0b0,
}
num_inputs = 2
num_outputs = 1

# Create and display the reversible function
rf = ReversibleFunction(f, num_inputs, num_outputs)
rf.print_reversible_function()
rf.print_as_output_lists()
