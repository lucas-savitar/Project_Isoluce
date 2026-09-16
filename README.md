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

## Journal des corrections

Le projet contenait au départ plusieurs défauts volontaires. Voici le détail de chacun : le symptôme, la cause exacte, la correction apportée, et le ou les tests qui la garantissent dans le temps.

# 1. parser.py — La validation du client vide ne fonctionnait pas

Symptôme. Un client vide (ex. "   ") était accepté alors qu'il aurait dû être rejeté avec une erreur "client is required".

# Cause
La condition testait une mauvaise chose :

# exemple 

python
if client is None:
    raise ValueError("client is required")

client est le résultat de normalize_label(...), qui renvoie toujours une chaîne, jamais None — même pour une entrée vide, elle renvoie "". Or "" is None vaut False. La condition ne pouvait donc jamais se déclencher, quel que soit le contenu du client.

is None teste l'identité d'un objet (est-ce précisément l'objet None ?), alors qu'on voulait tester si la chaîne était vide après nettoyage — un test de « vérité » (truthiness), pas d'identité.

# Correction.

python
if not client:
    raise ValueError("client is required")

not "" vaut True (chaîne vide = falsy), donc l'erreur est bien levée. C'est la même logique que les vérifications déjà présentes juste en dessous pour action et message.

# Test qui le garantit. 
tests/test_parser.py::test_blank_client_is_rejected



# 2. parser.py — unique_preserve ne préservait pas l'ordre

# Symptôme.
La fonction censée dédupliquer une liste de noms « en conservant l'ordre d'apparition » (d'après sa docstring) les triait en fait par ordre alphabétique.

# Cause.
def unique_preserve(values: Iterable[str]) -> list[str]:
    return sorted({normalize_label(value) for value in values if normalize_label(value)})

Deux problèmes cumulés : l'utilisation d'un set (qui n'a aucun ordre garanti en Python), puis un sorted() par-dessus — qui trie alphabétiquement, en contradiction totale avec le nom et la docstring de la fonction.


# Correction.
Reconstruction de la liste en la parcourant dans l'ordre, avec un set utilisé uniquement comme mémoire de ce qui a déjà été vu :

python
def unique_preserve(values: Iterable[str]) -> list[str]:
    """Return unique non-empty values in their original order."""
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = normalize_label(value)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result

# Test qui le garantit.
tests/test_parser.py::test_people_are_deduplicated_without_reordering

# Erreurs de frappe rencontrées en cours de route
(corrigées avant d'aboutir à la version ci-dessus) :

normalize_label in seen au lieu de normalized in seen — confusion entre le nom de la fonction et la variable locale, provoquant TypeError: argument of type 'function' is not iterable.
seen: set[str] = set au lieu de set() — oubli des parenthèses, seen référençait la classe set elle-même plutôt qu'un ensemble vide, provoquant TypeError: argument of type 'type' is not iterable.


# 3. planner.py — merge_tasks n'était pas implémentée

# Symptôme.
Deux demandes concernant en réalité le même client et la même action (écrites différemment : casse, espaces) donnaient deux tâches distinctes au lieu d'une seule fusionnée.

# Cause.
def merge_tasks(tasks: Iterable[Task]) -> list[Task]:
    """Merge equivalent tasks.

    The current implementation is intentionally incomplete.
    """
    return list(tasks)

La fonction ne faisait rien d'autre que renvoyer la liste telle quelle.

# Correction.
Implémentation complète, avec les règles de regroupement suivantes :

- Deux tâches sont considérées équivalentes si leur client et leur action, comparés sans tenir compte de la casse, sont identiques.
- source_ids : concaténés puis dédupliqués via unique_preserve, en conservant l'ordre de première apparition.
- people : fusionnés et dédupliqués via unique_preserve, même logique.
- priority : la plus haute des deux est conservée (low < medium < high), via une table PRIORITY_RANK.
- deadline : la date la plus proche (la plus urgente) est conservée ; si une seule des deux tâches a une date, celle-ci est gardée.
- missing_information : fusionnée et dédupliquée, puis l'alerte "deadline" (absence de date) est retirée si le deadline final de la tâche fusionnée est connu.

PRIORITY_RANK = {"low": 0, "medium": 1, "high": 2}

python
def _merge_two(existing: Task, incoming: Task) -> None:
    """Merge `incoming` into `existing`, in place."""
    existing.source_ids = unique_preserve(existing.source_ids + incoming.source_ids)
    existing.people = unique_preserve(existing.people + incoming.people)

    if PRIORITY_RANK[incoming.priority] > PRIORITY_RANK[existing.priority]:
        existing.priority = incoming.priority

    if existing.deadline is None:
        existing.deadline = incoming.deadline
    elif incoming.deadline is not None and incoming.deadline < existing.deadline:
        existing.deadline = incoming.deadline

    missing = unique_preserve(existing.missing_information + incoming.missing_information)
    if existing.deadline is not None:
        missing = [item for item in missing if item != "deadline"]
    existing.missing_information = missing


def merge_tasks(tasks: Iterable[Task]) -> list[Task]:
    """Merge equivalent tasks (same client and action, case-insensitive)."""
    merged: dict[tuple[str, str], Task] = {}
    order: list[tuple[str, str]] = []

    for task in tasks:
        key = (task.client.lower(), task.action.lower())
        if key not in merged:
            merged[key] = task
            order.append(key)
            continue
        _merge_two(merged[key], task)

    return [merged[key] for key in order]

unique_preserve est importée depuis parser.py :

python
from .parser import parse_request, unique_preserve

# Erreur rencontrée en cours de route.
Un import dupliqué a temporairement existé (from .parser import parse_request en plus de la ligne fusionnée) — sans effet fonctionnel, mais nettoyé pour la lisibilité.

# Tests qui le garantissent.
- tests/test_planner.py::test_requests_differing_by_case_and_spacing_are_merged — la fusion a bien lieu malgré la casse et les espaces différents.
- tests/test_planner.py::test_merge_keeps_highest_priority_and_nearest_deadline — priorité la plus haute et deadline la plus proche conservées, vérifié dans les deux ordres d'arrivée des demandes.
- tests/test_planner.py::test_merge_preserves_people_order_without_duplicates — les personnes communes aux deux demandes ne sont listées qu'une fois, dans l'ordre de première apparition.


# 4. planner.py — Règles de fusion affinées après relecture du brief

Deux comportements plus fins, précisés a posteriori, ont nécessité un ajustement de _merge_two :

# 4a. source_ids n'était pas dédupliqué.
Avant l'ajustement, la fusion utilisait .extend() :

python
existing.source_ids.extend(incoming.source_ids)

.extend() concatène sans vérifier les doublons. Exemple concret : si les demandes R2, R1, R2 sont fusionnées dans cet ordre (le même id R2 apparaissant deux fois), le résultat devenait ["R2", "R1", "R2"] au lieu du ["R2", "R1"] attendu.

# Correction : 
Remplacement par unique_preserve, comme pour people (voir code complet ci-dessus).

# Test qui le garantit.
tests/test_planner.py::test_source_ids_are_deduplicated_preserving_first_appearance


# 4b. L'alerte "deadline" restait dans missing_information même une fois la date connue.

Avant l'ajustement, missing_information était fusionnée avant que le deadline final soit résolu. Résultat : si une demande sans date était fusionnée avec une demande apportant une date valide, l'alerte "deadline" (déjà copiée dans la liste fusionnée) restait présente alors que la tâche avait désormais une date connue — un faux signalement.

# Correction : 
Le deadline final est calculé avant la fusion de missing_information, puis l'alerte "deadline" est explicitement retirée si existing.deadline n'est plus None (voir code complet ci-dessus). L'alerte "deadline_invalid", elle, n'est jamais retirée automatiquement : une date mal formée reste un signalement pertinent même si une autre demande du même groupe avait une date correcte.

# Test qui le garantit.
tests/test_planner.py::test_known_deadline_clears_missing_alert_regardless_of_order (vérifié dans les deux ordres d'arrivée des demandes).



Chaque correction a été validée selon la méthode suivante : réintroduction volontaire du bug corrigé → le test correspondant échoue (FAILED) → restauration de la correction → le test repasse (ok). Cela confirme que chaque test détecte réellement le défaut qu'il est censé couvrir, et pas seulement qu'il « passe » par coïncidence.

Certains comportements ont été volontairement incomplets ou incorrects au départ. Le brief du test en précisait le travail demandé ; ce journal documente la démarche de correction et de test suivie pour y répondre.