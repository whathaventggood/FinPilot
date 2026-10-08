from pydantic import BaseModel,Field,ConfigDict
import json


class AnalysisResult(BaseModel):
    summary: str = Field(min_length=1)
    limitations: list[str]
    model_config = ConfigDict(str_strip_whitespace=True)


def parse_analysis_result(raw_text: str) -> AnalysisResult:
    result = json.loads(raw_text)
    analysis = AnalysisResult.model_validate(result,strict=True)
    return analysis