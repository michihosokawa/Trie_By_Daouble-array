class	TempDATrieNode:
	"""
	ダブル配列作成のための一時情報
	ノードの分岐情報
	一つの表記には一つのレコード番号
	遷移文字は、bytearrayでintに変換しておく
	"""
	def	__init__(self):
		'''
		recordとnode_dictは同時に存在する
		Tailはいずれとも同時に存在しない
		'''
		self.record = -1		# レコード情報　int
		self.node_dict = {}		# ノード遷移　　文字byte --> ノード分岐
		self.tail = None		# Tail文字列
		self.tail_record = -1	# Tailのレコード

	def	clear(self):
		'''
		初期化
		'''
		self.record = -1		# レコード情報　int
		self.node_dict = {}		# ノード遷移　　文字byte --> ノード分岐
		self.tail = None		# Tail文字列
		self.tail_record = -1	# Tailのレコード

	def	set(self, record_no):
		'''
		登録
		レコード番号を登録する
		'''
		self.record = record_no
		# Tailに登録されているなら、
		# 衝突を避け、それを BCに展開、BCができたら Tailは削除する
		if self.tail_record != -1:
			self.add_node(self.tail, self.tail_record, 0)

	def	add(self, word_bytes, record_no, pos=0):
		'''
		文字列を追加登録

		Parameters
		----------
		word_bytes : bytes
			登録文字列のバイト列
		record_no : int
			レコード番号
		pos : int
			このノードに関連付ける文字位置
		'''
		if self.tail_record == -1:
			if self.record == -1 and len(self.node_dict) == 0:
				# 空のノード（BCも Tailも未設定）なら、 Tailに設定
				if len(word_bytes) == pos:
					# 残り文字列がなければ、レコードに追加
					self.record = record_no
				else:
					# 残り文字列があれば、Tailに追加
					self.tail = word_bytes[pos:]
					self.tail_record = record_no
			else:
				# すでに、レコードかBCが存在するなら、BCに一文字追加して、残りを追加
				self.add_node(word_bytes, record_no, pos)
		else:
			# Tailがあった場合
			temp = word_bytes[pos:]

			if temp == self.tail:
				# Tailが登録しようとする文字列と同じなら、エラー
				raise Exception
			else:
				# Tailが登録しようとする文字列と違うなら、 Tailを BCに展開
				# BCを作成
				self.add_node(self.tail, self.tail_record, 0)
				# BCができたら元あったTailは削除する
				self.tail = None		# Tail文字列
				self.tail_record = -1	# Tailのレコード
				# 登録文字列をBCに展開
				self.add_node(word_bytes, record_no, pos)

	def	add_node(self, word_bytes, record_no, pos=0):
		'''
		文字列を追加
		dictへの登録

		Parameters
		----------
		word_bytes : bytes
			登録文字列のバイト列
		pos : int
			このノードに関連付ける文字位置
		record_no : int
			レコード番号
		'''
		b = word_bytes[pos]
		if b not in self.node_dict:
			# 未登録なら、新しく登録
			self.node_dict[b] = TempDATrieNode()
		# 現在位置の文字につながるノードを取り出す
		node = self.node_dict[b]

		if pos+1 >= len(word_bytes):
			if node.get_record() == -1:
				# 全文字登録したならレコードを設定
				node.set(record_no)
			else:
				# すでにレコードが登録済みならエラー
				raise Exception
		else:
			# 次の文字を登録
			node.add(word_bytes, record_no, pos+1)

	def	search(self, search_bytes, pos=0):
		'''
		指定文字列に該当するレコード情報を保持するノードを取得する
		該当するノードが見つからなければ NULLを返す

		Parameters
		----------
		search_bytes : bytes
			検索文字列のバイト列
		pos : int
			検索位置、省略時は先頭から検索
		'''
		if self.tail_record != -1:
			# Tailがあれば、その文字列と比較する
			if self.tail == search_bytes[pos:]:
				# Tailが検索文字列と同じなら、このノードが目的地
				return self
			else:
				# Tailが検索文字列と違うなら、検索失敗→ Noneを返す
				return None
		else:
			# Tailがなければ、ノード遷移を繰り返す
			b = search_bytes[pos]
			if b not in self.node_dict:
				# 未登録なら、検索失敗
				return None
			node = self.node_dict[b]

			return node if pos+1 >= len(search_bytes) else node.search(search_bytes, pos+1)
	
	def get_record(self):
		'''
		レコード番号を返す
		'''
		return self.record

	def	range_size(self):
		'''
		現ノードからの遷移文字（バイト値）の最小から最大の範囲を返す
		リンク数ではなく、最大と最小の差を計算しているので注意
		'''
		if len(self.node_dict) > 0:
			b_list = self.node_dict.keys()
			return max(b_list) + 2 if self.record != 0 else max(b_list) - min(b_list) + 1
		else:
			return 0 if self.record == -1 else 1

	def	range_size_recursive(self):
		'''
		下層（遷移先）も含めた範囲数の合計を求める
		'''
		size = self.range_size()
		for v in self.node_dict.values():
			size += v.range_size_recursive()
		return size

	def	tolist(self):
		'''
		256文字分の遷移先である TrieNodeポインタのリストを返す
		遷移がない文字位置には、 Noneが入る
		'''
		if len(self.node_dict.items()) == 0:
			return None, 0, 0
		else:
			trie_node_list = [None] * 256
			min_no = 255
			max_no = 0
			for k, v in self.node_dict.items():
				trie_node_list[k] = v
				if min_no > k:
					min_no = k
				if max_no < k:
					max_no = k
			return trie_node_list, min_no, max_no

	def	get_tails(self):
		'''
		Tailを抜き出して、レコード番号->Tailのdictを作成
		BCチェック後にレコード番号からTail部を取得するためのものなので、Tailのみを登録

		Returns
		-------
		tail_dict : dict
			レコード番号とTailバイト列を紐づけたdict
		'''
		tail_dict = {self.tail_record:self.tail} if self.tail_record != -1 else {}
		for v in self.node_dict.values():
			tail_dict.update(v.get_tails())
		return tail_dict

	def	has_tail(self):
		return self.tail_record != -1

	def	get_tail_record(self):
		return self.tail_record

if __name__ == "__main__":
	trie = TempDATrieNode()

	trie.add(bytes('a', encoding='utf-8'),  0)
	trie.add(bytes('ab', encoding='utf-8'),  1)
	trie.add(bytes('aaa', encoding='utf-8'),  2)
	trie.add(bytes('abc', encoding='utf-8'),  3)
	trie.add(bytes('abcd', encoding='utf-8'), 4)
	trie.add(bytes('abz', encoding='utf-8'),  5)

	ret = trie.search(bytes('a', encoding='utf-8'))
	if ret != None:
		print('a {} {}'.format(ret.record, ret.tail_record ))

	ret = trie.search(bytes('ab', encoding='utf-8'))
	if ret != None:
		print('ab {} {}'.format(ret.record, ret.tail_record ))

	ret = trie.search(bytes('aaa', encoding='utf-8'))
	if ret != None:
		print('aaa {} {}'.format(ret.record, ret.tail_record ))

	ret = trie.search(bytes('abc', encoding='utf-8'))
	if ret != None:
		print('abc {} {}'.format(ret.record, ret.tail_record ))

	ret = trie.search(bytes('abcd', encoding='utf-8'))
	if ret != None:
		print('abcd {} {}'.format(ret.record, ret.tail_record ))

	ret = trie.search(bytes('abz', encoding='utf-8'))
	if ret != None:
		print('abz {} {}'.format(ret.record, ret.tail_record ))
