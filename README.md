# Proxmox VE — intégration custom Home Assistant

Intégration Home Assistant **custom** pour piloter et surveiller un ou plusieurs serveurs [Proxmox VE](https://www.proxmox.com/), refactorée depuis la version legacy du core (quality_scale « legacy ») vers une structure modulaire testée.

> ⚠️ **Override du core** : le domaine `proxmoxve` est identique à l'intégration officielle. Une fois installée, elle la **remplace**. Si vous l'installez via HACS, retirez toute référence à l'intégration core avant.

## Installation

### HACS (recommandé)
1. Ajoutez ce dépôt à HACS → Intégrations custom.
2. Recherchez « Proxmox VE » et installez.
3. Redémarrez Home Assistant.

### Manuel
Copiez le dossier `custom_components/proxmoxve/` dans votre dossier `custom_components/` local puis redémarrez HA.

## Configuration

Paramétrez via **Paramètres → Intégrations → Ajouter une intégration → Proxmox VE** :

| Champ | Description |
|---|---|
| Méthode d'authentification | `pam` (utilisateur Linux), `pve` (utilisateur Proxmox) ou `other` (royaume custom) |
| Hôte | IP ou hostname du nœud Proxmox VE |
| Nom d'utilisateur | ex. `root@pam` |
| Port | défaut `8006` |
| Utiliser un jeton d'API | cochez pour une auth par token |
| Vérifier SSL | désactivez uniquement en cas de certificat auto-signé |

### Options (après configuration)
- **Intervalle de rafraîchissement** : secondes entre deux cycles d'interrogation de l'API (défaut 60 s, minimum 5 s).

## Entités

Par nœud, VM (QEMU), conteneur (LXC) et stockage :

- **Capteurs** : CPU, mémoire, disque, uptime, statut, réseau entrant/sortant, dernier backup, durée de backup, pourcentages d'utilisation.
- **Capteurs binaires** : statut du nœud/VM/conteneur, état du backup, stockage actif/activé/partagé.
- **Boutons** : reboot/arrêt du nœud, start all/stop all/suspend all, et par VM/conteneur : start, stop, restart, hibernate, resume, reset, shutdown, création d'instantané.

Les entités de diagnostic sont marquées `entity_category: diagnostic` et plusieurs sont désactivées par défaut (activables dans Paramètres → Entités).

## Remarques

- **Authentification par mot de passe** : le mot de passe est stocké chiffré dans la configuration HA.
- **Permissions** : les entités/boutons sont créés selon les permissions (`Sys.Audit`, `VM.PowerMgmt`, `VM.Snapshot`…) de l'utilisateur configuré. Utilisez un utilisateur/token dédié avec les permissions minimales.
- **Backups** : le capteur « Dernière sauvegarde » ne reflète que la dernière tâche `vzdump` terminée sur le nœud.
- **Client synchrone** : la bibliothèque `proxmoxer` est synchrone ; tous les appels API sont délégués à un executor pour ne pas bloquer la boucle d'événements.

## Dépannage

- **Cannot connect** : vérifiez hôte/port et que l'API est accessible (`https://<hôte>:8006`).
- **SSL check failed** : certificat auto-signé → désactivez « Vérifier SSL ».
- **Invalid auth** : vérifiez utilisateur/royaume ou token (format `user@realm!tokenid`).
- **Aucun nœud/VM trouvé** : l'utilisateur n'a pas les permissions d'audit minimales.
- **Bouton 501 Not Implemented** : ancienne version de l'intégration — mettez à jour (le correctif route `/status/{command}` est inclus).

## Tests

```bash
pytest -q --cov=custom_components.proxmoxve
```

## Remerciements

Cette intégration est dérivée du composant **`proxmoxve` de Home Assistant Core**, dont elle reprend l'architecture (coordinator, entités par type de device, config flow) avant un refactor complet :

- **Source d'origine** : [`home-assistant/core` — `homeassistant/components/proxmoxve`](https://github.com/home-assistant/core/tree/dev/homeassistant/components/proxmoxve)
- **Codeowners d'origine** : [@Corbeno](https://github.com/Corbeno), [@erwindouna](https://github.com/erwindouna), [@CoMPaTech](https://github.com/CoMPaTech)
- **Client API** : [proxmoxer](https://github.com/proxmoxer/proxmoxer)
- **Documentation officielle** : [Proxmox VE integration](https://www.home-assistant.io/integrations/proxmoxve/)

Merci aux mainteneurs de Home Assistant Core et de proxmoxer pour leur travail, qui a rendu cette intégration possible.

## Licence

Ceci est une intégration custom à usage personnel, dérivée du composant `proxmoxve` de Home Assistant Core (Apache-2.0).
