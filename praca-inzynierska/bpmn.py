# import bpmn_python as diagram
# import bpmn_python as layouter
import bpmn_python.bpmn_diagram_layouter as layouter
import bpmn_python.bpmn_diagram_rep as diagram
from pathlib import Path


class BPMN:
    # i o -> start end T -> non empty set of task G -> union of the set of AND XOR OR Em -> set of edges g ∈ G -> g
    # is a split gateway if there is one outgoing edge or join gataway if there is more then one incoming edge
    def __init__(self, i, o, T):
        self.i = i
        self.o = o
        self.T = T
        self.and_gateways = []
        self.xor_gateways = []
        self.or_gateways = []
        self.edges = []
        self.to_remove = []

    def add_gateway(self, gate, _set, event, cover, future, cover_u, future_u, K, gateway_list):
        gateway_list.append(gate)
        self.edges += [(gate, s) for s in _set]
        self.edges.append((event, gate))
        # print("HALO")
        # print([(event, s) for s in _set])
        # print(self.edges)
        for s in _set:
            self.edges.remove((event, s))
            self.to_remove.append((event, s))
        # print("USUNIETO?")
        # print(self.edges)

        for sx in _set:
            cover[sx] = None
            future[sx] = None
        cover[gate] = cover_u
        future[gate] = future_u
        K.add(gate)
        K.difference_update(_set)

    def discover_XOR_splits(self, K, cover, future, event):
        # print(cover)
        x = True
        while x:
            set_X = set()
            for successor in K:
                cover_u: set = cover[successor]
                future_u: set = future[successor]
                future_s1: set = future[successor]

                for successor2 in K:
                    future_s2: set = future[successor2]
                    if future_s1 == future_s2 and successor2 != successor:
                        set_X.add(successor2)
                        cover_u = cover_u.union(cover[successor2])

                if len(set_X) != 0:
                    set_X.add(successor)
                    break
            if len(set_X) != 0:
                gate_xor = f"xor{len(self.xor_gateways)+1}"
                self.add_gateway(gate=gate_xor, _set=set_X, event=event, cover=cover, future=future, cover_u=cover_u,
                                 future_u=future_u, K=K, gateway_list=self.xor_gateways)

            if len(set_X) == 0:
                x = False

        return K, cover, future

    def discover_AND_splits(self, K, cover, future, event):
        for successor in K:
            set_A = set()
            cover_u: set = cover[successor]
            future_u: set = future[successor]
            cf_s1: set = future[successor].union(cover[successor])

            for successor2 in K:
                cf_s2: set = future[successor2].union(cover[successor2])
                if cf_s1 == cf_s2 and successor2 != successor:
                    set_A.add(successor2)
                    cover_u = cover_u.union(cover[successor2])
                    future_u = future_u.intersection(future[successor2])

            if len(set_A) != 0:
                set_A.add(successor)
                break

        if len(set_A) != 0:
            gate_and = f"and{len(self.and_gateways)+1}"
            self.add_gateway(gate=gate_and, _set=set_A, event=event, cover=cover, future=future, cover_u=cover_u,
                             future_u=future_u, K=K, gateway_list=self.and_gateways)

        return K, cover, future

    def format(self):
        result = {}
        for edge in self.edges:
            source = edge[0]
            target = edge[1]
            if source not in result:
                result[source] = [target]
            else:
                if target not in result[source]:
                    result[source].append(target)

        return result

    def make_networkx_graph(self, output_path=Path):
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.create_new_diagram_graph(diagram_name="diagram1")
        process_id = bpmn_graph.add_process_to_diagram()

        [start_id, _] = bpmn_graph.add_start_event_to_diagram(process_id, start_event_name="start_event")
        [end_id, _] = bpmn_graph.add_end_event_to_diagram(process_id, end_event_name="end_event")

        # dodajemy node'y
        nodes_and_gates = {}
        #print(self.T)
        #print(f"self.edges: {self.edges}")
        for v in self.T:
            [nodes_and_gates[v], _] = bpmn_graph.add_task_to_diagram(process_id, task_name=v)

        # and
        for a in self.and_gateways:
            [nodes_and_gates[a], _] = bpmn_graph.add_parallel_gateway_to_diagram(process_id, gateway_name=a)

        # or
        for o in self.or_gateways:
            [nodes_and_gates[o], _] = bpmn_graph.add_inclusive_gateway_to_diagram(process_id, gateway_name=o)

        # xor
        for x in self.xor_gateways:
            [nodes_and_gates[x], _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id, gateway_name=x)

        bpmn_graph.add_sequence_flow_to_diagram(process_id, start_id, nodes_and_gates[self.i])


        self.edges = [x for x in self.edges if (x[0] in self.T or x[0] in self.and_gateways or x[0] in self.or_gateways or x[0] in self.xor_gateways) \
                      and (x[1] in self.T or x[1] in self.and_gateways or x[1] in self.or_gateways or x[1] in self.xor_gateways) ]


        # print(f"SELF.EDGES: {self.edges}")
        # print(f"nodes_and_edges.keys(): {nodes_and_gates.keys()}")
        for trace in self.edges:
            bpmn_graph.add_sequence_flow_to_diagram(process_id, nodes_and_gates[trace[0]], nodes_and_gates[trace[1]])

        bpmn_graph.add_sequence_flow_to_diagram(process_id, nodes_and_gates[self.o], end_id)


        # [start_id, _] = bpmn_graph.add_start_event_to_diagram(process_id, start_event_name="start_event")
        # [task1_id, _] = bpmn_graph.add_task_to_diagram(process_id, task_name="First task")
        # [subprocess1_id, _] = bpmn_graph.add_subprocess_to_diagram(process_id, subprocess_name="Subprocess")
        # bpmn_graph.add_sequence_flow_to_diagram(process_id, start_id, task1_id)
        # bpmn_graph.add_sequence_flow_to_diagram(process_id, task1_id, subprocess1_id)
        #
        #
        # [parallel_gate_fork_id, _] = bpmn_graph.add_parallel_gateway_to_diagram(process_id,
        #                                                                         gateway_name="parallel_gate_fork")
        # [task1_par_id, _] = bpmn_graph.add_task_to_diagram(process_id, task_name="task1_par")
        # [task2_par_id, _] = bpmn_graph.add_task_to_diagram(process_id, task_name="task2_par")
        # [parallel_gate_join_id, _] = bpmn_graph.add_parallel_gateway_to_diagram(process_id,
        #                                                                         gateway_name="parallel_gate_join")
        #
        # bpmn_graph.add_sequence_flow_to_diagram(process_id, subprocess1_id, parallel_gate_fork_id)
        # bpmn_graph.add_sequence_flow_to_diagram(process_id, parallel_gate_fork_id, task1_par_id)
        # bpmn_graph.add_sequence_flow_to_diagram(process_id, parallel_gate_fork_id, task2_par_id)
        # bpmn_graph.add_sequence_flow_to_diagram(process_id, task1_par_id, parallel_gate_join_id)
        # bpmn_graph.add_sequence_flow_to_diagram(process_id, task2_par_id, parallel_gate_join_id)
        #
        # [exclusive_gate_fork_id, _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id,
        #                                                                           gateway_name="exclusive_gate_fork")
        # [task1_ex_id, _] = bpmn_graph.add_task_to_diagram(process_id, task_name="task1_ex")
        # [task2_ex_id, _] = bpmn_graph.add_task_to_diagram(process_id, task_name="task2_ex")
        # [exclusive_gate_join_id, _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id,
        #                                                                           gateway_name="exclusive_gate_join")
        #
        # bpmn_graph.add_sequence_flow_to_diagram(process_id, parallel_gate_join_id, exclusive_gate_fork_id)
        # bpmn_graph.add_sequence_flow_to_diagram(process_id, exclusive_gate_fork_id, task1_ex_id)
        # bpmn_graph.add_sequence_flow_to_diagram(process_id, exclusive_gate_fork_id, task2_ex_id)
        # bpmn_graph.add_sequence_flow_to_diagram(process_id, task1_ex_id, exclusive_gate_join_id)
        # bpmn_graph.add_sequence_flow_to_diagram(process_id, task2_ex_id, exclusive_gate_join_id)
        #
        # [inclusive_gate_fork_id, _] = bpmn_graph.add_inclusive_gateway_to_diagram(process_id,
        #                                                                           gateway_name="inclusive_gate_fork")
        # [task1_in_id, _] = bpmn_graph.add_task_to_diagram(process_id, task_name="task1_in")
        # [task2_in_id, _] = bpmn_graph.add_task_to_diagram(process_id, task_name="task2_in")
        # [inclusive_gate_join_id, _] = bpmn_graph.add_inclusive_gateway_to_diagram(process_id,
        #                                                                           gateway_name="inclusive_gate_join")
        #
        # bpmn_graph.add_sequence_flow_to_diagram(process_id, exclusive_gate_join_id, inclusive_gate_fork_id)
        # bpmn_graph.add_sequence_flow_to_diagram(process_id, inclusive_gate_fork_id, task1_in_id)
        # bpmn_graph.add_sequence_flow_to_diagram(process_id, inclusive_gate_fork_id, task2_in_id)
        # bpmn_graph.add_sequence_flow_to_diagram(process_id, task1_in_id, inclusive_gate_join_id)
        # bpmn_graph.add_sequence_flow_to_diagram(process_id, task2_in_id, inclusive_gate_join_id)
        #
        # [end_id, _] = bpmn_graph.add_end_event_to_diagram(process_id, end_event_name="end_event")
        # bpmn_graph.add_sequence_flow_to_diagram(process_id, inclusive_gate_join_id, end_id)

        layouter.generate_layout(bpmn_graph)
        # bpmn_graph.export_xml_file_no_di("./", "manually-generated-complex-output.xml")
        # bpmn_graph.export_xml_file("./", "manually-generated-complex-output2.xml")

        bpmn_graph.export_xml_file(output_path, "\manually-generated-complex-output.xml")