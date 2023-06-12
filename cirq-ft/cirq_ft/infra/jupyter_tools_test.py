# Copyright 2023 The Cirq Developers
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
import cirq_ft
import cirq_ft.infra.testing as cq_testing
import IPython.display
import ipywidgets
from cirq_ft.infra.jupyter_tools import display_gate_and_compilation, svg_circuit


def test_svg_circuit():
    g = cq_testing.GateHelper(cirq_ft.And(cv=(1, 1, 1)))
    svg = svg_circuit(g.circuit, g.r)
    svg_str = svg.data

    # check that the order is respected in the svg data.
    assert svg_str.find('control') < svg_str.find('ancilla') < svg_str.find('target')


def test_display_gate_and_compilation(monkeypatch):
    call_args = []

    def _dummy_display(stuff):
        call_args.append(stuff)

    monkeypatch.setattr(IPython.display, "display", _dummy_display)
    g = cq_testing.GateHelper(cirq_ft.And(cv=(1, 1, 1)))
    display_gate_and_compilation(g)

    (display_arg,) = call_args
    assert isinstance(display_arg, ipywidgets.HBox)
    assert len(display_arg.children) == 2


def test_circuit_with_costs():
    g = cq_testing.GateHelper(cirq_ft.And(cv=(1, 1, 1)))
    circuit = cirq_ft.infra.jupyter_tools.circuit_with_costs(g.circuit)
    expected_circuit = cirq.Circuit(g.operation.with_tags('t:8,r:0'))
    cirq.testing.assert_same_circuits(circuit, expected_circuit)
