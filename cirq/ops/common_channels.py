# Copyright 2018 The Cirq Developers
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

"""Quantum channels that are commonly used in the literature."""

from typing import Iterable

import numpy as np

from cirq import protocols
from cirq.ops import raw_types


class AsymmetricDepolarizingChannel(raw_types.Gate):
    """A channel that depolarizes asymmetrically along different directions."""

    def __init__(self, p_x: float, p_y: float, p_z: float) -> None:
        """The asymmmetric depolarizing channel.

        This channel applies one of four disjoint possibilities: nothing (the
        identity channel) or one of the three pauli gates. The disjoint
        probabilities of the three gates are p_x, p_y, and p_z and the
        identity is done with probability 1 - p_x - p_y - p_z. The supplied
        probabilities must be valid probabilities and the sum p_x + p_y + p_z
        must be a valid probability or else this constructor will raise a
        ValueError.

        This channel evolves a density matrix via
            \rho -> (1 -p_x + p_y + p_z) \rho
                    + p_x X \rho X + p_y Y \rho Y + p_z Z \rho Z

        Args:
            p_x: The probability that a Pauli X and no other gate occurs.
            p_y: The probability that a Pauli Y and no other gate occurs.
            p_z: The probability that a Pauli Z and no other gate occurs.

        Raises:
            ValueError if the args or the sum of the args are not probabilities.
        """

        def validate_probability(p, p_str):
            if p < 0:
                raise ValueError('{} was less than 0.'.format(p_str))
            elif p > 1:
                raise ValueError('{} was greater than 1.'.format(p_str))
            return p

        self._p_x = validate_probability(p_x, 'p_x')
        self._p_y = validate_probability(p_y, 'p_y')
        self._p_z = validate_probability(p_z, 'p_z')
        self._p_i = 1 - validate_probability(p_x + p_y + p_z, 'p_x + p_y + p_z')

    def _channel_(self) -> Iterable[np.ndarray]:
        return (
            np.sqrt(self._p_i) * np.eye(2),
            np.sqrt(self._p_x) * np.array([[0, 1], [1, 0]]),
            np.sqrt(self._p_y) * np.array([[0, -1j], [1j, 0]]),
            np.sqrt(self._p_z) * np.array([[1, 0], [0, -1]])
        )

    def _eq_tuple(self):
        return (AsymmetricDepolarizingChannel, self._p_x, self._p_y, self._p_z)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._eq_tuple() == other._eq_tuple()

    def __ne__(self, other):
        return not self == other

    def __repr__(self) -> str:
        return 'cirq.asymmetric_depolarize(p_x={!r},p_y={!r},p_z={!r})'.format(
            self._p_x, self._p_y, self._p_z
        )

    def __str__(self) -> str:
        return 'asymmetric_depolarize(p_x={!r},p_y={!r},p_z={!r})'.format(
            self._p_x, self._p_y, self._p_z
        )

    def _circuit_diagram_info_(
        self, args: protocols.CircuitDiagramInfoArgs
    ) -> str:
        return 'A({!r},{!r},{!r})'.format(self._p_x, self._p_y, self._p_z)


def asymmetric_depolarize(
    p_x: float, p_y: float, p_z: float
) -> AsymmetricDepolarizingChannel:
    """Returns a AsymmetricDepolarizingChannel with given parameter.

    This channel evolves a density matrix via
        \rho -> (1 -p_x + p_y + p_z) \rho
                + p_x X \rho X + p_y Y \rho Y + p_z Z \rho Z

    Args:
        p_x: The probability that a Pauli X and no other gate occurs.
        p_y: The probability that a Pauli Y and no other gate occurs.
        p_z: The probability that a Pauli Z and no other gate occurs.

    Raises:
        ValueError if the args or the sum of the args are not probabilities.
    """
    return AsymmetricDepolarizingChannel(p_x, p_y, p_z)


class DepolarizingChannel(raw_types.Gate):
    """A channel that depolarizes a qubit."""

    def __init__(self, p) -> None:
        """The symmetric depolarizing channel.

        This channel applies one of four disjoint possibilities: nothing (the
        identity channel) or one of the three pauli gates. The disjoint
        probabilities of the three gates are all the same, p / 3, and the
        identity is done with probability 1 - p. The supplied probability
        must be a valid probability or else this constructor will raise a
        ValueError.

        This channel evolves a density matrix via
            \rho -> (1 - p) \rho
                    + (p / 3) X \rho X + (p / 3) Y \rho Y + (p / 3) Z \rho Z

        Args:
            p: The probability that one of the Pauli gates is applied. Each of
                the Pauli gates is applied independently with probability p / 3.

        Raises:
            ValueError if p is not a valid probability.
        """

        self._p = p
        self._delegate = AsymmetricDepolarizingChannel(p / 3, p / 3, p / 3)

    def _channel_(self) -> Iterable[np.ndarray]:
        return self._delegate._channel_()

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._p == other._p

    def __ne__(self, other):
        return not self == other

    def __repr__(self) -> str:
        return 'cirq.depolarize(p={!r})'.format(self._p)

    def __str__(self) -> str:
        return 'depolarize(p={!r})'.format(self._p)

    def _circuit_diagram_info_(
        self, args: protocols.CircuitDiagramInfoArgs
    ) -> str:
        return 'D({!r})'.format(self._p)


def depolarize(p: float) -> DepolarizingChannel:
    """Returns a DepolarizingChannel with given probability of error.

    This channel applies one of four disjoint possibilities: nothing (the
    identity channel) or one of the three pauli gates. The disjoint
    probabilities of the three gates are all the same, p / 3, and the
    identity is done with probability 1 - p. The supplied probability
    must be a valid probability or else this constructor will raise a
    ValueError.

    This channel evolves a density matrix via
        \rho -> (1 - p) \rho
                + (p / 3) X \rho X + (p / 3) Y \rho Y + (p / 3) Z \rho Z

    Args:
        p: The probability that one of the Pauli gates is applied. Each of
            the Pauli gates is applied independently with probability p / 3.

    Raises:
        ValueError if p is not a valid probability.
    """
    return DepolarizingChannel(p)


class GeneralizedAmplitudeDampingChannel(raw_types.Gate):
    """ The generalized amplitude damping channel."""

    def __init__(self, p, gamma) -> None:

        """
        This channel models the effect of dissipation to the environment
        at possibly non zero tempurature. Where gamma is the damping rate
        and p is the probability of

        This channel evovles a density matrix via
            \rho -> M_0 \rho M_0^\dagger + M_1 \rho M_1^\dagger
                  + M_2 \rho M_2^\dagger + M_3 \rho M_3^\dagger

        With
            M_0 = \sqrt{p} \begin{bmatrix} 1 & 0  \\
                            0 & \sqrt{1 - \gamma} \end{bmatrix}
            M_1 = \sqrt{p} \begin{bmatrix} 0 & \sqrt{\gamma} \\
                            0 & 0 \end{bmatrix}
            M_2 = \sqrt{1-p} \begin{bmatrix} \sqrt{1-\gamma} & 0 \\
                            0 & 1 \end{bmatrix}
            M_3 = \sqrt{1-p} \begin{bmatrix} 0 & 0 \\
                            \sqrt{gamma} & 0 \end{bmatrix}

        Args:
            gamma: The damping rate
            p: the probability of

        Raises:
            ValueError is gamma or p is not a valid probability.
        """

        def validate_probability(p, p_str):
            if p < 0:
                raise ValueError('{} was less than 0.'.format(p_str))
            elif p > 1:
                raise ValueError('{} was greater than 1.'.format(p_str))
            return p

        self._gamma = validate_probability(gamma, 'gamma')
        self._p = validate_probability(p, 'p')

    def _channel_(self) -> Iterable[np.ndarray]:
        return (
            np.sqrt(self._p)
            * np.array([[1.0, 0.0], [0.0, np.sqrt(1.0 - self._gamma)]]),
            np.sqrt(self._p)
            * np.array([[0.0, np.sqrt(self._gamma)], [0.0, 0.0]]),
            np.sqrt(1.0 - self._p)
            * np.array([[np.sqrt(1.0 - self._gamma), 0.0], [0.0, 1.0]]),
            np.sqrt(1.0 - self._p)
            * np.array([[0.0, 0.0], [np.sqrt(self._gamma), 0.0]])
        )

    def _eq_tuple(self):
        return (GeneralizedAmplitudeDampingChannel, self._p, self._gamma)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._eq_tuple() == other._eq_tuple()

    def __ne__(self, other):
        return not self == other

    def __repr__(self) -> str:
        return 'cirq.generalized_amplitude_damping(p={!r},gamma={!r})'.format(
            self._p, self._gamma
        )

    def __str__(self) -> str:
        return 'generalized_amplitude_damping(p={!r},gamma={!r})'.format(
            self._p, self._gamma
        )

    def _circuit_diagram_info_(
        self, args: protocols.CircuitDiagramInfoArgs
    ) -> str:
        return 'GAD({!r},{!r})'.format(self._p, self._gamma)


def generalized_amplitude_damping(
    p: float, gamma: float
) -> GeneralizedAmplitudeDampingChannel:
    """
    Returns a GeneralizedAmplitudeDampingChannel with the given damping rate

    This channel evovles a density matrix via
            \rho -> M_0 \rho M_0^\dagger + M_1 \rho M_1^\dagger

    With
        M_0 = \begin{bmatrix} 1 & 0  \\ 0 & \sqrt{1 - \gamma} \end{bmatrix}
        M_1 = \begin{bmatrix} 0 & \sqrt{\gamma} \\ 0 & 0 \end{bmatrix}

    Args:
        gamma: The damping rate
        p: the probability of

    Raises:
        ValueError gamma or p is not a valid probability.
    """
    return GeneralizedAmplitudeDampingChannel(p, gamma)


class AmplitudeDampingChannel(raw_types.Gate):
    """ The amplitude damping channel."""

    def __init__(self, gamma) -> None:

        """
        This channel models the possible spontanious emmission of a photon
        dependant on a parameter gamma

        This channel evovles a density matrix via
            \rho -> M_0 \rho M_0^\dagger + M_1 \rho M_1^\dagger

        With
            M_0 = \begin{bmatrix} 1 & 0  \\ 0 & \sqrt{1 - \gamma} \end{bmatrix}
            M_1 = \begin{bmatrix} 0 & \sqrt{\gamma} \\ 0 & 0 \end{bmatrix}

        Args:
            gamma: The damping rate

        Raises:
            ValueError is gamma is not a valid probability.
        """

        def validate_probability(p, p_str):
            if p < 0:
                raise ValueError('{} was less than 0.'.format(p_str))
            elif p > 1:
                raise ValueError('{} was greater than 1.'.format(p_str))
            return p

        self._gamma = validate_probability(gamma, 'gamma')
        self._delegate = GeneralizedAmplitudeDampingChannel(1.0, self._gamma)

    def _channel_(self) -> Iterable[np.ndarray]:
        # just return first two kraus ops, we don't care about
        # the last two.
        return list(self._delegate._channel_())[:2]

    def _eq_tuple(self):
        return (AmplitudeDampingChannel, self._gamma)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._eq_tuple() == other._eq_tuple()

    def __ne__(self, other):
        return not self == other

    def __repr__(self) -> str:
        return 'cirq.amplitude_damping(gamma={!r})'.format(self._gamma)

    def __str__(self) -> str:
        return 'amplitude_damping(gamma={!r})'.format(self._gamma)

    def _circuit_diagram_info_(
        self, args: protocols.CircuitDiagramInfoArgs
    ) -> str:
        return 'AD({!r})'.format(self._gamma)


def amplitude_damping(gamma: float) -> AmplitudeDampingChannel:
    """
    Returns an AmplitudeDampingChannel with the given damping rate

    This channel evovles a density matrix via
            \rho -> M_0 \rho M_0^\dagger + M_1 \rho M_1^\dagger

    With
        M_0 = \begin{bmatrix} 1 & 0  \\ 0 & \sqrt{1 - \gamma} \end{bmatrix}
        M_1 = \begin{bmatrix} 0 & \sqrt{\gamma} \\ 0 & 0 \end{bmatrix}

    Args:
        gamma: the damping rate

    Raises:
        ValueError is gamma is not a valid probability.
    """
    return AmplitudeDampingChannel(gamma)


class PhaseDampingChannel(raw_types.Gate):
    """Phase Damping of a qubit"""

    def __init__(self, gamma) -> None:

        """
        This channel models phase damping which is the loss of quantum
        information without the loss of energy

        This channel evovles a density matrix via
            \rho -> M_0 \rho M_0^\dagger + M_1 \rho M_1^\dagger

        With
            M_0 = \begin{bmatrix} 1 & 0  \\ 0 & \sqrt{1 - \gamma} \end{bmatrix}
            M_1 = \begin{bmatrix} 0 & 0 \\ 0 & \sqrt{\gamma} \end{bmatrix}

        Args:
            gamma: The damping rate

        Raises:
            ValueError is gamma is not a valid probability.
        """

        def validate_probability(p, p_str):
            if p < 0:
                raise ValueError('{} was less than 0.'.format(p_str))
            elif p > 1:
                raise ValueError('{} was greater than 1.'.format(p_str))
            return p

        self._gamma = validate_probability(gamma, 'gamma')

    def _channel_(self) -> Iterable[np.ndarray]:
        return (
            np.array([[1.0, 0.0], [0.0, np.sqrt(1.0 - self._gamma)]]),
            np.array([[0.0, 0.0], [0.0, np.sqrt(self._gamma)]])
        )

    def _eq_tuple(self):
        return (PhaseDampingChannel, self._gamma)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._eq_tuple() == other._eq_tuple()

    def __ne__(self, other):
        return not self == other

    def __repr__(self) -> str:
        return 'cirq.phase_damping(gamma={!r})'.format(self._gamma)

    def __str__(self) -> str:
        return 'phase_damping(gamma={!r})'.format(self._gamma)

    def _circuit_diagram_info_(
        self, args: protocols.CircuitDiagramInfoArgs
    ) -> str:
        return 'PD({!r})'.format(self._gamma)


def phase_damping(gamma: float) -> PhaseDampingChannel:
    """
    Creates a phase damping channel with damping rate gamma

    This channel evovles a density matrix via
           \rho -> M_0 \rho M_0^\dagger + M_1 \rho M_1^\dagger

    With
        M_0 = \begin{bmatrix} 1 & 0  \\ 0 & \sqrt{1 - \gamma} \end{bmatrix}
        M_1 = \begin{bmatrix} 0 & 0 \\ 0 & \sqrt{\gamma} \end{bmatrix}

    Args:
        gamma: The damping rate

    Raises:
        ValueError is gamma is not a valid probability.
    """
    return PhaseDampingChannel(gamma)


class PhaseFlipChannel(raw_types.Gate):
    """Channel to flip a qubit's Phase"""

    def __init__(self, p) -> None:

        """
        This channel flips a qubit's Phase with probability p

        This channel evovles a density matrix via
            \rho -> M_0 \rho M_0^\dagger + M_1 \rho M_1^\dagger

        With
            M_0 = \sqrt{p} \begin{bmatrix} 1 & 0  \\ 0 & 1 \end{bmatrix}
            M_1 = \sqrt{1-p} \begin{bmatrix} 1 & 0 \\ 0 & -1 \end{bmatrix}

        Args:
            p: the probability of a phase flip

        Raises:
            ValueError if p is not a valid probability.
        """

        def validate_probability(p, p_str):
            if p < 0:
                raise ValueError('{} was less than 0.'.format(p_str))
            elif p > 1:
                raise ValueError('{} was greater than 1.'.format(p_str))
            return p

        self._p = validate_probability(p, 'p')
        self._delegate = AsymmetricDepolarizingChannel(0.0, 0.0, 1.0 - p)

    def _channel_(self) -> Iterable[np.ndarray]:
        kraus_ops = list(self._delegate._channel_())
        # just return identity and z term
        return (kraus_ops[0], kraus_ops[3])

    def _eq_tuple(self):
        return (PhaseFlipChannel, self._p)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._eq_tuple() == other._eq_tuple()

    def __ne__(self, other):
        return not self == other

    def __repr__(self) -> str:
        return 'cirq.phase_flip(p={!r})'.format(self._p)

    def __str__(self) -> str:
        return 'phase_flip(p={!r})'.format(self._p)

    def _circuit_diagram_info_(
        self, args: protocols.CircuitDiagramInfoArgs
    ) -> str:
        return 'PF({!r})'.format(self._p)


def phase_flip(p: float) -> PhaseFlipChannel:
    """
    Constructs a channel that flips a qubit's phase with probability p

    This channel evovles a density matrix via
           \rho -> M_0 \rho M_0^\dagger + M_1 \rho M_1^\dagger

    With
        M_0 = \sqrt{p} \begin{bmatrix} 1 & 0  \\ 0 & 1 \end{bmatrix}
        M_1 = \sqrt{1-p} \begin{bmatrix} 1 & 0 \\ 0 & -1 \end{bmatrix}

    Args:
        p: the probability of a phase flip

    Raises:
        ValueError if p is not a valid probability.
    """
    return PhaseFlipChannel(p)


class BitFlipChannel(raw_types.Gate):
    """Channel to flip a qubit"""

    def __init__(self, p) -> None:

        """
        This channel flips a qubit phase with probability p

        This channel evovles a density matrix via
            \rho -> M_0 \rho M_0^\dagger + M_1 \rho M_1^\dagger

        With
            M_0 = \sqrt{p} \begin{bmatrix} 1 & 0  \\ 0 & 1 \end{bmatrix}
            M_1 = \sqrt{1-p} \begin{bmatrix} 0 & 1 \\ 1 & -0 \end{bmatrix}

        Args:
            p: the probability of a bit flip

        Raises:
            ValueError if p is not a valid probability.
        """

        def validate_probability(p, p_str):
            if p < 0:
                raise ValueError('{} was less than 0.'.format(p_str))
            elif p > 1:
                raise ValueError('{} was greater than 1.'.format(p_str))
            return p

        self._p = validate_probability(p, 'p')
        self._delegate = AsymmetricDepolarizingChannel(1.0 - p, 0.0, 0.0)

    def _channel_(self) -> Iterable[np.ndarray]:
        # Return just the I and X pieces.
        return list(self._delegate._channel_())[:2]

    def _eq_tuple(self):
        return (BitFlipChannel, self._p)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._eq_tuple() == other._eq_tuple()

    def __ne__(self, other):
        return not self == other

    def __repr__(self) -> str:
        return 'cirq.bit_flip(p={!r})'.format(self._p)

    def __str__(self) -> str:
        return 'bit_flip(p={!r})'.format(self._p)

    def _circuit_diagram_info_(
        self, args: protocols.CircuitDiagramInfoArgs
    ) -> str:
        return 'BF({!r})'.format(self._p)


def bit_flip(p: float) -> BitFlipChannel:
    """
    Construct a bit flip channel with probability of a flip given by p

    This channel evovles a density matrix via
            \rho -> M_0 \rho M_0^\dagger + M_1 \rho M_1^\dagger

    With
        M_0 = \sqrt{p} \begin{bmatrix} 1 & 0  \\ 0 & 1 \end{bmatrix}
        M_1 = \sqrt{1-p} \begin{bmatrix} 0 & 1 \\ 1 & -0 \end{bmatrix}

    Args:
        p: the probability of a bit flip

    Raises:
        ValueError if p is not a valid probability.
    """
    return BitFlipChannel(p)


class RotationErrorChannel(raw_types.Gate):
    """Channel to introduce rotation error in X, Y, Z"""

    def __init__(self, eps_x, eps_y, eps_z) -> None:

        """
        This channel introduces rotation error by epsilon for
        rotations in X, Y and Z that are constant in time.

        This channel evovles a density matrix via
            \rho ->
           \exp{-i \epsilon_x \frac{X}{2}} \rho \exp{i \epsilon_x \frac{X}{2}}
          + \exp{-i \epsilon_y \frac{Y}{2}} \rho \exp{i \epsilon_y \frac{Y}{2}}
          + \exp{-i \epsilon_z \frac{Z}{2}} \rho \exp{i \epsilon_z \frac{Z}{2}}

        Args:
            eps_x: angle to over rotate in x
            eps_y: angle to over rotate in y
            eps_z: angle to over rotate in z
        """

        # Angles could be anything, so no validation nescessary ?
        self._eps_x = eps_x
        self._eps_y = eps_y
        self._eps_z = eps_z

    def _channel_(self) -> Iterable[np.ndarray]:
        return (
            np.exp(
                0.5
                * (0.0 - 1.0j)
                * self._eps_x
                * np.array([[0.0, 1.0], [1.0, 0.0]])
            ),
            np.exp(
                0.5
                * (0.0 - 1.0j)
                * self._eps_y
                * np.array([[0.0, (0.0 - 1.0j)], [(0.0 + 1.0j), 0.0]])
            ),
            np.exp(
                0.5
                * (0.0 - 1.0j)
                * self._eps_z
                * np.array([[1.0, 0.0], [0.0, -1.0]])
            )
        )

    def _eq_tuple(self):
        return (RotationErrorChannel, self._eps_x, self._eps_y, self._eps_z)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._eq_tuple() == other._eq_tuple()

    def __ne__(self, other):
        return not self == other

    def __repr__(self) -> str:
        return 'cirq.rotation_error(eps_x={!r},eps_y={!r},eps_z={!r})'.format(
            self._eps_x, self._eps_y, self._eps_z
        )

    def __str__(self) -> str:
        return 'rotation_error(eps_x={!r},eps_y={!r},eps_z={!r})'.format(
            self._eps_x, self._eps_y, self._eps_z
        )

    def _circuit_diagram_info_(
        self, args: protocols.CircuitDiagramInfoArgs
    ) -> str:
        return 'RE({!r},{!r},{!r})'.format(
            self._eps_x, self._eps_y, self._eps_z
        )


def rotation_error(
    eps_x: float, eps_y: float, eps_z: float
) -> RotationErrorChannel:

    """
    Constructs a rotation error channel that can over/under rotate
    a qubit in X, Y, Z by given error angles.

    This channel evovles a density matrix via
        \rho ->
        \exp{-i \epsilon_x \frac{X}{2}} \rho \exp{i \epsilon_x \frac{X}{2}}
        + \exp{-i \epsilon_y \frac{Y}{2}} \rho \exp{i \epsilon_y \frac{Y}{2}}
        + \exp{-i \epsilon_z \frac{Z}{2}} \rho \exp{i \epsilon_z \frac{Z}{2}}

    Args:
        eps_x: angle to over rotate in x
        eps_y: angle to over rotate in y
        eps_z: angle to over rotate in z
    """

    return RotationErrorChannel(eps_x, eps_y, eps_z)
