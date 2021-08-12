import cirq
import numpy as np
from typing import Optional, Sequence
from cirq.devices.noise_model import validate_all_measurements
from itertools import product
import cirq_google

class Fidelity():
  def __init__(
      self,
      *,
      t1: Optional = None,
      decay_constant: Optional = None,
      xeb_fidelity: Optional = None,
      pauli_error: Optional = None,
      p00: Optional = None,
      p11: Optional = None
  ) -> None:
    """
    Detailed comments about arguments here
    """
    if not any([t1, decay_constant, xeb_fidelity, pauli_error, p00, p11]):
      raise ValueError('At least one metric must be specified')

    for metric in [xeb_fidelity, pauli_error, p00, p11]:
      if metric is not None and not 0.0 <= metric <= 1.0:
        raise ValueError('xeb, pauli error, p00, and p11 must be between 0 and 1')

    if np.count_nonzero([metric is not None for metric in [xeb_fidelity, pauli_error, decay_constant]]) > 1:
      raise ValueError('Only one of xeb fidelity, pauli error, or decay constant should be defined')

    self._t1 = t1
    self._p = decay_constant
    self._p00 = p00
    self._p11 = p11
    self._pauli_error = pauli_error
    self._xeb = xeb_fidelity

    if self._pauli_error is not None:
      self._p = self.pauli_error_to_decay_constant()
      self._xeb = self.pauli_error_to_xeb_fidelity()
    elif self._p is not None:
      self._pauli_error = self.decay_constant_to_pauli_error()
      self._xeb = self.decay_constant_to_xeb_fidelity()
    elif self._xeb is not None:
      self._p = self.xeb_fidelity_to_decay_constant()
      self._pauli_error = self.decay_constant_to_pauli_error()

  @property
  def decay_constant(self):
    return self._p

  @property
  def p00(self):
    return self._p00

  @property
  def p11(self):
    return self._p11

  @property
  def pauli_error(self):
    return self._pauli_error

  @property
  def t1(self):
    return self._t1

  @property
  def xeb(self):
    return self._xeb

  def decay_constant_to_xeb_fidelity(self, N: int = 4):
    return 1 - ((1 - self._p) * (1 - 1 / N))

  def decay_constant_to_pauli_error(self, N: int = 2):
    return (1 - self._p) * (1 - 1 / N / N)

  def pauli_error_to_xeb_fidelity(self, N: int = 4):
    decay_constant = 1 - (self._pauli_error / (1 - 1 / N))
    return self.decay_constant_to_xeb_fidelity(decay_constant)

  def pauli_error_to_decay_constant(self, N: int = 2):
    return 1 - (self._pauli_error / (1 - 1 / N / N))

  def xeb_fidelity_to_decay_constant(self, N: int = 4):
    return 1 - (1 - self._xeb) / (1 - 1 / N)

  def pauli_error_from_t1(self, t: float, t1: float):
    t2 = 2 * t1
    return (1 - np.exp(-t / t2)) / 2 + (1 - np.exp(-t / t1)) / 4

  def pauli_error_from_depolarization(self, t : float):
    if self._t1 is not None:
      return self._pauli_error - self.pauli_error_from_t1(t, self._t1)
    else:
      return self._pauli_error

  def rb_pauli_error(self, N: int = 2):
    return (1 - self._p) * (1 - 1 / N**2)

  def rb_average_error(self, N: int = 2):
    return (1 - self._p) * (1 - 1 / N)

def fidelity_from_calibration(calibration: cirq_google.Calibration):

  def unpack_from_calibration(metric_name):
    if metric_name in calibration.keys():
      return np.mean([value for qubit, value in calibration[metric_name].items()])
    else:
      return None

  def rb_error_to_decay_constant(rb_pauli_error, N: int = 2):
    if rb_pauli_error is not None:
      return 1 - rb_pauli_error / (1 - 1 / N**2)
    else:
      return None

  t1_micros = unpack_from_calibration('single_qubit_idle_t1_micros')
  t1_nanos = t1_micros * 1000 if t1_micros is not None else None
  xeb_fidelity = unpack_from_calibration('xeb')
  rb_pauli_error = unpack_from_calibration('single_qubit_rb_pauli_error_per_gate')
  p00 = unpack_from_calibration('single_qubit_p00_error')
  p11 = unpack_from_calibration('single_qubit_p11_error')
  decay_constant = rb_error_to_decay_constant(rb_pauli_error)

  if decay_constant is not None: # can't define both decay constant and xeb
    return Fidelity(t1 = t1_nanos, decay_constant = decay_constant, p00 = p00, p11 = p11)
  return Fidelity(t1 = t1_nanos, xeb_fidelity = xeb_fidelity, p00 = p00, p11 = p11)



class NoiseModelFromFidelity(cirq.NoiseModel):
  def __init__(
      self,
      fidelity: Fidelity
  ) -> None:
    if fidelity is not None:
      self._fidelity = fidelity
    else:
      raise ValueError('A fidelity object must be specified')

  def get_duration(self, gate):
    if isinstance(gate, cirq.FSimGate):
      theta,_ = gate._value_equality_values_()
      if np.abs(theta) % (np.pi / 2) == 0:
        return 12.0 ## syc
      return 32.0 ## fsim_pi_4
    elif isinstance(gate, cirq.ISwapPowGate):
      return 32.0 #inv_fsim_pi_4
    elif isinstance(gate, cirq.ZPowGate):
      return 0.0
    elif isinstance(gate, cirq.MeasurementGate):
      return 4000.0
    return 25.0

  def apply_readout_noise(self, p00, p11, moments, system_qubits):
    if p00 is not None and p11 is not None:
      p = p11 / (p00 + p11)
      gamma = p11 / p
      moments.append(cirq.Moment(cirq.GeneralizedAmplitudeDampingChannel(p = p, gamma = gamma)(q) for q in system_qubits))
    elif p00 is not None:
      moments.append(cirq.Moment(cirq.GeneralizedAmplitudeDampingChannel(p = 0.0, gamma = p00)(q) for q in system_qubits))
    elif p11 is not None:
      moments.append(cirq.Moment(cirq.GeneralizedAmplitudeDampingChannel(p = 1.0, gamma = p11)(q) for q in system_qubits))


  def apply_depol_noise(self, pauli_error, moments, system_qubits):
    _sq_inds = np.arange(4)
    pauli_inds = np.array(list(product(_sq_inds, repeat = 1)))
    num_inds = len(pauli_inds)
    p_other = pauli_error / (num_inds - 1) # probability of other pauli gates
    moments.append(cirq.Moment(cirq.depolarize(p_other)(q) for q in system_qubits))

  def apply_ampl_damp_noise(self, duration, t1, moments, system_qubits):
    moments.append(cirq.Moment(cirq.amplitude_damp(1 - np.exp(-duration / t1)).on_each(system_qubits)))

  def noisy_moment(self, moment: cirq.Moment, system_qubits: Sequence[cirq.Qid]) -> cirq.OP_TREE:
    moments = []

    if validate_all_measurements(moment): ## add after measurement gate
      p00 = self._fidelity._p00
      p11 = self._fidelity._p11
      self.apply_readout_noise(p00, p11, moments, system_qubits)
      moments.append(moment)
    else:
      moments.append(moment)
      if self._fidelity._pauli_error is not None: ## pauli error
        duration = max([self.get_duration(op.gate) for op in moment.operations])
        pauli_error = self._fidelity.pauli_error_from_depolarization(duration)
        self.apply_depol_noise(pauli_error, moments, system_qubits)

      if self._fidelity._t1 is not None: # t1 decay noise
        duration = max([self.get_duration(op.gate) for op in moment.operations])
        self.apply_ampl_damp_noise(duration, self._fidelity._t1, moments, system_qubits)
    return moments

