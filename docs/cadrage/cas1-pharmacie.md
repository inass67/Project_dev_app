# Fiche de cadrage : Ordonnances incomplètes en pharmacie

> Remplir chaque rubrique en une à trois phrases. Les rubriques marquées (obligatoire) sont vérifiées par `pytest`.

## Besoin en une phrase (obligatoire)

Détecter automatiquement les ordonnances incomplètes (dosage, durée, signature ou posologie manquants) avant la délivrance des médicaments.

## Utilisateur final (obligatoire)

Le pharmacien et le préparateur en pharmacie, qui vérifient chaque ordonnance au comptoir.

## Approche retenue (obligatoire)

Cocher une seule case :

- [x] Règles métier
- [ ] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

J'ai choisi les règles métier car :
- (b) Vérifiabilité : chaque règle est explicite (par exemple « le dosage est présent »), donc le pharmacien peut vérifier pourquoi une ordonnance est signalée.
- (d) Conséquence d'une erreur : une ordonnance incomplète mal détectée peut mettre en danger le patient, il faut donc un comportement prévisible et contrôlable.
- (c) Coût par requête : les règles ne coûtent presque rien par ordonnance, contrairement à un modèle génératif.

## Données nécessaires et leur origine (obligatoire)

Des exemples d'ordonnances (anonymisées) fournies par la pharmacie, et la liste des champs obligatoires définie par la réglementation et par le pharmacien.

## Métrique de succès et seuil d'acceptation (obligatoire)

Taux de détection des ordonnances incomplètes (rappel) d'au moins 95 % sur un échantillon de test, avec moins de 10 % de fausses alertes.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Une erreur peut conduire à délivrer un traitement mal dosé. Le pharmacien valide toujours l'ordonnance avant la délivrance : le système ne fait que signaler.

## Risques éthiques ou de confidentialité (obligatoire)

Les ordonnances sont des données de santé confidentielles : il faut les anonymiser, limiter l'accès, ne pas les envoyer à un service externe sans accord, et respecter la réglementation sur la protection des données.