# Campanion Android

Jetpack Compose Android MVP for the AI buddy planning app.

## Current Scope

- dev login
- onboarding for buddy style + goal + focus block + optional weekly schedule
- today task home screen
- chat screen wired to backend
- task detail with complete, reschedule, and proof upload

## Stack

- Kotlin
- Jetpack Compose
- Navigation Compose
- ViewModel + StateFlow
- Retrofit + OkHttp

## Backend Base URL

Default debug URL is:

```text
http://10.0.2.2:8000/api/v1/
```

That works for the Android emulator talking to the local FastAPI backend.

## Open In Android Studio

1. Install JDK 17
2. Install Android SDK / Platform 34
3. Open the `android/` folder in Android Studio
4. Let Gradle sync
5. Run the `app` configuration

## Local Build

Windows PowerShell:

```powershell
$env:JAVA_HOME="C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot"
.\gradlew.bat assembleDebug
```

## Notes

- The project path currently contains non-ASCII characters, so `android.overridePathCheck=true` is enabled in `gradle.properties`.
- Gradle wrapper files have already been generated.
- The local machine has been verified with `D:\SDK`, and `assembleDebug` succeeded in this workspace.

## Testing Guide

For handing the app to another person for real-device testing, use:

- [REAL_DEVICE_TESTING_GUIDE.md](./REAL_DEVICE_TESTING_GUIDE.md)
