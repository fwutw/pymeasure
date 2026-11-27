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
"""Live hardware tests for Rigol DHO900 series oscilloscopes (e.g. DHO924S).

Run against a connected instrument::

    pytest tests/instruments/rigol/test_rigol_dho900_with_device.py \
        --device-address "TCPIP0::192.168.1.100::INSTR"

To record real hardware communication and generate protocol tests using
:class:`pymeasure.generator.Generator`, set ``PYMEASURE_GENERATE_PROTOCOL=1``::

    PYMEASURE_GENERATE_PROTOCOL=1 pytest \
        tests/instruments/rigol/test_rigol_dho900_with_device.py \
        --device-address "TCPIP0::192.168.1.100::INSTR"

The generated protocol test file will be saved next to this file as
``test_rigol_dho900_generated.py`` for review.
"""

import os
from pathlib import Path

import pytest

from pymeasure.generator import Generator
from pymeasure.instruments.rigol import RigolDHO924S


@pytest.fixture(scope="module")
def scope(connected_device_address):
    """Connect to a real Rigol DHO924S; skip if --device-address is not given."""
    if os.environ.get("PYMEASURE_GENERATE_PROTOCOL") == "1":
        gen = Generator()
        instr = gen.instantiate(
            RigolDHO924S,
            connected_device_address,
            "rigol",
            adapter_kwargs={"timeout": 5000, "read_termination": "\n"},
        )
        yield instr
        output = Path(__file__).with_name("test_rigol_dho900_generated.py")
        gen.write_file(str(output))
    else:
        instr = RigolDHO924S(connected_device_address)
        yield instr


# ================================================================== #
#  SYSTEM & IDENTIFICATION                                            #
# ================================================================== #


def test_id_and_version(scope):
    assert "DHO9" in scope.id
    assert isinstance(scope.version, str)
    assert len(scope.version) > 0


def test_beeper_and_lock(scope):
    orig_beep = scope.beeper
    scope.beeper = False
    assert scope.beeper is False
    scope.beeper = orig_beep

    scope.lock_fp_key = False
    assert scope.lock_fp_key is False


# ================================================================== #
#  DHO900 CHANNEL EXTENSIONS                                          #
# ================================================================== #


@pytest.mark.parametrize("ch_n", [1, 2, 3, 4])
def test_channel_bandwidth_limit(scope, ch_n):
    ch = getattr(scope, f"ch_{ch_n}")
    original = ch.bandwidth_limit
    ch.bandwidth_limit = "20M"
    assert ch.bandwidth_limit == "20M"
    ch.bandwidth_limit = "OFF"
    assert ch.bandwidth_limit == "OFF"
    ch.bandwidth_limit = original


@pytest.mark.parametrize("ch_n", [1, 2, 3, 4])
def test_channel_vernier(scope, ch_n):
    ch = getattr(scope, f"ch_{ch_n}")
    original = ch.vernier
    ch.vernier = True
    assert ch.vernier is True
    ch.vernier = False
    assert ch.vernier is False
    ch.vernier = original


def test_channel_position(scope):
    original = scope.ch_1.position
    scope.ch_1.position = 0.0
    assert scope.ch_1.position == pytest.approx(0.0, abs=1e-3)
    scope.ch_1.position = original


# ================================================================== #
#  ACQUISITION, TIMEBASE & TRIGGER EXTENSIONS                         #
# ================================================================== #


def test_acquisition_memory_depth(scope):
    original = scope.acquisition_memory_depth
    scope.acquisition_memory_depth = 10_000
    assert scope.acquisition_memory_depth == 10_000
    scope.acquisition_memory_depth = "AUTO"
    assert scope.acquisition_memory_depth == "AUTO"
    scope.acquisition_memory_depth = original


def test_timebase_extensions(scope):
    orig_xy = scope.timebase_mode_xy
    scope.timebase_mode_xy = False
    assert scope.timebase_mode_xy is False
    scope.timebase_mode_xy = orig_xy

    orig_mode = scope.timebase_href_mode
    scope.timebase_href_mode = "CENT"
    assert scope.timebase_href_mode == "CENT"
    scope.timebase_href_mode = orig_mode

    orig_pos = scope.timebase_href_position
    scope.timebase_href_position = 0
    assert scope.timebase_href_position == 0
    scope.timebase_href_position = orig_pos


def test_trigger_pos(scope):
    assert isinstance(scope.trigger_pos, float)


# ================================================================== #
#  MEASUREMENTS EXTENSIONS                                            #
# ================================================================== #


def test_measurement_extensions(scope):
    orig_src = scope.measure_source
    scope.measure_source = "CHAN1"
    assert scope.measure_source == "CHAN1"
    scope.measure_source = orig_src

    orig_ams = scope.measure_all_of
    scope.measure_all_of = "OFF"
    assert scope.measure_all_of == "OFF"
    scope.measure_all_of = orig_ams

    orig_stat = scope.measure_statistic_enable
    scope.measure_statistic_enable = True
    assert scope.measure_statistic_enable is True
    scope.measure_statistic_reset()
    scope.measure_statistic_enable = orig_stat


# ================================================================== #
#  BUILT-IN AFG CHANNEL (DHO914S / DHO924S)                           #
# ================================================================== #


def test_afg_basic_waveform(scope):
    scope.afg.output_enabled = False
    assert scope.afg.output_enabled is False

    scope.afg.function = "SIN"
    assert scope.afg.function == "SIN"

    scope.afg.frequency = 1000.0
    assert scope.afg.frequency == pytest.approx(1000.0, rel=1e-3)

    scope.afg.phase = 0.0
    assert scope.afg.phase == pytest.approx(0.0, abs=1e-2)

    scope.afg.amplitude = 1.0
    assert scope.afg.amplitude == pytest.approx(1.0, rel=1e-2)

    scope.afg.offset = 0.0
    assert scope.afg.offset == pytest.approx(0.0, abs=1e-2)

    scope.afg.function = "SQU"
    scope.afg.square_duty_cycle = 50.0
    assert scope.afg.square_duty_cycle == pytest.approx(50.0, abs=1e-1)

    scope.afg.function = "RAMP"
    scope.afg.ramp_symmetry = 50.0
    assert scope.afg.ramp_symmetry == pytest.approx(50.0, abs=1e-1)

    scope.afg.function = "SIN"


def test_afg_modulation(scope):
    scope.afg.output_enabled = False
    scope.afg.function = "SIN"
    scope.afg.frequency = 10_000.0

    scope.afg.modulation_enabled = False
    assert scope.afg.modulation_enabled is False

    scope.afg.modulation_type = "AM"
    assert scope.afg.modulation_type == "AM"
    scope.afg.am_depth = 50.0
    assert scope.afg.am_depth == pytest.approx(50.0, abs=1e-1)
    scope.afg.am_frequency = 100.0
    assert scope.afg.am_frequency == pytest.approx(100.0, rel=1e-2)
    scope.afg.am_function = "SIN"
    assert scope.afg.am_function == "SIN"

    scope.afg.modulation_type = "FM"
    assert scope.afg.modulation_type == "FM"
    scope.afg.fm_deviation = 100.0
    assert scope.afg.fm_deviation == pytest.approx(100.0, rel=1e-2)
    scope.afg.fm_frequency = 100.0
    assert scope.afg.fm_frequency == pytest.approx(100.0, rel=1e-2)
    scope.afg.fm_function = "SIN"
    assert scope.afg.fm_function == "SIN"

    scope.afg.modulation_type = "PM"
    assert scope.afg.modulation_type == "PM"
    scope.afg.pm_deviation = 90.0
    assert scope.afg.pm_deviation == pytest.approx(90.0, abs=1e-1)
    scope.afg.pm_frequency = 100.0
    assert scope.afg.pm_frequency == pytest.approx(100.0, rel=1e-2)
    scope.afg.pm_function = "SIN"
    assert scope.afg.pm_function == "SIN"

    scope.afg.modulation_enabled = False
