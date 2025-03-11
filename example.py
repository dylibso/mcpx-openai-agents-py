from mcpx_openai_agents import Agent

import readline
import asyncio


history = []


async def run(agent, msg):
    """
    Send a message to an agent and return the result
    """
    global history
    history.append({"content": msg, "role": "user"})
    result = await agent.run(history)
    history.extend(result.new_items)
    return result


agent = Agent("example")

while True:
    msg = input("> ")
    readline.add_history(msg)
    if msg == "exit":
        break
    elif len(msg) == 0:
        continue
    res = asyncio.run(run(agent, msg))
    print(">>", res.final_output)
