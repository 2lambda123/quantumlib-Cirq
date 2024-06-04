# Copyright 2019 The Cirq Developers
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
"""Tests for Heatmap."""

import pathlib
import shutil
import string
from tempfile import mkdtemp

import numpy as np
import pytest

import matplotlib as mpl
import matplotlib.pyplot as plt

from cirq.devices import grid_qubit
from cirq.vis import heatmap


@pytest.fixture
def ax():
    figure = mpl.figure.Figure()
    return figure.add_subplot(111)


def test_default_ax():
    row_col_list = ((0, 5), (8, 1), (7, 0), (13, 5), (1, 6), (3, 2), (2, 8))
    test_value_map = {
        grid_qubit.GridQubit(row, col): np.random.random() for (row, col) in row_col_list
    }
    _, _ = heatmap.Heatmap(test_value_map).plot()


@pytest.mark.parametrize('tuple_keys', [True, False])
def test_cells_positions(ax, tuple_keys):
    row_col_list = ((0, 5), (8, 1), (7, 0), (13, 5), (1, 6), (3, 2), (2, 8))
    qubits = [grid_qubit.GridQubit(row, col) for (row, col) in row_col_list]
    values = np.random.random(len(qubits))
    test_value_map = {
        (qubit,) if tuple_keys else qubit: value for qubit, value in zip(qubits, values)
    }
    _, collection = heatmap.Heatmap(test_value_map).plot(ax)

    found_qubits = set()
    for path in collection.get_paths():
        vertices = path.vertices[0:4]
        row = int(round(np.mean([v[1] for v in vertices])))
        col = int(round(np.mean([v[0] for v in vertices])))
        found_qubits.add((row, col))
    assert found_qubits == set(row_col_list)


def test_two_qubit_heatmap(ax):
    value_map = {
        (grid_qubit.GridQubit(3, 2), grid_qubit.GridQubit(4, 2)): 0.004619111460557768,
        (grid_qubit.GridQubit(4, 1), grid_qubit.GridQubit(4, 2)): 0.0076079162393482835,
    }
    title = "Two Qubit Interaction Heatmap"
    heatmap.TwoQubitInteractionHeatmap(value_map, title=title).plot(ax)
    assert ax.get_title() == title
    # Test default axis
    heatmap.TwoQubitInteractionHeatmap(value_map, title=title).plot()


def test_invalid_args():
    value_map = {
        (grid_qubit.GridQubit(3, 2), grid_qubit.GridQubit(4, 2)): 0.004619111460557768,
        (grid_qubit.GridQubit(4, 1), grid_qubit.GridQubit(4, 2)): 0.0076079162393482835,
    }
    with pytest.raises(ValueError, match="invalid argument.*colormap"):
        heatmap.TwoQubitInteractionHeatmap(value_map, colormap='Greys')


def test_two_qubit_nearest_neighbor(ax):
    value_map = {
        (grid_qubit.GridQubit(3, 2), grid_qubit.GridQubit(4, 2)): 0.004619111460557768,
        (grid_qubit.GridQubit(4, 1), grid_qubit.GridQubit(3, 2)): 0.0076079162393482835,
    }
    with pytest.raises(ValueError, match="not nearest neighbors"):
        heatmap.TwoQubitInteractionHeatmap(value_map, coupler_width=0).plot(ax)


# Test colormaps are the first one in each category in
# https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html.
@pytest.mark.parametrize(
    'colormap_name', ['viridis', 'Greys', 'binary', 'PiYG', 'twilight', 'Pastel1', 'flag']
)
def test_cell_colors(ax, colormap_name):
    row_col_list = ((0, 5), (8, 1), (7, 0), (13, 5), (1, 6), (3, 2), (2, 8))
    qubits = [grid_qubit.GridQubit(row, col) for (row, col) in row_col_list]
    values = 1.0 + 2.0 * np.random.random(len(qubits))  # [1, 3)
    test_value_map = {(qubit,): value for qubit, value in zip(qubits, values)}
    test_row_col_map = {rc: value for rc, value in zip(row_col_list, values)}
    vmin, vmax = 1.5, 2.5
    random_heatmap = heatmap.Heatmap(
        test_value_map, collection_options={'cmap': colormap_name}, vmin=vmin, vmax=vmax
    )
    _, mesh = random_heatmap.plot(ax)

    colormap = mpl.colormaps[colormap_name]
    for path, facecolor in zip(mesh.get_paths(), mesh.get_facecolors()):
        vertices = path.vertices[0:4]
        row = int(round(np.mean([v[1] for v in vertices])))
        col = int(round(np.mean([v[0] for v in vertices])))
        value = test_row_col_map[(row, col)]
        color_scale = (value - vmin) / (vmax - vmin)
        color_scale = max(color_scale, 0.0)
        color_scale = min(color_scale, 1.0)
        expected_color = np.array(colormap(color_scale))
        assert np.all(np.isclose(facecolor, expected_color))


def test_default_annotation(ax):
    """Tests that the default annotation is '.2g' format on float(value)."""
    row_col_list = ((0, 5), (8, 1), (7, 0), (13, 5), (1, 6), (3, 2), (2, 8))
    qubits = [grid_qubit.GridQubit(row, col) for (row, col) in row_col_list]
    values = ['3.752', '42', '-5.27e8', '-7.34e-9', 732, 0.432, 3.9753e28]
    test_value_map = {(qubit,): value for qubit, value in zip(qubits, values)}
    test_row_col_map = {rc: value for rc, value in zip(row_col_list, values)}
    random_heatmap = heatmap.Heatmap(test_value_map)
    random_heatmap.plot(ax)
    actual_texts = set()
    for artist in ax.get_children():
        if isinstance(artist, mpl.text.Text):
            col, row = artist.get_position()
            text = artist.get_text()
            actual_texts.add(((row, col), text))
    expected_texts = set(
        (qubit, format(float(value), '.2g')) for qubit, value in test_row_col_map.items()
    )
    assert expected_texts.issubset(actual_texts)


@pytest.mark.parametrize('format_string', ['.3e', '.2f', '.4g'])
def test_annotation_position_and_content(ax, format_string):
    row_col_list = ((0, 5), (8, 1), (7, 0), (13, 5), (1, 6), (3, 2), (2, 8))
    qubits = [grid_qubit.GridQubit(row, col) for (row, col) in row_col_list]
    values = np.random.random(len(qubits))
    test_value_map = {(qubit,): value for qubit, value in zip(qubits, values)}
    test_row_col_map = {rc: value for rc, value in zip(row_col_list, values)}
    random_heatmap = heatmap.Heatmap(test_value_map, annotation_format=format_string)
    random_heatmap.plot(ax)
    actual_texts = set()
    for artist in ax.get_children():
        if isinstance(artist, mpl.text.Text):
            col, row = artist.get_position()
            text = artist.get_text()
            actual_texts.add(((row, col), text))
    expected_texts = set(
        (qubit, format(value, format_string)) for qubit, value in test_row_col_map.items()
    )
    assert expected_texts.issubset(actual_texts)


def test_annotation_map(ax):
    row_col_list = [(0, 5), (8, 1), (7, 0), (13, 5), (1, 6), (3, 2), (2, 8)]
    qubits = [grid_qubit.GridQubit(*row_col) for row_col in row_col_list]
    values = np.random.random(len(qubits))
    annos = np.random.choice([c for c in string.ascii_letters], len(qubits))
    test_value_map = {(qubit,): value for qubit, value in zip(qubits, values)}
    test_anno_map = {
        (qubit,): anno
        for qubit, row_col, anno in zip(qubits, row_col_list, annos)
        if row_col != (1, 6)
    }
    random_heatmap = heatmap.Heatmap(test_value_map, annotation_map=test_anno_map)
    random_heatmap.plot(ax)
    actual_texts = set()
    for artist in ax.get_children():
        if isinstance(artist, mpl.text.Text):
            col, row = artist.get_position()
            assert (row, col) != (1, 6)
            actual_texts.add(((row, col), artist.get_text()))
    expected_texts = set(
        (row_col, anno) for row_col, anno in zip(row_col_list, annos) if row_col != (1, 6)
    )
    assert expected_texts.issubset(actual_texts)


@pytest.mark.parametrize('format_string', ['.3e', '.2f', '.4g', 's'])
def test_non_float_values(ax, format_string):
    class Foo:
        def __init__(self, value: float, unit: str):
            self.value = value
            self.unit = unit

        def __float__(self):
            return self.value

        def __format__(self, format_string):
            if format_string == 's':
                return f'{self.value}{self.unit}'
            else:
                return format(self.value, format_string)

    row_col_list = ((0, 5), (8, 1), (7, 0), (13, 5), (1, 6), (3, 2), (2, 8))
    qubits = [grid_qubit.GridQubit(row, col) for (row, col) in row_col_list]
    values = np.random.random(len(qubits))
    units = np.random.choice([c for c in string.ascii_letters], len(qubits))
    test_value_map = {
        (qubit,): Foo(float(value), unit) for qubit, value, unit in zip(qubits, values, units)
    }
    row_col_map = {
        row_col: Foo(float(value), unit)
        for row_col, value, unit in zip(row_col_list, values, units)
    }
    colormap_name = 'viridis'
    vmin, vmax = 0.0, 1.0
    random_heatmap = heatmap.Heatmap(
        test_value_map,
        collection_options={'cmap': colormap_name},
        vmin=vmin,
        vmax=vmax,
        annotation_format=format_string,
    )

    _, mesh = random_heatmap.plot(ax)

    colormap = mpl.colormaps[colormap_name]
    for path, facecolor in zip(mesh.get_paths(), mesh.get_facecolors()):
        vertices = path.vertices[0:4]
        row = int(round(np.mean([v[1] for v in vertices])))
        col = int(round(np.mean([v[0] for v in vertices])))
        foo = row_col_map[(row, col)]
        color_scale = (foo.value - vmin) / (vmax - vmin)
        expected_color = np.array(colormap(color_scale))
        assert np.all(np.isclose(facecolor, expected_color))

    for artist in ax.get_children():
        if isinstance(artist, mpl.text.Text):
            col, row = artist.get_position()
            if (row, col) in test_value_map:
                foo = test_value_map[(row, col)]
                actual_text = artist.get_text()
                expected_text = format(foo, format_string)
                assert actual_text == expected_text


@pytest.mark.parametrize(
    'position,size,pad',
    [
        ('right', "5%", "2%"),
        ('right', "5%", "10%"),
        ('right', "20%", "2%"),
        ('right', "20%", "10%"),
        ('left', "5%", "2%"),
        ('left', "5%", "10%"),
        ('left', "20%", "2%"),
        ('left', "20%", "10%"),
        ('top', "5%", "2%"),
        ('top', "5%", "10%"),
        ('top', "20%", "2%"),
        ('top', "20%", "10%"),
        ('bottom', "5%", "2%"),
        ('bottom', "5%", "10%"),
        ('bottom', "20%", "2%"),
        ('bottom', "20%", "10%"),
    ],
)
def test_colorbar(ax, position, size, pad):
    row_col_list = ((0, 5), (8, 1), (7, 0), (13, 5), (1, 6), (3, 2), (2, 8))
    qubits = [grid_qubit.GridQubit(row, col) for (row, col) in row_col_list]
    values = np.random.random(len(qubits))
    test_value_map = {(qubit,): value for qubit, value in zip(qubits, values)}
    random_heatmap = heatmap.Heatmap(test_value_map, plot_colorbar=False)
    fig1, ax1 = plt.subplots()
    random_heatmap.plot(ax1)
    fig2, ax2 = plt.subplots()
    random_heatmap.plot(
        ax2, plot_colorbar=True, colorbar_position=position, colorbar_size=size, colorbar_pad=pad
    )

    # We need to call savefig() explicitly for updating axes position since the figure
    # object has been altered in the HeatMap._plot_colorbar function.
    tmp_dir = mkdtemp()
    fig2.savefig(pathlib.Path(tmp_dir) / 'tmp.png')

    # Check that the figure has one more object in it when colorbar is on.
    assert len(fig2.get_children()) == len(fig1.get_children()) + 1

    fig_pos = fig2.get_axes()[0].get_position()
    colorbar_pos = fig2.get_axes()[1].get_position()

    origin_axes_size = (
        fig_pos.xmax - fig_pos.xmin
        if position in ["left", "right"]
        else fig_pos.ymax - fig_pos.ymin
    )
    expected_pad = int(pad.replace("%", "")) / 100 * origin_axes_size
    expected_size = int(size.replace("%", "")) / 100 * origin_axes_size

    if position == "right":
        pad_distance = colorbar_pos.xmin - fig_pos.xmax
        colorbar_size = colorbar_pos.xmax - colorbar_pos.xmin
    elif position == "left":
        pad_distance = fig_pos.xmin - colorbar_pos.xmax
        colorbar_size = colorbar_pos.xmax - colorbar_pos.xmin
    elif position == "top":
        pad_distance = colorbar_pos.ymin - fig_pos.ymax
        colorbar_size = colorbar_pos.ymax - colorbar_pos.ymin
    elif position == "bottom":
        pad_distance = fig_pos.ymin - colorbar_pos.ymax
        colorbar_size = colorbar_pos.ymax - colorbar_pos.ymin

    assert np.isclose(colorbar_size, expected_size)
    assert np.isclose(pad_distance, expected_pad)

    plt.close(fig1)
    plt.close(fig2)
    shutil.rmtree(tmp_dir)


@pytest.mark.usefixtures('closefigures')
def test_plot_updates_local_config():
    value_map_2d = {
        (grid_qubit.GridQubit(3, 2), grid_qubit.GridQubit(4, 2)): 0.004619111460557768,
        (grid_qubit.GridQubit(4, 1), grid_qubit.GridQubit(4, 2)): 0.0076079162393482835,
    }
    value_map_1d = {
        (grid_qubit.GridQubit(3, 2),): 0.004619111460557768,
        (grid_qubit.GridQubit(4, 2),): 0.0076079162393482835,
    }
    original_title = "Two Qubit Interaction Heatmap"
    new_title = "Temporary title for the plot"
    for random_heatmap in [
        heatmap.TwoQubitInteractionHeatmap(value_map_2d, title=original_title),
        heatmap.Heatmap(value_map_1d, title=original_title),
    ]:
        _, ax = plt.subplots()
        random_heatmap.plot(ax, title=new_title)
        assert ax.get_title() == new_title
        _, ax = plt.subplots()
        random_heatmap.plot(ax)
        assert ax.get_title() == original_title





# Unit tests for new functionalities
import unittest
from unittest.mock import MagicMock
from cirq.devices import GridQubit
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Assuming Heatmap and TwoQubitInteractionHeatmap classes are defined as per your code

class TestHeatmap(unittest.TestCase):
    
    def setUp(self):
        # Create a simple value map for testing
        self.qubits = [GridQubit(row, col) for row in range(3) for col in range(3)]
        self.value_map = {q: float(row + col) for q, (row, col) in zip(self.qubits, [(q.row, q.col) for q in self.qubits])}
        self.heatmap = Heatmap(self.value_map)
    
    def test_initialization(self):
        self.assertEqual(len(self.heatmap.value_map), 9)
        self.assertTrue(all(isinstance(key, GridQubit) for key in self.heatmap.value_map.keys()))
    
    def test_set_annotation_map(self):
        annot_map = {(q.row, q.col): 'test' for q in self.qubits}
        self.heatmap.set_annotation_map(annot_map, fontsize=12, color='red')
        self.assertEqual(self.heatmap.annot_map, annot_map)
        self.assertEqual(self.heatmap.annot_kwargs, {'fontsize': 12, 'color': 'red'})
    
    def test_set_colorbar(self):
        self.heatmap.set_colorbar(position='bottom', size='10%', pad='5%')
        self.assertTrue(self.heatmap._config['plot_colorbar'])
        self.assertEqual(self.heatmap._config['colorbar_position'], 'bottom')
        self.assertEqual(self.heatmap._config['colorbar_size'], '10%')
        self.assertEqual(self.heatmap._config['colorbar_pad'], '5%')
    
    def test_plot(self):
        fig, ax = plt.subplots()
        ax, mesh, value_table = self.heatmap.plot(ax=ax)
        self.assertIsNotNone(ax)
        self.assertIsNotNone(mesh)
        self.assertIsInstance(value_table, pd.DataFrame)
        plt.close(fig)


class TestTwoQubitInteractionHeatmap(unittest.TestCase):
    
    def setUp(self):
        # Create a simple value map for testing
        self.qubits = [GridQubit(row, col) for row in range(5) for col in range(5)]
        self.value_map = {(q1, q2): float(q1.row + q1.col + q2.row + q2.col) for q1 in self.qubits for q2 in self.qubits if q1 != q2}
        self.heatmap = TwoQubitInteractionHeatmap(self.value_map)
    
    def test_initialization(self):
        self.assertEqual(len(self.heatmap.value_map), 600)
        self.assertTrue(all(isinstance(key, tuple) and len(key) == 2 for key in self.heatmap.value_map.keys()))
    
    def test_set_annotation_map(self):
        annot_map = {(q1.row, q1.col, q2.row, q2.col): 'test' for q1, q2 in self.value_map.keys()}
        self.heatmap.set_annotation_map(annot_map, fontsize=12, color='red')
        self.assertEqual(self.heatmap.annot_map, annot_map)
        self.assertEqual(self.heatmap.annot_kwargs, {'fontsize': 12, 'color': 'red'})
    
    def test_set_colorbar(self):
        self.heatmap.set_colorbar(position='bottom', size='10%', pad='5%')
        self.assertTrue(self.heatmap._config['plot_colorbar'])
        self.assertEqual(self.heatmap._config['colorbar_position'], 'bottom')
        self.assertEqual(self.heatmap._config['colorbar_size'], '10%')
        self.assertEqual(self.heatmap._config['colorbar_pad'], '5%')
    
    def test_plot(self):
        fig, ax = plt.subplots()
        ax, mesh, value_table = self.heatmap.plot(ax=ax)
        self.assertIsNotNone(ax)
        self.assertIsNotNone(mesh)
        self.assertIsInstance(value_table, pd.DataFrame)
        plt.close(fig)


if __name__ == '__main__':
    unittest.main()

