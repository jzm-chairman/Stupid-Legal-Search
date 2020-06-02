import time
import re
from collections import defaultdict
import numpy as np


def is_chinese_char(ch):
    return '\u4e00' <= ch <= '\u9fff'


def is_chinese_str(s):
    for c in s:
        if not is_chinese_char(c):
            return False
    return True


def trim_and_cut(text):
    text = re.split(r"[^0-9\u4e00-\u9af5]", text)
    return text


class Embedding:
    def __init__(self, file):
        begin_time = time.time()
        cnt = 0
        self.unk_id = 0
        # self.id_to_key = ['UNK']
        # self.key_to_id = {'UNK': 0}
        self.id_to_key = []
        self.key_to_id = defaultdict(int)
        self.id_to_emb = [[0] * 300]
        with open(file, "r", encoding='utf8') as f:
            for i, line in enumerate(f.readlines()):
                val_list = line.split(' ')

                if i == 0:
                    self.dim = int(val_list[1])
                else:
                    word = val_list[0]
                    if is_chinese_char(word):
                        cnt += 1
                        self.id_to_key += [word]
                        self.key_to_id[word] = cnt
                        self.id_to_emb += [list(map(lambda x: float(x), val_list[1: -1]))]
        self.cnt = cnt
        print("embedding load finishs, got %d words, cost %lf time" % (cnt, time.time() - begin_time))

    def get_emb(self, word):
        word = self.key_to_id[word]
        return self.id_to_emb[word]


def calc_doc_vec(word_times_dict, word_doc_dict, total_doc, doc_len, emb):
    doc_vec = [0] * 300
    for word, times in word_times_dict.items():
        word_doc = word_doc_dict[word]
        tf_idf = times / doc_len * np.log(total_doc / (word_doc + 1))
        # print('word: {}, vector: {}'.format(word, emb.get_emb(word)))
        doc_vec = [np.around(x * tf_idf + y, decimals=2) for x, y in zip(emb.get_emb(word), doc_vec)]
    return doc_vec
