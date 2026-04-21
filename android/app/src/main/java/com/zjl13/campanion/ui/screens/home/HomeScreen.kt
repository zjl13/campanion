package com.zjl13.campanion.ui.screens.home

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
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.zjl13.campanion.core.prettyDateTime
import com.zjl13.campanion.core.ratioLabel
import com.zjl13.campanion.ui.components.ListRow
import com.zjl13.campanion.ui.components.MetricPill
import com.zjl13.campanion.ui.components.SectionCard
import com.zjl13.campanion.ui.theme.ColorTokens


@Composable
fun HomeScreen(
    viewModel: HomeViewModel,
    onOpenTask: (String) -> Unit,
    onOpenChat: (String?) -> Unit,
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        item {
            Spacer(modifier = Modifier.height(18.dp))
            Text(
                text = "今天的推进节奏",
                style = MaterialTheme.typography.headlineMedium,
            )
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                text = "${uiState.nickname}，先把最小启动动作做出来，后面的阻力会小很多。",
                style = MaterialTheme.typography.bodyLarge,
            )
        }
        uiState.stats?.let { stats ->
            item {
                SectionCard(title = "进度快照", subtitle = "你不需要一次做完，只需要继续往前。") {
                    Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
                        MetricPill("完成率", ratioLabel(stats.completionRate))
                        MetricPill("打卡率", ratioLabel(stats.checkinRate))
                        MetricPill("连续完成", "${stats.currentStreakDays}")
                    }
                }
            }
        }
        uiState.risk?.let { risk ->
            item {
                SectionCard(
                    title = "风险预警 ${risk.riskLevel.uppercase()}",
                    subtitle = risk.reasons.firstOrNull(),
                    accent = if (risk.riskLevel == "high") ColorTokens.warning else ColorTokens.cardAlt,
                ) {
                    risk.suggestions.take(2).forEach { suggestion ->
                        Text(text = "• $suggestion", style = MaterialTheme.typography.bodyMedium)
                        Spacer(modifier = Modifier.height(6.dp))
                    }
                }
            }
        }
        item {
            SectionCard(title = "今日任务", subtitle = if (uiState.tasks.isEmpty()) "今天还没有任务，去计划页生成一个。" else "点进任务详情可以改期、打卡或发起聊天。") {
                if (uiState.tasks.isEmpty()) {
                    Text("当前没有任务，说明你还没生成计划，或者今天的任务已经全部完成。")
                } else {
                    uiState.tasks.forEach { task ->
                        ListRow(
                            title = task.title,
                            subtitle = "${prettyDateTime(task.startTime)} - ${prettyDateTime(task.endTime)}",
                            trailing = task.status,
                            onClick = { onOpenTask(task.id) },
                        )
                    }
                }
            }
        }
        item {
            SectionCard(title = "快速动作", accent = ColorTokens.cardAlt) {
                Button(onClick = { onOpenChat(uiState.tasks.firstOrNull()?.id) }, modifier = Modifier.fillMaxWidth()) {
                    Text("和搭子聊聊现在卡在哪")
                }
                Spacer(modifier = Modifier.height(10.dp))
                Button(onClick = viewModel::refresh, modifier = Modifier.fillMaxWidth()) {
                    Text("刷新今日状态")
                }
            }
        }
        uiState.errorMessage?.let { message ->
            item {
                Text(
                    text = message,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.error,
                    modifier = Modifier.padding(bottom = 24.dp),
                )
            }
        }
    }
}

