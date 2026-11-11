<div align="center">

# BakeDown

**Schwere 3D-Modelle → spielfertige Assets, direkt in Blender.**

[English](README.md) · [Русский](README.ru.md) · [Español](README.es.md) · **Deutsch** · [简体中文](README.zh-CN.md)

[![Blender 4.5+](https://img.shields.io/badge/Blender-4.5%2B-E87D0D?logo=blender&logoColor=white)](https://www.blender.org/download/)
[![Latest release](https://img.shields.io/github/v/release/keeraa/bakedown?label=release&color=2ea44f)](https://github.com/keeraa/bakedown/releases/latest)
[![Tests](https://github.com/keeraa/bakedown/actions/workflows/tests.yml/badge.svg)](https://github.com/keeraa/bakedown/actions/workflows/tests.yml)
[![License: GPL-3.0-or-later](https://img.shields.io/badge/license-GPL--3.0--or--later-blue)](LICENSE)
[![UI: EN · RU · ES · DE · ZH](https://img.shields.io/badge/UI-EN%20·%20RU%20·%20ES%20·%20DE%20·%20ZH-555)](#sprachen-der-oberfläche)
[![AI agents ready](https://img.shields.io/badge/AI%20agents-ready-8A2BE2)](AGENTS.md)

<img src="docs/images/bakedown_hero.gif" width="640" alt="Original mit 49.988 Dreiecken und BakeDown mit 3.000 Dreiecken: gleiches Aussehen, 94 % weniger Dreiecke">

**−94 % Dreiecke · gleiches Aussehen · PBR-Texturen in Sekunden gebacken**

[**⬇ Download**](https://github.com/keeraa/bakedown/releases/latest) · [🤖 Für KI-Agenten](AGENTS.md) · [❓ FAQ](docs/FAQ.md)

</div>

---

BakeDown ist ein kostenloses Blender-Add-on, das **jedes schwere Mesh** – KI-generiert (Hunyuan, Meshy, Tripo, Rodin), 3D-Scans, Sculpts, High-Poly-Modelle aus Marktplätzen oder Kitbash – in ein leichtes, texturiertes, spielfertiges Asset verwandelt. Es vereinfacht das Mesh, backt die Texturen des Originals darauf, erzeugt LODs, überträgt Rigs und exportiert nach Unity, Unreal Engine oder glTF. Nicht-destruktiv: Das Original bleibt erhalten, **Zurücksetzen** holt es zurück.

## Schnellstart

1. `bakedown.py` aus dem [neuesten Release](https://github.com/keeraa/bakedown/releases/latest) **herunterladen**.
2. In Blender: **Edit → Preferences → Add-ons → Install from Disk…**, `bakedown.py` wählen, **BakeDown — Game Asset Optimizer** aktivieren.
3. Modell auswählen, **N** drücken, Reiter **BakeDown** öffnen: **Vereinfachen → Backen → Exportieren**.

Charaktere: **Vereinfachen → Backen → Rig → LOD → Exportieren** (LODs nach dem Rig übernehmen das Skelett).

## Warum BakeDown

| | Von Hand in Blender | **BakeDown** |
|---|---|---|
| Original behalten, alles rückgängig machen | duplizieren und selbst verwalten | ✅ automatische Sicherung, **Zurücksetzen** mit einem Klick |
| Ergebnis festlegen | Decimate-Ratio raten | ✅ Ziel in Dreiecken **oder** als erlaubter Formfehler, in mm und % |
| KI-Meshes und Scans bereinigen | Verschweißen, lose Teile, Normalen, Split Normals von Hand | ✅ in **Vereinfachen** eingebaut |
| Aussehen erhalten | 5 Selected-to-Active-Bakes, UVs und Materialien einrichten | ✅ Base Color, Roughness, Metallic, Normal, AO mit einem Klick, Rollback bei Abbruch |
| LODs | duplizieren, reduzieren, neu riggen, umbenennen | ✅ LOD0–LOD3-Presets, gemeinsame Texturen, Skelett-bewusst, Warnung bei veralteten LODs |
| Engine-Export | Achsen, Skalierung, Glättung, Normal-Map-Format merken | ✅ Presets für Unity / Unreal / glTF |
| Automatisierung | `bpy`-Skripte schreiben und debuggen | ✅ Python-API und Kommandozeile mit JSON-Bericht |

Ein Charakter mit 50.000 Dreiecken wird in **etwa 7 Sekunden** zu 3.000 Dreiecken mit 2K-PBR-Bake, vier LODs und einem Unity-FBX.

Qualität wird gemessen, nicht geschätzt: [`tools/quality_eval.py`](tools/quality_eval.py) rendert Original und Ergebnis von vier Seiten und vergleicht Form, Farbe und Silhouette. Version 1.5 senkte den Fehler im vollständigen Render um das 3- bis 4-Fache bei einem stilisierten Charakter und um das 10- bis 40-Fache bei einer metallischen Skulptur – Details in [docs/VERIFICATION.md](docs/VERIFICATION.md).

## Sieh selbst

| Texturiert | Drahtgitter |
|---|---|
| ![Ganze Figur, texturiert](docs/images/compare_full_textured.jpg) | ![Ganze Figur, Drahtgitter](docs/images/compare_full_wireframe.jpg) |
| ![Nahaufnahme, texturiert](docs/images/compare_closeup_textured.jpg) | ![Nahaufnahme, Drahtgitter](docs/images/compare_closeup_wireframe.jpg) |

Original (links) und BakeDown (rechts): 49.988 → 3.000 Dreiecke, ca. 1,8 mm Verzerrung (0,14 %), 4K-Baking.

## Was drin ist

- **Vereinfachen** — Ziel in echten Dreiecken oder als Verzerrungsbudget, Bereinigung von KI-Meshes und Scans, Edge-Collapse, automatische Schattierung passend zum Original; optional Löcher füllen, Innenflächen entfernen, begradigen, triangulieren. Nur das aktive Mesh wird verändert.
- **Backen** — Cycles-Baking von Base Color, Roughness, Metallic, Tangent-Normal, Ambient Occlusion, Emission und Transparenz auf ein neues UV-Layout in 1K/2K/4K; automatische Strahldistanz, Live-Normal-Stärke, Schärfen; Fortschritt, Abbruch mit Esc, vollständiger Rollback.
- **LOD** — LOD0–LOD3 mit den Presets Strategie / 3D-Shooter / Mobil / Eigene, ein gemeinsamer Textursatz, Skelett-bewusst, Benennung `_LOD0…3` für Unity-LOD-Groups.
- **Rig-Übertragung** — geskinnte FBX-Vorlage importieren und Skelett samt Gewichten auf das aktive Mesh übertragen.
- **Export** — FBX für Unity, FBX für Unreal, eigenständiges GLB; PNG-Maps neben dem Modell, ORM-Packing mit echtem AO, glTF-Occlusion, DirectX-Normalen für Unreal.
- **Prüfen** — Form-Modus (MatCap + Drahtgitter) und Vergleichen Original ↔ Ergebnis.

## Nutzung mit KI-Agenten

KI-Agenten (Claude, ChatGPT, Codex, Blender MCP…) können BakeDown steuern, statt eigenen Blender-Code zu improvisieren – in den Tests des Autors lieferte das deutlich bessere Assets. Beide Einstiegspunkte liefern einen JSON-Bericht (Dreiecke, Verzerrung, gebackene Maps, LODs, exportierte Dateien):

```bash
blender -b --factory-startup --python tools/bakedown_cli.py -- model.glb --out ./out --triangles 3000 --resolution 2048 --engine unity
```

```python
import bakedown
report = bakedown.process(obj, triangles=3000, resolution=2048, export_dir="/tmp/out", engine="UNITY")
```

Anleitung für Agenten: [AGENTS.md](AGENTS.md) (Englisch).

## Sprachen der Oberfläche

Englisch, Russisch, Spanisch, Deutsch und vereinfachtes Chinesisch – Blender wechselt automatisch über **Preferences → Interface → Translation**.

## FAQ

Dreiecksziele, Verzerrung, schwarze Flecken nach dem Backen, geriggte Charaktere, Besonderheiten von Unity und Unreal sowie Einschränkungen: [docs/FAQ.md](docs/FAQ.md) (Englisch).

## Mitwirken

Fehlerberichte und Ideen sind willkommen – [Issue anlegen](https://github.com/keeraa/bakedown/issues/new/choose). Für Entwickler: [CONTRIBUTING.md](CONTRIBUTING.md), [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md), [docs/VERIFICATION.md](docs/VERIFICATION.md), [CHANGELOG.md](CHANGELOG.md).

## Lizenz

GPL-3.0-or-later © Kirill Migachev. Siehe [LICENSE](LICENSE).
