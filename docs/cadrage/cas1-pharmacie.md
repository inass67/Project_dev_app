# Fiche de cadrage : Ordonnances incomplètes en pharmacie

## Besoin en une phrase (obligatoire)

Repérer les informations manquantes dans les ordonnances afin d'aider le pharmacien à vérifier leur complétude avant leur traitement.

## Utilisateur final (obligatoire)

Les pharmaciens et les préparateurs en pharmacie qui vérifient les ordonnances et accompagnent les patients.

## Approche retenue (obligatoire)

- [x] Règles métier
- [ ] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire)

(b) Les informations obligatoires peuvent être vérifiées à partir d'une liste de critères définis et contrôlables. (d) Une erreur peut avoir des conséquences importantes pour le patient ; une vérification humaine par le pharmacien reste donc indispensable.

## Données nécessaires et leur origine (obligatoire)

Les informations présentes sur les ordonnances, comme la date, l'identification du prescripteur et les informations nécessaires au traitement, ainsi qu'une liste de vérification validée par les professionnels de la pharmacie.

## Métrique de succès et seuil d'acceptation (obligatoire)

Mesurer le taux de détection des informations manquantes sur un ensemble d'ordonnances vérifiées par des pharmaciens. Viser au moins 95 % de détection avant toute utilisation en situation réelle.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Une information manquante non détectée pourrait entraîner une mauvaise prise en charge. Le pharmacien doit contrôler chaque alerte et prendre la décision finale avant le traitement de l'ordonnance.

## Risques éthiques ou de confidentialité (obligatoire)

Les ordonnances contiennent des données personnelles et médicales. Il faut limiter leur accès, anonymiser les données utilisées pour les tests et respecter la confidentialité des patients.

## Approche écartée et pourquoi (facultatif)

Un modèle génératif seul est écarté, car les vérifications doivent être fondées sur des critères précis et contrôlables.
