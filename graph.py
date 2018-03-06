#encoding:utf-8
import random
import copy
import Queue
#import networkx as nx
class Graph:
#from graph import Graph
	def __init__(self,numofnode):
		self.topo = [] #connect
		self.bdwithtopo = [] #andwith resource
		self.savedpath = [] #保存已有的路径便于恢复
		self.apath = []
		self.numofnode = numofnode

		#self.specgraph = []
		for i in range(numofnode):
			pernodedist = []
			pernodeband = []
			for j in range(numofnode):
				bandwith = 0
				c = random.randint(1,10)
				if c > 3:
					connect = 1
				else:
					connect = 0
				if i == j:
					connect = 0
				if connect == 1:
					bandwith = random.randint(200, 400) #链路带宽范围
				pernodedist.append(connect)
				pernodeband.append(bandwith)
			self.topo.append(pernodedist)
			self.bdwithtopo.append(pernodeband)
		self.storedbdwidthtopo = copy.deepcopy(self.bdwithtopo)
	#def updateG(self):

	def restoreG(self,limitbdwith):
		for i in range(len(self.savedpath)):
			for j in range(len(self.savedpath[i]) - 1):
				self.bdwithtopo[j][j+1] += limitbdwith 



	def bfs(self,specgraph,start):
		self.visited = [None]*self.numofnode
		self.distant = [None]*self.numofnode
		self.pre = [None]*self.numofnode
		for i in range(self.numofnode) :
			if i != start:
				self.visited[i] = False
				self.distant[i] = 1000 #无穷大
				self.pre[i] = -1
			else:
				self.visited[i] = True
				self.distant[i] = 0
				self.pre[i] = -1
		Q = Queue.Queue()
		Q.put(start)
		while not Q.empty():
			u = Q.get()
			for i in range(self.numofnode) :
				if (i != u ) and (specgraph[u][i] != 0):
					if self.visited[i] == False:
						self.visited[i] = True
						self.distant[i] = self.distant[u] + 1
						self.pre[i] = u
						Q.put(i)
		#print "前继",self.pre
		
		#减带宽：
	def shortest_path(self,start,end,limitband):
		self.bfs(self.restrainG(limitband),start)
		while end != -1:
			if end == start:
				self.apath.append(start)
				if len(self.apath) > 1:
					self.savedpath.append(self.apath)
				self.apath = []
				return 0
			elif self.pre[end] == -1 :
				self.apath = []
				return -1
			else:
				self.bdwithtopo[start][end] -= limitband
				self.apath.append(end)
				end = self.pre[end]
# 边不相邻如何表示

	def restrainG(self,minband): #在带宽限制下的图
		specgraph = copy.deepcopy(self.topo)
		for i in range(self.numofnode):
			for j in range(self.numofnode):
				if self.bdwithtopo[i][j] < minband:
					specgraph[i][j] = 0 
		#print "专有图",specgraph
		return specgraph
    
	def reset(self):
		self.savedpath = []
	def bdreset(self):
		self.bdwithtopo = copy.deepcopy(self.storedbdwidthtopo)

if __name__ == "__main__":
	mygp = Graph(6)
	print mygp.topo
	print mygp.bdwithtopo
	#mygp.restrainG(30)
	#mygp.bfs(mygp.restrainG(30),0)
	mygp.shortest_path(0,0,100)
	print "path:",mygp.savedpath#,mygp.apath
	mygp.restoreG(100)
	print "bdtopo",mygp.bdwithtopo


