package com.zjl13.campanion.ui.screens.chat

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.zjl13.campanion.core.prettyDateTime
import com.zjl13.campanion.ui.components.SelectChip
import com.zjl13.campanion.ui.theme.AlertSoft
import com.zjl13.campanion.ui.theme.InkBlue
import com.zjl13.campanion.ui.theme.Mist
import com.zjl13.campanion.ui.theme.Sand
import com.zjl13.campanion.ui.theme.WarmWhite


@Composable
fun ChatScreen(
    viewModel: ChatViewModel,
    selectedTaskId: String?,
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    LaunchedEffect(selectedTaskId) {
        viewModel.load(selectedTaskId)
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
    ) {
        Text(
            text = if (selectedTaskId == null) "搭子聊天" else "任务协商中",
            style = MaterialTheme.typography.headlineMedium,
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "这里接的是后端聊天接口，适合做提醒、拖延协商和快速改期讨论。",
            style = MaterialTheme.typography.bodyLarge,
        )
        Spacer(modifier = Modifier.height(16.dp))
        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            items(uiState.messages, key = { it.id }) { message ->
                val isAssistant = message.role == "assistant"
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalAlignment = if (isAssistant) Alignment.Start else Alignment.End,
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth(0.84f)
                            .background(
                                color = if (isAssistant) Sand else Mist,
                                shape = RoundedCornerShape(22.dp),
                            )
                            .padding(14.dp),
                    ) {
                        Text(
                            text = message.content,
                            style = MaterialTheme.typography.bodyLarge,
                            color = InkBlue,
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(
                            text = prettyDateTime(message.createdAt),
                            style = MaterialTheme.typography.bodySmall,
                            color = InkBlue.copy(alpha = 0.66f),
                        )
                    }
                }
            }
        }
        if (uiState.quickActions.isNotEmpty()) {
            Spacer(modifier = Modifier.height(10.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                uiState.quickActions.forEach { action ->
                    SelectChip(label = action.label, selected = false) {
                        viewModel.updateDraft(action.label)
                    }
                }
            }
        }
        Spacer(modifier = Modifier.height(12.dp))
        OutlinedTextField(
            value = uiState.draft,
            onValueChange = viewModel::updateDraft,
            modifier = Modifier.fillMaxWidth(),
            label = { Text("告诉搭子你现在的状态") },
            minLines = 2,
        )
        uiState.errorMessage?.let { message ->
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = message,
                color = AlertSoft,
                textAlign = TextAlign.Start,
            )
        }
        Spacer(modifier = Modifier.height(12.dp))
        Button(
            onClick = { viewModel.send(selectedTaskId) },
            modifier = Modifier.fillMaxWidth(),
            enabled = !uiState.isSending,
        ) {
            Text(if (uiState.isSending) "发送中..." else "发给搭子")
        }
    }
}

