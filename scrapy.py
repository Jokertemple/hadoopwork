import sys
import time
import datetime
import csv
import pandas as pd
from DrissionPage import ChromiumPage
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def get_time(ctime):
    return time.strftime("%Y.%m.%d", time.localtime(ctime))

def save_video_info(video_data):
    minutes = video_data['video']['duration'] // 1000 // 60
    seconds = video_data['video']['duration'] // 1000 % 60
    video_dict = {
        '用户名': video_data['author']['nickname'].strip(),
        '用户uid': 'a' + str(video_data['author']['uid']),
        '用户ID': video_data['author']['sec_uid'],
        '粉丝数量': video_data['author']['follower_count'],
        '发表时间': get_time(video_data['create_time']),
        '视频awemeid': 'a' + video_data['aweme_id'],
        '视频url': 'https://www.douyin.com/video/' + str(video_data['aweme_id']),
        '视频描述': video_data['desc'].strip().replace('\n', ''),
        '视频时长': f"{minutes:02d}:{seconds:02d}",
        '点赞数量': video_data['statistics']['digg_count'],
        '收藏数量': video_data['statistics']['collect_count'],
        '评论数量': video_data['statistics']['comment_count'],
        '下载数量': video_data['statistics']['download_count'],
        '分享数量': video_data['statistics']['share_count'],
        '总互动量': 0
    }

    print(
        f"用户名: {video_dict['用户名']}\n",
        f"用户uid: {video_dict['用户uid']}\n",
        f"用户ID: {video_dict['用户ID']}\n",
        f"粉丝数量: {video_dict['粉丝数量']}\n",
        f"发表时间: {video_dict['发表时间']}\n",
        f"视频awemeid: {video_dict['视频awemeid']}\n",
        f"视频url: {video_dict['视频url']}\n",
        f"视频描述: {video_dict['视频描述']}\n",
        f"视频时长: {video_dict['视频时长']}\n",
        f"点赞数量: {video_dict['点赞数量']}\n",
        f"收藏数量: {video_dict['收藏数量']}\n",
        f"评论数量: {video_dict['评论数量']}\n",
        f"下载数量: {video_dict['下载数量']}\n",
        f"分享数量: {video_dict['分享数量']}\n"
        f"总互动量: {video_dict['总互动量']}\n"
        
    )

    return video_dict

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python scrapy.py <keyword> <output_dir>")
        sys.exit(1)

    keyword = sys.argv[1]
    output_dir = sys.argv[2]
    timestamp = sys.argv[3]
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 创建文件对象并写入表头
    today_indx = datetime.date.today()
    csv_file_path = os.path.join(output_dir, f'{timestamp}.csv')

    with open(csv_file_path, mode='w', encoding='utf-8-sig', newline='') as f:
        csv_writer = csv.DictWriter(f, fieldnames=[
            '用户名', '用户uid', '用户ID', '粉丝数量', '发表时间', '视频awemeid',
            '视频url', '视频描述', '视频时长', '点赞数量', '收藏数量', '评论数量',
            '下载数量', '分享数量','总互动量'
        ])
        csv_writer.writeheader()

    # 打开浏览器并监听数据包
    driver = ChromiumPage()
    driver.listen.start('www.douyin.com/aweme/v1/web/search/item', method='GET')

    url = f'https://www.douyin.com/search/{keyword}?type=video'
    print(url)
    driver.get(url)

    data_list = []
    for page in range(10):
        print(f'正在采集第{page + 1}页的数据内容')
        driver.scroll.to_bottom()
        resp = driver.listen.wait()
        json_data = resp.response.body
        time.sleep(2)

        if not json_data['has_more']:
            break

        for json_aweme_info in json_data['data']:
            data = save_video_info(json_aweme_info['aweme_info'])
            data_list.append(data)

    df = pd.DataFrame(data=data_list)

    # 只保留CSV输出
    df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')  # 防止乱码

    print(f"数据已成功保存到 {csv_file_path}")