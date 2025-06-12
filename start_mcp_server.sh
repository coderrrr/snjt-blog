#!/bin/bash

# DeepSeek V3 Pro API 配置
export DEEPSEEK_API_KEY="your_api_key_here"  # 请替换为实际的 API Key
export DEEPSEEK_API_URL="https://api.deepseek.com"  # DeepSeek API 基础URL

# 其他服务配置
export SERVICE_PORT=8000
export CONSUL_HOST="consul-server"
export CONSUL_PORT=8500

# 启动 MCP 服务器
python src/mcp_server.py