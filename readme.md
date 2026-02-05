# 🌌 EchoSoul | 影子伴侣 1.0

> **“你是谁，取决于你如何定义我。”**

EchoSoul 是一款基于 DeepSeek 大模型开发的治愈系 AI 交互应用。它通过深邃的“极光星河”界面与多重人格设定，为用户提供深夜里的情绪陪伴与理性引导。

## ✨ 核心特性
* **星河美学 UI**：动态流光背景，沉浸式交互体验。
* **四大安慰风格**：支持“温暖陪伴”、“犀利点拨”、“温和鼓励”及“理性分析”一键切换。
* **状态深度定制**：用户可自定义当前心境，获得精准的情绪反馈。
* **隐私安全**：基于 Streamlit Secrets 机制，严格保护 API 密钥安全。

## 🛠️ 技术栈
* **Core**: Python + Streamlit
* **LLM**: DeepSeek-Chat API
* **UI/UX**: CSS Injection (Custom Aurora Theme)

## 🚀 快速开始
1. 克隆本项目。
2. 在本地创建 `.streamlit/secrets.toml` 并填入你的 `DEEPSEEK_API_KEY`。
3. 运行 `streamlit run app.py`。