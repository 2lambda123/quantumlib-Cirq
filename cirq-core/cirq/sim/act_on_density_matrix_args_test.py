# Copyright 2021 The Cirq Developers
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

import numpy as np
import pytest

import cirq


def test_decomposed_fallback():
    class Composite(cirq.Gate):
        def num_qubits(self) -> int:
            return 1

        def _decompose_(self, qubits):
            yield cirq.X(*qubits)

    qid_shape = (2,)
    tensor = cirq.to_valid_density_matrix(
        0, len(qid_shape), qid_shape=qid_shape, dtype=np.complex64
    )
    args = cirq.ActOnDensityMatrixArgs(
        target_tensor=tensor,
        available_buffer=[np.empty_like(tensor) for _ in range(3)],
        qubits=cirq.LineQubit.range(1),
        prng=np.random.RandomState(),
        log_of_measurement_results={},
        qid_shape=qid_shape,
    )

    cirq.act_on_qubits(Composite(), args, cirq.LineQubit.range(1))
    np.testing.assert_allclose(
        args.target_tensor, cirq.one_hot(index=(1, 1), shape=(2, 2), dtype=np.complex64)
    )


def test_cannot_act():
    class NoDetails:
        pass

    qid_shape = (2,)
    tensor = cirq.to_valid_density_matrix(
        0, len(qid_shape), qid_shape=qid_shape, dtype=np.complex64
    )
    args = cirq.ActOnDensityMatrixArgs(
        target_tensor=tensor,
        available_buffer=[np.empty_like(tensor) for _ in range(3)],
        qubits=cirq.LineQubit.range(1),
        prng=np.random.RandomState(),
        log_of_measurement_results={},
        qid_shape=qid_shape,
    )
    with pytest.raises(TypeError, match="Can't simulate operations"):
        cirq.act_on_qubits(NoDetails(), args, qubits=())


def test_axes_deprecation():
    qid_shape = (2,)
    state = cirq.to_valid_density_matrix(0, len(qid_shape), qid_shape=qid_shape, dtype=np.complex64)
    with cirq.testing.assert_deprecated("axes", deadline="v0.13"):
        args = cirq.ActOnDensityMatrixArgs(
            state,
            [],
            (1,),
            qubits=cirq.LineQubit.range(1),
            prng=np.random.RandomState(),
            log_of_measurement_results={},
            qid_shape=qid_shape,
        )
    with cirq.testing.assert_deprecated("axes", deadline="v0.13"):
        assert args.axes == (1,)
    assert args.qid_shape is qid_shape
    assert args.target_tensor is state

    with cirq.testing.assert_deprecated("axes", deadline="v0.13"):
        args = cirq.ActOnDensityMatrixArgs(
            state,
            [],
            (1,),
            qid_shape,
            qubits=cirq.LineQubit.range(1),
            prng=np.random.RandomState(),
            log_of_measurement_results={},
        )
    with cirq.testing.assert_deprecated("axes", deadline="v0.13"):
        assert args.axes == (1,)
    assert args.qid_shape is qid_shape
    assert args.target_tensor is state

    with cirq.testing.assert_deprecated("axes", deadline="v0.13"):
        args = cirq.ActOnDensityMatrixArgs(
            state,
            [],
            axes=(1,),
            qubits=cirq.LineQubit.range(1),
            prng=np.random.RandomState(),
            log_of_measurement_results={},
            qid_shape=qid_shape,
        )
    with cirq.testing.assert_deprecated("axes", deadline="v0.13"):
        assert args.axes == (1,)
    assert args.qid_shape is qid_shape
    assert args.target_tensor is state
