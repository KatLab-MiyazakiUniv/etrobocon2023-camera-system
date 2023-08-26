help:
	@echo "カメラシステムを実行する"
	@echo " $$ make run"
	@echo "Pytestを実行する"
	@echo " $$ make test"
	@echo "全てのソースコードをフォーマットする"
	@echo " $$ make format"
	@echo "全てのソースコードのスタイルをチェックする"
	@echo " $$ make check_style"
	@echo "カバレッジレポートの表示"
	@echo " $$ make coverage"
	@echo "物体検出を行う"
	@echo " $$ make detect"

run:
	poetry run python src

test:
	poetry run pytest --ignore=tests/test_detect_fig.py
	pytest tests/test_detect_fig.py

format:
	poetry run python -m autopep8 -i -r src/ tests/

check_style:
	poetry run python -m pycodestyle src/ tests/
	poetry run python -m pydocstyle src/ tests/

coverage:
	poetry run coverage run -m pytest
	poetry run coverage report -i

detect:
	python3 src/detect_fig.py

image_process:
	python3 src/image_processing.py