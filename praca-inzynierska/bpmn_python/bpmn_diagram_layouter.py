# coding=utf-8
"""
Package with BPMNDiagramGraph - graph representation of BPMN diagram
"""
import copy

import bpmn_python.bpmn_python_consts as consts
import bpmn_python.grid_cell_class as cell_class


def generate_layout(bpmn_graph, symmetric=False):
    """
    :param bpmn_graph: an instance of BPMNDiagramGraph class.
    """

    classification = generate_elements_clasification(bpmn_graph)

    nodes_copy_reversed = copy.deepcopy(classification[0])
    flows_copy_reversed = copy.deepcopy(bpmn_graph.sequence_flows)

    detach_edges_from_boundary_events(nodes_copy_reversed, flows_copy_reversed)

    start_nodes = []
    for node in classification[0]:
        if "Start Event" in node['classification']:
            start_nodes.append(node)

    back_edges_ids = []

    reversed_anything = True
    while reversed_anything:
        discovered = []
        finished = []
        iteration_back_edges_ids = []
        for start_node in start_nodes:
            classify_edges(start_node, flows_copy_reversed, nodes_copy_reversed, discovered,
                           finished, iteration_back_edges_ids)
        reverse_flows(flows_copy_reversed, nodes_copy_reversed,
                      iteration_back_edges_ids)
        if iteration_back_edges_ids:
            reversed_anything = True
            for back_edge_id in iteration_back_edges_ids:
                if back_edge_id in back_edges_ids:
                    back_edges_ids.remove(back_edge_id)
                else:
                    back_edges_ids.append(back_edge_id)
        else:
            reversed_anything = False

    (sorted_nodes_with_classification) = topological_sort(
        flows_copy_reversed, nodes_copy_reversed)

    grid = grid_layout(flows_copy_reversed,
                       sorted_nodes_with_classification, bpmn_graph, back_edges_ids, symmetric)

    set_coordinates_for_nodes(bpmn_graph, grid)
    set_flows_waypoints(bpmn_graph, back_edges_ids,
                        sorted_nodes_with_classification)


def generate_elements_clasification(bpmn_graph):
    """
    :param bpmn_graph:
    :return:
    """
    nodes_classification = []
    node_param_name = "node"
    flow_param_name = "flow"
    classification_param_name = "classification"

    classification_element = "Element"
    classification_boundary = "Boundary"
    classification_join = "Join"
    classification_split = "Split"
    classification_start_event = "Start Event"
    classification_end_event = "End Event"

    task_list = bpmn_graph.get_nodes(consts.Consts.task)
    for element in task_list:
        tmp = [classification_element]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element,
                                  classification_param_name: tmp}]

    subprocess_list = bpmn_graph.get_nodes(consts.Consts.subprocess)
    for element in subprocess_list:
        tmp = [classification_element]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element,
                                  classification_param_name: tmp}]

    complex_gateway_list = bpmn_graph.get_nodes(consts.Consts.complex_gateway)
    for element in complex_gateway_list:
        tmp = [classification_element]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element,
                                  classification_param_name: tmp}]

    event_based_gateway_list = bpmn_graph.get_nodes(
        consts.Consts.event_based_gateway)
    for element in event_based_gateway_list:
        tmp = [classification_element]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element,
                                  classification_param_name: tmp}]

    inclusive_gateway_list = bpmn_graph.get_nodes(
        consts.Consts.inclusive_gateway)
    for element in inclusive_gateway_list:
        tmp = [classification_element]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element,
                                  classification_param_name: tmp}]

    exclusive_gateway_list = bpmn_graph.get_nodes(
        consts.Consts.exclusive_gateway)
    for element in exclusive_gateway_list:
        tmp = [classification_element]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element,
                                  classification_param_name: tmp}]

    parallel_gateway_list = bpmn_graph.get_nodes(
        consts.Consts.parallel_gateway)
    for element in parallel_gateway_list:
        tmp = [classification_element]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element,
                                  classification_param_name: tmp}]

    start_event_list = bpmn_graph.get_nodes(consts.Consts.start_event)
    for element in start_event_list:
        tmp = [classification_element, classification_start_event]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element,
                                  classification_param_name: tmp}]

    intermediate_catch_event_list = bpmn_graph.get_nodes(
        consts.Consts.intermediate_catch_event)
    for element in intermediate_catch_event_list:
        tmp = [classification_element]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element,
                                  classification_param_name: tmp}]

    end_event_list = bpmn_graph.get_nodes(consts.Consts.end_event)
    for element in end_event_list:
        tmp = [classification_element, classification_end_event]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element,
                                  classification_param_name: tmp}]

    intermediate_throw_event_list = bpmn_graph.get_nodes(
        consts.Consts.intermediate_throw_event)
    for element in intermediate_throw_event_list:
        tmp = [classification_element]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element,
                                  classification_param_name: tmp}]

    boundary_event_list = bpmn_graph.get_nodes(consts.Consts.boundary_event)
    for element in boundary_event_list:
        nodes_classification += [{node_param_name: element,
                                  classification_param_name: [classification_boundary]}]

    flows_classification = []
    flows_list = bpmn_graph.get_flows()
    for flow in flows_list:
        flows_classification += [{flow_param_name: flow,
                                  classification_param_name: ["Flow"]}]

    return nodes_classification, flows_classification


def classify_edges(start_node, flows, nodes, discovered, finished, back_edges_ids):
    discovered.append(start_node[consts.Consts.node][0])
    reversed = False

    start_node_outflows = start_node[consts.Consts.node][1][consts.Consts.outgoing_flow]
    for edge_id in start_node_outflows:
        edge = flows[edge_id]
        successor_id = edge[consts.Consts.target_ref]
        if successor_id not in discovered:
            successor = next(
                node for node in nodes if node[consts.Consts.node][0] == successor_id)
            reversed = classify_edges(
                successor, flows, nodes, discovered, finished, back_edges_ids)
            if reversed:
                start_node_out_count = len(start_node_outflows)
                for back_edge_id in back_edges_ids:
                    if back_edge_id in start_node_outflows:
                        start_node_out_count -= 1
                if start_node_out_count > 1:
                    reversed = False
                back_edges_ids.append(edge_id)
        elif successor_id not in finished:
            back_edges_ids.append(edge_id)
            reversed = True
            start_node_out_count = len(start_node_outflows)
            for back_edge_id in back_edges_ids:
                if back_edge_id in start_node_outflows:
                    start_node_out_count -= 1
            # start_node_out_count + 1 > 1 because one edge (main loop) is important
            if start_node_out_count > 0:
                reversed = False
    finished.append(start_node[consts.Consts.node][0])
    return reversed


def detach_edges_from_boundary_events(nodes_copy_reversed, flows_copy_reversed):
    pass


def topological_sort(flows, tmp_nodes_with_classification):
    """
    :return:
    """
    node_param_name = "node"
    attached_param_name = 'attachedToRef'
    classification_param_name = "classification"

    sorted_nodes_with_classification = []
    no_incoming_flow_nodes = []

    boundary_events = []
    for node in tmp_nodes_with_classification:
        if "Boundary" in node[classification_param_name]:
            attached_to_id = node[node_param_name][1][attached_param_name]
            flow_id = node[node_param_name][1][consts.Consts.outgoing_flow].pop()
            flows[flow_id][consts.Consts.source_ref] = attached_to_id
            attached_to = next(tmp_node for tmp_node in tmp_nodes_with_classification
                               if tmp_node[node_param_name][0] == attached_to_id)
            attached_to[node_param_name][1][consts.Consts.outgoing_flow].append(
                flow_id)
            boundary_events.append(node)

    for boundary in boundary_events:
        tmp_nodes_with_classification.remove(boundary)
    tmp_nodes_with_classification_copy = copy.deepcopy(
        tmp_nodes_with_classification)

    while tmp_nodes_with_classification:
        for node_with_classification in tmp_nodes_with_classification:
            incoming_list = node_with_classification[node_param_name][1][consts.Consts.incoming_flow]
            if len(incoming_list) == 0:
                no_incoming_flow_nodes.append(node_with_classification)
        if len(no_incoming_flow_nodes) > 0:
            while len(no_incoming_flow_nodes) > 0:
                node_with_classification = no_incoming_flow_nodes.pop()
                tmp_nodes_with_classification.remove(node_with_classification)
                sorted_nodes_with_classification.append(next(tmp_node for tmp_node in tmp_nodes_with_classification_copy
                                                             if tmp_node[node_param_name][0] ==
                                                             node_with_classification[node_param_name][0]))

                outgoing_list = list(
                    node_with_classification[node_param_name][1][consts.Consts.outgoing_flow])
                tmp_outgoing_list = list(outgoing_list)

                for flow_id in tmp_outgoing_list:
                    '''
                    - Remove the outgoing flow for source flow node (the one without incoming flows)
                    - Get the target node
                    - Remove the incoming flow for target flow node
                    '''
                    outgoing_list.remove(flow_id)
                    node_with_classification[node_param_name][1][consts.Consts.outgoing_flow].remove(
                        flow_id)

                    flow = flows[flow_id]
                    target_id = flow[consts.Consts.target_ref]
                    target = next(tmp_node[node_param_name]
                                  for tmp_node in tmp_nodes_with_classification
                                  if tmp_node[node_param_name][0] == target_id)
                    target[1][consts.Consts.incoming_flow].remove(flow_id)
    return sorted_nodes_with_classification


def reverse_flows(flows, tmp_nodes_with_classification, back_edges_ids):
    node_param_name = "node"
    for flow_id in back_edges_ids:
        flow = flows[flow_id]
        source_id = flow[consts.Consts.source_ref]
        target_id = flow[consts.Consts.target_ref]
        flow[consts.Consts.source_ref] = target_id
        flow[consts.Consts.target_ref] = source_id

        source_finished = False
        target_finished = False
        for node in tmp_nodes_with_classification:
            if node[node_param_name][0] == source_id:
                node[node_param_name][1][consts.Consts.outgoing_flow].remove(
                    flow_id)
                node[node_param_name][1][consts.Consts.incoming_flow].append(
                    flow_id)
                source_finished = True
            elif node[node_param_name][0] == target_id:
                node[node_param_name][1][consts.Consts.incoming_flow].remove(
                    flow_id)
                node[node_param_name][1][consts.Consts.outgoing_flow].append(
                    flow_id)
                target_finished = True
            if source_finished and target_finished:
                break


def grid_layout(flows, sorted_nodes_with_classification, bpmn_graph, back_edges_ids, symmetric):
    """

    :param sorted_nodes_with_classification:
    :param bpmn_graph:
    :return:
    """
    tmp_nodes_with_classification = list(sorted_nodes_with_classification)

    last_row = consts.Consts.grid_column_width
    last_col = 1
    grid = []
    while tmp_nodes_with_classification:
        node_with_classification = tmp_nodes_with_classification.pop(0)
        (grid, last_row, last_col) = place_element_in_grid(node_with_classification, grid, last_row, last_col,
                                                           flows, tmp_nodes_with_classification,
                                                           sorted_nodes_with_classification, bpmn_graph, back_edges_ids,
                                                           symmetric)
    return grid


def place_element_in_grid(node_with_classification, grid, last_row, last_col, flows, nodes_with_classification,
                          all_nodes_with_classification, bpmn_graph, back_edges_ids, symmetric):
    """

    :param node_with_classification:
    :param grid:
    :param last_row:
    :param last_col:
    :param bpmn_graph:
    :param nodes_with_classification:
    :param enforced_row_num:
    :return:
    """
    node_param_name = "node"

    node_id = node_with_classification[node_param_name][0]
    incoming_flows = node_with_classification[node_param_name][1][consts.Consts.incoming_flow]
    outgoing_flows = node_with_classification[node_param_name][1][consts.Consts.outgoing_flow]

    if node_with_classification[node_param_name][1]["node_name"] == "Task3":
        print("dfgrg")

    if len(incoming_flows) == 0:
        # if node has no incoming flow, put it in new row
        current_element_row = last_row
        current_element_col = last_col
        insert_into_grid(grid, current_element_row, current_element_col, [last_row - 1], node_id)
        last_row += consts.Consts.grid_column_width
    # not join
    elif len(incoming_flows) == 1:
        # if node is not a Join, put it right from its predecessor (element should only have one predecessor)
        flow_id = incoming_flows[0]
        flow = flows[flow_id]
        predecessor_id = flow[consts.Consts.source_ref]
        predecessor = next(
            node for node in all_nodes_with_classification if node[node_param_name][0] == predecessor_id)
        predecessor_cell = next(
            grid_cell for grid_cell in grid if grid_cell.node_id == predecessor_id)
        predecessor_outs = len(
            predecessor[node_param_name][1][consts.Consts.outgoing_flow])
        if predecessor_outs == 1:  # predecessor is not split
            # insert into cell right from predecessor - no need to insert new column or row
            current_element_col = predecessor_cell.col + 1
            current_element_row = predecessor_cell.row
            insert_into_grid(grid, current_element_row,
                             current_element_col, predecessor_cell.branches, node_id)
        else:  # predecessor is split
            flow_before_split_id = predecessor[node_param_name][1][consts.Consts.incoming_flow][0]
            current_element_col = predecessor_cell.col + 1

            # non-symmetrical:
            if predecessor[consts.Consts.center_branch_free] and predecessor[
                consts.Consts.corresponding_join] is None and \
                    ((flow_id in back_edges_ids and flow_before_split_id in back_edges_ids) or (
                            flow_id not in back_edges_ids and flow_before_split_id not in back_edges_ids)):
                branches = predecessor_cell.branches + [predecessor[consts.Consts.center_branch_number]]
                insert_into_grid(grid, predecessor_cell.row,
                                 current_element_col, branches, node_id)
                predecessor[consts.Consts.center_branch_free] = False
                if predecessor[consts.Consts.next_free_branch] == predecessor[consts.Consts.center_branch_number]:
                    predecessor[consts.Consts.next_free_branch] += 1
            else:
                if predecessor[consts.Consts.next_free_branch] == predecessor[consts.Consts.center_branch_number]:
                    predecessor[consts.Consts.next_free_branch] += 1
                branches = predecessor_cell.branches + \
                           [predecessor[consts.Consts.next_free_branch]]
                insert_into_grid(grid, predecessor_cell.row + predecessor[consts.Consts.next_free_branch] - predecessor[
                    consts.Consts.center_branch_number],
                                 current_element_col, branches, node_id)
                predecessor[consts.Consts.next_free_branch] += 1
                shift_nodes(branches, predecessor[consts.Consts.center_branch_number], grid)
    # TODO consider rule for split/join node
    else:  # join
        # find the rightmost predecessor - put into next column
        # if last_split was passed, use row number from it, otherwise compute mean from predecessors
        predecessors_id_list = []
        for flow_id in incoming_flows:
            flow = flows[flow_id]
            predecessors_id_list.append(flow[consts.Consts.source_ref])

        max_col_num = 0
        for grid_cell in grid:
            if grid_cell.node_id in predecessors_id_list:
                if grid_cell.col > max_col_num:
                    max_col_num = grid_cell.col
        current_element_col = max_col_num + 1

        # find corresponding split:
        previous_cell = next(
            node for node in all_nodes_with_classification if node[node_param_name][0] == predecessors_id_list[0])
        forks = 1
        found = True
        while True:
            predecessors_ids = []
            in_flows = previous_cell[node_param_name][1][consts.Consts.incoming_flow]
            for flow_id in in_flows:
                flow = flows[flow_id]
                predecessors_ids.append(flow[consts.Consts.source_ref])

            successors_ids = []
            out_flows = previous_cell[node_param_name][1][consts.Consts.outgoing_flow]
            for flow_id in out_flows:
                flow = flows[flow_id]
                successors_ids.append(flow[consts.Consts.target_ref])

            if len(predecessors_ids) > 1:
                forks += 1
            if len(successors_ids) > 1:
                forks -= 1

            if forks == 0:
                break

            if len(predecessors_ids) > 0:
                previous_cell = next(
                    node for node in all_nodes_with_classification if node[node_param_name][0] == predecessors_ids[0])
            else:
                found = False
                break

        if found:
            for grid_cell in grid:
                if grid_cell.node_id == previous_cell[node_param_name][0]:
                    current_element_row = grid_cell.row
        else:
            row_num_sum = 0
            for grid_cell in grid:
                if grid_cell.node_id in predecessors_id_list:
                    row_num_sum += grid_cell.row
            current_element_row = row_num_sum // len(predecessors_id_list)
        branches = next(grid_cell for grid_cell in grid if grid_cell.node_id ==
                        previous_cell[node_param_name][0]).branches
        insert_into_grid(grid, current_element_row,
                         current_element_col, branches, node_id)

        corresponding_split = next(node for node in all_nodes_with_classification if
                                   node[node_param_name][0] == previous_cell[node_param_name][0])
        corresponding_split_id = corresponding_split[node_param_name][0]
        for flow_id in incoming_flows:
            flow = flows[flow_id]
            if flow[consts.Consts.source_ref] == corresponding_split_id:
                if corresponding_split[consts.Consts.corresponding_join] is None:
                    bpmn_graph.get_flow_by_id(flow_id)[2][consts.Consts.branch_offset] = corresponding_split[consts.Consts.next_free_branch] - corresponding_split[consts.Consts.center_branch_number]
                break

        # remove unneccesary finished branches
        # for cell in grid:
        #     try:
        #         if cell.branches[:len(branches)] == branches and len(cell.branches) > len(branches):
        #             # del cell.branches
        #             cell.branches = []
        #     except AttributeError:
        #         pass

    # if split
    if len(outgoing_flows) > 1:
        # non-symmetrical:
        branches = next(grid_cell for grid_cell in grid if grid_cell.node_id == node_id).branches
        node_with_classification[consts.Consts.next_free_branch] = 0
        if len(outgoing_flows) % 2 == 0 and not (
                branches[-1] == 0 and len(branches) > 1):  # pair and branches go 1 level down
            node_with_classification[consts.Consts.center_branch_number] = len(outgoing_flows) // 2 - 1
        else:
            node_with_classification[consts.Consts.center_branch_number] = len(outgoing_flows) // 2

        node_with_classification[consts.Consts.center_branch_free] = True

        node_with_classification[consts.Consts.corresponding_join] = None
        for flow_id in node_with_classification[node_param_name][1][consts.Consts.outgoing_flow]:
            flow = flows[flow_id]
            potential_join_id = flow[consts.Consts.target_ref]
            potential_join = next(
                node for node in all_nodes_with_classification if node[node_param_name][0] == potential_join_id)
            if len(potential_join[node_param_name][1][consts.Consts.incoming_flow]) > 1:  # is corresponding join
                if (incoming_flows[0] in back_edges_ids) and (flow_id in back_edges_ids) or \
                        (incoming_flows[0] not in back_edges_ids) and (flow_id not in back_edges_ids):
                    node_with_classification[consts.Consts.corresponding_join] = potential_join_id
                break

    return grid, last_row, last_col


def shift_nodes(branches, center, grid):
    if branches[-1] < center:  # shift appropriate nodes up
        for level in range(1, len(branches)):
            slice = branches[:level]
            slice[-1] -= 1
            found = True
            while found:
                found = False
                for cell in grid:
                    try:
                        if cell.branches[:len(slice)] == slice:
                            found = True
                            cell.row -= 1
                    except AttributeError:
                        pass
                slice[-1] -= 1
    else:  # shift appropriate nodes down
        for level in range(1, len(branches)):
            slice = branches[:level]
            slice[-1] += 1
            found = True
            while found:
                found = False
                for cell in grid:
                    try:
                        if cell.branches[:len(slice)] == slice:
                            found = True
                            cell.row += 1
                    except AttributeError:
                        pass
                slice[-1] += 1


def insert_into_grid(grid, row, col, branches, node_id):
    """

    :param grid:
    :param row:
    :param col:
    :param node_id:
    """
    # if row <= 0:
    #     row = 1
    grid.append(cell_class.GridCell(row, col, branches, node_id))


def set_coordinates_for_nodes(bpmn_graph, grid):
    """

    :param bpmn_graph:
    :param grid:
    """

    nodes = bpmn_graph.get_nodes()
    for node in nodes:
        try:
            cell = next(
                grid_cell for grid_cell in grid if grid_cell.node_id == node[0])
            node[1][consts.Consts.x] = str(
                cell.col * 150 + (100 - int(node[1][consts.Consts.width])) // 2)
            node[1][consts.Consts.y] = str(
                cell.row * 150 + (100 - int(node[1][consts.Consts.height])) // 2)
        except:  # boundary events
            pass
    boundary_events = bpmn_graph.get_nodes(consts.Consts.boundary_event)
    for boundary in boundary_events:
        attached_to_id = boundary[1][consts.Consts.attached_to_ref]
        attached_to = next(tmp_node for tmp_node in nodes
                           if tmp_node[0] == attached_to_id)
        successor_id = bpmn_graph.get_flow_by_id(
            boundary[1][consts.Consts.outgoing_flow][0])[2][consts.Consts.target_ref]
        successor = next(tmp_node for tmp_node in nodes
                         if tmp_node[0] == successor_id)

        successor_y_center = int(
            successor[1][consts.Consts.y]) + int(successor[1][consts.Consts.height]) // 2
        att_y_center = int(
            attached_to[1][consts.Consts.y]) + int(attached_to[1][consts.Consts.height]) // 2
        if att_y_center < successor_y_center:
            boundary[1][consts.Consts.x] = str(
                int(attached_to[1][consts.Consts.x]) + 30)
            boundary[1][consts.Consts.y] = str(
                int(attached_to[1][consts.Consts.y]) + 80)
        elif att_y_center == successor_y_center:
            boundary[1][consts.Consts.x] = str(
                int(attached_to[1][consts.Consts.x]) + 80)
            boundary[1][consts.Consts.y] = str(
                int(attached_to[1][consts.Consts.y]) + 30)
        else:
            boundary[1][consts.Consts.x] = str(
                int(attached_to[1][consts.Consts.x]) + 30)
            boundary[1][consts.Consts.y] = str(
                int(attached_to[1][consts.Consts.y]) - 20)


def set_flows_waypoints(bpmn_graph, back_edges_ids, reversed_nodes):
    """

    :param bpmn_graph:
    """
    # TODO get rid of string cast
    flows = bpmn_graph.get_flows()
    node_param_name = "node"
    for flow in flows:
        if flow[2][consts.Consts.id] in back_edges_ids:
            reversed = True
            source_node = bpmn_graph.get_node_by_id(
                flow[2][consts.Consts.target_ref])
            try:
                source_node_copy = next(
                    node for node in reversed_nodes if node[node_param_name][0] == flow[2][consts.Consts.target_ref])[
                    node_param_name]
                source_outgoing = len(
                    source_node_copy[1][consts.Consts.outgoing_flow])
            except StopIteration:  # boundary event
                attached_to_id = source_node[1][consts.Consts.attached_to_ref]
                attached_to = \
                next(tmp_node for tmp_node in reversed_nodes if tmp_node[node_param_name][0] == attached_to_id)[
                    node_param_name]
                source_outgoing = len(
                    attached_to[1][consts.Consts.outgoing_flow])
            target_node = bpmn_graph.get_node_by_id(
                flow[2][consts.Consts.source_ref])
        else:
            reversed = False
            source_node = bpmn_graph.get_node_by_id(
                flow[2][consts.Consts.source_ref])
            try:
                source_node_copy = next(
                    node for node in reversed_nodes if node[node_param_name][0] == flow[2][consts.Consts.source_ref])[
                    node_param_name]
                source_outgoing = len(
                    source_node_copy[1][consts.Consts.outgoing_flow])
            except StopIteration:  # boundary event
                attached_to_id = source_node[1][consts.Consts.attached_to_ref]
                attached_to = \
                next(tmp_node for tmp_node in reversed_nodes if tmp_node[node_param_name][0] == attached_to_id)[
                    node_param_name]
                source_outgoing = len(
                    attached_to[1][consts.Consts.outgoing_flow])
            target_node = bpmn_graph.get_node_by_id(
                flow[2][consts.Consts.target_ref])
        source_width = int(source_node[1][consts.Consts.width])
        source_height = int(source_node[1][consts.Consts.height])
        source_x = int(source_node[1][consts.Consts.x])
        source_y = int(source_node[1][consts.Consts.y])

        target_width = int(target_node[1][consts.Consts.width])
        target_height = int(target_node[1][consts.Consts.height])
        target_x = int(target_node[1][consts.Consts.x])
        target_y = int(target_node[1][consts.Consts.y])

        if consts.Consts.branch_offset in flow[2]:
            if reversed:
                if flow[2][consts.Consts.branch_offset] == 0:
                    flow[2][consts.Consts.waypoints] = [(str(target_x),
                                                         str(target_y + target_height // 2)),
                                                        (str(source_x + source_width),
                                                         str(source_y + source_height // 2))]
                elif flow[2][consts.Consts.branch_offset] > 0:
                    flow[2][consts.Consts.waypoints] = [(str(target_x + target_width // 2),
                                                         str(target_y + target_height)),
                                                        (str(target_x + target_width // 2),
                                                         str(target_y + target_height // 2 + 150 * flow[2][
                                                             consts.Consts.branch_offset])),
                                                        (str(source_x + source_width // 2),
                                                         str(target_y + target_height // 2 + 150 * flow[2][
                                                             consts.Consts.branch_offset])),
                                                        (str(source_x + source_width // 2),
                                                         str(source_y + source_height))]
                else:
                    flow[2][consts.Consts.waypoints] = [(str(target_x + target_width // 2),
                                                         str(target_y)),
                                                        (str(target_x + target_width // 2),
                                                         str(target_y + target_height // 2 + 150 * flow[2][
                                                             consts.Consts.branch_offset])),
                                                        (str(source_x + source_width // 2),
                                                         str(target_y + target_height // 2 + 150 * flow[2][
                                                             consts.Consts.branch_offset])),
                                                        (str(source_x + source_width // 2),
                                                         str(source_y))]
            else:
                if flow[2][consts.Consts.branch_offset] == 0:
                    flow[2][consts.Consts.waypoints] = [(str(source_x + source_width),
                                                         str(source_y + source_height // 2)),
                                                        (str(target_x),
                                                         str(target_y + target_height // 2))]
                elif flow[2][consts.Consts.branch_offset] > 0:
                    flow[2][consts.Consts.waypoints] = [(str(source_x + source_width // 2),
                                                         str(source_y + source_height)),
                                                        (str(source_x + source_width // 2),
                                                         str(source_y + source_height // 2 + 150 * flow[2][
                                                             consts.Consts.branch_offset])),
                                                        (str(target_x + target_width // 2),
                                                         str(source_y + source_height // 2 + 150 * flow[2][
                                                             consts.Consts.branch_offset])),
                                                        (str(target_x + target_width // 2),
                                                         str(source_y + source_height))]
                else:
                    flow[2][consts.Consts.waypoints] = [(str(source_x + source_width // 2),
                                                         str(source_y)),
                                                        (str(source_x + source_width // 2),
                                                         str(source_y + source_height // 2 + 150 * flow[2][
                                                             consts.Consts.branch_offset])),
                                                        (str(target_x + target_width // 2),
                                                         str(source_y + source_height // 2 + 150 * flow[2][
                                                             consts.Consts.branch_offset])),
                                                        (str(target_x + target_width // 2),
                                                         str(target_y))]
        elif source_y + source_height // 2 == target_y + target_height // 2:
            if reversed:
                flow[2][consts.Consts.waypoints] = [(str(target_x),
                                                     str(target_y + target_height // 2)),
                                                    (str(source_x + source_width),
                                                     str(source_y + source_height // 2))]
            else:
                flow[2][consts.Consts.waypoints] = [(str(source_x + source_width),
                                                     str(source_y + source_height // 2)),
                                                    (str(target_x),
                                                     str(target_y + target_height // 2))]
        elif source_y < target_y:
            if source_outgoing > 1:  # split
                if reversed:
                    flow[2][consts.Consts.waypoints] = [(str(target_x),
                                                         str(target_y + target_height // 2)),
                                                        (str(source_x + source_width // 2),
                                                         str(target_y + target_height // 2)),
                                                        (str(source_x + source_width // 2),
                                                         str(source_y + source_height))]
                else:
                    flow[2][consts.Consts.waypoints] = [(str(source_x + source_width // 2),
                                                         str(source_y + source_height)),
                                                        (str(source_x + source_width // 2),
                                                         str(target_y + target_height // 2)),
                                                        (str(target_x),
                                                         str(target_y + target_height // 2))]
            else:
                if reversed:
                    flow[2][consts.Consts.waypoints] = [(str(target_x + target_width // 2),
                                                         str(target_y)),
                                                        (str(target_x + target_width // 2),
                                                         str(source_y + source_height // 2)),
                                                        (str(source_x + source_width),
                                                         str(source_y + source_height // 2))]
                else:
                    flow[2][consts.Consts.waypoints] = [(str(source_x + source_width),
                                                         str(source_y + source_height // 2)),
                                                        (str(target_x + target_width // 2),
                                                         str(source_y + source_height // 2)),
                                                        (str(target_x + target_width // 2),
                                                         str(target_y))]
        else:
            if source_outgoing > 1:  # split
                if reversed:
                    flow[2][consts.Consts.waypoints] = [(str(target_x),
                                                         str(target_y + target_height // 2)),
                                                        (str(source_x + source_width // 2),
                                                         str(target_y + target_height // 2)),
                                                        (str(source_x + source_width // 2),
                                                         str(source_y))]
                else:
                    flow[2][consts.Consts.waypoints] = [(str(source_x + source_width // 2),
                                                         str(source_y)),
                                                        (str(source_x + source_width // 2),
                                                         str(target_y + target_height // 2)),
                                                        (str(target_x),
                                                         str(target_y + target_height // 2))]
            else:
                if reversed:
                    flow[2][consts.Consts.waypoints] = [(str(target_x + target_width // 2),
                                                         str(target_y + target_height)),
                                                        (str(target_x + target_width // 2),
                                                         str(source_y + source_height // 2)),
                                                        (str(source_x + source_width),
                                                         str(source_y + source_height // 2))]
                else:
                    flow[2][consts.Consts.waypoints] = [(str(source_x + source_width),
                                                         str(source_y + source_height // 2)),
                                                        (str(target_x + target_width // 2),
                                                         str(source_y + source_height // 2)),
                                                        (str(target_x + target_width // 2),
                                                         str(target_y + target_height))]