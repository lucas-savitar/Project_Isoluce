# Mini Task Engine

Petit moteur Python qui transforme des demandes clients structurées en tâches exploitables.

Le projet utilise uniquement la bibliothèque standard de Python.

## Lancer les tests

```bash
python -m unittest discover -s tests -v
```

## Lancer le programme

```bash
python main.py sample_requests.json
```

Le programme écrit le résultat JSON sur la sortie standard.

## Structure

- `task_engine/parser.py` valide et normalise les demandes
- `task_engine/planner.py` construit le plan de tâches
- `task_engine/models.py` contient les structures de données
- `tests/` contient les tests existants

Certains comportements sont volontairement incomplets ou incorrects. Le brief du test précise le travail demandé.
