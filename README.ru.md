<div align="center">

# BakeDown

**Тяжёлые 3D-модели → игровые ассеты прямо в Blender.**

[English](README.md) · **Русский** · [Español](README.es.md) · [Deutsch](README.de.md) · [简体中文](README.zh-CN.md)

[![Blender 4.5+](https://img.shields.io/badge/Blender-4.5%2B-E87D0D?logo=blender&logoColor=white)](https://www.blender.org/download/)
[![Latest release](https://img.shields.io/github/v/release/keeraa/bakedown?label=release&color=2ea44f)](https://github.com/keeraa/bakedown/releases/latest)
[![Tests](https://github.com/keeraa/bakedown/actions/workflows/tests.yml/badge.svg)](https://github.com/keeraa/bakedown/actions/workflows/tests.yml)
[![License: GPL-3.0-or-later](https://img.shields.io/badge/license-GPL--3.0--or--later-blue)](LICENSE)
[![UI: EN · RU · ES · DE · ZH](https://img.shields.io/badge/UI-EN%20·%20RU%20·%20ES%20·%20DE%20·%20ZH-555)](#языки-интерфейса)
[![AI agents ready](https://img.shields.io/badge/AI%20agents-ready-8A2BE2)](AGENTS.md)

<img src="docs/images/bakedown_hero.gif" width="640" alt="Оригинал 49 988 треугольников и BakeDown 2 734 треугольника: выглядит так же, треугольников на 95% меньше">

**−95% треугольников · выглядит так же · PBR-текстуры запекаются за секунды**

[**⬇ Скачать**](https://github.com/keeraa/bakedown/releases/latest) · [▶ Демо на 40 секунд](docs/media/bakedown_demo.mp4) · [🤖 Для AI-агентов](AGENTS.md) · [❓ Вопросы и ответы](docs/FAQ.md)

</div>

---

BakeDown — бесплатный аддон для Blender, который превращает **любую тяжёлую модель** — из нейросетей (Hunyuan, Meshy, Tripo, Rodin), 3D-скан, скульпт, high-poly модель из маркетплейса или китбаша — в лёгкий текстурированный игровой ассет. Он упрощает меш, запекает на него текстуры оригинала, делает LOD, переносит риг и экспортирует в Unity, Unreal Engine или glTF. Работа недеструктивна: оригинал сохраняется, **Сброс** возвращает его.

## Быстрый старт

1. **Скачайте** `bakedown.py` из [последнего релиза](https://github.com/keeraa/bakedown/releases/latest).
2. В Blender: **Edit → Preferences → Add-ons → Install from Disk…**, выберите `bakedown.py`, включите **BakeDown — Game Asset Optimizer**.
3. Выделите модель, нажмите **N**, откройте вкладку **BakeDown**: **Упростить → Текстурировать → Экспорт**.

Персонажи: **Упростить → Текстурировать → Риг → LOD → Экспорт** (LOD после рига наследуют скелет).

## Почему BakeDown

| | Вручную в Blender | **BakeDown** |
|---|---|---|
| Сохранить оригинал и всё откатить | дублировать и следить самому | ✅ автоматическая копия, **Сброс** в один клик |
| Выбрать результат | угадывать коэффициент Decimate | ✅ цель по треугольникам **или** по допустимому искажению, в мм и % |
| Почистить AI-меш или скан | сварка, мусор, нормали, split-нормали вручную | ✅ встроено в **Упростить** |
| Сохранить внешний вид | настроить 4 запекания selected-to-active, UV, материалы | ✅ Base Color, Roughness, Metallic, Normal в один клик, откат при отмене |
| LOD | дублировать, упрощать, перепривязывать, переименовывать | ✅ пресеты LOD0–LOD3, общие текстуры, учёт скелета, предупреждение об устаревших LOD |
| Экспорт в движок | помнить оси, масштаб, сглаживание, формат нормалей | ✅ пресеты Unity / Unreal / glTF |
| Автоматизация | писать и отлаживать `bpy`-скрипты | ✅ Python API и командная строка с отчётом JSON |

Персонаж на 50 тысяч треугольников превращается в 2,7 тысячи с запеканием PBR 2K, четырьмя LOD и FBX для Unity **примерно за 5 секунд**.

## Сравните сами

| С текстурами | Сетка |
|---|---|
| ![Целиком, с текстурами](docs/images/compare_full_textured.jpg) | ![Целиком, сетка](docs/images/compare_full_wireframe.jpg) |
| ![Крупно, с текстурами](docs/images/compare_closeup_textured.jpg) | ![Крупно, сетка](docs/images/compare_closeup_wireframe.jpg) |

Оригинал (слева) и BakeDown (справа): 49 988 → 2 734 треугольника, искажение ≈7,3 мм (0,56%), запекание 4K.

## Что внутри

- **Упрощение** — цель по реальным треугольникам или по бюджету искажения, чистка AI-мешей и сканов, слияние плоских граней, коллапс; по желанию заполнение дыр, удаление внутренних граней, выравнивание, триангуляция. Меняется только активный меш.
- **Запекание** — Cycles-запекание Base Color, Roughness, Metallic и tangent Normal на новую UV-развёртку в 1K/2K/4K; авто-дистанция луча, живая сила рельефа, резкость; прогресс, отмена по Esc, полный откат.
- **LOD** — LOD0–LOD3 с пресетами Стратегия / 3D-шутер / Мобильные / Свой, один набор текстур, учёт скелета, имена `_LOD0…3` для LOD Group в Unity.
- **Перенос рига** — импорт заскиненного FBX-шаблона и перенос скелета и весов на активный меш.
- **Экспорт** — FBX для Unity, FBX для Unreal, самодостаточный GLB; PNG-карты рядом с моделью, упаковка ORM, инверсия нормалей в формат DirectX для Unreal.
- **Осмотр** — режим «Форма» (MatCap + каркас) и «Сравнить» оригинал ↔ результат.

## Работа с нейросетями (AI-агентами)

AI-агенты (Claude, ChatGPT, Codex, Blender MCP…) могут управлять BakeDown вместо того, чтобы сочинять собственный код для Blender: в тестах автора это давало заметно лучший результат. Оба способа возвращают отчёт в JSON (треугольники, искажение, запечённые карты, LOD, экспортированные файлы):

```bash
blender -b --factory-startup --python tools/bakedown_cli.py -- model.glb --out ./out --triangles 3000 --resolution 2048 --engine unity
```

```python
import bakedown
report = bakedown.process(obj, triangles=3000, resolution=2048, export_dir="/tmp/out", engine="UNITY")
```

Инструкция для агентов: [AGENTS.md](AGENTS.md).

## Языки интерфейса

Английский, русский, испанский, немецкий и упрощённый китайский — Blender переключает автоматически через **Preferences → Interface → Translation**.

## Вопросы и ответы

Цели по треугольникам, искажение, чёрные пятна после запекания, персонажи с ригом, особенности Unity и Unreal, ограничения: [docs/FAQ.md](docs/FAQ.md) (на английском).

## Участие в разработке

Сообщения об ошибках и идеи приветствуются — [создайте issue](https://github.com/keeraa/bakedown/issues/new/choose). Разработчикам: [CONTRIBUTING.md](CONTRIBUTING.md), [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md), [docs/VERIFICATION.md](docs/VERIFICATION.md), [CHANGELOG.md](CHANGELOG.md).

## Лицензия

GPL-3.0-or-later © Kirill Migachev. См. [LICENSE](LICENSE).
