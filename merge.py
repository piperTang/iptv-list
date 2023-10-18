import os

# 获取当前目录下的所有txt文件
txt_files = [file for file in os.listdir() if file.endswith(".txt")]

# 打开index.txt文件，以追加模式添加内容
with open("index.txt", "a") as index_file:
    for txt_file in txt_files:
        # 检查当前文件是否为index.txt，如果是则跳过
        if txt_file == "index.txt":
            continue

        # 获取文件名（去掉后缀名）
        file_name = os.path.splitext(txt_file)[0]

        # 写入文件名,#genre#作为单独一行，并添加换行符
        index_file.write(f"{file_name},#genre#\n")

        # 打开当前txt文件，读取内容并写入index.txt
        with open(txt_file, "r") as current_file:
            # 读取当前文件的内容并写入index.txt
            content = current_file.read()
            index_file.write(content)
            # 添加换行符
            index_file.write("\n")
            # 写入空行
            index_file.write("\n")

print("合并完成！")
