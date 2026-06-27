# 微信 AI 陪伴机器人

一个可以接入微信的 AI 陪伴助手，支持定制性格、长期记忆。

## 功能特点

- 🎭 **定制性格** - 在 `config.py` 中修改 AI 的名字、性格、说话风格
- 💬 **长期记忆** - 记住你们的对话历史，下次聊天能接着聊
- 📱 **接入微信** - 通过 Webhook 接收微信消息（需要配合微信桥接工具）
- 🧪 **本地测试** - 不用微信也能测试 AI 效果

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

编辑 `config.py`，把 `DEEPSEEK_API_KEY` 改成你自己的 Key：

```python
DEEPSEEK_API_KEY = "sk-your-key-here"
```

### 3. 启动服务

```bash
python main.py
```

服务会在 `http://localhost:8000` 启动

### 4. 测试 AI

用浏览器或 Postman 发送 POST 请求到 `http://localhost:8000/test`：

```json
{
  "user_id": "test",
  "message": "你好呀"
}
```

## 定制 AI 性格

编辑 `config.py` 中的这些参数：

```python
# AI 的名字
AI_NAME = "小暖"

# AI 的性格设定（系统提示词）
AI_PERSONALITY = """你是一个温暖、贴心的AI陪伴助手..."""
```

改完保存，重启服务即可生效！

## 接入微信

### 方案 A：使用 gewechat（推荐）

1. 下载并运行 [gewechat](https://github.com/Devo97/gewechat)
2. 配置 gewechat 的回调地址为 `http://你的服务器地址/wechat/message`
3. 扫码登录微信
4. 完成！现在在微信里发消息，AI 会自动回复

### 方案 B：使用第三方微信机器人工具

- Friday Bot
- 可爱猫
- 等企业微信方案（更稳定）

## 目录结构

```
wechat-ai-bot/
├── config.py           # 配置文件（定制AI性格在这里）
├── main.py             # FastAPI 主服务
├── ai_service.py       # DeepSeek API 调用
├── memory_manager.py   # 对话记忆管理
├── requirements.txt    # Python 依赖
├── memory/             # 对话历史数据库
└── README.md           # 本文件
```

## 常用命令

在微信里发送这些命令：

- `/reset` - 清除记忆，重新开始
- `/intro` - 查看 AI 自我介绍

## 部署到云端

### Vercel（免费）

1. 注册 [vercel.com](https://vercel.com)
2. 连接 GitHub 仓库
3. 设置环境变量 `DEEPSEEK_API_KEY`
4. 部署完成！

### Railway（$5/月）

1. 注册 [railway.app](https://railway.app)
2. 上传代码
3. 设置环境变量
4. 部署完成！

## 注意事项

- ⚠️ 个人微信接入存在封号风险，建议使用小号测试
- 💰 DeepSeek API 按用量收费，但非常便宜（10元用半年）
- 🔒 不要泄露你的 API Key

## 问题反馈

遇到问题？检查：
1. API Key 是否正确
2. 服务器是否能访问 `api.deepseek.com`
3. 查看控制台错误信息

---
打造属于你的专属 AI 陪伴 🌸
