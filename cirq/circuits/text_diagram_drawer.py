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

import collections
from typing import (
        Any, Callable, Dict, Iterable, List, Mapping,
        NamedTuple, Optional, Sequence, Tuple, TYPE_CHECKING)

if TYPE_CHECKING:
    # pylint: disable=unused-import
    from typing import Tuple, DefaultDict, Dict, Optional

_HorizontalLine = NamedTuple('HorizontalLine', [
    ('y', int),
    ('x1', int),
    ('x2', int),
    ('emphasize', bool),
])
_VerticalLine = NamedTuple('VerticalLine', [
    ('x', int),
    ('y1', int),
    ('y2', int),
    ('emphasize', bool),
])
_DiagramText = NamedTuple('DiagramText', [
    ('text', str),
    ('transposed_text', str),
])


class TextDiagramDrawer:
    """A utility class for creating simple text diagrams.
    """

    def __init__(self,
                 entries: Optional[Mapping[Tuple[int, int],
                                           _DiagramText]] = None,
                 horizontal_lines: Optional[Iterable[_HorizontalLine]] = None,
                 vertical_lines: Optional[Iterable[_VerticalLine]] = None,
                 horizontal_padding : Optional[Mapping[int, int]] = None,
                 vertical_padding: Optional[Mapping[int, int]] = None
                 ) -> None:
        self.entries = (dict() if entries is None else dict(entries)
                ) # type: Dict[Tuple[int, int], _DiagramText]
        self.horizontal_lines = ([] if horizontal_lines is None
                else list(horizontal_lines)) # type: List[_HorizontalLine]
        self.vertical_lines = ([] if vertical_lines is None
                else list(vertical_lines)) # type: List[_VerticalLine]
        self.horizontal_padding = (dict() if horizontal_padding is None
                else dict(horizontal_padding)) # type: Dict[int, int]
        self.vertical_padding = (dict() if vertical_padding is None
                else dict(vertical_padding)) # type: Dict[int, int]

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        attrs = ('entries', 'horizontal_lines', 'vertical_lines',
                 'horizontal_padding', 'vertical_padding')
        return all(getattr(self, attr) ==
                   getattr(other, attr) for attr in attrs)

    def write(self, x: int, y: int, text: str, transposed_text: str = None):
        """Adds text to the given location.

        Args:
            x: The column in which to write the text.
            y: The row in which to write the text.
            text: The text to write at location (x, y).
            transposted_text: Optional text to write instead, if the text
                diagram is transposed.
        """
        entry = self.entries.get((x, y), _DiagramText('', ''))
        self.entries[(x, y)] = _DiagramText(
            entry.text + text,
            entry.transposed_text + (transposed_text if transposed_text
                                                     else text))

    def content_present(self, x: int, y: int) -> bool:
        """Determines if a line or printed text is at the given location."""

        # Text?
        if (x, y) in self.entries:
            return True

        # Vertical line?
        if any(v.x == x and v.y1 < y < v.y2 for v in self.vertical_lines):
            return True

        # Horizontal line?
        if any(line_y == y and x1 < x < x2
               for line_y, x1, x2, _ in self.horizontal_lines):
            return True

        return False

    def grid_line(self, x1: int, y1: int, x2: int, y2: int,
                  emphasize: bool = False):
        """Adds a vertical or horizontal line from (x1, y1) to (x2, y2).

        Horizontal line is selected on equality in the second coordinate and
        vertical line is selected on equality in the first coordinate.

        Raises:
            ValueError: If line is neither horizontal nor vertical.
        """
        if x1 == x2:
            self.vertical_line(x1, y1, y2, emphasize)
        elif y1 == y2:
            self.horizontal_line(y1, x1, x2, emphasize)
        else:
            raise ValueError("Line is neither horizontal nor vertical")

    def vertical_line(self, x: int, y1: int, y2: int, emphasize: bool = False
                      ) -> None:
        """Adds a line from (x, y1) to (x, y2)."""
        y1, y2 = sorted([y1, y2])
        self.vertical_lines.append(_VerticalLine(x, y1, y2, emphasize))

    def horizontal_line(self, y: int, x1: int, x2: int, emphasize: bool = False
                        ) -> None:
        """Adds a line from (x1, y) to (x2, y)."""
        x1, x2 = sorted([x1, x2])
        self.horizontal_lines.append(_HorizontalLine(y, x1, x2, emphasize))

    def transpose(self) -> 'TextDiagramDrawer':
        """Returns the same diagram, but mirrored across its diagonal."""
        out = TextDiagramDrawer()
        out.entries = {(y, x): _DiagramText(v.transposed_text, v.text)
                       for (x, y), v in self.entries.items()}
        out.vertical_lines = [_VerticalLine(*e)
                              for e in self.horizontal_lines]
        out.horizontal_lines = [_HorizontalLine(*e)
                                for e in self.vertical_lines]
        out.vertical_padding = self.horizontal_padding.copy()
        out.horizontal_padding = self.vertical_padding.copy()
        return out

    def width(self) -> int:
        """Determines how many entry columns are in the diagram."""
        max_x = -1
        for x, _ in self.entries.keys():
            max_x = max(max_x, x)
        for v in self.vertical_lines:
            max_x = max(max_x, v.x)
        for h in self.horizontal_lines:
            max_x = max(max_x, h.x1, h.x2)
        return 1 + max_x

    def height(self) -> int:
        """Determines how many entry rows are in the diagram."""
        max_y = -1
        for _, y in self.entries.keys():
            max_y = max(max_y, y)
        for h in self.horizontal_lines:
            max_y = max(max_y, h.y)
        for v in self.vertical_lines:
            max_y = max(max_y, v.y1, v.y2)
        return 1 + max_y

    def force_horizontal_padding_after(self, index: int, padding: int) -> None:
        """Change the padding after the given column."""
        self.horizontal_padding[index] = padding

    def force_vertical_padding_after(self, index: int, padding: int) -> None:
        """Change the padding after the given row."""
        self.vertical_padding[index] = padding

    def _transform_coordinates(
        self, func: Callable[[int, int], Tuple[int, int]]) -> None:
        """Helper method to transformer either row or column coordinates."""
        def func_x(x: int) -> int:
            return func(x, 0)[0]
        def func_y(y: int) -> int:
            return func(0, y)[1]
        self.entries = {func(x, y): v for (x, y), v in self.entries.items()}
        self.vertical_lines = [
            _VerticalLine(func_x(x), func_y(y1), func_y(y2), emph)
            for x, y1, y2, emph in self.vertical_lines]
        self.horizontal_lines = [
            _HorizontalLine(func_y(y), func_x(x1), func_x(x2), emph)
            for y, x1, x2, emph in self.horizontal_lines]
        self.horizontal_padding = {func_x(x): padding
            for x, padding in self.horizontal_padding.items()}
        self.vertical_padding = {func_y(y): padding
            for y, padding in self.vertical_padding.items()}

    def insert_empty_columns(self, x: int, amount: int = 1) -> None:
        """Insert a number of columns after the given column."""
        def transform_columns(column: int, row: int) -> Tuple[int, int]:
            return column + (amount if column >= x else 0), row
        self._transform_coordinates(transform_columns)

    def insert_empty_rows(self, y: int, amount: int = 1) -> None:
        """Insert a number of rows after the given row."""
        def transform_rows(column: int, row: int) -> Tuple[int, int]:
            return column, row + (amount if row >= y else 0)
        self._transform_coordinates(transform_rows)

    def render(self,
               horizontal_spacing: int = 1,
               vertical_spacing: int = 1,
               crossing_char: str = None,
               use_unicode_characters: bool = True) -> str:
        """Outputs text containing the diagram."""

        char = _normal_char if use_unicode_characters else _ascii_char

        w = self.width()
        h = self.height()

        grid = [[''] * w for _ in range(h)]
        horizontal_separator = [[' '] * w for _ in range(h)]
        vertical_separator = [[' '] * w for _ in range(h)]

        # Place lines.
        verticals = {
            (v.x, y): v.emphasize
            for v in self.vertical_lines
            for y in range(v.y1, v.y2)
        }
        horizontals = {
            (x, h.y): h.emphasize
            for h in self.horizontal_lines
            for x in range(h.x1, h.x2)
        }
        for (x, y), emph in verticals.items():
            c = char('│', emph)
            grid[y][x] = c
            vertical_separator[y][x] = c
        for (x, y), emph in horizontals.items():
            c = char('─', emph)
            grid[y][x] = c
            horizontal_separator[y][x] = c
        for x, y in set(horizontals.keys()) & set(verticals.keys()):
            grid[y][x] = crossing_char or _cross_char(
                not use_unicode_characters,
                horizontals[(x, y)],
                verticals[(x, y)])

        # Place entries.
        for (x, y), v in self.entries.items():
            grid[y][x] = v.text

        # Pad rows and columns to fit contents with desired spacing.
        multiline_grid = _pad_into_multiline(w,
                                             grid,
                                             horizontal_separator,
                                             vertical_separator,
                                             horizontal_spacing,
                                             vertical_spacing,
                                             self.horizontal_padding,
                                             self.vertical_padding)

        # Concatenate it all together.
        return '\n'.join(''.join(sub_row).rstrip()
                         for row in multiline_grid
                         for sub_row in row).rstrip()

    def copy(self):
        return self.__class__(
                entries=self.entries,
                vertical_lines=self.vertical_lines,
                horizontal_lines=self.horizontal_lines,
                vertical_padding=self.vertical_padding,
                horizontal_padding=self.horizontal_padding)

    def shift(self, dx: int = 0, dy: int = 0) -> 'TextDiagramDrawer':
        self._transform_coordinates(lambda x, y: (x + dx, y + dy))
        return self

    def shifted(self, dx: int = 0, dy: int = 0) -> 'TextDiagramDrawer':
        return self.copy().shift(dx, dy)

    def update(self, other: 'TextDiagramDrawer') -> 'TextDiagramDrawer':
        self.entries.update(other.entries)
        self.horizontal_lines += other.horizontal_lines
        self.vertical_lines += other.vertical_lines
        self.horizontal_padding.update(other.horizontal_padding)
        self.vertical_padding.update(other.vertical_padding)
        return self

    @classmethod
    def vstack(cls,
               diagrams: Iterable['TextDiagramDrawer'],
               padding_resolver: Optional[Callable[[Sequence[int]], int]] = None
               ):
        """Vertically stack text diagrams.

        Args:
            diagrams: The diagrams to stack, ordered from bottom to top.
            padding_resolver: A function that takes a list of paddings
                specified for a column and returns the padding to use in the
                stacked diagram. If None, defaults to raising ValueError if the
                diagrams to stack contain inconsistent padding in any column,
                including if some specify a padding and others don't.

        Raises:
            ValueError: Inconsistent padding cannot be resolved.

        Returns:
            The vertically stacked diagram.
        """

        if padding_resolver is None:
            padding_resolver = _same_element_or_throw_error

        stacked = cls()
        dy = 0
        horizontal_paddings = collections.defaultdict(
                list) # type: DefaultDict[int, List[int]]
        for diagram in diagrams:
            stacked.update(diagram.shifted(dy=dy))
            for x, p in diagram.horizontal_padding.items():
                horizontal_paddings[x].append(p)
            dy += diagram.height()
        for x, P in horizontal_paddings.items():
            padding = padding_resolver(P)
            if padding is not None:
                stacked.horizontal_padding[x] = padding
        return stacked

    @classmethod
    def hstack(cls,
               diagrams: Iterable['TextDiagramDrawer'],
               padding_resolver:Optional[Callable[[Sequence[int]], int]] = None
               ):
        """Horizontally stack text diagrams.

        Args:
            diagrams: The diagrams to stack, ordered from left to right.
            padding_resolver: A function that takes a list of paddings
                specified for a row and returns the padding to use in the
                stacked diagram. Defaults to raising ValueError if the diagrams
                to stack contain inconsistent padding in any row, including
                if some specify a padding and others don't.

        Raises:
            ValueError: Inconsistent padding cannot be resolved.

        Returns:
            The horizontally stacked diagram.
        """

        if padding_resolver is None:
            padding_resolver = _same_element_or_throw_error
        stacked = cls()
        dx = 0
        vertical_paddings = collections.defaultdict(
                list) # type: DefaultDict[int, List[int]]
        for diagram in diagrams:
            stacked.update(diagram.shifted(dx=dx))
            for y, p in diagram.vertical_padding.items():
                vertical_paddings[y].append(p)
            dx += diagram.width()
        for y, P in vertical_paddings.items():
            padding = padding_resolver(P)
            if padding is not None:
                stacked.vertical_padding[y] = padding
        return stacked


_BoxChars = [
    ('─', '━', '-'),
    ('│', '┃', '|'),
    ('┌', '┏', '/'),
    ('└', '┗', '\\'),
    ('┐', '┓', '\\'),
    ('┘', '┛', '/'),
    ('├', '┣', '>'),
    ('┼', '╋', '+'),
    ('┤', '┫', '<'),
    ('┬', '┳', 'v'),
    ('┴', '┻', '^'),
]  # type: List[Tuple[str, ...]]

_EmphasisMap = {k: v for k, v, _ in _BoxChars}
_AsciiMap = {k: v for k, _, v in _BoxChars}


def _normal_char(k: str, emphasize: bool = False) -> str:
    return _EmphasisMap.get(k, k) if emphasize else k


def _ascii_char(k: str, emphasize: bool = False) -> str:
    del emphasize
    return _AsciiMap.get(k, k)


def _cross_char(use_ascii: bool, horizontal_emph: bool, vertical_emph: bool
                ) -> str:
    if use_ascii:
        return '+'
    if horizontal_emph != vertical_emph:
        return '┿' if horizontal_emph else '╂'
    return _normal_char('┼', horizontal_emph)


def _pad_into_multiline(width: int,
                        grid: List[List[str]],
                        horizontal_separator: List[List[str]],
                        vertical_separator: List[List[str]],
                        horizontal_spacing: int,
                        vertical_spacing: int,
                        horizontal_padding: Dict[int, int],
                        vertical_padding: Dict[int, int]
                        ) -> List[List[List[str]]]:
    multiline_grid = []  # type: List[List[List[str]]]

    # Vertical padding.
    for row in range(len(grid)):
        multiline_cells = [cell.split('\n') for cell in grid[row]]
        row_height = max(1, max(len(cell) for cell in multiline_cells))
        row_height += vertical_padding.get(row, vertical_spacing)

        multiline_row = []
        for sub_row in range(row_height):
            sub_row_cells = []
            for col in range(width):
                cell_lines = multiline_cells[col]
                sub_row_cells.append(cell_lines[sub_row]
                                     if sub_row < len(cell_lines)
                                     else vertical_separator[row][col])
            multiline_row.append(sub_row_cells)

        multiline_grid.append(multiline_row)

    # Horizontal padding.
    for col in range(width):
        col_width = max(1, max(len(sub_row[col])
                               for row in multiline_grid
                               for sub_row in row))
        col_width += horizontal_padding.get(col, horizontal_spacing)
        for row in range(len(multiline_grid)):
            for sub_row in range(len(multiline_grid[row])):
                sub_row_contents = multiline_grid[row][sub_row]
                pad_char = (horizontal_separator[row][col]
                            if sub_row == 0
                            else ' ')
                sub_row_contents[col] = sub_row_contents[col].ljust(
                    col_width, pad_char)

    return multiline_grid

def _same_element_or_throw_error(elements: Sequence[Any]):
    """Extract an element or throw an error.

    Args:
        elements: A sequence of something.

    copies of it. Returns None on an empty sequence.

    Raises:
        ValueError: The sequence constai

    Returns:
        The element when given a sequence containing only multiple copies of a
        single element. None if elements is empty.
    """
    unique_elements = set(elements)
    if len(unique_elements) > 1:
        raise ValueError('len(set({})) > 1'.format(elements))
    return unique_elements.pop() if elements else None
