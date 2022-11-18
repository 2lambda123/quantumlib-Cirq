# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: cirq_google/api/v1/operations.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n#cirq_google/api/v1/operations.proto\x12\x12\x63irq.google.api.v1\"!\n\x05Qubit\x12\x0b\n\x03row\x18\x01 \x01(\x05\x12\x0b\n\x03\x63ol\x18\x02 \x01(\x05\"E\n\x12ParameterizedFloat\x12\r\n\x03raw\x18\x01 \x01(\x02H\x00\x12\x17\n\rparameter_key\x18\x02 \x01(\tH\x00\x42\x07\n\x05value\"\xae\x01\n\x04\x45xpW\x12)\n\x06target\x18\x01 \x01(\x0b\x32\x19.cirq.google.api.v1.Qubit\x12?\n\x0f\x61xis_half_turns\x18\x02 \x01(\x0b\x32&.cirq.google.api.v1.ParameterizedFloat\x12:\n\nhalf_turns\x18\x03 \x01(\x0b\x32&.cirq.google.api.v1.ParameterizedFloat\"m\n\x04\x45xpZ\x12)\n\x06target\x18\x01 \x01(\x0b\x32\x19.cirq.google.api.v1.Qubit\x12:\n\nhalf_turns\x18\x02 \x01(\x0b\x32&.cirq.google.api.v1.ParameterizedFloat\"\x9b\x01\n\x05\x45xp11\x12*\n\x07target1\x18\x01 \x01(\x0b\x32\x19.cirq.google.api.v1.Qubit\x12*\n\x07target2\x18\x02 \x01(\x0b\x32\x19.cirq.google.api.v1.Qubit\x12:\n\nhalf_turns\x18\x03 \x01(\x0b\x32&.cirq.google.api.v1.ParameterizedFloat\"[\n\x0bMeasurement\x12*\n\x07targets\x18\x01 \x03(\x0b\x32\x19.cirq.google.api.v1.Qubit\x12\x0b\n\x03key\x18\x02 \x01(\t\x12\x13\n\x0binvert_mask\x18\x03 \x03(\x08\"\xfa\x01\n\tOperation\x12%\n\x1dincremental_delay_picoseconds\x18\x01 \x01(\x04\x12)\n\x05\x65xp_w\x18\n \x01(\x0b\x32\x18.cirq.google.api.v1.ExpWH\x00\x12)\n\x05\x65xp_z\x18\x0b \x01(\x0b\x32\x18.cirq.google.api.v1.ExpZH\x00\x12+\n\x06\x65xp_11\x18\x0c \x01(\x0b\x32\x19.cirq.google.api.v1.Exp11H\x00\x12\x36\n\x0bmeasurement\x18\r \x01(\x0b\x32\x1f.cirq.google.api.v1.MeasurementH\x00\x42\x0b\n\toperationB2\n\x1d\x63om.google.cirq.google.api.v1B\x0fOperationsProtoP\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'cirq_google.api.v1.operations_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\035com.google.cirq.google.api.v1B\017OperationsProtoP\001'
  _QUBIT._serialized_start=59
  _QUBIT._serialized_end=92
  _PARAMETERIZEDFLOAT._serialized_start=94
  _PARAMETERIZEDFLOAT._serialized_end=163
  _EXPW._serialized_start=166
  _EXPW._serialized_end=340
  _EXPZ._serialized_start=342
  _EXPZ._serialized_end=451
  _EXP11._serialized_start=454
  _EXP11._serialized_end=609
  _MEASUREMENT._serialized_start=611
  _MEASUREMENT._serialized_end=702
  _OPERATION._serialized_start=705
  _OPERATION._serialized_end=955
# @@protoc_insertion_point(module_scope)
