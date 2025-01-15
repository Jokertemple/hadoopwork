const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors'); // 导入 cors 中间件
const { exec } = require('child_process');
const util = require('util');
const fs = require('fs');
const path = require('path');
const moment = require('moment');
const baseDir = ('Users/123/Desktop/hadoopwork');

const app = express();
const port = 3000;

app.use(bodyParser.json());
app.use(cors()); // 使用 cors 中间件
// 将 exec 函数转换为 Promise 形式
const execPromise = util.promisify(exec);
// 将 fs.unlink 转换为 Promise 形式
const unlinkPromise = util.promisify(fs.unlink);
const deleteOldFiles = async (dir, keyword, today) => { //删除旧文件，实现拓展功能可能会用到
  try {
    const files = await fs.promises.readdir(dir);
    for (const file of files) {
      if (file.startsWith(`${keyword}-${today}`)) {
        const filePath = path.join(dir, file);
        await unlinkPromise(filePath);
        console.log(`Deleted old file: ${filePath}`);
      }
    }
  } catch (err) {
    if (err.code === 'ENOENT') {
      console.log(`Directory does not exist: ${dir}`);
    } else {
      console.error(`Error deleting old files: ${err.message}`);
    }
  }
};


app.post('/submit', async (req, res) => {
  try {
    console.log('开始处理提交请求...');
    const keyword = req.body.keyword;
    console.log(`接收到关键词: ${keyword}`);
    
    const now = moment();
    const timestamp = now.format('YYYY-MM-DD-HH-mm');
    console.log(`当前日期: ${timestamp}`);

    const inputDir = path.join(__dirname, 'input'); // 定义输入目录
    const outputDir = path.join(__dirname, 'output'); // 定义输出目录
    console.log(`输入目录: ${inputDir}`);
//    // 如果已经存在，删除input和output并重新生成         没必要了，因为python本身是会覆盖同名文件的
//    await deleteOldFiles(inputDir, keyword, today);
//    await deleteOldFiles(outputDir, keyword, today);
    const scrapyOutputFile = path.join(inputDir, `${timestamp}.csv`);
    console.log(`爬虫输出文件路径: ${scrapyOutputFile}`);

    // 调用 Python 爬虫脚本，并传递关键词
    console.log('调用Python爬虫脚本...');
    await execPromise(`python scrapy.py "${keyword}" "${inputDir}" "${timestamp}"`);
    console.log('Python爬虫脚本调用完成.');

    if (!fs.existsSync(scrapyOutputFile)) {
      throw new Error(`爬虫生成的文件不存在: ${scrapyOutputFile}`);
    }
    console.log(`确认爬虫输出文件存在: ${scrapyOutputFile}`);


    const hadoopInputPath = `C:/Users/123/Desktop/hadoopwork/input/${timestamp}.csv`;
    const hadoopOutputPath = `C:/Users/123/Desktop/hadoopwork/output/${timestamp}output`;
    console.log('调用Hadoop MapReduce作业...');
    await execPromise(`python video_interaction.py "${hadoopInputPath}" --output-dir="${hadoopOutputPath}"`);
    await execPromise(`python video_interaction.py "${hadoopInputPath}" --output-dir="${hadoopOutputPath}"`);
    console.log('Hadoop MapReduce作业调用完成.');

   
    const combinedOutputFile = path.join(outputDir, `${timestamp}_combined_output.txt`);
    console.log('调用Python脚本合并输出文件...');
    await execPromise(`python together.py "${hadoopOutputPath}" "${combinedOutputFile}"`);
    console.log(`所有输出已合并到 ${combinedOutputFile}`);

    // 检查Hadoop MapReduce作业的输出文件是否存在
    if (!fs.existsSync(combinedOutputFile)) {
      throw new Error(`Hadoop MapReduce作业的输出文件不存在: ${combinedOutputFile}`);
    }
    console.log(`确认Hadoop MapReduce作业的输出文件存在: ${combinedOutputFile}`);
    
    
    // 读取合并后的输出文件并创建 awemeid 到互动量的映射
    const interactionData = fs.readFileSync(combinedOutputFile, 'utf-8')
      .split('\n')
      .filter(line => line.trim() !== '')
      .reduce((map, line) => {
        const [awemeid, interactions] = line.split('\t');
        map[awemeid.replace(/"/g, '')] = parseInt(interactions, 10);
        return map;
      }, {});

    console.log('读取到的总互动量信息:', interactionData);

    // 读取原始 CSV 文件并转换为数组的数组
    const csvData = fs.readFileSync(scrapyOutputFile, 'utf-8')
      .split('\n')
      .filter(line => line.trim() !== '')
      .map(line => line.split(','));

    // 遍历 CSV 文件中的每一行，替换互动量
    csvData.forEach((row, index) => {
      if (index === 0) return; // 跳过表头
      const awemeid = row[5]; // 假设视频awemeid在第6列 (F列)
      const interaction = interactionData[awemeid] || 0; // 获取互动量，如果没有则为0
      row[14] = interaction; // 假设“总互动量”在第15列 (O列)
    });

    // 覆盖原始CSV文件
    const updatedCsvContent = csvData.map(row => row.join(',')).join('\n');
    fs.writeFileSync(scrapyOutputFile, updatedCsvContent, 'utf-8');
    console.log(`原始CSV文件已更新: ${scrapyOutputFile}`);

    //定义输出文件路径

    const resultHtmlName = `${timestamp}.html`;
    const resultHtmlPath = path.join(outputDir, resultHtmlName);
    const scatterHtmlPath = resultHtmlPath.replace('.html', '_scatter.html');
    const heatmapHtmlPath = resultHtmlPath.replace('.html', '_heatmap.html');
    const correlationTxtPath = resultHtmlPath.replace('.html', '.txt');
    const interactionsHtmlPath = path.join(outputDir, `${timestamp}_interactions.html`);
    console.log(`定义总互动量分析结果文件路径: ${interactionsHtmlPath}`);
    console.log(`定义结果文件路径:\n主HTML: ${resultHtmlPath}\n散点图HTML: ${scatterHtmlPath}\n热图HTML: ${heatmapHtmlPath}\n相关性文本: ${correlationTxtPath}`);

    const scriptsToRun = [
      execPromise(`python test.py "${scrapyOutputFile}" "${resultHtmlPath}"`),
      execPromise(`python test2.py "${scrapyOutputFile}" "${scatterHtmlPath.replace('_scatter.html', '')}"`),
      execPromise(`python test3.py "${scrapyOutputFile}" "${interactionsHtmlPath}"`)
    ];

    console.log('并发执行所有Python脚本...');
    await Promise.all(scriptsToRun);
    console.log('所有Python脚本执行完毕.');

    const filesToCheck = [
      resultHtmlPath,
      scatterHtmlPath,
      heatmapHtmlPath,
      correlationTxtPath,
      interactionsHtmlPath
    ];
    for (const file of filesToCheck) {
      console.log(`检查文件是否存在: ${file}`);
      if (!fs.existsSync(file)) {
        throw new Error(`结果文件不存在: ${file}`);
      }
      console.log(`确认文件存在: ${file}`);
    }

    let correlationMessage = '';
    try {
      correlationMessage = fs.readFileSync(correlationTxtPath, 'utf-8');
    } catch (err) {
      console.error('读取相关性信息文本文件失败:', err.message);
    }

    console.log('准备发送响应给客户端...');
    res.json({
      message: '任务已完成',
      correlationMessage,
      htmlUrls: {
        main: `/${outputDir}/${timestamp}.html`,
        scatter: `/${outputDir}/${timestamp}_scatter.html`,
        heatmap: `/${outputDir}/${timestamp}_heatmap.html`,
        interactions: `/${outputDir}/${timestamp}_interactions.html`
      }
    });
    console.log('响应已发送给客户端.');
  } catch (error) {
    handleError(error.message, res);
  }
});

function handleError(message, res) {
  console.error('发生错误:', message);
  if (!res.headersSent) { // 确保只有在没有发送响应头的情况下才发送错误响应
    console.error('发送错误响应给客户端...');
    res.status(500).json({ error: message });
  }
}

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});