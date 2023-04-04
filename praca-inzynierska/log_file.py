import pandas as pd
from opyenxes.data_in.XUniversalParser import XUniversalParser
from more_itertools import pairwise
from collections import Counter

class LogFile:
    def __init__(self, log_path,
                 case_column,
                 activity_column,
                 start_column,
                 output_column='trace'):

        self._log_path = log_path
        self._log_type = self.get_log_type()
        self._case_column = case_column
        self._activity_column = activity_column
        self._start_column = start_column
        self._output_column = output_column
        self._traces = None
        self.traces_list = []
        self.parse_log_file()
        
    def get_log_type(self):
        if '.csv' in str(self._log_path):
            return 'CSV'
        elif '.xes' in str(self._log_path):
            print("XES")
            return 'XES'
        else:
            raise NotImplementedError
            

    def parse_log_file(self):
        if self._log_type == 'CSV':
            self._traces = self.get_traces_from_csv()
        elif self._log_type == 'XES':
            self._traces = self.get_traces_from_xes()
        else:
            raise NotImplementedError
            
            
    def get_traces_from_csv(self):
        df = pd.read_csv(self._log_path)
        dfs = df[[self._case_column, self._activity_column, self._start_column]]
        dfs = dfs.sort_values(by=[self._case_column, self._start_column]) \
            .groupby([self._case_column]) \
            .agg({self._activity_column: ';'.join})
        dfs[self._output_column] = [trace.split(';') for trace in dfs[self._activity_column]]
        self.traces_list = [trace.split(';') for trace in dfs[self._activity_column]]
        return dfs[[self._output_column]]
        
    def get_traces_from_xes(self):
        CASE_ID = 'concept:name'
        traces_list = []
        indexes_list = []
        with open(self._log_path) as log_file:
            loaded_log = XUniversalParser().parse(log_file)[0]
        for trace in loaded_log:
            event_list = []
            for event in trace:
                event_list.append(str(event.get_attributes()[CASE_ID]))
            traces_list.append(event_list)
            indexes_list.append(trace.get_attributes()[CASE_ID])
        dfs = pd.DataFrame({self._output_column: traces_list}, index=indexes_list)
        self.traces_list = traces_list
        dfs.index.rename(self._case_column, inplace=True)
        return dfs[[self._output_column]]
    

    def get_dfg_and_traces(self):
        dfg = dict()
        traces = []
        indexes = []
        for row in self.traces_list:
            traces.append(row)
            for ev_i, ev_j in pairwise(row):
                if ev_i not in dfg.keys():
                    dfg[ev_i] = Counter()
                dfg[ev_i][ev_j] += 1


        return dfg, traces
