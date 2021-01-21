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
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

import abc
import collections
import dataclasses
import re

from cirq.circuits import Circuit
from cirq.ops import Gate, Qid
from cirq.google.api import v2
from cirq.google.engine import CalibrationLayer, CalibrationResult


_FLOQUET_PHASED_FSIM_HANDLER_NAME = 'floquet_phased_fsim_characterization'

if TYPE_CHECKING:
    # Workaround for mypy custom dataclasses (python/mypy#5406)
    from dataclasses import dataclass as json_serializable_dataclass
else:
    from cirq.protocols import json_serializable_dataclass


@json_serializable_dataclass(frozen=True)
class PhasedFSimCharacterization:
    """Holder for the unitary angles of the cirq.PhasedFSimGate.

    This class stores five unitary parameters (θ, ζ, χ, γ and φ) that describe the
    cirq.PhasedFSimGate which is the most general particle conserving two-qubit gate. The unitary
    of the underlying gate is:

        [[1,                        0,                       0,                0],
         [0,    exp(-i(γ + ζ)) cos(θ), -i exp(-i(γ - χ)) sin(θ),               0],
         [0, -i exp(-i(γ + χ)) sin(θ),    exp(-i(γ - ζ)) cos(θ),               0],
         [0,                        0,                       0,  exp(-i(2γ + φ))]]

    The parameters θ, γ and φ are symmetric and parameters ζ and χ asymmetric under the qubits
    exchange.

    All the angles described by this class are optional and can be left unknown. This is relevant
    for characterization routines that characterize only subset of the gate parameters. All the
    angles are assumed to take a fixed numerical values which reflect the current state of the
    characterized gate.

    This class supports JSON serialization and deserialization.

    Attributes:
        theta: θ angle in radians or None when unknown.
        zeta: ζ angle in radians or None when unknown.
        chi: χ angle in radians or None when unknown.
        gamma: γ angle in radians or None when unknown.
        phi: φ angle in radians or None when unknown.
    """

    theta: Optional[float] = None
    zeta: Optional[float] = None
    chi: Optional[float] = None
    gamma: Optional[float] = None
    phi: Optional[float] = None

    def asdict(self) -> Dict[str, float]:
        """Converts parameters to a dictionary that maps angle names to values."""
        return dataclasses.asdict(self)

    def all_none(self) -> bool:
        """Returns True if all the angles are None"""
        return (
            self.theta is None
            and self.zeta is None
            and self.chi is None
            and self.gamma is None
            and self.phi is None
        )

    def any_none(self) -> bool:
        """Returns True if any the angle is None"""
        return (
            self.theta is None
            or self.zeta is None
            or self.chi is None
            or self.gamma is None
            or self.phi is None
        )

    def parameters_for_qubits_swapped(self) -> 'PhasedFSimCharacterization':
        """Parameters for the gate with qubits swapped between each other.

        The angles theta, gamma and phi are kept unchanged. The angles zeta and chi are negated for
        the gate with swapped qubits.

        Returns:
            New instance with angles adjusted for swapped qubits.
        """
        return PhasedFSimCharacterization(
            theta=self.theta,
            zeta=-self.zeta if self.zeta is not None else None,
            chi=-self.chi if self.chi is not None else None,
            gamma=self.gamma,
            phi=self.phi,
        )

    def merge_with(self, other: 'PhasedFSimCharacterization') -> 'PhasedFSimCharacterization':
        """Substitutes missing parameter with values from other.

        Args:
            other: Parameters to use for None values.

        Returns:
            New instance of PhasedFSimCharacterization with values from this instance if they are
            set or values from other when some parameter is None.
        """
        return PhasedFSimCharacterization(
            theta=other.theta if self.theta is None else self.theta,
            zeta=other.zeta if self.zeta is None else self.zeta,
            chi=other.chi if self.chi is None else self.chi,
            gamma=other.gamma if self.gamma is None else self.gamma,
            phi=other.phi if self.phi is None else self.phi,
        )

    def override_by(self, other: 'PhasedFSimCharacterization') -> 'PhasedFSimCharacterization':
        """Overrides other parameters that are not None.

        Args:
            other: Parameters to use for override.

        Returns:
            New instance of PhasedFSimCharacterization with values from other if set (values from
            other that are not None). Otherwise the current values are used.
        """
        return other.merge_with(self)


@dataclasses.dataclass(frozen=True)
class PhasedFSimCalibrationResult:
    """The PhasedFSimGate characterization result.

    Attributes:
        parameters: Map from qubit pair to characterization result. For each pair of characterized
            quibts a and b either only (a, b) or only (b, a) is present.
        gate: Characterized gate for each qubit pair.
    """

    parameters: Dict[Tuple[Qid, Qid], PhasedFSimCharacterization]
    gate: Gate

    def get_parameters(self, a: Qid, b: Qid) -> Optional['PhasedFSimCharacterization']:
        """Returns parameters for a qubit pair (a, b) or None when unknown."""
        if (a, b) in self.parameters:
            return self.parameters[(a, b)]
        elif (b, a) in self.parameters:
            return self.parameters[(b, a)].parameters_for_qubits_swapped()
        else:
            return None

    @classmethod
    def _create_parameters_dict(
        cls,
        parameters: List[Tuple[Qid, Qid, PhasedFSimCharacterization]],
    ) -> Dict[Tuple[Qid, Qid], PhasedFSimCharacterization]:
        """Utility function to create parameters from JSON.

        Can be used from child classes to instantiate classes in a _from_json_dict_
        method."""
        return {(entry[0], entry[1]): entry[2] for entry in parameters}

    @classmethod
    def _from_json_dict_(
        cls,
        parameters: List[Tuple[Qid, Qid, PhasedFSimCharacterization]],
        gate: Gate,
        **kwargs,
    ) -> 'PhasedFSimCalibrationResult':
        """Magic method for the JSON serialization protocol.

        Converts serialized dictionary into a dict suitable for
        class instantiation."""
        return cls(cls._create_parameters_dict(parameters), gate)

    def _json_dict_(self) -> Dict[str, Any]:
        """Magic method for the JSON serialization protocol."""
        return {
            'cirq_type': 'PhasedFSimCalibrationResult',
            'gate': self.gate,
            'parameters': [(key[0], key[1], self.parameters[key]) for key in self.parameters],
        }


# We have to relax a mypy constraint, see https://github.com/python/mypy/issues/5374
@dataclasses.dataclass(frozen=True)  # type: ignore
class PhasedFSimCalibrationRequest(abc.ABC):
    """Description of the request to characterize PhasedFSimGate.

    Attributes:
        pairs: Set of qubit pairs to characterize. A single qubit can appear on at most one pair in
            the set.
        gate: Gate to characterize for each qubit pair from pairs. This must be a supported gate
            which can be described cirq.PhasedFSim gate.
    """

    pairs: Tuple[Tuple[Qid, Qid], ...]
    gate: Gate  # Any gate which can be described by cirq.PhasedFSim

    @abc.abstractmethod
    def to_calibration_layer(self) -> CalibrationLayer:
        """Encodes this characterization request in a CalibrationLayer object."""

    @abc.abstractmethod
    def parse_result(self, result: CalibrationResult) -> PhasedFSimCalibrationResult:
        """Decodes the characterization result issued for this request."""


@json_serializable_dataclass(frozen=True)
class FloquetPhasedFSimCalibrationOptions:
    """Options specific to Floquet PhasedFSimCalibration.

    Some angles require another angle to be characterized first so result might have more angles
    characterized than requested here.

    Attributes:
        characterize_theta: Whether to characterize θ angle.
        characterize_zeta: Whether to characterize ζ angle.
        characterize_chi: Whether to characterize χ angle.
        characterize_gamma: Whether to characterize γ angle.
        characterize_phi: Whether to characterize φ angle.
    """

    characterize_theta: bool
    characterize_zeta: bool
    characterize_chi: bool
    characterize_gamma: bool
    characterize_phi: bool


@dataclasses.dataclass(frozen=True)
class FloquetPhasedFSimCalibrationResult(PhasedFSimCalibrationResult):
    """PhasedFSim characterization result specific to Floquet calibration.

    Attributes:
        options: Options of the characterization from the request.
    """

    options: FloquetPhasedFSimCalibrationOptions

    @classmethod
    def _from_json_dict_(
        cls,
        parameters: List[Tuple[Qid, Qid, PhasedFSimCharacterization]],
        gate: Gate,
        **kwargs,
    ) -> 'PhasedFSimCalibrationResult':
        """Magic method for the JSON serialization protocol.

        Converts serialized dictionary into a dict suitable for
        class instantiation."""
        return cls(cls._create_parameters_dict(parameters), gate, kwargs['options'])

    def _json_dict_(self) -> Dict[str, Any]:
        """Magic method for the JSON serialization protocol."""
        result_dict = super()._json_dict_()
        result_dict['cirq_type'] = 'FloquetPhasedFSimCalibrationResult'
        result_dict['options'] = self.options
        return result_dict


@dataclasses.dataclass(frozen=True)
class FloquetPhasedFSimCalibrationRequest(PhasedFSimCalibrationRequest):
    """PhasedFSim characterization request specific to Floquet calibration.

    Attributes:
        options: Floquet-specific characterization options.
    """

    options: FloquetPhasedFSimCalibrationOptions

    def to_calibration_layer(self) -> CalibrationLayer:
        circuit = Circuit([self.gate.on(*pair) for pair in self.pairs])
        return CalibrationLayer(
            calibration_type=_FLOQUET_PHASED_FSIM_HANDLER_NAME,
            program=circuit,
            args={
                'est_theta': self.options.characterize_theta,
                'est_zeta': self.options.characterize_zeta,
                'est_chi': self.options.characterize_chi,
                'est_gamma': self.options.characterize_gamma,
                'est_phi': self.options.characterize_phi,
                'readout_corrections': True,
            },
        )

    def parse_result(self, result: CalibrationResult) -> PhasedFSimCalibrationResult:
        decoded: Dict[int, Dict[str, Any]] = collections.defaultdict(lambda: {})
        for keys, values in result.metrics['angles'].items():
            for key, value in zip(keys, values):
                match = re.match(r'(\d+)_(.+)', str(key))
                if not match:
                    raise ValueError(f'Unknown metric name {key}')
                index = int(match[1])
                name = match[2]
                decoded[index][name] = value

        parsed = {}
        for data in decoded.values():
            a = v2.qubit_from_proto_id(data['qubit_a'])
            b = v2.qubit_from_proto_id(data['qubit_b'])
            parsed[(a, b)] = PhasedFSimCharacterization(
                theta=data.get('theta_est', None),
                zeta=data.get('zeta_est', None),
                chi=data.get('chi_est', None),
                gamma=data.get('gamma_est', None),
                phi=data.get('phi_est', None),
            )

        return FloquetPhasedFSimCalibrationResult(
            parameters=parsed, gate=self.gate, options=self.options
        )

    @classmethod
    def _from_json_dict_(
        cls,
        gate: Gate,
        pairs: List[Tuple[Qid, Qid]],
        options: FloquetPhasedFSimCalibrationOptions,
        **kwargs,
    ) -> 'PhasedFSimCalibrationRequest':
        """Magic method for the JSON serialization protocol.

        Converts serialized dictionary into a dict suitable for
        class instantiation."""
        instantiation_pairs = tuple((entry[0], entry[1]) for entry in pairs)
        return cls(instantiation_pairs, gate, options)

    def _json_dict_(self) -> Dict[str, Any]:
        """Magic method for the JSON serialization protocol."""
        return {
            'cirq_type': 'FloquetPhasedFSimCalibrationRequest',
            'pairs': [(pair[0], pair[1]) for pair in self.pairs],
            'gate': self.gate,
            'options': self.options,
        }
