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
import itertools
from typing import Iterable
from unittest.mock import MagicMock

import cirq
import cirq_google as cg
import networkx as nx
import pytest
from cirq_google import (
    draw_gridlike,
    LineTopology,
    TiltedSquareLattice,
    get_placements,
    draw_placements,
)


@pytest.mark.parametrize('width, height', list(itertools.product([1, 2, 3, 24], repeat=2)))
def test_tilted_square_lattice(width, height):
    topo = TiltedSquareLattice(width, height)
    assert topo.graph.number_of_edges() == width * height
    assert all(1 <= topo.graph.degree[node] <= 4 for node in topo.graph.nodes)
    assert topo.name == f'tilted-square-lattice-{width}-{height}'
    assert topo.n_nodes == topo.graph.number_of_nodes()
    assert nx.is_connected(topo.graph)
    assert nx.algorithms.planarity.check_planarity(topo.graph)


def test_bad_tilted_square_lattice():
    with pytest.raises(ValueError):
        _ = TiltedSquareLattice(0, 3)
    with pytest.raises(ValueError):
        _ = TiltedSquareLattice(3, 0)


def test_tilted_square_methods():
    topo = TiltedSquareLattice(5, 5)
    ax = MagicMock()
    topo.draw(ax=ax)
    ax.scatter.assert_called()

    qubits = topo.nodes_as_gridqubits()
    assert all(isinstance(q, cirq.GridQubit) for q in qubits)


def test_tilted_square_lattice_n_nodes():
    for width, height in itertools.product(list(range(1, 4 + 1)), repeat=2):
        topo = TiltedSquareLattice(width, height)
        assert topo.n_nodes == topo.graph.number_of_nodes()


def test_line_topology():
    n = 10
    topo = LineTopology(n)
    assert topo.n_nodes == n
    assert topo.n_nodes == topo.graph.number_of_nodes()
    assert all(1 <= topo.graph.degree[node] <= 2 for node in topo.graph.nodes)
    assert topo.name == 'line-10'

    ax = MagicMock()
    topo.draw(ax=ax)
    ax.scatter.assert_called()

    with pytest.raises(ValueError, match='greater than 1.*'):
        _ = LineTopology(1)
    assert LineTopology(2).n_nodes == 2
    assert LineTopology(2).graph.number_of_nodes() == 2


@pytest.mark.parametrize('tilted', [True, False])
def test_draw_gridlike(tilted):
    graph = nx.grid_2d_graph(3, 3)
    ax = MagicMock()
    pos = draw_gridlike(graph, tilted=tilted, ax=ax)
    ax.scatter.assert_called()
    for (row, column), _ in pos.items():
        assert 0 <= row < 3
        assert 0 <= column < 3


def _gridqubits_to_graph_device(qubits: Iterable[cirq.GridQubit]):
    # cirq contrib routing --> gridqubits_to_graph_device
    def _manhattan_distance(qubit1: cirq.GridQubit, qubit2: cirq.GridQubit) -> int:
        return abs(qubit1.row - qubit2.row) + abs(qubit1.col - qubit2.col)

    return nx.Graph(
        pair for pair in itertools.combinations(qubits, 2) if _manhattan_distance(*pair) == 1
    )


def test_get_placements():
    topo = TiltedSquareLattice(4, 2)
    syc23 = _gridqubits_to_graph_device(cg.Sycamore23.qubits)
    placements = get_placements(syc23, topo.graph)
    assert len(placements) == 12

    axes = [MagicMock() for _ in range(4)]
    draw_placements(syc23, topo.graph, placements[::3], axes=axes)
    for ax in axes:
        ax.scatter.assert_called()
