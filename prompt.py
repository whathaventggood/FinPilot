def build_analysis_prompt(ts_code: str,metrics: dict) -> str:
    return f"""
    用中文简要总结这只股票在指定区间的表现
    股票代码：{ts_code}
    实际首尾日期：{metrics["first_date"]} - {metrics["last_date"]}
    记录数：{metrics["record_count"]}
    首尾价格：{metrics["first_close"]} - {metrics["last_close"]} 
    收盘价涨跌幅：{metrics["price_change_pct"]:.2f}%
    日均成交量：{metrics["average_volume"]:.2f}手
    仅依据提供的数据；不编造新闻或涨跌原因；不预测未来价格；说明价格为未复权收盘价；仅提供区间日均成交量，不能据此判断缩量或放量。
"""