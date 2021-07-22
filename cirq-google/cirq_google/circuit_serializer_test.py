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

from typing import Dict
import pytest
import sympy
from google.protobuf import json_format

import cirq
import cirq_google as cg
from cirq_google.api import v2


def op_proto(json: Dict) -> v2.program_pb2.Operation:
    op = v2.program_pb2.Operation()
    json_format.ParseDict(json, op)
    return op


Q0 = cirq.GridQubit(2, 4)
Q1 = cirq.GridQubit(2, 5)


X_PROTO = op_proto(
    {
        'xpowgate': {'exponent': {'float_value': 1.0}},
        'qubit_constant_index': [0],
    }
)


OPERATIONS = [
    (cirq.X(Q0), X_PROTO),
    (
        cirq.Y(Q0),
        op_proto(
            {
                'ypowgate': {'exponent': {'float_value': 1.0}},
                'qubit_constant_index': [0],
            }
        ),
    ),
    (
        cirq.Z(Q0),
        op_proto(
            {
                'zpowgate': {'exponent': {'float_value': 1.0}},
                'qubit_constant_index': [0],
            }
        ),
    ),
    (
        cirq.XPowGate(exponent=0.125)(Q1),
        op_proto(
            {
                'xpowgate': {'exponent': {'float_value': 0.125}},
                'qubit_constant_index': [0],
            }
        ),
    ),
    (
        cirq.XPowGate(exponent=sympy.Symbol('a'))(Q1),
        op_proto(
            {
                'xpowgate': {'exponent': {'symbol': 'a'}},
                'qubit_constant_index': [0],
            }
        ),
    ),
    (
        cirq.XPowGate(exponent=0.25 + sympy.Symbol('t'))(Q1),
        op_proto(
            {
                'xpowgate': {
                    'exponent': {
                        'func': {
                            'type': 'add',
                            'args': [{'arg_value': {'float_value': 0.25}}, {'symbol': 't'}],
                        }
                    }
                },
                'qubit_constant_index': [0],
            }
        ),
    ),
    (
        cirq.XPowGate(exponent=2 * sympy.Symbol('a'))(Q1),
        op_proto(
            {
                'xpowgate': {
                    'exponent': {
                        'func': {
                            'type': 'mul',
                            'args': [{'arg_value': {'float_value': 2.00}}, {'symbol': 'a'}],
                        }
                    }
                },
                'qubit_constant_index': [0],
            }
        ),
    ),
    (
        cirq.XPowGate(exponent=2 ** sympy.Symbol('a'))(Q1),
        op_proto(
            {
                'xpowgate': {
                    'exponent': {
                        'func': {
                            'type': 'pow',
                            'args': [{'arg_value': {'float_value': 2.00}}, {'symbol': 'a'}],
                        }
                    }
                },
                'qubit_constant_index': [0],
            }
        ),
    ),
    (
        cirq.YPowGate(exponent=0.25)(Q0),
        op_proto(
            {
                'ypowgate': {'exponent': {'float_value': 0.25}},
                'qubit_constant_index': [0],
            }
        ),
    ),
    (
        cirq.ZPowGate(exponent=0.5)(Q0),
        op_proto(
            {
                'zpowgate': {'exponent': {'float_value': 0.5}},
                'qubit_constant_index': [0],
            }
        ),
    ),
    (
        cirq.ZPowGate(exponent=0.5)(Q0).with_tags(cg.PhysicalZTag()),
        op_proto(
            {
                'zpowgate': {'exponent': {'float_value': 0.5}, 'is_physical_z': True},
                'qubit_constant_index': [0],
            }
        ),
    ),
    (
        cirq.PhasedXPowGate(phase_exponent=0.125, exponent=0.5)(Q0),
        op_proto(
            {
                'phasedxpowgate': {
                    'phase_exponent': {'float_value': 0.125},
                    'exponent': {'float_value': 0.5},
                },
                'qubit_constant_index': [0],
            }
        ),
    ),
    (
        cirq.PhasedXZGate(x_exponent=0.125, z_exponent=0.5, axis_phase_exponent=0.25)(Q0),
        op_proto(
            {
                'phasedxzgate': {
                    'x_exponent': {'float_value': 0.125},
                    'z_exponent': {'float_value': 0.5},
                    'axis_phase_exponent': {'float_value': 0.25},
                },
                'qubit_constant_index': [0],
            }
        ),
    ),
    (
        cirq.CZ(Q0, Q1),
        op_proto(
            {
                'czpowgate': {'exponent': {'float_value': 1.0}},
                'qubit_constant_index': [0, 1],
            }
        ),
    ),
    (
        cirq.CZPowGate(exponent=0.5)(Q0, Q1),
        op_proto(
            {
                'czpowgate': {'exponent': {'float_value': 0.5}},
                'qubit_constant_index': [0, 1],
            }
        ),
    ),
    (
        cirq.ISwapPowGate(exponent=0.5)(Q0, Q1),
        op_proto(
            {
                'iswappowgate': {'exponent': {'float_value': 0.5}},
                'qubit_constant_index': [0, 1],
            }
        ),
    ),
    (
        cirq.FSimGate(theta=0.5, phi=0.25)(Q0, Q1),
        op_proto(
            {
                'fsimgate': {'theta': {'float_value': 0.5}, 'phi': {'float_value': 0.25}},
                'qubit_constant_index': [0, 1],
            }
        ),
    ),
    (
        cirq.WaitGate(duration=cirq.Duration(nanos=15))(Q0),
        op_proto(
            {
                'waitgate': {'duration_nanos': {'float_value': 15}},
                'qubit_constant_index': [0],
            }
        ),
    ),
    (
        cirq.MeasurementGate(num_qubits=2, key='iron', invert_mask=(True, False))(Q0, Q1),
        op_proto(
            {
                'measurementgate': {
                    'key': {'arg_value': {'string_value': 'iron'}},
                    'invert_mask': {'arg_value': {'bool_values': {'values': [True, False]}}},
                },
                'qubit_constant_index': [0, 1],
            }
        ),
    ),
]


@pytest.mark.parametrize(('op', 'op_proto'), OPERATIONS)
def test_serialize_deserialize_ops(op, op_proto):
    serializer = cg.CircuitSerializer('my_gate_set')

    # Serialize / Deserializer operation
    raw_constants = {}
    constants = []
    assert op_proto == serializer.serialize_op(
        op, raw_constants=raw_constants, constants=constants, arg_function_language='exp'
    )

    deserialized_constants = [v2.qubit_from_proto_id(constant.qubit.id) for constant in constants]
    assert (
        serializer.deserialize_op(
            op_proto,
            constants=constants,
            deserialized_constants=deserialized_constants,
            arg_function_language='exp',
        )
        == op
    )

    # Serialize / Deserializer circuit with single operation
    circuit = cirq.Circuit(op)
    circuit_proto = v2.program_pb2.Program(
        language=v2.program_pb2.Language(arg_function_language='', gate_set='my_gate_set'),
        circuit=v2.program_pb2.Circuit(
            scheduling_strategy=v2.program_pb2.Circuit.MOMENT_BY_MOMENT,
            moments=[v2.program_pb2.Moment(operations=[op_proto])],
        ),
        constants=constants,
    )
    assert circuit_proto == serializer.serialize(circuit)
    assert serializer.deserialize(circuit_proto) == circuit


def test_serialize_deserialize_circuit():
    serializer = cg.CircuitSerializer('my_gate_set')
    q0 = cirq.GridQubit(1, 1)
    q1 = cirq.GridQubit(1, 2)
    circuit = cirq.Circuit(cirq.X(q0), cirq.X(q1), cirq.X(q0))

    proto = v2.program_pb2.Program(
        language=v2.program_pb2.Language(arg_function_language='', gate_set='my_gate_set'),
        circuit=v2.program_pb2.Circuit(
            scheduling_strategy=v2.program_pb2.Circuit.MOMENT_BY_MOMENT,
            moments=[
                v2.program_pb2.Moment(
                    operations=[
                        v2.program_pb2.Operation(
                            xpowgate=v2.program_pb2.XPowGate(
                                exponent=v2.program_pb2.FloatArg(float_value=1.0)
                            ),
                            qubit_constant_index=[0],
                        ),
                        v2.program_pb2.Operation(
                            xpowgate=v2.program_pb2.XPowGate(
                                exponent=v2.program_pb2.FloatArg(float_value=1.0)
                            ),
                            qubit_constant_index=[1],
                        ),
                    ],
                ),
                v2.program_pb2.Moment(
                    operations=[
                        v2.program_pb2.Operation(
                            xpowgate=v2.program_pb2.XPowGate(
                                exponent=v2.program_pb2.FloatArg(float_value=1.0)
                            ),
                            qubit_constant_index=[0],
                        ),
                    ],
                ),
            ],
        ),
        constants=[
            v2.program_pb2.Constant(qubit=v2.program_pb2.Qubit(id='1_1')),
            v2.program_pb2.Constant(qubit=v2.program_pb2.Qubit(id='1_2')),
        ],
    )
    assert proto == serializer.serialize(circuit)
    assert serializer.deserialize(proto) == circuit


def test_serialize_deserialize_circuit_with_tokens():
    serializer = cg.CircuitSerializer('my_gate_set')
    tag1 = cg.CalibrationTag('abc123')
    tag2 = cg.CalibrationTag('def456')
    circuit = cirq.Circuit(cirq.X(Q0).with_tags(tag1), cirq.X(Q1).with_tags(tag2), cirq.X(Q0))

    op1 = v2.program_pb2.Operation()
    op1.xpowgate.exponent.float_value = 1.0
    op1.qubit_constant_index.append(0)
    op1.token_constant_index = 1

    op2 = v2.program_pb2.Operation()
    op2.xpowgate.exponent.float_value = 1.0
    op2.qubit_constant_index.append(2)
    op2.token_constant_index = 3

    proto = v2.program_pb2.Program(
        language=v2.program_pb2.Language(arg_function_language='', gate_set='my_gate_set'),
        circuit=v2.program_pb2.Circuit(
            scheduling_strategy=v2.program_pb2.Circuit.MOMENT_BY_MOMENT,
            moments=[
                v2.program_pb2.Moment(
                    operations=[op1, op2],
                ),
                v2.program_pb2.Moment(
                    operations=[X_PROTO],
                ),
            ],
        ),
        constants=[
            v2.program_pb2.Constant(qubit=v2.program_pb2.Qubit(id='2_4')),
            v2.program_pb2.Constant(string_value='abc123'),
            v2.program_pb2.Constant(qubit=v2.program_pb2.Qubit(id='2_5')),
            v2.program_pb2.Constant(string_value='def456'),
        ],
    )
    assert proto == serializer.serialize(circuit)
    assert serializer.deserialize(proto) == circuit


def test_serialize_deserialize_circuit_with_subcircuit():
    serializer = cg.CircuitSerializer('my_gate_set')
    tag1 = cg.CalibrationTag('abc123')
    fcircuit = cirq.FrozenCircuit(cirq.X(Q0))
    circuit = cirq.Circuit(
        cirq.X(Q1).with_tags(tag1),
        cirq.CircuitOperation(fcircuit).repeat(repetition_ids=['a', 'b']),
        cirq.CircuitOperation(fcircuit).with_qubit_mapping({Q0: Q1}),
        cirq.X(Q0),
    )

    op1 = v2.program_pb2.Operation()
    op1.xpowgate.exponent.float_value = 1.0
    op1.qubit_constant_index.append(0)
    op1.token_constant_index = 1
    op2 = v2.program_pb2.Operation()
    op2.xpowgate.exponent.float_value = 1.0
    op2.qubit_constant_index.append(2)

    c_op1 = v2.program_pb2.CircuitOperation()
    c_op1.circuit_constant_index = 3
    rep_spec = c_op1.repetition_specification
    rep_spec.repetition_count = 2
    rep_spec.repetition_ids.ids.extend(['a', 'b'])

    c_op2 = v2.program_pb2.CircuitOperation()
    c_op2.circuit_constant_index = 3
    c_op2.repetition_specification.repetition_count = 1
    qmap = c_op2.qubit_map.entries.add()
    qmap.key.id = '2_4'
    qmap.value.id = '2_5'

    proto = v2.program_pb2.Program(
        language=v2.program_pb2.Language(arg_function_language='', gate_set='my_gate_set'),
        circuit=v2.program_pb2.Circuit(
            scheduling_strategy=v2.program_pb2.Circuit.MOMENT_BY_MOMENT,
            moments=[
                v2.program_pb2.Moment(
                    operations=[op1],
                    circuit_operations=[c_op1],
                ),
                v2.program_pb2.Moment(
                    operations=[op2],
                    circuit_operations=[c_op2],
                ),
            ],
        ),
        constants=[
            v2.program_pb2.Constant(qubit=v2.program_pb2.Qubit(id='2_5')),
            v2.program_pb2.Constant(string_value='abc123'),
            v2.program_pb2.Constant(qubit=v2.program_pb2.Qubit(id='2_4')),
            v2.program_pb2.Constant(
                circuit_value=v2.program_pb2.Circuit(
                    scheduling_strategy=v2.program_pb2.Circuit.MOMENT_BY_MOMENT,
                    moments=[
                        v2.program_pb2.Moment(
                            operations=[op2],
                        )
                    ],
                )
            ),
        ],
    )
    assert proto == serializer.serialize(circuit)
    assert serializer.deserialize(proto) == circuit


def test_serialize_deserialize_empty_circuit():
    serializer = cg.CircuitSerializer('my_gate_set')
    circuit = cirq.Circuit()

    proto = v2.program_pb2.Program(
        language=v2.program_pb2.Language(arg_function_language='', gate_set='my_gate_set'),
        circuit=v2.program_pb2.Circuit(
            scheduling_strategy=v2.program_pb2.Circuit.MOMENT_BY_MOMENT, moments=[]
        ),
    )
    assert proto == serializer.serialize(circuit)
    assert serializer.deserialize(proto) == circuit


def test_deserialize_empty_moment():
    serializer = cg.CircuitSerializer('my_gate_set')
    circuit = cirq.Circuit([cirq.Moment()])

    proto = v2.program_pb2.Program(
        language=v2.program_pb2.Language(arg_function_language='', gate_set='my_gate_set'),
        circuit=v2.program_pb2.Circuit(
            scheduling_strategy=v2.program_pb2.Circuit.MOMENT_BY_MOMENT,
            moments=[
                v2.program_pb2.Moment(),
            ],
        ),
    )
    assert serializer.deserialize(proto) == circuit


def test_serialize_unrecognized():
    serializer = cg.CircuitSerializer('my_gate_set')
    with pytest.raises(NotImplementedError, match='program type'):
        serializer.serialize("not quite right")


def test_serialize_deserialize_op():
    serializer = cg.CircuitSerializer('my_gate_set')
    q0 = cirq.GridQubit(1, 1)
    proto = op_proto(
        {
            'xpowgate': {
                'exponent': {'float_value': 0.125},
            },
            'qubit_constant_index': [0],
        }
    )
    constants = []
    raw_constants = {}
    assert proto == serializer.serialize_op(
        cirq.XPowGate(exponent=0.125)(q0), constants=constants, raw_constants=raw_constants
    )

    assert serializer.deserialize_op(
        proto, constants=constants, deserialized_constants=[q0]
    ) == cirq.XPowGate(exponent=0.125)(q0)


def test_serialize_deserialize_op_with_constants():
    serializer = cg.CircuitSerializer('my_gate_set')
    q0 = cirq.GridQubit(1, 1)
    proto = op_proto(
        {
            'xpowgate': {
                'exponent': {'float_value': 0.125},
            },
            'token_constant_index': 1,
            'qubit_constant_index': [0],
        }
    )
    op = cirq.XPowGate(exponent=0.125)(q0).with_tags(cg.CalibrationTag('abc123'))
    constants = []
    raw_constants = {}
    assert proto == serializer.serialize_op(op, constants=constants, raw_constants=raw_constants)
    constant0 = v2.program_pb2.Constant()
    constant0.qubit.id = '1_1'
    constant1 = v2.program_pb2.Constant()
    constant1.string_value = 'abc123'
    assert constants == [constant0, constant1]
    assert q0 in raw_constants
    assert (
        serializer.deserialize_op(proto, constants=constants, deserialized_constants=[q0, 'abc123'])
        == op
    )


def default_circuit_proto():
    op1 = v2.program_pb2.Operation()
    op1.gate.id = 'x_pow'
    op1.args['half_turns'].arg_value.string_value = 'k'
    op1.qubits.add().id = '1_1'

    return v2.program_pb2.Circuit(
        scheduling_strategy=v2.program_pb2.Circuit.MOMENT_BY_MOMENT,
        moments=[
            v2.program_pb2.Moment(
                operations=[op1],
            ),
        ],
    )


def default_circuit():
    return cirq.FrozenCircuit(
        cirq.X(cirq.GridQubit(1, 1)) ** sympy.Symbol('k'),
        cirq.measure(cirq.GridQubit(1, 1), key='m'),
    )


def test_serialize_circuit_op_errors():
    serializer = cg.CircuitSerializer('my_gate_set')
    constants = [default_circuit_proto()]
    raw_constants = {default_circuit(): 0}

    op = cirq.CircuitOperation(default_circuit())
    with pytest.raises(ValueError, match='CircuitOp serialization requires a constants list'):
        serializer.serialize_op(op)

    with pytest.raises(ValueError, match='CircuitOp serialization requires a constants list'):
        serializer.serialize_op(op, constants=constants)

    with pytest.raises(ValueError, match='CircuitOp serialization requires a constants list'):
        serializer.serialize_op(op, raw_constants=raw_constants)


def test_serialize_deserialize_circuit_op():
    serializer = cg.CircuitSerializer('my_gate_set')
    constants = [default_circuit_proto()]
    raw_constants = {default_circuit(): 0}
    deserialized_constants = [default_circuit()]

    proto = v2.program_pb2.CircuitOperation()
    proto.circuit_constant_index = 0
    proto.repetition_specification.repetition_count = 1

    op = cirq.CircuitOperation(default_circuit())
    assert proto == serializer.serialize_op(op, constants=constants, raw_constants=raw_constants)
    assert (
        serializer.deserialize_op(
            proto, constants=constants, deserialized_constants=deserialized_constants
        )
        == op
    )


def test_deserialize_op_bad_operation_proto():
    serializer = cg.CircuitSerializer('my_gate_set')
    proto = v2.program_pb2.Circuit()
    with pytest.raises(ValueError, match='Operation proto has unknown type'):
        serializer.deserialize_op(proto)


def test_deserialize_unsupported_gate_type():
    serializer = cg.CircuitSerializer('my_gate_set')
    proto = op_proto(
        {
            'gate': {'id': 'no_pow'},
            'args': {
                'half_turns': {'arg_value': {'float_value': 0.125}},
            },
            'qubits': [{'id': '1_1'}],
        }
    )
    with pytest.raises(ValueError, match='no_pow'):
        serializer.deserialize_op(proto)


def test_serialize_op_unsupported_type():
    serializer = cg.CircuitSerializer('my_gate_set')
    q0 = cirq.GridQubit(1, 1)
    q1 = cirq.GridQubit(1, 2)
    with pytest.raises(ValueError, match='CNOT'):
        serializer.serialize_op(cirq.CNOT(q0, q1), constants=[], raw_constants={})


def test_serialize_op_bad_operation():
    serializer = cg.CircuitSerializer('my_gate_set')

    class NullOperation(cirq.Operation):
        @property
        def qubits(self):
            return tuple()  # coverage: ignore

        def with_qubits(self, *qubits):
            return self  # coverage: ignore

    null_op = NullOperation()
    with pytest.raises(ValueError, match='Operation is of an unrecognized type'):
        serializer.serialize_op(null_op)


def test_serialize_op_bad_operation_proto():
    serializer = cg.CircuitSerializer('my_gate_set')
    q0 = cirq.GridQubit(1, 1)
    msg = v2.program_pb2.Circuit()
    with pytest.raises(ValueError, match='Operation proto is of an unrecognized type'):
        serializer.serialize_op(cirq.X(q0), msg)


def test_deserialize_invalid_gate_set():
    serializer = cg.CircuitSerializer('my_gate_set')
    proto = v2.program_pb2.Program(
        language=v2.program_pb2.Language(gate_set='not_my_gate_set'),
        circuit=v2.program_pb2.Circuit(
            scheduling_strategy=v2.program_pb2.Circuit.MOMENT_BY_MOMENT, moments=[]
        ),
    )
    with pytest.raises(ValueError, match='not_my_gate_set'):
        serializer.deserialize(proto)

    proto.language.gate_set = ''
    with pytest.raises(ValueError, match='Missing gate set'):
        serializer.deserialize(proto)

    proto = v2.program_pb2.Program(
        circuit=v2.program_pb2.Circuit(
            scheduling_strategy=v2.program_pb2.Circuit.MOMENT_BY_MOMENT, moments=[]
        )
    )
    with pytest.raises(ValueError, match='Missing gate set'):
        serializer.deserialize(proto)


def test_serialize_qubit_backwards_compatibilty():
    """Tests functionality without use_constants"""
    serializer = cg.CircuitSerializer('my_gate_set')
    op = cirq.X(Q0).with_tags(cg.CalibrationTag('blah'))
    actual_proto = serializer.serialize_op(op)
    assert len(actual_proto.qubits) == 1
    assert actual_proto.qubits[0].id == '2_4'
    actual = serializer.deserialize_op(actual_proto)
    assert actual == op


def test_deserialize_schedule_not_supported():
    serializer = cg.CircuitSerializer('my_gate_set')
    proto = v2.program_pb2.Program(
        language=v2.program_pb2.Language(gate_set='my_gate_set'),
        schedule=v2.program_pb2.Schedule(
            scheduled_operations=[v2.program_pb2.ScheduledOperation(start_time_picos=0)]
        ),
    )
    with pytest.raises(ValueError, match='no longer supported'):
        serializer.deserialize(proto, cg.Bristlecone)


def test_deserialize_fsim_missing_parameters():
    serializer = cg.CircuitSerializer('my_gate_set')
    op = op_proto(
        {
            'fsimgate': {
                'theta': {'float_value': 3.0},
            },
            'qubit_constant_index': [0],
        }
    )
    constants = [v2.program_pb2.Constant(qubit=v2.program_pb2.Qubit(id='1_1'))]
    deserialized_constants = [cirq.GridQubit(1, 1)]
    with pytest.raises(ValueError, match='theta and phi must be specified'):
        serializer.deserialize_op(
            op, constants=constants, deserialized_constants=deserialized_constants
        )


def test_deserialize_wrong_types():
    serializer = cg.CircuitSerializer('my_gate_set')
    op = op_proto(
        {
            'measurementgate': {
                'key': {'arg_value': {'float_value': 3.0}},
                'invert_mask': {'arg_value': {'bool_values': {'values': [True, False]}}},
            },
            'qubit_constant_index': [0],
        }
    )
    constants = [v2.program_pb2.Constant(qubit=v2.program_pb2.Qubit(id='1_1'))]
    deserialized_constants = [cirq.GridQubit(1, 1)]
    with pytest.raises(ValueError, match='Incorrect types for measurement gate'):
        serializer.deserialize_op(
            op, constants=constants, deserialized_constants=deserialized_constants
        )
    op = op_proto(
        {
            'measurementgate': {
                'key': {'arg_value': {'string_value': 'key'}},
                'invert_mask': {'arg_value': {'string_value': 'not_a_mask'}},
            },
            'qubit_constant_index': [0],
        }
    )


def test_no_constants_table():
    serializer = cg.CircuitSerializer('my_gate_set')
    op = op_proto(
        {
            'xpowgate': {'exponent': {'float_value': 1.0}},
            'qubits': [{'id': '1_2'}],
            'token_constant_index': 0,
        }
    )

    with pytest.raises(ValueError, match='Proto has references to constants table'):
        serializer.deserialize_op(op)
