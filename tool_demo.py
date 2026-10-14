import json
import httpx
import os
import readline
from pydantic import BaseModel, ConfigDict
from validators import is_valid_date, is_valid_stock_code
from market_data import fetch_daily_prices
from metrics import calculate_metrics
from pandas import DataFrame
import pandas as pd

stock_metrics_tool = {
    "type": "function",
    "function": {
        "description": (
            "查询指定股票在指定日期区间的日线行情并计算区间指标，"
            "用于分析该股票在此区间的表现。"
            "返回首尾收盘价，涨跌幅百分数，日均成交量，实际首尾交易日期和记录数。"
            "价格为未复权收盘价，成交量单位为手。"
        ),
        "name": "get_stock_metrics",
        "parameters": {
            "type": "object",
            "properties": {
                "ts_code": {
                    "type": "string",
                    "description": "Tushare股票代码，格式为六位ASCII数字加.SZ或者.SH，例如000001.SZ"
                },
                "start_date": {
                    "type": "string",
                    "description": "查询开始日期，格式为YYYYMMDD，例如20250901，必须是真实日期，且不能晚于结束日期"
                },
                "end_date": {
                    "type": "string",
                    "description": "查询结束日期，格式为YYYYMMDD，例如20250901，必须是真实日期"
                }
            },
            "required": ["ts_code", "start_date", "end_date"],
        }
    }
}


class StockMetricsArguments(BaseModel):
    ts_code: str
    start_date: str
    end_date: str
    model_config = ConfigDict(extra="forbid")


def get_stock_metrics(arguments: StockMetricsArguments, token: str) -> dict:
    dataframe = fetch_daily_prices(ts_code=arguments.ts_code, start_date=arguments.start_date,
                                   end_date=arguments.end_date, token=token)
    if dataframe.empty:
        raise ValueError("没有查到行情")
    metrics = calculate_metrics(dataframe)
    metrics["ts_code"] = arguments.ts_code
    return metrics


def validate_stock_query(arguments: StockMetricsArguments) -> None:
    parts = arguments.ts_code.split(".")
    if len(parts) != 2:
        raise ValueError("股票代码格式应为六位数字加.SZ或.SH")
    stock_code, exchange = parts
    if not (is_valid_stock_code(stock_code) and exchange in ("SZ", "SH")):
        raise ValueError("股票代码格式应为六位数字加.SZ或.SH")
    if not is_valid_date(arguments.end_date) or not is_valid_date(arguments.start_date):
        raise ValueError("请输入有效的八位数字日期YYYYMMDD，例：20250901")
    if arguments.start_date > arguments.end_date:
        raise ValueError("开始日期不能晚于结束日期")


def request_stock_tool(messages: list[dict], api_key: str) -> dict:
    for index, message in enumerate(messages):
        content = message.get("content")
        if isinstance(content, str):
            try:
                content.encode("utf-8")
            except UnicodeEncodeError as error:
                raise ValueError(f"第{index + 1}条消息{message["role"]}含异常字符"
                                 f"字符位置为{error.start + 1}至{error.end}"
                                 )from error
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "deepseek-flash",
        "messages": messages,
        "tools": [stock_metrics_tool],
        "tool_choice": "auto",
        "max_tokens": 512,
        "thinking": {"type": "disabled"},
        "stream": False,
    }
    response = httpx.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload,
                          timeout=60)
    response.raise_for_status()
    data = response.json()

    return data["choices"][0]


TOOL_REGISTRY = {
    "get_stock_metrics": get_stock_metrics,
}


def execute_tool(tool_call: dict, token: str) -> dict:
    tool_name = tool_call["function"]["name"]
    if tool_name not in TOOL_REGISTRY:
        raise ValueError("不支持这个工具")
    arguments = json.loads(tool_call["function"]["arguments"])
    validate_arguments = StockMetricsArguments.model_validate(arguments, strict=True)
    validate_stock_query(validate_arguments)
    tool_function = TOOL_REGISTRY[tool_name]
    result = tool_function(validate_arguments, token)
    return result


def run_agent(
        messages: list[dict],
        api_key: str,
        token: str,
        max_iterations: int = 4,
) -> str:
    if max_iterations < 1:
        raise ValueError("最大请求轮数至少为1")
    for iteration in range(max_iterations):
        choice = request_stock_tool(messages, api_key)
        finish_reason = choice["finish_reason"]
        print(f"第{iteration + 1}轮结束原因：{finish_reason}")
        if finish_reason == "stop":
            result = choice["message"]["content"]
            if not isinstance(result, str):
                raise ValueError("模型返回的结果非标准字符串")
            result = result.strip()
            if result == "":
                raise ValueError("模型返回空内容")

            messages.append(choice["message"])
            return result

        elif finish_reason == "tool_calls":
            tool_calls = choice["message"]["tool_calls"]
            if not tool_calls:
                raise ValueError("模型没有返回工具调用")
            if iteration == max_iterations - 1:
                raise ValueError("达到最大轮请求数，任务尚未完成")
            messages.append(choice["message"])
            for tool_call in tool_calls:
                result = execute_tool(tool_call, token)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result, ensure_ascii=False),
                })

        elif finish_reason == "length":
            raise ValueError("输出长度受限")
        else:
            raise ValueError(f"模型未正常结束{finish_reason}")

    raise ValueError("任务未完成")


if __name__ == "__main__":
    api_key = os.getenv("DEEPSEEK_API_KEY")
    tushare_token = os.getenv("TUSHARE_TOKEN")
    if not api_key:
        print("请先配置DEEPSEEK_API_KEY")
    elif not tushare_token:
        print("请先配置TUSHARE_TOKEN")
    else:
        question = input("请输入你的问题：").strip()
        if not question:
            raise SystemExit("问题不能为空")
        messages = [
            {
                "role": "system",
                "content": (
                    "你是股票数据分析助手，用中文回答。"
                    "需要查询具体股票的区间行情时，使用get_stock_metrics工具。"
                    "回答一般概念问题时直接回答。"
                    "调用工具所需信息缺失时，向用户询问，不自行编造股票代码或日期。"
                    "总结股票区间表现时，仅依据工具结果。"
                    "使用实际首尾日期和记录数；价格为未复权收盘价，"
                    "区间价格变化不等同于总投资收益。"
                    "price_change_pct已经乘以100，展示时只追加百分号，保留两位小数。"
                    "average_volume的单位为手。"
                    "不能仅凭日均成交量判断放量或缩量。"
                    "不编造新闻或涨跌原因，不预测未来价格。"
                    "不要承诺当前工具尚未提供的指标或功能。"
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ]
        try:
            while True:
                answer = run_agent(messages, api_key, tushare_token)
                print(answer)
                question = input("请继续输入(按 exit 退出)：").strip()
                while not question:
                    question = input("输入内容不能为空，请重新输入").strip()
                if question == "exit":
                    break
                messages.append({
                    "role": "user",
                    "content": question,
                })

        except httpx.TimeoutException:
            print("请求超时，本次任务已结束")
        except httpx.HTTPStatusError as error:
            print(f"服务返回 HTTP {error.response.status_code},本次任务已终止")
        except httpx.RequestError:
            print("网络请求失败，本次任务已终止")
        except ValueError as error:
            print(f"任务失败：{error}")
