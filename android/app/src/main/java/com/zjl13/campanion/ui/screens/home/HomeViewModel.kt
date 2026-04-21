package com.zjl13.campanion.ui.screens.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.zjl13.campanion.data.model.OverviewStatsResponse
import com.zjl13.campanion.data.model.RiskResponse
import com.zjl13.campanion.data.model.TaskDetail
import com.zjl13.campanion.data.repository.CampanionRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch


data class HomeUiState(
    val isLoading: Boolean = true,
    val nickname: String = "你",
    val tasks: List<TaskDetail> = emptyList(),
    val stats: OverviewStatsResponse? = null,
    val risk: RiskResponse? = null,
    val errorMessage: String? = null,
)


class HomeViewModel(
    private val repository: CampanionRepository,
) : ViewModel() {
    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            runCatching {
                val me = repository.getMe()
                val tasks = repository.getTodayTasks()
                val stats = repository.getOverviewStats()
                val risk = repository.lastGoalId?.let { repository.getGoalRisk(it) }
                HomeUiState(
                    isLoading = false,
                    nickname = me.user.nickname,
                    tasks = tasks.tasks,
                    stats = stats,
                    risk = risk,
                )
            }.onSuccess { state ->
                _uiState.value = state
            }.onFailure { error ->
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        errorMessage = error.message ?: "加载首页失败",
                    )
                }
            }
        }
    }
}

