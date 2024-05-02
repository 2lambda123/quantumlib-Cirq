# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: cirq_google/api/v2/run_context.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import program_pb2 as cirq__google_dot_api_dot_v2_dot_program__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n$cirq_google/api/v2/run_context.proto\x12\x12\x63irq.google.api.v2\x1a cirq_google/api/v2/program.proto\"\x98\x01\n\nRunContext\x12<\n\x10parameter_sweeps\x18\x01 \x03(\x0b\x32\".cirq.google.api.v2.ParameterSweep\x12L\n\x1a\x64\x65vice_parameters_override\x18\x02 \x01(\x0b\x32(.cirq.google.api.v2.DeviceParametersDiff\"O\n\x0eParameterSweep\x12\x13\n\x0brepetitions\x18\x01 \x01(\x05\x12(\n\x05sweep\x18\x02 \x01(\x0b\x32\x19.cirq.google.api.v2.Sweep\"\x86\x01\n\x05Sweep\x12;\n\x0esweep_function\x18\x01 \x01(\x0b\x32!.cirq.google.api.v2.SweepFunctionH\x00\x12\x37\n\x0csingle_sweep\x18\x02 \x01(\x0b\x32\x1f.cirq.google.api.v2.SingleSweepH\x00\x42\x07\n\x05sweep\"\xc6\x01\n\rSweepFunction\x12\x45\n\rfunction_type\x18\x01 \x01(\x0e\x32..cirq.google.api.v2.SweepFunction.FunctionType\x12)\n\x06sweeps\x18\x02 \x03(\x0b\x32\x19.cirq.google.api.v2.Sweep\"C\n\x0c\x46unctionType\x12\x1d\n\x19\x46UNCTION_TYPE_UNSPECIFIED\x10\x00\x12\x0b\n\x07PRODUCT\x10\x01\x12\x07\n\x03ZIP\x10\x02\"W\n\x0f\x44\x65viceParameter\x12\x0c\n\x04path\x18\x01 \x03(\t\x12\x10\n\x03idx\x18\x02 \x01(\x03H\x00\x88\x01\x01\x12\x12\n\x05units\x18\x03 \x01(\tH\x01\x88\x01\x01\x42\x06\n\x04_idxB\x08\n\x06_units\"\xf3\x02\n\x14\x44\x65viceParametersDiff\x12:\n\x04\x64irs\x18\x01 \x03(\x0b\x32,.cirq.google.api.v2.DeviceParametersDiff.Dir\x12:\n\x04keys\x18\x02 \x03(\x0b\x32,.cirq.google.api.v2.DeviceParametersDiff.Key\x12?\n\tdeletions\x18\x03 \x03(\x0b\x32,.cirq.google.api.v2.DeviceParametersDiff.Del\x12\x0c\n\x04strs\x18\x04 \x03(\t\x1a#\n\x03\x44ir\x12\x0e\n\x06parent\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\x05\x1aM\n\x03Key\x12\x0b\n\x03\x64ir\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\x05\x12+\n\x05value\x18\x03 \x01(\x0b\x32\x1c.cirq.google.api.v2.ArgValue\x1a \n\x03\x44\x65l\x12\x0b\n\x03\x64ir\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\x05\"\xc5\x01\n\x0bSingleSweep\x12\x15\n\rparameter_key\x18\x01 \x01(\t\x12,\n\x06points\x18\x02 \x01(\x0b\x32\x1a.cirq.google.api.v2.PointsH\x00\x12\x30\n\x08linspace\x18\x03 \x01(\x0b\x32\x1c.cirq.google.api.v2.LinspaceH\x00\x12\x36\n\tparameter\x18\x04 \x01(\x0b\x32#.cirq.google.api.v2.DeviceParameterB\x07\n\x05sweep\"\x18\n\x06Points\x12\x0e\n\x06points\x18\x01 \x03(\x02\"G\n\x08Linspace\x12\x13\n\x0b\x66irst_point\x18\x01 \x01(\x02\x12\x12\n\nlast_point\x18\x02 \x01(\x02\x12\x12\n\nnum_points\x18\x03 \x01(\x03\x42\x32\n\x1d\x63om.google.cirq.google.api.v2B\x0fRunContextProtoP\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'cirq_google.api.v2.run_context_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\035com.google.cirq.google.api.v2B\017RunContextProtoP\001'
  _globals['_RUNCONTEXT']._serialized_start=95
  _globals['_RUNCONTEXT']._serialized_end=247
  _globals['_PARAMETERSWEEP']._serialized_start=249
  _globals['_PARAMETERSWEEP']._serialized_end=328
  _globals['_SWEEP']._serialized_start=331
  _globals['_SWEEP']._serialized_end=465
  _globals['_SWEEPFUNCTION']._serialized_start=468
  _globals['_SWEEPFUNCTION']._serialized_end=666
  _globals['_SWEEPFUNCTION_FUNCTIONTYPE']._serialized_start=599
  _globals['_SWEEPFUNCTION_FUNCTIONTYPE']._serialized_end=666
  _globals['_DEVICEPARAMETER']._serialized_start=668
  _globals['_DEVICEPARAMETER']._serialized_end=755
  _globals['_DEVICEPARAMETERSDIFF']._serialized_start=758
  _globals['_DEVICEPARAMETERSDIFF']._serialized_end=1129
  _globals['_DEVICEPARAMETERSDIFF_DIR']._serialized_start=981
  _globals['_DEVICEPARAMETERSDIFF_DIR']._serialized_end=1016
  _globals['_DEVICEPARAMETERSDIFF_KEY']._serialized_start=1018
  _globals['_DEVICEPARAMETERSDIFF_KEY']._serialized_end=1095
  _globals['_DEVICEPARAMETERSDIFF_DEL']._serialized_start=1097
  _globals['_DEVICEPARAMETERSDIFF_DEL']._serialized_end=1129
  _globals['_SINGLESWEEP']._serialized_start=1132
  _globals['_SINGLESWEEP']._serialized_end=1329
  _globals['_POINTS']._serialized_start=1331
  _globals['_POINTS']._serialized_end=1355
  _globals['_LINSPACE']._serialized_start=1357
  _globals['_LINSPACE']._serialized_end=1428
# @@protoc_insertion_point(module_scope)
