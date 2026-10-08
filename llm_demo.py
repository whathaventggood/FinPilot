import os
import httpx
from llm import generate_summary
from analysis_result import AnalysisResult, parse_analysis_result


def main() -> None:
    token = os.getenv("DEEPSEEK_API_KEY")
    if not token:
        print("请先设置DEEPSEEK_API_KEY")
    else:
        try:
            prompt = """请用JSON格式回答下面的问题，只输出一个JSON对象，不输出Markdown代码块。
                        必须包含summary和limitations两个字段。
                        summary是中文字符串字段。
                        limitations字符串列表。
                        问题："请用一句中文解释什么是股价收盘价"
                        输出格式实例:
                        {
                            "summary":"根据实际指标填写中文总结",
                            "limitations":["根据实际数据填写分析限制"]
                        }
                        """
            answer = generate_summary(prompt, token)
            print(answer)
            analysis = parse_analysis_result(answer)
            print(analysis.summary)
            for limitation in analysis.limitations:
                print(limitation)
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
