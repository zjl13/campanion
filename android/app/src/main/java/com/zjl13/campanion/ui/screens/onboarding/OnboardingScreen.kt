package com.zjl13.campanion.ui.screens.onboarding

import androidx.compose.foundation.layout.Arrangement
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


private val buddyStyles: List<Pair<String, String>> = listOf(
    "gentle" to "Gentle",
    "humorous" to "Humorous",
    "calm" to "Calm",
    "serious" to "Direct",
)

private val strictnessModes: List<Pair<String, String>> = listOf(
    "gentle" to "Light",
    "standard" to "Standard",
    "strict" to "Strict",
)

private val goalTypes: List<Pair<String, String>> = listOf(
    "study" to "Study",
    "reading" to "Reading",
    "fitness" to "Fitness",
    "general" to "General",
)

private val weekdays: List<Int> = (1..7).toList()


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
                text = "Build the first plan loop",
                style = MaterialTheme.typography.headlineMedium,
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "We only need the shortest useful setup: buddy style, goal, one focus window, and an optional repeating block.",
                style = MaterialTheme.typography.bodyLarge,
            )
        }
        item {
            SectionCard(
                title = "Buddy style",
                subtitle = "This controls reminder tone and reschedule replies.",
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.fillMaxWidth().wrapContentHeight(),
                ) {
                    buddyStyles.forEach { option: Pair<String, String> ->
                        val value = option.first
                        val label = option.second
                        SelectChip(label = label, selected = uiState.buddyStyle == value) {
                            viewModel.selectBuddyStyle(value)
                        }
                    }
                }
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.fillMaxWidth().wrapContentHeight(),
                ) {
                    strictnessModes.forEach { option: Pair<String, String> ->
                        val value = option.first
                        val label = option.second
                        SelectChip(label = label, selected = uiState.strictness == value) {
                            viewModel.selectStrictness(value)
                        }
                    }
                }
            }
        }
        item {
            SectionCard(
                title = "Goal setup",
                subtitle = "Use yyyy-MM-dd for the deadline.",
                accent = ColorTokens.cardAlt,
            ) {
                OutlinedTextField(
                    value = uiState.goalTitle,
                    onValueChange = viewModel::updateGoalTitle,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Goal title") },
                    singleLine = true,
                )
                Spacer(modifier = Modifier.height(12.dp))
                OutlinedTextField(
                    value = uiState.goalDescription,
                    onValueChange = viewModel::updateGoalDescription,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Goal description") },
                    minLines = 3,
                )
                Spacer(modifier = Modifier.height(12.dp))
                OutlinedTextField(
                    value = uiState.deadlineDate,
                    onValueChange = viewModel::updateDeadlineDate,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Deadline date") },
                    singleLine = true,
                )
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.fillMaxWidth().wrapContentHeight(),
                ) {
                    goalTypes.forEach { option: Pair<String, String> ->
                        val value = option.first
                        val label = option.second
                        SelectChip(label = label, selected = uiState.goalType == value) {
                            viewModel.selectGoalType(value)
                        }
                    }
                }
            }
        }
        item {
            SectionCard(
                title = "Preferred focus window",
                subtitle = "The backend planner will prioritize this window when scheduling tasks.",
            ) {
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    weekdays.forEach { day: Int ->
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
                    label = { Text("Focus start, e.g. 19:00") },
                    singleLine = true,
                )
                Spacer(modifier = Modifier.height(12.dp))
                OutlinedTextField(
                    value = uiState.focusEnd,
                    onValueChange = viewModel::updateFocusEnd,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Focus end, e.g. 21:00") },
                    singleLine = true,
                )
            }
        }
        item {
            SectionCard(
                title = "Optional weekly block",
                subtitle = "Add one repeating block now so plan generation can avoid it.",
            ) {
                OutlinedTextField(
                    value = uiState.scheduleTitle,
                    onValueChange = viewModel::updateScheduleTitle,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Block title, optional") },
                    singleLine = true,
                )
                Spacer(modifier = Modifier.height(12.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    weekdays.forEach { day: Int ->
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
                    label = { Text("Block start, e.g. 20:00:00") },
                    singleLine = true,
                )
                Spacer(modifier = Modifier.height(12.dp))
                OutlinedTextField(
                    value = uiState.scheduleEnd,
                    onValueChange = viewModel::updateScheduleEnd,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Block end, e.g. 21:30:00") },
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
                    Text("Generate first plan")
                }
            }
        }
    }
}
