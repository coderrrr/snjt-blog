import os
import logging
import requests
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from consulate import Consul

# 配置日志
logger = logging.getLogger("consul-client")

class ConsulClient:
    def __init__(self, host: str = None, port: int = None):
        """
        初始化Consul客户端
        
        Args:
            host: Consul服务器主机名
            port: Consul服务器端口
        """
        self.host = host or os.environ.get('CONSUL_HOST', 'consul-server')
        self.port = port or int(os.environ.get('CONSUL_PORT', 8500))
        self.consul = Consul(host=self.host, port=self.port)
        logger.info(f"已连接到Consul服务: {self.host}:{self.port}")
    
    def get_service_url(self, service_name: str) -> str:
        """
        从服务发现获取服务地址
        
        Args:
            service_name: 服务名称
            
        Returns:
            服务的完整URL
            
        Raises:
            HTTPException: 当服务不可用时
        """
        services = self.consul.catalog.service(service_name)
        if not services:
            logger.error(f"服务不可用: {service_name}")
            raise HTTPException(status_code=503, detail=f"{service_name}服务不可用")
        
        service = services[0]
        service_url = f"http://{service['ServiceAddress']}:{service['ServicePort']}"
        logger.debug(f"获取到服务地址: {service_name} -> {service_url}")
        return service_url
    
    def call_inventory_service(self, farm_id: str) -> List[Dict[str, Any]]:
        """
        调用库存服务获取可用药品
        
        Args:
            farm_id: 猪场ID
            
        Returns:
            可用药品列表
            
        Raises:
            HTTPException: 当调用服务失败时
        """
        try:
            inventory_url = f"{self.get_service_url('inventory-service')}/api/inventory"
            response = requests.get(
                inventory_url,
                params={'farm_id': farm_id},
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"调用库存服务失败: {str(e)}")
            raise HTTPException(status_code=502, detail=f"调用库存服务失败: {str(e)}")
    
    def call_disease_service(self, symptoms: List[str], age_days: int) -> Dict[str, Any]:
        """
        调用疫病数据服务获取相关疫病信息
        
        Args:
            symptoms: 症状列表
            age_days: 猪只日龄
            
        Returns:
            疫病数据
            
        Raises:
            HTTPException: 当调用服务失败时
        """
        try:
            disease_url = f"{self.get_service_url('disease-data-service')}/api/diseases"
            response = requests.post(
                disease_url,
                json={'symptoms': symptoms, 'age_days': age_days},
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"调用疫病数据服务失败: {str(e)}")
            raise HTTPException(status_code=502, detail=f"调用疫病数据服务失败: {str(e)}")
    
    def record_treatment_plan(self, treatment_record: Dict[str, Any]) -> bool:
        """
        记录治疗方案到业务系统
        
        Args:
            treatment_record: 治疗记录数据
            
        Returns:
            是否成功记录
        """
        try:
            treatment_services = self.consul.catalog.service('treatment-service')
            if not treatment_services:
                logger.warning("治疗记录服务不可用，无法保存治疗方案")
                return False
                
            treatment_url = f"{self.get_service_url('treatment-service')}/api/treatments"
            response = requests.post(treatment_url, json=treatment_record, timeout=5)
            response.raise_for_status()
            logger.info(f"治疗方案已记录到业务系统，猪场ID: {treatment_record.get('farm_id')}")
            return True
        except Exception as e:
            logger.error(f"记录治疗方案失败: {str(e)}")
            return False

# 创建默认客户端实例
consul_client = ConsulClient()