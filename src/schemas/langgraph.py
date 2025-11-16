from typing import Annotated, List
from langgraph.graph.message import add_messages, MessagesState, AnyMessage


class AgentState(MessagesState):
    summary: Annotated[str, "A brief summary of the conversation so far."]
    history: Annotated[List[AnyMessage], add_messages]
