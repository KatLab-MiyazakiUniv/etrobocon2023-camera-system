help:
	@echo 予測する
	@echo " $$ make predict"
	@echo 予測データ、学習済みモデルを削除する
	@echo " $$ make rm"

predict:
	python detect.py --data data/data.yaml --weight runs/train/exp/weights/best.pt --source verification_data/ --imgsz 640 --device cpu

rm:
	rm -rf runs/detect/