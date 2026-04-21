package com.zjl13.campanion.data.model

data class DevLoginRequest(
    val deviceId: String,
    val nickname: String,
)

data class DevLoginResponse(
    val accessToken: String,
    val user: UserSummary,
)

data class UserSummary(
    val id: String,
    val nickname: String,
    val timezone: String,
)

data class FocusBlock(
    val weekday: Int,
    val start: String,
    val end: String,
)

data class SleepTime(
    val start: String,
    val end: String,
)

data class PreferenceUpdateRequest(
    val preferredFocusBlocks: List<FocusBlock>,
    val sleepTime: SleepTime? = null,
    val timezone: String? = "Asia/Shanghai",
    val reminderLevel: String? = "standard",
    val preferredStyle: String? = "encouraging",
)

data class PreferenceResponse(
    val preferredFocusBlocks: List<FocusBlock>,
    val sleepTime: SleepTime?,
    val timezone: String,
    val reminderLevel: String,
    val preferredStyle: String,
)

data class MeResponse(
    val user: UserSummary,
    val preferences: PreferenceResponse?,
)

data class BuddyCreateRequest(
    val style: String,
    val tone: String,
    val strictness: String,
    val buddyType: String,
    val language: String = "zh-CN",
)

data class BuddyResponse(
    val buddyId: String,
    val displayName: String,
    val personaSummary: String,
)

data class CalendarBlockRequest(
    val title: String,
    val type: String,
    val weekday: Int,
    val startTime: String,
    val endTime: String,
    val repeat: String = "weekly",
)

data class CalendarBlockResponse(
    val id: String,
    val title: String,
    val type: String,
    val weekday: Int,
    val startTime: String,
    val endTime: String,
    val repeat: String,
)

data class GoalCreateRequest(
    val title: String,
    val description: String,
    val goalType: String,
    val deadline: String,
    val priority: String,
    val buddyId: String?,
)

data class GoalCreateResponse(
    val goalId: String,
    val planningStatus: String,
)

data class ProofRequirement(
    val type: String,
    val hint: String,
)

data class PlannedTask(
    val id: String,
    val title: String,
    val status: String,
    val startTime: String,
    val endTime: String,
    val estimatedMinutes: Int,
    val proofRequirement: ProofRequirement,
)

data class GoalPlanResponse(
    val goalId: String,
    val planId: String,
    val riskScore: Int,
    val summary: String,
    val tasks: List<PlannedTask>,
)

data class TaskDetail(
    val id: String,
    val goalId: String,
    val title: String,
    val description: String?,
    val status: String,
    val startTime: String,
    val endTime: String,
    val estimatedMinutes: Int,
    val actualMinutes: Int?,
    val proofRequirement: ProofRequirement,
    val completionNote: String?,
)

data class TodayTasksResponse(
    val date: String,
    val tasks: List<TaskDetail>,
)

data class TaskCompleteRequest(
    val completionNote: String?,
)

data class TaskRescheduleRequest(
    val reasonText: String,
    val preferredStrategy: String = "auto",
)

data class RescheduledTaskSummary(
    val id: String,
    val startTime: String,
    val endTime: String,
)

data class TaskRescheduleResponse(
    val result: String,
    val reasonCategory: String,
    val newTask: RescheduledTaskSummary,
    val assistantReply: String,
)

data class ProofUploadResponse(
    val proofId: String,
    val reviewStatus: String,
)

data class ProofReviewResponse(
    val proofId: String,
    val reviewStatus: String,
    val confidence: Double,
    val feedback: String,
)

data class QuickAction(
    val type: String,
    val label: String,
)

data class ChatMetadata(
    val actions: List<QuickAction> = emptyList(),
)

data class ChatMessage(
    val id: String,
    val role: String,
    val content: String,
    val messageType: String,
    val relatedGoalId: String?,
    val relatedTaskId: String?,
    val metadata: ChatMetadata?,
    val createdAt: String,
)

data class ChatListResponse(
    val messages: List<ChatMessage>,
    val nextCursor: String?,
)

data class ChatCreateRequest(
    val message: String,
    val contextTaskId: String?,
)

data class ChatCreateResponse(
    val assistantMessage: ChatMessage,
    val actions: List<QuickAction>,
)

data class RiskResponse(
    val riskScore: Int,
    val riskLevel: String,
    val reasons: List<String>,
    val suggestions: List<String>,
)

data class OverviewStatsResponse(
    val completedTasks: Int,
    val completionRate: Double,
    val checkinRate: Double,
    val rescheduleCount: Int,
    val currentStreakDays: Int,
)

