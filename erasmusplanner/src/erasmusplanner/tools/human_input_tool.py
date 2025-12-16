from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import time


# --------------------------------------------------
# Input schema
# --------------------------------------------------

class HumanInputToolInput(BaseModel):
    """Input schema for HumanInputTool."""
    prompt: str = Field(
        ...,
        description="The question or instruction to show to the user."
    )


# --------------------------------------------------
# Tool implementation
# --------------------------------------------------

class HumanInputTool(BaseTool):
    name: str = "request_human_input"
    description: str = (
        "Use this tool when you need to ask the user for information "
        "and must wait for their response before continuing."
    )
    args_schema: Type[BaseModel] = HumanInputToolInput

    def _run(self, prompt: str) -> str:
        """
        Sends a message to the Panel chat UI and blocks until the user replies.
        """
        # Lazy import to avoid circular imports
        from erasmusplanner.crew import chat_interface
        from erasmusplanner.ui_state import wait_for_user_input

        # Send prompt to UI
        chat_interface.send(prompt, user="System", respond=False)

        # Block until user replies in UI
        return wait_for_user_input()