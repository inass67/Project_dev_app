# Fiche de cadrage : Priorisation des avis négatifs

> Remplir chaque rubrique en une à trois phrases. Les rubriques marquées (obligatoire) sont vérifiées par `pytest`.

## Besoin en une phrase (obligatoire)

Trier automatiquement les avis négatifs des clients par urgence et par thème afin que l'équipe traite en premier les plus graves.

## Utilisateur final (obligatoire)

Le responsable du service client et son équipe, qui reçoivent chaque jour de nombreux avis et doivent décider lesquels traiter en priorité.

## Approche retenue (obligatoire)

Cocher une seule case :

- [ ] Règles métier
- [x] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

J'ai choisi le machine learning car :
- (a) Données étiquetées : l'entreprise possède un historique d'avis déjà classés par niveau d'urgence, ce qui permet d'entraîner un modèle supervisé.
- (b) Vérifiabilité : chaque prédiction peut être contrôlée par un humain en relisant l'avis.
- (c) Coût par requête : un petit modèle de classification coûte très peu par avis, même avec des milliers d'avis par jour.

## Données nécessaires et leur origine (obligatoire)

Un historique de plusieurs centaines d'avis négatifs, étiquetés par niveau de priorité (urgent, normal, faible) par l'équipe du service client.

## Métrique de succès et seuil d'acceptation (obligatoire)

Rappel d'au moins 90 % sur la classe « urgent » et un F1-score global d'au moins 0,80, mesurés sur un échantillon de test non utilisé pour l'entraînement.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Un avis urgent classé comme faible serait traité trop tard et nuirait à la réputation. Un humain relit régulièrement un échantillon des avis classés, et les cas incertains lui sont envoyés.

## Risques éthiques ou de confidentialité (obligatoire)

Les avis peuvent contenir des noms ou des informations personnelles : il faut les anonymiser avant l'entraînement. Il faut aussi vérifier que le modèle ne pénalise pas certains types de clients ou de langues.

## Approche écartée et pourquoi (facultatif)

J'ai écarté les règles métier car des mots-clés seuls ratent les avis formulés de façon indirecte, et le modèle génératif seul car son coût par requête est plus élevé et ses résultats moins vérifiables.