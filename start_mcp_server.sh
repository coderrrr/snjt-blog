#!/bin/bash
# start_mcp_server.sh - 启动MCP Server的脚本

# 默认配置
SERVICE_PORT=${SERVICE_PORT:-"5000"}
CONSUL_HOST=${CONSUL_HOST:-"consul-server"}
CONSUL_PORT=${CONSUL_PORT:-"8500"}
DEEPSEEK_API_URL=${DEEPSEEK_API_URL:-"http://deepseek-api:8000/v1/completions"}

# 启动MCP Server
python mcp_client.py