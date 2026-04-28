.PHONY: start down recreate logs

start:
	docker-compose up -d

down:
	docker-compose down

recreate:
	docker-compose up -d --build --force-recreate

logs:
	docker-compose logs -f

import:
	docker cp "Електронна таблиця без назви.xlsx" $$(docker-compose ps -q bot):/app/import.xlsx
	docker-compose exec bot python3 app/scripts/parse_excel.py /app/import.xlsx /app/data_dump.json
	docker-compose exec bot python3 -m app.scripts.load_data /app/data_dump.json
