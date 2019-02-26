# Copyright 2018 The Cirq Developers
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

from typing import Any

import numpy as np

from cirq import protocols
from cirq.linalg import operator_spaces


def assert_pauli_expansion_is_consistent_with_unitary(val: Any) -> None:
    """Checks Pauli expansion against unitary matrix."""
    pauli_expansion = protocols.pauli_expansion(val, default=None)
    if pauli_expansion is None:
        return

    unitary = protocols.unitary(val, None)
    if unitary is None:
        return

    basis = {'': 1.0}
    k = unitary.shape[0] >> 1
    while k:
        basis = operator_spaces.kron_bases(basis, operator_spaces.PAULI_BASIS)
        k >>= 1

    recovered_unitary = operator_spaces.matrix_from_basis_coefficients(
        pauli_expansion, basis)
    assert np.allclose(unitary, recovered_unitary, rtol=0, atol=1e-12)
