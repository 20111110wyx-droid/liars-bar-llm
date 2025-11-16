import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class PlayerInitialState:
    player_name: str
    bullet_position: int
    current_gun_position: int
    initial_hand: List[str]

class GameRecord:
    def __init__(self):
        self.game_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.record = {
            "game_id": self.game_id,
            "start_time": datetime.now().isoformat(),
            "players": [],
            "winner": None,
            "rounds": []
        }
        self.current_round = None
        self.current_round_actions = []
        self.current_round_results = {}

    def start_game(self, players: List[str]) -> None:
        """记录游戏开始信息"""
        self.record["players"] = players

    def start_round(self, round_id: int, target_card: str, round_players: List[str], 
                   starting_player: str, player_initial_states: List[PlayerInitialState],
                   player_opinions: Dict[str, Dict[str, str]]) -> None:
        """开始记录新的回合"""
        # 保存之前的回合（如果有）
        if self.current_round is not None:
            self.current_round["actions"] = self.current_round_actions
            self.current_round["results"] = self.current_round_results
            self.record["rounds"].append(self.current_round)
            
        # 重置当前回合记录
        self.current_round = {
            "round_id": round_id,
            "target_card": target_card,
            "round_players": round_players,
            "starting_player": starting_player,
            "player_initial_states": [
                {
                    "player_name": state.player_name,
                    "bullet_position": state.bullet_position,
                    "current_gun_position": state.current_gun_position,
                    "initial_hand": state.initial_hand
                }
                for state in player_initial_states
            ],
            "player_opinions": player_opinions,
            "actions": [],
            "results": {}
        }
        self.current_round_actions = []
        self.current_round_results = {}

    def record_play(self, player_name: str, played_cards: List[str], remaining_cards: List[str],
                   play_reason: str, behavior: str, next_player: str, play_thinking: str) -> None:
        """记录玩家出牌"""
        action = {
            "type": "play",
            "player": player_name,
            "played_cards": played_cards,
            "remaining_cards": remaining_cards,
            "play_reason": play_reason,
            "behavior": behavior,
            "next_player": next_player,
            "play_thinking": play_thinking,
            "timestamp": datetime.now().isoformat()
        }
        self.current_round_actions.append(action)

    def record_challenge(self, was_challenged: bool, reason: str, result: Optional[bool], 
                       challenge_thinking: str) -> None:
        """记录质疑结果"""
        action = {
            "type": "challenge",
            "was_challenged": was_challenged,
            "reason": reason,
            "result": result,  # None表示未质疑，True表示质疑成功，False表示质疑失败
            "challenge_thinking": challenge_thinking,
            "timestamp": datetime.now().isoformat()
        }
        self.current_round_actions.append(action)

    def record_shooting(self, shooter_name: str, bullet_hit: bool) -> None:
        """记录射击结果"""
        action = {
            "type": "shooting",
            "shooter": shooter_name,
            "bullet_hit": bullet_hit,
            "timestamp": datetime.now().isoformat()
        }
        self.current_round_actions.append(action)

    def finish_game(self, winner: str) -> None:
        """记录游戏结束信息并保存到文件"""
        # 确保最后一轮也被保存
        if self.current_round is not None:
            self.current_round["actions"] = self.current_round_actions
            self.current_round["results"] = self.current_round_results
            self.record["rounds"].append(self.current_round)
            
        self.record["winner"] = winner
        self.record["end_time"] = datetime.now().isoformat()
        self.save_to_file()

    def save_to_file(self) -> None:
        """将游戏记录保存到JSON文件"""
        # 确保保存目录存在
        directory = "game_records"
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # 保存记录
        file_path = os.path.join(directory, f"{self.game_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.record, f, ensure_ascii=False, indent=2)
        print(f"游戏记录已保存到 {file_path}")

    def get_latest_round_info(self) -> str:
        """获取当前轮次的基础信息，用于生成提示词"""
        if not self.current_round:
            return ""
        
        info = f"轮次：{self.current_round['round_id']}\n"
        info += f"目标牌：{self.current_round['target_card']}\n"
        info += f"当前参与玩家：{', '.join(self.current_round['round_players'])}\n"
        info += f"起始玩家：{self.current_round['starting_player']}\n"
        
        return info

    def get_latest_round_actions(self, player_name: str, include_latest: bool = True) -> str:
        """获取当前轮次中与指定玩家相关的操作记录，用于生成提示词"""
        if not self.current_round_actions:
            return "本轮尚未有操作记录。"
        
        actions = self.current_round_actions if include_latest else self.current_round_actions[:-1]
        action_descriptions = []
        
        for action in actions:
            if action["type"] == "play":
                if action["player"] == player_name:
                    action_descriptions.append(f"你打出了 {', '.join(action['played_cards'])}")
                else:
                    action_descriptions.append(f"{action['player']} 打出了 {', '.join(action['played_cards'])}")
            elif action["type"] == "challenge":
                if action["was_challenged"]:
                    if action["result"] is not None:
                        result_text = "成功" if action["result"] else "失败"
                        action_descriptions.append(f"质疑{result_text}")
                    else:
                        action_descriptions.append("质疑")
                else:
                    action_descriptions.append("未质疑")
            elif action["type"] == "shooting":
                result_text = "命中" if action["bullet_hit"] else "未命中"
                action_descriptions.append(f"{action['shooter']} 开枪，{result_text}")
        
        return " | ".join(action_descriptions) if action_descriptions else "本轮尚未有操作记录。"

    def get_play_decision_info(self, player_name: str, next_player_name: str) -> str:
        """获取出牌决策所需的信息，用于生成提示词"""
        # 获取当前玩家对下一位玩家的印象
        if self.current_round and player_name in self.current_round.get("player_opinions", {}) and \
           next_player_name in self.current_round["player_opinions"][player_name]:
            opinion = self.current_round["player_opinions"][player_name][next_player_name]
        else:
            opinion = "还不了解这个玩家"
        
        # 获取当前玩家的初始状态
        player_state = None
        for state in self.current_round.get("player_initial_states", []):
            if state["player_name"] == player_name:
                player_state = state
                break
        
        if not player_state:
            return ""
        
        info = f"你对 {next_player_name} 的印象：{opinion}\n"
        info += f"你的初始手牌：{', '.join(player_state['initial_hand'])}\n"
        info += f"你的子弹位置：{player_state['bullet_position']}\n"
        info += f"当前弹舱位置：{player_state['current_gun_position']}\n"
        
        return info

    def get_challenge_decision_info(self, player_name: str, target_player_name: str) -> str:
        """获取质疑决策所需的信息，用于生成提示词"""
        # 获取当前玩家对目标玩家的印象
        if self.current_round and player_name in self.current_round.get("player_opinions", {}) and \
           target_player_name in self.current_round["player_opinions"][player_name]:
            opinion = self.current_round["player_opinions"][player_name][target_player_name]
        else:
            opinion = "还不了解这个玩家"
        
        info = f"你对 {target_player_name} 的印象：{opinion}\n"
        
        # 获取当前玩家的初始状态
        player_state = None
        for state in self.current_round.get("player_initial_states", []):
            if state["player_name"] == player_name:
                player_state = state
                break
        
        if player_state:
            info += f"你的子弹位置：{player_state['bullet_position']}\n"
            info += f"当前弹舱位置：{player_state['current_gun_position']}\n"
        
        return info

    def get_latest_play_behavior(self) -> str:
        """获取最近一次出牌的行为描述"""
        for action in reversed(self.current_round_actions):
            if action["type"] == "play":
                return action["behavior"]
        return ""

    def get_latest_round_result(self, player_name: str) -> str:
        """获取当前轮次的结果信息，用于生成提示词"""
        if not self.current_round_actions:
            return "本轮尚未有结果。"
        
        # 寻找射击结果
        for action in reversed(self.current_round_actions):
            if action["type"] == "shooting":
                result = "命中" if action["bullet_hit"] else "未命中"
                return f"射击结果：{action['shooter']} 开枪，{result}"
        
        # 寻找质疑结果
        for action in reversed(self.current_round_actions):
            if action["type"] == "challenge" and action["was_challenged"]:
                result = "成功" if action["result"] else "失败"
                return f"质疑结果：{result}"
        
        return "本轮尚未有结果。"