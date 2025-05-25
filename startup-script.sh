#!/bin/bash
# 这里放置你想要在开机时执行的命令
echo "系统启动时间: $(date)" >> /var/log/my-startup.log
# 添加其他你需要的命令