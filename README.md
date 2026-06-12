# GitHub Hot Daily

低成本 GitHub 热点公众号素材生成工具。项目每天通过 GitHub REST API 抓取公开仓库数据，筛选 AI、LLM、Agent、MCP、RAG、Python、开发者工具、效率工具、自动化、前端、Web、安全、数据、开源模型、CLI 工具等方向的热点项目，并生成适合复制到 ChatGPT Plus 的素材包。

本项目不会调用 OpenAI API、Gemini API、Claude API、DeepSeek API 或任何付费 AI 生成接口。它只负责抓取、过滤、排序和整理素材，最终文章由你手动复制素材到 ChatGPT Plus 后生成。

本项目也不包含邮件发送功能，不模拟登录 ChatGPT。

## 功能

- 使用 GitHub REST API 抓取公开仓库。
- 支持 GitHub Actions 内置 `GITHUB_TOKEN` 认证。
- 过滤 fork、archived、disabled、低信息量、课程作业、个人简历、测试仓库、广告、破解盗版、色情赌博灰产等项目。
- 生成 10 到 20 个候选项目。
- 使用综合热度分排序，不只按总 star 排序。
- 保存最近 30 天 `history.json`，用于计算 `star_delta`。
- 输出 `daily_raw.md`、`projects.json`、`history.json`、`chatgpt_prompt.txt`。

## 本地运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
GITHUB_TOKEN=你的 GitHub Token python -m src.main
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:GITHUB_TOKEN="你的 GitHub Token"
python -m src.main
```

不设置 `GITHUB_TOKEN` 也可以运行，但 GitHub API 速率限制更低。

## GitHub Actions 自动运行

工作流文件位于 `.github/workflows/daily.yml`。

触发方式：

- `workflow_dispatch`：支持在 GitHub 页面手动运行。
- `schedule`：每天北京时间 20:00 自动运行。

当前 GitHub Actions 的 `schedule` 支持在 cron 条目下设置 IANA 时区，因此本项目使用：

```yaml
on:
  schedule:
    - cron: "0 20 * * *"
      timezone: "Asia/Shanghai"
  workflow_dispatch:
```

如果你的仓库所在 GitHub 环境不支持 `timezone` 字段，可以改成 UTC 备用写法。北京时间是 UTC+8，所以北京时间 20:00 等于 UTC 12:00：

```yaml
on:
  schedule:
    - cron: "0 12 * * *"
  workflow_dispatch:
```

工作流步骤：

- checkout 代码。
- setup-python。
- 安装 `requirements.txt`。
- 运行 `python -m src.main`。
- 上传 `output` 目录中的结果文件为 artifact。

工作流会通过环境变量把 `GITHUB_TOKEN` 传给程序：

```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 如何打开 Actions

1. 把项目推送到 GitHub 仓库。
2. 打开仓库页面。
3. 点击顶部的 `Actions` 标签。
4. 如果页面提示启用 Actions，点击启用。
5. 在左侧选择 `Daily GitHub Hot Projects` 工作流。

## 如何手动运行一次

1. 打开仓库的 `Actions` 页面。
2. 左侧选择 `Daily GitHub Hot Projects`。
3. 点击右侧 `Run workflow`。
4. 选择默认分支。
5. 再次点击绿色的 `Run workflow` 按钮。
6. 等待运行完成，状态变成绿色对勾。

## 如何下载 artifact

1. 进入刚刚完成的 workflow run。
2. 在页面底部找到 `Artifacts` 区域。
3. 下载 `github-hot-daily-output-<run_id>`。
4. 解压后可以看到：
   - `daily_raw.md`
   - `projects.json`
   - `history.json`
   - `chatgpt_prompt.txt`

## 输出文件

- `output/daily_raw.md`：中文素材包，包含总体观察、优先项目、备选项目和提示词。
- `output/projects.json`：结构化项目数据。
- `output/history.json`：最近 30 天 star 历史。
- `output/chatgpt_prompt.txt`：可复制到 ChatGPT Plus 的提示词。

## 常见错误

### Actions 没运行

- 确认 `.github/workflows/daily.yml` 已经在默认分支上。
- 确认仓库的 `Actions` 功能已启用。
- 定时任务只会在默认分支触发。
- GitHub 定时任务可能延迟，不保证精确到分钟。

### artifact 找不到

- 先确认 workflow run 是否成功完成。
- 如果 `Upload output artifact` 步骤失败，通常说明程序没有生成完整的输出文件。
- 打开 `Generate daily material` 步骤日志，检查是否有 GitHub API 请求失败或运行异常。

### 输出项目太少

- 可能是 GitHub 搜索结果当天较少。
- 可能是过滤规则过滤掉了低质量项目。
- 可能是未设置有效 `GITHUB_TOKEN` 导致 API 速率限制更低。
- 可以适当调大 `.env.example` 中对应的候选数量配置，再同步到 Actions 环境变量。

### GitHub API rate limit

- Actions 中默认使用 `GITHUB_TOKEN`，比匿名请求更稳定。
- 如果仍然触发 rate limit，减少关键词数量、降低每次搜索页大小，或错开运行时间。
- 不要把个人 token 写进代码；如需自定义 token，应使用 GitHub Secrets。

## 测试

```bash
pytest
```

## 为什么不调用付费 AI API

这个项目定位是低成本素材准备工具。自动化部分只做公开数据抓取、规则过滤、打分排序和 Markdown 渲染，不承担付费模型生成任务。这样可以避免 API 成本、密钥管理和额度风险，也符合“手动复制到 ChatGPT Plus 生成公众号文章”的工作流。
