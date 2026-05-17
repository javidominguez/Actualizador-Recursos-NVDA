# -*- coding: utf-8 -*-
# ejemplo_integracion.py
#
# Ejemplos de integración de ActualizadorRecursos en complementos NVDA.
# Desde uso mínimo hasta control total con diálogos de progreso wxPython.
#
# Licencia: GPL v2

# ═══════════════════════════════════════════════════════════════
# EJEMPLO 1: Mínimo — todo por defecto
# ═══════════════════════════════════════════════════════════════
"""
import addonHandler
import globalPluginHandler
addonHandler.initTranslation()
from .actualizadorRecursos import ActualizadorRecursos

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._actualizador = ActualizadorRecursos("mi-usuario", "mi-repo")

	def terminate(self):
		self._actualizador.detener()
		super().terminate()
"""

# ═══════════════════════════════════════════════════════════════
# EJEMPLO 2: Solo manual — sin comprobación automática
# El usuario decide cuándo comprobar (mediante menú o gesto)
# ═══════════════════════════════════════════════════════════════
"""
self._actualizador = ActualizadorRecursos(
	"mi-usuario", "mi-repo",
	modo_comprobacion="manual",  # No comprueba al iniciar ni periódicamente
	notificar_sin_cambios=True,  # Informar cuando no hay novedades
)

# Luego el usuario llama a esto cuando quiera:
# self._actualizador.forzarActualizacion()
"""

# ═══════════════════════════════════════════════════════════════
# EJEMPLO 3: Periódico — comprueba cada N horas en segundo plano
# ═══════════════════════════════════════════════════════════════
"""
self._actualizador = ActualizadorRecursos(
	"mi-usuario", "mi-repo",
	modo_comprobacion="periodico",  # Timer que se repite
	intervalo_horas=12,             # Cada 12 horas
)
"""

# ═══════════════════════════════════════════════════════════════
# EJEMPLO 4: Con diálogo de progreso wxPython (no bloqueante)
# ═══════════════════════════════════════════════════════════════
"""
import wx
import gui

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._dialogo_progreso = None

		self._actualizador = ActualizadorRecursos(
			"mi-usuario", "mi-repo",
			modo_comprobacion="manual",
			callback_progreso=self._alProgreso,
			callback_finalizado=self._alFinalizar,
			callback_error=self._alError,
		)

	def _alProgreso(self, descargados, total, etapa):
		# IMPORTANTE: wx.CallAfter porque esto se llama desde hilo secundario
		if etapa == "descargando" and total > 0:
			porcentaje = int((descargados / total) * 100)
			wx.CallAfter(self._actualizarDialogo, porcentaje, f"Descargando... {porcentaje}%")
		elif etapa == "instalando_idiomas":
			wx.CallAfter(self._actualizarDialogo, -1, "Instalando traducciones...")
		elif etapa == "instalando_docs":
			wx.CallAfter(self._actualizarDialogo, -1, "Instalando documentación...")

	def _alFinalizar(self, exito, resultado):
		wx.CallAfter(self._cerrarDialogo)
		if exito and resultado["instalados"] > 0:
			wx.CallAfter(
				gui.messageBox,
				f"Se actualizaron {resultado['instalados']} archivos.\\n"
				f"Idiomas: {', '.join(resultado['idiomas'])}\\n"
				f"Documentación: {', '.join(resultado['docs'])}",
				"Actualización completada",
				wx.OK | wx.ICON_INFORMATION,
			)

	def _alError(self, excepcion):
		wx.CallAfter(self._cerrarDialogo)
		wx.CallAfter(
			gui.messageBox,
			f"Error: {excepcion}",
			"Error de actualización",
			wx.OK | wx.ICON_ERROR,
		)

	def _mostrarDialogo(self):
		self._dialogo_progreso = wx.ProgressDialog(
			"Actualizando recursos",
			"Preparando...",
			maximum=100,
			parent=gui.mainFrame,
			style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_CAN_ABORT,
		)

	def _actualizarDialogo(self, valor, mensaje):
		if self._dialogo_progreso:
			if valor < 0:
				self._dialogo_progreso.Pulse(mensaje)
			else:
				self._dialogo_progreso.Update(valor, mensaje)

	def _cerrarDialogo(self):
		if self._dialogo_progreso:
			self._dialogo_progreso.Destroy()
			self._dialogo_progreso = None

	def script_actualizarRecursos(self, gesto):
		wx.CallAfter(self._mostrarDialogo)
		self._actualizador.forzarActualizacion()
"""

# ═══════════════════════════════════════════════════════════════
# EJEMPLO 5: Filtros de idioma
# ═══════════════════════════════════════════════════════════════
"""
# Solo actualizar el idioma actual de NVDA (+ inglés como fallback)
ActualizadorRecursos(
	"mi-usuario", "mi-repo",
	solo_idioma_actual=True,
)

# Solo idiomas específicos
ActualizadorRecursos(
	"mi-usuario", "mi-repo",
	idiomas_incluidos=["es", "fr", "pt_BR"],
)

# Todos excepto algunos
ActualizadorRecursos(
	"mi-usuario", "mi-repo",
	idiomas_excluidos=["zh_CN", "zh_TW"],
)
"""

# ═══════════════════════════════════════════════════════════════
# EJEMPLO 6: Repositorio privado + respaldo
# ═══════════════════════════════════════════════════════════════
"""
ActualizadorRecursos(
	"mi-organizacion", "mi-repo-privado",
	token_github="ghp_xxxxxxxxxxxxxxxxxxxx",
	hacer_respaldo=True,
	directorio_respaldo="respaldo_recursos",
)
"""

# ═══════════════════════════════════════════════════════════════
# EJEMPLO 7: Callback de pre-actualización para confirmar
# ═══════════════════════════════════════════════════════════════
"""
import wx, gui

def confirmar_actualizacion():
	# Este callback se ejecuta en hilo secundario,
	# así que usamos wx.CallAfter + Event para esperar
	evento = threading.Event()
	resultado = [False]

	def preguntar():
		r = gui.messageBox(
			"Hay traducciones nuevas disponibles. ¿Desea instalarlas?",
			"Actualización disponible",
			wx.YES_NO | wx.ICON_QUESTION,
		)
		resultado[0] = (r == wx.YES)
		evento.set()

	wx.CallAfter(preguntar)
	evento.wait(timeout=60)
	return resultado[0]

ActualizadorRecursos(
	"mi-usuario", "mi-repo",
	callback_pre_actualizacion=confirmar_actualizacion,
)
"""

# ═══════════════════════════════════════════════════════════════
# EJEMPLO 8: Personalización completa — todas las opciones
# ═══════════════════════════════════════════════════════════════
"""
ActualizadorRecursos(
	"mi-usuario", "mi-repo",

	# GitHub
	rama="main",
	tag_release="recursos-latest",
	timeout_http=15,
	token_github=None,  # o "ghp_xxx" para repos privados

	# Qué actualizar
	actualizar_idiomas=True,
	actualizar_documentacion=True,

	# Rutas
	directorio_idiomas="locale",
	directorio_documentacion="doc",

	# Extensiones
	extensiones_idiomas=[".mo", ".po", ".ini"],
	extensiones_documentacion=[".html", ".md", ".txt", ".css"],

	# Modo
	modo_comprobacion="inicio",  # "inicio", "periodico", "manual"
	intervalo_horas=24,

	# Filtros
	solo_idioma_actual=False,
	idiomas_incluidos=None,   # o ["es", "fr"]
	idiomas_excluidos=None,   # o ["zh_CN"]

	# Respaldo
	hacer_respaldo=True,
	directorio_respaldo="respaldo_recursos",

	# Notificaciones
	notificar_usuario=True,
	notificar_sin_cambios=False,
	mensaje_exito="¡Recursos actualizados!",
	mensaje_sin_cambios="Todo al día.",
	mensaje_error="Error al actualizar.",
	mensaje_comprobando="Buscando actualizaciones...",

	# Callbacks
	callback_progreso=mi_funcion_progreso,        # (descargados, total, etapa)
	callback_finalizado=mi_funcion_finalizado,     # (exito, resultado)
	callback_error=mi_funcion_error,               # (excepcion)
	callback_pre_actualizacion=mi_funcion_confirmar,  # () -> bool

	# Avanzado
	tamaño_bloque_descarga=4096,  # Bloques pequeños = progreso más granular
)
"""

# ═══════════════════════════════════════════════════════════════
# EJEMPLO 9: Integración con menú Herramientas
# ═══════════════════════════════════════════════════════════════
"""
Añade una entrada al menú Herramientas > Actualizar recursos del complemento
con el nombre del complemento. Al hacer clic, muestra un diálogo de progreso
y los resultados de la actualización.

VENTAJAS:
- El usuario puede actualizar manualmente desde el menú
- Diálogos informativos con los resultados
- Manejo automático de errores
- Diálogos bloqueantes (wait for user feedback)

FORMA 1: Usando el parámetro menuHerramientas=True (RECOMENDADO)
==============================================================
El menú se crea automáticamente al instanciar el ActualizadorRecursos:

import addonHandler
import globalPluginHandler
addonHandler.initTranslation()
from .actualizadorRecursos import ActualizadorRecursos

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		# Crear el actualizador con menuHerramientas=True
		# El menú se crea automáticamente
		self._actualizador = ActualizadorRecursos(
			"mi-usuario",
			"mi-repo",
			modo_comprobacion="manual",
			menuHerramientas=True,  # ← ACTIVAR MENÚ AUTOMÁTICAMENTE
		)
	
	def terminate(self):
		self._actualizador.detener()
		super().terminate()


FORMA 2: Llamar manualmente (para casos específicos)
===================================================
Si necesitas crear el menú después de la instanciación:

self._actualizador = ActualizadorRecursos(
	"mi-usuario",
	"mi-repo",
	modo_comprobacion="manual",
)

# Crear el menú manualmente más adelante si es necesario
self._actualizador.integrarMenuHerramientas()


RESULTADO EN EL MENÚ:
=====================
Menú: Herramientas
├─ Actualizar recursos del complemento
│  └─ Nombre del complemento (ejecuta la actualización)
│  └─ Otro complemento (si hay otro)


COMPORTAMIENTO AL HACER CLIC:
=============================
1. Se muestra un diálogo de progreso
2. Durante la descarga se muestra: "Descargando recursos... 25%"
3. Durante la instalación se muestra: "Instalando traducciones..."
4. Al finalizar:
   - Si hay actualizaciones: "Se actualizaron N archivos" + lista de idiomas
   - Si no hay cambios: "Los recursos ya están actualizados"
   - Si hay error: "Error al actualizar recursos: [motivo]"
5. Se sugiere reiniciar NVDA si se instalaron archivos

NOTAS:
======
- Este método SOLO funciona dentro de NVDA (requiere las bibliotecas wx y gui)
- Si se llama fuera de NVDA, se registra un warning y retorna sin hacer nada
- Los callbacks de progreso/finalización se reemplazan durante la actualización
- Se restauran los callbacks originales al terminar
- Si se llama múltiples veces, NO se crean duplicados (verifica que exista)
- Compatible con menuHerramientas=True en el __init__ (no crea duplicados)
"""
