# AI_NOTES.md

Notes sur le travail réalisé avec l'assistance de Claude (Anthropic) pour corriger et
compléter le projet Mini Task Engine.

## Principales questions posées à l'IA

- Explique-moi ce que fait chaque fichier du projet avant de corriger quoi que ce soit.
- Pour `parser.py` : qu'est-ce qui ne va pas, et pourquoi précisément (`client is None` vs
  `not client`, `unique_preserve` qui triait au lieu de préserver l'ordre) ?
- Pour `planner.py` : comment concevoir `merge_tasks` alors qu'aucun test ne dicte
  exactement la règle de fusion à appliquer (client/action, priorité, deadline, personnes) ?
- Deux variantes de code proposées (tout dans une seule fonction vs. un helper séparé
  `_merge_two`) : quelles différences concrètes entre les deux ?
- Pourquoi une erreur `TypeError: argument of type 'type' is not iterable` apparaît après
  une correction, et comment la lire précisément ?
- Comment prouver qu'un test corrige vraiment un bug, et pas seulement qu'il « passe » par
  hasard (méthode : réintroduire le bug, vérifier que le test échoue, puis le corriger et
  vérifier qu'il passe) ?
- Quelle est la différence exacte entre `is None` et `not` en Python ?
- Que reste-t-il d'incorrect ou de non spécifié dans le projet, une fois les bugs du brief
  corrigés ?

## Ce que j'ai retenu

- Un test qui passe ne prouve rien en soi : il faut vérifier qu'il **échoue** quand le bug
  est présent, sinon il ne teste peut-être rien d'utile.
- `is None` teste une identité précise (l'objet `None` lui-même), alors que `not` teste la
  « vérité » d'une valeur (une chaîne vide, une liste vide, `0`, `None` sont tous *falsy*).
  Confondre les deux peut masquer un bug de validation sans lever d'erreur visible.
- Une erreur Python donne des indices précis sur sa cause : le message
  `TypeError: argument of type 'type' is not iterable` pointait vers une variable qui
  référençait une **classe** (`set`) au lieu d'une **instance** (`set()`), à cause d'un oubli
  de parenthèses.
- Réutiliser une fonction déjà validée (`unique_preserve`) pour un nouveau besoin similaire
  (dédupliquer `source_ids` en plus de `people`) évite de réinventer une logique déjà
  éprouvée, et limite les points de défaillance.
- La couverture de tests d'un projet peut être trompeuse : les tests existants passaient
  tous alors que `merge_tasks` ne faisait rien — aucun test ne couvrait la fonctionnalité
  centrale du regroupement.

## Une proposition que j'ai rejetée / fait modifier

Claude avait d'abord proposé d'implémenter toute la logique de fusion directement dans
`merge_tasks`, en un seul bloc. J'ai demandé à voir l'alternative avec un helper séparé
(`_merge_two`), pour que `merge_tasks` ne s'occupe que du regroupement (les clés, la boucle,
l'ordre) et que `_merge_two` s'occupe uniquement de la logique de fusion champ par champ.
J'ai choisi cette seconde version : chaque fonction a une seule responsabilité, ce qui la
rend plus lisible et plus facile à tester isolément si besoin.

## Ce que j'améliorerais avec plus de temps

- Trancher les zones grises identifiées en fin de session : le champ `message` qui disparaît
  silencieusement entre `ClientRequest` et `Task`, l'absence de signalement pour une priorité
  invalide (asymétrique avec le traitement de `deadline_invalid`), et la casse non
  harmonisée entre la clé de fusion des tâches (insensible à la casse) et la déduplication
  des personnes (sensible à la casse).
- Ajouter des tests explicites pour les branches de validation jamais exercées
  (`"people must be an array"`, `"input must be an array"`).
- Utiliser systématiquement la méthode rouge → vert (écrire le test avant la correction,
  vérifier qu'il échoue, corriger, vérifier qu'il passe) dès le départ, plutôt que de l'avoir
  appliquée après coup sur certains cas seulement.
- Documenter dans le README.
