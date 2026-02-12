def clean_json_response(text: str) -> str:
    """清理 LLM 返回的 JSON 响应，去除 markdown 代码块标记"""
    text = text.strip()
    # 移除 markdown 代码块
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()
