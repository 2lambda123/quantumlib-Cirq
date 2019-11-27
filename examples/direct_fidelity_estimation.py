"""Implements direct fidelity estimation.

Direct Fidelity Estimation from Few Pauli Measurements
https://arxiv.org/abs/1104.4695

Practical characterization of quantum devices without tomography
https://arxiv.org/abs/1104.3835
"""

import argparse
import itertools
from typing import cast
from typing import List
from typing import Optional
from typing import Tuple
import sys
import numpy as np
import cirq


def build_circuit():
    # Builds an arbitrary circuit to test. The circuit is non Clifford to show
    # the use of simulators.
    qubits = cirq.LineQubit.range(3)
    circuit = cirq.Circuit(
        cirq.Z(qubits[0])**0.25,  # T-Gate, non Clifford.
        cirq.X(qubits[1])**0.123,
        cirq.X(qubits[2])**0.456)
    return circuit, qubits


def compute_characteristic_function(circuit: cirq.Circuit,
                                    P_i: Tuple[cirq.Gate, ...],
                                    qubits: List[cirq.Qid],
                                    density_matrix: np.ndarray):
    n_qubits = len(P_i)
    d = 2**n_qubits

    pauli_string = cirq.PauliString(dict(zip(qubits, P_i)))
    qubit_map = dict(zip(qubits, range(n_qubits)))
    # rho_i or sigma_i in https://arxiv.org/pdf/1104.3835.pdf
    trace = pauli_string.expectation_from_density_matrix(
        density_matrix, qubit_map)
    assert np.isclose(trace.imag, 0.0, atol=1e-6)
    trace = trace.real

    prob = trace * trace / d  # Pr(i) in https://arxiv.org/pdf/1104.3835.pdf

    return trace, prob


def direct_fidelity_estimation(circuit: cirq.Circuit, qubits: List[cirq.Qid],
                               noise: cirq.NoiseModel, sampled: bool,
                               n_trials: int, samples_per_term: int):
    # n_trials is upper-case N in https://arxiv.org/pdf/1104.3835.pdf

    # Number of qubits, lower-case n in https://arxiv.org/pdf/1104.3835.pdf
    n_qubits = len(qubits)
    d = 2**n_qubits

    # Computes for every \hat{P_i} of https://arxiv.org/pdf/1104.3835.pdf,
    # estimate rho_i and Pr(i). We then collect tuples (rho_i, Pr(i), \hat{Pi})
    # inside the variable 'pauli_traces'.
    pauli_traces = []

    simulator = cirq.DensityMatrixSimulator()
    # rho in https://arxiv.org/pdf/1104.3835.pdf
    density_matrix = cast(cirq.DensityMatrixTrialResult,
                          simulator.simulate(circuit)).final_density_matrix

    # TODO(tonybruguier): Sample the Pauli states more efficenitly when the
    # circuit consists of Clifford gates only, as described on page 4 of:
    # https://arxiv.org/pdf/1104.4695.pdf
    for P_i in itertools.product([cirq.I, cirq.X, cirq.Y, cirq.Z],
                                 repeat=n_qubits):
        rho_i, Pr_i = compute_characteristic_function(circuit, P_i, qubits,
                                                      density_matrix)
        pauli_traces.append({'P_i': P_i, 'rho_i': rho_i, 'Pr_i': Pr_i})

    assert len(pauli_traces) == 4**n_qubits

    p = [x['Pr_i'] for x in pauli_traces]
    assert np.isclose(sum(p), 1.0, atol=1e-6)

    # The package np.random.choice() is quite sensitive to probabilities not
    # summing up to 1.0. Even an absolute difference below 1e-6 (as checked just
    # above) does bother it, so we re-normalize the probs.
    inv_sum_p = 1 / sum(p)
    norm_p = [x * inv_sum_p for x in p]

    simulator = cirq.DensityMatrixSimulator(noise=noise)
    if sampled:
        fidelity = 0.0
        for _ in range(n_trials):
            # Randomly sample as per probability.
            i = np.random.choice(len(pauli_traces), p=norm_p)

            Pr_i = pauli_traces[i]['Pr_i']
            P_i = pauli_traces[i]['P_i']
            rho_i = pauli_traces[i]['rho_i']

            pauli_string = cirq.PauliString(dict(zip(qubits, P_i)))
            qubit_map = dict(zip(qubits, range(n_qubits)))

            p = cirq.PauliSumCollector(circuit=circuit,
                                       observable=pauli_string,
                                       samples_per_term=samples_per_term)

            completion = p.collect_async(sampler=simulator)
            cirq.testing.assert_asyncio_will_have_result(completion, None)

            sigma_i = p.estimated_energy()
            assert np.isclose(sigma_i.imag, 0.0, atol=1e-6)
            sigma_i = sigma_i.real

            fidelity += Pr_i * sigma_i / rho_i

        return fidelity
    else:
        # sigma in https://arxiv.org/pdf/1104.3835.pdf
        density_matrix = cast(cirq.DensityMatrixTrialResult,
                              simulator.simulate(circuit)).final_density_matrix

        fidelity = 0.0
        for _ in range(n_trials):
            # Randomly sample as per probability.
            i = np.random.choice(len(pauli_traces), p=norm_p)

            Pr_i = pauli_traces[i]['Pr_i']
            P_i = pauli_traces[i]['P_i']
            rho_i = pauli_traces[i]['rho_i']

            sigma_i, _ = compute_characteristic_function(
                circuit, P_i, qubits, density_matrix)

            fidelity += Pr_i * sigma_i / rho_i

        return fidelity / n_trials


def parse_arguments(args):
    """Helper function that parses the given arguments."""
    parser = argparse.ArgumentParser('Direct fidelity estimation.')

    parser.add_argument('--sampled',
                        default=False,
                        type=bool,
                        help='Run and do measurements on a real device.')

    parser.add_argument('--n_trials',
                        default=10,
                        type=int,
                        help='Number of trials to run.')

    parser.add_argument('--samples_per_term',
                        default=10,
                        type=int,
                        help='Number of samples per trial.')

    return vars(parser.parse_args(args))


def main(*, sampled: bool, n_trials: int, samples_per_term: int):
    circuit, qubits = build_circuit()
    circuit.append(cirq.measure(*qubits, key='y'))

    noise = cirq.ConstantQubitNoiseModel(cirq.depolarize(0.1))

    estimated_fidelity = direct_fidelity_estimation(
        circuit,
        qubits,
        noise,
        sampled=sampled,
        n_trials=n_trials,
        samples_per_term=samples_per_term)
    print(estimated_fidelity)


if __name__ == '__main__':
    main(**parse_arguments(sys.argv[1:]))
