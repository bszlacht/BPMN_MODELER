package pl.edu.agh;

import org.jbpt.algo.tree.rpst.RPST;
import org.json.JSONException;

public class Main {

    public static void main(String[] args) throws JSONException {
//        String inputBpmn = args[0];
        String inputBpmn = "{'ER Registration': ['ER Triage'], 'Leucocytes': ['CRP'], 'LacticAcid': ['Leucocytes'], 'ER Sepsis Triage': ['IV Liquid'], 'IV Liquid': ['IV Antibiotics'], 'Release A': ['Return ER'], 'Admission IC': ['LacticAcid'], 'Release D': ['Return ER'], 'Release E': ['Return ER'], 'Release C': ['Return ER'], 'Return ER': ['CRP'], 'ER Triage': ['ER Sepsis Triage'], 'xor1': ['LacticAcid', 'Release D', 'Release C', 'Release E', 'Release B', 'Release A'], 'CRP': ['xor1'], 'xor2': ['ER Registration', 'Admission IC', 'Admission NC'], 'IV Antibiotics': ['xor2'], 'xor3': ['Leucocytes', 'CRP'], 'Admission NC': ['xor3']}";
        System.out.println(discoverJoins(inputBpmn));
    }

    private static String discoverJoins(String inputBpmn) throws JSONException {
        Graph graph = new Graph(inputBpmn);
        JoinMiner joinMiner = new JoinMiner(new RPST<>(graph), graph);
        joinMiner.discoverJoins();
//        System.out.println();
//        System.out.println(graph.toString());
        return graph.toString();
    }
}