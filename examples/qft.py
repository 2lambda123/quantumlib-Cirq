# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import cirq
import numpy as np

def _cz_and_swap(q0, q1, rot):
    yield cirq.CZ(q0, q1)**rot
    yield cirq.SWAP(q0,q1)

# Create a quantum fourier transform circuit for 2*2 planar qubit architecture.
def generate_2x2_grid_qft_circuit() -> cirq.Circuit:

    # Define a 2*2 square grid of qubits.
    a,b,c,d = [cirq.google.XmonQubit(0, 0), cirq.google.XmonQubit(0, 1), cirq.google.XmonQubit(1, 0), cirq.google.XmonQubit(1, 1)]

    circuit = cirq.Circuit.from_ops(
        cirq.H(a),
        _cz_and_swap(a, b, 0.5),
        _cz_and_swap(b, c, 0.25),
        _cz_and_swap(c, d, 0.125),
        cirq.H(a),
        _cz_and_swap(a, b, 0.5),
        _cz_and_swap(b, c, 0.25),
        cirq.H(a),
        _cz_and_swap(a, b, 0.5),
        cirq.H(a),
        strategy=cirq.InsertStrategy.EARLIEST
    )
    return circuit


if __name__ == '__main__':
    """Demonstrates Quantum Fourier transform.
    """

    qft_circuit = generate_2x2_grid_qft_circuit()

    # Debug step
    print(qft_circuit)

    # Run and collect results
    simulator = cirq.google.Simulator()
    result = simulator.run(qft_circuit)
    print(np.around(result.final_states[0], 3))
