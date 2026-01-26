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
    node = schemdraw.util.Point(node)
    
    if node in takenDirDict.keys():
        takenDirDict[node].append(direction)
    else:
        takenDirDict[node] = [direction]

def avail_directions(takenDirDict, node):
    node = schemdraw.util.Point(node)
    
    if node not in takenDirDict.keys():
        return ["up", "down", "right", "left"]

    l = []
    for direction in ["up", "down", "right", "left"]:
        if direction not in takenDirDict[node]:
            l.append(direction)
    return l

def rand_dir(takenDirDict, node):
    return random.choice(avail_directions(takenDirDict, node))

def generate_label(element):
    label = element.name
    if element.__class__.__name__ == "VoltageSource":
        label += "\n" + str(element.dc_value)
    elif element.__class__.__name__ == "Resistor":
        label += "\n" + str(element.resistance)
    return label
    


def draw(circuit, predefinedNodes = None, separateGround = False, groundNode = "0"):
    knownNodes = dict()
    takenDirections = dict()
    firstElement = True
    gndCount = 0

    if predefinedNodes != None:
        for obj in predefinedNodes:
            knownNodes[obj[0]] = obj[1]
    
    with schemdraw.Drawing():
        
        for element in circuit.elements:
            print(element.__class__.__name__, element.name, element.nodes)
            elmtype = translate_type[element.__class__.__name__]

            comp = None
            
            nodes = [None, None]
            nodeNames = [str(i) for i in element.nodes]

            if separateGround:
                for i in range(0, len(nodeNames)):
                    if nodeNames[i] == groundNode:
                        print(nodeNames[i])
                        nodeNames[i] = "GND_" + str(gndCount)
                        gndCount += 1
            
            for i in range(0, len(nodeNames)):
                if nodeNames[i] in knownNodes.keys():
                    print(nodeNames[i])
                    nodes[i] = knownNodes[nodeNames[i]]

            
            if firstElement and nodes[0] == None and nodes[1] == None:
                comp = elmtype().up()
                knownNodes[nodeNames[0]] = comp.start
                knownNodes[nodeNames[1]] = comp.end

                take_direction(takenDirections, comp.start, "up")
                take_direction(takenDirections, comp.end, "down")

            elif nodes[0] != None and nodes[1] == None:
                print(nodes)
                direction = rand_dir(takenDirections, nodes[0])

                if direction == "up": comp = elmtype().up().at(nodes[0])
                if direction == "down": comp = elmtype().down().at(nodes[0])
                if direction == "right": comp = elmtype().right().at(nodes[0])
                if direction == "left": comp = elmtype().left().at(nodes[0])

                take_direction(takenDirections, nodes[0], direction)
                take_direction(takenDirections, comp.end, opposite[direction])
                
                knownNodes[nodeNames[1]] = comp.end



            elif nodes[0] != None and nodes[1] != None:
                comp = elmtype().label(generate_label(element)).endpoints(nodes[0], nodes[1])

            else:
                print("ERROR: ", nodes)

            if elmtype == elm.SourceV: # PySpice defines + as first node, - as second
                comp.reverse()
                print("did flip")

            comp.label(generate_label(element))

            firstElement = False

        for key, val in knownNodes.items():
            elm.Label().at(val).label(key).color("red")
