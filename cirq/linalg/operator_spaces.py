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

"""Utilities for manipulating linear operators as elements of vector space."""

from typing import Dict

import numpy as np

PAULI_BASIS = {
    'I': np.eye(2),
    'X': np.array([[0., 1.], [1., 0.]]),
    'Y': np.array([[0., -1j], [1j, 0.]]),
    'Z': np.diag([1., -1]),
}


def kron_bases(*bases: Dict[str, np.ndarray],
               repeat: int = 1) -> Dict[str, np.ndarray]:
    """Creates tensor product of bases."""
    product_basis = {'': 1}
    for basis in bases * repeat:
        product_basis = {
            name1 + name2: np.kron(matrix1, matrix2)
            for name1, matrix1 in product_basis.items()
            for name2, matrix2 in basis.items()
        }
    return product_basis


def hilbert_schmidt_inner_product(m1: np.ndarray, m2: np.ndarray) -> complex:
    """Computes Hilbert-Schmidt inner product of two matrices.

    Linear in second argument.
    """
    return np.einsum('ij,ij', m1.conj(), m2)


def expand_matrix_in_orthogonal_basis(
        m: np.ndarray,
        basis: Dict[str, np.ndarray],
) -> Dict[str, complex]:
    """Computes coefficients of expansion of m in basis.

    We require that basis be orthogonal w.r.t. the Hilbert-Schmidt inner
    product. We do not require that basis be orthonormal. Note that Pauli
    basis (I, X, Y, Z) is orthogonal, but not orthonormal.
    """
    return {
        name: (hilbert_schmidt_inner_product(b, m) /
               hilbert_schmidt_inner_product(b, b))
        for name, b in basis.items()
    }


def matrix_from_basis_coefficients(expansion: Dict[str, complex],
                                   basis: Dict[str, np.ndarray]) -> np.ndarray:
    """Computes linear combination of basis vectors with given coefficients."""
    some_element = next(iter(basis.values()))
    result = np.zeros_like(some_element, dtype=np.complex128)
    for name, coefficient in expansion.items():
        result += coefficient * basis[name]
    return result


def operator_power(pauli_coefficients: Dict[str, complex],
                   exponent: int) -> Dict[str, complex]:
    """Computes non-negative integer power of single-qubit linear operator.

    Both input and output operators are represented using their expansion in
    the Pauli basis.

    Correctness of the formulas below follows from the binomial expansion using
    the fact that for any normalized real vector (b, c, d) and any non-negative
    integer k:

        [bX + cY + dZ]^(2k) = I

    """
    if exponent == 0:
        return {'I': 1}

    a = pauli_coefficients.get('I', 0.0)
    b = pauli_coefficients.get('X', 0.0)
    c = pauli_coefficients.get('Y', 0.0)
    d = pauli_coefficients.get('Z', 0.0)

    v = np.sqrt(b*b + c*c + d*d)
    s = np.power(a + v, exponent)
    t = np.power(a - v, exponent)

    ci = (s + t) / 2
    if s == t:
        cxyz = exponent * np.power(a, exponent - 1)
    else:
        cxyz = (s - t) / 2
        cxyz = cxyz / v

    return {
        'I': ci,
        'X': cxyz * b,
        'Y': cxyz * c,
        'Z': cxyz * d,
    }
