'''
Copyright (C) 2018 CaptainHansode(https://x.com/CaptainHansode)
sakaiden@live.jp

Created by CaptainHansode(https://x.com/CaptainHansode)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import datetime as dt
import requests
import xml.etree.ElementTree as ET

from xml.dom import minidom


def get_elevation(lat, lon, timeout):
    """国土地理院の情報より標高を取得
    Ref:
    http://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php?lon=137.263868&lat=36.146384&outtype=JSON
    http://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php?lon=%s&lat=%s&outtype=%s
    https://tkstock.site/2021/07/14/python-requests-ec%E3%82%B5%E3%82%A4%E3%83%88-%E3%82%B9%E3%82%AF%E3%83%AC%E3%82%A4%E3%83%94%E3%83%B3%E3%82%B0-403-%E3%82%A8%E3%83%A9%E3%83%BC/
    """
    timeout = timeout or 10
    ele = 0.0
    url = "http://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php" \
        "?lon=%s&lat=%s&outtype=%s" %(lon, lat, "JSON")
    resp = None
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        resp = requests.get(url, timeout=timeout, headers=headers)
    except requests.exceptions.ConnectTimeout as e:
        print("TimeOut!: ", lon, lat)
        print(e)

    if resp is not None and resp.status_code == 200:
        data = resp.json()
        ele = data["elevation"]
    return ele


def convert_route_to_track(gpx_file, hours, minutes, seconds):
    r"""rteトラックをrtkデータに変換
    ガーミンなどのデータをYamapやヤマレコ用に変換
    TODO: 出力先を指定出来た方がよいかも
    Args:
        gpx_file (str):
        hours (int):
        minites (int):
        seconds (int):
    Returns:
        None
    """
    print("-" * 80)
    print(f"Start convert: {gpx_file}")

    hours = hours or 1
    minutes = minutes or 0
    seconds = seconds or 0
    # ネームスペース定義
    # Ref: https://qiita.com/yuki2006/items/d84b37f07b70d02c5504
    ET.register_namespace("", "http://www.topografix.com/GPX/1/1")
    ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")
    # カシミール
    ET.register_namespace("kashmir3d", "http://www.kashmir3d.com/namespace/kashmir3d")
    # カシミール3D
    # ET.register_namespace("schemaLocation", "http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.kashmir3d.com/namespace/kashmir3d http://www.kashmir3d.com/namespace/kashmir3d.xsd")
    # ガーミンのネームスペース定義
    # ET.register_namespace("schemaLocation", "http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd")

    converted_gpx_file = f"{os.path.splitext(gpx_file)[0]}_converted_route_to_track.gpx"
    tree = ET.parse(gpx_file)
    root = tree.getroot()

    # コンバート用のxmlを準備
    conv_root = minidom.Document()
    conv_root.encoding = "UTF-8"
    gpx = conv_root.createElement("gpx")
    conv_root.appendChild(gpx)
    
    # NameSpace Attrbute追加
    gpx.setAttribute("version", "1.1")
    gpx.setAttribute("creator", "Converted GPX")
    gpx.setAttribute("xmlns", "http://www.topografix.com/GPX/1/1")
    gpx.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    gpx.setAttribute("xsi:schemaLocation", "http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd")
    # gpx.setAttribute("xsi:schemaLocation", "http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd")

    # メインのTrack
    track = conv_root.createElement("trk")
    gpx.appendChild(track)

    track_name = root.findtext(".//{http://www.topografix.com/GPX/1/1}metadata/{http://www.topografix.com/GPX/1/1}name")
    author_name = root.findtext(".//{http://www.topografix.com/GPX/1/1}author/{http://www.topografix.com/GPX/1/1}name")

    if track_name is None:
        track_name = os.path.basename(gpx_file)
    if author_name is None:
        # author_name = "UnknownAuthor"
        author_name = "GpxConv"

    print(f"Track Name: {track_name}")
    print(f"Author Name: {author_name}")
    name_elm = conv_root.createElement("name")
    name_elm.appendChild(conv_root.createTextNode(track_name))
    track.appendChild(name_elm)
    author_elm = conv_root.createElement("author")
    author_elm.appendChild(conv_root.createTextNode(author_name))
    track.appendChild(author_elm)

    # メインのセグメント情報
    trkseg_elm = conv_root.createElement("trkseg")
    track.appendChild(trkseg_elm)

    # 全セグメント取得
    track_segment = root.findall(".//{http://www.topografix.com/GPX/1/1}rtept")
    # time = dt.datetime.now().strftime("%Y/%m/%dT%H:%M:%S")  # dataと時間の間にTが必要

    time = dt.datetime.now()

    print(f"Track segments: {len(track_segment)}")
    seg_max_num = 5000
    seg_count_up = int(len(track_segment)/seg_max_num)

    if len(track_segment) == 0:
        print("Not found TrackData")
        trkpt_eml = conv_root.createElement("trkpt")
        trkpt_eml.setAttribute("lat", "35.68401924641666")
        trkpt_eml.setAttribute("lon", "139.7530031204224")
        ele_elm = conv_root.createElement("ele")
        ele_elm.appendChild(conv_root.createTextNode("0.00"))
        trkpt_eml.appendChild(ele_elm)

        tm_elm = conv_root.createElement("time")
        tm_elm.appendChild(conv_root.createTextNode(time))
        trkpt_eml.appendChild(tm_elm)

        trkseg_elm.appendChild(trkpt_eml)
    else:
        route_time = dt.timedelta(hours=hours, minutes=minutes , seconds=seconds)
        add_time = route_time / seg_max_num

    cnt = 1
    for i in range(0, len(track_segment), seg_count_up):
        seg = track_segment[i]
        ele = seg.find(".//{http://www.topografix.com/GPX/1/1}ele")
        ele = ele.text
        if float(ele) == 0.0:
            ele = get_elevation(float(seg.get("lat")), float(seg.get("lon")), 3)

        trkpt_eml = conv_root.createElement("trkpt")
        trkpt_eml.setAttribute("lat", seg.get("lat"))
        trkpt_eml.setAttribute("lon", seg.get("lon"))
        ele_elm = conv_root.createElement("ele")
        ele_elm.appendChild(conv_root.createTextNode(str(ele)))
        trkpt_eml.appendChild(ele_elm)

        _time = time + (add_time * cnt)

        tm_elm = conv_root.createElement("time")
        tm_elm.appendChild(conv_root.createTextNode(_time.strftime("%Y/%m/%dT%H:%M:%S")))
        trkpt_eml.appendChild(tm_elm)

        trkseg_elm.appendChild(trkpt_eml)
        cnt += 1

    seg = track_segment[-1]
    ele = seg.find(".//{http://www.topografix.com/GPX/1/1}ele")

    trkpt_eml = conv_root.createElement("trkpt")
    trkpt_eml.setAttribute("lat", seg.get("lat"))
    trkpt_eml.setAttribute("lon", seg.get("lon"))
    ele_elm = conv_root.createElement("ele")
    ele_elm.appendChild(conv_root.createTextNode(ele.text))
    trkpt_eml.appendChild(ele_elm)

    _time = str(time + (add_time * cnt))
    tm_elm = conv_root.createElement("time")
    tm_elm.appendChild(conv_root.createTextNode(_time))
    trkpt_eml.appendChild(tm_elm)

    trkseg_elm.appendChild(trkpt_eml)

    print(f"Save to: {converted_gpx_file}")
    with open(converted_gpx_file, "w", encoding="utf-8") as f:
        conv_root.writexml(f, indent=" ", addindent="", newl="\n", encoding="UTF-8")
    
    print("Convert route to track Finish")
    return None


def convert_trak_to_route(gpx_file, hours, minutes, seconds):
    r"""
    Yamapやヤマレコ用などのデータをSunntoやGarmin用に変換
    Args:
        gpx_file (str):
        hours (int):
        minites (int):
        seconds (int):
    Returns:
        None
    """
    print("-" * 80)
    print(f"Start convert: {gpx_file}")
    hours = hours or 1
    minutes = minutes or 0
    seconds = seconds or 0
    ET.register_namespace("", "http://www.topografix.com/GPX/1/1")
    ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")
    # ガーミンのネームスペース定義
    ET.register_namespace("schemaLocation", "http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd")

    converted_gpx_file = f"{os.path.splitext(gpx_file)[0]}_converted_track_to_route.gpx"
    tree = ET.parse(gpx_file)
    root = tree.getroot()

    # コンバート用のxmlを準備
    conv_root = minidom.Document()
    conv_root.encoding = "UTF-8"
    gpx = conv_root.createElement("gpx")
    conv_root.appendChild(gpx)
    
    # NameSpace Attrbute追加
    gpx.setAttribute("version", "1.1")
    gpx.setAttribute("creator", "Converted GPX")
    gpx.setAttribute("xmlns", "http://www.topografix.com/GPX/1/1")
    gpx.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    gpx.setAttribute("xsi:schemaLocation", "http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd")
    # gpx.setAttribute("xsi:schemaLocation", "http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd")

    # メインのTrack
    metadata = conv_root.createElement("metadata")
    gpx.appendChild(metadata)

    track_name = root.findtext(".//{http://www.topografix.com/GPX/1/1}trk/{http://www.topografix.com/GPX/1/1}name")
    author_name = root.findtext(".//{http://www.topografix.com/GPX/1/1}trk/{http://www.topografix.com/GPX/1/1}author")
    if track_name is None or track_name == "":
        track_name = os.path.basename(gpx_file)
    if author_name is None:
        # author_name = "UnknownAuthor"
        author_name = "GpxConv"

    print(f"Track Name: {track_name}")
    print(f"Author Name: {author_name}")
    name_elm = conv_root.createElement("name")
    name_elm.appendChild(conv_root.createTextNode(track_name))
    metadata.appendChild(name_elm)
    author_elm = conv_root.createElement("author")
    author_name_elm = conv_root.createElement("name")
    author_name_elm.appendChild(conv_root.createTextNode(author_name))
    author_elm.appendChild(author_name_elm)
    metadata.appendChild(author_elm)

    # メインのセグメント情報
    rte_elm = conv_root.createElement("rte")
    gpx.appendChild(rte_elm)

    # 全セグメント
    track_segment = root.findall(".//{http://www.topografix.com/GPX/1/1}trkpt")
    time = dt.datetime.now()

    print(f"Track segments: {len(track_segment)}")    
    # TODO:白馬国際のGPSが読み込めなかった
    if len(track_segment) == 0:
        # trk # trkseg
        track_segment = root.findall(".//{http://www.topografix.com/GPX/1/0}trkpt")

    if len(track_segment) == 0:
        print("Not found TrackData")
        rtept_eml = conv_root.createElement("rtept")
        rtept_eml.setAttribute("lat", "35.68401924641666")
        rtept_eml.setAttribute("lon", "139.7530031204224")
        ele_elm = conv_root.createElement("ele")
        ele_elm.appendChild(conv_root.createTextNode("0.00"))
        rtept_eml.appendChild(ele_elm)

        tm_elm = conv_root.createElement("time")
        rtept_eml.appendChild(tm_elm)

        rte_elm.appendChild(rtept_eml)
    else:
        route_time = dt.timedelta(hours=hours, minutes=minutes , seconds=seconds)
        add_time = route_time / len(track_segment)

    cnt = 1
    table = ""  # csv用
    for seg in track_segment:
        ele_vale = 0.0
        ele = seg.find(".//{http://www.topografix.com/GPX/1/1}ele")
        if ele is None:
            print("ele is None")
            ele = seg.find(".//{http://www.topografix.com/GPX/1/0}ele")
            if ele is not None:
                ele_vale = ele.text
        else:
            ele_vale = ele.text

        if float(ele_vale) == 0.0:
            ele_vale = get_elevation(float(seg.get("lat")), float(seg.get("lon")), 3)
        _lat = float(seg.get("lat"))
        table += f"{_lat}, {ele_vale}\n"
        # print(f"{_lat}, {ele_vale}")

        rtept_eml = conv_root.createElement("rtept")
        rtept_eml.setAttribute("lat", seg.get("lat"))
        rtept_eml.setAttribute("lon", seg.get("lon"))
        ele_elm = conv_root.createElement("ele")
        ele_elm.appendChild(conv_root.createTextNode(str(ele_vale)))
        rtept_eml.appendChild(ele_elm)

        # trkseg_elm.appendChild(trkpt_eml)
        rte_elm.appendChild(rtept_eml)
        cnt += 1

    print(f"Save to: {converted_gpx_file}")
    with open(converted_gpx_file, "w", encoding="utf-8") as f:
        conv_root.writexml(f, indent="  ", addindent="  ", newl="\n", encoding="UTF-8", standalone=False)

    print("Convert trak to route Finish")
    return None


def convert_klm_to_gpx(kml_file, hours, minutes, seconds):
    r"""
    GoogleなどのklmデータをSunntoやGarmin用に変換
    Args:
        kml_file (str):
        hours (int):
        minites (int):
        seconds (int):
    Returns:
        None
    """
    print("-" * 80)
    print(f"Start convert: {kml_file}")

    hours = hours or 1
    minutes = minutes or 0
    seconds = seconds or 0
    ET.register_namespace('', 'http://www.opengis.net/kml/2.2')

    converted_gpx_file = f"{os.path.splitext(kml_file)[0]}.gpx"
    tree = ET.parse(kml_file)
    root = tree.getroot()

    # コンバート用のxmlを準備
    conv_root = minidom.Document()
    conv_root.encoding = "UTF-8"
    gpx = conv_root.createElement("gpx")
    conv_root.appendChild(gpx)
    
    # NameSpace Attrbute追加
    gpx.setAttribute("version", "1.1")
    gpx.setAttribute("creator", "Converted GPX")
    gpx.setAttribute("xmlns", "http://www.topografix.com/GPX/1/1")
    gpx.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    gpx.setAttribute("xsi:schemaLocation", "http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd")

    # メインのTrack
    track = conv_root.createElement("trk")
    gpx.appendChild(track)

    track_name = root.findtext(".//{http://www.opengis.net/kml/2.2}Document/{http://www.opengis.net/kml/2.2}name")
    author_name = os.path.basename(kml_file)

    if track_name is None:
        track_name = "UnknownTrack"

    print(f"Track Name: {track_name}")
    print(f"Author Name: {author_name}")
    name_elm = conv_root.createElement("name")
    name_elm.appendChild(conv_root.createTextNode(track_name))
    track.appendChild(name_elm)
    author_elm = conv_root.createElement("author")
    author_elm.appendChild(conv_root.createTextNode(author_name))
    track.appendChild(author_elm)

    # メインのセグメント情報
    trkseg_elm = conv_root.createElement("trkseg")
    track.appendChild(trkseg_elm)

    # KMLのコーディネートはスペースか改行で区切られている
    track_segment = root.find(".//{http://www.opengis.net/kml/2.2}coordinates")
    track_segment = track_segment.text.replace("\n", "")
    track_segment = track_segment.replace("\r\n", "")
    track_segment = track_segment.split(" ")
    track_segment = [t for t in track_segment if t != ""]

    time = dt.datetime.now()  # dataと時間の間にTが必要

    if len(track_segment) == 0:
        print("Not found TrackData")
        trkpt_eml = conv_root.createElement("trkpt")
        trkpt_eml.setAttribute("lat", "35.68401924641666")
        trkpt_eml.setAttribute("lon", "139.7530031204224")
        ele_elm = conv_root.createElement("ele")
        ele_elm.appendChild(conv_root.createTextNode("0.00"))
        trkpt_eml.appendChild(ele_elm)

        tm_elm = conv_root.createElement("time")
        tm_elm.appendChild(conv_root.createTextNode(time))
        trkpt_eml.appendChild(tm_elm)

        trkseg_elm.appendChild(trkpt_eml)
    else:
        route_time = dt.timedelta(hours=hours, minutes=minutes , seconds=seconds)
        add_time = route_time / len(track_segment)

    cnt = 1

    placemarks = root.findall(".//{http://www.opengis.net/kml/2.2}Placemark")
    all_segments = []

    for elm in placemarks:
        coodinate = elm.find(".//{http://www.opengis.net/kml/2.2}LineString/{http://www.opengis.net/kml/2.2}coordinates")
        if coodinate is None:
            continue
        segments = coodinate.text.replace(" ", "").split("\n")

        for seg in segments:
            seg = seg.split(",")
            if len(seg) < 2:
                continue
            all_segments.append(seg)

    route_time = dt.timedelta(hours=hours, minutes=minutes , seconds=seconds)
    add_time = route_time / len(all_segments)
    _pre_ele = 0.0  # 一つ前の標高

    print(f"Track segments: {len(all_segments)}")
    for seg in all_segments:
        if len(seg) == 3:  # 標高
            if int(seg[2]) == 0:  # 標高が0だったら取得する
                ele = get_elevation(float(seg[1]), float(seg[0]), 3)
            else:
                ele = str(seg[2])
        else:
            ele = get_elevation(seg[1], seg[0], 3)
        if ele == 0.0:  # データが0だった場合一つ前を採用
            print("Use one previous data: ", _pre_ele)
            ele = _pre_ele
        else:
            _pre_ele = ele

        trkpt_eml = conv_root.createElement("trkpt")
        trkpt_eml.setAttribute("lat", seg[1])
        trkpt_eml.setAttribute("lon", seg[0])
        ele_elm = conv_root.createElement("ele")
        ele_elm.appendChild(conv_root.createTextNode(str(ele)))
        trkpt_eml.appendChild(ele_elm)

        _time = time + (add_time * cnt)
        tm_elm = conv_root.createElement("time")
        tm_elm.appendChild(conv_root.createTextNode(_time.strftime("%Y/%m/%dT%H:%M:%S")))
        trkpt_eml.appendChild(tm_elm)

        trkseg_elm.appendChild(trkpt_eml)
        cnt += 1

    print(f"Save to: {converted_gpx_file}")
    with open(converted_gpx_file, "w", encoding="utf-8") as f:
        conv_root.writexml(f, indent="  ", addindent="  ", newl="\n", encoding="UTF-8", standalone=False)

    print("Convert klm to gpx Finish")
    return None

"""Tests"""
# curt_dir = os.path.dirname(__file__)
# gpx_file_path = os.path.abspath(os.path.join(curt_dir, '../gpx_datas'))
# convert_route_to_track(os.path.join(gpx_file_path, "suunt_utmf2023_original.gpx"), 40, 37, 0)
# convert_klm_to_gpx(os.path.join(gpx_file_path, "hasetune.kml"), 24, 0, 0)
# convert_trak_to_route(os.path.join(gpx_file_path, "hidatakayama_ultra_marathon2023.gpx"), 24, 0, 0)
