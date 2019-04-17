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

from cirq._version import (
    __version__,
)

# Flattened sub-modules.

from cirq.circuits import (
    Circuit,
    CircuitDag,
    InsertStrategy,
    PointOptimizationSummary,
    PointOptimizer,
    QasmOutput,
    TextDiagramDrawer,
    Unique,
)

from cirq.devices import (
    Device
    GridQubit,
    UnconstrainedDevice,
)

from cirq.experiments import (
    generate_supremacy_circuit_google_v2,
    generate_supremacy_circuit_google_v2_bristlecone,
    generate_supremacy_circuit_google_v2_grid,
)

from cirq.linalg import (
    all_near_zero,
    all_near_zero_mod,
    allclose_up_to_global_phase,
    apply_matrix_to_slices,
    bidiagonalize_real_matrix_pair_with_symmetric_products,
    bidiagonalize_unitary_with_special_orthogonals,
    block_diag,
    commutes,
    CONTROL_TAG,
    diagonalize_real_symmetric_and_sorted_diagonal_matrices,
    diagonalize_real_symmetric_matrix,
    dot,
    expand_matrix_in_orthogonal_basis,
    hilbert_schmidt_inner_product,
    is_diagonal,
    is_hermitian,
    is_orthogonal,
    is_special_orthogonal,
    is_special_unitary,
    is_unitary,
    kak_canonicalize_vector,
    kak_decomposition,
    KakDecomposition,
    kron,
    kron_bases,
    kron_factor_4x4_to_2x2s,
    kron_with_controls,
    map_eigenvalues,
    match_global_phase,
    matrix_from_basis_coefficients,
    partial_trace,
    PAULI_BASIS,
    reflection_matrix_pow,
    slice_for_qubits_equal_to,
    so4_to_magic_su2s,
    targeted_conjugate_about,
    targeted_left_multiply,
)

from cirq.line import (
    LineQubit,
)

from cirq.ops import (
    amplitude_damp,
    AmplitudeDampingChannel,
    ApproxPauliStringExpectation,
    asymmetric_depolarize,
    AsymmetricDepolarizingChannel,
    bit_flip,
    BitFlipChannel,
    CCX,
    CCXPowGate,
    CCZ,
    CCZPowGate,
    CNOT,
    CNotPowGate,
    ControlledGate,
    ControlledOperation,
    CSWAP,
    CSwapGate,
    CZ,
    CZPowGate,
    DensityMatrixDisplay,
    depolarize,
    DepolarizingChannel,
    EigenGate,
    flatten_op_tree,
    FREDKIN,
    freeze_op_tree,
    Gate,
    GateOperation,
    generalized_amplitude_damp,
    GeneralizedAmplitudeDampingChannel,
    H,
    HPowGate,
    I,
    IdentityGate,
    InterchangeableQubitsGate,
    ISWAP,
    ISwapPowGate,
    LinearCombinationOfGates,
    measure,
    measure_each,
    MeasurementGate,
    Moment,
    NamedQubit,
    op_gate_of_type,
    OP_TREE,
    Operation,
    ParallelGateOperation,
    Pauli,
    pauli_string_expectation,
    PauliInteractionGate,
    PauliString,
    PauliStringExpectation,
    PauliTransform,
    phase_damp,
    phase_flip,
    PhaseDampingChannel,
    PhasedXPowGate,
    PhaseFlipChannel,
    Qid,
    QubitOrder,
    QubitOrderOrList,
    Rx,
    Ry,
    Rz,
    S,
    SamplesDisplay,
    SingleQubitCliffordGate,
    SingleQubitGate,
    SingleQubitMatrixGate,
    SWAP,
    SwapPowGate,
    T,
    ThreeQubitGate,
    TOFFOLI,
    transform_op_tree,
    TwoQubitGate,
    TwoQubitMatrixGate,
    WaveFunctionDisplay,
    X,
    XPowGate,
    XX,
    XXPowGate,
    Y,
    YPowGate,
    YY,
    YYPowGate,
    Z,
    ZPowGate,
    ZZ,
    ZZPowGate,
)

from cirq.optimizers import (
    ConvertToCzAndSingleGates,
    DropEmptyMoments,
    DropNegligible,
    EjectPhasedPaulis,
    EjectZ,
    ExpandComposite,
    is_negligible_turn,
    merge_single_qubit_gates_into_phased_x_z,
    MergeInteractions,
    MergeSingleQubitGates,
    single_qubit_matrix_to_gates,
    single_qubit_matrix_to_pauli_rotations,
    single_qubit_matrix_to_phased_x_z,
    single_qubit_op_to_framed_phase_form,
    two_qubit_matrix_to_operations,
)

from cirq.schedules import (
    moment_by_moment_schedule,
    Schedule,
    ScheduledOperation,
)

from cirq.sim import (
    bloch_vector_from_state_vector,
    density_matrix_from_state_vector,
    DensityMatrixSimulator,
    DensityMatrixSimulatorState,
    DensityMatrixStepResult,
    DensityMatrixTrialResult,
    dirac_notation,
    measure_density_matrix,
    measure_state_vector,
    sample,
    sample_density_matrix,
    sample_state_vector,
    sample_sweep,
    SimulatesFinalState,
    SimulatesIntermediateState,
    SimulatesIntermediateWaveFunction,
    SimulatesSamples,
    SimulationTrialResult,
    Simulator,
    SparseSimulatorStep,
    StateVectorMixin,
    StepResult,
    to_valid_density_matrix,
    to_valid_state_vector,
    validate_normalized_state,
    WaveFunctionSimulatorState,
    WaveFunctionStepResult,
    WaveFunctionTrialResult,
)

from cirq.study import (
    ComputeDisplaysResult,
    Linspace,
    ParamResolver,
    ParamResolverOrSimilarType,
    plot_state_histogram,
    Points,
    Sweep,
    Sweepable,
    to_resolvers,
    TrialResult,
    UnitSweep,
)

from cirq.value import (
    canonicalize_half_turns,
    chosen_angle_to_canonical_half_turns,
    chosen_angle_to_half_turns,
    Duration,
    LinearDict,
    PeriodicValue,
    Timestamp,
    validate_probability,
    value_equality,
)

# pylint: disable=redefined-builtin
from cirq.protocols import (
    apply_channel,
    apply_unitary,
    ApplyChannelArgs,
    ApplyUnitaryArgs,
    approx_eq,
    control,
    channel,
    circuit_diagram_info,
    CircuitDiagramInfo,
    CircuitDiagramInfoArgs,
    decompose,
    decompose_once,
    decompose_once_with_qubits,
    has_channel,
    has_mixture,
    has_mixture_channel,
    has_unitary,
    inverse,
    is_measurement,
    is_parameterized,
    measurement_key,
    mixture,
    mixture_channel,
    mul,
    pauli_expansion,
    phase_by,
    pow,
    qasm,
    QasmArgs,
    resolve_parameters,
    SupportsApplyChannel,
    SupportsApplyUnitary,
    SupportsApproximateEquality,
    SupportsChannel,
    SupportsCircuitDiagramInfo,
    SupportsDecompose,
    SupportsDecomposeWithQubits,
    SupportsMixture,
    SupportsParameterization,
    SupportsPhase,
    SupportsQasm,
    SupportsQasmWithArgs,
    SupportsQasmWithArgsAndQubits,
    SupportsTraceDistanceBound,
    SupportsUnitary,
    trace_distance_bound,
    unitary,
    validate_mixture,
)

from cirq.ion import (
    ConvertToIonGates,
    IonDevice,
    MS,
    two_qubit_matrix_to_ion_operations,
)
from cirq.neutral_atoms import (
    ConvertToNeutralAtomGates,
    is_native_neutral_atom_gate,
    is_native_neutral_atom_op,
    NeutralAtomDevice,
)
# pylint: enable=redefined-builtin

# Unflattened sub-modules.

from cirq import (
    contrib,
    google,
    testing,
)
