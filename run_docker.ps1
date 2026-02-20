param([string]$command = "ayuda")

switch ($command) {
    "build" {
        docker compose build
    }
    "up" {
        docker compose up -d
    }
    "down" {
        docker compose down
    }
    "logs" {
        docker compose logs -f
    }
    "instalar-modelo" {
        docker exec -it ollama-server ollama pull llama2
    }
    "shell-app" {
        docker exec -it agente-python /bin/bash
    }
    "limpieza" {
        docker system prune -af
        docker volume prune -f
    }
    default {
        Write-Host ""
        Write-Host "Comandos a disposicion"
        Write-Host ".\run_docker.ps1 build,up,down,logs,instalar-modelo,shell-app" 
    }
}