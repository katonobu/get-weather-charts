import os
import glob
import json
import requests
import tempfile
import zipfile
import shutil
import markdown
import webbrowser

if __name__ == "__main__":
    # 設定項目
    GITHUB_TOKEN = "github_pat_access_token"  # ここにGitHubのアクセストークンを設定
    OWNER = "katonobu"
    REPO = "get-weather-charts"
    API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/artifacts"

    # APIリクエストのヘッダー
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    download_artifact_names = ["long-range-output-zip", "short-range-output-zip"]

    # 出力ディレクトリ定義
    output_dir = os.path.join(os.path.dirname(__file__), "weather_charts")
    if not os.path.isdir(output_dir):
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(output_dir, exist_ok=True)

    # artifact_ids.json定義
    artifact_ids_file = os.path.join(output_dir, "artifact_ids.json")
    # artifact_ids.jsonが存在しない場合は空のリストを作成
    if not os.path.isfile(artifact_ids_file):
        # 出力ディレクトリにartifact_ids.jsonが存在しない場合は作成
        with open(artifact_ids_file, "w", encoding="utf-8") as f:
            f.write("[]")

    # artifact_ids.jsonを読み込む
    with open(artifact_ids_file, "r", encoding="utf-8") as f:
        artifact_ids = set(json.load(f))

    # APIリクエストを送信
    response = requests.get(API_URL, headers=headers)

    # レスポンスを処理
    if response.status_code == 200:
        artifacts = response.json().get("artifacts", [])
        if artifacts:
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f'{len(artifacts)} artifacts found. Downloading and extracting...')
                for artifact in artifacts:
    #                print(json.dumps(artifact, indent=2, ensure_ascii=False))
                    if artifact["name"] in download_artifact_names and "id" in artifact and "archive_download_url" in artifact:
                        # アーティファクトのIDがまだ保存されていない場合
                        if artifact["id"] not in artifact_ids:
                            # 新しいアーティファクトのIDを追加
                            artifact_ids.add(artifact["id"])

                            print(f'{artifact["name"]} : {artifact["created_at"]} ({artifact["size_in_bytes"]} bytes) id:{artifact["id"]}')
                            archive_url = artifact["archive_download_url"]

                            # ZIPファイルをダウンロード
                            response = requests.get(archive_url, headers=headers, stream=True)
                            if response.status_code == 200:
                                zip_path = os.path.join(temp_dir, f'{artifact["id"]}.zip')
                                with open(zip_path, "wb") as file:
                                    count = 0
                                    for chunk in response.iter_content(chunk_size=8192):
                                        file.write(chunk)
                                        count += 1
                                        if count % 64 == 0:
                                            print('.', flush=True)
                                        else:
                                            print('.', end="", flush=True)
                                    print("O")
                                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                                    zip_ref.extractall(temp_dir)
                                with zipfile.ZipFile(os.path.join(temp_dir, "output.zip"), "r") as zip_ref:
                                    zip_ref.extractall(temp_dir)
                                os.remove(os.path.join(temp_dir, "output.zip"))
                            else:
                                print(f"Error downloading {artifact['name']}: {response.status_code}, {response.text}")
                                continue
                        else:
                            print(f'Skipping {artifact["name"]} {artifact["created_at"]} id:{artifact["id"]} (already downloaded).')
                    else:
                        print(f'Skipping {artifact["name"]} (not in download list or missing ID/archive URL).')
                # temp_dir内のディレクトリを取得
                downloaded_dirs = [item for item in glob.glob(os.path.join(temp_dir, "*")) if os.path.isdir(item)]
                for dir in downloaded_dirs:
                    title = os.path.basename(dir)
                    shutil.copytree(dir, os.path.join(output_dir, title), dirs_exist_ok=True)
                # Markdownテキストを作成
                md_text = "# 一覧\n\n"
                all_dirs = [item for item in glob.glob(os.path.join(output_dir, "*")) if os.path.isdir(item)]
                all_dirs.sort(reverse=True)  # 新しい順にソート
                for dir in all_dirs:
                    year = os.path.basename(dir)[:4]
                    month = os.path.basename(dir)[4:6]
                    day = os.path.basename(dir)[6:8]
                    hour =os.path.basename(dir)[9:11]  
                    min = os.path.basename(dir)[11:13]
                    time_stamp_str = f'{year}年{month}月{day}日 {hour}時{min}分'
                    # ディレクトリ名が00で終わっていたら
                    if dir.endswith("00"):
                        title = f'{time_stamp_str} 週間天気予報解説資料'
                    else:
                        title = f'{time_stamp_str} 短期予報解説資料'
                    # ディレクトリ名をタイトルとして使用
                    md_text += f'- <a href="./{os.path.basename(dir)}/index.html" target="_blank">{title}</a>\n'

                # output_dirにindex.htmlを作成
                html_text = markdown.markdown(md_text)
                top_html_path = os.path.join(output_dir, "index.html")
                with open(top_html_path, "w", encoding="utf-8") as f:
                    f.write(html_text)
                print(f'{len(downloaded_dirs)} artifacts downloaded and extracted successfully.')
                print(f'{len(all_dirs)} artifacts are ready to see.')
                # デフォルトブラウザでHTMLファイルを開く
                webbrowser.open("file://" + os.path.abspath(top_html_path))

            # artifact_ids.jsonを更新
            with open(artifact_ids_file, "w", encoding="utf-8") as f:
                json.dump(list(artifact_ids), f, ensure_ascii=False, indent=2)
        else:
            print("No artifacts found.")
    else:
        print(f"Error: {response.status_code}, {response.text}")

    print("Done.")