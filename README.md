# 大语言模型驱动的AI版骗子酒馆对战框架

本项目实现了一个基于大语言模型的"骗子酒馆"(Liars' Bar)游戏对战框架。在这个游戏中，多个AI智能体（由不同的大语言模型驱动）将相互竞争，通过出牌和质疑的策略，努力成为最后一位存活者。

## 文件结构

项目包含以下主要文件：

- `game.py`: 游戏主体逻辑实现
- `player.py`: 玩家类实现，包含LLM智能体的核心交互逻辑
- `llm_client.py`: LLM客户端实现，处理与大语言模型API的通信
- `game_record.py`: 游戏记录模块，用于记录游戏过程和保存结果
- `game_analyze.py`: 游戏分析工具，用于分析游戏记录和生成可视化结果
- `prompt/`: 提示词模板目录，包含游戏规则和各种场景的提示词模板
  - `rule_base.txt`: 游戏规则基础描述
  - `play_card_prompt_template.txt`: 出牌场景提示词模板
  - `challenge_prompt_template.txt`: 质疑场景提示词模板
  - `reflect_prompt_template.txt`: 反思场景提示词模板

## 配置方法

在运行游戏前，您需要配置以下内容：

1. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

2. **配置LLM API**:
   在 `llm_client.py` 中，配置您的API密钥和基础URL：
   ```python
   API_BASE_URL = "YOUR_API_BASE_URL"
   API_KEY = "YOUR_API_KEY"
   ```

3. **配置玩家**:
   在 `game.py` 的主函数中，配置您要使用的玩家和对应的模型：
   ```python
   player_configs = [
       {
           "name": "Player1",
           "model": "your-model-name-1"
       },
       {
           "name": "Player2",
           "model": "your-model-name-2"
       }
   ]
   ```

## 使用步骤

1. 确保已完成上述配置
2. 运行游戏：
   ```bash
   python game.py
   ```
3. 游戏将自动进行，直到有玩家获胜
4. 游戏记录将保存在 `game_records` 目录下的JSON文件中

## Demo

为了展示游戏的运行效果，我们提供了一个完整的游戏演示视频。视频中展示了4个不同的大语言模型驱动的AI智能体（DeepSeek, ChatGPT, Claude, Gemini）进行的一局完整游戏。

您可以在以下链接观看演示视频：
[演示视频链接](https://example.com/demo-video)  
(注：请替换为实际视频链接)

## 已知问题

1. **模型输出不稳定**：有时LLM可能不按照要求的JSON格式输出，我们已经实现了重试机制来应对这种情况。

2. **解决方法**：如果遇到持续的格式问题，请检查提示词模板是否清晰，并考虑添加更明确的格式指导。

## 贡献

欢迎提交Pull Request来改进本项目！

## 许可证

本项目采用MIT许可证 - 详情请查看LICENSE文件