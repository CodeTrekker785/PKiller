[app]

# App name
title = My Python App

# Package name: lowercase letters and numbers only
package.name = mypythonapp

# Package domain
package.domain = org.example

# Source code directory
source.dir = .

# Files to include
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt

# Application version
version = 1.0.0

# Python dependencies required by Android
requirements = python3,kivy,kivymd,requests

# Screen orientation
orientation = portrait

# Keep Android status/navigation bars visible
fullscreen = 0

# Android permissions
android.permissions = INTERNET

# Android architectures
android.archs = arm64-v8a

# Minimum Android API
android.minapi = 24

# Target Android API
android.api = 35

# Build debug APK
android.debug_artifact = apk

# Build release APK
android.release_artifact = apk

# Android application theme
android.presplash_color = #FFFFFF

# Version code
android.numeric_version = 1

# Don't include unnecessary files
exclude_exts = spec,pyc,pyo

[buildozer]

# Build log level
log_level = 2

# Warn if Buildozer is run as root
warn_on_root = 1