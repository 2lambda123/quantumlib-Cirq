# Copyright 2024 The Cirq Developers
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

from cirq_google.api.v2 import program_pb2
from cirq_google.api.v2 import run_context_pb2
import cirq_google.api.v2.run_context as run_context
import google.protobuf.text_format as text_format


def test_to_device_parameters_diff() -> None:
    readout_paths = (["q3_4", "readout_default"], ["q5_6", "readout_default"])

    device_params = []
    for readout_path in readout_paths:
        device_params.extend(
            [
                (
                    run_context_pb2.DeviceParameter(
                        path=[*readout_path, "readoutDemodDelay"], units="ns"
                    ),
                    program_pb2.ArgValue(float_value=5.0),
                ),
                (
                    run_context_pb2.DeviceParameter(path=[*readout_path, "readoutFidelities"]),
                    program_pb2.ArgValue(
                        double_values=program_pb2.RepeatedDouble(values=[0.991, 0.993])
                    ),
                ),
                (
                    run_context_pb2.DeviceParameter(path=[*readout_path, "demod", "phase_i_rad"]),
                    program_pb2.ArgValue(double_value=0.0),
                ),
            ]
        )
    diff = run_context.to_device_parameters_diff(device_params)
    expected_diff_pb_text = """
        dirs {
          parent: -1
        }
        dirs {
          name: 1
        }
        dirs {
          name: 4
        }
        dirs {
          parent: -1
          name: 6
        }
        dirs {
          parent: 3
          name: 1
        }
        dirs {
          parent: 3
          name: 4
        }
        keys {
          name: 2
          value {
            float_value: 5
          }
        }
        keys {
          name: 3
          value {
            double_values {
              values: 0.991
              values: 0.993
            }
          }
        }
        keys {
          dir: 2
          name: 5
          value {
            double_value: 0
          }
        }
        keys {
          dir: 3
          name: 2
          value {
            float_value: 5
          }
        }
        keys {
          dir: 3
          name: 3
          value {
            double_values {
              values: 0.991
              values: 0.993
            }
          }
        }
        keys {
          dir: 5
          name: 5
          value {
            double_value: 0
          }
        }
        strs: "q3_4"
        strs: "readout_default"
        strs: "readoutDemodDelay"
        strs: "readoutFidelities"
        strs: "demod"
        strs: "phase_i_rad"
        strs: "q5_6"
    """
    assert text_format.Parse(expected_diff_pb_text, run_context_pb2.DeviceParametersDiff()) == diff
