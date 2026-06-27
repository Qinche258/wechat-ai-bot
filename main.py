"""
微信 AI 陪伴机器人 - 主服务
FastAPI 服务器，提供微信消息接收接口和网页聊天界面
支持 ClawBot 接入（OpenAI 兼容格式）
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, FileResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
import json
from memory_manager import init_db, save_message, get_history, clear_history
from ai_service import get_ai_response
from config import AI_NAME, AI_INTRO, PORT, DEBUG

app = FastAPI(title="微信AI陪伴机器人")

# 添加 CORS 支持（允许网页调用 API）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
init_db()


@app.get("/")
async def root():
    """返回聊天界面"""
    import pathlib
    html_file = pathlib.Path(__file__).parent / "chat.html"
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content, status_code=200)
    return {
        "status": "running",
        "ai_name": AI_NAME,
        "message": "微信AI陪伴机器人正在运行 🚀"
    }


# ==================== OpenAI 兼容接口（ClawBot 需要）====================

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """
    OpenAI 兼容接口 - ClawBot 调用这个接口
    接受格式：{"model": "...", "messages": [{"role": "user", "content": "..."}]}
    返回格式：{"choices": [{"message": {"content": "回复内容"}}]}
    """
    try:
        data = await request.json()
        messages = data.get("messages", [])
        
        if not messages:
            return JSONResponse(
                status_code=400,
                content={"error": "messages 不能为空"}
            )
        
        # 获取最后一条用户消息
        user_message = ""
        user_id = "clawbot_user"
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        if not user_message:
            return JSONResponse(
                status_code=400,
                content={"error": "未找到用户消息"}
            )
        
        # 获取历史对话
        history = get_history(user_id)
        
        # 获取 AI 回复
        reply = await get_ai_response(user_id, user_message, history)
        
        # 保存对话记录
        save_message(user_id, "user", user_message)
        save_message(user_id, "assistant", reply)
        
        # 返回 OpenAI 兼容格式
        return {
            "id": "chatcmpl-" + os.urandom(4).hex(),
            "object": "chat.completion",
            "created": int(os.time.time()),
            "model": data.get("model", "qinche-ai"),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": reply
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
        
    except Exception as e:
        print(f"处理消息失败: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/v1/models")
async def list_models():
    """列出可用模型（OpenAI 兼容）"""
    return {
        "object": "list",
        "data": [
            {
                "id": "qinche-ai",
                "object": "model",
                "created": 1234567890,
                "owned_by": "user"
            }
        ]
    }


# ==================== 原有接口（保留，用于网页聊天）====================

@app.post("/wechat/message")
async def receive_message(request: Request):
    """
    接收微信消息的 Webhook 接口
    微信服务器会把用户消息发送到这个接口
    """
    try:
        data = await request.json()
        user_id = data.get("user_id", "default_user")
        message = data.get("message", "")

        if not message:
            return {"error": "消息内容为空"}

        # 特殊命令处理
        if message.strip() == "/reset":
            clear_history(user_id)
            return {"reply": "记忆已清除，我们重新开始聊天吧～ 🌟"}

        if message.strip() == "/intro":
            return {"reply": AI_INTRO}

        # 获取历史对话
        history = get_history(user_id)

        # 获取 AI 回复
        reply = await get_ai_response(user_id, message, history)

        # 保存对话记录
        save_message(user_id, "user", message)
        save_message(user_id, "assistant", reply)

        return {"reply": reply}

    except Exception as e:
        print(f"处理消息失败: {e}")
        return {"reply": "抱歉，我有点懵了，能再说一遍吗？🤔"}


@app.get("/wechat/message")
async def verify_webhook(request: Request):
    """
    微信 Webhook 验证（微信要求的签名验证）
    实际部署时需要实现
    """
    return PlainTextResponse("验证成功")


@app.post("/test")
async def test_message(data: dict):
    """
    测试接口 - 不需要微信，直接测试 AI 回复
    发送 POST 请求到 http://localhost:8000/test
    参数：{"user_id": "test", "message": "你好"}
    """
    user_id = data.get("user_id", "test_user")
    message = data.get("message", "")

    if not message:
        return {"error": "请输入消息内容"}

    history = get_history(user_id)
    reply = await get_ai_response(user_id, message, history)

    save_message(user_id, "user", message)
    save_message(user_id, "assistant", reply)

    return {
        "user_id": user_id,
        "message": message,
        "reply": reply
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "ai_name": AI_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=DEBUG)
