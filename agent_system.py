"""
作用：审核NPC行为，协调资源冲突
核心功能：
1. 接收NPC输出
2. 检测资源冲突
3. 调用AI生成建议
4. 返回审核结果

为什么需要：
- 维护全局状态
- 保证资源使用不冲突
- 转发NPC之间的对话
"""
from google import genai
from google.genai import types
import config
import re

class AgentSystem:
    """智能体系统（带记忆功能）"""
    def __init__(self, resource_manager):
        """
        初始化智能体
        参数:
            resource_manager: 资源管理器实例
        """
        self.resource_manager = resource_manager
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        
        # 加载系统指令
        system_instruction = self.load_first_prompt()
        
        # 创建持续对话会话（智能体会记住所有审核历史）
        self.chat = self.client.chats.create(
            model=config.MODEL_NAME,
            config={
                "system_instruction": system_instruction  # 智能体角色设定
            }
            
        )
        
        # 使用chat模式后，不再需要initialized标记
    def load_first_prompt(self):
        """加载智能体首次提示词"""
        try:
            with open("智能体-系统提示词.txt", 'r', encoding='utf-8') as f:
                content = f.read()
                start = content.find("首次提示词（系统初始化）")
                end = content.find("后续提示词（每轮交互）")
                if start != -1 and end != -1:
                    return content[start:end].strip()
                return content
        except Exception as e:
            print(f"警告：加载智能体提示词失败: {e}")
            return ""
    def build_prompt(self, npc_output, time, scene):
        """
        构建智能体提示词
        参数:
            npc_output: NPC输出
            time: 当前时间
            scene: 当前场景
        返回:
            True: 有冲突, False: 无冲突
        """
        prompt = f"现在是{time}，场景是{scene}。\n\n"
        prompt += "【当前资源状态】\n"
        prompt += self.resource_manager.get_status_text()
        prompt += "\n\n"

        # NPC输出
        prompt += "【接收到的NPC输出】\n"
        prompt += f"角色: {npc_output['角色']}\n"
        prompt += f"时间: {npc_output['时间']} 场景: {npc_output['场景']}\n"
        prompt += f"1-想法:「{npc_output['想法']}」\n"

        if npc_output['对话目标']:
            prompt += f"2-对「{npc_output['对话目标']}」说的话「{npc_output['对话内容']}」\n"
        else:
            prompt += "2-对「角色」说的话: null\n"
        prompt += "\n【请审核并回复】\n"
        prompt += "按照标准格式输出\n"
        return prompt
    def review(self, npc_output, time, scene):
        """
        审核NPC行为（使用记忆模式）
        完全由AI自主判断，不做任何预判或干预
        AI会：
        1. 查看NPC的想法和对话
        2. 检查当前资源状态
        3. 自主判断是否存在冲突
        4. 决定是否需要干预或转发对话
        5. 记住所有审核历史，做出更连贯的决策
        参数:
            npc_output: NPC输出
            time: 当前时间
            scene: 当前场景
        返回:
            审核结果字典
            """
        # 构建提示词（包含资源状态和NPC输出）
        prompt = self.build_prompt(npc_output, time, scene)
        
        try:
            # 发送消息到对话会话（智能体会记住之前所有审核）
            response = self.chat.send_message(prompt)
            
            # 解析输出
            return self.parse_output(response.text, npc_output)
            
        except Exception as e:
            print(f"错误：智能体AI调用失败: {e}")
            # 返回默认结果
            return {
                "判断结果": "无需干预",
                "转发对话": npc_output.get("对话内容"),
                "对话目标": npc_output.get("对话目标"),
                "智能体建议": None
            }
    def parse_output(self, text, npc_output):
        """
        解析智能体输出
        
        格式要求：使用 {} 包裹内容
        1-{角色}对我说{内容}
        2-审核智能体说{内容}
        
        参数:
            text: AI返回的文本
            npc_output: NPC输出
        返回:
            审核结果字典
        """
        import re
        result = {
            "判断结果": "无需干预",
            "转发对话": None,
            "对话目标": None,
            "智能体建议": None
        }
        
        # 提取判断结果
        if "需要干预" in text:
            result["判断结果"] = "需要干预"
        
        # 提取转发对话 - 使用 {} 包裹
        # 格式：1-{角色}对我说{内容}
        dialog_match = re.search(r'1-\{(.+?)\}对我说\{(.+?)\}', text, re.DOTALL)
        if dialog_match:
            # 如果智能体要转发对话，使用NPC原本的对话信息
            result["对话目标"] = npc_output.get("对话目标")
            result["转发对话"] = npc_output.get("对话内容")
        
        # 提取智能体建议 - 使用 {} 包裹
        advice_match = re.search(r'2-审核智能体说\{(.+?)\}', text, re.DOTALL)
        if advice_match:
            result["智能体建议"] = advice_match.group(1).strip()
        
        return result