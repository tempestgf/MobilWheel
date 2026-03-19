# -*- coding: utf-8 -*-
import io

new_dict = '''I18N = {
    'en': {
        'status_stop': 'STATUS: STOPPED',
        'status_run': 'STATUS: RUNNING',
        'btn_start': '? START SERVER',
        'btn_stop': '¦ STOP SERVER',
        'btn_vjoy': '?? Setup vJoy',
        'btn_about': '?? About',
        'sec_control': 'CONTROL CENTER',
        'sec_logs': 'SYSTEM LOGS',
        'sec_misc': 'MISCELLANEOUS',
        'sec_telemetry': 'GAME TELEMETRY',
        'sec_axis': 'AXIS INPUTS',
        'sec_buttons': 'BUTTON STATES',
        'vjoy_title': 'vJoy Virtual Joystick',
        'vjoy_text': 'This application requires vJoy (virtual joystick) to be installed and properly configured.\\n\\nDo you want to run the automatic setup now?\\n(Requires administrator privileges)',
        'vjoy_inst_err': 'Error running vJoy installer: ',
        'vjoy_inst_err_title': 'Error',
        'vjoy_prob': 'There was a problem installing vJoy. Check logs.',
        'vjoy_prob_title': 'vJoy',
        'update_avail': 'Update available: ',
        'update_prompt': 'Do you want to download and install it now?',
        'update_err': 'Error checking updates: ',
        'cb_startup': 'Startup',
        'cb_autostart_srv': 'Auto-start',
        'cb_autoupdate': 'Auto-update',
        'pill_online': '  ?  ONLINE  ',
        'pill_offline': '  ?  OFFLINE  ',
        'pill_search': '? Searching for game...',
        'pill_conn': '? Connected ({0})',
        'btn_start_short': '?  START',
        'btn_stop_short': '¦  STOP',
        'btn_restart_short': '?  RESTART',
        'btn_update_short': '?  UPDATE',
        'btn_disconnect': 'DISCONNECT',
        'btn_checking': 'CHECKING...',
        'btn_downloading': 'DOWNLOADING...',
        'gas': 'GAS',
        'brake': 'BRAKE',
        'upd_title': 'Update',
        'upd_err1': 'Could not check for updates.\\n\\n{0}',
        'upd_err2': 'Could not complete the update.\\n\\n{0}',
        'upd_no': 'You have the latest version.',
        'msg_vjoy_installed': 'vJoy is already installed on the system.',
        'msg_vjoy_install_prompt': 'vJoy is not installed.\\nDo you want to download and install vJoy automatically? (Requires admin permissions)',
        'msg_vjoy_success': 'vJoy was installed successfully.',
        'msg_upd_latest': 'You already have the latest version ({0}).',
        'msg_upd_bad_url': 'The server did not return a valid download URL.',
        'msg_upd_dl_done': 'The update has been downloaded. The installer will start now.',
        'msg_upd_inst_err': 'Could not start the installer.\\n\\n{0}',
        'msg_about_title': 'About Mobile Wheel Server',
        'msg_about_desc': 'Use your mobile device as a PC racing wheel.',
        'msg_vjoy_title': 'Install vJoy',
        'msg_upd_title': 'Update',
        'msg_upd_avail_title': 'Update available',
        'lang_label': 'Language:',
        'upd_btn': 'Check updates'
    },
    'es': {
        'status_stop': 'ESTADO: DETENIDO',
        'status_run': 'ESTADO: EN EJECUCIÓN',
        'btn_start': '? INICIAR SERVIDOR',
        'btn_stop': '¦ DETENER SERVIDOR',
        'btn_vjoy': '?? Instalar vJoy',
        'btn_about': '?? Acerca de',
        'sec_control': 'CENTRO DE CONTROL',
        'sec_logs': 'REGISTROS DEL SISTEMA',
        'sec_misc': 'MISCELÁNEA',
        'sec_telemetry': 'TELEMETRÍA',
        'sec_axis': 'EJES DE ENTRADA',
        'sec_buttons': 'ESTADO DE BOTONES',
        'vjoy_title': 'Joystick Virtual vJoy',
        'vjoy_text': 'Esta aplicación requiere que vJoy (joystick virtual) esté instalado y configurado correctamente.\\n\\n¿Quieres ejecutar la configuración automática ahora?\\n(Requiere privilegios de administrador)',
        'vjoy_inst_err': 'Error ejecutando instalador vJoy: ',
        'vjoy_inst_err_title': 'Error',
        'vjoy_prob': 'Hubo un problema instalando vJoy. Revisa los logs.',      
        'vjoy_prob_title': 'vJoy',
        'update_avail': 'Actualización disponible: ',
        'update_prompt': '¿Quieres descargarla e instalarla ahora?',
        'update_err': 'Error buscando actualizaciones: ',
        'cb_startup': 'Inicio auto',
        'cb_autostart_srv': 'Auto-arranque',
        'cb_autoupdate': 'Auto-actualizar',
        'pill_online': '  ?  EN LÍNEA  ',
        'pill_offline': '  ?  DESCONECTADO  ',
        'pill_search': '? Buscando juego...',
        'pill_conn': '? Conectado ({0})',
        'btn_start_short': '?  INICIAR',
        'btn_stop_short': '¦  DETENER',
        'btn_restart_short': '?  REINICIAR',
        'btn_update_short': '?  ACTUALIZAR',
        'btn_disconnect': 'DESCONECTAR',
        'btn_checking': 'BUSCANDO...',
        'btn_downloading': 'DESCARGANDO...',
        'gas': 'ACELERADOR',
        'brake': 'FRENO',
        'upd_title': 'Actualización',
        'upd_err1': 'No se pudo comprobar actualizaciones.\\n\\n{0}',
        'upd_err2': 'No se pudo completar la actualización.\\n\\n{0}',
        'upd_no': 'Tienes la última versión.',
        'msg_vjoy_installed': 'vJoy ya está instalado en el sistema.',
        'msg_vjoy_install_prompt': 'vJoy no está instalado.\\n¿Deseas descargar e instalar vJoy automáticamente? (Requiere permisos de administrador)',
        'msg_vjoy_success': 'vJoy se instaló correctamente.',
        'msg_upd_latest': 'Ya tienes la última versión ({0}).',
        'msg_upd_bad_url': 'El servidor no devolvió una URL de descarga válida.',
        'msg_upd_dl_done': 'La actualización se ha descargado. El instalador se ejecutará ahora.',
        'msg_upd_inst_err': 'No se pudo iniciar el instalador.\\n\\n{0}',
        'msg_about_title': 'Acerca de Mobile Wheel Server',
        'msg_about_desc': 'Utiliza tu dispositivo móvil como volante de carreras en PC.',
        'msg_vjoy_title': 'Instalar vJoy',
        'msg_upd_title': 'Actualización',
        'msg_upd_avail_title': 'Actualización disponible',
        'lang_label': 'Idioma:',
        'upd_btn': 'Buscar actualizaciones'
    },
    'ca': {
        'status_stop': 'ESTAT: ATURAT',
        'status_run': 'ESTAT: EN EXECUCIÓ',
        'btn_start': '? INICIAR SERVIDOR',
        'btn_stop': '¦ ATURAR SERVIDOR',
        'btn_vjoy': '?? Instal·lar vJoy',
        'btn_about': '?? Quant a',
        'sec_control': 'CENTRE DE CONTROL',
        'sec_logs': 'REGISTRES DEL SISTEMA',
        'sec_misc': 'MISCEL·LÀNIA',
        'sec_telemetry': 'TELEMETRIA',
        'sec_axis': 'EIXOS D\\'ENTRADA',
        'sec_buttons': 'ESTAT DE BOTONS',
        'vjoy_title': 'Joystick Virtual vJoy',
        'vjoy_text': 'Aquesta aplicació requereix que vJoy (joystick virtual) estigui instal·lat i configurat correctament.\\n\\nVols executar la configuració automàtica ara?\\n(Requereix privilegis d\\'administrador)',
        'vjoy_inst_err': 'Error executant l\\'instal·lador vJoy: ',
        'vjoy_inst_err_title': 'Error',
        'vjoy_prob': 'Hi ha hagut un problema instal·lant vJoy. Revisa els logs.',
        'vjoy_prob_title': 'vJoy',
        'update_avail': 'Actualització disponible: ',
        'update_prompt': 'Vols descarregar-la i instal·lar-la ara?',
        'update_err': 'Error cercant actualitzacions: ',
        'cb_startup': 'Inici auto',
        'cb_autostart_srv': 'Auto-arrencada',
        'cb_autoupdate': 'Auto-actualitzar',
        'pill_online': '  ?  EN LÍNIA  ',
        'pill_offline': '  ?  DESCONNECTAT  ',
        'pill_search': '? Cercant joc...',
        'pill_conn': '? Connectat ({0})',
        'btn_start_short': '?  INICIAR',
        'btn_stop_short': '¦  ATURAR',
        'btn_restart_short': '?  REINICIAR',
        'btn_update_short': '?  ACTUALITZAR',
        'btn_disconnect': 'DESCONNECTAR',
        'btn_checking': 'CERCANT...',
        'btn_downloading': 'DESCARREGANT...',
        'gas': 'ACCELERADOR',
        'brake': 'FRE',
        'upd_title': 'Actualització',
        'upd_err1': 'No s\\'han pogut cercar actualitzacions.\\n\\n{0}',        
        'upd_err2': 'No s\\'ha pogut completar l\\'actualització.\\n\\n{0}',   
        'upd_no': 'Tens la darrera versió.',
        'msg_vjoy_installed': 'vJoy ja està instal·lat en el sistema.',
        'msg_vjoy_install_prompt': 'vJoy no està instal·lat.\\nVols descarregar i instal·lar vJoy automàticament? (Requereix permisos d\\'administrador)',
        'msg_vjoy_success': 'vJoy s\\'ha instal·lat correctament.',
        'msg_upd_latest': 'Ja tens la darrera versió ({0}).',
        'msg_upd_bad_url': 'El servidor no ha retornat una URL de descàrrega vàlida.',
        'msg_upd_dl_done': 'L\\'actualització s\\'ha descarregat. L\\'instal·lador s\\'iniciarà ara.',
        'msg_upd_inst_err': 'No s\\'ha pogut iniciar l\\'instal·lador.\\n\\n{0}',
        'msg_about_title': 'Quant a Mobile Wheel Server',
        'msg_about_desc': 'Utilitza el teu dispositiu mòbil com a volant de carreres a PC.',
        'msg_vjoy_title': 'Instal·lar vJoy',
        'msg_upd_title': 'Actualització',
        'msg_upd_avail_title': 'Actualització disponible',
        'lang_label': 'Idioma:',
        'upd_btn': 'Cercar actualitzacions'
    }
}

_LANG = "es"

def set_language(lang):
    global _LANG
    _LANG = lang

def tr(key):
    return I18N.get(_LANG, I18N["en"]).get(key, key)
'''

with io.open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Insert before "class WorkerSignals(QObject):"
if 'class WorkerSignals(QObject):' in text and 'I18N =' not in text:
    text = text.replace('class WorkerSignals(QObject):', new_dict + '\n\nclass WorkerSignals(QObject):')

# Find the language combo box creation area to restore that
init_ui_imports = '''from PyQt5.QtWidgets import QComboBox'''
if 'from PyQt5.QtWidgets import QComboBox' not in text:
    text = text.replace('from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,', 'from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox,\n                             ')

# Now add language selector to title bar
# Wait, let's look at init_ui in ServerApp.py
# If it's too complex I can just replace specific strings first

reps = {
    '"ESTADO: DETENIDO"': 'tr("status_stop")',
    '"ESTADO: EN EJECUCIÓN"': 'tr("status_run")',
    '"? INICIAR SERVIDOR"': 'tr("btn_start")',
    '"¦ DETENER SERVIDOR"': 'tr("btn_stop")',
    '"?? Instalar vJoy"': 'tr("btn_vjoy")',
    '"?? Acerca de"': 'tr("btn_about")',
    '"CENTRO DE CONTROL"': 'tr("sec_control")',
    '"REGISTROS DEL SISTEMA"': 'tr("sec_logs")',
    '"MISCELÁNEA"': 'tr("sec_misc")',
    '"TELEMETRÍA"': 'tr("sec_telemetry")',
    '"EJES DE ENTRADA"': 'tr("sec_axis")',
    '"ESTADO DE BOTONES"': 'tr("sec_buttons")',
    '"Buscando actualizaciones..."': 'tr("btn_checking")',
    '"Buscar actualizaciones"': 'tr("upd_btn")',
    '"  ?  EN LÍNEA  "': 'tr("pill_online")',
    '"  ?  DESCONECTADO  "': 'tr("pill_offline")',
    '"? Buscando juego..."': 'tr("pill_search")',
    'lbl_connection.setText(f"? Conectado ({telemetry.game_name})")': 'lbl_connection.setText(tr("pill_conn").format(telemetry.game_name))',
    '"ACELERADOR"': 'tr("gas")',
    '"FRENO"': 'tr("brake")',
    'QMessageBox.warning(self, "Actualizacion", f"No se pudo comprobar actualizaciones.\\n\\n{message}")': 'QMessageBox.warning(self, tr("msg_upd_title"), tr("upd_err1").format(message))',
    'QMessageBox.information(self, "Actualizacion", f"Ya tienes la ultima version ({APP_VERSION}).")': 'QMessageBox.information(self, tr("msg_upd_title"), tr("msg_upd_latest").format(APP_VERSION))',
    'QMessageBox.warning(self, "Actualizacion", "El servidor no devolvio una URL de descarga valida.")': 'QMessageBox.warning(self, tr("msg_upd_title"), tr("msg_upd_bad_url"))',
    'QMessageBox.question(self, "Actualizacion disponible", msg, buttons)': 'QMessageBox.question(self, tr("msg_upd_avail_title"), msg, buttons)',
    'QMessageBox.warning(self, "Actualizacion", f"No se pudo completar la actualizacion.\\n\\n{message}")': 'QMessageBox.warning(self, tr("msg_upd_title"), tr("upd_err2").format(message))',
    'QMessageBox.information(\n            self,\n            "Actualizacion descargada",\n            "Se procedera a lanzar el instalador de la nueva version.",\n        )': 'QMessageBox.information(self, tr("msg_upd_title"), tr("msg_upd_dl_done"))',
    'QMessageBox.warning(self, "Actualizacion", f"No se pudo iniciar el instalador.\\n\\n{exc}")': 'QMessageBox.warning(self, tr("msg_upd_title"), tr("msg_upd_inst_err").format(exc))',
    'QMessageBox.information(self, "vJoy", "vJoy ya está instalado en el sistema.")': 'QMessageBox.information(self, tr("vjoy_prob_title"), tr("msg_vjoy_installed"))',
    '"vJoy no está instalado.\\n¿Deseas descargar e instalar vJoy automáticamente? (Requiere permisos de administrador)"': 'tr("msg_vjoy_install_prompt")',
    'QMessageBox.question(self, \\'Instalar vJoy\\',': 'QMessageBox.question(self, tr("msg_vjoy_title"),',
    'QMessageBox.information(self, "vJoy", "vJoy se instaló correctamente.")': 'QMessageBox.information(self, tr("vjoy_prob_title"), tr("msg_vjoy_success"))',
    'QMessageBox.warning(self, "vJoy", "Hubo un problema instalando vJoy. Revisa los logs.")': 'QMessageBox.warning(self, tr("vjoy_prob_title"), tr("vjoy_prob"))',
    'QMessageBox.critical(self, "Error", f"Error iniciando instalador de vJoy: {e}")': 'QMessageBox.critical(self, tr("vjoy_inst_err_title"), f"{tr(\\'vjoy_inst_err\\')} {e}")',
    'msg.setWindowTitle("About Mobile Wheel Server")': 'msg.setWindowTitle(tr("msg_about_title"))',
    '"<p>Permite usar tu dispositivo móvil como un volante para juegos en PC.</p>"': 'f"<p>{tr(\\'msg_about_desc\\')}</p>"',
    'logging.info("Buscando actualizaciones automáticas...")': 'logging.info("Checking for automatic updates...")',
    '"Inicio con Windows"': 'tr("cb_startup")',
    '"Auto-arranque servidor"': 'tr("cb_autostart_srv")',
    '"Auto-actualizar"': 'tr("cb_autoupdate")'
}

for k, v in reps.items():
    text = text.replace(k, v)

with io.open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Patch applied for I18N and initial translations")
