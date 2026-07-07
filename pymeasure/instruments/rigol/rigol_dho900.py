#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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
import logging
from enum import Enum
from typing import Optional

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range, truncated_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Channel:
    """Implementation of a Rigol DHO900 series oscilloscope channel.

    Implementation modeled on Channel object of Keysight DSOX1102G instrument."""

    BOOLS = {True: 1, False: 0}

    bwlimit = Instrument.control(
        "BWL?",
        "BWL %s",
        """ A boolean parameter that toggles 20 MHz internal low-pass filter.""",
        validator=strict_discrete_set,
        values={True: "20M", False: "OFF"},
        map_values=True,
    )

    coupling = Instrument.control(
        "COUP?",
        "COUP %s",
        """ Control the coupling mode ("ac", "dc", or "gnd").""",
        validator=strict_discrete_set,
        values={"ac": "AC", "dc": "DC", "gnd": "GND"},
        map_values=True,
    )

    display = Instrument.control(
        "DISP?",
        "DISP %d",
        """ Control enable/disable the specified channel.""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True,
    )

    invert = Instrument.control(
        "INV?",
        "INV %d",
        """ Control the inversion of the input signal.""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True,
    )

    offset = Instrument.control(
        "OFFS?",
        "OFFS %g",
        """ Control the voltage at center of screen. The range of legal values varies depending on
        range and scale. If the specified value is outside of the legal range, the offset value is
        automatically set to the nearest legal value.
        """,
    )

    scale = Instrument.control(
        "SCAL?",
        "SCAL %g",
        """Control the vertical scale (or units per division) of the specified channel, in V/div.""",
    )

    probe_attenuation = Instrument.control(
        "PROB?",
        "PROB %g",
        """ Control the probe attenuation. The probe attenuation may be from 0.001 to 50000.""",
        validator=strict_discrete_set,
        values=(
            0.001,
            0.002,
            0.005,
            0.01,
            0.02,
            0.05,
            0.1,
            0.2,
            0.5,
            1,
            2,
            5,
            10,
            20,
            50,
            100,
            200,
            500,
            1000,
            2000,
            5000,
            10000,
            20000,
            50000,
        ),
    )

    label_show = Instrument.control(
        "LAB:SHOW?",
        "LAB:SHOW %d",
        """ Control to sets or queries whether to display the label of the specified channel. """,
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True,
    )

    label = Instrument.control(
        "LAB:CONT?",
        'LAB:CONT "%s"',
        """ Control to label the channel. """,
        get_process=lambda v: str(v[1:-1]),
    )

    unit = Instrument.control(
        "UNIT?",
        "UNIT %s",
        """ Control the unit of the specified channel. """,
        validator=strict_discrete_set,
        values={"watt": "WATT", "amp": "AMP", "volt": "VOLT", "unknown": "UNKN"},
        map_values=True,
    )

    vernier = Instrument.control(
        "VERN?",
        "VERN %d",
        """ Control fine adjustment of the vertical scale of the specified channel. """,
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True,
    )

    position = Instrument.control(
        "POS?",
        "POS %g",
        """ Control the bias voltage of the specified chanel. The range of legal values varies depending on
        range and scale. If the specified value is outside of the legal range, the offset value is
        automatically set to the nearest legal value.
        """,
    )

    def __init__(self, instrument, number):
        self.instrument = instrument
        self.number = number

    def values(self, command, **kwargs):
        """Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return self.instrument.values(f":channel{self.number}:{command}", **kwargs)

    def ask(self, command):
        self.instrument.ask(f":CHAN{self.number}:{command}")

    def write(self, command):
        self.instrument.write(f":CHAN{self.number}:{command}")

    def setup(
        self,
        bwlimit=None,
        coupling=None,
        display=None,
        invert=None,
        offset=None,
        scale=None,
        probe_attenuation=None,
        label_show=None,
        label=None,
        unit=None,
        vernier=None,
        position=None,
    ):
        """Setup channel. Unspecified settings are not modified. Modifying values such as
        probe attenuation will modify offset, range, etc. Refer to oscilloscope documentation and
        make multiple consecutive calls to setup() if needed.

        :param bwlimit: A boolean, which enables 25 MHz internal low-pass filter.
        :param coupling: "ac" or "dc".
        :param display: A boolean, which enables channel display.
        :param invert: A boolean, which enables input signal inversion.
        :param label: Label string with max. 10 commonly used ASCII characters.
        :param offset: Numerical value represented at center of screen, must be inside
            the legal range.
        :param probe_attenuation: Probe attenuation values from 0.1 to 1000.
        :param vertical_range: Full-scale vertical axis of the selected channel. When using 1:1
            probe attenuation, legal values for the range are  from 8mV to 40 V. If the probe
            attenuation is changed, the range value is multiplied by the probe attenuation factor.
        :param scale: Units per division."""

        if bwlimit is not None:
            self.bwlimit = bwlimit
        if coupling is not None:
            self.coupling = coupling
        if display is not None:
            self.display = display
        if invert is not None:
            self.invert = invert
        if offset is not None:
            self.offset = offset
        if scale is not None:
            self.scale = scale
        if probe_attenuation is not None:
            self.probe_attenuation = probe_attenuation
        if label_show is not None:
            self.label_show = label_show
        if label is not None:
            self.label = label
        if unit is not None:
            self.unit = unit
        if vernier is not None:
            self.vernier = vernier
        if position is not None:
            self.position = position

    @property
    def current_configuration(self):
        """Read channel configuration as a dict containing the following keys:
        - "CHAN": channel number (int)
        - "OFFS": vertical offset (float)
        - "RANG": vertical range (float)
        - "COUP": "dc" or "ac" coupling (str)
        - "IMP": input impedance (str)
        - "DISP": currently displayed (bool)
        - "BWL": bandwidth limiting enabled (bool)
        - "INV": inverted (bool)
        - "UNIT": unit (str)
        - "PROB": probe attenuation (float)
        - "PROB:SKEW": skew factor (float)
        - "STYP": probe signal type (str)
        """

        ch_setup_list = (
            "bwlimit",
            "coupling",
            "display",
            "invert",
            "offset",
            "scale",
            "probe_attenuation",
            "label_show",
            "label",
            "unit",
            "vernier",
            "position",
        )

        ch_setup_dict = {}

        for setup in ch_setup_list:
            ch_setup_dict[setup] = getattr(self, setup)

        return ch_setup_dict


class RigolDHO900(Instrument):
    # """ Represents the Keysight DSOX1102G Oscilloscope interface for interacting
    """Represents the Rigol DOH900 Series Oscilloscope interface for interacting
    with the instrument.

    DHO914(s) has 125MHz bandwidth, while DHO924(s) has 250MHz bandwidth. "S" represents
    the arbitrary signal generator.

    Refer to the Keysight DSOX1102G Oscilloscope Programmer's Guide for further details about
    using the lower-level methods to interact directly with the scope.

    .. code-block:: python

        scope = RigolDHO900(resource)
        scope.autoset()
        ch1_data_array = scope.waveform_data
        # ...
        scope.close()

    """

    BOOLS = {True: 1, False: 0}

    class SOURCE(Enum):
        ch1 = "CHAN1"
        ch2 = "CHAN2"
        ch3 = "CHAN3"
        ch4 = "CHAN4"
        d0 = "D0"
        d1 = "D1"
        d2 = "D2"
        d3 = "D3"
        d4 = "D4"
        d5 = "D5"
        d6 = "D6"
        d7 = "D7"
        d8 = "D8"
        d9 = "D9"
        d10 = "D10"
        d11 = "D11"
        d12 = "D12"
        d13 = "D13"
        d14 = "D14"
        d15 = "D15"
        math1 = "MATH1"
        math2 = "MATH2"
        math3 = "MATH3"
        math4 = "MATH4"

    class MEASURE(Enum):
        """Measurement item name."""

        Vmax = "VMAX"
        Vmin = "VMIN"
        Vpp = "VPP"
        Vtop = "VTOP"
        Vbase = "VBAS"
        Vamp = "VAMP"
        Vavg = "VAVG"
        Vrms = "VRMS"
        overshoot = "OVER"
        preshoot = "PRES"
        area = "MAR"
        area_one_period = "MPAR"
        period = "PER"
        frequency = "FREQ"
        rise_time = "RTIM"
        fall_time = "FTIM"
        positive_width = "PWID"
        negative_width = "NWID"
        duty = "PDUT"
        duty_neg = "NDUT"
        Tvmax = "TVMAX"
        Tvmin = "TVMIN"
        positive_slew_rate = "PSL"
        negative_slew_rate = "NSL"
        Vupper = "VUPP"
        Vmid = "VMID"
        Vlower = "VLOW"
        variance = "VAR"
        Vrms_one_period = "PVRM"
        positive_pulse_count = "PPUL"
        negative_pulse_count = "NPUL"
        rise_edge_count = "PEDG"
        fall_edge_count = "NEDG"
        delay_rise_rise = "RRD"
        delay_rise_fall = "RFD"
        delay_fall_rise = "FRD"
        delay_fall_fall = "FFD"
        phase_rise_rise = "RRPH"
        phase_rise_fall = "RFPH"
        phase_fall_rise = "FRPH"
        phase_fall_fall = "FFPH"
        AC_rms = "ACRM"

    def __init__(self, adapter, name="Rigol DHO900 Oscilloscope", **kwargs):
        super().__init__(adapter, name, **kwargs)
        # Account for setup time for timebase_mode, waveform_points_mode
        self.ch1 = Channel(self, 1)
        self.ch2 = Channel(self, 2)
        self.ch3 = Channel(self, 3)
        self.ch4 = Channel(self, 4)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.adapter.close()
        self.shutdown()

    #################
    # Channel setup #
    #################

    def autoset(self):
        """Autoscale displayed channels."""
        self.write(":AUT")

    ##################
    # Timebase Setup #
    ##################

    timebase_mode = Instrument.control(
        ":TIM:MODE?",
        ":TIM:MODE %s",
        """ A string parameter that sets the current time base. Can be 'main',
        'xy', or 'roll'. The query returns 'main' or 'roll'.""",
        validator=strict_discrete_set,
        values={"main": "MAIN", "xy": "MAIN", "roll": "ROLL"},
        map_values=True,
    )

    timebase_mode_xy = Instrument.control(
        ":TIM:XY:ENAB?",
        ":TIM:XY:ENAB %d",
        """ Control XY mode to enable/disable. """,
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True,
    )

    timebase_offset = Instrument.control(
        ":TIM?",
        ":TIM %g",
        """ A float parameter that sets the time interval in seconds between the trigger
       event and the reference position (at center of screen by default).""",
    )

    timebase_scale = Instrument.control(
        ":TIM:SCAL?",
        ":TIM:SCAL %g",
        """ A float parameter that sets the horizontal scale (units per division) in seconds
       for the main window.""",
    )

    timebase_href_mode = Instrument.control(
        ":TIM:HREF:MODE?",
        ":TIM:HREF:MODE %s",
        """ Control the horizontal reference mode. Can be 'center', 'left_border', 'right_border',
        'trigger', or 'user'.""",
        validator=strict_discrete_set,
        values={
            "center": "CENT",
            "left_border": "LB",
            "right_border": "RB",
            "trigger": "TRIG",
            "user": "USER",
        },
        map_values=True,
    )

    timebase_href_position = Instrument.control(
        ":TIM:HREF:POS?",
        ":TIM:HREF:POS %d",
        """ Control user-defined reference position when the waveforms are expanded or compressed horizontally. """,
        validator=truncated_range,
        values=[-500, 500],
    )

    @property
    def timebase_configuration(self):
        """Read all timebase configurations as a dict."""
        ch_setup_list = (
            "timebase_mode",
            "timebase_mode_xy",
            "timebase_offset",
            "timebase_scale",
            "timebase_href_mode",
            "timebase_href_position",
        )
        ch_setup_dict = {}
        for setup in ch_setup_list:
            ch_setup_dict[setup] = getattr(self, setup)
        return ch_setup_dict

    ################
    ## Acquisition #
    ################

    acquisition_type = Instrument.control(
        ":ACQ:TYPE?",
        ":ACQ:TYPE %s",
        """ A string parameter that sets the type of data acquisition. Can be "normal", "average",
       "peak", or "ultra".""",
        validator=strict_discrete_set,
        values={"normal": "NORM", "average": "AVER", "ultra": "ULTR", "peak": "PEAK"},
        map_values=True,
    )

    memory_depth = Instrument.control(
        ":ACQ:MDEP?",
        ":ACQ:MDEP %s",
        """ Control memory depth of the oscilloscope and default unit is pts. Can be
       'auto', '1k', '10k', '100k', '1M', '10M', '25M', '50M' or its numeric value. 
       """,
        validator=strict_discrete_set,
        values=(
            "auto",
            "1e3",
            "1e4",
            "1e5",
            "1e6",
            "1e7",
            "2.5e7",
            "5e7",
            "1k",
            "10k",
            "100k",
            "1M",
            "10M",
            "25M",
            "50M",
            1e3,
            1e4,
            1e5,
            1e6,
            1e7,
            2.5e7,
            5e7,
        ),
    )

    sample_rate = Instrument.control(
        ":ACQ:SRAT?",
        ":ACQ:SRAT %s",
        """ Control sample rate and unit is Sa/s. """,
    )

    def run(self):
        """Starts repetitive acquisitions.
        This is the same as pressing the Run key on the front panel.
        """
        self.write(":RUN")

    def stop(self):
        """Stops the acquisition. This is the same as pressing the Stop key on the front panel."""
        self.write(":STOP")

    def single(self):
        """Causes the instrument to acquire a single trigger of data.
        This is the same as pressing the Single key on the front panel."""
        self.write(":SING")

    def force_trigger(self):
        """Generates a trigger signal forcefully."""
        self.write(":TFOR")

    waveform_source = Instrument.control(
        ":WAV:SOUR?",
        ":WAV:SOUR %s",
        """ A string parameter that selects the analog channel, function, or reference waveform
        to be used as the source for the waveform methods. Can be "d0" to "d15", 
        "ch1" to "ch4", "math1" to "math4". """,
        validator=strict_discrete_set,
        values={member.name: member.value for member in SOURCE},
        map_values=True,
    )

    waveform_mode = Instrument.control(
        ":WAV:MODE?",
        ":WAV:MODE %s",
        """ A string parameter that sets the data record to be transferred with the waveform_data
        method. Can be "normal", "maximum", or "raw".
          "normal": reads the waveform data currently displayed on the screen.
          "maximum": reads data on the screen in Run state; read data from the internal memory in Stop state.
          "raw": reads data from the internal memory. Must be in Stop state.
        """,
        validator=strict_discrete_set,
        values={"normal": "NORM", "maximum": "MAX", "raw": "RAW"},
        map_values=True,
    )

    waveform_format = Instrument.control(
        ":WAV:FORM?",
        ":WAV:FORM %s",
        """ A string parameter that controls how the data is formatted when sent from the
       oscilloscope. Can be "ascii", "word" or "byte". Words are transmitted in big endian by
       default.""",
        validator=strict_discrete_set,
        values={"ascii": "ASC", "word": "WORD", "byte": "BYTE"},
        map_values=True,
    )

    waveform_points = Instrument.control(
        ":WAV:POIN?",
        ":WAV:POIN %d",
        """ An integer parameter that sets the number of waveform points to be transferred with
       the waveform_data method. Can be any of the following values:
       100, 250, 500, 1000, 2 000, 5 000, 10 000, 20 000, 50 000, 62 500.

       Note that the oscilloscope may provide less than the specified nb of points. """,
        # validator=strict_discrete_set,
        # values=[100, 250, 500, 1000, 2000, 5000, 10000, 20000, 50000, 62500]
    )

    xinc = Instrument.measurement(
        ":WAV:XINC?",
        """ Queries the reference time of the waveform points of the currently selected channel source in the X direction. """,
    )
    xref = Instrument.measurement(
        ":WAV:XREF?", """ Queries the time interval between two neighboring points. """
    )
    xo = Instrument.measurement(
        ":WAV:XOR?",
        """ Queries the start time of the waveform data of the currently selected channel source in the X direction.""",
    )
    yinc = Instrument.measurement(
        ":WAV:YINC?", """ Queries the unit voltage value of the current source in Y. """
    )
    yref = Instrument.measurement(
        ":WAV:YREF?", """ Queries the vertical reference position of the current source in Y. """
    )
    yo = Instrument.measurement(
        ":WAV:YOR?",
        """ Queries the vertical offset relative to the vertical reference position of the currently selected channel source in the Y direction. """,
    )

    @property
    def waveform_preamble(self):
        """Get preamble information for the selected waveform source as a dict with the following keys:
        - "format": byte, word, or ascii (str)
        - "type": normal, maximum, or raw (str)
        - "points": nb of data points transferred (int)
        - "count": always 1 (int)
        - "xincrement": time difference between data points (float)
        - "xorigin": first data point in memory (float)
        - "xreference": data point associated with xorigin (int)
        - "yincrement": voltage difference between data points (float)
        - "yorigin": voltage at center of screen (float)
        - "yreference": data point associated with yorigin (int)"""
        return self._waveform_preamble()

    @property
    def waveform_data(self):
        """Get waveform data by ASCII format."""
        # Other waveform formats raise UnicodeDecodeError
        return self.waveform_data_from("ascii")

    def waveform_data_from(self, fmt: str = "ascii") -> list:
        """Get data from binary block of sampled data points transmitted using the IEEE 488.2 arbitrary
        block data format."""
        if not fmt in ("ascii", "byte", "word"):
            return []

        # In 'raw' mode, the oscilloscope must be in STOP state.
        if self.waveform_mode == "raw" and self.trigger_status != "STOP":
            self.stop()
        self.waveform_format = fmt
        cmd = ":WAV:DATA?"
        if fmt == "ascii":
            return self.values(cmd)
        elif fmt == "byte" or fmt == "word":
            self.write(cmd)
            res = self.read_bytes(-1)
            # assert chr(res[0]) == "#"
            # if chr(res[0]) != "#":
            #    log.error("Incorrct return format.")
            # read_length = int(chr(res[1]))
            # datasize = int(res[2 : 2 + read_length])
            # bytes_data = res[2 + read_length : 2 + read_length + datasize]
            bytes_data = self._extract_byte_data(res)

            # Calculate real value from bytes data
            yo, yref, yinc = self.yo, self.yref, self.yinc
            if fmt == "byte":
                assert len(bytes_data) == self.waveform_points
                if len(bytes_data) != self.waveform_points:
                    log.error("Data size mismatch.")
                return [(i - yo - yref) * yinc for i in bytes_data]
            elif fmt == "word":
                assert len(bytes_data) / 2 == self.waveform_points
                data = []
                for i in (bytes_data[i : i + 2] for i in range(0, len(bytes_data), 2)):
                    v = int.from_bytes(i, byteorder="little")
                    data.append((v - yo - yref) * yinc)
                return data

    #################
    ## System Setup #
    #################

    def _extract_byte_data(self, res: bytes) -> bytes:
        """Extract bytes data according to Rigol binary data format."""
        # if chr(res[0]) != "#":
        #    log.error("Incorrct return format.")
        try:
            assert chr(res[0]) == "#"
        except AssertionError:
            log.error("Incorrct return format.")
            return res

        read_length = int(chr(res[1]))
        datasize = int(res[2 : 2 + read_length])
        return res[2 + read_length : 2 + read_length + datasize]

    @property
    def system_setup(self):
        """Sends or reads the data stream of the system setup file."""
        self.write(":SYST:SET?")
        return self.read_bytes(-1)

    @system_setup.setter
    def system_setup(self, setup_string: bytes):
        self.write_bytes(b":SYST:SET " + setup_string)

    def ch(self, channel_number):
        if 1 <= channel_number <= 4:
            return getattr(self, f"ch{channel_number}")
        else:
            raise ValueError("Invalid channel number. Must be 1 to 4.")

    trigger_status = Instrument.measurement(
        ":TRIG:STAT?", """ Queries the current trigger status. """
    )

    trigger_mode = Instrument.control(
        ":TRIG:MODE?", ":TRIG:MODE %s", """ Control the trigger type. """
    )

    @property
    def display_clear(self):
        """Clear all the waveforms on the screen."""
        self.write(":DISP:CLE")

    def capture_screen(self, fn="screen.png") -> None:
        """Get image of oscilloscope screen in PNG file format.

        :param fn: filename, default to "screen.png".
        """
        self.write(":DISP:DATA? PNG")
        res = self.read_bytes(2)
        img_bin = self._extract_byte_data(res)
        with open(fn, "wb") as f:
            f.write(img_bin)
            print(f"{fn} saved.")

    def _waveform_preamble(self):
        """
        Reads waveform preamble and converts it to a more convenient dict of values.
        """
        vals = self.values(":WAV:PRE?")
        # Get values to dict
        vals_dict = dict(
            zip(
                [
                    "format",
                    "type",
                    "points",
                    "count",
                    "xincrement",
                    "xorigin",
                    "xreference",
                    "yincrement",
                    "yorigin",
                    "yreference",
                ],
                vals,
            )
        )
        # Map element values
        format_map = {0: "BYTE", 1: "WORD", 2: "ASCII"}
        type_map = {0: "NORMAL", 1: "MAX", 2: "RAW"}
        vals_dict["format"] = format_map[int(vals_dict["format"])]
        vals_dict["type"] = type_map[int(vals_dict["type"])]

        # Correct types
        to_int = ["points", "count", "xreference", "yreference"]
        to_float = ["xincrement", "xorigin", "yincrement", "yorigin"]
        for key in vals_dict:
            if key in to_int:
                vals_dict[key] = int(vals_dict[key])
            elif key in to_float:
                vals_dict[key] = float(vals_dict[key])

        return vals_dict

    lock_fp_key = Instrument.control(
        ":SYST:LOCK?",
        ":SYST:LOCK %d",
        """ Control front-panel and toch screen's opeation. """,
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True,
    )

    beeper = Instrument.control(
        ":SYST:BEEP?",
        ":SYST:BEEP %d",
        """ Control on or off the beeper. """,
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True,
    )

    #################
    ## Measurements #
    #################

    measure_source = Instrument.control(
        ":MEAS:SOUR?",
        ":MEAS:SOUR %s",
        """ Control source of measurement. Can be "d0" to "d15", "ch1" to "ch4", or "math1" to "math4". """,
        validator=strict_discrete_set,
        values={member.name: member.value for member in SOURCE},
        map_values=True,
    )

    @property
    def measure_clear(self) -> None:
        self.write(":MEAS:CLE")

    measure_all_of = Instrument.control(
        ":MEAS:AMS?",
        ":MEAS:AMS %s",
        """ Control channel to display all measurement values on screen. Can be 'off', 'ch1' to 'ch4'. """,
        validator=strict_discrete_set,
        values={"off": "OFF", "ch1": "CHAN1", "ch2": "CHAN2", "ch3": "CHAN3", "ch4": "CHAN4"},
        map_values=True,
    )

    measure_statistic_enable = Instrument.control(
        ":MEAS:STAT:DISP?",
        ":MEAS:STAT:DISP %d",
        """ Control enable/disable the statistical function. """,
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True,
    )

    measure_statistic_reset = Instrument.control(
        ":MEAS:STAT:RES?",
        ":MEAS:STAT:RES %d",
        """ Control enable/disable the statistical function. """,
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True,
    )

    def measure(self, item: MEASURE, src1: Optional[SOURCE] = None, src2: Optional[SOURCE] = None):
        if src1 is None and src2 is None:
            cmd = f"{item.value}"
        elif src1 is not None and src2 is None:
            cmd = f"{item.value},{src1.value}"
        elif src1 is not None and src2 is not None:
            cmd = f"{item.value},{src1.value},{src2.value}"
        else:
            cmd = f"{item.value}"

        self.write(f":MEAS:ITEM {cmd}")
        res = self.value(f":MEAS:ITEM? {cmd}")
        return res

class RigolDHO914(RigolDHO900):
  pass

class RigolDHO924(RigolDHO900):
  pass

class RigolDHO914S(RigolDHO900):
  pass

class RigolDHO924S(RigolDHO900):
  pass
