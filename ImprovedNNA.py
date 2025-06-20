import networkx as nx
import os, math, copy, time
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, LineString
script_dir = os.path.dirname(os.path.abspath(__file__))

LevelRange = 7
AreaZeroPoints = [
    (404, 491), (409, 502),
    (401, 503), (395, 515),
    (400, 522), (413, 528),
    (413, 541), (433, 558),
    (449, 578), (482, 586),
    (499, 594), (496, 582),
    (519, 564), (556, 600),
    (576, 594), (606, 601),
    (615, 589), (617, 547),
    (619, 474), (590, 416),
    (569, 388), (547, 397),
    (518, 379), (495, 389),
    (469, 391), (448, 407),
    (439, 436), (415, 453),
    (412, 479)
]

AlfornadaAlternatePathPoints = [
    (236, 654),
    (221, 666),
    (220, 683),
    (219, 696),
    (227, 701)
]

def file_path(filename) :
    return os.path.join(script_dir, filename)

nodefile = file_path('Badge_Data.txt')


def moveTo(Array, idx, Elmt) :
    ArrayNew = []
    for x in Array :
        if (x != Elmt) :
            ArrayNew.append(x)
    ArrayNew.insert(idx, Elmt)
    
    return ArrayNew

def initializeNodes(file, G, pos) :
    data = open(file_path(file))
    line = data.readline()[:-1]
    n = 0
    while line != '=======================' :
        name, attr = line.split(' : ')
        coords, lvl = attr.split(' ; ')
        nodecoords=[]
        for x in coords.split(',') :
            nodecoords.append(int(x))
        G.add_node(n, name=name, level=int(lvl), x=nodecoords[0], y=nodecoords[1])
        pos[n] = nodecoords
        n += 1
        line = data.readline()[:-1]



def midPoint(point1, point2) :
    x1 = point1[0]
    x2 = point2[0]
    y1 = point1[1]
    y2 = point2[1]
    return (((x1 + x2)/2), ((y1 + y2)/2))

def pointDistance(point1, point2) :
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def AlfornadaAlternatePathDistance(G) :
    AlfornadaCoords = (G.nodes[14]['x'], G.nodes[14]['y'])
    distance = 0
    for i in range(len(AlfornadaAlternatePathPoints) - 1) :
        distance += pointDistance(AlfornadaAlternatePathPoints[i], AlfornadaAlternatePathPoints[i + 1])
    distance += pointDistance(AlfornadaAlternatePathPoints[len(AlfornadaAlternatePathPoints) - 1], AlfornadaCoords)
    return distance

def isPathIntersectingAreaZero(point1, point2) :
    line = LineString([point1, point2])
    AreaZeroPolygon = Polygon(AreaZeroPoints)
    if line.intersects(AreaZeroPolygon) :
        if line.intersection(AreaZeroPolygon).geom_type == 'Point' :
            state = False
        else :
            state = True
    else :
        state = False
    return state

def pathDistanceAroundAreaZero(point1, point2) :
    CurrPath = [point1, point2]
    while True :
        state = False
        for i in [0, len(CurrPath) - 2]:
            if isPathIntersectingAreaZero(CurrPath[i], CurrPath[i+1]) :
                state = True
                middle = midPoint(CurrPath[i], CurrPath[i+1])
                closestPoint = AreaZeroPoints[0]
                for x in AreaZeroPoints :
                    state2 = True
                    for y in CurrPath :
                        if (x == y) :
                            state2 = False
                            break

                    if state2 and (pointDistance(closestPoint, middle) > pointDistance(x, middle)) :
                        closestPoint = x
                CurrPath.insert(i + 1, closestPoint)
        if not(state) :
            break

    while not(isPathIntersectingAreaZero(CurrPath[0], CurrPath[2])) :
        CurrPath.pop(1)
    while not(isPathIntersectingAreaZero(CurrPath[len(CurrPath) - 1], CurrPath[len(CurrPath) - 3])) :
        CurrPath.pop(len(CurrPath) - 2)

    distance = 0
    for i in range(len(CurrPath) - 1) :
        distance += pointDistance(CurrPath[i], CurrPath[i + 1])

    return distance
            

def pathDistance(G, node1, node2, visitedNodes) :
    nodepoint1 = (G.nodes[node1]['x'], G.nodes[node1]['y'])
    nodepoint2 = (G.nodes[node2]['x'], G.nodes[node2]['y'])
    climb_obtained = False
    alternate_distance = 0
    for x in visitedNodes :
        if (x == 17) or (x == 8) :
            climb_obtained = True

    if (node2 == 14) and not(climb_obtained) :
        nodepoint2 = AlfornadaAlternatePathPoints[0]
        alternate_distance += AlfornadaAlternatePathDistance(G)
        
    if isPathIntersectingAreaZero(nodepoint1, nodepoint2) :
        distance = pathDistanceAroundAreaZero(nodepoint1, nodepoint2)
        path_shape = 'modified'
    else :
        distance = pointDistance(nodepoint1, nodepoint2)
        path_shape = 'straight'

    if alternate_distance > 0 :
        path_shape = 'modified'
        distance += alternate_distance
    return distance, path_shape

def addInitialEdges(G) :
    for i in (G.nodes) :
        offset = 0
        for j in (G.nodes) :
            if (j != 17) and (j != 19) :
                if (G.nodes[j]['level'] <= G.nodes[i]['level'] + LevelRange) and (G.nodes[i]['level'] <= G.nodes[j]['level']) and (i != j) :
                    distance, shape = pathDistance(G,i,j,[0])
                    G.add_edge(i, j, weight=round(distance), shape=shape)
                    offset += 1

def currentLevel(G, VisitedNodes) :
    Curr = G.nodes[VisitedNodes[0]]['level']
    for l in VisitedNodes :
        if (G.nodes[l]['level'] > Curr) :
            Curr = G.nodes[l]['level']
    
    return Curr

def updateGraphRoutes(G, VisitedNodes) :
    G.remove_edges_from(list(G.edges()))
    CurrentNode = VisitedNodes[len(VisitedNodes) - 1]
    CurrentLevel = currentLevel(G, VisitedNodes)
    state2 = False
            
    for Dest in (G.nodes) :
        state = True
        state1 = True
        state2 = True
        for (_,v) in (G.edges(CurrentNode)) :
            if (v == Dest) :
                state = False
                break
        for x in VisitedNodes :
            if (x == Dest) :
                if (len(VisitedNodes) != len(G.nodes)) or (x != VisitedNodes[0]) :
                    state = False
                    break
                
        if (Dest == 17) : #False Dragon Badge can only be obtained once the Open Sky Badge is obtained
            state1 = False
            for y in VisitedNodes :
                if y == 4 :
                    state1 = True
                    break
        
        if (Dest == 19) : #Path of Legends Finale can only be triggered once all Titan Badges are obtained
            state2 = False
            z2 = 0
            for z in VisitedNodes :
                if (z == 2) or (z == 4) or (z == 8) or (z == 13) or (z == 17) :
                    z2+=1

            if z2 == 5 :
                state2 = True
        if state and state1 and state2 and (CurrentLevel + LevelRange >= G.nodes[Dest]['level']) :
            distance, shape = pathDistance(G, CurrentNode, Dest, VisitedNodes)
            G.add_edge(CurrentNode, Dest, weight=round(distance), shape=shape)

def closestPossibleNode(G, VisitedNodes) :
    if len(VisitedNodes) == len(G.nodes) :
        return VisitedNodes[0]
    CurrentNode = VisitedNodes[len(VisitedNodes) - 1]
    state = True
    for (_,x) in G.edges(CurrentNode) :
        state1 = True
        for y in VisitedNodes :
            if x == y :
                state1 = False
                break
        
        if state1 :
            if state :
                closestNode = x
                state = False
            else:
                if (G[CurrentNode][x]['weight'] < G[CurrentNode][closestNode]['weight']) :
                    closestNode = x
    
    return closestNode

def currentDistanceTraveled(G, VisitedNodes) :
    distance = 0
    for i in range(len(VisitedNodes) - 1) :
        d, _ = pathDistance(G, VisitedNodes[i], VisitedNodes[i + 1], VisitedNodes[:(i + 1)])
        distance += d
        
    return round(distance)

def nearestLoopLength(G, VisitedNodes, NextNode) :
    G1 = copy.deepcopy(G)
    CurrVisited = []
    for x in VisitedNodes :
        CurrVisited.append(x)
    DestNode = NextNode
    while len(CurrVisited) <= len(G1.nodes) :
        CurrVisited.append(DestNode)
        updateGraphRoutes(G1, CurrVisited)
        if (len(CurrVisited) <= len(G1.nodes)) :
            DestNode = closestPossibleNode(G1, CurrVisited)

    return currentDistanceTraveled(G1, CurrVisited), CurrVisited

def recommendedNextNode(G, VisitedNodes) :
    if len(VisitedNodes) == len(G.nodes) :
        return VisitedNodes[0]
    CurrentNode = VisitedNodes[len(VisitedNodes) - 1]
    state = True
    for (_,x) in G.edges(CurrentNode) :
        state1 = True
        for y in VisitedNodes :
            if x == y :
                state1 = False
                break
        
        if state1 :
            if state :
                nextNode = x
                state = False
            else:
                if (nearestLoopLength(G, VisitedNodes, x)[0] < nearestLoopLength(G, VisitedNodes, nextNode)[0]) :
                    nextNode = x

        
    return nextNode

def recommendedNextNodeVer2(G, VisitedNodes) :
    if len(VisitedNodes) == len(G.nodes) :
        return VisitedNodes[0]
    CurrentNode = VisitedNodes[len(VisitedNodes) - 1]
    state = True
    for (_,x) in G.edges(CurrentNode) :
        state1 = True
        for y in VisitedNodes :
            if x == y :
                state1 = False
                break
        
        if state1 :
            if state :
                nextNode = x
                state = False
            else:
                if (nearestLoopLength(G, VisitedNodes, x)[0] < nearestLoopLength(G, VisitedNodes, nextNode)[0]) :
                    nextNode = x

    newNextNode = nextNode
    plannedLoopPath = nearestLoopLength(G, VisitedNodes, nextNode)[1]
    while True :
        shortestLoopPath = plannedLoopPath
        for (_,z) in G.edges(CurrentNode) :
            state1 = True
            for y in VisitedNodes :
                if z == y :
                    state1 = False
                    break
                
            if state1 and z != nextNode :
                if (currentDistanceTraveled(G, shortestLoopPath) > currentDistanceTraveled(G, moveTo(plannedLoopPath, len(VisitedNodes), z))) :
                    shortestLoopPath = moveTo(plannedLoopPath, len(VisitedNodes), z)
                    newNextNode = z
        plannedLoopPath = shortestLoopPath
        if nextNode == newNextNode :
            break
        else :
            nextNode = newNextNode
        
    return nextNode
    

def saveGraph(G, pos, filename) :
    edge_colors = []
    for (u,v) in G.edges :
        if G[u][v]['shape'] == 'modified' :
            edge_colors.append('orange')
        else :
            edge_colors.append('black')
    edge_labels = nx.get_edge_attributes(G,'weight')
    plt.figure(figsize =(10.24, 8.4))
    plt.gca().invert_yaxis()
    nx.draw(G, pos, with_labels=True, edge_color=edge_colors)
    nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels)
    plt.savefig(file_path(filename))

def findShortestCycle(G) :
    G2 = nx.DiGraph()
    pos2 = {}
    initializeNodes(nodefile, G2, pos2)
    addInitialEdges(G)
    visitedNodes = [0]
    n = 0
    while len(visitedNodes) <= len(G.nodes) :
        n += 1
        CN = closestPossibleNode(G, visitedNodes)
        print(f'{G.nodes[visitedNodes[len(visitedNodes) - 1]]['name']}->{G.nodes[CN]['name']} : {round(pathDistance(G, visitedNodes[len(visitedNodes) - 1], CN, visitedNodes)[0])}')
        visitedNodes.append(CN)
        G2.add_edge(visitedNodes[len(visitedNodes) - 2], CN, 
                    weight = G[visitedNodes[len(visitedNodes) - 2]][CN]['weight'],
                    shape = G[visitedNodes[len(visitedNodes) - 2]][CN]['shape'])
        updateGraphRoutes(G, visitedNodes)
    print(f'Total Distance :  {currentDistanceTraveled(G,
          visitedNodes)}')
    saveGraph(G2, pos2, 'GraphVis/ShortestCycleVer1.png')
    
def findShortestCycleVer2(G) :
    G2 = nx.DiGraph()
    pos2 = {}
    initializeNodes(nodefile, G2, pos2)
    addInitialEdges(G)
    visitedNodes = [0]
    n = 0
    while len(visitedNodes) <= len(G.nodes) :
        n += 1
        CN = recommendedNextNode(G, visitedNodes)
        print(f'{G.nodes[visitedNodes[len(visitedNodes) - 1]]['name']}->{G.nodes[CN]['name']} : {round(pathDistance(G, visitedNodes[len(visitedNodes) - 1], CN, visitedNodes)[0])}')
        visitedNodes.append(CN)
        G2.add_edge(visitedNodes[len(visitedNodes) - 2], CN, 
                    weight = G[visitedNodes[len(visitedNodes) - 2]][CN]['weight'],
                    shape = G[visitedNodes[len(visitedNodes) - 2]][CN]['shape'])
        updateGraphRoutes(G, visitedNodes)
        #saveGraph(G2, pos2, f'GraphVis/ShortestCycleVer2_{n}.png')
    print(f'Total Distance :  {currentDistanceTraveled(G,
          visitedNodes)}')
    saveGraph(G2, pos2, 'GraphVis/ShortestCycleVer2.png')
    
def findShortestCycleVer3(G) :
    G2 = nx.DiGraph()
    pos2 = {}
    initializeNodes(nodefile, G2, pos2)
    addInitialEdges(G)
    visitedNodes = [0]
    n = 0
    while len(visitedNodes) <= len(G.nodes) :
        n += 1
        CN = recommendedNextNodeVer2(G, visitedNodes)
        print(f'{G.nodes[visitedNodes[len(visitedNodes) - 1]]['name']}->{G.nodes[CN]['name']} : {round(pathDistance(G, visitedNodes[len(visitedNodes) - 1], CN, visitedNodes)[0])}')
        visitedNodes.append(CN)
        G2.add_edge(visitedNodes[len(visitedNodes) - 2], CN, 
                    weight = G[visitedNodes[len(visitedNodes) - 2]][CN]['weight'],
                    shape = G[visitedNodes[len(visitedNodes) - 2]][CN]['shape'])
        updateGraphRoutes(G, visitedNodes)
    print(f'Total Distance :  {currentDistanceTraveled(G,
          visitedNodes)}')
    saveGraph(G2, pos2, 'GraphVis/ShortestCycleVer3.png')

start_time = time.time()
G = nx.DiGraph()  
pos = {}
initializeNodes(nodefile, G, pos)
findShortestCycleVer3(G)
print(f'--- {(time.time() - start_time)} seconds ---')