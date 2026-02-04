# AI Clipboard - 剪贴板智能纠错工具

一个 Windows 桌面小工具，自动监听剪贴板内容，提供 AI 文本纠错和 Snippaste 风格的图片浮窗功能。

## 功能特点

- **自动监听剪贴板**：后台无感记录文本和图片，智能去重
- **智能文本纠错**：错字、病句、标点符号自动修正，附带详细修改说明
- **多种润色风格**：正式商务、轻松口语、学术专业、简洁明了、创意生动
- **Snippaste 风格浮窗**：按 `Ctrl+Shift+V` 将复制的图片以浮窗形式显示在桌面上
  - 置顶显示
  - 拖动移动
  - 双击关闭
  - 拖拽边缘缩放
- **快速便捷**：一键复制纠错结果

## 截图

```
┌─────────────────────────────────────┐
│  剪贴板记录                          │
│  ┌──────────┬─────────────────────┐ │
│  │ 记录列表 │    预览区域          │ │
│  │          │                     │ │
│  ├──────────┤                     │ │
│  │ 记录 1   │                     │ │
│  │ 记录 2   │                     │ │
│  │ ...      │                     │ │
│  └──────────┴─────────────────────┘ │
│  [清空记录] [📷 显示浮窗]           │
└─────────────────────────────────────┘
```

## 安装

### 1. 克隆项目

```bash
git clone https://github.com/ruskin-pkucala/AIclipboard.git
cd AIclipboard
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 获取智谱 AI API Key

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册/登录账号
3. 在控制台获取 API Key

## 使用方法

### 启动程序

```bash
python main.py
```

或使用批处理文件：

```bash
启动.bat
```

### 首次运行

首次运行时，会提示输入智谱 AI API Key，程序会自动保存到 `~/.clipboard-polisher/config.json`。

### API Key 配置

工具会按以下顺序读取 API Key：

1. 本地配置文件 `~/.clipboard-polisher/config.json`
2. 环境变量 `ZHIPUAI_API_KEY`

**手动设置环境变量（可选）：**
```bash
# Windows PowerShell
$env:ZHIPUAI_API_KEY="your-api-key"

# Windows CMD
set ZHIPUAI_API_KEY=your-api-key
```

## 功能说明

### 1. 剪贴板监听

- 复制任何文本或图片，工具自动记录
- 智能去重：相同内容不会重复记录
- 最大记录数：50条（FIFO 自动清理）

### 2. 文本纠错

1. 双击任意文本记录
2. 选择纠错模式
3. 查看纠错结果和详细修改说明
4. 一键复制结果

### 3. 图片浮窗（Snippaste 风格）

1. 复制任意图片
2. 按 `Ctrl+Shift+V` 显示浮窗
3. 浮窗功能：
   - **拖动**：按住左键拖动
   - **缩放**：拖拽边缘或角落
   - **关闭**：双击左键

### 4. 系统托盘

- 双击托盘图标：打开主窗口
- 右键菜单：打开主窗口 / 退出

## 纠错模式

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| 纯纠错 | 修正错字、病句、标点 | 日常使用 |
| 正式商务 | 商务邮件、报告 | 工作场合 |
| 轻松口语 | 社交媒体、聊天 | 非正式交流 |
| 学术专业 | 论文、技术文档 | 学术写作 |
| 简洁明了 | 摘要、要点 | 快速传达 |
| 创意生动 | 营销文案、广告 | 创意表达 |

## 数据存储

- 配置：`~/.clipboard-polisher/config.json`
- 数据库：`~/.clipboard-polisher/records.db`（SQLite）
- 图片：`~/.clipboard-polisher/images/`
- 日志：`~/.clipboard-polisher/*.log`

## 打包成 exe

```bash
pip install pyinstaller
pyinstaller build.spec
```

生成的单文件 exe 在 `dist/剪贴板智能纠错工具.exe`，可独立运行无需 Python 环境。

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Shift+V` | 显示最后复制的图片浮窗 |

## 技术栈

- Python 3.8+
- PyQt5（GUI）
- Zhipu AI GLM-4-flash（AI 纠错）
- SQLite（数据存储）
- pywin32（剪贴板监听）
- keyboard（全局热键）

## 许可证

MIT License

## 致谢

- [智谱 AI](https://open.bigmodel.cn/) - AI 文本纠错 API
- [Snippaste](https://www.snipaste.com/) - 图片浮窗灵感来源
