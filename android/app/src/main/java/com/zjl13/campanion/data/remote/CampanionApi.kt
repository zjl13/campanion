package com.zjl13.campanion.data.remote

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
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Part
import retrofit2.http.Path
import retrofit2.http.Query


interface CampanionApi {
    @POST("auth/dev-login")
    suspend fun devLogin(@Body body: DevLoginRequest): DevLoginResponse

    @GET("me")
    suspend fun getMe(): MeResponse

    @PUT("me/preferences")
    suspend fun updatePreferences(@Body body: PreferenceUpdateRequest): PreferenceResponse

    @POST("buddies")
    suspend fun createBuddy(@Body body: BuddyCreateRequest): BuddyResponse

    @POST("calendar/blocks")
    suspend fun createCalendarBlock(@Body body: CalendarBlockRequest): CalendarBlockResponse

    @GET("calendar/blocks")
    suspend fun getCalendarBlocks(): List<CalendarBlockResponse>

    @POST("goals")
    suspend fun createGoal(@Body body: GoalCreateRequest): GoalCreateResponse

    @GET("goals/{goalId}/plan")
    suspend fun getGoalPlan(@Path("goalId") goalId: String): GoalPlanResponse

    @POST("goals/{goalId}/generate-plan")
    suspend fun regeneratePlan(@Path("goalId") goalId: String): GoalPlanResponse

    @GET("goals/{goalId}/risk")
    suspend fun getGoalRisk(@Path("goalId") goalId: String): RiskResponse

    @GET("tasks/today")
    suspend fun getTodayTasks(): TodayTasksResponse

    @GET("tasks/{taskId}")
    suspend fun getTask(@Path("taskId") taskId: String): TaskDetail

    @POST("tasks/{taskId}/complete")
    suspend fun completeTask(
        @Path("taskId") taskId: String,
        @Body body: TaskCompleteRequest,
    ): TaskDetail

    @POST("tasks/{taskId}/reschedule")
    suspend fun rescheduleTask(
        @Path("taskId") taskId: String,
        @Body body: TaskRescheduleRequest,
    ): TaskRescheduleResponse

    @Multipart
    @POST("tasks/{taskId}/proofs")
    suspend fun uploadProof(
        @Path("taskId") taskId: String,
        @Part file: MultipartBody.Part?,
        @Part("text_note") note: RequestBody?,
    ): ProofUploadResponse

    @GET("proofs/{proofId}")
    suspend fun getProofReview(@Path("proofId") proofId: String): ProofReviewResponse

    @GET("chat/messages")
    suspend fun getChatMessages(
        @Query("cursor") cursor: String? = null,
        @Query("limit") limit: Int = 40,
    ): ChatListResponse

    @POST("chat/messages")
    suspend fun sendChatMessage(@Body body: ChatCreateRequest): ChatCreateResponse

    @GET("stats/overview")
    suspend fun getOverviewStats(): OverviewStatsResponse
}

