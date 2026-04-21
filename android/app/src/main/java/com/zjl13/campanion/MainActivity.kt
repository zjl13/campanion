package com.zjl13.campanion

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.core.view.WindowCompat
import com.zjl13.campanion.ui.navigation.CampanionApp
import com.zjl13.campanion.ui.theme.CampanionTheme


class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        WindowCompat.setDecorFitsSystemWindows(window, false)
        setContent {
            CampanionTheme {
                CampanionApp()
            }
        }
    }
}

