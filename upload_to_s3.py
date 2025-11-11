import os
import time
import shutil
import datetime

if __name__ == "__main__":
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    output_base_dir = os.path.join(os.path.dirname(__file__), datetime.datetime.now().strftime('%Y%m%d_%H%M'))
    # 発表時刻名のディレクトリを掘る
    os.makedirs(output_base_dir, exist_ok=True)

    for i in range(5):
        file_path = os.path.join(output_base_dir, f'test_file_{i+1}.txt')
        with open(file_path , "w", encoding="utf-8") as f:
            f.write(f"This is test file {i+1}.\n")
        time.sleep(1)

    shutil.make_archive("output", format='zip', root_dir=os.path.dirname(output_base_dir), base_dir=os.path.basename(output_base_dir))
    print(f'Output saved to {output_base_dir} and output.zip')
    print(f'Finished at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    exit(0)
