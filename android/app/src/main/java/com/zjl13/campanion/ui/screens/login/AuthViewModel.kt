package com.zjl13.campanion.ui.screens.login

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.zjl13.campanion.data.repository.CampanionRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch


data class AuthUiState(
    val nickname: String = "",
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
)


class AuthViewModel(
    private val repository: CampanionRepository,
) : ViewModel() {
    private val _uiState = MutableStateFlow(
        AuthUiState(
            nickname = repository.storedNickname,
        ),
    )
    val uiState: StateFlow<AuthUiState> = _uiState.asStateFlow()

    fun updateNickname(value: String) {
        _uiState.update { it.copy(nickname = value, errorMessage = null) }
    }

    fun submit(onSuccess: () -> Unit) {
        val nickname = uiState.value.nickname.trim()
        if (nickname.isBlank()) {
            _uiState.update { it.copy(errorMessage = "先给自己起个昵称吧") }
            return
        }
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            runCatching { repository.login(nickname) }
                .onSuccess { onSuccess() }
                .onFailure { error ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            errorMessage = error.message ?: "登录失败，请确认后端已启动",
                        )
                    }
                }
            _uiState.update { it.copy(isLoading = false) }
        }
    }
}
