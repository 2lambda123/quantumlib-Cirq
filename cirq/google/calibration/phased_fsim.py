from typing import Callable, Dict, List, Optional, Tuple, Union, TYPE_CHECKING

import abc
import collections
from cirq.circuits import Circuit
from cirq.ops import Gate, Moment, Qid
import cirq.google.api.v2 as v2
from cirq.google.engine import CalibrationLayer, CalibrationResult, Engine
from cirq.google.serializable_gate_set import SerializableGateSet
import re

if TYPE_CHECKING:
    # Workaround for mypy custom dataclasses
    from dataclasses import dataclass as json_serializable_dataclass
else:
    from cirq.protocols import json_serializable_dataclass


@json_serializable_dataclass(frozen=True)
class PhasedFSimParameters:
    theta: Optional[float] = None
    zeta: Optional[float] = None
    chi: Optional[float] = None
    gamma: Optional[float] = None
    phi: Optional[float] = None


@json_serializable_dataclass
class FloquetPhasedFSimCalibrationOptions:
    estimate_theta: bool
    estimate_zeta: bool
    estimate_chi: bool
    estimate_gamma: bool
    estimate_phi: bool


@json_serializable_dataclass
class PhasedFSimCalibrationResult(abc.ABC):
    parameters: Dict[Tuple[Qid, Qid], PhasedFSimParameters]
    gate: Gate
    gate_set: SerializableGateSet


@json_serializable_dataclass
class PhasedFSimCalibrationRequest(abc.ABC):
    gate: Gate  # Any gate which can be described by cirq.PhasedFSim
    gate_set: SerializableGateSet
    pairs: Tuple[Tuple[Qid, Qid]]

    @abc.abstractmethod
    def to_calibration_layer(self, handler_name: str) -> CalibrationLayer:
        pass

    @abc.abstractmethod
    def parse_result(self, result: CalibrationResult) -> PhasedFSimCalibrationResult:
        pass


@json_serializable_dataclass
class FloquetPhasedFSimCalibrationResult(PhasedFSimCalibrationResult):
    options: FloquetPhasedFSimCalibrationOptions


@json_serializable_dataclass
class FloquetPhasedFSimCalibrationRequest(PhasedFSimCalibrationRequest):
    options: FloquetPhasedFSimCalibrationOptions

    def to_calibration_layer(self, handler_name: str) -> CalibrationLayer:
        circuit = Circuit([self.gate.on(*pair) for pair in self.pairs])
        return CalibrationLayer(
            calibration_type='floquet_phased_fsim_characterization',
            program=circuit,
            args={
                'est_theta': self.options.estimate_theta,
                'est_zeta': self.options.estimate_zeta,
                'est_chi': self.options.estimate_chi,
                'est_gamma': self.options.estimate_gamma,
                'est_phi': self.options.estimate_phi,
                'readout_corrections': True
            }
        )

    def parse_result(self, result: CalibrationResult) -> PhasedFSimCalibrationResult:
        decoded = collections.defaultdict(lambda: {})
        for keys, values in result.metrics['angles']:
            for key, value in zip(keys, values):
                match = re.match(r'(\d+)_(.+)', key)
                if not match:
                    raise ValueError(f'Unknown metric name {key}')
                index = int(match[1])
                name = match[2]
                decoded[index][name] = value

        parsed = {}
        for data in decoded.values():
            a = v2.qubit_from_proto_id(data['0'])
            b = v2.qubit_from_proto_id(data['1'])
            parsed[(a, b)] = PhasedFSimParameters(
                theta=data.get('theta_est', None),
                zeta=data.get('zeta_est', None),
                chi=data.get('chi_est', None),
                gamma=data.get('gamma_est', None),
                phi=data.get('phi_est', None)
            )

        return FloquetPhasedFSimCalibrationResult(
            parameters=parsed,
            gate=self.gate,
            gate_set=self.gate_set,
            options=self.options
        )


def run_calibrations(calibrations: List[PhasedFSimCalibrationRequest],
                     engine: Engine,
                     processor_id: str,
                     handler_name: str
                     ) -> List[PhasedFSimCalibrationResult]:
    if not calibrations:
        return []

    gate_sets = [calibration.gate_set for calibration in calibrations]
    gate_set = gate_sets[0]
    if not all(gate_set == other for other in gate_sets):
        raise ValueError('All calibrations that run together must be defined for a shared gate set')

    requests = [calibration.to_calibration_layer(handler_name) for calibration in calibrations]
    job = engine.run_calibration(requests,
                                 processor_id=processor_id,
                                 gate_set=gate_set)
    return [calibration.parse_result(result)
            for calibration, result in zip(calibrations, job.calibration_results())]


def default_fsim_floquet_options(
        gate: Gate) -> Optional[FloquetPhasedFSimCalibrationOptions]:
    return NotImplemented


def floquet_calibration_for_moment(
        moment: Moment,
        options_generator: Callable[
            [Gate], Optional[FloquetPhasedFSimCalibrationOptions]
        ] = default_fsim_floquet_options
) -> FloquetPhasedFSimCalibrationRequest:
    return NotImplemented


def floquet_calibration_for_circuit(
        circuit: Circuit,
        options_generator: Callable[
            [Gate], Optional[FloquetPhasedFSimCalibrationOptions]
        ] = default_fsim_floquet_options,
        merge_sub_sets: bool = True
) -> Tuple[List[FloquetPhasedFSimCalibrationRequest], List[Optional[int]]]:
    """
    Returns:
        Tuple of:
          - list of calibration requests,
          - list of indices of the generated calibration requests for each
            moment in the supplied circuit. If None occurs at certain position,
            it means that the related moment was not recognized for calibration.
    """
    return NotImplemented


def run_floquet_calibration_for_circuit(
        engine: Engine,
        circuit: Circuit,
        options_generator: Callable[
            [Gate], Optional[FloquetPhasedFSimCalibrationOptions]
        ] = default_fsim_floquet_options,
        merge_sub_sets: bool = True
) -> List[FloquetPhasedFSimCalibrationResult]:
    return NotImplemented
