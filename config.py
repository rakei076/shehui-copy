# API配置
GEMINI_API_KEY = "AIzaSyCn5ubu9I3LxuAksQBOzhv3ztuohKVrb1Q"
MODEL_NAME = "gemini-2.5-flash"

# NPC配置
NPCS = {
    "小明": "小明-程序员-提示词.txt",
    "小庄": "小庄-设计师-提示词.txt",
    "小张": "小张-厨师-提示词.txt",
    "小李": "小李-学生-提示词.txt"
}

# 资源配置
RESOURCES = {
    "厕所": {"type": "single", "capacity": 1},
    "厨房": {"type": "single", "capacity": 1},
    "客厅": {"type": "multiple", "capacity": 4},
}

# 时间配置
TICK_INTERVAL = 5  # 每个时间步间隔（秒）
