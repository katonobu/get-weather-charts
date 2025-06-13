import os
import re
import time
import requests
import tempfile
from PIL import Image

def get_from_url(url):
    result_obj = {
         "result":False,
         "url":url,
         "response_ok":False,
         "content":None
    }

    response = requests.get(url)
    result_obj.update({"response_ok":response.ok})
    response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
    result_obj.update({"content":response.content})
    result_obj.update({"result":True})
    return result_obj

def get_border_png():
    url = "https://www.jma.go.jp/bosai/rain/const/map/border_a00.png"
    return get_from_url(url)

def get_rain_png(time_str):
    if re.match(r'^\d{10}0000$', time_str) is None:
        raise ValueError("Invalid time_str format. Expected format: YYYYMMDDHH0000")
    url = f"https://www.jma.go.jp/bosai/rain/data/rain/{time_str}/rain_{time_str}_f00_a00.png"
    return get_from_url(url)

def combie_border_rain_image(border_path, rain_path, output_path):
    # 得られた2つのpngを重ね合わせたファイルを生成する
    frame = Image.open(border_path).convert("RGBA")  # 枠線画像
    data = Image.open(rain_path).convert("RGBA")  # 時間変化する値
    white_background = Image.new("RGBA", frame.size, (255, 255, 255, 255))  # 白 (R=255, G=255, B=255, Alpha=255)

    white_background.paste(data, (0, 0), data)  # まずデータ画像を重ねる
    white_background.paste(frame, (0, 0), frame)  # 次に枠線画像を重ねる
    white_background.save(output_path)


def get_rader_png(yyyymmddhh_utc_str, output_dir):
    output_path = None
    if re.match(r'^\d{10}$', yyyymmddhh_utc_str) is not None:
        os.makedirs(output_dir, exist_ok=True)
        with tempfile.TemporaryDirectory() as temp_dir:
            result = get_border_png()
            if result["result"]:
                border_path = os.path.join(temp_dir, "border_a00.png")
                with open(border_path, "wb") as f:
                    f.write(result["content"])
                print("Border image saved successfully.")
                time_str = f"{yyyymmddhh_utc_str}0000"
                try:
                    result = get_rain_png(time_str)
                    if result["result"]:
                        target_path = os.path.join(temp_dir, f"rain_{time_str}_f00_a00.png")
                        with open(target_path, "wb") as f:
                            f.write(result["content"])
                        print(f"Image for {time_str} saved successfully.")

                        output_path = os.path.join(output_dir, f"rain_{time_str}_f00_a00_combined.png")
                        combie_border_rain_image(border_path, target_path, output_path)
                        print(f"Combined image saved to {output_path}")

                    else:
                        print(f"Failed to retrieve image for {time_str}: {result['url']}")
                except ValueError as e:
                    print(f"Error for {time_str}: {e}")
            else:
                print("Failed to retrieve border image:", result["url"])
    else:
        print(f"Invalid date format: {yyyymmddhh_utc_str}. Expected format: YYYYMMDDHH")

    return output_path


def get_rader_png_by_utc_date(yyyymmdd_str):
    if re.match(r'^\d{8}$', yyyymmdd_str) is None:
        raise ValueError("Invalid date format. Expected format: YYYYMMDD")

    # 現在時刻文字列の出力ディレクトリ作成
    now_str = time.strftime("%Y%m%d%H%M%S", time.localtime())
    output_dir = os.path.join(os.path.dirname(__file__), 'output', now_str)
    os.makedirs(output_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        result = get_border_png()
        if result["result"]:
            border_path = os.path.join(temp_dir, "border_a00.png")
            with open(border_path, "wb") as f:
                f.write(result["content"])
            print("Border image saved successfully.")
            for hour in range(24):
                time_str = f"{yyyymmdd_str}{hour:02d}0000"
                try:
                    result = get_rain_png(time_str)
                    if result["result"]:
                        target_path = os.path.join(temp_dir, f"rain_{time_str}_f00_a00.png")
                        with open(target_path, "wb") as f:
                            f.write(result["content"])
                        print(f"Image for {time_str} saved successfully.")

                        output_path = os.path.join(output_dir, f"rain_{time_str}_f00_a00_combined.png")
                        combie_border_rain_image(border_path, target_path, output_path)
                        print(f"Combined image saved to {output_path}")

                    else:
                        print(f"Failed to retrieve image for {time_str}: {result['url']}")
                except ValueError as e:
                    print(f"Error for {time_str}: {e}")
        else:
            print("Failed to retrieve border image:", result["url"])

    return output_dir

if __name__ == "__main__":
    import shutil
    from datetime import datetime, timedelta, timezone

    # UTCと日本時間（JST）のタイムゾーンを定義
    UTC = timezone.utc
    JST = timezone(timedelta(hours=9))

    # **現在の日本時間を取得**
    now_jst = datetime.now(JST)
    print(f"現在の日本時間: {now_jst}")
    if now_jst.hour >= 9:  # JSTの9:00以降 → 前日のUTC日
        utc_target_date = (now_jst - timedelta(days=1)).date()
    else:  # JSTの8:59以前 → 前前日のUTC日
        utc_target_date = (now_jst - timedelta(days=2)).date()

    yyyymmdd_str = utc_target_date.strftime("%Y%m%d")
    output_dir = get_rader_png_by_utc_date(yyyymmdd_str)
    shutil.make_archive("output", format='zip', root_dir=os.path.dirname(output_dir), base_dir=os.path.basename(output_dir))
