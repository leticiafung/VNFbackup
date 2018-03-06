#encoding:utf-8
import random
import numpy as np    
import matplotlib.mlab as mlab    
import matplotlib.pyplot as plt 
import time
from graph import Graph

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

						
class Fullbp(object):
	def __init__(self):
		self.node = []
		self.requires = []
		self.nodenum = random.randint(10,20) #node的规模
		for i in range(self.nodenum):
			self.node.append(Node(i))
		self.node.sort(reverse = True)
		self.usedpynode = []
		self.embedlinkrelia = [] #达到可靠性需求后的所有SFC可靠性
		self.embednum = 0
		#self.backupnum = 0
		#self.usedbacknode = []
		self.mygraph = Graph(self.nodenum)
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

	def embedPrim(self,require1):#single require at a time,not backup embed ,require1[0] must be sorted!!!
		self.node.sort(reverse = True)
		#self.usedpynode = [] 只记录一条链使用的物理节点
		primnode = []
		k = 0
		for i in range(len(require1[0])):
			length = len(primnode)
			for j in range(k,self.nodenum):
				if self.node[j].sharetime < 2 and self.node[j].resource >= require1[0][i]:
					self.node[j].update(require1[0][i])
					#self.usedpynode.append(self.node[j])
					primnode.append(self.node[j])
					k = j + 1
					break
			if length != len(primnode) - 1:
				for m in range(len(primnode)):
					primnode[m].restore(require1[0][m])
				return False
			# else:
			# 	length += 1 
		# for i in range(len(require1[0])):
		# 	self.usedpynode[i].update(require1[0][i])
		#先映射点再映射链路
		for m in range(len(primnode) - 1):
			if self.mygraph.shortest_path(primnode[m].number , primnode[m + 1].number,require1[2]) == -1:
				for n in range(len(primnode)):
					primnode[n].restore(require1[0][n])
				self.mygraph.restoreG(require1[2])
				return False
		self.usedpynode.append(primnode)
		for i in range(len(primnode)):
			print "映射的点：",primnode[i].number
		return True
	def embedBackup(self,require1,number):#number 第几条备份链
		#leftnode = [item for item in self.node if item not in self.usedpynode and item not in self.usedbacknode]
		leftnode = [item for item in self.node if item not in self.usedpynode[number]]
		leftnode.sort(reverse = True)
		usedbpnode = [] #一条备份链使用的，一次出现一个
		usedbpvarnode = [] #多次出现，一条备份链
		for i in range(len(require1[0])):
			length = len(usedbpvarnode)
			for j in range(len(leftnode)):	
				if leftnode[j].sharetime < 2 and leftnode[j].resource >= require1[0][i]:
					leftnode[j].update(require1[0][i])
					#self.usedbacknode.append(leftnode[j])
					usedbpvarnode.append(leftnode[j]) #full node
					if leftnode[j] not in self.usedpynode[number]:#对一个链而言所有备份链，原始链间均无共享
						usedbpnode.append(leftnode[j])
						self.usedpynode[number].append(leftnode[j])
					break
			if length != len(usedbpvarnode) - 1:
				for k in range(len(usedbpvarnode)):
					usedbpvarnode[k].restore(require1[0][k])		
				return False
		#for i in range(len(require1[0])):
			# usedbpvarnode[i].update(require1[0][i])
			#print "the real used",usedbpvarnode[i].resource
		#self.usedbacknode.append(leftnode[j]) #记录使用的
		for m in range(len(usedbpvarnode) - 1):
			if self.mygraph.shortest_path(usedbpvarnode[m].number , usedbpvarnode[m + 1].number,require1[2]) == -1:
				for n in range(len(usedbpvarnode)):
					usedbpvarnode[n].restore(require1[0][n])
				self.mygraph.restoreG(require1[2])
				return False
		return usedbpnode
	def calrelias(self,usednode):#计算一条链的可靠性
		singleSFC = 1
		if usednode != False:
			for k in range(len(usednode)):
				singleSFC *= usednode[k].relia
			return singleSFC
		else :
			return -2
	def embedloop(self):
		temprequire = []
		#print "before",len(self.requires)
		for i in range(len(self.requires)):
			if self.embedPrim(self.requires[i]):
				temprequire.append(self.requires[i])
			self.mygraph.reset() ###here
				#self.embednum += len(self.requires[i][0])
		for k in range(mybp.nodenum):
				if mybp.node[k].sharetime > 0:
					self.embednum += 1
		self.requires = temprequire
		#self.requires = filter(self.embedPrim,self.requires)
		#print "after",len(self.requires)
		for i in range(len(self.requires)):
			#self.usedpynode = []
			temprelia = 0
			#if self.embedPrim(self.requires[i]):
			primrelia = self.calrelias(self.usedpynode[i])
			
			if primrelia >= self.requires[i][1]:
					self.embedlinkrelia.append(primrelia)
			else:
				temprelia = 1 - primrelia
				j = 0
				for time in range(10):#备份链最多次数
					self.mygraph.reset() ###here
					if self.embedBackup(self.requires[i],i) != False:

						bnode = self.embedBackup(self.requires[i],i)
						temprelia *= 1-self.calrelias(bnode)
						if 1 - temprelia >= self.requires[i][1]:
							self.embedlinkrelia.append(1 - temprelia)
							break
					else:
						self.embedlinkrelia.append(0) #没有满足要求的链直接置0
						break
					j += 1 
				if j == 10:
					self.embedlinkrelia.append(-2)
					#self.usedbpnode = []
			# else:
			# 	self.embedlinkrelia.append(-1)
	def getembedlinkrelia(self):
		return self.embedlinkrelia

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
				aSFC.sort(reverse = True)
				linkbawidth = random.choice([100,200])
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
		requires = requestcreat(2,[0.95,0.99,0.999])
		# start = time.clock()
		mybp = Fullbp()
		# end = time.clock()
		# end-start
		#多次
		looptime = 1
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
		print "相应的可靠性增长",increasetotal

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
		print "个数",lens
		for i in range(1):
			Y.append(sums[i]/float(lens[i]))
			M.append(usenode[i]/ci[i])
			Z.append(ac[i]/ci[i])
			if M[i] != 0:
				W.append(Y[i]/float(M[i]))
			else:
				W.append(0)
			S[i] = S[i]/ci[i]
			T[i] = T[i]/ci[i]

		# f = open('mybp.txt','a')
		# f.writelines('increase: ' + str(Y) +'\n'+'usedresource: ' + str(M) + '\n')
		# f.writelines('acceptrate:'+ str(Z) + '\n'+ 'bizhi: '+ str(W) + '\n')
		# f.writelines('embedresourece: ' + str(S) + '\n' + 'cputime' + str(T)+'\n')
		# f.close()

		# #plot
		# names=["0.95","0.99","0.999"]  
		# X = range(len(names))

		# fig = plt.figure()
		# plt.subplot(221)  
		# plt.bar(X,Z,0.4,color="green")  
		# plt.xticks(X, names)
		# plt.ylabel("acrate")  
		# plt.title("acceptance of SFCs in FullBP")  

		# plt.subplot(222)
		# plt.bar(X,M,0.4,color="red")  
		# plt.xticks(X, names) 
		# plt.ylabel("userate")  
		# plt.title("use of nodes in FullBP")

		# plt.subplot(223)
		# plt.bar(X,Y,0.4,color="blue")  
		# plt.xticks(X, names)
		# plt.ylabel("increaserate")  
		# plt.title("increaserate  in FullBP")

		# plt.subplot(224) 
		# plt.bar(X,W,0.4,color="black")  
		# plt.xticks(X, names) 
		# plt.ylabel("bizhi")  
		# plt.title("bizhi  in FullBP")

		# fig = plt.figure()
		# plt.bar(X,T,0.4,color="orange")  
		# plt.xticks(X, names) 
		# plt.ylabel("cputime")  
		# plt.title("cputime of FullBP")
		# plt.show()  


		







    					









