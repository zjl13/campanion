package com.zjl13.campanion.ui.screens.login

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.zjl13.campanion.ui.components.SectionCard
import com.zjl13.campanion.ui.theme.AlertSoft
import com.zjl13.campanion.ui.theme.InkBlue
import com.zjl13.campanion.ui.theme.WarmWhite


@Composable
fun LoginScreen(
    viewModel: AuthViewModel,
    onLoginSuccess: () -> Unit,
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(InkBlue)
            .padding(horizontal = 20.dp, vertical = 32.dp),
        verticalArrangement = Arrangement.Center,
    ) {
        Text(
            text = "Campanion",
            style = MaterialTheme.typography.headlineLarge,
            color = WarmWhite,
        )
        Spacer(modifier = Modifier.height(10.dp))
        Text(
            text = "一个更像搭子的计划执行助手。先登录，我们把第一版目标和提醒链路跑起来。",
            style = MaterialTheme.typography.bodyLarge,
            color = WarmWhite.copy(alpha = 0.86f),
        )
        Spacer(modifier = Modifier.height(24.dp))
        SectionCard(
            title = "开发登录",
            subtitle = "当前使用后端 dev-login，适合先联调主流程。",
            accent = WarmWhite,
        ) {
            OutlinedTextField(
                value = uiState.nickname,
                onValueChange = viewModel::updateNickname,
                modifier = Modifier.fillMaxWidth(),
                label = { Text("昵称") },
                singleLine = true,
            )
            uiState.errorMessage?.let { message ->
                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    text = message,
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
            Spacer(modifier = Modifier.height(18.dp))
            Button(
                onClick = { viewModel.submit(onLoginSuccess) },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(54.dp),
                enabled = !uiState.isLoading,
                shape = RoundedCornerShape(18.dp),
            ) {
                if (uiState.isLoading) {
                    CircularProgressIndicator(color = WarmWhite)
                } else {
                    Text("进入搭子计划")
                }
            }
        }
        Spacer(modifier = Modifier.height(18.dp))
        Text(
            text = "建议先启动后端：uvicorn app.main:app --reload",
            style = MaterialTheme.typography.bodyMedium,
            color = AlertSoft,
        )
    }
}

