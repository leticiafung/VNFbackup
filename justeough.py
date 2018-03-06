#encoding:utf-8
import random
import numpy as np    
import matplotlib.mlab as mlab    
import matplotlib.pyplot as plt 
import time
from Graphadd import addGraph
from FullBack import Fullbp
import copy

#以可靠性为正好满足，但评估函数考虑资源的消耗,禁忌搜索两个禁忌搜索列表virtual n 选择。
#候选集是每个virtual node 的最佳作为候选集。
class Node(object):
	def __init__(self,tial):
		self.number = tial #编号
		self.relia = random.uniform(0.9, 0.99)
		self.resource = random.randint(50, 60)
		self.sharetime = 0
		self.storedresource = self.resource
	def update(self,useresource):
		self.resource -= useresource
		self.sharetime += 1
	def restore(self,usedresource):
		self.resource += usedresource
		self.sharetime -= 1
	def reset(self):
		self.sharetime = 0
		self.resource = self.storedresource
	def __cmp__(self,other):#rewrite cmp to sort
		return cmp(self.resource , other.resource)
	def __eq__(self,other):#此处注意
		if id(self) == id(other):
			return 1
		else:
			return 0

						
class JENA(Fullbp):
	def __init__(self,fnode,fgraph,numofnode,mt):
		self.node = []
		self.node = copy.deepcopy(fnode)
		self.requires = []
		self.nodenum = numofnode  #node的规模
		# for i in range(self.nodenum):
		# 	self.node.append(Node(i))
		self.node.sort(reverse = True)

		
		
		self.mygraph = copy.deepcopy(fgraph)

		self.embedprimnode = [] #single sfc node not number
		self.usednodenum = []
		
		self.bestsofar = [] #lowest cost  sfc:[[[sfc],cost],[[sfc2],cost]],sfc is node number
		self.tabulistofvirtual = []
		self.tabulistofphy = []
		self.allcandidates = []
		self.allcost = []
#rewirte member in parent class
		self.usedpynode = []
		self.embedlinkrelia = [] #达到可靠性需求后的所有SFC可靠性
		self.embednum = 0
		
		self.maxtime = mt
		#self.mygraph = copy.deepcopy(fgraph)
		self.notfirstembed = []
		self.notfirstrequire = [] 
	def getrequire(self,require):
		#[[[resource],reliability],[],[]] 0为资源，1为可靠性,2为带宽需求
		self.requires = require

	def resetnode(self):
		for i in range(self.nodenum):
			self.node[i].reset()
		self.embedlinkrelia = []
		self.embednum = 0
		self.usedpynode = []
		self.mygraph.bdreset()

		self.notfirstembed = []
		self.notfirstrequire = []

	def embedPrim(self,require1): #greedy embed ,still cannot share physics node in a sfc
		maxnode = Node(-1) #记录最大的
		maxnode.relia = 0
		maxnode.resource = 0
		maxnode.sharetime = 0
		self.usednodenum = []
		self.embedprimnode = []
		#print require1,"require"
		self.node.sort(reverse = True)
		
		tempre = 1 #暂时的可靠性
		for j in range(len(require1[0])):
			for i in range(self.nodenum):#i is already sorted 
				if i not in self.usednodenum:
					if self.node[i].resource >= require1[0][j] and self.node[i].sharetime < 2 and self.node[i].relia > maxnode.relia:
						maxnode = self.node[i]
						#print maxnode,"maxnode"
			if maxnode.number != -1:#find the highest reliability
				self.embedprimnode.append(maxnode)
				self.usednodenum.append(maxnode.number)
				tempre *= maxnode.relia
			else:
				return False
			
					# elif self.node[i].resource >= require1[0][j] and self.node[i].sharetime < 2 and self.node[i].relia > maxnode.relia:
					# 	maxnode = self.node[i]
					# else:
		if tempre >= require1[1]:			# 	pass
			return True
		else:
			self.notfirstrequire.append(require1)
			self.notfirstembed.append(self.embedprimnode) #初始映射
			self.updatesfc(require1)
			return False
			#未对资源进行减少，sharetime 进行减少

	def calcurelia(self,tempsfc,require3):#requrie3 是可靠性需求tempsfc是要选择的
		temprelia = 1
		for i in range(len(tempsfc)):
			temprelia *= tempsfc[i]
		if temprelia >= require3:
			return True
		else:
			return False
	#node的顺序可能会变化，node.number 不变！！！！！！所有的都替换成node！不是node.number
	#禁忌搜索，惩罚准则不详细，未考虑 ,藐视准则只考虑物理节点的禁忌表
	def discard(self,nodelist,require,requestrelia,oldv):#nodelist 是number的链,oldv 是要替换的物理节点
	#discard the node,require is resource need and 相应的可靠性
		otherrelia = 1
		for m in range(len(self.embedprimnode)):
			if m != oldv:
				otherrelia *= self.embedprimnode[m].relia

		discardnode = []
		innernode = []
		for c in range(self.nodenum):
			if len(innernode) == len(nodelist):
				break
			if self.node[c].number in nodelist:
				innernode.append(self.node[c])
		for i in range(len(nodelist)):
			if innernode[i].resource < require or innernode[i].relia*otherrelia < requestrelia or innernode[i] in self.embedprimnode or\
			 innernode[i].sharetime >= 1:
				discardnode.append(innernode[i].number)

		leftnode = [item for item in nodelist if item not in discardnode]	
		
		return leftnode
	
	def aspiration(self,acandicost,tabunode,vnode):#藐视准则,解禁bestsofar 是[[[sfc],cost],[]]
		if tabunode in self.tabulistofphy:
			if self.bestsofar[-1][1] > acandicost :
				biaohao = self.tabulistofphy.index(tabunode) # 有没有可能禁忌表里有多个相同禁忌元素 ：no
				self.tabulistofphy[biaohao] = None
				if vnode in self.tabulistofvirtual:
					self.tabulistofvirtual[self.tabulistofvirtual.index(vnode)] = None
				return 1
			else:
				self.allcost[vnode][self.allcost[vnode].index(acandicost)] = 1000 #设为极大值
				return -1
		else :
			return 0


	def Diversification(self,candidates,requirev):#candidates 是满足要求的候选集，随机生成,满足vnode的需求的
		if 	len(candidates) == 0:
			while len(candidates) < 1:
				randstart = random.randint(0,self.nodenum-1)
				if randstart not in self.usednodenum and self.node[randstart].resource >= requirev and self.node[randstart].sharetime <= 1:
					candidates.append(self.node[randstart].number)
					break
		self.allcandidates.append(candidates) #diversification 添加candidates
		

	def evaluate(self,candidates,oldn,request,requestrelia):
	#oldv 是要被替换的,candidates是所有候选集的number,可靠性需求,对一个vnode来说的
	#在计算期间新的资源需求没有在每个node中减掉，因此不用restore,request是一个SFC链的一个nfv可靠性
		leftload = 0
		mulextrarelia = 1
		candidatenodes = []
		tempnow = []
		
		for z in range(self.nodenum):
			if len(candidatenodes) == len(candidates):
				break
			if self.node[z].number in candidates:
				candidatenodes.append(self.node[z])

		for i in range(len(self.embedprimnode)):
			if oldn != self.embedprimnode[i].number:
				leftload += self.embedprimnode[i].storedresource - self.embedprimnode[i].resource
				if self.embedprimnode[i].relia > requestrelia:
					mulextrarelia *= (self.embedprimnode[i].relia - requestrelia)/100
		for j in range(len(candidatenodes)):
			candicost = leftload + (candidatenodes[j].storedresource - candidatenodes[j].resource) + request\
			  + mulextrarelia*(candidatenodes[j].relia - requestrelia)/100
			tempnow.append(candicost)

		self.allcost.append(tempnow)

		


	#final resource update
	def updatesfc(self,finalrequire):#[[],可靠性，带宽]
		for i in range(len(self.embedprimnode)):
			self.embedprimnode[i].update(finalrequire[0][i])

#loop for all requires
	def tabuloop(self,arequire):	#for every sfc 如果初始映射不行，就转备份，初始可以选最优。
		self.embedprimnode = []
		self.tabulistofphy = []
		self.tabulistofvirtual = []
		self.bestsofar = []

		if self.embedPrim(arequire):
			#print self.embedprimnode,"prim"
			load = 0
			extrarelia = 1
			for i in range(len(self.embedprimnode)):
				load += self.embedprimnode[i].storedresource - self.embedprimnode[i].resource + arequire[0][i]
				if self.embedprimnode[i].relia > arequire[1]:
					extrarelia *= (self.embedprimnode[i].relia - arequire[1])/100
			primcost = load + extrarelia
			self.bestsofar.append([self.usednodenum,primcost])
			clock = 0
			while clock < 7: 
			#连续七次没有最佳就停止
			#???位置对吗
				self.allcost = []
				self.allcandidates = []
				for j in range(len(self.usednodenum)):
					allnode = self.mygraph.findkhop(3,self.usednodenum[j]) #3跳以内
					nowcandidate = self.discard(allnode,arequire[0][j],arequire[1],j)
					self.Diversification(nowcandidate,arequire[0][j])
					self.evaluate(nowcandidate,self.usednodenum[j],arequire[0][j],arequire[1])
					#self.aspiration(move[1],move[0][1])

				mincost = 1000
				mincandidatenum = -1 #candidate 的number
				minvnode = -1
				while True:
					mincost = 1000
					#print self.allcost
					for k in range(len(self.allcost)):
						if min(self.allcost[k]) < mincost:
							mincost = min(self.allcost[k])
							mincandidatenum = self.allcandidates[k][self.allcost[k].index(min(self.allcost[k]))]
							minvnode = k
				#	if minvnode != -1 and mincandidatenum != -1:
					#print "mincost,mincandidatenum,minvnode",mincost,mincandidatenum,minvnode
					value = self.aspiration(mincost,mincandidatenum,minvnode) 
					#else : value = here!!!
					if value >= 0:
						if value == 0:
							clock += 1
							if mincost < self.bestsofar[-1][1]:
								if len(self.bestsofar) == 7:
									del(self.bestsofar[0])
								self.bestsofar.append([self.usednodenum,mincost])
						elif value == 1:
							self.usednodenum[minvnode] = mincandidatenum
							for e in range(self.nodenum):
								if self.node[e].number == mincandidatenum:
									self.embedprimnode[minvnode] = self.node[e]
									break
							if len(self.bestsofar) == 7:
								del(self.bestsofar[0])
							 #track k bestsofar
							self.bestsofar.append([self.usednodenum,mincost])

						if len(self.tabulistofvirtual) == 2:#length
							del(self.tabulistofvirtual[0])
						if len(self.tabulistofphy) == 7:#length
							del(self.tabulistofphy[0])
						self.tabulistofphy.append(mincandidatenum)
						self.tabulistofvirtual.append(minvnode)
						break
					elif value == -1 and mincost == 1000:
						#random start2
						changepos = random.randint(0,len(arequire[0])-1)
						randnum = [key for key in range(self.nodenum) if key not in self.tabulistofphy]
						self.usednodenum[changepos] = random.choice(randnum)
						self.embedprimnode[changepos] = self.node[self.usednodenum[changepos] ]
						clock += 1
						break
					#elif value == -1 and mincost != 1000:

						
			return self.bestsofar
		else:

			return False

	def embedPrimloop(self):#allcandidate 和 allcost 置空！
		acprim = [] #初始映射成功的require 
		for gr in range(len(self.requires)):
			if self.tabuloop(self.requires[gr]) != False:#对bestsofar 找链路映射
				tag = -1
				while tag <= 0 :
					if len(self.bestsofar) == 0:
						self.embedlinkrelia.append(-3)
						break
					for i in range(len(self.bestsofar[-1][0]) - 1):
						if self.mygraph.shortest_path(self.bestsofar[-1][0][i] ,self.bestsofar[-1][0][i + 1],self.requires[gr][2]) == -1:
							self.mygraph.restoreG(self.requires[gr][2])
							self.bestsofar.pop()
							tag = 0
							break
					
					if tag == -1:
						self.updatesfc(self.requires[gr])
						acprim.append(self.requires[gr])
						
						templink = []#初始映射节点
						successrelia = 1
						for z in range(len(self.bestsofar[-1][0])):
							for w in range(len(self.node)):
								if self.node[w].number == self.bestsofar[-1][0][z]:
									successrelia *= self.node[w].relia
									templink.append(self.node[w])
									break
						#self.embedlinkrelia.append(successrelia)
						tag = 1

					self.mygraph.reset()

				if tag == 1:#会出现小于可靠性需求的成功的？为何:有随机生成的！！
					print '成功的',successrelia
					if successrelia >= self.requires[gr][1] :
						self.embedlinkrelia.append(successrelia)
					else:
						self.notfirstembed.append(templink)
						self.notfirstrequire.append(self.requires[gr])

		return acprim
#验证映射算法的影响，论文中更新记录bestsofar what if bestsofar  都没有最短路呢,检查同名函数成员变量
	def embedBackup(self,require1,number):#number 第几条备份链
		#leftnode = [item for item in self.node if item not in self.usedpynode and item not in self.usedbacknode]
		leftnode = [item for item in self.node if item not in self.notfirstembed[number]]
		leftnode.sort(reverse = True)
		usedbpnode = [] #一条备份链使用的，一次出现一个
		usedbpvarnode = [] #多次出现，一条备份链
		for i in range(len(require1[0])):
			length = len(usedbpvarnode)
			for j in range(len(leftnode)):	
				if leftnode[j].sharetime < self.maxtime and leftnode[j].resource >= require1[0][i]:
					leftnode[j].update(require1[0][i])
					#self.usedbacknode.append(leftnode[j])
					usedbpvarnode.append(leftnode[j]) #full node
					if leftnode[j] not in self.notfirstembed[number]:#对一个链而言所有备份链，原始链间均无共享
						usedbpnode.append(leftnode[j])
						self.notfirstembed[number].append(leftnode[j])
					break
			if length != len(usedbpvarnode) - 1:
				for k in range(len(usedbpvarnode)):
					usedbpvarnode[k].restore(require1[0][k])		
				return False
		#for i in range(len(require1[0])):
			# usedbpvarnode[i].update(require1[0][i])
			#print "the real used",usedbpvarnode[i].resource
		#self.usedbacknode.append(leftnode[j]) #记录使用的
		self.mygraph.reset()
		for m in range(len(usedbpvarnode) - 1):
			if self.mygraph.shortest_path(usedbpvarnode[m].number , usedbpvarnode[m + 1].number,require1[2]) == -1:
				for n in range(len(usedbpvarnode)):
					usedbpvarnode[n].restore(require1[0][n])
				self.mygraph.restoreG(require1[2])
				return False
		return usedbpnode
	def embedloop(self):#改写fullbp的loop,其他与fullBP相同
		temprequire = []
		self.embedPrimloop()
		#print "before",len(self.requires)
		# for i in range(len(self.requires)):
		# 	if self.embedPrim(self.requires[i]):
		# 		temprequire.append(self.requires[i])
		# 	self.mygraph.reset() ###here
		# 		#self.embednum += len(self.requires[i][0])
		# #embed prim nodes
		for k in range(self.nodenum):
			if self.node[k].sharetime > 0:
				self.embednum += 1
		#self.requires = self.embedPrimloop()
		#self.requires = temprequire
		#self.requires = filter(self.embedPrim,self.requires)
		print "不成功的",len(self.notfirstrequire)
		for i in range(len(self.notfirstrequire)):
			#self.usedpynode = []
			temprelia = 0
			#if self.embedPrim(self.requires[i]):
			primrelia = self.calrelias(self.notfirstembed[i])
			
			# if primrelia >= self.requires[i][1]:
			# 		self.embedlinkrelia.append(primrelia)
			temprelia = 1 - primrelia
			j = 0
			for time in range(10):#备份链最多次数
				self.mygraph.reset() ###here
				bnode = self.embedBackup(self.notfirstrequire[i],i)
				if bnode != False:
					temprelia *= 1-self.calrelias(bnode)
					if 1 - temprelia >= self.notfirstrequire[i][1]:
						self.embedlinkrelia.append(1 - temprelia)
						break
				else:
					self.embedlinkrelia.append(0) #没有满足要求的链直接置0
					break
				j += 1 
			if j == 10:
				self.embedlinkrelia.append(-2)

if __name__ == '__main__':
	def requestcreat(numsfc,relia):
	#creat random sorted request
		totalrequest = [] 
		request1 = []
		request2 = []
		request3 = []
		for i in range(numsfc):
			vnfnum = random.randint(2,6)
			tempsfc1 = []
			tempsfc2 = []
			tempsfc3 = []
			aSFC = []
			for j in range(vnfnum):
				tempresource = random.randint(1,30)
				aSFC.append(tempresource)
			#aSFC.sort(reverse = True)
			linkbawidth = random.choice([10,40,100,200])
			tempsfc1.append(aSFC),tempsfc1.append(relia[0]),tempsfc1.append(linkbawidth)
			tempsfc2.append(aSFC),tempsfc2.append(relia[1]),tempsfc2.append(linkbawidth)
			tempsfc3.append(aSFC),tempsfc3.append(relia[2]),tempsfc3.append(linkbawidth)
			request1.append(tempsfc1)
			request2.append(tempsfc2)
			request3.append(tempsfc3)
		totalrequest.append(request1)
		totalrequest.append(request2)
		totalrequest.append(request3)
		return totalrequest
	def calac(relialist,increaserate,req):
		count = 0
		for item in relialist:
			if item > 0:
				count += 1
				increaserate.append(item - req)
		#print increaserate
	
		return count/float(len(relialist))
		
	

	# increasetotal = [] #一个元素保存一个可靠性的值
	# acratio = []  #保存按0.95,0.99,0.999保存接受率
	# usedresource = [] #节点使用，按0.95,0.99,0.999
	# usedembednum = []#节点使用，按0.95,0.99,0.999
	# requires = []
	# cputime = []
	# rate = [0.95,0.99,0.999]
	# # requires.append(requestcreat(1100,0.95))
	# # requires.append(requestcreat(1100,0.99))
	# # requires.append(requestcreat(1100,0.999))
	# requires = requestcreat(50,[0.95,0.99,0.999])
	# # start = time.clock()
	# mybp = JENA()#要带参数
	# print "success!"
	# end = time.clock()
	# end-start
	#多次
	# looptime = 3
	# for i in range(looptime):
	# 	increaseratio = []
	# 	print "第 %d 次",i
	# 	mybp.getrequire(requires[i%3])

		#print requires[i%3]

		# start = time.clock()
		# accept = mybp.embedPrimloop()
		# end = time.clock()
		# print "接受的：",accept
		# print "运行时间：",end - start
		# cputime.append(end-start)
		# mybp.resetnode()
		# random.shuffle(requires[i%3])
	nodes = random.randint(500,600) #节点数
	node = []
	for i in range(nodes):
		node.append(Node(i))
	mygraph = addGraph(nodes)

	increasetotal = [] #一个元素保存一个可靠性的值
	acratio = []  #保存按0.95,0.99,0.999保存接受率
	usedresource = [] #节点使用，按0.95,0.99,0.999
	usedembednum = []#节点使用，按0.95,0.99,0.999
	requires = []
	cputime = []
	rate = [0.95,0.99,0.999]
	# requires.append(requestcreat(1100,0.95))
	# requires.append(requestcreat(1100,0.99))
	# requires.append(requestcreat(1100,0.999))
	requires = requestcreat(100,[0.95,0.99,0.999])
	# start = time.clock()
	#mybp = Fullbp()
	mybp =JENA(node,mygraph,nodes,2)
	print "success!"
	# end = time.clock()
	# end-start
	#多次
	looptime = 3
	for i in range(looptime):
		increaseratio = []
		mybp.getrequire(requires[i%3])
		start = time.clock()
		mybp.embedloop()
		end = time.clock()
		print "运行时间：",end - start
		cputime.append(end-start)
		print "可靠性list:",mybp.getembedlinkrelia()
		if len(mybp.getembedlinkrelia()) != 0:
			acratio.append(calac(mybp.getembedlinkrelia(),increaseratio,rate[i%3]))
			if len(increaseratio) == 0:
				increaseratio.append(0)
		else:
			acratio.append(0)
			increaseratio.append(0)
		increasetotal.append(increaseratio)
		usednum = 0
		for k in range(mybp.nodenum):
			if mybp.node[k].sharetime > 0:
				usednum += 1
		usedresource.append(usednum)
		usedembednum.append(mybp.embednum)
		mybp.resetnode()
		random.shuffle(requires[i%3])
	#print "相应的可靠性增长",increasetotal

	M = [] # aver usedresource
	S = [0,0,0] #aver embedsource
	Y = [] #aver increase rate
	W = [] #aver bizhi
	Z = [] #aver accept rate
	T = [0,0,0] #aver cputime
	usenode = [0,0,0] 
	sums = [0,0,0]
	lens = [0,0,0]
	ci = [0,0,0]
	ac = [0,0,0]
	ss = [0,0,0]
	for j in range(looptime):
		if j % 3 == 0:
			sums[0] += sum(increasetotal[j])
			lens[0] += len(increasetotal[j])
			usenode[0] += usedresource[j]
			ac[0] += acratio[j]
			ci[0] += 1
			S[0] += usedembednum[j]
			T[0] += cputime[j]
		elif j % 3 == 1:
			sums[1] += sum(increasetotal[j])
			lens[1] += len(increasetotal[j])
			usenode[1] += usedresource[j]
			ac[1] += acratio[j]
			ci[1] += 1
			S[1] += usedembednum[j]
			T[1] += cputime[j]
		else:
			sums[2] += sum(increasetotal[j])
			lens[2] += len(increasetotal[j])
			usenode[2] += usedresource[j]
			ac[2] += acratio[j]
			ci[2] += 1
			S[2] += usedembednum[j]
			T[2] += cputime[j]
		 	#z = sum(increasetotal[j])/len(increasetotal[j])
	#print "个数",lens
	for i in range(3):
		Y.append(sums[i]/float(lens[i]))
		M.append(usenode[i]/ci[i])
		Z.append(ac[i]/ci[i])
		if M[i] != 0:
			W.append(Y[i]/float(M[i]))
		else:
			W.append(0)
		S[i] = S[i]/ci[i]
		T[i] = T[i]/ci[i]

	f = open('JENA.txt','a')
	f.writelines('\n'+ 'increase: ' + str(Y) +'\n'+'usedresource: ' + str(M) + '\n')
	f.writelines('acceptrate:'+ str(Z) + '\n'+ 'bizhi: '+ str(W) + '\n')
	f.writelines('embedresourece: ' + str(S) + '\n' + 'cputime' + str(T)+'\n')
	f.close()


						





			  
			   		



