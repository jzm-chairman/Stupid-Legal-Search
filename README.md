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

