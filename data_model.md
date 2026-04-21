# 数据模型建议

## 1. 核心实体总览

- User
- UserPreference
- BuddyProfile
- Goal
- CalendarBlock
- Plan
- Task
- ReminderEvent
- ChatMessage
- ProofSubmission
- ProofReview
- RescheduleRequest
- RiskSnapshot
- AnalyticsEvent

## 2. 表结构建议

## 2.1 users
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| nickname | varchar | 用户昵称 |
| avatar_url | varchar | 头像 |
| timezone | varchar | 时区 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

## 2.2 user_preferences
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| user_id | uuid | 用户 ID |
| sleep_start | time | 睡眠开始 |
| sleep_end | time | 睡眠结束 |
| reminder_level | varchar | 轻/标准/严格 |
| preferred_style | varchar | 简洁/鼓励/聊天感 |
| focus_time_blocks | jsonb | 偏好专注时间段 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

## 2.3 buddy_profiles
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| user_id | uuid | 用户 ID |
| style | varchar | 严肃/幽默/温柔等 |
| buddy_type | varchar | study/fitness/reading/general |
| strictness | varchar | 轻/标准/严格 |
| persona_name | varchar | 搭子显示名 |
| persona_summary | text | 人格摘要 |
| persona_config | jsonb | 结构化人设配置 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

## 2.4 goals
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| user_id | uuid | 用户 ID |
| buddy_id | uuid | 绑定搭子 |
| title | varchar | 目标名称 |
| description | text | 目标描述 |
| goal_type | varchar | study/fitness/reading/general |
| priority | varchar | low/medium/high |
| deadline | timestamptz | 截止时间 |
| status | varchar | active/completed/archived |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

## 2.5 calendar_blocks
固定安排、课表、会议、睡眠等。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| user_id | uuid | 用户 ID |
| title | varchar | 标题 |
| block_type | varchar | class/work/meeting/sleep/custom |
| start_time | time | 开始时间 |
| end_time | time | 结束时间 |
| weekday | int | 周几（1-7） |
| repeat_rule | varchar | weekly / none |
| start_date | date | 生效日期 |
| end_date | date | 结束日期 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

## 2.6 plans
一版规划记录，便于追踪历史重排。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| goal_id | uuid | 目标 ID |
| version | int | 计划版本号 |
| source | varchar | initial / regenerated / rescheduled |
| summary | text | 本版计划摘要 |
| risk_score | int | 风险评分 |
| raw_model_output | jsonb | 模型原始结构化输出 |
| created_at | timestamptz | 创建时间 |

## 2.7 tasks
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| goal_id | uuid | 目标 ID |
| plan_id | uuid | 计划版本 |
| parent_task_id | uuid | 父任务，可为空 |
| title | varchar | 任务标题 |
| description | text | 任务描述 |
| task_type | varchar | study/reading/fitness/custom |
| status | varchar | planned/scheduled/active/completed/missed/rescheduled/waived |
| scheduled_start | timestamptz | 计划开始 |
| scheduled_end | timestamptz | 计划结束 |
| estimated_minutes | int | 预计时长 |
| actual_minutes | int | 实际时长 |
| difficulty | varchar | easy/medium/hard |
| proof_requirement | jsonb | 建议证明方式 |
| completion_note | text | 完成备注 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

## 2.8 reminder_events
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| task_id | uuid | 任务 ID |
| reminder_type | varchar | pre_start/start/overdue/checkin |
| scheduled_at | timestamptz | 计划触发时间 |
| status | varchar | pending/sent/failed/cancelled |
| payload | jsonb | 推送内容 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

## 2.9 chat_messages
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| user_id | uuid | 用户 ID |
| buddy_id | uuid | 搭子 ID |
| role | varchar | system/user/assistant |
| message_type | varchar | normal/reminder/risk/checkin_feedback |
| content | text | 文本内容 |
| related_goal_id | uuid | 相关目标 |
| related_task_id | uuid | 相关任务 |
| metadata | jsonb | 快捷按钮、事件信息 |
| created_at | timestamptz | 创建时间 |

## 2.10 proof_submissions
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| task_id | uuid | 任务 ID |
| user_id | uuid | 用户 ID |
| media_type | varchar | image/text/audio/video |
| file_url | varchar | 文件地址 |
| text_note | text | 文字说明 |
| submitted_at | timestamptz | 提交时间 |

## 2.11 proof_reviews
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| proof_id | uuid | 打卡提交 ID |
| review_status | varchar | pending_review/accepted/needs_more_evidence/rejected |
| confidence | numeric | 置信度 |
| feedback | text | 反馈文案 |
| raw_model_output | jsonb | 模型输出 |
| reviewed_at | timestamptz | 审核时间 |

## 2.12 reschedule_requests
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| task_id | uuid | 原任务 ID |
| user_id | uuid | 用户 ID |
| reason_text | text | 用户原始原因 |
| reason_category | varchar | emergency/fatigue/conflict/procrastination/other |
| action_taken | varchar | postpone/split/downgrade/waive |
| new_task_id | uuid | 新任务 ID |
| model_summary | text | AI 说明 |
| created_at | timestamptz | 创建时间 |

## 2.13 risk_snapshots
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| goal_id | uuid | 目标 ID |
| risk_score | int | 0-100 |
| risk_level | varchar | low/medium/high |
| reasons | jsonb | 原因列表 |
| suggestions | jsonb | 建议列表 |
| created_at | timestamptz | 创建时间 |

## 2.14 analytics_events
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| user_id | uuid | 用户 ID |
| event_name | varchar | 事件名 |
| event_time | timestamptz | 事件时间 |
| properties | jsonb | 扩展属性 |

## 3. 关键索引建议

- `tasks(goal_id, scheduled_start)`
- `tasks(status, scheduled_start)`
- `reminder_events(status, scheduled_at)`
- `chat_messages(user_id, created_at)`
- `proof_submissions(task_id, submitted_at)`
- `risk_snapshots(goal_id, created_at desc)`

## 4. 数据关系说明

- 一个用户可以有多个目标。
- 一个用户通常只有一个主搭子，也可以扩展成多个搭子。
- 一个目标可生成多个计划版本。
- 一个计划版本包含多个任务。
- 一个任务可对应多个打卡提交。
- 一个任务可对应多个提醒事件。
- 一个任务可有 0 到多次改期记录。

## 5. 推荐枚举值

### goal_type
- `study`
- `fitness`
- `reading`
- `general`

### strictness
- `gentle`
- `standard`
- `strict`

### reminder_type
- `pre_start`
- `start`
- `overdue`
- `checkin`
- `risk_warning`

### reason_category
- `schedule_conflict`
- `fatigue`
- `emergency`
- `low_motivation`
- `procrastination_risk`
- `other`

## 6. MVP 简化建议

为了尽快落地，MVP 可以先简化：
- `proof_submissions` 只支持图片 + 文字。
- `calendar_blocks` 只支持按周重复。
- `buddy_profiles` 仅支持 4~6 种预设风格。
- `analytics_events` 先只埋核心事件。
