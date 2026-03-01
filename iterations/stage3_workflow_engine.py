#####################################################################
# Stages Completed
# Stage 1: Workflow DAG Spine
# Stage 2: Execution Engine Layer
# Stage 3: LLM-proposed Initial Workflow DAG
#####################################################################

#####################################################################
# Step 0: Libraries
#####################################################################

from collections import defaultdict;
from llm_planner import GrokPlanner;
import uuid;
print("# Step 0: Libraries Imported");

#####################################################################
# Step 1: Tool Registry
#####################################################################

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name, func):
        self.tools[name] = func

    def execute(self, name, context):
        if name not in self.tools:
            raise ValueError(f"Tool {name} not registered.")
        return self.tools[name](context)

print("# Step 1: Tool Registry created");

#####################################################################
# Step 2: Execution Engine
#####################################################################

class ExecutionEngine:
    def __init__(self, graph, tool_registry):
        self.graph = graph
        self.registry = tool_registry
        self.context = \
            {
            "capability_gap": None
            }

    def run(self):
        print("\nStarting execution loop...\n")

        while True:
            executable = self.graph.get_next_executable_nodes()

            if not executable:
                print("No more executable nodes.")
                break

            for node_id in executable:
                node = self.graph.nodes[node_id]

                print(f"Executing node: {node_id}")
                node.status = "running"

                try:
                    result = self.registry.execute(node_id, self.context)

                    if result.get("status") == "failed":
                        node.status = "failed"
                        self.context["capability_gap"] = result.get("capability_gap")
                        print(f"Node {node_id} failed.")
                        return "failure"

                    node.status = "complete"

                except Exception as e:
                    node.status = "failed"
                    print(f"Execution error in {node_id}: {e}")
                    return "failure"

        return "complete"

print("# Step 2: Execution Engine created");

#####################################################################
# Step 3: Mock Tool Implementations
#####################################################################

def run_tests_tool(context):
    print("Running tests...")
    return {"status": "success"}

def fix_code_tool(context):
    print("Attempting to fix code...")
    # Simulate capability gap
    return \
        {
        "status": "failed",
        "capability_gap": "nested_schema_validation"
        }

def verify_tool(context):
    print("Verifying final result...")
    return {"status": "success"}

def read_local_knowledge_tool(context):
    print("Reading local knowledge base...")
    return {"status": "success"}

def sandbox_experiment_tool(context):
    print("Running sandbox experiment...")
    return {"status": "success"}

def approval_gate_tool(context):
    print("Awaiting human approval...")
    approval = input("Approve new skill? (y/n): ")
    if approval.lower() == "y":
        return {"status": "success"}
    return {"status": "failed"}

def register_skill_tool(context):
    print("Registering new skill into registry...")
    return {"status": "success"}

print("# Step 3: Mock Tool Implementations completed");

#####################################################################
# Step 4: Node Model
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

print("# Step 4: Node Model Defined");

#####################################################################
# Step 5: Workflow Graph
#####################################################################

class WorkflowGraph:
    def __init__(self):
        self.nodes = {};
        self.edges = defaultdict(list); # from_node -> [to_nodes]
        self.reverse_edges = defaultdict(list); # to_node -> [from_nodes]

    ##################################
    # Step 5A: Node & Edge Management
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
    
    print("# Step 5A: Node & Edge Management Done");

    ##################################
    # Step 5B: Execution Helpers
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

    print("# Step 5B: Execution Helpers Created");

    ##################################
    # Step 5C: Subgraph Injection
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

    print("# Step 5C: Subgraph Injection Functionality Defined");

    ##################################
    # Step 5D: Graph Printing
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

    print("# Step 5D: Graph Printing Functionality Defined");

#####################################################################
# Step 6: Hardcoded Test Simulation
#####################################################################

def simulate_workflow():
    
    graph = WorkflowGraph();
    registry = ToolRegistry();

    # Register initial tools
    registry.register("run_tests", run_tests_tool);
    registry.register("fix_code", fix_code_tool);
    registry.register("verify", verify_tool);

    # The initial graph was manually hardcoded in earlier iterations
    # Now it is being dynamically created by the LLM (Grok)

    # graph.add_node(Node("run_tests", "tool")); graph.add_node(Node("fix_code", "tool"));
    # graph.add_edge("run_tests", "fix_code");
    # graph.add_node(Node("verify", "tool"));
    # graph.add_edge("fix_code", "verify");

    # Dynamic Workflow Graph Creation below between the # lines

    ###############################################################

    planner = GrokPlanner();

    task_description = "Fix failing tests in a Python repository.";
    available_tools = ["run_tests", "fix_code", "verify"];

    workflow_json = planner.propose_workflow\
    (
        task_description,
        available_tools
    );

    # Building the graph dynamically with an LLM (Grok)
    for node_name in workflow_json["nodes"]:
        graph.add_node(Node(node_name, "tool"));
    for edge in workflow_json["edges"]:
        graph.add_edge(edge[0], edge[1]);

    ###############################################################

    graph.print_graph();

    engine = ExecutionEngine(graph, registry);
    result = engine.run();

    if result == "failure" and engine.context["capability_gap"]:
        print("\nCapability gap detected. Injecting acquisition subgraph...\n");

        # Mark fix_code as structurally handled
        graph.nodes["fix_code"].status = "complete"; 

        # Register new tools
        registry.register("read_local_knowledge", read_local_knowledge_tool);
        registry.register("sandbox_experiment", sandbox_experiment_tool);
        registry.register("approval_gate", approval_gate_tool);
        registry.register("register_skill", register_skill_tool);

        sub_nodes = \
            [
            Node("read_local_knowledge", "tool"),
            Node("sandbox_experiment", "tool"),
            Node("approval_gate", "control"),
            Node("register_skill", "tool"),
            ];

        sub_edges = \
            [
            ("read_local_knowledge", "sandbox_experiment"),
            ("sandbox_experiment", "approval_gate"),
            ("approval_gate", "register_skill"),
            ];

        graph.inject_subgraph_after("fix_code", sub_nodes, sub_edges);

        graph.print_graph();

        print("\nResuming execution...\n");
        engine = ExecutionEngine(graph, registry);
        engine.run();

    print("\nFinal Graph State:");
    graph.print_graph();

print("# Step 6: Hardcoded Test Simulation Created");
    
#####################################################################
# Entry Point
#####################################################################

if __name__ == "__main__":
    simulate_workflow();