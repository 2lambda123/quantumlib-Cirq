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

"""Protocol and methods for quantum channels."""

from typing import Any, Iterable, Optional, Tuple, TypeVar, Union

import numpy as np
import scipy as sp
from typing_extensions import Protocol

from cirq.type_workarounds import NotImplementedType


# This is a special indicator value used by the channel method to determine
# whether or not the caller provided a 'default' argument. It must be of type
# Sequence[np.ndarray] to ensure the method has the correct type signature in
# that case. It is checked for using `is`, so it won't have a false positive
# if the user provides a different (np.array([]),) value.
RaiseTypeErrorIfNotProvided = (np.array([]),)


TDefault = TypeVar('TDefault')


class SupportsChannel(Protocol):
    """An object that may be describable as a quantum channel."""

    def _channel_(self) -> Union[Iterable[np.ndarray], NotImplementedType]:
        """A list of matrices describing the quantum channel.

        These matrices are the terms in the operator sum representation of
        a quantum channel. If the returned matrices are {A_0,A_1,..., A_{r-1}},
        then this describes the channel:
            \rho -> \sum_{k=0}^{r-1} A_0 \rho A_0^\dagger
        These matrices are required to satisfy the trace preserving condition
            \sum_{k=0}^{r-1} A_i^\dagger A_i = I
        where I is the identity matrix. The matrices A_i are sometimes called
        Krauss or noise operators.

        This method is used by the global `cirq.channel` method. If this method
        or the _unitary_ method is not present, or returns NotImplement,
        it is assumed that the receiving object doesn't have a channel
        (resulting in a TypeError or default result when calling `cirq.channel`
        on it). (The ability to return NotImplemented is useful when a class
        cannot know if it is a channel until runtime.)

        The order of cells in the matrices is always implicit with respect to
        the object being called. For example, for GateOperations these matrices
        must be ordered with respect to the list of qubits that the channel is
        applied to. The qubit-to-amplitude order mapping matches the
        ordering of numpy.kron(A, B), where A is a qubit earlier in the list
        than the qubit B.

        Returns:
            A list of matrices describing the channel (Krauss operators), or
            NotImplemented if there is no such matrix.
        """


def channel(val: Any,
            default: Iterable[TDefault] = RaiseTypeErrorIfNotProvided
            ) -> Union[Tuple[np.ndarray], Iterable[TDefault]]:
    """Returns a list of matrices describing the channel for the given value.

    These matrices are the terms in the operator sum representation of
    a quantum channel. If the returned matrices are {A_0,A_1,..., A_{r-1}},
    then this describes the channel:
        \rho -> \sum_{k=0}^{r-1} A_0 \rho A_0^\dagger
    These matrices are required to satisfy the trace preserving condition
        \sum_{k=0}^{r-1} A_i^\dagger A_i = I
    where I is the identity matrix. The matrices A_i are sometimes called
    Krauss or noise operators.

    Args:
        val: The value to describe by a channel.
        default: Determines the fallback behavior when `val` doesn't have
            a channel. If `default` is not set, a TypeError is raised. If
            default is set to a value, that value is returned.

    Returns:
        If `val` has a _channel_ method and its result is not NotImplemented,
        that result is returned. Otherwise, if `val` has a _unitary_ method and
        its result is not NotImplemented a tuple made up of that result is
        returned. Otherwise, if a default value was specified, the default
        value is returned.

    Raises:
        TypeError: `val` doesn't have a _channel_ or _unitary_ method (or that
            method returned NotImplemented) and also no default value was
            specified.
    """
    channel_getter = getattr(val, '_channel_', None)
    channel_result = (
        NotImplemented if channel_getter is None else channel_getter())

    if channel_result is not NotImplemented:
        return tuple(channel_result)

    unitary_getter = getattr(val, '_unitary_', None)
    unitary_result = (
        NotImplemented if unitary_getter is None else unitary_getter())

    if unitary_result is not NotImplemented:
        return (unitary_result,)

    if default is not RaiseTypeErrorIfNotProvided:
        return default

    if channel_getter is None and unitary_getter is None:
        raise TypeError("object of type '{}' has no _channel_ or "
                        "_unitary_ method.".format(type(val)))
    raise TypeError("object of type '{}' does have a _channel_  or _unitary_ "
                    "method, but it returned NotImplemented.".format(type(val)))


def stochastic_unitary(
    val: SupportsChannel,
    rtol=1.e-5,
    atol=1.e-8, ) -> Optional[Tuple[Tuple[float, np.ndarray], ...]]:
    """Gives a stochastic representation of a channel by unitaries, if possible.

    If a channel has Krauss operators A_0,A_1,...,A_{r-1} this checks whether
    each A_i is proportional to a unitary matrix, U_i, and if so, returns
    each each unitary U_i along with the probability of the unitary p_i,
    (i.e. A_i = \sqrt{p_i} U_i). Note that this does NOT check whether
    there is some equivalent channel (under unitary equivalences of channels)
    that supports interpretation as a stochastic unitary, only that the
    decomposition into Krauss operators does have such an interpretation.

    Args:
        val: the value that implements the SupportsChannel protocol.
        rtol: relative tolerance for the unitary times conjugate transpose
            itself being close to identity (see numpy.allclose).
        atol: absolute tolerance for the unitary times conjugate transpose
            itself being close to identity (see numpy.allclose).

    Returns:
        A tuple of tuples of the form (p_i, U_i) where p_i is the probability
        of the unitary U_i occurring for the channel, or None if no such
        decomposition is possible.
    """
    results = []
    for op in val._channel_():
        # If polar decomposition has Hermitian part that is proportional to
        # identity, it does not matter whether we use the left or right polar
        # decomposition.
        u, p = sp.linalg.polar(op)
        if p[0, 0] == 0:
            return None
        potential_eye = p / p[0, 0]
        if np.allclose(potential_eye, np.eye(op.shape[0]), rtol=rtol,
                       atol=atol):
            results.append((np.abs(p[0, 0]) ** 2, u))
        else:
            return None
    return tuple(results)