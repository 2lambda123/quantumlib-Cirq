# Copyright 2024 The Cirq Developers
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

"""A Gauge transformer for CZ**±0.5 gate."""


import numpy as np

from cirq.transformers.gauge_compiling.gauge_compiling import (
    GaugeTransformer,
    GaugeSelector,
    ConstantGauge,
    Gauge,
)
from cirq import ops

_SQRT_CZ = ops.CZ**0.5
_ADJ_S = ops.S**-1


class SqrtCZGauge(Gauge):

    def weight(self) -> float:
        return 3.0

    def sample(self, gate: ops.Gate, prng: np.random.Generator) -> ConstantGauge:
        if prng.choice([True, False]):
            return ConstantGauge(two_qubit_gate=gate)
        swap_qubits = prng.choice([True, False])
        if swap_qubits:
            return ConstantGauge(
                pre_q1=ops.X,
                post_q1=ops.X,
                post_q0=ops.S if gate == _SQRT_CZ else _ADJ_S,
                two_qubit_gate=gate**-1,
                swap_qubits=True,
            )
        else:
            return ConstantGauge(
                pre_q0=ops.X,
                post_q0=ops.X,
                post_q1=ops.S if gate == _SQRT_CZ else _ADJ_S,
                two_qubit_gate=gate**-1,
            )


SqrtCZGaugeTransformer = GaugeTransformer(
    target=ops.Gateset(ops.CZ**0.5, ops.CZ**-0.5),
    gauge_selector=GaugeSelector(gauges=[SqrtCZGauge()]),
)
