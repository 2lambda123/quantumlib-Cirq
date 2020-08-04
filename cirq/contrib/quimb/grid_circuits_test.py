import networkx as nx
import numpy as np
import pytest
import quimb.tensor as qtn

import cirq
import cirq.contrib.quimb as ccq


def _get_circuit(width=3, height=None, rs=None, p=2):
    if height is None:
        height = width

    if rs is None:
        rs = np.random.RandomState(52)

    graph = nx.grid_2d_graph(width, height)
    nx.set_edge_attributes(
        graph,
        name='weight',
        values={e: np.round(rs.uniform(), 2) for e in graph.edges})
    qubits = [cirq.GridQubit(*n) for n in graph]
    circuit = cirq.Circuit(cirq.H.on_each(qubits),
                           [(ccq.get_grid_moments(graph),
                             cirq.Moment([cirq.rx(0.456).on_each(qubits)]))
                            for _ in range(p)])
    return circuit, qubits


def test_simplify_sandwich():
    rs = np.random.RandomState(52)
    for width in [2, 3]:
        for height in [1, 3]:
            for p in [1, 2]:
                circuit, qubits = _get_circuit(width=width,
                                               height=height,
                                               p=p,
                                               rs=rs)
                operator = cirq.PauliString({
                    q: cirq.Z for q in rs.choice(qubits, size=2, replace=False)
                })
                tot_c = ccq.circuit_for_expectation_value(circuit, operator)
                tot_c_init = tot_c.copy()
                ccq.simplify_expectation_value_circuit(tot_c)
                assert len(list(tot_c.all_operations())) < len(
                    list(tot_c_init.all_operations()))
                np.testing.assert_allclose(
                    tot_c.unitary(qubit_order=qubits),
                    tot_c_init.unitary(qubit_order=qubits),
                    atol=1e-5)


@pytest.mark.parametrize('simplify', [False, True])
def test_circuit_to_tensors(simplify):
    rs = np.random.RandomState(52)
    qubits = cirq.LineQubit.range(5)
    circuit = cirq.testing.random_circuit(qubits=qubits,
                                          n_moments=10,
                                          op_density=0.8)
    operator = cirq.PauliString(
        {q: cirq.Z for q in rs.choice(qubits, size=2, replace=False)})

    circuit_sand = ccq.circuit_for_expectation_value(circuit, operator)
    if simplify:
        ccq.simplify_expectation_value_circuit(circuit_sand)
    qubits = sorted(circuit_sand.all_qubits())
    tensors, _, _ = ccq.circuit_to_tensors(circuit=circuit_sand,
                                           qubits=qubits,
                                           initial_state=None)
    tn = qtn.TensorNetwork(tensors)
    u_tn = tn.contract()
    # Important! Re-order indices. Rows index output legs, cols index input
    # legs. however, within the {input, output} block,
    # qubits are ordered lexicographically
    inds = u_tn.inds
    desired_inds = inds[len(inds) // 2:] + inds[:len(inds) // 2]
    u_tn.transpose(*desired_inds, inplace=True)
    u_tn = u_tn.data.reshape((2 ** len(qubits), 2 ** len(qubits)))
    u_cirq = cirq.unitary(circuit_sand)
    # print()
    # print(np.round(u_tn, 3))
    # print()
    # print(np.round(u_cirq, 3))
    # print()
    np.testing.assert_allclose(u_tn, u_cirq, atol=1e-6)


def test_tensor_expectation_value():
    for _ in range(10):
        for width in [2, 3]:
            for height in [1, 3]:
                for p in [1, 2]:
                    # print(_, width, height, p)
                    rs = np.random.RandomState(52)
                    circuit, qubits = _get_circuit(width=width,
                                                   height=height,
                                                   p=p,
                                                   rs=rs)
                    operator = cirq.PauliString(
                        {
                            q: cirq.Z
                            for q in rs.choice(qubits, size=2, replace=False)
                        },
                        coefficient=rs.uniform(-1, 1))

                    eval_tn = ccq.tensor_expectation_value(circuit, operator)

                    wfn = cirq.Simulator().simulate(circuit)
                    eval_normal = operator.expectation_from_wavefunction(
                        wfn.final_state, wfn.qubit_map)
                    assert eval_normal.imag < 1e-6
                    eval_normal = eval_normal.real
                    np.testing.assert_allclose(eval_tn, eval_normal, atol=1e-3)
