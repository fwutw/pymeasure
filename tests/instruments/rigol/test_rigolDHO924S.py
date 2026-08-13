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

from pymeasure.test import expected_protocol
from pymeasure.instruments.rigol.rigol_dho900 import (
    Channel,
    RigolDHO900,
    RigolDHO914,
    RigolDHO924,
    RigolDHO914S,
    RigolDHO924S,
)


def test_channel_bools():
    assert Channel.BOOLS == {True: 1, False: 0}


def test_channel_bwlimit():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":CHAN1:BWL 20M", None),
            (b":channel1:BWL?", b"20M\n"),
            (b":channel1:BWL?", b"OFF\n"),
        ],
    ) as inst:
        inst.ch1.bwlimit = True
        assert inst.ch1.bwlimit is True
        assert inst.ch1.bwlimit is False


def test_channel_coupling():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":CHAN1:COUP AC", None),
            (b":channel1:COUP?", b"DC\n"),
        ],
    ) as inst:
        inst.ch1.coupling = "ac"
        assert inst.ch1.coupling == "dc"


def test_channel_display():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":CHAN1:DISP 1", None),
            (b":channel1:DISP?", b"1\n"),
        ],
    ) as inst:
        inst.ch1.display = True
        assert inst.ch1.display is True


def test_channel_invert():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":CHAN1:INV 1", None),
            (b":channel1:INV?", b"0\n"),
        ],
    ) as inst:
        inst.ch1.invert = True
        assert inst.ch1.invert is False


def test_channel_offset():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":CHAN1:OFFS 1.5", None),
            (b":channel1:OFFS?", b"1.5\n"),
        ],
    ) as inst:
        inst.ch1.offset = 1.5
        assert inst.ch1.offset == 1.5


def test_channel_scale():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":CHAN1:SCAL 0.5", None),
            (b":channel1:SCAL?", b"0.5\n"),
        ],
    ) as inst:
        inst.ch1.scale = 0.5
        assert inst.ch1.scale == 0.5


def test_channel_probe_attenuation():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":CHAN1:PROB 10", None),
            (b":channel1:PROB?", b"10\n"),
        ],
    ) as inst:
        inst.ch1.probe_attenuation = 10
        assert inst.ch1.probe_attenuation == 10.0


def test_channel_label_show():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":CHAN1:LAB:SHOW 1", None),
            (b":channel1:LAB:SHOW?", b"1\n"),
        ],
    ) as inst:
        inst.ch1.label_show = True
        assert inst.ch1.label_show is True


def test_channel_label():
    with expected_protocol(
        RigolDHO924S,
        [
            (b':CHAN1:LAB:CONT "TEST"', None),
            (b":channel1:LAB:CONT?", b'"TEST"\n'),
        ],
    ) as inst:
        inst.ch1.label = "TEST"
        assert inst.ch1.label == "TEST"


def test_channel_unit():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":CHAN1:UNIT VOLT", None),
            (b":channel1:UNIT?", b"VOLT\n"),
        ],
    ) as inst:
        inst.ch1.unit = "volt"
        assert inst.ch1.unit == "volt"


def test_channel_vernier():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":CHAN1:VERN 1", None),
            (b":channel1:VERN?", b"1\n"),
        ],
    ) as inst:
        inst.ch1.vernier = True
        assert inst.ch1.vernier is True


def test_channel_position():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":CHAN1:POS 2", None),
            (b":channel1:POS?", b"2\n"),
        ],
    ) as inst:
        inst.ch1.position = 2.0
        assert inst.ch1.position == 2.0


def test_channel_values():
    with expected_protocol(
        RigolDHO924S,
        [(b":channel1:SCAL?", b"0.25\n")],
    ) as inst:
        assert inst.ch1.values("SCAL?") == [0.25]


def test_channel_ask():
    with expected_protocol(
        RigolDHO924S,
        [(b":CHAN1:SCAL?", b"0.25\n")],
    ) as inst:
        assert inst.ch1.ask("SCAL?") == "0.25\n"


def test_channel_write():
    with expected_protocol(
        RigolDHO924S,
        [(b":CHAN1:SCAL 1", None)],
    ) as inst:
        inst.ch1.write("SCAL 1")


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
            (b':CHAN1:LAB:CONT "CH1"', None),
            (b":CHAN1:UNIT VOLT", None),
            (b":CHAN1:VERN 0", None),
            (b":CHAN1:POS 0", None),
        ],
    ) as inst:
        inst.ch1.setup(
            bwlimit=True,
            coupling="dc",
            display=True,
            invert=False,
            offset=0.1,
            scale=1.0,
            probe_attenuation=1,
            label_show=True,
            label="CH1",
            unit="volt",
            vernier=False,
            position=0.0,
        )


def test_channel_current_configuration():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":channel1:BWL?", b"20M\n"),
            (b":channel1:COUP?", b"DC\n"),
            (b":channel1:DISP?", b"1\n"),
            (b":channel1:INV?", b"0\n"),
            (b":channel1:OFFS?", b"0.5\n"),
            (b":channel1:SCAL?", b"1.0\n"),
            (b":channel1:PROB?", b"10\n"),
            (b":channel1:LAB:SHOW?", b"1\n"),
            (b":channel1:LAB:CONT?", b'"TEST"\n'),
            (b":channel1:UNIT?", b"VOLT\n"),
            (b":channel1:VERN?", b"0\n"),
            (b":channel1:POS?", b"0.0\n"),
        ],
    ) as inst:
        config = inst.ch1.current_configuration
        assert config == {
            "bwlimit": True,
            "coupling": "dc",
            "display": True,
            "invert": False,
            "offset": 0.5,
            "scale": 1.0,
            "probe_attenuation": 10.0,
            "label_show": True,
            "label": "TEST",
            "unit": "volt",
            "vernier": False,
            "position": 0.0,
        }


@pytest.mark.parametrize(
    "cls",
    [RigolDHO900, RigolDHO914, RigolDHO924, RigolDHO914S, RigolDHO924S],
)
def test_init_all_classes(cls):
    with expected_protocol(cls, []) as inst:
        assert isinstance(inst.ch1, Channel)
        assert isinstance(inst.ch2, Channel)
        assert isinstance(inst.ch3, Channel)
        assert isinstance(inst.ch4, Channel)
        assert inst.adapter.connection.timeout == 5000
        assert inst.adapter.connection.read_termination == "\n"
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


def test_exit_and_close():
    with expected_protocol(RigolDHO924S, []) as inst:
        inst.close()


def test_autoset():
    with expected_protocol(
        RigolDHO924S,
        [(b":AUT", None)],
    ) as inst:
        inst.autoset()


def test_ch():
    with expected_protocol(RigolDHO924S, []) as inst:
        assert inst.ch(1) == inst.ch1
        assert inst.ch(4) == inst.ch4
        with pytest.raises(ValueError):
            inst.ch(0)
        with pytest.raises(ValueError):
            inst.ch(5)


def test_timebase_mode():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":TIM:MODE MAIN", None),
            (b":TIM:MODE?", b"MAIN\n"),
        ],
    ) as inst:
        inst.timebase_mode = "main"
        assert inst.timebase_mode == "main"


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


def test_timebase_offset():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":TIM 0.001", None),
            (b":TIM?", b"0.001\n"),
        ],
    ) as inst:
        inst.timebase_offset = 0.001
        assert inst.timebase_offset == 0.001


def test_timebase_scale():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":TIM:SCAL 1e-06", None),
            (b":TIM:SCAL?", b"1e-06\n"),
        ],
    ) as inst:
        inst.timebase_scale = 1e-6
        assert inst.timebase_scale == 1e-6


def test_timebase_href_mode():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":TIM:HREF:MODE CENT", None),
            (b":TIM:HREF:MODE?", b"CENT\n"),
        ],
    ) as inst:
        inst.timebase_href_mode = "center"
        assert inst.timebase_href_mode == "center"


def test_timebase_href_position():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":TIM:HREF:POS 100", None),
            (b":TIM:HREF:POS?", b"100\n"),
        ],
    ) as inst:
        inst.timebase_href_position = 100
        assert inst.timebase_href_position == 100


def test_timebase_configs():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":TIM:MODE?", b"MAIN\n"),
            (b":TIM:XY:ENAB?", b"0\n"),
            (b":TIM?", b"0.0\n"),
            (b":TIM:SCAL?", b"0.001\n"),
            (b":TIM:HREF:MODE?", b"CENT\n"),
            (b":TIM:HREF:POS?", b"0\n"),
        ],
    ) as inst:
        config = inst.timebase_configs
        assert config == {
            "timebase_mode": "main",
            "timebase_mode_xy": False,
            "timebase_offset": 0.0,
            "timebase_scale": 0.001,
            "timebase_href_mode": "center",
            "timebase_href_position": 0,
        }


def test_acquisition_type():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":ACQ:TYPE AVER", None),
            (b":ACQ:TYPE?", b"AVER\n"),
        ],
    ) as inst:
        inst.acquisition_type = "average"
        assert inst.acquisition_type == "average"


def test_memory_depth():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":ACQ:MDEP 10k", None),
            (b":ACQ:MDEP?", b"10k\n"),
        ],
    ) as inst:
        inst.memory_depth = "10k"
        assert inst.memory_depth == "10k"


def test_sample_rate():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":ACQ:SRAT 1000000000.0", None),
            (b":ACQ:SRAT?", b"1e+09\n"),
        ],
    ) as inst:
        inst.sample_rate = 1e9
        assert inst.sample_rate == 1e9


def test_run():
    with expected_protocol(
        RigolDHO924S,
        [(b":RUN", None)],
    ) as inst:
        inst.run()


def test_stop():
    with expected_protocol(
        RigolDHO924S,
        [(b":STOP", None)],
    ) as inst:
        inst.stop()


def test_single():
    with expected_protocol(
        RigolDHO924S,
        [(b":SING", None)],
    ) as inst:
        inst.single()


def test_force_trigger():
    with expected_protocol(
        RigolDHO924S,
        [(b":TFOR", None)],
    ) as inst:
        inst.force_trigger()


def test_waveform_source():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":WAV:SOUR CHAN1", None),
            (b":WAV:SOUR?", b"CHAN1\n"),
        ],
    ) as inst:
        inst.waveform_source = "ch1"
        assert inst.waveform_source == "ch1"
        assert RigolDHO900.SOURCE.ch1.value == "CHAN1"


def test_waveform_mode():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":WAV:MODE NORM", None),
            (b":WAV:MODE?", b"NORM\n"),
        ],
    ) as inst:
        inst.waveform_mode = "normal"
        assert inst.waveform_mode == "normal"


def test_waveform_format():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":WAV:FORM ASC", None),
            (b":WAV:FORM?", b"ASC\n"),
        ],
    ) as inst:
        inst.waveform_format = "ascii"
        assert inst.waveform_format == "ascii"


def test_waveform_points():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":WAV:POIN 1000", None),
            (b":WAV:POIN?", b"1000\n"),
        ],
    ) as inst:
        inst.waveform_points = 1000
        assert inst.waveform_points == 1000


def test_waveform_measurements():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":WAV:XINC?", b"1e-6\n"),
            (b":WAV:XREF?", b"0\n"),
            (b":WAV:XOR?", b"-0.005\n"),
            (b":WAV:YINC?", b"0.04\n"),
            (b":WAV:YREF?", b"128\n"),
            (b":WAV:YOR?", b"0\n"),
        ],
    ) as inst:
        assert inst.xinc == 1e-6
        assert inst.xref == 0.0
        assert inst.xo == -0.005
        assert inst.yinc == 0.04
        assert inst.yref == 128.0
        assert inst.yo == 0.0


def test_waveform_preamble():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":WAV:PRE?", b"2,0,1000,1,1e-6,-0.005,0,0.04,0,128\n"),
            (b":WAV:PRE?", b"2,0,1000,1,1e-6,-0.005,0,0.04,0,128\n"),
        ],
    ) as inst:
        preamble1 = inst.waveform_preamble
        preamble2 = inst._waveform_preamble()
        expected = {
            "format": "ASCII",
            "type": "NORMAL",
            "points": 1000,
            "count": 1,
            "xincrement": 1e-6,
            "xorigin": -0.005,
            "xreference": 0,
            "yincrement": 0.04,
            "yorigin": 0.0,
            "yreference": 128,
        }
        assert preamble1 == expected
        assert preamble2 == expected


def test_waveform_data_ascii():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":WAV:MODE?", b"NORM\n"),
            (b":WAV:FORM ASC", None),
            (b":WAV:DATA?", b"1.0,2.0,3.0\n"),
        ],
    ) as inst:
        assert inst.waveform_data == [1.0, 2.0, 3.0]


def test_waveform_data_raw_stop():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":WAV:MODE?", b"RAW\n"),
            (b":TRIG:STAT?", b"RUN\n"),
            (b":STOP", None),
            (b":WAV:FORM ASC", None),
            (b":WAV:DATA?", b"1.0,2.0\n"),
        ],
    ) as inst:
        assert inst.waveform_data_from("ascii") == [1.0, 2.0]


def test_waveform_data_byte():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":WAV:MODE?", b"NORM\n"),
            (b":WAV:FORM BYTE", None),
            (b":WAV:DATA?", b"#14\x80\x81\x82\x83"),
            (b":WAV:YOR?", b"0\n"),
            (b":WAV:YREF?", b"128\n"),
            (b":WAV:YINC?", b"0.1\n"),
            (b":WAV:POIN?", b"4\n"),
        ],
    ) as inst:
        data = inst.waveform_data_from("byte")
        assert len(data) == 4
        assert data[0] == pytest.approx((128 - 0 - 128) * 0.1)
        assert data[1] == pytest.approx((129 - 0 - 128) * 0.1)


def test_waveform_data_word():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":WAV:MODE?", b"NORM\n"),
            (b":WAV:FORM WORD", None),
            (b":WAV:DATA?", b"#14\x80\x00\x81\x00"),
            (b":WAV:YOR?", b"0\n"),
            (b":WAV:YREF?", b"128\n"),
            (b":WAV:YINC?", b"0.1\n"),
            (b":WAV:POIN?", b"2\n"),
        ],
    ) as inst:
        data = inst.waveform_data_from("word")
        assert len(data) == 2
        assert data[0] == pytest.approx((128 - 0 - 128) * 0.1)
        assert data[1] == pytest.approx((129 - 0 - 128) * 0.1)


def test_waveform_data_invalid_fmt():
    with expected_protocol(RigolDHO924S, []) as inst:
        assert inst.waveform_data_from("invalid") == []


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
    fn = tmp_path / "test_screen_byte.png"
    with expected_protocol(
        RigolDHO924S,
        [
            (b":WAV:FORM?", b"BYTE\n"),
            (b":DISP:DATA? PNG", b"#14PNGD"),
        ],
    ) as inst:
        inst.capture_screen(str(fn))
        assert fn.read_bytes() == b"PNGD"


def test_read_byte_data_invalid_header():
    with expected_protocol(
        RigolDHO924S,
        [(None, b"XX")],
    ) as inst:
        res = inst._read_byte_data()
        assert res == b"XX"


def test_read_byte_data_tcpip():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":DISP:DATA? PNG", b"#14PNGD\n"),
        ],
    ) as inst:
        inst.adapter.resource_name = "TCPIP0::192.168.1.100::INSTR"
        inst.write(":DISP:DATA? PNG")
        data = inst._read_byte_data()
        assert data == b"PNGD"


def test_capture_screen_empty(tmp_path):
    fn = tmp_path / "test_screen_empty.png"
    with expected_protocol(
        RigolDHO924S,
        [
            (b":WAV:FORM?", b"BYTE\n"),
            (b":DISP:DATA? PNG", None),
        ],
    ) as inst:
        with patch.object(inst, "_read_byte_data", return_value=b""):
            inst.capture_screen(str(fn))
            assert not fn.exists()


def test_waveform_data_byte_size_mismatch():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":WAV:MODE?", b"NORM\n"),
            (b":WAV:FORM BYTE", None),
            (b":WAV:DATA?", b"#12\x80\x81"),
            (b":WAV:YOR?", b"0\n"),
            (b":WAV:YREF?", b"128\n"),
            (b":WAV:YINC?", b"0.1\n"),
            (b":WAV:POIN?", b"4\n"),
        ],
    ) as inst:
        with pytest.raises(AssertionError):
            inst.waveform_data_from("byte")


def test_system_reset():
    with expected_protocol(
        RigolDHO924S,
        [(b"*RST", None)],
    ) as inst:
        inst.reset()


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
    with expected_protocol(RigolDHO924S, []) as inst:
        with patch.object(inst, "_tcp_ping", side_effect=[True, False, False, True]) as mock_ping:
            inst._wait_for_tcpip_reboot("TCPIP::192.168.1.100::5555::SOCKET", timeout=10, interval=0.1)
            assert mock_ping.call_count >= 2


@patch("pymeasure.instruments.rigol.rigol_dho900.time.sleep")
@patch("pymeasure.instruments.rigol.rigol_dho900.time.time")
def test_wait_for_tcpip_reboot_timeout(mock_time, mock_sleep):
    mock_time.side_effect = [0, 10, 20]
    with expected_protocol(RigolDHO924S, []) as inst:
        with patch.object(inst, "_tcp_ping", return_value=False):
            with pytest.raises(TimeoutError, match="failed to come online via Ethernet"):
                inst._wait_for_tcpip_reboot("TCPIP::192.168.1.100::INSTR", timeout=5, interval=0.1)


@patch("pymeasure.instruments.rigol.rigol_dho900.time.sleep")
@patch("pymeasure.instruments.rigol.rigol_dho900.time.time")
def test_wait_for_usb_reboot_timeout(mock_time, mock_sleep):
    mock_time.side_effect = [0, 10, 20]
    with expected_protocol(RigolDHO924S, []) as inst:
        inst.adapter.connection.open.side_effect = Exception("USB open error")
        with pytest.raises(TimeoutError, match="failed to come online via USB"):
            inst._wait_for_usb_reboot(timeout=5, interval=0.1)


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


def test_check_errors():
    with expected_protocol(
        RigolDHO924S,
        [(b":SYST:ERR?", b'0,"No error"\n')],
    ) as inst:
        assert inst.check_errors() == '0,"No error"\n'


def test_system_setup():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":SYST:SET?", b"SETUP_DATA"),
            (b":SYST:SET SETUP_DATA", None),
        ],
    ) as inst:
        data = inst.system_setup
        assert data == b"SETUP_DATA"
        inst.system_setup = b"SETUP_DATA"


def test_trigger_status():
    with expected_protocol(
        RigolDHO924S,
        [(b":TRIG:STAT?", b"RUN\n")],
    ) as inst:
        assert inst.trigger_status == "RUN"


def test_trigger_mode():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":TRIG:MODE EDGE", None),
            (b":TRIG:MODE?", b"EDGE\n"),
        ],
    ) as inst:
        inst.trigger_mode = "EDGE"
        assert inst.trigger_mode == "EDGE"


def test_trigger_pos():
    with expected_protocol(
        RigolDHO924S,
        [(b":TRIG:POS?", b"0.001\n")],
    ) as inst:
        assert inst.trigger_pos == 0.001


def test_trigger_edge_level():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":TRIG:EDGE:LEV 1.5", None),
            (b":TRIG:EDGE:LEV?", b"1.5\n"),
        ],
    ) as inst:
        inst.trigger_edge_level = 1.5
        assert inst.trigger_edge_level == 1.5


def test_display_clear():
    with expected_protocol(
        RigolDHO924S,
        [(b":DISP:CLE", None)],
    ) as inst:
        inst.display_clear()


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
        ],
    ) as inst:
        inst.beeper = True
        assert inst.beeper is True


def test_measure_source():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":MEAS:SOUR CHAN1", None),
            (b":MEAS:SOUR?", b"CHAN1\n"),
        ],
    ) as inst:
        inst.measure_source = "ch1"
        assert inst.measure_source == "ch1"


def test_measure_clear():
    with expected_protocol(
        RigolDHO924S,
        [(b":MEAS:CLE", None)],
    ) as inst:
        inst.measure_clear()


def test_measure_all_of():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":MEAS:AMS CHAN1", None),
            (b":MEAS:AMS?", b"CHAN1\n"),
        ],
    ) as inst:
        inst.measure_all_of = "ch1"
        assert inst.measure_all_of == "ch1"


def test_measure_statistic_enable():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":MEAS:STAT:DISP 1", None),
            (b":MEAS:STAT:DISP?", b"1\n"),
        ],
    ) as inst:
        inst.measure_statistic_enable = True
        assert inst.measure_statistic_enable is True


def test_measure_statistic_reset():
    with expected_protocol(
        RigolDHO924S,
        [(b":MEAS:STAT:RES", None)],
    ) as inst:
        inst.measure_statistic_reset()


def test_measure():
    with expected_protocol(
        RigolDHO924S,
        [
            (b":MEAS:ITEM VMAX", None),
            (b":MEAS:ITEM? VMAX", b"3.3\n"),
            (b":MEAS:ITEM VPP,CHAN1", None),
            (b":MEAS:ITEM? VPP,CHAN1", b"2.0\n"),
            (b":MEAS:ITEM RRD,CHAN1,CHAN2", None),
            (b":MEAS:ITEM? RRD,CHAN1,CHAN2", b"0.001\n"),
        ],
    ) as inst:
        assert inst.measure(RigolDHO900.MEASITEMS.Vmax) == 3.3
        assert inst.measure(RigolDHO900.MEASITEMS.Vpp, RigolDHO900.SOURCE.ch1) == 2.0
        assert (
            inst.measure(
                RigolDHO900.MEASITEMS.delay_rise_rise,
                RigolDHO900.SOURCE.ch1,
                RigolDHO900.SOURCE.ch2,
            )
            == 0.001
        )


def test_version():
    with expected_protocol(
        RigolDHO924S,
        [(b":SYST:VERS?", b"00.01.02\n")],
    ) as inst:
        assert inst.version == "00.01.02\n"


def test_id():
    with expected_protocol(
        RigolDHO924S,
        [(b"*IDN?", b"RIGOL TECHNOLOGIES,DHO924S,DHO9A123456789,00.01.02\n")],
    ) as inst:
        assert inst.id == "RIGOL TECHNOLOGIES,DHO924S,DHO9A123456789,00.01.02\n"


def test_context_manager():
    with expected_protocol(RigolDHO924S, []) as inst:
        with inst as scope:
            assert scope == inst
