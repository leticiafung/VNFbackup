#encoding:utf-8
import random

class Node(object):
	def __init__(self):
		self.relia = random.uniform(0.9, 0.99)
		self.resource = random.randint(100, 500)
		self.sharetime = 0
		
	def update(self,useresource):
		self.resource -= usesharetime
		self.sharetime += 1
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
			self.node.append(Node())
		self.usedpynode = []
		self.embedlinkrelia = [] #达到可靠性需求后的链路可靠性
		#self.usedbacknode = []
	def getrequire(self,require):
		#[[[resource],reliability],[]] 0为资源，1为可靠性
		self.requires = require

	def embedPrim(self,require1):#single require at a time,not backup embed 
		self.node.sort(reverse = True)
		self.usedpynode = []	
		for i in range(len(require1[0])):
			for j in range(nodenum):	
				if self.node[j].sharetime < 2 and self.node[j].resource >= require[0][i]:
					self.node[j].update(require[0][i])
					usedpynode.append(self.node[j])
					break	 		
			return False
		return True
	def embedBackup(self,require1):
		leftnode = [item for item in self.node if item not in self.usedpynode]
		leftnode.sort(reverse = True)
		usedbacknode = []
		for i in range(len(require1[0])):
			for j in range(len(leftnode)):	
				if leftnode[j].sharetime < 2 and leftnode[j].resource >= require[0][i]:
					leftnode[j].update(require[0][i])
					usedbacknode.append(leftnode[j])
					break	 		
			return False
		return usedbacknode
	def calrelias(usednode):#计算一条链的可靠性
		singleSFC = 1
		for k in range(len(usedpynode)):
			singleSFC *= usedpynode[k].relia
		return singleSFC

	def embedloop(self):
		for i in range(len(self.requires)):

			temprelia = 0
			primrelia = self.calrelias(self.usedpynode)
			if self.embedPrim(self.requires[i]):
				if primrelia >= self.requires[i][1]:
					self.embedlinkrelia.append(primrelia)
				else:
					for time in range(10):#备份链最多次数
						temprelia = 1 - primrelia
						if self.embedBackup():
							temprelia *= 1-calrelias(self.embedBackup())
							if 1 - temprelia >= self.require[i][1]:
								self.embedlinkrelia.append(1 - temprelia)
								break
						else:
							self.embedlinkrelia.append(0) #没有满足要求的链直接置0
							break
	def getembedlinkrelia(self):
		return self.embedlinkrelia

	if __name__ == '__main__':
		mybp = Fullbp()
		requre = [[[100,200,300],0.95],[[250,300],0.95]]
		mybp.getrequire(requre)
		mybp.embedloop()
		c = mybp.getembedlinkrelia()
		print c







    					









