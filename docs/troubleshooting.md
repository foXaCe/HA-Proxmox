# Dépannage

| Problème | Solution |
|---|---|
| Cannot connect | Vérifiez hôte/port, API accessible sur `https://<hôte>:8006` |
| SSL check failed | Certificat auto-signé → désactivez « Vérifier SSL » |
| Invalid auth | Vérifiez utilisateur/royaume ou token (`user@realm!tokenid`) |
| Aucun nœud/VM trouvé | L'utilisateur manque de permissions d'audit |
| Bouton 501 | Mettez à jour l'intégration (correctif route `/status/{command}`) |
