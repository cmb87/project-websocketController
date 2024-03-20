
.PHONY: webappbuild start stop

webappbuild:
	cd ./webapp-client && npm run build && rm -r ../webserver/build && mv build ../webserver/.

start:
	docker compose up -d

stop:
	docker compose down