import datetime
import json
from typing import Any, Literal

import pydantic
from dbt.events.types import NodeFinished


def _dict_adapter_response(adapter_response: Any) -> dict[str, Any]:
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


def run_result_json(node_finished_event: NodeFinished) -> str:
    run_result = node_finished_event.data.run_result
    invocation_id = node_finished_event.info.invocation_id
    dict_adapter_response = _dict_adapter_response(run_result.adapter_response)
    message = run_result.message
    full_dict = {"adapter_response": dict_adapter_response, "dbt_invocation_id": invocation_id, "message": message}
    return json.dumps(full_dict)


class XrayRunResult(pydantic.BaseModel):
    test_key: str
    status: Literal["pass", "fail"] | None = None
    started_timestamp: datetime.datetime
    finished_timestamp: datetime.datetime | None = None
    execution_evidence: str | None = None

    @classmethod
    def from_node_finished_event(cls, node_finished_event: NodeFinished, test_key: str):
        execute_timing_info = next(
            info for info in node_finished_event.data.run_result.timing_info if info.name == "execute"
        )
        started_at = execute_timing_info.started_at.seconds + execute_timing_info.started_at.nanos / 1e9
        completed_at = execute_timing_info.completed_at.seconds + execute_timing_info.completed_at.nanos / 1e9
        status = node_finished_event.data.run_result.status
        return cls(
            test_key=test_key,
            status="pass" if status == "pass" else "fail",
            started_timestamp=datetime.datetime.fromtimestamp(started_at),
            finished_timestamp=datetime.datetime.fromtimestamp(completed_at),
            execution_evidence=run_result_json(node_finished_event),
        )
