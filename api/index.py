"""
Vercel 入口文件
将 FastAPI 应用导出给 Vercel（ASGI 模式）
"""

from main import app
from mangum import Mangum

# 创建 handler（Vercel Serverless Function 需要）
handler = Mangum(app, lifespan="off")
