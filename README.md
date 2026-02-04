# 剪贴板智能纠错工具

一个 Windows 桌面小工具，自动记录剪贴板内容，并调用**智谱 GLM-4.7**进行智能文本纠错和润色。

## 功能特点

- **自动监听剪贴板**：后台无感记录文本和图片
- **智能文本纠错**：错字、病句、标点符号自动修正
- **多种润色风格**：正式商务、轻松口语、学术专业、简洁明了、创意生动
- **图片 OCR**：支持从提取图片中的文字进行纠错
- **快速便捷**：一键复制纠错结果

## 安装

### 1. 克隆项目

```bash
git clone <repository-url>
cd clipboard-polisher
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 安装 Tesseract OCR（图片文字识别，可选）

下载并安装：https://github.com/UB-Mannheim/tesseract/wiki

## 使用方法

### 直接运行

```bash
python main.py
```

### 首次运行

首次运行时，如果未检测到 API Key，会提示输入：
- 输入你的智谱 AI API Key
- 程序会自动保存到 `~/.clipboard-polisher/config.json`

### 获取智谱 AI API Key

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册/登录账号
3. 在控制台获取 API Key

### API Key 配置方式

工具会按以下顺序读取 API Key：

1. 本地配置文件 `~/.clipboard-polisher/config.json`（首次运行后自动保存）
2. 环境变量 `ZHIPUAI_API_KEY`

**设置环境变量（可选）：**
```bash
# Windows PowerShell
$env:ZHIPUAI_API_KEY="your-api-key"

# Windows CMD
set ZHIPUAI_API_KEY=your-api-key
```

## 使用说明

1. **自动记录**：复制任何文本或图片，工具会自动记录
2. **查看记录**：打开主窗口查看所有历史记录
3. **文本纠错**：双击任意记录，打开纠错窗口
4. **选择模式**：选择纠错模式（纯纠错/各种风格润色）
5. **复制结果**：一键复制纠错后的文本

## 纠错模式

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| 纯纠错 | 修正错字、病句、标点 | 日常使用 |
| 正式商务 | 商务邮件、报告 | 工作场合 |
| 轻松口语 | 社交媒体、聊天 | 非正式交流 |
| 学术专业 | 论文、技术文档 | 学术写作 |
| 简洁明了 | 摘要、要点 | 快速传达 |
| 创意生动 | 营销文案、广告 | 创意表达 |

## 配置说明

配置文件位置：`~/.clipboard-polisher/config.json`

```json
{
  "api_key": "7497c5ae5c6c493eba36c24aa1e50a38.xxx..."
}
```

## 数据存储

- 数据库：`~/.clipboard-polisher/records.db`（SQLite）
- 图片：`~/.clipboard-polisher/images/`
- 最大记录数：50条（FIFO 自动清理）

## 系统托盘

程序最小化到系统托盘：
- 双击托盘图标：打开主窗口
- 右键菜单：打开主窗口 / 退出

## 打包成 exe

```bash
pip install pyinstaller
pyinstaller build.spec
```

生成的单文件 exe 在 `dist/` 目录，可独立运行无需 Python 环境。

## 常见问题

**Q: 提示 "未找到智谱 AI API Key"？**
A: 首次运行会提示输入，或手动设置环境变量 `ZHIPUAI_API_KEY`。

**Q: 纠错速度慢？**
A: 取决于网络和 API 响应速度，建议使用稳定的网络环境。

**Q: 支持哪些图片格式？**
A: PNG, JPG, BMP, GIF 等常见格式。

**Q: 如何更换 API Key？**
A: 编辑 `~/.clipboard-polisher/config.json` 文件，或删除后重新运行程序。

## 技术栈

- Python 3.8+
- PyQt5（GUI）
- 智谱 GLM-4.7（AI 纠错）
- SQLite（数据存储）
- pywin32（剪贴板监听）

## 许可证

MIT License
