import json
from typing import List

from cirq import ops, circuits
from cirq.contrib.quirk.linearize_circuit import linearize_circuit_qubits
from cirq.contrib.quirk.quirk_gate import (
    quirk_gate_ext,
    QuirkGate,
    UNKNOWN_GATE,
    single_qubit_matrix_gate)


def _try_convert_to_quirk_gate(gate: ops.Gate,
                               prefer_unknown_gate_to_failure: bool
                               ) -> QuirkGate:
    cast = quirk_gate_ext.try_cast(gate, QuirkGate)
    if cast is not None:
        return cast
    known_matrix = quirk_gate_ext.try_cast(gate, ops.KnownMatrixGate)
    if known_matrix is not None:
        known_matrix = single_qubit_matrix_gate(known_matrix)
    if known_matrix is not None:
        return known_matrix
    if prefer_unknown_gate_to_failure:
        return UNKNOWN_GATE
    raise TypeError('Unrecognized gate: {!r}'.format(gate))


def _to_quirk_cols(op: ops.Operation,
                   prefer_unknown_gate_to_failure: bool
                   ) -> List[str]:
    gate = _try_convert_to_quirk_gate(op.gate, prefer_unknown_gate_to_failure)

    max_index = max(q.x for q in op.qubits)
    col = [1] * (max_index + 1)
    for i, q in enumerate(op.qubits):
        col[q.x] = gate.keys[min(i, len(gate.keys) - 1)]
    yield col, gate.can_merge


def circuit_to_quirk_url(circuit: circuits.Circuit,
                         prefer_unknown_gate_to_failure: bool=False) -> str:
    circuit = circuits.Circuit(circuit.moments)
    linearize_circuit_qubits(circuit)

    cols = []
    for moment in circuit.moments:
        can_merges = []
        for op in moment.operations:
            for col, can_merge in _to_quirk_cols(
                    op,
                    prefer_unknown_gate_to_failure):
                if can_merge:
                    can_merges.append(col)
                else:
                    cols.append(col)
        if can_merges:
            merged_col = [1] * max(len(e) for e in can_merges)
            for col in can_merges:
                for i in range(len(col)):
                    if col[i] != 1:
                        merged_col[i] = col[i]
            cols.append(merged_col)

    return 'http://algassert.com/quirk#circuit={}'.format(
        json.JSONEncoder(ensure_ascii=False,
                         separators=(',', ':'),
                         sort_keys=True).encode({'cols': cols}))
