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
"""Tests for channels."""
import numpy as np
import pytest

import cirq


def apply_channel(channel: cirq.SupportsChannel, rho: np.ndarray) -> np.ndarray:
    ks = cirq.channel(channel)
    d_out, d_in = ks[0].shape
    assert rho.shape == (d_in, d_in)
    out = np.zeros((d_out, d_out), dtype=np.complex128)
    for k in ks:
        out += k @ rho @ k.conj().T
    return out


def expected_choi(channel: cirq.SupportsChannel) -> np.ndarray:
    ks = cirq.channel(channel)
    d_out, d_in = ks[0].shape
    d = d_in * d_out
    c = np.zeros((d, d), dtype=np.complex128)
    for i in range(d_in):
        for j in range(d_in):
            e_ij = np.zeros((d_in, d_in))
            e_ij[i, j] = 1
            c += np.kron(apply_channel(channel, e_ij), e_ij)
    return c


@pytest.mark.parametrize(
    'channel',
    (
        cirq.I,
        cirq.X,
        cirq.CNOT,
        cirq.depolarize(0.1),
        cirq.depolarize(0.1, n_qubits=2),
        cirq.amplitude_damp(0.2),
    ),
)
def test_choi(channel):
    """Verifies that cirq.choi correctly computes the Choi matrix."""
    n_qubits = cirq.num_qubits(channel)
    actual = cirq.choi(channel)
    expected = expected_choi(channel)
    assert np.isclose(np.trace(actual), 2 ** n_qubits)
    assert np.all(actual == expected)


def test_choi_on_completely_dephasing_channel():
    """Checks that cirq.choi returns the right matrix for the completely dephasing channel."""
    assert np.all(cirq.choi(cirq.phase_damp(1)) == np.diag([1, 0, 0, 1]))
