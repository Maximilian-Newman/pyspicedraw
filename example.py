import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()
from PySpice.Unit import *
from PySpice.Spice.Netlist import Circuit
import pyspicedraw

circuit = Circuit('Circuit 2')

circuit.V('1', 1, circuit.gnd, 20@u_V)
circuit.R(1, 1, 2, 1@u_kΩ)
circuit.R(2, 2, 3, 1@u_kΩ)
circuit.R(4, 3, circuit.gnd, 1@u_kΩ)
circuit.R(3, 2, circuit.gnd, 3@u_kΩ)


predefinedNodes = [["0", [0,0]], ["1", [0,3]], ["2", [3,3]], ["3", [3,0]]]

# first schematic: closed circuit, no analysis, determinisic and looks neat
pyspicedraw.draw(circuit, predefinedNodes, separateGround = False)

pyspicedraw.probe_all(circuit) # required to get currents
print(circuit)

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.operating_point()

print()
print()
pyspicedraw.print_voltages(analysis)
print()
pyspicedraw.print_currents(analysis)
print()
print()


# schematic with analysis, automatic non-deterministic node positioning
# loop to generate new ones until satisfied with node positioning
while True: pyspicedraw.draw(circuit, analysis = analysis)
