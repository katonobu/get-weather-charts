import os
import json
import shutil
import keyring

# 汎用資格情報から指定したサービス名、ユーザ名のパスワードを取得する

URL ="https://github.com/katonobu/get-weather-charts"
USER = "github-token"

def get_github_token():
    """keyringからGitHubのアクセストークンを取得する"""
    return keyring.get_password(URL, USER)

def _get_output_dir():
    # 出力ディレクトリ定義
    output_dir = os.path.join(os.path.dirname(__file__), "weather_charts")
    if not os.path.isdir(output_dir):
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(output_dir, exist_ok=True)
    return output_dir

def _get_artifact_ids_file_path():
    output_dir = _get_output_dir()
    return os.path.join(output_dir, "artifact_ids.json")

def get_artifact_ids():
    # ファイルパス取得
    artifact_ids_file = _get_artifact_ids_file_path()

    # artifact_ids.jsonが存在しない場合は空のリストを作成
    if not os.path.isfile(artifact_ids_file):
        # 出力ディレクトリにartifact_ids.jsonが存在しない場合は作成
        with open(artifact_ids_file, "w", encoding="utf-8") as f:
            f.write("[]")

    # artifact_ids.jsonを読み込む
    with open(artifact_ids_file, "r", encoding="utf-8") as f:
        artifact_ids = set(json.load(f))

    return artifact_ids

def copy_output(src_dir):
    title = os.path.basename(src_dir)
    output_dir = _get_output_dir()
    print(f'copying output to {os.path.join(output_dir, title)}')
    shutil.copytree(src_dir, os.path.join(output_dir, title), dirs_exist_ok=True)
    return {}

def append_artifact_info(artifact, src_dir, copy_result_obj):
    artifact_ids = list(get_artifact_ids())
    artifact_ids.append(artifact["id"])
    artifact_ids_file = _get_artifact_ids_file_path()
    with open(artifact_ids_file, "w", encoding="utf-8") as f:
        json.dump(artifact_ids, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    if get_github_token() is None:
        print("GitHub token not found in keyring. Please enter your GitHub token:")
        token = input().strip()
        keyring.set_password(URL, USER, token)
        print("GitHub token saved in keyring.")
    else:
        print("GitHub token already set in keyring.")
        token = get_github_token()
        print(f'{token[:3]}{"*"*(len(token)-6)}{token[-3:]}')