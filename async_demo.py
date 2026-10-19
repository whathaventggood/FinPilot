import asyncio
from time import perf_counter


async def simulate_query(stock_code:str)->None:
    print(f"开始查询：{stock_code}")
    await asyncio.sleep(1)
    print(f"完成查询：{stock_code}")

async def main()->None:
    started_at = perf_counter()
    await simulate_query("000001.SZ")
    await simulate_query("600000.SH")

    elapsed_time =perf_counter()-started_at
    print(f"顺序等待耗时：{elapsed_time}秒")

    started_at = perf_counter()
    await asyncio.gather(
        simulate_query("000001.SZ"),
        simulate_query("600000.SH"),
    )

    elapsed_time = perf_counter()-started_at
    print(f"并发等待耗时：{elapsed_time}秒")

if __name__ == "__main__":
    asyncio.run(main())
