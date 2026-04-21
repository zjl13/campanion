package com.zjl13.campanion.ui.screens.task

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.zjl13.campanion.data.model.ProofReviewResponse
import com.zjl13.campanion.data.model.TaskDetail
import com.zjl13.campanion.data.model.TaskRescheduleResponse
import com.zjl13.campanion.data.repository.CampanionRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch


data class TaskDetailUiState(
    val isLoading: Boolean = true,
    val task: TaskDetail? = null,
    val note: String = "",
    val rescheduleReason: String = "",
    val proofReview: ProofReviewResponse? = null,
    val rescheduleResult: TaskRescheduleResponse? = null,
    val errorMessage: String? = null,
)


class TaskDetailViewModel(
    private val repository: CampanionRepository,
) : ViewModel() {
    private val _uiState = MutableStateFlow(TaskDetailUiState())
    val uiState: StateFlow<TaskDetailUiState> = _uiState.asStateFlow()
    private var loadedTaskId: String? = null

    fun load(taskId: String, force: Boolean = false) {
        if (!force && loadedTaskId == taskId && uiState.value.task != null) return
        loadedTaskId = taskId
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            runCatching { repository.getTask(taskId) }
                .onSuccess { task ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            task = task,
                            note = task.completionNote.orEmpty(),
                        )
                    }
                }
                .onFailure { error ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            errorMessage = error.message ?: "任务加载失败",
                        )
                    }
                }
        }
    }

    fun updateNote(value: String) = _uiState.update { it.copy(note = value) }
    fun updateRescheduleReason(value: String) = _uiState.update { it.copy(rescheduleReason = value) }

    fun complete(taskId: String) {
        viewModelScope.launch {
            runCatching { repository.completeTask(taskId, uiState.value.note.takeIf { it.isNotBlank() }) }
                .onSuccess { task ->
                    _uiState.update { it.copy(task = task, errorMessage = null) }
                }
                .onFailure { error ->
                    _uiState.update { it.copy(errorMessage = error.message ?: "标记完成失败") }
                }
        }
    }

    fun reschedule(taskId: String) {
        val reason = uiState.value.rescheduleReason.trim()
        if (reason.isBlank()) {
            _uiState.update { it.copy(errorMessage = "写一句改期原因会更有帮助") }
            return
        }
        viewModelScope.launch {
            runCatching { repository.rescheduleTask(taskId, reason) }
                .onSuccess { result ->
                    _uiState.update { it.copy(rescheduleResult = result, errorMessage = null) }
                    load(taskId, force = true)
                }
                .onFailure { error ->
                    _uiState.update { it.copy(errorMessage = error.message ?: "改期失败") }
                }
        }
    }

    fun uploadProof(taskId: String, imageName: String?, imageBytes: ByteArray?) {
        viewModelScope.launch {
            runCatching {
                repository.uploadProof(
                    taskId = taskId,
                    note = uiState.value.note.takeIf { it.isNotBlank() },
                    imageName = imageName,
                    imageBytes = imageBytes,
                )
            }.onSuccess { review ->
                _uiState.update { it.copy(proofReview = review, errorMessage = null) }
                load(taskId, force = true)
            }.onFailure { error ->
                _uiState.update { it.copy(errorMessage = error.message ?: "打卡提交失败") }
            }
        }
    }
}
