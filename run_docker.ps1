param([string]$command = "ayuda")

switch ($command) {
    "build" {
        docker compose build
    }
    "run" {
        Write-Host "Build"
        docker compose up -d 
        Write-Host "instalar modelos"
        docker exec -it ollama-server ollama pull llama3.2:1b
        Write-Host "reiniciando agente-python"
        docker restart agente-python
        Write-Host "COMPLETADO"
    }
    "down" {
        docker compose down
    }
    "logs" {
        docker compose logs -f
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