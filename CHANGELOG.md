# Changelog

Toutes les modifications notables de cette intégration custom sont documentées ici.

## 2.0.0 — 2026-08-09

Refactor complet depuis le composant legacy de Home Assistant Core (quality_scale « legacy »).

### Ajouts
- **Options flow** : intervalle de rafraîchissement configurable (défaut 60 s, min 5 s).
- **`system_health`** : version du client et nombre d'instances dans l'écran Système.
- **Traductions françaises complètes** (`translations/fr.json`, vouvoiement, parité 150 clés).
- **Manifest modernisé** : `integration_type: hub`, `quality_scale: silver`, `version`.

### Structure
- Découpage modulaire : `api/` (client, exceptions, models), `devices/` (node, vm, container, storage), plateformes allégées.
- `sanitize_config_entry` et `is_granted` déplacés dans `helpers.py` (fonctions pures).
- Exceptions API typées (`ProxmoxAuthError`, `ProxmoxConnectionError`, …).

### Correctifs
- **Boutons LXC/VM** : route API corrigée vers `/status/{command}` (les boutons renvoyaient `501 Not Implemented`).
- Client API délégué à l'executor (jamais dans la boucle d'événements).
- Logging nettoyé : aucun identifiant/secret en clair.

### Qualité
- 101 tests, coverage ≥ 95 %.
- ruff + mypy verts, hassfest validé.
- Perf : import module 618 ms → 606 ms, coordinator 289 ms → 241 ms.
