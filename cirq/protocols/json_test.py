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
import abc
import inspect

import io
import os

import pytest

import numpy as np
import cirq
import cirq.protocols


def assert_roundtrip(obj, text_should_be=None):
    buffer = io.StringIO()
    cirq.protocols.to_json(obj, buffer)

    if text_should_be is not None:
        buffer.seek(0)
        text = buffer.read()
        assert text == text_should_be

    buffer.seek(0)
    obj2 = cirq.protocols.read_json(buffer)
    if isinstance(obj, np.ndarray):
        np.testing.assert_equal(obj, obj2)
    else:
        assert obj == obj2


def test_line_qubit_roundtrip():
    q1 = cirq.LineQubit(12)
    assert_roundtrip(q1,
                     text_should_be="""{
  "cirq_type": "LineQubit",
  "x": 12
}""")


def test_gridqubit_roundtrip():
    q = cirq.GridQubit(15, 18)
    assert_roundtrip(q,
                     text_should_be="""{
  "cirq_type": "GridQubit",
  "row": 15,
  "col": 18
}""")


def test_op_roundtrip():
    q = cirq.LineQubit(5)
    op1 = cirq.Rx(.123).on(q)
    assert_roundtrip(op1,
                     text_should_be="""{
  "cirq_type": "GateOperation",
  "gate": {
    "cirq_type": "XPowGate",
    "exponent": 0.03915211600060625,
    "global_shift": -0.5
  },
  "qubits": [
    {
      "cirq_type": "LineQubit",
      "x": 5
    }
  ]
}""")


def test_op_roundtrip_filename(tmpdir):
    filename = f'{tmpdir}/op.json'
    q = cirq.LineQubit(5)
    op1 = cirq.Rx(.123).on(q)
    cirq.to_json(op1, filename)
    assert os.path.exists(filename)
    op2 = cirq.read_json(filename)
    assert op1 == op2


def test_fail_to_resolve():
    buffer = io.StringIO()
    buffer.write("""
    {
      "cirq_type": "MyCustomClass",
      "data": [1, 2, 3]
    }
    """)
    buffer.seek(0)

    with pytest.raises(ValueError) as e:
        cirq.read_json(buffer)
    assert e.match("Could not resolve type 'MyCustomClass' "
                   "during deserialization")


QUBITS = cirq.LineQubit.range(5)
Q0, Q1, Q2, Q3, Q4 = QUBITS

TEST_OBJECTS = {
    'CCNOT':
    cirq.CCNOT,
    'CCX':
    cirq.CCX,
    'CCXPowGate':
    cirq.CCXPowGate(exponent=0.123, global_shift=0.456),
    'CCZ':
    cirq.CCZ,
    'CCZPowGate':
    cirq.CCZPowGate(exponent=0.123, global_shift=0.456),
    'CNOT':
    cirq.CNOT,
    'CNotPowGate':
    cirq.CNotPowGate(exponent=0.123, global_shift=0.456),
    'CX':
    cirq.CX,
    'CSWAP':
    cirq.CSWAP,
    'CSwapGate':
    cirq.CSwapGate(),
    'CZ':
    cirq.CZ,
    'CZPowGate':
    cirq.CZPowGate(exponent=0.123, global_shift=0.456),
    'Circuit': [
        cirq.Circuit.from_ops(cirq.H.on_each(QUBITS), cirq.measure(*QUBITS)),
        cirq.Circuit.from_ops(cirq.CCNOT(Q0, Q1, Q2),
                              cirq.X(Q0)**0.123)
    ],
    'FREDKIN':
    cirq.FREDKIN,
    'FSimGate':
    cirq.FSimGate(theta=0.123, phi=.456),
    'GateOperation': [
        cirq.CCNOT(*cirq.LineQubit.range(3)),
        cirq.CCZ(*cirq.LineQubit.range(3)),
        cirq.CNOT(*cirq.LineQubit.range(2)),
        cirq.CSWAP(*cirq.LineQubit.range(3)),
        cirq.CZ(*cirq.LineQubit.range(2))
    ],
    'GlobalPhaseOperation':
    cirq.GlobalPhaseOperation(-1j),
    'GridQubit':
    cirq.GridQubit(10, 11),
    'H':
    cirq.H,
    'HPowGate': [cirq.HPowGate(exponent=-8), cirq.H**0.123],
    'I':
    cirq.I,
    'ISWAP':
    cirq.ISWAP,
    'ISwapPowGate': [cirq.ISwapPowGate(exponent=-8), cirq.ISWAP**0.123],
    'IdentityGate': [cirq.I, cirq.IdentityGate(num_qubits=5)],
    'LineQubit': [cirq.LineQubit(0), cirq.LineQubit(123)],
    'MeasurementGate': [
        cirq.MeasurementGate(num_qubits=3, key='z'),
        cirq.MeasurementGate(num_qubits=3,
                             key='z',
                             invert_mask=(True, False, True)),
    ],
    'Moment': [
        cirq.Moment(operations=[cirq.X(Q0), cirq.Y(Q1),
                                cirq.Z(Q2)]),
    ],
    'NamedQubit':
    cirq.NamedQubit('hi mom'),
    'PauliString': [
        cirq.PauliString({
            Q0: cirq.X,
            Q1: cirq.Y,
            Q2: cirq.Z
        }),
        cirq.X(Q0) * cirq.Y(Q1) * 123
    ],
    'PhasedXPowGate':
    cirq.PhasedXPowGate(phase_exponent=0.123,
                        exponent=0.456,
                        global_shift=0.789),
    'X':
    cirq.X,
    'Y':
    cirq.Y,
    'Z':
    cirq.Z,
    'S':
    cirq.S,
    'SWAP':
    cirq.SWAP,
    'SingleQubitPauliStringGateOperation':
    cirq.X(Q0),
    'SwapPowGate': [cirq.SwapPowGate(), cirq.SWAP**0.5],
    'T':
    cirq.T,
    'TOFFOLI':
    cirq.TOFFOLI,
    'UnconstrainedDevice':
    cirq.UnconstrainedDevice,
    'XPowGate':
    cirq.X**0.123,
    'XX':
    cirq.XX,
    'XXPowGate': [cirq.XXPowGate(), cirq.XX**0.123],
    'YPowGate':
    cirq.Y**0.456,
    'YY':
    cirq.YY,
    'YYPowGate': [cirq.YYPowGate(), cirq.YY**0.456],
    'ZPowGate':
    cirq.Z**0.789,
    'ZZ':
    cirq.ZZ,
    'ZZPowGate': [cirq.ZZPowGate(), cirq.ZZ**0.789],
    'complex': [1 + 2j],
    'ndarray': [np.ones((11, 5)), np.arange(3)],
    'int':
    5,
}

SHOULDNT_BE_SERIALIZED = [

    # Circuit optimizers are function-like. Only attributes
    # are ignore_failures, tolerance, and other feature flags
    'ConvertToCzAndSingleGates',
    'ConvertToIonGates',
    'ConvertToNeutralAtomGates',
    'DropEmptyMoments',
    'DropNegligible',
    'EjectPhasedPaulis',
    'EjectZ',
    'ExpandComposite',
    'MergeInteractions',
    'MergeSingleQubitGates',
    'PointOptimizer',

    # global objects
    'CONTROL_TAG',
    'PAULI_BASIS',

    # abstract, but not inspect.isabstract():
    'InterchangeableQubitsGate',
    'Pauli',
    'SingleQubitGate',
    'ThreeQubitGate',
    'TwoQubitGate',

    # protocols:
    'SupportsApplyChannel',
    'SupportsApproximateEquality',
    'SupportsChannel',
    'SupportsCircuitDiagramInfo',
    'SupportsConsistentApplyUnitary',
    'SupportsDecompose',
    'SupportsDecomposeWithQubits',
    'SupportsExplicitNumQubits',
    'SupportsExplicitQidShape',
    'SupportsMixture',
    'SupportsParameterization',
    'SupportsPhase',
    'SupportsQasm',
    'SupportsQasmWithArgs',
    'SupportsQasmWithArgsAndQubits',
    'SupportsTraceDistanceBound',
    'SupportsUnitary',

    # mypy types:
    'OP_TREE',
    'ParamResolverOrSimilarType',
    'PauliSumLike',
    'QubitOrderOrList',
    'Sweepable',
    'TParamVal',

    # utility:
    'Unique',
]


def _get_all_public_classes():
    for cls_name, cls_cls in inspect.getmembers(cirq):
        if inspect.isfunction(cls_cls) or inspect.ismodule(cls_cls):
            continue

        if cls_name in SHOULDNT_BE_SERIALIZED:
            continue

        if not inspect.isclass(cls_cls):
            # singletons, for instance
            cls_cls = cls_cls.__class__

        if cls_name.startswith('_'):
            continue

        if (inspect.isclass(cls_cls) and
            (inspect.isabstract(cls_cls) or issubclass(cls_cls, abc.ABCMeta))):
            continue

        yield cls_name, cls_cls

    # extra
    yield 'complex', complex
    yield 'ndarray', np.ndarray
    yield 'int', int


def test_shouldnt_be_serialized_no_superfluous():
    # everything in the list should be ignored for a reason
    names = [
        name for name, _ in inspect.getmembers(
            cirq, lambda x: not (inspect.ismodule(x) or inspect.isfunction(x)))
    ]
    for name in SHOULDNT_BE_SERIALIZED:
        assert name in names


def test_not_yet_serializable_no_superfluous():
    # everything in the list should be ignored for a reason
    names = [
        name for name, _ in inspect.getmembers(
            cirq, lambda x: not (inspect.ismodule(x) or inspect.isfunction(x)))
    ]
    for name in NOT_YET_SERIALIZABLE:
        assert name in names


def test_mutually_exclusive_blacklist():
    assert len(set(SHOULDNT_BE_SERIALIZED) & set(NOT_YET_SERIALIZABLE)) == 0


NOT_YET_SERIALIZABLE = [
    'AmplitudeDampingChannel',
    'ApplyChannelArgs',
    'ApplyUnitaryArgs',
    'ApproxPauliStringExpectation',
    'AsymmetricDepolarizingChannel',
    'AxisAngleDecomposition',
    'BitFlipChannel',
    'CircuitDag',
    'CircuitDiagramInfo',
    'CircuitDiagramInfoArgs',
    'CircuitSampleJob',
    'ComputeDisplaysResult',
    'ConstantQubitNoiseModel',
    'ControlledGate',
    'ControlledOperation',
    'DensityMatrixSimulator',
    'DensityMatrixSimulatorState',
    'DensityMatrixStepResult',
    'DensityMatrixTrialResult',
    'DepolarizingChannel',
    'Duration',
    'GeneralizedAmplitudeDampingChannel',
    'Heatmap',
    'InsertStrategy',
    'IonDevice',
    'KakDecomposition',
    'LinearCombinationOfGates',
    'LinearCombinationOfOperations',
    'LinearDict',
    'Linspace',
    'NO_NOISE',
    'NeutralAtomDevice',
    'ParallelGateOperation',
    'ParamResolver',
    'PauliInteractionGate',
    'PauliStringExpectation',
    'PauliStringPhasor',
    'PauliSum',
    'PauliSumCollector',
    'PauliTransform',
    'PeriodicValue',
    'PhaseDampingChannel',
    'PhaseFlipChannel',
    'PointOptimizationSummary',
    'Points',
    'Product',
    'QasmArgs',
    'QasmOutput',
    'QubitOrder',
    'ResetChannel',
    'Schedule',
    'ScheduledOperation',
    'SimulationTrialResult',
    'Simulator',
    'SingleQubitCliffordGate',
    'SingleQubitMatrixGate',
    'SparseSimulatorStep',
    'StateVectorMixin',
    'TextDiagramDrawer',
    'ThreeQubitDiagonalGate',
    'Timestamp',
    'TrialResult',
    'TwoQubitMatrixGate',
    'UnitSweep',
    'WaveFunctionSimulatorState',
    'WaveFunctionTrialResult',
    'Zip',
    'reset',
]


@pytest.mark.parametrize('cirq_type,cls', _get_all_public_classes())
def test_all_roundtrip(cirq_type: str, cls):
    if cirq_type in NOT_YET_SERIALIZABLE:
        return pytest.xfail(reason="Not serializable (yet)")

    objs = TEST_OBJECTS[cirq_type]
    if not isinstance(objs, list):
        objs = [objs]

    for obj in objs:
        assert isinstance(obj, cls)

        # more strict: must be exact (no subclasses)
        assert type(obj) == cls
        assert_roundtrip(obj)
