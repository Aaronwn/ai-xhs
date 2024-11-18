import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)

# 初始化 OpenAI 客户端，使用 Deepseek API
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def generate_note(theme):
    """生成小红书风格的笔记"""
    prompt = f"""你是一位深谙小红书爆款笔记创作的资深博主。请根据用户输入的主题"{theme}"，生成一篇吸引人的小红书笔记。

- 基于用户输入的主题，生成更吸引眼球的标题
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
- 结尾加上3个相关话题标签，用#号开头

整体要求：
- 正文字数控制在300字以内
- 内容要有价值和可操作性
- 避免过度营销感和虚假信息
- 适量使用标点符号增强表达力（❗️、❓、～）
- 注意性别中立的表达方式，内容要适合所有用户群体"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位深谙小红书运营之道的博主，擅长创作爆款笔记。你的文章结构清晰，重点突出，并善于使用emoji增加文章趣味性。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1000,
            timeout=25
        )
        return response.choices[0].message.content
    except Exception as e:
        error_message = str(e)
        print(f"Deepseek API Error: {error_message}")
        if "timeout" in error_message.lower():
            return {"error": "请求超时，请稍后重试"}
        return {"error": f"生成失败: {error_message}"}

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        theme = data.get('theme')
        if not theme:
            return jsonify({"error": "请提供主题"}), 400

        note = generate_note(theme)

        if isinstance(note, dict) and "error" in note:
            return jsonify(note), 500

        return jsonify({"note": note})
    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
