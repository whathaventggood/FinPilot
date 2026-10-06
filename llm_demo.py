import os
import httpx
from llm import generate_summary


def main() -> None:
    token = os.getenv("DEEPSEEK_API_KEY")
    if not token:
        print("请先设置DEEPSEEK_API_KEY")
    else:
        try:
            answer = generate_summary("请用一句中文解释什么是股价收盘价", token)
            print(answer)
        except httpx.HTTPStatusError:
            print("请求服务失败")
        except httpx.TimeoutException:
            print("请求超时")
        except httpx.RequestError:
            print("网路请求失败，请检查网络或代理设置")
        except ValueError as error:
            print(f"{error}")


if __name__ == "__main__":
    main()
