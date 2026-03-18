
import os

xml_content = """<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@drawable/bg_tech_mesh"
    android:keepScreenOn="true">

    <!-- TOP HEADER -->
    <LinearLayout
        android:id="@+id/header_bar"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:gravity="center_vertical"
        android:padding="24dp"
        app:layout_constraintTop_toTopOf="parent">

        <ImageView
            android:layout_width="32dp"
            android:layout_height="32dp"
            android:src="@drawable/app_logo"
            android:alpha="0.9" />

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginStart="12dp"
            android:text="GENEON"
            android:textColor="@color/white"
            android:fontFamily="sans-serif-black"
            android:textSize="18sp"
            android:letterSpacing="0.2" />

        <View
            android:layout_width="0dp"
            android:layout_height="1dp"
            android:layout_weight="1" />

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="M-WHEEL V2"
            android:textColor="@color/racing_silver"
            android:fontFamily="monospace"
            android:textSize="12sp" />
    </LinearLayout>

    <!-- CENTER HERO: START ENGINE -->
    <androidx.constraintlayout.widget.ConstraintLayout
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        android:translationY="-20dp">

        <!-- Decorative rings -->
        <View
            android:layout_width="280dp"
            android:layout_height="280dp"
            android:background="@drawable/modern_bg"
            android:alpha="0.2"
            app:layout_constraintBottom_toBottomOf="@+id/button_start"
            app:layout_constraintEnd_toEndOf="@+id/button_start"
            app:layout_constraintStart_toStartOf="@+id/button_start"
            app:layout_constraintTop_toTopOf="@+id/button_start" />

        <Button
            android:id="@+id/button_start"
            android:layout_width="220dp"
            android:layout_height="220dp"
            android:background="@drawable/btn_push_start"
            app:backgroundTint="@null"
            android:elevation="16dp"
            android:text="START"
            android:textColor="@color/white"
            android:textSize="28sp"
            android:fontFamily="sans-serif-black"
            android:textStyle="italic"
            android:letterSpacing="0.05"
            android:stateListAnimator="@null"
            app:layout_constraintBottom_toBottomOf="parent"
            app:layout_constraintEnd_toEndOf="parent"
            app:layout_constraintStart_toStartOf="parent"
            app:layout_constraintTop_toTopOf="parent" />

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="24dp"
            android:text="TAP TO CONNECT"
            android:textColor="@color/racing_silver"
            android:fontFamily="sans-serif-condensed"
            android:letterSpacing="0.3"
            android:textSize="12sp"
            app:layout_constraintTop_toBottomOf="@+id/button_start"
            app:layout_constraintStart_toStartOf="parent"
            app:layout_constraintEnd_toEndOf="parent" />

    </androidx.constraintlayout.widget.ConstraintLayout>

    <!-- BOTTOM ACTIONS -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:paddingHorizontal="32dp"
        android:paddingBottom="48dp"
        android:clipChildren="false"
        app:layout_constraintBottom_toBottomOf="parent">

        <Button
            android:id="@+id/button_settings"
            android:layout_width="0dp"
            android:layout_weight="1"
            android:layout_height="56dp"
            android:layout_marginEnd="12dp"
            android:background="@drawable/btn_ghost_tech"
            app:backgroundTint="@null"
            android:text="@string/button_settings"
            android:textColor="@color/white"
            android:fontFamily="sans-serif-medium"
            android:letterSpacing="0.1" />

        <Button
            android:id="@+id/button_about"
            android:layout_width="0dp"
            android:layout_weight="1"
            android:layout_height="56dp"
            android:layout_marginStart="12dp"
            android:background="@drawable/btn_ghost_tech"
            app:backgroundTint="@null"
            android:text="@string/button_about"
            android:textColor="@color/white"
            android:fontFamily="sans-serif-medium"
            android:letterSpacing="0.1" />

    </LinearLayout>

    <!-- COPYRIGHT FLOATING -->
    <TextView
        android:id="@+id/footer_text"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="© 2026 Geneon // RACING MOD"
        android:textColor="#50FFFFFF"
        android:textSize="10sp"
        android:fontFamily="monospace"
        android:layout_marginBottom="16dp"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>"""

target_path = r"c:\Users\Tempestgf\Coding\MobilWheel\android-client\app\src\main\res\layout\activity_main_menu.xml"

# Force write
try:
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print(f"Successfully overwrote {target_path}")
except Exception as e:
    print(f"Error writing file: {e}")

# Verify read
with open(target_path, "r", encoding="utf-8") as f:
    read_back = f.read()
    if "Geneon // RACING MOD" in read_back:
        print("Verification: geneon copyright present.")
    else:
        print("Verification FAILED.")

"""

script_path = r"c:\Users\Tempestgf\Coding\MobilWheel\apply_final_design.py"
with open(script_path, "w", encoding="utf-8") as f:
    f.write(content)
