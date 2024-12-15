import datetime
import json
from typing import Any, Literal

import pydantic


def json_adapter_response(adapter_response: Any) -> str:
    def _dict_adapter_response(adapter_respone: Any) -> dict[str, Any]:
        adapter_response_data = {}
        for field in adapter_response.fields:
            key: str = field
            _try_get_value = lambda k: (
                getattr(adapter_response.fields[k], "string_value", None)
                or getattr(adapter_response.fields[k], "number_value", None)
            )
            value = _try_get_value(key)
            adapter_response_data[key] = value
        return adapter_response_data

    return json.dumps(_dict_adapter_response(adapter_response))


class XrayRunResult(pydantic.BaseModel):
    test_key: str
    status: Literal["pass", "fail"] | None = None
    started_timestamp: datetime.datetime
    finished_timestamp: datetime.datetime | None = None
    execution_evidence: str | None = None

    @classmethod
    def from_node_finished_data(cls, node_finished_data: Any, test_key: str):
        execute_timing_info = next(info for info in node_finished_data.run_result.timing_info if info.name == "execute")
        started_at = execute_timing_info.started_at.seconds + execute_timing_info.started_at.nanos / 1e9
        completed_at = execute_timing_info.completed_at.seconds + execute_timing_info.completed_at.nanos / 1e9
        status = node_finished_data.run_result.status
        return cls(
            test_key=test_key,
            status="pass" if status == "pass" else "fail",
            started_timestamp=datetime.datetime.fromtimestamp(started_at),
            finished_timestamp=datetime.datetime.fromtimestamp(completed_at),
            execution_evidence=json_adapter_response(node_finished_data.run_result.adapter_response),
        )
