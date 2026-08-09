# Configuration

Paramètres → Intégrations → Ajouter une intégration → **Proxmox VE**

| Champ | Description |
|---|---|
| Méthode d'authentification | `pam` (Linux), `pve` (Proxmox), `other` (royaume custom) |
| Hôte | IP ou hostname du nœud |
| Nom d'utilisateur | ex. `root@pam` |
| Port | 8006 (défaut) |
| Utiliser un jeton d'API | cochez pour une auth par token |
| Vérifier SSL | désactivez si certificat auto-signé |

## Options

- **Intervalle de rafraîchissement** : secondes entre deux polls (défaut 60, min 5)
