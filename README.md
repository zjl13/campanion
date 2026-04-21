# AI Buddy Specs + Backend MVP

这个仓库现在包含两部分内容：

- 根目录规格文档：`prd.md`、`architecture.md`、`api_spec.md`、`data_model.md`、`prompts.md`、`implementation_plan.md`
- 已实现的后端 MVP：[`backend/`](./backend)

## 当前交付范围

本次已经按文档落地了一个可运行的 FastAPI 后端 MVP，覆盖：

- `dev-login`
- 用户偏好配置
- AI 搭子创建
- 固定日程 CRUD
- 目标创建与规则版 7 天计划生成
- 今日任务查询
- 聊天消息与支持式回复
- 任务改期与重排
- 打卡上传与 mock 审核
- 风险快照与概览统计

## 目录说明

```text
.
├─ backend/              # FastAPI 后端 MVP
├─ infra/                # docker-compose
├─ prd.md
├─ architecture.md
├─ api_spec.md
├─ data_model.md
├─ prompts.md
└─ implementation_plan.md
```

## 本地运行

先安装 Python 3.11+，然后在 `backend/` 下执行：

```bash
pip install -e .[dev]
uvicorn app.main:app --reload
```

默认使用 SQLite，本地 proof 文件会写到 `backend/storage/proofs/`。

## 测试

在 `backend/` 下执行：

```bash
pytest -p no:cacheprovider
```

## 后续建议

- 先接真实 LLM 网关，替换 `planner / chat / proof review` 的 mock 逻辑
- 再补 Android Kotlin + Jetpack Compose 客户端
- 如果需要，我可以继续把这个仓库扩成完整前后端联调版本
