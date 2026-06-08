[app]

# (str) Title of your application
title = Dakati Game

# (str) Package name
package.name = dakatigame

# (str) Package domain (needed for android packaging)
package.domain = org.dakati

# (str) Source code directory where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (list) List of exclusions using pattern matching
source.exclude_dirs = tests, bin, .git, .github

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.1

# (str) Custom source folders for requirements
# Useful to avoid reloading requirements on every build
#requirements.source.kivy = ../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/assets/dakati_intro_image.png

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/icon.jpg

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services =

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
#android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android NDK directory (if empty, it will be automatically downloaded)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded)
#android.ant_path =

# (bool) Use --private data directory (True, default) or --dir public directory (False)
#android.private_storage = True

# (str) Android entry point, default is to use start.py of python-for-android
#android.entrypoint = default

# (str) Android app theme, default is ok for Kivy-based app
#android.apptheme = "@android:style/Theme.NoTitleBar.Fullscreen"

# (list) Pattern to exclude for shrink resources
#android.shrink_resources_exclude_patterns =

# (list) Directory clean before build
#android.clean = False

# (list) Android AAR archives to add
#android.add_aars =

# (list) Gradle dependencies
#android.gradle_dependencies =

# (list) Java files to add to the project
#android.add_srcs =

# (list) Android packaging options
#packaging.options =

# (list) Java compiler options
#android.javac_options =

# (bool) Enable AndroidX support
android.enable_androidx = True

# (bool) Automatically accept Android SDK license
android.accept_sdk_license = True

# (str) Format of the artifact to build (apk or aab)
android.archs = armeabi-v7a, arm64-v8a

# (bool) Skip byte compile for .py files
#android.skip_byte_compile = False

# (str) Log level (info, debug, trace)
log_level = 2

# (int) Port to use for android debug (default 8000)
#android.port = 8000

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug and stdout)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to buildozer work directory
#build_dir = ./.buildozer

# (str) Path to buildozer bin directory
#bin_dir = ./bin
