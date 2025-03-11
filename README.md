# mcpx-openai-agents

A Python library for using mcp.run tools with the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)

## Example

```python
agent = Agent()
results = agent.run_sync(
    "find the largest prime under 1000 that ends with the digit '3'"
)
print(results.final_output)
```
