#NO EJECUTADO
param([string]$command = "help")
$OLLAMA = (Get-Command ollama).source
switch ($command) {
    "instalar-modelos" {
        $env:OLLAMA_MODELS = "G:\ollama\models"
        ollama pull llama2
    }
    "serve-ollama" {
        $env:OLLAMA_MODELS = "G:\ollama\models"
        ollama serve
    }
    "run" {
        python -m app.main
    }
    default {
        Write-Host "Usar .\run.ps1 [instalar-modelos|serve-ollama|run]"
    }
}
