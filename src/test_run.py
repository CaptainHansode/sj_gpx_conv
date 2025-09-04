import os
import sys
cur_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(cur_path)
sys.path.append(cur_path)
import src.gpx_conv

gpx_file_path = "D:\\ランニング\\トレイル\\トレイル_竜王山ハーフ\\竜王山トレイル.gpx"
src.gpx_conv.convert_trak_to_route(gpx_file_path, 5, 0, 0)