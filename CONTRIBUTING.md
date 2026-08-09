# Contributing

Merci de votre intérêt pour **Proxmox VE** !

## Bug reports

Utilisez le [bug report template](.github/ISSUE_TEMPLATE/bug_report.yml). Indiquez :
- La version de Home Assistant
- La version de l'intégration
- Les logs pertinents (Settings → System → Logs, filtrés par `proxmoxve`)
- Le dump diagnostics si possible

## Feature requests

Utilisez le [feature request template](.github/ISSUE_TEMPLATE/feature_request.yml).

## Pull requests

1. Forkez le dépôt.
2. Créez une branche dédiée : `git checkout -b feat/ma-feature`
3. Installez le runner pre-commit : `pipx install prek && prek install`
4. Écrivez le code + les tests : `pytest --cov=custom_components/proxmoxve`
5. Lint : `ruff check . && ruff format .`
6. Type check : `mypy custom_components/proxmoxve`
7. Validez avec hassfest : `docker run --rm -v "$PWD":/github/workspace ghcr.io/home-assistant/hassfest:latest`
8. Commitez en [conventional commits](https://www.conventionalcommits.org/) : `feat: …`, `fix: …`, `docs: …`
9. Poussez et ouvrez une PR vers `main`.

## Convention de commits

```
feat: ajoute le support des captures réseau
fix: corrige le crash quand l'uptime est absent
docs: README — précise la configuration token
chore(deps): bump proxmoxer from 2.3.0 to 2.3.1
```

## Gestion des dépendances

Ce dépôt utilise **Renovate** (et non Dependabot). Les PR de mise à jour sont
ouvertes par le bot `@renovate[bot]`. Voir le [dashboard Renovate](../../issues?q=is:issue+author:app/renovate).

## Setup local

```bash
pip install -r requirements_dev.txt
pipx install prek   # ou brew install j178/prek/prek
prek install
```

(prek est un drop-in Rust de pre-commit, 10× plus rapide. Si vous préférez la version Python : `pipx install pre-commit`.)
