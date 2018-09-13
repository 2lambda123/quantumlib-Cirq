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

# pylint: disable=line-too-long
"""Create a circuit, optimize it, and map it onto a Bristlecone chip.

===EXAMPLE_OUTPUT===

Length 10 line on Bristlecone:
(5, 0)━━(5, 1)
        ┃
        (6, 1)━━(6, 2)
                ┃
                (7, 2)━━(7, 3)
                        ┃
                        (8, 3)━━(8, 4)
                                ┃
                                (9, 4)━━(9, 5)
Initial circuit:
0: ───×───────M('all')───
      │       │
1: ───×───×───M──────────
          │   │
2: ───×───×───M──────────
      │       │
3: ───×───×───M──────────
          │   │
4: ───×───×───M──────────
      │       │
5: ───×───×───M──────────
          │   │
6: ───×───×───M──────────
      │       │
7: ───×───×───M──────────
          │   │
8: ───×───×───M──────────
      │       │
9: ───×───────M──────────

Xmon circuit:
(5, 0): ───Y^-0.5───@───Y^0.5───@───────Y^-0.5───@──────────────────────────────────────────────────────────────────M('all')───
                    │           │                │                                                                  │
(5, 1): ───X^-0.5───@───X^0.5───@───────X^-0.5───@────────X^0.5───────────@───X^-0.5───@────────X^0.5───@───────────M──────────
                                                                          │            │                │           │
(6, 1): ───Y^-0.5───────@───────Y^0.5───@────────Y^-0.5───@───────Y^0.5───@───Y^-0.5───@────────Y^0.5───@───────────M──────────
                        │               │                 │                                                         │
(6, 2): ───X^-0.5───────@───────X^0.5───@────────X^-0.5───@───────X^0.5───────@────────X^-0.5───@───────X^0.5───@───M──────────
                                                                              │                 │               │   │
(7, 2): ───Y^-0.5───@───Y^0.5───@───────Y^-0.5───@────────Y^0.5───────────────@────────Y^-0.5───@───────Y^0.5───@───M──────────
                    │           │                │                                                                  │
(7, 3): ───X^-0.5───@───X^0.5───@───────X^-0.5───@────────X^0.5───────────@───X^-0.5───@────────X^0.5───@───────────M──────────
                                                                          │            │                │           │
(8, 3): ───Y^-0.5───────@───────Y^0.5───@────────Y^-0.5───@───────Y^0.5───@───Y^-0.5───@────────Y^0.5───@───────────M──────────
                        │               │                 │                                                         │
(8, 4): ───X^-0.5───────@───────X^0.5───@────────X^-0.5───@───────X^0.5───────@────────X^-0.5───@───────X^0.5───@───M──────────
                                                                              │                 │               │   │
(9, 4): ───Y^-0.5───@───Y^0.5───@───────Y^-0.5───@────────Y^0.5───────────────@────────Y^-0.5───@───────Y^0.5───@───M──────────
                    │           │                │                                                                  │
(9, 5): ───X^-0.5───@───X^0.5───@───────X^-0.5───@──────────────────────────────────────────────────────────────────M──────────
"""

import cirq


def main():
    print("Length 10 line on Bristlecone:")
    line = cirq.line_on_device(cirq.google.Bristlecone, length=10)
    print(line)

    print("Initial circuit:")
    n = 10
    depth = 2
    circuit = cirq.Circuit.from_ops(
        cirq.SWAP(cirq.LineQubit(j), cirq.LineQubit(j + 1))
        for i in range(depth)
        for j in range(i % 2, n - 1, 2)
    )
    circuit.append(cirq.measure(*cirq.LineQubit.range(n), key='all'))
    print(circuit)

    print()
    print("Xmon circuit:")
    translated = cirq.google.optimized_for_xmon(
        circuit=circuit,
        new_device=cirq.google.Bristlecone,
        qubit_map=lambda q: line[q.x])
    print(translated)


if __name__ == '__main__':
    main()
