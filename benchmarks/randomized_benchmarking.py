# Copyright 2022 The Cirq Developers
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
from typing import Any, List, Iterable
import functools
import numpy as np
import cirq
import cirq.experiments.qubit_characterizations as ceqc


def unitary(val: Any) -> np.ndarray:
    return (
        functools.reduce(np.dot, [unitary(c) for c in val])
        if isinstance(val, Iterable)
        else cirq.unitary(val)
    )


class SingleQubitRandomizedBenchmarking:
    params = [[1, 10, 50, 100, 250, 500, 1000], [100], [20]]
    param_names = ["depth", "num_qubits", "num_circuits"]
    timeout = 600  # Change timeout to 10 minutes instead of default 60 seconds.

    def setup_cache(self):
        sq_xz_matrices = np.array(
            [unitary(group) for group in ceqc._single_qubit_cliffords().c1_in_xz]
        )
        sq_xz_cliffords: List[cirq.Gate] = [
            cirq.PhasedXZGate.from_matrix(mat) for mat in sq_xz_matrices
        ]
        with open("single_qubit_rb_rest.dat", "wb") as fd:
            cirq.to_json_gzip((sq_xz_matrices, sq_xz_cliffords), file_or_fn=fd)

    def setup(self, *_):
        with open("single_qubit_rb_rest.dat", "rb") as fd:
            self.sq_xz_matrices, self.sq_xz_cliffords = cirq.read_json_gzip(fd)

    def _get_op_grid(self, qubits: List[cirq.Qid], depth: int) -> List[List[cirq.Operation]]:
        op_grid: List[List[cirq.Operation]] = []
        for q in qubits:
            gate_ids = list(np.random.choice(len(self.sq_xz_cliffords), depth))
            op_sequence = [self.sq_xz_cliffords[id].on(q) for id in gate_ids]
            idx = ceqc._find_inv_matrix(unitary(op_sequence), self.sq_xz_matrices)
            op_sequence.append(self.sq_xz_cliffords[idx].on(q))
            op_grid.append(op_sequence)
        return op_sequence

    def time_rb_op_grid_generation(self, depth: int, num_qubits: int, num_circuits: int):
        qubits = cirq.GridQubit.rect(1, num_qubits)
        for _ in range(num_circuits):
            self._get_op_grid(qubits, depth)

    def time_rb_circuit_construction(self, depth: int, num_qubits: int, num_circuits: int):
        qubits = cirq.GridQubit.rect(1, num_qubits)
        for _ in range(num_circuits):
            op_grid = self._get_op_grid(qubits, depth)
            cirq.Circuit(
                [cirq.Moment(ops[d] for ops in op_grid) for d in range(depth + 1)],
                cirq.Moment(cirq.measure(*qubits)),
            )
