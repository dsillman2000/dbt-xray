import datetime
import json
import time
from typing import Callable

from dbt.adapters.events.types import SQLQuery
from dbt.events.types import LogStartLine, LogTestResult
from dbt_common.events.base_types import EventMsg

from dbt_xray import utils
from dbt_xray.model import XrayRunResult

dbtCallback = Callable[[EventMsg], None]


class XrayTestResultsCollection:
    _lookup: dict[str, str]  # unique_id -> test_key
    _test_results: dict[str, XrayRunResult] = {}  # test key -> XrayRunResult

    def __init__(self, _lookup: dict[str, str] | None = None):
        self._lookup = _lookup or {}

    def callbacks(self) -> list[dbtCallback]:
        def _collect_results(event: EventMsg):
            # Fired when test completes, collect test passage and run result info
            if event.info.name == "NodeFinished":
                unique_id = event.data.node_info.unique_id  # type: ignore
                test_key = self._lookup.get(unique_id, "")
                if test_key not in self._test_results:
                    self._test_results[test_key] = XrayRunResult.from_node_finished_event(event, test_key)  # type: ignore
                else:
                    result = XrayRunResult.from_node_finished_event(event, test_key)  # type: ignore
                    self._test_results[test_key].status = result.status
                    self._test_results[test_key].started_timestamp = result.started_timestamp
                    self._test_results[test_key].finished_timestamp = result.finished_timestamp
                    evidence = (
                        {}
                        if not self._test_results[test_key].execution_evidence
                        else json.loads(self._test_results[test_key].execution_evidence)  # type: ignore
                    )
                    if result.execution_evidence and "message" in result.execution_evidence:
                        if "message" not in evidence:
                            evidence["message"] = json.loads(result.execution_evidence).get("message", "")  # type: ignore
                        else:
                            evidence["message"] += "\n" + json.loads(result.execution_evidence).get("message", "")  # type: ignore
            # Fired on any {{ log(...) }} call, useful for capturing dbt_unit_testing evidences
            if event.info.name == "JinjaLogInfo":
                unique_id = event.data.node_info.unique_id  # type: ignore
                test_key = self._lookup.get(unique_id, "")
                if test_key in self._test_results:
                    json_data = (
                        {}
                        if not self._test_results[test_key].execution_evidence
                        else json.loads(self._test_results[test_key].execution_evidence)  # type: ignore
                    )
                    if "message" not in json_data:
                        json_data["message"] = ""
                    json_data["message"] += "\n" + event.data.msg  # type: ignore
                    self._test_results[test_key].execution_evidence = json.dumps(json_data)
                else:
                    self._test_results[test_key] = XrayRunResult(test_key=test_key)
                    json_data = {"message": event.data.msg}  # type: ignore
                    self._test_results[test_key].execution_evidence = json.dumps(json_data)

        def _upload_results(event: EventMsg):
            if event.info.name == "CommandCompleted":
                for test_key, result in self._test_results.items():
                    utils.dbt_log_note(f"Uploading results for {test_key}: {result.status}")
                    # (placeholder: upload results to Xray here)
                    time.sleep(0.5)

        def _log_notes(event: EventMsg):
            if event.info.name == "JinjaLogInfo":
                print("JinjaLogInfo received! ", event)

        return [_collect_results, _upload_results, _log_notes]
