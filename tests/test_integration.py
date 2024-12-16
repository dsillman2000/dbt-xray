import pytest
from click.testing import CliRunner

from dbt_xray.main import cli


@pytest.mark.parametrize(
    "args,expected_substrings",
    [
        pytest.param(["ls"], ["IGDP-13: ", "IGDP-14: ", "IGDP-15: ", "IGDP-16: ", "IGDP-70: ", "IGDP-71: "], id="ls"),
        pytest.param(["ls", "--test-key", "IGDP-14"], ["IGDP-14: ", ".one_row"], id="ls --test-key IGDP-14"),
        pytest.param(
            ["ls", "--test-key", "IGDP-14,IGDP-13"],
            ["IGDP-14: ", "IGDP-13: ", ".one_row", ".empty"],
            id="ls --test-key IGDP-14,IGDP-13",
        ),
        pytest.param(
            ["ls", "--test-plan", "IGDP-28"],
            ["IGDP-13: ", "IGDP-15: ", ".unit_test__empty", ".empty"],
            id="ls --test-plan IGDP-28",
        ),
    ],
)
def test_dbt_xray_ls(args: list[str], expected_substrings: list[str]):
    runner = CliRunner()
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, result.output
    for substring in expected_substrings:
        assert substring in result.output


@pytest.mark.parametrize(
    "args,expected_substrings",
    [
        pytest.param(
            ["run"],
            ["IGDP-13: pass", "IGDP-14: pass", "IGDP-15: pass", "IGDP-16: pass", "IGDP-70: fail", "IGDP-71: fail"],
            id="run",
        ),
        pytest.param(
            ["run", "--test-key", "IGDP-14"],
            ["IGDP-14: pass"],
            id="run --test-key IGDP-14",
        ),
        pytest.param(
            ["run", "--test-key", "IGDP-14,IGDP-13"],
            ["IGDP-14: pass", "IGDP-13: pass"],
            id="run --test-key IGDP-14,IGDP-13",
        ),
        pytest.param(
            ["run", "--test-plan", "IGDP-28"],
            ["IGDP-13: pass", "IGDP-15: pass"],
            id="run --test-plan IGDP-28",
        ),
    ],
)
def test_dbt_xray_run(args: list[str], expected_substrings: list[str]):
    runner = CliRunner()
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, result.output
    for substring in expected_substrings:
        assert substring in result.output
