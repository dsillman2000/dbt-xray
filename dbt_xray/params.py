import click

test_plan = click.option(
    "--test-plan",
    "-p",
    type=str,
    default=None,
    help="Select test nodes with the given Jira test plan",
)

test_key = click.option(
    "--test-key",
    "-k",
    type=str,
    default=None,
    help="Select test nodes with the given Jira test key (or keys if comma-separated)",
)

quiet = click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress output",
)
