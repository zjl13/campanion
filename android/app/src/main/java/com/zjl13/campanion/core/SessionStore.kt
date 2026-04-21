package com.zjl13.campanion.core

import android.content.Context
import java.util.UUID


class SessionStore(context: Context) {
    private val preferences = context.getSharedPreferences("campanion_session", Context.MODE_PRIVATE)

    var authToken: String?
        get() = preferences.getString("auth_token", null)
        set(value) {
            preferences.edit().putString("auth_token", value).apply()
        }

    var userNickname: String?
        get() = preferences.getString("user_nickname", null)
        set(value) {
            preferences.edit().putString("user_nickname", value).apply()
        }

    var userId: String?
        get() = preferences.getString("user_id", null)
        set(value) {
            preferences.edit().putString("user_id", value).apply()
        }

    var onboardingCompleted: Boolean
        get() = preferences.getBoolean("onboarding_completed", false)
        set(value) {
            preferences.edit().putBoolean("onboarding_completed", value).apply()
        }

    var lastGoalId: String?
        get() = preferences.getString("last_goal_id", null)
        set(value) {
            preferences.edit().putString("last_goal_id", value).apply()
        }

    val deviceId: String
        get() {
            val existing = preferences.getString("device_id", null)
            if (!existing.isNullOrBlank()) return existing
            val generated = "android-${UUID.randomUUID()}"
            preferences.edit().putString("device_id", generated).apply()
            return generated
        }

    fun clearSession() {
        preferences.edit()
            .remove("auth_token")
            .remove("user_nickname")
            .remove("user_id")
            .remove("onboarding_completed")
            .remove("last_goal_id")
            .apply()
    }
}

