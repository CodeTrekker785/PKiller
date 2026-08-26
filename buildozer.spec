[app]

# App name
title = My Python App

# Package name
package.name = mypythonapp

# Package domain
package.domain = org.example

# Source code directory
source.dir = .

# Files to include in the APK
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt

# Application version
version = 1.0.0
android.numeric_version = 1

# Python dependencies
requirements = python3,kivy,kivymd,requests

# Screen orientation
orientation = portrait

# Keep status/navigation bars visible
fullscreen = 0

# Android permissions
android.permissions = INTERNET

# Android architecture
android.archs = arm64-v8a

# Android API versions
android.minapi = 24
android.api = 35

# Android SDK Build Tools
android.sdk = 35
android.ndk = 27c

# APK output
android.debug_artifact = apk
android.release_artifact = apk

# Splash screen background
android.presplash_color = #FFFFFF

# Exclude unnecessary files
exclude_exts = spec,pyc,pyo

[buildozer]

# Build log level
log_level = 2

# Warn when running as root
warn_on_root = 1