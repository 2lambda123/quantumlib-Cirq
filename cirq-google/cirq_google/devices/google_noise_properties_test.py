from typing import Dict, List, Tuple
import numpy as np
import pytest
import cirq, cirq_google

# from cirq.testing import assert_equivalent_op_tree
from cirq.devices.noise_utils import (
    OpIdentifier,
    PHYSICAL_GATE_TAG,
)

from cirq_google.devices.google_noise_properties import (
    GoogleNoiseProperties,
    NoiseModelFromGoogleNoiseProperties,
)


SINGLE_QUBIT_GATES = GoogleNoiseProperties.single_qubit_gates()
TWO_QUBIT_GATES = GoogleNoiseProperties.two_qubit_gates()
SYMMETRIC_TWO_QUBIT_GATES = TWO_QUBIT_GATES

DEFAULT_GATE_NS: Dict[type, float] = {
    cirq.ZPowGate: 25.0,
    cirq.MeasurementGate: 4000.0,
    cirq.ResetChannel: 250.0,
    cirq.PhasedXZGate: 25.0,
    # SYC is normally 12ns, but setting it equal to other two-qubit gates
    # simplifies the tests.
    cirq_google.SycamoreGate: 32.0,
    cirq.FSimGate: 32.0,
    cirq.PhasedFSimGate: 32.0,
    cirq.ISwapPowGate: 32.0,
    cirq.CZPowGate: 32.0,
    # cirq.WaitGate is a special case.
}


# These properties are for testing purposes only - they are not representative
# of device behavior for any existing hardware.
def sample_noise_properties(
    system_qubits: List[cirq.Qid], qubit_pairs: List[Tuple[cirq.Qid, cirq.Qid]]
):
    return GoogleNoiseProperties(
        gate_times_ns=DEFAULT_GATE_NS,
        T1_ns={q: 1e5 for q in system_qubits},
        Tphi_ns={q: 2e5 for q in system_qubits},
        ro_fidelities={q: [0.001, 0.01] for q in system_qubits},
        gate_pauli_errors={
            **{OpIdentifier(g, q): 0.001 for g in SINGLE_QUBIT_GATES for q in system_qubits},
            **{OpIdentifier(g, q0, q1): 0.01 for g in TWO_QUBIT_GATES for q0, q1 in qubit_pairs},
        },
        fsim_errors={
            OpIdentifier(g, q0, q1): cirq.PhasedFSimGate(0.01, 0.03, 0.04, 0.05, 0.02)
            for g in SYMMETRIC_TWO_QUBIT_GATES
            for q0, q1 in qubit_pairs
        },
    )


def test_str():
    q0 = cirq.LineQubit(0)
    props = sample_noise_properties([q0], [])
    assert str(props) == 'GoogleNoiseProperties'


def test_repr_evaluation():
    q0, q1 = cirq.LineQubit.range(2)
    props = sample_noise_properties([q0, q1], [(q0, q1), (q1, q0)])
    props_from_repr = eval(repr(props))
    assert props_from_repr == props


def test_json_serialization():
    q0, q1 = cirq.LineQubit.range(2)
    props = sample_noise_properties([q0, q1], [(q0, q1), (q1, q0)])
    props_json = cirq.to_json(props)
    props_from_json = cirq.read_json(json_text=props_json)
    assert props_from_json == props


def test_init_validation():
    q0, q1 = cirq.LineQubit.range(2)
    with pytest.raises(ValueError, match='Keys specified for T1 and Tphi are not identical.'):
        _ = GoogleNoiseProperties(
            gate_times_ns=DEFAULT_GATE_NS,
            T1_ns={},
            Tphi_ns={q0: 1},
            ro_fidelities={q0: [0.1, 0.2]},
            gate_pauli_errors={},
        )

    with pytest.raises(ValueError, match='does not appear in the symmetric or asymmetric'):
        _ = GoogleNoiseProperties(
            gate_times_ns=DEFAULT_GATE_NS,
            T1_ns={q0: 1},
            Tphi_ns={q0: 1},
            ro_fidelities={q0: [0.1, 0.2]},
            gate_pauli_errors={
                OpIdentifier(cirq.ZPowGate, q0): 0.1,
                OpIdentifier(cirq.CZPowGate, q0, q1): 0.1,
                OpIdentifier(cirq.CZPowGate, q1, q0): 0.1,
            },
            fsim_errors={
                OpIdentifier(cirq.CNOT, q0, q1): cirq.PhasedFSimGate(theta=0.1),
            },
        )

    # Errors are ignored if validation is disabled.
    _ = GoogleNoiseProperties(
        gate_times_ns=DEFAULT_GATE_NS,
        T1_ns={q0: 1},
        Tphi_ns={q0: 1},
        ro_fidelities={q0: [0.1, 0.2]},
        gate_pauli_errors={
            OpIdentifier(cirq.ZPowGate, q0): 0.1,
            OpIdentifier(cirq.CZPowGate, q0, q1): 0.1,
            OpIdentifier(cirq.CZPowGate, q1, q0): 0.1,
        },
        validate=False,
        fsim_errors={
            OpIdentifier(cirq.CNOT, q0, q1): cirq.PhasedFSimGate(theta=0.1),
        },
    )


def test_depol_memoization():
    # Verify that depolarizing error is memoized.
    q0 = cirq.LineQubit(0)
    props = sample_noise_properties([q0], [])
    depol_error_a = props.get_depolarizing_error()
    depol_error_b = props.get_depolarizing_error()
    assert depol_error_a == depol_error_b
    assert depol_error_a is depol_error_b


def test_zphase_gates():
    q0 = cirq.LineQubit(0)
    props = sample_noise_properties([q0], [])
    model = NoiseModelFromGoogleNoiseProperties(props)
    circuit = cirq.Circuit(cirq.Z(q0) ** 0.3)
    noisy_circuit = circuit.with_noise(model)
    assert noisy_circuit == circuit


@pytest.mark.parametrize(
    'op',
    [
        (cirq.Z(cirq.LineQubit(0)) ** 0.3).with_tags(cirq_google.PhysicalZTag),
        cirq.PhasedXZGate(x_exponent=0.8, z_exponent=0.2, axis_phase_exponent=0.1).on(
            cirq.LineQubit(0)
        ),
    ],
)
def test_single_qubit_gates(op):
    q0 = cirq.LineQubit(0)
    props = sample_noise_properties([q0], [])
    model = NoiseModelFromGoogleNoiseProperties(props)
    circuit = cirq.Circuit(op)
    noisy_circuit = circuit.with_noise(model)
    assert len(noisy_circuit.moments) == 3
    assert len(noisy_circuit.moments[0].operations) == 1
    assert noisy_circuit.moments[0].operations[0] == op.with_tags(PHYSICAL_GATE_TAG)

    # Depolarizing noise
    assert len(noisy_circuit.moments[1].operations) == 1
    depol_op = noisy_circuit.moments[1].operations[0]
    assert isinstance(depol_op.gate, cirq.DepolarizingChannel)
    assert np.isclose(depol_op.gate.p, 0.00081252)

    # Thermal noise
    assert len(noisy_circuit.moments[2].operations) == 1
    thermal_op = noisy_circuit.moments[2].operations[0]
    assert isinstance(thermal_op.gate, cirq.KrausChannel)
    thermal_choi = cirq.kraus_to_choi(cirq.kraus(thermal_op))
    assert np.allclose(
        thermal_choi,
        [
            [1, 0, 0, 9.99750031e-01],
            [0, 2.49968753e-04, 0, 0],
            [0, 0, 0, 0],
            [9.99750031e-01, 0, 0, 9.99750031e-01],
        ],
    )


@pytest.mark.parametrize(
    'op',
    [
        cirq.ISWAP(*cirq.LineQubit.range(2)) ** 0.6,
        cirq.CZ(*cirq.LineQubit.range(2)) ** 0.3,
        cirq_google.SYC(*cirq.LineQubit.range(2)),
    ],
)
def test_two_qubit_gates(op):
    q0, q1 = cirq.LineQubit.range(2)
    props = sample_noise_properties([q0, q1], [(q0, q1), (q1, q0)])
    model = NoiseModelFromGoogleNoiseProperties(props)
    circuit = cirq.Circuit(op)
    noisy_circuit = circuit.with_noise(model)
    assert len(noisy_circuit.moments) == 4
    assert len(noisy_circuit.moments[0].operations) == 1
    assert noisy_circuit.moments[0].operations[0] == op.with_tags(PHYSICAL_GATE_TAG)

    # Depolarizing noise
    assert len(noisy_circuit.moments[1].operations) == 1
    depol_op = noisy_circuit.moments[1].operations[0]
    assert isinstance(depol_op.gate, cirq.DepolarizingChannel)
    assert np.isclose(depol_op.gate.p, 0.00719705)

    # FSim angle corrections
    assert len(noisy_circuit.moments[2].operations) == 1
    fsim_op = noisy_circuit.moments[2].operations[0]
    assert isinstance(fsim_op.gate, cirq.PhasedFSimGate)
    assert fsim_op == cirq.PhasedFSimGate(
        theta=0.01,
        zeta=0.03,
        chi=0.04,
        gamma=0.05,
        phi=0.02
    ).on(q0, q1)

    # Thermal noise
    assert len(noisy_circuit.moments[3].operations) == 2
    thermal_op_0 = noisy_circuit.moments[3].operation_at(q0)
    thermal_op_1 = noisy_circuit.moments[3].operation_at(q1)
    assert isinstance(thermal_op_0.gate, cirq.KrausChannel)
    assert isinstance(thermal_op_1.gate, cirq.KrausChannel)
    thermal_choi_0 = cirq.kraus_to_choi(cirq.kraus(thermal_op_0))
    thermal_choi_1 = cirq.kraus_to_choi(cirq.kraus(thermal_op_1))
    # TODO: check iswap noise
    expected_thermal_choi = np.array(
        [
            [1, 0, 0, 9.99680051e-01],
            [0, 3.19948805e-04, 0, 0],
            [0, 0, 0, 0],
            [9.99680051e-01, 0, 0, 9.99680051e-01],
        ]
    )
    assert np.allclose(thermal_choi_0, expected_thermal_choi)
    assert np.allclose(thermal_choi_1, expected_thermal_choi)


def test_measure_gates():
    q00, q01, q10, q11 = cirq.GridQubit.rect(2, 2)
    qubits = [q00, q01, q10, q11]
    props = sample_noise_properties(
        qubits,
        [
            (q00, q01),
            (q01, q00),
            (q10, q11),
            (q11, q10),
            (q00, q10),
            (q10, q00),
            (q01, q11),
            (q11, q01),
        ],
    )
    model = NoiseModelFromGoogleNoiseProperties(props)
    op = cirq.measure(*qubits, key='m')
    circuit = cirq.Circuit(cirq.measure(*qubits, key='m'))
    noisy_circuit = circuit.with_noise(model)
    assert len(noisy_circuit.moments) == 2

    # Amplitude damping before measurement
    assert len(noisy_circuit.moments[0].operations) == 4
    for q in qubits:
        op = noisy_circuit.moments[0].operation_at(q)
        assert isinstance(op.gate, cirq.GeneralizedAmplitudeDampingChannel), q
        assert np.isclose(op.gate.p, 0.90909090), q
        assert np.isclose(op.gate.gamma, 0.011), q

    # Original measurement is after the noise.
    assert len(noisy_circuit.moments[1].operations) == 1
    # Measurements are untagged during reconstruction.
    assert noisy_circuit.moments[1] == circuit.moments[0]


def test_wait_gates():
    q0 = cirq.LineQubit(0)
    props = sample_noise_properties([q0], [])
    model = NoiseModelFromGoogleNoiseProperties(props)
    op = cirq.wait(q0, nanos=100)
    circuit = cirq.Circuit(op)
    noisy_circuit = circuit.with_noise(model)
    assert len(noisy_circuit.moments) == 2
    assert noisy_circuit.moments[0].operations[0] == op.with_tags(PHYSICAL_GATE_TAG)

    # No depolarizing noise because WaitGate has none.

    assert len(noisy_circuit.moments[1].operations) == 1
    thermal_op = noisy_circuit.moments[1].operations[0]
    assert isinstance(thermal_op.gate, cirq.KrausChannel)
    thermal_choi = cirq.kraus_to_choi(cirq.kraus(thermal_op))
    assert np.allclose(
        thermal_choi,
        [
            [1, 0, 0, 9.990005e-01],
            [0, 9.99500167e-04, 0, 0],
            [0, 0, 0, 0],
            [9.990005e-01, 0, 0, 9.990005e-01],
        ],
    )
