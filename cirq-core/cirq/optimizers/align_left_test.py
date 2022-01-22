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

import cirq


def assert_optimizes(before, after):
    opt = cirq.AlignLeft()
    opt(before)
    assert before == after


def test_align_left():
    q1 = cirq.NamedQubit('q1')
    q2 = cirq.NamedQubit('q2')
    assert_optimizes(
        before=cirq.Circuit(
            [
                cirq.Moment([cirq.X(q1)]),
                cirq.Moment([cirq.Y(q1), cirq.X(q2)]),
                cirq.Moment([cirq.X(q1), cirq.Y(q2)]),
                cirq.Moment([cirq.Y(q1)]),
                cirq.measure(*[q1, q2], key='a'),
            ]
        ),
        after=cirq.Circuit(
            [
                cirq.Moment([cirq.X(q1), cirq.X(q2)]),
                cirq.Moment([cirq.Y(q1), cirq.Y(q2)]),
                cirq.Moment([cirq.X(q1)]),
                cirq.Moment([cirq.Y(q1)]),
                cirq.measure(*[q1, q2], key='a'),
            ]
        ),
    )


def test_classical_control():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.H(q0), cirq.measure(q0, key='m'), cirq.X(q1).with_classical_controls('m')
    )
    assert_optimizes(before=circuit, after=circuit.copy())
