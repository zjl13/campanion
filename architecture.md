# 系统架构建议

## 1. 总体架构

推荐采用 **Android 客户端 + Python 后端 + AI 网关 + 异步任务系统** 的结构。

```text
[Android App]
   |  HTTPS
   v
[FastAPI Backend]
   |-- Auth / User / Goals / Tasks / Chat API
   |-- Planner Service
   |-- Buddy Persona Service
   |-- Reschedule Service
   |-- Proof Review Service
   |-- Risk Scoring Service
   |
   |--> [PostgreSQL]
   |--> [Redis]
   |--> [Object Storage]
   |--> [Worker Queue]
   |--> [LLM Gateway]
   |
   '--> [Push Provider / FCM]
```

## 2. 设计原则

1. **AI 逻辑放后端**：避免提示词泄露、便于升级模型与策略。
2. **提醒以服务端为准**：保证用户离线或更换设备后仍可用。
3. **本地保留兜底提醒**：若推送延迟，可由 WorkManager 本地补偿。
4. **AI 输出结构化**：所有模型输出尽量约束为 JSON，降低不可控性。
5. **模型解耦**：通过统一网关封装不同大模型供应商。

## 3. Android 端模块划分

## 3.1 建议分层
- `ui/`：Compose 页面、ViewModel
- `domain/`：UseCase、实体、业务规则
- `data/`：Repository、RemoteDataSource、LocalDataSource
- `core/`：网络、日志、认证、通知、序列化

## 3.2 关键页面状态
- Home：今日任务、进度、风险横幅
- Chat：消息流、快捷操作
- Goal Setup：目标、截止时间、日程输入
- Check-in：上传证明、查看审核结果
- Settings：人格、提醒、隐私

## 3.3 本地能力
- Room：缓存任务、聊天消息、提醒记录
- WorkManager：本地提醒兜底、失败任务重试
- FCM：接收服务端提醒

## 4. 后端服务划分

## 4.1 API 层
负责认证、参数校验、返回 DTO。

## 4.2 Buddy Persona Service
根据用户选择的风格、类型、强度，生成并持久化人格配置：
- 语言风格
- 监督强度
- 常用口头禅范围
- 禁用表达（避免攻击/羞辱）

## 4.3 Planner Service
负责目标拆解、任务颗粒度控制、时间分配和重规划。

输入：
- 用户目标
- 截止时间
- 不可用日程
- 过去完成表现
- 用户偏好时段

输出：
- 分阶段计划
- 未来若干天的任务安排
- 每个任务的建议证明方式
- 风险因子

## 4.4 Chat Orchestrator
负责把系统事件转成聊天消息，例如：
- 任务即将开始
- 用户迟迟未开始
- 用户申请改期
- 用户完成打卡
- 风险预警

输入：结构化事件
输出：人格一致的聊天文案

## 4.5 Reschedule Service
负责解析用户请假/改期请求：
- 分类原因
- 判断是紧急情况、合理冲突、疲劳还是拖延风险
- 决定重排策略
- 更新任务时间

## 4.6 Proof Review Service
负责审核打卡材料。

MVP 处理方式建议：
1. 先做图片 + 文字说明。
2. 调用多模态模型判断“是否与任务相关”。
3. 输出 `accepted / needs_more_evidence / rejected`。
4. 返回简短建议，而不是过度武断地判定真假。

## 4.7 Risk Scoring Service
基于规则 + 模型联合计算风险：
- 剩余任务总时长
- 剩余可用时间
- 改期次数
- 实际完成率
- 连续 missed 次数

产出：
- 风险分数 0-100
- 风险等级 low / medium / high
- 解释文本
- 建议动作

## 4.8 Scheduler / Worker
负责：
- 定时提醒
- 任务到点状态切换
- 风险扫描
- 推送发送
- 审核重试

## 5. 推荐数据流

## 5.1 创建目标
1. Android 提交目标与日程
2. Backend 保存目标
3. Planner Service 调用模型进行拆解
4. 结果结构化后写入 task 表
5. Scheduler 生成 reminder events
6. 返回今日计划给客户端

## 5.2 到点提醒
1. Worker 扫描未来 5~10 分钟内任务
2. 生成提醒事件
3. Chat Orchestrator 生成拟人文案
4. 发送 FCM
5. 客户端展示推送并同步到聊天页

## 5.3 请假改期
1. 用户点击“今天做不了”
2. 客户端发送原因文本
3. Reschedule Service 分类原因
4. Planner Service 重新排期
5. 更新任务、提醒、风险分数
6. 通过聊天返回协商结果

## 5.4 打卡审核
1. 用户上传图片 + 说明
2. 文件存入对象存储
3. 创建 proof_review_job
4. Worker 调用多模态模型审核
5. 回写审核结果
6. Chat Orchestrator 生成反馈消息

## 6. 计划生成策略

推荐采用“规则优先 + 模型补充”的混合方案。

### 6.1 为什么不用纯模型直接排所有时间
- 纯模型不稳定，容易忽略硬性冲突
- 调整成本高
- 可解释性差

### 6.2 推荐流程
1. 规则层先计算可用时间块。
2. 模型负责目标拆解和任务建议。
3. 规则层做时间分配与冲突检测。
4. 模型再润色说明与提醒文案。

### 6.3 伪代码

```python
available_slots = subtract_fixed_blocks(user_calendar, sleep_blocks)
plan_outline = llm_generate_plan(goal, deadline, user_preferences)
tasks = normalize_and_validate(plan_outline)
allocated = allocate_tasks_into_slots(tasks, available_slots)
risk = compute_risk(allocated, deadline, historical_stats)
```

## 7. 任务颗粒度策略

- 默认单任务 25~60 分钟
- 若用户频繁拖延，则降为 10~20 分钟微任务
- 若目标复杂，则自动拆为：准备 -> 执行 -> 收尾 -> 打卡

例如：
- “写作业 2 小时” 拆成：
  - 整理题目 10 分钟
  - 完成前半部分 40 分钟
  - 完成后半部分 40 分钟
  - 拍照提交 5 分钟

## 8. 提醒策略

### 8.1 建议提醒点
- T-10 分钟：预告
- T 时刻：开始提醒
- T+15 分钟：未开始时轻催
- 截止前 5 分钟：提交提醒

### 8.2 提醒强度
- 轻提醒：每天较少催办
- 标准：按节点提醒
- 严格：对 missed 和未提交打卡做额外跟进

## 9. 状态机建议

### 9.1 任务状态机

```text
planned -> scheduled -> active -> completed
                     \-> missed
active -> rescheduled
scheduled -> rescheduled
scheduled -> waived
```

### 9.2 打卡状态机

```text
none -> pending_review -> accepted
                     \-> needs_more_evidence -> pending_review
                     \-> rejected
```

## 10. 模型调用策略

### 10.1 推荐模型分工
- 文本模型：人格、规划、聊天、重排、风险解释
- 多模态模型：图片打卡审核

### 10.2 输出约束
所有模型结果尽量返回 JSON，例如：

```json
{
  "reason_category": "fatigue",
  "risk_level": "medium",
  "action": "split_task",
  "new_plan": [
    {
      "title": "背 20 个单词",
      "start_time": "2026-04-21T20:00:00+08:00",
      "end_time": "2026-04-21T20:20:00+08:00"
    }
  ],
  "reply": "看起来你今天状态一般，我们先别硬顶整块任务，改成 20 分钟保底版。"
}
```

## 11. 安全与隐私

### 11.1 敏感数据
- 日程表
- 目标内容
- 打卡图片
- 聊天记录
- 行为分析结果

### 11.2 最低要求
- 对象存储使用签名 URL
- 数据库敏感字段加密或最小化存储
- 打卡素材可删除
- 提供隐私说明和素材保留周期设置

## 12. 可观测性

建议记录：
- reminder_sent
- reminder_opened
- task_started
- task_completed
- proof_uploaded
- proof_accepted
- reschedule_requested
- risk_warning_sent

这些事件可用于后续优化规划质量和提醒策略。
