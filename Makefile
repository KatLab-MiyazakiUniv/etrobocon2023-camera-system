help:
	@echo "カメラシステムを実行する"
	@echo " $$ make run"
	@echo "Pytestを実行する"
	@echo " $$ make test"
	@echo "全てのソースコードをフォーマットする"
	@echo " $$ make format"

run:
	poetry run python src

test:
	poetry run pytest

format:
	poetry run python -m autopep8 -i -r src/ tests/