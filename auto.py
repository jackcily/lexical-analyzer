# -*-coding:utf-8 -*-
from os import popen
import time

class Automata:   #基本自动机类

	def __init__(self,lang =set(['0','1'])):  # 五元组  状态集  开始状态  结束状态集  转化集  语言表（默认0 1）
		self.status =set()
		self.startstatu =None
		self.finalstatus=[]
		self.transform = dict()    #转换关系
		self.lang  = lang
	def removes(self,setuseless):
		for i in setuseless:
			self.status.remove(i)
		for i in self.transform.keys():
			if self.transform[i] or i in setuseless:
				self.transform.popitem()

	@staticmethod
	def epsilon():
		return ":e:"                              #设置 空

	def setstartstatu(self,statu):                #设置开始状态
		self.startstatu = statu
		self.status.add(statu)

	def addfinalstatus(self,statu):              #加入结束状态
		if isinstance(statu,int):
			statu =[statu]
		for s in statu:
			if s not in self.finalstatus:
				self.finalstatus.append(s)

	def addtrans(self,fromst,tost,inp):   #添加从fromst经 inp 转移到tost的一个转移关系    即添加边
		if isinstance(inp,str):
			inp = set([inp])
		self.status.add(fromst)
		self.status.add(tost)
		if fromst in self.transform:
			if tost in self.transform[fromst]:
				self.transform[fromst][tost] = self.transform[fromst][tost].union(inp)
			else:
				self.transform[fromst][tost] = inp
		else:
			self.transform[fromst] = {tost:inp}


	def addtrans_dict(self,transform):  #用于将别的自动机的转化集添加到自己的转化集中去
		for fromst, tosts in transform.items():
			for statu in tosts:
				self.addtrans(fromst,statu,tosts[statu])


	def gettransform(self,statu,key):   #  从 status 经过 key 转移能到达的所有状态的集合
		if isinstance(statu,int):
			statu =[statu]

		trstatus = set()
		for st in statu:
			if st in self.transform:
				for tns in self.transform[st]:
					if key in self.transform[st][tns]:
						trstatus.add(tns)

		return trstatus


	def getEClose(self,findst):  #获取一个状态经由 空 所能到达的所有状态
		status_all = set()
		status = set( [findst])
		while len(status)!=0:
			st = status.pop()
			status_all.add(st)
			if st in self.transform:
				for tns in self.transform[st]:
					if tns not in status_all and Automata.epsilon() in self.transform[st][tns]: #判断  如果有权值为空的边，就把该值加入队列
						status.add(tns)
		return status_all



	def display(self):
		print(" 状态集 ",self.status)
		print(" 开始状态 ",self.startstatu)
		print(" 结束状态 ",self.finalstatus)
		print(" 转换关系 ")
		for fromst ,tosts in self.transform.items():
			for statu in  tosts:
				for char in tosts[statu]:
					print(" ",fromst," -> ",statu,"on '"+char+"'")

			print()

																								#todo 此处少打印了一个函数

	def newBuildNum(self,startnum):   #以 startnum 为起点 对本自动机中的状态进行重新编号
		translations ={}             #返回新编号的自动机和最新的startnum
		for i in list(self.status):
			translations[i] = startnum
			startnum+=1
		newbuild = Automata(self.lang)
		newbuild.setstartstatu(translations[self.startstatu])
		newbuild.addfinalstatus(translations[self.finalstatus[0]])

		for fromst, tosts in self.transform.items():
			for statu in tosts:
				newbuild.addtrans(translations[fromst],translations[statu],tosts[statu])

		return [newbuild,startnum]



	def  newBuildFromEquivalentstatus(self,equivalent,pos): #根据最简化的合并结果新建一个最简自动机
		newbuild = Automata(self.lang)
		for fromst,tosts in self.transform.items():        #根据新合并的关系建边
			for statu in tosts:
				newbuild.addtrans(pos[fromst],pos[statu],tosts[statu])

		newbuild.setstartstatu(pos[self.startstatu])
		for i in self.finalstatus:
			newbuild.addfinalstatus(pos[i])
		return newbuild

	def getnewAutominimize(self,dicts,dfa):
		newbuild = Automata()
		newbuild.startstatu = dicts[dfa.startstatu]   #进行状态的替换
		for i in dfa.finalstatus:
			newbuild.finalstatus.append(dicts[i])     #进行状态的替换

		newbuild.lang = dfa.lang

		sets=[]
		for i in dfa.transform:
			for j in dfa.transform[i]:
				char = list(dfa.transform[i][j])
				tmp = [  dicts[i],   dicts[j] ,char[0]  ]
				sets.append(tmp)
		sets.sort()

		previous = -1
		for i in sets:
			if previous ==-1 :
				previous =i
			elif  previous[0] == i[0] and previous[1] == i[1] and previous[2] == i[2]:
				continue

			if i[0] not in newbuild.status:
				newbuild.status.add(i[0])
			if i[1] not in newbuild.status:
				newbuild.status.add(i[1])
			newbuild.addtrans(i[0],i[1],i[2])
			previous =i


		return newbuild



	def getDotFile(self):                                                                          # 用于建图   根据边自动生成dot 文件
		dotFile = "digraph DFA {\nrankdir=LR\n"
		if len(self.status) != 0:
			dotFile += "root=s1\nstart [shape=point]\nstart->s%d\n" % self.startstatu
			for statu in self.status:
				if statu in self.finalstatus:
					dotFile += "s%d [shape=doublecircle]\n" % statu
				else:
					dotFile += "s%d [shape=circle]\n" % statu
			for fromstatu, tostatus in self.transform.items():
				for statu in tostatus:
					for char in tostatus[statu]:
						dotFile += 's%d->s%d [label="%s"]\n' % (fromstatu, statu, char)
		dotFile += "}"
		return dotFile



class BuildAutomata:     #定义自动机的结构  以及自动机的运算

	@staticmethod
	def basicstruct(inp):
		statu1 = 1
		statu2 = 2
		basic = Automata()  #basic 存储基本NFA 结构
		basic.setstartstatu(statu1)
		basic.addfinalstatus(statu2)
		basic.addtrans(1,2,inp)
		return basic

	@staticmethod
	def plusstruct(a,b):  #进行或运算
		[a,m1] = a.newBuildNum(2)   #进行运算之前首先对自动机的状态进行重新编号
		[b,m2] = b.newBuildNum(m1)
		statu1 = 1
		statu2 = m2
		plus = Automata()
		plus.setstartstatu(statu1)
		plus.addfinalstatus(statu2)
		plus.addtrans(plus.startstatu,a.startstatu,Automata.epsilon())
		plus.addtrans(plus.startstatu,b.startstatu,Automata.epsilon())
		plus.addtrans(a.finalstatus[0],plus.finalstatus[0],Automata.epsilon())
		plus.addtrans(b.finalstatus[0],plus.finalstatus[0],Automata.epsilon())
		plus.addtrans_dict(a.transform)
		plus.addtrans_dict(b.transform)
		return plus




	@staticmethod
	def dotstruct(a,b):  #进行与运算
		[a, m1] = a.newBuildNum(1)  # 进行运算之前首先对自动机的状态进行重新编号
		[b, m2] = b.newBuildNum(m1)
		statu1 = 1
		statu2 = m2-1
		ands = Automata()
		ands.setstartstatu(statu1)
		ands.addfinalstatus(statu2)
		ands.addtrans(a.finalstatus[0],b.startstatu,Automata.epsilon())
		ands.addtrans_dict(a.transform)
		ands.addtrans_dict(b.transform)
		return ands

	@staticmethod
	def starstruct(a):  #进行闭包运算
		[a,m1] = a.newBuildNum(2)
		statu1 = 1
		statu2 = m1
		star = Automata()
		star.setstartstatu(statu1)
		star.addfinalstatus(statu2)
		star.addtrans(star.startstatu,a.startstatu,Automata.epsilon())
		star.addtrans(star.startstatu,star.finalstatus[0],Automata.epsilon())
		star.addtrans(a.finalstatus[0],star.finalstatus[0],Automata.epsilon())
		star.addtrans(a.finalstatus[0],a.startstatu,Automata.epsilon())
		star.addtrans_dict(a.transform)  # 加入字典
		return star




class RegextoNFA:        #正规式转化成NFA

	def __init__(self, regex):
		self.star = '*'
		self.plus = '|'
		self.dot = '.'
		self.openingBracket = '('
		self.closingBracket = ')'
		self.operator = [self.plus, self.dot]
		self.regex = regex

		# 规定合法字符集范围是 A-Z a-z 0-9
		self.alphabet = [chr(i) for i in range(65, 91)]
		self.alphabet.extend([chr(i) for i in range(97, 123)])
		self.alphabet.extend([chr(i) for i in range(48, 58)])
		self.buildNFA()


	def processOperator(self,operator):  #根据运算符进行相应运算
		if len(self.automata) == 0:
			raise BaseException ("calc error  empty stack")
		if operator == self.star:        #闭包运算
			a = self.automata.pop()
			self.automata.append(BuildAutomata.starstruct(a))
		elif operator in self.operator:  #双目运算
			if len(self.automata) < 2:
				raise BaseException("双目运算错误")
			a = self.automata.pop()
			b = self.automata.pop()
			if operator == self.plus:    #或
				self.automata.append(BuildAutomata.plusstruct(b,a))
			else:                        #与
				self.automata.append(BuildAutomata.dotstruct(b,a))



	def addOperatorToStack(self,char):   #向  stack中压入符号
		while(1):
			if len(self.stack)==0:   #空栈
				break
			top = self.stack[len(self.stack) - 1]
			if top == self.openingBracket:  #左括号跳出循环
				break
			if top == char or top == self.dot: #连接符或当前运算符优先级相同 直接运算
				op = self.stack.pop()
				self.processOperator(op)
			else:
				break
		self.stack.append(char)

	def buildNFA(self):
		lang = set()
		self.stack = []     #运算符栈
		self.automata = []  #NFA边栈
		previous = "::e::"  # 初始化
		for char in self.regex:

			# 状态1  遇见字符  建边
			if char in self.alphabet:
				lang.add(char)  # 把字符加入语言表
				# 如果前面没有执行过连接运算
				if previous != self.dot and (previous in self.alphabet or previous in [self.closingBracket, self.star]):
					self.addOperatorToStack(self.dot)  # 压点的时候 如果已经有一个连接操作符，就先计算该连接操作符再压入
				self.automata.append(BuildAutomata.basicstruct(char))  # 构造一个字符的边

			# 状态2  遇见左括号 压栈
			elif char == self.openingBracket:
				if previous != self.dot and (previous in self.alphabet or previous in [self.closingBracket, self.star]):
					self.addOperatorToStack(self.dot)
				self.stack.append(char)

			# 状态3  遇到右括号 出栈 做运算
			elif char == self.closingBracket:
				if previous in self.operator:
					raise BaseException("errot when push )")
				while (1):
					if len(self.stack) == 0:
						raise BaseException(" error when push ) empty stack")

					op = self.stack.pop()
					if op == self.openingBracket:
						break
					elif op in self.operator:
						self.processOperator(op)
					# todo 想做的修改
			# 状态4 遇到运算符 *   直接进行闭包运算
			elif char in self.star:
				self.processOperator(char)
			# 状态5 遇到运算符
			elif char in self.operator:
				self.addOperatorToStack(char)  # 把运算符进行压栈
			else:
				raise BaseException(" symbol not allowed")

			previous = char

		while len(self.stack)!=0:   #如果还有未进行运算的符号
			op = self.stack.pop()
			self.processOperator(op)

		if len(self.automata) > 1:
			raise  BaseException("Regex to NFA  faild")

		self.nfa = self.automata.pop()
		self.nfa.lang = lang


	def getNFA(self):
		return self.nfa

	def displayNFA(self):  #直接调用基类函数
		self.nfa.display()








class NFAtoDFA: #NFA 生成 DFA

	def __init__(self,nfa):
		self.buildDFA(nfa)

	def buildDFA(self,nfa):  #构建dfa
		allstat = dict()     #记录中间过程出现的所有状态  编号
		eclose = dict()      #记录以某个状态为起点   经过 空 能到达的所有状态
		counts = 1
		statu1 = nfa.getEClose(nfa.startstatu)
		eclose[nfa.startstatu] = statu1
		dfa = Automata(nfa.lang)
		dfa.setstartstatu(counts)
		status = [[statu1,counts]]
		counts+=1

		while len(status) !=0:       #当还有新状态的时候  继续遍历
			[statu,fromindex] = status.pop()

			for char in dfa.lang:   #从新状态开始  经过每一个char
				trstatus = nfa.gettransform(statu,char)   #合并当前状态 与它能到达的空状态
				for s in list(trstatus)[:]:
					if s not in eclose:
						eclose[s] = nfa.getEClose(s)
					trstatus = trstatus.union(eclose[s])

				if len(trstatus) !=0:                    #如果该状态在之前从未出现过  编号存储
					if trstatus not in allstat.values():
						status.append([trstatus,counts])
						allstat[counts] = trstatus
						toindex = counts
						counts+=1
					else:                                # 否则找到之前编的号  赋值给  toindex
						toindex = [k for k,v in allstat.items() if v == trstatus][0]

					dfa.addtrans(fromindex,toindex,char) #加入转化关系

		for value,statu in allstat.items():     #最后判断每一个状态是否包含终点终点状态  如果是  加入终点状态集
			if nfa.finalstatus[0] in statu:
				dfa.addfinalstatus(value)
		self.dfa = dfa


	def getDFA(self):
		return self.dfa

	def dispalyDFA(self):
		self.dfa.display()






class DFAtoMFA:   #进行dfa的最小化

	def __init__(self,dfa):
		self.dfa = dfa
	#	self.get_unreachable_states()
		self.buildMFA()

	def buildMFA(self):
		if len(self.dfa.status)<=1:      #如果只有一个元素 无需再化简 直接返回
			self.mfa = self.dfa
			return

		status=self.dfa.status
		pos = dict(zip(status, range(len(status))))#pos 中存储每一个状态对应处于的集合编号  一直处于不断地变化中

		set1 = set(self.dfa.finalstatus)
		set2 = set(self.dfa.status) - set1
		set1 = list(set1)
		set2 = list(set2)
		for i in set1:       #初始化pos
			pos[i]=1
		for i in set2:
			pos[i] = 0

		allset = [set1,set2]
		counts =2           # 0 1 均被使用，集合编号从2 开始
		flag= True
		while flag:
			flag=False
			for char in self.dfa.lang:
				for sub_set in allset:

					dic = dict()   # 存储状态和新对应的编号
					lists =[]
					for i in sub_set:
						num =self.dfa.gettransform(i,char)
						if len(num) ==0:
							continue
						num = list(num)
						num = num[0]
						num = pos[num] #获取转移状态对应的集合编号

						if num not in  dic.keys():   #如果没有建立 该状态对应的集合编号  的字典关系  新建
							dic[num] =counts
							counts+=1
						lists.append(dic[num])


					if len(dic) >1: #证明该集合中状态转移 不是转移到同一处 拆分元素 跳出循环
						flag = True
						tmp_set=dict()   #新编号与新数值相对应  加入不同的新list
						for i1 in range(len(sub_set)):
							if lists[i1] not  in tmp_set.keys():
								tmp_set[lists[i1]]=list()
							tmp_set[ lists[i1] ].append(sub_set[i1])
							pos[sub_set[i1]] = lists[i1] #更新pos  更新状态 所在的集合的编号

						allset.remove(sub_set) #将旧的list移除
						for i1 in tmp_set.values(): #将新的list 加入
							allset.append(i1)
						break

				if flag == True:
					break
		print(allset)


		for i in range(len(allset)):    #计算出每个数值对应的新的数值
			for j in allset[i]:
				pos[j] =i+1

		self.mfa = self.dfa.getnewAutominimize(pos,self.dfa)













	# def buildMFA(self,dfa):
	# 	self.dfa = dfa
	#
	# 	status = list(self.dfa.status)
	# 	n = len(status)
	# 	uncheck =dict()
	# 	counts =1
	# 	disting = []
	#
	# 	equ = dict(zip(range(len(status)),[{s} for s in status]))
	# 	pos = dict(zip(status,range(len(status)) ) )
	#
	# 	for i in range(n-1):   #进行所有状态的枚举
	# 		for j in range(i+1,n):
	# 			if not ([status[i],status[j]] in disting or [status[j],status[i]] in disting):    #如果这一对还没有进行过判别
	# 				eq=1
	# 				toappend=[]
	# 				for char in self.dfa.lang: #遍历每一个字符的所能达到的转移，如果完全相同 判定相同  如果长度不同  判定不同  如果长度相同 但转移不同 加入待判断集合
	# 					s1 = self.dfa.gettransform(status[i],char)
	# 					s2 = self.dfa.gettransform(status[j],char)
	# 					if len(s1)!=len(s2):
	# 						eq =0
	# 						break
	# 					if len(s1) > 1: #应该只有一个后继状态
	# 						raise BaseException("DFA  to  MFA   error1")
	# 					elif len(s1)==0:
	# 						continue
	# 					s1 = s1.pop()
	# 					s2 = s2.pop()
	# 					if s1!=s2:
	# 						if [s1,s2] in disting or [s2,s1] in disting:
	# 							eq =0
	# 							break
	# 						else:
	# 							toappend.append([s1,s2,char])
	# 							eq=-1
	# 				if eq==0:   #如果已经确定不相等就放在不等的集合中
	# 					disting.append([status[i],status[j]])
	# 				elif eq==-1:#如果还不确定就先放在未合并的里面
	# 					s = [status[i],status[j]]
	# 					s.extend(toappend)
	# 					uncheck[counts] = s
	# 					counts+=1
	# 				else:   #如果二者相等就进行合并
	# 					p1 = pos[status[i]]
	# 					p2 = pos[status[j]]
	# 					if p1!=p2:
	# 						st = equ.pop(p2)
	# 						for s in st:
	# 							pos[s] = p1
	# 						equ[p1] = equ[p1].union(st)
	#
	#
	#
	# 	newF =True    #flag
	# 	while newF and len(uncheck) > 0:
	# 		newF = False
	#
	# 		for po ,pair in uncheck.items(): #将未划分的取出来进行判断  只要有新发现对  就标记为true  进行循环判定
	# 			for tr in pair[2:]:
	# 				if [tr[0],tr[1]] in disting or [tr[1],tr[0]] in disting:
	# 					uncheck.pop(po)
	# 					disting.append([pair[0],pair[1]])
	# 					newF = True
	# 					break
	#
	# 	for pair in uncheck.values():  #对剩下还没能区分的 开始进行合并
	# 		p1 = pos[pair[0]]
	# 		p2 = pos[pair[1]]
	# 		if p1!=p2:
	# 			st = equ.pop(p2)
	# 			for s in  st:
	# 				pos[s] = p1
	# 			equ[p1] = equ[p1].union(st)
	# 	if len(equ) == len(status):     #如果没有进行状态的合并
	# 		self.minDFA = self.dfa
	# 	else:
	# 		self.minDFA = self.dfa.newBuildFromEquivalentstatus(equ,pos)  #根据合并后的编号关系  新建一个自动机

	def getMFA(self):
		return self.mfa

	def dispalyMFA(self):
		return self.mfa.display()





def drawGraph(automata, file=""):       #绘图
	"""From https://github.com/max99x/automata-editor/blob/master/util.py"""
	f = popen(r"dot -Tpng -o graph%s.png" % file, 'w')
	try:
		f.write(automata.getDotFile())
	except:
		raise BaseException("Error creating graph")
	finally:
		f.close()


# def isInstalled(program):
# 	"""From http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python"""
# 	import os
# 	def is_exe(fpath):
# 		return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
#
# 	fpath, fname = os.path.split(program)
# 	if fpath:
# 		if is_exe(program) or is_exe(program + ".exe"):
# 			return True
# 	else:
# 		for path in os.environ["PATH"].split(os.pathsep):
# 			exe_file = os.path.join(path, program)
# 			if is_exe(exe_file) or is_exe(exe_file + ".exe"):
# 				return True
# 	return False













