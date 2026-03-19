# -*- coding: utf-8 -*-
import os
import io

base_dir = 'android-client/app/src/main/res/'

strings_to_add = {
    'values': '''
    <string name="title_settings">SETTINGS</string>
    <string name="label_steering_angle">STEERING ANGLE</string>
    <string name="label_swipe_threshold">SWIPE THRESHOLD</string>
    <string name="label_click_time_limit">CLICK TIME LIMIT</string>
    <string name="label_accel_sens">ACCELERATOR SENSITIVITY</string>
    <string name="label_brake_sens">BRAKE SENSITIVITY</string>
    <string name="checkbox_mute_bg">MUTE BACKGROUND VIDEO</string>
    <string name="checkbox_enable_telemetry">ENABLE TELEMETRY</string>
    <string name="button_reset_defaults">RESET DEFAULTS</string>
    <string name="heading_description">DESCRIPTION</string>
    <string name="heading_credits">CREDITS</string>
    <string name="heading_links">LINKS</string>
''',
    'values-es': '''
    <string name="title_settings">AJUSTES</string>
    <string name="label_steering_angle">ÁNGULO DE DIRECCIÓN</string>
    <string name="label_swipe_threshold">UMBRAL DE DESLIZAMIENTO</string>
    <string name="label_click_time_limit">LÍMITE TIEMPO CLIC</string>
    <string name="label_accel_sens">SENSIBILIDAD ACELERADOR</string>
    <string name="label_brake_sens">SENSIBILIDAD FRENO</string>
    <string name="checkbox_mute_bg">SILENCIAR VIDEO DE FONDO</string>
    <string name="checkbox_enable_telemetry">HABILITAR TELEMETRÍA</string>
    <string name="button_reset_defaults">RESTAURAR VALORES DE FÁBRICA</string>
    <string name="heading_description">DESCRIPCIÓN</string>
    <string name="heading_credits">CRÉDITOS</string>
    <string name="heading_links">ENLACES</string>
''',
    'values-ca': '''
    <string name="title_settings">AJUSTOS</string>
    <string name="label_steering_angle">ANGLE DE DIRECCIÓ</string>
    <string name="label_swipe_threshold">LLINDAR DE LISCAMENT</string>
    <string name="label_click_time_limit">LÍMIT TEMPS CLIC</string>
    <string name="label_accel_sens">SENSIBILITAT ACCELERADOR</string>
    <string name="label_brake_sens">SENSIBILITAT FRE</string>
    <string name="checkbox_mute_bg">SILENCIAR VÍDEO DE FONS</string>
    <string name="checkbox_enable_telemetry">HABILITAR TELEMETRIA</string>
    <string name="button_reset_defaults">RESTAURAR VALORS DE FÀBRICA</string>
    <string name="heading_description">DESCRIPCIÓ</string>
    <string name="heading_credits">CRÈDITS</string>
    <string name="heading_links">ENLLAÇOS</string>
'''
}

for folder, lines in strings_to_add.items():
    filepath = os.path.join(base_dir, folder, 'strings.xml')
    if os.path.exists(filepath):
        with io.open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # insert before </resources>
        text = text.replace('</resources>', lines + '</resources>')
        
        with io.open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)

print("Strings added to strings.xml")

