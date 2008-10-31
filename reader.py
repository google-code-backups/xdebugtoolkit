import sys
import pydot

class Entry:

    def __init__(self):
        self.fn = None
        self.fl = None
        self.selfTime = None
        self.calls = []
        self.summary = None

class Call:

    def __init__(self):
        self.cfn = None
        self.position = None
        self.inclusiveTime = None

class Node:

    def __init__(self):
        self.fn = None
        self.fl = None
        self.calls = []
        self.selfTime = None
        self.inclusiveTime = None

class XdebugCachegrindFsaParser:
    """
    A low-level lexer
    """

    # header states
    # -2 got eof or fl, finish parsing
    # -1 error, finish parsing
    # 0 start
    # 1 got version, expecting cmd
    # 2 got cmd, expecting part
    # 3 gor part, expecting events
    # 4 got events, expecting fl or eof
    header_fsm = {
        #    0   1   2   3   4
        0: [ 1, -1, -1, -1, -1], # version
        1: [-1,  2, -1, -1, -1], # cmd
        2: [-1, -1,  3, -1, -1], # part
        3: [-1, -1, -1,  4, -1], # events
        4: [-1, -1, -1, -1, -2], # fl
        5: [-1, -1, -1, -1, -2], # eof
    }

    # body states:
    # -2 got eof, finish parsing
    # -1 error, finish parsing
    # 0 got header line, expectine more header lines or fl or eof
    # 1 got fl, expecting fn
    # 2 got fn, expecting num or summary
    # 3 got num, expecting fl or cfn or eof
    # 4 got cfn, expecting calls
    # 5 got calls, expecting subcall num
    # 6 got subcall num, expecting fl or cfn or eof
    # 7 got summary, expecting num
    body_fsm = {
        #    0   1   2   3   4   5   6   7
        0: [ 0, -1, -1, -1, -1, -1, -1, -1], # header
        1: [ 1, -1, -1,  1, -1, -1,  1, -1], # fl
        2: [-1,  2, -1, -1, -1, -1, -1, -1], # fn
        3: [-1, -1,  3, -1, -1,  6, -1,  3], # num
        4: [-1, -1, -1,  4, -1, -1,  4, -1], # cfn
        5: [-1, -1, -1, -1,  5, -1, -1, -1], # calls
        6: [-1, -1,  7, -1, -1, -1, -1, -1], # summary
        7: [-2, -1, -1, -2, -1, -1, -2, -1], # eof
    }

    def __init__(self, filename):
        self.fh = file(filename, 'rU')
        self.fl_map = {}
        self.fl_inc = 1
        self.fn_map = {}
        self.fn_inc = 1

    def getHeader(self):
        self.fh.seek(0)

        state = 0;
        line_no = 0

        while True:
            token = None
            try:
                line = self.fh.next()
                line_no += 1
                if line == '\n':
                    continue
                if line == 'version: 0.9.6\n':
                    token = 0
                if line[0:5] == 'cmd: ':
                    token = 1
                if line == 'part: 1\n':
                    token = 2
                if line == 'events: Time\n':
                    token = 3
                if line[0:3] == 'fl=':
                    token = 4
            except StopIteration:
                token = 5

            try:
                state = self.header_fsm[token][state]
            except:
                state = -1

            if state == -2:
                break

            elif state == -1:
                raise Exception(line_no, line, token)

            elif state == 2:
                cmd = line[5:-1]

        return {
            'cmd': cmd,
        }

    def getBody(self):
        body = []

        self.getHeader()

        self.fh.seek(0)

        state = 0;
        line_no = 0

        total_self = 0
        total_calls = 0

        while True:
            token = None
            line = None
            try:
                line = self.fh.next()
                line_no += 1
                if line == '\n':
                    continue
                elif line[0].isdigit():
                    token = 3
                elif line[0:3] == 'fl=':
                    token = 1
                elif line[0:3] == 'fn=':
                    token = 2
                elif line[0:4] == 'cfn=':
                    token = 4
                elif line[0:6] == 'calls=':
                    token = 5
                elif line[0:9] == 'summary: ':
                    token = 6
                elif state == 0:
                    token = 0
            except StopIteration:
                token = 7

            try:
                state = self.body_fsm[token][state]
            except KeyError:
                state = -1

            if state == 1:
                fl = line[3:-1]
                if fl not in self.fl_map:
                    self.fl_map[fl] = self.fl_inc
                    self.fl_inc += 1

                # re-init entry
                entry = Entry()
                body.append(entry)

                entry.fl = self.fl_map[fl]

            elif state == 2:
                fn = line[3:-1]
                if fn not in self.fn_map:
                    self.fn_map[fn] = self.fn_inc
                    self.fn_inc += 1

                entry.fn = self.fn_map[fn]

            elif state == 3:
                position, time_taken = map(int, line.split(' '))
                total_self += time_taken
                if fn == '{main}':
                    total_calls += time_taken
                    total_self_before_summary = total_self

            elif state == 4:
                cfn = line[4:-1]
                if cfn not in self.fn_map:
                    self.fn_map[cfn] = self.fn_inc
                    self.fn_inc += 1

                # init call
                call = Call()
                entry.calls.append(call)

                call.cfn = self.fn_map[cfn]

            elif state == 5:
                calls = line[6:-1]

            elif state == 6:
                position, time_taken = map(int, line.split(' '))
                if fn == '{main}':
                    total_calls += time_taken

                # set call's time and position
                call.position = position
                call.inclusiveTime = time_taken

            elif state == 7:
                summary = int(line[9:-1])

            elif state == -2:
                break

            elif state == -1:
                raise Exception(line_no, line, token)

        print 'summary:    ', summary
        print 'total_self: ', total_self_before_summary
        print 'total_calls:', total_calls
        return body

class XdebugCachegrindTreeBuilder:
    """
    A tree builder class.
    """
    def __init__(self, parser):
        self.parser = parser

    def getTree(self):
        fl_map = self.parser.fl_map
        fl_rev = dict([(v, k) for k, v in fl_map.iteritems()])

        fn_map = self.parser.fn_map
        fn_rev = dict([(v, k) for k, v in fn_map.iteritems()])

        body = self.parser.getBody()

        nodes = []
        stack = []
        rootNode = Node()
        stack.append([0, -1])
        nodes.append(rootNode)
        i = len(body)
        while i >= 0:
            i -= 1
            node = Node()
            node.fn = body[i].fn
            node.fl = body[i].fl
            node_id = len(nodes)
            nodes.append(node)

            expected_calls = len(body[i].calls)

            # add node to it's parent
            nodes[stack[-1][0]].calls.append(node)

            # fill stack
            stack.append([node_id, expected_calls])

            # clean up stack
            j = len(stack) - 1
            while len(nodes[stack[j][0]].calls) == stack[j][1]:
                del(stack[j])
                j -= 1
        return rootNode

class dotBuilder:
    def getDot(self, tree):
	self.getDot(node)
        graph = pydot.Graph(rankdir='TB', ordering='out', graph_type='digraph')
        graph.set_edge_defaults(labelfontsize='12')
        graph.set_node_defaults(shape='box', style='filled')
        graph.add_node(pydot.Node('A'))
        graph.add_node(pydot.Node('B'))
	graph.add_edge(pydot.Edge('A', 'B'))
        return graph.to_string()

if __name__ == '__main__':
    parser = XdebugCachegrindFsaParser(sys.argv[1])
    tree = XdebugCachegrindTreeBuilder(parser)
    print tree.getTree()
    #print dotBuilder().getDot(1)