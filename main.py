from typing import List, Sequence 
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, MessageGraph 

from chains import generate_chain, reflect_chain

# keys for nodes in graph
REFLECT = "reflect"
GENERATE = "generate"

def generation_node(state: Sequence[BaseMessage]):
    return generate_chain.invoke({"messages": state})

def reflection_node(state: Sequence[BaseMessage]):
    res = reflect_chain.invoke({"messages": state})
    return [HumanMessage(content=res.content)]

builder = MessageGraph()
builder.add_node(GENERATE, generation_node)
builder.add_node(REFLECT, reflection_node)
builder.set_entry_point(GENERATE)

def should_continue(state: List[BaseMessage]):
    if len(state) > 6:
        return END
    return REFLECT

builder.add_conditional_edges(GENERATE, should_continue)
builder.add_edge(REFLECT, GENERATE)

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
