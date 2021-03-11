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
"""Estimation of fidelity associated with experimental circuit executions."""
from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import (
    List,
    Optional,
    Sequence,
    Tuple,
    TYPE_CHECKING,
    Dict,
)

import numpy as np
import pandas as pd
import scipy.optimize
import scipy.stats
import sympy

from cirq import ops
from cirq.circuits import Circuit
from cirq.protocols import json_serializable_dataclass
from cirq.experiments.xeb_simulation import simulate_2q_xeb_circuits

if TYPE_CHECKING:
    import cirq
    import multiprocessing

THETA_SYMBOL, ZETA_SYMBOL, CHI_SYMBOL, GAMMA_SYMBOL, PHI_SYMBOL = sympy.symbols(
    'theta zeta chi gamma phi'
)
SQRT_ISWAP = ops.ISWAP ** 0.5


def benchmark_2q_xeb_fidelities(
    sampled_df: pd.DataFrame,
    circuits: Sequence['cirq.Circuit'],
    cycle_depths: Sequence[int],
    param_resolver: 'cirq.ParamResolverOrSimilarType' = None,
    pool: Optional['multiprocessing.pool.Pool'] = None,
):
    """Simulate and benchmark two-qubit XEB circuits.

    This uses the estimator from
    `cirq.experiments.fidelity_estimation.least_squares_xeb_fidelity_from_expectations`, but
    adapted for use on pandas DataFrames for efficient vectorized operation.

    Args:
         sampled_df: The sampled results to benchmark. This is likely produced by a call to
            `sample_2q_xeb_circuits`.
        circuits: The library of circuits corresponding to the sampled results in `sampled_df`.
        cycle_depths: The sequence of cycle depths to simulate the circuits.
        param_resolver: If circuits contain parameters, resolve according to this ParamResolver
            prior to simulation
        pool: If provided, execute the simulations in parallel.

    Returns:
        A DataFrame with columns 'cycle_depth' and 'fidelity'.
    """
    simulated_df = simulate_2q_xeb_circuits(
        circuits=circuits, cycle_depths=cycle_depths, param_resolver=param_resolver, pool=pool
    )
    df = sampled_df.join(simulated_df)

    D = 4  # two qubits
    pure_probs = np.array(df['pure_probs'].to_list())
    sampled_probs = np.array(df['sampled_probs'].to_list())
    df['e_u'] = np.sum(pure_probs ** 2, axis=1)
    df['u_u'] = np.sum(pure_probs, axis=1) / D
    df['m_u'] = np.sum(pure_probs * sampled_probs, axis=1)
    df['y'] = df['m_u'] - df['u_u']
    df['x'] = df['e_u'] - df['u_u']
    df['numerator'] = df['x'] * df['y']
    df['denominator'] = df['x'] ** 2

    def per_cycle_depth(df):
        """This function is applied per cycle_depth in the following groupby aggregation."""
        fid_lsq = df['numerator'].sum() / df['denominator'].sum()
        ret = {'fidelity': fid_lsq}

        def _try_keep(k):
            """If all the values for a key `k` are the same in this group, we can keep it."""
            if k not in df.columns:
                return  # coverage: ignore
            vals = df[k].unique()
            if len(vals) == 1:
                ret[k] = vals[0]
            else:
                # coverage: ignore
                raise AssertionError(
                    f"When computing per-cycle-depth fidelity, multiple "
                    f"values for {k} were grouped together: {vals}"
                )

        _try_keep('pair')
        return pd.Series(ret)

    if 'pair_i' in df.columns:
        groupby_names = ['layer_i', 'pair_i', 'cycle_depth']
    else:
        groupby_names = ['cycle_depth']

    return df.reset_index().groupby(groupby_names).apply(per_cycle_depth).reset_index()


class XEBCharacterizationOptions(ABC):
    @staticmethod
    @abstractmethod
    def should_parameterize(op: 'cirq.Operation') -> bool:
        """Whether to replace `op` with a parameterized version."""

    @abstractmethod
    def get_parameterized_gate(self) -> 'cirq.Gate':
        """The parameterized gate to use."""

    @abstractmethod
    def get_initial_simplex_and_names(
        self, initial_simplex_step_size: float = 0.1
    ) -> Tuple[np.ndarray, List[str]]:
        """Return an initial Nelder-Mead simplex and the names for each parameter."""


# mypy issue: https://github.com/python/mypy/issues/5374
@json_serializable_dataclass(frozen=True)  # type: ignore
class XEBPhasedFSimCharacterizationOptions(XEBCharacterizationOptions):
    """Options for calibrating a PhasedFSim-like gate using XEB.

    You may want to use more specific subclasses like `SqrtISwapXEBOptions`
    which have sensible defaults.

    Attributes:
        characterize_theta: Whether to characterize θ angle.
        characterize_zeta: Whether to characterize ζ angle.
        characterize_chi: Whether to characterize χ angle.
        characterize_gamma: Whether to characterize γ angle.
        characterize_phi: Whether to characterize φ angle.
        theta_default: The initial or default value to assume for the θ angle.
        zeta_default: The initial or default value to assume for the ζ angle.
        chi_default: The initial or default value to assume for the χ angle.
        gamma_default: The initial or default value to assume for the γ angle.
        phi_default: The initial or default value to assume for the φ angle.
    """

    characterize_theta: bool = True
    characterize_zeta: bool = True
    characterize_chi: bool = True
    characterize_gamma: bool = True
    characterize_phi: bool = True

    theta_default: float = 0.0
    zeta_default: float = 0.0
    chi_default: float = 0.0
    gamma_default: float = 0.0
    phi_default: float = 0.0

    def get_initial_simplex_and_names(
        self, initial_simplex_step_size: float = 0.1
    ) -> Tuple[np.ndarray, List[str]]:
        """Get an initial simplex and parameter names for the optimization implied by these options.

        The initial simplex initiates the Nelder-Mead optimization parameter. We
        use the standard simplex of `x0 + s*basis_vec` where x0 is given by the
        `xxx_default` attributes, s is `initial_simplex_step_size` and `basis_vec`
        is a one-hot encoded vector for each parameter for which the `parameterize_xxx`
        attribute is True.

        We also return a list of parameter names so the Cirq `param_resovler`
        can be accurately constructed during optimization.
        """
        x0 = []
        names = []
        if self.characterize_theta:
            x0 += [self.theta_default]
            names += [THETA_SYMBOL.name]
        if self.characterize_zeta:
            x0 += [self.zeta_default]
            names += [ZETA_SYMBOL.name]
        if self.characterize_chi:
            x0 += [self.chi_default]
            names += [CHI_SYMBOL.name]
        if self.characterize_gamma:
            x0 += [self.gamma_default]
            names += [GAMMA_SYMBOL.name]
        if self.characterize_phi:
            x0 += [self.phi_default]
            names += [PHI_SYMBOL.name]

        x0 = np.asarray(x0)
        n_param = len(x0)
        initial_simplex = [x0]
        for i in range(n_param):
            basis_vec = np.eye(1, n_param, i)[0]
            initial_simplex += [x0 + initial_simplex_step_size * basis_vec]
        initial_simplex = np.asarray(initial_simplex)

        return initial_simplex, names

    def get_parameterized_gate(self):
        theta = THETA_SYMBOL if self.characterize_theta else self.theta_default
        zeta = ZETA_SYMBOL if self.characterize_zeta else self.zeta_default
        chi = CHI_SYMBOL if self.characterize_chi else self.chi_default
        gamma = GAMMA_SYMBOL if self.characterize_gamma else self.gamma_default
        phi = PHI_SYMBOL if self.characterize_phi else self.phi_default
        return ops.PhasedFSimGate(theta=theta, zeta=zeta, chi=chi, gamma=gamma, phi=phi)

    @staticmethod
    def should_parameterize(op: 'cirq.Operation') -> bool:
        if isinstance(op.gate, (ops.PhasedFSimGate, ops.FSimGate)):
            return True
        if op.gate == SQRT_ISWAP:
            return True
        return False


@dataclass(frozen=True)
class SqrtISwapXEBOptions(XEBPhasedFSimCharacterizationOptions):
    """Options for calibrating a sqrt(ISWAP) gate using XEB.

    As such, the default for theta is changed to -pi/4 and the parameterization
    predicate seeks out sqrt(ISWAP) gates.
    """

    theta_default: float = -np.pi / 4


def parameterize_circuit(
    circuit: 'cirq.Circuit',
    options: XEBCharacterizationOptions,
) -> 'cirq.Circuit':
    """Parameterize PhasedFSim-like gates in a given circuit according to
    `phased_fsim_options`.
    """
    gate = options.get_parameterized_gate()
    return Circuit(
        ops.Moment(
            gate.on(*op.qubits) if options.should_parameterize(op) else op
            for op in moment.operations
        )
        for moment in circuit.moments
    )


QPair_T = Tuple['cirq.Qid', 'cirq.Qid']


@dataclass(frozen=True)
class XEBCharacterizationResult:
    """The result of `characterize_phased_fsim_parameters_with_xeb`.

    Attributes:
        optimization_results: A mapping from qubit pair to the raw scipy OptimizeResult object
        final_params: A mapping from qubit pair to a dictionary of (angle_name, angle_value)
            key-value pairs
        fidelities_df: A dataframe containing per-cycle_depth and per-pair fidelities after
            fitting the characterization.
    """

    optimization_results: Dict[QPair_T, scipy.optimize.OptimizeResult]
    final_params: Dict[QPair_T, Dict[str, float]]
    fidelities_df: pd.DataFrame


def characterize_phased_fsim_parameters_with_xeb(
    sampled_df: pd.DataFrame,
    parameterized_circuits: List['cirq.Circuit'],
    cycle_depths: Sequence[int],
    options: XEBCharacterizationOptions,
    initial_simplex_step_size: float = 0.1,
    xatol: float = 1e-3,
    fatol: float = 1e-3,
    verbose: bool = True,
    pool: Optional['multiprocessing.pool.Pool'] = None,
) -> XEBCharacterizationResult:
    """Run a classical optimization to fit phased fsim parameters to experimental data, and
    thereby characterize PhasedFSim-like gates.

    Args:
        sampled_df: The DataFrame of sampled two-qubit probability distributions returned
            from `sample_2q_xeb_circuits`.
        parameterized_circuits: The circuits corresponding to those sampled in `sampled_df`,
            but with some gates parameterized, likely by using `parameterize_circuit`.
        cycle_depths: The depths at which circuits were truncated.
        options: A set of options that controls the classical optimization loop
            for characterizing the parameterized gates.
        initial_simplex_step_size: Set the size of the initial simplex for Nelder-Mead.
        xatol: The `xatol` argument for Nelder-Mead. This is the absolute error for convergence
            in the parameters.
        fatol: The `fatol` argument for Nelder-Mead. This is the absolute error for convergence
            in the function evaluation.
        verbose: Whether to print progress updates.
        pool: An optional multiprocessing pool to execute circuit simulations in parallel.
    """
    (pair,) = sampled_df['pair'].unique()
    initial_simplex, names = options.get_initial_simplex_and_names(
        initial_simplex_step_size=initial_simplex_step_size
    )
    x0 = initial_simplex[0]

    def _mean_infidelity(angles):
        params = dict(zip(names, angles))
        if verbose:
            params_str = ''
            for name, val in params.items():
                params_str += f'{name:5s} = {val:7.3g} '
            print(f"Simulating with {params_str}")
        fids = benchmark_2q_xeb_fidelities(
            sampled_df, parameterized_circuits, cycle_depths, param_resolver=params, pool=pool
        )

        loss = 1 - fids['fidelity'].mean()
        if verbose:
            print(f"Loss: {loss:7.3g}", flush=True)
        return loss

    optimization_result = scipy.optimize.minimize(
        _mean_infidelity,
        x0=x0,
        options={'initial_simplex': initial_simplex, 'xatol': xatol, 'fatol': fatol},
        method='nelder-mead',
    )

    final_params = dict(zip(names, optimization_result.x))
    fidelities_df = benchmark_2q_xeb_fidelities(
        sampled_df, parameterized_circuits, cycle_depths, param_resolver=final_params
    )
    return XEBCharacterizationResult(
        optimization_results={pair: optimization_result},
        final_params={pair: final_params},
        fidelities_df=fidelities_df,
    )


@dataclass(frozen=True)
class _CharacterizePhasedFsimParametersWithXebClosure:
    """A closure object to wrap `characterize_phased_fsim_parameters_with_xeb` for use in
    multiprocessing."""

    parameterized_circuits: List['cirq.Circuit']
    cycle_depths: Sequence[int]
    options: XEBCharacterizationOptions
    initial_simplex_step_size: float = 0.1
    xatol: float = 1e-3
    fatol: float = 1e-3

    def __call__(self, sampled_df) -> XEBCharacterizationResult:
        return characterize_phased_fsim_parameters_with_xeb(
            sampled_df=sampled_df,
            parameterized_circuits=self.parameterized_circuits,
            cycle_depths=self.cycle_depths,
            options=self.options,
            initial_simplex_step_size=self.initial_simplex_step_size,
            xatol=self.xatol,
            fatol=self.fatol,
            verbose=False,
            pool=None,
        )


def characterize_phased_fsim_parameters_with_xeb_by_pair(
    sampled_df: pd.DataFrame,
    parameterized_circuits: List['cirq.Circuit'],
    cycle_depths: Sequence[int],
    options: XEBCharacterizationOptions,
    initial_simplex_step_size: float = 0.1,
    xatol: float = 1e-3,
    fatol: float = 1e-3,
    pool: Optional['multiprocessing.pool.Pool'] = None,
) -> XEBCharacterizationResult:
    """Run a classical optimization to fit phased fsim parameters to experimental data, and
    thereby characterize PhasedFSim-like gates grouped by pairs.

    This is appropriate if you have run parallel XEB on multiple pairs of qubits.

    The optimization is done per-pair. If you have the same pair in e.g. two different
    layers the characterization optimization will lump the data together. This is in contrast
    with the benchmarking functionality, which will always index on `(layer_i, pair_i, pair)`.

    Args:
        sampled_df: The DataFrame of sampled two-qubit probability distributions returned
            from `sample_2q_xeb_circuits`.
        parameterized_circuits: The circuits corresponding to those sampled in `sampled_df`,
            but with some gates parameterized, likely by using `parameterize_circuit`.
        cycle_depths: The depths at which circuits were truncated.
        options: A set of options that controls the classical optimization loop
            for characterizing the parameterized gates.
        initial_simplex_step_size: Set the size of the initial simplex for Nelder-Mead.
        xatol: The `xatol` argument for Nelder-Mead. This is the absolute error for convergence
            in the parameters.
        fatol: The `fatol` argument for Nelder-Mead. This is the absolute error for convergence
            in the function evaluation.
        pool: An optional multiprocessing pool to execute pair optimization in parallel. Each
            optimization (and the simulations therein) runs serially.
    """
    pairs = sampled_df['pair'].unique()
    closure = _CharacterizePhasedFsimParametersWithXebClosure(
        parameterized_circuits=parameterized_circuits,
        cycle_depths=cycle_depths,
        options=options,
        initial_simplex_step_size=initial_simplex_step_size,
        xatol=xatol,
        fatol=fatol,
    )
    subselected_dfs = [sampled_df[sampled_df['pair'] == pair] for pair in pairs]
    if pool is not None:
        results = pool.map(closure, subselected_dfs)
    else:
        results = [closure(df) for df in subselected_dfs]

    optimization_results = {}
    all_final_params = {}
    fid_dfs = []
    for result in results:
        optimization_results.update(result.optimization_results)
        all_final_params.update(result.final_params)
        fid_dfs.append(result.fidelities_df)

    return XEBCharacterizationResult(
        optimization_results=optimization_results,
        final_params=all_final_params,
        fidelities_df=pd.concat(fid_dfs),
    )


def exponential_decay(cycle_depths: np.ndarray, a: float, layer_fid: float) -> np.ndarray:
    """An exponential decay for fitting.

    This computes `a * layer_fid**cycle_depths`

    Args:
        cycle_depths: The various depths at which fidelity was estimated. This is the independent
            variable in the exponential function.
        a: A scale parameter in the exponential function.
        layer_fid: The base of the exponent in the exponential function.
    """
    return a * layer_fid ** cycle_depths


def _fit_exponential_decay(
    cycle_depths: np.ndarray, fidelities: np.ndarray
) -> Tuple[float, float, float, float]:
    """Fit an exponential model fidelity = a * layer_fid**x using nonlinear least squares.

    This uses `exponential_decay` as the function to fit with parameters `a` and `layer_fid`.

    Args:
        cycle_depths: The various depths at which fidelity was estimated. Each element is `x`
            in the fit expression.
        fidelities: The estimated fidelities for each cycle depth. Each element is `fidelity`
            in the fit expression.

    Returns:
        a: The first fit parameter that scales the exponential function, perhaps accounting for
            state prep and measurement (SPAM) error.
        layer_fid: The second fit parameters which serves as the base of the exponential.
        a_std: The standard deviation of the `a` parameter estimate.
        layer_fid_std: The standard deviation of the `layer_fid` parameter estimate.
    """
    cycle_depths = np.asarray(cycle_depths)
    fidelities = np.asarray(fidelities)

    # Get initial guess by linear least squares with logarithm of model.
    # This only works for positive fidelities. We use numpy fancy indexing
    # with `positives` (an ndarray of bools).
    positives = fidelities > 0
    if np.sum(positives) <= 1:
        # The sum of the boolean array is the number of `True` entries.
        # For one or fewer positive values, we cannot perform the linear fit.
        return 0, 0, np.inf, np.inf
    cycle_depths_pos = cycle_depths[positives]
    log_fidelities = np.log(fidelities[positives])
    slope, intercept, _, _, _ = scipy.stats.linregress(cycle_depths_pos, log_fidelities)
    layer_fid_0 = np.clip(np.exp(slope), 0, 1)
    a_0 = np.clip(np.exp(intercept), 0, 1)

    try:
        (a, layer_fid), pcov = scipy.optimize.curve_fit(
            exponential_decay,
            cycle_depths,
            fidelities,
            p0=(a_0, layer_fid_0),
            bounds=((0, 0), (1, 1)),
        )
    except ValueError:  # coverage: ignore
        # coverage: ignore
        return 0, 0, np.inf, np.inf

    a_std, layer_fid_std = np.sqrt(np.diag(pcov))
    return a, layer_fid, a_std, layer_fid_std


def _one_unique(df, name, default):
    """Helper function to assert that there's one unique value in a column and return it."""
    if name not in df.columns:
        return default
    vals = df[name].unique()
    assert len(vals) == 1, name
    return vals[0]


def fit_exponential_decays(fidelities_df: pd.DataFrame) -> pd.DataFrame:
    """Fit exponential decay curves to a fidelities DataFrame.

    Args:
         fidelities_df: A DataFrame that is the result of `benchmark_2q_xeb_fidelities`. It
            may contain results for multiple pairs of qubits identified by the "pair" column.
            Each pair will be fit separately. At minimum, this dataframe must contain
            "cycle_depth", "fidelity", and "pair" columns.

    Returns:
        A new, aggregated dataframe with index given by (pair, layer_i, pair_i); columns
        for the fit parameters "a" and "layer_fid"; and nested "cycles_depths" and "fidelities"
        lists (now grouped by pair).
    """

    def _per_pair(f1):
        a, layer_fid, a_std, layer_fid_std = _fit_exponential_decay(
            f1['cycle_depth'], f1['fidelity']
        )
        record = {
            'a': a,
            'layer_fid': layer_fid,
            'cycle_depths': f1['cycle_depth'].values,
            'fidelities': f1['fidelity'].values,
            'a_std': a_std,
            'layer_fid_std': layer_fid_std,
        }
        return pd.Series(record)

    if 'layer_i' in fidelities_df.columns:
        groupby = ['layer_i', 'pair_i', 'pair']
    else:
        groupby = ['pair']
    return fidelities_df.groupby(groupby).apply(_per_pair)


def before_and_after_characterization(
    fidelities_df_0: pd.DataFrame, characterization_result: XEBCharacterizationResult
) -> pd.DataFrame:
    """A convenience function for horizontally stacking results pre- and post- characterization
    optimization.

    Args:
        fidelities_df_0: A dataframe (before fitting), likely resulting from
            `benchmark_2q_xeb_fidelities`.
        characterization_result: The result of running a characterization. This contains the
            second fidelities dataframe as well as the new parameters.

    Returns:
          A joined dataframe with original column names suffixed by "_0" and characterized
          column names suffixed by "_c".
    """
    fit_decay_df_0 = fit_exponential_decays(fidelities_df_0)
    fit_decay_df_c = fit_exponential_decays(characterization_result.fidelities_df)

    joined_df = fit_decay_df_0.join(fit_decay_df_c, how='outer', lsuffix='_0', rsuffix='_c')
    # Remove (layer_i, pair_i) from the index. While we keep this for `fit_exponential_decays`
    # so the same pair can be benchmarked in different contexts, the multi-pair characterization
    # function only keys on the pair identity. This can be seen acutely by the
    # `characterization_result.final_params` dictionary being keyed only by the pair.
    joined_df = joined_df.reset_index().set_index('pair')

    joined_df['characterized_angles'] = [
        characterization_result.final_params[pair] for pair in joined_df.index
    ]
    # Take any `final_params` (for any pair). We just need the angle names.
    fp, *_ = characterization_result.final_params.values()
    for angle_name in fp.keys():
        joined_df[angle_name] = [
            characterization_result.final_params[pair][angle_name] for pair in joined_df.index
        ]
    return joined_df
