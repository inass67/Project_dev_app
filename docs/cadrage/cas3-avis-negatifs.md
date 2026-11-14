# Fiche de cadrage : Priorisation des avis négatifs

## Besoin en une phrase (obligatoire)

Classer les avis négatifs des clients selon leur niveau de priorité afin d'aider l'équipe concernée à traiter rapidement les réclamations importantes.

## Utilisateur final (obligatoire)

Les responsables du service client et les employés chargés de consulter les avis et de répondre aux réclamations.

## Approche retenue (obligatoire)

- [ ] Règles métier
- [x] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire)

(a) Un historique d'avis déjà classés par niveau de priorité peut fournir des exemples étiquetés pour entraîner le modèle. (c) Le classement automatique permet de traiter un grand nombre d'avis à un coût réduit par rapport à une analyse manuelle de chaque message.

## Données nécessaires et leur origine (obligatoire)

Les avis clients provenant des plateformes de publication, avec leur texte, leur date et leur niveau de priorité lorsqu'il est connu. Les données doivent être anonymisées et les catégories vérifiées par l'équipe du service client.

## Métrique de succès et seuil d'acceptation (obligatoire)

Mesurer le F1 macro sur un jeu de test indépendant. Viser un score d'au moins 0,85 et vérifier particulièrement que les réclamations les plus urgentes sont correctement détectées.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Un avis urgent mal classé pourrait recevoir une réponse tardive. Un employé doit pouvoir vérifier les priorités, corriger le classement et décider de l'ordre réel de traitement.

## Risques éthiques ou de confidentialité (obligatoire)

Les avis peuvent contenir des noms, des coordonnées ou des informations personnelles. Il faut anonymiser les données, limiter leur accès et éviter les classements discriminatoires.

## Approche écartée et pourquoi (facultatif)

Les règles par mots-clés seules sont écartées, car elles risquent de mal interpréter les formulations ironiques ou les réclamations exprimées de différentes manières.
