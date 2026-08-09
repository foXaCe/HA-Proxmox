# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.0.0 (2026-08-09)


### Bug Fixes

* CI tags (codecov v7, cache v6, stale v11, gh-release v3, osv-scanner v2.5.0), add proxmoxer to test reqs, add brand assets ([c52227e](https://github.com/foXaCe/HA-Proxmox/commit/c52227e26f4256b802ba98e138ca17974cd1d7d7))
* hacs zip_release and release workflow zip structure ([74db6e4](https://github.com/foXaCe/HA-Proxmox/commit/74db6e483f15251ebd2013bd2ddbd0369a4c30a6))
* osv-scanner scan-args (remove unsupported --skip-git) ([0d2f8a4](https://github.com/foXaCe/HA-Proxmox/commit/0d2f8a4c97a1c61c9148a48b5060dfbe5ba379c5))
* release-please config-file/manifest-file inputs for v5 ([cdf4509](https://github.com/foXaCe/HA-Proxmox/commit/cdf450969957692142493a38e2c4e55afa8abbd1))
* remove mypy from pre-commit hooks (528MiB build exceeds CI limit); covered by dedicated CI lint job ([9fa6ddf](https://github.com/foXaCe/HA-Proxmox/commit/9fa6ddf6f5a90d8e18d5f7fc0d39585de377cb01))
* security audit osv scanner reports without failing (test transitive CVE non-resolvable) ([5c4afd6](https://github.com/foXaCe/HA-Proxmox/commit/5c4afd6c5d822107ac6d7d53ba0b8d043da07e6c))

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
