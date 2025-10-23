"""
作用：控制整个模拟的运行
核心功能：
1. 初始化所有系统
2. 运行时间步循环
3. 协调NPC和智能体
4. 打印运行日志
5. 分发环境感知信息

为什么需要：
- 统一调度所有模块
- 管理游戏状态
- 协调环境感知生成和分发
"""

from agent_system import AgentSystem
from npc_chracter import NPCCharacter
import config
import time

class GameLoop:
    """游戏主循环"""
    
    def __init__(self):
        """初始化游戏循环"""
        # 创建智能体（环境感知系统）
        self.agent = AgentSystem()
        
        # 创建所有NPC
        self.npcs = {}
        for name, prompt_file in config.NPCS.items():
            self.npcs[name] = NPCCharacter(name, prompt_file)
        
        # 消息队列（每个NPC的收件箱）
        self.messages = {name: [] for name in self.npcs}
        
        # 游戏状态
        self.time = "早上7:00"
        self.tick_count = 0
        
        # 时间系统（用于推进时间）
        self.hour = 7
        self.minute = 0
    
    def get_current_time(self):
        """获取当前时间字符串"""
        period = "早上" if self.hour < 12 else "下午" if self.hour < 18 else "晚上"
        return f"{period}{self.hour}:{self.minute:02d}"
    
    def advance_time(self, minutes=15):
        """推进时间（默认15分钟）"""
        self.minute += minutes
        if self.minute >= 60:
            self.hour += self.minute // 60
            self.minute = self.minute % 60
        if self.hour >= 24:
            self.hour = self.hour % 24
        # 更新时间字符串
        self.time = self.get_current_time()
    
    def run_tick(self):
        """
        运行一个时间步

        新的流程：
        1. 遍历所有NPC
        2. 每个NPC读取消息并行动
        3. 智能体生成环境感知描述
        4. 处理结果（分发环境感知/转发对话）
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
            
            # 2. 智能体生成环境感知
            result = self.agent.generate_perception(name, output, self.time)
            
            # 3. 打印日志
            self.print_log(name, output, result)
            
            # 4. 处理结果（分发环境感知和对话）
            self.handle_result(name, output, result)
            
            # 5. 清空消息
            self.messages[name] = []
            
            # 延迟避免API超限
            print(f"  [等待API冷却...]")
            time.sleep(8)  # 等待8秒，确保不超过API限制
        
        # 更新时间（每个tick推进15分钟）
        self.advance_time(minutes=15)
        self.tick_count += 1
    
    def handle_result(self, npc_name, output, result):
        """
        处理智能体的结果
        
        功能：
        1. 将环境感知分发给该NPC（下一轮使用）
        2. 将对话转发给目标NPC
        
        参数:
            npc_name: NPC名字
            output: NPC输出
            result: 智能体生成的结果
        """
        # 1. 分发环境感知给该NPC（供下一轮使用）
        if result.get('环境感知'):
            self.messages[npc_name].append({
                'from': '环境',
                'content': result['环境感知'],
                'type': '环境感知'
            })
        
        # 2. 转发对话
        if result.get('转发对话') and result.get('对话目标'):
            target = result['对话目标']
            
            # 处理多人对话（用逗号分隔的名字）
            if ',' in target:
                # 分割成多个目标
                targets = [t.strip() for t in target.split(',')]
                for t in targets:
                    if t in self.messages:
                        self.messages[t].append({
                            'from': npc_name,
                            'content': result['转发对话'],
                            'type': '对话'
                        })
            # 单人对话
            elif target in self.messages:
                self.messages[target].append({
                    'from': npc_name,
                    'content': result['转发对话'],
                    'type': '对话'
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
        
        if result.get('环境感知'):
            print(f"  🌍 环境感知: {result['环境感知'][:50]}..." if len(result['环境感知']) > 50 else f"  🌍 环境感知: {result['环境感知']}")
        
        print()
    
    def run(self, num_ticks=5):
        """
        运行模拟
        
        参数:
            num_ticks: 运行的时间步数
        """
        for _ in range(num_ticks):
            self.run_tick()
            time.sleep(config.TICK_INTERVAL)
