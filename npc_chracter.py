"""
作用：定义NPC的行为和AI调用
核心功能：
1. 加载角色提示词
2. 调用AI生成行为
3. 解析AI输出
4. 处理环境感知信息

为什么需要：
- 每个NPC是独立的AI实例
- 封装AI调用逻辑
- 接收并响应环境感知
"""
from google import genai
from google.genai import types
import config
import re

class NPCCharacter:
    """NPC角色类（带记忆功能）"""
    
    def __init__(self, name, prompt_file):
        """
        初始化NPC
        
        参数:
            name: 角色名字
            prompt_file: 提示词文件路径
        """
        self.name = name
        self.prompt_file = prompt_file
        
        # 创建AI客户端
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        
        # 加载首次提示词作为系统指令
        system_instruction = self.load_first_prompt()
        
        # 创建持续对话会话（AI会记住所有历史对话）
        self.chat = self.client.chats.create(
            model=config.MODEL_NAME,
            config={
                "system_instruction": system_instruction  # 角色设定
            }
        )
    
    def load_first_prompt(self):
        """
        从txt文件加载首次提示词
        
        返回:
            首次提示词文本
        """
        try:
            with open(self.prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取首次提示词部分
                start = content.find("首次提示词（系统初始化）")
                end = content.find("后续提示词（每轮交互）")
                if start != -1 and end != -1:
                    return content[start:end].strip()
                return content  # 如果找不到标记，返回全部内容
        except Exception as e:
            print(f"警告：加载{self.name}的提示词失败: {e}")
            return ""
    
    def build_prompt(self, time, scene, messages):
        """
        构建后续提示词
        
        参数:
            time: 当前时间
            scene: 当前场景
            messages: 接收到的消息列表
                
        返回:
            构建好的提示词
        """
        prompt = f"你是{self.name}，现在是{time}，你在{scene}。\n\n"
        
        # 添加接收到的消息
        prompt += "【接收到的信息】\n"
        
        # 分离对话和环境感知
        dialog_msg = None
        perception_msg = None
        
        if messages:
            for msg in messages:
                if msg['type'] == '对话':
                    dialog_msg = msg
                elif msg['type'] == '环境感知':
                    perception_msg = msg
        
        # 1. 对话信息
        if dialog_msg:
            prompt += f"1-{{{dialog_msg['from']}}}对我说{{{dialog_msg['content']}}}\n"
        else:
            prompt += "1-{null}对我说{null}\n"
        
        # 2. 环境感知
        if perception_msg:
            prompt += f"2-环境感知: {{{perception_msg['content']}}}\n"
        else:
            prompt += "2-环境感知: {周围很安静}\n"
        
        prompt += "\n【请按照格式回复】\n"
        prompt += "时间: xxx 场景: xxx\n"
        prompt += "1-想法:{想法内容，必须不少于200字，要结合环境感知}\n"
        prompt += "2-对{角色名}说的话{对话内容}\n"
        
        prompt += "\n【重要规则】\n"
        prompt += "- 想法必须不少于200字，要详细描述你的心理活动\n"
        prompt += "- 想法要结合环境感知的内容（听到什么、看到什么、闻到什么）\n"
        prompt += "- 对话目标必须是具体名字：{小明}、{小庄}、{小张}、{小李}\n"
        prompt += "- 如果想对多人说话，写成：{小明,小庄,小张}（用逗号分隔）\n"
        prompt += "- 禁止使用：{全体室友}、{大家}、{室友们} 等模糊称呼\n"
        prompt += "- 如果没有对话，写：2-对{null}说的话{null}\n"
        
        return prompt
    
    def act(self, time, scene, messages):
        """
        NPC思考并行动（使用记忆模式）
        
        参数:
            time: 当前时间
            scene: 当前场景
            messages: 接收到的消息
                
        返回:
            解析后的输出字典
        """
        # 构建当前轮的提示词
        prompt = self.build_prompt(time, scene, messages)
        
        try:
            # 发送消息到对话会话（AI会记住之前所有对话）
            response = self.chat.send_message(prompt)
            
            # 解析输出
            return self.parse_output(response.text, time, scene)
            
        except Exception as e:
            print(f"错误：{self.name}的AI调用失败: {e}")
            # 返回默认输出
            return {
                "角色": self.name,
                "时间": time,
                "场景": scene,
                "想法": "（思考中...）",
                "对话目标": None,
                "对话内容": None
            }
    
    def parse_output(self, text, time, scene):
        """
        解析AI输出
        
        格式要求：使用 {} 包裹内容
        1-想法:{内容}
        2-对{角色}说的话{内容}
        
        参数:
            text: AI返回的文本
            time: 当前时间
            scene: 当前场景
            
        返回:
            解析后的字典
        """
        result = {
            "角色": self.name,
            "时间": time,
            "场景": scene,
            "想法": None,
            "对话目标": None,
            "对话内容": None
        }
        
        # 提取想法 - 使用 {} 包裹
        thought_match = re.search(r'1-想法[：:]\s*\{(.+?)\}', text, re.DOTALL)
        if thought_match:
            result["想法"] = thought_match.group(1).strip()
        
        # 提取对话 - 使用 {} 包裹
        dialog_match = re.search(r'2-对\{(.+?)\}说的话\{(.+?)\}', text, re.DOTALL)
        if dialog_match:
            result["对话目标"] = dialog_match.group(1).strip()
            result["对话内容"] = dialog_match.group(2).strip()
        
        return result
