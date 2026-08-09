# Proxmox VE

Intégration custom Home Assistant pour piloter et surveiller un ou plusieurs serveurs Proxmox VE, dérivée du composant core (refactorée, testée, qualité Silver).

## Fonctionnalités

- Capteurs : CPU, mémoire, disque, uptime, statut, réseau, backups (par nœud, VM, conteneur, stockage)
- Capteurs binaires : statut nœud/VM/conteneur, état backup, stockage actif/activé/partagé
- Boutons : contrôle puissance nœud/VM/conteneur, création d'instantanés
- Auth par mot de passe ou jeton d'API
- Intervalle de rafraîchissement configurable

## Configuration

1. Paramètres → Intégrations → Ajouter une intégration → **Proxmox VE**
2. Renseignez hôte, port (8006), utilisateur (ex. `root@pam`), mot de passe ou jeton
3. Désactivez la vérification SSL si certificat auto-signé

## Installation

Via HACS (repo custom : `https://github.com/foXaCe/HA-Proxmox`) ou manuellement en copiant `custom_components/proxmoxve/`.
