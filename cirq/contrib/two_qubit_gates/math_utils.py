from functools import reduce
from itertools import chain, permutations, product
from typing import Tuple, Union

import numpy as np
from matplotlib import pyplot

TWO_PI = np.pi * 2

_RealArraylike = Union[np.ndarray, float]


def _single_qubit_unitary(theta: _RealArraylike, phi_d: _RealArraylike,
                          phi_o: _RealArraylike) -> np.ndarray:
    """Single qubit unitary matrix.
    
    Args:
        theta: cos(theta) is magnitude of 00 matrix element. May be a scalar
           or real ndarray (for broadcasting).
        phi_d: exp(i phi_d) is the phase of 00 matrix element. May be a scalar
           or real ndarray (for broadcasting).
        phi_o: i exp(i phi_o) is the phase of 10 matrix element. May be a scalar
           or real ndarray (for broadcasting).

    
    Notes:
        The output is vectorized with respect to the angles. I.e, if the angles
        are (broadcastable) arraylike objects whose sum would have shape (...),
        the output is an array of shape (...,2,2), where the final two indices
        correspond to unitary matrices.
    """

    U00 = np.cos(theta) * np.exp(1j * np.asarray(phi_d))
    U10 = 1j * np.sin(theta) * np.exp(
        1j * np.asarray(phi_o))

    # This implementation is agnostic to the shapes of the angles, as long
    # as they can be broadcast together.
    Udiag = np.array([[U00, np.zeros_like(U00)],
                      [np.zeros_like(U00), U00.conj()]])
    Udiag = np.moveaxis(Udiag, [0, 1], [-2, -1])
    Uoff = np.array([[np.zeros_like(U10), -U10.conj()],
                     [U10, np.zeros_like(U10)]])
    Uoff = np.moveaxis(Uoff, [0, 1], [-2, -1])
    return Udiag + Uoff


def random_qubit_unitary(number: int = 1,
                         sample_phase: bool = False) -> np.ndarray:
    """Random qubit unitary distributed over the Haar measure.

    The implementation is vectorized for speed.

    Args:
        number: If not 1, an ndarray of shape (number,2,2) is returned.
            Otherwise a single 2x2 matrix is returned.
        sample_phase: (Default False) If True, a global phase is also sampled
            randomly. This corresponds to sampling over U(2) instead of SU(2).
    """
    theta = np.arcsin(np.sqrt(np.random.rand(number)))
    phi_d = np.random.rand(number) * TWO_PI
    phi_o = np.random.rand(number) * TWO_PI

    out = _single_qubit_unitary(theta, phi_d, phi_o)

    if sample_phase:
        global_phase = np.exp(1j * TWO_PI * np.random.rand(number))
        np.einsum('t,tab->tab', global_phase, out, out=out)
    return out


def vector_kron(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    """Vectorized implementation of kron for square matrices."""
    s_0, s_1 = first.shape[-2:], second.shape[-2:]
    assert s_0[0] == s_0[1]
    assert s_1[0] == s_1[1]
    out = np.einsum('...ab,...cd->...acbd', first, second)
    s_v = out.shape[:-4]
    return out.reshape(s_v + (s_0[0] * s_1[0],) * 2)


_MAGIC = np.array([[1, 0, 0, 1j],
                   [0, 1j, 1, 0],
                   [0, 1j, -1, 0],
                   [1, 0, 0, -1j]]) * np.sqrt(0.5)

_gamma = np.array([[1, 1, 1, 1],
                   [1, 1, -1, -1],
                   [-1, 1, -1, 1],
                   [1, -1, -1, 1]]) * 0.25


def canonicalize_kak_vector(k_vec: np.ndarray,
                            atol: float = 1e-8) -> np.ndarray:
    r"""Map a KAK vector into its Weyl chamber equivalent vector.

    This implementation is vectorized but does not produce the single qubit
    unitaries required to bring the KAK vector into canonical form.

    Args:
        k_vec: THe KAK vector to be canonicalized. This input may be vectorized,
            with shape (...,3), where the final axis denotes the k_vector and
            all other axes are broadcast.
        atol: How close x2 must be to π/4 to guarantee z2 >= 0.

    Returns:
        The canonicalized decomposition, with vector coefficients (x2, y2, z2)
        satisfying:

            0 ≤ abs(z2) ≤ y2 ≤ x2 ≤ π/4
            if x2 = π/4, z2 >= 0
        The output is vectorized, with shape k_vec.shape[:-1] + (3,).
    """
    k_vec = np.asarray(k_vec)
    # Get all strengths to (-¼π, ¼π]
    k_vec = np.mod(k_vec + np.pi / 4, np.pi / 2) - np.pi / 4

    # Sort in descending order with respect to absolute value.
    order = np.argsort(np.abs(k_vec), axis=-1)
    k_vec = np.take_along_axis(k_vec, order, axis=-1)[..., ::-1]

    # Multiply x,z and y,z components by -1 to fix x,y sign.
    x_negative = k_vec[..., 0] < 0
    k_vec[x_negative, 0] *= -1
    k_vec[x_negative, 2] *= -1
    y_negative = k_vec[..., 1] < 0
    k_vec[y_negative, 1] *= -1
    k_vec[y_negative, 2] *= -1

    # If x = π/4, force z to be positive.
    x_is_pi_over_4 = np.isclose(k_vec[..., 0], np.pi / 4, atol=atol)
    z_is_negative = k_vec[..., 2] < 0
    need_diff = np.logical_and(x_is_pi_over_4, z_is_negative)
    # -1 to x and z components, then shift x up by pi/2. Since x is pi/4, we
    # actually do nothing to that index.
    k_vec[need_diff, 2] *= -1

    return k_vec


def KAK_infidelity(unitary_a: np.ndarray,
                   unitary_b: np.ndarray,
                   ignore_equivalent_vectors: bool = False) -> np.ndarray:
    """Minimum entanglement infidelity between two unitaries, up to local gates.
    """
    return KAK_vector_infidelity(KAK_vector(unitary_a), KAK_vector(unitary_b),
                                 ignore_equivalent_vectors)


# all permutations of (1,2,3)
_perms_123 = np.zeros((6, 3, 3), int)
for ind, perm in enumerate(permutations((0, 1, 2))):
    _perms_123[ind, (0, 1, 2), perm] = 1

_negations = np.zeros((4, 3, 3), int)
_negations[0, (0, 1, 2), (0, 1, 2)] = 1
_negations[1, (0, 1, 2), (0, 1, 2)] = (1, -1, -1)
_negations[2, (0, 1, 2), (0, 1, 2)] = (-1, 1, -1)
_negations[3, (0, 1, 2), (0, 1, 2)] = (-1, -1, 1)

_offsets = np.zeros((4, 3))
_offsets[1, (1, 2)] = np.pi / 2
_offsets[1, (0, 2)] = np.pi / 2
_offsets[1, (0, 1)] = np.pi / 2


def _kak_equivalent_vectors(kak_vec) -> np.ndarray:
    """Generates all KAK vectors equivalent under a given KAK decomposition."""
    kak_vec = np.asarray(kak_vec)
    # Produce all shift-negations of the kak vector
    out = np.einsum('nab,...b->...na', _negations, kak_vec,
                    dtype=float)  # (...,4,3)
    out[..., :, :] += _offsets

    # Apply all permutations of indices
    out = np.einsum('pcb,...nb->...pnc', _perms_123, out)  # (...,6,4,3)

    # Merge indices
    return np.reshape(out, out.shape[:-3] + (24, 3))


def KAK_vector_infidelity(k_vec_a: np.ndarray,
                          k_vec_b: np.ndarray,
                          ignore_equivalent_vectors: bool = False
                          ) -> np.ndarray:
    """Minimum entanglement fidelity error between two KAK vectors. """
    if ignore_equivalent_vectors:
        k_diff = k_vec_a - k_vec_b
        out = 1 - np.product(np.cos(k_diff), axis=-1) ** 2
        out -= np.product(np.sin(k_diff), axis=-1) ** 2
        return out

    # We must take the minimum infidelity over all possible locally equivalent
    # KAK vectors
    k_vec_a = np.asarray(k_vec_a)[..., np.newaxis, :]  # (...,1,3)
    k_vec_b = _kak_equivalent_vectors(np.asarray(k_vec_b))  # (...,24,3)

    k_diff = k_vec_a - k_vec_b

    out = 1 - np.product(np.cos(k_diff), axis=-1) ** 2
    out -= np.product(np.sin(k_diff), axis=-1) ** 2  # (...,24)

    return out.min(axis=-1)


def in_weyl_chamber(xp: np.ndarray, yp: np.ndarray,
                    zp: np.ndarray) -> np.ndarray:
    """Whether a given collection of coordinates is within the Weyl chamber.

    Args:
        xp: X coordinates for the KAK vector.
        yp: Y coordinates for the KAK vector. Must have same shape as xp.
        zp: Z coordinates for the KAK vector. Must have same shape as xp.

    Returns:
        np.ndarray of boolean values denoting whether the given coordinates
        are in the Weyl chamber.
    """
    pi_4 = np.pi / 4

    x_inside = np.logical_and(0 <= xp, xp <= pi_4)

    y_inside = np.logical_and(0 <= yp, yp <= pi_4)
    y_inside = np.logical_and(y_inside, xp >= yp)

    z_inside = np.abs(zp) <= yp

    out = np.logical_and(x_inside, y_inside)
    return np.logical_and(out, z_inside)


def weyl_chamber_mesh(spacing: float) -> np.ndarray:
    """Cubic mesh of points in the Weyl chamber.

    Args:
        spacing: Distance between neighboring KAK vectors.

    Returns:
        np.ndarray of shape (N,3) corresponding to the points in the Weyl
        chamber.
    """
    if spacing < 1e-3:  # memory required ~ 1 GB
        raise ValueError(f'Generating a mesh with '
                         f'spacing {spacing} may cause system to crash.')

    # Uniform mesh
    disps = np.arange(-np.pi / 4, np.pi / 4, step=spacing)
    xs, ys, zs = [a.ravel() for a in np.array(np.meshgrid(*(disps,) * 3))]

    # Reduce to points within Weyl chamber
    sub_inds = in_weyl_chamber(xs, ys, zs)
    xs, ys, zs = xs[sub_inds], ys[sub_inds], zs[sub_inds]
    return np.array([xs, ys, zs]).T


def plot_points_in_weyl_chamber(points: np.ndarray, plot_bounds: bool = True
                                , **kwargs) -> pyplot.Axes:
    fig = pyplot.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(*points.T, **kwargs)

    # Weyl chamber vertices
    if plot_bounds:
        vertices = np.array([[0, 0, 0],
                             [1, 0, 0],
                             [1, 1, -1],
                             [1, 1, 1]]) * np.pi / 4

        path = (0, 1, 2, 3, 0, 2, 3, 1)
        path_mat = np.zeros((len(path), 4))
        path_mat[range(len(path)), path] = 1
        vertices = path_mat @ vertices

        ax.plot(vertices[:, 0], vertices[:, 1], vertices[:, 2], color='k',
                label='Bounds')

    ax.set_xlabel(r'$k_x$')
    ax.set_ylabel(r'$k_y$')
    ax.set_zlabel(r'$k_z$')
    return ax


_XX = np.zeros((4, 4))
_XX[(0, 1, 2, 3), (3, 2, 1, 0)] = 1
_ZZ = np.diag([1, -1, -1, 1])
_YY = -_XX @ _ZZ
_kak_gens = np.array([_XX, _YY, _ZZ])


def random_two_qubit_unitaries_and_kak_vecs(num_samples: int
                                            ) -> Tuple[
    np.ndarray, np.ndarray]:
    """Generate random two-qubit unitaries.

    Args:
        num_samples: Number of samples.

    Returns:
        unitaries: tensor storing the unitaries, shape (num_samples,4,4).
        kak_vecs: tensor storing KAK vectors of the unitaries (not canonical),
            shape (num_samples, 3).

    """
    kl, kr = _two_local_2Q_unitaries(num_samples)

    # Generate the non-local part by explict matrix exponentiation.
    kak_vecs = np.random.rand(num_samples, 3) * np.pi  # / 4
    # kak_vecs = np.sort(kak_vecs, axis=-1)[::-1]
    A = KAK_vector_to_unitary(kak_vecs)
    # Add a random phase
    phases = np.random.rand(num_samples) * np.pi * 2
    A = np.einsum('...,...ab->...ab', np.exp(1j * phases), A)

    return np.einsum('...ab,...bc,...cd', kl, A, kr), kak_vecs


def KAK_vector_to_unitary(vector: np.ndarray) -> np.ndarray:
    r"""Convert a KAK vector to its unitary matrix equivalent.

    Args:
        vector: A KAK vector shape (..., 3). (Input may be vectorized).

    Returns:
        unitary: Corresponding 2-qubit unitary, of the form
           exp( i k_x \sigma_x \sigma_x + i k_y \sigma_y \sigma_y
                + i k_z \sigma_z \sigma_z).
           matrix or tensor of matrices of shape (..., 4,4).
    """
    vector = np.asarray(vector)
    gens = np.einsum('...a,abc->...bc', vector, _kak_gens)
    evals, evecs = np.linalg.eigh(gens)

    return np.einsum('...ab,...b,...cb', evecs, np.exp(1j * evals),
                     evecs.conj())


def _two_local_2Q_unitaries(num_samples):
    kl_0 = random_qubit_unitary(num_samples)
    kl_1 = random_qubit_unitary(num_samples)
    kr_0 = random_qubit_unitary(num_samples)
    kr_1 = random_qubit_unitary(num_samples)
    kl = vector_kron(kl_0, kl_1)
    kr = vector_kron(kr_0, kr_1)
    return kl, kr
