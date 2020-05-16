# Stupid-Legal-Search
搜索引擎课的大作业：司法搜索

最简单的原型用法：

```
python preprocess.py 生成文件列表和倒排索引(暂时只用100篇)
python search.py 输入关键词搜索
```

Recall & Ranker Version1：

查询词分词后对取出的文档进行排序，第一关键字为出现的查询词数量，第二关键字为查询词的词频

倒排索引结构Version 1：

```json
temp/inverted_index.json
{
	term1(string): {
    	doc1(int): {
            "freq": freq1(int),
			"offset": [...](list(int))
        },
		doc2: {
            ...
        }
	},
	term2(string): {
        ...(同上)
    }
}
```

记录所有文书所在的相对路径的文件：

```
temp/filename.pkl
[name1, name2, ...]
```

## 简单服务器

首先将preprocess的结果导入MongoDB，在MongoDB的`bin/`目录下运行：

```bash
mongoimport --db SearchEngine --collection InvertedIndex --file sources/temp/inverted_index.json --jsonArray
```

接着在`sources/SearchEngine`启动服务器：

```bash
python manage.py runserver
```

访问`127.0.0.1:8000/query?term=$your term$`可以获取对应的倒排索引列表。

## 有前端了

先确定文件列表和倒排索引的位置在`temp/`

在`source/SearchEngine`下运行`manage.py`启动服务器

在`source/SearchEngine-FrontEnd`下运行

```
npm install
npm run dev
```

在前端代码中指定了后端端口为8000

如果发送请求的时候chrome浏览器报CORS错误(控制台可见)，就右键打开桌面chrome的快捷方式“属性”，在“目标”最后添加

```
--disable-web-security --user-data-dir=<某个目录>
```

关闭浏览器安全控制。用这种方式打开chrome，个人设置和历史记录会全部清空（不用这种方式打开即可恢复）。

