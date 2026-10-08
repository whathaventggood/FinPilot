import os
import httpx
import pandas as pd
from metrics import calculate_metrics
from market_data import fetch_daily_prices
from validators import is_valid_stock_code
from validators import is_valid_date
from prompt import build_analysis_prompt
from llm import generate_summary
from analysis_result import parse_analysis_result


def main() -> None:
    token = os.getenv("TUSHARE_TOKEN")
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not token:
        print("请先设置TUSHARE_TOKEN")
    elif not api_key:
        print("请先设置DEEPSEEK_API_KEY")
    else:
        stock_code = input("请输入六位股票代码：").strip()

        if not is_valid_stock_code(stock_code):
            print("股票代码格式错误")
            return

        exchange = input("请输入市场：SZ/SH：").strip().upper()

        if exchange not in ["SZ", "SH"]:
            print("市场不支持，请输入 SZ 或 SH")
            return

        ts_code = f"{stock_code}.{exchange}"

        start_date = input("请输入查询期初日期：").strip()

        end_date = input("请输入查询期末日期：").strip()

        if not (is_valid_date(start_date) and is_valid_date(end_date)):
            print("请输入有效的八位数字日期，例：20250901")
            return

        if start_date > end_date:
            print("开始日期不能晚于结束日期")
            return

        try:
            df = fetch_daily_prices(ts_code, start_date, end_date, token)

            if df.empty:
                print("没有查到行情")
            else:
                print(f"股票：{ts_code}")
                metrics = calculate_metrics(df)
                print(
                    f"实际数据范围：{metrics["first_date"]}至{metrics["last_date"]}，共获取{metrics["record_count"]}条交易记录")
                print(f"期初收盘价：{metrics["first_close"]}")
                print(f"期末收盘价：{metrics["last_close"]}")
                print(f"区间收盘价涨跌幅：{metrics['price_change_pct']:.2f}%")
                print(f"日均成交量：{metrics['average_volume']:.2f}手")
                analysis_prompt = build_analysis_prompt(ts_code, metrics)
                answer = generate_summary(analysis_prompt, api_key)
                analysis = parse_analysis_result(answer)
                print(analysis.summary)
                for limitation in analysis.limitations:
                    print(limitation)
        except httpx.TimeoutException:
            print("请求超时，请稍后再试")

        except httpx.HTTPStatusError:
            print("服务返回错误，无法完成分析")

        except ValueError as error:
            print(f"分析失败：{error}")

        except httpx.RequestError:
            print("网路请求失败，请检查网络或代理设置")


if __name__ == "__main__":
    main()
