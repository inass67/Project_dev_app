# Fabrique les deux fichiers a deposer dans le formulaire :
#   LIVRABLE_FORMULAIRE\Paquet_TP6.zip      (roue .whl + .tar.gz + rapport)
#   LIVRABLE_FORMULAIRE\Serialisation.zip   (modele .joblib + metriques + scripts)
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "`n=== 1. Donnees ===" -ForegroundColor Cyan
python src/make_demo.py
if ($LASTEXITCODE -ne 0) { throw "make_demo a echoue" }

Write-Host "`n=== 2. Entrainement + serialisation (joblib) ===" -ForegroundColor Cyan
python src/train.py
if ($LASTEXITCODE -ne 0) { throw "train a echoue" }
python src/predict.py "Livraison rapide, produit conforme, tres satisfait"

Write-Host "`n=== 3. Modele copie dans le paquet ===" -ForegroundColor Cyan
Copy-Item models\sentiment.joblib src\sentiment_app\modele\ -Force

Write-Host "`n=== 4. Construction de la roue ===" -ForegroundColor Cyan
python -m pip install -q build
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue
Get-ChildItem src -Filter *.egg-info -Directory | Remove-Item -Recurse -Force
python -m build
if ($LASTEXITCODE -ne 0) { throw "python -m build a echoue" }
python -m zipfile -l dist\sentiment_app-1.0.0-py3-none-any.whl

Write-Host "`n=== 5. Verification du paquet (1 a 2 minutes) ===" -ForegroundColor Cyan
python scripts/verifier_livrable.py

Write-Host "`n=== 6. Fichiers pour le formulaire ===" -ForegroundColor Cyan
$out = "LIVRABLE_FORMULAIRE"
Remove-Item $out -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory $out | Out-Null
Compress-Archive -Path dist\*, docs\livrable-tp4.txt, pyproject.toml, README-PAQUET.md, CHANGELOG.md, src\sentiment_app `
  -DestinationPath "$out\Paquet_TP6.zip" -Force
Compress-Archive -Path models\sentiment.joblib, models\metrics.json, src\train.py, src\predict.py `
  -DestinationPath "$out\Serialisation.zip" -Force
Get-ChildItem $out | Select-Object Name, Length
Write-Host "`nTERMINE : depose les 2 fichiers du dossier $out dans le formulaire." -ForegroundColor Green
