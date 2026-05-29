<p align="center">
  <h1 align="center">🎥 Code Capture Tool</h1>
  <p align="center"><b>看视频，代码自动到手，不用手敲</b></p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License MIT">
</p>

---

## 📖 目录

- [这是什么？](#这是什么)
- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [安装指南](#安装指南)
  - [1. 安装 Python](#1-安装-python)
  - [2. 安装 Tesseract OCR](#2-安装-tesseract-ocr)
  - [3. 获取 API Key](#3-获取-deepseek-api-key)
  - [4. 安装依赖](#4-安装-python-依赖包)
- [使用方法](#使用方法)
  - [一键运行](#一键运行)
  - [分步运行](#分步运行)
- [参数说明](#参数说明)
- [常见问题](#常见问题)
- [支持的语言](#支持的语言)
- [项目结构](#项目结构)
- [许可](#许可)
- [作者](#作者)

---

## 这是什么？

在看编程教学视频或参加在线会议时，讲师会在屏幕上写代码。这个工具可以自动截屏、OCR 识别、AI 整理，**最终输出干净完整的代码文件**。

```
屏幕画面 → 自动截屏 → OCR识别代码 → AI修复整理 → 可运行的代码文件
```

---

## 功能特性

- 🖥️ **自动窗口检测** — 无需手动框选，自动找到目标窗口
- 📸 **变化感知截图** — 画面内容变化时才截图，不重复、不遗漏
- 🔍 **OCR 代码识别** — 从截图中提取代码，自动过滤 UI 元素和菜单栏
- 🧠 **AI 代码修复** — 修复 OCR 识别错误（1/l 混淆、符号错误等），合并重复片段
- 📁 **智能文件分组** — 按类名/文件名自动分组，还原项目结构
- 🔌 **多 LLM 支持** — 兼容 DeepSeek、OpenAI 及任何 OpenAI 格式的 API

---

## 快速开始

> 以下以 Windows 为例。macOS / Linux 用户请参考对应系统的安装方式。

```bash
# 1. 安装依赖（仅需一次）
pip install -r requirements.txt

# 2. 运行（把 sk-xxx 换成你的 API Key）
python run.py -k sk-xxx

# 3. 视频结束时按 Ctrl+C，等待自动处理
# 4. 代码出现在 session_xxxx_final/ 目录中
```

---

## 安装指南

### 1. 安装 Python

| 系统 | 安装方式 |
|------|----------|
| **Windows** | [python.org](https://www.python.org/downloads/) 下载安装包，**务必勾选 "Add Python to PATH"** |
| **macOS** | `brew install python@3.11` 或从 [python.org](https://www.python.org/downloads/) 下载 |
| **Linux** | `sudo apt install python3.11` (Debian/Ubuntu) |

验证安装：

```bash
python --version
# 应输出：Python 3.11.x 或更高
```

### 2. 安装 Tesseract OCR

| 系统 | 安装方式 |
|------|----------|
| **Windows** | [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki) 下载 `tesseract-ocr-w64-setup-5.x.x.exe`，默认路径安装 |
| **macOS** | `brew install tesseract` |
| **Linux** | `sudo apt install tesseract-ocr` |

> 脚本会自动检测常见安装路径。如安装在其他位置，使用 `--tesseract` 参数手动指定。

### 3. 获取 DeepSeek API Key

1. 访问 [platform.deepseek.com](https://platform.deepseek.com/) 注册并登录
2. 进入 **API Keys** 页面，点击 **创建 API Key**
3. 复制生成的 Key（格式为 `sk-xxxxxxxx`），妥善保存

> 💰 费用极低，处理一场 2 小时视频通常不到 1 元人民币。

### 4. 安装 Python 依赖包

```bash
cd code-capture-tool
pip install -r requirements.txt
```

依赖说明：

| 包名 | 用途 |
|------|------|
| `opencv-python` | 图像截取与预处理 |
| `mss` | 高速屏幕截取 |
| `numpy` | 图像数据运算 |
| `pytesseract` | Tesseract OCR 的 Python 封装 |
| `openai` | LLM API 客户端（兼容 DeepSeek / OpenAI） |

---

## 使用方法

### 一键运行

```bash
python run.py -k 你的API_KEY
```

**运行流程：**

1. 脚本自动搜索目标窗口（腾讯会议/Zoom/Teams 等）
2. 每隔 5 秒检测一次画面，变化时自动截图
3. 你正常观看视频
4. **视频结束后，按 `Ctrl + C`** 停止截屏
5. 自动执行 OCR 识别 → AI 代码清理
6. 最终代码保存在 `session_YYYYMMDD_HHMM_final/` 目录中

### 分步运行

如果需要更精细的控制，可以逐步运行：

```bash
# 第一步：仅截屏（按 Ctrl+C 停止）
python step1_capture.py -o ./screenshots -i 3

# 第二步：OCR 识别（对已有截图）
python step2_ocr.py -i ./screenshots -o ./ocr_output

# 第三步：AI 清理（需要 API Key）
python step3_deepseek.py -i ./ocr_output -o ./final_code -k 你的API_KEY
```

### 使用其他 AI 模型

```bash
# OpenAI GPT-4o
python run.py -k sk-xxx --base-url https://api.openai.com/v1 --model gpt-4o

# 其他兼容 OpenAI 格式的 API
python run.py -k sk-xxx --base-url https://你的API地址 --model 模型名
```

---

## 参数说明

### `run.py`（推荐使用）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-k` | 必填 | — | API Key |
| `-w` | 可选 | `腾讯会议,会议室,Zoom,Teams,...` | 窗口标题匹配关键词（逗号分隔） |
| `-i` | 可选 | `5` | 画面检测间隔（秒），建议 3~10 |
| `--fullscreen` | 可选 | 关闭 | 截取整个主显示器 |
| `--tesseract` | 可选 | 自动检测 | 手动指定 tesseract 可执行文件路径 |
| `--base-url` | 可选 | `https://api.deepseek.com` | LLM API 地址 |
| `--model` | 可选 | `deepseek-chat` | 模型名称 |
| `-o` | 可选 | `session_<时间戳>` | 输出目录前缀 |

### `step1_capture.py`

| 参数 | 说明 |
|------|------|
| `-o` | 截图输出目录 |
| `-i` | 检测间隔（秒） |
| `-w` | 窗口标题关键词 |
| `--fullscreen` | 全屏模式 |

### `step2_ocr.py`

| 参数 | 说明 |
|------|------|
| `-i` | 输入目录（PNG 截图） |
| `-o` | 输出目录（OCR 文本） |
| `--tesseract` | tesseract 路径 |

### `step3_deepseek.py`

| 参数 | 说明 |
|------|------|
| `-i` | 输入目录（OCR 文本） |
| `-o` | 输出目录（最终代码） |
| `-k` | API Key |
| `--base-url` | API 地址 |
| `--model` | 模型名称 |

---

## 常见问题

<details>
<summary><b>找不到窗口怎么办？</b></summary>

使用 `-w` 参数指定窗口标题中的关键词：

```bash
python run.py -k sk-xxx -w "B站,YouTube"
```

或者使用全屏模式：

```bash
python run.py -k sk-xxx --fullscreen
```
</details>

<details>
<summary><b>OCR 识别效果不好？</b></summary>

- 提高视频清晰度（至少 720P）
- IDE 使用深色主题 + 亮色字体，对比度越高越好
- 让代码窗口尽量占满屏幕
- 适当降低检测间隔 `-i 3`，增加截图频率
</details>

<details>
<summary><b>报错 ModuleNotFoundError？</b></summary>

依赖未安装，执行：

```bash
pip install -r requirements.txt
```
</details>

<details>
<summary><b>报错 TesseractNotFoundError？</b></summary>

Tesseract 未安装或路径不正确。检查默认路径 `C:\Program Files\Tesseract-OCR\tesseract.exe` 是否存在，或手动指定：

```bash
python run.py -k sk-xxx --tesseract "你的Tesseract路径"
```
</details>

<details>
<summary><b>命令行中文乱码？</b></summary>

在运行脚本前，先执行：

```bash
chcp 65001
```
</details>

<details>
<summary><b>截图太多占空间？</b></summary>

一场 1-2 小时视频通常产生 100-300 张截图，约 50-150 MB。处理完成后可以删除截图目录。
</details>

---

## 支持的语言

经过测试，以下语言效果最好：

- Java、Python、C/C++、TypeScript、JavaScript、Go、Rust

其他英文编程语言理论上也能识别，只要 OCR 能分辨出代码符号，AI 就能处理。

---

## 项目结构

```
code-capture-tool/
├── README.md               ← 本文件
├── LICENSE                 ← 许可协议
├── requirements.txt        ← Python 依赖清单
├── run.py                  ← 一键运行（推荐入口）
├── step1_capture.py        ← 第一步：屏幕截取
├── step2_ocr.py            ← 第二步：OCR 识别
├── step3_deepseek.py       ← 第三步：AI 代码清理
└── .gitignore              ← Git 忽略规则
```

---

## 许可

本项目基于 MIT 协议开源。详见 [LICENSE](./LICENSE) 文件。

---

## 作者

**刘瀚文**

如有问题或建议，欢迎提 Issue。
