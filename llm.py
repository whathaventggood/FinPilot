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
        "thinking": {"type": "disabled"},
        "stream": False,
    }

    response = httpx.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload,
                          timeout=60)
    response.raise_for_status()
    data = response.json()
    answer = data["choices"][0]["message"]["content"]

    if not isinstance(answer, str):
        raise ValueError("模型未返回有效的回答文本")

    answer = answer.strip()
    if not answer:
        raise ValueError("模型未返回有效的回答文本")

    return answer
