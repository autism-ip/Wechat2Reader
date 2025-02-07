from flask import Flask, render_template, request, jsonify
import wechat_to_reader
import wechat_to_readwise
import traceback

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        data = request.json
        url = data.get('url')
        target = data.get('target')
        
        if not url or not target:
            return jsonify({'error': '请提供URL和目标平台'}), 400
            
        if target == 'reader':
            result = wechat_to_reader.process_article(url)
            return jsonify({'message': '成功导入到Reader！'})
        elif target == 'readwise':
            result = wechat_to_readwise.process_article(url)
            return jsonify({'message': '成功导出入Readwise！'})
        else:
            return jsonify({'error': '不支持的目标平台'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
