import os
import json
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
import requests
import uvicorn
from consulate import Consul
from openai_client import invoke

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

# 连接Consul服务注册中心（仅用于发现业务服务）
consul_host = os.environ.get('CONSUL_HOST', 'consul-server')
consul_port = int(os.environ.get('CONSUL_PORT', 8500))
consul = Consul(host=consul_host, port=consul_port)

# 初始化FastAPI应用
app = FastAPI(title="MCP Server", description="业务系统集成API")

# 定义请求和响应模型
class TreatmentPlanRequest(BaseModel):
    symptoms: List[str]
    age_days: int
    farm_id: str

class TreatmentPlanResponse(BaseModel):
    success: bool
    treatment_plan: Optional[str] = None
    diagnosis: Optional[List[str]] = None
    error: Optional[str] = None

@app.post("/api/treatment-plan", response_model=TreatmentPlanResponse, operation_id="generate_treatment_plan")
async def generate_treatment_plan(request: TreatmentPlanRequest):
    """
    根据猪只症状、日龄和猪场信息生成治疗方案
    
    - **symptoms**: 症状列表，例如['发热', '咳嗽', '食欲不振']
    - **age_days**: 猪只日龄，单位为天
    - **farm_id**: 猪场ID，用于查询该猪场可用药品
    """
    try:
        # # 从服务发现获取库存服务地址
        # inventory_services = consul.catalog.service('inventory-service')
        # if not inventory_services:
        #     raise HTTPException(status_code=503, detail="库存服务不可用")
        # inventory_service = inventory_services[0]
        # inventory_url = f"http://{inventory_service['ServiceAddress']}:{inventory_service['ServicePort']}/api/inventory"
        
        # # 从服务发现获取疫病数据服务地址
        # disease_services = consul.catalog.service('disease-data-service')
        # if not disease_services:
        #     raise HTTPException(status_code=503, detail="疫病数据服务不可用")
        # disease_service = disease_services[0]
        # disease_url = f"http://{disease_service['ServiceAddress']}:{disease_service['ServicePort']}/api/diseases"
        
        # logger.info(f"处理治疗方案请求: 症状={request.symptoms}, 日龄={request.age_days}, 猪场ID={request.farm_id}")
        
        # # 调用库存服务获取可用药品
        # try:
        #     inventory_response = requests.get(
        #         inventory_url,
        #         params={'farm_id': request.farm_id},
        #         timeout=5
        #     )
        #     inventory_response.raise_for_status()
        #     available_medicines = inventory_response.json()
        # except Exception as e:
        #     logger.error(f"调用库存服务失败: {str(e)}")
        #     raise HTTPException(status_code=502, detail=f"调用库存服务失败: {str(e)}")
        
        # # 调用疫病数据服务获取相关疫病信息
        # try:
        #     disease_response = requests.post(
        #         disease_url,
        #         json={'symptoms': request.symptoms, 'age_days': request.age_days},
        #         timeout=5
        #     )
        #     disease_response.raise_for_status()
        #     disease_data = disease_response.json()
        # except Exception as e:
        #     logger.error(f"调用疫病数据服务失败: {str(e)}")
        #     raise HTTPException(status_code=502, detail=f"调用疫病数据服务失败: {str(e)}")
        
        # 准备发送给大模型的提示

        disease_data = {
            'possible_diseases': ['疫苗A', '疫苗B'],
            'epidemic_status': '流行中'
        }

        available_medicines = [
            {'name': '药品A', 'dosage': '1片', 'quantity': 10},
            {'name': '药品B', 'dosage': '2片', 'quantity': 5}
        ]

        prompt = f"""
        基于以下信息生成猪禽治疗方案:
        
        症状: {', '.join(request.symptoms)}
        日龄: {request.age_days}天
        可能的疾病: {', '.join(disease_data.get('possible_diseases', []))}
        疾病流行情况: {disease_data.get('epidemic_status', '无数据')}
        
        可用药品清单:
        {json.dumps(available_medicines, indent=2, ensure_ascii=False)}
        
        请提供详细的治疗方案，包括:
        1. 推荐用药及用量
        2. 治疗周期
        3. 注意事项
        4. 预防措施
        """
        
        # 调用OpenAI模型生成治疗方案
        try:            
            response_data = invoke(prompt)
            treatment_plan = response_data.get("choices", [{}])[0].get("message", {}).get("content", "无法生成治疗方案")
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"调用OpenAI模型失败: {str(e)}")
            raise HTTPException(status_code=502, detail=f"调用LLM服务失败: {str(e)}")
        
        # # 记录治疗方案到业务系统
        # treatment_services = consul.catalog.service('treatment-service')
        # if not treatment_services:
        #     logger.warning("治疗记录服务不可用，无法保存治疗方案")
        # else:
        #     treatment_service = treatment_services[0]
        #     treatment_url = f"http://{treatment_service['ServiceAddress']}:{treatment_service['ServicePort']}/api/treatments"
            
        #     treatment_record = {
        #         'farm_id': request.farm_id,
        #         'age_days': request.age_days,
        #         'symptoms': request.symptoms,
        #         'diagnosis': disease_data.get('possible_diseases', []),
        #         'treatment_plan': treatment_plan,
        #         'created_by': 'ai-assistant'
        #     }
            
        #     try:
        #         requests.post(treatment_url, json=treatment_record, timeout=5)
        #         logger.info(f"治疗方案已记录到业务系统，猪场ID: {request.farm_id}")
        #     except Exception as e:
        #         logger.error(f"记录治疗方案失败: {str(e)}")
        
        return TreatmentPlanResponse(
            success=True,
            treatment_plan=treatment_plan,
            diagnosis=disease_data.get('possible_diseases', [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成治疗方案时发生错误: {str(e)}")
        return TreatmentPlanResponse(
            success=False,
            error=str(e)
        )

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}

# 创建 MCP 服务器
mcp = FastApiMCP(
    app,
    name="MCP Server",                    # MCP 名称
    describe_all_responses=True,          # 展示所有响应模型
    describe_full_response_schema=True    # 展示完整 JSON 模式
)

# 挂载 MCP
mcp.mount()

# 启动服务
if __name__ == '__main__':
    port = int(os.environ.get('SERVICE_PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)