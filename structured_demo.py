from json import JSONDecodeError
from pydantic import ValidationError
from analysis_result import parse_analysis_result


raw_text = """{
    "summary":"摘要",
    "limitations":[
        "仅有两条行情记录",
        "不能仅凭日均成交量判断是放量还是缩量"
    ]
}"""

try:
    analysis = parse_analysis_result(raw_text)
    print(type(analysis))
    print(analysis.summary)
    for limitation in analysis.limitations:
        print(limitation)
except ValidationError as error:
    print(f"分析结果格式不符合要求：{error}")
except JSONDecodeError as error:
    print(f"模型返回的内容不是有效JSON：{error}")


