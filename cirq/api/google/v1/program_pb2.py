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
  serialized_pb=_b('\n cirq/api/google/v1/program.proto\x12\x12\x63irq.api.google.v1\x1a#cirq/api/google/v1/operations.proto\x1a\x1f\x63irq/api/google/v1/params.proto\"y\n\x07Program\x12\x31\n\noperations\x18\x01 \x03(\x0b\x32\x1d.cirq.api.google.v1.Operation\x12;\n\x0fparameter_sweep\x18\x02 \x03(\x0b\x32\".cirq.api.google.v1.ParameterSweep\"e\n\x13ParameterizedResult\x12\x31\n\x06params\x18\x01 \x01(\x0b\x32!.cirq.api.google.v1.ParameterDict\x12\x1b\n\x13measurement_results\x18\x02 \x01(\x0c\"+\n\x0eMeasurementKey\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x0c\n\x04size\x18\x02 \x01(\x05\"\xa7\x01\n\x06Result\x12<\n\x10measurement_keys\x18\x01 \x03(\x0b\x32\".cirq.api.google.v1.MeasurementKey\x12\x17\n\x0fnum_repetitions\x18\x02 \x01(\x05\x12\x46\n\x15parameterized_results\x18\x03 \x03(\x0b\x32\'.cirq.api.google.v1.ParameterizedResultB/\n\x1d\x63om.google.cirq.api.google.v1B\x0cProgramProtoP\x01\x62\x06proto3')
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
      name='parameter_sweep', full_name='cirq.api.google.v1.Program.parameter_sweep', index=1,
      number=2, type=11, cpp_type=10, label=3,
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
  serialized_start=126,
  serialized_end=247,
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
  serialized_start=249,
  serialized_end=350,
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
      name='size', full_name='cirq.api.google.v1.MeasurementKey.size', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
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
  serialized_start=352,
  serialized_end=395,
)


_RESULT = _descriptor.Descriptor(
  name='Result',
  full_name='cirq.api.google.v1.Result',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='measurement_keys', full_name='cirq.api.google.v1.Result.measurement_keys', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='num_repetitions', full_name='cirq.api.google.v1.Result.num_repetitions', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='parameterized_results', full_name='cirq.api.google.v1.Result.parameterized_results', index=2,
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
  serialized_start=398,
  serialized_end=565,
)

_PROGRAM.fields_by_name['operations'].message_type = cirq_dot_api_dot_google_dot_v1_dot_operations__pb2._OPERATION
_PROGRAM.fields_by_name['parameter_sweep'].message_type = cirq_dot_api_dot_google_dot_v1_dot_params__pb2._PARAMETERSWEEP
_PARAMETERIZEDRESULT.fields_by_name['params'].message_type = cirq_dot_api_dot_google_dot_v1_dot_params__pb2._PARAMETERDICT
_RESULT.fields_by_name['measurement_keys'].message_type = _MEASUREMENTKEY
_RESULT.fields_by_name['parameterized_results'].message_type = _PARAMETERIZEDRESULT
DESCRIPTOR.message_types_by_name['Program'] = _PROGRAM
DESCRIPTOR.message_types_by_name['ParameterizedResult'] = _PARAMETERIZEDRESULT
DESCRIPTOR.message_types_by_name['MeasurementKey'] = _MEASUREMENTKEY
DESCRIPTOR.message_types_by_name['Result'] = _RESULT

Program = _reflection.GeneratedProtocolMessageType('Program', (_message.Message,), dict(
  DESCRIPTOR = _PROGRAM,
  __module__ = 'cirq.api.google.v1.program_pb2'
  # @@protoc_insertion_point(class_scope:cirq.api.google.v1.Program)
  ))
_sym_db.RegisterMessage(Program)

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

Result = _reflection.GeneratedProtocolMessageType('Result', (_message.Message,), dict(
  DESCRIPTOR = _RESULT,
  __module__ = 'cirq.api.google.v1.program_pb2'
  # @@protoc_insertion_point(class_scope:cirq.api.google.v1.Result)
  ))
_sym_db.RegisterMessage(Result)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n\035com.google.cirq.api.google.v1B\014ProgramProtoP\001'))
# @@protoc_insertion_point(module_scope)
