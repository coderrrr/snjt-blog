#!/bin/bash
# start_mcp_server.sh - 启动MCP Server的脚本

# 设置环境变量并导出，使子进程可以访问
export SERVICE_PORT=${SERVICE_PORT:-"8000"}
export CONSUL_HOST=${CONSUL_HOST:-"consul-server"}
export CONSUL_PORT=${CONSUL_PORT:-"8500"}
export OPENAI_API_URL=${OPENAI_API_URL:-"https://api.siliconflow.cn"}
export OPENAI_API_KEY=${OPENAI_API_KEY:-"your-api-key-here"}

# 启动MCP Server
python mcp_server.py