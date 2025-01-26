package com.example.mapreduce;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.log4j.Logger;

import java.io.IOException;

public class VideoInteractionReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
    private static final Logger logger = Logger.getLogger(VideoInteractionReducer.class);
    private final IntWritable result = new IntWritable();

    @Override
    protected void reduce(Text key, Iterable<IntWritable> values, Context context) throws IOException, InterruptedException {
        int sum = 0;
        for (IntWritable val : values) {
            sum += val.get();
        }
        result.set(sum);
        context.write(key, result);
        logger.info("Reduced key: " + key.toString() + " -> " + sum);
    }
}
