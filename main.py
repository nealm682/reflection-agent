from typing import List, Sequence 
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, MessageGraph 

from chains import generate_chain, reflect_chain

# keys for nodes in graph
REFLECT = "reflect"
GENERATE = "generate"

# Define the nodes
# Each node is a function that takes a list of messages and returns a list of messages
# The first node is the generation node, which generates a new message
def generation_node(state: Sequence[BaseMessage]):
    return generate_chain.invoke({"messages": state})

# The second node is the reflection node, which reflects on the generated message
def reflection_node(state: Sequence[BaseMessage]):
    res = reflect_chain.invoke({"messages": state})
    return [HumanMessage(content=res.content)]

# Create the graph
builder = MessageGraph()
builder.add_node(GENERATE, generation_node)
builder.add_node(REFLECT, reflection_node)
builder.set_entry_point(GENERATE)

# Add conditional edges. The first argument is the source node, the second is a function that takes the state and returns the destination node
def should_continue(state: List[BaseMessage]):
    if len(state) > 6:
        return END
    return REFLECT

# Add the conditional edges to the graph
builder.add_conditional_edges(GENERATE, should_continue)
builder.add_edge(REFLECT, GENERATE)

# Compile the graph and print it
graph = builder.compile()
print(graph.get_graph().draw_mermaid())

if __name__ == "__main__":
    print("Welcome to the Twitter Techie Influencer Assistant!")
    
    # Initial input
    inputs = HumanMessage(content="""Make this tweet better:
                          @langChainAI
                          - newly Tool Calling feature is seriously underrated.
                          After a long wait, it's finally here - making the implementation of the tool easier than ever.
                          Made a video covering their newest feature, check it out!
                          #langchain #toolcalling #newfeature""")
    
    # Start the chain with the initial message
    messages = [inputs]  # Start with the initial message

    # Run the graph
    result = graph.invoke(messages)

    # Print the final output
    for message in result:
        print(message.content)
