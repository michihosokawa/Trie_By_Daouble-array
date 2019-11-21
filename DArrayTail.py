import array
from TempDATrieNode import TempDATrieNode

class	DArrayTail:
	"""
	ダブル配列によるTRIE実装（Tail付）
	基本的には、全文帰しているTRIEと同じ
	ただし、TAILがある場合は、概念的にはTAILを1ノードとみなす
	実装上は、レコードとみなしてレコード中にTAIL文字列を格納する

	base[index+code]には次のbaseへのindexが格納されている
	あるノードが、レコード番号とTRIEを持つことがある。（部分文字列が単語になっている場合）
	このことを考慮し、終端文字は常に文字コード=0の分岐を持つことにする（文字コード=0が終端記号）

	レコード番号はindexと区別するために、0x80000000のビットがオンになっている
	TAILを持っているかどうかは、終端記号で遷移したかどうかで判定する

	indexは常に正でなければならない。index=0も許可されない
	index=0の領域base[0], check[0]は使用されない
	index=1が開始位置として使われる。
	したがってbaseとcheckの初期値は0でよい
	"""
	def	__init__(self):
		'''
		領域の初期化
		'''
		self.tails = {}		# record_no --> Tail文字列

		self.base = None	# ダブル配列：ベース
		self.check = None	# ダブル配列：チェック

	def	search_string(self, search_str):
		'''
		完全一致検索
		検索文字列と完全一致する単語のレコード番号を返す

		Parameters
		----------
		search_str : str
			検索単語(utf-8)

		Returns
		-------
		result : int
			レコード番号、存在しない単語なら-1
		'''
		# データ不正
		if self.base == None or len(self.base) ==0:
			return 0
		
		# 検索対象文字列のバイト列
		search_bytes = bytes(search_str, encoding='utf-8')

		search_pos = 0
		search_end = len(search_bytes)
		da_index_pre = 1
		da_index_base = self.base[da_index_pre]
		jump_code = int(search_bytes[search_pos])

		while True:
			da_index = da_index_base + jump_code
			base_value = self.base[da_index]
			check_value = self.check[da_index]
			if check_value == da_index_pre:
				if (base_value & 0x80000000) != 0:
					# record
					record_no = base_value & 0x7fffffff
					if jump_code == 0:
						# Leaf
						return record_no
					else:
						# has_tail
						if record_no in self.tails:
							if search_bytes[(search_pos+1):] == self.tails[record_no]:
								return record_no
					return -1
				# link 
				da_index_pre = da_index
				da_index_base = base_value 
				search_pos += 1
				if search_pos < search_end:
					# 文字コードで遷移
					jump_code = int(search_bytes[search_pos])
				elif search_pos == search_end:
					# 終端記号で遷移する
					jump_code = 0
				else:
					break
			else:
				break
		return -1

	def make(self, words):
		'''
		単語一覧をTRIE領域（仮）に作成し、DArrayに変換
		配列サイズが不明なので、まず、すべてのノードの幅の合計を配列サイズとし、その後、正しいサイズに調整する

		Parameters
		----------
		words : list
			単語文字列のリスト、インデックス番号がレコード番号
		'''
		# TRIE領域（仮）の作成
		temp_trie = TempDATrieNode()

		# 単語の登録
		for idx, word in enumerate(words):
			# 文字列をバイト列に変換してTRIE作成に渡す
			temp_trie.add(bytes(word, encoding='utf-8'), idx)

		# Trieの配列幅の合計
		# 配列間の隙間を埋めることを考えていないので冗長
		# 要素0は使わない
		temp_array_size = temp_trie.range_size_recursive() + 2

		# ダブル配列領域（仮）：実バイト数が不明なので最大サイズで領域確保
		self.base  = array.array('L', [0] * temp_array_size)
		self.check = array.array('L', [0] * temp_array_size)

		# TRIEを仮領域から正式領域にコピー
		self.write_pos_search_start = 2
		self.write_pos_end = 2
		self.check[1] = 0xffffffff
		self.__copy_from_temp_to_darray(1, temp_trie)

		# Tail領域：dict：record番号 --> 部分文字列
		self.tails = temp_trie.get_tails()

		# ダブル配列涼気を実サイズに縮小する
		base_temp = self.base
		check_temp = self.check
		self.base  = base_temp[:self.write_pos_end]
		self.check = check_temp[:self.write_pos_end]

	def	__copy_from_temp_to_darray(self, da_pos, node):
		'''
		先頭から次の状態への遷移を作成

		Parameters
		----------
		da_pos : int
			ダブル配列上の状態位置
		node : TempDATrieNode
			その状態と等価な一時TRIEノード
		'''
		if node == None:
			return

		# Tailだけの場合
		if node.has_tail():
			# 0x80000000 = 終端
			self.base[da_pos] = (0x80000000 | node.get_tail_record())
			return
		
		# recordだけの場合
		# record+BCの場合
		record = node.get_record()
		temp_list, min_no, max_no = node.tolist()

		# レコードがある場合は、base[0]に格納するので、先頭のNoneをスキップできない
		if record != -1:
			min_no = 0

		# 前後のNoneを除いた長さ
		width = max_no - min_no + 1
		if temp_list == None:
			width = 0
			#width = 0 if record == -1 else 1

		# 先頭のNoneの数
		skip_none = 0 if width == 0 else min_no

		# 書き込み可能先頭位置を補正
		while self.check[self.write_pos_search_start] != 0:
			self.write_pos_search_start += 1

		# 書き込み可能位置を探し出す
		# base[]に書き込まれるインデックスが負にならないように調整する
		write_pos_top = skip_none + 1 if self.write_pos_search_start < skip_none  + 1 else self.write_pos_search_start
		# 先頭位置は書き込めても、後のデータが書き込めないならだめ
		# BASEの値>0となるように、データの状態によって書き込み位置を補正
		while True:
			check_pos = write_pos_top

			# レコードがある場合は、base[0]に書き込めるかどうかをチェックする
			if record != -1 and self.check[check_pos] != 0:
				write_pos_top += 1
				continue
			
			# 文字遷移の格納が可能かどうかをチェックする
			for i in range(width):
				# 書き込みに失敗する場合
				if temp_list[skip_none+i] != None and self.check[check_pos+i] != 0:
					# 先頭位置を一つずらして、再度チェックしなおす
					write_pos_top += 1
					break
			else:
				# forですべてのチェックがOKだったら終了 --> write_pos_topが確定
				break

		if record != -1:
			# レコードが先頭につく
			self.base[write_pos_top] = record | 0x80000000
			self.check[write_pos_top] = da_pos
		
		# 頭のNone列を除いて、Darrayにコピーする
		for i in range(width):
			if temp_list[skip_none+i] != None:
				self.check[write_pos_top+i] = da_pos

		self.base[da_pos] = write_pos_top - skip_none

		# 再起呼び出しでDArrayにコピーする
		for i in range(width):
			if temp_list[skip_none+i] != None:
				self.__copy_from_temp_to_darray(write_pos_top+i, temp_list[skip_none+i])
		
		if self.write_pos_end < write_pos_top+width:
			self.write_pos_end = write_pos_top+width

	def	get_real_size(self):
		return self.write_pos_end
