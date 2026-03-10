from ikpy.chain import Chain
import ikpy.link
from ikpy.link import OriginLink, URDFLink
import matplotlib.pyplot
from mpl_toolkits.mplot3d import Axes3D
import math
pi = math.pi

link1 = ikpy.link.DHLink("link1",0,40,pi/2,pi/2)
link1.bounds=(0,0.0000001)
link2 = ikpy.link.DHLink("link2",-80,0,pi/2,pi/2)
link3 = ikpy.link.DHLink("link3",280,0,pi/2,0)
link4 = ikpy.link.DHLink("link4",0,280,0,pi/2)

my_chain = Chain(name="arm", links=[
ikpy.link.OriginLink(),
link1,
link2,
link3,
link4,
])

coords = [-100,450,-290]
juntas = ["Origen: ","BP: ","High: ","Front: ","Bicep: "]
ct = 0

angulos = my_chain.inverse_kinematics(coords)

for i in angulos:
    print(juntas[ct] + str(math.degrees(i)))
    ct += 1


ax = matplotlib.pyplot.figure().add_subplot(111, projection='3d')

my_chain.plot(my_chain.inverse_kinematics(coords), ax)
matplotlib.pyplot.show()