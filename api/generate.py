from http.client import HTTPSConnection
import json
import os
from urllib.parse import urlencode

def create_chat_completion(api_key, messages, model="deepseek-chat", temperature=0.8, max_tokens=1000):
    conn = HTTPSConnection("api.deepseek.com")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    conn.request("POST", "/v1/chat/completions", body=json.dumps(data), headers=headers)
    response = conn.getresponse()
    result = json.loads(response.read().decode())

    if "error" in result:
        raise Exception(result["error"]["message"])

    return result["choices"][0]["message"]["content"]

def generate_prompt(theme):
    return f"""你是一位深谙小红书爆款笔记创作的资深博主。请根据用户输入的主题"{theme}"，生成一篇吸引人的小红书笔记。

- 基于用户输入的主题，生成��吸引眼球的标题
- 标题字数控制在20字符以内(包含emoji)
- 标题需包含1-2个emoji，放在标题开头或结尾
- 标题要有爆点，制造好奇心
- 可以用"？""！"等标点增强表现力

- 开头要吸引眼球，用简短有力的文案hook住读者
- 必须分3个要点展开，每个要点需要：
 * 每个要点使用"🔍|💡|✨|📌|💫"作为开头
  * 要点标题需要加粗
  * 要点内容简明扼要
  * 要点之间空一行分隔
  * 无需添加"要点一"等序号标识
  * 要点标题与内容紧接排列
  * 要点内多条内容需添加序号emoji
- 文风要求：
  * 亲和力强的对话式表达，像在跟好朋友分享
  * 口语化表达，自然不做作
  * 适度使用"绝绝子""yyds""无语子"等小红书流行用语
  * 传递真诚和专业感
- 结尾加上3个相关话题标签，用#号开头"""

def handle(request):
    if request.method == "OPTIONS":
        return {
            "status": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        }

    if request.method != "POST":
        return {
            "status": 405,
            "body": json.dumps({"error": "Method not allowed"}),
            "headers": {"Content-Type": "application/json"},
        }

    try:
        body = json.loads(request.body)
        theme = body.get("theme")

        if not theme:
            return {
                "status": 400,
                "body": json.dumps({"error": "请提供主题"}),
                "headers": {"Content-Type": "application/json"},
            }

        messages = [
            {"role": "system", "content": "你是一位深谙小红书运营之道的博主，擅长创作爆款笔记。你的文章结构清晰，重点突出，并善于使用emoji增加文章趣味性。"},
            {"role": "user", "content": generate_prompt(theme)}
        ]

        note = create_chat_completion(
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
            messages=messages
        )

        return {
            "status": 200,
            "body": json.dumps({"note": note}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        }

    except Exception as e:
        return {
            "status": 500,
            "body": json.dumps({"error": f"生成失败: {str(e)}"}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        }