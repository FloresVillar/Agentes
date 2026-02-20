# NO SE EJECUTO
.PHONY: instalar-modelos ejecutar-servidor-ollama run
instalar-modelos:
	ollama pull llama2
serve-ollama:
	ollama serve
run:
	python -m app.main
	