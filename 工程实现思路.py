"""
==========================================
合租生活模拟器 - 工程实现方案
==========================================

这是一个完整的代码框架示例，包含详细注释
你可以直接复制这些代码到对应的文件中

项目结构：
shehui-copy/
├── config.py              # 配置文件
├── resource_manager.py    # 资源管理
├── npc_character.py       # NPC角色类
├── agent_system.py        # 智能体系统
├── game_loop.py           # 主循环
├── utils.py               # 工具函数
└── app.py                 # 程序入口
"""

# ==========================================
# 1. config.py - 配置文件
# ==========================================
"""
作用：统一管理所有配置参数
为什么需要：避免硬编码，方便修改
"""

# API配置
GEMINI_API_KEY = "your-api-key-here"  # 你的Google AI API密钥
MODEL_NAME = "gemini-2.0-flash-exp"   # 使用的模型名称

# NPC配置
NPCS = {
    "小明": "小明-程序员-提示词.txt",
    "小庄": "小庄-设计师-提示词.txt",
    "小张": "小张-厨师-提示词.txt",
    "小李": "小李-学生-提示词.txt"
}

# 资源配置
# single: 单人使用，multiple: 多人使用
RESOURCES = {
    "厕所": {"type": "single", "capacity": 1},
    "厨房": {"type": "single", "capacity": 1},
    "客厅": {"type": "multiple", "capacity": 4},
}

# 时间配置
TICK_INTERVAL = 5  # 每个时间步间隔（秒）


# ==========================================
# 2. resource_manager.py - 资源管理系统
# ==========================================
"""
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
        
        status_lines.append("- 卧室：各自可用")
        
        return "\n".join(status_lines)


# ==========================================
# 3. npc_character.py - NPC角色类
# ==========================================
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
import config

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
        
        # 注意：使用chat模式后，不再需要initialized标记
        # AI会自动记住整个对话历史
    
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
        
        参数:
            text: AI返回的文本
            time: 当前时间
            scene: 当前场景
            
        返回:
            解析后的字典
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


# ==========================================
# 4. agent_system.py - 智能体系统
# ==========================================
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
            构建好的提示词
        """
        prompt = f"现在是{time}，场景是{scene}。\n\n"
        
        # 资源状态
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
        
        参数:
            text: AI返回的文本
            npc_output: NPC的输出
            
        返回:
            解析后的字典
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
        
        # 提取转发对话
        dialog_match = re.search(r'1-[「『](.+?)[」』]对我说[「『](.+?)[」』]', text)
        if dialog_match:
            result["对话目标"] = npc_output.get("对话目标")
            result["转发对话"] = npc_output.get("对话内容")
        
        # 提取智能体建议
        advice_match = re.search(r'2-审核智能体说[「『](.+?)[」』]', text)
        if advice_match:
            result["智能体建议"] = advice_match.group(1)
        
        return result


# ==========================================
# 5. game_loop.py - 游戏主循环
# ==========================================
"""
作用：控制整个模拟的运行
核心功能：
1. 初始化所有系统
2. 运行时间步循环
3. 协调NPC和智能体
4. 打印运行日志

为什么需要：
- 统一调度所有模块
- 管理游戏状态
"""

class GameLoop:
    """游戏主循环"""
    
    def __init__(self):
        """初始化游戏循环"""
        # 创建资源管理器
        self.resource_manager = ResourceManager()
        
        # 创建智能体
        self.agent = AgentSystem(self.resource_manager)
        
        # 创建所有NPC
        self.npcs = {}
        for name, prompt_file in config.NPCS.items():
            self.npcs[name] = NPCCharacter(name, prompt_file)
        
        # 消息队列（每个NPC的收件箱）
        self.messages = {name: [] for name in self.npcs}
        
        # 游戏状态
        self.time = "早上7:00"
        self.tick_count = 0
    
    def run_tick(self):
        """
        运行一个时间步
        
        一个时间步的流程：
        1. 遍历所有NPC
        2. 每个NPC读取消息并行动
        3. 智能体审核NPC行为
        4. 处理审核结果（转发对话/给建议）
        5. 清空已读消息
        """
        print(f"\n{'='*60}")
        print(f"时间: {self.time} | Tick: {self.tick_count}")
        print(f"{'='*60}\n")
        
        # 遍历所有NPC
        for name, npc in self.npcs.items():
            # 1. NPC行动
            messages = self.messages[name]
            output = npc.act(self.time, f"{name}的位置", messages)
            
            # 2. 智能体审核
            result = self.agent.review(output, self.time, f"{name}的位置")
            
            # 3. 打印日志
            self.print_log(name, output, result)
            
            # 4. 处理结果
            self.handle_result(name, output, result)
            
            # 5. 清空消息
            self.messages[name] = []
        
        # 更新时间
        self.tick_count += 1
    
    def handle_result(self, npc_name, output, result):
        """
        处理智能体的审核结果
        
        参数:
            npc_name: NPC名字
            output: NPC输出
            result: 智能体审核结果
        """
        # 转发对话
        if result.get('转发对话') and result.get('对话目标'):
            target = result['对话目标']
            if target in self.messages:
                self.messages[target].append({
                    'from': npc_name,
                    'content': result['转发对话'],
                    'type': '对话'
                })
        
        # 智能体建议
        if result.get('智能体建议'):
            self.messages[npc_name].append({
                'from': '智能体',
                'content': result['智能体建议'],
                'type': '建议'
            })
    
    def print_log(self, name, output, result):
        """
        打印日志
        
        参数:
            name: NPC名字
            output: NPC输出
            result: 智能体结果
        """
        print(f"[{name}]")
        print(f"  想法: {output['想法']}")
        
        if output['对话目标'] and output['对话内容']:
            print(f"  对话: 对{output['对话目标']}说「{output['对话内容']}」")
        
        if result['智能体建议']:
            print(f"  → 智能体: {result['智能体建议']}")
        
        print()
    
    def run(self, num_ticks=5):
        """
        运行模拟
        
        参数:
            num_ticks: 运行的时间步数
        """
        for _ in range(num_ticks):
            self.run_tick()
            import time
            time.sleep(config.TICK_INTERVAL)


# ==========================================
# 6. app.py - 程序入口
# ==========================================
"""
作用：程序的启动入口
功能：
1. 初始化游戏循环
2. 启动模拟
3. 处理异常
"""

def main():
    """主函数"""
    print("="*60)
    print("    合租生活模拟器")
    print("="*60)
    print()
    
    try:
        # 创建游戏循环
        game = GameLoop()
        
        # 运行5个时间步
        game.run(num_ticks=5)
        
    except KeyboardInterrupt:
        print("\n\n模拟已停止")
    except Exception as e:
        print(f"\n\n错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n模拟结束")

if __name__ == "__main__":
    main()


"""
==========================================
使用说明
==========================================

1. 安装依赖:
   pip install google-genai

2. 配置API密钥:
   在config.py中设置你的GEMINI_API_KEY

3. 准备提示词文件:
   确保以下文件存在：
   - 小明-程序员-提示词.txt
   - 小庄-设计师-提示词.txt
   - 小张-厨师-提示词.txt
   - 小李-学生-提示词.txt
   - 智能体-系统提示词.txt

4. 运行程序:
   python app.py

==========================================
学习要点
==========================================

1. 类的设计:
   - ResourceManager: 管理状态
   - NPCCharacter: 封装AI调用
   - AgentSystem: 审核协调
   - GameLoop: 调度控制

2. 数据流转:
   NPC → 智能体 → 处理结果 → 更新状态

3. 提示词管理:
   - 首次提示词: 建立认知
   - 后续提示词: 快速交互

4. 错误处理:
   - try-except捕获异常
   - 返回默认值保证继续运行

5. 调试技巧:
   - 打印日志观察流程
   - 逐步测试每个模块
   - 简化场景定位问题

6. 核心设计理念:
   - AI完全自主判断，不做任何硬编码干预
   - 智能体通过提示词中的资源状态自主决策
   - 不用关键词匹配，让AI理解语义
   - 保持系统的灵活性和智能性

==========================================
关键设计决策说明
==========================================

【为什么不做预判？】
在 AgentSystem 中，我们移除了 detect_conflict() 函数，
原因：
- ❌ 关键词匹配太死板，无法理解复杂语义
- ❌ 需要维护大量关键词列表
- ❌ 限制了AI的智能判断能力

【AI自主判断的优势】
✅ 智能理解："想去洗个澡" = "想洗澡" = "准备洗漱"
✅ 灵活决策：根据上下文自主判断是否需要干预
✅ 无需维护：不需要添加新规则和关键词
✅ 更真实：像真实的管理者一样做判断

【实现方式】
智能体AI通过提示词接收：
1. 当前所有资源的使用状态
2. NPC的想法和对话
3. 当前时间和场景

然后自主决定：
- 是否存在资源冲突
- 是否需要给出建议
- 是否需要转发对话

这就是"AI驱动的社会模拟"的核心理念！

==========================================
记忆系统说明
==========================================

【使用Gemini的Chat模式（推荐）】

旧方式（无记忆）：
```python
# 每次都是独立调用
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents=prompt
)
# 问题：AI不记得之前的对话
```

新方式（有记忆）：
```python
# 创建持续对话会话
chat = client.chats.create(
    model="gemini-2.0-flash-exp",
    config={
        "system_instruction": "你是小明，程序员..."
    }
)

# 发送消息（AI会记住所有历史）
response = chat.send_message("现在是早上7:00...")
```

【记忆的好处】

1. NPC行为更连贯
   - 记得自己说过要去洗澡
   - 记得和谁约了吃饭
   - 记得之前的对话内容

2. 智能体决策更准确
   - 记得之前处理过的冲突
   - 记得谁在使用什么资源
   - 可以追踪长期的行为模式

3. 涌现更真实的互动
   - NPC之间的关系会演化
   - 可以产生长期的故事线
   - 行为模式更像真人

【实现对比】

场景：小明想洗澡，但厕所被占用

无记忆模式：
- 第1次：AI说"想去洗澡"
- 智能体说："厕所被占用，请等待"
- 第2次：AI可能又说"想去洗澡"（忘记了刚才的事）

有记忆模式：
- 第1次：AI说"想去洗澡"
- 智能体说："厕所被占用，请等待"
- 第2次：AI说"好的，那我先看会书等一下"（记得刚才被告知要等）
- 第3次：AI主动问"厕所现在空了吗？"（记得之前想洗澡）

【技术细节】

system_instruction vs 普通prompt：
- system_instruction: 角色设定，始终生效
- 普通prompt: 当前轮的具体情况

对话历史自动管理：
- Gemini会自动维护对话历史
- 不需要手动管理历史记录
- 每次调用send_message()都会累积记忆

==========================================
"""

