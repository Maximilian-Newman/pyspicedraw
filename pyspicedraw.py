# draws a circuit created using PySpice
# for sanity checks, to make sure the circuit was properly defined

import schemdraw
import schemdraw.elements as elm

translate_type = {
"VoltageSource" : elm.SourceV,
"Resistor" : elm.Resistor
    }





def draw(circuit):
    knownNodes = dict()
    with schemdraw.Drawing() as d:
        #elm.Resistor() # temporary
        
        for element in circuit.elements:
            print(element.__class__.__name__, element.name, element.nodes, type(element.nodes))
            elmtype = translate_type[element.__class__.__name__]
            
            nodes = [None, None]
            for i in range(0, len(element.nodes)):
                if element.nodes[i] in knownNodes.keys():
                    nodes[i] = knownNodes[element.nodes[i]]

            
            if nodes[0] == None and nodes[1] == None: #assume first element
                comp = elmtype()
                d.add(comp)
                knownNodes[element.nodes[0]] = comp.start
                knownNodes[element.nodes[1]] = comp.end

            elif nodes[0] != None and nodes[1] == None:
                comp = elmtype().right().at(nodes[0])
                d.add(comp)
                knownNodes[element.nodes[1]] = comp.end

            elif nodes[0] != None and nodes[1] != None:
                print(nodes)
                comp = elmtype().endpoints(nodes[0], nodes[1])
                d.add(comp)

            else:
                print("ERROR: ", nodes)
