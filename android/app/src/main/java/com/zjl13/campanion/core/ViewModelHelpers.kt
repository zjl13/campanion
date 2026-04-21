package com.zjl13.campanion.core

import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewmodel.compose.viewModel
import com.zjl13.campanion.CampanionApplication


@Composable
inline fun <reified VM : ViewModel> appViewModel(
    crossinline factoryBlock: (AppContainer) -> VM,
): VM {
    val application = LocalContext.current.applicationContext as CampanionApplication
    val factory = object : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            return factoryBlock(application.container) as T
        }
    }
    return viewModel(factory = factory)
}

