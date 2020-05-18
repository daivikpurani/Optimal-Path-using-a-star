#!/usr/bin/env python
# coding: utf-8

# In[1]:


from google.colab import drive
drive.mount('/content/drive')


# In[2]:


get_ipython().run_line_magic('pip', 'install haversine')
#Earth is almost a spherical body so we should use haversine distance between two points
from haversine import haversine


# In[ ]:


#read the node.csv file
import pandas as pd
latlonData = pd.read_csv('/content/drive/My Drive/AI Assignment/nodes.csv')

#function to get h(node)
def calculateHeuristic(currNode):
  [currLat,currLon] = latlonData[latlonData['id']==currNode].iloc[0][['lat','lon']]
  curr = (currLat, currLon)
  dest = (17.240673, 78.432342)

  return haversine(curr, dest)


# In[4]:


#to construct graph from edges.csv
get_ipython().run_line_magic('pip', 'install networkx')
import networkx as nx

#read the edges.csv file
graphData = pd.read_csv('/content/drive/My Drive/AI Assignment/edges.csv')
#we require only three columns to make a weighted graph
graphData = graphData[['source','target','length']]

#making graph
graphType = nx.Graph()
g = nx.from_pandas_edgelist(graphData, edge_attr='length', create_using=graphType)

#using openSet as a heap
import heapq

#function to create final route
def createPath(cameFrom, current):
  path = [current]
  while current in cameFrom.keys():
    current = cameFrom[current]
    path.insert(0,current)
  return path

#A* algorithm implementation
def aStar(srcNode, destNode):
  
  #set of discovered node that may need to be re-expanded. Implemented as heap.
  openSet = []
  
  #cameFrom[node] is the parent node of current node.
  cameFrom = {}
  cameFrom[srcNode] = None
  
  #tentative gScore 
  #i.e. in while loop this need to be changed if new gScore for the same node is less via some other optimal path
  cost = {}
  cost[srcNode] = 0
  
  #fScore(node) = gScore(node) + h(node)
  fScore = {}
  fScore[srcNode] = 0
  
  #cost to reach current node from the source node following an optimal path
  gScore = {}
  gScore[srcNode] = 0
  
  #pushing current node to openSet which is implemented as a heap
  heapq.heappush(openSet, (srcNode, fScore))
  
  #search begins
  while len(openSet) > 0:
    
    #popping out the visited node from openSet
    currentNode = heapq.heappop(openSet)
    
    #if arrived at destination then create path and return it
    if (currentNode[0] == destNode):
      return createPath(cameFrom,currentNode[0])
        
    #fetch neighbours of current node from graph
    neighbourData = list(g.neighbors(currentNode[0]))
        
    #in neighbourData
    for item in neighbourData:
      #distance = length of edge between currentNode & neighbourNode
      #neighbourNode is osm id of the node
      neighbourNode = item
      distance = g[currentNode[0]][neighbourNode]['length']

      #if neighbourNode has not been visited before
      if neighbourNode not in cameFrom:
        
        #cost = distance from srcNode to neighbourNode through currentNode i.e. tentative gScore of neighbourNode
        cost[neighbourNode] = gScore[currentNode[0]] + distance
        
        # if we have a neighbour that has been visited already by some other path
        # and we are visiting it again via some new path, we check which path is optimum
        if cost[neighbourNode] < gScore.get(neighbourNode, float('inf')):
          #if true then this path is better one than the previous
          #so we update everything
          cameFrom[neighbourNode] = currentNode[0]
          gScore[neighbourNode] = cost[neighbourNode]
          fScore[neighbourNode] = gScore[neighbourNode] + calculateHeuristic(neighbourNode)
          if neighbourNode not in openSet:
            heapq.heappush(openSet, (neighbourNode, fScore))

  #return openSet: it is empty, so destination was never reached. [Failure]
  return openSet


# In[ ]:


#osm id of source node
srcNode = 7065632060
#osm ide of destination node
destNode = 5711258337

#call to aStar
route = aStar(srcNode, destNode)
#popping the None
route.pop(0)

#if path not found, inform the user
if len(route)==0:
  print(f'Fatal Error: Path doesn\'t exist')


# In[6]:


#aStar function return list(route) which contains osm id's so we need to obtain lat lons from latlonData for each osm id
latlonRoute = []
for node in route:
  [lat,lon] = latlonData[latlonData['id']==node].iloc[0][['lat','lon']]
  latlonRoute.append((lat,lon))

#to find meanLat and meanLon so as to display middle location on map
from statistics import mean
meanLat = mean(point[0] for point in latlonRoute)
meanLon = mean(point[1] for point in latlonRoute)

get_ipython().run_line_magic('pip', 'install gmplot')
import gmplot

routeLats, routeLons = zip(*latlonRoute)
gmap = gmplot.GoogleMapPlotter(meanLat, meanLon, 13)
#uncomment the foloowing line to make a scatter plot the nodes along thr route
#gmap.scatter(routeLats, routeLons, '#FF0000', size = 50, marker = False )
gmap.plot(routeLats, routeLons, 'cornflowerblue', edge_width = 3.0)
gmap.draw('route.html')

