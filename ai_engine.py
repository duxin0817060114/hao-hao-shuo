import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")
MODEL_NAME = "deepseek-chat"

SYSTEM_PROMPT = """
你是「好好说」AI家校沟通助手的核心判断引擎。
你的核心任务是帮助家长理解老师的表达、识别沟通问题、判断合理的沟通策略，并生成极具生活画面感、大白话、像真人在微信群里聊天的回复。

【一、核心语气：必须像极了真实的中国家长群聊天】
1. **绝对大白话与口水话**：多用“哎呀”、“确实”、“得嘞”、“哈”、“啦”、“嘛”，就像坐在沙发上随手敲出来的字。
2. **严禁官腔与假大空**：坚决不用“收到您的反馈”、“督促其认真学习”、“谨遵教诲”这种机器人词汇。
3. **极强的场景画面感**：家长回复要带出家里的真实生活状态（如“这小子在家就皮得很”、“天天盯着他写作业血压都高”等）。

【二、输出格式】
只输出合法JSON，不要输出Markdown代码块或额外解释：
{
  "teacher_analysis": {
    "surface_meaning": "老师消息的整体表面意思",
    "message_categories": ["课堂表现", "学习反馈"],
    "issue_points": [
      {
        "topic": "问题主题",
        "teacher_feedback": "老师具体反馈的内容",
        "information_type": "行为描述或老师评价",
        "evidence": "老师原话中的依据",
        "unknowns": ["尚未确认的信息"]
      }
    ],
    "facts": ["老师原话明确描述的情况"],
    "teacher_evaluations": ["老师对孩子表现作出的评价"],
    "explicit_request": "老师明确提出的要求",
    "possible_intentions": ["可能的意图"],
    "unknowns": ["目前无法确认的信息"],
    "risk_level": "普通、关注或较高风险"
  },
  "communication_strategy": {
    "strategy": "cooperate、clarify、correct、disagree、protect或normal之一",
    "reason": "选择这一策略的依据",
    "suggestion": "给家长的具体沟通建议"
  },
  "replies": {
    "natural": "极其接地气、充满生活烟火气的自然回复",
    "rational": "温和好奇、探究学校细节的理性询问",
    "principled": "温和坚定、保护孩子自尊心的有原则表达"
  }
}
"""

OUTPUT_FORMAT = {"type": "json_object"}

def create_client():
    if not API_KEY:
        raise ValueError("没有读取到 API Key，请检查 .env 文件。")
    return OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com", timeout=60.0)

def build_user_message(teacher_message, parent_position="", context="", conversation_history=None):
    history = (conversation_history or [])[-12:]
    cleaned_history = []
    for item in history:
        if isinstance(item, dict) and item.get("role") in ["teacher", "parent"] and isinstance(item.get("content"), str):
            cleaned_history.append({"role": item["role"], "content": item["content"].strip()[:1000]})
    
    data = {
        "teacher_message": teacher_message.strip(),
        "parent_position": parent_position.strip(),
        "context": context.strip(),
        "conversation_history": cleaned_history
    }
    return json.dumps(data, ensure_ascii=False)

def validate_result(data):
    required_fields = ["teacher_analysis", "communication_strategy", "replies"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"模型返回数据缺少字段：{field}")
    return data

def analyze_message(teacher_message, parent_position="", context="", conversation_history=None, max_retries=2):
    if not teacher_message.strip():
        raise ValueError("老师消息不能为空。")
    
    client = create_client()
    user_message = build_user_message(teacher_message, parent_position, context, conversation_history)
    
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                response_format=OUTPUT_FORMAT,
                max_tokens=1800,
                stream=False
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("模型没有返回有效内容。")
            
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            data = json.loads(content)
            return validate_result(data)
        except (json.JSONDecodeError, ValueError) as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(1)
                continue
            raise ValueError(f"AI 返回的数据格式解析失败，请重试。详细错误: {str(e)}")
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(2)
                continue
            raise e

def get_friendly_error(error):
    message = str(error)
    if "402" in message:
        return "API 账户余额不足，请先充值。"
    if "401" in message:
        return "API Key 验证失败，请检查密钥配置。"
    if "429" in message:
        return "请求过于频繁，请稍后再试。"
    return f"AI 服务暂时无法使用：{message}"