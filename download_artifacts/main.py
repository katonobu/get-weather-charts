import os
import glob
import json
import datetime
import requests
import tempfile
import zipfile
import shutil

from keyring_util import get_github_token

if __name__ == "__main__":
    # 設定項目
    # 右上のSettings > Developer settings > Fine-grained personal access tokens からトークンを取得
    # Repository access で Only select repositoriesを選択して、DropDownlistでget-weather-chartsを選択
    # Permissions で Actions > Read-only を選択
    GITHUB_TOKEN = get_github_token()
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
        loaded_artifacts = response.json().get("artifacts", [])
        if loaded_artifacts:
            artifacts = sorted(loaded_artifacts, key=lambda x: datetime.datetime.strptime(x['created_at'], "%Y-%m-%dT%H:%M:%SZ"))
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f'{len(artifacts)} artifacts found. Downloading and extracting...')
                for artifact in artifacts[:min(10, len(artifacts))]:
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
                                downloaded_dirs = [item for item in glob.glob(os.path.join(temp_dir, "*")) if os.path.isdir(item)]
                                if len(downloaded_dirs) == 1:
                                    dir = downloaded_dirs[0]
                                    title = os.path.basename(dir)
                                    print(f'Extracting {title}')
                                    shutil.copytree(dir, os.path.join(output_dir, title), dirs_exist_ok=True)
                                    shutil.rmtree(dir)
                                    # artifact_ids.jsonを更新
                                    with open(artifact_ids_file, "w", encoding="utf-8") as f:
                                        json.dump(list(artifact_ids), f, ensure_ascii=False, indent=2)
                                else:
                                    print('Unexpected number of extracted directories.')
                                    break
                                # delete dirs
                                [shutil.rmtree(dir) for dir in downloaded_dirs if os.path.isdir(dir)]
                                # delete files
                                [os.remove(item) for item in glob.glob(os.path.join(temp_dir, "*")) if os.path.isfile(item)]
                                pass
                            else:
                                print(f"Error downloading {artifact['name']}: {response.status_code}, {response.text}")
                                continue
                        else:
                            print(f'Skipping {artifact["name"]} {artifact["created_at"]} id:{artifact["id"]} (already downloaded).')
                    else:
                        print(f'Skipping {artifact["name"]} (not in download list or missing ID/archive URL).')

        else:
            print("No artifacts found.")
    else:
        print(f"Error: {response.status_code}, {response.text}")

    print("Done.")