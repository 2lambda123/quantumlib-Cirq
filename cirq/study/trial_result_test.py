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

import collections
import numpy as np

import cirq


# Python 2 gives a different repr due to unicode strings being prefixed with u.
@cirq.testing.only_test_in_python3
def test_repr():
    v = cirq.TrialResult(
        params=cirq.ParamResolver({'a': 2}),
        repetitions=2,
        measurements={'m': np.array([[1, 2]])})

    assert repr(v) == ("TrialResult(params=ParamResolver({'a': 2}), "
                       "repetitions=2, measurements={'m': array([[1, 2]])})")


def test_str():
    result = cirq.TrialResult(
        params=cirq.ParamResolver({}),
        repetitions=5,
        measurements={
            'ab': np.array([[0, 1],
                            [0, 1],
                            [0, 1],
                            [1, 0],
                            [0, 1]]),
            'c': np.array([[0], [0], [1], [0], [1]])
        })
    assert str(result) == 'ab=00010, 11101\nc=00101'


def test_histogram():
    result = cirq.TrialResult(
        params=cirq.ParamResolver({}),
        repetitions=5,
        measurements={
            'ab': np.array([[0, 1],
                            [0, 1],
                            [0, 1],
                            [1, 0],
                            [0, 1]], dtype=np.bool),
            'c': np.array([[0], [0], [1], [0], [1]], dtype=np.bool)
        })

    assert result.histogram(key='ab') == collections.Counter({
        0b01: 4,
        0b10: 1
    })
    assert result.histogram(key='ab', fold_func=tuple) == collections.Counter({
        (False, True): 4,
        (True, False): 1
    })
    assert result.histogram(key='ab',
                            fold_func=lambda e: None) == collections.Counter({
        None: 5,
    })
    assert result.histogram(key='c') == collections.Counter({
        0: 3,
        1: 2
    })


def test_combined_histogram():
    result = cirq.TrialResult(
        params=cirq.ParamResolver({}),
        repetitions=5,
        measurements={
            'ab': np.array([[0, 1],
                            [0, 1],
                            [0, 1],
                            [1, 0],
                            [0, 1]], dtype=np.bool),
            'c': np.array([[0], [0], [1], [0], [1]], dtype=np.bool)
        })

    assert result.combined_histogram(keys=[]) == collections.Counter({
        (): 5,
    })
    assert result.combined_histogram(keys=['ab']) == collections.Counter({
        (0b01,): 4,
        (0b10,): 1,
    })
    assert result.combined_histogram(keys=['c']) == collections.Counter({
        (0,): 3,
        (1,): 2,
    })
    assert result.combined_histogram(keys=['ab', 'c']) == collections.Counter({
        (0b01, 0,): 2,
        (0b01, 1,): 2,
        (0b10, 0,): 1,
    })

    assert result.combined_histogram(keys=[], fold_func=lambda e: None
                                     ) == collections.Counter({
        None: 5,
    })
    assert result.combined_histogram(keys=['ab'], fold_func=lambda e: None
                                     ) == collections.Counter({
        None: 5,
    })
    assert result.combined_histogram(keys=['ab', 'c'], fold_func=lambda e: None
                                     ) == collections.Counter({
        None: 5,
    })

    assert result.combined_histogram(keys=['ab', 'c'],
                                     fold_func=lambda e: tuple(tuple(f)
                                                               for f in e)
                                     ) == collections.Counter({
        ((False, True), (False,)): 2,
        ((False, True), (True,)): 2,
        ((True, False), (False,)): 1,
    })
