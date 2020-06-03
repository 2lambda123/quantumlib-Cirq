# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: cirq/google/api/v2/result.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from cirq.google.api.v2 import program_pb2 as cirq_dot_google_dot_api_dot_v2_dot_program__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='cirq/google/api/v2/result.proto',
  package='cirq.google.api.v2',
  syntax='proto3',
  serialized_options=_b('\n\035com.google.cirq.google.api.v2B\013ResultProtoP\001'),
  serialized_pb=_b('\n\x1f\x63irq/google/api/v2/result.proto\x12\x12\x63irq.google.api.v2\x1a cirq/google/api/v2/program.proto\"@\n\x06Result\x12\x36\n\rsweep_results\x18\x01 \x03(\x0b\x32\x1f.cirq.google.api.v2.SweepResult\"<\n\rBatchedResult\x12+\n\x07results\x18\x01 \x03(\x0b\x32\x1a.cirq.google.api.v2.Result\"j\n\x0bSweepResult\x12\x13\n\x0brepetitions\x18\x01 \x01(\x05\x12\x46\n\x15parameterized_results\x18\x02 \x03(\x0b\x32\'.cirq.google.api.v2.ParameterizedResult\"\x8c\x01\n\x13ParameterizedResult\x12\x31\n\x06params\x18\x01 \x01(\x0b\x32!.cirq.google.api.v2.ParameterDict\x12\x42\n\x13measurement_results\x18\x02 \x03(\x0b\x32%.cirq.google.api.v2.MeasurementResult\"o\n\x11MeasurementResult\x12\x0b\n\x03key\x18\x01 \x01(\t\x12M\n\x19qubit_measurement_results\x18\x02 \x03(\x0b\x32*.cirq.google.api.v2.QubitMeasurementResult\"S\n\x16QubitMeasurementResult\x12(\n\x05qubit\x18\x01 \x01(\x0b\x32\x19.cirq.google.api.v2.Qubit\x12\x0f\n\x07results\x18\x02 \x01(\x0c\"\x8c\x01\n\rParameterDict\x12G\n\x0b\x61ssignments\x18\x01 \x03(\x0b\x32\x32.cirq.google.api.v2.ParameterDict.AssignmentsEntry\x1a\x32\n\x10\x41ssignmentsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x02:\x02\x38\x01\x42.\n\x1d\x63om.google.cirq.google.api.v2B\x0bResultProtoP\x01\x62\x06proto3')
  ,
  dependencies=[cirq_dot_google_dot_api_dot_v2_dot_program__pb2.DESCRIPTOR,])




_RESULT = _descriptor.Descriptor(
  name='Result',
  full_name='cirq.google.api.v2.Result',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sweep_results', full_name='cirq.google.api.v2.Result.sweep_results', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=89,
  serialized_end=153,
)


_BATCHEDRESULT = _descriptor.Descriptor(
  name='BatchedResult',
  full_name='cirq.google.api.v2.BatchedResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='results', full_name='cirq.google.api.v2.BatchedResult.results', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=155,
  serialized_end=215,
)


_SWEEPRESULT = _descriptor.Descriptor(
  name='SweepResult',
  full_name='cirq.google.api.v2.SweepResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='repetitions', full_name='cirq.google.api.v2.SweepResult.repetitions', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='parameterized_results', full_name='cirq.google.api.v2.SweepResult.parameterized_results', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=217,
  serialized_end=323,
)


_PARAMETERIZEDRESULT = _descriptor.Descriptor(
  name='ParameterizedResult',
  full_name='cirq.google.api.v2.ParameterizedResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='params', full_name='cirq.google.api.v2.ParameterizedResult.params', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='measurement_results', full_name='cirq.google.api.v2.ParameterizedResult.measurement_results', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=326,
  serialized_end=466,
)


_MEASUREMENTRESULT = _descriptor.Descriptor(
  name='MeasurementResult',
  full_name='cirq.google.api.v2.MeasurementResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='cirq.google.api.v2.MeasurementResult.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='qubit_measurement_results', full_name='cirq.google.api.v2.MeasurementResult.qubit_measurement_results', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=468,
  serialized_end=579,
)


_QUBITMEASUREMENTRESULT = _descriptor.Descriptor(
  name='QubitMeasurementResult',
  full_name='cirq.google.api.v2.QubitMeasurementResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='qubit', full_name='cirq.google.api.v2.QubitMeasurementResult.qubit', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='results', full_name='cirq.google.api.v2.QubitMeasurementResult.results', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=581,
  serialized_end=664,
)


_PARAMETERDICT_ASSIGNMENTSENTRY = _descriptor.Descriptor(
  name='AssignmentsEntry',
  full_name='cirq.google.api.v2.ParameterDict.AssignmentsEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='cirq.google.api.v2.ParameterDict.AssignmentsEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='cirq.google.api.v2.ParameterDict.AssignmentsEntry.value', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=757,
  serialized_end=807,
)

_PARAMETERDICT = _descriptor.Descriptor(
  name='ParameterDict',
  full_name='cirq.google.api.v2.ParameterDict',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='assignments', full_name='cirq.google.api.v2.ParameterDict.assignments', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_PARAMETERDICT_ASSIGNMENTSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=667,
  serialized_end=807,
)

_RESULT.fields_by_name['sweep_results'].message_type = _SWEEPRESULT
_BATCHEDRESULT.fields_by_name['results'].message_type = _RESULT
_SWEEPRESULT.fields_by_name['parameterized_results'].message_type = _PARAMETERIZEDRESULT
_PARAMETERIZEDRESULT.fields_by_name['params'].message_type = _PARAMETERDICT
_PARAMETERIZEDRESULT.fields_by_name['measurement_results'].message_type = _MEASUREMENTRESULT
_MEASUREMENTRESULT.fields_by_name['qubit_measurement_results'].message_type = _QUBITMEASUREMENTRESULT
_QUBITMEASUREMENTRESULT.fields_by_name['qubit'].message_type = cirq_dot_google_dot_api_dot_v2_dot_program__pb2._QUBIT
_PARAMETERDICT_ASSIGNMENTSENTRY.containing_type = _PARAMETERDICT
_PARAMETERDICT.fields_by_name['assignments'].message_type = _PARAMETERDICT_ASSIGNMENTSENTRY
DESCRIPTOR.message_types_by_name['Result'] = _RESULT
DESCRIPTOR.message_types_by_name['BatchedResult'] = _BATCHEDRESULT
DESCRIPTOR.message_types_by_name['SweepResult'] = _SWEEPRESULT
DESCRIPTOR.message_types_by_name['ParameterizedResult'] = _PARAMETERIZEDRESULT
DESCRIPTOR.message_types_by_name['MeasurementResult'] = _MEASUREMENTRESULT
DESCRIPTOR.message_types_by_name['QubitMeasurementResult'] = _QUBITMEASUREMENTRESULT
DESCRIPTOR.message_types_by_name['ParameterDict'] = _PARAMETERDICT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Result = _reflection.GeneratedProtocolMessageType('Result', (_message.Message,), {
  'DESCRIPTOR' : _RESULT,
  '__module__' : 'cirq.google.api.v2.result_pb2'
  # @@protoc_insertion_point(class_scope:cirq.google.api.v2.Result)
  })
_sym_db.RegisterMessage(Result)

BatchedResult = _reflection.GeneratedProtocolMessageType('BatchedResult', (_message.Message,), {
  'DESCRIPTOR' : _BATCHEDRESULT,
  '__module__' : 'cirq.google.api.v2.result_pb2'
  # @@protoc_insertion_point(class_scope:cirq.google.api.v2.BatchedResult)
  })
_sym_db.RegisterMessage(BatchedResult)

SweepResult = _reflection.GeneratedProtocolMessageType('SweepResult', (_message.Message,), {
  'DESCRIPTOR' : _SWEEPRESULT,
  '__module__' : 'cirq.google.api.v2.result_pb2'
  # @@protoc_insertion_point(class_scope:cirq.google.api.v2.SweepResult)
  })
_sym_db.RegisterMessage(SweepResult)

ParameterizedResult = _reflection.GeneratedProtocolMessageType('ParameterizedResult', (_message.Message,), {
  'DESCRIPTOR' : _PARAMETERIZEDRESULT,
  '__module__' : 'cirq.google.api.v2.result_pb2'
  # @@protoc_insertion_point(class_scope:cirq.google.api.v2.ParameterizedResult)
  })
_sym_db.RegisterMessage(ParameterizedResult)

MeasurementResult = _reflection.GeneratedProtocolMessageType('MeasurementResult', (_message.Message,), {
  'DESCRIPTOR' : _MEASUREMENTRESULT,
  '__module__' : 'cirq.google.api.v2.result_pb2'
  # @@protoc_insertion_point(class_scope:cirq.google.api.v2.MeasurementResult)
  })
_sym_db.RegisterMessage(MeasurementResult)

QubitMeasurementResult = _reflection.GeneratedProtocolMessageType('QubitMeasurementResult', (_message.Message,), {
  'DESCRIPTOR' : _QUBITMEASUREMENTRESULT,
  '__module__' : 'cirq.google.api.v2.result_pb2'
  # @@protoc_insertion_point(class_scope:cirq.google.api.v2.QubitMeasurementResult)
  })
_sym_db.RegisterMessage(QubitMeasurementResult)

ParameterDict = _reflection.GeneratedProtocolMessageType('ParameterDict', (_message.Message,), {

  'AssignmentsEntry' : _reflection.GeneratedProtocolMessageType('AssignmentsEntry', (_message.Message,), {
    'DESCRIPTOR' : _PARAMETERDICT_ASSIGNMENTSENTRY,
    '__module__' : 'cirq.google.api.v2.result_pb2'
    # @@protoc_insertion_point(class_scope:cirq.google.api.v2.ParameterDict.AssignmentsEntry)
    })
  ,
  'DESCRIPTOR' : _PARAMETERDICT,
  '__module__' : 'cirq.google.api.v2.result_pb2'
  # @@protoc_insertion_point(class_scope:cirq.google.api.v2.ParameterDict)
  })
_sym_db.RegisterMessage(ParameterDict)
_sym_db.RegisterMessage(ParameterDict.AssignmentsEntry)


DESCRIPTOR._options = None
_PARAMETERDICT_ASSIGNMENTSENTRY._options = None
# @@protoc_insertion_point(module_scope)
