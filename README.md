<p align="center">
  <img src="images/logo.png" alt="Wechat2Reader Logo" width="200">
</p>

# Wechat2Reader

中文 | [English](README_EN.md)

将微信公众号文章导入到 Reader 或 Readwise

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
git clone https://github.com/Penn-Lam/Wechat2Reader.git
cd Wechat2Reader
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 安装 ChromeDriver：
   - Windows:
     1. 创建 chromedriver 文件夹：
     ```powershell
     mkdir chromedriver
     ```
     2. 获取 Chrome 版本号：
     ```powershell
     (Get-Item (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe').'(Default)').VersionInfo.FileVersion
     ```
     3. 下载对应版本的 ChromeDriver（将命令中的 VERSION 替换为上一步获取的版本号）：
     ```powershell
     curl -L "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/VERSION/win64/chromedriver-win64.zip" -o chromedriver\chromedriver.zip
     ```
     4. 解压并移动文件：
     ```powershell
     Expand-Archive -Path "chromedriver\chromedriver.zip" -DestinationPath "chromedriver" -Force
     Move-Item -Path "chromedriver\chromedriver-win64\chromedriver.exe" -Destination "chromedriver\chromedriver.exe" -Force
     ```

   - macOS:
     1. 创建 chromedriver 文件夹：
     ```bash
     mkdir chromedriver
     ```
     2. 获取 Chrome 版本号：
     ```bash
     /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version | awk '{print $3}'
     ```
     3. 下载对应版本的 ChromeDriver（将命令中的 VERSION 替换为上一步获取的版本号）：
     ```bash
     curl -L "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/VERSION/mac-x64/chromedriver-mac-x64.zip" -o chromedriver/chromedriver.zip
     ```
     4. 解压并移动文件：
     ```bash
     unzip chromedriver/chromedriver.zip -d chromedriver/
     mv chromedriver/chromedriver-mac-x64/chromedriver chromedriver/
     chmod +x chromedriver/chromedriver
     ```

   - Linux:
     1. 创建 chromedriver 文件夹：
     ```bash
     mkdir chromedriver
     ```
     2. 获取 Chrome 版本号：
     ```bash
     google-chrome --version | awk '{print $3}'
     ```
     3. 下载对应版本的 ChromeDriver（将命令中的 VERSION 替换为上一步获取的版本号）：
     ```bash
     curl -L "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/VERSION/linux64/chromedriver-linux64.zip" -o chromedriver/chromedriver.zip
     ```
     4. 解压并移动文件：
     ```bash
     unzip chromedriver/chromedriver.zip -d chromedriver/
     mv chromedriver/chromedriver-linux64/chromedriver chromedriver/
     chmod +x chromedriver/chromedriver
     ```

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

3. 导入完成后，删除测试所用的 example 文章

## 常见问题

1. **Chrome 浏览器未安装**
   - 请安装最新版本的 Google Chrome 浏览器

2. **ChromeDriver 问题**
   - 如果看到 ChromeDriver 相关错误，请尝试：
     1. 确保 Chrome 浏览器为最新版本
     2. 如果在中国大陆使用，可能需要科学上网
     3. 如果以上方法都不行，再尝试手动下载安装

3. **API 密钥错误**
   - 确保已正确配置 `config.ini`
   - 检查 API 密钥是否有效

4. **文章无法导入**
   - 确保文章链接来自微信公众号
   - 确保文章可以正常访问（非付费文章）

## 贡献指南

欢迎提交 Pull Requests 和 Issues！

## License

本项目采用 MIT License - 详见 [LICENSE](LICENSE.txt) 文件
