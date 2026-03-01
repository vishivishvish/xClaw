#####################################################################
# Stages Completed
# Stage 1: Workflow DAG Spine
#####################################################################

#####################################################################
# Step 0: Libraries
#####################################################################

from collections import defaultdict;
import uuid;
print("# Step 0: Libraries Imported");

#####################################################################
# Step 1: Node Model
#####################################################################

class Node:
    def __init__(self, node_id, node_type, metadata = None):
        self.id = node_id;
        self.type = node_type;
        self.metadata = metadata or {};
        self.status = "pending"; 
        # This can toggle between pending | running | complete | failed

    def __repr__(self):
        return f"Node(id={self.id}, type={self.type}, status={self.status})";

print("# Step 1: Node Model Defined");

#####################################################################
# Step 2: Workflow Graph
#####################################################################

class WorkflowGraph:
    def __init__(self):
        self.nodes = {};
        self.edges = defaultdict(list); # from_node -> [to_nodes]
        self.reverse_edges = defaultdict(list); # to_node -> [from_nodes]

    ##################################
    # Step 2A: Node & Edge Management
    ##################################

    def add_node(self, node):
        if node.id in self.nodes:
            raise ValueError(f"Node {node.id} already exists");
        self.nodes[node.id] = node;

    def add_edge(self, from_node, to_node):
        if from_node not in self.nodes or to_node not in self.nodes:
            raise ValueError("Both nodes must exist before adding an edge");
        self.edges[from_node].append(to_node);
        self.reverse_edges[to_node].append(from_node);
    
    def remove_edge(self, from_node, to_node):
        if to_node in self.edges[from_node]:
            self.edges[from_node].remove(to_node);
        if from_node in self.reverse_edges[to_node]:
            self.reverse_edges[to_node].remove(from_node);
    
    print("# Step 2A: Node & Edge Management Done");

    ##################################
    # Step 2B: Execution Helpers
    ##################################

    def get_next_executable_nodes(self):
        """
        A node is executable if:
        - status == "pending"
        - all parents are "complete"
        """
        executable = [];
        for node_id, node in self.nodes.items():
            if node.status != "pending":
                continue;

            parents = self.reverse_edges[node_id];
            if all(self.nodes[p].status == "complete" for p in parents):
                executable.append(node_id);

        return executable;

    def mark_complete(self, node_id):
        self.nodes[node_id].status = "complete";

    def mark_failed(self, node_id):
        self.nodes[node_id].status = "failed";

    print("# Step 2B: Execution Helpers Created");

    ##################################
    # Step 2C: Subgraph Injection
    ##################################

    def inject_subgraph_after(self, after_node_id, subgraph_nodes, subgraph_edges):
        """
        Injects a subgraph after `after_node_id`
        Rewires outgoing edges of after_node to the entry node of the subgraph
        """
        if after_node_id not in self.nodes:
            raise ValueError("after_node_id does not exist");

        # Capture original outgoing edges
        original_children = list(self.edges[after_node_id]);

        # Remove existing outgoing edges
        for child in original_children:
            self.remove_edge(after_node_id, child);

        # Add subgraph nodes
        for node in subgraph_nodes:
            self.add_node(node);

        # Add subgraph edges
        for from_node, to_node in subgraph_edges:
            self.add_edge(from_node, to_node);

        # Connect after_node to subgraph entry
        entry_node_id = subgraph_nodes[0].id;
        self.add_edge(after_node_id, entry_node_id);

        # Find subgraph exit node(s)
        subgraph_node_ids = {node.id for node in subgraph_nodes};
        exit_nodes = \
            [
                node_id for node_id in subgraph_node_ids \
                if not any(child in subgraph_node_ids for child in self.edges[node_id])
            ];

        # Reconnect exit nodes to original children
        for exit_node in exit_nodes:
            for child in original_children:
                self.add_edge(exit_node, child);

    print("# Step 2C: Subgraph Injection Functionality Defined");

    ##################################
    # Step 2D: Graph Printing
    ##################################

    def print_graph(self):
        print("\nCurrent Workflow Graph:");

        printed_edges = set();
        terminal_nodes = [];

        for node_id in self.nodes:
            children = self.edges[node_id];
            status = self.nodes[node_id].status;
            
            if children:
                for child in children:
                    print(f"[{node_id} ({status})] --> [{child} ({self.nodes[child].status})]");
                    printed_edges.add(child);
            else:
                terminal_nodes.append(node_id);
        
        for node_id in terminal_nodes:
            if node_id not in printed_edges:
                print(f"[{node_id} ({self.nodes[node_id].status})]");
        
        print("-" * 50);

    print("# Step 2D: Graph Printing Functionality Defined");

#####################################################################
# Step 3: Hardcoded Test Simulation
#####################################################################

def simulate_workflow():
    
    print("\nInitializing Workflow...\n");

    graph = WorkflowGraph();

    # Initial linear workflow
    run_tests = Node("run_tests", "tool");
    fix_code = Node("fix_code", "tool");
    verify = Node("verify", "tool");

    graph.add_node(run_tests); graph.add_node(fix_code);
    graph.add_edge("run_tests", "fix_code");
    graph.add_node(verify);
    graph.add_edge("fix_code", "verify");

    graph.print_graph();

    ##################################
    # Step 3A: Simulate Execution
    ##################################

    # run_tests completes
    print("\nRunning run_tests...");
    graph.mark_complete("run_tests");

    # fix_code runs but FAILS
    print("Running fix_code...");
    graph.mark_failed("fix_code");
    print("Failure detected: capability gap (nested_schema_validation) \n");

    ##################################
    # Step 3B: Inject Capability Acquisition Subgraph
    ##################################

    print("Injecting capability acquisition subgraph...\n");

    read_kb = Node("read_local_knowledge", "tool");
    sandbox = Node("sandbox_experiment", "tool");
    approval = Node("approval_gate", "control");
    register = Node("register_skill", "tool");

    subgraph_nodes = [read_kb, sandbox, approval, register];
    subgraph_edges = \
    [
        ("read_local_knowledge", "sandbox_experiment"),
        ("sandbox_experiment", "approval_gate"),
        ("approval_gate", "register_skill")
    ];

    graph.inject_subgraph_after\
    (
        after_node_id = "fix_code",
        subgraph_nodes = subgraph_nodes,
        subgraph_edges = subgraph_edges
    );

    graph.print_graph();

    print("\nSubgraph successfully injected.\n");

    return graph;
    

#####################################################################
# Entry Point
#####################################################################

if __name__ == "__main__":
    simulate_workflow();