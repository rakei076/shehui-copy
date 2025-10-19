"""
==========================================
Gemini记忆模式对比示例
==========================================

这个文件展示两种方式的区别，帮助你理解为什么需要使用记忆模式
"""

from google import genai

API_KEY = "your-api-key"

# ==========================================
# 方式1：无记忆模式（旧方式）
# ==========================================

def example_without_memory():
    """无记忆模式示例"""
    print("=" * 60)
    print("方式1：无记忆模式")
    print("=" * 60)
    
    client = genai.Client(api_key=API_KEY)
    
    # 第1次对话
    print("\n第1次对话：")
    prompt1 = "你是小明，现在是早上7:00，你想做什么？"
    response1 = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt1
    )
    print(f"AI: {response1.text}")
    # AI可能回答："我想去洗澡"
    
    # 第2次对话（完全独立，不记得第1次）
    print("\n第2次对话：")
    prompt2 = "智能体说：厕所被占用了，请等一下。你现在想做什么？"
    response2 = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt2
    )
    print(f"AI: {response2.text}")
    # 问题：AI不记得自己刚才说要去洗澡
    # AI可能回答不连贯的内容
    
    # 第3次对话（还是不记得）
    print("\n第3次对话：")
    prompt3 = "现在是早上7:05，你想做什么？"
    response3 = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt3
    )
    print(f"AI: {response3.text}")
    # 问题：AI不记得之前的所有对话
    
    print("\n❌ 问题：每次都是新对话，AI没有记忆")


# ==========================================
# 方式2：有记忆模式（新方式，推荐）
# ==========================================

def example_with_memory():
    """有记忆模式示例"""
    print("\n\n" + "=" * 60)
    print("方式2：有记忆模式（推荐）")
    print("=" * 60)
    
    client = genai.Client(api_key=API_KEY)
    
    # 创建对话会话，设置角色身份
    chat = client.chats.create(
        model="gemini-2.0-flash-exp",
        config={
            "system_instruction": "你是小明，一个大一的程序员专业学生，性格内向..."
        }
    )
    
    # 第1次对话
    print("\n第1次对话：")
    prompt1 = "现在是早上7:00，你想做什么？"
    response1 = chat.send_message(prompt1)
    print(f"AI: {response1.text}")
    # AI回答："我想去洗澡"
    # 并且记住了这个想法
    
    # 第2次对话（AI记得第1次的内容）
    print("\n第2次对话：")
    prompt2 = "智能体说：厕所被占用了，请等一下。"
    response2 = chat.send_message(prompt2)
    print(f"AI: {response2.text}")
    # AI回答："好的，那我先看会书，等厕所空了再去"
    # AI记得自己想去洗澡，所以回答很连贯
    
    # 第3次对话（AI记得所有之前的对话）
    print("\n第3次对话：")
    prompt3 = "现在是早上7:05，厕所空了。"
    response3 = chat.send_message(prompt3)
    print(f"AI: {response3.text}")
    # AI回答："太好了！现在可以去洗澡了"
    # AI记得自己一直想洗澡，行为非常连贯
    
    print("\n✅ 优势：AI记住所有对话，行为连贯自然")


# ==========================================
# 完整对比：模拟3个回合
# ==========================================

def full_comparison():
    """完整对比示例"""
    print("\n\n" + "=" * 60)
    print("完整对比：模拟小明的一天")
    print("=" * 60)
    
    # 无记忆模式
    print("\n【无记忆模式的结果】")
    print("-" * 60)
    print("第1回合：")
    print("  提示：现在是早上7:00，你想做什么？")
    print("  AI: 我想去洗澡")
    print()
    print("第2回合：")
    print("  提示：智能体说厕所被占用")
    print("  AI: 我想吃早饭  ← 忘记了刚才想洗澡")
    print()
    print("第3回合：")
    print("  提示：现在是早上7:05")
    print("  AI: 我想学习  ← 完全不连贯")
    print()
    print("❌ 问题：行为不连贯，像失忆了一样")
    
    # 有记忆模式
    print("\n【有记忆模式的结果】")
    print("-" * 60)
    print("第1回合：")
    print("  提示：现在是早上7:00，你想做什么？")
    print("  AI: 我想去洗澡")
    print("  [AI记住：我想洗澡]")
    print()
    print("第2回合：")
    print("  提示：智能体说厕所被占用")
    print("  AI: 好的，那我先看会书，等厕所空了再去")
    print("  [AI记住：我想洗澡 + 厕所被占用 + 我在等待]")
    print()
    print("第3回合：")
    print("  提示：现在是早上7:05，厕所空了")
    print("  AI: 太好了！现在可以去洗澡了")
    print("  [AI记住：所有之前的对话，行为连贯]")
    print()
    print("✅ 优势：行为连贯，像真人一样有记忆")


# ==========================================
# 技术细节说明
# ==========================================

def technical_details():
    """技术细节说明"""
    print("\n\n" + "=" * 60)
    print("技术细节：如何实现记忆")
    print("=" * 60)
    
    print("""
【Chat对象的工作原理】

1. 创建会话时设置角色：
   chat = client.chats.create(
       model="gemini-2.0-flash-exp",
       config={
           "system_instruction": "你是小明..."  # 角色设定，永久生效
       }
   )

2. 每次发送消息都会累积历史：
   response1 = chat.send_message("消息1")  # 历史：[消息1]
   response2 = chat.send_message("消息2")  # 历史：[消息1, AI回复1, 消息2]
   response3 = chat.send_message("消息3")  # 历史：[消息1, AI回复1, 消息2, AI回复2, 消息3]

3. AI在处理新消息时能看到完整历史：
   当前输入 = system_instruction + 历史对话 + 新消息
   
【对比】

无记忆模式：
  每次调用：只看到当前提示词
  AI视角：每次都是第一次见面

有记忆模式：
  每次调用：看到角色设定 + 所有历史对话 + 当前输入
  AI视角：就像和老朋友连续聊天

【在你的项目中】

NPC（小明、小庄等）：
- 每个NPC有自己的chat对象
- 记住自己说过的话
- 记住收到的消息
- 行为更加连贯

智能体：
- 有自己的chat对象
- 记住审核过的所有NPC行为
- 记住之前的冲突处理
- 决策更加一致

【内存管理】

注意：对话历史会累积，如果运行很长时间：
- 历史记录会很长
- 可能达到token限制
- 可以定期重置chat对象（如每天重置）

示例：
if time == "00:00":  # 每天0点
    # 重置chat，但保留角色设定
    chat = client.chats.create(...)
""")


# ==========================================
# 实际应用示例
# ==========================================

def practical_example():
    """实际应用示例"""
    print("\n\n" + "=" * 60)
    print("实际应用：在你的项目中如何使用")
    print("=" * 60)
    
    print("""
【NPC类实现】

class NPCCharacter:
    def __init__(self, name, prompt_file):
        self.name = name
        self.client = genai.Client(api_key=API_KEY)
        
        # 加载角色设定
        system_instruction = self.load_first_prompt()
        
        # 创建持续对话会话
        self.chat = self.client.chats.create(
            model="gemini-2.0-flash-exp",
            config={
                "system_instruction": system_instruction
            }
        )
    
    def act(self, time, scene, messages):
        # 构建当前情况
        prompt = f"现在是{time}，你在{scene}..."
        
        # 发送到会话（AI会记住所有历史）
        response = self.chat.send_message(prompt)
        
        return response.text

【智能体类实现】

class AgentSystem:
    def __init__(self, resource_manager):
        self.client = genai.Client(api_key=API_KEY)
        
        # 加载智能体设定
        system_instruction = self.load_first_prompt()
        
        # 创建智能体会话
        self.chat = self.client.chats.create(
            model="gemini-2.0-flash-exp",
            config={
                "system_instruction": system_instruction
            }
        )
    
    def review(self, npc_output, time, scene):
        # 构建审核信息
        prompt = f"资源状态：...\\nNPC行为：..."
        
        # 发送到会话（智能体记住所有审核历史）
        response = self.chat.send_message(prompt)
        
        return response.text

【运行效果】

启动游戏：
- 创建4个NPC，每个有自己的chat
- 创建1个智能体，有自己的chat
- 总共5个独立的对话会话

第1回合：
- 小明chat: 记住小明的行为
- 小庄chat: 记住小庄的行为
- 小张chat: 记住小张的行为
- 小李chat: 记住小李的行为
- 智能体chat: 记住所有审核

第2回合：
- 每个chat都记得第1回合的内容
- 行为变得连贯

第N回合：
- 每个chat记得所有历史
- 产生复杂的社会互动
- 涌现真实的关系演化
""")


# ==========================================
# 主函数
# ==========================================

if __name__ == "__main__":
    print("""
这个文件展示了两种AI调用方式的区别：

1. 无记忆模式：每次调用都是独立的
2. 有记忆模式：AI记住所有对话历史

在你的项目中，应该使用【有记忆模式】，
这样NPC和智能体的行为才会连贯、真实。
""")
    
    # 取消注释来运行示例（需要有效的API_KEY）
    # example_without_memory()
    # example_with_memory()
    # full_comparison()
    technical_details()
    practical_example()
    
    print("\n" + "=" * 60)
    print("总结：使用chat模式让AI拥有记忆，行为更加真实！")
    print("=" * 60)

