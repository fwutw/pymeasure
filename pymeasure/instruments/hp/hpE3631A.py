#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, truncated_range
from pyvisa.constants import StopBits, Parity
from time import sleep


class HPE3631A(Instrument):
    """Represents the HP E3631A Triple Outupt DC Power Supply.

    For a connection through USB-to-RS232, the `resourceName` is: 'ASRL<board>[::INSTR]'
    On Linux, ex: 'ASRL/dev/ttyUSB0' or 'ASRL/dev/ttyUSB0::INSTR'
    """

    vers = Instrument.measurement(
        "SYST:VERS?", "Ask what version of SCPI the power supply conforms to"
    )

    set_output_on = Instrument.control(
        "OUTPut?",
        "OUTPut %d",
        """A boolean property that controls whether the source is enabled, takes
        values True or False.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    voltage_setpoint = Instrument.control(
        ":SOUR:VOLT?",
        ":SOUR:VOLT %g",
        """A floating point property that controls the source voltage
        in volts. This is not checked against the allowed range. Depending on
        whether the instrument is in constant current or constant voltage mode,
        this might differ from the actual voltage achieved.""",
        validator=truncated_range,
        values=(0, 6.18),
        dynamic=True,
    )

    current_limit = Instrument.control(
        ":SOUR:CURR?",
        ":SOUR:CURR %g",
        """A floating point property that controls the source current
        in amps. This is not checked against the allowed range. Depending on
        whether the instrument is in constant current or constant voltage mode,
        this might differ from the actual current achieved.""",
        validator=truncated_range,
        values=(0, 5.15),
        dynamic=True,
    )

    voltage = Instrument.measurement(
        ":MEAS:VOLT?",
        """Reads the voltage (in Volt) the dc power supply is putting out.
        """,
    )

    current = Instrument.measurement(
        ":MEAS:CURR?",
        """Reads the current (in Ampere) the dc power supply is putting out.
        """,
    )

    applied = Instrument.control(
        ":APPly?",
        ":APPly %g,%g",
        """Simultaneous control of voltage (volts) and current (amps).
        Values need to be supplied as tuple of (voltage, current). Depending on
        whether the instrument is in constant current or constant voltage mode,
        the values achieved by the instrument will differ from the ones set.
        """,
        get_process=lambda y: (float(y[0].replace('"', "")), float(y[1].replace('"', ""))),
    )

    _output_ch = {0: "P6V", 1: "P25V", 2: "N25V"}
    _voltage_range = {0: (0, 6.18), 1: (0, 25.75), 2: (-25.75, 0)}
    _current_range = {0: (0, 5.15), 1: (0, 1.03), 2: (0, 1.03)}

    select_output = Instrument.control(
        "INST:SEL?",
        "INST:SEL %s",
        """An integer property to indicate output selections port.
        0 for +6V, 1 for +25V, and 2 for -25V.
        or or setting voltage or current limit, or for querying setting values.""",
        validator=strict_discrete_set,
        values=_output_ch,
        map_values=True,
    )

    def __init__(self, resourceName, baud_rate=9600, **kwargs):
        super().__init__(
            resourceName,
            "HP E3631A Triple Output DC Power Supply",
            asrl={
                "baud_rate": baud_rate,
                "data_bits": 7,
                "parity": Parity.even,
                "stop_bits": StopBits.two,
                "write_termination": "\n",
                "read_termination": "\r\n",
            },
            **kwargs,
        )

    def set_remote(self, lock_local_key=False):
        """This command places the power supply in the remote mode for RS-232
        operation. All keys on the front panel, include or exclude the
        'Local' key on the front panel"""

        if lock_local_key:
            self.write("SYST:RWL")
        else:
            self.write("SYST:REM")

    def set_local(self):
        """This command places the power supply in the local mode during RS-232
        operation. All keys on the front panel are fully functional."""
        self.write("SYST:LOC")

    def set_current(self, value, select):
        """Set current output limit

        Args:
            value (float) : set current in Amp
            select (int) : an index for 3 outputs. 0->"6V", 1->"25V", 2->"-25V"

        """

        if select not in range(len(self._output_ch)):
            raise NotImplementedError

        self.select_output = select
        self.current_limit_values = self._current_range.get(select)
        self.current_limit = value

    def set_voltage(self, value, select):
        """Set current output voltage

        Args:
            value (float) : set voltage in volt
            select (int) : an index for 3 outputs. 0->"6V", 1->"25V", 2->"-25V"

        """

        if select not in range(len(self._output_ch)):
            raise NotImplementedError

        self.select_output = select
        self.voltage_setpoint_values = self._voltage_range.get(select)
        self.voltage_setpoint = value

    def meas_current(self, select):
        """Return current selected supply current

        Args:
            select (int) : an index for 3 outputs. 0->"6V", 1->"25V", 2->"-25V"

        """
        if select not in range(len(self._output_ch)):
            raise NotImplementedError

        if self.select_output == select:
            return self.current
        else:
            self.select_output = select
            sleep(0.2)
            return self.current

    def meas_voltage(self, select):
        """Return current selected supply voltage

        Args:
            select (int) : an index for 3 outputs. 0->"6V", 1->"25V", 2->"-25V"

        """
        if select not in range(len(self._output_ch)):
            raise NotImplementedError

        if self.select_output == select:
            return self.voltage
        else:
            self.select_output = select
            sleep(0.2)
            return self.voltage
