package com.zjl13.campanion.ui.screens.task

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.zjl13.campanion.core.prettyDateTime
import com.zjl13.campanion.ui.components.SectionCard
import com.zjl13.campanion.ui.theme.ColorTokens


@Composable
fun TaskDetailScreen(
    viewModel: TaskDetailViewModel,
    taskId: String,
    onBack: () -> Unit,
    onOpenChat: () -> Unit,
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current
    var selectedImageUri by remember { mutableStateOf<Uri?>(null) }
    val imagePicker = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { uri ->
        selectedImageUri = uri
    }

    LaunchedEffect(taskId) {
        viewModel.load(taskId)
    }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        item {
            Spacer(modifier = Modifier.height(18.dp))
            Text(text = "任务详情", style = MaterialTheme.typography.headlineMedium)
        }
        uiState.task?.let { task ->
            item {
                SectionCard(title = task.title, subtitle = "${prettyDateTime(task.startTime)} - ${prettyDateTime(task.endTime)}") {
                    Text(text = task.description ?: "这是一段围绕目标推进的小任务。")
                    Spacer(modifier = Modifier.height(10.dp))
                    Text(text = "状态：${task.status}")
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(text = "建议打卡：${task.proofRequirement.hint}")
                }
            }
        }
        item {
            SectionCard(title = "完成与打卡", accent = ColorTokens.cardAlt) {
                OutlinedTextField(
                    value = uiState.note,
                    onValueChange = viewModel::updateNote,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("完成说明 / 打卡备注") },
                    minLines = 3,
                )
                Spacer(modifier = Modifier.height(12.dp))
                Button(onClick = { imagePicker.launch("image/*") }, modifier = Modifier.fillMaxWidth()) {
                    Text(if (selectedImageUri == null) "选择一张图片证明" else "已选择图片，点下方提交")
                }
                Spacer(modifier = Modifier.height(10.dp))
                Button(
                    onClick = {
                        val bytes = selectedImageUri?.let { uri ->
                            context.contentResolver.openInputStream(uri)?.use { stream -> stream.readBytes() }
                        }
                        val name = selectedImageUri?.lastPathSegment?.substringAfterLast('/')
                        viewModel.uploadProof(taskId, name, bytes)
                    },
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text("提交打卡")
                }
                Spacer(modifier = Modifier.height(10.dp))
                Button(onClick = { viewModel.complete(taskId) }, modifier = Modifier.fillMaxWidth()) {
                    Text("仅标记完成")
                }
                uiState.proofReview?.let { review ->
                    Spacer(modifier = Modifier.height(12.dp))
                    Text("审核结果：${review.reviewStatus}")
                    Text(review.feedback)
                }
            }
        }
        item {
            SectionCard(title = "改期协商") {
                OutlinedTextField(
                    value = uiState.rescheduleReason,
                    onValueChange = viewModel::updateRescheduleReason,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("为什么今天做不了？") },
                    minLines = 3,
                )
                Spacer(modifier = Modifier.height(12.dp))
                Button(onClick = { viewModel.reschedule(taskId) }, modifier = Modifier.fillMaxWidth()) {
                    Text("让搭子帮我改期")
                }
                uiState.rescheduleResult?.let { result ->
                    Spacer(modifier = Modifier.height(12.dp))
                    Text(text = result.assistantReply)
                    Text(text = "新时间：${prettyDateTime(result.newTask.startTime)}")
                }
            }
        }
        item {
            Button(onClick = onOpenChat, modifier = Modifier.fillMaxWidth()) {
                Text("去聊天页继续协商")
            }
            Spacer(modifier = Modifier.height(10.dp))
            Button(onClick = onBack, modifier = Modifier.fillMaxWidth()) {
                Text("返回")
            }
            uiState.errorMessage?.let { message ->
                Spacer(modifier = Modifier.height(12.dp))
                Text(text = message, color = MaterialTheme.colorScheme.error)
            }
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}
