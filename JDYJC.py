import os
import re
import time
from datetime import datetime
import threading
from queue import Queue
import requests
import eventlet
eventlet.monkey_patch()

# 线程安全的队列，用于存储下载任务
task_queue = Queue()

# 线程安全的列表，用于存储结果
results = []

channels = []
error_channels = []

with open("JDY.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line:
            channel_name, channel_url = line.split(',')
            if 'CCTV' in channel_name:
                channels.append((channel_name, channel_url))


# 定义工作线程函数
def worker():
    while True:
        # 从队列中获取一个任务
        channel_name, channel_url = task_queue.get()
        try:
            channel_url_t = channel_url.rstrip(channel_url.split('/')[-1])  # m3u8链接前缀
            lines = requests.get(channel_url).text.strip().split('\n')  # 获取m3u8文件内容
            ts_lists = [line.split('/')[-1] for line in lines if line.startswith('#') == False]  # 获取m3u8文件下视频流后缀
            ts_lists_0 = ts_lists[0].rstrip(ts_lists[0].split('.ts')[-1])  # m3u8链接前缀
            ts_url = channel_url_t + ts_lists[0]  # 拼接单个视频片段下载链接

            # 多获取的视频数据进行5秒钟限制
            with eventlet.Timeout(5, False):
                start_time = time.time()
                content = requests.get(ts_url).content
                end_time = time.time()
                response_time = (end_time - start_time) * 1

            if content:
                with open(ts_lists_0, 'ab') as f:
                    f.write(content)  # 写入文件
                file_size = len(content)
                # print(f"文件大小：{file_size} 字节")
                download_speed = file_size / response_time / 1024
                # print(f"下载速度：{download_speed:.3f} kB/s")
                normalized_speed = min(max(download_speed / 1024, 0.001), 100)  # 将速率从kB/s转换为MB/s并限制在1~100之间
                # print(f"标准化后的速率：{normalized_speed:.3f} MB/s")

                # 删除下载的文件
                os.remove(ts_lists_0)
                result = channel_name, channel_url, f"{normalized_speed:.3f} MB/s"
                results.append(result)
                numberx = (len(results) + len(error_channels)) / len(channels) * 100
                print(
                    f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
        except:
            error_channel = channel_name, channel_url
            error_channels.append(error_channel)
            numberx = (len(results) + len(error_channels)) / len(channels) * 100
            print(
                f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")

        # 标记任务完成
        task_queue.task_done()


# 创建多个工作线程
num_threads = 10
for _ in range(num_threads):
    t = threading.Thread(target=worker, daemon=True)
    # t = threading.Thread(target=worker, args=(event,len(channels)))  # 将工作线程设置为守护线程
    t.start()
    # event.set()

# 添加下载任务到队列
for channel in channels:
    task_queue.put(channel)

# 等待所有任务完成
task_queue.join()


def channel_key(channel_name):
    match = re.search(r'\d+', channel_name)
    if match:
        return int(match.group())
    else:
        return float('inf')  # 返回一个无穷大的数字作为关键字


# 对频道进行排序
results.sort(key=lambda x: (x[0], -float(x[2].split()[0])))
results.sort(key=lambda x: channel_key(x[0]))

result_counter = 10  # 每个频道需要的个数

with open("cctv.txt", 'w', encoding='utf-8') as file:
    channel_counters = {}
    file.write('央视频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if 'CCTV' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1

with open("cctv.m3u", 'w', encoding='utf-8') as file:
    channel_counters = {}
    file.write('#EXTM3U\n')
    for result in results:
        channel_name, channel_url, speed = result
        if 'CCTV' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"#EXTINF:-1 group-title=\"央视频道\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"#EXTINF:-1 group-title=\"央视频道\",{channel_name}\n")
                file.write(f"{channel_url}\n")
                channel_counters[channel_name] = 1

# 线程安全的队列，用于存储下载任务
task_queue = Queue()

# 线程安全的列表，用于存储结果
results = []

channels = []
error_channels = []

with open("JDY.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line:
            channel_name, channel_url = line.split(',')
            if 'CCTV' not in channel_name:
                channels.append((channel_name, channel_url))


# 定义工作线程函数
def worker():
    while True:
        # 从队列中获取一个任务
        channel_name, channel_url = task_queue.get()
        try:
            channel_url_t = channel_url.rstrip(channel_url.split('/')[-1])  # m3u8链接前缀
            lines = requests.get(channel_url).text.strip().split('\n')  # 获取m3u8文件内容
            ts_lists = [line.split('/')[-1] for line in lines if line.startswith('#') == False]  # 获取m3u8文件下视频流后缀
            ts_lists_0 = ts_lists[0].rstrip(ts_lists[0].split('.ts')[-1])  # m3u8链接前缀
            ts_url = channel_url_t + ts_lists[0]  # 拼接单个视频片段下载链接

            # 多获取的视频数据进行5秒钟限制
            with eventlet.Timeout(5, False):
                start_time = time.time()
                content = requests.get(ts_url).content
                end_time = time.time()
                response_time = (end_time - start_time) * 1

            if content:
                with open(ts_lists_0, 'ab') as f:
                    f.write(content)  # 写入文件
                file_size = len(content)
                # print(f"文件大小：{file_size} 字节")
                download_speed = file_size / response_time / 1024
                # print(f"下载速度：{download_speed:.3f} kB/s")
                normalized_speed = min(max(download_speed / 1024, 0.001), 100)  # 将速率从kB/s转换为MB/s并限制在1~100之间
                # print(f"标准化后的速率：{normalized_speed:.3f} MB/s")

                # 删除下载的文件
                os.remove(ts_lists_0)
                result = channel_name, channel_url, f"{normalized_speed:.3f} MB/s"
                results.append(result)
                numberx = (len(results) + len(error_channels)) / len(channels) * 100
                print(
                    f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
        except:
            error_channel = channel_name, channel_url
            error_channels.append(error_channel)
            numberx = (len(results) + len(error_channels)) / len(channels) * 100
            print(
                f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")

        # 标记任务完成
        task_queue.task_done()


# 创建多个工作线程
num_threads = 10
for _ in range(num_threads):
    t = threading.Thread(target=worker, daemon=True)
    # t = threading.Thread(target=worker, args=(event,len(channels)))  # 将工作线程设置为守护线程
    t.start()
    # event.set()

# 添加下载任务到队列
for channel in channels:
    task_queue.put(channel)

# 等待所有任务完成
task_queue.join()


def channel_key(channel_name):
    match = re.search(r'\d+', channel_name)
    if match:
        return int(match.group())
    else:
        return float('inf')  # 返回一个无穷大的数字作为关键字


# 对频道进行排序
results.sort(key=lambda x: (x[0], -float(x[2].split()[0])))
# results.sort(key=lambda x: channel_key(x[0]))
result_counter = 10  # 每个频道需要的个数

with open("JDY_list.txt", 'w', encoding='utf-8') as file:
    channel_counters = {}
    file.write('卫视频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '卫视' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1

    channel_counters = {}
    file.write('省内频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '湖南' in channel_name or '长沙' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1

    channel_counters = {}
    file.write('港澳频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '凤凰' in channel_name or '翡翠' in channel_name or 'TVB' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1

    channel_counters = {}
    file.write('少儿频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '卡通' in channel_name or '少儿' in channel_name or '动画' in channel_name or '炫动' in channel_name or '动漫' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1

    # channel_counters = {}
    # file.write('求索纪实,#genre#\n')
    # for result in results:
    #     channel_name, channel_url, speed = result
    #     if '求索' in channel_name or '纪实' in channel_name or '地理' in channel_name:
    #         if channel_name in channel_counters:
    #             if channel_counters[channel_name] >= result_counter:
    #                 continue
    #             else:
    #                 file.write(f"{channel_name},{channel_url}\n")
    #                 channel_counters[channel_name] += 1
    #         else:
    #             file.write(f"{channel_name},{channel_url}\n")
    #             channel_counters[channel_name] = 1

    channel_counters = {}
    file.write('影视综合,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '电影' in channel_name or '影院' in channel_name or '戏剧' in channel_name or '戏曲' in channel_name or '影视' in channel_name or '梨园' in channel_name or '电视剧' in channel_name or '综艺' in channel_name or '剧场' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1

    channel_counters = {}
    file.write('其他频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if 'CCTV' not in channel_name and '卫视' not in channel_name and '地理' not in channel_name and 'BTV卡酷' not in channel_name and '凤凰' not in channel_name and '翡翠' not in channel_name and 'TVB' not in channel_name and '求索' not in channel_name and '纪实' not in channel_name and '钓' not in channel_name and '锦至' not in channel_name and '测试' not in channel_name and '演示' not in channel_name and '茶' not in channel_name and '购物' not in channel_name and '理财' not in channel_name and '湖南' not in channel_name and '长沙' not in channel_name and '卡通' not in channel_name and '少儿' not in channel_name and '动画' not in channel_name and '炫动' not in channel_name and '动漫' not in channel_name and '剧场' not in channel_name and '电影' not in channel_name and '影院' not in channel_name and '戏剧' not in channel_name and '戏曲' not in channel_name and '影视' not in channel_name and '梨园' not in channel_name and '电视剧影' not in channel_name and '综艺' not in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1


with open("JDY_list.m3u", 'w', encoding='utf-8') as file:
    channel_counters = {}
    # file.write('卫视频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '卫视' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"#EXTINF:-1 group-title=\"卫视频道\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"#EXTINF:-1 group-title=\"卫视频道\",{channel_name}\n")
                file.write(f"{channel_url}\n")
                channel_counters[channel_name] = 1

    channel_counters = {}
    # file.write('少儿频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '卡通' in channel_name or '少儿' in channel_name or '动画' in channel_name or '炫动' in channel_name or '动漫' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"#EXTINF:-1 group-title=\"少儿频道\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"#EXTINF:-1 group-title=\"少儿频道\",{channel_name}\n")
                file.write(f"{channel_url}\n")
                channel_counters[channel_name] = 1

    # channel_counters = {}
    # # file.write('求索纪实,#genre#\n')
    # for result in results:
    #     channel_name, channel_url, speed = result
    #     if '求索' in channel_name or '纪实' in channel_name or '地理' in channel_name:
    #         if channel_name in channel_counters:
    #             if channel_counters[channel_name] >= result_counter:
    #                 continue
    #             else:
    #                 file.write(f"#EXTINF:-1 group-title=\"求索纪实\",{channel_name}\n")
    #                 file.write(f"{channel_url}\n")
    #                 channel_counters[channel_name] += 1
    #         else:
    #             file.write(f"#EXTINF:-1 group-title=\"求索纪实\",{channel_name}\n")
    #             file.write(f"{channel_url}\n")
    #             channel_counters[channel_name] = 1

    channel_counters = {}
    # file.write('地方频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '湖南' in channel_name or '长沙' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"#EXTINF:-1 group-title=\"地方频道\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"#EXTINF:-1 group-title=\"地方频道\",{channel_name}\n")
                file.write(f"{channel_url}\n")
                channel_counters[channel_name] = 1

    channel_counters = {}
    # file.write('港澳频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '凤凰' in channel_name or '翡翠' in channel_name or 'TVB' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"#EXTINF:-1 group-title=\"港澳频道\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"#EXTINF:-1 group-title=\"港澳频道\",{channel_name}\n")
                file.write(f"{channel_url}\n")
                channel_counters[channel_name] = 1

    channel_counters = {}
    # file.write('影视综合,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '电影' in channel_name or '影院' in channel_name or '戏剧' in channel_name or '戏曲' in channel_name or '影视' in channel_name or '梨园' in channel_name or '电视剧' in channel_name or '综艺' in channel_name or '剧场' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"#EXTINF:-1 group-title=\"影视综合\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"#EXTINF:-1 group-title=\"影视综合\",{channel_name}\n")
                file.write(f"{channel_url}\n")
                channel_counters[channel_name] = 1

    channel_counters = {}
    # file.write('其他频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if 'CCTV' not in channel_name and '卫视' not in channel_name and '地理' not in channel_name and 'BTV卡酷' not in channel_name and '凤凰' not in channel_name and '翡翠' not in channel_name and 'TVB' not in channel_name and '求索' not in channel_name and '纪实' not in channel_name and '钓' not in channel_name and '锦至' not in channel_name and '测试' not in channel_name and '演示' not in channel_name and '茶' not in channel_name and '购物' not in channel_name and '理财' not in channel_name and '湖南' not in channel_name and '长沙' not in channel_name and '卡通' not in channel_name and '少儿' not in channel_name and '动画' not in channel_name and '炫动' not in channel_name and '动漫' not in channel_name and '剧场' not in channel_name and '电影' not in channel_name and '影院' not in channel_name and '戏剧' not in channel_name and '戏曲' not in channel_name and '影视' not in channel_name and '梨园' not in channel_name and '电视剧影' not in channel_name and '综艺' not in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"#EXTINF:-1 group-title=\"其他频道\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"#EXTINF:-1 group-title=\"其他频道\",{channel_name}\n")
                file.write(f"{channel_url}\n")
                channel_counters[channel_name] = 1

    # 合并自定义频道文件内容
    file_contents = []
    file_paths = ["cctv.txt", "JDY_list.txt", "zdy.txt"]  # 替换为实际的文件路径列表
    for file_path in file_paths:
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
            file_contents.append(content)

    # 写入合并后的文件
    with open("JDY_list.txt", "w", encoding="utf-8") as output:
        output.write('\n'.join(file_contents))
    # 写入更新日期时间
        now = datetime.now()
        output.write(f"更新时间,#genre#\n")
        output.write(f"{now.strftime("%Y-%m-%d")},url\n")
        output.write(f"{now.strftime("%H:%M:%S")},url\n")
   
    # 合并自定义频道文件内容
    file_contents = []
    file_paths = ["cctv.m3u", "JDY_list.m3u"]  # 替换为实际的文件路径列表
    for file_path in file_paths:
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
            file_contents.append(content)

    # 写入合并后的文件
    with open("JDY_list.m3u", "w", encoding="utf-8") as output:
        output.write('\n'.join(file_contents))

    os.remove("JDY.txt")
    os.remove("cctv.txt")
    os.remove("cctv.m3u")        

print("任务运行完毕，分类频道列表可查看文件夹内JDY_list.txt和JDY_list.m3u文件！")
