package com.zjl13.campanion.ui.screens.onboarding

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.zjl13.campanion.data.model.BuddyCreateRequest
import com.zjl13.campanion.data.model.CalendarBlockRequest
import com.zjl13.campanion.data.model.FocusBlock
import com.zjl13.campanion.data.model.GoalCreateRequest
import com.zjl13.campanion.data.model.PreferenceUpdateRequest
import com.zjl13.campanion.data.repository.CampanionRepository
import java.time.LocalDate
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch


data class OnboardingUiState(
    val buddyStyle: String = "gentle",
    val strictness: String = "standard",
    val goalType: String = "study",
    val goalTitle: String = "",
    val goalDescription: String = "",
    val deadlineDate: String = LocalDate.now().plusDays(30).toString(),
    val focusWeekday: Int = 1,
    val focusStart: String = "19:00",
    val focusEnd: String = "21:00",
    val scheduleTitle: String = "",
    val scheduleStart: String = "20:00:00",
    val scheduleEnd: String = "21:30:00",
    val scheduleWeekday: Int = 2,
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
)


class OnboardingViewModel(
    private val repository: CampanionRepository,
) : ViewModel() {
    private val _uiState = MutableStateFlow(OnboardingUiState())
    val uiState: StateFlow<OnboardingUiState> = _uiState.asStateFlow()

    fun updateGoalTitle(value: String) = _uiState.update { it.copy(goalTitle = value, errorMessage = null) }
    fun updateGoalDescription(value: String) = _uiState.update { it.copy(goalDescription = value) }
    fun updateDeadlineDate(value: String) = _uiState.update { it.copy(deadlineDate = value) }
    fun selectBuddyStyle(value: String) = _uiState.update { it.copy(buddyStyle = value) }
    fun selectStrictness(value: String) = _uiState.update { it.copy(strictness = value) }
    fun selectGoalType(value: String) = _uiState.update { it.copy(goalType = value) }
    fun updateFocusWeekday(value: Int) = _uiState.update { it.copy(focusWeekday = value) }
    fun updateFocusStart(value: String) = _uiState.update { it.copy(focusStart = value) }
    fun updateFocusEnd(value: String) = _uiState.update { it.copy(focusEnd = value) }
    fun updateScheduleTitle(value: String) = _uiState.update { it.copy(scheduleTitle = value) }
    fun updateScheduleWeekday(value: Int) = _uiState.update { it.copy(scheduleWeekday = value) }
    fun updateScheduleStart(value: String) = _uiState.update { it.copy(scheduleStart = value) }
    fun updateScheduleEnd(value: String) = _uiState.update { it.copy(scheduleEnd = value) }

    fun submit(onFinished: () -> Unit) {
        val state = uiState.value
        if (state.goalTitle.isBlank()) {
            _uiState.update { it.copy(errorMessage = "目标名还没填") }
            return
        }
        val deadline = runCatching {
            "${LocalDate.parse(state.deadlineDate)}T23:59:59+08:00"
        }.getOrElse {
            _uiState.update { current -> current.copy(errorMessage = "截止日期格式请用 2026-06-15 这种写法") }
            return
        }

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            runCatching {
                repository.updatePreferences(
                    PreferenceUpdateRequest(
                        preferredFocusBlocks = listOf(
                            FocusBlock(
                                weekday = state.focusWeekday,
                                start = state.focusStart,
                                end = state.focusEnd,
                            ),
                        ),
                    ),
                )
                val buddy = repository.createBuddy(
                    BuddyCreateRequest(
                        style = state.buddyStyle,
                        tone = "supportive",
                        strictness = state.strictness,
                        buddyType = state.goalType,
                    ),
                )
                if (state.scheduleTitle.isNotBlank()) {
                    repository.createCalendarBlock(
                        CalendarBlockRequest(
                            title = state.scheduleTitle,
                            type = "class",
                            weekday = state.scheduleWeekday,
                            startTime = state.scheduleStart,
                            endTime = state.scheduleEnd,
                        ),
                    )
                }
                val goal = repository.createGoal(
                    GoalCreateRequest(
                        title = state.goalTitle,
                        description = state.goalDescription,
                        goalType = state.goalType,
                        deadline = deadline,
                        priority = "high",
                        buddyId = buddy.buddyId,
                    ),
                )
                repository.markOnboardingCompleted(goal.goalId)
            }.onSuccess {
                onFinished()
            }.onFailure { error ->
                _uiState.update {
                    it.copy(
                        errorMessage = error.message ?: "计划生成失败，请确认后端可用",
                    )
                }
            }
            _uiState.update { it.copy(isLoading = false) }
        }
    }
}

