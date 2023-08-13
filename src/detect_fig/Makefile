help:
	@echo 予測する
	@echo " $$ make predict"
	@echo 予測データ、学習済みモデルを削除する
	@echo " $$ make rm"

# predict:
	# python detect.py --source detect_image/image1.png --save_dir detect_result

predict:
	python detect.py --source detect_image --save_dir detect_result
# python detect.py --source detect_image/image1.png --save_dir detect_result --conf-thres 0.99

rm:
	rm -rf detect_result/