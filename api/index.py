"""
Vercel Serverless Function - 秦彻AI陪伴机器人
直接转发消息到DeepSeek API，不需要本地存储
兼容 ClawBot OpenAI 格式
"""

import os
import json
import httpx
from config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_MODEL,
    MAX_TOKENS,
    TEMPERATURE,
    AI_PERSONALITY,
)


async def handler(request):
    """
    Vercel Serverless 入口函数
    处理所有请求，返回响应
    """

    # 获取请求信息
    method = request.get("method", "GET").upper()
    path = request.get("path", "/")
    headers = request.get("headers", {})
    body = request.get("body", None)

    # 解析 body
    if body and isinstance(body, str):
        try:
            body_data = json.loads(body)
        except Exception:
            body_data = {}
    else:
        body_data = body or {}

    # ==================== 路由分发 ====================

    # 健康检查
    if method == "GET" and path == "/health":
        return {
            "status": 200,
            "body": json.dumps({"status": "ok", "ai_name": "秦彻"}),
            "headers": {"Content-Type": "application/json"},
        }

    # 模型列表（ClawBot 需要）
    if method == "GET" and path == "/v1/models":
        return {
            "status": 200,
            "body": json.dumps({
                "object": "list",
                "data": [{"id": "qinche-ai", "object": "model", "owned_by": "user"}]
            }),
            "headers": {"Content-Type": "application/json"},
        }

    # 根路径 - 返回简单状态
    if method == "GET" and path == "/":
        return {
            "status": 200,
            "body": json.dumps({"status": "running", "ai_name": "秦彻", "message": "秦彻AI陪伴机器人运行中"}),
            "headers": {"Content-Type": "application/json"},
        }

    # 核心接口: OpenAI 兼容格式（ClawBot 调用）
    if method == "POST" and path == "/v1/chat/completions":
        return await handle_chat_completion(body_data)

    # 测试接口
    if method == "POST" and path == "/test":
        return await handle_chat_completion(
            {"messages": [{"role": "user", "content": body_data.get("message", "")}]}
        )

    # 404
    return {
        "status": 404,
        "body": json.dumps({"error": "Not Found"}),
        "headers": {"Content-Type": "application/json"},
    }


async def handle_chat_completion(data):
    """
    处理聊天请求 - 直接调用 DeepSeek API
    支持完整对话历史传递（ClawBot 会发送历史消息）
    """
    messages = data.get("messages", [])

    if not messages:
        return {
            "status": 400,
            "body": json.dumps({"error": "messages 不能为空"}),
            "headers": {"Content-Type": "application/json"},
        }

    # 构建发给 DeepSeek 的消息列表
    # 在最前面插入系统提示词（人设）
    deepseek_messages = [
        {"role": "system", "content": AI_PERSONALITY}
    ]

    # 追加所有历史消息
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role in ("user", "assistant") and content:
            deepseek_messages.append({
                "role": role,
                "content": content
            })

    # 调用 DeepSeek API
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": DEEPSEEK_MODEL,
                "messages": deepseek_messages,
                "max_tokens": MAX_TOKENS,
                "temperature": TEMPERATURE,
            },
        )

        result = response.json()

    if response.status_code != 200:
        error_msg = result.get("error", {}).get("message", "未知错误")
        return {
            "status": 500,
            "body": json.dumps({"error": f"DeepSeek API 错误: {error_msg}"}),
            "headers": {"Content-Type": "application/json"},
        }

    # 提取回复内容
    reply_content = result["choices"][0]["message"]["content"]

    # 返回 OpenAI 兼容格式
    return {
        "status": 200,
        "body": json.dumps({
            "id": "chatcmpl-" + os.urandom(4).hex(),
            "object": "chat.completion",
            "model": data.get("model", "qinche-ai"),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": reply_content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": result.get("usage", {}),
        }, ensure_ascii=False),
        "headers": {"Content-Type": "application/json"},
    }
