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

"""Expectation value tool for pauli operators given a circuit"""

from typing import Dict, Union

import numpy as np
from cirq.google import XmonSimulator, XmonMeasurementGate
from cirq.circuits.circuit import Circuit
from cirq.ops import RotXGate, RotYGate, MeasurementGate, Pauli, PauliString, \
    QubitId


def measurement_gates(circuit: Circuit,
                      q_dict: Dict[QubitId,
                                   Union[int, str]]):
    """
    Helper Function to add measurement gates to qubits

    Args:
        circuit: cirq.Circuit to add measurements to
        q_dict: dictionary of qubits, keys are integers or strings,
            values are corresponding qubits

    Returns:
         circuit with measurements added
    """
    meas = [XmonMeasurementGate(key=index).on(
        qubit) for qubit, index in q_dict.items()]

    circuit.append(meas)

    return circuit


def expectation_from_sampling(circuit: Circuit,
                              operator: Dict[PauliString, float],
                              n_samples: int):
    """
    Calculates the expactation value of cost function (operator)

    Args:
        circuit: circ.Circuit type which prepares the state we are interested
                 in calculating the expectation value of operator
        operator: Operator input as a dictionary where keys are
                    cirq.ops.PauliString type and values are coefficients
                  example:
                  paulistring = cirq.PauliString(qubit_pauli_map=
                    {qubits[0]:cirq.Pauli.X, qubits[1]: (cirq.Pauli.Z)})
                  paulistring2 = cirq.PauliString(qubit_pauli_map=
                    {qubits[0]:cirq.Pauli.Z, qubits[2]: (cirq.Pauli.Y)})
                  operator = {paulistring: 1.234, paulistring2: -5.678}
        n_samples: number of runs for sampling

    Returns:
        expectation value of operator argument

    """

    qubits = list(circuit.all_qubits())
    sim = XmonSimulator()

    # remove measurements from circuit such that appropriate rotations
    # can be applied, measurements are added later
    circuit = no_meas(circuit)

    # check if operator is quadratic in Pauli Z:
    quadratic_z = True
    zz = [Pauli.Z, Pauli.Z]
    for key in operator.keys():
        if (len(key) != 2):
            quadratic_z = False
            break
        if list(key.values()) != zz:
            quadratic_z = False
            break

    # if operator is only of the form ZZ then call helper function
    if quadratic_z:

        expectation = _expectation_from_sampling_assuming_quadratic(circuit,
                                                                    operator,
                                                                    n_samples)
        return expectation


    # For general operators, the expectation value by sampling
    # over n_samples circuit runs is computed here
    if not quadratic_z:

        expectation = 0
        identity_coeficient = 0.

        for term, coef in operator.items():

            # remove old measurements
            circuit = no_meas(circuit)

            # check if identity:
            if term == ():
                identity_coeficient = coef
                continue

            # Add appropriate rotation gates to circuit
            # and add measurement gates
            # dictionary of qubits to be measured and its indices
            q_dict = dict()

            for qubit, pauli in term.items():

                if pauli == Pauli.X:
                    circuit.append(RotYGate(half_turns=-1 / 2).on(
                        qubit))

                elif pauli == Pauli.Y:
                    circuit.append(RotXGate(half_turns=+1 / 2).on(
                        qubit))

                # After rotation we can re-add measurement gates
                q_dict[qubit] = qubits.index(qubit)

            # Add Measurement gates:
            circuit = measurement_gates(circuit, q_dict)

            # run circuit:
            results = sim.run(circuit, repetitions=n_samples)

            operator_meas = 1

            for qubit_key in results.measurements.keys():
                operator_meas *= results.measurements[qubit_key][:, 0] \
                                 * (-2) + 1

            mean_measurement = np.mean(operator_meas)

            expectation += mean_measurement * coef

        # add identity term:
        expectation += identity_coeficient

        return expectation


def _expectation_from_sampling_assuming_quadratic(
        circuit: Circuit,
        operator: Dict[PauliString, float],
        n_samples: int):
    """
    Helper function that calculates expectation value if operator is
    quadratic and contains only Pauli Z operators.

    Args:
        circuit: circ.Circuit type which prepares the state we are interested
                 in calculating the expectation value of operator
        operator: Operator input as a dictionary where keys are
                    cirq.ops.PauliString type and values are coefficients
                  example:
                  paulistring = cirq.PauliString(qubit_pauli_map=
                    {qubits[0]:cirq.Pauli.X, qubits[1]: (cirq.Pauli.Z)})
                  paulistring2 = cirq.PauliString(qubit_pauli_map=
                    {qubits[0]:cirq.Pauli.Z, qubits[2]: (cirq.Pauli.Y)})
                  operator = {paulistring: 1.234, paulistring2: -5.678}
        n_samples: number of runs for sampling

    Returns:
        expectation value of operator argument
    """

    qubits = list(circuit.all_qubits())
    sim = XmonSimulator()

    # Check whether circuit already has measurement gates:
    last_moment_index = len(circuit) - 1
    last_operations = circuit[last_moment_index].operations

    measurement_qubits = list(qubits)
    indices_measurement = list(range(len(qubits)))

    for operation in last_operations:
        if MeasurementGate.is_measurement(operation):
            measurement_qubits.remove(operation.qubits[0])
            indices_measurement.remove(qubits.index(operation.qubits[0]))

    assert len(indices_measurement) == len(
        measurement_qubits), 'Indices do not match qubits'

    q_dict = {}
    for index in indices_measurement:
        q_dict[measurement_qubits[index]] = index

    # add measurement gate to appropriate qubits

    circuit = measurement_gates(circuit, q_dict)

    # run circuit and store results
    results = sim.run(circuit, repetitions=n_samples)
    results_dict = results.measurements

    identity_coeficient = 0
    expectation_samples = []
    for rep in range(n_samples):
        rep_term = rep
        expectation = 0

        # loop over terms in cost function
        for term, coef in operator.items():
            # skip over identity terms
            if len(term) == 0:
                identity_coeficient = coef
                continue

            # here we enforce that hamiltonian is quadratic in pauli.Z

            # no more than 2 terms
            assert len(term) <= 2, \
                'quadratic_z flag only accepts quadratic Operators'

            # enforce that operators are pauli.Z
            # first create a pauli string of Z acting on same qubits
            z_paulis = {}
            for qubit in term.keys():
                z_paulis[qubit] = Pauli.Z

            new_pauli_string = PauliString(qubit_pauli_map=z_paulis)

            # enforce commutativity with new string
            assert term.commutes_with(new_pauli_string), \
                'Operator must be diagonal in computational basis' \
                'and can only contain Pauli.Z is quadratic_z == True'

            # caculates expectation

            q1 = q_dict[list(term.qubits())[0]]
            if len(term) == 2:
                q2 = q_dict[list(term.qubits())[1]]
            else:
                q2 = q1

            x1 = -2 * int(results_dict[q1][rep_term][0]) + 1
            x2 = -2 * int(results_dict[q2][rep_term][0]) + 1
            print(x1,x2)

            expectation += x1 * coef * x2

        expectation_samples.append(expectation)

    expectation_mean = np.mean(expectation_samples) + identity_coeficient

    return expectation_mean


def expectation_value(circuit: Circuit,
                      operator: Dict[PauliString, float]
                      ):
    """
    Calculates the expactation value of cost function (operator)
    for a circuit run through a simulator by taking an inner product with
    the wavefunction

    Args:
        circuit: circ.Circuit type which prepares the state we are interested
                 in calculating the expectation value of

        operator: Operator input as a dictionary where keys are
                    cirq.ops.PauliString type and values are coefficients
                  example:
                  paulistring = cirq.PauliString(qubit_pauli_map=
                    {qubits[0]:cirq.Pauli.X, qubits[1]: (cirq.Pauli.Z)})
                  paulistring2 = cirq.PauliString(qubit_pauli_map=
                    {qubits[0]:cirq.Pauli.Z, qubits[2]: (cirq.Pauli.Y)})
                  operator = {paulistring: 1.234, paulistring2: -5.678}

    Returns:
        expectation value of operator argument in the state prepared by
        circuit.

    """

    qubits = list(circuit.all_qubits())
    sim = XmonSimulator()

    # ensures no measurements are performed:
    if any(MeasurementGate.is_measurement(op) for op
           in circuit.all_operations()):
        raise ValueError("Circuit has measurements.")

    # number of qubits
    n_qubits = len(qubits)

    # setup the bit strings for each final state:
    # bits = [bin(i)[2:].zfill(n_qubits) for i in range(2**n_qubits)]

    # runs circuit:
    results = sim.simulate(circuit)

    # setup the probabilities for each state
    final_state = results.final_state

    expectation = 0

    # Arrays to help in computation

    pauli_x = np.array([[0, 1], [1, 0]])
    pauli_y = np.array([[0, -1j], [1j, 0]])
    pauli_z = np.array([[1, 0], [0, -1]])
    identity = np.identity(2)

    identity_coeficient = 0
    for term, coef in operator.items():
        # reset operator
        full_op_list = [identity for i in range(n_qubits)]

        # skip over identity terms
        if len(term) == 0:
            identity_coeficient = coef
            continue

        # contruct correct operator
        for qubit, pauli in term.items():

            q_idx = qubits.index(qubit)

            if pauli == Pauli.X:
                full_op_list[q_idx] = pauli_x

            if pauli == Pauli.Y:
                full_op_list[q_idx] = pauli_y

            if pauli == Pauli.Z:
                full_op_list[q_idx] = pauli_z

        # put into matrix form (tensor product)
        if len(full_op_list) == 1:
            full_op = full_op_list[0]
        else:
            full_op = np.kron(full_op_list[0], full_op_list[1])
            for i in range(2, len(full_op_list)):
                full_op = np.kron(full_op, full_op_list[i])

        # caculates expectation for term
        op_on_state = full_op.dot(final_state)

        inner_product = final_state.conjugate().dot(op_on_state)

        expectation += inner_product * coef

    expectation += identity_coeficient
    return expectation.real


# Helper function to remove measurement gates
# ensures there are no measurement gates since rotation gates
# must still be added:
def no_meas(circuit: Circuit):
    cir2 = Circuit()
    for moment in circuit:
        new_moment = []
        for op in moment.operations:
            if not MeasurementGate.is_measurement(op):
                new_moment.append(op)

        cir2.append(new_moment)

    return cir2
