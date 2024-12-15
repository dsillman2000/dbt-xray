import datetime
from typing import Callable

from dbt.adapters.events.types import SQLQuery
from dbt.events.types import LogStartLine, LogTestResult
from dbt_common.events.base_types import EventMsg

from dbt_xray.model import XrayRunResult

dbtCallback = Callable[[EventMsg], None]


class XrayTestResultsCollection:
    _lookup: dict[str, str]  # unique_id -> test_key
    _test_results: dict[str, XrayRunResult] = {}  # test key -> XrayRunResult

    def __init__(self, _lookup: dict[str, str] | None = None):
        self._lookup = _lookup or {}

    def callbacks(self) -> list[dbtCallback]:
        def _collect_results(event: EventMsg):
            if event.info.name == "NodeFinished":
                unique_id = event.data.node_info.unique_id  # type: ignore
                test_key = self._lookup.get(unique_id, "")
                self._test_results[test_key] = XrayRunResult.from_node_finished_data(event.data, test_key)  # type: ignore

        def _upload_results(event: EventMsg):
            if event.info.name == "CommandCompleted":
                for test_key, result in self._test_results.items():
                    print(f"Uploading results for {test_key}: {result.status}")
                    # Upload results to Xray here

        return [_collect_results, _upload_results]
