import pytest
from click.testing import CliRunner

from dbt_xray.main import cli


@pytest.mark.parametrize(
    "args,expected_substrings",
    [
        pytest.param(["ls"], [".unit_test__empty", ".unit_test__one_row", ".empty", ".one_row"], id="ls"),
        pytest.param(["ls", "--test-key", "IGDP-14"], [".one_row"], id="ls --test-key IGDP-14"),
        pytest.param(
            ["ls", "--test-key", "IGDP-14,IGDP-13"],
            [".one_row", ".empty"],
            id="ls --test-key IGDP-14,IGDP-13",
        ),
        pytest.param(["ls", "--test-plan", "IGDP-28"], [".unit_test__empty", ".empty"], id="ls --test-plan IGDP-28"),
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
            [
                ".unit_test__empty): pass",
                ".unit_test__one_row): pass",
                ".empty): pass",
                ".one_row): pass",
            ],
            id="run",
        ),
        pytest.param(
            ["run", "--test-key", "IGDP-14"],
            [".one_row): pass"],
            id="run --test-key IGDP-14",
        ),
        pytest.param(
            ["run", "--test-key", "IGDP-14,IGDP-13"],
            [".one_row): pass", ".empty): pass"],
            id="run --test-key IGDP-14,IGDP-13",
        ),
        pytest.param(
            ["run", "--test-plan", "IGDP-28"],
            [".unit_test__empty): pass", ".empty): pass"],
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
