# Contributing to liketypeless

感谢参与 liketypeless。项目目前以 Windows 本地优先体验为主，优先级是：

1. 可用性和输入体验。
2. 本地隐私。
3. 稳定性和可诊断性。
4. 速度。
5. 跨机器安装和打包。

## 开始之前

请先阅读：

- `README.md`
- `docs/decisions/`

如果修改的是核心架构、模型、快捷键或输入流程，请先提交一个简短的设计讨论或更新决策记录，再开始实现。

## 本地开发

```powershell
npm install
.\.venv\Scripts\python.exe -m pip install -r apps/local-api/requirements.txt
npm run check
npm run check:api
npm run dev
```

## 分支和提交

推荐使用以下分支命名：

```text
feature/<short-name>
fix/<short-name>
docs/<short-name>
```

提交信息保持简洁，说明实际变化：

```text
feat: add global voice input hotkey
fix: preserve clipboard after auto paste
docs: update model setup guide
```

## Pull Request

Pull Request 至少说明：

- 修改解决了什么问题。
- 采用了什么技术方案。
- 是否改变模型、快捷键、权限或安装步骤。
- 如何验证。
- 已知限制。

提交前运行：

```powershell
npm run check
npm run check:api
```

如果修改了录音、ASR、自动粘贴或桌面行为，还应手动测试：

- 普通记事本输入框。
- 浏览器输入框。
- 中文输入法。
- 原剪贴板内容是否恢复。
- 快捷键冲突时的行为。

## 不要提交的内容

以下内容不应提交到 Git：

- `.venv/`
- `.venv-asr-py312/`
- `node_modules/`
- `apps/local-api/data/`
- 本地录音文件。
- 本地模型文件。
- `.env` 和 API 密钥。
- 日志和构建输出。
- 包含私人信息的测试文本。

## Issue

Bug 报告请包含：

- Windows 版本。
- Python、Node.js、Ollama 版本。
- GPU 型号和驱动情况。
- 使用的 ASR 模型。
- 是否使用代理。
- 复现步骤。
- 相关日志中的错误信息。

请不要直接上传录音文件；如果需要分析音频问题，先确认其中不包含隐私内容。
