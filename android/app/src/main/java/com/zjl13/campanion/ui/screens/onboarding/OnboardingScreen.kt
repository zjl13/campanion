package com.zjl13.campanion.ui.screens.onboarding

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.wrapContentHeight
import androidx.compose.foundation.lazy.LazyColumn
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
import com.zjl13.campanion.ui.components.SelectChip
import com.zjl13.campanion.ui.theme.ColorTokens


private val buddyStyles = listOf("gentle" to "温柔", "humorous" to "幽默", "calm" to "冷静", "serious" to "直接")
private val strictnessModes = listOf("gentle" to "轻提醒", "standard" to "标准", "strict" to "严格")
private val goalTypes = listOf("study" to "学习", "reading" to "阅读", "fitness" to "健身", "general" to "通用成长")
private val weekdays = (1..7).toList()


@Composable
fun OnboardingScreen(
    viewModel: OnboardingViewModel,
    onFinished: () -> Unit,
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        item {
            Spacer(modifier = Modifier.height(20.dp))
            Text(
                text = "先把第一版计划搭起来",
                style = MaterialTheme.typography.headlineMedium,
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "这里优先走最短闭环：搭子风格 + 目标 + 一个常用专注时段 + 可选固定安排。",
                style = MaterialTheme.typography.bodyLarge,
            )
        }
        item {
            SectionCard(title = "搭子风格", subtitle = "决定提醒文案和改期语气。") {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth().wrapContentHeight()) {
                    buddyStyles.forEach { (value, label) ->
                        SelectChip(label = label, selected = uiState.buddyStyle == value) {
                            viewModel.selectBuddyStyle(value)
                        }
                    }
                }
                Spacer(modifier = Modifier.height(12.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth().wrapContentHeight()) {
                    strictnessModes.forEach { (value, label) ->
                        SelectChip(label = label, selected = uiState.strictness == value) {
                            viewModel.selectStrictness(value)
                        }
                    }
                }
            }
        }
        item {
            SectionCard(title = "目标设置", subtitle = "截止日期用 yyyy-MM-dd。", accent = ColorTokens.cardAlt) {
                OutlinedTextField(
                    value = uiState.goalTitle,
                    onValueChange = viewModel::updateGoalTitle,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("目标名称") },
                    singleLine = true,
                )
                Spacer(modifier = Modifier.height(12.dp))
                OutlinedTextField(
                    value = uiState.goalDescription,
                    onValueChange = viewModel::updateGoalDescription,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("目标描述") },
                    minLines = 3,
                )
                Spacer(modifier = Modifier.height(12.dp))
                OutlinedTextField(
                    value = uiState.deadlineDate,
                    onValueChange = viewModel::updateDeadlineDate,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("截止日期") },
                    singleLine = true,
                )
                Spacer(modifier = Modifier.height(12.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth().wrapContentHeight()) {
                    goalTypes.forEach { (value, label) ->
                        SelectChip(label = label, selected = uiState.goalType == value) {
                            viewModel.selectGoalType(value)
                        }
                    }
                }
            }
        }
        item {
            SectionCard(title = "专注时间偏好", subtitle = "规则排期会优先往这个时段放任务。") {
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    weekdays.forEach { day ->
                        SelectChip(label = day.toString(), selected = uiState.focusWeekday == day) {
                            viewModel.updateFocusWeekday(day)
                        }
                    }
                }
                Spacer(modifier = Modifier.height(12.dp))
                OutlinedTextField(
                    value = uiState.focusStart,
                    onValueChange = viewModel::updateFocusStart,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("开始时间，如 19:00") },
                    singleLine = true,
                )
                Spacer(modifier = Modifier.height(12.dp))
                OutlinedTextField(
                    value = uiState.focusEnd,
                    onValueChange = viewModel::updateFocusEnd,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("结束时间，如 21:00") },
                    singleLine = true,
                )
            }
        }
        item {
            SectionCard(title = "可选固定安排", subtitle = "先支持添加 1 条周重复安排。") {
                OutlinedTextField(
                    value = uiState.scheduleTitle,
                    onValueChange = viewModel::updateScheduleTitle,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("安排名称，可留空") },
                    singleLine = true,
                )
                Spacer(modifier = Modifier.height(12.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    weekdays.forEach { day ->
                        SelectChip(label = day.toString(), selected = uiState.scheduleWeekday == day) {
                            viewModel.updateScheduleWeekday(day)
                        }
                    }
                }
                Spacer(modifier = Modifier.height(12.dp))
                OutlinedTextField(
                    value = uiState.scheduleStart,
                    onValueChange = viewModel::updateScheduleStart,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("固定开始时间，如 20:00:00") },
                    singleLine = true,
                )
                Spacer(modifier = Modifier.height(12.dp))
                OutlinedTextField(
                    value = uiState.scheduleEnd,
                    onValueChange = viewModel::updateScheduleEnd,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("固定结束时间，如 21:30:00") },
                    singleLine = true,
                )
            }
        }
        item {
            uiState.errorMessage?.let { message ->
                Text(text = message, color = MaterialTheme.colorScheme.error)
                Spacer(modifier = Modifier.height(12.dp))
            }
            Button(
                onClick = { viewModel.submit(onFinished) },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 24.dp)
                    .height(54.dp),
                enabled = !uiState.isLoading,
            ) {
                if (uiState.isLoading) {
                    CircularProgressIndicator()
                } else {
                    Text("生成我的第一版计划")
                }
            }
        }
    }
}
