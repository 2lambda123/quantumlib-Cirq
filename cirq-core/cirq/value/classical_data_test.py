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

import pytest

import cirq

mkey_m = cirq.MeasurementKey('m')
mkey_c = cirq.MeasurementKey('c')
two_qubits = tuple(cirq.LineQubit.range(2))


def test_init():
    cd = cirq.ClassicalData()
    assert cd.measurements == {}
    assert cd.keys() == ()
    assert cd.measured_qubits == {}
    assert cd.channel_measurements == {}
    assert cd.measurement_types == {}
    cd = cirq.ClassicalData(
        _measurements={mkey_m: (0, 1)},
        _measured_qubits={mkey_m: two_qubits},
        _channel_measurements={mkey_c: 3},
    )
    assert cd.measurements == {mkey_m: (0, 1)}
    assert cd.keys() == (mkey_m, mkey_c)
    assert cd.measured_qubits == {mkey_m: two_qubits}
    assert cd.channel_measurements == {mkey_c: 3}
    assert cd.measurement_types == {
        mkey_m: cirq.MeasurementType.MEASUREMENT,
        mkey_c: cirq.MeasurementType.CHANNEL,
    }


def test_record_measurement():
    cd = cirq.ClassicalData()
    cd.record_measurement(mkey_m, (0, 1), two_qubits)
    assert cd.measurements == {mkey_m: (0, 1)}
    assert cd.keys() == (mkey_m,)
    assert cd.measured_qubits == {mkey_m: two_qubits}


def test_record_measurement_errors():
    cd = cirq.ClassicalData()
    with pytest.raises(ValueError, match='3 measurements but 2 qubits'):
        cd.record_measurement(mkey_m, (0, 1, 2), two_qubits)
    cd.record_measurement(mkey_m, (0, 1), two_qubits)
    with pytest.raises(ValueError, match='Measurement already logged to key m'):
        cd.record_measurement(mkey_m, (0, 1), two_qubits)


def test_record_channel_measurement():
    cd = cirq.ClassicalData()
    cd.record_channel_measurement(mkey_m, 1)
    assert cd.channel_measurements == {mkey_m: 1}
    assert cd.keys() == (mkey_m,)


def test_record_channel_measurement_errors():
    cd = cirq.ClassicalData()
    cd.record_channel_measurement(mkey_m, 1)
    with pytest.raises(ValueError, match='Measurement already logged to key m'):
        cd.record_channel_measurement(mkey_m, 1)


def test_get_int():
    cd = cirq.ClassicalData()
    cd.record_measurement(mkey_m, (0, 1), two_qubits)
    assert cd.get_int(mkey_m) == 1
    cd = cirq.ClassicalData()
    cd.record_measurement(mkey_m, (1, 1), two_qubits)
    assert cd.get_int(mkey_m) == 3
    cd = cirq.ClassicalData()
    cd.record_channel_measurement(mkey_m, 1)
    assert cd.get_int(mkey_m) == 1
    cd = cirq.ClassicalData()
    cd.record_measurement(mkey_m, (1, 1), (cirq.LineQid.range(2, dimension=3)))
    assert cd.get_int(mkey_m) == 4
    cd = cirq.ClassicalData()
    with pytest.raises(KeyError, match='The measurement key m is not in {}'):
        cd.get_int(mkey_m)


def test_copy():
    cd = cirq.ClassicalData(
        _measurements={mkey_m: (0, 1)},
        _measured_qubits={mkey_m: two_qubits},
        _channel_measurements={mkey_c: 3},
        _measurement_types={
            mkey_m: cirq.MeasurementType.MEASUREMENT,
            mkey_c: cirq.MeasurementType.CHANNEL,
        },
    )
    cd1 = cd.copy()
    assert cd1 is not cd
    assert cd1 == cd
    assert cd1.measurements is not cd.measurements
    assert cd1.measurements == cd.measurements
    assert cd1.measured_qubits is not cd.measured_qubits
    assert cd1.measured_qubits == cd.measured_qubits
    assert cd1.channel_measurements is not cd.channel_measurements
    assert cd1.channel_measurements == cd.channel_measurements
    assert cd1.measurement_types is not cd.measurement_types
    assert cd1.measurement_types == cd.measurement_types


def test_repr():
    cd = cirq.ClassicalData(
        _measurements={mkey_m: (0, 1)},
        _measured_qubits={mkey_m: two_qubits},
        _channel_measurements={mkey_c: 3},
        _measurement_types={
            mkey_m: cirq.MeasurementType.MEASUREMENT,
            mkey_c: cirq.MeasurementType.CHANNEL,
        },
    )
    cirq.testing.assert_equivalent_repr(cd)
