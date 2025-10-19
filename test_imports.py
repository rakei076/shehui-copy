"""测试所有导入是否正确"""

print("测试导入...")

try:
    print("1. 导入 config...", end=" ")
    import config
    print("✓")
except Exception as e:
    print(f"✗ {e}")

try:
    print("2. 导入 resource_manager...", end=" ")
    from resource_manager import ResourceManager
    print("✓")
except Exception as e:
    print(f"✗ {e}")

try:
    print("3. 导入 npc_chracter...", end=" ")
    from npc_chracter import NPCCharacter
    print("✓")
except Exception as e:
    print(f"✗ {e}")

try:
    print("4. 导入 agent_system...", end=" ")
    from agent_system import AgentSystem
    print("✓")
except Exception as e:
    print(f"✗ {e}")

try:
    print("5. 导入 game_loop...", end=" ")
    from game_loop import GameLoop
    print("✓")
except Exception as e:
    print(f"✗ {e}")

print("\n所有导入测试完成！")

