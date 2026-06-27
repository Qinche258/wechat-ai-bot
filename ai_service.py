"""
AI 服务模块 - 调用 DeepSeek API
"""

import httpx
from config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL, MAX_TOKENS, TEMPERATURE, AI_PERSONALITY


DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


async def get_ai_response(user_id: str, user_message: str, history: list) -> str:
    """
    获取 AI 回复
    """
    # 构建消息列表
    messages = [{"role": "system", "content": AI_PERSONALITY}]

    # 添加历史对话
    messages.extend(history)

    # 添加当前用户消息
    messages.append({"role": "user", "content": user_message})

    # 调用 DeepSeek API
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "stream": False
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                DEEPSEEK_API_URL,
                headers=headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"AI 调用失败: {e}")
            return "抱歉，我现在有点累了，稍后再聊好不好～ 😅"
