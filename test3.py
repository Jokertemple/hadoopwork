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

    hashtag_interactions_counter = Counter()

    for index, row in df.iterrows():
        hashtags = row['话题标签']
        interactions = row.get('总互动量', 0)
        for hashtag in hashtags:
            hashtag_interactions_counter[hashtag] += interactions

    df_hashtag_interactions = pd.DataFrame(list(hashtag_interactions_counter.items()), columns=['话题标签', '总互动量'])
    df_hashtag_interactions_sorted = df_hashtag_interactions.sort_values(by='总互动量', ascending=False)

    top_n = 10
    top_hashtags_interactions = df_hashtag_interactions_sorted.head(top_n)

    if len(df_hashtag_interactions_sorted) > top_n:
        other_interactions = df_hashtag_interactions_sorted[top_n:]['总互动量'].sum()
        other_df_interactions = pd.DataFrame([{'话题标签': '其他', '总互动量': other_interactions}])
        top_hashtags_interactions = pd.concat([top_hashtags_interactions, other_df_interactions], ignore_index=True)

    fig = px.pie(top_hashtags_interactions, names='话题标签', values='总互动量', title=f'Top {top_n} 最受欢迎话题标签及其互动量的比例')
    fig.update_traces(textposition='inside', textinfo='percent+label')

    fig.update_layout(
        width=700,  # 设置饼图的宽度
        height=500,  # 设置饼图的高度
        margin=dict(l=100, r=200, t=50, b=50),  # 饼图位置
        legend=dict(x=1.0, y=0.5)  # 调整图例位置
    )
    
    # Save the figure to an HTML file.
    fig.write_html(output_html_path)
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test3.py <csv_file_path> <output_html_path>")
        sys.exit(1)

    csv_file_path = sys.argv[1]
    output_html_path = sys.argv[2]
    main(csv_file_path, output_html_path)
