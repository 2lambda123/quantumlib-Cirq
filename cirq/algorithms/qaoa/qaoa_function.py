# Cirq Quantum Approximate Optimization
#
# Fabio Sanches

# imports
import typing
import numpy as np
import QAOA

from typing import Union

def qaoa_solver(n_qubits,
                objective_function,
                optimization_method,
                p,
                mixing = 'X', expectation_method = 'wavefunction'):
    """
    QAOA solver helper function

    :param n_qubits: number of qubits
    :param objective_function: objective function to be optimized
        type should be Dict[PauliString: float]
    :param optimization_method: type of optimizer used, currently available are
        swarm, nelder-mead, bayesian
    :param p: number of gamma and beta parameters/number of repeated
        applications of unitaries from QAOA paper
    :param mixing: mixing operator 'B' in QAOA paper. If standard 'X' on every
        qubit, set to 'X', otherwise specify with type Dict[PauliString: float]

    :return: dict with solution and gamma and beta values for optimal solution
    """

    qaoa = QAOA.QAOA(n_qubits=n_qubits,
                objective_function=objective_function,
                mixing_operator=mixing)

    optimzation_dict = {'swarm': 'swarm',
                        'nelder-mead': 'NM',
                        'bayesian': 'bayesian'}

    return qaoa.optimization(p=p, initial_params=None,
                             optimizer=optimzation_dict[optimization_method],
                             expectation_method=expectation_method)


def qaoa_regular_graph(n_qubits: int,
                       n_connections: int,
                       p: int, optimization_method: str,
                       expectation_method: Union[str, int] = 'wavefunction'):
    """
    Runs QAOA on a regular n_connections graph

    :param n_qubits: number of qubits
    :param n_connections: number of connections for each vertex on regular graph
    :param p: number of gamma and beta parameters/number of repeated
        applications of unitaries from QAOA paper
    :param optimization_method: type of optimizer used, currently available are
        swarm, nelder-mead, bayesian
    :param expectation_method: whether objective function is calculated using
        the final state on the simulator or sampling by measurement
        set to 'wavefunction' for final state
        set to an integer for sampling, integer corresponds to number of samples

    :return: dict with solution and gamma and beta values for optimal solution
    """

    qaoa = QAOA.QAOA(n_qubits=n_qubits,
                objective_function=None)

    qaoa.regular_tree_max_cut_graph(n_connections)
    optimzation_dict = {'swarm':'swarm',
                        'nelder-mead':'NM',
                        'bayesian':'bayesian'}

    return qaoa.optimization(p=p,
                             initial_params=None,
                             optimizer=optimzation_dict[optimization_method],
                             expectation_method=expectation_method)

