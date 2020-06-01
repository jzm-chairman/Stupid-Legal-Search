import time
from collections import defaultdict


def is_chinese_char(ch):
    return '\u4e00' <= ch <= '\u9fff'


def is_chinese_str(s):
    for c in s:
        if not is_chinese_char(c):
            return False
    return True


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
                # if i > 100:
                #     break
        self.cnt = cnt
        print("embedding load finishs, got %d words, cost %lf time" % (cnt, time.time() - begin_time))

    def get_emb(self, word):
        word = self.key_to_id[word]
        return self.id_to_emb[word]