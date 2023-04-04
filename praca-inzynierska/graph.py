from copy import deepcopy

# import pandas as pd
from itertools import groupby
from more_itertools import pairwise
from collections import Counter
import pylab

from queue import PriorityQueue
import networkx as nx
from bpmn import BPMN
from join_miner import JoinMiner


# def _get_dfs(csv_name) -> dict:
#     df = pd.read_csv(csv_name)
#     df['start'] = pd.to_datetime(df['Start Timestamp'])
#     df['complete'] = pd.to_datetime(df['Complete Timestamp'])
#     df['duration'] = df['complete'] - df['start']
#     dfs = df[['Case ID', 'Activity', 'start']]
#     return dfs


class GraphStruct:
    def __init__(self):
        # self.data_frame = _get_dfs(csv_name)  # dataframe that stores Case ID Activity and Start Timestamp
        # self.ev_counter = self.data_frame.Activity.value_counts()  # the number of node occurrences
        self.ev_counter = None
        self.start_node = None
        self.end_node = None
        # todo ev_counter narazie jest lekko useless
        # self.dfg = self.get_dfg()  # contains direct edge value from node a to b
        self.dfg = None
        self.traces = None
        self.concurrent_tasks = None
        self.short_loop_frequency = dict()
        self.bpmn = None
        self.filtered_edges = None

    def get_dfg(self):
        # todo check if methods are correct f.e concurrency
        traces_count = self.get_traces_count()
        dfg = dict()
        ev_start_set = set()
        ev_end_set = set()
        for trace, count in traces_count.items():
            if trace[0] not in ev_start_set:
                ev_start_set.add(trace[0])
            if trace[-1] not in ev_end_set:
                ev_end_set.add(trace[-1])
            for ev_i, ev_j in pairwise(trace):  # ABCD -> AB BC CD
                if ev_i not in dfg.keys():
                    dfg[ev_i] = Counter()
                dfg[ev_i][ev_j] += count
        return dfg

    def get_ev_start_and_end_sets(self):
        traces_count = self.get_traces_count()
        ev_start_set = set()
        ev_end_set = set()
        for trace, count in traces_count.items():
            if trace[0] not in ev_start_set:
                ev_start_set.add(trace[0])
            if trace[-1] not in ev_end_set:
                ev_end_set.add(trace[-1])
        return ev_start_set, ev_end_set

    def get_traces_count(self):
        traces = self.data_frame.sort_values(by=['Case ID', 'start']).groupby(['Case ID']).agg(
            {'Activity': lambda x: tuple(x)})
        traces_count = traces.groupby("Activity")["Activity"].count()
        return traces_count

    def get_trace_count(self, a, b):
        if a in self.dfg and b in self.dfg[a][b]:
            return self.dfg[a][b]
        else:
            raise ValueError("no trace from", a, " to ", b)

    def set_start_and_end_node(self):
        trace = self.traces[0]
        self.start_node = trace[0]
        self.end_node = trace[-1]

    def delete_edge(self, a, b):
        if a in self.dfg and b in self.dfg[a]:
            self.dfg[a].pop(b)

    def get_short_loop_frequency(self):
        short_loop_frequency = dict()
        for trace in self.traces:
            for a, b, c in zip(trace[0::], trace[1::], trace[2::]):
                if a == c and a != b:
                    if not (a, b) in short_loop_frequency:
                        short_loop_frequency[(a, b)] = 0
                    # if not (b, a) in short_loop_frequency:
                    #     short_loop_frequency[(b, a)] = 0
                    short_loop_frequency[(a, b)] += 1
                    # short_loop_frequency[(b, a)] += 1
        self.short_loop_frequency = short_loop_frequency
        # print("ASDASDADSADS")
        # print(short_loop_frequency)
        return short_loop_frequency

    def delete_short_loops(self):
        short_loops = []

        self.get_short_loop_frequency()

        for key in self.short_loop_frequency:
            a, b = key
            r_key = (b, a)
            if self.short_loop_frequency[key] + self.short_loop_frequency[r_key] != 0:
                if a not in self.dfg[a] and b not in self.dfg[b]:
                    short_loops.append(key)
        for u, v in short_loops:
            self.delete_edge(u, v)

    def concurrency_discovery(self, eps):
        self.concurrent_tasks = set()
        to_delete = []
        print("dfg")
        print(self.dfg)
        print("slf")
        print(self.short_loop_frequency)
        for event, successors in self.dfg.items():
            for successor, cnt in successors.items():
                if successor in self.dfg and event in self.dfg[successor]:
                    if self.dfg[event][successor] > 0 and self.dfg[successor][event] > 0:
                        if (event, successor) in self.short_loop_frequency.keys():
                            if self.short_loop_frequency[(event, successor)] + self.short_loop_frequency[
                                (successor, event)] != 0:
                                continue
                        metric = abs((self.dfg[event][successor] - self.dfg[successor][event])) / (self.dfg[event][
                                                                                                       successor] +
                                                                                                   self.dfg[successor][
                                                                                                       event])
                        if metric <= eps:
                            self.concurrent_tasks.add((event, successor))
                            to_delete.append(
                                [event, successor])  # tylko w jedna strone bo i tak potem wchodzimy w odwrotna krawedz
                        else:
                            if self.dfg[event][successor] < self.dfg[successor][event]:
                                to_delete.append([event, successor])
                            else:
                                to_delete.append([successor, event])
        for u, v in to_delete:
            self.delete_edge(u, v)
        print("todelete")
        print(to_delete)

    def prune_dfg(self, eps):
        self.delete_short_loops()
        self.concurrency_discovery(eps)

    def get_incoming_edges_count(self):
        res = dict()
        for event, successors in self.dfg.items():
            for successor, cnt in successors.items():
                if successor not in res.keys():
                    res[successor] = 0
                res[successor] += 1
        return res

    def get_all_edges_values(self) -> list:
        res = []
        for event, successors in self.dfg.items():
            for successor, cnt in successors.items():
                res.append(cnt)
        return res

    def edge_is_necessary(self, a, b):
        incoming_edge_counter = self.get_incoming_edges_count()
        if a in self.dfg:
            if len(self.dfg[a]) == 1:
                return True
        if b in incoming_edge_counter:
            if incoming_edge_counter[b] == 1:
                return True
        return False

    def node_is_necessary(self, u):
        incoming_edge_counter = self.get_incoming_edges_count()
        flag1 = False
        flag2 = False

        for event, successors in self.dfg.items():
            if u in successors:
                if len(self.dfg[event]) == 1:
                    flag1 = True
        if u in self.dfg:
            for v in self.dfg[u]:
                if incoming_edge_counter[v] == 1:
                    flag2 = True
        if flag1 and flag2:
            return False
        return True

    def get_best_incoming(self, i):
        q = PriorityQueue()
        U = set()
        E = dict()
        Cf = dict()
        for e in self.ev_counter.keys():
            E[e] = 0
            Cf[e] = 0
            U.add(e)

        U.remove(i)
        Cf[i] = 9999

        q.put((0, i))
        while not q.empty():
            val, p = q.get()
            if p in self.dfg.keys():
                for n in self.dfg[p].keys():
                    f = self.dfg[p][n]
                    c_max = min(Cf[p], f)
                    if c_max > Cf[n]:
                        Cf[n] = c_max
                        E[n] = (p, n)
                        isInqueues = False
                        if n in U:
                            isInqueues = True
                        for (_, x) in q.queue:
                            if x == n:
                                isInqueues = True
                        if not isInqueues:
                            q.put((-f, n))
                    if n in U:
                        U.remove(n)
                        q.put((-f, n))
        return E

    def get_best_outgoing(self, o):
        q = PriorityQueue()
        U = set()
        E = dict()
        C = dict()
        for e in self.ev_counter.keys():
            E[e] = 0
            C[e] = 0
        C[o] = 9999

        q.put((0, o))
        while not q.empty():
            val, n = q.get()
            for event, successors in self.dfg.items():
                for successor, cnt in successors.items():
                    if successor == n:
                        p = event
                        f = cnt
                        c_max = min(C[n], f)
                        if c_max > C[p]:
                            C[p] = c_max
                            E[p] = (p, n)
                            isInqueues = False
                            if p in U:
                                isInqueues = True
                            for (_, x) in q.queue:
                                if x == p:
                                    isInqueues = True
                            if isInqueues == False:
                                q.put((-f, p))
                        if p in U:
                            U.remove(p)
                            q.put((-f, p))
        return E

    def get_best_incoming_and_outgoing_edges(self, i, o):
        return [self.get_best_incoming(i), self.get_best_outgoing(o)]

    def better_filter_edges(self, threshold, i, o):
        Ei, Eo = self.get_best_incoming_and_outgoing_edges(i, o)
        dfg_copy = deepcopy(self.dfg)
        for event, successors in dfg_copy.items():
            for successor in successors.keys():
                cnt = self.dfg[event][successor]
                if cnt < threshold and not \
                        self.edge_is_necessary(event, successor):
                    if Ei[successor] != (event, successor) \
                            and Eo[event] != (event, successor):
                        self.dfg[event].pop(successor)

    def splits_discovery(self):
        l = list(self.dfg.keys())
        l.append(self.end_node)
        self.bpmn = BPMN(i=self.start_node, o=self.end_node, T=set(l))
        tasks_for_discovery = [(event, successors) for event, successors in self.dfg.items() if successors is not None]
        if len(tasks_for_discovery) == 0:
            self.bpmn.edges = self.filtered_edges
            return self
        for event, successors in tasks_for_discovery:
            K = set([val for val in successors])
            cover = dict([(val, None) for val in K])
            future = dict([(val, None) for val in K])

            for s1 in K:
                cover_s1 = set()
                cover_s1.add(s1)
                future_s1 = set()
                for s2 in K:
                    if s2 != s1 and (s1, s2) in self.concurrent_tasks:
                        future_s1.add(s2)
                cover[s1] = cover_s1
                future[s1] = future_s1

            self.bpmn.edges = self.bpmn.edges + [(event, s) for (event, successors) in self.dfg.items() for s in
                                                 successors.keys() if event not in K]
            while len(K) > 1:
                K, cover, future = self.bpmn.discover_XOR_splits(K, cover, future, event)
                K, cover, future = self.bpmn.discover_AND_splits(K, cover, future, event)

        for e in self.bpmn.to_remove:
            self.bpmn.edges = list(filter(e.__ne__, self.bpmn.edges))

    def prepare_edges_to_bpmn(self, edges):

        # print(edges)

        edges_keys = set([part[0] for part in edges] + [part[1] for part in edges])
        edge_dict = {}
        for part in edges_keys:
            new_part = part
            if not part[-1].isdigit():
                if part.startswith('xor'):
                    if any([part.endswith(i) for i in self.bpmn.T]):
                        new_part = f"xor{len(self.bpmn.xor_gateways) + 1}"
                    self.bpmn.xor_gateways.append(new_part)
                if part.startswith('or'):
                    if any([part.endswith(i) for i in self.bpmn.T]):
                        new_part = f"or{len(self.bpmn.or_gateways) + 1}"
                    self.bpmn.or_gateways.append(new_part)
                if part.startswith('and'):
                    if any([part.endswith(i) for i in self.bpmn.T]):
                        new_part = f"and{len(self.bpmn.and_gateways) + 1}"
                    self.bpmn.and_gateways.append(new_part)

            edge_dict[part] = new_part
        return edge_dict

    def discover_joins(self):
        if len(self.bpmn.xor_gateways + self.bpmn.and_gateways + self.bpmn.or_gateways) > 0:
            # print("FORMAT")
            # print(self.bpmn.format())
            rpst = JoinMiner()
            # print()
            # print("RPST")
            # print(rpst.call(self.bpmn.format()))
            # print(f"BPMN.FORMAT: {self.bpmn.format()}")
            # print("\n")
            edges = rpst.call(self.bpmn.format())

            edge_dict = self.prepare_edges_to_bpmn(edges)
            self.bpmn.edges = [(edge_dict[start], edge_dict[end]) for (start, end) in edges]

    def visualize(self):
        G = nx.DiGraph()
        for event, successors in self.dfg.items():
            for successor in successors.keys():
                G.add_edge(event, successor)

        ev_start, ev_end = self.get_ev_start_and_end_sets()
        for ev in ev_start:
            if G.has_node(ev):
                G.add_edge('start', ev)

        for ev in ev_end:
            if G.has_node(ev):
                G.add_edge(ev, 'end')

        nx.draw_spring(G, with_labels=True)
        pylab.show()

    def visualize_from_edges(self):
        G = nx.DiGraph()
        for edge in self.bpmn.edges:
            G.add_edge(edge[0], edge[1])

        G.add_edge('start', self.start_node)
        G.add_edge(self.end_node, 'end')

        nx.draw_spring(G, with_labels=True)
        pylab.show()
