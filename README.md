# GitHub Hot Daily

低成本 GitHub 热点公众号素材生成工具。项目每天通过 GitHub REST API 抓取公开仓库数据，筛选 AI、LLM、Agent、MCP、RAG、Python、开发者工具、效率工具、自动化、前端、Web、安全、数据、开源模型、CLI 工具等方向的热点项目，并生成适合复制到 ChatGPT Plus 的素材包。

本项目不会调用 OpenAI API、Gemini API、Claude API、DeepSeek API 或任何付费 AI 生成接口。它只负责抓取、过滤、排序和整理素材，最终文章由你手动复制素材到 ChatGPT Plus 后生成。

本项目支持可选 SMTP 邮件发送，用于把素材包发到你的邮箱。不配置邮箱时会自动跳过邮件发送，不影响 GitHub Actions 生成 artifact。本项目不模拟登录 ChatGPT。

## 功能

- 使用 GitHub REST API 抓取公开仓库。
- 支持 GitHub Actions 内置 `GITHUB_TOKEN` 认证。
- 过滤 fork、archived、disabled、低信息量、课程作业、个人简历、测试仓库、广告、破解盗版、色情赌博灰产等项目。
- 生成 10 到 20 个候选项目。
- 使用综合热度分排序，不只按总 star 排序。
- 保存最近 30 天 `history.json`，用于计算 `star_delta`，并对最近几天已经出现过的项目做降权，减少跨天重复。
- 输出 `daily_raw.md`、`projects.json`、`history.json`、`chatgpt_prompt.txt`。
- 可选通过 SMTP 邮件发送素材包附件。

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
- `schedule`：每天北京时间 19:37 自动运行。

当前 GitHub Actions 的 `schedule` 支持在 cron 条目下设置 IANA 时区，因此本项目使用：

```yaml
on:
  schedule:
    - cron: "37 19 * * *"
      timezone: "Asia/Shanghai"
  workflow_dispatch:
```

如果你的仓库所在 GitHub 环境不支持 `timezone` 字段，可以改成 UTC 备用写法。北京时间是 UTC+8，所以北京时间 19:37 等于 UTC 11:37：

```yaml
on:
  schedule:
    - cron: "37 11 * * *"
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
  SMTP_HOST: ${{ secrets.SMTP_HOST }}
  SMTP_PORT: ${{ secrets.SMTP_PORT }}
  SMTP_USER: ${{ secrets.SMTP_USER }}
  SMTP_PASSWORD: ${{ secrets.SMTP_PASSWORD }}
  MAIL_FROM: ${{ secrets.MAIL_FROM }}
  MAIL_TO: ${{ secrets.MAIL_TO }}
```

SMTP 邮件配置是可选的。如果没有配置这些 Secrets，日志会显示 `SMTP 配置不完整，已跳过邮件发送。`，workflow 仍然会成功并上传 artifact。

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

## 如何配置邮件发送

邮件功能是可选的。不配置邮箱也不影响 GitHub Actions 抓取项目、生成 output 文件和上传 artifact。

如果你想每天直接在邮箱里收到素材包，需要在 GitHub 仓库里添加 Secrets。添加路径：

`GitHub 仓库页面 → Settings → Secrets and variables → Actions → New repository secret`

需要添加这些 Secrets：

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `MAIL_FROM`
- `MAIL_TO`

`MAIL_FROM` 通常填写发件邮箱。`MAIL_TO` 填写接收素材包的邮箱，可以和发件邮箱相同。

注意：`SMTP_PASSWORD` 通常不是邮箱登录密码，而是邮箱的 SMTP 授权码或应用专用密码。不要把邮箱密码、授权码或 token 写进代码。

常见邮箱配置示例：

Gmail：

```text
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

Gmail 通常需要 Google 账号的应用专用密码。

QQ 邮箱：

```text
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
```

QQ 邮箱通常需要在邮箱设置中开启 SMTP，并使用授权码。

163 邮箱：

```text
SMTP_HOST=smtp.163.com
SMTP_PORT=465
```

163 邮箱也可能使用 `994` 或 `587`，以 163 邮箱后台显示为准，通常需要授权码。

Outlook：

```text
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
```

配置后可以手动测试一次：

1. 打开仓库的 `Actions` 页面。
2. 左侧选择 `Daily GitHub Hot Projects`。
3. 点击 `Run workflow`。
4. 选择 `main` 分支并运行。
5. 等待运行完成。
6. 打开这次运行的 `Generate daily material` 日志，查看是否出现 `邮件发送成功：你的接收邮箱`。
7. 即使邮件失败，也继续到页面底部检查 artifact 是否已经上传。

如果邮件没收到，先检查：

- GitHub Actions 日志。
- 垃圾邮件箱。
- `SMTP_HOST` / `SMTP_PORT` 是否正确。
- `SMTP_PASSWORD` 是否是授权码或应用专用密码，不是登录密码。
- 发件邮箱是否开启 SMTP。
- 是否被邮箱服务商拦截。

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
