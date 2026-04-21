package com.zjl13.campanion.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.navigation.NavType
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.navArgument
import androidx.navigation.compose.rememberNavController
import com.zjl13.campanion.CampanionApplication
import com.zjl13.campanion.core.appViewModel
import com.zjl13.campanion.ui.screens.chat.ChatScreen
import com.zjl13.campanion.ui.screens.chat.ChatViewModel
import com.zjl13.campanion.ui.screens.home.HomeScreen
import com.zjl13.campanion.ui.screens.home.HomeViewModel
import com.zjl13.campanion.ui.screens.login.AuthViewModel
import com.zjl13.campanion.ui.screens.login.LoginScreen
import com.zjl13.campanion.ui.screens.onboarding.OnboardingScreen
import com.zjl13.campanion.ui.screens.onboarding.OnboardingViewModel
import com.zjl13.campanion.ui.screens.task.TaskDetailScreen
import com.zjl13.campanion.ui.screens.task.TaskDetailViewModel


@Composable
fun CampanionApp() {
    val application = LocalContext.current.applicationContext as CampanionApplication
    val repository = application.container.repository
    var hasSession by remember { mutableStateOf(repository.hasSession) }
    var onboardingCompleted by remember { mutableStateOf(repository.onboardingCompleted) }
    val navController = rememberNavController()

    val startDestination = when {
        !hasSession -> AppDestination.Login.route
        onboardingCompleted -> AppDestination.Home.route
        else -> AppDestination.Onboarding.route
    }

    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = backStackEntry?.destination?.route
    val showBottomBar = currentRoute in listOf(
        AppDestination.Home.route,
        AppDestination.Onboarding.route,
        AppDestination.Chat.route,
        "chat",
    )

    Scaffold(
        bottomBar = {
            if (showBottomBar) {
                NavigationBar {
                    bottomDestinations.forEach { destination ->
                        val selected = when (destination) {
                            AppDestination.Chat -> currentRoute?.startsWith("chat") == true
                            else -> currentRoute == destination.route
                        }
                        NavigationBarItem(
                            selected = selected,
                            onClick = {
                                navController.navigate(
                                    when (destination) {
                                        AppDestination.Chat -> AppDestination.Chat.createRoute()
                                        else -> destination.route
                                    },
                                ) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            },
                            icon = {
                                destination.icon?.let { icon ->
                                    Icon(imageVector = icon, contentDescription = destination.label)
                                }
                            },
                            label = { Text(destination.label) },
                        )
                    }
                }
            }
        },
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = startDestination,
            modifier = Modifier.padding(innerPadding),
        ) {
            composable(AppDestination.Login.route) {
                val viewModel = appViewModel { container -> AuthViewModel(container.repository) }
                LoginScreen(
                    viewModel = viewModel,
                    onLoginSuccess = {
                        hasSession = true
                        onboardingCompleted = repository.onboardingCompleted
                        navController.navigate(
                            if (onboardingCompleted) AppDestination.Home.route else AppDestination.Onboarding.route,
                        ) {
                            popUpTo(AppDestination.Login.route) { inclusive = true }
                        }
                    },
                )
            }
            composable(AppDestination.Onboarding.route) {
                val viewModel = appViewModel { container -> OnboardingViewModel(container.repository) }
                OnboardingScreen(
                    viewModel = viewModel,
                    onFinished = {
                        onboardingCompleted = true
                        navController.navigate(AppDestination.Home.route) {
                            popUpTo(AppDestination.Onboarding.route) { inclusive = true }
                        }
                    },
                )
            }
            composable(AppDestination.Home.route) {
                val viewModel = appViewModel { container -> HomeViewModel(container.repository) }
                HomeScreen(
                    viewModel = viewModel,
                    onOpenTask = { taskId -> navController.navigate(AppDestination.TaskDetail.createRoute(taskId)) },
                    onOpenChat = { taskId -> navController.navigate(AppDestination.Chat.createRoute(taskId)) },
                )
            }
            composable(
                route = AppDestination.Chat.route,
                arguments = listOf(navArgument("taskId") {
                    type = NavType.StringType
                    nullable = true
                    defaultValue = null
                }),
            ) { entry ->
                val taskId = entry.arguments?.getString("taskId")
                val viewModel = appViewModel { container -> ChatViewModel(container.repository) }
                ChatScreen(viewModel = viewModel, selectedTaskId = taskId)
            }
            composable(AppDestination.TaskDetail.route) { entry ->
                val taskId = entry.arguments?.getString("taskId").orEmpty()
                val viewModel = appViewModel { container -> TaskDetailViewModel(container.repository) }
                TaskDetailScreen(
                    viewModel = viewModel,
                    taskId = taskId,
                    onBack = { navController.popBackStack() },
                    onOpenChat = { navController.navigate(AppDestination.Chat.createRoute(taskId)) },
                )
            }
        }
    }
}
