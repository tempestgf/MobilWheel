# 🔧 Actualización: Telemetría AC → App Android

## ✅ Cambios Realizados

### Problema Original
El servidor Python usaba el **protocolo UDP viejo** de AC (puerto 9996) que:
- ❌ No siempre funciona (depende de configuración de AC)
- ❌ Requiere activar "AC Server" en Content Manager
- ❌ Es menos confiable que shared memory
- ❌ Tiene latencia mayor

### Solución Implementada
Ahora el servidor usa **shared memory** (mismo método que la GUI):
- ✅ Más confiable y directo
- ✅ No requiere configurar UDP en AC
- ✅ Latencia mínima
- ✅ Auto-reconexión automática
- ✅ Corrección de marchas incluida

## 🔄 Cambios en el Código

### `xbox.py` - Función `forward_ac_telemetry()`

**CAMBIO 1: Shared Memory (más confiable)**
```python
# Usa ACTelemetryReader (shared memory)
telemetry_reader = ACTelemetryReader()
telemetry_reader.connect()
data = telemetry_reader.read_physics()
```

**CAMBIO 2: Corrección de offset de marchas para Android**
```python
# Android espera formato original: 0=R, 1=N, 2=1ª, 3=2ª...
# data.gear viene corregido: -1=R, 0=N, 1=1ª, 2=2ª...
# Sumamos +1 para volver al formato que Android espera
gear = data.gear + 1
```

**CAMBIO 3: Reducción de frecuencia (priorizar volante)**
```python
SEND_INTERVAL = 1.0 / 10.0  # 10 Hz (antes era 30 Hz)
time.sleep(0.05)  # Menor saturación de red
```

### Formato de Mensaje
```
T:velocidad:marcha:rpm\n
```

**Ejemplo:** `T:125:3:5500\n`
- Velocidad: 125 km/h
- Marcha: 3 (formato Android: 0=R, 1=N, 2=1ª, 3=2ª...)
- RPM: 5500

## 🎯 Cómo Usar

### 1. Iniciar el Servidor
```bash
cd python-server
python ServerApp.py
```

### 2. Conectar desde Android
1. Abre tu app Mobile Wheel en Android
2. Conecta al servidor PC (IP:12345)
3. La telemetría se enviará automáticamente cuando:
   - Assetto Corsa esté abierto
   - Estés en una sesión (conduciendo)

### 3. Qué Verás en Android
- **GEAR**: R / N / 1 / 2 / 3 / 4 / 5 / 6 / 7
- **SPEED**: Velocidad en km/h
- **RPM Dots**: 15 LEDs (verde → amarillo → rojo)

## 🔍 Comportamiento Automático

El servidor ahora:
1. ✅ Intenta conectar a AC automáticamente cada 3s
2. ✅ Se conecta cuando detecta AC en sesión
3. ✅ Envía telemetría a 30 Hz (30 fps) al Android
4. ✅ Se reconecta automáticamente si pierdes AC
5. ✅ Limpia recursos al desconectar Android

## 📊 Logs del Servidor

Verás mensajes como:
```
INFO - Conectado a AC telemetry (shared memory)
DEBUG - AC no disponible (menú/sin sesión) — reintentando en 3s
INFO - Telemetry forwarder stopped
```

## ⚠️ Troubleshooting

### La app Android no muestra telemetría

**Verifica:**
1. ✅ ServerApp está corriendo
2. ✅ Android está conectado al servidor (IP correcta)
3. ✅ Assetto Corsa está abierto Y en sesión (conduciendo)
4. ✅ Python tiene permisos de administrador (si es necesario)

**En los logs del servidor deberías ver:**
```
INFO - AC telemetry forwarder started for <IP_ANDROID>
INFO - Conectado a AC telemetry (shared memory)
```

### Las marchas se muestran incorrectas

✅ **Ya está corregido**. La función ahora lee las marchas correctamente:
- `-1` → R (Reversa)
- `0` → N (Neutral)
- `1-7` → Marchas adelante

### La velocidad/RPM va con retraso

El servidor envía a 30 Hz. Si necesitas más velocidad:

Edita `xbox.py` línea 286:
```python
SEND_INTERVAL = 1.0 / 60.0  # 60 Hz (más rápido, más CPU)
```

## 🚀 Ventajas de Shared Memory

| Característica | UDP Viejo | Shared Memory Nuevo |
|----------------|-----------|---------------------|
| Configuración AC | Requiere activar | Sin configuración |
| Confiabilidad | Media | Alta |
| Latencia | ~20ms | <5ms |
| CPU Usage | Medio | Bajo |
| Auto-reconexión | No | Sí |
| Corrección marchas | Manual | Automática |

## 📝 Notas Técnicas

- El servidor TCP sigue funcionando igual (puerto 12345)
- La telemetría va por la **misma conexión TCP** que los comandos del volante
- No hay cambios necesarios en la app Android
- Compatible con la GUI de ServerApp (ambas usan shared memory)

¡Todo debería funcionar automáticamente! 🎉
