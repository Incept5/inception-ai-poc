from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.base import BaseCheckpointSaver

class CheckpointerService:
    @staticmethod
    def get_checkpointer(checkpointer_type: str = "sqlite", **kwargs) -> BaseCheckpointSaver:
        if checkpointer_type == "sqlite":
            conn_string = kwargs.get("conn_string", ":memory:")
            return SqliteSaver.from_conn_string(conn_string)
        # Add more checkpointer types here as needed
        else:
            raise ValueError(f"Unsupported checkpointer type: {checkpointer_type}")