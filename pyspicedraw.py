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


def take_direction(takenDirDict, node, direction, strict = True):
    # strict=False should be used to mark that a neighboring node is already claimed, but that there is no connection yet
    node = round_point(node)

    if strict:
        print("taking direction:", node, direction)
    
    if node in takenDirDict.keys():
        takenDirDict[node].append([direction, strict])
    else:
        takenDirDict[node] = [[direction, strict]]

def claim_node(takenDirDict, node):
    node = round_point(node)
    print("claiming node:", node)
    take_direction(takenDirDict, [node[0]+3, node[1]], "left", strict=False)
    take_direction(takenDirDict, [node[0]-3, node[1]], "right", strict=False)
    take_direction(takenDirDict, [node[0], node[1]+3], "down", strict=False)
    take_direction(takenDirDict, [node[0], node[1]-3], "up", strict=False)

def avail_directions(takenDirDict, node, strict = True):
    #node = schemdraw.util.Point(node)
    node = round_point(node)
    
    if node not in takenDirDict.keys():
        return ["up", "down", "right", "left"]

    l = []
    for direction in ["up", "down", "right", "left"]:
        if [direction, True] in takenDirDict[node]:
            pass
        elif [direction, False] in takenDirDict[node] and strict:
            pass
        else:
            l.append(direction)
            
    print(node, l)
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

def round_point(point):
    return schemdraw.util.Point([round(point[0], 0), round(point[1]), 0])

def standard_actions(comp, element, elmtype):
    comp.label(generate_label(element))
    if elmtype == elm.SourceV: # PySpice defines + as first node, - as second
        comp.reverse()


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
            print()
            print()
            print(element.__class__.__name__, element.name, element.nodes)
            elmtype = translate_type[element.__class__.__name__]

            comp = None
            
            nodes = [None, None]
            nodeNames = [str(i) for i in element.nodes]

            if separateGround:
                for i in range(0, len(nodeNames)):
                    if nodeNames[i] == groundNode:
                        nodeNames[i] = "GND_" + str(gndCount)
                        gndCount += 1
            
            for i in range(0, len(nodeNames)):
                if nodeNames[i] in knownNodes.keys():
                    print("already known:", nodeNames[i])
                    nodes[i] = round_point(knownNodes[nodeNames[i]])

            
            if firstElement and nodes[0] == None and nodes[1] == None:
                comp = elmtype().down()
                
                standard_actions(comp, element, elmtype)
                
                knownNodes[nodeNames[0]] = comp.start
                knownNodes[nodeNames[1]] = comp.end

                take_direction(takenDirections, comp.start, "down")
                take_direction(takenDirections, comp.end, "up")
                claim_node(takenDirections, comp.start)
                claim_node(takenDirections, comp.end)


            elif nodes[0] != None and nodes[1] == None:
                #print(nodes)
                direction = rand_dir(takenDirections, nodes[0])

                if direction == "up": comp = elmtype().up().at(nodes[0])
                if direction == "down": comp = elmtype().down().at(nodes[0])
                if direction == "right": comp = elmtype().right().at(nodes[0])
                if direction == "left": comp = elmtype().left().at(nodes[0])

                standard_actions(comp, element, elmtype)

                take_direction(takenDirections, nodes[0], direction)
                take_direction(takenDirections, comp.end, opposite[direction])
                claim_node(takenDirections, comp.end)
                
                knownNodes[nodeNames[1]] = comp.end



            elif nodes[0] != None and nodes[1] != None:
                comp = elmtype().endpoints(nodes[0], nodes[1])
                standard_actions(comp, element, elmtype)
                
                if nodes[0][0] == nodes[1][0]: # same x
                    if nodes[0][1] > nodes[1][1]:
                        take_direction(takenDirections, nodes[0], "down")
                        take_direction(takenDirections, nodes[1], "up")
                    else:
                        take_direction(takenDirections, nodes[0], "up")
                        take_direction(takenDirections, nodes[1], "down")
                
                if nodes[0][1] == nodes[1][1]: # same y
                    if nodes[0][0] > nodes[1][0]:
                        take_direction(takenDirections, nodes[0], "left")
                        take_direction(takenDirections, nodes[1], "right")
                    else:
                        take_direction(takenDirections, nodes[0], "right")
                        take_direction(takenDirections, nodes[1], "left")
                        

            else:
                print("ERROR: ", nodes)

            firstElement = False

        for key, val in knownNodes.items():
            if key.startswith("GND_"):
                avail = avail_directions(takenDirections, val, strict=False)
                if "down" in avail:
                    elm.Ground().at(val)
                elif "right" in avail:
                    elm.Ground().at(round_point([val[0]+1, val[1]]))
                    w = elm.Wire().to(val)
                elif "left" in avail:
                    elm.Ground().at(round_point([val[0]-1, val[1]]))
                    w = elm.Wire().to(val)
                elif "up" in avail:
                    elm.Ground().at(round_point([val[0]+1, val[1]+1]))
                    w = elm.Wire("n").to(val)
                else:
                    print("ERROR: couldn't draw ground, node full")
            else:
                elm.Label().at(val).label(key).color("red")
                    
