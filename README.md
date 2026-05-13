# Sistema de Actualización de Recursos para Complementos NVDA

Sistema reutilizable para actualizar **traducciones** (`.mo` + `.po` + `manifest.ini` traducidos), **documentación** (`.html` generado desde `.md`, `.txt`) y **estilo** (`.css`) de complementos NVDA desde GitHub, sin publicar nueva release. Todo configurable por el desarrollador.

## Archivos

| Archivo | Descripción |
|---|---|
| `actualizadorRecursos.py` | Módulo reutilizable — copiar al complemento |
| `.github/workflows/compilar_idiomas.yml` | Workflow de GitHub Actions |
| `scons_idiomas.py` | Compilación local `.po` → `.mo`, `manifest.ini`, `.md` → `.html` |
| `ejemplo_integracion.py` | 8 ejemplos de uso |

## Qué genera el sistema

El workflow y `scons_idiomas.py` realizan automáticamente:

1. **Compilación de traducciones:** `.po` → `.mo` (usando `msgfmt`)
2. **Generación de `manifest.ini` traducidos:** Usa el `.mo` compilado + `manifest-translated.ini.tpl` + `buildVars.py` para crear el `manifest.ini` en cada `locale/{idioma}/`
3. **Conversión de documentación:** `.md` → `.html` con el formato estándar NVDA (título traducido, CSS, lang)
4. **Copia de readme.md raíz** a `addon/doc/{baseLanguage}/`
5. **Copia de style.css** a `addon/doc/`
6. **Empaquetado:** ZIP con todos los recursos (`.mo`, `.po`, `manifest.ini`, `.html`, `.md`, `.css`)
7. **Metadatos:** `recursos_info.json` con hash combinado para detección de cambios

## Integración rápida

### 1. Copiar `actualizadorRecursos.py` al complemento
```
addon/globalPlugins/miComplemento/actualizadorRecursos.py
```

### 2. Usar en `__init__.py`
```python
import addonHandler, globalPluginHandler
addonHandler.initTranslation()
from .actualizadorRecursos import ActualizadorRecursos

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._actualizador = ActualizadorRecursos("tu-usuario", "tu-repo")

	def terminate(self):
		self._actualizador.detener()
		super().terminate()
```

### 3. Copiar workflow a `.github/workflows/`

Editar las variables `env` del workflow:
- `NOMBRE_COMPLEMENTO` — nombre del addon
- `TAG_RELEASE` — tag de la release (debe coincidir con `tag_release` en Python)

### 4. Requisitos del repositorio

Para que el workflow genere `manifest.ini` y `.html` correctamente, tu repositorio debe contener en la raíz:

| Archivo | Descripción |
|---|---|
| `buildVars.py` | Variables del addon (`addon_info` con summary, description, changelog) |
| `manifest-translated.ini.tpl` | Plantilla del manifest traducido |
| `readme.md` | README del addon (se copia a `addon/doc/{baseLanguage}/`) |
| `style.css` | Hoja de estilos para la documentación HTML |
| `site_scons/` | Herramientas SCons (necesario para que `buildVars.py` importe sus tipos) |

> **Nota:** El workflow usa un mock de SCons para importar `buildVars.py` sin necesitar SCons instalado.

## Uso local con `scons_idiomas.py`

```bash
# Compilar todo (po→mo, manifest.ini, md→html, metadatos)
python scons_idiomas.py

# Solo compilar traducciones (sin HTML)
python scons_idiomas.py --solo-idiomas

# Solo generar documentación HTML (sin compilar .po)
python scons_idiomas.py --solo-docs

# Sin generar manifest.ini traducidos
python scons_idiomas.py --sin-manifest

# Sin generar HTML desde Markdown
python scons_idiomas.py --sin-html

# Directorio personalizado
python scons_idiomas.py -i addon/locale -d addon/doc
```

## Opciones configurables

Todas se pasan como `**kwargs` al constructor.

### GitHub

| Opción | Tipo | Defecto | Descripción |
|---|---|---|---|
| `rama` | str | `"main"` | Rama del repositorio |
| `tag_release` | str | `"recursos-latest"` | Tag de la release de recursos |
| `timeout_http` | int | `30` | Timeout HTTP en segundos |
| `token_github` | str | `None` | Token para repositorios privados |

### Qué actualizar

| Opción | Tipo | Defecto | Descripción |
|---|---|---|---|
| `actualizar_idiomas` | bool | `True` | Actualizar `.mo` + `.po` + `manifest.ini` |
| `actualizar_documentacion` | bool | `True` | Actualizar documentación (`.html`, `.md`, `.css`) |
| `directorio_idiomas` | str | `"locale"` | Ruta de locales (relativa al addon) |
| `directorio_documentacion` | str | `"doc"` | Ruta de docs (relativa al addon) |
| `extensiones_idiomas` | list | `[".mo", ".po", ".ini"]` | Extensiones de idiomas |
| `extensiones_documentacion` | list | `[".html", ".md", ".txt", ".css"]` | Extensiones de docs |

### Modo de comprobación

| Opción | Tipo | Defecto | Descripción |
|---|---|---|---|
| `modo_comprobacion` | str | `"inicio"` | `"inicio"`, `"periodico"` o `"manual"` |
| `intervalo_horas` | int | `24` | Horas entre comprobaciones |

Modos disponibles:
- **`"inicio"`** — Comprueba al cargar el complemento, respetando el intervalo.
- **`"periodico"`** — Timer en segundo plano que comprueba cada `intervalo_horas`.
- **`"manual"`** — Solo cuando el desarrollador llama a `comprobarActualizacion()` o `forzarActualizacion()`.

### Filtros de idioma

| Opción | Tipo | Defecto | Descripción |
|---|---|---|---|
| `solo_idioma_actual` | bool | `False` | Solo actualizar el idioma activo de NVDA + en |
| `idiomas_incluidos` | list | `None` | Lista de códigos a incluir (None = todos) |
| `idiomas_excluidos` | list | `None` | Lista de códigos a excluir |

### Callbacks del desarrollador

| Opción | Firma | Descripción |
|---|---|---|
| `callback_progreso` | `(descargados, total, etapa)` | Progreso de descarga/instalación |
| `callback_finalizado` | `(exito, resultado)` | Al completar (éxito o fallo) |
| `callback_error` | `(excepcion)` | Al ocurrir un error |
| `callback_pre_actualizacion` | `() -> bool` | Confirmar antes de instalar (False cancela) |

> ⚠️ Los callbacks se invocan desde un **hilo secundario**. Usar `wx.CallAfter()` para actualizar la interfaz.

Valores de `etapa` en `callback_progreso`:
- `"comprobando"` — Comprobando si hay actualizaciones
- `"descargando"` — Descargando paquete (con bytes y total)
- `"instalando_idiomas"` — Instalando traducciones
- `"instalando_docs"` — Instalando documentación
- `"instalando"` — Copiando archivos individuales

### Notificaciones

| Opción | Tipo | Defecto | Descripción |
|---|---|---|---|
| `notificar_usuario` | bool | `True` | Mostrar mensaje al actualizar |
| `notificar_sin_cambios` | bool | `False` | Mostrar mensaje si no hay cambios |
| `mensaje_exito` | str | *(texto)* | Mensaje tras actualización exitosa |
| `mensaje_sin_cambios` | str | *(texto)* | Mensaje sin cambios |
| `mensaje_error` | str | *(texto)* | Mensaje de error |
| `mensaje_comprobando` | str | *(texto)* | Mensaje al iniciar |

### Respaldo y avanzado

| Opción | Tipo | Defecto | Descripción |
|---|---|---|---|
| `hacer_respaldo` | bool | `False` | Crear respaldo antes de actualizar |
| `directorio_respaldo` | str | `"respaldo_recursos"` | Directorio de respaldos |
| `tamaño_bloque_descarga` | int | `8192` | Bytes por bloque (menor = progreso más granular) |

## API pública

```python
# Comprobar en segundo plano
actualizador.comprobarActualizacion()

# Forzar (ignora intervalo, ideal para botones/gestos)
actualizador.forzarActualizacion()

# Detener (llamar en terminate())
actualizador.detener()

# Estado actual
estado = actualizador.obtenerEstado()
# → idiomas_instalados, documentacion_instalada, fecha_*, hash_*, configuracion

# Configuración activa
config = actualizador.obtenerConfiguracion()
```

## Configuración del workflow

Variables `env` en el archivo YAML:

| Variable | Descripción |
|---|---|
| `NOMBRE_COMPLEMENTO` | Nombre del complemento |
| `TAG_RELEASE` | Tag de la release (debe coincidir con `tag_release` en Python) |
| `INCLUIR_IDIOMAS` | `"true"` / `"false"` |
| `INCLUIR_DOCUMENTACION` | `"true"` / `"false"` |
| `GENERAR_MANIFEST` | `"true"` / `"false"` — genera `manifest.ini` por idioma |
| `GENERAR_HTML` | `"true"` / `"false"` — convierte `.md` a `.html` |
| `EXTENSIONES_DOC` | Extensiones separadas por espacio (defecto: `.html .md .txt .css`) |

## Estructura del paquete generado

El ZIP `{nombre}_recursos.zip` contiene:

```
├── locale/
│   └── {idioma}/
│       ├── LC_MESSAGES/
│       │   ├── nvda.po        ← fuente de traducción
│       │   └── nvda.mo        ← traducción compilada
│       └── manifest.ini       ← resumen/descripción/changelog traducidos
├── doc/
│   ├── style.css              ← estilos para documentación HTML
│   └── {idioma}/
│       ├── readme.md          ← documentación fuente
│       └── readme.html        ← documentación HTML generada
└── recursos_info.json         ← metadatos y hash para detección de cambios
```

## Licencia

GPL v2 — Compatible con NVDA.
