from graph import GraphStruct
from itertools import groupby
from more_itertools import pairwise
from collections import Counter
import itertools
from log_file import LogFile
from pathlib import Path


def discover_process_main(log_path=Path,
                          out_path=Path,
                          case_column=None,
                          activity_column=None,
                          start_column=None,
                          eps=0.2,
                          filter_threshold=20):

    graph = GraphStruct()

    log = LogFile(log_path=log_path, case_column=case_column,
                  activity_column=activity_column, start_column=start_column)

    dfg, traces = log.get_dfg_and_traces()
    graph.dfg = dfg
    graph.traces = traces

    graph.set_start_and_end_node()

    totals = Counter(i for i in list(itertools.chain.from_iterable(traces)))
    graph.ev_counter = totals

    graph.prune_dfg(eps)

    graph.better_filter_edges(filter_threshold, graph.start_node, graph.end_node)

    graph.filtered_edges = [(event, s) for (event, successors) in graph.dfg.items() for s in successors.keys()]

    graph.splits_discovery()

    graph.discover_joins()

    graph.bpmn.make_networkx_graph(output_path=str(out_path))

    max_e = 0
    for el in graph.dfg.values():
        for e in el.values():
            if e > max_e:
                max_e = e
    return max_e

# log_file = Path("logs/article.csv")
# out_path = Path("cache")
# case_column='Case ID'
# activity_column='Activity'
# start_column='Start Timestamp'
#
# discover_process_main(log_path=log_file, out_path=out_path, case_column=case_column,
#                       activity_column=activity_column, start_column=start_column)
