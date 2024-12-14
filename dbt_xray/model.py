import datetime
from typing import Any, Literal

import pydantic


class XrayRunResult(pydantic.BaseModel):
    test_key: str
    status: Literal["pass", "fail"]
    execution_timestamp: datetime.datetime
    execution_evidence: dict[str, Any] = None
