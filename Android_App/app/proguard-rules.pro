# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.
#
# For more details, see
#   http://developer.android.com/guide/developing/tools/proguard.html

# If your project uses WebView with JS, uncomment the following
# and specify the fully qualified class name to the JavaScript interface
# class:
#-keepclassmembers class fqcn.of.javascript.interface.for.webview {
#   public *;
#}

# Uncomment this to preserve the line number information for
# debugging stack traces.
#-keepattributes SourceFile,LineNumberTable

# If you keep the line number information, uncomment this to
# hide the original source file name.
#-renamesourcefileattribute SourceFile

# Keep VoicePay classes
-keep class com.voicepay.** { *; }

# Keep speech recognition classes
-keep class android.speech.** { *; }

# Keep TTS classes  
-keep class android.speech.tts.** { *; }

# Keep UPI intent data
-keepclassmembers class * {
    public static final java.lang.String EXTRA_*;
}

# Preserve annotations
-keepattributes *Annotation*

# Keep native methods
-keepclasseswithmembernames class * {
    native <methods>;
}

# Keep classes used by reflection
-keepclassmembers class * {
    @androidx.annotation.Keep *;
}

# Kotlin coroutines
-keep class kotlinx.coroutines.** { *; }
-dontwarn kotlinx.coroutines.**

# Keep LiveData and ViewModel
-keep class androidx.lifecycle.** { *; }
-dontwarn androidx.lifecycle.**
