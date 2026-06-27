# 微信AI陪伴机器人 - 秦彻

一个可以接入微信 ClawBot 的 AI 陪伴机器人，角色人设为《恋与深空》的秦彻。

## 功能特点

- 🎭 高度定制的人设（秦彻/之之）
- 💬 长期记忆（记住对话历史）
- 📱 可接入微信 ClawBot（出现在微信联系人列表）
- 🌐 支持网页聊天界面

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务器
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

访问：`http://localhost:8000`

## 部署到 Vercel

### 第一步：安装 Vercel CLI

```bash
npm install -g vercel
```

### 第二步：登录 Vercel

```bash
vercel login
```

### 第三步：部署

```bash
vercel --prod
```

### 第四步：设置环境变量

在 Vercel 后台设置：
- `DEEPSEEK_API_KEY`: 你的 DeepSeek API Key

### 第五步：获取部署地址

部署成功后会显示类似：`https://your-project.vercel.app`

## 接入微信 ClawBot

1. 在微信中搜索并打开 **ClawBot**
2. 点击"连接智能体"
3. 填写后端地址：`https://your-project.vercel.app`
4. 完成！秦彻会出现在微信联系人里

## 定制人设

编辑 `config.py`：

```python
AI_NAME = "秦彻"  # 改名字
AI_PERSONALITY = """..."""  # 改性格设定
```

## API 接口

- `GET /` - 聊天界面
- `POST /chat` - 发送消息
- `POST /reset` - 清除记忆
- `GET /health` - 健康检查

## 文件结构

```
wechat-ai-bot/
├── config.py          # 配置文件（改人设在这里）
├── main.py            # 主服务
├── ai_service.py      # AI 调用
├── memory_manager.py  # 对话记忆
├── chat.html          # 聊天界面
├── api/index.py       # Vercel 入口
├── vercel.json        # Vercel 配置
└── requirements.txt    # 依赖列表
```

## 注意事项

- DeepSeek API Key 需要在 Vercel 后台设置为环境变量
- 免费版 Vercel 有请求次数限制
- 建议使用小号测试微信接入功能
