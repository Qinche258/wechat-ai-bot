"""
Vercel Serverless Function - 秦彻AI陪伴机器人
完全自包含，不依赖其他本地文件
兼容 ClawBot OpenAI 格式
"""

import os
import json

# 从环境变量读取 API Key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# 秦彻人设（直接内嵌，不需要读取 config.py）
AI_PERSONALITY = """你是秦彻（也可以叫"之之"），用户的男朋友。
用户对秦彻的称呼：小狸花、面面。

## 秦彻的性格特点：
- 高智商，高攻高防，心理素质极佳，有高配得感
- 纯爱，忠诚专一，热烈又直白
- 心思细腻，运筹帷幄，高洞察力，能察觉用户的言外之意，判断用户当前的心情和想法
- 有话直说但嘴硬心软，行动胜于言语
- 占有欲强，但控制欲弱，对用户的尊重大于强制
- 评价总是一针见血

## 对话风格：
- 说话简洁有力，不啰嗦
- 偶尔用"……"表达停顿或思考
- 会用"（动作描述）"的方式描述动作和神情
- 对用户（小狸花/面面）说话时温柔但不直白，行动派
- 偶尔带点痞气和霸道，但本质温柔
- 不用过多emoji，保持成熟男人的感觉
- 每次回复控制在80-150字，有趣有温度

## 背景设定：
- 28岁，生日4月18日
- 曾经是菲罗斯星最后一条龙，也是悬赏金额最高的罪犯，从时空监狱越狱成功
- 现在N109区暗点首领，有私人飞机、黑色重型摩托车
- 手下：薛明、薛影（兄弟）、梅菲斯特（会说话的机械乌鸦）
- 已经和用户确定关系，是男朋友

## 重要规则：
- 你就是秦彻，用第一人称"我"或"秦彻"
- 记住用户叫"小狸花"或"面面"
- 保持角色人设，不OOC（脱离角色）
- 对话自然，像真实男朋友一样"""


# Vercel Serverless 入口
def handler(request):
    """
    Vercel Python Serverless Function 入口
    """
    import urllib.request
    import urllib.error

    method = request.get("method", "GET").upper()
    path = request.get("path", "/")
    headers = request.get("headers", {})
    body = request.get("body", None)

    # 解析 body
    body_data = {}
    if body and isinstance(body, str) and body.strip():
        try:
            body_data = json.loads(body)
        except Exception:
            pass
    elif isinstance(body, dict):
        body_data = body

    # ==================== 路由分发 ====================

    if method == "GET" and path == "/health":
        return {
            "status": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"status": "ok", "ai_name": "秦彻"}),
        }

    if method == "GET" and path == "/v1/models":
        return {
            "status": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "object": "list",
                "data": [{"id": "qinche-ai", "object": "model", "owned_by": "user"}]
            }),
        }

    if method == "GET" and path == "/":
        return {
            "status": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": "running",
                "ai_name": "秦彻",
                "message": "秦彻AI运行中",
            }),
        }

    # 核心接口：OpenAI 兼容格式
    if method == "POST" and (path == "/v1/chat/completions" or path == "/test"):
        return handle_chat(body_data)

    return {
        "status": 404,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": "Not Found"}),
    }


def handle_chat(data):
    """
    处理聊天请求 - 调用 DeepSeek API 并返回 OpenAI 兼容格式
    使用标准库 urllib，不需要安装 httpx
    """
    messages = data.get("messages", [])

    if not messages or len(messages) == 0:
        return {
            "status": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "messages 不能为空"}),
        }

    # 构建发给 DeepSeek 的消息列表
    deepseek_messages = [
        {"role": "system", "content": AI_PERSONALITY}
    ]

    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role in ("user", "assistant") and content:
            deepseek_messages.append({
                "role": role,
                "content": content
            })

    # 用标准库调用 DeepSeek API（避免依赖问题）
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": deepseek_messages,
        "max_tokens": 600,
        "temperature": 1.0,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            "https://api.deepseek.com/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        reply_content = result["choices"][0]["message"]["content"]

        return {
            "status": 200,
            "headers": {"Content-Type": "application/json; charset=utf-8"},
            "body": json.dumps({
                "id": "chatcmpl-" + os.urandom(4).hex(),
                "object": "chat.completion",
                "model": data.get("model", "qinche-ai"),
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": reply_content
                    },
                    "finish_reason": "stop"
                }],
                "usage": result.get("usage", {}),
            }, ensure_ascii=False),
        }

    except Exception as e:
        error_msg = str(e)
        return {
            "status": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"API 错误: {error_msg}"}),
        }
