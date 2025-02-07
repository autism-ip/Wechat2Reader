# Wechat2Reader

将微信公众号文章导入到 Reader 或 Readwise。

## 功能特点
- 📱 支持微信公众号文章
- 🔄 支持导入到 Reader 和 Readwise

## 系统要求

- Python 3.8+
- Google Chrome 浏览器
- Windows/macOS/Linux

## 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/Wechat2Reader.git
cd Wechat2Reader
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 安装 ChromeDriver：
   - 方法一：使用命令行安装（推荐）
   ```bash
   python -m webdriver_manager.chrome
   ```
   - 方法二：让程序自动安装
     - 首次运行时会自动下载对应版本的 ChromeDriver
   - 方法三：手动下载（如果上述方法都失败）
     1. 查看你的 Chrome 浏览器版本（设置 -> 关于 Chrome）
     2. 访问 https://chromedriver.chromium.org/downloads
     3. 下载对应版本的 ChromeDriver
     4. 将 chromedriver.exe（Windows）或 chromedriver（Mac/Linux）放在项目根目录

4. 配置 API 密钥：
   - 复制 `config.template.ini` 为 `config.ini`
   - 访问 https://readwise.io/access_token 获取你的 API key
   - 在 `config.ini` 中填入你的 API key

## 使用方法

1. 启动服务器：
```bash
python app.py
```

2. 在网页界面上：
   - 选择目标平台（Reader 或 Readwise）
   - 粘贴微信公众号文章链接
   - 点击"开始导入"

## 常见问题

1. **Chrome 浏览器未安装**
   - 请安装最新版本的 Google Chrome 浏览器

2. **ChromeDriver 问题**
   - 如果看到 ChromeDriver 相关错误，请尝试：
     1. 使用命令行安装：`python -m webdriver_manager.chrome`
     2. 确保 Chrome 浏览器为最新版本
     3. 如果在中国大陆使用，可能需要科学上网
     4. 如果以上方法都不行，再尝试手动下载安装

3. **API 密钥错误**
   - 确保已正确配置 `config.ini`
   - 检查 API 密钥是否有效

4. **文章无法导入**
   - 确保文章链接来自微信公众号
   - 确保文章可以正常访问

## 贡献指南

欢迎提交 Pull Requests 和 Issues！

## License

本项目采用 MIT License - 详见 [LICENSE](LICENSE.txt) 文件
