"""
第二次运行 - 加载记忆并继续对话
功能:
1. 从文件加载对话历史
2. 恢复聊天会话
3. 发送第二条消息
4. 显示完整对话历史
"""
from google import genai
from google.genai import types
import json
import os

# 检查历史文件是否存在
if not os.path.exists("chat_history.json"):
    print("❌ 错误: 找不到 chat_history.json 文件")
    print("请先运行 app_first.py 创建对话历史")
    exit(1)

# 加载对话历史
print("=== 第二次运行 ===")
print("正在加载对话记忆...")
with open("chat_history.json", "r", encoding="utf-8") as f:
    history_data = json.load(f)

print(f"✅ 成功加载 {len(history_data)} 条历史记录\n")

# 初始化客户端
client = genai.Client(
    api_key="AIzaSyCn5ubu9I3LxuAksQBOzhv3ztuohKVrb1Q"
)

# 创建新的聊天会话并恢复历史
chat = client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        temperature=1.0
    )
)

# 恢复对话历史
# 注意: Gemini API的历史恢复需要重新发送消息来建立上下文
print("正在恢复对话上下文...")
for i, msg in enumerate(history_data):
    if msg["role"] == "user":
        # 重新发送用户消息(但不显示回复)
        chat.send_message(msg["content"])
        print(f"已恢复记忆 {i+1}: {msg['content']}")

print("\n=== 继续对话 ===")
# 发送第二条消息
print("发送消息: 你认为ai未来会取代人类吗")
response = chat.send_message("你认为ai未来会取代人类吗")
print(f"AI回复: {response.text}\n")

# 显示完整对话历史
print("=== 完整对话历史 ===")
for message in chat.get_history():
    print(f"{message.role}: {message.parts[0].text}")
    print("-" * 50)

# 更新保存的历史记录
history_data = []
for message in chat.get_history():
    message_dict = {
        "role": message.role,
        "content": message.parts[0].text
    }
    history_data.append(message_dict)

with open("chat_history.json", "w", encoding="utf-8") as f:
    json.dump(history_data, f, ensure_ascii=False, indent=2)

print("\n✅ 更新后的对话历史已保存")

