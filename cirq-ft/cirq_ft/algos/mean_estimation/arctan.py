# Copyright 2023 The Cirq Developers
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

from typing import Iterable, Sequence, Union

import attr
from fixedpoint import FixedPoint
import cirq
import bitstring
import numpy as np
from cirq_ft import infra


@attr.frozen
class ArcTan(cirq.ArithmeticGate):
    r"""Applies U|x>|0>|0000...0> = |x>|sign>|abs(-2 arctan(x) / pi)>.

    Args:
        selection_bitsize: The bitsize of input register |x>.
        target_bitsize: The bitsize of output register. The computed quantity,
            $\abs(-2 * \arctan(x) / \pi)$ is stored as a fixed-length binary approximation
            in the output register of size `target_bitsize`.
    """

    selection_bitsize_before_decimal: int
    selection_bitsize_after_decimal: int
    target_bitsize: int

    def selection_bitsize(self):
        return self.selection_bitsize_before_decimal + self.selection_bitsize_after_decimal

    def registers(self) -> Sequence[Union[int, Sequence[int]]]:
        return (2,) * self.selection_bitsize(), (2,), (2,) * self.target_bitsize

    def with_registers(self, *new_registers: Union[int, Sequence[int]]) -> "ArcTan":
        raise NotImplementedError()

    def apply(self, *register_values: int) -> Union[int, Iterable[int]]:
        input_val, target_sign, target_val = register_values
        # Convert the binary representation to a float
        input_val_float = float(
            FixedPoint(
                f"0b_{bitstring.BitArray(uint=input_val, length=self.selection_bitsize()).bin}",
                signed=False,
                m=self.selection_bitsize_before_decimal,
                n=self.selection_bitsize_after_decimal,
                str_base=2,
            )
        )
        output_val = -2 * np.arctan(input_val_float, dtype=np.double) / np.pi
        assert -1 <= output_val <= 1
        output_sign, output_bin = infra.bit_tools.float_as_fixed_width_int(
            output_val, 1 + self.target_bitsize
        )
        return input_val, target_sign ^ output_sign, target_val ^ output_bin

    def _t_complexity_(self) -> infra.TComplexity:
        # Approximate T-complexity of O(target_bitsize)
        return infra.TComplexity(t=self.target_bitsize)

    def __pow__(self, power) -> 'ArcTan':
        if power in [+1, -1]:
            return self
        raise NotImplementedError("__pow__ is only implemented for +1/-1.")  # coverage: ignore
