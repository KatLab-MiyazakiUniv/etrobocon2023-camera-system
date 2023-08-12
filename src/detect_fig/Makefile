help:
	@echo robo_learn
	@echo 学習する
	@echo " $$ make train"
	@echo 予測する
	@echo " $$ make predict"
	@echo 予測データ、学習済みモデルを削除する
	@echo " $$ make rm"

train:
	python train.py --data ./data/data.yaml --cfg models/yolov5s.yaml --weights yolov5s.pt --batch-size 10 --epoch 300 --imgsz 640

predict:
	python detect.py --data data/data.yaml --weight runs/train/exp/weights/best.pt --source verification_data/ --imgsz 640

rm:
	rm -rf runs/detect/