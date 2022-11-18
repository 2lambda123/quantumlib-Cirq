"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import cirq_google.api.v2.program_pb2
import cirq_google.api.v2.result_pb2
import cirq_google.api.v2.run_context_pb2
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.message
import sys

if sys.version_info >= (3, 8):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing_extensions.final
class BatchProgram(google.protobuf.message.Message):
    """A Batch of multiple circuits that should be run together
    as one QuantumProgram within Quantum Engine.

    Note: Batching is done on a best-effort basis.
    Circuits will be be bundled together, but the size
    of the total batch and different hardware constraints may
    cause the programs to be executed seperately on the hardware.
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    PROGRAMS_FIELD_NUMBER: builtins.int
    @property
    def programs(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[cirq_google.api.v2.program_pb2.Program]:
        """The circuits that should be bundled together as one program"""
    def __init__(
        self,
        *,
        programs: collections.abc.Iterable[cirq_google.api.v2.program_pb2.Program] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["programs", b"programs"]) -> None: ...

global___BatchProgram = BatchProgram

@typing_extensions.final
class BatchRunContext(google.protobuf.message.Message):
    """A batch of contexts for running a bundled batch of programs
    To be used in conjunction with BatchProgram
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    RUN_CONTEXTS_FIELD_NUMBER: builtins.int
    @property
    def run_contexts(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[cirq_google.api.v2.run_context_pb2.RunContext]:
        """Run contexts for each program in the BatchProgram
        Each RunContext should map directly to a Program in the corresponding
        BatchProgram.

        This message must have one RunContext for each Program in the
        BatchProgram, and the order of the RunContext messages should
        match the order of the Programs in the BatchProgram.
        """
    def __init__(
        self,
        *,
        run_contexts: collections.abc.Iterable[cirq_google.api.v2.run_context_pb2.RunContext] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["run_contexts", b"run_contexts"]) -> None: ...

global___BatchRunContext = BatchRunContext

@typing_extensions.final
class BatchResult(google.protobuf.message.Message):
    """The result returned from running a BatchProgram/BatchRunContext"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    RESULTS_FIELD_NUMBER: builtins.int
    @property
    def results(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[cirq_google.api.v2.result_pb2.Result]:
        """Results returned from executing a BatchProgram/BatchRunContext pair.

        After a BatchProgram and BatchRunContext is successfully run in
        Quantum Engine, the expected result if successful will be a BatchResult.

        Each Result in this message will directly correspond to a Program/
        RunContext pair in the request.  There will be one Result in this message
        for each corresponding pair in the request and the order of the Results
        will match the order of the Programs from the request.

        In case of partial results, an empty (default) Result object will be
        populated for programs that were not able to be run correctly.
        """
    def __init__(
        self,
        *,
        results: collections.abc.Iterable[cirq_google.api.v2.result_pb2.Result] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["results", b"results"]) -> None: ...

global___BatchResult = BatchResult
