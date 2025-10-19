"""
作用：定义NPC的行为和AI调用
核心功能：
1. 加载角色提示词
2. 调用AI生成行为
3. 解析AI输出

为什么需要：
- 每个NPC是独立的AI实例
- 封装AI调用逻辑
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
        
        """
        self.name = name
        self.prompt_file = prompt_file
        
        # 创建AI客户端
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)

        # 加载首次提示词
        system_instruction = self.load_first_prompt()

        # 创建持续对话会话（AI会记住所有历史对话）
        self.chat = self.client.chats.create(
            model=config.MODEL_NAME,
            config={
                "system_instruction": system_instruction  # 角色设定
            }
        )
        
        # 注意：使用chat模式后，不再需要initialized标记
        # AI会自动记住整个对话历史
    def load_first_prompt(self):
        """
        从txt文件加载首次提示词
        
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
        
        """
        prompt = f"你是{self.name}，现在是{time}，你在{scene}。\n\n"
        
        # 添加接收到的消息
        prompt += "【接收到的信息】\n"
        
        if messages:
            for msg in messages:
                if msg['type'] == '对话':
                    prompt += f"1-「{msg['from']}」对我说「{msg['content']}」\n" 
                elif msg['type'] == '建议':
                    prompt += f"2-审核智能体说「{msg['content']}」\n"
        else:
            prompt += "1-「角色」对我说: null\n"
            prompt += "2-审核智能体说: null\n"
        prompt += "\n【请按照格式回复】\n"
        prompt += "时间: xxx 场景: xxx\n"
        prompt += "1-想法:「想法」\n"
        prompt += "2-对「角色」说的话「文本」\n"
        prompt += "以上若没有可以显示为null\n"
        return prompt
    def act(self, time, scene, messages):
        """
        NPC思考并行动

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
        
        """
        import re
        result = {
            "角色": self.name,
            "时间": time,
            "场景": scene,
            "想法": None,
            "对话目标": None,
            "对话内容": None
        }
        # 提取想法
        thought_match = re.search(r'1-想法[：:]\s*[「『](.+?)[」』]', text)
        if thought_match:
            result["想法"] = thought_match.group(1)
        # 提取对话
        dialog_match = re.search(r'2-对[「『](.+?)[」』]说的话[「『](.+?)[」』]', text)
        if dialog_match:
            result["对话目标"] = dialog_match.group(1)
            result["对话内容"] = dialog_match.group(2)
        return result