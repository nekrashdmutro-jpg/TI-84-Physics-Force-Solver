"""Structural and packaging tests for the FORCES suite.

These are the checks that can be run without a calculator: the TI-BASIC source
rules, the tokenizer, and the group file. They do not execute TI-BASIC.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import forces_builder as fb


def test_all_programs_are_present():
    assert set(fb.PROGRAMS) == set(fb.ORDER)
    assert len(fb.ORDER) == 8


def test_names_are_valid_calculator_names():
    for name in fb.ORDER:
        assert len(name) <= 8, name
        assert fb.NAME_RE.match(name), name
        assert name == name.upper(), name


def test_no_program_is_empty():
    for name in fb.ORDER:
        assert fb.clean_source(fb.PROGRAMS[name]).strip(), name


def test_sources_pass_the_builtin_validator():
    assert fb.validate_sources() == []


def test_launcher_reaches_every_solver():
    source = fb.clean_source(fb.PROGRAMS["FORCEMNU"])
    for name in (
        "GSET",
        "VECADD",
        "FLATFRC",
        "ANGPULL",
        "RAMPSLV",
        "FBDDRAW",
        "FBDHELP",
    ):
        assert "prgm" + name in source


def test_every_program_sets_degree_mode():
    for name in fb.ORDER:
        lines = fb.clean_source(fb.PROGRAMS[name]).splitlines()
        assert "Degree" in lines, name


def test_solvers_never_hardcode_gravity():
    """Solvers may only default G when it is unset, never replace it."""
    for name in ("FLATFRC", "ANGPULL", "RAMPSLV", "FBDDRAW"):
        lines = fb.clean_source(fb.PROGRAMS[name]).splitlines()
        for index, line in enumerate(lines):
            if "9.8->G" in line:
                assert lines[index - 1] == "If G<=0", (name, index)


def test_output_stays_on_screen():
    """Every Output( must fit: start column plus written width <= 26.

    Output( wraps to the next row instead of erroring, so a too-wide write
    silently corrupts the layout underneath.
    """
    outputs = 0
    for name in fb.ORDER:
        for line in fb.clean_source(fb.PROGRAMS[name]).splitlines():
            if line.startswith("Output("):
                outputs += 1
                match = fb.OUTPUT_RE.match(line)
                assert match, line
                row = int(match.group(1))
                col = int(match.group(2))
                width = fb._output_width(match.group(3))
                assert 1 <= row <= fb.MAX_ROW, line
                assert col >= 1, line
                assert col + width - 1 <= fb.MAX_COL, line
    assert outputs > 100


def test_display_overflow_is_rejected():
    original = fb.PROGRAMS["GSET"]
    try:
        fb.PROGRAMS["GSET"] = 'ClrHome\nOutput(1,20,"TOO WIDE TO FIT")\n'
        errors = fb.validate_sources()
        assert any("reaches column" in error for error in errors), errors
    finally:
        fb.PROGRAMS["GSET"] = original


def test_menu_text_limits_are_rejected():
    original = fb.PROGRAMS["GSET"]
    try:
        fb.PROGRAMS["GSET"] = 'ClrHome\nMenu("T","%s",2)\nLbl 2\nReturn\n' % ("X" * 25)
        errors = fb.validate_sources()
        assert any("Menu( item" in error for error in errors), errors
    finally:
        fb.PROGRAMS["GSET"] = original


def test_acceleration_uses_the_motion_direction():
    """Kinetic friction must be signed by the motion, not by the push."""
    for name in ("FLATFRC", "ANGPULL"):
        source = fb.clean_source(fb.PROGRAMS[name])
        assert "MOVING WHICH WAY?" in source, name
        assert "R*E" in source, name


def test_vector_angles_and_forces_are_validated():
    source = fb.clean_source(fb.PROGRAMS["VECADD"])
    assert source.count("MUST BE 0 TO 360") >= 2, "angle range not checked"
    assert source.count("MUST BE 0 OR MORE") >= 5, "N/S/E/W totals not checked"


def test_vector_solver_names_each_cardinal_direction():
    source = fb.clean_source(fb.PROGRAMS["VECADD"])
    for label in ('"EAST (N)"', '"WEST (N)"', '"NORTH (N)"', '"SOUTH (N)"'):
        assert label in source, label


def test_programs_force_the_full_screen():
    """Split screen makes Output( rows 5-10 an error, so each program sets Full."""
    for name in fb.ORDER:
        lines = fb.clean_source(fb.PROGRAMS[name]).splitlines()
        assert "Full" in lines, name


def test_each_program_has_a_way_back():
    """Every program either stops or returns, so the menu can take over."""
    for name in fb.ORDER:
        lines = fb.clean_source(fb.PROGRAMS[name]).splitlines()
        assert "Return" in lines or "Stop" in lines, name


def test_unbalanced_source_is_rejected():
    original = fb.PROGRAMS["GSET"]
    try:
        fb.PROGRAMS["GSET"] = "ClrHome\nIf G<=0\nThen\n9.8->G\n"
        errors = fb.validate_sources()
        assert any("Then but" in error or "End" in error for error in errors)
    finally:
        fb.PROGRAMS["GSET"] = original


def test_missing_label_target_is_rejected():
    original = fb.PROGRAMS["GSET"]
    try:
        fb.PROGRAMS["GSET"] = "ClrHome\nGoto 42\n"
        errors = fb.validate_sources()
        assert any("Goto 42" in error for error in errors)
    finally:
        fb.PROGRAMS["GSET"] = original


def test_fbddraw_uses_only_allowed_force_labels():
    source = fb.clean_source(fb.PROGRAMS["FBDDRAW"])
    for label in ('"Fg"', '"FN"', '"Fa"', '"Ff"', '"Ffs"', '"Ffk"', '"FT"'):
        assert label in source, label
    lower = source.lower()
    for forbidden in ("air", "drag", "fair", "fdrag"):
        assert forbidden not in lower, forbidden


def test_fbddraw_supports_required_situations_and_drawing_commands():
    source = fb.clean_source(fb.PROGRAMS["FBDDRAW"])
    for situation in ("HORIZONTAL", "ANGLED", "INCLINED PLANE"):
        assert situation in source, situation
    for cmd in ("ClrDraw", "AxesOff", "Line(", "Text("):
        assert cmd in source, cmd


def test_fbddraw_does_not_assume_friction():
    source = fb.clean_source(fb.PROGRAMS["FBDDRAW"])
    assert 'Menu("FRICTION FORCE?","1 NONE"' in source
    assert "If H=0\nGoto 60" in source


# --- checks that need the tivars package -------------------------------------


def _tivars():
    return pytest.importorskip("tivars")


def test_every_program_tokenizes():
    _tivars()
    from tivars.models import TI_84PCE
    from tivars.types import TIProgram

    for name in fb.ORDER:
        source = fb.clean_source(fb.PROGRAMS[name])
        program = TIProgram(name=name)
        program.load_string(source, model=TI_84PCE)
        tokens = program.tokens()
        assert tokens, name
        decoded = program.string()
        assert decoded.count("\n") == source.count("\n"), name


def _normalize(text):
    return "\n".join(line.strip() for line in text.replace("\r\n", "\n").splitlines())


def test_tokens_round_trip_to_the_same_source():
    """Tokenizing then decoding must give back exactly what was written.

    This is the test that catches silent mis-munching: if a command such as
    "Pause " were read as the letters P,A,U,S,E, tokenization would still
    succeed, but the decoded text would come back as "PAUSE" and fail here.
    """
    _tivars()
    from tivars.models import TI_84PCE
    from tivars.types import TIProgram

    for name in fb.ORDER:
        source = fb.clean_source(fb.PROGRAMS[name])
        program = TIProgram(name=name)
        program.load_string(source, model=TI_84PCE)
        decoded = f"{program:a}"
        assert _normalize(decoded) == _normalize(source), name


def test_group_file_holds_every_program(tmp_path):
    _tivars()
    target = tmp_path / fb.GROUP_FILE
    fb.build_group(target)
    assert target.exists()
    assert fb.verify_group(target) == []


def test_group_survives_a_round_trip(tmp_path):
    _tivars()
    from tivars.types import TIGroup

    target = tmp_path / fb.GROUP_FILE
    fb.build_group(target)
    entries = TIGroup.open(str(target)).ungroup()
    rebuilt = tmp_path / "roundtrip.8xg"
    from tivars.models import TI_84PCE

    TIGroup.group(entries, name="FORCES").save(str(rebuilt), model=TI_84PCE)
    assert fb.verify_group(rebuilt) == []