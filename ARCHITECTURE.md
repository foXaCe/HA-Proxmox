# Architecture

## Vue d'ensemble

```
Proxmox VE API (REST, port 8006)
        │  proxmoxer (sync) → exécuté dans un executor
        ▼
┌─────────────────────────────┐
│ api/                        │
│  client.py   ProxmoxClient  │  connexion, auth (pam/pve/token),
│             (sync wrapper)  │  fetch nodes/VMs/LXC/storages/backups,
│  exceptions.py  exceptions │  actions power + snapshots
│  models.py      dataclasses │  NodeResources, ProxmoxNodeData
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ coordinator.py              │
│  ProxmoxCoordinator         │  DataUpdateCoordinator[dict[node, ProxmoxNodeData]]
│                             │  update_interval 60s (configurable via options)
│                             │  détection nodes/VM/container/storage ajoutés/retirés
└──────────────┬──────────────┘
               │ coordinator.data (dict) + callbacks new_*_nodes
               ▼
┌─────────────────────────────┐
│ devices/ + plateformes      │
│  node.py, vm.py,           │  EntityDescription + classes par type
│  container.py, storage.py  │  (sensor / binary_sensor / button)
│  sensor.py / binary_sensor │  async_setup_entry : instancie les entités
│  / button.py                │
└──────────────┬──────────────┘
               │
               ▼
   Entités Home Assistant (has_entity_name, CoordinatorEntity)
```

## Flux de données

1. **Setup** (`__init__.py`) : crée `ProxmoxCoordinator`, `async_config_entry_first_refresh()`, enregistre les device nodes, forward les plateformes.
2. **Polling** : le coordinator appelle `client.fetch_all_nodes()` dans un executor (proxmoxer est synchrone) toutes les `scan_interval` secondes.
3. **Diffing** : `_async_add_remove_nodes()` détecte les nodes/VMs/containers/storages nouveaux → déclenche les callbacks `new_*_callbacks` qui créent les entités, et retire les devices obsolètes.
4. **Entités** : lisent `coordinator.data` (jamais d'appel API direct). `available` = `last_update_success` ET device présent.
5. **Actions** (boutons) : exécutent le client dans un executor, erreurs API traduites en `HomeAssistantError` (translation_key).

## Structure

```
custom_components/proxmoxve/
├── __init__.py          # setup/unload/migration config entry (VERSION 3)
├── config_flow.py       # ConfigFlow (user/reauth/reconfigure) + OptionsFlow (scan_interval)
├── coordinator.py       # ProxmoxCoordinator + device_info helpers
├── const.py             # constantes + permissions (StrEnum)
├── helpers.py           # sanitize_config_entry, is_granted (pures)
├── entity.py            # classes d'entité de base + ProxmoxBaseButton
├── diagnostics.py       # diagnostics (redaction des secrets)
├── system_health.py     # info système
├── api/                 # client, exceptions typées, models
├── devices/             # descriptions + entités par type (node/vm/container/storage)
├── sensor.py            # plateforme sensor (setup uniquement)
├── binary_sensor.py     # plateforme binary_sensor
├── button.py            # plateforme button
├── strings.json         # traductions EN (source)
├── icons.json           # icônes par entité
└── translations/        # en.json, fr.json
```

## Authentification

- `pam` / `pve` : mot de passe, utilisateur `user@realm`.
- `other` : royaume custom.
- Token API : `token_name` (format `user@realm!tokenid`) + `token_value`, privilégié (pas de mot de passe stocké).

## Permissions

`is_granted()` vérifie les permissions Proxmox (`Sys.Audit`, `VM.PowerMgmt`, `VM.Snapshot`, `Sys.PowerMgmt`) sur `/vms/<id>`, `/vms` puis `/` — seules les entités/boutons autorisés sont créés.

## Limites connues

- Client `proxmoxer` synchrone → tout est délégué à un executor (Platinum inaccessible).
- L'intervalle de polling minimum est de 5 secondes (option).
