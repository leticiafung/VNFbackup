#encoding:utf-8
import random
import numpy as np    
import matplotlib.mlab as mlab    
import matplotlib.pyplot as plt 
import time
import copy
#相邻节点的链路，？？备份后是否计算,逻辑链路计算出错！！！
from graph import Graph

class Node(object):
	def __init__(self,tial):
		self.number = tial #编号
		self.relia = random.uniform(0.9, 0.99)
		self.resource = random.randint(50, 60)
		self.sharetime = 0
		self.storedresource = self.resource

		self.backupnode = []
		self.temprelia = self.relia#在某条链的可靠性
		self.subrelia = 0 #该节点所属子网的可靠性
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

#同一条链的初始映射节点不可共享，不同备份间也不可共享，不同链间无要求，物理节点共享次数是2
						
class GREP(object):
	def __init__(self,fnode,fgraph,numofnode,mt):
		self.node = []
		self.requires = []
		#self.nodenum = random.randint(500,600) #node的规模
		# for i in range(self.nodenum):
		# 	self.node.append(Node(i))
		self.node = copy.deepcopy(fnode)
		self.node.sort(reverse = True)
		self.usedpynode = []
		self.embedlinkrelia = [] #达到可靠性需求后的所有SFC可靠性
		self.embednum = 0
		#self.usedbacknode = []
		#self.mygraph = Graph(self.nodenum)
		self.nodenum = numofnode #node的规模
		self.mygraph = copy.deepcopy(fgraph)
		self.maxtime = mt
		
		self.subnets = [] #一个服务链的子网[[],[],]
		
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

	def embedPrim(self,require1):
	#single require at a time,not backup embed ,require1[0] must be sorted!!!,
	#mistake:require1 should not be sorted for the order can not be changed

		self.node.sort(reverse = True)
		#self.usedpynode = [] 只记录一条链使用的物理节点
		primnode = []
		k = 0
		for i in range(len(require1[0])):
			length = len(primnode)
			for j in range(k,self.nodenum):
				if self.node[j].sharetime < self.maxtime and self.node[j].resource >= require1[0][i]:
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
		self.mygraph.reset()
		for m in range(len(primnode) - 1):
			if self.mygraph.shortest_path(primnode[m].number , primnode[m + 1].number,require1[2]) == -1:
				for n in range(len(primnode)):
					primnode[n].restore(require1[0][n])
				self.mygraph.restoreG(require1[2])
				return False
		self.usedpynode.append(primnode)
		return True

	def embedbackup(self,embedprimnode,tempprimnode,require,snumber):
	#receive a single embeded sfc,namely the prim physics,require 是该条链,embedprimnode 是初始映射后的链
		if embedprimnode[0].temprelia > embedprimnode[1].temprelia:
			minnode = embedprimnode[1]
			secondnode = embedprimnode[0]
			minnum = 1 #相应的require中顺序
			secnum = 0
		else:
			minnode = embedprimnode[0]
			secondnode = embedprimnode[1]
			minnum = 0
			secnum = 1

		for i in range(2,len(embedprimnode)):#require 与 embedprim 顺序一致
			if embedprimnode[i].temprelia < minnode.temprelia:
				secondnode = minnode
				minnode = embedprimnode[i]
				secnum = minnum
				minnum = i 
			elif embedprimnode[i].temprelia < secondnode.temprelia:
				secondnode = embedprimnode[i]
				secnum = i
			else:
				pass

		#print 'new usednode',len(self.usedpynode[snumber])
		#两个选中节点是否相邻，分为2种情况
		minleft = minnum -1
		minright = minnum + 1
		secleft = secnum -1
		secright = secnum + 1
		if minnum == 0:
			minleft = -1# -1 表示没有左边点
		elif minnum == len(embedprimnode) - 1:
			minright = -1	
		if secnum == 0:
			secleft = -1# -1 表示没有左边点
		elif secnum == len(embedprimnode) - 1:
			secright = -1
		if minnum - secnum == 1 or  minnum - secnum == -1:#相邻
			if minnum > secnum:
				minleft = -1
				secright = -1
			else:
				minright = -1
				secleft = -1
		fournode = [minleft,minright,secleft,secright]#在sfc链的序号
		fournode = [nor for nor in fournode if nor != -1 ]


		leftnode = [item for item in self.node if item not in self.usedpynode[snumber]]
		leftnode.sort(reverse = True)
		flag = 0
		inflag = 0
		for j in range(len(leftnode)):
			self.mygraph.reset()
			if leftnode[j].sharetime < self.maxtime and leftnode[j].resource >= require[0][minnum] + require[0][secnum]:
				
				choosednode = leftnode[j] #选中的备份节点
				for i in range(len(fournode)):
					singlepath = self.mygraph.shortest_path(embedprimnode[fournode[i]].number,choosednode.number,require[2])
					if singlepath != 0:
						self.mygraph.restoreG(requirebd)
						self.mygraph.reset()
						inflag = 1
						break

				#firstpath = self.mygraph.shortest_path(minnode.number , choosednode.number,require[2])
				# if firstpath == 0:
				# 	secondpath = self.mygraph.shortest_path(secondnode.number , choosednode.number,require[2])
				# 	if secondpath == 0:
				# 		leftnode[j].update(require[0][minnum] + require[0][secnum])
						#minnode.backupnode.append(leftnode[j])
						# secondnode.backupnode.append(leftnode[j]) 此处先不添加刚来的备份点，在计算子网可靠性时加入
				if inflag == 0:

					self.usedpynode[snumber].append(leftnode[j])
					leftnode[j].update(require[0][minnum] + require[0][secnum])
					if len(tempprimnode) > 0:
						tempprimnode.remove(minnode) #改写eq 方法，可以如此
					if len(tempprimnode) > 0:
						tempprimnode.remove(secondnode)
					flag = 1
					break
				# else:
				# 	self.mygraph.restoreG(requirebd)

				# else: 
				# 	self.mygraph.restoreG(requirebd)
		if flag == 1:
			subnetnode = []
			subnetnode.append(minnode),subnetnode.append(secondnode),subnetnode.append(choosednode)
			return subnetnode
		else:
			return False

	def calrelias(self,usednode):#计算一条链的可靠性
		singleSFC = 1
		if usednode != False:
			for k in range(len(usednode)):
				singleSFC *= usednode[k].relia
			return singleSFC
		else :
			return -2
	def calsubnetrelia(self,subnode):#计算一次备份映射的可靠性
		minnodelen = len(subnode[0].backupnode) 
		secnodelen = len(subnode[1].backupnode)
		subnet = []
		if  minnodelen == 0  and  secnodelen == 0:
			subrel = 1 - (1 - subnode[2].temprelia)*(1 - subnode[0].temprelia*subnode[1].temprelia)
			subnet.append(subnode[0])
			subnet.append(subnode[1])
			self.subnets.append(subnet)
			subnode[0].subrelia = subrel
			subnode[1].subrelia = subrel
		elif minnodelen == 0 and secnodelen != 0:
			rn = subnode[1].subrelia
			#fenzi = 1
			fenmu = 1
			tao = 1 + 0.07
			for i in range(secnodelen):
				fenmu *= ( 1 - subnode[1].backupnode[i].temprelia)
			fenzi = fenmu*rn

			exceptrelia = (1 - subnode[1].temprelia)*fenzi/(tao - (1 - subnode[1].temprelia)*fenmu)
			subrel = rn * (1-(1-subnode[2].temprelia)*(1-subnode[0].temprelia)) + subnode[2].temprelia*exceptrelia
			for j in range(len(self.subnets)):
				if subnode[1] in self.subnets[j]:
					self.subnets[j].append(subnode[0])
					for k in range(len(self.subnets[j])):
						self.subnets[j][k].subrelia = subrel
		elif minnodelen != 0 and secnodelen == 0:
			rn = subnode[0].subrelia #最新子网的可靠性
			fenmu = 1
			tao = 1 + 0.07
			for i in range(minnodelen):
				fenmu *= ( 1 - subnode[0].backupnode[i].temprelia)
			fenzi = fenmu*rn
			exceptrelia = (1 - subnode[0].temprelia)*fenzi/(tao - (1 - subnode[0].temprelia)*fenmu)
			subrel = rn * (1-(1-subnode[2].temprelia)*(1-subnode[1].temprelia)) + subnode[2].temprelia*exceptrelia
			for j in range(len(self.subnets)):
				if subnode[0] in self.subnets[j]:
					self.subnets[j].append(subnode[1])
					for k in range(len(self.subnets[j])):
						self.subnets[j][k].subrelia = subrel
		elif  minnodelen != 0 and secnodelen != 0:
			firstsubnet = -1
			secondsubnet = -2
			for m in range(len(self.subnets)):
				if subnode[0] in self.subnets[m]:
					firstsubnet = m
				if subnode[1] in self.subnets[m]:
					secondsubnet = m
			if secondsubnet == firstsubnet:
				subrel = subnode[1].subrelia + subnode[2].temprelia * (1 - subnode[1].subrelia)
				for i in range(len(self.subnets[firstsubnet])):
					self.subnets[firstsubnet][i].subrelia = subrel
			else:
				minrn = subnode[0].subrelia #最新的子网的可靠性
				secrn = subnode[1].subrelia
				minfenmu = 1
				secfenmu = 1
				tao = 1 + 0.07
				for i in range(minnodelen):
					minfenmu *= ( 1 - subnode[0].backupnode[i].temprelia)
				for i in range(secnodelen):
					secfenmu *= ( 1 - subnode[1].backupnode[i].temprelia)
				minfenzi = minfenmu*minrn
				secfenzi = secfenmu*secrn
				exceptmin = (1 - subnode[0].temprelia)*minfenzi/(tao - (1 - subnode[0].temprelia)*minfenmu)
				exceptsec = (1 - subnode[1].temprelia)*secfenzi/(tao - (1 - subnode[1].temprelia)*secfenmu)
				subrel = minrn*secrn +  subnode[2].temprelia*(exceptsec*exceptmin + exceptsec*minrn + exceptmin*secrn)
				for i in range(len(self.subnets[firstsubnet])):
					self.subnets[firstsubnet][i].subrelia = subrel
				for i in range(len(self.subnets[secondsubnet])):
					self.subnets[secondsubnet][i].subrelia = subrel 
				self.subnets[firstsubnet].extend(self.subnets[secondsubnet])
				del(self.subnets[secondsubnet]) #check if firtstsubnet has changed as well!!!!

		subnode[0].temprelia = 1 - (1 - subnode[2].temprelia)*(1 - subnode[0].temprelia)
		subnode[1].temprelia = 1 - (1 - subnode[2].temprelia)*(1 - subnode[1].temprelia)
		subnode[0].backupnode.append(subnode[2])
		subnode[1].backupnode.append(subnode[2])

	def embedloop(self):
		temprequire = []
		#print "before",len(self.requires)
		for i in range(len(self.requires)):
			if self.embedPrim(self.requires[i]):
				temprequire.append(self.requires[i])
			self.mygraph.reset() ###here
				#self.embednum += len(self.requires[i][0])
		#embed prim nodes
		for k in range(self.nodenum):
			if self.node[k].sharetime > 0:
				self.embednum += 1
		print "初始映射：",self.embednum
		self.requires = temprequire

		for i in range(len(self.requires)):
			self.subnets = []
			
			#if self.embedPrim(self.requires[i]):
			primrelia = self.calrelias(self.usedpynode[i])
			if primrelia >= self.requires[i][1]:
				self.embedlinkrelia.append(primrelia)
			else:
				primsfc = [] #用于计算子网的初始映射节点
				primnodes = [] #保存初始映射节点
				for k in range(len(self.usedpynode[i])):#挨个引用不会跟self.usednode同时修改
					primsfc.append(self.usedpynode[i][k])
					primnodes.append(self.usedpynode[i][k])
				#primsfc = self.usedpynode[i]#初始映射的节点
				tag = len(self.embedlinkrelia)
				for time in range(10):#备份最多次数
					self.mygraph.reset() ###here
					temprelia = 1
					bnode = self.embedbackup(primnodes,primsfc,self.requires[i],i)
					if bnode != False:
						self.calsubnetrelia(bnode)
						for j in range(len(self.subnets)):
							temprelia *=self.subnets[j][0].temprelia
						for m in range(len(primsfc)):
							temprelia *= primsfc[m].temprelia
						#print temprelia
						if temprelia >= self.requires[i][1]:
							self.embedlinkrelia.append(temprelia)
							break
					else:
						self.embedlinkrelia.append(-1) #映射不成功的
						break
				if tag != (len(self.embedlinkrelia) - 1):
					self.embedlinkrelia.append(-2) #备份次数达到上限

				for n in range(len(primnodes)):
					primnodes[n].temprelia = primnodes[n].relia
					primnodes[n].backupnode = []
					primnodes[n].subrelia = 0 # in fact  it is  redundant and just in case	
			

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
		requires = requestcreat(3,[0.95,0.99,0.999])
		# start = time.clock()
		nodes = random.randint(500,600) #节点数
		node = []
		for i in range(nodes):
			node.append(Node(i))
		mygraph = Graph(nodes)
		mybp = GREP(node,mygraph,nodes,2)
		#mybp = GREP()#要带参数
		print "success!"
		# end = time.clock()
		# end-start
		#多次
		looptime = 3
		for i in range(looptime):
			increaseratio = []
			mybp.getrequire(requires[i%3])

			#print requires[i%3]

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

		f = open('myGreptest.txt','a')
		f.writelines('\n'+ 'increase: ' + str(Y) +'\n'+'usedresource: ' + str(M) + '\n')
		f.writelines('acceptrate:'+ str(Z) + '\n'+ 'bizhi: '+ str(W) + '\n')
		f.writelines('embedresourece: ' + str(S) + '\n' + 'cputime' + str(T)+'\n')
		f.close()

		#plot
		names=["0.95","0.99","0.999"]  
		X = range(len(names))

		fig = plt.figure()
		plt.subplot(221)  
		plt.bar(X,Z,0.4,color="green")  
		plt.xticks(X, names)
		plt.ylabel("acrate")  
		plt.title("acceptance of SFCs in GREP")  

		plt.subplot(222)
		plt.bar(X,M,0.4,color="red")  
		plt.xticks(X, names) 
		plt.ylabel("userate")  
		plt.title("use of nodes in GREP")

		plt.subplot(223)
		plt.bar(X,Y,0.4,color="blue")  
		plt.xticks(X, names)
		plt.ylabel("increaserate")  
		plt.title("increaserate  in GREP")

		plt.subplot(224) 
		plt.bar(X,W,0.4,color="black")  
		plt.xticks(X, names) 
		plt.ylabel("bizhi")  
		plt.title("bizhi  in GREP")

		fig = plt.figure()
		plt.bar(X,T,0.4,color="orange")  
		plt.xticks(X, names) 
		plt.ylabel("cputime")  
		plt.title("cputime of GREP")
		plt.show()  






						









