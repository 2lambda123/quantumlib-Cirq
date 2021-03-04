# Copyright 2020 The Cirq developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import dataclasses
import itertools
from typing import Iterable, List, Tuple, TYPE_CHECKING, Sequence, Dict

import numpy as np
import sympy

from cirq import circuits, ops, value
from cirq.work.observable_settings import (
    InitObsSetting,
    _MeasurementSpec,
)

if TYPE_CHECKING:
    import cirq
    from cirq.value.product_state import _NamedOneQubitState


def _with_parameterized_layers(
    circuit: 'cirq.Circuit',
    qubits: Sequence['cirq.Qid'],
    needs_init_layer: bool,
) -> 'cirq.Circuit':
    """Return a copy of the input circuit with parameterized single-qubit rotations.

    These rotations flank the circuit: the initial two layers of X and Y gates
    are given parameter names "{qubit}-Xi" and "{qubit}-Yi" and are used
    to set up the initial state. If `needs_init_layer` is False,
    these two layers of gates are omitted.

    The final two layers of X and Y gates are given parameter names
    "{qubit}-Xf" and "{qubit}-Yf" and are use to change the frame of the
    qubit before measurement, effectively measuring in bases other than Z.
    """
    x_beg_mom = ops.Moment([ops.X(q) ** sympy.Symbol(f'{q}-Xi') for q in qubits])
    y_beg_mom = ops.Moment([ops.Y(q) ** sympy.Symbol(f'{q}-Yi') for q in qubits])
    x_end_mom = ops.Moment([ops.X(q) ** sympy.Symbol(f'{q}-Xf') for q in qubits])
    y_end_mom = ops.Moment([ops.Y(q) ** sympy.Symbol(f'{q}-Yf') for q in qubits])
    meas_mom = ops.Moment([ops.measure(*qubits, key='z')])
    if needs_init_layer:
        total_circuit = circuits.Circuit([x_beg_mom, y_beg_mom])
        total_circuit += circuit.copy()
    else:
        total_circuit = circuit.copy()
    total_circuit.append([x_end_mom, y_end_mom, meas_mom])
    return total_circuit


_OBS_TO_PARAM_VAL: Dict[Tuple['cirq.Pauli', bool], Tuple[float, float]] = {
    (ops.X, False): (0, -1 / 2),
    (ops.X, True): (0, +1 / 2),
    (ops.Y, False): (1 / 2, 0),
    (ops.Y, True): (-1 / 2, 0),
    (ops.Z, False): (0, 0),
    (ops.Z, True): (1, 0),
}
"""Mapping from single-qubit Pauli observable to the X- and Y-rotation parameter values. The
second element in the key is whether to measure in the positive or negative (flipped) basis
for readout symmetrization."""

_STATE_TO_PARAM_VAL: Dict['_NamedOneQubitState', Tuple[float, float]] = {
    value.KET_PLUS: (0, +1 / 2),
    value.KET_MINUS: (0, -1 / 2),
    value.KET_IMAG: (-1 / 2, 0),
    value.KET_MINUS_IMAG: (+1 / 2, 0),
    value.KET_ZERO: (0, 0),
    value.KET_ONE: (1, 0),
}
"""Mapping from an initial _NamedOneQubitState to the X- and Y-rotation parameter values."""


def _get_params_for_setting(
    setting: InitObsSetting,
    flips: Iterable[bool],
    qubits: Sequence['cirq.Qid'],
    needs_init_layer: bool,
) -> Dict[str, float]:
    """Return the parameter dictionary for the given setting.

    This must be used in conjunction with a circuit generated by
    `_with_parameterized_layers`. `flips` (used for readout symmetrization)
    should be of the same length as `qubits` and will modify the parameters
    to also include a bit flip (`X`). Code responsible for running the
    circuit should make sure to flip bits back prior to analysis.

    Like `_with_parameterized_layers`, we omit params for initialization gates
    if we know that `setting.init_state` is the all-zeros state and
    `needs_init_layer` is False.
    """
    params = {}
    for qubit, flip in itertools.zip_longest(qubits, flips):
        if qubit is None or flip is None:
            raise ValueError("`qubits` and `flips` must be equal length")
        # When getting the one-qubit state / observable for this qubit,
        # you may be wondering what if there's no observable specified
        # for that qubit. We mandate that by the time you get to this stage,
        # each _max_setting has
        # weight(in_state) == weight(out_operator) == len(qubits)
        # See _pad_setting
        pauli = setting.observable[qubit]
        xf_param, yf_param = _OBS_TO_PARAM_VAL[pauli, flip]
        params[f'{qubit}-Xf'] = xf_param
        params[f'{qubit}-Yf'] = yf_param

        if needs_init_layer:
            state = setting.init_state[qubit]
            xi_param, yi_param = _STATE_TO_PARAM_VAL[state]
            params[f'{qubit}-Xi'] = xi_param
            params[f'{qubit}-Yi'] = yi_param

    return params


def _pad_setting(
    max_setting: InitObsSetting,
    qubits: List['cirq.Qid'],
    pad_init_state_with=value.KET_ZERO,
    pad_obs_with: 'cirq.Gate' = ops.Z,
) -> InitObsSetting:
    """Pad `max_setting`'s `init_state` and `observable` with `pad_xx_with` operations
    (defaults:  |0> and Z) so each max_setting has the same qubits. We need this
    to be the case so we can fill in all the parameters, see `_get_params_for_setting`.
    """
    obs = max_setting.observable
    assert obs.coefficient == 1, "Only the max_setting should be padded."
    for qubit in qubits:
        if not qubit in obs:
            obs *= pad_obs_with(qubit)

    init_state = max_setting.init_state
    init_state_original_qubits = init_state.qubits
    for qubit in qubits:
        if not qubit in init_state_original_qubits:
            init_state *= pad_init_state_with(qubit)

    return InitObsSetting(init_state=init_state, observable=obs)


@dataclasses.dataclass(frozen=True)
class _FlippyMeasSpec:
    """Internally, each MeasurementSpec class is split into two
    _FlippyMeasSpecs to support readout symmetrization.

    Bitstring results are combined, so this should be opaque to the user.
    """

    meas_spec: _MeasurementSpec
    flips: np.ndarray
    qubits: Sequence['cirq.Qid']

    def param_tuples(self, *, needs_init_layer=True):
        yield from _get_params_for_setting(
            self.meas_spec.max_setting,
            flips=self.flips,
            qubits=self.qubits,
            needs_init_layer=needs_init_layer,
        ).items()
        yield from self.meas_spec.circuit_params.items()


def _subdivide_meas_specs(
    meas_specs: Iterable[_MeasurementSpec],
    repetitions: int,
    qubits: Sequence['cirq.Qid'],
    readout_symmetrization: bool,
) -> Tuple[List[_FlippyMeasSpec], int]:
    """Split measurement specs into sub-jobs for readout symmetrization

    In readout symmetrization, we first run the "normal" circuit followed
    by running the circuit with flipped measurement.
    One _MeasurementSpec is split into two _FlippyMeasSpecs. These are run
    separately but accumulated according to their shared _MeasurementSpec.
    """
    n_qubits = len(qubits)
    flippy_mspecs = []
    for meas_spec in meas_specs:
        all_normal = np.zeros(n_qubits, dtype=bool)
        flippy_mspecs.append(
            _FlippyMeasSpec(
                meas_spec=meas_spec,
                flips=all_normal,
                qubits=qubits,
            )
        )

        if readout_symmetrization:
            all_flipped = np.ones(n_qubits, dtype=bool)
            flippy_mspecs.append(
                _FlippyMeasSpec(
                    meas_spec=meas_spec,
                    flips=all_flipped,
                    qubits=qubits,
                )
            )

    if readout_symmetrization:
        repetitions //= 2

    return flippy_mspecs, repetitions
