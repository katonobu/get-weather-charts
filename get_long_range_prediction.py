import os
import json
import datetime
import markdown
from get_svg_from_pdf_url import get_svg_from_pdf_url, get_svg_from_url, extract_date

def parse_text(text):
    results = []
    lines = text.split("\n")
    sentences = []
    stt = "idle"
    for line in lines:
        print(line)
        if stt == "idle":
            if line == "週間天気予報解説資料":
                stt = "header"
                name = line.strip()
            elif line.endswith("利⽤ください。)"):
                stt = "forecast"
                name = line.split("(")[0].replace("◆","").strip()
            elif line.startswith("＜主要じょう乱の概要"):
                stt = "disturbance"
                name = line.strip()
        elif stt == "header":
            if line.endswith("発表"):
                sentences.append(line.strip())
            elif line == "気象庁":
                sentences.append(line.strip())
            elif line.startswith("予報期間") and line.endswith("まで") and stt == "header":
                stt = "idle"
                sentences.append(line.strip())
                results.append({
                    "name":name,
                    "sentences":sentences
                })
                sentences = []
        elif stt == "forecast":
            if line.startswith("天気") or line.startswith("晴") or line.startswith("曇り") or line.startswith("⾬") or line.startswith("雪"):
                pass
            elif line.endswith("今期間のポイント"):
                stt = "idle"
                results.append({
                    "name":name,
                    "sentences":sentences
                })
                sentences = []
            else:
                sentences.append(line.strip())
        elif stt == "disturbance":
            if line.startswith("＜防災事項"):
                stt = "disaster"
                results.append({
                    "name":name,
                    "sentences":sentences
                })
                name = "＜防災事項＞"
                sentences = []
            else:
                sentences.append(line.strip())
        elif stt == "disaster":
            if line.startswith("※最新の"):
                stt = "idle"
                results.append({
                    "name":name,
                    "sentences":sentences
                })
                name = ""
                sentences = []
            else:
                sentences.append(line.strip())
    return results

if __name__ == "__main__":

    file_infos = []
    md_text = '<a id="top"></a>\n'
    print(f'Start at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    # 週間天気予報解説資料を取得
    print("Getting 週間天気予報解説資料...")
    weekly_obj = get_svg_from_pdf_url("https://www.data.jma.go.jp/yoho/data/jishin/kaisetsu_shukan_latest.pdf")
    # textが抽出されていたら
    if weekly_obj["result"] and 0 < len(weekly_obj["pages"]) and "texts" in weekly_obj["pages"][0]:
        # textから発表日時を取得
        text_objs = parse_text(weekly_obj["pages"][0]["texts"])
#        print(json.dumps(), indent=2, ensure_ascii=False))        
        title_str = weekly_obj["pages"][0]["texts"].split("\n")[0]
        md_text += f'# {text_objs[0]["name"]}\n'
        reported_at_str = weekly_obj["pages"][0]["texts"].split("\n")[1]
        md_text += f'## {text_objs[0]["sentences"][0]}\n'
        released_datetime = extract_date(reported_at_str)
        print(f'Published at {released_datetime}(JST)')

        output_base_dir = os.path.join(os.path.dirname(__file__), "output", released_datetime.strftime('%Y%m%d_%H%M'))

        # 発表時刻名のディレクトリを掘る
        os.makedirs(output_base_dir, exist_ok=True)

        for idx, page in enumerate(weekly_obj["pages"]):
            if "svg" in page:
                # ページごとにsvgを保存
                file_name = f'syukan_yoho_{idx + 1}.svg'
                page_svg_path_name = os.path.join(output_base_dir, file_name)
                with open(page_svg_path_name, "w", encoding="utf-8") as f:
                    f.write(page["svg"])
                file_infos.append({
                    "id":file_name.replace(".svg","").replace(".png",""),
                    "name":file_name,
                    "title":f'週間天気予報解説資料ページ{idx + 1}'
                })
        # 週間予報支援図
        url_filename_objs = [
            {
                "url":'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/fzcx50.png',
                "name":"FZCX50.png",
                "title":"週間予報支援図（アンサンブル）"
            },
            {
                "url":'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/fxxn519.png',
                "name":"FXXN519.png",
                "title":"週間予報支援図"
            }
        ]
        yoho_objs = [
            {
                "url":'https://www.data.jma.go.jp/yoho/data/wxchart/quick/FSAS24_MONO_ASIA.pdf',
                "name":"FSAS24.svg",
                "title":"アジア太平洋域 24時間"
            },
            {
                "url":'https://www.data.jma.go.jp/yoho/data/wxchart/quick/FSAS48_MONO_ASIA.pdf',
                "name":"FSAS48.svg",
                "title":"アジア太平洋域 48時間"
            },

        ]
        for url_file_obj in url_filename_objs:
            print(f'  Getting {url_file_obj["name"].replace(".svg","").replace(".png","")} {url_file_obj["title"]}...')
            obj = get_svg_from_url(url_file_obj["url"])
            if obj["result"] and "svg" in obj:
                file_name = url_file_obj["name"]
                png_path_name = os.path.join(output_base_dir, file_name)
                with open(png_path_name, "wb") as f:
                    f.write(obj["svg"])
                file_infos.append({
                    "id":file_name.replace(".svg","").replace(".png",""),
                    "name":file_name,
                    "title":url_file_obj["title"]
                })

        for url_file_obj in yoho_objs:
            print(f'  Getting {url_file_obj["name"].replace(".svg","").replace(".png","")} {url_file_obj["title"]}...')
            obj = get_svg_from_pdf_url(url_file_obj["url"])
            if obj["result"] and 0 < len(obj["pages"]) and "svg" in obj["pages"][0]:
                file_name = url_file_obj["name"]
                svg_path_name = os.path.join(output_base_dir, file_name)
                with open(svg_path_name, "w", encoding="utf-8") as f:
                    f.write(obj["pages"][0]["svg"])
                file_infos.append({
                    "id":file_name.replace(".svg","").replace(".png",""),
                    "name":file_name,
                    "title":url_file_obj["title"]
                })

       
        md_text += '## ページ内画像リンク\n'
        for file_info in file_infos:
            md_text += f'- [{file_info["title"]}](#{file_info["id"]})\n'
        md_text += '\n\n'

        md_text += '## 画像\n'
        md_text += f'[ページトップ](#top)\n\n'
        for file_info in file_infos:
            md_text += f'<a href="{file_info["name"]}" target="_blank" id="{file_info["id"]}">{file_info["title"]}</a>\n'
            md_text += f'<img width="100%" height="auto" style="border: 2px solid black;" src="{file_info["name"]}"></img>\n'
            md_text += f'[ページトップ](#top)\n\n'

        md_path_name = os.path.join(output_base_dir, "index.md")
        with open(md_path_name, "w", encoding="utf-8") as f:
            f.write(md_text)

        html_text = """
<!doctype html>
<html lang="ja">

<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width" />
    <title>週間天気予報解説資料</title>
</head>

<body>
"""    
        html_text += markdown.markdown(md_text)
        html_text += """
</body>
</html>
"""

        html_path_name = os.path.join(output_base_dir, "index.html")
        with open(html_path_name, "w", encoding="utf-8") as f:
            f.write(html_text)

        text_path_name = os.path.join(output_base_dir, "syukan_yuoho.json")
        with open(text_path_name, "w", encoding="utf-8") as f:
            json.dump(text_objs, f, ensure_ascii=False, indent=2)

        # メタデータ生成
        meta_obj = {
            "title": text_objs[0]["name"],
            "released_at_j":text_objs[0]["sentences"][0],
            "released_at": released_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            "files": file_infos
        }
        metadata_path_name = os.path.join(output_base_dir, "metadata.json")
        with open(metadata_path_name, "w", encoding="utf-8") as f:
            json.dump(meta_obj, f, indent=2, ensure_ascii=False)


        print(f'Output saved to {output_base_dir}')
        print(f'Finished at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        exit(0)
    else:
        print("Failed to get 週間天気予報解説資料 or no text found.")
        exit(1)