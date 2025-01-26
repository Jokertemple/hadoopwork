import sys
import pandas as pd
import re
from collections import Counter
import plotly.express as px

def extract_hashtags(text):
    # 确保输入是字符串，如果是数字或其他类型，转换为字符串
    text = str(text)
    hashtags = re.findall(r'#\w+', text)
    return hashtags

def main(csv_file_path, output_html_path):
    df = pd.read_csv(csv_file_path)

    if '话题标签' not in df.columns:
        df['话题标签'] = df['视频描述'].apply(extract_hashtags)

    hashtag_likes_counter = Counter()

    for index, row in df.iterrows():
        hashtags = row['话题标签']
        likes = row.get('点赞数量', 0)
        for hashtag in hashtags:
            hashtag_likes_counter[hashtag] += likes

    df_hashtag_likes = pd.DataFrame(list(hashtag_likes_counter.items()), columns=['话题标签', '总点赞数'])
    df_hashtag_likes_sorted = df_hashtag_likes.sort_values(by='总点赞数', ascending=False)

    top_n = 10
    top_hashtags = df_hashtag_likes_sorted.head(top_n)

    if len(df_hashtag_likes_sorted) > top_n:
        other_likes = df_hashtag_likes_sorted[top_n:]['总点赞数'].sum()
        other_df = pd.DataFrame([{'话题标签': '其他', '总点赞数': other_likes}])
        top_hashtags = pd.concat([top_hashtags, other_df], ignore_index=True)

    fig = px.pie(top_hashtags, names='话题标签', values='总点赞数', title=f'Top {top_n} 最受欢迎话题标签及其点赞数的比例')
    fig.update_traces(textposition='inside', textinfo='percent+label')

    fig.update_layout(
    width=700,  # 设置饼图的宽度
    height=500,  # 设置饼图的高度
    margin=dict(l=100, r=200, t=50, b=50),  # 饼图位置
    legend=dict(x=1.1, y=0.5)  # 调整图例位置
    )
    
    # Save the figure to an HTML file.
    fig.write_html(output_html_path)

if __name__ == "__main__":
    csv_file_path = sys.argv[1]
    output_html_path = sys.argv[2]
    main(csv_file_path, output_html_path)   