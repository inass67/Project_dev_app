# Fiche de cadrage : Questions sur le règlement intérieur

> Remplir chaque rubrique en une à trois phrases. Les rubriques marquées (obligatoire) sont vérifiées par `pytest`.

## Besoin en une phrase (obligatoire)

Permettre aux étudiants et aux employés de poser une question en langage naturel sur le règlement intérieur et d'obtenir une réponse qui cite l'article concerné.

## Utilisateur final (obligatoire)

Les étudiants et le personnel de l'établissement, qui cherchent une règle précise (absences, examens, sanctions) sans lire tout le document.

## Approche retenue (obligatoire)

Cocher une seule case :

- [ ] Règles métier
- [ ] Machine learning
- [x] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

J'ai choisi le RAG car :
- (b) Vérifiabilité : la réponse s'appuie sur des passages réels du règlement et cite l'article, donc l'utilisateur peut vérifier la source.
- (d) Conséquence d'une erreur : une règle inventée pourrait causer une sanction injuste, le RAG limite ce risque en ancrant la réponse dans le texte officiel.
- (a) Données étiquetées : nous n'avons pas de questions étiquetées, ce qui exclut un modèle supervisé.

## Données nécessaires et leur origine (obligatoire)

Le texte officiel du règlement intérieur (PDF ou Word) fourni par l'établissement, découpé en articles et en passages.

## Métrique de succès et seuil d'acceptation (obligatoire)

Dans au moins 90 % des cas, l'article cité doit être le bon, mesuré sur une vingtaine de questions de test dont la réponse est connue.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Une mauvaise réponse peut induire en erreur sur un droit ou une sanction. Le système affiche toujours l'article cité et invite à contacter l'administration en cas de doute.

## Risques éthiques ou de confidentialité (obligatoire)

Le règlement est un document public interne, peu sensible. Il faut toutefois ne pas enregistrer les questions des utilisateurs avec leur identité et éviter qu'une réponse soit présentée comme une décision officielle.

## Approche écartée et pourquoi (facultatif)

J'ai écarté le modèle génératif seul car il peut inventer des règles qui n'existent pas, et les règles métier car les questions sont formulées librement et ne se prêtent pas à des règles fixes.