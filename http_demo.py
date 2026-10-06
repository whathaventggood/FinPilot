import httpx
from validators import is_valid_stock_code

stock_code = input("请输入股票代码:")
stock_code = stock_code.strip()

if is_valid_stock_code(stock_code):
    try:
        params = {"stock_code": stock_code}
        response = httpx.get("https://httpbin.org/get", timeout=5, params=params)
        response.raise_for_status()
        data = response.json()
        received_stock_code = data["args"]["stock_code"]
        print(f"收到的股票代码是:{received_stock_code}")
    except httpx.TimeoutException:
        print("请求超时，请稍后再试")
    except httpx.HTTPStatusError:
        print("服务返回错误，无法完成查询")
else:
    print("代码格式错误")
