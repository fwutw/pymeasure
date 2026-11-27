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
import socket
import time

from pyvisa.errors import VisaIOError

from pymeasure.instruments import Channel, Instrument
from pymeasure.instruments.instrument import AdapterType
from pymeasure.instruments.rigol.rigol_dho_base import DHOBase, DHOBaseChannel
from pymeasure.instruments.validators import strict_discrete_set, strict_range, truncated_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

BOOLS = {True: 1, False: 0}

DIGITAL_SOURCE_CHANNELS = tuple(f"D{i}" for i in range(16))
ANALOG_SOURCE_CHANNELS = ("CHAN1", "CHAN2", "CHAN3", "CHAN4")
MATH_SOURCE_CHANNELS = ("MATH1", "MATH2", "MATH3", "MATH4")
ALL_SOURCES = ANALOG_SOURCE_CHANNELS + DIGITAL_SOURCE_CHANNELS + MATH_SOURCE_CHANNELS
AFG_FUNCTIONS = ("SIN", "SQU", "RAMP", "DC", "NOIS", "ARB")
MODULATION_FUNCTIONS = ("SIN", "SQU", "TRI", "UPR", "DNR", "NOIS")


class DHO900Channel(DHOBaseChannel):
    """A single analog input channel of the Rigol DHO900 series."""

    bandwidth_limit = Channel.control(
        ":CHAN{ch}:BWL?",
        ":CHAN{ch}:BWL %s",
        """Control the bandwidth limit: ``"OFF"`` or ``"20M"`` (str).""",
        validator=strict_discrete_set,
        values=["OFF", "20M"],
        cast=str,
    )

    vernier = Channel.control(
        ":CHAN{ch}:VERN?",
        ":CHAN{ch}:VERN %d",
        """Control fine adjustment of the vertical scale of the channel (bool).""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True,
    )

    position = Channel.control(
        ":CHAN{ch}:POS?",
        ":CHAN{ch}:POS %g",
        """Control the bias voltage of the specified channel (float).

        The range of legal values varies depending on range and scale. If the specified value is
        outside of the legal range, the position value is automatically set to the nearest legal
        value.
        """,
    )

    def setup(
        self,
        bandwidth_limit=None,
        coupling=None,
        display_enabled=None,
        invert=None,
        offset=None,
        scale=None,
        probe=None,
        label_enabled=None,
        label=None,
        units=None,
        vernier=None,
        position=None,
    ):
        """Configure multiple channel parameters at once.

        Unspecified settings are not modified. Modifying values such as probe attenuation may
        affect offset and scale.

        :param str bandwidth_limit: Bandwidth limit (``"OFF"`` or ``"20M"``).
        :param str coupling: Input coupling (``"AC"``, ``"DC"``, or ``"GND"``).
        :param bool display_enabled: Enable or disable channel display.
        :param bool invert: Enable or disable input signal inversion.
        :param float offset: Vertical offset at center of screen in Volts.
        :param float scale: Vertical scale in V/div.
        :param float probe: Probe attenuation ratio (0.001 to 50000).
        :param bool label_enabled: Enable or disable channel label display.
        :param str label: Channel label string (max 10 characters).
        :param str units: Vertical axis unit (``"VOLT"``, ``"WATT"``, ``"AMP"``, or ``"UNKN"``).
        :param bool vernier: Enable or disable fine adjustment of vertical scale.
        :param float position: Bias voltage of the channel.
        """
        if bandwidth_limit is not None:
            self.bandwidth_limit = bandwidth_limit
        if coupling is not None:
            self.coupling = coupling
        if display_enabled is not None:
            self.display_enabled = display_enabled
        if invert is not None:
            self.invert = invert
        if offset is not None:
            self.offset = offset
        if scale is not None:
            self.scale = scale
        if probe is not None:
            self.probe = probe
        if label_enabled is not None:
            self.label_enabled = label_enabled
        if label is not None:
            self.label = label
        if units is not None:
            self.units = units
        if vernier is not None:
            self.vernier = vernier
        if position is not None:
            self.position = position

    @property
    def current_configuration(self) -> dict:
        """Get channel configuration as a dictionary.

        Keys include: ``bandwidth_limit``, ``coupling``, ``display_enabled``, ``invert``,
        ``offset``, ``scale``, ``probe``, ``label_enabled``, ``label``, ``units``,
        ``vernier``, and ``position``.
        """
        ch_setup_list = (
            "bandwidth_limit",
            "coupling",
            "display_enabled",
            "invert",
            "offset",
            "scale",
            "probe",
            "label_enabled",
            "label",
            "units",
            "vernier",
            "position",
        )
        return {setup: getattr(self, setup) for setup in ch_setup_list}


class DHO900AFGChannel(Channel):
    """Built-in 25 MHz Arbitrary Function Generator (AFG) of the Rigol DHO914S and DHO924S."""

    output_enabled = Channel.control(
        ":SOUR:OUTP:STAT?",
        ":SOUR:OUTP:STAT %d",
        """Control whether the AFG output is enabled (bool).""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True,
    )

    function = Channel.control(
        ":SOUR:FUNC?",
        ":SOUR:FUNC %s",
        """Control the basic waveform function (str).

        Allowed values: ``"SIN"``, ``"SQU"``, ``"RAMP"``, ``"DC"``, ``"NOIS"``, or ``"ARB"``.
        """,
        validator=strict_discrete_set,
        values=AFG_FUNCTIONS,
        cast=str,
    )

    frequency = Channel.control(
        ":SOUR:FREQ?",
        ":SOUR:FREQ %g",
        """Control the waveform frequency in Hz (float strictly from 2e-3 to 25e6).

        Upper limit depends on waveform type: Sine 25 MHz, Square 15 MHz, Ramp 150 kHz, Arb 10 MHz.
        """,
        validator=strict_range,
        values=[2e-3, 25e6],
    )

    phase = Channel.control(
        ":SOUR:PHAS?",
        ":SOUR:PHAS %g",
        """Control the starting phase of basic waveforms in degrees (float strictly 0 to 360).""",
        validator=strict_range,
        values=[0, 360],
    )

    ramp_symmetry = Channel.control(
        ":SOUR:FUNC:RAMP:SYMM?",
        ":SOUR:FUNC:RAMP:SYMM %g",
        """Control the symmetry of the ramp waveform in percent (float strictly 0 to 100).""",
        validator=strict_range,
        values=[0, 100],
    )

    square_duty_cycle = Channel.control(
        ":SOUR:FUNC:SQU:DUTY?",
        ":SOUR:FUNC:SQU:DUTY %g",
        """Control the duty cycle of the square waveform in percent (float strictly 0 to 100).""",
        validator=strict_range,
        values=[0, 100],
    )

    amplitude = Channel.control(
        ":SOUR:VOLT:AMPL?",
        ":SOUR:VOLT:AMPL %g",
        """Control the output amplitude in Volts (float strictly from 2e-3 to 10).

        Upper limit depends on frequency: 10 V for frequency <= 10 MHz, 5 V for > 10 MHz.
        """,
        validator=strict_range,
        values=[2e-3, 10.0],
    )

    offset = Channel.control(
        ":SOUR:VOLT:OFFS?",
        ":SOUR:VOLT:OFFS %g",
        """Control the DC offset voltage in Volts (float strictly from -5 to 5).

        Effective range depends on amplitude: +/- (max_amplitude - amplitude) / 2.
        """,
        validator=strict_range,
        values=[-5.0, 5.0],
    )

    modulation_enabled = Channel.control(
        ":SOUR:MOD:STAT?",
        ":SOUR:MOD:STAT %d",
        """Control whether modulation output is enabled (bool).""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True,
    )

    modulation_type = Channel.control(
        ":SOUR:MOD:TYP?",
        ":SOUR:MOD:TYP %s",
        """Control the modulation type (str strictly in ``"AM"``, ``"FM"``, ``"PM"``).""",
        validator=strict_discrete_set,
        values=("AM", "FM", "PM"),
        cast=str,
    )

    am_depth = Channel.control(
        ":SOUR:MOD:AM:DEPT?",
        ":SOUR:MOD:AM:DEPT %g",
        """Control the AM modulation depth in percent (float strictly from 0 to 120).""",
        validator=strict_range,
        values=[0, 120],
    )

    am_frequency = Channel.control(
        ":SOUR:MOD:AM:INT:FREQ?",
        ":SOUR:MOD:AM:INT:FREQ %g",
        """Control the AM internal modulation frequency in Hz (float strictly 2e-3 to 1e6).""",
        validator=strict_range,
        values=[2e-3, 1e6],
    )

    am_function = Channel.control(
        ":SOUR:MOD:AM:INT:FUNC?",
        ":SOUR:MOD:AM:INT:FUNC %s",
        """Control the AM internal modulation waveform (str).

        Allowed values: ``"SIN"``, ``"SQU"``, ``"TRI"``, ``"UPR"``, ``"DNR"``, or ``"NOIS"``.
        """,
        validator=strict_discrete_set,
        values=MODULATION_FUNCTIONS,
        cast=str,
    )

    fm_deviation = Channel.control(
        ":SOUR:MOD:FM:DEV?",
        ":SOUR:MOD:FM:DEV %g",
        """Control the FM frequency deviation in Hz (float).""",
    )

    fm_frequency = Channel.control(
        ":SOUR:MOD:FM:INT:FREQ?",
        ":SOUR:MOD:FM:INT:FREQ %g",
        """Control the FM internal modulation frequency in Hz (float strictly 2e-3 to 1e6).""",
        validator=strict_range,
        values=[2e-3, 1e6],
    )

    fm_function = Channel.control(
        ":SOUR:MOD:FM:INT:FUNC?",
        ":SOUR:MOD:FM:INT:FUNC %s",
        """Control the FM internal modulation waveform (str).

        Allowed values: ``"SIN"``, ``"SQU"``, ``"TRI"``, ``"UPR"``, ``"DNR"``, or ``"NOIS"``.
        """,
        validator=strict_discrete_set,
        values=MODULATION_FUNCTIONS,
        cast=str,
    )

    pm_deviation = Channel.control(
        ":SOUR:MOD:PM:DEV?",
        ":SOUR:MOD:PM:DEV %g",
        """Control the PM phase deviation in degrees (float strictly from 0 to 360).""",
        validator=strict_range,
        values=[0, 360],
    )

    pm_frequency = Channel.control(
        ":SOUR:MOD:PM:INT:FREQ?",
        ":SOUR:MOD:PM:INT:FREQ %g",
        """Control the PM internal modulation frequency in Hz (float strictly 2e-3 to 1e6).""",
        validator=strict_range,
        values=[2e-3, 1e6],
    )

    pm_function = Channel.control(
        ":SOUR:MOD:PM:INT:FUNC?",
        ":SOUR:MOD:PM:INT:FUNC %s",
        """Control the PM internal modulation waveform (str).

        Allowed values: ``"SIN"``, ``"SQU"``, ``"TRI"``, ``"UPR"``, ``"DNR"``, or ``"NOIS"``.
        """,
        validator=strict_discrete_set,
        values=MODULATION_FUNCTIONS,
        cast=str,
    )


class RigolDHO900(DHOBase):
    """Represents the Rigol DHO900 Series Oscilloscope interface.

    DHO914(S) has 125 MHz bandwidth, while DHO924(S) has 250 MHz bandwidth. "S" represents
    the built-in 25 MHz arbitrary function generator (AFG) and Bode plot support.

    Refer to the Rigol DHO800/DHO900 Programming Guide for further details.

    :param adapter: Adapter instance to communicate with the instrument.
    :param str name: Name of the instrument.

    .. code-block:: python

        scope = RigolDHO924S(resource)
        scope.autoset()
        t, v = scope.get_waveform(channel=1)
        scope.shutdown()

    """

    BANDWIDTH: float = 125e6
    ANALOG_CHANNELS: int = 4
    DIGITAL_CHANNELS: int = 16
    MAX_SAMPLE_RATE: float = 1.25e9
    MAX_MEMORY_DEPTH: float = 50e6
    RESOLUTION_BITS: int = 12
    HAS_AFG: bool = False
    HAS_BODE_PLOT: bool = False
    AFG_MAX_FREQUENCY: float | None = None

    ch_1 = Instrument.ChannelCreator(DHO900Channel, 1)
    ch_2 = Instrument.ChannelCreator(DHO900Channel, 2)
    ch_3 = Instrument.ChannelCreator(DHO900Channel, 3)
    ch_4 = Instrument.ChannelCreator(DHO900Channel, 4)

    def __init__(self, adapter: AdapterType, name: str = "Rigol DHO900 Oscilloscope", **kwargs):
        super().__init__(adapter, name, **kwargs)

    # ================================================================== #
    #  ACQUISITION (DHO900 OVERRIDES)                                     #
    # ================================================================== #

    acquisition_memory_depth = Instrument.control(
        ":ACQ:MDEP?",
        ":ACQ:MDEP %s",
        """Control the memory depth per channel (up to 50 Mpts on DHO900).

        Accepted values: ``"AUTO"``, 1000, 10000, 100000, 1000000,
        10000000, 25000000, 50000000.
        """,
        validator=strict_discrete_set,
        values=[
            "AUTO",
            1_000,
            10_000,
            100_000,
            1_000_000,
            10_000_000,
            25_000_000,
            50_000_000,
        ],
    )

    # ================================================================== #
    #  TIMEBASE (DHO900 EXTENSIONS)                                       #
    # ================================================================== #

    timebase_mode_xy = Instrument.control(
        ":TIM:XY:ENAB?",
        ":TIM:XY:ENAB %d",
        """Control whether XY mode is enabled (bool).""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True,
    )

    timebase_href_mode = Instrument.control(
        ":TIM:HREF:MODE?",
        ":TIM:HREF:MODE %s",
        """Control the horizontal reference mode (str).

        Allowed values: ``"CENT"``, ``"LB"``, ``"RB"``, ``"TRIG"``, or ``"USER"``.
        """,
        validator=strict_discrete_set,
        values=["CENT", "LB", "RB", "TRIG", "USER"],
        cast=str,
    )

    timebase_href_position = Instrument.control(
        ":TIM:HREF:POS?",
        ":TIM:HREF:POS %d",
        """Control user-defined horizontal reference position (int truncated from -500 to 500).""",
        validator=truncated_range,
        values=[-500, 500],
        cast=int,
    )

    @property
    def timebase_configs(self) -> dict:
        """Get all timebase configurations as a dictionary."""
        tb_setup_list = (
            "timebase_mode",
            "timebase_mode_xy",
            "timebase_offset",
            "timebase_scale",
            "timebase_href_mode",
            "timebase_href_position",
        )
        return {setup: getattr(self, setup) for setup in tb_setup_list}

    # ================================================================== #
    #  TRIGGER (DHO900 EXTENSIONS)                                        #
    # ================================================================== #

    trigger_source = Instrument.control(
        ":TRIG:EDGE:SOUR?",
        ":TRIG:EDGE:SOUR %s",
        """Control the edge trigger source channel: ``"CHAN1"`` … ``"CHAN4"``,
        ``"D0"`` … ``"D15"``, ``"AC"``, or ``"EXT"``.""",
        validator=strict_discrete_set,
        values=[*ANALOG_SOURCE_CHANNELS, *DIGITAL_SOURCE_CHANNELS, "AC", "EXT"],
        cast=str,
    )

    trigger_pos = Instrument.measurement(
        ":TRIG:POS?",
        """Get the waveform trigger position (float).""",
    )

    # ================================================================== #
    #  SCREEN CAPTURE                                                     #
    # ================================================================== #

    def capture_screen(self, fn: str = "screen.png") -> None:
        """Save an image of the oscilloscope screen in PNG file format.

        :param str fn: Output filename, default to "screen.png".
        """
        old_fmt = self.ask(":WAV:FORM?").strip()
        if old_fmt != "BYTE":
            self.write(":WAV:FORM BYTE")
        self.write(":DISP:DATA? PNG")
        img_byte = self._read_byte_data()
        if old_fmt != "BYTE":
            self.write(f":WAV:FORM {old_fmt}")
        if img_byte:
            with open(fn, "wb") as f:
                f.write(img_byte)
                log.info("%s saved.", fn)
        else:
            log.warning("Empty data.")

    def _read_byte_data(self) -> bytes:
        """Read bytes data according to Rigol binary block data format.

        :return: Raw payload bytes extracted from the block.
        """
        header = self.read_bytes(2)
        try:
            assert header[0:1] == b"#"
        except AssertionError:
            log.error("Incorrect return format: %s.", header)
            self.adapter.flush_read_buffer()
            return header

        digits_count = int(header[1:2])
        data_count = int(self.read_bytes(digits_count))
        img_payload = self.read_bytes(data_count)
        # For Ethernet connection, a termination byte is appended and not counted in data_count.
        if hasattr(self.adapter, "resource_name") and "TCPIP" in self.adapter.resource_name:
            self.read_bytes(1)

        return img_payload

    # ================================================================== #
    #  SYSTEM (DHO900 EXTENSIONS)                                         #
    # ================================================================== #

    def reboot(self, timeout: int = 180, ping_interval: int = 3) -> None:
        """Send the system reset command and block until the oscilloscope reconnects.

        :param int timeout: Maximum wait time in seconds.
        :param int ping_interval: Polling interval for connection checks in seconds.
        """
        self.write(":SYST:RES")
        log.info("Waiting for oscilloscope to reboot and reconnect...")
        resource_name = getattr(self.adapter, "resource_name", "")
        try:
            self.adapter.close()
        except (OSError, VisaIOError) as err:
            log.debug("Ignoring error while closing adapter before reboot: %s", err)

        # Grace period for the oscilloscope to initiate shutdown
        # (prevents false positive connections from lingering sockets)
        time.sleep(5)

        if "TCPIP" in resource_name:
            self._wait_for_tcpip_reboot(resource_name, timeout, ping_interval)
            self.adapter.connection.open()
        else:
            self._wait_for_usb_reboot(timeout, ping_interval)

        self.adapter.connection.read_termination = "\n"
        self.adapter.connection.timeout = 5000
        log.info("Oscilloscope reboot and reconnection complete.")

    def _wait_for_tcpip_reboot(self, resource_name: str, timeout: int, interval: int) -> None:
        """Monitor Ethernet disconnection and reconnection via low-level TCP sockets.

        :param str resource_name: VISA resource name string.
        :param int timeout: Maximum timeout in seconds.
        :param int interval: Polling interval in seconds.
        """
        # Format examples: TCPIP0::192.168.1.100::5555::SOCKET or TCPIP::192.168.1.100::INSTR
        parts = resource_name.split("::")
        ip = parts[1]
        port = int(parts[2]) if len(parts) > 3 and parts[2].isdigit() else 5555

        start_time = time.time()

        # Phase A: Wait for the old connection to fully drop (confirms shutdown initiated)
        while (time.time() - start_time) < timeout:
            if not self._tcp_ping(ip, port, timeout=1):
                break
            time.sleep(1)

        # Phase B: Wait for the device to come back online (TCP socket reachable again)
        while (time.time() - start_time) < timeout:
            if self._tcp_ping(ip, port, timeout=2):
                # Allow extra 2 seconds for SCPI software initialization
                time.sleep(2)
                return
            time.sleep(interval)

        raise TimeoutError(
            f"Oscilloscope failed to come online via Ethernet ({ip}:{port}) "
            f"within {timeout} seconds."
        )

    def _wait_for_usb_reboot(self, timeout: int, interval: int) -> None:
        """Wait for USB interface reconnection after reboot.

        :param int timeout: Maximum timeout in seconds.
        :param int interval: Polling interval in seconds.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self.adapter.connection.open()
                return
            except (OSError, VisaIOError):
                time.sleep(interval)

        raise TimeoutError(f"Oscilloscope failed to come online via USB within {timeout} seconds.")

    @staticmethod
    def _tcp_ping(ip: str, port: int, timeout: float = 1) -> bool:
        """Send a low-level TCP probe to check if the target port is reachable.

        :param str ip: Target IP address.
        :param int port: Target TCP port.
        :param float timeout: Socket connect timeout in seconds.
        :return: True if port is reachable, False otherwise.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            s.connect((ip, port))
            s.shutdown(socket.SHUT_RDWR)
            return True
        except OSError:
            return False
        finally:
            s.close()

    @property
    def system_setup(self) -> bytes:
        """Control the raw data stream of the system setup file (bytes)."""
        self.write(":SYST:SET?")
        return self.read_bytes(-1)

    @system_setup.setter
    def system_setup(self, setup_string: bytes) -> None:
        self.write_bytes(b":SYST:SET " + setup_string)

    lock_fp_key = Instrument.control(
        ":SYST:LOCK?",
        ":SYST:LOCK %d",
        """Control front-panel and touch screen operation lock (bool).""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True,
    )

    beeper = Instrument.control(
        ":SYST:BEEP?",
        ":SYST:BEEP %d",
        """Control whether the beeper is enabled (bool).""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True,
    )

    version = Instrument.measurement(
        ":SYST:VERS?",
        """Get the SCPI version string of the oscilloscope (str).""",
        cast=str,
    )

    # ================================================================== #
    #  MEASUREMENTS (DHO900 EXTENSIONS)                                   #
    # ================================================================== #

    measure_source = Instrument.control(
        ":MEAS:SOUR?",
        ":MEAS:SOUR %s",
        """Control the measurement source channel (str).

        Allowed values: ``"CHAN1"`` … ``"CHAN4"``, ``"D0"`` … ``"D15"``,
        or ``"MATH1"`` … ``"MATH4"``.
        """,
        validator=strict_discrete_set,
        values=ALL_SOURCES,
        cast=str,
    )

    measure_all_of = Instrument.control(
        ":MEAS:AMS?",
        ":MEAS:AMS %s",
        """Control channel to display all measurement values on screen (str).

        Allowed values: ``"OFF"``, ``"CHAN1"`` … ``"CHAN4"``.
        """,
        validator=strict_discrete_set,
        values=("OFF", *ANALOG_SOURCE_CHANNELS),
        cast=str,
    )

    measure_statistic_enable = Instrument.control(
        ":MEAS:STAT:DISP?",
        ":MEAS:STAT:DISP %d",
        """Control whether the statistical function is enabled (bool).""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True,
    )

    def measure_statistic_reset(self) -> None:
        """Clear the history statistics data and restart statistics."""
        self.write(":MEAS:STAT:RES")


class RigolDHO914(RigolDHO900):
    """Represents the Rigol DHO914 125MHz 4-channel oscilloscope."""

    BANDWIDTH = 125e6
    HAS_AFG = False
    HAS_BODE_PLOT = False
    AFG_MAX_FREQUENCY = None

    def __init__(self, adapter: AdapterType, name: str = "Rigol DHO914 Oscilloscope", **kwargs):
        super().__init__(adapter, name, **kwargs)


class RigolDHO924(RigolDHO900):
    """Represents the Rigol DHO924 250MHz 4-channel oscilloscope."""

    BANDWIDTH = 250e6
    HAS_AFG = False
    HAS_BODE_PLOT = False
    AFG_MAX_FREQUENCY = None

    def __init__(self, adapter: AdapterType, name: str = "Rigol DHO924 Oscilloscope", **kwargs):
        super().__init__(adapter, name, **kwargs)


class RigolDHO914S(RigolDHO900):
    """Represents the Rigol DHO914S 125MHz 4-channel oscilloscope with signal generator."""

    BANDWIDTH = 125e6
    HAS_AFG = True
    HAS_BODE_PLOT = True
    AFG_MAX_FREQUENCY = 25e6

    afg = Instrument.ChannelCreator(DHO900AFGChannel, "")

    def __init__(self, adapter: AdapterType, name: str = "Rigol DHO914S Oscilloscope", **kwargs):
        super().__init__(adapter, name, **kwargs)


class RigolDHO924S(RigolDHO900):
    """Represents the Rigol DHO924S 250MHz 4-channel oscilloscope with signal generator."""

    BANDWIDTH = 250e6
    HAS_AFG = True
    HAS_BODE_PLOT = True
    AFG_MAX_FREQUENCY = 25e6

    afg = Instrument.ChannelCreator(DHO900AFGChannel, "")

    def __init__(self, adapter: AdapterType, name: str = "Rigol DHO924S Oscilloscope", **kwargs):
        super().__init__(adapter, name, **kwargs)
