package com.zjl13.campanion.data.repository

import com.zjl13.campanion.core.SessionStore
import com.zjl13.campanion.data.model.BuddyCreateRequest
import com.zjl13.campanion.data.model.BuddyResponse
import com.zjl13.campanion.data.model.CalendarBlockRequest
import com.zjl13.campanion.data.model.CalendarBlockResponse
import com.zjl13.campanion.data.model.ChatCreateRequest
import com.zjl13.campanion.data.model.ChatCreateResponse
import com.zjl13.campanion.data.model.ChatListResponse
import com.zjl13.campanion.data.model.DevLoginRequest
import com.zjl13.campanion.data.model.DevLoginResponse
import com.zjl13.campanion.data.model.GoalCreateRequest
import com.zjl13.campanion.data.model.GoalCreateResponse
import com.zjl13.campanion.data.model.GoalPlanResponse
import com.zjl13.campanion.data.model.MeResponse
import com.zjl13.campanion.data.model.OverviewStatsResponse
import com.zjl13.campanion.data.model.PreferenceResponse
import com.zjl13.campanion.data.model.PreferenceUpdateRequest
import com.zjl13.campanion.data.model.ProofReviewResponse
import com.zjl13.campanion.data.model.ProofUploadResponse
import com.zjl13.campanion.data.model.RiskResponse
import com.zjl13.campanion.data.model.TaskCompleteRequest
import com.zjl13.campanion.data.model.TaskDetail
import com.zjl13.campanion.data.model.TaskRescheduleRequest
import com.zjl13.campanion.data.model.TaskRescheduleResponse
import com.zjl13.campanion.data.model.TodayTasksResponse
import com.zjl13.campanion.data.remote.CampanionApi
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody


class CampanionRepository(
    private val api: CampanionApi,
    private val sessionStore: SessionStore,
) {
    val deviceId: String
        get() = sessionStore.deviceId

    val hasSession: Boolean
        get() = !sessionStore.authToken.isNullOrBlank()

    val storedNickname: String
        get() = sessionStore.userNickname ?: "小林"

    val onboardingCompleted: Boolean
        get() = sessionStore.onboardingCompleted

    val lastGoalId: String?
        get() = sessionStore.lastGoalId

    suspend fun login(nickname: String): DevLoginResponse {
        val response = api.devLogin(
            DevLoginRequest(
                deviceId = sessionStore.deviceId,
                nickname = nickname,
            ),
        )
        sessionStore.authToken = response.accessToken
        sessionStore.userId = response.user.id
        sessionStore.userNickname = response.user.nickname
        return response
    }

    suspend fun getMe(): MeResponse = api.getMe()

    suspend fun updatePreferences(body: PreferenceUpdateRequest): PreferenceResponse {
        return api.updatePreferences(body)
    }

    suspend fun createBuddy(body: BuddyCreateRequest): BuddyResponse {
        return api.createBuddy(body)
    }

    suspend fun createCalendarBlock(body: CalendarBlockRequest): CalendarBlockResponse {
        return api.createCalendarBlock(body)
    }

    suspend fun getCalendarBlocks(): List<CalendarBlockResponse> = api.getCalendarBlocks()

    suspend fun createGoal(body: GoalCreateRequest): GoalCreateResponse {
        val response = api.createGoal(body)
        sessionStore.lastGoalId = response.goalId
        return response
    }

    suspend fun getGoalPlan(goalId: String): GoalPlanResponse = api.getGoalPlan(goalId)

    suspend fun regeneratePlan(goalId: String): GoalPlanResponse = api.regeneratePlan(goalId)

    suspend fun getGoalRisk(goalId: String): RiskResponse = api.getGoalRisk(goalId)

    suspend fun getTodayTasks(): TodayTasksResponse = api.getTodayTasks()

    suspend fun getTask(taskId: String): TaskDetail = api.getTask(taskId)

    suspend fun completeTask(taskId: String, note: String?): TaskDetail {
        return api.completeTask(taskId, TaskCompleteRequest(note))
    }

    suspend fun rescheduleTask(taskId: String, reasonText: String): TaskRescheduleResponse {
        return api.rescheduleTask(taskId, TaskRescheduleRequest(reasonText = reasonText))
    }

    suspend fun uploadProof(
        taskId: String,
        note: String?,
        imageName: String?,
        imageBytes: ByteArray?,
    ): ProofReviewResponse {
        val filePart = if (!imageName.isNullOrBlank() && imageBytes != null) {
            MultipartBody.Part.createFormData(
                "file",
                imageName,
                imageBytes.toRequestBody("image/*".toMediaType()),
            )
        } else {
            null
        }
        val notePart = note?.takeIf { it.isNotBlank() }?.toRequestBody("text/plain".toMediaType())
        val uploadResponse: ProofUploadResponse = api.uploadProof(taskId, filePart, notePart)
        return api.getProofReview(uploadResponse.proofId)
    }

    suspend fun getChatMessages(): ChatListResponse = api.getChatMessages()

    suspend fun sendChatMessage(message: String, taskId: String?): ChatCreateResponse {
        return api.sendChatMessage(ChatCreateRequest(message = message, contextTaskId = taskId))
    }

    suspend fun getOverviewStats(): OverviewStatsResponse = api.getOverviewStats()

    fun markOnboardingCompleted(goalId: String) {
        sessionStore.onboardingCompleted = true
        sessionStore.lastGoalId = goalId
    }

    fun logout() {
        sessionStore.clearSession()
    }
}
