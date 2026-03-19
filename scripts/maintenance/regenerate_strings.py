# -*- coding: utf-8 -*-
import os
import io

base_dir = 'android-client/app/src/main/res/'

files = {
    'values': '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Mobil Wheel</string>
    <string name="app_version">Version 1.1</string>
    <string name="app_description">This application allows you to control a virtual steering wheel using various input methods like WiFi, USB tethering, and manual IP input.</string>
    <string name="app_authors">Developed by: Geneon</string>
    <string name="back_button">Back</string>
    <string name="main_menu_title">MOBIL WHEEL</string>
    <string name="main_menu_subtitle">Virtual Controller Interface</string>
    <string name="button_start_engine">START ENGINE</string>
    <string name="button_dashboard">DASHBOARD</string>
    <string name="button_settings">SETTINGS</string>
    <string name="button_about">About</string>
    <string name="button_left_top">Left Top Button</string>
    <string name="button_left_bottom">Left Bottom Button</string>
    <string name="button_right_top">Right Top Button</string>
    <string name="button_right_bottom">Right Bottom Button</string>
    <string-array name="orientation_options">
        <item>Auto</item>
        <item>Screen faces on top</item>
        <item>Screen faces on your body</item>
    </string-array>
    
    <string name="title_connected">CONNECTED</string>
    <string name="title_offline">OFFLINE</string>
    <string name="about_link_discord">Discord</string>
    <string name="about_link_github">GitHub</string>
    <string name="about_link_web">Web</string>
    <string name="about_url_discord">https://discord.gg/XyxkZkay</string>
    <string name="about_url_github">https://github.com/tempestgf/mobilwheel</string>
    <string name="about_url_web">https://mobilwheel.com</string>
    
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
</resources>
''',
    'values-es': '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Mobil Wheel</string>
    <string name="app_version">Versión 1.1</string>
    <string name="app_description">Esta aplicación te permite controlar un volante virtual usando varios métodos de entrada como WiFi, anclaje de red USB y entrada de IP manual.</string>
    <string name="app_authors">Desarrollado por: Geneon</string>
    <string name="back_button">Atrás</string>
    <string name="main_menu_title">MOBIL WHEEL</string>
    <string name="main_menu_subtitle">Interfaz de Controlador Virtual</string>
    <string name="button_start_engine">START ENGINE</string>
    <string name="button_dashboard">DASHBOARD</string>
    <string name="button_settings">SETTINGS</string>
    <string name="button_about">ACERCA DE</string>
    <string name="button_left_top">Botón Superior Izquierdo</string>
    <string name="button_left_bottom">Botón Inferior Izquierdo</string>
    <string name="button_right_top">Botón Superior Derecho</string>
    <string name="button_right_bottom">Botón Inferior Derecho</string>
    <string-array name="orientation_options">
        <item>Automático</item>
        <item>Pantalla hacia arriba</item>
        <item>Pantalla hacia tu cuerpo</item>
    </string-array>
    <string name="title_connected">CONECTADO</string>
    <string name="title_offline">DESCONECTADO</string>
    <string name="about_link_discord">Discord</string>
    <string name="about_link_github">GitHub</string>
    <string name="about_link_web">Web</string>
    <string name="about_url_discord">https://discord.gg/XyxkZkay</string>
    <string name="about_url_github">https://github.com/tempestgf/mobilwheel</string>
    <string name="about_url_web">https://mobilwheel.com</string>

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
</resources>
''',
    'values-ca': '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Mobil Wheel</string>
    <string name="app_version">Versió 1.1</string>
    <string name="app_description">Aquesta aplicació et permet controlar un volant virtual utilitzant diversos mètodes d'entrada com ara WiFi, ancoratge de xarxa per USB i entrada d'IP manual.</string>
    <string name="app_authors">Desenvolupat per: Geneon</string>
    <string name="back_button">Enrere</string>
    <string name="main_menu_title">MOBIL WHEEL</string>
    <string name="main_menu_subtitle">Interfície de Controlador Virtual</string>
    <string name="button_start_engine">START ENGINE</string>
    <string name="button_dashboard">DASHBOARD</string>
    <string name="button_settings">SETTINGS</string>
    <string name="button_about">SOBRE L'APP</string>
    <string name="button_left_top">Botó Superior Esquerre</string>
    <string name="button_left_bottom">Botó Inferior Esquerre</string>
    <string name="button_right_top">Botó Superior Dret</string>
    <string name="button_right_bottom">Botó Inferior Dret</string>
    <string-array name="orientation_options">
        <item>Automàtic</item>
        <item>Pantalla cap amunt</item>
        <item>Pantalla cap al teu cos</item>
    </string-array>
    <string name="title_connected">CONECTAT</string>
    <string name="title_offline">DESCONECTAT</string>
    <string name="about_link_discord">Discord</string>
    <string name="about_link_github">GitHub</string>
    <string name="about_link_web">Web</string>
    <string name="about_url_discord">https://discord.gg/XyxkZkay</string>
    <string name="about_url_github">https://github.com/tempestgf/mobilwheel</string>
    <string name="about_url_web">https://mobilwheel.com</string>
    
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
</resources>
'''
}

for folder, content in files.items():
    filepath = os.path.join(base_dir, folder, 'strings.xml')
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
    with io.open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Strings generated successfully in UTF-8")
