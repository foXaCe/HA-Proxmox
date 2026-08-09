# Installation

## HACS (recommandé)

1. Dans HACS → « … » → Custom repositories
2. Ajoutez `https://github.com/foXaCe/HA-Proxmox` (catégorie : Integration)
3. Recherchez « Proxmox VE » → Installez
4. Redémarrez Home Assistant

## Manuel

1. Copiez le dossier `custom_components/proxmoxve/` dans votre dossier `config/custom_components/`
2. Redémarrez Home Assistant
3. Retirez toute référence à l'intégration core `proxmoxve` si elle était installée
