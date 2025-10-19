"""
资源管理系统

作用：管理所有资源的使用状态
核心功能：
1. 检查资源是否可用
2. 占用和释放资源
3. 生成资源状态文本

为什么需要：
- 智能体需要知道资源状态来判断冲突
- 统一管理避免状态不一致
"""

class ResourceManager:
    """资源管理器"""
    
    def __init__(self):
        """初始化所有资源为空闲状态"""
        self.resources = {
            "厕所": {"status": "空闲", "user": None},
            "厨房": {"status": "空闲", "user": None},
            "客厅": {"status": "空闲", "users": []},
        }
    
    def is_available(self, resource_name, user_name):
        """
        检查资源是否可用
        
        参数:
            resource_name: 资源名称（如"厕所"）
            user_name: 想使用的用户名
            
        返回:
            True: 可用, False: 被占用
        """
        if resource_name not in self.resources:
            return True  # 未定义的资源默认可用
        
        resource = self.resources[resource_name]
        
        # 单人资源：检查是否有人使用
        if resource_name in ["厕所", "厨房"]:
            return resource["user"] is None
        
        # 多人资源：检查是否已满
        if resource_name == "客厅":
            return len(resource["users"]) < 4
        
        return True
    
    def occupy(self, resource_name, user_name):
        """
        占用资源
        
        参数:
            resource_name: 资源名称
            user_name: 用户名
        """
        if resource_name not in self.resources:
            return
        
        resource = self.resources[resource_name]
        
        # 单人资源
        if resource_name in ["厕所", "厨房"]:
            resource["status"] = "使用中"
            resource["user"] = user_name
        
        # 多人资源
        elif resource_name == "客厅":
            if user_name not in resource["users"]:
                resource["users"].append(user_name)
            if len(resource["users"]) > 0:
                resource["status"] = "使用中"
    
    def release(self, resource_name, user_name):
        """
        释放资源
        
        参数:
            resource_name: 资源名称
            user_name: 用户名
        """
        if resource_name not in self.resources:
            return
        
        resource = self.resources[resource_name]
        
        # 单人资源
        if resource_name in ["厕所", "厨房"]:
            if resource["user"] == user_name:
                resource["status"] = "空闲"
                resource["user"] = None
        
        # 多人资源
        elif resource_name == "客厅":
            if user_name in resource["users"]:
                resource["users"].remove(user_name)
            if len(resource["users"]) == 0:
                resource["status"] = "空闲"
    
    def get_status_text(self):
        """
        获取资源状态文本（用于智能体）
        
        返回:
            格式化的资源状态文本
        """
        status_lines = []
        
        # 厕所状态
        if self.resources["厕所"]["user"]:
            status_lines.append(f"- 厕所：{self.resources['厕所']['user']}使用中")
        else:
            status_lines.append("- 厕所：空闲")
        
        # 厨房状态
        if self.resources["厨房"]["user"]:
            status_lines.append(f"- 厨房：{self.resources['厨房']['user']}使用中")
        else:
            status_lines.append("- 厨房：空闲")
        
        # 客厅状态
        if self.resources["客厅"]["users"]:
            users_str = "、".join(self.resources["客厅"]["users"])
            status_lines.append(f"- 客厅：{users_str}")
        else:
            status_lines.append("- 客厅：空闲")
        
        status_lines.append("- 卧室：各自可用（可以自由进入）")
        
        return "\n".join(status_lines)
