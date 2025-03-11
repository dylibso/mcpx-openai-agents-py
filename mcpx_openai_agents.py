import mcp_run
from agents import Agent as OpenAIAgent, FunctionTool, Runner
import agents

from typing import List, Set, AsyncIterator, Any
import traceback
import json

__all__ = ["Agent", "mcp_run", "agents"]


def _convert_type(t):
    if t == "string":
        return str
    elif t == "boolean":
        return bool
    elif t == "number":
        return float
    elif t == "integer":
        return int
    elif t == "object":
        return dict
    elif t == "array":
        return list
    raise TypeError(f"Unhandled conversion type: {t}")


class Agent(OpenAIAgent):
    """
    An OpenAI Agent using tools from mcp.run
    """

    client: mcp_run.Client
    ignore_tools: Set[str]
    _original_tools: list
    _registered_tools: List[str]

    def __init__(
        self,
        *args,
        client: mcp_run.Client | None = None,
        ignore_tools: List[str] | None = None,
        **kw,
    ):
        self.client = client or mcp_run.Client()
        self._original_tools = kw.get("tools", [])
        self._registered_tools = []
        self.ignore_tools = set(ignore_tools or [])
        super().__init__(*args, **kw)
        self._update_tools()

        for t in self._original_tools:
            self._registered_tools.append(t.name)

    def set_profile(self, profile: str):
        self.client.set_profile(profile)
        self._update_tools()

    def register_tool(self, tool: mcp_run.Tool, f=None):
        if tool.name in self.ignore_tools:
            return

        def wrap(tool, inner):
            if inner is not None:

                async def f(_ignore, input):
                    try:
                        return inner(**json.loads(input))
                    except Exception as exc:
                        return f"ERROR call to tool {tool.name} failed: {traceback.format_exception(exc)}"
            else:

                async def f(_ignore, input):
                    try:
                        res = self.client.call_tool(
                            tool=tool.name, params=json.loads(input)
                        )
                        return res.content[0].text
                    except Exception as exc:
                        return f"ERROR call to tool {tool.name} failed: {traceback.format_exception(exc)}"

            return f

        t = FunctionTool(
            name=tool.name,
            description=tool.description,
            params_json_schema=tool.input_schema,
            on_invoke_tool=wrap(tool, f),
            strict_json_schema=False,
        )
        self.tools.append(t)

        if f is not None:
            self._registered_tools.append(tool.name)

    def reset_tools(self):
        new_tools = []
        for tool in list(self.tools):
            if tool in self._registered_tools:
                new_tools.append(tool)
        self.tools = new_tools

    def _update_tools(self):
        self.reset_tools()
        for tool in self.client.tools.values():
            self.register_tool(tool)

    async def run(self, *args, update_tools: bool = True, **kw):
        if update_tools:
            self._update_tools()
        return await Runner.run(self, *args, **kw)

    def run_sync(self, *args, update_tools: bool = True, **kw):
        if update_tools:
            self._update_tools()
        return Runner.run_sync(self, *args, **kw)

    async def run_async(self, *args, update_tools: bool = True, **kw):
        if update_tools:
            self._update_tools()
        return await Runner.run(self, *args, **kw)

    def run_stream(
        self,
        *args,
        update_tools: bool = True,
        **kw,
    ) -> AsyncIterator[Any]:
        if update_tools:
            self._update_tools()
        return Runner.run_streamed(self, *args, **kw)
