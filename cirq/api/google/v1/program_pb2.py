# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: cirq/api/google/v1/program.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from cirq.api.google.v1 import operations_pb2 as cirq_dot_api_dot_google_dot_v1_dot_operations__pb2
from cirq.api.google.v1 import params_pb2 as cirq_dot_api_dot_google_dot_v1_dot_params__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='cirq/api/google/v1/program.proto',
  package='cirq.api.google.v1',
  syntax='proto3',
  serialized_pb=_b('\n cirq/api/google/v1/program.proto\x12\x12\x63irq.api.google.v1\x1a#cirq/api/google/v1/operations.proto\x1a\x1f\x63irq/api/google/v1/params.proto\"~\n\x07Program\x12\x31\n\noperations\x18\x01 \x03(\x0b\x32\x1d.cirq.api.google.v1.Operation\x12@\n\x10parameter_sweeps\x18\x02 \x03(\x0b\x32\".cirq.api.google.v1.ParameterSweepB\x02\x18\x01\"J\n\nRunContext\x12<\n\x10parameter_sweeps\x18\x01 \x03(\x0b\x32\".cirq.api.google.v1.ParameterSweep\"e\n\x13ParameterizedResult\x12\x31\n\x06params\x18\x01 \x01(\x0b\x32!.cirq.api.google.v1.ParameterDict\x12\x1b\n\x13measurement_results\x18\x02 \x01(\x0c\"]\n\x0eMeasurementKey\x12\x0b\n\x03key\x18\x01 \x01(\t\x12)\n\x06qubits\x18\x02 \x03(\x0b\x32\x19.cirq.api.google.v1.Qubit\x12\x13\n\x0binvert_mask\x18\x03 \x03(\x08\"\xa8\x01\n\x0bSweepResult\x12\x13\n\x0brepetitions\x18\x01 \x01(\x05\x12<\n\x10measurement_keys\x18\x02 \x03(\x0b\x32\".cirq.api.google.v1.MeasurementKey\x12\x46\n\x15parameterized_results\x18\x03 \x03(\x0b\x32\'.cirq.api.google.v1.ParameterizedResult\"@\n\x06Result\x12\x36\n\rsweep_results\x18\x01 \x03(\x0b\x32\x1f.cirq.api.google.v1.SweepResultB/\n\x1d\x63om.google.cirq.api.google.v1B\x0cProgramProtoP\x01\x62\x06proto3')
  ,
  dependencies=[cirq_dot_api_dot_google_dot_v1_dot_operations__pb2.DESCRIPTOR,cirq_dot_api_dot_google_dot_v1_dot_params__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_PROGRAM = _descriptor.Descriptor(
  name='Program',
  full_name='cirq.api.google.v1.Program',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='operations', full_name='cirq.api.google.v1.Program.operations', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='parameter_sweeps', full_name='cirq.api.google.v1.Program.parameter_sweeps', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=_descriptor._ParseOptions(descriptor_pb2.FieldOptions(), _b('\030\001'))),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=126,
  serialized_end=252,
)


_RUNCONTEXT = _descriptor.Descriptor(
  name='RunContext',
  full_name='cirq.api.google.v1.RunContext',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='parameter_sweeps', full_name='cirq.api.google.v1.RunContext.parameter_sweeps', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=254,
  serialized_end=328,
)


_PARAMETERIZEDRESULT = _descriptor.Descriptor(
  name='ParameterizedResult',
  full_name='cirq.api.google.v1.ParameterizedResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='params', full_name='cirq.api.google.v1.ParameterizedResult.params', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='measurement_results', full_name='cirq.api.google.v1.ParameterizedResult.measurement_results', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=330,
  serialized_end=431,
)


_MEASUREMENTKEY = _descriptor.Descriptor(
  name='MeasurementKey',
  full_name='cirq.api.google.v1.MeasurementKey',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='cirq.api.google.v1.MeasurementKey.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='qubits', full_name='cirq.api.google.v1.MeasurementKey.qubits', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='invert_mask', full_name='cirq.api.google.v1.MeasurementKey.invert_mask', index=2,
      number=3, type=8, cpp_type=7, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=433,
  serialized_end=526,
)


_SWEEPRESULT = _descriptor.Descriptor(
  name='SweepResult',
  full_name='cirq.api.google.v1.SweepResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='repetitions', full_name='cirq.api.google.v1.SweepResult.repetitions', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='measurement_keys', full_name='cirq.api.google.v1.SweepResult.measurement_keys', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='parameterized_results', full_name='cirq.api.google.v1.SweepResult.parameterized_results', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=529,
  serialized_end=697,
)


_RESULT = _descriptor.Descriptor(
  name='Result',
  full_name='cirq.api.google.v1.Result',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sweep_results', full_name='cirq.api.google.v1.Result.sweep_results', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=699,
  serialized_end=763,
)

_PROGRAM.fields_by_name['operations'].message_type = cirq_dot_api_dot_google_dot_v1_dot_operations__pb2._OPERATION
_PROGRAM.fields_by_name['parameter_sweeps'].message_type = cirq_dot_api_dot_google_dot_v1_dot_params__pb2._PARAMETERSWEEP
_RUNCONTEXT.fields_by_name['parameter_sweeps'].message_type = cirq_dot_api_dot_google_dot_v1_dot_params__pb2._PARAMETERSWEEP
_PARAMETERIZEDRESULT.fields_by_name['params'].message_type = cirq_dot_api_dot_google_dot_v1_dot_params__pb2._PARAMETERDICT
_MEASUREMENTKEY.fields_by_name['qubits'].message_type = cirq_dot_api_dot_google_dot_v1_dot_operations__pb2._QUBIT
_SWEEPRESULT.fields_by_name['measurement_keys'].message_type = _MEASUREMENTKEY
_SWEEPRESULT.fields_by_name['parameterized_results'].message_type = _PARAMETERIZEDRESULT
_RESULT.fields_by_name['sweep_results'].message_type = _SWEEPRESULT
DESCRIPTOR.message_types_by_name['Program'] = _PROGRAM
DESCRIPTOR.message_types_by_name['RunContext'] = _RUNCONTEXT
DESCRIPTOR.message_types_by_name['ParameterizedResult'] = _PARAMETERIZEDRESULT
DESCRIPTOR.message_types_by_name['MeasurementKey'] = _MEASUREMENTKEY
DESCRIPTOR.message_types_by_name['SweepResult'] = _SWEEPRESULT
DESCRIPTOR.message_types_by_name['Result'] = _RESULT

Program = _reflection.GeneratedProtocolMessageType('Program', (_message.Message,), dict(
  DESCRIPTOR = _PROGRAM,
  __module__ = 'cirq.api.google.v1.program_pb2'
  # @@protoc_insertion_point(class_scope:cirq.api.google.v1.Program)
  ))
_sym_db.RegisterMessage(Program)

RunContext = _reflection.GeneratedProtocolMessageType('RunContext', (_message.Message,), dict(
  DESCRIPTOR = _RUNCONTEXT,
  __module__ = 'cirq.api.google.v1.program_pb2'
  # @@protoc_insertion_point(class_scope:cirq.api.google.v1.RunContext)
  ))
_sym_db.RegisterMessage(RunContext)

ParameterizedResult = _reflection.GeneratedProtocolMessageType('ParameterizedResult', (_message.Message,), dict(
  DESCRIPTOR = _PARAMETERIZEDRESULT,
  __module__ = 'cirq.api.google.v1.program_pb2'
  # @@protoc_insertion_point(class_scope:cirq.api.google.v1.ParameterizedResult)
  ))
_sym_db.RegisterMessage(ParameterizedResult)

MeasurementKey = _reflection.GeneratedProtocolMessageType('MeasurementKey', (_message.Message,), dict(
  DESCRIPTOR = _MEASUREMENTKEY,
  __module__ = 'cirq.api.google.v1.program_pb2'
  # @@protoc_insertion_point(class_scope:cirq.api.google.v1.MeasurementKey)
  ))
_sym_db.RegisterMessage(MeasurementKey)

SweepResult = _reflection.GeneratedProtocolMessageType('SweepResult', (_message.Message,), dict(
  DESCRIPTOR = _SWEEPRESULT,
  __module__ = 'cirq.api.google.v1.program_pb2'
  # @@protoc_insertion_point(class_scope:cirq.api.google.v1.SweepResult)
  ))
_sym_db.RegisterMessage(SweepResult)

Result = _reflection.GeneratedProtocolMessageType('Result', (_message.Message,), dict(
  DESCRIPTOR = _RESULT,
  __module__ = 'cirq.api.google.v1.program_pb2'
  # @@protoc_insertion_point(class_scope:cirq.api.google.v1.Result)
  ))
_sym_db.RegisterMessage(Result)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n\035com.google.cirq.api.google.v1B\014ProgramProtoP\001'))
_PROGRAM.fields_by_name['parameter_sweeps'].has_options = True
_PROGRAM.fields_by_name['parameter_sweeps']._options = _descriptor._ParseOptions(descriptor_pb2.FieldOptions(), _b('\030\001'))
# @@protoc_insertion_point(module_scope)
