.PHONY: up down rebuild update logs ps backup import

up:
	docker compose up -d

down:
	docker compose down

# Перезібрати образ і перезапустити контейнер
rebuild:
	docker compose up -d --build --force-recreate

# Підтягнути код з git і одразу перезібрати (основна команда для деплою)
update:
	git pull
	docker compose up -d --build --force-recreate

logs:
	docker compose logs -f bot

ps:
	docker compose ps

# Копія бази в ./backups з датою в імені
backup:
	mkdir -p backups
	cp data/monitoring_db.sqlite backups/db_$$(date +%F_%H%M%S).sqlite
	@echo "Бекап: backups/db_$$(date +%F_%H%M%S).sqlite"

import:
	docker cp "Електронна таблиця без назви.xlsx" $$(docker compose ps -q bot):/app/import.xlsx
	docker compose exec bot python3 app/scripts/parse_excel.py /app/import.xlsx /app/data_dump.json
	docker compose exec bot python3 -m app.scripts.load_data /app/data_dump.json
