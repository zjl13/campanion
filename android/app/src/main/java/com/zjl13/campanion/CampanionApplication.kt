package com.zjl13.campanion

import android.app.Application
import com.zjl13.campanion.core.AppContainer


class CampanionApplication : Application() {
    lateinit var container: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        container = AppContainer(this)
    }
}

