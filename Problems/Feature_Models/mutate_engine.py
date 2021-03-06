from copy import deepcopy
from random import randint, shuffle


class mutateEngine(object):
    def __init__(self, feature_tree):
        self.ft = feature_tree
        self.fea_fulfill = [-1] * len(self.ft.features)
        self.con_fulfill = [0] * self.ft.get_cons_num()
        self.con_repo = deepcopy(self.ft.constraints)

    def refresh(self):
        self.fea_fulfill = [-1] * len(self.ft.features)
        self.con_fulfill = [0] * self.ft.get_cons_num()
        self.con_repo = deepcopy(self.ft.constraints)

    def getFulfill(self, node):
        index = self.ft.features.index(node)
        return self.fea_fulfill[index]

    def setFulfill(self, node, setting, checkConstraint=True):
        if not self.checkWhetherSet(node, setting): Exception('setting conflict')
        index = self.ft.features.index(node)
        self.fea_fulfill[index] = setting
        if checkConstraint:
            self.checkConstraints(node)

    @staticmethod
    def getShuffleList(l, cut='notset'):
        from copy import copy
        l2 = copy(l)
        shuffle(l2)
        if cut != 'notset':
            return l2[0:cut]
        else:
            return l2

    def checkConstraints(self, setted_node):
        me = self.getFulfill(setted_node)
        for i, con in enumerate(self.con_repo):
            if self.con_fulfill[i]: continue
            if setted_node.id not in con.literals: continue
            location = con.literals.index(setted_node.id)
            if con.li_pos[location] == me:
                self.con_fulfill[i] = 1
            else:
                con.literals.pop(location)
                con.li_pos.pop(location)
                if len(con.literals) == 0:
                    raise Exception('constraint fail!')

    def checkWhetherSet(self, node, want):
        a = self.getFulfill(node)
        if a == -1: return True  # not set before
        return a == want

    def mutateChild(self, node):
        me = self.getFulfill(node)
        if node.children == []: return
        if node.node_type == 'g':  # the current node is a group
            if not me:
                map(lambda x: self.setFulfill(x, 0), node.children)
            else:
                want = randint(node.g_d, node.g_u)
                exist_1 = len([c for c in node.children if self.getFulfill(c) == 1])
                want = want - exist_1
                if want < 0: raise Exception('group fail!')
                for i, c in enumerate(self.getShuffleList(node.children)):
                    self.setFulfill(c, int(i < want))
                    self.mutateChild(c)
            return
        if node.children[0].node_type == 'g':  # my child is a group-> just to set as me
            c = node.children[0]
            self.setFulfill(c, me, False)
            self.mutateChild(c)
            return
        # the current node is root, mandory or optional
        m_child = [c for c in node.children if c.node_type == 'm']
        o_child = [c for c in node.children if c.node_type == 'o']
        shuffle(m_child)
        shuffle(o_child)

        if me:
            for m in m_child:
                self.setFulfill(m, 1)
                self.mutateChild(m)
            for o in o_child:
                self.setFulfill(o, randint(0, 1))
                self.mutateChild(o)
        if not me:
            if len(m_child) == 0:
                for o in o_child:
                    self.setFulfill(o, 0)
                    self.mutateChild(o)
            else:
                self.setFulfill(m_child[0], 0)
                self.mutateChild(m_child[0])
                for other in m_child[1:] + o_child:
                    self.setFulfill(other, randint(0, 1))
                    self.mutateChild(other)
        return

    def findLevesFulfill(self, fulfill):
        r = []
        for x in self.ft.leaves:
            index = self.ft.features.index(x)
            r.append(fulfill[index])
        return r

    """
    Generate valid candidates with size equals given pop
    if returnFulfill is True,  then return a list--list[0] is fulfill lists; list[1] is same as upper introduction. Note: list[0][a] is matching list[1][a]
    if returnFulfill is False, then list[0] is None
    """

    def generate(self, pop=10, returnFulfill=False):
        i = 0
        fulfill2return = []
        while True:
            try:
                print ".",
                self.refresh()
                self.setFulfill(self.ft.root, 1)
                self.mutateChild(self.ft.root)
                fulfill2return.append(self.fea_fulfill)
                i = i + 1
                if i >= pop:
                    leaves2return = [self.findLevesFulfill(r) for r in fulfill2return]
                    if returnFulfill:
                        return fulfill2return, leaves2return
                    else:
                        return None, leaves2return
            except:
                # import pdb
                # pdb.set_trace()
                pass


def comparePerformance():
    for name in ['cellphone', 'eshop', 'webportal', 'EIS']:
        m = FTModel('../feature_tree_data/' + name + '.xml', name, name + '.cost')
        m.printModelInfo()
        engine = mutateEngine(m.ft)
        start_time = time.time()
        engine.setFulfill(m.ft.root, 1)
        engine.generate(10)
        print("--- %s seconds --- for 10 by new mutate engine" % (time.time() - start_time))
        start_time = time.time()
        for i in range(10):
            m.genRandomCan(guranteeOK=True)
        print("--- %s seconds --- for 10 by origin mutate engine" % (time.time() - start_time))


def unitTest():
    from feature_model import FeatureTreeModel
    m = FeatureTreeModel("Web_Portal")
    m.printModelInfo()
    engine = mutateEngine(m.ft)
    q = engine.generate(10, True)
    print q


if __name__ == '__main__':
    # comparePerformance()
    unitTest()
