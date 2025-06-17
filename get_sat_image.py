import os
import io
import requests
from PIL import Image

def merge_images(base_url, utc_str):
    # タイルの座標範囲（a_valuesが横方向、b_valuesが縦方向）
    a_values = [25, 26, 27, 28, 29, 30]#, 31]  # 横方向（列）
    b_values = [11, 12, 13, 14]  # 縦方向（行）

    # **各タイル画像をダウンロード**
    tiles = []
    tile_width, tile_height = None, None

    for b in b_values:  # 縦方向（行）を先に処理
        row_images = []
        for a in a_values:  # 横方向（列）を内側で処理
            url = base_url.format(a=a, b=b, utc_str=utc_str)
            response = requests.get(url)
            image = Image.open(io.BytesIO(response.content))

            if tile_width is None or tile_height is None:
                tile_width, tile_height = image.size  # 最初の画像からタイルサイズ取得

            row_images.append(image)
        tiles.append(row_images)

    # **統合画像のサイズを計算**
    merged_width = len(a_values) * tile_width  # 横の合計サイズ
    merged_height = len(b_values) * tile_height  # 縦の合計サイズ

    # **統合画像を作成**
    merged_image = Image.new("RGBA", (merged_width, merged_height),(0, 0, 0, 0))

    # **タイルを統合**
    for row_index, row_images in enumerate(tiles):
        for col_index, img in enumerate(row_images):
            x_offset = col_index * tile_width  # a_values に対応
            y_offset = row_index * tile_height  # b_values に対応
            merged_image.paste(img, (x_offset, y_offset))
    return merged_image


def get_sat_images(output_dir, utc_str):
    """
    衛星画像をダウンロードして統合する関数
    :param output_dir: 出力ディレクトリ
    :param utc_str: UTC時間の文字列（例: "20250617120000")
    """
    # ベースURL
    url_infos = [
        {
            "url": "https://www.jma.go.jp/bosai/himawari/data/satimg/{utc_str}/fd/{utc_str}/B03/ALBD/5/{a}/{b}.jpg",
            "name":"可視画像",
            "en": "vis"
        },{
            "url": "https://www.jma.go.jp/bosai/himawari/data/satimg/{utc_str}/fd/{utc_str}/B13/TBB/5/{a}/{b}.jpg",
            "name":"赤外画像",
            "en": "ir"
        },{
            "url": "https://www.jma.go.jp/bosai/himawari/data/satimg/{utc_str}/fd/{utc_str}/B08/TBB/5/{a}/{b}.jpg",
            "name":"水蒸気画像",
            "en": "vap"
        },{
            "url": "https://www.jma.go.jp/bosai/himawari/data/satimg/{utc_str}/fd/{utc_str}/REP/ETC/5/{a}/{b}.jpg",
            "name":"カラー画像",
            "en": "color"
        },{
            "url": "https://www.jma.go.jp/bosai/himawari/data/satimg/{utc_str}/fd/{utc_str}/SND/ETC/5/{a}/{b}.jpg",
            "name":"雲頂強調画像",
            "en": "strengthen"
        }
    ]

    result_objs = []
    os.makedirs(output_dir, exist_ok=True)
    print("Downloading overlay images...")
    overlay_image = merge_images("https://www.jma.go.jp/tile/jma/sat/5/{a}/{b}.png","")
    for info in url_infos:
        # 各タイル画像をダウンロードして統合
        print(f'Downloading {info["name"]} images...')
        merged_image = merge_images(info["url"], utc_str)

        final_image = Image.alpha_composite(merged_image, overlay_image)

        # **保存**
        file_name = os.path.join(output_dir, f'{utc_str}_{info["en"]}.png')
        final_image.convert("RGB").save(file_name)
        result_objs.append({
            "id":f'sat_{info["en"]}',
            "name":os.path.basename(file_name),
            "title":f'{info["name"]}({utc_str[:10]})'
        })
    return result_objs

if __name__ == "__main__":
    import os
    import json

    # 出力ディレクトリの指定
    output_dir = os.path.join(os.path.dirname(__file__),"satellite_images")

    # UTC時間の文字列を指定（例: 2025年6月17日03時00分00秒）
    utc_strs = [
        "20250616120000",
        "20250617000000"
    ]
    for utc_str in utc_strs:
        print(f"Processing UTC time: {utc_str}")
        print(json.dumps(get_sat_images(output_dir, utc_str), indent=2, ensure_ascii=False))
        print(f"Images saved to {output_dir}")
