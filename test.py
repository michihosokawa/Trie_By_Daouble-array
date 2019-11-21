from DArrayTail import DArrayTail
from measure import MeasureTime, MeasureMemory
import numpy as np
import sys

"""
USAGE : python test.py 辞書ファイル テストファイル 試行回数 結果ファイル
"""
if len(sys.argv) < 5:
    print('Format = {} source_file test_file count result_file'.format(sys.argv[0]))
    sys.exit()

source_file = sys.argv[1]
test_file = sys.argv[2]
trial = int(sys.argv[3])
result_file = sys.argv[4]

# 辞書ファイル読み込み
words_org_set = set()
with open(source_file, 'r', encoding='utf-8') as f:
    line = f.readline()
    while line:
        line = line.rstrip()
        words_org_set.add(line)
        line = f.readline()
words_org = sorted(words_org_set)

# テストデータ読み込み
words = []
with open(test_file, 'r', encoding='utf-8') as f:
    line = f.readline()
    while line:
        line = line.rstrip()
        words.append(line)
        line = f.readline()

# 結果出力ファイル
f = open(result_file, 'w')

print("=========================== 使用データ ===========================", file=f)
print("PATH：",sys.argv[2], file=f)
print("サンプルサイズ：", len(words), file=f)
print("テスト回数：",trial, file=f)

# Trie木作成
print("=========================== 使用メモリ ===========================", file=f)

# TRIE作成
da_trie = DArrayTail()
da_trie.make(words_org)

m = MeasureMemory()
# Nodeの使用メモリ
print("tail:", m.convert_bytes(m.compute_object_size(da_trie.tails)), file=f)
print("base:", m.convert_bytes(m.compute_object_size(da_trie.base)), file=f)
print("check:", m.convert_bytes(m.compute_object_size(da_trie.check)), file=f)

# 実行時間計測
print("============================ 実行時間 ============================", file=f)
exact_search = []

for j in range(trial):
    # word検索の実行時間測定インスタンス作成
    es = MeasureTime(da_trie.search_string)
    c = 0

    # 検索を実行
    for query in words:
        # 単語検索
        rec_no = es.exe_func(query)
        if rec_no != -1 and words_org[rec_no] == query:
            c+=1

    print("--",  j+1, "回目", file=f)
    print(" ・完全一致検索:", " time:"+str(round(es.exe_time, 4))+"秒", " 検索件数："+"{:,d}".format(c)+"件", file=f)
    exact_search.append(es.exe_time)

print("============================ 平均実行時間 ============================", file=f)
print("完全一致検索：", str(round(np.mean(exact_search), 4))+"秒", file=f)

f.close()

print("Test is done.")
