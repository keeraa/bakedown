# BakeDown

[English](README.md) · [Русский](README.ru.md) · **Español** · [Deutsch](README.de.md) · [简体中文](README.zh-CN.md)

**Versión 1.4.0 · Blender 4.5+ · GPL-3.0-or-later**

BakeDown es un complemento de Blender que convierte mallas pesadas generadas por IA o por fotogrametría (Hunyuan, Meshy, Tripo, Rodin, escaneos — a menudo 50k+ polígonos con una sola textura 4K) en **assets listos para juegos**. Simplifica solo la malla activa, hornea texturas PBR del original sobre la malla ligera, genera LOD, transfiere rigs y exporta a Unity, Unreal Engine o glTF.

Funciona con **cualquier malla pesada**, no solo con resultados de IA: escaneos 3D, esculturas, modelos high-poly de tiendas o kitbash y conversiones de CAD.

El flujo es **no destructivo**: el original se guarda como copia de seguridad, puedes probar valores libremente y **Restablecer** lo devuelve todo a su estado.

Autor: **Kirill Migachev**

[![Demo de BakeDown: 49.988 → 2.734 triángulos y horneado de texturas 4K](docs/images/demo_poster.jpg)](docs/media/bakedown_demo.mp4)

▶ **[Ver la demo de 40 segundos](docs/media/bakedown_demo.mp4)**

### El mismo aspecto con un 95 % menos de triángulos

| Figura completa, con texturas | Figura completa, malla |
|---|---|
| ![Figura completa, con texturas](docs/images/compare_full_textured.jpg) | ![Figura completa, malla](docs/images/compare_full_wireframe.jpg) |
| **Primer plano, con texturas** | **Primer plano, malla** |
| ![Primer plano, con texturas](docs/images/compare_closeup_textured.jpg) | ![Primer plano, malla](docs/images/compare_closeup_wireframe.jpg) |

Original (izquierda) frente al resultado de BakeDown (derecha): 49.988 → 2.734 triángulos, distorsión aprox. 7,3 mm (0,56 %), horneado 4K.

## Instalación

1. Descarga `bakedown.py` de la [última versión](https://github.com/keeraa/bakedown/releases/latest).
2. En Blender: **Edit → Preferences → Add-ons → Install from Disk…** y elige `bakedown.py`.
3. Activa **BakeDown — Game Asset Optimizer**.
4. Abre la barra lateral de la vista 3D con **N** y selecciona la pestaña **BakeDown**.

Para actualizar, instala el nuevo `bakedown.py` sobre el anterior y reinicia Blender.

## Flujo de trabajo

Objeto estático (edificio, accesorio):

```text
Simplificar → Hornear → (LOD) → Exportar
```

Personaje:

```text
Simplificar → Hornear → Rig → LOD → Exportar
```

Genera los LOD **después** del rig para que hereden el esqueleto. Si hay varios objetos seleccionados, BakeDown procesa solo la malla activa (la del contorno más claro).

## Funciones

### Simplificación
- Objetivo por número real de triángulos (deslizador + preajustes 1K/3K/5K/10K/20K) o por margen de distorsión aproximado (una búsqueda binaria encuentra el número de triángulos).
- Soldado de vértices, limpieza de geometría suelta, corrección de normales (incluidas las split normals personalizadas de mallas de IA), disolución de caras planas y diezmado Collapse; opcionalmente relleno de agujeros, eliminación de caras interiores, aplanado y triangulación explícita.
- Estimación de distorsión en milímetros y % del tamaño del objeto directamente en el panel.
- Inspección **Forma** (Solid + MatCap + malla de alambre) y **Comparar** original ↔ resultado.

### Horneado de texturas
- Horneado en Cycles de Base Color, Roughness, Metallic y un mapa de normales opcional en espacio tangente sobre un nuevo despliegue UV, a 1K/2K/4K.
- Modal, con progreso y cancelación; reversión completa al cancelar o si hay un error.
- Distancia de rayo automática, intensidad de normales en vivo, nitidez de Base Color.

### LOD
- LOD0–LOD3 con preajustes Estrategia, Shooter 3D, Móvil y Personalizado. Todos los LOD comparten un mismo juego de texturas.
- Compatibles con esqueletos: los LOD de una malla con rig heredan el esqueleto y los pesos.
- Nombres `<objeto>_LOD0..3`, así Unity crea el LOD Group automáticamente.
- Avisa cuando los LOD quedan desactualizados tras una nueva simplificación u horneado, y no permite exportarlos.

### Transferencia de rig
- Importa un FBX con skinning como plantilla y transfiere el esqueleto y los pesos a la malla activa (para humanoides similares).
- Trabaja en Rest Position y restaura el estado de la pose incluso tras un error.

### Exportación
- FBX para Unity, FBX para Unreal (smoothing groups) y GLB autónomo.
- El modelo y las texturas PNG se guardan en una subcarpeta con el nombre del archivo .blend; el FBX referencia los PNG con rutas relativas.
- Opciones: inversión del canal verde del mapa de normales (convención DirectX), empaquetado ORM.
- Exporta un objeto o toda su colección de LOD (con el esqueleto) en un solo archivo.

## Uso con agentes de IA

Los agentes de IA (Claude, ChatGPT, Codex, Blender MCP…) pueden manejar BakeDown en lugar de escribir su propio código para Blender. En las pruebas del autor, un agente que trabajaba con BakeDown obtuvo assets claramente mejores que el mismo agente improvisando scripts de diezmado y horneado.

Dos puntos de entrada; ambos devuelven un informe JSON (triángulos, distorsión, mapas horneados, LOD, archivos exportados):

```bash
blender -b --factory-startup --python tools/bakedown_cli.py -- model.glb --out ./out --triangles 3000 --resolution 2048 --engine unity
```

```python
import bakedown
report = bakedown.process(obj, triangles=3000, resolution=2048, export_dir="/tmp/out", engine="UNITY")
```

Instrucciones completas para agentes: [AGENTS.md](AGENTS.md) (en inglés).

## Idiomas de la interfaz

El idioma original de la interfaz es el inglés. Incluye traducciones al **ruso, español, alemán y chino simplificado**; Blender las muestra automáticamente según su idioma de interfaz (**Preferences → Interface → Translation**).

## Consejos

- El horneado usa Cycles en CPU: de decenas de segundos a un par de minutos por objeto en 4K.
- Manchas negras tras hornear → aumenta la **Distancia de rayo**; detalles finos borrosos → vuelve a 0 (auto).
- La triangulación está desactivada por defecto: los motores triangulan al importar y el coste en GPU es el mismo.
- Para animaciones de Mixamo: haz el rig una vez; las animaciones son FBX separados que se redirigen en Unity con un Humanoid Avatar.

## Limitaciones

- La distorsión es una métrica aproximada por muestreo, no una distancia de Hausdorff exacta.
- Un paso de horneado en curso no se puede interrumpir; la cancelación se aplica entre mapas.
- La detección de caras interiores es experimental y está desactivada por defecto.
- Revisa escalas negativas o no uniformes antes de importar en el motor.

## Desarrollo

Consulta [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) (en inglés) para la arquitectura y [docs/VERIFICATION.md](docs/VERIFICATION.md) para el estado de las pruebas. Pruebas sin interfaz:

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python-exit-code 1 --python tests/run_tests.py
```

## Licencia

GNU General Public License v3.0 o posterior. Consulta [LICENSE](LICENSE).
