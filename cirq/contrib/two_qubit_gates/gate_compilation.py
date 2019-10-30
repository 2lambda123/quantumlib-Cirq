"""Attempt to tabulate single qubit gates required to generate a target 2Q gate
with a product A k A."""
from functools import reduce
from typing import Tuple, Dict, Sequence, List, NamedTuple
from warnings import warn

import numpy as np
import attr
from cirq import kak_decomposition, kak_vector
from cirq.contrib.two_qubit_gates.math_utils import (KAK_vector_infidelity,
                                                     vector_kron,
                                                     weyl_chamber_mesh,
                                                     random_qubit_unitary,
                                                     KAK_vector_to_unitary)

_SingleQubitGatePair = Tuple[np.ndarray, np.ndarray]


class TwoQubitGateCompilation(NamedTuple):
    """Represents a compilation of a target 2-qubit with respect to a base gate.

    This object encodes the relationship between 4x4 unitary operators

    U_target ~ k_N · U_base · k_{N-1} · ... · k_1 · U_base · k_0

    where U_target, U_base are 2-local and k_j are 1-local.

    Attributes:
        base_gate: 4x4 unitary denoting U_base above.
        target_gate: 4x4 unitary denoting U_target above.
        local_unitaries: Sequence of 2-tuples (k_{00},k_{01}),(k_{10},k_{11})...
            where k_j = k_{j0} ⊗ k_{j1} in the product above. Each k_{j0},
            k_{j1} is a 2x2 unitary.
        actual_gate: 4x4 unitary denoting the right hand side above, ideally
            equal to U_target.
        success: Whether actual_gate is expected to be close to U_target.
    """
    base_gate: np.ndarray
    target_gate: np.ndarray
    local_unitaries: Tuple[_SingleQubitGatePair, ...]
    actual_gate: np.ndarray
    success: bool


@attr.s(auto_attribs=True)
class GateTabulation:
    """A 2-qubit gate compiler based on precomputing/tabulating gate products.

    """
    base_gate: np.ndarray  # Base two qubit gate. (4x4 unitary)
    # Sequence of KAK vectors, ideally "dense" in the Weyl chamber. Shape (N,3).
    kak_vecs: np.ndarray
    # Sequence of 1-local operations required to achieve a given KAK vector.
    # Index j corresponds to KAK_vecs[j], and is of the form
    # ( (u0[0],u1[0]), (u0[1],u1[1]), ...) where u0[k] is the kth single qubit
    # unitary acting on qubit 0 (similarly for u1)
    single_qubit_gates: Sequence[Sequence[_SingleQubitGatePair]]
    max_expected_infidelity: float

    def compile_two_qubit_gate(
            self, unitary: np.ndarray
    ) -> TwoQubitGateCompilation:
        r"""Compute single qubit gates required to compile a desired unitary.

        Given a desired unitary U, this computes the sequence of 1-local gates
        k_j such that the product

        k_{n-1} A k_{n-2} A ... k_1 A k_0

        is close to U. Here A is the base_gate of the tabulation.

        Args:
            unitary: Unitary (U above) to compile.

        Returns:
            A TwoQubitGateCompilation object encoding the required local
            unitaries and resulting product above.
        """
        unitary = np.asarray(unitary)
        kak_vec = kak_vector(unitary, check_preconditions=False)
        infidelities = KAK_vector_infidelity(kak_vec,
                                             self.kak_vecs,
                                             ignore_equivalent_vectors=True)
        nearest_ind = infidelities.argmin()

        success = infidelities[nearest_ind] < self.max_expected_infidelity

        # shape (n,2,2,2)
        inner_gates = np.array(self.single_qubit_gates[nearest_ind])

        if inner_gates.size == 0:  # Only need base gate
            kR, kL, actual = _outer_locals_for_unitary(
                unitary, self.base_gate)
            return TwoQubitGateCompilation(self.base_gate, unitary, (kR, kL),
                                           actual, success)

        # reshape to operators on 2 qubits, (n,4,4)
        inner_gates = vector_kron(inner_gates[..., 0, :, :],
                                  inner_gates[..., 1, :, :])

        assert inner_gates.ndim == 3
        inner_product = reduce(lambda a, b: self.base_gate @ b @ a, inner_gates,
                               self.base_gate)
        kR, kL, actual = _outer_locals_for_unitary(unitary, inner_product)

        out = [kR]
        out.extend(self.single_qubit_gates[nearest_ind])
        out.append(kL)

        return TwoQubitGateCompilation(self.base_gate, unitary, tuple(out),
                                       actual, success)


def _outer_locals_for_unitary(
        target: np.ndarray, base: np.ndarray
) -> Tuple[_SingleQubitGatePair, _SingleQubitGatePair, np.ndarray]:
    """Local unitaries mapping between locally equivalent 2-local unitaries.

    Finds the left and right 1-local unitaries kL, kR such that

    U_target = kL @ U_base @ kR

    Args:
        target: The unitary to which we want to map.
        base: The base unitary which maps to target.

    Returns:
        kR: The right 1-local unitaries in the equation above, expressed as
            2-tuples of (2x2) single qubit unitaries.
        kL: The left 1-local unitaries in the equation above, expressed as
            2-tuples of (2x2) single qubit unitaries.
        actual: The outcome of kL @ base @ kR
    """
    target_decomp = kak_decomposition(target)
    base_decomp = kak_decomposition(base)

    # From the KAK decomposition, we have
    # kLt At kRt = kL kLb Ab KRb kR
    # If At=Ab, we can solve for kL and kR as
    # kLt = kL kLb --> kL = kLt kLb^\dagger
    # kRt = kRb kR --> kR = kRb\dagger kRt

    # 0 and 1 are qubit indices.
    kLt0, kLt1 = target_decomp.single_qubit_operations_after
    kLb0, kLb1 = base_decomp.single_qubit_operations_after
    kL = kLt0 @ kLb0.conj().T, kLt1 @ kLb1.conj().T

    kRt0, kRt1 = target_decomp.single_qubit_operations_before
    kRb0, kRb1 = base_decomp.single_qubit_operations_before
    kR = kRb0.conj().T @ kRt0, kRb1.conj().T @ kRt1

    actual = np.kron(*kL) @ base
    actual = actual @ np.kron(*kR)
    actual *= np.conj(target_decomp.global_phase)

    return kR, kL, actual


def _tabulate_KAK_vectors(
        tabulation: Dict[int, Tuple[_SingleQubitGatePair, ...]],
        base_gate: np.ndarray,
        max_dist: float,
        kak_mesh: np.ndarray,
        *local_unitary_pairs: _SingleQubitGatePair,
) -> Tuple[List[np.ndarray], List[Tuple[_SingleQubitGatePair, ...]]]:
    """Tabulate KAK vectors from products of local unitaries with a base gate.

    Args:
        tabulation: Dictionary mapping indices of the KAK vector mesh to the
            gate products required to achieve the corresponding KAK vector,
            within some Pauli error.
        base_gate: The base 2 qubit gate used in the gate product.
        max_dist: The largest allowed Pauli error between a generated 2Q
           unitary and a KAK vector mesh point that it is tabulated to.
        kak_mesh: Sequence of KAK vectors filling the Weyl chamber whose
            nearest neighbor distance is about 2*max_error.
        *local_unitary_pairs: 2-Tuples of single qubit unitary tensors, each
            of shape (N,2,2).

    Returns:
        kept_kaks: Generated KAK vectors that are uniquely close to at least one
            mesh point.
        kept_cycles: The corresponding single qubit unitaries required to obtain
            the desired KAK vectors.
    """
    shapes = {pair[0].shape for pair in local_unitary_pairs}
    shapes.update({pair[0].shape for pair in local_unitary_pairs})
    assert len(shapes) == 1
    assert len(shapes.pop()) == 3

    # Generate products
    local_cycles = np.array(
        [vector_kron(*pairs) for pairs in local_unitary_pairs])

    prods = np.einsum('ab,...bc,cd', base_gate, local_cycles[0], base_gate)
    for local_cycle in local_cycles[1:]:
        np.einsum('ab,...bc,...cd', base_gate, local_cycle, prods, out=prods)

    kak_vectors = kak_vector(prods, check_preconditions=False)

    kept_kaks = []
    kept_cycles = []

    for ind, vec in enumerate(kak_vectors):
        # dists = KAK_vector_infidelity(vec, KAK_mesh)
        # The L2 distance is an upper bound to the locally invariant distance,
        # but it's much faster to compute.
        dists = np.sqrt(np.sum((kak_mesh - vec) ** 2, axis=-1))
        close = (dists < max_dist).nonzero()[0]
        assert close.shape[0] in (0, 1), f'shape: {close.shape}'
        cycles_for_gate = tuple(
            (k_0[ind], k_1[ind]) for k_0, k_1 in local_unitary_pairs)

        kept = False
        for mesh_ind in close:
            if mesh_ind not in tabulation:
                tabulation[mesh_ind] = cycles_for_gate
                kept = True

        if kept:
            kept_kaks.append(vec)
            kept_cycles.append(cycles_for_gate)

    return kept_kaks, kept_cycles


def gate_product_tabulation(base_gate: np.ndarray,
                            max_infidelity: float,
                            verbose: bool = False,
                            include_warnings: bool = True,
                            sample_scaling: int = 50) -> GateTabulation:
    r"""Generate a GateTabulation for a base two qubit unitary.

    Args:
        base_gate: The base gate of the tabulation.
        max_infidelity: Sets the desired density of tabulated product unitaries.
            The typical nearest neighbor Euclidean spacing (of the KAK vectors)
            will be on the order of \sqrt(max_infidelity). Thus the number of
            tabulated points will scale as max_infidelity^{-3/2}.
        verbose: Whether to print gate tabulation statistics.
        include_warnings: If True, warn the user if a point in the Weyl
            chamber has no tabulated points within the desired distance.
        sample_scaling: Relative number of random gate products to use in the
            tabulation. The total number of random local unitaries scales as
            ~ max_infidelity^{-3/2} * sample_scaling. Must be positive.

    Returns:
        A GateTabulation object used to compile new two-qubit gates from
        products of the base gate with 1-local unitaries.
    """
    assert 1 / 2 > max_infidelity > 0
    spacing = np.sqrt(max_infidelity / 3)
    mesh_points = weyl_chamber_mesh(spacing)

    # Number of random gate products to sample over in constructing the
    # tabulation. This has to be at least the number of mesh points, as
    # a single product can only be associated with one mesh point.
    assert sample_scaling > 0, 'Input sample_scaling must positive.'
    num_samples = mesh_points.shape[0] * sample_scaling

    # include the base gate itself
    kak_vecs = [kak_vector(base_gate, check_preconditions=False)]
    sq_cycles: List[Tuple[_SingleQubitGatePair, ...]] = [()]

    # Tabulate gates that are close to gates in the mesh
    u_locals_0 = random_qubit_unitary(num_samples)
    u_locals_1 = random_qubit_unitary(num_samples)

    u_locals_for_gate: Dict[int, Tuple[_SingleQubitGatePair, ...]] = {}
    tabulation_cutoff = 0.5 * spacing
    out = _tabulate_KAK_vectors(u_locals_for_gate, base_gate, tabulation_cutoff,
                                mesh_points, (u_locals_0, u_locals_1))
    kak_vecs.extend(out[0])
    sq_cycles.extend(out[1])

    # Will be used later for getting missing KAK vectors.
    kak_vecs_single = np.array(kak_vecs[1:])
    sq_cycles_single = list(sq_cycles[1:])

    if verbose:
        # coverage: ignore
        print(f'fraction satisfied with 2 gates'
              f': {len(u_locals_for_gate) / mesh_points.shape[0]:.3f}')

    # repeat for double products
    # Multiply by the same local unitary!
    out = _tabulate_KAK_vectors(u_locals_for_gate, base_gate, tabulation_cutoff,
                                mesh_points, (u_locals_0, u_locals_1),
                                (u_locals_0, u_locals_1))

    kak_vecs.extend(out[0])
    sq_cycles.extend(out[1])

    if verbose:
        # coverage: ignore
        print(f'fraction satisfied with 2 gates and 3 gates(same single qubit)'
              f': {len(u_locals_for_gate) / mesh_points.shape[0]:.3f}')

    # If all KAK vectors in the mesh have been tabulated, return.
    missing_vec_inds = set(range(mesh_points.shape[0])) - set(u_locals_for_gate)

    if not missing_vec_inds:
        # coverage: ignore
        return GateTabulation(base_gate, np.array(kak_vecs), sq_cycles,
                              max_infidelity)

    # Run through remaining KAK vectors that don't have products and try to
    # correct them

    u_locals_0p = random_qubit_unitary(100)
    u_locals_1p = random_qubit_unitary(100)
    u_locals = vector_kron(u_locals_0p, u_locals_1p)

    # Loop through the mesh points that have not yet been tabulated.
    # Consider their nonlocal parts A and compute products of the form
    # base_gate^\dagger k A
    # Compare the KAK vector of any of those products to the already tabulated
    # KAK vectors from single products of the form
    # base_gate k0 base_gate.
    # If they are close, then base_gate^\dagger k A  ~ base_gate k0 base_gate
    # So we may compute the outer local unitaries kL, kR such that
    #    base_gate^\dagger k A = kL base_gate k0 base_gate kR
    #    A = k^\dagger base_gate kL base_gate k0 base_gate kR
    #    the single-qubit unitary kL is the one we need to get the desired
    #    KAK vector.
    base_gate_dag = base_gate.conj().T
    for ind in missing_vec_inds:
        missing_vec = mesh_points[ind]
        missing_unitary = KAK_vector_to_unitary(missing_vec)

        products = np.einsum('ab,...bc,cd', base_gate_dag, u_locals,
                             missing_unitary)
        kaks = kak_vector(products, check_preconditions=False)
        kaks = kaks[..., np.newaxis, :]

        dists2 = np.sum((kaks - kak_vecs_single) ** 2, axis=-1)
        min_dist_inds = np.unravel_index(dists2.argmin(), dists2.shape)
        min_dist = np.sqrt(dists2[min_dist_inds])
        if min_dist < tabulation_cutoff:
            new_ind, old_ind = min_dist_inds

            old_sq_cycle = sq_cycles_single[old_ind][0]
            old_k = np.kron(*old_sq_cycle)
            base_product = base_gate @ old_k @ base_gate
            new_product = products[new_ind]

            kR, kL, actual = _outer_locals_for_unitary(new_product,
                                                       base_product)
            # Add to the enumeration
            sq_cycles.append((old_sq_cycle, kL))
            kak_vecs.append(
                kak_vector(base_gate @ actual, check_preconditions=False))
        elif include_warnings:
            # coverage: ignore
            warn(f'Failed to tabulate a KAK vector near {missing_vec}')

    kak_vecs = np.array(kak_vecs)
    if verbose:
        # coverage: ignore
        print(f'fraction satisfied with 2 gates and 3 gates (after patchup)'
              f': {(len(kak_vecs) - 1) / mesh_points.shape[0]:.3f}')

    return GateTabulation(base_gate, kak_vecs, sq_cycles, max_infidelity)
