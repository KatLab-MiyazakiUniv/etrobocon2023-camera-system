help:
	@echo 予測する
	@echo " $$ make predict"
	@echo 予測データ、学習済みモデルを削除する
	@echo " $$ make rm"

predict:
	python detect.py --weight runs/train/exp/weights/best.pt --source verification_data/ --imgsz 640

rm:
	rm -rf runs/detect/