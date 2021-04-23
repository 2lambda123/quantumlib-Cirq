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

import numpy as np


import cirq
import cirq_google as cg
from cirq.experiments import random_rotations_between_grid_interaction_layers_circuit
from cirq.experiments.xeb_fitting import XEBPhasedFSimCharacterizationOptions
from cirq_google.calibration.phased_fsim import XEBPhasedFSimCalibrationOptions
from cirq_google.calibration.xeb_wrapper import run_calibration

SQRT_ISWAP = cirq.ISWAP ** -0.5

import scipy.optimize
import scipy.optimize._minimize


# Necessary for the monkeypatching to work.
import multiprocessing
multiprocessing.set_start_method('fork', force=True)

def minimize_patch(fun, x0, args=(), method=None, jac=None, hess=None,
                   hessp=None, bounds=None, constraints=(), tol=None,
                   callback=None, options=None):
    print('patching worked', flush=True)
    assert method == 'nelder-mead'

    return scipy.optimize.OptimizeResult(
        fun=0, nit=0, nfev=0,
        status=0, success=True,
        message='monkeypatched', x=x0.copy(), final_simplex=None)




def test_run_calibration(monkeypatch):
    monkeypatch.setattr('cirq.experiments.xeb_fitting.scipy.optimize.minimize', minimize_patch)
    _old_minimize = scipy.optimize.minimize
    qubit_indices = [
        (0, 5), (0, 6), (1, 6), (2, 6),
    ]
    qubits = [cirq.GridQubit(*idx) for idx in qubit_indices]
    sampler = cirq.ZerosSampler()

    circuits = [random_rotations_between_grid_interaction_layers_circuit(
        qubits,
        depth=depth,
        two_qubit_op_factory=lambda a, b, _: SQRT_ISWAP.on(a, b),
        pattern=cirq.experiments.GRID_ALIGNED_PATTERN,
        seed=10,
    ) for depth in [5, 10]]

    options = XEBPhasedFSimCalibrationOptions(
        fsim_options=XEBPhasedFSimCharacterizationOptions(
            characterize_zeta=True,
            characterize_gamma=True,
            characterize_chi=True,
            characterize_theta=False,
            characterize_phi=False,
            theta_default=np.pi / 4,
        ),
    )

    characterization_requests = []
    for circuit in circuits:
        characterized_circuit, characterization_requests = \
            cg.prepare_characterization_for_moments(
                circuit, options=options,
                initial=characterization_requests)
    assert len(characterization_requests) == 2

    print('1', flush=True)
    characterizations = [
        run_calibration(request, sampler)
        for request in characterization_requests
    ]
    print(characterizations)

    final_params = dict()
    for c in characterizations:
        final_params.update(c.parameters)
    assert len(final_params) == 3  # pairs

