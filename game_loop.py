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

from resource_manager import ResourceManager
from agent_system import AgentSystem
from npc_chracter import NPCCharacter
import config

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