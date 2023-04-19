dev-start-0:
	docker compose up -d --no-deps --build
dev-start:
	docker compose up -d --build
dev-stop:
	docker compose down -v
