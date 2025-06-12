#!/bin/bash
# start_mcp_server.sh - 启动MCP Server的脚本

# 默认配置
SERVICE_PORT=${SERVICE_PORT:-"8000"}
CONSUL_HOST=${CONSUL_HOST:-"consul-server"}
CONSUL_PORT=${CONSUL_PORT:-"8500"}
OPENAI_API_URL=${OPENAI_API_URL:-"https://api.openai.com/v1"}
OPENAI_API_KEY=${OPENAI_API_KEY:-"your-api-key-here"}

# 启动MCP Server
python mcp_server.py