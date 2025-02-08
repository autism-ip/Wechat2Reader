<p align="center">
  <img src="images/logo.png" alt="Wechat2Reader Logo" width="200">
</p>

# Wechat2Reader

[中文](README.md) | English

Import WeChat articles to Reader or Readwise.

## Features
- 📱 Support for WeChat Official Account articles
- 🔄 Import to Reader or Readwise

## Requirements

- Python 3.8+
- Google Chrome browser
- Windows/macOS/Linux

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Wechat2Reader.git
cd Wechat2Reader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install ChromeDriver:
   - Method 1: Using command line (Recommended)
   ```bash
   python -m webdriver_manager.chrome
   ```
   - Method 2: Automatic installation
     - Will download the appropriate ChromeDriver version on first run
   - Method 3: Manual download (if above methods fail)
     1. Check your Chrome browser version (Settings -> About Chrome)
     2. Visit https://chromedriver.chromium.org/downloads
     3. Download the matching ChromeDriver version
     4. Place chromedriver.exe (Windows) or chromedriver (Mac/Linux) in the project root

4. Configure API key:
   - Copy `config.template.ini` to `config.ini`
   - Get your API key from https://readwise.io/access_token
   - Fill in your API key in `config.ini`

## Usage

1. Start the server:
```bash
python app.py
```

2. In the web interface:
   - Select target platform (Reader or Readwise)
   - Paste the WeChat article URL
   - Click "Start Import"
   
3. After the import is complete, delete the example article used for testing.

## Troubleshooting

1. **Chrome browser not installed**
   - Please install the latest version of Google Chrome

2. **ChromeDriver issues**
   - If you encounter ChromeDriver errors, try:
     1. Install via command line: `python -m webdriver_manager.chrome`
     2. Ensure Chrome browser is up to date
     3. If in mainland China, you might need a VPN
     4. If all else fails, try manual installation

3. **API key errors**
   - Ensure `config.ini` is properly configured
   - Verify API key is valid

4. **Article import fails**
   - Ensure the URL is from a WeChat Official Account
   - Verify the article is accessible

## Contributing

Pull Requests and Issues are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details
