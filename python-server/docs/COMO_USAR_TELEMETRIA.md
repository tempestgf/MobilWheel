# 🎮 Cómo Usar el Visualizador de Telemetría AC

## ✅ Paso 1: Asegúrate de tener los requisitos

```bash
cd python-server
pip install -r requirements.txt
```

## 🚀 Paso 2: Inicia la aplicación

```bash
python ServerApp.py
```

## 📊 Paso 3: La app detecta AC automáticamente

### ¡Nueva funcionalidad! Detección automática
La aplicación **busca y se conecta automáticamente** a Assetto Corsa:

1. ✅ Al iniciar verás: **● Searching for AC...** (naranja)
2. ✅ Abre Assetto Corsa y entra a una sesión
3. ✅ La app se conectará automáticamente: **● Connected (auto)** (verde)
4. ✅ Los datos empezarán a actualizarse en tiempo real

### Estados de conexión:
- **● Searching for AC...** 🟠 - Buscando Assetto Corsa (intenta cada 2 segundos)
- **● Connected (auto)** 🟢 - Conectado y recibiendo telemetría
- Si desconectas manualmente, vuelve a buscar automáticamente

### Lo que verás:
- **Speed**: Velocidad actual en km/h
- **Gear**: Marcha actual
  - **R** = Reversa
  - **N** = Neutral
  - **1-7** = Marchas adelante
- **RPM**: Barra de progreso y valor numérico de las revoluciones
- **Gas**: Porcentaje de acelerador (0-100%)
- **Brake**: Porcentaje de freno (0-100%)

## ⚠️ Solución de Problemas

### "Searching for AC..." no se conecta

**Causa 1: AC no está en sesión**
- La app solo puede conectarse cuando estás **conduciendo en la pista**
- NO funciona en el menú principal, garage o replays
- Entra a Practice/Race/Hotlap y conduce

**Causa 2: Permisos insuficientes**
- Cierra la app
- Clic derecho en Command Prompt → **"Run as Administrator"**
- Ejecuta de nuevo: `cd python-server` → `python ServerApp.py`

**Causa 3: Versión diferente de AC**
- Algunas versiones usan un nombre diferente de shared memory
- Edita `ac_telemetry.py` línea 147:
  ```python
  SHARED_MEMORY_NAME = "acpmf_physics"  # Quita "Local\\"
  ```

### Las marchas no se muestran correctamente

✅ **Ya está arreglado en la última versión**
- La app ahora lee correctamente: R (reversa), N (neutral), 1-7 (marchas)
- Si sigue mostrando incorrectamente, verifica que tengas la última versión del código

## 🎯 Uso Normal

1. **Inicia ServerApp** → `python ServerApp.py`
2. **Verás**: ● Searching for AC... (naranja)
3. **Abre AC** → Entra a una sesión y conduce
4. **Se conecta automáticamente** → ● Connected (auto) (verde)
5. **Conduce** → Verás la telemetría actualizar en tiempo real
6. **Para desconectar** → Clic en "Disconnect" (opcional)
7. **Al cerrar AC** → La app volverá a buscar automáticamente cuando lo abras de nuevo

## 💡 Tips

- El RPM máximo por defecto es 8000. Si tu coche tiene más, edita `ServerApp.py` línea ~260:
  ```python
  maximum=12000  # Para coches con más RPM
  ```

- La actualización es a 20fps (0.05s) para no saturar la CPU. Para más velocidad, edita línea ~361:
  ```python
  poll_rate=0.033  # ~30fps
  ```

## 🔥 Características

✅ **Detección automática de AC** - No necesitas presionar ningún botón
✅ Reconexión automática si sales de AC y vuelves a entrar
✅ Actualización en tiempo real (20fps)
✅ Bajo consumo de CPU (~1-2%)
✅ Indicador visual de estado de conexión
✅ Manejo automático de errores
✅ Logs de debug integrados
✅ Lectura correcta de marchas (R/N/1-7)

## 📱 Próximos Pasos

Para enviar esta telemetría a tu app Android:
- Ver `ac_integration_examples.py` → Opción 3 (WebSocket Server)
- O implementar el servidor combinado (wheel input + telemetry)

---

**¿Problemas?** Revisa los logs en la parte inferior de la aplicación.
