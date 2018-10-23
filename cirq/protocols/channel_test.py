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

"""Tests for channel.py."""

from typing import Sequence

import numpy as np
import pytest

import cirq


LOCAL_DEFAULT = [np.array([])]

def test_channel_no_methods():
    class NoMethod:
        pass

    with pytest.raises(TypeError, match='no _channel_ or _unitary_ method'):
        _ = cirq.channel(NoMethod())

    assert cirq.channel(NoMethod(), None) is None
    assert cirq.channel(NoMethod, NotImplemented) is NotImplemented
    assert cirq.channel(NoMethod(), (1,)) == (1,)
    assert cirq.channel(NoMethod(), LOCAL_DEFAULT) is LOCAL_DEFAULT

def test_channel_returns_not_implemented():
    class ReturnsNotImplemented:
        def _channel_(self):
            return NotImplemented

    with pytest.raises(TypeError, match='returned NotImplemented'):
        _ = cirq.channel(ReturnsNotImplemented())

    assert cirq.channel(ReturnsNotImplemented(), None) is None
    assert (cirq.channel(ReturnsNotImplemented(),
                         NotImplemented) is NotImplemented)
    assert cirq.channel(ReturnsNotImplemented(), (1,)) == (1,)
    assert cirq.channel(ReturnsNotImplemented(), LOCAL_DEFAULT) is LOCAL_DEFAULT


def test_unitary_returns_not_implemented():
    class ReturnsNotImplemented:
        def _unitary_(self):
            return NotImplemented

    with pytest.raises(TypeError, match='returned NotImplemented'):
        _ = cirq.channel(ReturnsNotImplemented())
    assert cirq.channel(ReturnsNotImplemented(), None) is None
    assert (cirq.channel(ReturnsNotImplemented(),
                         NotImplemented) is NotImplemented)
    assert cirq.channel(ReturnsNotImplemented(), (1,)) == (1,)
    assert cirq.channel(ReturnsNotImplemented(), LOCAL_DEFAULT) is LOCAL_DEFAULT


def test_channel():
    a0 = np.array([[0, 0], [1, 0]])
    a1 = np.array([[1, 0], [0, 0]])
    c = (a0, a1)

    class ReturnsChannel:
        def _channel_(self) -> Sequence[np.ndarray]:
            return c

    assert cirq.channel(ReturnsChannel()) is c
    assert cirq.channel(ReturnsChannel(), None) is c
    assert cirq.channel(ReturnsChannel(), NotImplemented) is c
    assert cirq.channel(ReturnsChannel(), (1,)) is c
    assert cirq.channel(ReturnsChannel(), LOCAL_DEFAULT) is c


def test_channel_fallback_to_unitary():
    u = np.array([[1, 0], [1, 0]])

    class ReturnsUnitary:
        def _unitary_(self) -> np.ndarray:
            return u

    np.testing.assert_equal(cirq.channel(ReturnsUnitary()), (u,))
    np.testing.assert_equal(cirq.channel(ReturnsUnitary(), None), (u,))
    np.testing.assert_equal(cirq.channel(ReturnsUnitary(), NotImplemented),
                            (u,))
    np.testing.assert_equal(cirq.channel(ReturnsUnitary(), (1,)), (u,))
    np.testing.assert_equal(cirq.channel(ReturnsUnitary(), LOCAL_DEFAULT), (u,))


def call_stochastic_unitary(channel):
    class ReturnsChannel:
        def _channel_(self) -> Sequence[np.ndarray]:
            return channel
    return cirq.stochastic_unitary(ReturnsChannel())


Z = np.array([[1, 0], [0, -1]])
X = np.array([[0, 1], [1, 0]])
H = np.sqrt(0.5) * np.array([[1, 1], [1, -1]])
I = np.eye(2)
PHASER = np.sqrt(0.5) * (np.kron(I, I) + 1j * np.kron(Z, Z))


@pytest.mark.parametrize('channel,expected',(
    ((Z,) , ((1.0, Z),)),
    ((np.sqrt(0.5) * Z, np.sqrt(0.5) * X), ((0.5, Z), (0.5, X))),
    ((np.sqrt(0.3) * H, np.sqrt(0.7) * X), ((0.3, H), (0.7, X))),
    ((np.sqrt(0.3) * H, np.sqrt(0.7) * H), ((0.3, H), (0.7, H))),
    ((np.sqrt(0.3) * I, np.sqrt(0.7) * H), ((0.3, I), (0.7, H))),
    ((np.sqrt(0.3) * Z, np.sqrt(0.7) * H * 1j), ((0.3, Z), (0.7, H * 1j))),
    ((np.sqrt(0.3) * np.kron(X, Z), np.sqrt(0.7) * np.kron(Z, X)),
        ((0.3, np.kron(X, Z)), (0.7, np.kron(Z, X)))),
    ((np.sqrt(0.3) * PHASER, np.sqrt(0.7) * np.kron(Z, X)),
        ((0.3, PHASER), (0.7, np.kron(Z, X)))),
))
def test_stochastic_unitary(channel, expected):
    actual = call_stochastic_unitary(channel)
    assert len(actual) == len(expected), ('Actual and expected had differing '
                                          'numbers of elements.')
    for a, e in zip(actual, expected):
        assert len(a) == len(e), 'Tuples had more than two elements.'
        np.testing.assert_almost_equal(a[0], e[0])
        np.testing.assert_allclose(a[1], e[1])


@pytest.mark.parametrize('channel', (
    (np.array([[0, 1], [0, 0]]),),
    (np.array([[0.5, 0], [0, 0]]),),
    (np.sqrt(0.5) * np.eye(2), np.array([[0, np.sqrt(0.5)], [0, 0]])),
    (np.array([[0, 0], [0, 0]]),),
    ((np.sqrt(0.3) * PHASER, np.sqrt(0.35) * (np.kron(I, I) + np.kron(Z, Z)))),
))
def test_stochastic_unitary_not_decomposable(channel):
    assert call_stochastic_unitary(channel) is None



def test_stochastic_unitary_accuracy():
    channel = (np.sqrt(0.5) * Z, np.diag([np.sqrt(0.5), np.sqrt(0.5) * 1e-2]))
    class ReturnsChannel:
        def _channel_(self) -> Sequence[np.ndarray]:
            return channel
    assert cirq.stochastic_unitary(ReturnsChannel(), rtol=1e-4) is None


