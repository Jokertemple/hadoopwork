package com.example.mapreduce;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.log4j.Logger;

import java.io.IOException;

public class VideoInteractionMapper extends Mapper<LongWritable, Text, Text, IntWritable> {
    private static final Logger logger = Logger.getLogger(VideoInteractionMapper.class);
    private final static IntWritable one = new IntWritable();
    private Text videoId = new Text();

    @Override
    protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        String line = value.toString();
        String[] columns = line.split(",");

        if (columns.length == 14 && !line.startsWith("用户名")) { // 跳过标题行
            try {
                String videoUrl = columns[6].trim(); // 视频 URL 作为唯一标识符
                int likes = Integer.parseInt(columns[9].trim());
                int favorites = Integer.parseInt(columns[10].trim());
                int comments = Integer.parseInt(columns[11].trim());
                int downloads = Integer.parseInt(columns[12].trim());
                int shares = Integer.parseInt(columns[13].trim());

                int totalInteractions = likes + favorites + comments + downloads + shares;
                videoId.set(videoUrl);
                one.set(totalInteractions);
                context.write(videoId, one);
                logger.info("Processed line: " + line + " -> " + videoUrl + " : " + totalInteractions);
            } catch (NumberFormatException e) {
                logger.warn("Ignoring line due to format error: " + line, e);
            }
        }
    }
}
