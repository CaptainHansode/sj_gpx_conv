import os
import sys
cur_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path = list(set(sys.path + [cur_path]))

# if cur_path not in sys.path:
#     sys.path.insert(0, cur_path)

import src.gpx_conv


# gpx_file_path = "D:\\ランニング\\トレイル\\トレイル_竜王山ハーフ\\竜王山トレイル.gpx"
# kml_file_path = "D:\\ランニング\\大会関連\\神戸マラソン\\KoubeMarathon2025.kml"
# gpx_file_path = "D:\\ランニング\\大会関連\\神戸マラソン\\KoubeMarathon2025.gpx"
kml_file_path = "D:\\ランニング\\トレイル\\トレイル_PPY30\\PPY30K.kml"
gpx_file_path = "D:\\ランニング\\トレイル\\トレイル_PPY30\\PPY30K.gpx"

# KLMをSunnto, COROSやGarmin用に変換
# 2026現在はヤマレコではこの形式が読み込めるようになった
src.gpx_conv.convert_kml_to_gpx(kml_file_path, 7, 0, 0)

# Yamapやヤマレコ用などのデータをSunnto, COROSやGarmin用に変換
# src.gpx_conv.convert_route_to_track(gpx_file_path, 7, 0, 0)

# GarminなどのデータをYamapやヤマレコ用に変換
# src.gpx_conv.convert_trak_to_route(gpx_file_path, 7, 0, 0)
