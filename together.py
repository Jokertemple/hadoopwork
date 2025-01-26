import os
import glob

def merge_files(input_dir, output_file_path):
    # 获取所有 part 文件
    part_files = glob.glob(os.path.join(input_dir, 'part-*'))

    # 读取并合并内容
    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        for part_file in part_files:
            with open(part_file, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())

    print(f"所有输出已合并到 {output_file_path}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python together.py <input_dir> <output_file_path>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_file_path = sys.argv[2]
    merge_files(input_dir, output_file_path)
