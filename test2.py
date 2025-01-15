import sys
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import os.path

# 设置plotly默认主题（可选）
px.defaults.template = 'simple_white'

def convert_duration_to_seconds(duration_str):
    """将视频时长字符串转换为秒数"""
    if isinstance(duration_str, str):  # 确保输入是字符串
        parts = duration_str.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        else:
            return int(parts[0])  # 如果只有秒数
    return duration_str  # 如果不是字符串，则保持原样

def process_csv_and_create_visualizations(input_file_path, output_base_path):
    df = pd.read_csv(input_file_path)

    if '视频时长' in df.columns:
        df['视频时长_秒'] = df['视频时长'].apply(convert_duration_to_seconds)

    df.dropna(subset=['视频时长_秒', '点赞数量'], inplace=True)
    df['点赞数量_log'] = np.log1p(df['点赞数量'])

    scatter_html_path = f"{output_base_path}_scatter.html"
    heatmap_html_path = f"{output_base_path}_heatmap.html"
    main_txt_path = f"{output_base_path}.txt"

    fig = px.scatter(df, x='视频时长_秒', y='点赞数量_log',
                     title='视频时长与经过对数转换后的点赞数量的关系',
                     labels={'视频时长_秒': '视频时长 (秒)', '点赞数量_log': '点赞数量 (Log Scale)'})

    correlation_log = df[['视频时长_秒', '点赞数量_log']].corr().iloc[0, 1]
    correlation_message = f'视频时长与经过对数转换后的点赞数量之间的皮尔逊相关系数: {correlation_log:.2f}'

    fig.write_html(scatter_html_path)

    fig_heatmap = ff.create_2d_density(
        df['视频时长_秒'], df['点赞数量_log'],
        title='视频时长与点赞数量的密度分布',
        colorscale='Viridis',
        hist_color='rgba(255, 217, 102, .8)',
        point_size=3
    )

    # 更新布局中的标题属性
    fig_heatmap.update_layout(
        title={
            'text': '视频时长与点赞数量的密度分布',
            'y': 0.95,  # 调整标题与图表内容的距离
            'x': 0.5,  # 标题居中
            'yref': 'container'  # 相对于容器的 y 坐标
        },
        xaxis_title="视频时长 (秒)",
        yaxis_title="点赞数量 (Log Scale)"
        
    )

    # 显示图表
    # fig_heatmap.show()
    fig_heatmap.write_html(heatmap_html_path)
    # 将消息写入文本文件
    with open(main_txt_path, 'w') as file:
        file.write(correlation_message)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python test2.py <input_csv_path> <output_base_path>")
        sys.exit(1)

    input_csv_path = sys.argv[1]
    output_base_path = sys.argv[2].replace('.html', '')  # 去掉可能存在的.html后缀
    process_csv_and_create_visualizations(input_csv_path, output_base_path)


