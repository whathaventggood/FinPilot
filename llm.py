import httpx


def generate_summary(prompt: str, api_key: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "deepseek-flash",
        "messages": [
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 512,
        "thinking": {"type": "disabled"},
        "stream": False,
    }

    response = httpx.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload,
                          timeout=60)
    response.raise_for_status()
    data = response.json()
    answer = data["choices"][0]["message"]["content"]
    finish_reason = data["choices"][0]["finish_reason"]
    if finish_reason == "length":
        raise ValueError("模型的回答长度达到token限制")
    elif finish_reason != "stop":
        raise ValueError("模型的回答生成未正常完成")
    if not isinstance(answer, str):
        raise ValueError("模型未返回有效的回答文本")

    answer = answer.strip()
    if not answer:
        raise ValueError("模型未返回有效的回答文本")

    return answer
