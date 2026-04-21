package com.zjl13.campanion.ui.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.ChatBubbleOutline
import androidx.compose.material.icons.rounded.Home
import androidx.compose.material.icons.rounded.PostAdd
import androidx.compose.ui.graphics.vector.ImageVector


sealed class AppDestination(
    val route: String,
    val label: String,
    val icon: ImageVector? = null,
) {
    data object Login : AppDestination("login", "登录")
    data object Home : AppDestination("home", "今天", Icons.Rounded.Home)
    data object Chat : AppDestination("chat?taskId={taskId}", "搭子", Icons.Rounded.ChatBubbleOutline) {
        fun createRoute(taskId: String? = null): String = if (taskId.isNullOrBlank()) "chat" else "chat?taskId=$taskId"
    }

    data object Onboarding : AppDestination("onboarding", "计划", Icons.Rounded.PostAdd)
    data object TaskDetail : AppDestination("task/{taskId}", "任务") {
        fun createRoute(taskId: String): String = "task/$taskId"
    }
}

val bottomDestinations = listOf(
    AppDestination.Home,
    AppDestination.Chat,
    AppDestination.Onboarding,
)

