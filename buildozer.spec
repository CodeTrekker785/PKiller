[app]

title = My Python App
package.name = mypythonapp
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt

version = 1.0.0
android.numeric_version = 1

requirements = python3,kivy,kivymd,requests

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.archs = arm64-v8a

android.minapi = 24
android.api = 35

android.debug_artifact = apk
android.release_artifact = apk

android.presplash_color = #FFFFFF

exclude_exts = spec,pyc,pyo

[buildozer]

log_level = 2
warn_on_root = 1