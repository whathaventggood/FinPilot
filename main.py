from validators import is_valid_stock_code


stock_code = input("请输入股票代码:")
stock_code = stock_code.strip()
if is_valid_stock_code(stock_code):
    print(f"准备分析股票:{stock_code}")
else:
    print("股票代码格式错误，请输入六位数")
