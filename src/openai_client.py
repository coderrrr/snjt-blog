import os
import logging
import requests
from fastapi import HTTPException

# 配置日志
logger = logging.getLogger("openai-client")

def invoke(prompt: str) -> str:    
    # 获取OpenAI API配置
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    openai_api_url = os.environ.get('OPENAI_API_URL')
        
    try:
        # 调用OpenAI模型
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}"
        }
        
        payload = {
            "model": "gpt-4",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.2
        }
        
        response = requests.post(
            f"{openai_api_url}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        # 从API响应中提取生成的内容
        response_data = response.json()        
        return response_data
    except Exception as e:
        logger.error(f"调用OpenAI模型失败: {str(e)}")
        raise HTTPException(status_code=502, detail=f"调用LLM服务失败: {str(e)}")