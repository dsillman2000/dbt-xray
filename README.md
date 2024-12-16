# dbt-xray

A dbt companion CLI for reporting unit test executions to Jira X-Ray. It supports dbt unit tests that are written with
[native dbt Unit Tests](https://docs.getdbt.com/docs/build/unit-tests) or 
[Equal Experts dbt_unit_testing tests](https://github.com/EqualExperts/dbt-unit-testing).

## Jira tag system

To label a unit test for Jira X-ray execution, you must add a tag like the following to the test:

```yaml
tags: ['key:JIRA-123']
```

Likewise, you can label a group of tests with a `plan:` tag to group them into a shared test plan corresponding to a Jira Test Plan:

```yaml
tags: ['key:JIRA-123', 'plan:JIRA-456']
```

## Basic usage

### Selecting tests with `ls`

List all tests in the project with jira tags:

```bash
dbt-xray ls
```

Identify a specific test by Jira key:

```bash
dbt-xray ls --test-key JIRA-123
dbt-xray ls -k JIRA-123
```

Identify multiple tests by Jira keys:

```bash
dbt-xray ls --test-key JIRA-123,JIRA-234,JIRA-345
dbt-xray ls -k JIRA-123,JIRA-234,JIRA-345
```

Identify all tests in a test plan by Jira key:

```bash
dbt-xray ls --test-plan JIRA-456
dbt-xray ls -p JIRA-456
```

### Running tests with `run`

Run all tests in the project with jira tags:

```bash
dbt-xray run
```

Run a specific test by Jira key:

```bash
dbt-xray run --test-key JIRA-123
dbt-xray run -k JIRA-123
```

Run multiple tests by Jira keys:

```bash
dbt-xray run --test-key JIRA-123,JIRA-234,JIRA-345
dbt-xray run -k JIRA-123,JIRA-234,JIRA-345
```

Run all tests in a test plan by Jira key:

```bash
dbt-xray run --test-plan JIRA-456
dbt-xray run -p JIRA-456
```

Run all tests in the project with jira tags, sequentially:

```bash
dbt-xray run --mode serial
dbt-xray run -m serial
```

By default, `--mode bulk` is supplied, which runs tests in parallel with the threads configured in the dbt profile.

## To-do

- [ ] Implement missing API calls for Jira X-Ra
- [ ] Better tests
- [ ] `dbt-xray check` command to alert whether or not dbt test contents disagree with corresponding Jira tickets (check hash, maybe description and test details).
- [ ] `dbt-xray sync` command to update Jira tickets with their corresponding dbt test contents (update hash, maybe description and test details).
- [ ] Better dbt version compatibility for <1.8.0

## Acknowledgements

Author:
- David Sillman <dsillman2000@gmail.com>
