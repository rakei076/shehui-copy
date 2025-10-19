"""
第一次运行 - 开始对话并保存记忆
功能: 
1. 创建聊天会话
2. 发送第一条消息
3. 保存对话历史到文件
"""
from google import genai
from google.genai import types
import json

# 初始化客户端
client = genai.Client(
    api_key="AIzaSyCn5ubu9I3LxuAksQBOzhv3ztuohKVrb1Q"
)

# 创建新的聊天会话
chat = client.chats.create(model="gemini-2.5-flash")

# 发送第一条消息
print("=== 第一次运行 ===")
print("发送消息: I have 2 dogs in my house.")
response = chat.send_message("I have 2 dogs in my house.")
print(f"AI回复: {response.text}\n")

# 获取对话历史
history = chat.get_history()

# 将历史保存到文件
history_data = []
for message in history:
    message_dict = {
        "role": message.role,
        "content": message.parts[0].text
    }
    history_data.append(message_dict)
    print(f"保存记忆 - {message.role}: {message.parts[0].text}")

# 保存到JSON文件
with open("chat_history.json", "w", encoding="utf-8") as f:
    json.dump(history_data, f, ensure_ascii=False, indent=2)

print("\n✅ 对话历史已保存到 chat_history.json")
print("现在可以运行 app_second.py 继续对话")

