import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)#
import sys
import os
from sidfam import Automaton, AutoGroup
from sidfam.gallery import from_dataset, _from_dataset_topo, print_time
from sidfam.language import any_ip, Variable, no_guard, no_update, \
            no_require, Resource, src_ip, dst_ip, PacketClass, AddInfo
from pathlib import Path
from sys import argv, exit
print_time('program start: ')
topo, bandwidth_resource, packet_class_list, bandwidth_require, switch_class = \
    from_dataset(Path(argv[1]))
num_pkt = Variable()
counting=Variable()
bandwidth = Resource(shared=True)
guard_list = [
    no_guard,
    counting==1,
]
require_list=[no_require]
update_list=[
    no_update,
    num_pkt<<num_pkt+1
]
def main_automaton():
    auto = Automaton()
    auto._append_transition(0, 1, 0, 0, 0, 0)
    auto._append_transition(0, 2, 1, 0, 0, 0)
    auto._append_transition(0, 3, 1, 0, 1, 0)
    auto._append_transition(0, 4, 1, 0, 1, -1)
    auto._append_transition(1, 1, 0, 0, 0, 0)
    auto._append_transition(1, 2, 1, 0, 0, 0)
    auto._append_transition(1, 3, 1, 0, 1, 0)
    auto._append_transition(1, 4, 1, 0, 1, -1)
    auto._append_transition(2, 2, 0, 0, 0, 0)
    auto._append_transition(2, 3, 0, 0, 1, 0)
    auto._append_transition(2, 4, 0, 0, 1, -1)
    auto._append_transition(3, 3, 0, 0, 0, 0)
    auto._append_transition(3, 4, 0, 0, 0, -1)
    return auto

def simple_routing():
    auto = Automaton()
    auto._append_transition(0, 1, 0, 0, 0, 0)
    auto._append_transition(1, 1, 0, 0, 0, 0)
    auto._append_transition(1, 2, 0, 0, 0, -1)
    return auto

group = AutoGroup(packet_class_list, guard_list, require_list, update_list)
for i, packet_class in enumerate(packet_class_list):
    src_host, dst_host = packet_class._src_ip, packet_class._dst_ip
    src_switch, dst_switch = packet_class.endpoints()
    if src_host == argv[2] and dst_host == argv[3]:
        group._append_automaton \
                (main_automaton(), i, src_switch, dst_switch)
    else:
        group._append_automaton \
                (simple_routing(), i, src_switch, dst_switch)
print_time('finish create automaton group: ')
problem = group @ topo
print_time('finish searching path: ')
splited = problem.split()
print_time('finish spliting problem: ')
bandwidth.map = bandwidth_resource
state_class={counting:0,num_pkt:1}
recognise=0
if argv[4]=='1':
    recognise=1
target_flow=-1
for i,packet_class in enumerate(packet_class_list):
    if packet_class._src_ip==argv[2] and packet_class._dst_ip==argv[3]:
        target_flow=i
        break
addInfo=AddInfo(switch_class, recognise, state_class, \
        guard_list, update_list, target_flow)
rule=splited.solve(save=True,extra=addInfo)
print_time('problem solved: ')
print(rule)