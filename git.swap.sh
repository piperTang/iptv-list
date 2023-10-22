#!/bin/bash
pwd
# 进入到目录
cd /ql/data/scripts/iptv-list
# 获取当前日期，格式为“年月日”
current_date=$(date +'%Y%m%d')
# 拉取最新代码
git pull origin main
# 提交变更并添加带有时间戳的 commit 注释
git add .
git commit -m "1panel自动提交-${current_date}"

# 推送到远程仓库（如果需要）
git push origin main

# 输出提交成功消息
echo "变更已提交到 Git 仓库。"

