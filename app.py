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
        response = client.chat.completions.create(
            model="deepseek-chat",  # 修改为 Deepseek 的模型名
            messages=[
                {"role": "system", "content": "你是一位深谙小红书运营之道的博主，擅长创作爆款笔记。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Deepseek API Error: {str(e)}")  # 修改错误日志提示
        return str(e)

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    # 打印环境变量值（注意：不要在生产环境中暴露完整的 API key）
    api_key = os.getenv("DEEPSEEK_API_KEY")
    print(f"API Key exists: {bool(api_key)}")

    data = request.json
    theme = data.get('theme')
    if not theme:
        return jsonify({"error": "请提供主题"}), 400

    note = generate_note(theme)
    return jsonify({"note": note})

if __name__ == '__main__':
    app.run(debug=True)
