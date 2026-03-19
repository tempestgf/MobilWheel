import os
import re
import io

base_dir = 'android-client/app/src/main/res/'

def process_file(filepath, replacements):
    with io.open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    for old, new in replacements.items():
        text = text.replace(old, new)
        
    with io.open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

settings_xml = os.path.join(base_dir, 'layout/activity_settings.xml')
process_file(settings_xml, {
    'android:text="SETTINGS"': 'android:text="@string/title_settings"',
    'android:text="STEERING ANGLE"': 'android:text="@string/label_steering_angle"',
    'android:text="SWIPE THRESHOLD"': 'android:text="@string/label_swipe_threshold"',
    'android:text="CLICK TIME LIMIT"': 'android:text="@string/label_click_time_limit"',
    'android:text="ACCELERATOR SENSITIVITY"': 'android:text="@string/label_accel_sens"',
    'android:text="BRAKE SENSITIVITY"': 'android:text="@string/label_brake_sens"',
    'android:text="MUTE BACKGROUND VIDEO"': 'android:text="@string/checkbox_mute_bg"',
    'android:text="ENABLE TELEMETRY"': 'android:text="@string/checkbox_enable_telemetry"',
    'android:text="RESET DEFAULTS"': 'android:text="@string/button_reset_defaults"'
})

about_xml = os.path.join(base_dir, 'layout/activity_about.xml')
process_file(about_xml, {
    'android:text="DESCRIPTION"': 'android:text="@string/heading_description"',
    'android:text="CREDITS"': 'android:text="@string/heading_credits"',
    'android:text="LINKS"': 'android:text="@string/heading_links"'
})

main_menu_xml = os.path.join(base_dir, 'layout/activity_main_menu.xml')
process_file(main_menu_xml, {
    'android:text="START ENGINE"': 'android:text="@string/button_start_engine"',
    'android:text="DASHBOARD"': 'android:text="@string/button_dashboard"',
    'android:text="SETTINGS"': 'android:text="@string/button_settings"',
    'android:text="ABOUT"': 'android:text="@string/button_about"'
})

print("XML layouts patched")
