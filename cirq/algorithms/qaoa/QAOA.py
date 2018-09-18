# Cirq Quantum Approximate Optimization
#
# Fabio Sanches - QC Ware

# imports
import numpy as np
import pyswarm

# import for cirq with new functionality - change path here
# import sys
# sys.path.insert(0,'PATH')
# cirq has to come after this import

from scipy.optimize import minimize
from cirq.google import XmonSimulator, XmonMeasurementGate
from cirq.circuits import Circuit
from cirq.ops import RotXGate, RotYGate, MeasurementGate, H, Pauli, PauliString
from cirq.devices import GridQubit
# from cirq.circuits import exponentiate, expectation_value
from exponentiate import exponentiate_qubit_operator
from expectation_value import expectation_value, expectation_from_sampling
from bayes_opt import BayesianOptimization


# QAOA class
class QAOA:
    """
    A class for the quantum approximate optimization algorithm
        based on https://arxiv.org/pdf/1411.4028.pdf

    """

    def __init__(self, n_qubits, objective_function, mixing_operator='X'):
        """
        Initializes the QAOA object

        :param n_qubits: number of qubits used in the circuit
        :param objective_function: Dict[PauliString: Coefficient]
            the objective function QAOA wants to maximize
        :param mixing_operator: Dict[PauliString: Coefficient]
            default set to 'X' which sets it to pauli H on every qubit

        :return:
        """

        # QAOA details
        self.n_qubits = n_qubits
        self.objective_function = objective_function

        # setup cirq circuit and device
        self.circuit = Circuit()
        self.qubits = [GridQubit(0, i) for i in range(n_qubits)]

        # set mixing, or use standard if 'X'
        if mixing_operator == 'X':
            self.set_mixing_operator()
        else:
            self.mixing_operator = mixing_operator


    def set_objective_function(self, objective_function):
        """
        sets new objective_function

        :param objective_function: the objective function QAOA wants to maximize
        """
        self.objective_function = objective_function

    def set_mixing_operator(self, mixing_operator=None):
        """
        sets new mixing hermitian operator (B in QAOA paper) that will be
        used to construct the unitary U_B(\beta) = Exp(-i*beta*B)

        :param mixing_operator: Dict[PauliString: Coefficient]
            operator B in QAOA paper, used to create unitary by exponentiation
            default set to 'X' which sets it to pauli H on every qubit
        """

        # initialize operator dict
        self.mixing_operator = {}

        # sets it to X on every qubit
        if mixing_operator == None:
            # X on every qubit
            for i in range(self.n_qubits):
                self.mixing_operator[PauliString(
                    qubit_pauli_map={self.qubits[i]:Pauli.X})] = 1

        # sets it to argument given in function
        else:
            self.mixing_operator = mixing_operator

    def regular_tree_max_cut_graph(self, n_connections):
        """
        sets up the cost function for a regular tree graph (no loops) where
        each vertex has n_connections edges connected to it.

        :param n_connections: integer determining the number of connections
            for each vertex in the regular tree graph
        """
        z = Pauli.Z

        # Ignores constant term since it just adds a phase
        self.objective_function = dict()

        # connect 0 to 1:
        self.objective_function[PauliString(qubit_pauli_map={self.qubits[0]:z,
                                            self.qubits[1]:z})] = -1/2

        self.objective_function[()] = 1 / 2

        # connections
        # odd: (n_connections-1)*i + (4-n_connections + 2*j)
        # even: (n_connections-1)*i + 2 + 2*j
        for i in range(self.n_qubits):
            for j in range(n_connections-1):

                if i % 2 == 1:
                    odd_connection = (n_connections-1)*i + (4 -
                                                            n_connections + 2*j)
                    if odd_connection < self.n_qubits:
                        self.objective_function[PauliString(
                            qubit_pauli_map={self.qubits[i]:z,
                                            self.qubits[odd_connection]:z})] \
                            = -1/2

                        self.objective_function[()] += 1/2

                # even qubits
                if i % 2 == 0:
                    even_connection = (n_connections-1)*i + 2 + 2*j
                    if even_connection < self.n_qubits:
                        self.objective_function[PauliString(
                            qubit_pauli_map={self.qubits[i]:z,
                                             self.qubits[even_connection]:z})] \
                            = -1/2

                        self.objective_function[()] += 1 / 2

    def setup_circuit(self, p, params):

        """
        Constructs circuit to generate state |beta,gamma> U_B U_C .... |s>

        :param p: number of repetitions of the unitaries U_C and U_B used in
            the state preparation in QAOA. Since each time a unitary is applied
            we introduce a new parameter, there are 2*p total parameters we
            want to optimize
        :param params: list with values of gammas and betas, gammas
            are the entries params[0:p] and betas are params[p:2p]
        """

        # initial uniform superposition
        self.circuit.append([H.on(qb) for qb in self.qubits])

        # loop over p iterations
        for iter in range(p):
            gamma = params[iter]
            beta = params[p+iter]

            # calculates exponentiation of cost with appropriate gamma
            U_C = exponentiate_qubit_operator(time=gamma,
                                              operator=self.objective_function,
                                              trotter_steps=1)

            # appends to circuit
            self.circuit += U_C

            # calculates exponentiation of mixing operator B
            # with beta coefficient
            U_B = exponentiate_qubit_operator(time=beta,
                                              operator=self.mixing_operator,
                                              trotter_steps=1)

            # appends to circuit
            self.circuit += U_B
            # print(self.circuit)

    def run_circuit(self, params, p,
                    expectation_method = 'wavefunction',
                    min_flag = False):
        """
        Sets up circuit and returns expectation value

        :param params: list with values of gammas and betas, gammas are the
            entries params[0:p] and betas are params[p:2p]
        :param p: number of repetitions of the unitaries U_C and U_B used in
            the state preparation in QAOA. Since each time a unitary is applied
            we introduce a new parameter, there are 2*p total parameters we
            want to optimize
        :param expectation_method: determines whether expectation value
            is obtained by an inner product with the final state or
            by sampling from measurements given repeated runs from the circuit
            if sampling is desired, enter int corresponding to the number of
            samples used to get expectation value
        :param min_flag: bool that determines whether to return negative of cost

        :return: expectation value of self.objective_function in state prepared
            by circuit created using params
        """

        # clears old circuit
        self.circuit = Circuit()

        # new circuit to prepare QAOA state with appropriate params
        self.setup_circuit(p, params)

        # calculates expectation value in state according to method
        if expectation_method == 'wavefunction':
            cost = expectation_value(circuit=self.circuit,
                                     operator=self.objective_function)

        elif isinstance(expectation_method, int):
            cost = expectation_from_sampling(circuit=self.circuit,
                                             operator=self.objective_function,
                                             n_samples=expectation_method)

        else:
            raise TypeError('method must be wavefunction or an '
                            'integer representing number of samples')

        # default is maximizing objectvie function, if flag is passed,
        # multiplies it by -1
        if min_flag:
            return -1*cost

        return cost

    def optimization(self, p,
                     initial_params=None,
                     optimizer='swarm',
                     expectation_method='wavefunction'):
        """
        Main function that optimizes the parameters for QAOA

        :param p: number of repetitions of the unitaries U_C and U_B used in
            the state preparation in QAOA. Since each time a unitary is applied
            we introduce a new parameter, there are 2*p total parameters we
            want to optimize
        :param initial_params:
        :param optimizer: string that sets the optimization method used to
            obtain the parameters gamma and beta that maximize the objective
            function. Currently supports:
            swarm - swarming algorithm
            NM - Nelder-Mead
            bayesian - Bayesian optimization
        :param expectation_method: determines whether expectation value
            is obtained by an inner product with the final state or
            by sampling from measurements given repeated runs from the circuit
            if sampling is desired, enter int corresponding to the number of
            samples used to get expectation value

        :return: returns a dictionary of the solution found using the given
            optimization method
            keys:
            cost - final value of the objective function we are maximizing
            gammas - list containing the p optimal gammas
            betas - list containing the p  optimal gammas
        """

        # initialize solution dict
        solution = {}

        if optimizer == 'swarm':

            # lower and upper bounds for parameters in swarming optimization
            lower_bound = np.zeros(2 * p)
            upper_bound = np.concatenate((np.ones(p) * (2 * np.pi),
                                          np.ones(p) * np.pi))

            # flag needed since pyswarm finds min
            min_flag = True

            # calls swarming algo
            xopt, fopt = pyswarm.pso(self.run_circuit, lower_bound, upper_bound,
                                     f_ieqcons=None,
                                     args=(p, expectation_method, min_flag),
                                     swarmsize=20)

            # constructs solution dict
            solution['cost'] = -1*fopt
            solution['gammas'] = xopt[:p]
            solution['betas'] = xopt[p:]

            return solution

        elif optimizer == 'NM':

            # initial parameters in optimization
            if initial_params == None:
                initial_gammas = np.random.random(p) * 2 * np.pi
                initial_betas = np.random.random(p) * np.pi
                initial_params = np.concatenate((initial_gammas, initial_betas))

            # flag needed since scipy.optimize.minimize finds min
            min_flag = True

            # call optimization routine
            result = minimize(fun=self.run_circuit,
                              x0=initial_params,
                              args=(p, expectation_method, min_flag),
                              method='Nelder-Mead')

            # constructs solution dict
            solution['cost'] = -1*result.fun
            solution['gammas'] = result.x[:p]
            solution['betas'] = result.x[p:]

            return solution

        elif optimizer == 'bayesian':

            # helper function to unpack parameters
            def bayesian_run_custom(pval = p,
                                    expectation = expectation_method,
                                    **kwargs):

                p = pval
                params = [kwargs['gamma_{}'.format(m)] for m in range(p)]
                expectation_method = expectation
                # print(params)
                for i in range(p):
                    params.append(kwargs['beta_{}'.format(i)])

                return self.run_circuit(params, p,
                                        expectation_method=expectation_method,
                                        min_flag=False)

            # parameter dict needed for bayesian optimization
            args_dict = dict()
            # args_dict['p'] = p

            # set up bounds for gammas and betas
            for i in range(p):
                args_dict['gamma_{}'.format(i)] = (0, 2*np.pi)
                args_dict['beta_{}'.format(i)] = (0, np.pi)

            # initialize the optimizer
            boptimizer = BayesianOptimization(bayesian_run_custom, args_dict)

            # call maximization method
            boptimizer.maximize()

            # constructs solution dict
            solution['cost'] = boptimizer.Y.max()
            solution['gammas'] = boptimizer.X[:, :p]
            solution['betas'] = boptimizer.X[:, p:]

            return solution

        else:
            raise TypeError('Optimizer not supported')

