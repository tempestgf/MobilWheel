# -*- coding: utf-8 -*-
import io

with io.open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

# For 'en' block:
text = text.replace("'upd_no': 'You have the latest version.'\n    },", "'upd_no': 'You have the latest version.',\n        'msg_vjoy_installed': 'vJoy is already installed on the system.',\n        'msg_vjoy_install_prompt': 'vJoy is not installed.\\nDo you want to download and install vJoy automatically? (Requires admin permissions)',\n        'msg_vjoy_success': 'vJoy was installed successfully.',\n        'msg_upd_latest': 'You already have the latest version ({0}).',\n        'msg_upd_bad_url': 'The server did not return a valid download URL.',\n        'msg_upd_dl_done': 'The update has been downloaded. The installer will start now.',\n        'msg_upd_inst_err': 'Could not start the installer.\\n\\n{0}',\n        'msg_about_title': 'About Mobile Wheel Server',\n        'msg_about_desc': 'Use your mobile device as a PC racing wheel.',\n        'msg_vjoy_title': 'Install vJoy',\n        'msg_upd_title': 'Update',\n        'msg_upd_avail_title': 'Update available'\n    },")

# For 'es' block:
text = text.replace("'upd_no': 'Tienes la última versión.'\n    },", "'upd_no': 'Tienes la última versión.',\n        'msg_vjoy_installed': 'vJoy ya está instalado en el sistema.',\n        'msg_vjoy_install_prompt': 'vJoy no está instalado.\\n¿Deseas descargar e instalar vJoy automáticamente? (Requiere permisos de administrador)',\n        'msg_vjoy_success': 'vJoy se instaló correctamente.',\n        'msg_upd_latest': 'Ya tienes la última versión ({0}).',\n        'msg_upd_bad_url': 'El servidor no devolvió una URL de descarga válida.',\n        'msg_upd_dl_done': 'La actualización se ha descargado. El instalador se ejecutará ahora.',\n        'msg_upd_inst_err': 'No se pudo iniciar el instalador.\\n\\n{0}',\n        'msg_about_title': 'Acerca de Mobile Wheel Server',\n        'msg_about_desc': 'Utiliza tu dispositivo móvil como volante de carreras en PC.',\n        'msg_vjoy_title': 'Instalar vJoy',\n        'msg_upd_title': 'Actualización',\n        'msg_upd_avail_title': 'Actualización disponible'\n    },")

# For 'ca' block:
text = text.replace("'upd_no': 'Tens la darrera versió.'\n    }\n}", "'upd_no': 'Tens la darrera versió.',\n        'msg_vjoy_installed': 'vJoy ja està instal·lat en el sistema.',\n        'msg_vjoy_install_prompt': 'vJoy no està instal·lat.\\nVols descarregar i instal·lar vJoy automàticament? (Requereix permisos d\\'administrador)',\n        'msg_vjoy_success': 'vJoy s\\'ha instal·lat correctament.',\n        'msg_upd_latest': 'Ja tens la darrera versió ({0}).',\n        'msg_upd_bad_url': 'El servidor no ha retornat una URL de descàrrega vàlida.',\n        'msg_upd_dl_done': 'L\\'actualització s\\'ha descarregat. L\\'instal·lador s\\'iniciarà ara.',\n        'msg_upd_inst_err': 'No s\\'ha pogut iniciar l\\'instal·lador.\\n\\n{0}',\n        'msg_about_title': 'Quant a Mobile Wheel Server',\n        'msg_about_desc': 'Utilitza el teu dispositiu mòbil com a volant de carreres a PC.',\n        'msg_vjoy_title': 'Instal·lar vJoy',\n        'msg_upd_title': 'Actualització',\n        'msg_upd_avail_title': 'Actualització disponible'\n    }\n}")

reps = {
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
    'logging.info("Buscando actualizaciones automáticas...")': 'logging.info("Checking for automatic updates...")'
}

for k, v in reps.items():
    text = text.replace(k, v)

with io.open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Messages replaced perfectly.")
