import asyncio
import os
import httpx
from market_data import fetch_daily_prices_async
from metrics import calculate_metrics
from time import perf_counter
import json

from tool_demo import (StockMetricsArguments, get_stock_metrics_async, validate_stock_query, execute_tool_async)


async def main() -> None:
    token = os.getenv("TUSHARE_TOKEN")
    if not token:
        raise SystemExit("Please set TUSHARE_TOKEN environment variable")

    tool_calls = []
    for stock_code in ["000001.SZ", "600000.SH"]:
        tool_calls.append(
            {
                "id": f"test_{stock_code}",
                "type": "function",
                "function": {
                    "name": "get_stock_metrics",
                    "arguments": json.dumps({
                        "ts_code": stock_code,
                        "start_date": "20250901",
                        "end_date": "20250902",
                    }),
                },
            }
        )

    async with httpx.AsyncClient() as client:
        tool_results = await asyncio.gather(
            *(
                execute_tool_async(tool_call,token,client)
                for tool_call in tool_calls
            )
        )

    for tool_call,tool_result in zip(tool_calls,tool_results):
        print(tool_call['id'],tool_result)


if __name__ == "__main__":
    asyncio.run(main())
