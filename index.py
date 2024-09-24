# -*- coding: utf-8 -*-
import os
from flask import Flask, request, jsonify, Response
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import json
import time

## 加载环境变量
_ = load_dotenv(find_dotenv())

# 配置 OpenAI 服务
client = OpenAI()

# 初始化Flask应用
app = Flask(__name__)

@app.route('/generate_answer', methods=['POST'])
def generate_answer():
    try:
        # 获取请求中的参数（可选）
        data = request.get_json()
        question = data.get('question') if data else None

        if not question:
            error_response = {
                'status': 'error',
                'message': 'lack "question" parameter'
            }
            return Response(json.dumps(error_response, ensure_ascii=False), mimetype='application/json', status=400)
    
        # 拼接提示词
        prompt_question = f"请用英文回答这个问题，不要用其他语言:{question} \n 注意：1. 请使用英文回答问题。2.问题的范围仅限于在澳大利亚北领地(NT)或Darwin的事物。如果问题不在这个范围内，请回答：Sorry, we didn't find the answer you were looking for.(请精确的返回这句话，不要返回其他多余的内容)"

        # 调用OpenAI API
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt_question,
                }
            ],
            model="gpt-4o-mini"
        )

        # 提取生成的内容
        if response.choices and len(response.choices) > 0:
            answer_content = response.choices[0].message.content
        else:
            raise ValueError("未收到生成的回答。")

        # 获取当前时间戳
        current_timestamp = int(time.time())

        # 准备返回的数据
        response_data = {
            'status': 'success',
            'answer': {
                'id': '',  # 这里可以替换为实际生成的ID
                'questionId': '',  # 这里可以替换为实际问题ID
                'content': answer_content,
                'authorId': response.model,  # 这里可以替换为实际作者ID
                'createAt': current_timestamp,
                'updateAt': current_timestamp,
                'upvotes': 0,
                'downvotes': 0,
                'question': question
            }
        }

        # 使用 json.dumps 并设置 ensure_ascii=False 以返回可读的中文字符
        response_json = json.dumps(response_data, ensure_ascii=False)

        # 返回JSON响应
        return Response(response_json, mimetype='application/json', status=200)

    except Exception as e:
        app.logger.error(f"Error: {e}")
        error_response = {
            'status': 'error',
            'message': str(e)
        }
        return Response(json.dumps(error_response, ensure_ascii=False), mimetype='application/json', status=500)

if __name__ == '__main__':
    # 运行Flask应用，监听所有公网IP的5555端口
    app.run(host='0.0.0.0', port=80)
