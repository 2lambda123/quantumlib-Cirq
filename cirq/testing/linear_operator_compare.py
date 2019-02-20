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

import numpy as np

from cirq.linalg import operator_spaces
from cirq.ops import linear_operator
from cirq.protocols.pauli_expansion import pauli_expansion


def assert_linear_operator_is_consistent(
        op: linear_operator.LinearOperator,
        *,
        atol: float = 1e-9) -> None:
    """Verifies that LinearOperator instance is internally consistent."""
    matrix = op.matrix()
    if matrix is None:
        return
    expansion = pauli_expansion(op)
    if expansion is None or expansion is NotImplemented:
        return

    matrix2 = operator_spaces.reconstruct_from_expansion(
        expansion, operator_spaces.PAULI_BASIS)
    expansion2 = operator_spaces.expand_in_basis(
        matrix, operator_spaces.PAULI_BASIS)

    print('matrix\n', matrix)
    print('matrix2\n', matrix2)
    print('expansion', expansion)
    print('expansion2', expansion2)

    assert np.allclose(matrix, matrix2, atol=atol)
    assert np.allclose(expansion, expansion2, atol=atol)


def assert_linear_operators_are_equal(
        actual: linear_operator.LinearOperator,
        reference: linear_operator.LinearOperator,
        *,
        atol: float = 1e-9) -> None:
    """Determines whether two linear operators are equal.

    Two linear operators A and B on the same vector space V are equal if for
    every vector v, Av == Bv.

    Alternatively, fix basis of V and denote the matrix of operator D as M(D).
    The above is then equivalent to M(A) == M(B).

    Alternatively, fix basis E1,..., En of the space L(V) of linear operators
    on V and expand A = a1*E1 + ... + an*En and B = b1*E1 + ... bn*En.
    The above is then equivalent to ak == bk for every k=1,...,n.

    We test the two latter conditions since they are more tractable than the
    first. Note that some LinearOperator instances may not have a Pauli basis
    expansion or the matrix, but none should lack both.
    """
    assert_linear_operator_is_consistent(actual, atol=atol)
    assert_linear_operator_is_consistent(reference, atol=atol)

    actual_matrix = actual.matrix()
    reference_matrix = reference.matrix()
    print('actual_matrix\n', actual_matrix)
    print('reference_matrix\n', reference_matrix)
    if actual_matrix is not None and reference_matrix is not None:
        assert actual_matrix.shape == reference_matrix.shape
        assert np.allclose(actual_matrix, reference_matrix, rtol=0, atol=atol)

    actual_expansion = pauli_expansion(actual)
    reference_expansion = pauli_expansion(reference)
    print('actual_expansion', actual_expansion)
    print('reference_expansion', reference_expansion)
    if (actual_expansion is not NotImplemented and
        reference_expansion is not NotImplemented):
        assert np.allclose(actual_expansion,
                           reference_expansion,
                           rtol=0,
                           atol=atol)

    assert actual_matrix is not None or actual_expansion is not NotImplemented
    assert (reference_matrix is not None or
            reference_expansion is not NotImplemented)
