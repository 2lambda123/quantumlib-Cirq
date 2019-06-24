from typing import (Dict, Iterable, Iterator, List, Optional, Set, Tuple, Union,
                    cast)

import numpy as np

from cirq.api.google.v2 import result_pb2
from cirq import circuits
from cirq import devices
from cirq import ops
from cirq import schedules
from cirq import study


class Measurement:
    """Info about a single measurement within a circuit or schedule."""

    def __init__(self, key: str, qubits: List[devices.GridQubit], slot: int):
        self.key = key
        self.qubits = qubits
        self.slot = slot


def find_measurements(program: Union[circuits.Circuit, schedules.Schedule],
                     ) -> List[Measurement]:
    """Find measurements in the given program (circuit or schedule).

    Returns:
        List of Measurement objects with named measurements in this program.
    """
    measurements: List[Measurement] = []
    keys: Set[str] = set()

    if isinstance(program, circuits.Circuit):
        measure_iter = _circuit_measurements(program)
    else:
        measure_iter = _schedule_measurements(program)

    for m in measure_iter:
        if m.key in keys:
            raise ValueError('Duplicate measurement key: {}'.format(m.key))
        keys.add(m.key)
        measurements.append(m)

    return measurements


def _circuit_measurements(circuit: circuits.Circuit) -> Iterator[Measurement]:
    for i, moment in enumerate(circuit):
        for op in moment:
            if (isinstance(op, ops.GateOperation) and
                    isinstance(op.gate, ops.MeasurementGate)):
                yield Measurement(key=op.gate.key,
                                  qubits=_grid_qubits(op),
                                  slot=i)


def _schedule_measurements(schedule: schedules.Schedule
                          ) -> Iterator[Measurement]:
    for so in schedule.scheduled_operations:
        op = so.operation
        if (isinstance(op, ops.GateOperation) and
                isinstance(op.gate, ops.MeasurementGate)):
            yield Measurement(key=op.gate.key,
                              qubits=_grid_qubits(op),
                              slot=so.time.raw_picos())


def _grid_qubits(op: ops.Operation) -> List[devices.GridQubit]:
    if not all(isinstance(q, devices.GridQubit) for q in op.qubits):
        raise ValueError('Expected GridQubits: {}'.format(op.qubits))
    return cast(List[devices.GridQubit], list(op.qubits))


def pack_bits(bits: np.ndarray) -> bytes:
    """Pack bits given as a numpy array of bools into bytes."""
    # Pad length to multiple of 8 if needed.
    remainder = len(bits) % 8
    if remainder:
        bits = np.pad(bits, (0, 8 - remainder), 'constant')

    # Pack in little-endian bit order.
    bits = bits.reshape((-1, 8))[:, ::-1]
    byte_arr = np.packbits(bits, axis=1).reshape(-1)

    return byte_arr.tobytes()


def unpack_bits(data: bytes, repetitions: int) -> np.ndarray:
    """Unpack bits from a byte array into numpy array of bools."""
    byte_arr = np.frombuffer(data, dtype='uint8').reshape((len(data), 1))
    bits = np.unpackbits(byte_arr, axis=1)[:, ::-1].reshape(-1).astype(bool)
    return bits[:repetitions]


def results_to_proto(
        trial_sweeps: Iterable[Iterable[study.TrialResult]],
        measurements: List[Measurement],
        msg: Optional[result_pb2.Result] = None,
) -> result_pb2.Result:
    """Converts trial results from multiple sweeps to v2 protobuf message.

    Args:
        trial_sweeps: Iterable over sweeps and then over trial results within
            each sweep.
        measurements: List of info about measurements in the program.
        msg: Optional message to populate. If not given, create a new message.
    """
    if msg is None:
        msg = result_pb2.Result()
    for trial_sweep in trial_sweeps:
        sweep_result = msg.sweep_results.add()
        for i, trial_result in enumerate(trial_sweep):
            if i == 0:
                sweep_result.repetitions = trial_result.repetitions
            elif trial_result.repetitions != sweep_result.repetitions:
                raise ValueError(
                    'different numbers of repetitions in one sweep')
            pr = sweep_result.parameterized_results.add()
            pr.params.assignments.update(trial_result.params.param_dict)
            for m in measurements:
                mr = pr.measurement_results.add()
                mr.key = m.key
                m_data = trial_result.measurements[m.key]
                for i, qubit in enumerate(m.qubits):
                    qmr = mr.qubit_measurement_results.add()
                    qmr.qubit.id = qubit.proto_id()
                    qmr.results = pack_bits(m_data[:, i])
    return msg


def results_from_proto(
        msg: result_pb2.Result,
        measurements: List[Measurement],
) -> List[List[study.TrialResult]]:
    """Converts a v2 result proto into List of list of trial results.

    Args:
        msg: v2 Result message to convert.
        measurements: List of info about expected measurements in the program.

    Returns:
        A list containing a list of trial results for each sweep.
    """
    measure_map = {m.key: m for m in measurements}
    return [
        _trial_sweep_from_proto(sweep_result, measure_map)
        for sweep_result in msg.sweep_results
    ]


def _trial_sweep_from_proto(
        msg: result_pb2.SweepResult,
        measurements: Dict[str, Measurement],
) -> List[study.TrialResult]:
    trial_sweep: List[study.TrialResult] = []
    for pr in msg.parameterized_results:
        m_data: Dict[str, np.ndarray] = {}
        for mr in pr.measurement_results:
            m = measurements[mr.key]
            qubit_results: Dict[devices.GridQubit, np.ndarray] = {}
            for qmr in mr.qubit_measurement_results:
                qubit = devices.GridQubit.from_proto_id(qmr.qubit.id)
                if qubit in qubit_results:
                    raise ValueError('qubit already exists: {}'.format(qubit))
                qubit_results[qubit] = unpack_bits(qmr.results, msg.repetitions)
            ordered_results = [qubit_results[qubit] for qubit in m.qubits]
            m_data[mr.key] = np.array(ordered_results).transpose()
        trial_sweep.append(
            study.TrialResult(
                params=study.ParamResolver(dict(pr.params.assignments)),
                measurements=m_data,
                repetitions=msg.repetitions,
            ))
    return trial_sweep
