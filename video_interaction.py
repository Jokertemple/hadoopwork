from mrjob.job import MRJob
from mrjob.step import MRStep
import csv

class VideoInteractionMRJob(MRJob):

    def configure_args(self):
        super(VideoInteractionMRJob, self).configure_args()
        self.add_passthru_arg('--num-reducers', type=int, default=1, help='Number of reducers')

    def steps(self):
        return [
            MRStep(mapper=self.mapper, reducer=self.reducer)
        ]

    def mapper(self, _, line):
        # 跳过标题行
        if line.startswith('用户名'):
            return

        # 解析 CSV 行
        reader = csv.reader([line])
        for row in reader:
            if len(row) == 15:
                video_id = row[5]  # 视频awemeid
                likes = row[9].strip()
                favorites = row[10].strip()
                comments = row[11].strip()
                downloads = row[12].strip()
                shares = row[13].strip()

                # 验证数据是否为整数
                if likes.isdigit() and favorites.isdigit() and comments.isdigit() and downloads.isdigit() and shares.isdigit():
                    # 计算总互动量
                    total_interactions = int(likes) + int(favorites) + int(comments) + int(downloads) + int(shares)
                    yield video_id, total_interactions

    def reducer(self, video_id, total_interactions):
        # 汇总每个视频的总互动量
        total_interactions_sum = sum(total_interactions)
        yield video_id, total_interactions_sum

if __name__ == '__main__':
    VideoInteractionMRJob.run()
