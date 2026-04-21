package com.zjl13.campanion.ui.screens.chat

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.zjl13.campanion.data.model.ChatMessage
import com.zjl13.campanion.data.model.QuickAction
import com.zjl13.campanion.data.repository.CampanionRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch


data class ChatUiState(
    val messages: List<ChatMessage> = emptyList(),
    val quickActions: List<QuickAction> = emptyList(),
    val draft: String = "",
    val isLoading: Boolean = true,
    val isSending: Boolean = false,
    val errorMessage: String? = null,
)


class ChatViewModel(
    private val repository: CampanionRepository,
) : ViewModel() {
    private val _uiState = MutableStateFlow(ChatUiState())
    val uiState: StateFlow<ChatUiState> = _uiState.asStateFlow()
    private var loadedTaskId: String? = null

    fun load(taskId: String?) {
        if (loadedTaskId == taskId && uiState.value.messages.isNotEmpty()) return
        loadedTaskId = taskId
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            runCatching { repository.getChatMessages() }
                .onSuccess { response ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            messages = response.messages,
                            quickActions = response.messages.lastOrNull()?.metadata?.actions.orEmpty(),
                        )
                    }
                }
                .onFailure { error ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            errorMessage = error.message ?: "聊天记录加载失败",
                        )
                    }
                }
        }
    }

    fun updateDraft(value: String) {
        _uiState.update { it.copy(draft = value) }
    }

    fun send(taskId: String?) {
        val message = uiState.value.draft.trim()
        if (message.isBlank()) return
        viewModelScope.launch {
            _uiState.update { it.copy(isSending = true, errorMessage = null) }
            runCatching {
                repository.sendChatMessage(message, taskId)
                repository.getChatMessages()
            }.onSuccess { response ->
                _uiState.update {
                    it.copy(
                        draft = "",
                        isSending = false,
                        messages = response.messages,
                        quickActions = response.messages.lastOrNull()?.metadata?.actions.orEmpty(),
                    )
                }
            }.onFailure { error ->
                _uiState.update {
                    it.copy(
                        isSending = false,
                        errorMessage = error.message ?: "消息发送失败",
                    )
                }
            }
        }
    }
}

