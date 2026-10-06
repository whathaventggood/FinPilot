import pandas as pd

def calculate_metrics(df: pd.DataFrame) -> dict:
    required_columns = ["trade_date", "close", "vol"]
    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"缺少必须列：{column}")
        if df[column].isna().any():
            raise ValueError(f"当前列{column}有缺失")
    if len(df) < 2:
        raise ValueError("至少需要两条行情记录")

    df = df.sort_values(by="trade_date", ascending=True, ignore_index=True)
    first_close = df["close"].iloc[0]
    if first_close <= 0:
        raise ValueError("期初价格不大于0")
    first_date = df["trade_date"].iloc[0]
    last_date = df["trade_date"].iloc[-1]
    record_count = len(df)
    last_close = df["close"].iloc[-1]
    price_change_pct = (last_close - first_close) / first_close * 100
    average_volume = df["vol"].mean()
    return {
        "first_close": float(first_close),
        "last_close": float(last_close),
        "price_change_pct": float(price_change_pct),
        "average_volume": float(average_volume),
        "record_count": int(record_count),
        "first_date": first_date,
        "last_date": last_date,
    }

