import os
import shutil
import datetime
import markdown
from get_svg_from_pdf_url import get_svg_from_pdf_url, get_svg_from_url, extract_date

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
        title_str = weekly_obj["pages"][0]["texts"].split("\n")[0]
        md_text += f'# {title_str}\n'
        reported_at_str = weekly_obj["pages"][0]["texts"].split("\n")[1]
        md_text += f'## {reported_at_str}\n'
        released_datetime = extract_date(reported_at_str)
        print(f'Published at {released_datetime}(JST)')

        output_base_dir = os.path.join(os.path.dirname(__file__), released_datetime.strftime('%Y%m%d_%H%M'))

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

        html_text = markdown.markdown(md_text)
        html_path_name = os.path.join(output_base_dir, "index.html")
        with open(html_path_name, "w", encoding="utf-8") as f:
            f.write(html_text)

        shutil.make_archive("output", format='zip', root_dir=os.path.dirname(output_base_dir), base_dir=os.path.basename(output_base_dir))
        print(f'Output saved to {output_base_dir} and output.zip')
        print(f'Finished at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        exit(0)
    else:
        print("Failed to get 週間天気予報解説資料 or no text found.")
        exit(1)