# 开发实施计划（面向 Codex）

## 1. 实施目标

以最短路径做出一个能演示核心闭环的 Android MVP：
- 创建搭子
- 创建目标
- 自动规划
- 聊天提醒
- 改期重排
- 打卡审核
- 风险预警

## 2. 推荐开发顺序

## Phase 1：定义基础工程骨架

### Backend
1. 初始化 FastAPI 项目
2. 接入 PostgreSQL、Redis、对象存储
3. 建立基础模型与 migration
4. 提供 dev-login
5. 建立 Goals / Tasks / CalendarBlocks CRUD

### Android
1. 初始化 Jetpack Compose 项目
2. 建立导航框架
3. 建立网络层、Repository、ViewModel
4. 完成登录页、首页、目标创建页基础 UI

## Phase 2：先不用真实 AI，跑通闭环

### Backend
1. 写死一个 Buddy Persona 生成 stub
2. 写规则版 Planner：
   - 目标拆成固定模板任务
   - 按空闲时间分配
3. 写规则版 Reschedule：
   - 改期到最近可用空档
4. 写假的 Proof Review：
   - 有图即 accepted
   - 无图则 needs_more_evidence

### Android
1. 接今日任务页
2. 接聊天页
3. 接任务详情页
4. 接打卡上传页
5. 接改期弹窗

> 到这里应该可以形成完整 DEMO。

## Phase 3：引入真实模型

### Backend
1. 增加 LLM Gateway
2. 把 Buddy Persona 生成替换为真实模型
3. 把 Goal Planner 替换为真实模型 + 规则校验
4. 加入改期原因分类与支持式回复
5. 加入多模态 Proof Review
6. 加入 Risk Scoring（先规则，后模型解释）

## Phase 4：提醒系统

1. 建 ReminderEvent 表
2. 建 Worker 扫描未来提醒
3. 对接 FCM
4. Android 端接收推送并写入聊天页
5. WorkManager 做本地兜底提醒

## Phase 5：质量与体验优化

1. 补埋点
2. 优化加载态和错误态
3. 增加计划解释文本
4. 增加重试与 fallback
5. 加隐私设置与素材删除

## 3. Codex 建议优先生成的文件

### 后端优先
- `backend/app/main.py`
- `backend/app/core/config.py`
- `backend/app/db/session.py`
- `backend/app/models/*.py`
- `backend/app/schemas/*.py`
- `backend/app/api/routes/*.py`
- `backend/app/services/planner.py`
- `backend/app/services/rescheduler.py`
- `backend/app/services/chat_service.py`
- `backend/app/services/proof_review.py`
- `backend/app/workers/reminder_worker.py`

### Android 优先
- `android/app/src/main/java/.../MainActivity.kt`
- `ui/navigation/AppNavGraph.kt`
- `ui/screens/onboarding/*`
- `ui/screens/home/*`
- `ui/screens/chat/*`
- `ui/screens/task/*`
- `data/remote/ApiService.kt`
- `data/repository/*.kt`
- `domain/model/*.kt`

## 4. 建议的 MVP 验收 Demo 脚本

### Demo 场景 A：学习目标
1. 创建“英语四级复习”目标
2. 导入每周课程时间
3. AI 生成未来 7 天学习计划
4. 晚上 19:00 收到搭子聊天提醒
5. 用户上传单词书照片打卡
6. 系统反馈通过

### Demo 场景 B：请假改期
1. 用户点击“今晚做不了”
2. 输入“临时组会 + 状态不好”
3. 系统建议改成 20 分钟保底任务或改到 21:00
4. 用户确认后系统重排成功

### Demo 场景 C：风险预警
1. 连续 3 次改期
2. 系统发消息提示“按当前节奏赶不上”
3. 用户选择“冲刺模式”
4. 系统重排为更高频微任务

## 5. MVP 关键 fallback 机制

### 5.1 计划生成失败
- 返回规则版默认计划
- 提示“我先给你出一个基础版计划，之后还能继续优化”

### 5.2 模型超时
- 继续保留旧计划
- 记录失败日志
- 返回默认提醒文案

### 5.3 打卡审核不确定
- 返回 `needs_more_evidence`
- 要求补一句文字说明

## 6. 技术风险提醒

1. **推送不稳定**：必须做本地兜底。
2. **模型输出不稳定**：必须做 schema 校验。
3. **审核结果争议**：避免说得太绝对。
4. **时间规划复杂**：先用规则保证正确，再让 AI 提升体验。

## 7. 最适合让 Codex 直接执行的首条任务

建议你把下面这段话直接交给 Codex：

```text
请基于 docs 目录下的 prd.md、architecture.md、api_spec.md、data_model.md、prompts.md、implementation_plan.md，先生成一个可运行的后端 MVP：
1. 使用 FastAPI + PostgreSQL + SQLAlchemy；
2. 实现 dev-login、buddy 创建、goal 创建、calendar block CRUD、today tasks 查询、task reschedule、proof upload、chat message 基础接口；
3. 先使用 mock planner / mock proof review / mock chat reply；
4. 提供 docker-compose、.env.example、README；
5. 写基础测试；
6. 接口和字段尽量遵循 docs 中定义。
```

接着第二条任务给 Codex：

```text
请生成 Android Kotlin + Jetpack Compose 客户端 MVP，包含：登录页、搭子配置页、目标创建页、今日任务页、聊天页、打卡页，并对接后端 mock API。使用 MVVM、Repository、Retrofit、Room。UI 简洁，重点突出任务、提醒、打卡和改期。
```
