#
import operator


class PacketClass:
    def __init__(self, src_ip, dst_ip, src_switch, dst_switch):
        self._src_ip = src_ip
        self._dst_ip = dst_ip
        self._src_switch = src_switch
        self._dst_switch = dst_switch

    def endpoints(self):
        return self._src_switch, self._dst_switch
class AddInfo:
    def __init__(self, switch_class, recognise, state_class, guard_list, update_list,target_flow):
        self._switch_class=switch_class
        self._recognise=recognise
        self._state_class=state_class
        self._guard_list=guard_list
        self._update_list=update_list
        self._target_flow=target_flow

class IPConstr:
    def __and__(self, other):
        return AndIPConstr(self, other)

    def __contains__(self, packet_class):
        raise NotImplementedError()


class AnyIP(IPConstr):
    def __contains__(self, _packet_class):
        return True

any_ip = AnyIP()


class SrcIPConstr(IPConstr):
    def __init__(self, op, rhs):
        self._op = op
        self._rhs = rhs

    def __contains__(self, packet_class):
        # print(packet_class._src_ip, self._rhs)
        return self._op(packet_class._src_ip, self._rhs)


class DstIPConstr(IPConstr):
    def __init__(self, op, rhs):
        self._op = op
        self._rhs = rhs

    def __contains__(self, packet_class):
        return self._op(packet_class._dst_ip, self._rhs)


class AndIPConstr(IPConstr):
    def __init__(self, constr1, constr2):
        self._constr1 = constr1
        self._constr2 = constr2

    def __contains__(self, packet_class):
        return packet_class in self._constr1 and packet_class in self._constr2


class SrcIPLHS:
    def __eq__(self, rhs):
        return SrcIPConstr(operator.eq, rhs)

src_ip = SrcIPLHS()


class DstIPLHS:
    def __eq__(self, rhs):
        return DstIPConstr(operator.eq, rhs)

dst_ip = DstIPLHS()


class DepElement:
    pass


class CombinedDep(DepElement):
    def __init__(self, v1, v2):
        self.dep = set()
        if isinstance(v1, DepElement):
            self.dep |= v1.dep
        if isinstance(v2, DepElement):
            self.dep |= v2.dep


class Expr(CombinedDep):
    def __lt__(self, other):
        return GuardUpdate(self, other)

    def __eq__(self, other):
        return GuardUpdate(self, other)

    def __lshift__(self, other):
        return GuardUpdate(self, other)


class Variable(Expr):
    def __init__(self):
        self.dep = {self}

    def __add__(self, other):
        return Expr(self, other)

    def __sub__(self, other):
        return Expr(self, other)

    def __hash__(self):
        return id(self)


class GuardUpdate(CombinedDep):
    def __and__(self, other):
        return GuardUpdate(self, other)


no_guard = no_update = GuardUpdate(None, None)


class Resource:
    def __init__(self, shared):
        self.shared = shared
        self.map = None

    def __mul__(self, other):
        return Require({self: other})


class Require:
    def __init__(self, res_map):
        self.res_map = res_map

    def __add__(self, other):
        res_map = dict(self.res_map)
        for res, req in other.res_map.items():
            if res not in res_map:
                res_map[res] = req
            else:
                res_map[res] += req
        return Require(res_map)


no_require = Require({})
