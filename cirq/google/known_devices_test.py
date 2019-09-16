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

from cirq.google import known_devices
from cirq.devices import GridQubit


def test_foxtail_qubits():
    expected_qubits = []
    for i in range(0, 2):
        for j in range(0, 11):
            expected_qubits.append(GridQubit(i, j))
    assert set(expected_qubits) == known_devices.Foxtail.qubits


def test_foxtail_device_proto():
    assert str(known_devices.FOXTAIL_PROTO) == """valid_gate_sets {
  name: "xmon"
  valid_gates {
    id: "exp_w"
    gate_duration_picos: 20000
    valid_targets: "grid"
  }
  valid_gates {
    id: "exp_z"
    valid_targets: "grid"
  }
  valid_gates {
    id: "exp_11"
    gate_duration_picos: 50000
    valid_targets: "grid"
  }
  valid_gates {
    id: "meas"
    gate_duration_picos: 1000000
    valid_targets: "grid"
  }
}
valid_qubits: "0_0"
valid_qubits: "0_1"
valid_qubits: "0_2"
valid_qubits: "0_3"
valid_qubits: "0_4"
valid_qubits: "0_5"
valid_qubits: "0_6"
valid_qubits: "0_7"
valid_qubits: "0_8"
valid_qubits: "0_9"
valid_qubits: "0_10"
valid_qubits: "1_0"
valid_qubits: "1_1"
valid_qubits: "1_2"
valid_qubits: "1_3"
valid_qubits: "1_4"
valid_qubits: "1_5"
valid_qubits: "1_6"
valid_qubits: "1_7"
valid_qubits: "1_8"
valid_qubits: "1_9"
valid_qubits: "1_10"
valid_targets {
  name: "grid"
  target_ordering: SYMMETRIC
  targets {
    ids: "0_0"
    ids: "0_1"
  }
  targets {
    ids: "0_0"
    ids: "1_0"
  }
  targets {
    ids: "0_1"
    ids: "0_2"
  }
  targets {
    ids: "0_1"
    ids: "1_1"
  }
  targets {
    ids: "0_2"
    ids: "0_3"
  }
  targets {
    ids: "0_2"
    ids: "1_2"
  }
  targets {
    ids: "0_3"
    ids: "0_4"
  }
  targets {
    ids: "0_3"
    ids: "1_3"
  }
  targets {
    ids: "0_4"
    ids: "0_5"
  }
  targets {
    ids: "0_4"
    ids: "1_4"
  }
  targets {
    ids: "0_5"
    ids: "0_6"
  }
  targets {
    ids: "0_5"
    ids: "1_5"
  }
  targets {
    ids: "0_6"
    ids: "0_7"
  }
  targets {
    ids: "0_6"
    ids: "1_6"
  }
  targets {
    ids: "0_7"
    ids: "0_8"
  }
  targets {
    ids: "0_7"
    ids: "1_7"
  }
  targets {
    ids: "0_8"
    ids: "0_9"
  }
  targets {
    ids: "0_8"
    ids: "1_8"
  }
  targets {
    ids: "0_9"
    ids: "0_10"
  }
  targets {
    ids: "0_9"
    ids: "1_9"
  }
  targets {
    ids: "0_10"
    ids: "1_10"
  }
  targets {
    ids: "1_0"
    ids: "1_1"
  }
  targets {
    ids: "1_1"
    ids: "1_2"
  }
  targets {
    ids: "1_2"
    ids: "1_3"
  }
  targets {
    ids: "1_3"
    ids: "1_4"
  }
  targets {
    ids: "1_4"
    ids: "1_5"
  }
  targets {
    ids: "1_5"
    ids: "1_6"
  }
  targets {
    ids: "1_6"
    ids: "1_7"
  }
  targets {
    ids: "1_7"
    ids: "1_8"
  }
  targets {
    ids: "1_8"
    ids: "1_9"
  }
  targets {
    ids: "1_9"
    ids: "1_10"
  }
}
"""
