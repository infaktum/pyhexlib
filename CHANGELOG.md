# Changelog

Alle nennenswerten Änderungen an `pyhexlib` werden hier dokumentiert. Das Format
folgt [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Fixed

- Die angenäherte Richtung zwischen entfernten Hexfeldern liefert wieder einen `Direction`-Wert.
- Umgekehrte Clipping-Grenzen wählen wieder alle Hexfelder im angegebenen Bereich aus.
- Terrain-Ebenen geben für Wasser den gespeicherten Wert zurück, ohne eine Debug-Ausgabe zu schreiben.

### Changed

- Paketversion, Python-Anforderung und Abhängigkeiten werden einheitlich über `pyproject.toml` verwaltet.

## [0.1.1]

- Bestehender Paketstand vor Einführung dieses Changelogs.
