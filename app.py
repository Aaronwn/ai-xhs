import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)

# 设置OpenAI API密钥
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_note(theme):
    """生成小红书风格的笔记"""
    prompt = f"""请以小红书博主的风格，围绕主题"{theme}"创作一篇爆款笔记。要求：
    1. 标题吸引人，带有emoji表情
    2. 内容真实有用，语气亲和
    3. 分点描述，重点突出
    4. 结尾互动引导
    5. 适当使用emoji表情
    6. 添加3-5个相关话题标签
    
    格式示例：
    标题
    ---
    正文内容
    ---
    话题标签
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一位深谙小红书运营之道的博主，擅长创作爆款笔记。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return str(e)

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    theme = data.get('theme')
    if not theme:
        return jsonify({"error": "请提供主题"}), 400
    
    note = generate_note(theme)
    return jsonify({"note": note})

if __name__ == '__main__':
    app.run(debug=True)
