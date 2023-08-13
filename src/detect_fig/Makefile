help:
	@echo 予測する
	@echo " $$ make predict"
	@echo 予測データ、学習済みモデルを削除する
	@echo " $$ make rm"

predict:
	python detect.py --source detect_image --project detect_result
# python detect.py --source detect_image/image1.png --project detect_result
# python detect.py --source detect_image/image1.png --project detect_result --conf-thres 0.99

rm:
	rm -rf detect_result/