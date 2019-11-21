# Trie By Double-array
PythonによるTRIE実装　～ダブル配列（Tailあり）～

## 概要
Pythonによるダブル配列の実装です。ダブル配列によるTRIEのPythonによる実装の性能を確認したかったのですが、納得のいく実装が見つからなかったので、自作しました。

TRIE構造作成での速度・メモリに関してはあまり考慮していません。

メモリ上でダブル配列を作成して、メモリ上で性能測定しています。TRIEのファイル書き出し／読み込みはありません。動的追加等も未対応です。

今のところ、完全一致検索のみを実装しています。

## ファイル構成
| ファイル | 内容 | 
|---|---|
| DArrayTail.py | ダブル配列本体 |
| TempDATrieNode.py | TRIE構造(仮) |
| test.py | 性能計測用 |
| measure.py | メモリ量／実行時間計測ツール | 
| sample | データ形式確認用サンプルを格納|
| sample / source.txt | 辞書データファイルサンプル|
| sample / text.txt | テストデータファイルサンプル|

## 実行例
```shell
python test.py sample/source.txt sample/test.txt 10 result.txt
```

- source.txtを辞書データとしてTRIE構造を作成します
	- 辞書データには1行に1単語の文字列が書かれています
- test.txtをテストデータとして完全一致検索を実施します
	- テストデータも辞書データと同じ形式です
- 10は試行回数です。10回繰り返して平均速度を計算します。
- result.txtは結果ファイルです。計測結果を書き出します。

