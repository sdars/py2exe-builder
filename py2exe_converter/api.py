from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import json
import tempfile
from werkzeug.utils import secure_filename
from .core import PyToExeConverter


class PyToExeAPI:
    """Python转exe的API服务"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.converter = PyToExeConverter()
        self.setup_routes()
        
        # 文件上传配置
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
        self.app.config['UPLOAD_FOLDER'] = '/tmp/py2exe_uploads'
        
        # 创建上传目录
        os.makedirs(self.app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    def setup_routes(self):
        """设置API路由"""
        
        @self.app.route('/', methods=['GET'])
        def index():
            """主页面"""
            return render_template_string(WEB_CONSOLE_HTML)
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """健康检查"""
            return jsonify({'status': 'ok'})
        
        @self.app.route('/api/convert', methods=['POST'])
        def convert_file():
            """转换文件"""
            try:
                # 检查是否有文件
                if 'file' not in request.files:
                    return jsonify({
                        'success': False,
                        'error': 'No file provided'
                    }), 400
                
                file = request.files['file']
                if file.filename == '':
                    return jsonify({
                        'success': False,
                        'error': 'No file selected'
                    }), 400
                
                # 保存文件
                filename = secure_filename(file.filename)
                if not filename.endswith('.py'):
                    return jsonify({
                        'success': False,
                        'error': 'Only Python files are allowed'
                    }), 400
                
                file_path = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # 获取转换选项
                options = {}
                if request.form.get('noconsole') == 'true':
                    options['noconsole'] = True
                if request.form.get('onefile') == 'true':
                    options['onefile'] = True
                if request.form.get('name'):
                    options['name'] = request.form.get('name')
                if request.form.get('no_auto_deps') == 'true':
                    options['auto_install_deps'] = False
                
                # 处理图标文件
                if 'icon' in request.files and request.files['icon'].filename:
                    icon_file = request.files['icon']
                    icon_filename = secure_filename(icon_file.filename)
                    icon_path = os.path.join(self.app.config['UPLOAD_FOLDER'], icon_filename)
                    icon_file.save(icon_path)
                    options['icon'] = icon_path
                
                # 执行转换
                result = self.converter.convert(file_path, options)
                
                # 清理临时文件
                try:
                    os.remove(file_path)
                    if 'icon' in options:
                        os.remove(options['icon'])
                except:
                    pass
                
                return jsonify(result)
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/validate', methods=['POST'])
        def validate_file():
            """验证Python文件"""
            try:
                if 'file' not in request.files:
                    return jsonify({
                        'valid': False,
                        'error': 'No file provided'
                    }), 400
                
                file = request.files['file']
                if file.filename == '':
                    return jsonify({
                        'valid': False,
                        'error': 'No file selected'
                    }), 400
                
                # 保存临时文件
                filename = secure_filename(file.filename)
                file_path = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # 验证文件
                result = self.converter.validate_python_file(file_path)
                
                # 如果验证成功，获取依赖
                if result.get('valid'):
                    result['dependencies'] = self.converter.get_dependencies(file_path)
                
                # 清理临时文件
                try:
                    os.remove(file_path)
                except:
                    pass
                
                return jsonify(result)
                
            except Exception as e:
                return jsonify({
                    'valid': False,
                    'error': str(e)
                }), 500
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """运行API服务"""
        self.app.run(host=host, port=port, debug=debug)


# 网页控制台HTML模板
WEB_CONSOLE_HTML = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python转EXE转换器</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .header {
            background: #2c3e50;
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #2c3e50;
        }
        
        .file-input-wrapper {
            position: relative;
            display: inline-block;
            width: 100%;
        }
        
        .file-input {
            width: 100%;
            padding: 12px;
            border: 2px dashed #ddd;
            border-radius: 5px;
            background: #f8f9fa;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .file-input:hover {
            border-color: #667eea;
            background: #e3f2fd;
        }
        
        .options {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 25px 0;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
        }
        
        .checkbox-group input[type="checkbox"] {
            margin-right: 10px;
            transform: scale(1.2);
        }
        
        .input-field {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            transition: border-color 0.3s ease;
        }
        
        .input-field:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 5px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s ease;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .result {
            margin-top: 30px;
            padding: 20px;
            border-radius: 5px;
            display: none;
        }
        
        .result.success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        
        .result.error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .file-info {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
            display: none;
        }
        
        .dependencies {
            margin-top: 10px;
        }
        
        .dependency-tag {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            margin: 2px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Python转EXE转换器</h1>
            <p>轻松将您的Python脚本转换为可执行文件</p>
        </div>
        
        <div class="content">
            <form id="convertForm">
                <div class="form-group">
                    <label for="pythonFile">选择Python文件 (.py)</label>
                    <input type="file" id="pythonFile" name="file" accept=".py" class="file-input" required>
                    <div id="fileInfo" class="file-info"></div>
                </div>
                
                <div class="form-group">
                    <label for="iconFile">选择图标文件 (可选)</label>
                    <input type="file" id="iconFile" name="icon" accept=".ico,.png,.jpg,.jpeg" class="file-input">
                </div>
                
                <div class="form-group">
                    <label for="exeName">可执行文件名称 (可选)</label>
                    <input type="text" id="exeName" name="name" class="input-field" placeholder="留空使用Python文件名">
                </div>
                
                <div class="options">
                    <div class="checkbox-group">
                        <input type="checkbox" id="onefile" name="onefile" checked>
                        <label for="onefile">打包为单个文件</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="noconsole" name="noconsole" checked>
                        <label for="noconsole">无控制台窗口</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="auto_deps" name="auto_deps" checked>
                        <label for="auto_deps">自动安装依赖</label>
                    </div>
                </div>
                
                <button type="submit" class="btn" id="convertBtn">开始转换</button>
            </form>
            
            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p>正在转换中，请稍候...</p>
            </div>
            
            <div id="result" class="result"></div>
        </div>
    </div>

    <script>
        document.getElementById('pythonFile').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                validateFile(file);
            }
        });

        document.getElementById('convertForm').addEventListener('submit', function(e) {
            e.preventDefault();
            convertFile();
        });

        function validateFile(file) {
            const formData = new FormData();
            formData.append('file', file);
            
            fetch('/api/validate', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                const fileInfo = document.getElementById('fileInfo');
                if (data.valid) {
                    fileInfo.innerHTML = `
                        <h4>✅ 文件验证成功</h4>
                        <p>文件大小: ${(data.size / 1024).toFixed(2)} KB</p>
                        <div class="dependencies">
                            <strong>检测到的依赖:</strong><br>
                            ${data.dependencies.map(dep => `<span class="dependency-tag">${dep}</span>`).join('')}
                        </div>
                    `;
                    fileInfo.style.display = 'block';
                } else {
                    fileInfo.innerHTML = `<h4>❌ 文件验证失败</h4><p>${data.error}</p>`;
                    fileInfo.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('验证失败:', error);
            });
        }

        function convertFile() {
            const form = document.getElementById('convertForm');
            const formData = new FormData(form);
            
            // 添加复选框值
            formData.append('onefile', document.getElementById('onefile').checked);
            formData.append('noconsole', document.getElementById('noconsole').checked);
            formData.append('no_auto_deps', !document.getElementById('auto_deps').checked);
            
            // 显示加载状态
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            document.getElementById('convertBtn').disabled = true;
            
            fetch('/api/convert', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('convertBtn').disabled = false;
                
                const result = document.getElementById('result');
                if (data.success) {
                    result.className = 'result success';
                    result.innerHTML = `
                        <h3>🎉 转换成功!</h3>
                        <p>EXE文件已生成: ${data.exe_path}</p>
                        <details>
                            <summary>详细输出</summary>
                            <pre>${data.stdout}</pre>
                        </details>
                    `;
                } else {
                    result.className = 'result error';
                    result.innerHTML = `
                        <h3>❌ 转换失败</h3>
                        <p>错误信息: ${data.error}</p>
                        ${data.stderr ? `<details><summary>错误详情</summary><pre>${data.stderr}</pre></details>` : ''}
                    `;
                }
                result.style.display = 'block';
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('convertBtn').disabled = false;
                
                const result = document.getElementById('result');
                result.className = 'result error';
                result.innerHTML = `<h3>❌ 网络错误</h3><p>${error.message}</p>`;
                result.style.display = 'block';
            });
        }
    </script>
</body>
</html>
'''