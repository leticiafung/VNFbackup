#encoding:utf-8
import random
import numpy as np    
import matplotlib.mlab as mlab    
import matplotlib.pyplot as plt 
import time
import copy
from graph import Graph
from FullBack import Fullbp
from Grep import GREP
from Grep import Node #grep的node 私有成员多一些，哎应该用继承的！
from justeough import JENA
from Graphadd import addGraph

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
			
		nodes = random.randint(500,600) #节点数
		node = []
		for i in range(nodes):
			node.append(Node(i))
		mygraph = Graph(nodes)
		newgraph = Graph(nodes)
		everyrequires = requestcreat(100,[0.95,0.99,0.999])
		for algo in range(4):
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
			requires = copy.deepcopy(everyrequires)
			# start = time.clock()
			#mybp = Fullbp()
			if algo  == 0:
				mybp = Fullbp(node,mygraph,nodes,2)#共享程度为2
			elif algo == 1 :
				mybp = GREP(node,mygraph,nodes,2)
			elif algo == 2:
				mybp = Fullbp(node,newgraph,nodes,2)
			else:
				mybp = GREP(node,newgraph,nodes,2)




			print "success!"
			# end = time.clock()
			# end-start
			#多次
			looptime = 30
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
			if algo  == 0 or algo == 2 :	
				f = open('mybpgraph.txt','a')
			else:
				f = open('myGrepgraph.txt','a')
			f.writelines('graph =' + str(algo) +'\n')#algo = 0,1原图，2,3新图
			f.writelines('\n'+ 'increase: ' + str(Y) +'\n'+'usedresource: ' + str(M) + '\n')
			f.writelines('acceptrate:'+ str(Z) + '\n'+ 'bizhi: '+ str(W) + '\n')
			f.writelines('embedresourece: ' + str(S) + '\n' + 'cputime' + str(T)+'\n')
			f.close()

			#plot
			# names=["0.95","0.99","0.999"]  
			# X = range(len(names))

			# fig = plt.figure()
			# plt.subplot(221)  
			# plt.bar(X,Z,0.4,color="green")  
			# plt.xticks(X, names)
			# plt.ylabel("acrate")
			# if algo  == 0 or algo == 2:
			# 	plt.title("acceptance of SFCs in FullBP") 
			# else:
			# 	plt.title("acceptance of SFCs in GREP")

			# plt.subplot(222)
			# plt.bar(X,M,0.4,color="red")  
			# plt.xticks(X, names) 
			# plt.ylabel("userate") 
			# if algo  == 0 or algo == 2:
			# 	plt.title("use of nodes in FullBP") 
			# else:
			# 	plt.title("use of nodes  in GREP") 
			# #plt.title("use of nodes in FullBP")

			# plt.subplot(223)
			# plt.bar(X,Y,0.4,color="blue")  
			# plt.xticks(X, names)
			# plt.ylabel("increaserate")  
			# #plt.title("increaserate  in FullBP")
			# if algo  == 0 or algo == 2:
			# 	plt.title("increaserate  in FullBP") 
			# else:
			# 	plt.title("increaserate   in GREP") 

			# plt.subplot(224) 
			# plt.bar(X,W,0.4,color="black")  
			# plt.xticks(X, names) 
			# plt.ylabel("bizhi")  
			# if algo  == 0 or algo == 2:
			# 	plt.title("bizhi in FullBP") 
			# else:
			# 	plt.title("bizhi in GREP") 
			# #plt.title("bizhi  in FullBP")

			# fig = plt.figure()
			# plt.bar(X,T,0.4,color="orange")  
			# plt.xticks(X, names) 
			# plt.ylabel("cputime")  
			# if algo  == 0 or algo == 2:
			# 	plt.title("cputime of FullBP") 
			# else:
			# 	plt.title("cputime of GREP") 
			# #plt.title("cputime of FullBP")
			# plt.show()  
