import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib3
import os
import sys
import subprocess
import re

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_chrome_version():
    try:
        # 尝试从注册表获取Chrome版本
        result = subprocess.run(
            'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version',
            capture_output=True,
            text=True
        )
        version = re.search(r"[\d.]+", result.stdout)
        if version:
            return version.group(0)
    except:
        pass
    
    # 如果从注册表获取失败，尝试从Chrome可执行文件获取版本
    try:
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if not os.path.exists(chrome_path):
            chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        
        result = subprocess.run([chrome_path, "--version"], capture_output=True, text=True)
        version = re.search(r"[\d.]+", result.stdout)
        if version:
            return version.group(0)
    except:
        pass
    
    return None

def setup_driver():
    try:
        print("正在设置 Chrome 浏览器...")
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # SSL 相关设置
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--allow-insecure-localhost')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--reduce-security-for-testing')
        
        # 代理设置（如果需要）
        chrome_options.add_argument('--proxy-server="direct://"')
        chrome_options.add_argument('--proxy-bypass-list=*')
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # 禁用日志
        
        # 获取Chrome版本
        chrome_version = get_chrome_version()
        if not chrome_version:
            raise Exception("无法获取Chrome版本信息")
            
        print(f"检测到Chrome版本: {chrome_version}")
        
        # 使用本地的ChromeDriver
        driver_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromedriver")
        if not os.path.exists(driver_dir):
            os.makedirs(driver_dir)
        
        driver_path = os.path.join(driver_dir, "chromedriver.exe")
        if not os.path.exists(driver_path):
            print("请下载对应版本的ChromeDriver并放置在以下位置：")
            print(driver_path)
            print(f"\n下载地址：https://googlechromelabs.github.io/chrome-for-testing/")
            print("请确保下载的ChromeDriver版本与Chrome版本匹配")
            raise Exception("未找到ChromeDriver")
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 设置页面加载超时
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)
        
        # 设置自定义请求头
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        return driver
    except Exception as e:
        print(f"设置 Chrome 浏览器时出错：{str(e)}")
        if "chromedriver" in str(e).lower():
            print("\n请按照以下步骤操作：")
            print("1. 访问 https://googlechromelabs.github.io/chrome-for-testing/")
            print("2. 下载与您的Chrome版本匹配的ChromeDriver")
            print(f"3. 将chromedriver.exe放在此目录下：{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chromedriver')}")
        raise

# 函数：测试 Readwise API Key
def test_api_key(api_key):
    print(f"当前使用的 API Key: {api_key[:8]}...{api_key[-4:]}")  # 只显示开头和结尾，保护隐私
    
    # 使用 save endpoint 来测试 API key
    url = "https://readwise.io/api/v3/save/"
    headers = {
        'Authorization': f"Token {api_key}",
        'Content-Type': 'application/json'
    }
    test_data = {
        'url': 'https://example.com/test/',
        'tags': ['test']
    }
    
    try:
        print("正在测试 API 连接...")
        response = requests.post(url, headers=headers, json=test_data)
        if response.status_code == 401:
            print("API Key 无效，请检查是否正确设置了环境变量 READWISE_API_KEY")
            print("可以在 Readwise 网站上找到你的 API key: https://readwise.io/access_token")
            return False
        elif response.status_code == 400:
            # 400 错误通常意味着请求格式正确但内容有问题，说明 API key 是有效的
            return True
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"验证 API Key 时出错：{str(e)}")
        if hasattr(e, 'response') and e.response is not None and e.response.status_code == 401:
            print("API Key 无效，请检查是否正确设置了环境变量 READWISE_API_KEY")
            print("可以在 Readwise 网站上找到你的 API key: https://readwise.io/access_token")
        return False

# 函数：解析微信公众号文章
def parse_wechat_article(url):
    driver = None
    try:
        driver = setup_driver()
        print("正在打开文章链接...")
        
        # 添加重试机制
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                driver.get(url)
                break
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    raise
                print(f"连接失败，正在重试 ({retry_count}/{max_retries})...")
                time.sleep(2)
        
        # 等待文章内容加载
        print("等待页面加载...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "rich_media_content"))
        )
        time.sleep(2)  # 额外等待以确保内容完全加载
        
        # 获取页面内容
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # 提取标题和内容
        title = soup.find('h1', {'class': 'rich_media_title'})
        if not title:
            raise Exception("无法找到文章标题")
        title = title.get_text().strip()
        
        content_elem = soup.find('div', {'class': 'rich_media_content'})
        if not content_elem:
            raise Exception("无法找到文章内容")
        
        # 保存原始HTML和纯文本内容
        content_html = str(content_elem)
        content = content_elem.get_text().strip()
        
        # 提取图片
        images = []
        img_elements = soup.find_all('img', {'data-src': True})
        for img in img_elements:
            if 'data-src' in img.attrs:
                images.append(img['data-src'])
        
        return {
            'title': title,
            'content': content,
            'html': content_html,
            'images': images,
            'url': url
        }
    except Exception as e:
        print(f"解析文章时出错：{str(e)}")
        raise
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

# 函数：保存文章到 Reader
def save_to_reader(article_content, api_key):
    if not api_key or api_key == "YOUR_API_KEY":
        raise Exception("请设置有效的 Readwise API Key")
    
    # 首先测试 API Key
    if not test_api_key(api_key):
        raise Exception("API Key 验证失败")
        
    url = "https://readwise.io/api/v3/save/"
    headers = {
        'Authorization': f"Token {api_key}",
        'Content-Type': 'application/json'
    }
    data = {
        'url': article_content['url'],  # 必需字段
        'title': article_content['title'],
        'text': article_content['content'],  # 使用text而不是content
        'html': article_content.get('html', ''),
        'should_clean_html': True,
        'tags': ['wechat'],
        'images': article_content['images']
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print("文章已成功保存到 Reader！")
        print(f"标题：{article_content['title']}")
        print(f"内容长度：{len(article_content['content'])} 字符")
        print(f"图片数量：{len(article_content['images'])}")
    except requests.exceptions.RequestException as e:
        print(f"保存到 Reader 失败：{str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"请求数据格式错误：{e.response.text}")
        raise

# 主程序
def main():
    try:
        # 检查是否安装了 Chrome
        if sys.platform == 'win32':
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            if not os.path.exists(chrome_path):
                chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                if not os.path.exists(chrome_path):
                    raise Exception("未找到 Google Chrome，请先安装 Chrome 浏览器")
        
        # 获取 API key
        api_key = os.getenv('READWISE_API_KEY')
        if not api_key:
            raise Exception(
                "未找到 Readwise API Key。请按以下步骤设置：\n"
                "1. 访问 https://readwise.io/access_token 获取你的 API key\n"
                "2. 在终端中运行：$env:READWISE_API_KEY = '你的API_KEY'"
            )
        
        # 询问用户输入公众号文章链接
        url = input("请输入微信公众号文章链接：")
        if not url.startswith("https://mp.weixin.qq.com/"):
            raise Exception("请输入有效的微信公众号文章链接")
        
        # 解析文章内容
        print("正在获取文章内容...")
        article_content = parse_wechat_article(url)
        print(f"成功获取文章：{article_content['title']}")
        
        # 保存到 Reader
        save_to_reader(article_content, api_key)
        
    except Exception as e:
        print(f"发生错误：{str(e)}")
        if "chromedriver" in str(e).lower() or "chrome" in str(e).lower():
            print("\n故障排除建议：")
            print("1. 确保已安装 Google Chrome 浏览器")
            print("2. 尝试重新运行程序")
            print("3. 如果问题持续，可以尝试手动下载 ChromeDriver")
        sys.exit(1)

if __name__ == "__main__":
    main()
