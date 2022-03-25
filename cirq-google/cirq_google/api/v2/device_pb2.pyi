# @generated by generate_proto_mypy_stubs.py.  Do not edit!
import sys
from google.protobuf.descriptor import (
    EnumDescriptor as google___protobuf___descriptor___EnumDescriptor,
)

from google.protobuf.internal.containers import (
    RepeatedCompositeFieldContainer as google___protobuf___internal___containers___RepeatedCompositeFieldContainer,
    RepeatedScalarFieldContainer as google___protobuf___internal___containers___RepeatedScalarFieldContainer,
)

from google.protobuf.message import (
    Message as google___protobuf___message___Message,
)

from typing import (
    Iterable as typing___Iterable,
    List as typing___List,
    Optional as typing___Optional,
    Text as typing___Text,
    Tuple as typing___Tuple,
    cast as typing___cast,
)

from typing_extensions import (
    Literal as typing_extensions___Literal,
)


class DeviceSpecification(google___protobuf___message___Message):
    valid_qubits = ... # type: google___protobuf___internal___containers___RepeatedScalarFieldContainer[typing___Text]
    developer_recommendations = ... # type: typing___Text

    @property
    def valid_gate_sets(self) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[GateSet]: ...

    @property
    def valid_gates(self) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[GateSpecification]: ...

    @property
    def valid_targets(self) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[TargetSet]: ...

    def __init__(self,
        valid_gate_sets : typing___Optional[typing___Iterable[GateSet]] = None,
        valid_gates : typing___Optional[typing___Iterable[GateSpecification]] = None,
        valid_qubits : typing___Optional[typing___Iterable[typing___Text]] = None,
        valid_targets : typing___Optional[typing___Iterable[TargetSet]] = None,
        developer_recommendations : typing___Optional[typing___Text] = None,
        ) -> None: ...
    @classmethod
    def FromString(cls, s: bytes) -> DeviceSpecification: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    if sys.version_info >= (3,):
        def ClearField(self, field_name: typing_extensions___Literal[u"developer_recommendations",u"valid_gate_sets",u"valid_gates",u"valid_qubits",u"valid_targets"]) -> None: ...
    else:
        def ClearField(self, field_name: typing_extensions___Literal[b"developer_recommendations",b"valid_gate_sets",b"valid_gates",b"valid_qubits",b"valid_targets"]) -> None: ...

class GateSpecification(google___protobuf___message___Message):
    class Sycamore(google___protobuf___message___Message):

        def __init__(self,
            ) -> None: ...
        @classmethod
        def FromString(cls, s: bytes) -> GateSpecification.Sycamore: ...
        def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
        def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...

    class SqrtISwap(google___protobuf___message___Message):

        def __init__(self,
            ) -> None: ...
        @classmethod
        def FromString(cls, s: bytes) -> GateSpecification.SqrtISwap: ...
        def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
        def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...

    class SqrtISwapInv(google___protobuf___message___Message):

        def __init__(self,
            ) -> None: ...
        @classmethod
        def FromString(cls, s: bytes) -> GateSpecification.SqrtISwapInv: ...
        def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
        def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...

    class CZ(google___protobuf___message___Message):

        def __init__(self,
            ) -> None: ...
        @classmethod
        def FromString(cls, s: bytes) -> GateSpecification.CZ: ...
        def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
        def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...

    class PhasedXZ(google___protobuf___message___Message):

        def __init__(self,
            ) -> None: ...
        @classmethod
        def FromString(cls, s: bytes) -> GateSpecification.PhasedXZ: ...
        def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
        def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...

    class VirtualZPow(google___protobuf___message___Message):

        def __init__(self,
            ) -> None: ...
        @classmethod
        def FromString(cls, s: bytes) -> GateSpecification.VirtualZPow: ...
        def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
        def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...

    class PhysicalZPow(google___protobuf___message___Message):

        def __init__(self,
            ) -> None: ...
        @classmethod
        def FromString(cls, s: bytes) -> GateSpecification.PhysicalZPow: ...
        def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
        def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...

    class CouplerPulse(google___protobuf___message___Message):

        def __init__(self,
            ) -> None: ...
        @classmethod
        def FromString(cls, s: bytes) -> GateSpecification.CouplerPulse: ...
        def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
        def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...

    class Measurement(google___protobuf___message___Message):

        def __init__(self,
            ) -> None: ...
        @classmethod
        def FromString(cls, s: bytes) -> GateSpecification.Measurement: ...
        def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
        def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...

    class Wait(google___protobuf___message___Message):

        def __init__(self,
            ) -> None: ...
        @classmethod
        def FromString(cls, s: bytes) -> GateSpecification.Wait: ...
        def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
        def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...

    gate_duration_picos = ... # type: int
    valid_targets = ... # type: google___protobuf___internal___containers___RepeatedScalarFieldContainer[typing___Text]

    @property
    def syc(self) -> GateSpecification.Sycamore: ...

    @property
    def sqrt_iswap(self) -> GateSpecification.SqrtISwap: ...

    @property
    def sqrt_iswap_inv(self) -> GateSpecification.SqrtISwapInv: ...

    @property
    def cz(self) -> GateSpecification.CZ: ...

    @property
    def phased_xz(self) -> GateSpecification.PhasedXZ: ...

    @property
    def virtual_zpow(self) -> GateSpecification.VirtualZPow: ...

    @property
    def physical_zpow(self) -> GateSpecification.PhysicalZPow: ...

    @property
    def coupler_pulse(self) -> GateSpecification.CouplerPulse: ...

    @property
    def meas(self) -> GateSpecification.Measurement: ...

    @property
    def wait(self) -> GateSpecification.Wait: ...

    def __init__(self,
        gate_duration_picos : typing___Optional[int] = None,
        valid_targets : typing___Optional[typing___Iterable[typing___Text]] = None,
        syc : typing___Optional[GateSpecification.Sycamore] = None,
        sqrt_iswap : typing___Optional[GateSpecification.SqrtISwap] = None,
        sqrt_iswap_inv : typing___Optional[GateSpecification.SqrtISwapInv] = None,
        cz : typing___Optional[GateSpecification.CZ] = None,
        phased_xz : typing___Optional[GateSpecification.PhasedXZ] = None,
        virtual_zpow : typing___Optional[GateSpecification.VirtualZPow] = None,
        physical_zpow : typing___Optional[GateSpecification.PhysicalZPow] = None,
        coupler_pulse : typing___Optional[GateSpecification.CouplerPulse] = None,
        meas : typing___Optional[GateSpecification.Measurement] = None,
        wait : typing___Optional[GateSpecification.Wait] = None,
        ) -> None: ...
    @classmethod
    def FromString(cls, s: bytes) -> GateSpecification: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    if sys.version_info >= (3,):
        def HasField(self, field_name: typing_extensions___Literal[u"coupler_pulse",u"cz",u"gate",u"meas",u"phased_xz",u"physical_zpow",u"sqrt_iswap",u"sqrt_iswap_inv",u"syc",u"virtual_zpow",u"wait"]) -> bool: ...
        def ClearField(self, field_name: typing_extensions___Literal[u"coupler_pulse",u"cz",u"gate",u"gate_duration_picos",u"meas",u"phased_xz",u"physical_zpow",u"sqrt_iswap",u"sqrt_iswap_inv",u"syc",u"valid_targets",u"virtual_zpow",u"wait"]) -> None: ...
    else:
        def HasField(self, field_name: typing_extensions___Literal[u"coupler_pulse",b"coupler_pulse",u"cz",b"cz",u"gate",b"gate",u"meas",b"meas",u"phased_xz",b"phased_xz",u"physical_zpow",b"physical_zpow",u"sqrt_iswap",b"sqrt_iswap",u"sqrt_iswap_inv",b"sqrt_iswap_inv",u"syc",b"syc",u"virtual_zpow",b"virtual_zpow",u"wait",b"wait"]) -> bool: ...
        def ClearField(self, field_name: typing_extensions___Literal[b"coupler_pulse",b"cz",b"gate",b"gate_duration_picos",b"meas",b"phased_xz",b"physical_zpow",b"sqrt_iswap",b"sqrt_iswap_inv",b"syc",b"valid_targets",b"virtual_zpow",b"wait"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions___Literal[u"gate",b"gate"]) -> typing_extensions___Literal["syc","sqrt_iswap","sqrt_iswap_inv","cz","phased_xz","virtual_zpow","physical_zpow","coupler_pulse","meas","wait"]: ...

class GateSet(google___protobuf___message___Message):
    name = ... # type: typing___Text

    @property
    def valid_gates(self) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[GateDefinition]: ...

    def __init__(self,
        name : typing___Optional[typing___Text] = None,
        valid_gates : typing___Optional[typing___Iterable[GateDefinition]] = None,
        ) -> None: ...
    @classmethod
    def FromString(cls, s: bytes) -> GateSet: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    if sys.version_info >= (3,):
        def ClearField(self, field_name: typing_extensions___Literal[u"name",u"valid_gates"]) -> None: ...
    else:
        def ClearField(self, field_name: typing_extensions___Literal[b"name",b"valid_gates"]) -> None: ...

class GateDefinition(google___protobuf___message___Message):
    id = ... # type: typing___Text
    number_of_qubits = ... # type: int
    gate_duration_picos = ... # type: int
    valid_targets = ... # type: google___protobuf___internal___containers___RepeatedScalarFieldContainer[typing___Text]

    @property
    def valid_args(self) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[ArgDefinition]: ...

    def __init__(self,
        id : typing___Optional[typing___Text] = None,
        number_of_qubits : typing___Optional[int] = None,
        valid_args : typing___Optional[typing___Iterable[ArgDefinition]] = None,
        gate_duration_picos : typing___Optional[int] = None,
        valid_targets : typing___Optional[typing___Iterable[typing___Text]] = None,
        ) -> None: ...
    @classmethod
    def FromString(cls, s: bytes) -> GateDefinition: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    if sys.version_info >= (3,):
        def ClearField(self, field_name: typing_extensions___Literal[u"gate_duration_picos",u"id",u"number_of_qubits",u"valid_args",u"valid_targets"]) -> None: ...
    else:
        def ClearField(self, field_name: typing_extensions___Literal[b"gate_duration_picos",b"id",b"number_of_qubits",b"valid_args",b"valid_targets"]) -> None: ...

class ArgDefinition(google___protobuf___message___Message):
    class ArgType(int):
        DESCRIPTOR: google___protobuf___descriptor___EnumDescriptor = ...
        @classmethod
        def Name(cls, number: int) -> str: ...
        @classmethod
        def Value(cls, name: str) -> ArgDefinition.ArgType: ...
        @classmethod
        def keys(cls) -> typing___List[str]: ...
        @classmethod
        def values(cls) -> typing___List[ArgDefinition.ArgType]: ...
        @classmethod
        def items(cls) -> typing___List[typing___Tuple[str, ArgDefinition.ArgType]]: ...
    UNSPECIFIED = typing___cast(ArgType, 0)
    FLOAT = typing___cast(ArgType, 1)
    REPEATED_BOOLEAN = typing___cast(ArgType, 2)
    STRING = typing___cast(ArgType, 3)

    name = ... # type: typing___Text
    type = ... # type: ArgDefinition.ArgType

    @property
    def allowed_ranges(self) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[ArgumentRange]: ...

    def __init__(self,
        name : typing___Optional[typing___Text] = None,
        type : typing___Optional[ArgDefinition.ArgType] = None,
        allowed_ranges : typing___Optional[typing___Iterable[ArgumentRange]] = None,
        ) -> None: ...
    @classmethod
    def FromString(cls, s: bytes) -> ArgDefinition: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    if sys.version_info >= (3,):
        def ClearField(self, field_name: typing_extensions___Literal[u"allowed_ranges",u"name",u"type"]) -> None: ...
    else:
        def ClearField(self, field_name: typing_extensions___Literal[b"allowed_ranges",b"name",b"type"]) -> None: ...

class ArgumentRange(google___protobuf___message___Message):
    minimum_value = ... # type: float
    maximum_value = ... # type: float

    def __init__(self,
        minimum_value : typing___Optional[float] = None,
        maximum_value : typing___Optional[float] = None,
        ) -> None: ...
    @classmethod
    def FromString(cls, s: bytes) -> ArgumentRange: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    if sys.version_info >= (3,):
        def ClearField(self, field_name: typing_extensions___Literal[u"maximum_value",u"minimum_value"]) -> None: ...
    else:
        def ClearField(self, field_name: typing_extensions___Literal[b"maximum_value",b"minimum_value"]) -> None: ...

class TargetSet(google___protobuf___message___Message):
    class TargetOrdering(int):
        DESCRIPTOR: google___protobuf___descriptor___EnumDescriptor = ...
        @classmethod
        def Name(cls, number: int) -> str: ...
        @classmethod
        def Value(cls, name: str) -> TargetSet.TargetOrdering: ...
        @classmethod
        def keys(cls) -> typing___List[str]: ...
        @classmethod
        def values(cls) -> typing___List[TargetSet.TargetOrdering]: ...
        @classmethod
        def items(cls) -> typing___List[typing___Tuple[str, TargetSet.TargetOrdering]]: ...
    UNSPECIFIED = typing___cast(TargetOrdering, 0)
    SYMMETRIC = typing___cast(TargetOrdering, 1)
    ASYMMETRIC = typing___cast(TargetOrdering, 2)
    SUBSET_PERMUTATION = typing___cast(TargetOrdering, 3)

    name = ... # type: typing___Text
    target_ordering = ... # type: TargetSet.TargetOrdering

    @property
    def targets(self) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[Target]: ...

    def __init__(self,
        name : typing___Optional[typing___Text] = None,
        target_ordering : typing___Optional[TargetSet.TargetOrdering] = None,
        targets : typing___Optional[typing___Iterable[Target]] = None,
        ) -> None: ...
    @classmethod
    def FromString(cls, s: bytes) -> TargetSet: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    if sys.version_info >= (3,):
        def ClearField(self, field_name: typing_extensions___Literal[u"name",u"target_ordering",u"targets"]) -> None: ...
    else:
        def ClearField(self, field_name: typing_extensions___Literal[b"name",b"target_ordering",b"targets"]) -> None: ...

class Target(google___protobuf___message___Message):
    ids = ... # type: google___protobuf___internal___containers___RepeatedScalarFieldContainer[typing___Text]

    def __init__(self,
        ids : typing___Optional[typing___Iterable[typing___Text]] = None,
        ) -> None: ...
    @classmethod
    def FromString(cls, s: bytes) -> Target: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    if sys.version_info >= (3,):
        def ClearField(self, field_name: typing_extensions___Literal[u"ids"]) -> None: ...
    else:
        def ClearField(self, field_name: typing_extensions___Literal[b"ids"]) -> None: ...
