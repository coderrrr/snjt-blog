# 基于 AWS 构建企业 AI 助手：云南神农集团案例分析

## 1. 云南神农集团企业介绍

云南神农集团是云南省领先的农业科技企业，专注于现代农业技术研发、农产品生产加工及销售。近年来，随着数字化转型的实施，企业已完成了各核心业务系统向云端的迁移，其中最具代表性的是成功实施了 SAP Rise with AWS，将企业 ERP 系统部署至亚马逊云科技的中国宁夏区域，为神农集团带来了显著的业务价值。

然而，随着企业信息系统的不断丰富，一个新的挑战逐渐显现：如何让员工高效地获取分散在各个系统中的信息资源？

## 2. 企业 AI 助手的需求介绍

在与企业 IT 团队和业务部门的深入沟通中，我们发现企业面临以下关键痛点：

1. **信息孤岛问题**：尽管各业务系统已迁移至云端，但系统间的数据流通仍不够顺畅，员工需要在多个系统间切换才能获取完整信息。

2. **知识获取效率低**：企业积累了大量的业务知识、SOP 手册和最佳实践，但较为分散，员工查找信息耗时长。

3. **专业支持资源有限**：IT 支持团队和业务专家的资源有限，无法及时响应所有的日常咨询需求。

4. **新员工培训成本高**：新员工需要较长时间才能熟悉企业各系统的操作和业务流程，培训成本高。

基于以上痛点，神农集团提出了构建企业 AI 助手的需求，希望通过 AI 整合企业内部知识资源，并实现与业务系统的交互，具体需求包括：

- **统一知识访问入口**：提供一个集中的界面，让员工通过自然语言提问以获取分散在各业务系统/知识库中的信息。

- **业务系统交互**：代表用户执行简单的系统操作，如：分析各项数据并生成报料计划；查询药品库存和上游供应厂的疫病数据，生成针对性的治疗方案。

- **安全合规**：确保数据访问和处理符合企业安全策略和相关法规要求。

## 3. 企业 AI 助手的架构设计

在充分理解企业的需求后，我们设计了一套基于 AWS 服务和开源工具的企业 AI 助手解决方案。整体架构如下：

### 3.1 架构概览

![企业 AI 助手架构图](architecture_diagram.png)

该架构主要包含以下几个核心组件：

1. **前端交互层**
   - 基于 VUE 开发的 Web 应用，部署在 Amazon S3 和 CloudFront 上

2. **AI 工作流及编排**
   - AI 助手网关，负责路由请求以及用户权限校验
   - 使用 Dify 作为 AI 应用编排平台

3. **AI 推理层**
   - DeepSeek-R1-14B 或同类小参数模型作为问题分类器以获得良好的速度
   - DeepSeek-R1-70B 或同类大参数模型作为 AI 推理模型

4. **知识管理层**
   - Amazon OpenSearch 作为向量数据库
   - BGE-large-zh-v1.5 作为向量模型，它在中文场景下表现良好且资源消耗较低。
   - BGE-Reranker 作为 Rerenk 模型，对候选检索结果进行精细排序，提升检索的精度。
   - Amazon S3 存储原始企业文档，Amazon Lambda 检索 S3 上原始文档的变化事件以触发知识库的 Re-indexing

5. **数据存储与集成层**
   - RDS 和 Redshift 为企业的业务数据库和用作数据分析的数据湖服务
   - **MCP Server（Model-Controller-Provider）**作为业务数据查询的中间件，在 AI 助手架构中扮演着关键角色，它使 AI 助手能够安全、高效地访问分散在各个业务系统中的数据，而无需了解底层系统的复杂性。通过统一的接口和权限控制，既保障了数据安全，又提高了 AI 助手的响应速度和准确性。

## 4. RAG 的实现及优化

检索增强生成（Retrieval-Augmented Generation，RAG）是企业 AI 助手的核心能力之一，它使系统能够基于企业内部知识库提供准确、相关的回答。我们采用了多项技术手段来优化 RAG 效果。

### 4.1 知识库构建

客户的知识库资料分散在多个系统中，格式各异（Word、PDF、HTML、PPT等）。我们构建了统一的处理流水线：

1. **文档转换**：使用 AWS Lambda 将不同格式的文档转换为纯文本。

2. **文档内容分段**：使用大模型将长文档根据章节分布，在章节末尾插入明显的分隔符，例如 -----。

2. **文档分块**：将长文档切分为适合检索的小块（chunk），每块约 500-1000 个 token，并保留适当的上下文重叠。

3. **向量化**：使用 Embedding 模型将文本块转换为向量表示。

4. **索引构建**：将向量和原始文本存储在 Amazon OpenSearch 中，建立高效的向量索引。

### 4.2 检索策略优化

为提高检索质量，我们实施了以下优化策略：

#### 4.2.1 混合检索

结合了关键词检索和语义检索的优势：

- **BM25算法**：基于关键词匹配，能够捕捉精确的术语和专有名词。
- **向量相似度检索**：基于语义理解，能够处理同义词和意图相似的查询。
- **混合排序**：综合考虑两种检索结果，动态调整权重。

#### 4.2.2 查询重写

使用大语言模型对用户原始查询进行重写和扩展：

- **查询分解**：将复杂问题分解为多个子查询。
- **查询扩展**：添加相关术语和同义词，增加召回率。
- **查询精确化**：识别并强化查询中的关键概念。

通过这些优化措施，神农集团的 AI 助手在知识问答方面达到了一定的准确率。

## 5. Tool Use 的实现及优化

除了知识问答能力外，AI 助手还需要能够与企业内部系统交互，执行实际的业务操作。这种能力被称为 Tool Use（工具使用），是提升 AI 助手实用性的关键。Dify 作为 AI 应用编排平台负责对话管理、工具调用编排和LLM交互，而MCP Server则专注于业务系统集成，为Dify提供业务功能API。这种职责分工使系统更加模块化，便于维护和扩展。
现有业务系统使用 Java SpringCloud 实现，使用 Consul 作为服务注册中心；MCP Server 使用 Python 语言、FastAPI 和 FastAPI-MCP 实现，并使用 consulate 包接入 SpringCloud 微服务框架。
![Dify与MCP集成架构](dify_mcp_integration.png)

安装依赖：
```bash
pip install consulate fastapi fastapi-mcp uvicorn requests pydantic
```

### Remote MCP Server 实现（业务系统集成层）

```python
# mcp_server.py
import os
import json
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
import requests
from consulate import Consul

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

@app.post("/api/treatment-plan", response_model=TreatmentPlanResponse)
async def generate_treatment_plan(request: TreatmentPlanRequest):
    """
    根据猪只症状、日龄和猪场信息生成治疗方案
    
    - **symptoms**: 症状列表，例如['发热', '咳嗽', '食欲不振']
    - **age_days**: 猪只日龄，单位为天
    - **farm_id**: 猪场ID，用于查询该猪场可用药品
    """
    try:
        # 从服务发现获取库存服务地址
        inventory_services = consul.catalog.service('inventory-service')
        if not inventory_services:
            raise HTTPException(status_code=503, detail="库存服务不可用")
        inventory_service = inventory_services[0]
        inventory_url = f"http://{inventory_service['ServiceAddress']}:{inventory_service['ServicePort']}/api/inventory"
        
        # 从服务发现获取疫病数据服务地址
        disease_services = consul.catalog.service('disease-data-service')
        if not disease_services:
            raise HTTPException(status_code=503, detail="疫病数据服务不可用")
        disease_service = disease_services[0]
        disease_url = f"http://{disease_service['ServiceAddress']}:{disease_service['ServicePort']}/api/diseases"
        
        logger.info(f"处理治疗方案请求: 症状={request.symptoms}, 日龄={request.age_days}, 猪场ID={request.farm_id}")
        
        # 调用库存服务获取可用药品
        try:
            inventory_response = requests.get(
                inventory_url,
                params={'farm_id': request.farm_id},
                timeout=5
            )
            inventory_response.raise_for_status()
            available_medicines = inventory_response.json()
        except Exception as e:
            logger.error(f"调用库存服务失败: {str(e)}")
            raise HTTPException(status_code=502, detail=f"调用库存服务失败: {str(e)}")
        
        # 调用疫病数据服务获取相关疫病信息
        try:
            disease_response = requests.post(
                disease_url,
                json={'symptoms': request.symptoms, 'age_days': request.age_days},
                timeout=5
            )
            disease_response.raise_for_status()
            disease_data = disease_response.json()
        except Exception as e:
            logger.error(f"调用疫病数据服务失败: {str(e)}")
            raise HTTPException(status_code=502, detail=f"调用疫病数据服务失败: {str(e)}")
        
        # 准备发送给DeepSeek模型的提示
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
        
        # 调用DeepSeek模型生成治疗方案
        deepseek_url = os.environ.get('DEEPSEEK_API_URL')
        if not deepseek_url:
            logger.error("未配置DEEPSEEK_API_URL环境变量")
            raise HTTPException(status_code=500, detail="LLM服务配置错误")
            
        try:
            deepseek_response = requests.post(
                deepseek_url,
                headers={'Content-Type': 'application/json'},
                json={
                    'prompt': prompt,
                    'max_tokens': 1000,
                    'temperature': 0.2
                },
                timeout=30
            )
            deepseek_response.raise_for_status()
            treatment_plan = deepseek_response.json().get('response', '无法生成治疗方案')
        except Exception as e:
            logger.error(f"调用DeepSeek模型失败: {str(e)}")
            raise HTTPException(status_code=502, detail=f"调用LLM服务失败: {str(e)}")
        
        # 记录治疗方案到业务系统
        treatment_services = consul.catalog.service('treatment-service')
        if not treatment_services:
            logger.warning("治疗记录服务不可用，无法保存治疗方案")
        else:
            treatment_service = treatment_services[0]
            treatment_url = f"http://{treatment_service['ServiceAddress']}:{treatment_service['ServicePort']}/api/treatments"
            
            treatment_record = {
                'farm_id': request.farm_id,
                'age_days': request.age_days,
                'symptoms': request.symptoms,
                'diagnosis': disease_data.get('possible_diseases', []),
                'treatment_plan': treatment_plan,
                'created_by': 'ai-assistant'
            }
            
            try:
                requests.post(treatment_url, json=treatment_record, timeout=5)
                logger.info(f"治疗方案已记录到业务系统，猪场ID: {request.farm_id}")
            except Exception as e:
                logger.error(f"记录治疗方案失败: {str(e)}")
        
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
    import uvicorn
    port = int(os.environ.get('SERVICE_PORT'))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### Dify 工具注册
JSON Schema 文件示例：
```json
{
   "name": "generate_treatment_plan",
   "description": "根据猪只症状、日龄和猪场信息生成治疗方案",
   "parameters": {
      "type": "object",
      "properties": {
            "symptoms": {
               "type": "array",
               "items": {"type": "string"},
               "description": "症状列表，例如['发热', '咳嗽', '食欲不振']"
            },
            "age_days": {
               "type": "integer",
               "description": "猪只日龄，单位为天"
            },
            "farm_id": {
               "type": "string",
               "description": "猪场ID，用于查询该猪场可用药品"
            }
      },
      "required": ["symptoms", "age_days", "farm_id"]
   },
   "api_endpoint": f"{mcp_server_url}/api/treatment-plan",
   "method": "POST"
}
```

### 启动脚本

```bash
#!/bin/bash
# start_mcp_server.sh - 启动MCP Server的脚本

# 默认配置
SERVICE_PORT=${SERVICE_PORT:-"5000"}
CONSUL_HOST=${CONSUL_HOST:-"consul-server"}
CONSUL_PORT=${CONSUL_PORT:-"8500"}
DEEPSEEK_API_URL=${DEEPSEEK_API_URL:-"http://deepseek-api:8000/v1/completions"}

# 启动MCP Server
python mcp_client.py
```

## 6. 总结

通过与云南神农集团的紧密合作，我们共同构建了一个综合性的企业 AI 助手，通过将大语言模型与企业知识库和业务系统进行深度融合，创造了一个能够理解业务语境、解决实际问题的智能助手。