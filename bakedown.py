# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "BakeDown — Game Asset Optimizer",
    "author": "Kirill Migachev",
    "version": (1, 2, 2),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > BakeDown",
    "description": ("Turn AI-generated and photogrammetry meshes into game-ready assets: "
                    "active-object-only simplification, texture baking, LODs, rig transfer, "
                    "and Unity/Unreal/glTF export."),
    "category": "Mesh",
}

import bpy
import math
import os
import tempfile
import uuid


_TRANSLATIONS = {
    "ru_RU": {
        ("*", "BakeDown — Game Asset Optimizer"): "BakeDown — оптимизация игровых моделей",
        ("*", "Turn AI-generated and photogrammetry meshes into game-ready assets: active-object-only simplification, texture baking, LODs, rig transfer, and Unity/Unreal/glTF export."): "Преобразует AI- и фотограмметрические меши в игровые ассеты: упрощение только активного объекта, запекание текстур, LOD, перенос рига и экспорт в Unity/Unreal/glTF.",
        ("*", "Target triangles"): "Целевые треугольники",
        ("*", "How many real render triangles to keep after simplification. Game guidelines: hero prop 10–20k, building 3–8k, small prop 0.5–2k, distant background 0.1–0.5k."): "Сколько реальных треугольников рендера оставить после упрощения. Ориентиры: hero-объект 10–20k, здание 3–8k, мелкий декор 0.5–2k, дальний фон 0.1–0.5k.",
        ("*", "Target mode"): "Режим цели",
        ("*", "By triangles"): "По треугольникам",
        ("*", "Set the target triangle count manually"): "Задать число треугольников вручную",
        ("*", "By distortion"): "По искажению",
        ("*", "Choose a distortion budget and let BakeDown find the triangle count"): "Задать бюджет искажения — число треугольников подберётся автоматически",
        ("*", "Distortion budget %"): "Бюджет искажения %",
        ("*", "Maximum approximate bidirectional deviation. BakeDown searches for the most aggressive simplification that stays within this budget."): "Максимальное приблизительное двустороннее отклонение. BakeDown ищет самое агрессивное упрощение, которое укладывается в этот бюджет.",
        ("*", "Flatten near-planar surfaces"): "Выравнивать плоскости",
        ("*", "Project vertices of near-planar faces onto a plane. Useful for walls and floors; inspect complex corners afterwards."): "Проецировать вершины почти плоских граней на плоскость. Полезно для стен и полов; после обработки проверьте сложные углы.",
        ("*", "Simplify"): "Упростить",
        ("*", "Simplification"): "Упрощение",
        ("*", "Rig"): "Риг",
        ("*", "LOD"): "LOD",
        ("*", "Simplify → texture → export"): "Упрощение → текстура → экспорт",
        ("*", "Transfer an armature and vertex weights from a template"): "Перенести скелет и веса с шаблона",
        ("*", "Generate LOD0–LOD3"): "Сгенерировать LOD0–LOD3",
        ("*", "Preview"): "Превью",
        ("*", "Preset"): "Пресет",
        ("*", "Close camera, gentle reduction"): "Близкая камера, мягкое упрощение",
        ("*", "Isometric/strategy camera, aggressive reduction"): "Изометрия/стратегия, агрессивное упрощение",
        ("*", "Maximum reduction for mobile"): "Максимальная экономия для мобильных устройств",
        ("*", "Custom values"): "Свои значения",
        ("*", "Generate LOD1"): "Генерировать LOD1",
        ("*", "Generate LOD2"): "Генерировать LOD2",
        ("*", "Generate LOD3"): "Генерировать LOD3",
        ("*", "LOD1 triangles as a percentage of LOD0"): "Треугольники LOD1 в % от LOD0",
        ("*", "LOD2 triangles as a percentage of LOD0"): "Треугольники LOD2 в % от LOD0",
        ("*", "LOD3 triangles as a percentage of LOD0"): "Треугольники LOD3 в % от LOD0",
        ("*", "Dissolve angle"): "Угол Dissolve",
        ("*", "Merge near-planar faces before collapse"): "Сливать плоские грани до коллапса",
        ("*", "Final Limited Dissolve"): "Финальный Limited Dissolve",
        ("*", "Fill holes"): "Заполнять дыры",
        ("*", "Remove interior faces"): "Удалять внутренние грани",
        ("*", "Triangulate output"): "Триангулировать результат",
        ("*", "Resolution"): "Разрешение",
        ("*", "Bake a normal map"): "Запекать карту нормалей",
        ("*", "Normal strength"): "Сила рельефа",
        ("*", "Ray distance (0 = auto)"): "Дистанция луча (0 = авто)",
        ("*", "Sharpen"): "Резкость",
        ("*", "Settings"): "Настройка",
        ("*", "Rig template"): "Риг-шаблон",
        ("*", "Active object only"): "Только активный объект",
        ("*", "Only the active mesh will be processed; other selected objects remain unchanged."): "Будет обработан только активный меш; остальные выделенные объекты не изменятся.",
        ("*", "No active mesh"): "Нет активного меша",
        ("*", "Simplified to {:,} triangles"): "Упрощено до {:,} треугольников",
        ("*", "Reset"): "Сброс",
        ("*", "Restore the active object from its BakeDown backup"): "Восстановить активный объект из резервной копии BakeDown",
        ("*", "No backup is available"): "Резервной копии нет",
        ("*", "Original restored"): "Оригинал восстановлен",
        ("*", "Inspect shape"): "Осмотр формы",
        ("*", "Toggle Solid + MatCap + wireframe inspection"): "Переключить Solid + MatCap + каркас для оценки формы",
        ("*", "No 3D viewport"): "Нет 3D-вьюпорта",
        ("*", "Delete backup"): "Удалить резервную копию",
        ("*", "Release the original mesh backup after you are satisfied with the result"): "Освободить резервную копию оригинала после окончательной проверки результата",
        ("*", "Backup released"): "Резервная копия освобождена",
        ("*", "Bake textures"): "Перенести текстуру",
        ("*", "Bake Base Color, Roughness, Metallic and Normal from the original onto the simplified active mesh"): "Перенести Base Color, Roughness, Metallic и Normal с оригинала на упрощённый активный меш",
        ("*", "No backup — run Simplify first"): "Нет резервной копии — сначала выполните «Упростить»",
        ("*", "Base Color"): "Цвет",
        ("*", "Roughness"): "Шероховатость",
        ("*", "Normals"): "Нормали",
        ("*", "Metallic"): "Металличность",
        ("*", "Packing"): "Сохранение",
        ("*", "Preparing"): "Подготовка",
        ("*", "Bake failed: {}"): "Запекание завершилось ошибкой: {}",
        ("*", "Bake cancelled"): "Запекание отменено",
        ("*", "Bake complete"): "Запекание завершено",
        ("*", "Approximate distortion"): "Приблизительное искажение",
        ("*", "Approximate bidirectional surface deviation, sampled in both directions. Use it as a guide and inspect the shape visually."): "Приблизительное двустороннее отклонение поверхности с выборкой в обоих направлениях. Используйте как ориентир и проверяйте форму визуально.",
        ("*", "Cancel bake"): "Отменить запекание",
        ("*", "Export"): "Экспорт",
        ("*", "Export the active BakeDown object or its own LOD collection"): "Экспортировать активный объект BakeDown или его собственную LOD-коллекцию",
        ("*", "Engine"): "Движок",
        ("*", "Unity FBX"): "Unity FBX",
        ("*", "Unreal FBX"): "Unreal FBX",
        ("*", "Self-contained GLB"): "Самодостаточный GLB",
        ("*", "Save textures as PNG"): "Сохранить текстуры как PNG",
        ("*", "Flip normal-map green channel"): "Инвертировать зелёный канал normal map",
        ("*", "Pack ORM (R=AO, G=Roughness, B=Metallic)"): "Собрать ORM (R=AO, G=Roughness, B=Metallic)",
        ("*", "Export failed: {}"): "Экспорт завершился ошибкой: {}",
        ("*", "Exported to {}"): "Экспортировано в {}",
        ("*", "Compare with original"): "Сравнить с оригиналом",
        ("*", "Toggle the original mesh and the simplified result"): "Переключить оригинальный меш и упрощённый результат",
        ("*", "Generate LODs"): "Сгенерировать LOD",
        ("*", "Generate LOD0–LOD3 from the active BakeDown object"): "Сгенерировать LOD0–LOD3 из активного объекта BakeDown",
        ("*", "Import rig template"): "Загрузить риг из файла",
        ("*", "Import a skinned FBX and use it as the rig template"): "Импортировать заригованный FBX и использовать его как риг-шаблон",
        ("*", "An FBX file is required"): "Нужен файл FBX",
        ("*", "Import failed: {}"): "Импорт завершился ошибкой: {}",
        ("*", "No skinned mesh was found in the FBX"): "В FBX не найден заскиненный меш",
        ("*", "Template loaded: {}"): "Шаблон загружен: {}",
        ("*", "Transfer rig"): "Перенести риг",
        ("*", "Transfer armature and weights from the template to the active mesh"): "Перенести скелет и веса с шаблона на активный меш",
        ("*", "Select a rigged mesh template"): "Укажите заригованный меш-шаблон",
        ("*", "No armature was found on the template"): "У шаблона не найден скелет",
        ("*", "Weight transfer failed: {}"): "Перенос весов завершился ошибкой: {}",
        ("*", "Rig transferred from {} "): "Риг перенесён с {} ",
        ("*", "Original"): "Оригинал",
        ("*", "Approx. distortion: {:.1f} mm ({:.2f}%)"): "Оценка искажения: {:.1f} мм ({:.2f}%)",
        ("*", "Rig transfer from template"): "Перенос рига с шаблона",
        ("*", "Template"): "Шаблон",
        ("*", "Total in file: ~{:,} triangles"): "Итого в файле: ~{:,} треугольников",
        ("*", "Generate LOD"): "Сгенерировать LOD",
        ("*", "Run Simplify and Bake Textures first"): "Сначала выполните «Упростить» и «Перенести текстуру»",
        ("*", "Run Simplify first"): "Сначала выполните «Упростить»",
        ("*", "Export LODs"): "Экспорт LOD",
        ("*", "Triangles: {:,} → {:,} (−{:.0f}%)"): "Треугольники: {:,} → {:,} (−{:.0f}%)",
        ("*", "Triangles: {:,}"): "Треугольники: {:,}",
        ("*", "Select a mesh object"): "Выделите меш-объект",
        ("*", "1 — Simplify geometry"): "1 — Упростить геометрию",
        ("*", "Object"): "Объект",
        ("*", "Shape"): "Форма",
        ("*", "2 — Texture"): "2 — Текстура",
        ("*", "Cancel"): "Отменить",
        ("*", "Compare"): "Сравнить",
        ("*", "Hide comparison"): "Убрать сравнение",
        ("*", "Bake"): "Текстурировать",
        ("*", "The export folder is not writable"): "Папка экспорта недоступна для записи",
        ("*", "No baked textures were found; exporting geometry only"): "Запечённые текстуры не найдены; будет экспортирована только геометрия",
        ("*", "Negative scale detected; apply scale before engine import if shading is incorrect"): "Обнаружен отрицательный масштаб; примените масштаб, если в движке нарушится освещение",
        ("*", "Non-uniform scale detected; consider applying scale before export"): "Обнаружен неравномерный масштаб; рекомендуется применить масштаб перед экспортом",
        ("*", "More than one armature is attached to the export set"): "К экспортируемому набору привязано несколько скелетов",
        ("*", "Required exporter is unavailable"): "Необходимый экспортёр недоступен",
    }
}

_TRANSLATIONS["ru_RU"].update({
    ("*", "Interface"): "Интерфейс",
    ("*", "Custom"): "Свой",
    ("*", "Angle threshold for merging near-planar faces. Higher values are more aggressive and may smooth small details."): "Порог угла для слияния почти плоских граней. Большие значения работают агрессивнее и могут сгладить мелкие детали.",
    ("*", "Merge near-planar faces before the collapse decimation pass"): "Слить почти плоские грани до прохода Collapse Decimate.",
    ("*", "Run one more planar cleanup pass after collapse"): "Выполнить ещё один проход очистки плоских участков после Collapse.",
    ("*", "Close holes after simplification; intentional openings may also be filled"): "Закрыть отверстия после упрощения; намеренные проёмы тоже могут быть заполнены.",
    ("*", "Use Blender's interior-face detector before simplification. Review the result because complex meshes may be misclassified."): "Использовать детектор внутренних граней Blender до упрощения. Проверяйте результат: сложные меши могут быть распознаны неверно.",
    ("*", "Convert the final mesh to explicit triangles. Triangle statistics are always calculated from the render triangulation, even when this is off."): "Преобразовать финальный меш в явные треугольники. Статистика всегда считается по рендер-триангуляции, даже когда опция выключена.",
    ("*", "1024×1024 textures for small or distant assets"): "Текстуры 1024×1024 для мелких или дальних объектов.",
    ("*", "2048×2048 textures for medium assets"): "Текстуры 2048×2048 для средних объектов.",
    ("*", "4096×4096 textures for hero assets"): "Текстуры 4096×4096 для крупных hero-объектов.",
    ("*", "Resolution of Base Color, Roughness, Metallic and Normal maps"): "Разрешение карт Base Color, Roughness, Metallic и Normal.",
    ("*", "Restore high-poly surface detail with a tangent-space normal map"): "Вернуть детали high-poly поверхности через tangent-space normal map.",
    ("*", "Live normal-map strength; changing it does not require another bake"): "Сила normal map меняется вживую и не требует повторного запекания.",
    ("*", "Selected-to-active ray distance in local mesh units. Use 0 for automatic distance; increase only if the bake has missed areas."): "Дистанция луча Selected to Active в локальных единицах меша. Оставьте 0 для автоматики; увеличивайте только при пропусках запекания.",
    ("*", "Unsharp-mask amount applied to the baked Base Color map"): "Сила повышения резкости запечённой карты Base Color.",
    ("*", "Show advanced simplification settings"): "Показать дополнительные настройки упрощения.",
    ("*", "Show advanced baking settings"): "Показать дополнительные настройки запекания.",
    ("*", "Skinned template mesh that provides its armature and vertex weights"): "Заскиненный меш-шаблон, из которого переносятся скелет и веса вершин.",
    ("*", "Simplify only the active mesh to the target triangle count. The first run stores a non-destructive backup."): "Упростить только активный меш до целевого числа треугольников. Первый запуск создаёт недеструктивную резервную копию.",
    ("*", "Cancel the current bake"): "Отменить текущее запекание.",
    ("*", "Save baked maps next to the exported model"): "Сохранить запечённые карты рядом с экспортированной моделью.",
    ("*", "Convert the normal map to the DirectX green-channel convention"): "Преобразовать normal map в DirectX-конвенцию зелёного канала.",
    ("*", "Create an Occlusion/Roughness/Metallic packed texture"): "Создать упакованную текстуру Occlusion/Roughness/Metallic.",
    ("*", "Unity FBX"): "FBX для Unity",
    ("*", "Unreal FBX"): "FBX для Unreal Engine",
    ("*", "Select one active mesh"): "Выберите один активный меш",
    ("*", "LODs are out of date: regenerate them after Simplify or Bake"): "LOD устарели: сгенерируйте их заново после «Упростить» или «Текстурировать»",
    ("*", "LODs were created by an older BakeDown version; regenerate them if the base mesh or textures changed"): "LOD созданы старой версией BakeDown; сгенерируйте их заново, если меш или текстуры менялись",
    ("*", "LODs are out of date — regenerate"): "LOD устарели — сгенерируйте заново",
})

_TRANSLATIONS["ru_RU"].update({
    ("*", "Strategy"): "Стратегия",
    ("*", "3D Shooter"): "3D-шутер",
    ("*", "Mobile"): "Мобильные",
})

# Spanish ---------------------------------------------------------------------
_ES = {
    "BakeDown — Game Asset Optimizer": "BakeDown — optimizador de assets para juegos",
    "Turn AI-generated and photogrammetry meshes into game-ready assets: active-object-only simplification, texture baking, LODs, rig transfer, and Unity/Unreal/glTF export.": "Convierte mallas generadas por IA y de fotogrametría en assets listos para juegos: simplificación solo del objeto activo, horneado de texturas, LOD, transferencia de rig y exportación a Unity/Unreal/glTF.",
    "Target triangles": "Triángulos objetivo",
    "How many real render triangles to keep after simplification. Game guidelines: hero prop 10–20k, building 3–8k, small prop 0.5–2k, distant background 0.1–0.5k.": "Cuántos triángulos reales de render conservar tras la simplificación. Referencias: objeto principal 10–20k, edificio 3–8k, objeto pequeño 0.5–2k, fondo lejano 0.1–0.5k.",
    "Target mode": "Modo de objetivo",
    "By triangles": "Por triángulos",
    "Set the target triangle count manually": "Definir manualmente el número de triángulos",
    "By distortion": "Por distorsión",
    "Choose a distortion budget and let BakeDown find the triangle count": "Elige un margen de distorsión y BakeDown encontrará el número de triángulos",
    "Distortion budget %": "Margen de distorsión %",
    "Maximum approximate bidirectional deviation. BakeDown searches for the most aggressive simplification that stays within this budget.": "Desviación bidireccional aproximada máxima. BakeDown busca la simplificación más agresiva que se mantenga dentro de este margen.",
    "Flatten near-planar surfaces": "Aplanar superficies casi planas",
    "Project vertices of near-planar faces onto a plane. Useful for walls and floors; inspect complex corners afterwards.": "Proyecta los vértices de caras casi planas sobre un plano. Útil para paredes y suelos; revisa después las esquinas complejas.",
    "Simplify": "Simplificar",
    "Simplification": "Simplificación",
    "Rig": "Rig",
    "LOD": "LOD",
    "Simplify → texture → export": "Simplificar → textura → exportar",
    "Transfer an armature and vertex weights from a template": "Transferir esqueleto y pesos de vértices desde una plantilla",
    "Generate LOD0–LOD3": "Generar LOD0–LOD3",
    "Preview": "Vista previa",
    "Preset": "Preajuste",
    "Close camera, gentle reduction": "Cámara cercana, reducción suave",
    "Isometric/strategy camera, aggressive reduction": "Cámara isométrica/estrategia, reducción agresiva",
    "Maximum reduction for mobile": "Reducción máxima para móviles",
    "Custom values": "Valores personalizados",
    "Generate LOD1": "Generar LOD1",
    "Generate LOD2": "Generar LOD2",
    "Generate LOD3": "Generar LOD3",
    "LOD1 triangles as a percentage of LOD0": "Triángulos de LOD1 en % de LOD0",
    "LOD2 triangles as a percentage of LOD0": "Triángulos de LOD2 en % de LOD0",
    "LOD3 triangles as a percentage of LOD0": "Triángulos de LOD3 en % de LOD0",
    "Dissolve angle": "Ángulo de disolución",
    "Merge near-planar faces before collapse": "Fusionar caras casi planas antes del colapso",
    "Final Limited Dissolve": "Limited Dissolve final",
    "Fill holes": "Rellenar agujeros",
    "Remove interior faces": "Eliminar caras interiores",
    "Triangulate output": "Triangular el resultado",
    "Resolution": "Resolución",
    "Bake a normal map": "Hornear mapa de normales",
    "Normal strength": "Intensidad de normales",
    "Ray distance (0 = auto)": "Distancia de rayo (0 = auto)",
    "Sharpen": "Nitidez",
    "Settings": "Ajustes",
    "Rig template": "Plantilla de rig",
    "Active object only": "Solo el objeto activo",
    "Only the active mesh will be processed; other selected objects remain unchanged.": "Solo se procesará la malla activa; los demás objetos seleccionados no cambiarán.",
    "No active mesh": "No hay malla activa",
    "Simplified to {:,} triangles": "Simplificado a {:,} triángulos",
    "Reset": "Restablecer",
    "Restore the active object from its BakeDown backup": "Restaurar el objeto activo desde su copia de seguridad de BakeDown",
    "No backup is available": "No hay copia de seguridad",
    "Original restored": "Original restaurado",
    "Inspect shape": "Inspeccionar forma",
    "Toggle Solid + MatCap + wireframe inspection": "Alternar inspección Solid + MatCap + malla de alambre",
    "No 3D viewport": "No hay vista 3D",
    "Delete backup": "Eliminar copia de seguridad",
    "Release the original mesh backup after you are satisfied with the result": "Liberar la copia de la malla original cuando estés conforme con el resultado",
    "Backup released": "Copia de seguridad liberada",
    "Bake textures": "Hornear texturas",
    "Bake Base Color, Roughness, Metallic and Normal from the original onto the simplified active mesh": "Hornear Base Color, Roughness, Metallic y Normal del original sobre la malla activa simplificada",
    "No backup — run Simplify first": "Sin copia de seguridad: ejecuta primero Simplificar",
    "Base Color": "Color base",
    "Roughness": "Rugosidad",
    "Normals": "Normales",
    "Metallic": "Metálico",
    "Packing": "Empaquetando",
    "Preparing": "Preparando",
    "Bake failed: {}": "Error al hornear: {}",
    "Bake cancelled": "Horneado cancelado",
    "Bake complete": "Horneado completado",
    "Approximate distortion": "Distorsión aproximada",
    "Approximate bidirectional surface deviation, sampled in both directions. Use it as a guide and inspect the shape visually.": "Desviación aproximada de la superficie, muestreada en ambas direcciones. Úsala como guía e inspecciona la forma visualmente.",
    "Cancel bake": "Cancelar horneado",
    "Export": "Exportar",
    "Export the active BakeDown object or its own LOD collection": "Exportar el objeto activo de BakeDown o su propia colección de LOD",
    "Engine": "Motor",
    "Unity FBX": "FBX para Unity",
    "Unreal FBX": "FBX para Unreal Engine",
    "Self-contained GLB": "GLB autónomo",
    "Save textures as PNG": "Guardar texturas como PNG",
    "Flip normal-map green channel": "Invertir canal verde del mapa de normales",
    "Pack ORM (R=AO, G=Roughness, B=Metallic)": "Empaquetar ORM (R=AO, G=Roughness, B=Metallic)",
    "Export failed: {}": "Error al exportar: {}",
    "Exported to {}": "Exportado a {}",
    "Compare with original": "Comparar con el original",
    "Toggle the original mesh and the simplified result": "Alternar entre la malla original y el resultado simplificado",
    "Generate LODs": "Generar LOD",
    "Generate LOD0–LOD3 from the active BakeDown object": "Generar LOD0–LOD3 a partir del objeto activo de BakeDown",
    "Import rig template": "Importar plantilla de rig",
    "Import a skinned FBX and use it as the rig template": "Importar un FBX con skinning y usarlo como plantilla de rig",
    "An FBX file is required": "Se requiere un archivo FBX",
    "Import failed: {}": "Error al importar: {}",
    "No skinned mesh was found in the FBX": "No se encontró ninguna malla con skinning en el FBX",
    "Template loaded: {}": "Plantilla cargada: {}",
    "Transfer rig": "Transferir rig",
    "Transfer armature and weights from the template to the active mesh": "Transferir esqueleto y pesos de la plantilla a la malla activa",
    "Select a rigged mesh template": "Selecciona una plantilla de malla con rig",
    "No armature was found on the template": "No se encontró esqueleto en la plantilla",
    "Weight transfer failed: {}": "Error al transferir pesos: {}",
    "Rig transferred from {} ": "Rig transferido desde {} ",
    "Original": "Original",
    "Approx. distortion: {:.1f} mm ({:.2f}%)": "Distorsión aprox.: {:.1f} mm ({:.2f}%)",
    "Rig transfer from template": "Transferencia de rig desde plantilla",
    "Template": "Plantilla",
    "Total in file: ~{:,} triangles": "Total en el archivo: ~{:,} triángulos",
    "Generate LOD": "Generar LOD",
    "Run Simplify and Bake Textures first": "Ejecuta primero Simplificar y Hornear texturas",
    "Run Simplify first": "Ejecuta primero Simplificar",
    "Export LODs": "Exportar LOD",
    "Triangles: {:,} → {:,} (−{:.0f}%)": "Triángulos: {:,} → {:,} (−{:.0f}%)",
    "Triangles: {:,}": "Triángulos: {:,}",
    "Select a mesh object": "Selecciona un objeto de malla",
    "1 — Simplify geometry": "1 — Simplificar geometría",
    "Object": "Objeto",
    "Shape": "Forma",
    "2 — Texture": "2 — Textura",
    "Cancel": "Cancelar",
    "Compare": "Comparar",
    "Hide comparison": "Ocultar comparación",
    "Bake": "Hornear",
    "The export folder is not writable": "No se puede escribir en la carpeta de exportación",
    "No baked textures were found; exporting geometry only": "No se encontraron texturas horneadas; se exporta solo la geometría",
    "Negative scale detected; apply scale before engine import if shading is incorrect": "Escala negativa detectada; aplica la escala si el sombreado es incorrecto en el motor",
    "Non-uniform scale detected; consider applying scale before export": "Escala no uniforme detectada; considera aplicar la escala antes de exportar",
    "More than one armature is attached to the export set": "Hay más de un esqueleto vinculado al conjunto exportado",
    "Required exporter is unavailable": "El exportador necesario no está disponible",
    "Interface": "Interfaz",
    "Custom": "Personalizado",
    "Angle threshold for merging near-planar faces. Higher values are more aggressive and may smooth small details.": "Umbral de ángulo para fusionar caras casi planas. Valores altos son más agresivos y pueden suavizar detalles pequeños.",
    "Merge near-planar faces before the collapse decimation pass": "Fusionar caras casi planas antes del paso de diezmado Collapse",
    "Run one more planar cleanup pass after collapse": "Ejecutar otra pasada de limpieza de zonas planas tras el colapso",
    "Close holes after simplification; intentional openings may also be filled": "Cerrar agujeros tras la simplificación; también pueden rellenarse aberturas intencionadas",
    "Use Blender's interior-face detector before simplification. Review the result because complex meshes may be misclassified.": "Usar el detector de caras interiores de Blender antes de simplificar. Revisa el resultado: las mallas complejas pueden clasificarse mal.",
    "Convert the final mesh to explicit triangles. Triangle statistics are always calculated from the render triangulation, even when this is off.": "Convertir la malla final en triángulos explícitos. Las estadísticas siempre se calculan con la triangulación de render, aunque esté desactivado.",
    "1024×1024 textures for small or distant assets": "Texturas de 1024×1024 para objetos pequeños o lejanos",
    "2048×2048 textures for medium assets": "Texturas de 2048×2048 para objetos medianos",
    "4096×4096 textures for hero assets": "Texturas de 4096×4096 para objetos principales",
    "Resolution of Base Color, Roughness, Metallic and Normal maps": "Resolución de los mapas Base Color, Roughness, Metallic y Normal",
    "Restore high-poly surface detail with a tangent-space normal map": "Recuperar el detalle de la superficie high-poly con un mapa de normales en espacio tangente",
    "Live normal-map strength; changing it does not require another bake": "Intensidad del mapa de normales en vivo; cambiarla no requiere volver a hornear",
    "Selected-to-active ray distance in local mesh units. Use 0 for automatic distance; increase only if the bake has missed areas.": "Distancia de rayo Selected to Active en unidades locales de la malla. Usa 0 para distancia automática; auméntala solo si el horneado tiene zonas sin cubrir.",
    "Unsharp-mask amount applied to the baked Base Color map": "Intensidad de la máscara de enfoque aplicada al mapa Base Color horneado",
    "Show advanced simplification settings": "Mostrar ajustes avanzados de simplificación",
    "Show advanced baking settings": "Mostrar ajustes avanzados de horneado",
    "Skinned template mesh that provides its armature and vertex weights": "Malla plantilla con skinning que aporta su esqueleto y pesos de vértices",
    "Simplify only the active mesh to the target triangle count. The first run stores a non-destructive backup.": "Simplificar solo la malla activa al número de triángulos objetivo. La primera ejecución guarda una copia de seguridad no destructiva.",
    "Cancel the current bake": "Cancelar el horneado actual",
    "Save baked maps next to the exported model": "Guardar los mapas horneados junto al modelo exportado",
    "Convert the normal map to the DirectX green-channel convention": "Convertir el mapa de normales a la convención de canal verde de DirectX",
    "Create an Occlusion/Roughness/Metallic packed texture": "Crear una textura empaquetada Occlusion/Roughness/Metallic",
    "Select one active mesh": "Selecciona una malla activa",
    "LODs are out of date: regenerate them after Simplify or Bake": "Los LOD están desactualizados: vuelve a generarlos tras Simplificar u Hornear",
    "LODs were created by an older BakeDown version; regenerate them if the base mesh or textures changed": "Los LOD se crearon con una versión anterior de BakeDown; vuelve a generarlos si cambió la malla base o las texturas",
    "LODs are out of date — regenerate": "LOD desactualizados — vuelve a generarlos",
    "Strategy": "Estrategia",
    "3D Shooter": "Shooter 3D",
    "Mobile": "Móvil",
}

# German ----------------------------------------------------------------------
_DE = {
    "BakeDown — Game Asset Optimizer": "BakeDown — Game-Asset-Optimierer",
    "Turn AI-generated and photogrammetry meshes into game-ready assets: active-object-only simplification, texture baking, LODs, rig transfer, and Unity/Unreal/glTF export.": "Macht KI-generierte und Photogrammetrie-Meshes spielfertig: Vereinfachung nur des aktiven Objekts, Textur-Baking, LODs, Rig-Übertragung und Export nach Unity/Unreal/glTF.",
    "Target triangles": "Ziel-Dreiecke",
    "How many real render triangles to keep after simplification. Game guidelines: hero prop 10–20k, building 3–8k, small prop 0.5–2k, distant background 0.1–0.5k.": "Wie viele echte Render-Dreiecke nach der Vereinfachung bleiben. Richtwerte: Hero-Objekt 10–20k, Gebäude 3–8k, kleines Objekt 0.5–2k, ferner Hintergrund 0.1–0.5k.",
    "Target mode": "Zielmodus",
    "By triangles": "Nach Dreiecken",
    "Set the target triangle count manually": "Dreiecksanzahl manuell festlegen",
    "By distortion": "Nach Verzerrung",
    "Choose a distortion budget and let BakeDown find the triangle count": "Verzerrungsbudget wählen – BakeDown ermittelt die Dreiecksanzahl",
    "Distortion budget %": "Verzerrungsbudget %",
    "Maximum approximate bidirectional deviation. BakeDown searches for the most aggressive simplification that stays within this budget.": "Maximale ungefähre beidseitige Abweichung. BakeDown sucht die stärkste Vereinfachung, die innerhalb dieses Budgets bleibt.",
    "Flatten near-planar surfaces": "Fast ebene Flächen begradigen",
    "Project vertices of near-planar faces onto a plane. Useful for walls and floors; inspect complex corners afterwards.": "Vertices fast ebener Flächen auf eine Ebene projizieren. Nützlich für Wände und Böden; komplexe Ecken danach prüfen.",
    "Simplify": "Vereinfachen",
    "Simplification": "Vereinfachung",
    "Rig": "Rig",
    "LOD": "LOD",
    "Simplify → texture → export": "Vereinfachen → Textur → Export",
    "Transfer an armature and vertex weights from a template": "Skelett und Vertex-Gewichte von einer Vorlage übertragen",
    "Generate LOD0–LOD3": "LOD0–LOD3 erzeugen",
    "Preview": "Vorschau",
    "Preset": "Voreinstellung",
    "Close camera, gentle reduction": "Nahe Kamera, sanfte Reduktion",
    "Isometric/strategy camera, aggressive reduction": "Isometrische/Strategie-Kamera, starke Reduktion",
    "Maximum reduction for mobile": "Maximale Reduktion für Mobilgeräte",
    "Custom values": "Eigene Werte",
    "Generate LOD1": "LOD1 erzeugen",
    "Generate LOD2": "LOD2 erzeugen",
    "Generate LOD3": "LOD3 erzeugen",
    "LOD1 triangles as a percentage of LOD0": "LOD1-Dreiecke in % von LOD0",
    "LOD2 triangles as a percentage of LOD0": "LOD2-Dreiecke in % von LOD0",
    "LOD3 triangles as a percentage of LOD0": "LOD3-Dreiecke in % von LOD0",
    "Dissolve angle": "Dissolve-Winkel",
    "Merge near-planar faces before collapse": "Fast ebene Flächen vor dem Collapse zusammenführen",
    "Final Limited Dissolve": "Abschließendes Limited Dissolve",
    "Fill holes": "Löcher füllen",
    "Remove interior faces": "Innenflächen entfernen",
    "Triangulate output": "Ergebnis triangulieren",
    "Resolution": "Auflösung",
    "Bake a normal map": "Normal Map backen",
    "Normal strength": "Normal-Stärke",
    "Ray distance (0 = auto)": "Strahldistanz (0 = auto)",
    "Sharpen": "Schärfen",
    "Settings": "Einstellungen",
    "Rig template": "Rig-Vorlage",
    "Active object only": "Nur aktives Objekt",
    "Only the active mesh will be processed; other selected objects remain unchanged.": "Nur das aktive Mesh wird bearbeitet; andere ausgewählte Objekte bleiben unverändert.",
    "No active mesh": "Kein aktives Mesh",
    "Simplified to {:,} triangles": "Auf {:,} Dreiecke vereinfacht",
    "Reset": "Zurücksetzen",
    "Restore the active object from its BakeDown backup": "Aktives Objekt aus seiner BakeDown-Sicherung wiederherstellen",
    "No backup is available": "Keine Sicherung vorhanden",
    "Original restored": "Original wiederhergestellt",
    "Inspect shape": "Form prüfen",
    "Toggle Solid + MatCap + wireframe inspection": "Prüfansicht Solid + MatCap + Drahtgitter umschalten",
    "No 3D viewport": "Kein 3D-Viewport",
    "Delete backup": "Sicherung löschen",
    "Release the original mesh backup after you are satisfied with the result": "Sicherung des Original-Meshes freigeben, wenn das Ergebnis passt",
    "Backup released": "Sicherung freigegeben",
    "Bake textures": "Texturen backen",
    "Bake Base Color, Roughness, Metallic and Normal from the original onto the simplified active mesh": "Base Color, Roughness, Metallic und Normal vom Original auf das vereinfachte aktive Mesh backen",
    "No backup — run Simplify first": "Keine Sicherung – zuerst Vereinfachen ausführen",
    "Base Color": "Grundfarbe",
    "Roughness": "Rauheit",
    "Normals": "Normalen",
    "Metallic": "Metallisch",
    "Packing": "Packen",
    "Preparing": "Vorbereitung",
    "Bake failed: {}": "Backen fehlgeschlagen: {}",
    "Bake cancelled": "Backen abgebrochen",
    "Bake complete": "Backen abgeschlossen",
    "Approximate distortion": "Ungefähre Verzerrung",
    "Approximate bidirectional surface deviation, sampled in both directions. Use it as a guide and inspect the shape visually.": "Ungefähre Oberflächenabweichung, in beide Richtungen abgetastet. Als Richtwert nutzen und die Form visuell prüfen.",
    "Cancel bake": "Backen abbrechen",
    "Export": "Exportieren",
    "Export the active BakeDown object or its own LOD collection": "Aktives BakeDown-Objekt oder seine eigene LOD-Collection exportieren",
    "Engine": "Engine",
    "Unity FBX": "FBX für Unity",
    "Unreal FBX": "FBX für Unreal Engine",
    "Self-contained GLB": "Eigenständiges GLB",
    "Save textures as PNG": "Texturen als PNG speichern",
    "Flip normal-map green channel": "Grünkanal der Normal Map invertieren",
    "Pack ORM (R=AO, G=Roughness, B=Metallic)": "ORM packen (R=AO, G=Roughness, B=Metallic)",
    "Export failed: {}": "Export fehlgeschlagen: {}",
    "Exported to {}": "Exportiert nach {}",
    "Compare with original": "Mit Original vergleichen",
    "Toggle the original mesh and the simplified result": "Zwischen Original-Mesh und vereinfachtem Ergebnis umschalten",
    "Generate LODs": "LODs erzeugen",
    "Generate LOD0–LOD3 from the active BakeDown object": "LOD0–LOD3 aus dem aktiven BakeDown-Objekt erzeugen",
    "Import rig template": "Rig-Vorlage importieren",
    "Import a skinned FBX and use it as the rig template": "Geskinntes FBX importieren und als Rig-Vorlage verwenden",
    "An FBX file is required": "Eine FBX-Datei ist erforderlich",
    "Import failed: {}": "Import fehlgeschlagen: {}",
    "No skinned mesh was found in the FBX": "Im FBX wurde kein geskinntes Mesh gefunden",
    "Template loaded: {}": "Vorlage geladen: {}",
    "Transfer rig": "Rig übertragen",
    "Transfer armature and weights from the template to the active mesh": "Skelett und Gewichte von der Vorlage auf das aktive Mesh übertragen",
    "Select a rigged mesh template": "Geriggte Mesh-Vorlage auswählen",
    "No armature was found on the template": "An der Vorlage wurde kein Skelett gefunden",
    "Weight transfer failed: {}": "Gewichtsübertragung fehlgeschlagen: {}",
    "Rig transferred from {} ": "Rig übertragen von {} ",
    "Original": "Original",
    "Approx. distortion: {:.1f} mm ({:.2f}%)": "Ca. Verzerrung: {:.1f} mm ({:.2f}%)",
    "Rig transfer from template": "Rig-Übertragung von Vorlage",
    "Template": "Vorlage",
    "Total in file: ~{:,} triangles": "Gesamt in Datei: ~{:,} Dreiecke",
    "Generate LOD": "LOD erzeugen",
    "Run Simplify and Bake Textures first": "Zuerst Vereinfachen und Texturen backen ausführen",
    "Run Simplify first": "Zuerst Vereinfachen ausführen",
    "Export LODs": "LODs exportieren",
    "Triangles: {:,} → {:,} (−{:.0f}%)": "Dreiecke: {:,} → {:,} (−{:.0f}%)",
    "Triangles: {:,}": "Dreiecke: {:,}",
    "Select a mesh object": "Mesh-Objekt auswählen",
    "1 — Simplify geometry": "1 — Geometrie vereinfachen",
    "Object": "Objekt",
    "Shape": "Form",
    "2 — Texture": "2 — Textur",
    "Cancel": "Abbrechen",
    "Compare": "Vergleichen",
    "Hide comparison": "Vergleich ausblenden",
    "Bake": "Backen",
    "The export folder is not writable": "Der Exportordner ist nicht beschreibbar",
    "No baked textures were found; exporting geometry only": "Keine gebackenen Texturen gefunden; nur Geometrie wird exportiert",
    "Negative scale detected; apply scale before engine import if shading is incorrect": "Negative Skalierung erkannt; Skalierung anwenden, falls die Schattierung in der Engine falsch ist",
    "Non-uniform scale detected; consider applying scale before export": "Ungleichmäßige Skalierung erkannt; Skalierung vor dem Export anwenden empfohlen",
    "More than one armature is attached to the export set": "Mehr als ein Skelett gehört zum Export-Set",
    "Required exporter is unavailable": "Benötigter Exporter ist nicht verfügbar",
    "Interface": "Oberfläche",
    "Custom": "Eigene",
    "Angle threshold for merging near-planar faces. Higher values are more aggressive and may smooth small details.": "Winkelschwelle zum Zusammenführen fast ebener Flächen. Höhere Werte sind aggressiver und können kleine Details glätten.",
    "Merge near-planar faces before the collapse decimation pass": "Fast ebene Flächen vor dem Collapse-Decimate-Durchgang zusammenführen",
    "Run one more planar cleanup pass after collapse": "Nach dem Collapse einen weiteren Bereinigungsdurchgang für ebene Bereiche ausführen",
    "Close holes after simplification; intentional openings may also be filled": "Löcher nach der Vereinfachung schließen; gewollte Öffnungen können ebenfalls gefüllt werden",
    "Use Blender's interior-face detector before simplification. Review the result because complex meshes may be misclassified.": "Blenders Innenflächen-Erkennung vor der Vereinfachung nutzen. Ergebnis prüfen: komplexe Meshes können falsch erkannt werden.",
    "Convert the final mesh to explicit triangles. Triangle statistics are always calculated from the render triangulation, even when this is off.": "Endgültiges Mesh in explizite Dreiecke umwandeln. Die Statistik nutzt immer die Render-Triangulierung, auch wenn dies aus ist.",
    "1024×1024 textures for small or distant assets": "1024×1024-Texturen für kleine oder ferne Objekte",
    "2048×2048 textures for medium assets": "2048×2048-Texturen für mittlere Objekte",
    "4096×4096 textures for hero assets": "4096×4096-Texturen für Hero-Objekte",
    "Resolution of Base Color, Roughness, Metallic and Normal maps": "Auflösung der Maps Base Color, Roughness, Metallic und Normal",
    "Restore high-poly surface detail with a tangent-space normal map": "High-Poly-Oberflächendetails mit einer Tangent-Space-Normal-Map erhalten",
    "Live normal-map strength; changing it does not require another bake": "Live-Stärke der Normal Map; eine Änderung erfordert kein neues Backen",
    "Selected-to-active ray distance in local mesh units. Use 0 for automatic distance; increase only if the bake has missed areas.": "Selected-to-Active-Strahldistanz in lokalen Mesh-Einheiten. 0 für automatische Distanz; nur erhöhen, wenn beim Backen Bereiche fehlen.",
    "Unsharp-mask amount applied to the baked Base Color map": "Stärke der Unschärfemaske auf der gebackenen Base-Color-Map",
    "Show advanced simplification settings": "Erweiterte Vereinfachungseinstellungen anzeigen",
    "Show advanced baking settings": "Erweiterte Backeinstellungen anzeigen",
    "Skinned template mesh that provides its armature and vertex weights": "Geskinntes Vorlagen-Mesh, das Skelett und Vertex-Gewichte liefert",
    "Simplify only the active mesh to the target triangle count. The first run stores a non-destructive backup.": "Nur das aktive Mesh auf die Ziel-Dreiecksanzahl vereinfachen. Der erste Durchlauf legt eine nicht-destruktive Sicherung an.",
    "Cancel the current bake": "Aktuelles Backen abbrechen",
    "Save baked maps next to the exported model": "Gebackene Maps neben dem exportierten Modell speichern",
    "Convert the normal map to the DirectX green-channel convention": "Normal Map in die DirectX-Grünkanal-Konvention umwandeln",
    "Create an Occlusion/Roughness/Metallic packed texture": "Gepackte Occlusion/Roughness/Metallic-Textur erstellen",
    "Select one active mesh": "Ein aktives Mesh auswählen",
    "LODs are out of date: regenerate them after Simplify or Bake": "LODs sind veraltet: nach Vereinfachen oder Backen neu erzeugen",
    "LODs were created by an older BakeDown version; regenerate them if the base mesh or textures changed": "LODs stammen von einer älteren BakeDown-Version; neu erzeugen, falls sich Basis-Mesh oder Texturen geändert haben",
    "LODs are out of date — regenerate": "LODs veraltet — neu erzeugen",
    "Strategy": "Strategie",
    "3D Shooter": "3D-Shooter",
    "Mobile": "Mobil",
}

# Simplified Chinese ----------------------------------------------------------
_ZH = {
    "BakeDown — Game Asset Optimizer": "BakeDown — 游戏资产优化器",
    "Turn AI-generated and photogrammetry meshes into game-ready assets: active-object-only simplification, texture baking, LODs, rig transfer, and Unity/Unreal/glTF export.": "将 AI 生成和摄影测量网格转换为可用于游戏的资产：仅简化活动物体、烘焙纹理、生成 LOD、迁移骨骼绑定，并导出到 Unity/Unreal/glTF。",
    "Target triangles": "目标三角面数",
    "How many real render triangles to keep after simplification. Game guidelines: hero prop 10–20k, building 3–8k, small prop 0.5–2k, distant background 0.1–0.5k.": "简化后保留的实际渲染三角面数。参考：主角道具 10–20k，建筑 3–8k，小道具 0.5–2k，远景 0.1–0.5k。",
    "Target mode": "目标模式",
    "By triangles": "按三角面数",
    "Set the target triangle count manually": "手动设置目标三角面数",
    "By distortion": "按形变",
    "Choose a distortion budget and let BakeDown find the triangle count": "设定形变预算，由 BakeDown 自动确定三角面数",
    "Distortion budget %": "形变预算 %",
    "Maximum approximate bidirectional deviation. BakeDown searches for the most aggressive simplification that stays within this budget.": "最大近似双向偏差。BakeDown 会寻找不超出此预算的最大程度简化。",
    "Flatten near-planar surfaces": "压平近似平面",
    "Project vertices of near-planar faces onto a plane. Useful for walls and floors; inspect complex corners afterwards.": "将近似平面的顶点投影到平面上。适用于墙面和地面；之后请检查复杂的转角。",
    "Simplify": "简化",
    "Simplification": "简化",
    "Rig": "绑定",
    "LOD": "LOD",
    "Simplify → texture → export": "简化 → 纹理 → 导出",
    "Transfer an armature and vertex weights from a template": "从模板迁移骨架和顶点权重",
    "Generate LOD0–LOD3": "生成 LOD0–LOD3",
    "Preview": "预览",
    "Preset": "预设",
    "Close camera, gentle reduction": "近景镜头，温和简化",
    "Isometric/strategy camera, aggressive reduction": "等距/策略视角，大幅简化",
    "Maximum reduction for mobile": "面向移动端的最大简化",
    "Custom values": "自定义数值",
    "Generate LOD1": "生成 LOD1",
    "Generate LOD2": "生成 LOD2",
    "Generate LOD3": "生成 LOD3",
    "LOD1 triangles as a percentage of LOD0": "LOD1 三角面数占 LOD0 的百分比",
    "LOD2 triangles as a percentage of LOD0": "LOD2 三角面数占 LOD0 的百分比",
    "LOD3 triangles as a percentage of LOD0": "LOD3 三角面数占 LOD0 的百分比",
    "Dissolve angle": "融并角度",
    "Merge near-planar faces before collapse": "塌陷前合并近似平面",
    "Final Limited Dissolve": "最终有限融并",
    "Fill holes": "填充孔洞",
    "Remove interior faces": "删除内部面",
    "Triangulate output": "三角化结果",
    "Resolution": "分辨率",
    "Bake a normal map": "烘焙法线贴图",
    "Normal strength": "法线强度",
    "Ray distance (0 = auto)": "射线距离（0 = 自动）",
    "Sharpen": "锐化",
    "Settings": "设置",
    "Rig template": "绑定模板",
    "Active object only": "仅活动物体",
    "Only the active mesh will be processed; other selected objects remain unchanged.": "只处理活动网格；其他选中的物体保持不变。",
    "No active mesh": "没有活动网格",
    "Simplified to {:,} triangles": "已简化至 {:,} 个三角面",
    "Reset": "重置",
    "Restore the active object from its BakeDown backup": "从 BakeDown 备份恢复活动物体",
    "No backup is available": "没有可用的备份",
    "Original restored": "已恢复原始模型",
    "Inspect shape": "检查形状",
    "Toggle Solid + MatCap + wireframe inspection": "切换 实体 + MatCap + 线框 检查视图",
    "No 3D viewport": "没有 3D 视图",
    "Delete backup": "删除备份",
    "Release the original mesh backup after you are satisfied with the result": "确认结果满意后释放原始网格备份",
    "Backup released": "备份已释放",
    "Bake textures": "烘焙纹理",
    "Bake Base Color, Roughness, Metallic and Normal from the original onto the simplified active mesh": "将原始模型的基础色、糙度、金属度和法线烘焙到简化后的活动网格上",
    "No backup — run Simplify first": "没有备份 — 请先执行“简化”",
    "Base Color": "基础色",
    "Roughness": "糙度",
    "Normals": "法线",
    "Metallic": "金属度",
    "Packing": "打包",
    "Preparing": "准备中",
    "Bake failed: {}": "烘焙失败：{}",
    "Bake cancelled": "烘焙已取消",
    "Bake complete": "烘焙完成",
    "Approximate distortion": "近似形变",
    "Approximate bidirectional surface deviation, sampled in both directions. Use it as a guide and inspect the shape visually.": "双向采样得到的近似表面偏差。仅供参考，请目视检查形状。",
    "Cancel bake": "取消烘焙",
    "Export": "导出",
    "Export the active BakeDown object or its own LOD collection": "导出活动的 BakeDown 物体或其 LOD 集合",
    "Engine": "引擎",
    "Unity FBX": "Unity 用 FBX",
    "Unreal FBX": "Unreal Engine 用 FBX",
    "Self-contained GLB": "独立 GLB",
    "Save textures as PNG": "将纹理保存为 PNG",
    "Flip normal-map green channel": "翻转法线贴图绿色通道",
    "Pack ORM (R=AO, G=Roughness, B=Metallic)": "打包 ORM（R=AO，G=糙度，B=金属度）",
    "Export failed: {}": "导出失败：{}",
    "Exported to {}": "已导出到 {}",
    "Compare with original": "与原始模型对比",
    "Toggle the original mesh and the simplified result": "在原始网格和简化结果之间切换",
    "Generate LODs": "生成 LOD",
    "Generate LOD0–LOD3 from the active BakeDown object": "从活动的 BakeDown 物体生成 LOD0–LOD3",
    "Import rig template": "导入绑定模板",
    "Import a skinned FBX and use it as the rig template": "导入带蒙皮的 FBX 并用作绑定模板",
    "An FBX file is required": "需要 FBX 文件",
    "Import failed: {}": "导入失败：{}",
    "No skinned mesh was found in the FBX": "FBX 中未找到带蒙皮的网格",
    "Template loaded: {}": "模板已加载：{}",
    "Transfer rig": "迁移绑定",
    "Transfer armature and weights from the template to the active mesh": "将模板的骨架和权重迁移到活动网格",
    "Select a rigged mesh template": "请选择已绑定的网格模板",
    "No armature was found on the template": "模板上未找到骨架",
    "Weight transfer failed: {}": "权重迁移失败：{}",
    "Rig transferred from {} ": "已从 {} 迁移绑定 ",
    "Original": "原始",
    "Approx. distortion: {:.1f} mm ({:.2f}%)": "近似形变：{:.1f} mm（{:.2f}%）",
    "Rig transfer from template": "从模板迁移绑定",
    "Template": "模板",
    "Total in file: ~{:,} triangles": "文件合计：约 {:,} 个三角面",
    "Generate LOD": "生成 LOD",
    "Run Simplify and Bake Textures first": "请先执行“简化”和“烘焙纹理”",
    "Run Simplify first": "请先执行“简化”",
    "Export LODs": "导出 LOD",
    "Triangles: {:,} → {:,} (−{:.0f}%)": "三角面：{:,} → {:,}（−{:.0f}%）",
    "Triangles: {:,}": "三角面：{:,}",
    "Select a mesh object": "请选择网格物体",
    "1 — Simplify geometry": "1 — 简化几何体",
    "Object": "物体",
    "Shape": "形状",
    "2 — Texture": "2 — 纹理",
    "Cancel": "取消",
    "Compare": "对比",
    "Hide comparison": "隐藏对比",
    "Bake": "烘焙",
    "The export folder is not writable": "导出文件夹不可写",
    "No baked textures were found; exporting geometry only": "未找到烘焙纹理；仅导出几何体",
    "Negative scale detected; apply scale before engine import if shading is incorrect": "检测到负缩放；若引擎中着色异常，请先应用缩放",
    "Non-uniform scale detected; consider applying scale before export": "检测到非等比缩放；建议导出前应用缩放",
    "More than one armature is attached to the export set": "导出集合关联了多个骨架",
    "Required exporter is unavailable": "所需的导出器不可用",
    "Interface": "界面",
    "Custom": "自定义",
    "Angle threshold for merging near-planar faces. Higher values are more aggressive and may smooth small details.": "合并近似平面的角度阈值。数值越大简化越激进，可能抹平细小细节。",
    "Merge near-planar faces before the collapse decimation pass": "在塌陷精简之前合并近似平面",
    "Run one more planar cleanup pass after collapse": "塌陷后再执行一次平面清理",
    "Close holes after simplification; intentional openings may also be filled": "简化后封闭孔洞；有意保留的开口也可能被填充",
    "Use Blender's interior-face detector before simplification. Review the result because complex meshes may be misclassified.": "简化前使用 Blender 的内部面检测。请检查结果：复杂网格可能被误判。",
    "Convert the final mesh to explicit triangles. Triangle statistics are always calculated from the render triangulation, even when this is off.": "将最终网格转换为显式三角面。即使关闭此项，统计也始终按渲染三角化计算。",
    "1024×1024 textures for small or distant assets": "1024×1024 纹理，适用于小型或远处物体",
    "2048×2048 textures for medium assets": "2048×2048 纹理，适用于中型物体",
    "4096×4096 textures for hero assets": "4096×4096 纹理，适用于主角物体",
    "Resolution of Base Color, Roughness, Metallic and Normal maps": "基础色、糙度、金属度和法线贴图的分辨率",
    "Restore high-poly surface detail with a tangent-space normal map": "用切线空间法线贴图还原高模表面细节",
    "Live normal-map strength; changing it does not require another bake": "实时法线强度；修改后无需重新烘焙",
    "Selected-to-active ray distance in local mesh units. Use 0 for automatic distance; increase only if the bake has missed areas.": "“选中到活动”烘焙的射线距离，单位为网格局部单位。0 为自动；仅在烘焙出现缺失区域时增大。",
    "Unsharp-mask amount applied to the baked Base Color map": "对烘焙的基础色贴图应用的 USM 锐化强度",
    "Show advanced simplification settings": "显示高级简化设置",
    "Show advanced baking settings": "显示高级烘焙设置",
    "Skinned template mesh that provides its armature and vertex weights": "提供骨架和顶点权重的带蒙皮模板网格",
    "Simplify only the active mesh to the target triangle count. The first run stores a non-destructive backup.": "仅将活动网格简化到目标三角面数。首次运行会保存非破坏性备份。",
    "Cancel the current bake": "取消当前烘焙",
    "Save baked maps next to the exported model": "将烘焙贴图保存在导出模型旁",
    "Convert the normal map to the DirectX green-channel convention": "将法线贴图转换为 DirectX 绿色通道约定",
    "Create an Occlusion/Roughness/Metallic packed texture": "创建 遮蔽/糙度/金属度 打包纹理",
    "Select one active mesh": "请选择一个活动网格",
    "LODs are out of date: regenerate them after Simplify or Bake": "LOD 已过期：执行“简化”或“烘焙”后请重新生成",
    "LODs were created by an older BakeDown version; regenerate them if the base mesh or textures changed": "LOD 由旧版 BakeDown 创建；如基础网格或纹理有变动，请重新生成",
    "LODs are out of date — regenerate": "LOD 已过期 — 请重新生成",
    "Strategy": "策略",
    "3D Shooter": "3D 射击",
    "Mobile": "移动端",
}

_TRANSLATIONS["es"] = {("*", k): v for k, v in _ES.items()}
_TRANSLATIONS["de_DE"] = {("*", k): v for k, v in _DE.items()}
_TRANSLATIONS["zh_HANS"] = {("*", k): v for k, v in _ZH.items()}
_TRANSLATIONS["zh_CN"] = dict(_TRANSLATIONS["zh_HANS"])   # Blender < 4.0 locale name


def _tr(text):
    return bpy.app.translations.pgettext_iface(text)


def _triangle_count_mesh(mesh):
    """Return the real render-triangle count, including triangulated n-gons."""
    if mesh is None:
        return 0
    try:
        mesh.calc_loop_triangles()
        return len(mesh.loop_triangles)
    except Exception:
        return sum(max(0, len(poly.vertices) - 2) for poly in mesh.polygons)


def _triangle_count_object(obj):
    return _triangle_count_mesh(obj.data) if obj and obj.type == 'MESH' else 0


def _capture_selection_state(context):
    active = context.view_layer.objects.active
    return {
        "selected": [obj.name for obj in context.selected_objects],
        "active": active.name if active else None,
        "mode": active.mode if active else 'OBJECT',
    }


def _activate_only(context, obj):
    """Guarantee that operators affect only the active mesh, never all selected meshes."""
    if obj is None:
        return
    try:
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
    except Exception:
        pass
    for other in context.view_layer.objects:
        try:
            other.select_set(False)
        except Exception:
            pass
    try:
        obj.hide_set(False)
        obj.select_set(True)
        context.view_layer.objects.active = obj
    except Exception:
        pass


def _restore_selection_state(context, state, fallback=None):
    try:
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
    except Exception:
        pass
    for obj in context.view_layer.objects:
        try:
            obj.select_set(False)
        except Exception:
            pass
    active = bpy.data.objects.get(state.get("active") or "") if state else None
    for name in (state.get("selected", []) if state else []):
        obj = bpy.data.objects.get(name)
        if obj is not None and obj.name in context.view_layer.objects:
            try:
                obj.select_set(True)
            except Exception:
                pass
    if active is None:
        active = fallback
    if active is not None and active.name in context.view_layer.objects:
        try:
            active.select_set(True)
            context.view_layer.objects.active = active
        except Exception:
            pass
    mode = state.get("mode", 'OBJECT') if state else 'OBJECT'
    if active is not None and mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode=mode)
        except Exception:
            pass


def _capture_bakedown_props(obj):
    """Capture all BakeDown custom properties so failed operations can restore them."""
    if obj is None:
        return {}
    return {key: obj[key] for key in obj.keys() if key.startswith("bakedown_")}


def _restore_bakedown_props(obj, state):
    if obj is None:
        return
    for key in [key for key in obj.keys() if key.startswith("bakedown_")]:
        try:
            del obj[key]
        except Exception:
            pass
    for key, value in (state or {}).items():
        try:
            obj[key] = value
        except Exception:
            pass


def _comparison_object_for(obj):
    """Return the comparison object associated with this result (or the object itself)."""
    if obj is None:
        return None
    if obj.get("bakedown_compare"):
        return obj
    for candidate in bpy.data.objects:
        if (candidate.get("bakedown_compare")
                and candidate.get("bakedown_result") == obj.name):
            return candidate
    return None


def _base_object(obj):
    if obj is None:
        return None
    base_name = obj.get("bakedown_lod_of")
    return bpy.data.objects.get(base_name) if base_name else obj


def _baked_image(obj, suffix):
    base = _base_object(obj)
    if base is None:
        return None
    custom_name = base.get(f"bakedown_image_{suffix}")
    return bpy.data.images.get(custom_name) if custom_name else bpy.data.images.get(f"{base.name}_{suffix}")


def _capture_viewport_state(context):
    state = []
    screen = getattr(context, "screen", None)
    if screen is None:
        return state
    for area in screen.areas:
        if area.type != 'VIEW_3D':
            continue
        space = area.spaces.active
        state.append((area.as_pointer(), space.shading.type, space.shading.light,
                      space.overlay.show_wireframes))
    return state


def _restore_viewport_state(context, state):
    screen = getattr(context, "screen", None)
    if screen is None:
        return
    by_pointer = {area.as_pointer(): area for area in screen.areas if area.type == 'VIEW_3D'}
    for pointer, shading_type, light, wireframes in state or []:
        area = by_pointer.get(pointer)
        if area is None:
            continue
        space = area.spaces.active
        try:
            space.shading.type = shading_type
            space.shading.light = light
            space.overlay.show_wireframes = wireframes
        except Exception:
            pass


def _capture_render_state(scene):
    bake = scene.render.bake
    state = {
        "engine": scene.render.engine,
        "bake": {},
        "cycles": {},
    }
    for attr in (
        "use_selected_to_active", "use_clear", "use_cage", "cage_extrusion",
        "max_ray_distance", "margin", "use_pass_direct", "use_pass_indirect",
        "use_pass_color",
    ):
        if hasattr(bake, attr):
            state["bake"][attr] = getattr(bake, attr)
    cycles = getattr(scene, "cycles", None)
    if cycles is not None:
        for attr in ("device", "samples"):
            if hasattr(cycles, attr):
                state["cycles"][attr] = getattr(cycles, attr)
    return state


def _restore_render_state(scene, state):
    if not state:
        return
    try:
        scene.render.engine = state.get("engine", scene.render.engine)
    except Exception:
        pass
    bake = scene.render.bake
    for attr, value in state.get("bake", {}).items():
        try:
            setattr(bake, attr, value)
        except Exception:
            pass
    cycles = getattr(scene, "cycles", None)
    if cycles is not None:
        for attr, value in state.get("cycles", {}).items():
            try:
                setattr(cycles, attr, value)
            except Exception:
                pass


def _safe_name(value):
    cleaned = "".join(c if c.isalnum() or c in "-_. " else "_" for c in value).strip()
    return cleaned or "BakeDownAsset"


def _armatures_for_objects(objects):
    arms = set()
    for obj in objects:
        if obj is None:
            continue
        if obj.type == 'ARMATURE':
            arms.add(obj)
        if obj.parent is not None and obj.parent.type == 'ARMATURE':
            arms.add(obj.parent)
        for mod in obj.modifiers:
            if mod.type == 'ARMATURE' and mod.object is not None:
                arms.add(mod.object)
    return arms


# ---------------------------------------------------------------------------
# Original-mesh backup (non-destructive workflow)
# ---------------------------------------------------------------------------
def _get_backup(o):
    key = o.get("bakedown_orig_mesh")
    return bpy.data.meshes.get(key) if key else None


def _ensure_backup(o):
    bk = _get_backup(o)
    if bk is None:
        bk = o.data.copy()
        bk.name = f"BakeDownOrig_{o.name}"
        bk.use_fake_user = True
        o["bakedown_orig_mesh"] = bk.name
    return bk


def _restore_from_backup(o):
    bk = _get_backup(o)
    if bk is None:
        return False
    old = o.data
    o.data = bk.copy()
    o.data.name = f"{o.name}_work"
    if old.users == 0 and old is not bk:
        bpy.data.meshes.remove(old)
    return True


def _screen_areas(context):
    screen = getattr(context, "screen", None)
    return getattr(screen, "areas", ()) if screen is not None else ()


def _redraw_ui(context):
    for area in _screen_areas(context):
        if area.type == 'VIEW_3D':
            area.tag_redraw()


def _exit_inspect(context):
    """Leave the "Inspect shape" mode (show materials again)."""
    for area in _screen_areas(context):
        if area.type != 'VIEW_3D':
            continue
        sp = area.spaces.active
        if (sp.shading.type == 'SOLID' and sp.shading.light == 'MATCAP'
                and sp.overlay.show_wireframes):
            sp.shading.type = 'MATERIAL'
            sp.overlay.show_wireframes = False


def _enter_inspect(context):
    """Enter the "Shape" mode (Solid + MatCap + wireframe) to judge geometry."""
    for area in _screen_areas(context):
        if area.type != 'VIEW_3D':
            continue
        sp = area.spaces.active
        sp.shading.type = 'SOLID'
        sp.shading.light = 'MATCAP'
        sp.overlay.show_wireframes = True


def _bbox_diag_for_mesh(mesh, matrix_world):
    if mesh is None or not mesh.vertices:
        return 0.0
    mn = [min(v.co[i] for v in mesh.vertices) for i in range(3)]
    mx = [max(v.co[i] for v in mesh.vertices) for i in range(3)]
    scale = matrix_world.to_scale()
    return math.sqrt(sum(((mx[i] - mn[i]) * abs(scale[i])) ** 2 for i in range(3)))


def _bbox_diag(ob):
    return _bbox_diag_for_mesh(ob.data, ob.matrix_world) if ob and ob.type == 'MESH' else 0.0


def _bake_ray(lo, pg):
    """Ray/cage distance for baking. A manual value (>0) is used as is; otherwise AUTO.

    IMPORTANT: bake cage_extrusion / max_ray_distance are in the mesh's LOCAL coordinates,
    not world space. AI imports often have scale 0.01 (the mesh is huge locally), so the
    size is measured from RAW vertex coordinates (without world scale). Otherwise the
    automatic distance ends up ~1/scale times too small on such objects → black misses."""
    if pg.bake_extrusion > 0.0:
        return pg.bake_extrusion, pg.bake_extrusion * 3.0
    vs = lo.data.vertices
    if vs:
        mn = [min(v.co[i] for v in vs) for i in range(3)]
        mx = [max(v.co[i] for v in vs) for i in range(3)]
        d = math.sqrt(sum((mx[i] - mn[i]) ** 2 for i in range(3)))
    else:
        d = 1.0
    extrusion = max(0.0005, 0.006 * d)   # ~0.6% of the local size
    raydist = extrusion * 3.0
    return extrusion, raydist


def _sample_mesh_points(mesh, matrix_world, max_vertices=700, max_faces=500):
    """Sample vertices and polygon centers in world space without copying a heavy mesh."""
    points = []
    nv = len(mesh.vertices)
    if nv:
        step = max(1, nv // max_vertices)
        for i in range(0, nv, step):
            points.append(matrix_world @ mesh.vertices[i].co)
    nf = len(mesh.polygons)
    if nf:
        step = max(1, nf // max_faces)
        for i in range(0, nf, step):
            points.append(matrix_world @ mesh.polygons[i].center)
    return points


def _mesh_bvh_world(mesh, matrix_world):
    from mathutils.bvhtree import BVHTree
    if mesh is None or not mesh.vertices or not mesh.polygons:
        raise ValueError("Mesh has no surface geometry")
    verts = [matrix_world @ v.co for v in mesh.vertices]
    polys = [tuple(p.vertices) for p in mesh.polygons]
    return BVHTree.FromPolygons(verts, polys, all_triangles=False)


def _max_distance_to_tree(points, tree):
    if not points:
        raise ValueError("No surface samples")
    max_dist = 0.0
    hits = 0
    for point in points:
        hit, _normal, _index, distance = tree.find_nearest(point)
        if hit is not None and distance is not None:
            max_dist = max(max_dist, distance)
            hits += 1
    if hits == 0:
        raise ValueError("No nearest-surface hits")
    return max_dist


def _clear_distortion_state(o):
    for key in ("bakedown_distort_mm", "bakedown_distort_pct",
                "bakedown_distort_forward_mm", "bakedown_distort_reverse_mm",
                "bakedown_distort_method"):
        if key in o:
            del o[key]


def _measure_distortion(context, o):
    """Approximate symmetric surface deviation, sampled in both directions."""
    _clear_distortion_state(o)
    bk = _get_backup(o)
    if bk is None or o.data is None:
        return False
    try:
        mw = o.matrix_world.copy()
        original_tree = _mesh_bvh_world(bk, mw)
        result_tree = _mesh_bvh_world(o.data, mw)
        result_to_original = _max_distance_to_tree(
            _sample_mesh_points(o.data, mw), original_tree)
        original_to_result = _max_distance_to_tree(
            _sample_mesh_points(bk, mw), result_tree)
        max_distance = max(result_to_original, original_to_result)
        diag = max(_bbox_diag_for_mesh(bk, mw), _bbox_diag_for_mesh(o.data, mw))
        unit_scale = getattr(context.scene.unit_settings, "scale_length", 1.0) or 1.0
        mm_factor = unit_scale * 1000.0
        o["bakedown_distort_mm"] = max_distance * mm_factor
        o["bakedown_distort_pct"] = (max_distance / diag * 100.0) if diag else 0.0
        o["bakedown_distort_forward_mm"] = result_to_original * mm_factor
        o["bakedown_distort_reverse_mm"] = original_to_result * mm_factor
        o["bakedown_distort_method"] = "bidirectional_sampled_v3"
        return True
    except Exception as exc:
        print(f"BakeDown distortion measurement failed: {exc}")
        return False


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
def _update_normal_strength(self, context):
    o = _base_object(context.active_object)
    if not o:
        return
    mat_name = o.get("bakedown_material_name") or f"{o.name}_Baked"
    mat = bpy.data.materials.get(mat_name)
    if mat and mat.use_nodes:
        for n in mat.node_tree.nodes:
            if n.type == 'NORMAL_MAP':
                n.inputs['Strength'].default_value = self.bake_normal_strength


def _lod_base_name(o):
    if o is None:
        return None
    return o.get("bakedown_lod_of") or o.name


def _lod_source_sig(base):
    """Geometry + bake state of the base object that LODs were generated from."""
    return "|".join([
        str(base.get("bakedown_geo_version", 0)),
        str(base.get("bakedown_baked_sig", "")),
        str(base.get("bakedown_material_name", "")),
    ])


def _lod_state(base, lods):
    """'OK', 'STALE' (base re-simplified or re-baked after LOD generation) or
    'UNKNOWN' (LODs from a version that did not record the source signature)."""
    if base is None or not lods:
        return 'OK'
    sigs = [ob.get("bakedown_lod_src_sig") for ob in lods]
    if any(sig is None for sig in sigs):
        return 'UNKNOWN'
    current = _lod_source_sig(base)
    return 'OK' if all(sig == current for sig in sigs) else 'STALE'


def _not_lod(context):
    """True if the active object is a regular mesh and NOT a generated LOD.
    Simplifying/baking generated LODs makes no sense, so it is blocked."""
    o = context.active_object
    return bool(o and o.type == 'MESH' and not o.get("bakedown_lod_of")
                and not o.get("bakedown_compare"))


def _update_lod_preview(self, context):
    """Show only the selected LOD in the viewport and make it active."""
    o = context.active_object
    base = _lod_base_name(o)
    if not base:
        return
    coll = bpy.data.collections.get(f"{base}_LODs")
    if coll is None:
        return
    sel = self.lod_preview
    shown = None
    for ob in coll.objects:
        level = ob.get("bakedown_lod_level")
        if not level:
            level = next((name for name in ("LOD0", "LOD1", "LOD2", "LOD3")
                          if ob.name.endswith("_" + name)), None)
        show = level == sel
        ob.hide_set(not show)
        ob.select_set(False)
        if show:
            shown = ob
    src = bpy.data.objects.get(base)
    if src is not None and src not in list(coll.objects):
        src.hide_set(True)                # the source duplicates LOD0 — always hide it
    # make the shown LOD active + selected so work can continue on it
    if shown is not None:
        shown.select_set(True)
        context.view_layer.objects.active = shown


_lod_syncing = False


def _update_lod_preset(self, context):
    """Genre presets for LOD levels."""
    global _lod_syncing
    if _lod_syncing:
        return
    presets = {'STRATEGY': (50.0, 25.0, 10.0),   # isometric/strategy — aggressive
               'CLOSEUP':  (75.0, 50.0, 25.0),   # 3D/shooter — gentle
               'MOBILE':   (40.0, 18.0, 8.0)}    # mobile — very aggressive
    if self.lod_preset in presets:
        _lod_syncing = True
        self.lod1_pct, self.lod2_pct, self.lod3_pct = presets[self.lod_preset]
        _lod_syncing = False


def _update_lod1(self, context):
    """LOD1 drives LOD2/LOD3 proportionally (×0.5 and ×0.2)."""
    global _lod_syncing
    if _lod_syncing:
        return
    _lod_syncing = True
    self.lod2_pct = max(1.0, round(self.lod1_pct * 0.5, 1))
    self.lod3_pct = max(1.0, round(self.lod1_pct * 0.2, 1))
    self.lod_preset = 'CUSTOM'
    _lod_syncing = False


def _update_lod_custom(self, context):
    """Editing LOD2/LOD3 by hand switches the preset to Custom."""
    global _lod_syncing
    if _lod_syncing:
        return
    _lod_syncing = True
    self.lod_preset = 'CUSTOM'
    _lod_syncing = False


def _bake_sig(o, pg):
    """Bake inputs that actually require new pixels. Normal strength is live-only."""
    return "|".join([
        str(o.get("bakedown_geo_version", 0)),
        pg.bake_resolution,
        "1" if pg.bake_normal else "0",
        f"{pg.bake_extrusion:.4f}",
        f"{pg.bake_sharpen:.3f}",
    ])


def _normalize_stored_bake_sig(signature):
    """Accept the v1.2 signature that contained live normal strength."""
    parts = str(signature or "").split("|")
    if len(parts) == 6:
        del parts[3]
    return "|".join(parts)


def _bake_assets_exist(o, pg):
    material_name = o.get("bakedown_material_name")
    if not material_name or bpy.data.materials.get(material_name) is None:
        return False
    required = ["BaseColor", "Rough", "Metal"]
    if pg.bake_normal:
        required.append("Normal")
    return all(_baked_image(o, suffix) is not None for suffix in required)


def _needs_bake(o, pg):
    """Whether the simplified active result needs fresh baked pixels."""
    if not (o and o.type == 'MESH' and o.get("bakedown_simplified") and o.get("bakedown_orig_mesh")):
        return False
    if not _bake_assets_exist(o, pg):
        return True
    return _bake_sig(o, pg) != _normalize_stored_bake_sig(o.get("bakedown_baked_sig", ""))


class BakeDownSettings(bpy.types.PropertyGroup):
    target_faces: bpy.props.IntProperty(
        name="Target triangles", default=10000, min=50, max=200000, step=100,
        description=("How many real render triangles to keep after simplification. "
                     "Game guidelines: hero prop 10–20k, building 3–8k, small prop "
                     "0.5–2k, distant background 0.1–0.5k."))
    target_mode: bpy.props.EnumProperty(
        name="Target mode",
        items=[('FACES', 'By triangles', 'Set the target triangle count manually'),
               ('DISTORTION', 'By distortion',
                'Choose a distortion budget and let BakeDown find the triangle count')],
        default='FACES')
    target_distortion: bpy.props.FloatProperty(
        name="Distortion budget %", default=0.30, min=0.01, max=5.0,
        description=("Maximum approximate bidirectional deviation. BakeDown searches "
                     "for the most aggressive simplification that stays within this budget."))
    planar_snap: bpy.props.BoolProperty(
        name="Flatten near-planar surfaces", default=False,
        description=("Project vertices of near-planar faces onto a plane. Useful for walls "
                     "and floors; inspect complex corners afterwards."))
    ui_mode: bpy.props.EnumProperty(
        name="Interface",
        items=[('STEPS', 'Simplification', 'Simplify → texture → export'),
               ('RIG', 'Rig', 'Transfer an armature and vertex weights from a template'),
               ('LOD', 'LOD', 'Generate LOD0–LOD3')],
        default='STEPS')
    lod_preview: bpy.props.EnumProperty(
        name="Preview",
        items=[('LOD0', 'LOD0', ''), ('LOD1', 'LOD1', ''),
               ('LOD2', 'LOD2', ''), ('LOD3', 'LOD3', '')],
        default='LOD0', update=_update_lod_preview)
    lod_preset: bpy.props.EnumProperty(
        name="Preset",
        items=[('CLOSEUP', '3D Shooter', 'Close camera, gentle reduction'),
               ('STRATEGY', 'Strategy', 'Isometric/strategy camera, aggressive reduction'),
               ('MOBILE', 'Mobile', 'Maximum reduction for mobile'),
               ('CUSTOM', 'Custom', 'Custom values')],
        default='STRATEGY', update=_update_lod_preset)
    lod1_on: bpy.props.BoolProperty(name="LOD1", default=True, description="Generate LOD1")
    lod2_on: bpy.props.BoolProperty(name="LOD2", default=True, description="Generate LOD2")
    lod3_on: bpy.props.BoolProperty(name="LOD3", default=True, description="Generate LOD3")
    lod1_pct: bpy.props.FloatProperty(
        name="LOD1", default=50.0, min=1.0, max=100.0, subtype='PERCENTAGE',
        update=_update_lod1, description="LOD1 triangles as a percentage of LOD0")
    lod2_pct: bpy.props.FloatProperty(
        name="LOD2", default=25.0, min=1.0, max=100.0, subtype='PERCENTAGE',
        update=_update_lod_custom, description="LOD2 triangles as a percentage of LOD0")
    lod3_pct: bpy.props.FloatProperty(
        name="LOD3", default=10.0, min=1.0, max=100.0, subtype='PERCENTAGE',
        update=_update_lod_custom, description="LOD3 triangles as a percentage of LOD0")
    dissolve_angle: bpy.props.FloatProperty(
        name="Dissolve angle", default=8.0, min=0.0, max=45.0,
        description=("Angle threshold for merging near-planar faces. Higher values are "
                     "more aggressive and may smooth small details."))
    do_dissolve_faces: bpy.props.BoolProperty(
        name="Merge near-planar faces before collapse", default=True,
        description="Merge near-planar faces before the collapse decimation pass")
    final_dissolve: bpy.props.BoolProperty(
        name="Final Limited Dissolve", default=True,
        description="Run one more planar cleanup pass after collapse")
    fill_holes: bpy.props.BoolProperty(
        name="Fill holes", default=False,
        description="Close holes after simplification; intentional openings may also be filled")
    remove_interior: bpy.props.BoolProperty(
        name="Remove interior faces", default=False,
        description=("Use Blender's interior-face detector before simplification. "
                     "Review the result because complex meshes may be misclassified."))
    triangulate_output: bpy.props.BoolProperty(
        name="Triangulate output", default=False,
        description=("Convert the final mesh to explicit triangles. Triangle statistics are "
                     "always calculated from the render triangulation, even when this is off."))
    bake_resolution: bpy.props.EnumProperty(
        name="Resolution",
        items=[('1024', '1K', '1024×1024 textures for small or distant assets'),
               ('2048', '2K', '2048×2048 textures for medium assets'),
               ('4096', '4K', '4096×4096 textures for hero assets')],
        default='4096',
        description="Resolution of Base Color, Roughness, Metallic and Normal maps")
    bake_normal: bpy.props.BoolProperty(
        name="Bake a normal map", default=True,
        description="Restore high-poly surface detail with a tangent-space normal map")
    bake_normal_strength: bpy.props.FloatProperty(
        name="Normal strength", default=0.5, min=0.0, max=2.0,
        update=_update_normal_strength,
        description="Live normal-map strength; changing it does not require another bake")
    bake_extrusion: bpy.props.FloatProperty(
        name="Ray distance (0 = auto)", default=0.0, min=0.0, max=2.0,
        description=("Selected-to-active ray distance in local mesh units. Use 0 for automatic "
                     "distance; increase only if the bake has missed areas."))
    bake_sharpen: bpy.props.FloatProperty(
        name="Sharpen", default=0.0, min=0.0, max=2.0,
        description="Unsharp-mask amount applied to the baked Base Color map")
    show_adv_decimate: bpy.props.BoolProperty(
        name="Settings", default=False,
        description="Show advanced simplification settings")
    show_adv_bake: bpy.props.BoolProperty(
        name="Settings", default=False,
        description="Show advanced baking settings")
    rig_template: bpy.props.PointerProperty(
        type=bpy.types.Object, name="Rig template",
        description="Skinned template mesh that provides its armature and vertex weights",
        poll=lambda self, ob: ob.type == 'MESH')
    is_baking: bpy.props.BoolProperty(default=False)
    bake_progress: bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    bake_cancel: bpy.props.BoolProperty(default=False)
    bake_stage: bpy.props.StringProperty(default="")


def _planar_snap(o):
    """Snap near-planar faces to a perfect plane (project vertices onto the face plane)."""
    import bmesh
    if o.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.normal_update()
    # small faces first, large faces last (large planes "win" for vertices
    # shared at the seams).
    for f in sorted(bm.faces, key=lambda fc: fc.calc_area()):
        if len(f.verts) < 4:
            continue
        n = f.normal
        if n.length < 1e-6:
            continue
        n = n.normalized()
        c = f.calc_center_median()
        for v in f.verts:
            v.co -= n * (v.co - c).dot(n)
    bm.to_mesh(me)
    bm.free()
    me.update()


def _evaluated_mesh_with_only_modifier(context, obj, modifier):
    """Evaluate a temporary modifier without baking the object's existing stack twice."""
    states = []
    for existing in obj.modifiers:
        if existing == modifier:
            continue
        states.append((existing, existing.show_viewport))
        existing.show_viewport = False
    try:
        context.view_layer.update()
        evaluated = obj.evaluated_get(context.evaluated_depsgraph_get())
        return bpy.data.meshes.new_from_object(evaluated)
    finally:
        for existing, show_viewport in states:
            try:
                existing.show_viewport = show_viewport
            except Exception:
                pass
        try:
            if obj.modifiers.get(modifier.name) is not None:
                obj.modifiers.remove(modifier)
        except Exception:
            pass
        context.view_layer.update()


def _run_pipeline(context, o, target, pg):
    """One simplification FROM THE BACKUP down to `target` triangles + distortion measurement."""
    _ensure_backup(o)
    if o.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    _restore_from_backup(o)
    delimit = {'NORMAL', 'MATERIAL'}
    ang = math.radians(pg.dissolve_angle)
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    context.view_layer.objects.active = o
    if o.data.has_custom_normals:
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=1e-4)
    bpy.ops.mesh.delete_loose()
    bpy.ops.mesh.normals_make_consistent(inside=False)
    if pg.remove_interior:
        # remove hidden interior faces (a common AI-mesh problem): saves polygons
        # and avoids bake misses. Done BEFORE collapse, on the fixed normals.
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_interior_faces()
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.mesh.select_all(action='SELECT')
    if pg.do_dissolve_faces:
        bpy.ops.mesh.dissolve_limited(angle_limit=ang, delimit=delimit)
    bpy.ops.object.mode_set(mode='OBJECT')
    cur = _triangle_count_object(o)
    if cur > target:
        ratio = max(0.0005, min(1.0, target / float(cur)))
        mod = o.modifiers.new("BakeDownCollapse", 'DECIMATE')
        mod.decimate_type = 'COLLAPSE'
        mod.ratio = ratio
        new_me = _evaluated_mesh_with_only_modifier(context, o, mod)
        old = o.data
        o.data = new_me
        o.data.name = f"{o.name}_work"
        if old.users == 0:
            bpy.data.meshes.remove(old)
    if o.data.has_custom_normals:
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    if pg.fill_holes:
        bpy.ops.mesh.fill_holes(sides=0)
    if pg.final_dissolve:
        bpy.ops.mesh.dissolve_limited(angle_limit=ang, delimit=delimit)
    if pg.triangulate_output:
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    if pg.planar_snap:
        _planar_snap(o)
    _measure_distortion(context, o)


def _auto_target(context, o, pg):
    """Find the triangle count that fits the distortion budget (binary search)."""
    _ensure_backup(o)
    orig = _triangle_count_mesh(_get_backup(o))
    budget = pg.target_distortion
    if orig <= 50:
        _run_pipeline(context, o, orig, pg)
        return
    lo, hi = 50, orig
    best = orig
    for _ in range(7):
        mid = (lo + hi) // 2
        _run_pipeline(context, o, mid, pg)
        d = o.get("bakedown_distort_pct", float("inf"))
        if d <= budget:
            best = mid
            hi = mid          # can go more aggressive (fewer triangles)
        else:
            lo = mid          # needs more triangles
        if hi - lo <= max(200, orig // 100):
            break
    _run_pipeline(context, o, best, pg)


def _finish_simplify(context, o):
    o["bakedown_simplified"] = True
    o["bakedown_geo_version"] = o.get("bakedown_geo_version", 0) + 1


# ---------------------------------------------------------------------------
# Simplification
# ---------------------------------------------------------------------------
class OBJECT_OT_bakedown_decimate(bpy.types.Operator):
    bl_idname = "object.bakedown_decimate"
    bl_label = "Simplify"
    bl_description = ("Simplify only the active mesh to the target triangle count. "
                      "The first run stores a non-destructive backup.")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return _not_lod(context)

    def execute(self, context):
        pg = context.scene.bakedown
        o = context.active_object
        if o is None or o.type != 'MESH':
            self.report({'ERROR'}, _tr("No active mesh"))
            return {'CANCELLED'}
        state = _capture_selection_state(context)
        previous_props = _capture_bakedown_props(o)
        previous_backup_name = previous_props.get("bakedown_orig_mesh")
        previous_mesh_name = o.data.name
        previous_mesh = o.data
        rollback_mesh = o.data.copy()
        rollback_mesh.name = f"__BakeDownSimplifyRollback_{uuid.uuid4().hex[:8]}"
        success = False
        _activate_only(context, o)
        try:
            if pg.target_mode == 'DISTORTION':
                _auto_target(context, o, pg)
            else:
                _run_pipeline(context, o, pg.target_faces, pg)
            _finish_simplify(context, o)
            _enter_inspect(context)
            success = True
        except Exception as exc:
            created_backup_name = o.get("bakedown_orig_mesh")
            failed_mesh = o.data
            o.data = rollback_mesh
            rollback_mesh.name = previous_mesh_name
            if failed_mesh is not rollback_mesh and failed_mesh.users == 0:
                try:
                    bpy.data.meshes.remove(failed_mesh)
                except Exception:
                    pass
            if (previous_mesh is not rollback_mesh and previous_mesh is not failed_mesh
                    and previous_mesh.users == 0):
                try:
                    bpy.data.meshes.remove(previous_mesh)
                except Exception:
                    pass
            _restore_bakedown_props(o, previous_props)
            if not previous_backup_name and created_backup_name:
                created_backup = bpy.data.meshes.get(created_backup_name)
                if created_backup is not None and created_backup is not rollback_mesh:
                    try:
                        created_backup.use_fake_user = False
                        bpy.data.meshes.remove(created_backup)
                    except Exception:
                        pass
            self.report({'ERROR'}, f"BakeDown: {exc}")
            return {'CANCELLED'}
        finally:
            if success and rollback_mesh.users == 0:
                try:
                    bpy.data.meshes.remove(rollback_mesh)
                except Exception:
                    pass
            _restore_selection_state(context, state, fallback=o)
        self.report({'INFO'}, _tr("Simplified to {:,} triangles").format(_triangle_count_object(o)))
        return {'FINISHED'}


class OBJECT_OT_bakedown_reset(bpy.types.Operator):
    bl_idname = "object.bakedown_reset"
    bl_label = "Reset"
    bl_description = "Restore the active object from its BakeDown backup"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        o = context.active_object
        if o is None or o.type != 'MESH':
            self.report({'ERROR'}, _tr("No active mesh"))
            return {'CANCELLED'}
        state = _capture_selection_state(context)
        try:
            _activate_only(context, o)
            if not _restore_from_backup(o):
                self.report({'WARNING'}, _tr("No backup is available"))
                return {'CANCELLED'}
            _clear_distortion_state(o)
            o["bakedown_simplified"] = False
            self.report({'INFO'}, _tr("Original restored"))
            return {'FINISHED'}
        finally:
            _restore_selection_state(context, state, fallback=o)


class OBJECT_OT_bakedown_inspect(bpy.types.Operator):
    bl_idname = "object.bakedown_inspect"
    bl_label = "Inspect shape"
    bl_description = "Toggle Solid + MatCap + wireframe inspection"
    bl_options = {'REGISTER'}

    def execute(self, context):
        sp = context.space_data
        if sp is None or sp.type != 'VIEW_3D':
            for area in _screen_areas(context):
                if area.type == 'VIEW_3D':
                    sp = area.spaces.active
                    break
        if sp is None or sp.type != 'VIEW_3D':
            self.report({'WARNING'}, _tr("No 3D viewport"))
            return {'CANCELLED'}
        sh = sp.shading
        ov = sp.overlay
        inspecting = (sh.type == 'SOLID' and sh.light == 'MATCAP' and ov.show_wireframes)
        if inspecting:
            sh.type = 'MATERIAL'
            ov.show_wireframes = False
        else:
            sh.type = 'SOLID'
            sh.light = 'MATCAP'
            ov.show_wireframes = True
        return {'FINISHED'}


class OBJECT_OT_bakedown_finalize(bpy.types.Operator):
    bl_idname = "object.bakedown_finalize"
    bl_label = "Delete backup"
    bl_description = "Release the original mesh backup after you are satisfied with the result"
    bl_options = {'REGISTER'}

    def execute(self, context):
        o = context.active_object
        if o is None or o.type != 'MESH':
            self.report({'ERROR'}, _tr("No active mesh"))
            return {'CANCELLED'}
        state = _capture_selection_state(context)
        try:
            _activate_only(context, o)
            bk = _get_backup(o)
            if bk is not None:
                bk.use_fake_user = False
                if "bakedown_orig_mesh" in o:
                    del o["bakedown_orig_mesh"]
                if bk.users == 0:
                    bpy.data.meshes.remove(bk)
            self.report({'INFO'}, _tr("Backup released"))
            return {'FINISHED'}
        finally:
            _restore_selection_state(context, state, fallback=o)


# ---------------------------------------------------------------------------
# Texture baking (modal bake with a progress bar)
# ---------------------------------------------------------------------------
def _metallic_emit_copy(orig):
    """Material copy with Metallic routed into Emission (for the EMIT metallic bake)."""
    mc = orig.copy()
    nt = mc.node_tree
    p = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
    if p is None or out is None:
        return mc
    em = nt.nodes.new("ShaderNodeEmission")
    minp = p.inputs['Metallic']
    if minp.is_linked:
        nt.links.new(minp.links[0].from_socket, em.inputs['Color'])
    else:
        c = minp.default_value
        em.inputs['Color'].default_value = (c, c, c, 1)
    nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    return mc


def _sharpen_image(im, amount):
    """Unsharp mask on albedo: result = orig + amount·(orig − blur)."""
    if im is None or amount <= 0.0:
        return
    try:
        import numpy as np
        w, h = im.size
        px = np.empty(w * h * 4, dtype=np.float32)
        im.pixels.foreach_get(px)
        rgba = px.reshape(h, w, 4)
        rgb = rgba[:, :, :3]
        blur = rgb.copy()
        for _ in range(2):   # two box-blur passes ≈ soft gaussian
            # edge padding instead of np.roll: roll wraps around and mixes the
            # opposite borders of the UV atlas into each other.
            p = np.pad(blur, ((1, 1), (1, 1), (0, 0)), mode='edge')
            blur = (p[1:-1, 1:-1] + p[:-2, 1:-1] + p[2:, 1:-1]
                    + p[1:-1, :-2] + p[1:-1, 2:]) / 5.0
        rgba[:, :, :3] = np.clip(rgb + amount * (rgb - blur), 0.0, 1.0)
        im.pixels.foreach_set(rgba.reshape(-1))
        im.update()
    except Exception:
        pass


# Whether a bake modal operator is actually running in this Blender session.
# `scene.bakedown.is_baking` is saved into .blend files (Ctrl+S, autosave, crash
# recovery), so it can't be trusted on its own after a file is loaded.
_BAKE_RUNNING = False


def _reset_bake_ui_state(pg):
    pg.is_baking = False
    pg.bake_cancel = False
    pg.bake_progress = 0.0
    pg.bake_stage = ""


@bpy.app.handlers.persistent
def _bakedown_load_post(_dummy=None):
    """A file saved mid-bake must not open with a permanently 'baking' panel."""
    global _BAKE_RUNNING
    _BAKE_RUNNING = False
    for scene in bpy.data.scenes:
        pg = getattr(scene, "bakedown", None)
        if pg is not None and (pg.is_baking or pg.bake_cancel):
            try:
                _reset_bake_ui_state(pg)
            except Exception:
                pass


def _alive(idblock):
    """Return the ID if its Python reference is still valid, otherwise None."""
    if idblock is None:
        return None
    try:
        idblock.name
        return idblock
    except ReferenceError:
        return None


class OBJECT_OT_bakedown_bake(bpy.types.Operator):
    bl_idname = "object.bakedown_bake"
    bl_label = "Bake textures"
    bl_description = ("Bake Base Color, Roughness, Metallic and Normal from the original "
                      "onto the simplified active mesh")
    bl_options = {'REGISTER'}

    _timer = None

    @classmethod
    def poll(cls, context):
        return _not_lod(context)

    def invoke(self, context, event):
        global _BAKE_RUNNING
        pg = context.scene.bakedown
        lo = context.active_object
        if lo is None or lo.type != 'MESH':
            self.report({'ERROR'}, _tr("No active mesh"))
            return {'CANCELLED'}
        bm = _get_backup(lo)
        if bm is None:
            self.report({'ERROR'}, _tr("No backup — run Simplify first"))
            return {'CANCELLED'}
        if _BAKE_RUNNING:
            return {'CANCELLED'}
        if pg.is_baking:
            # Stale flag from a file saved during a bake: no bake is running.
            _reset_bake_ui_state(pg)

        self.lo = lo
        self.hi = None
        self.mat = None
        self.nt = None
        self.copies = []
        self._temp_images = []
        self._image_targets = {}
        self._working_mesh = None
        self._rollback_mesh = None
        self._render_state = _capture_render_state(context.scene)
        self._viewport_state = _capture_viewport_state(context)
        self._selection_state = _capture_selection_state(context)
        self._previous_bake_props = _capture_bakedown_props(lo)
        self._previous_material_name = lo.get("bakedown_material_name")
        self._previous_image_names = {
            suffix: lo.get(f"bakedown_image_{suffix}")
            for suffix in ("BaseColor", "Rough", "Metal", "Normal")
        }
        self._nstr = pg.bake_normal_strength
        self._committed = False

        try:
            _activate_only(context, lo)
            _exit_inspect(context)
            res = int(pg.bake_resolution)
            extrusion, raydist = _bake_ray(lo, pg)

            # Transactional mesh workflow: all UV/material edits happen on a copy.
            self._rollback_mesh = lo.data
            self._working_mesh = lo.data.copy()
            self._working_mesh.name = f"__BakeDownWorking_{lo.name}_{uuid.uuid4().hex[:8]}"
            lo.data = self._working_mesh

            if not lo.data.uv_layers:
                lo.data.uv_layers.new(name="UVMap")
            _activate_only(context, lo)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project(angle_limit=math.radians(66.0),
                                     island_margin=0.003, correct_aspect=True)
            bpy.ops.uv.pack_islands(margin=0.003, rotate=True)
            bpy.ops.object.mode_set(mode='OBJECT')

            token = uuid.uuid4().hex[:8]

            def _img(suffix, non_color):
                im = bpy.data.images.new(
                    f"__BakeDownTemp_{token}_{suffix}", res, res,
                    alpha=False, float_buffer=False)
                im.colorspace_settings.name = 'Non-Color' if non_color else 'sRGB'
                self._temp_images.append(im)
                self._image_targets[im.name] = f"{lo.name}_{suffix}"
                return im

            self.img_base = _img("BaseColor", False)
            self.img_rough = _img("Rough", True)
            self.img_metal = _img("Metal", True)
            self.img_norm = _img("Normal", True) if pg.bake_normal else None

            self.hi = bpy.data.objects.new(f"__bakedown_hipoly_{token}", bm)
            context.scene.collection.objects.link(self.hi)
            self.hi.matrix_world = lo.matrix_world.copy()
            # Materials linked to the OBJECT (not the mesh) are not carried by the
            # backup mesh; copy them so the high-poly source keeps its look.
            for i, slot in enumerate(lo.material_slots):
                if (slot.link == 'OBJECT' and slot.material is not None
                        and i < len(self.hi.material_slots)):
                    self.hi.material_slots[i].link = 'OBJECT'
                    self.hi.material_slots[i].material = slot.material

            self.mat = bpy.data.materials.new(f"__BakeDownTempMaterial_{token}")
            self.mat.use_nodes = True
            nt = self.mat.node_tree
            nt.nodes.clear()
            self.nt = nt
            self.out = nt.nodes.new("ShaderNodeOutputMaterial"); self.out.location = (700, 0)
            self.bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); self.bsdf.location = (350, 0)
            nt.links.new(self.bsdf.outputs['BSDF'], self.out.inputs['Surface'])
            self.n_base = nt.nodes.new("ShaderNodeTexImage"); self.n_base.location = (-450, 350); self.n_base.image = self.img_base
            self.n_rgh = nt.nodes.new("ShaderNodeTexImage"); self.n_rgh.location = (-450, 50); self.n_rgh.image = self.img_rough
            self.n_met = nt.nodes.new("ShaderNodeTexImage"); self.n_met.location = (-450, -250); self.n_met.image = self.img_metal
            self.n_norm = None
            if self.img_norm is not None:
                self.n_norm = nt.nodes.new("ShaderNodeTexImage"); self.n_norm.location = (-450, -550)
                self.n_norm.image = self.img_norm
                self.n_norm.interpolation = 'Linear'
            self._slot_state = [(s.link, s.material) for s in lo.material_slots]
            lo.data.materials.clear()
            lo.data.materials.append(self.mat)
            # An OBJECT-linked slot would hide the bake material on the target.
            for slot in lo.material_slots:
                slot.link = 'DATA'

            scn = context.scene
            scn.render.engine = 'CYCLES'
            cycles = getattr(scn, 'cycles', None)
            if cycles is not None:
                try:
                    cycles.device = 'CPU'
                except Exception:
                    pass
                cycles.samples = 1
            b = scn.render.bake
            b.use_selected_to_active = True
            b.use_clear = True
            b.use_cage = False
            b.cage_extrusion = extrusion
            b.max_ray_distance = raydist
            b.margin = max(4, res // 512)

            self._passes = [(_tr("Base Color"), self._p_diffuse),
                            (_tr("Roughness"), self._p_rough)]
            if self.n_norm is not None:
                self._passes.append((_tr("Normals"), self._p_normal))
            self._passes.append((_tr("Metallic"), self._p_metal))
            for im in (self.img_base, self.img_rough, self.img_metal, self.img_norm):
                if im is not None:
                    self._passes.append((_tr("Packing"),
                                         (lambda image: (lambda _ctx: self._p_pack(image)))(im)))
            self._idx = 0

            pg.is_baking = True
            pg.bake_cancel = False
            pg.bake_progress = 0.0
            pg.bake_stage = _tr("Preparing")
            _redraw_ui(context)

            wm = context.window_manager
            self._timer = wm.event_timer_add(0.05, window=context.window)
            if not wm.modal_handler_add(self):
                raise RuntimeError("Could not start the modal bake handler")
            _BAKE_RUNNING = True
            return {'RUNNING_MODAL'}
        except Exception as exc:
            self.report({'ERROR'}, _tr("Bake failed: {}").format(exc))
            self._cleanup(context, cancelled=True)
            return {'CANCELLED'}

    def _do_bake(self, context, node, btype, **kw):
        for n in self.nt.nodes:
            n.select = False
        node.select = True
        self.nt.nodes.active = node
        _activate_only(context, self.lo)
        self.hi.select_set(True)
        self.lo.select_set(True)
        context.view_layer.objects.active = self.lo
        result = bpy.ops.object.bake(type=btype, **kw)
        if 'FINISHED' not in result:
            raise RuntimeError(f"Blender bake operator returned {result}")

    def _p_diffuse(self, context):
        b = context.scene.render.bake
        b.use_pass_direct = False
        b.use_pass_indirect = False
        b.use_pass_color = True
        self._do_bake(context, self.n_base, 'DIFFUSE')
        _sharpen_image(self.img_base, context.scene.bakedown.bake_sharpen)

    def _p_rough(self, context):
        self._do_bake(context, self.n_rgh, 'ROUGHNESS')

    def _p_normal(self, context):
        self._do_bake(context, self.n_norm, 'NORMAL', normal_space='TANGENT')

    def _p_metal(self, context):
        for slot in self.hi.material_slots:
            if slot.material is None:
                continue
            mc = _metallic_emit_copy(slot.material)
            self.copies.append(mc)
            slot.link = 'OBJECT'
            slot.material = mc
        self._do_bake(context, self.n_met, 'EMIT')

    def _p_pack(self, im):
        im.pack()

    def modal(self, context, event):
        pg = context.scene.bakedown
        # Undo/redo would reload the datablocks this operator holds references to.
        if event.type == 'Z' and (event.ctrl or event.oskey):
            return {'RUNNING_MODAL'}
        if event.type == 'ESC' or pg.bake_cancel:
            self._cleanup(context, cancelled=True)
            return {'CANCELLED'}
        if _alive(self.lo) is None or _alive(self.hi) is None:
            # The target or the temporary high-poly object was deleted mid-bake.
            self.report({'ERROR'}, _tr("Bake failed: {}").format("object was removed"))
            self._cleanup(context, cancelled=True)
            return {'CANCELLED'}
        if event.type == 'TIMER':
            if self._idx < len(self._passes):
                stage, fn = self._passes[self._idx]
                pg.bake_stage = stage
                try:
                    fn(context)
                except Exception as exc:
                    self.report({'ERROR'}, _tr("Bake failed: {}").format(exc))
                    self._cleanup(context, cancelled=True)
                    return {'CANCELLED'}
                self._idx += 1
                pg.bake_progress = self._idx / len(self._passes)
                _redraw_ui(context)
                return {'RUNNING_MODAL'}
            self._cleanup(context, cancelled=False)
            return {'FINISHED'}
        return {'PASS_THROUGH'}

    def _unique_asset_name(self, collection, desired):
        if collection.get(desired) is None:
            return desired
        version = self.lo.get("bakedown_geo_version", 0)
        candidate = f"{desired}_v{version}"
        index = 2
        while collection.get(candidate) is not None:
            candidate = f"{desired}_v{version}_{index}"
            index += 1
        return candidate

    def _commit(self, pg):
        nt = self.nt
        nt.links.new(self.n_base.outputs['Color'], self.bsdf.inputs['Base Color'])
        nt.links.new(self.n_rgh.outputs['Color'], self.bsdf.inputs['Roughness'])
        nt.links.new(self.n_met.outputs['Color'], self.bsdf.inputs['Metallic'])
        if self.n_norm is not None:
            nmap = nt.nodes.new("ShaderNodeNormalMap")
            nmap.location = (0, -500)
            nmap.inputs['Strength'].default_value = self._nstr
            nt.links.new(self.n_norm.outputs['Color'], nmap.inputs['Color'])
            nt.links.new(nmap.outputs['Normal'], self.bsdf.inputs['Normal'])

        for im in self._temp_images:
            desired = self._image_targets[im.name]
            existing = bpy.data.images.get(desired)
            if existing is not None and existing != im and existing.users == 0:
                bpy.data.images.remove(existing)
            final_name = self._unique_asset_name(bpy.data.images, desired)
            im.name = final_name
            suffix = desired.rsplit('_', 1)[-1]
            self.lo[f"bakedown_image_{suffix}"] = final_name

        desired_mat = f"{self.lo.name}_Baked"
        existing_mat = bpy.data.materials.get(desired_mat)
        if existing_mat is not None and existing_mat != self.mat and existing_mat.users == 0:
            bpy.data.materials.remove(existing_mat)
        final_mat_name = self._unique_asset_name(bpy.data.materials, desired_mat)
        self.mat.name = final_mat_name
        self.lo["bakedown_material_name"] = final_mat_name
        self.lo["bakedown_baked_sig"] = _bake_sig(self.lo, pg)
        self._committed = True

        if self._rollback_mesh is not None and self._rollback_mesh.users == 0:
            bpy.data.meshes.remove(self._rollback_mesh)
        self._rollback_mesh = None
        self._working_mesh = None

        previous_material = bpy.data.materials.get(self._previous_material_name or "")
        if previous_material is not None and previous_material != self.mat and previous_material.users == 0:
            try:
                bpy.data.materials.remove(previous_material)
            except Exception:
                pass
        for previous_name in self._previous_image_names.values():
            previous_image = bpy.data.images.get(previous_name or "")
            if previous_image is not None and previous_image not in self._temp_images and previous_image.users == 0:
                try:
                    bpy.data.images.remove(previous_image)
                except Exception:
                    pass

    def _rollback(self):
        if self.lo is not None and self._rollback_mesh is not None:
            current = self.lo.data
            self.lo.data = self._rollback_mesh
            if current is not None and current.users == 0:
                bpy.data.meshes.remove(current)
            for slot, (link, material) in zip(self.lo.material_slots,
                                              getattr(self, '_slot_state', [])):
                try:
                    slot.link = link
                    if link == 'OBJECT':
                        slot.material = _alive(material)
                except Exception:
                    pass
        self._working_mesh = None
        self._rollback_mesh = None
        if self.lo is not None:
            _restore_bakedown_props(self.lo, getattr(self, '_previous_bake_props', {}))
        if self.mat is not None and self.mat.users == 0:
            try:
                bpy.data.materials.remove(self.mat)
            except Exception:
                pass
        for im in list(self._temp_images):
            if im.users == 0:
                try:
                    bpy.data.images.remove(im)
                except Exception:
                    pass
        self._temp_images.clear()

    def _cleanup(self, context, cancelled):
        global _BAKE_RUNNING
        _BAKE_RUNNING = False
        pg = context.scene.bakedown
        # Drop references to datablocks that no longer exist (deleted mid-bake).
        self.lo = _alive(getattr(self, 'lo', None))
        self.hi = _alive(getattr(self, 'hi', None))
        self.mat = _alive(getattr(self, 'mat', None))
        self._rollback_mesh = _alive(getattr(self, '_rollback_mesh', None))
        self._temp_images = [im for im in getattr(self, '_temp_images', []) if _alive(im)]
        self.copies = [mc for mc in getattr(self, 'copies', []) if _alive(mc)]
        if self.lo is None:
            cancelled = True
        try:
            if cancelled:
                self._rollback()
            else:
                self._commit(pg)
        except Exception as exc:
            cancelled = True
            self.report({'ERROR'}, _tr("Bake failed: {}").format(exc))
            try:
                self._rollback()
            except Exception:
                pass

        for mc in getattr(self, 'copies', []):
            try:
                bpy.data.materials.remove(mc)
            except Exception:
                pass
        self.copies = []
        if getattr(self, 'hi', None) is not None:
            try:
                bpy.data.objects.remove(self.hi, do_unlink=True)
            except Exception:
                pass
            self.hi = None

        _restore_render_state(context.scene, getattr(self, '_render_state', None))
        _restore_viewport_state(context, getattr(self, '_viewport_state', None))
        _reset_bake_ui_state(pg)
        wm = context.window_manager
        if self._timer is not None:
            try:
                wm.event_timer_remove(self._timer)
            except Exception:
                pass
            self._timer = None
        _restore_selection_state(context, getattr(self, '_selection_state', None), fallback=self.lo)
        _redraw_ui(context)
        self.report({'INFO'}, _tr("Bake cancelled") if cancelled else _tr("Bake complete"))


class OBJECT_OT_bakedown_distort_info(bpy.types.Operator):
    bl_idname = "object.bakedown_distort_info"
    bl_label = "Approximate distortion"
    bl_description = "Approximate bidirectional surface deviation, sampled in both directions. Use it as a guide and inspect the shape visually."
    bl_options = {'INTERNAL'}

    def execute(self, context):
        return {'FINISHED'}


class OBJECT_OT_bakedown_bake_cancel(bpy.types.Operator):
    bl_idname = "object.bakedown_bake_cancel"
    bl_label = "Cancel bake"
    bl_description = "Cancel the current bake"
    bl_options = {'REGISTER'}

    def execute(self, context):
        context.scene.bakedown.bake_cancel = True
        return {'FINISHED'}


class OBJECT_OT_bakedown_export(bpy.types.Operator):
    bl_idname = "object.bakedown_export"
    bl_label = "Export"
    bl_description = "Export the active BakeDown object or its own LOD collection"
    bl_options = {'REGISTER'}

    directory: bpy.props.StringProperty(subtype='DIR_PATH')
    target_engine: bpy.props.EnumProperty(
        name="Engine",
        items=[('UNITY', 'Unity', 'Unity FBX'),
               ('UNREAL', 'Unreal', 'Unreal FBX'),
               ('GLTF', 'glTF', 'Self-contained GLB')],
        default='UNITY')
    save_textures: bpy.props.BoolProperty(
        name="Save textures as PNG", default=True,
        description="Save baked maps next to the exported model")
    flip_normal_green: bpy.props.BoolProperty(
        name="Flip normal-map green channel", default=False,
        description="Convert the normal map to the DirectX green-channel convention")
    pack_orm: bpy.props.BoolProperty(
        name="Pack ORM (R=AO, G=Roughness, B=Metallic)", default=False,
        description="Create an Occlusion/Roughness/Metallic packed texture")

    @classmethod
    def poll(cls, context):
        o = context.active_object
        return bool(o and o.type == 'MESH'
                    and (o.get("bakedown_simplified") or o.get("bakedown_lod_of")))

    def invoke(self, context, event):
        if not self.directory:
            self.directory = os.path.dirname(bpy.data.filepath) or os.path.expanduser("~")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        self.layout.prop(self, 'target_engine', expand=True)
        self.layout.prop(self, 'save_textures')
        self.layout.prop(self, 'flip_normal_green')
        self.layout.prop(self, 'pack_orm')

    def _validate_exporter(self):
        try:
            if self.target_engine == 'GLTF':
                return getattr(bpy.ops.export_scene, 'gltf') is not None
            return getattr(bpy.ops.export_scene, 'fbx') is not None
        except Exception:
            return False

    def _save_image_safely(self, image, path, flip_green=False):
        old_path = image.filepath_raw
        old_format = image.file_format
        flipped = False
        try:
            if flip_green:
                self._invert_green(image)
                flipped = True
            image.filepath_raw = path
            image.file_format = 'PNG'
            image.save()
        finally:
            if flipped:
                self._invert_green(image)
            image.filepath_raw = old_path
            image.file_format = old_format

    def execute(self, context):
        o = context.active_object
        if o is None or o.type != 'MESH':
            self.report({'ERROR'}, _tr("No active mesh"))
            return {'CANCELLED'}
        if not self._validate_exporter():
            self.report({'ERROR'}, _tr("Required exporter is unavailable"))
            return {'CANCELLED'}

        state = _capture_selection_state(context)
        base_obj = _base_object(o)
        base = base_obj.name if base_obj else _lod_base_name(o)
        coll = bpy.data.collections.get(f"{base}_LODs")
        mesh_objects = []
        if coll is not None:
            mesh_objects = [ob for ob in coll.objects if ob.type == 'MESH'
                            and ob.get("bakedown_lod_of") == base]
        if mesh_objects and base_obj is not None:
            lod_state = _lod_state(base_obj, mesh_objects)
            if lod_state == 'STALE':
                self.report({'ERROR'}, _tr("LODs are out of date: regenerate them after Simplify or Bake"))
                return {'CANCELLED'}
            if lod_state == 'UNKNOWN':
                self.report({'WARNING'}, _tr("LODs were created by an older BakeDown version; regenerate them if the base mesh or textures changed"))
        if not mesh_objects:
            mesh_objects = [o]
        arms = _armatures_for_objects(mesh_objects)
        if len(arms) > 1:
            self.report({'ERROR'}, _tr("More than one armature is attached to the export set"))
            return {'CANCELLED'}

        export_objects = list(mesh_objects) + list(arms)
        hidden_state = {ob.name: ob.hide_get() for ob in export_objects}
        image_state = []
        orm_image = None
        flipped_images = []
        result = {'CANCELLED'}

        try:
            root = os.path.abspath(bpy.path.abspath(self.directory or os.path.expanduser("~")))
            folder_name = (os.path.splitext(os.path.basename(bpy.data.filepath))[0]
                           if bpy.data.filepath else base)
            d = os.path.join(root, _safe_name(folder_name))
            os.makedirs(d, exist_ok=True)
            try:
                with tempfile.NamedTemporaryFile(dir=d, prefix=".bakedown_write_test_", delete=True):
                    pass
            except Exception as exc:
                raise RuntimeError(f"{_tr('The export folder is not writable')}: {exc}")

            for ob in mesh_objects:
                scale = ob.scale
                if any(v < 0.0 for v in scale) or ob.matrix_world.determinant() < 0.0:
                    self.report({'WARNING'}, _tr("Negative scale detected; apply scale before engine import if shading is incorrect"))
                    break
            for ob in mesh_objects:
                values = [abs(v) for v in ob.scale if abs(v) > 1e-8]
                if values and max(values) / min(values) > 1.001:
                    self.report({'WARNING'}, _tr("Non-uniform scale detected; consider applying scale before export"))
                    break

            found_images = []
            if self.save_textures:
                for suffix in ("BaseColor", "Rough", "Metal", "Normal"):
                    image = _baked_image(base_obj, suffix)
                    if image is None:
                        continue
                    found_images.append(image)
                    image_state.append((image, image.filepath_raw, image.file_format))
                    saved_path = os.path.join(d, f"{_safe_name(base)}_{suffix}.png")
                    self._save_image_safely(
                        image, saved_path,
                        flip_green=self.flip_normal_green and suffix == "Normal")
                    # The FBX exporter reads the image datablock path, not the path
                    # used by image.save(). Keep it pointed at the just-written PNG
                    # until export is complete, then restore it in finally.
                    image.filepath_raw = saved_path
                    image.file_format = 'PNG'
                if not found_images:
                    self.report({'WARNING'}, _tr("No baked textures were found; exporting geometry only"))
                if self.pack_orm:
                    orm_image = self._save_orm(base_obj, d)

            # GLB embeds the current image pixels. Keep a requested DirectX normal
            # conversion active only for the duration of the export, then restore it.
            if self.target_engine == 'GLTF' and self.flip_normal_green:
                normal_image = _baked_image(base_obj, "Normal")
                if normal_image is not None:
                    self._invert_green(normal_image)
                    flipped_images.append(normal_image)

            # Activate an object from the export set, never the hidden base object:
            # otherwise the base mesh is exported next to LOD0 as a duplicate.
            _activate_only(context, mesh_objects[0])
            for ob in export_objects:
                ob.hide_set(False)
                ob.select_set(True)
            context.view_layer.objects.active = mesh_objects[-1]

            if self.target_engine == 'GLTF':
                path = os.path.join(d, f"{_safe_name(base)}.glb")
                op_result = bpy.ops.export_scene.gltf(
                    filepath=path, use_selection=True, export_format='GLB')
            else:
                path = os.path.join(d, f"{_safe_name(base)}.fbx")
                kwargs = dict(filepath=path, use_selection=True, path_mode='RELATIVE',
                              embed_textures=False, add_leaf_bones=False)
                kwargs['mesh_smooth_type'] = 'FACE' if self.target_engine == 'UNREAL' else 'OFF'
                op_result = bpy.ops.export_scene.fbx(**kwargs)
            if 'FINISHED' not in op_result:
                raise RuntimeError(f"Blender exporter returned {op_result}")

            extra = f" ({len(mesh_objects)} LOD)" if len(mesh_objects) > 1 else ""
            self.report({'INFO'}, _tr("Exported to {}").format(d) + extra)
            result = {'FINISHED'}
        except Exception as exc:
            self.report({'ERROR'}, _tr("Export failed: {}").format(exc))
            result = {'CANCELLED'}
        finally:
            for image in flipped_images:
                try:
                    self._invert_green(image)
                except Exception:
                    pass
            for image, old_path, old_format in image_state:
                try:
                    image.filepath_raw = old_path
                    image.file_format = old_format
                except Exception:
                    pass
            if orm_image is not None and orm_image.users == 0:
                try:
                    bpy.data.images.remove(orm_image)
                except Exception:
                    pass
            for name, hidden in hidden_state.items():
                ob = bpy.data.objects.get(name)
                if ob is not None:
                    try:
                        ob.hide_set(hidden)
                    except Exception:
                        pass
            _restore_selection_state(context, state, fallback=o)
        return result

    @staticmethod
    def _invert_green(im):
        import numpy as np
        px = np.empty(len(im.pixels), dtype=np.float32)
        im.pixels.foreach_get(px)
        px[1::4] = 1.0 - px[1::4]
        im.pixels.foreach_set(px)
        im.update()

    def _save_orm(self, base_obj, directory):
        import numpy as np
        rough = _baked_image(base_obj, "Rough")
        metal = _baked_image(base_obj, "Metal")
        if rough is None or metal is None:
            return None
        if rough.size[:] != metal.size[:]:
            raise RuntimeError("Roughness and Metallic maps have different resolutions")
        r = np.empty(len(rough.pixels), dtype=np.float32)
        m = np.empty(len(metal.pixels), dtype=np.float32)
        rough.pixels.foreach_get(r)
        metal.pixels.foreach_get(m)
        orm = np.ones_like(r)
        orm[1::4] = r[0::4]
        orm[2::4] = m[0::4]
        orm[3::4] = 1.0
        image = bpy.data.images.new(
            f"__BakeDownORM_{uuid.uuid4().hex[:8]}", rough.size[0], rough.size[1], alpha=False)
        try:
            image.colorspace_settings.name = 'Non-Color'
            image.pixels.foreach_set(orm)
            self._save_image_safely(
                image, os.path.join(directory, f"{_safe_name(base_obj.name)}_ORM.png"))
            return image
        except Exception:
            if image.users == 0:
                bpy.data.images.remove(image)
            raise


class OBJECT_OT_bakedown_compare(bpy.types.Operator):
    bl_idname = "object.bakedown_compare"
    bl_label = "Compare with original"
    bl_description = "Toggle the original mesh and the simplified result"
    bl_options = {'REGISTER'}

    def execute(self, context):
        active = context.active_object
        existing = _comparison_object_for(active)
        if existing is not None:
            result_obj = bpy.data.objects.get(existing.get("bakedown_result") or "")
            mesh = existing.data
            bpy.data.objects.remove(existing, do_unlink=True)
            if mesh is not None and mesh.users == 0:
                bpy.data.meshes.remove(mesh)
            if result_obj is not None:
                result_obj.hide_set(False)
                bpy.ops.object.select_all(action='DESELECT')
                result_obj.select_set(True)
                context.view_layer.objects.active = result_obj
            return {'FINISHED'}

        o = active
        if o is None or o.type != 'MESH':
            self.report({'ERROR'}, _tr("No active mesh"))
            return {'CANCELLED'}
        bk = _get_backup(o)
        if bk is None:
            self.report({'WARNING'}, _tr("No backup — run Simplify first"))
            return {'CANCELLED'}

        name = f"__BakeDownBefore_{_safe_name(o.name)}"
        before = bpy.data.objects.new(name, bk.copy())
        context.scene.collection.objects.link(before)
        before.matrix_world = o.matrix_world.copy()
        before["bakedown_compare"] = True
        before["bakedown_result"] = o.name
        o.hide_set(True)
        bpy.ops.object.select_all(action='DESELECT')
        before.select_set(True)
        context.view_layer.objects.active = before
        return {'FINISHED'}


class OBJECT_OT_bakedown_lod(bpy.types.Operator):
    bl_idname = "object.bakedown_lod"
    bl_label = "Generate LODs"
    bl_description = "Generate LOD0–LOD3 from the active BakeDown object"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        o = context.active_object
        if not (o and o.type == 'MESH'):
            return False
        # allowed from the simplified base OR any LOD of this set (regeneration)
        return bool(o.get("bakedown_simplified") or o.get("bakedown_lod_of"))

    def execute(self, context):
        pg = context.scene.bakedown
        o = context.active_object
        _activate_only(context, o)
        # if a LOD is active, work from its base object
        if o.get("bakedown_lod_of"):
            src = bpy.data.objects.get(o["bakedown_lod_of"])
            if src is not None:
                o = src
        _activate_only(context, o)
        base = o.name
        coll_name = f"{base}_LODs"
        coll = bpy.data.collections.get(coll_name)
        if coll is not None:
            for ob in list(coll.objects):     # rebuild from scratch
                me = ob.data
                bpy.data.objects.remove(ob, do_unlink=True)
                if me and me.users == 0:
                    bpy.data.meshes.remove(me)
        else:
            coll = bpy.data.collections.new(coll_name)
            context.scene.collection.children.link(coll)

        bk = _get_backup(o)
        # armature-aware: if the base mesh is skinned, LODs inherit the armature and weights
        arm = next((m.object for m in o.modifiers
                    if m.type == 'ARMATURE' and m.object is not None), None)

        # LOD0 always; LOD1-3 only when enabled
        levels = [('LOD0', 100.0)]
        if pg.lod1_on:
            levels.append(('LOD1', pg.lod1_pct))
        if pg.lod2_on:
            levels.append(('LOD2', pg.lod2_pct))
        if pg.lod3_on:
            levels.append(('LOD3', pg.lod3_pct))

        made = []
        for name, pct in levels:
            me = o.data.copy()
            lod = bpy.data.objects.new(f"{base}_{name}", me)
            lod.matrix_world = o.matrix_world.copy()
            lod["bakedown_lod_of"] = base
            lod["bakedown_lod_level"] = name
            lod["bakedown_lod_src_sig"] = _lod_source_sig(o)
            coll.objects.link(lod)
            # vertex group names live on the OBJECT — the mesh copy does not carry them
            for vg in o.vertex_groups:
                lod.vertex_groups.new(name=vg.name)
            if pct < 100.0:
                # IMPORTANT: only Decimate on the object → new_from_object evaluates just it
                # (the armature is added AFTER, otherwise the pose gets baked in). Decimate
                # Collapse interpolates vertex weights → skinning is preserved.
                mod = lod.modifiers.new("LOD", 'DECIMATE')
                mod.decimate_type = 'COLLAPSE'
                mod.ratio = max(0.005, pct / 100.0)
                context.view_layer.update()
                ev = lod.evaluated_get(context.evaluated_depsgraph_get())
                newme = bpy.data.meshes.new_from_object(ev)
                lod.modifiers.remove(mod)
                oldme = lod.data
                lod.data = newme
                if oldme.users == 0:
                    bpy.data.meshes.remove(oldme)
            # now attach the armature (after decimation)
            if arm is not None:
                am = lod.modifiers.new("Armature", 'ARMATURE')
                am.object = arm
                lod.parent = arm
                lod.matrix_world = o.matrix_world.copy()
            # LOD distortion vs. the original (same as for Simplify)
            if bk is not None:
                lod["bakedown_orig_mesh"] = bk.name
                _measure_distortion(context, lod)
            made.append((lod, _triangle_count_object(lod)))

        o.hide_set(True)   # the source duplicates LOD0 — hide it
        lod0 = next((ob for ob, _count in made
                     if ob.get("bakedown_lod_level") == 'LOD0'), None)
        _exit_inspect(context)    # leave Shape mode, otherwise a black wireframe covers the LODs
        pg.lod_preview = 'LOD0'
        _update_lod_preview(pg, context)
        if lod0 is not None:
            lod0.select_set(True)
            context.view_layer.objects.active = lod0
        self.report({'INFO'}, "LOD: " + ", ".join(f"{ob.name} {count:,}" for ob, count in made))
        return {'FINISHED'}


def _capture_import_state():
    return {
        "objects": set(bpy.data.objects),
        "collections": set(bpy.data.collections),
        "meshes": set(bpy.data.meshes),
        "armatures": set(bpy.data.armatures),
        "materials": set(bpy.data.materials),
        "images": set(bpy.data.images),
        "actions": set(bpy.data.actions),
        "lights": set(bpy.data.lights),
        "cameras": set(bpy.data.cameras),
    }


def _cleanup_import_delta(before, keep_objects=()):
    """Remove objects and orphan datablocks created by a failed rig import."""
    keep = set(keep_objects)
    for obj in list(bpy.data.objects):
        if obj not in before.get("objects", set()) and obj not in keep:
            try:
                bpy.data.objects.remove(obj, do_unlink=True)
            except Exception:
                pass
    for key, collection in (
            ("collections", bpy.data.collections),
            ("meshes", bpy.data.meshes),
            ("armatures", bpy.data.armatures),
            ("materials", bpy.data.materials),
            ("images", bpy.data.images),
            ("actions", bpy.data.actions),
            ("lights", bpy.data.lights),
            ("cameras", bpy.data.cameras)):
        old = before.get(key, set())
        for datablock in list(collection):
            if datablock not in old and getattr(datablock, "users", 0) == 0:
                try:
                    collection.remove(datablock)
                except Exception:
                    pass


class OBJECT_OT_bakedown_rigimport(bpy.types.Operator):
    bl_idname = "object.bakedown_rigimport"
    bl_label = "Import rig template"
    bl_description = "Import a skinned FBX and use it as the rig template"
    bl_options = {'REGISTER'}

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')
    filter_glob: bpy.props.StringProperty(default="*.fbx;*.FBX", options={'HIDDEN'})

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not self.filepath.lower().endswith(".fbx"):
            self.report({'ERROR'}, _tr("An FBX file is required"))
            return {'CANCELLED'}
        before = _capture_import_state()
        # Work around a Blender 5.1 FBX importer bug: it writes lamp.cycles.cast_shadow,
        # which does not exist → crash on lights. The type is not in bpy.types, so get it
        # from a temporary light and temporarily add the missing property.
        RT = None
        probe = bpy.data.lights.new("__bd_probe", 'POINT')
        try:
            cyc = getattr(probe, 'cycles', None)
            if cyc is not None and not hasattr(cyc, 'cast_shadow'):
                RT = type(cyc)
                RT.cast_shadow = bpy.props.BoolProperty(name="cast_shadow", default=True)
        except Exception:
            RT = None
        finally:
            bpy.data.lights.remove(probe)
        try:
            bpy.ops.import_scene.fbx(filepath=self.filepath)
        except Exception as e:
            _cleanup_import_delta(before)
            self.report({'ERROR'}, _tr("Import failed: {}").format(e))
            return {'CANCELLED'}
        finally:
            if RT is not None:
                try:
                    del RT.cast_shadow
                except Exception:
                    pass

        new = [ob for ob in bpy.data.objects if ob not in before["objects"]]
        # drop imported lights/cameras — they are not needed and clutter the scene
        for ob in list(new):
            if ob.type in {'LIGHT', 'CAMERA'}:
                bpy.data.objects.remove(ob, do_unlink=True)
                new.remove(ob)
        tmpl = next((ob for ob in new if ob.type == 'MESH'
                     and any(m.type == 'ARMATURE' and m.object for m in ob.modifiers)), None)
        if tmpl is None:
            _cleanup_import_delta(before)
            self.report({'WARNING'}, _tr("No skinned mesh was found in the FBX"))
            return {'CANCELLED'}
        context.scene.bakedown.rig_template = tmpl
        self.report({'INFO'}, _tr("Template loaded: {}").format(tmpl.name))
        return {'FINISHED'}


def _meshes_coincide(a, b):
    """Do the meshes coincide in space (same model)? Compared by vertex POSITION,
    not by count — an FBX round trip splits vertices at UV seams, so counts lie."""
    from mathutils.kdtree import KDTree
    av = a.data.vertices
    bv = b.data.vertices
    if not av or not bv:
        return False
    amw = a.matrix_world
    bmw = b.matrix_world
    kd = KDTree(len(av))
    for i, v in enumerate(av):
        kd.insert(amw @ v.co, i)
    kd.balance()
    n = len(bv)
    step = max(1, n // 400)
    maxd = 0.0
    for i in range(0, n, step):
        _, _, dist = kd.find(bmw @ bv[i].co)
        if dist is not None and dist > maxd:
            maxd = dist
    diag = max(1e-6, b.dimensions.length)
    return maxd < 0.02 * diag   # every vertex of b lies on a's surface → same model


class OBJECT_OT_bakedown_rigtransfer(bpy.types.Operator):
    bl_idname = "object.bakedown_rigtransfer"
    bl_label = "Transfer rig"
    bl_description = "Transfer armature and weights from the template to the active mesh"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        o = context.active_object
        pg = context.scene.bakedown
        return bool(o and o.type == 'MESH' and pg.rig_template and pg.rig_template != o)

    def execute(self, context):
        pg = context.scene.bakedown
        tgt = context.active_object
        tmpl = pg.rig_template
        if tmpl is None or tmpl.type != 'MESH':
            self.report({'ERROR'}, _tr("Select a rigged mesh template"))
            return {'CANCELLED'}
        # find the armature robustly: modifier → parent → the only armature in the scene
        arm = next((m.object for m in tmpl.modifiers
                    if m.type == 'ARMATURE' and m.object is not None), None)
        if arm is None and tmpl.parent is not None and tmpl.parent.type == 'ARMATURE':
            arm = tmpl.parent
        if arm is None:
            arms = [a for a in bpy.data.objects if a.type == 'ARMATURE']
            if len(arms) == 1:
                arm = arms[0]
        if arm is None:
            self.report({'ERROR'}, _tr("No armature was found on the template"))
            return {'CANCELLED'}
        if tgt.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        # weight transfer: active = source (template) → selected (target)
        bpy.ops.object.select_all(action='DESELECT')
        tgt.select_set(True)
        tmpl.select_set(True)
        # Always NEAREST — copy weights from the nearest vertex WITHOUT spatial
        # interpolation (that caused creases). Whether the meshes coincide is decided by
        # POSITION, not vertex count (FBX splits vertices at seams → counts lie).
        # CRITICAL: the source must be in its bind pose (REST). If the armature is posed
        # (animation), the source mesh is deformed and NEAREST maps to displaced vertices →
        # a vertex grabs the wrong bone (e.g. shoulder → foot) → spike. Pose is disabled meanwhile.
        pose_prev = {}
        transfer_error = None
        coincident = False
        try:
            for m in tmpl.modifiers:
                if m.type == 'ARMATURE' and m.object is not None:
                    pose_prev[m.object] = m.object.data.pose_position
                    m.object.data.pose_position = 'REST'
            if arm not in pose_prev:
                pose_prev[arm] = arm.data.pose_position
                arm.data.pose_position = 'REST'
            context.view_layer.update()

            coincident = _meshes_coincide(tmpl, tgt)
            context.view_layer.objects.active = tmpl
            result = bpy.ops.object.data_transfer(
                data_type='VGROUP_WEIGHTS', use_create=True,
                vert_mapping='NEAREST',
                layers_select_src='ALL', layers_select_dst='NAME')
            if 'FINISHED' not in result:
                raise RuntimeError(f"Blender data transfer returned {result}")
        except Exception as exc:
            transfer_error = exc
        finally:
            for armature, previous_pose in pose_prev.items():
                try:
                    armature.data.pose_position = previous_pose
                except Exception:
                    pass
            context.view_layer.update()

        if transfer_error is not None:
            self.report({'ERROR'}, _tr("Weight transfer failed: {}").format(transfer_error))
            return {'CANCELLED'}
        # Same model (coincides in space) → weights are exact, do NOT smooth.
        # Different mesh → light smoothing against nearest-copy blockiness.
        context.view_layer.objects.active = tgt
        bpy.ops.object.select_all(action='DESELECT')
        tgt.select_set(True)
        try:
            if not coincident:
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', factor=0.5, repeat=2)
                bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.vertex_group_normalize_all(lock_active=False)
        except Exception:
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                pass
        # armature modifier + parent on the target
        if not any(m.type == 'ARMATURE' and m.object == arm for m in tgt.modifiers):
            am = tgt.modifiers.new("Armature", 'ARMATURE')
            am.object = arm
        mw = tgt.matrix_world.copy()
        tgt.parent = arm
        tgt.matrix_world = mw
        bpy.ops.object.select_all(action='DESELECT')
        tgt.select_set(True)
        context.view_layer.objects.active = tgt
        self.report({'INFO'}, _tr("Rig transferred from {} ").format(tmpl.name))
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Panel
# ---------------------------------------------------------------------------
class VIEW3D_PT_bakedown(bpy.types.Panel):
    bl_label = "BakeDown  ·  v1.2.2"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BakeDown'

    def _draw_target(self, layout, pg):
        layout.row(align=True).prop(pg, 'target_mode', expand=True)
        if pg.target_mode == 'FACES':
            col = layout.column(align=True)   # align → no gap between the slider and presets
            col.prop(pg, 'target_faces')
            pr = col.row(align=True)
            for lbl, val in (("1K", 1000), ("3K", 3000), ("5K", 5000),
                             ("10K", 10000), ("20K", 20000)):
                op = pr.operator("wm.context_set_int", text=lbl,
                                 depress=(pg.target_faces == val))
                op.data_path = "scene.bakedown.target_faces"
                op.value = val
                op.relative = False
        else:
            layout.prop(pg, 'target_distortion')

    def _draw_distort(self, layout, o, before_on, has_mesh):
        if before_on:
            layout.row().label(text=_tr("Original"), icon='INFO')
        elif has_mesh and "bakedown_distort_mm" in o:
            mm = o["bakedown_distort_mm"]
            dp = o.get("bakedown_distort_pct", 0.0)
            bad = dp > 0.5
            rr = layout.row(); rr.alert = bad
            rr.operator('object.bakedown_distort_info',
                        text=_tr("Approx. distortion: {:.1f} mm ({:.2f}%)").format(mm, dp),
                        icon='KEYTYPE_EXTREME_VEC' if bad else 'KEYTYPE_JITTER_VEC',
                        emboss=False)

    def _draw_rig(self, body, pg):
        box = body.box()
        box.label(text=_tr("Rig transfer from template"), icon='ARMATURE_DATA')
        srow = box.row(align=True)
        srow.prop(pg, 'rig_template', text=_tr("Template"))
        srow.operator('object.bakedown_rigimport', text="", icon='FILEBROWSER')
        r = box.row(); r.scale_y = 1.4
        r.operator('object.bakedown_rigtransfer', text=_tr("Transfer rig"), icon='BONE_DATA')

    def _draw_lod(self, context, body, pg, o, has_mesh):
        # LOD0 is always counted from the BASE object (the active one may be a LOD)
        base_name = _lod_base_name(o)
        base_obj = bpy.data.objects.get(base_name) if base_name else None
        base_poly = (_triangle_count_object(base_obj)
                     if (base_obj and base_obj.type == 'MESH') else
                     (_triangle_count_object(o) if has_mesh else 0))
        can_gen = bool(has_mesh and (o.get("bakedown_simplified") or o.get("bakedown_lod_of")))
        coll = bpy.data.collections.get(f"{base_name}_LODs") if base_name else None
        # actual generated LODs: level → (triangles, distortion %)
        dmap = {}
        if coll is not None:
            for ob in coll.objects:
                level = ob.get("bakedown_lod_level") or ob.name.split("_")[-1]
                dmap[level] = (_triangle_count_object(ob),
                               ob.get("bakedown_distort_pct"))

        box = body.box()
        box.row(align=True).prop(pg, 'lod_preset', expand=True)   # Strategy/3D Shooter/Mobile/Custom buttons

        total = base_poly
        # LOD0 (always, 100%)
        r = box.row(align=True)
        r.label(text="LOD0", icon='MOD_DECIM')
        r.label(text=f"{base_poly:,}")
        if 'LOD0' in dmap:
            r.prop_enum(pg, 'lod_preview', 'LOD0', text="", icon='HIDE_OFF')

        for on_prop, pct_prop, name in (('lod1_on', 'lod1_pct', 'LOD1'),
                                        ('lod2_on', 'lod2_pct', 'LOD2'),
                                        ('lod3_on', 'lod3_pct', 'LOD3')):
            enabled = getattr(pg, on_prop)
            r = box.row(align=True)
            r.prop(pg, on_prop)                       # checkbox + LODn label
            sub = r.row(align=True); sub.enabled = enabled
            sub.prop(pg, pct_prop, text="")
            if name in dmap:
                fp, dp = dmap[name]
                sub.label(text=(f"{fp:,} · {dp:.2f}%" if dp is not None else f"{fp:,}"))
                r.prop_enum(pg, 'lod_preview', name, text="", icon='HIDE_OFF')
            else:
                sub.label(text=f"≈{int(base_poly * getattr(pg, pct_prop) / 100):,}")
            if enabled:
                total += int(base_poly * getattr(pg, pct_prop) / 100)

        box.label(text=_tr("Total in file: ~{:,} triangles").format(total), icon='PLUGIN')
        if coll is not None and base_obj is not None:
            lods = [ob for ob in coll.objects if ob.get("bakedown_lod_of") == base_name]
            if _lod_state(base_obj, lods) == 'STALE':
                warn = box.row(); warn.alert = True
                warn.label(text=_tr("LODs are out of date — regenerate"), icon='ERROR')

        r = body.row(); r.scale_y = 1.4
        r.enabled = can_gen
        r.operator('object.bakedown_lod', text=_tr("Generate LOD"), icon='MOD_DECIM')
        if not can_gen:
            body.label(text=_tr("Run Simplify first"), icon='INFO')

        # export the whole LOD collection (Unity LODGroup)
        er = body.row(); er.scale_y = 1.2
        er.enabled = coll is not None
        er.operator('object.bakedown_export', text=_tr("Export LODs"), icon='EXPORT')

    def draw(self, context):
        L = self.layout
        pg = context.scene.bakedown
        o = context.active_object
        has_mesh = bool(o and o.type == 'MESH')
        bk = bpy.data.meshes.get(o.get('bakedown_orig_mesh') or "") if has_mesh else None
        has_backup = bool(bk)
        active_result = bool(has_mesh and o.get("bakedown_simplified") and has_backup)
        needs_bake = _needs_bake(o, pg)
        before_on = _comparison_object_for(o) is not None

        L.row(align=True).prop(pg, 'ui_mode', expand=True)
        if has_mesh and len(context.selected_objects) > 1:
            info = L.box()
            info.label(text=_tr("Active object only"), icon='RESTRICT_SELECT_OFF')
            info.label(text=_tr("Only the active mesh will be processed; other selected objects remain unchanged."))

        box = L.box()
        if has_mesh:
            cur = _triangle_count_object(o)
            if bk:
                orig = _triangle_count_mesh(bk)
                pctf = (1.0 - cur / orig) * 100.0 if orig else 0.0
                box.label(text=_tr("Triangles: {:,} → {:,} (−{:.0f}%)").format(orig, cur, pctf), icon='MESH_DATA')
            else:
                box.label(text=_tr("Triangles: {:,}").format(cur), icon='MESH_DATA')
            self._draw_distort(box, o, before_on, has_mesh)
        else:
            box.label(text=_tr("Select a mesh object"), icon='ERROR')

        inspecting = False
        sp = context.space_data
        if sp and sp.type == 'VIEW_3D':
            inspecting = (sp.shading.type == 'SOLID' and sp.shading.light == 'MATCAP'
                          and sp.overlay.show_wireframes)

        body = L.column()
        body.enabled = has_mesh

        if pg.ui_mode == 'RIG':
            self._draw_rig(body, pg)
        elif pg.ui_mode == 'LOD':
            self._draw_lod(context, body, pg, o, has_mesh)
        else:
            # STEP 1
            b1 = body.box()
            hdr = b1.row(align=True)
            hdr.label(text=_tr("1 — Simplify geometry"), icon='MOD_DECIM')
            hr = hdr.row(align=True); hr.alignment = 'RIGHT'; hr.enabled = active_result
            hr.operator('object.bakedown_reset', text="", icon='LOOP_BACK')
            row = b1.row(); row.alignment = 'LEFT'
            row.prop(pg, 'show_adv_decimate', text=_tr("Settings"),
                     icon='TRIA_DOWN' if pg.show_adv_decimate else 'TRIA_RIGHT', emboss=False)
            if pg.show_adv_decimate:
                c = b1.column(align=True)
                c.prop(pg, 'remove_interior')
                c.prop(pg, 'dissolve_angle')
                c.prop(pg, 'do_dissolve_faces')
                c.prop(pg, 'fill_holes')
                c.prop(pg, 'final_dissolve')
                c.prop(pg, 'planar_snap')
                c.prop(pg, 'triangulate_output')
            self._draw_target(b1, pg)
            r = b1.row(align=True); r.scale_y = 1.3
            fr = r.row(align=True); fr.scale_x = 0.7
            fr.operator('object.bakedown_inspect',
                        text=_tr("Object") if inspecting else _tr("Shape"),
                        icon='SHADING_WIRE', depress=inspecting)
            r.operator('object.bakedown_decimate', text=_tr("Simplify"), icon='MOD_DECIM')

            # STEP 2
            b2 = body.box()
            b2.label(text=_tr("2 — Texture"), icon='TEXTURE')
            row = b2.row(); row.alignment = 'LEFT'
            row.prop(pg, 'show_adv_bake', text=_tr("Settings"),
                     icon='TRIA_DOWN' if pg.show_adv_bake else 'TRIA_RIGHT', emboss=False)
            if pg.show_adv_bake:
                c = b2.column(align=True)
                c.row(align=True).prop(pg, 'bake_resolution', expand=True)
                c.prop(pg, 'bake_extrusion')
                c.prop(pg, 'bake_sharpen', slider=True)
                if pg.bake_normal:
                    c.prop(pg, 'bake_normal_strength', slider=True)
                c.prop(pg, 'bake_normal')
            if pg.is_baking and _BAKE_RUNNING:
                b2.progress(factor=pg.bake_progress,
                            text=f"{pg.bake_stage}… {int(pg.bake_progress * 100)}%")
                cr = b2.row(); cr.scale_y = 1.1; cr.alert = True
                cr.operator('object.bakedown_bake_cancel', text=_tr("Cancel"), icon='CANCEL')
            else:
                r = b2.row(align=True); r.scale_y = 1.4
                cr = r.row(align=True); cr.scale_x = 0.7
                cr.enabled = active_result or before_on
                cr.operator('object.bakedown_compare',
                            text=_tr("Hide comparison") if before_on else _tr("Compare"),
                            icon='ARROW_LEFTRIGHT', depress=before_on)
                br = r.row(align=True); br.enabled = needs_bake
                br.operator('object.bakedown_bake', text=_tr("Bake"), icon='RENDER_STILL')

            # Finish (export / delete backup)
            b3 = body.box()
            r = b3.row(align=True); r.scale_y = 1.2
            dl = r.row(align=True); dl.enabled = active_result; dl.alert = True
            dl.operator('object.bakedown_finalize', text="", icon='TRASH')
            r.operator('object.bakedown_export', text=_tr("Export"), icon='EXPORT')


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------
_classes = (
    BakeDownSettings,
    OBJECT_OT_bakedown_decimate,
    OBJECT_OT_bakedown_reset,
    OBJECT_OT_bakedown_inspect,
    OBJECT_OT_bakedown_distort_info,
    OBJECT_OT_bakedown_compare,
    OBJECT_OT_bakedown_export,
    OBJECT_OT_bakedown_bake_cancel,
    OBJECT_OT_bakedown_finalize,
    OBJECT_OT_bakedown_bake,
    OBJECT_OT_bakedown_lod,
    OBJECT_OT_bakedown_rigimport,
    OBJECT_OT_bakedown_rigtransfer,
    VIEW3D_PT_bakedown,
)


def register():
    try:
        bpy.app.translations.unregister(__name__)
    except Exception:
        pass
    bpy.app.translations.register(__name__, _TRANSLATIONS)
    for c in _classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.bakedown = bpy.props.PointerProperty(type=BakeDownSettings)
    if _bakedown_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_bakedown_load_post)


def unregister():
    if _bakedown_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_bakedown_load_post)
    if hasattr(bpy.types.Scene, "bakedown"):
        del bpy.types.Scene.bakedown
    for c in reversed(_classes):
        try:
            bpy.utils.unregister_class(c)
        except Exception:
            pass
    try:
        bpy.app.translations.unregister(__name__)
    except Exception:
        pass


if __name__ == "__main__":
    register()
