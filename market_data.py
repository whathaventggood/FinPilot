import pandas as pd
import httpx

def fetch_daily_prices(
        ts_code: str,
        start_date: str,
        end_date: str,
        token: str,
) -> pd.DataFrame:
    payload = {
        "api_name": "daily",
        "token": token,
        "params": {
            "ts_code": ts_code,
            "start_date": start_date,
            "end_date": end_date,
        },
        "fields": "ts_code,trade_date,close,vol",
    }
    response = httpx.post("https://api.tushare.pro", json=payload, timeout=10, )
    response.raise_for_status()
    data = response.json()
    if data["code"] != 0:
        raise ValueError(data["msg"])
    else:
        items = data["data"]["items"]
        fields = data["data"]["fields"]
        return pd.DataFrame(items,columns = fields)
