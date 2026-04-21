package com.zjl13.campanion.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable


private val LightColors = lightColorScheme(
    primary = InkBlue,
    onPrimary = WarmWhite,
    secondary = TideBlue,
    onSecondary = WarmWhite,
    tertiary = Poppy,
    background = WarmWhite,
    onBackground = InkBlue,
    surface = ColorTokens.card,
    onSurface = InkBlue,
    error = Poppy,
)

private val DarkColors = darkColorScheme(
    primary = Mist,
    onPrimary = InkBlue,
    secondary = AlertSoft,
    onSecondary = InkBlue,
    tertiary = Poppy,
    background = InkBlue,
    onBackground = WarmWhite,
    surface = PlumShadow,
    onSurface = WarmWhite,
    error = AlertSoft,
)

object ColorTokens {
    val card = Sand
    val cardAlt = Mist
    val success = Moss
    val warning = AlertSoft
}

@Composable
fun CampanionTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = LightColors,
        typography = CampanionTypography,
        content = content,
    )
}

