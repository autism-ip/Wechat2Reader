# Copyright (c) 2024 Wechat2Reader
# Licensed under the MIT License - see LICENSE file for details

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
import json
import configparser
from pathlib import Path

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
        
        # 提取作者
        author = None
        author_elem = soup.find('a', {'class': 'wx_tap_link js_wx_tap_highlight weui-wa-hotarea'})
        if author_elem:
            author = author_elem.get_text().strip()
        else:
            # 尝试其他可能的作者元素
            possible_author_selectors = [
                'span[data-author]',
                'a#js_name',
                'div#js_profile_qrcode > div > strong',
                'div#meta_content > span:first-child'
            ]
            for selector in possible_author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    author = author_elem.get_text().strip()
                    break
        
        if not author:
            author = "微信公众号"  # 默认作者
        
        content_elem = soup.find('div', {'class': 'rich_media_content'})
        if not content_elem:
            raise Exception("无法找到文章内容")
        
        # 保存原始HTML和纯文本内容
        content_html = str(content_elem)
        content = content_elem.get_text().strip()
        
        # 提取封面图片
        cover_image = None
        try:
            # 查找所有可能包含封面图片的script标签
            scripts = driver.find_elements(By.TAG_NAME, "script")
            for script in scripts:
                script_text = script.get_attribute('innerHTML')
                if not script_text:
                    continue
                
                # 尝试不同的变量名
                for var_name in ['msg_cdn_url', 'cdn_url', 'msg_link', 'cdn_url_235']:
                    if f'var {var_name} = "' in script_text:
                        cover_image = script_text.split(f'var {var_name} = "')[1].split('"')[0]
                        if cover_image.startswith('//'):
                            cover_image = 'https:' + cover_image
                        break
                if cover_image:
                    break
                    
            if not cover_image:
                # 如果还是没找到，尝试从页面中查找其他可能的封面图片元素
                possible_cover_selectors = [
                    "meta[property='og:image']",
                    "img#js_cover",
                    "img.rich_media_thumb_thumb",
                    "img.rich_media_thumb"
                ]
                for selector in possible_cover_selectors:
                    try:
                        cover_elem = driver.find_element(By.CSS_SELECTOR, selector)
                        if selector.startswith("meta"):
                            cover_image = cover_elem.get_attribute('content')
                        else:
                            cover_image = cover_elem.get_attribute('data-src') or cover_elem.get_attribute('src')
                        if cover_image:
                            if cover_image.startswith('//'):
                                cover_image = 'https:' + cover_image
                            break
                    except:
                        continue
        except Exception as e:
            print(f"提取封面图片时出错：{str(e)}")
        
        if cover_image:
            print(f"找到封面图片：{cover_image}")
        
        # 提取文章中的图片
        images = []
        img_elements = content_elem.find_all('img', {'data-src': True})
        for img in img_elements:
            if 'data-src' in img.attrs:
                img_url = img['data-src']
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                images.append(img_url)
        
        return {
            'title': title,
            'content': content,
            'html': content_html,
            'images': images,
            'cover_image': cover_image,
            'url': url,
            'author': author
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
    
    # 准备图片列表，处理图片URL
    images = []
    cover_image = None
    
    # 微信图片请求的headers（不包含 Referer）
    wx_img_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }
    
    session = requests.Session()
    session.headers.update(wx_img_headers)
    
    # 处理封面图片
    if article_content.get('cover_image'):
        cover_url = article_content['cover_image']
        if cover_url.startswith('//'):
            cover_url = 'https:' + cover_url
        if 'mmbiz.qpic.cn' in cover_url:
            try:
                img_response = session.get(cover_url, verify=False)
                if img_response.status_code == 200:
                    cover_image = cover_url
            except:
                print(f"无法获取封面图片：{cover_url}")
        else:
            cover_image = cover_url
    
    # 处理文章中的图片
    for img_url in article_content['images']:
        if img_url.startswith('//'):
            img_url = 'https:' + img_url
        if 'mmbiz.qpic.cn' in img_url:
            try:
                img_response = session.get(img_url, verify=False)
                if img_response.status_code == 200:
                    images.append(img_url)
            except:
                print(f"无法获取图片：{img_url}")
        else:
            images.append(img_url)
    
    # 准备发送到 Reader 的数据
    data = {
        'url': article_content['url'],
        'html': article_content['html'],
        'should_clean_html': True,
        'title': article_content['title'],
        'author': article_content['author'],
        'image_url': cover_image,  # 封面图片
        'location': 'new',  # 新文章
        'category': 'article',  # 文章类型
        'saved_using': 'Wechat2Reader',  # 保存来源
        'tags': ['wechat']  # 标签列表
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print("成功保存到 Reader！")
        result = response.json()
        print(f"阅读链接：{result.get('url', '')}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"保存到 Reader 失败：{str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"请求数据格式错误：{e.response.text}")
        raise

# 函数：从配置文件获取 Readwise API key
def get_api_key():
    """从配置文件获取 Readwise API key"""
    config = configparser.ConfigParser()
    config_file = Path(__file__).parent / 'config.ini'
    template_file = Path(__file__).parent / 'config.template.ini'
    
    if not config_file.exists():
        if template_file.exists():
            raise Exception(
                "未找到配置文件。请按以下步骤设置：\n"
                "1. 复制 config.template.ini 为 config.ini\n"
                "2. 访问 https://readwise.io/access_token 获取你的 API key\n"
                "3. 在 config.ini 中填入你的 API key"
            )
        else:
            raise Exception("配置文件模板 config.template.ini 不存在")
    
    config.read(config_file, encoding='utf-8')
    try:
        api_key = config['Readwise']['api_key']
        if api_key == 'YOUR_API_KEY':
            raise Exception(
                "请在 config.ini 中设置有效的 Readwise API Key\n"
                "访问 https://readwise.io/access_token 获取你的 API key"
            )
        return api_key
    except KeyError:
        raise Exception("配置文件格式错误，请确保包含 [Readwise] 部分和 api_key 设置")

def process_article(url):
    """处理单个文章"""
    try:
        # 检查 Chrome 是否安装
        if sys.platform == 'win32':
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            if not os.path.exists(chrome_path):
                chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                if not os.path.exists(chrome_path):
                    raise Exception("未找到 Google Chrome，请先安装 Chrome 浏览器")
        
        # 获取 API key
        api_key = get_api_key()
        
        # 处理文章
        article_content = parse_wechat_article(url)
        save_to_reader(article_content, api_key)
        return True
        
    except Exception as e:
        print(f"发生错误：{str(e)}")
        raise

# 主程序
def main():
    try:
        url = input("请输入微信公众号文章链接：")
        process_article(url)
        
    except KeyboardInterrupt:
        print("\n程序已终止")
    except Exception as e:
        print(f"发生错误：{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
