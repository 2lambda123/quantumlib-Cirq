# Copyright 2019 The Cirq Developers
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

import pytest

import pandas as pd

import cirq
import cirq.experiments.t2_decay_experiment as t2


def test_init_t2_decay_result():
    x_data = pd.DataFrame(columns=['delay_ns', 0, 1],
                          index=range(2),
                          data=[
                              [100.0, 0, 10],
                              [1000.0, 10, 0],
                          ])
    y_data = pd.DataFrame(columns=['delay_ns', 0, 1],
                          index=range(2),
                          data=[
                              [100.0, 5, 5],
                              [1000.0, 5, 5],
                          ])
    result = cirq.experiments.T2DecayResult(x_data, y_data)
    assert result

    bad_data = pd.DataFrame(columns=['delay_ms', 0, 1],
                            index=range(2),
                            data=[
                                [100.0, 0, 10],
                                [1000.0, 10, 0],
                            ])
    with pytest.raises(ValueError):
        cirq.experiments.T2DecayResult(bad_data, y_data)
    with pytest.raises(ValueError):
        cirq.experiments.T2DecayResult(x_data, bad_data)


def test_plot_does_not_raise_error():

    class _TimeDependentDecay(cirq.NoiseModel):

        def noisy_moment(self, moment, system_qubits):
            duration = max((op.gate.duration
                            for op in moment.operations
                            if isinstance(op.gate, cirq.WaitGate)),
                           default=cirq.Duration(nanos=1))
            yield cirq.amplitude_damp(1 - 0.99**duration.total_nanos()).on_each(
                system_qubits)
            yield moment

    results = cirq.experiments.t2_decay(
        sampler=cirq.DensityMatrixSimulator(noise=_TimeDependentDecay()),
        qubit=cirq.GridQubit(0, 0),
        num_points=3,
        repetitions=10,
        max_delay=cirq.Duration(nanos=500))
    results.plot_expectations()
    results.plot_bloch_vector()


def test_result_eq():
    example_data = pd.DataFrame(columns=['delay_ns', 0, 1],
                                index=range(5),
                                data=[
                                    [200.0, 0, 100],
                                    [400.0, 20, 80],
                                    [600.0, 40, 60],
                                    [800.0, 60, 40],
                                    [1000.0, 80, 20],
                                ])
    other_data = pd.DataFrame(columns=['delay_ns', 0, 1],
                              index=range(5),
                              data=[
                                  [200.0, 0, 100],
                                  [400.0, 19, 81],
                                  [600.0, 39, 61],
                                  [800.0, 59, 41],
                                  [1000.0, 79, 21],
                              ])
    eq = cirq.testing.EqualsTester()
    eq.make_equality_group(lambda: cirq.experiments.T2DecayResult(
        example_data, example_data))

    eq.add_equality_group(
        cirq.experiments.T2DecayResult(other_data, example_data))
    eq.add_equality_group(
        cirq.experiments.T2DecayResult(example_data, other_data))


def test_sudden_decay_results():

    class _SuddenDecay(cirq.NoiseModel):

        def noisy_moment(self, moment, system_qubits):
            duration = max((op.gate.duration
                            for op in moment.operations
                            if isinstance(op.gate, cirq.WaitGate)),
                           default=cirq.Duration())
            if duration > cirq.Duration(nanos=500):
                yield cirq.amplitude_damp(1).on_each(system_qubits)
            yield moment

    results = cirq.experiments.t2_decay(
        sampler=cirq.DensityMatrixSimulator(noise=_SuddenDecay()),
        qubit=cirq.GridQubit(0, 0),
        num_points=4,
        repetitions=500,
        min_delay=cirq.Duration(nanos=100),
        max_delay=cirq.Duration(micros=1))

    assert (results.expectation_pauli_y['value'][0:2] == -1).all()
    assert (results.expectation_pauli_y['value'][2:] < 0.20).all()

    # X Should be approximately zero
    assert (abs(results.expectation_pauli_x['value']) < 0.20).all()


def test_spin_echo_cancels_out_constant_rate_phase():

    class _TimeDependentPhase(cirq.NoiseModel):

        def noisy_moment(self, moment, system_qubits):
            duration = max((op.gate.duration
                            for op in moment.operations
                            if isinstance(op.gate, cirq.WaitGate)),
                           default=cirq.Duration(nanos=1))
            phase = duration.total_nanos() / 100.0
            yield (cirq.Y**phase).on_each(system_qubits)
            yield moment

    results = cirq.experiments.t2_decay(
        sampler=cirq.DensityMatrixSimulator(noise=_TimeDependentPhase()),
        qubit=cirq.GridQubit(0, 0),
        num_points=10,
        repetitions=100,
        min_delay=cirq.Duration(nanos=100),
        max_delay=cirq.Duration(micros=1),
        experiment_type=t2.ExperimentType.HAHN_ECHO)

    assert (results.expectation_pauli_y['value'] < -0.8).all()


@pytest.mark.parametrize(
    'experiment_type', [t2.ExperimentType.RAMSEY, t2.ExperimentType.HAHN_ECHO])
def test_all_on_results(experiment_type):
    results = t2.t2_decay(sampler=cirq.Simulator(),
                          qubit=cirq.GridQubit(0, 0),
                          num_points=4,
                          repetitions=500,
                          min_delay=cirq.Duration(nanos=100),
                          max_delay=cirq.Duration(micros=1),
                          experiment_type=experiment_type)

    assert (results.expectation_pauli_y['value'] == -1.0).all()

    # X Should be approximately zero
    assert (abs(results.expectation_pauli_x['value']) < 0.20).all()


@pytest.mark.parametrize(
    'experiment_type', [t2.ExperimentType.RAMSEY, t2.ExperimentType.HAHN_ECHO])
def test_all_off_results(experiment_type):
    results = t2.t2_decay(
        sampler=cirq.DensityMatrixSimulator(noise=cirq.amplitude_damp(1)),
        qubit=cirq.GridQubit(0, 0),
        num_points=4,
        repetitions=10,
        min_delay=cirq.Duration(nanos=100),
        max_delay=cirq.Duration(micros=1),
        experiment_type=experiment_type)
    assert results == cirq.experiments.T2DecayResult(
        x_basis_data=pd.DataFrame(columns=['delay_ns', 0, 1],
                                  index=range(4),
                                  data=[
                                      [100.0, 10, 0],
                                      [400.0, 10, 0],
                                      [700.0, 10, 0],
                                      [1000.0, 10, 0],
                                  ]),
        y_basis_data=pd.DataFrame(columns=['delay_ns', 0, 1],
                                  index=range(4),
                                  data=[
                                      [100.0, 10, 0],
                                      [400.0, 10, 0],
                                      [700.0, 10, 0],
                                      [1000.0, 10, 0],
                                  ]),
    )


def test_bad_args():
    with pytest.raises(ValueError, match='repetitions <= 0'):
        _ = cirq.experiments.t2_decay(sampler=cirq.Simulator(),
                                      qubit=cirq.GridQubit(0, 0),
                                      num_points=4,
                                      repetitions=0,
                                      max_delay=cirq.Duration(micros=1))

    with pytest.raises(ValueError, match='even number'):
        _ = cirq.experiments.t2_decay(sampler=cirq.Simulator(),
                                      qubit=cirq.GridQubit(0, 0),
                                      num_points=4,
                                      repetitions=737,
                                      max_delay=cirq.Duration(micros=1))

    with pytest.raises(ValueError, match='max_delay < min_delay'):
        _ = cirq.experiments.t2_decay(sampler=cirq.Simulator(),
                                      qubit=cirq.GridQubit(0, 0),
                                      num_points=4,
                                      repetitions=10,
                                      min_delay=cirq.Duration(micros=1),
                                      max_delay=cirq.Duration(micros=0))

    with pytest.raises(ValueError, match='min_delay < 0'):
        _ = cirq.experiments.t2_decay(sampler=cirq.Simulator(),
                                      qubit=cirq.GridQubit(0, 0),
                                      num_points=4,
                                      repetitions=10,
                                      max_delay=cirq.Duration(micros=1),
                                      min_delay=cirq.Duration(micros=-1))

    with pytest.raises(ValueError, match='not supported'):
        _ = cirq.experiments.t2_decay(sampler=cirq.Simulator(),
                                      qubit=cirq.GridQubit(0, 0),
                                      num_points=4,
                                      repetitions=100,
                                      max_delay=cirq.Duration(micros=1),
                                      experiment_type=t2.ExperimentType.CPMG)


def test_str():

    x_data = pd.DataFrame(columns=['delay_ns', 0, 1],
                          index=range(2),
                          data=[
                              [100.0, 0, 10],
                              [1000.0, 10, 0],
                          ])
    y_data = pd.DataFrame(columns=['delay_ns', 0, 1],
                          index=range(2),
                          data=[
                              [100.0, 5, 5],
                              [1000.0, 5, 5],
                          ])
    result = cirq.experiments.T2DecayResult(x_data, y_data)

    cirq.testing.assert_equivalent_repr(result)

    class FakePrinter:

        def __init__(self):
            self.text_pretty = ''

        def text(self, to_print):
            self.text_pretty += to_print

    p = FakePrinter()
    result._repr_pretty_(p, False)
    assert p.text_pretty == str(result)

    p = FakePrinter()
    result._repr_pretty_(p, True)
    assert p.text_pretty == 'T2DecayResult(...)'
