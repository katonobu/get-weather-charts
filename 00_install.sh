#/bin/bash
/usr/bin/python3 --version

cd "$(dirname "$0")"

echo --- generating venv ---
/usr/bin/python3 -m venv .venv

echo --- enter to venv。 ---
source ./.venv/bin/activate

echo --- upgrading pip ---
python -m pip install --upgrade pip

echo --- listing installed modues ---
pip list

#read -p "Hit enter: "

echo --- installing pip modules ---
pip install -r requirements.txt

echo --- listing installed modues ---
pip list
