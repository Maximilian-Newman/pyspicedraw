# draws a circuit created using PySpice
# for sanity checks, to make sure the circuit was properly defined

import schemdraw
import schemdraw.elements as elm
import random

translate_type = {
"VoltageSource" : elm.SourceV,
"Resistor" : elm.Resistor
    }

opposite = {
    "right" : "left",
    "left" : "right",
    "up": "down",
    "down" : "up"
}


def take_direction(takenDirDict, node, direction):
    if node in takenDirDict.keys():
        takenDirDict[node].append(direction)
    else:
        takenDirDict[node] = [direction]

def avail_directions(takenDirDict, node):
    if node not in takenDirDict.keys():
        return ["up", "down", "right", "left"]

    l = []
    for direction in ["up", "down", "right", "left"]:
        if direction not in takenDirDict[node]:
            l.append(direction)
    return l

def rand_dir(takenDirDict, node):
    return random.choice(avail_directions(takenDirDict, node))


    


def draw(circuit, predefinedNodes = None):
    knownNodes = dict()
    takenDirections = dict()
    firstElement = True

    if predefinedNodes != None:
        for obj in predefinedNodes:
            knownNodes[obj[0]] = obj[1]
    
    with schemdraw.Drawing():
        
        for element in circuit.elements:
            print(element.__class__.__name__, element.name, element.nodes, str(element.nodes[0]))
            elmtype = translate_type[element.__class__.__name__]
            
            nodes = [None, None]
            for i in range(0, len(element.nodes)):
                if str(element.nodes[i]) in knownNodes.keys():
                    nodes[i] = knownNodes[str(element.nodes[i])]

            
            if firstElement:
                comp = elmtype().up().label(element.name)
                knownNodes[str(element.nodes[0])] = comp.start
                knownNodes[str(element.nodes[1])] = comp.end

                take_direction(takenDirections, comp.start, "up")
                take_direction(takenDirections, comp.end, "down")

                firstElement = False

            elif nodes[0] != None and nodes[1] == None:
                direction = rand_dir(takenDirections, nodes[0])

                if direction == "up": comp = elmtype().label(element.name).up().at(nodes[0])
                if direction == "down": comp = elmtype().label(element.name).down().at(nodes[0])
                if direction == "right": comp = elmtype().label(element.name).right().at(nodes[0])
                if direction == "left": comp = elmtype().label(element.name).left().at(nodes[0])

                take_direction(takenDirections, nodes[0], direction)
                take_direction(takenDirections, comp.end, opposite[direction])
                
                #w = elm.Wire("-|").at(nodes[0])
                #comp = elmtype().label(element.name).right().at(w.end)
                
                knownNodes[str(element.nodes[1])] = comp.end

            elif nodes[0] != None and nodes[1] != None:
                comp = elmtype().label(element.name).endpoints(nodes[0], nodes[1])
                
                #w = elm.Wire("|-").at(nodes[0])
                #comp = elmtype().label(element.name).at(w.end)
                #elm.Wire("|-").endpoints(comp.end, nodes[1])
                
                #comp = elmtype().label(element.name).at(nodes[0])
                #print(nodes)
                #print(comp.end)
                #elm.Wire().to(nodes[1])

                #comp = elmtype().label(element.name).endpoints(nodes[0], nodes[1])

            else:
                print("ERROR: ", nodes)
