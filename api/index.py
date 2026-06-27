"""
Vercel Serverless Function - 秦彻AI陪伴机器人
完全自包含，不依赖其他本地文件
兼容 ClawBot OpenAI 格式 /v1/chat/completions
"""

import os
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# ==================== 配置 ====================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

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


# ==================== ASGI 应用 ====================
class VercelASGIApp:
    """轻量级 ASGI 应用，兼容 @vercel/python 构建器"""

    async def __call__(self, scope, receive, send):
        """ASGI 入口点 - Vercel 通过此函数识别应用"""
        if scope["type"] == "http":
            await self.handle_http(scope, receive, send)
        else:
            await send({
                "type": "http.response.start",
                "status": 400,
                "headers": [[b"content-type", b"text/plain"]],
            })
            await send({
                "type": "http.response.body",
                "body": b"Not supported",
            })

    async def handle_http(self, scope, receive, send):
        """处理 HTTP 请求"""
        method = scope["method"]
        path = scope.get("path", scope.get("raw_path", b"/").decode())

        # 读取请求体
        body = b""
        if method == "POST":
            message = await receive()
            body = message.get("body", b"")

        # 解析 JSON body
        body_data = {}
        if body:
            try:
                body_data = json.loads(body)
            except Exception:
                pass

        # 路由分发 → 获取响应
        response = self.route(method, path, body_data)

        # 发送响应
        await send({
            "type": "http.response.start",
            "status": response["status"],
            "headers": [
                [k.encode(), v.encode()] for k, v in response["headers"].items()
            ],
        })
        await send({
            "type": "http.response.body",
            "body": response["body"].encode("utf-8"),
        })

    def route(self, method, path, body_data):
        """路由分发"""

        # GET /
        if method == "GET" and path == "/":
            return self.json_response(200, {
                "status": "running",
                "ai_name": "秦彻",
                "message": "秦彻AI运行中",
            })

        # GET /health
        if method == "GET" and path == "/health":
            return self.json_response(200, {
                "status": "ok",
                "ai_name": "秦彻",
            })

        # GET /v1/models （ClawBot 探测接口）
        if method == "GET" and path == "/v1/models":
            return self.json_response(200, {
                "object": "list",
                "data": [
                    {"id": "qinche-ai", "object": "model", "owned_by": "user"},
                    {"id": "deepseek-chat", "object": "model", "owned_by": "deepseek"},
                ],
            })

        # POST /v1/chat/completions （核心聊天接口）
        if method == "POST" and path == "/v1/chat/completions":
            return self.handle_chat(body_data)

        # 404
        return self.json_response(404, {"error": "Not Found"})

    def handle_chat(self, data):
        """调用 DeepSeek API 处理聊天"""
        messages = data.get("messages", [])
        if not messages:
            return self.json_response(400, {"error": "messages 不能为空"})

        if not DEEPSEEK_API_KEY:
            return self.json_response(500, {"error": "未配置 DEEPSEEK_API_KEY 环境变量"})

        # 构建 DeepSeek 消息列表
        deepseek_messages = [{"role": "system", "content": AI_PERSONALITY}]
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                deepseek_messages.append({"role": role, "content": content})

        payload = json.dumps({
            "model": "deepseek-chat",
            "messages": deepseek_messages,
            "max_tokens": 600,
            "temperature": 1.0,
        }).encode("utf-8")

        try:
            req = Request(
                "https://api.deepseek.com/chat/completions",
                data=payload,
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            reply_content = result["choices"][0]["message"]["content"]

            return self.json_response(200, {
                "id": "chatcmpl-" + os.urandom(4).hex(),
                "object": "chat.completion",
                "model": data.get("model", "qinche-ai"),
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": reply_content},
                    "finish_reason": "stop",
                }],
                "usage": result.get("usage", {}),
            })

        except HTTPError as e:
            err_body = e.read().decode() if hasattr(e, 'read') else str(e.code)
            return self.json_response(502, {
                "error": f"DeepSeek API 错误 {e.code}",
                "detail": err_body[:500],
            })
        except URLError as e:
            return self.json_response(502, {"error": f"网络错误: {e.reason}"})
        except Exception as e:
            return self.json_response(500, {"error": f"服务器内部错误: {str(e)}"})

    @staticmethod
    def json_response(status, data):
        """构建 JSON 响应"""
        return {
            "status": status,
            "headers": {"Content-Type": "application/json; charset=utf-8"},
            "body": json.dumps(data, ensure_ascii=False),
        }


# ==================== 导出 ASGI 应用 ====================
# @vercel/python 构建器会查找名为 app / application / handler 的顶层 ASGI 对象
app = VercelASGIApp()
