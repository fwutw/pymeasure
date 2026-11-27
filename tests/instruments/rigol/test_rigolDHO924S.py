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
from unittest.mock import MagicMock, patch

import pytest

from pymeasure.instruments.rigol.rigol_dho900 import (
    DHO900Channel,
    RigolDHO900,
    RigolDHO914,
    RigolDHO914S,
    RigolDHO924,
    RigolDHO924S,
)
from pymeasure.instruments.rigol.rigol_dho_base import DHOBase, DHOBaseChannel
from pymeasure.test import expected_protocol

# ================================================================== #
#  INITIALIZATION & MODEL SPECIFICATIONS                              #
# ================================================================== #


@pytest.mark.parametrize(
    "cls",
    [RigolDHO900, RigolDHO914, RigolDHO924, RigolDHO914S, RigolDHO924S],
)
def test_init_all_classes(cls):
    with expected_protocol(cls, []) as inst:
        assert isinstance(inst, DHOBase)
        for ch in (inst.ch_1, inst.ch_2, inst.ch_3, inst.ch_4):
            assert isinstance(ch, DHO900Channel)
            assert isinstance(ch, DHOBaseChannel)
        assert inst.ANALOG_CHANNELS == 4
        assert inst.DIGITAL_CHANNELS == 16
        assert inst.MAX_SAMPLE_RATE == 1.25e9
        assert inst.MAX_MEMORY_DEPTH == 50e6
        assert inst.RESOLUTION_BITS == 12


def test_model_specifications():
    assert RigolDHO914.BANDWIDTH == 125e6
    assert RigolDHO914.HAS_AFG is False
    assert RigolDHO914.HAS_BODE_PLOT is False
    assert RigolDHO914.AFG_MAX_FREQUENCY is None

    assert RigolDHO924.BANDWIDTH == 250e6
    assert RigolDHO924.HAS_AFG is False
    assert RigolDHO924.HAS_BODE_PLOT is False
    assert RigolDHO924.AFG_MAX_FREQUENCY is None

    assert RigolDHO914S.BANDWIDTH == 125e6
    assert RigolDHO914S.HAS_AFG is True
    assert RigolDHO914S.HAS_BODE_PLOT is True
    assert RigolDHO914S.AFG_MAX_FREQUENCY == 25e6

    assert RigolDHO924S.BANDWIDTH == 250e6
    assert RigolDHO924S.HAS_AFG is True
    assert RigolDHO924S.HAS_BODE_PLOT is True
    assert RigolDHO924S.AFG_MAX_FREQUENCY == 25e6


# ================================================================== #
#  DHO900 CHANNEL OVERRIDES & EXTENSIONS                              #
# ================================================================== #


def test_channel_bandwidth_limit():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":CHAN1:BWL 20M", None),
            (b":CHAN1:BWL?", b"20M\n"),
            (b":CHAN1:BWL OFF", None),
            (b":CHAN1:BWL?", b"OFF\n"),
        ],
    ) as inst:
        inst.ch_1.bandwidth_limit = "20M"
        assert inst.ch_1.bandwidth_limit == "20M"
        inst.ch_1.bandwidth_limit = "OFF"
        assert inst.ch_1.bandwidth_limit == "OFF"
        with pytest.raises(ValueError):
            inst.ch_1.bandwidth_limit = "100M"


def test_channel_vernier():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":CHAN1:VERN 1", None),
            (b":CHAN1:VERN?", b"1\n"),
            (b":CHAN1:VERN 0", None),
            (b":CHAN1:VERN?", b"0\n"),
        ],
    ) as inst:
        inst.ch_1.vernier = True
        assert inst.ch_1.vernier is True
        inst.ch_1.vernier = False
        assert inst.ch_1.vernier is False


def test_channel_position():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":CHAN2:POS 1.25", None),
            (b":CHAN2:POS?", b"1.25\n"),
        ],
    ) as inst:
        inst.ch_2.position = 1.25
        assert inst.ch_2.position == pytest.approx(1.25)


def test_channel_setup():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":CHAN1:BWL 20M", None),
            (b":CHAN1:COUP DC", None),
            (b":CHAN1:DISP 1", None),
            (b":CHAN1:INV 0", None),
            (b":CHAN1:OFFS 0.1", None),
            (b":CHAN1:SCAL 1", None),
            (b":CHAN1:PROB 1", None),
            (b":CHAN1:LAB:SHOW 1", None),
            (b":CHAN1:LAB:CONT CH1", None),
            (b":CHAN1:UNIT VOLT", None),
            (b":CHAN1:VERN 0", None),
            (b":CHAN1:POS 0", None),
        ],
    ) as inst:
        inst.ch_1.setup(
            bandwidth_limit="20M",
            coupling="DC",
            display_enabled=True,
            invert=False,
            offset=0.1,
            scale=1.0,
            probe=1,
            label_enabled=True,
            label="CH1",
            units="VOLT",
            vernier=False,
            position=0.0,
        )


def test_channel_current_configuration():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":CHAN1:BWL?", b"20M\n"),
            (b":CHAN1:COUP?", b"DC\n"),
            (b":CHAN1:DISP?", b"1\n"),
            (b":CHAN1:INV?", b"0\n"),
            (b":CHAN1:OFFS?", b"0.5\n"),
            (b":CHAN1:SCAL?", b"1.0\n"),
            (b":CHAN1:PROB?", b"10\n"),
            (b":CHAN1:LAB:SHOW?", b"1\n"),
            (b":CHAN1:LAB:CONT?", b"TEST\n"),
            (b":CHAN1:UNIT?", b"VOLT\n"),
            (b":CHAN1:VERN?", b"0\n"),
            (b":CHAN1:POS?", b"0.0\n"),
        ],
    ) as inst:
        config = inst.ch_1.current_configuration
        assert config == {
            "bandwidth_limit": "20M",
            "coupling": "DC",
            "display_enabled": True,
            "invert": False,
            "offset": 0.5,
            "scale": 1.0,
            "probe": 10.0,
            "label_enabled": True,
            "label": "TEST",
            "units": "VOLT",
            "vernier": False,
            "position": 0.0,
        }


# ================================================================== #
#  ACQUISITION (DHO900 OVERRIDES)                                     #
# ================================================================== #


def test_acquisition_memory_depth_dho900_limit():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":ACQ:MDEP AUTO", None),
            (b":ACQ:MDEP 50000000", None),
            (b":ACQ:MDEP?", b"50000000\n"),
        ],
    ) as inst:
        inst.acquisition_memory_depth = "AUTO"
        inst.acquisition_memory_depth = 50_000_000
        assert inst.acquisition_memory_depth == 50_000_000
        with pytest.raises(ValueError):
            inst.acquisition_memory_depth = 100_000_000


# ================================================================== #
#  TIMEBASE (DHO900 EXTENSIONS)                                       #
# ================================================================== #


def test_timebase_mode_xy():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":TIM:XY:ENAB 1", None),
            (b":TIM:XY:ENAB?", b"1\n"),
        ],
    ) as inst:
        inst.timebase_mode_xy = True
        assert inst.timebase_mode_xy is True


def test_timebase_href_mode():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":TIM:HREF:MODE CENT", None),
            (b":TIM:HREF:MODE?", b"CENT\n"),
            (b":TIM:HREF:MODE LB", None),
            (b":TIM:HREF:MODE?", b"LB\n"),
            (b":TIM:HREF:MODE USER", None),
            (b":TIM:HREF:MODE?", b"USER\n"),
        ],
    ) as inst:
        inst.timebase_href_mode = "CENT"
        assert inst.timebase_href_mode == "CENT"
        inst.timebase_href_mode = "LB"
        assert inst.timebase_href_mode == "LB"
        inst.timebase_href_mode = "USER"
        assert inst.timebase_href_mode == "USER"
        with pytest.raises(ValueError):
            inst.timebase_href_mode = "INVALID"


def test_timebase_href_position():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":TIM:HREF:POS 100", None),
            (b":TIM:HREF:POS?", b"100\n"),
            (b":TIM:HREF:POS 500", None),
            (b":TIM:HREF:POS -500", None),
        ],
    ) as inst:
        inst.timebase_href_position = 100
        assert inst.timebase_href_position == 100
        inst.timebase_href_position = 999
        inst.timebase_href_position = -999


def test_timebase_configs():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":TIM:MODE?", b"MAIN\n"),
            (b":TIM:XY:ENAB?", b"0\n"),
            (b":TIM:MAIN:OFFS?", b"0.0\n"),
            (b":TIM:MAIN:SCAL?", b"0.001\n"),
            (b":TIM:HREF:MODE?", b"CENT\n"),
            (b":TIM:HREF:POS?", b"0\n"),
        ],
    ) as inst:
        assert inst.timebase_configs == {
            "timebase_mode": "MAIN",
            "timebase_mode_xy": False,
            "timebase_offset": 0.0,
            "timebase_scale": 0.001,
            "timebase_href_mode": "CENT",
            "timebase_href_position": 0,
        }


# ================================================================== #
#  TRIGGER (DHO900 EXTENSIONS)                                        #
# ================================================================== #


def test_trigger_source_digital_channels():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":TRIG:EDGE:SOUR D0", None),
            (b":TRIG:EDGE:SOUR?", b"D0\n"),
            (b":TRIG:EDGE:SOUR D15", None),
            (b":TRIG:EDGE:SOUR?", b"D15\n"),
        ],
    ) as inst:
        inst.trigger_source = "D0"
        assert inst.trigger_source == "D0"
        inst.trigger_source = "D15"
        assert inst.trigger_source == "D15"


def test_trigger_pos():
    with expected_protocol(
        RigolDHO924S,
        [(b":TRIG:POS?", b"128\n")],
    ) as inst:
        assert inst.trigger_pos == 128.0


# ================================================================== #
#  SCREEN CAPTURE                                                     #
# ================================================================== #


def test_capture_screen_switch_format(tmp_path):
    fn = tmp_path / "test_screen.png"
    with expected_protocol(
        RigolDHO924S,
        [
            (b":WAV:FORM?", b"ASC\n"),
            (b":WAV:FORM BYTE", None),
            (b":DISP:DATA? PNG", b"#14PNGD"),
            (b":WAV:FORM ASC", None),
        ],
    ) as inst:
        inst.capture_screen(str(fn))
        assert fn.read_bytes() == b"PNGD"


def test_capture_screen_byte_format(tmp_path):
    fn = tmp_path / "test_screen2.png"
    with expected_protocol(
        RigolDHO924S,
        [
            (b":WAV:FORM?", b"BYTE\n"),
            (b":DISP:DATA? PNG", b"#14PNGD"),
        ],
    ) as inst:
        inst.capture_screen(str(fn))
        assert fn.read_bytes() == b"PNGD"


def test_capture_screen_empty(tmp_path):
    fn = tmp_path / "test_screen_empty.png"
    with (
        expected_protocol(
            RigolDHO924S,
            [
                (b":WAV:FORM?", b"BYTE\n"),
                (b":DISP:DATA? PNG", None),
            ],
        ) as inst,
        patch.object(inst, "_read_byte_data", return_value=b""),
    ):
        inst.capture_screen(str(fn))
        assert not fn.exists()


def test_read_byte_data_invalid_header():
    with expected_protocol(
        RigolDHO924S,
        [(None, b"XX")],
    ) as inst:
        assert inst._read_byte_data() == b"XX"


def test_read_byte_data_tcpip():
    with expected_protocol(
        RigolDHO924S,
        [(b":DISP:DATA? PNG", b"#14PNGD\n")],
    ) as inst:
        inst.adapter.resource_name = "TCPIP0::192.168.1.100::INSTR"
        inst.write(":DISP:DATA? PNG")
        assert inst._read_byte_data() == b"PNGD"


# ================================================================== #
#  SYSTEM (DHO900 EXTENSIONS)                                         #
# ================================================================== #


@patch("pymeasure.instruments.rigol.rigol_dho900.time.sleep")
def test_system_reboot_usb(mock_sleep):
    with expected_protocol(
        RigolDHO924S,
        [(b":SYST:RES", None)],
    ) as inst:
        inst.reboot()
        assert inst.adapter.connection.read_termination == "\n"
        assert inst.adapter.connection.timeout == 5000


@patch("pymeasure.instruments.rigol.rigol_dho900.time.sleep")
@patch.object(RigolDHO924S, "_wait_for_tcpip_reboot")
def test_system_reboot_tcpip(mock_wait_tcpip, mock_sleep):
    with expected_protocol(
        RigolDHO924S,
        [(b":SYST:RES", None)],
    ) as inst:
        inst.adapter.resource_name = "TCPIP0::192.168.1.100::INSTR"
        inst.reboot()
        mock_wait_tcpip.assert_called_once_with("TCPIP0::192.168.1.100::INSTR", 180, 3)
        assert inst.adapter.connection.read_termination == "\n"
        assert inst.adapter.connection.timeout == 5000


@patch("pymeasure.instruments.rigol.rigol_dho900.time.sleep")
def test_wait_for_tcpip_reboot(mock_sleep):
    with (
        expected_protocol(RigolDHO924S, []) as inst,
        patch.object(inst, "_tcp_ping", side_effect=[True, False, False, True]) as mock_ping,
    ):
        inst._wait_for_tcpip_reboot("TCPIP::192.168.1.100::5555::SOCKET", timeout=10, interval=1)
        assert mock_ping.call_count >= 2


@patch("pymeasure.instruments.rigol.rigol_dho900.time.sleep")
@patch("pymeasure.instruments.rigol.rigol_dho900.time.time")
def test_wait_for_tcpip_reboot_timeout(mock_time, mock_sleep):
    mock_time.side_effect = [0, 10, 20]
    with (
        expected_protocol(RigolDHO924S, []) as inst,
        patch.object(inst, "_tcp_ping", return_value=False),
        pytest.raises(TimeoutError, match="failed to come online via Ethernet"),
    ):
        inst._wait_for_tcpip_reboot("TCPIP::192.168.1.100::INSTR", timeout=5, interval=1)


@patch("pymeasure.instruments.rigol.rigol_dho900.time.sleep")
@patch("pymeasure.instruments.rigol.rigol_dho900.time.time")
def test_wait_for_usb_reboot_timeout(mock_time, mock_sleep):
    mock_time.side_effect = [0, 10, 20]
    with expected_protocol(RigolDHO924S, []) as inst:
        inst.adapter.connection.open.side_effect = OSError("USB open error")
        with pytest.raises(TimeoutError, match="failed to come online via USB"):
            inst._wait_for_usb_reboot(timeout=5, interval=1)


@patch("pymeasure.instruments.rigol.rigol_dho900.socket.socket")
def test_tcp_ping_success(mock_socket_cls):
    mock_socket = MagicMock()
    mock_socket_cls.return_value = mock_socket
    assert RigolDHO900._tcp_ping("192.168.1.100", 5555, timeout=1) is True
    mock_socket.connect.assert_called_once_with(("192.168.1.100", 5555))
    mock_socket.close.assert_called_once()


@patch("pymeasure.instruments.rigol.rigol_dho900.socket.socket")
def test_tcp_ping_failure(mock_socket_cls):
    mock_socket = MagicMock()
    mock_socket.connect.side_effect = OSError("Connection refused")
    mock_socket_cls.return_value = mock_socket
    assert RigolDHO900._tcp_ping("192.168.1.100", 5555, timeout=1) is False
    mock_socket.close.assert_called_once()


def test_system_setup():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":SYST:SET?", b"SETUP_DATA"),
            (b":SYST:SET SETUP_DATA", None),
        ],
    ) as inst:
        assert inst.system_setup == b"SETUP_DATA"
        inst.system_setup = b"SETUP_DATA"


def test_lock_fp_key():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":SYST:LOCK 1", None),
            (b":SYST:LOCK?", b"1\n"),
        ],
    ) as inst:
        inst.lock_fp_key = True
        assert inst.lock_fp_key is True


def test_beeper():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":SYST:BEEP 1", None),
            (b":SYST:BEEP?", b"1\n"),
            (b":SYST:BEEP 0", None),
            (b":SYST:BEEP?", b"0\n"),
        ],
    ) as inst:
        inst.beeper = True
        assert inst.beeper is True
        inst.beeper = False
        assert inst.beeper is False


def test_version():
    with expected_protocol(
        RigolDHO924S,
        [(b":SYST:VERS?", b"1999.0\n")],
    ) as inst:
        assert inst.version == "1999.0"


# ================================================================== #
#  MEASUREMENTS (DHO900 EXTENSIONS)                                   #
# ================================================================== #


def test_measure_source():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":MEAS:SOUR CHAN1", None),
            (b":MEAS:SOUR?", b"CHAN1\n"),
            (b":MEAS:SOUR D0", None),
            (b":MEAS:SOUR?", b"D0\n"),
            (b":MEAS:SOUR MATH1", None),
            (b":MEAS:SOUR?", b"MATH1\n"),
        ],
    ) as inst:
        inst.measure_source = "CHAN1"
        assert inst.measure_source == "CHAN1"
        inst.measure_source = "D0"
        assert inst.measure_source == "D0"
        inst.measure_source = "MATH1"
        assert inst.measure_source == "MATH1"


def test_measure_all_of():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":MEAS:AMS CHAN2", None),
            (b":MEAS:AMS?", b"CHAN2\n"),
            (b":MEAS:AMS OFF", None),
            (b":MEAS:AMS?", b"OFF\n"),
        ],
    ) as inst:
        inst.measure_all_of = "CHAN2"
        assert inst.measure_all_of == "CHAN2"
        inst.measure_all_of = "OFF"
        assert inst.measure_all_of == "OFF"


def test_measure_statistic():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":MEAS:STAT:DISP 1", None),
            (b":MEAS:STAT:DISP?", b"1\n"),
            (b":MEAS:STAT:RES", None),
        ],
    ) as inst:
        inst.measure_statistic_enable = True
        assert inst.measure_statistic_enable is True
        inst.measure_statistic_reset()
