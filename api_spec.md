# API 草案（MVP）

> 风格：RESTful JSON API
> 
> 前缀建议：`/api/v1`

## 1. 认证

### POST /auth/dev-login
开发阶段快速登录。

**request**
```json
{
  "device_id": "android-emulator-001",
  "nickname": "小林"
}
```

**response**
```json
{
  "access_token": "jwt-token",
  "user": {
    "id": "usr_123",
    "nickname": "小林"
  }
}
```

## 2. 用户与搭子配置

### GET /me
返回当前用户信息。

### PUT /me/preferences
更新用户偏好与固定时间偏好。

**request**
```json
{
  "preferred_focus_blocks": [
    {"weekday": 1, "start": "19:00", "end": "22:00"}
  ],
  "sleep_time": {"start": "00:30", "end": "07:30"},
  "timezone": "Asia/Shanghai"
}
```

### POST /buddies
创建或重置 AI 搭子。

**request**
```json
{
  "style": "humorous",
  "tone": "supportive",
  "strictness": "standard",
  "buddy_type": "study",
  "language": "zh-CN"
}
```

**response**
```json
{
  "buddy_id": "bud_001",
  "display_name": "阿搭",
  "persona_summary": "一个会用轻松口吻监督你学习的搭子，愿意催你，但不会羞辱你。"
}
```

## 3. 固定安排 / 课表

### GET /calendar/blocks
获取固定不可用时间块。

### POST /calendar/blocks
创建固定时间块。

**request**
```json
{
  "title": "高数课",
  "type": "class",
  "weekday": 2,
  "start_time": "08:00",
  "end_time": "09:40",
  "repeat": "weekly"
}
```

### PUT /calendar/blocks/{block_id}
更新固定时间块。

### DELETE /calendar/blocks/{block_id}
删除固定时间块。

## 4. 目标与计划

### POST /goals
创建目标并触发首版规划。

**request**
```json
{
  "title": "6 月前完成英语四级复习",
  "description": "词汇、阅读、听力、真题",
  "goal_type": "study",
  "deadline": "2026-06-15T23:59:59+08:00",
  "priority": "high"
}
```

**response**
```json
{
  "goal_id": "goal_001",
  "planning_status": "queued"
}
```

### POST /goals/{goal_id}/generate-plan
手动触发重新规划。

### GET /goals/{goal_id}
获取目标详情与摘要。

### GET /goals/{goal_id}/plan
获取目标对应计划。

**response**
```json
{
  "goal_id": "goal_001",
  "risk_score": 28,
  "summary": "当前进度正常，建议保持每日 90 分钟学习。",
  "tasks": [
    {
      "id": "tsk_001",
      "title": "背 50 个高频单词",
      "status": "scheduled",
      "start_time": "2026-04-21T19:00:00+08:00",
      "end_time": "2026-04-21T19:40:00+08:00",
      "proof_requirement": {
        "type": "image_or_text",
        "hint": "可以上传单词书页面照片，或发送今天记住的 5 个词。"
      }
    }
  ]
}
```

## 5. 任务

### GET /tasks/today
获取今日任务。

### GET /tasks/{task_id}
获取任务详情。

### POST /tasks/{task_id}/start
手动开始任务。

### POST /tasks/{task_id}/complete
标记完成（仅用于无需证明或后续补证明场景）。

**request**
```json
{
  "completion_note": "已完成，等下补图"
}
```

### POST /tasks/{task_id}/reschedule
发起请假/改期。

**request**
```json
{
  "reason_text": "今晚临时要开组会，原来的时间做不了",
  "preferred_strategy": "auto"
}
```

**response**
```json
{
  "result": "rescheduled",
  "reason_category": "schedule_conflict",
  "new_task": {
    "id": "tsk_023",
    "start_time": "2026-04-21T21:00:00+08:00",
    "end_time": "2026-04-21T21:30:00+08:00"
  },
  "assistant_reply": "那先给你挪到 21:00，时长缩成 30 分钟，今晚先保底完成。"
}
```

## 6. 打卡与审核

### POST /tasks/{task_id}/proofs
上传打卡材料。

**request (multipart/form-data)**
- `file`: 图片
- `text_note`: 文字说明

**response**
```json
{
  "proof_id": "prf_001",
  "review_status": "pending_review"
}
```

### GET /proofs/{proof_id}
获取审核状态。

**response**
```json
{
  "proof_id": "prf_001",
  "review_status": "accepted",
  "confidence": 0.78,
  "feedback": "看起来和任务相关，已为你记录完成。下次可以补一行总结，方便我更准确判断。"
}
```

## 7. 聊天

### GET /chat/messages
拉取聊天消息。

参数：
- `cursor`
- `limit`

### POST /chat/messages
向 AI 搭子发送消息。

**request**
```json
{
  "message": "我今天真的不太想背单词了",
  "context_task_id": "tsk_001"
}
```

**response**
```json
{
  "assistant_message": {
    "id": "msg_100",
    "role": "assistant",
    "content": "你现在更像是累了，不一定是纯拖延。我们别直接放弃，先做 10 分钟启动版，做完再决定。"
  },
  "actions": [
    {"type": "quick_reschedule", "label": "改成 10 分钟启动版"},
    {"type": "keep_original", "label": "还是按原计划开始"}
  ]
}
```

## 8. 风险预警与统计

### GET /goals/{goal_id}/risk
获取目标风险评分。

**response**
```json
{
  "risk_score": 71,
  "risk_level": "high",
  "reasons": [
    "近 7 天已改期 4 次",
    "剩余任务总时长超过当前可用时间"
  ],
  "suggestions": [
    "降低每日计划颗粒度",
    "开启冲刺模式",
    "适当延后截止时间"
  ]
}
```

### GET /stats/overview
获取总览统计。

**response**
```json
{
  "completed_tasks": 18,
  "completion_rate": 0.72,
  "checkin_rate": 0.81,
  "reschedule_count": 5,
  "current_streak_days": 4
}
```

## 9. 推送事件（服务端内部事件，不一定暴露 API）

- `task.reminder.pre_start`
- `task.reminder.start`
- `task.reminder.overdue`
- `task.proof.needs_more_evidence`
- `goal.risk.high`
- `goal.plan.regenerated`

## 10. 错误码建议

```json
{
  "error": {
    "code": "TASK_CONFLICT",
    "message": "任务时间与固定安排冲突",
    "details": {}
  }
}
```

常见错误码：
- `INVALID_DEADLINE`
- `TASK_CONFLICT`
- `PROOF_TOO_LARGE`
- `UNSUPPORTED_MEDIA_TYPE`
- `PLAN_GENERATION_FAILED`
- `RESCHEDULE_NOT_ALLOWED`
- `MODEL_TIMEOUT`
