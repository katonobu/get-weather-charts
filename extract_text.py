import os
import json
import glob
import xml.etree.ElementTree as ET
import html


def extract_text_from_svg(svg_path_file_name):
    # SVGファイルを読み込み
    tree = ET.parse(svg_path_file_name)
    root = tree.getroot()

    # SVGの名前空間を定義
    namespace = {'svg': 'http://www.w3.org/2000/svg'}

    extracted_texts = ""
    # use要素を検索し、data-text属性を抽出
    for use in root.findall('.//svg:use', namespace):
        data_text = use.get('data-text')
        if data_text:
            # HTMLエスケープされた文字列をデコード
            extracted_texts += html.unescape(data_text)
    return extracted_texts

section_separetors = [
    "短期予報解説資料1",
    "１．実況上の着目点",
    "２．主要じょう乱の予想根拠と防災事項を含む解説上の留意点",
    "３．数値予報資料解釈上の留意点",
    "４．防災関連事項 [量的予報等] ",
    "５．全般気象情報発表の有無"
]
subsectoin_separetors = [
    "① ",
    "② ",
    "③ ",
    "④ ",
    "⑤ ",
    "⑥ ",
    "⑦ ",
    "⑧ ",
    "⑨ ",
    "⑩ ",
    "⑪ ",
    "⑫ ",
]


def parse_tanki_yoho_kaisetsu(svg_path_file_name):
    date_time_str = svg_path_file_name.split(os.path.sep)[-2]
    print(date_time_str)
    text = extract_text_from_svg(svg_path_file_name)

    # section_separetorsの各要素の直後に改行を付ける
    for sep in section_separetors:
        # なぜか、sectionタイトルが2回出てくる。(ずらして2回出して太字にしてる?)
        text = text.replace(f'{sep}{sep}', f"\n{sep}")
        text = text.replace(f'{sep} {sep}', f"\n{sep}")
        text = text.replace(f'{sep}  {sep}', f"\n{sep}")
        # 2回出てきていないsectionタイトルもあるので、改行を付与
        text = text.replace(sep, f"{sep}\n")

#    with open(os.path.join(output_dir, f"{date_time_str}.txt"), "w", encoding="utf-8") as f:
#        f.write(text)

    sections = []
    section_obj = {"name":"","sentences":[],"subsections":[]}
    idx = 0
    # 改行コードで分割された各文字列に対して。
    for line in text.split("\n"):
        stripped = line.strip()
        # section_separetorsの要素と一致する場合
        if stripped in section_separetors:
            idx += 1
            section_name = stripped.split("．")[-1].replace("1","")
            if 0 < len(section_obj["name"]):
                sections.append(section_obj)
            section_obj = {"name":section_name,"sentences":[],"subsections":[]}
        else:
            sentences = [sentence.strip() for sentence in line.strip().split("。") if 0 < len(sentence.strip())]

            sub_idx = 0
            subsection_name = None
            subsection_obj = {"name":"","sentences":[]}
            for ele in sentences:
                sentence = ele.strip()+"。"
                # 〇数字で始まるもの。
                if sentence.strip().startswith(subsectoin_separetors[sub_idx]):
                    subsection_name = subsectoin_separetors[sub_idx].strip()
                    if 0 < sub_idx:
                        section_obj["subsections"].append(subsection_obj)
                    subsection_obj = {"name":subsection_name,"sentences":[]}
                    subsection_obj["sentences"].append(sentence.replace(subsectoin_separetors[sub_idx], ""))
                    sub_idx += 1
                elif sub_idx == 0:
                    if sentence.startswith("1量的な予報については"):
                        sentence = sentence.replace("1量的な予報については", "量的な予報については")
                    section_obj["sentences"].append(sentence)
                else:
                    subsection_obj["sentences"].append(sentence)
            if 0 < len(subsection_obj["sentences"]):
                section_obj["subsections"].append(subsection_obj)
    sections.append(section_obj)
    return sections

if __name__ == "__main__":
    glob_path = os.path.join(os.path.dirname(__file__), "weather_charts", "**","kaisetsu_tanki.svg")
    files = glob.glob(glob_path)
    output_dir = os.path.join(os.path.dirname(__file__), "kaisetsu_tanki_text")
    os.makedirs(output_dir, exist_ok=True)
    for file in files:
        sections = parse_tanki_yoho_kaisetsu(file)
            
