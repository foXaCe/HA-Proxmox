# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1](https://github.com/foXaCe/HA-Proxmox/compare/v2.0.0...v2.0.1) (2026-08-10)


### Performance Improvements

* reuse cached nodes from connect() in first fetch to speed up boot ([2da4fc6](https://github.com/foXaCe/HA-Proxmox/commit/2da4fc65873dedd0422c8e8c3810e13922c66638))

## [Unreleased]

## [2.0.0] - 2026-08-09

Refactor complet depuis le composant legacy de Home Assistant Core (quality_scale « legacy »).

### Added
- **Options flow** : intervalle de rafraîchissement configurable (défaut 60 s, min 5 s).
- **`system_health`** : version du client et nombre d'instances dans l'écran Système.
- **Traductions françaises complètes** (`translations/fr.json`, vouvoiement, parité 150 clés).
- **Manifest modernisé** : `integration_type: hub`, `quality_scale: silver`, `version`.

### Changed
- Découpage modulaire : `api/` (client, exceptions, models), `devices/` (node, vm, container, storage), plateformes allégées.
- `sanitize_config_entry` et `is_granted` déplacés dans `helpers.py` (fonctions pures).
- Exceptions API typées (`ProxmoxAuthError`, `ProxmoxConnectionError`, …).

### Fixed
- **Boutons LXC/VM** : route API corrigée vers `/status/{command}` (les boutons renvoyaient `501 Not Implemented`).
- Client API délégué à l'executor (jamais dans la boucle d'événements).
- Logging nettoyé : aucun identifiant/secret en clair.

### Added
- 101 tests, coverage ≥ 95 %.
- ruff + mypy verts, hassfest validé.
- Perf : import module 618 ms → 606 ms, coordinator 289 ms → 241 ms.
