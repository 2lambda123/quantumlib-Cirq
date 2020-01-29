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
from typing import List, Optional, TYPE_CHECKING

from cirq.google.engine.client.quantum import types as qtypes
from cirq.google.api import v2
from cirq.google.engine import calibration

if TYPE_CHECKING:
    import cirq.google.engine.engine as engine_base


class EngineProcessor:
    """A processor available via the Quantum Engine API.

    Attributes:
        project_id: A project_id of the parent Google Cloud Project.
        processor_id: Unique ID of the processor.
    """

    def __init__(self, processor_id: str, engine: 'engine_base.Engine',
                 processor: qtypes.QuantumProcessor) -> None:
        """A processor available via the engine.

        Args:
            processor_id: Unique ID of the processor.
            engine: The parent Engine object.
            processor: The optional current processor state.
        """
        self.project_id = engine.project_id
        self.processor_id = processor_id
        self._engine = engine
        self._processor = processor

    def engine(self) -> 'engine_base.Engine':
        """Returns the parent Engine object.

        Returns:
            The program's parent Engine.
        """
        return self._engine

    def get_device_specification(
            self) -> Optional[v2.device_pb2.DeviceSpecification]:
        """Returns a device specification proto for use in determining
        information about the device.

        Returns:
            Device specification proto.
        """
        device_spec = v2.device_pb2.DeviceSpecification()
        device_spec.ParseFromString(self._processor.device_spec.value)
        return device_spec

    def _to_calibration(self, calibration_any: qtypes.any_pb2.Any
                       ) -> calibration.Calibration:
        metrics = v2.metrics_pb2.MetricsSnapshot()
        metrics.ParseFromString(calibration_any.value)
        return calibration.Calibration(metrics)

    def list_calibrations(self, earliest_timestamp_seconds: Optional[int],
                          latest_timestamp_seconds: Optional[int]
                         ) -> List[calibration.Calibration]:
        """Retrieve metadata about a specific calibration run.

        Params:
            earliest_timestamp_seconds: The earliest timestamp of a calibration
                to return.
            latest_timestamp_seconds: The latest timestamp of a calibration to
                return.

        Returns:
            The list of calibration data with the most recent first.
        """
        if earliest_timestamp_seconds and latest_timestamp_seconds:
            filter_str = 'timestamp >= %d AND timestamp <= %d' % (
                earliest_timestamp_seconds, latest_timestamp_seconds)
        elif earliest_timestamp_seconds:
            filter_str = 'timestamp >= %d' % earliest_timestamp_seconds
        elif latest_timestamp_seconds:
            filter_str = 'timestamp <= %d' % latest_timestamp_seconds
        else:
            filter_str = ''
        response = self.engine().client.list_calibrations(
            self.project_id, self.processor_id, filter_str)
        return [self._to_calibration(c.data) for c in list(response)]

    def get_calibration(self, calibration_timestamp_seconds: int
                       ) -> calibration.Calibration:
        """Retrieve metadata about a specific calibration run.

        Params:
            calibration_timestamp_seconds: The timestamp of the calibration in
                seconds since epoch.

        Returns:
            The calibration data.
        """
        response = self.engine().client.get_calibration(
            self.project_id, self.processor_id, calibration_timestamp_seconds)
        return self._to_calibration(response.data)

    def get_current_calibration(self,) -> Optional[calibration.Calibration]:
        """Returns metadata about the current calibration for a processor.

        Returns:
            The calibration data or None if there is no current calibration.
        """
        response = self.engine().client.get_current_calibration(
            self.project_id, self.processor_id)
        if response:
            return self._to_calibration(response.data)
        else:
            return None

    def __str__(self):
        return 'EngineProcessor(project_id=\'{}\', processor_id=\'{}\')'.format(
            self.project_id, self.processor_id)
