#encoding utf-8
from graph import Graph
import copy
class addGraph(Graph):

	def __init__(self,numofnode):
		Graph.__init__(self,numofnode)

	def findkhop(self,k,start):#find within k hop 
		storednode = []
		tempgragh = copy.deepcopy(self.topo)
		self.bfs(tempgragh,start)
		for i in range(self.numofnode):
			if self.distant[i] <= k and self.distant[i] > 0:
				storednode.append(i)
		#self.reset()
		return storednode


