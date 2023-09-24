
import sys

from dataclasses import dataclass
from typing import List

from react_runner import ReactRunner
from search import Search

@dataclass
class Tool:
    name: str
    input_description: str
    tool_description: str

def buildSystemPrompt(task: str, tools: List[Tool]):
    tool_names = "["
    for index, tool in enumerate(tools):
        if index > 0:
            tool_names += ","
        tool_names += tool.name
    tool_names += "]"

    tool_description = ""
    for index, tool in enumerate(tools):
        tool_description += f"""
Tool {index+1}:
Action: {tool.name}
Action Input: {tool.input_description}
Description: {tool.tool_description}

"""

    return f"""
You are an assistant helping a human.

Your task is to:
{task}

You use a Thought/Action/Action Input/Observation pattern:
'''
Thought: The thought you are having based on the observation
Action: The action you want to take.  One of {tool_names}
Action Input: The input to the action
Observation: An observation
'''

(...this Thought/Action/Action Input/Observation pattern can repeat N times)

== TOOLS ==

You have access to the following tools:

{tool_description}

== OPTIONS ==

Select ONLY ONE option below:

Option 1: To use a tool, you MUST use the following format:
'''
Thought: Do I need to use a tool? Yes because of the observation [the reason why you need to use a tool...]
Action: MUST be one of {tool_names}
Action Input: The input to the tool
Observation: The observation from the action
'''

Option 2: To output the final answer, you MUST use the following format:
'''
Final Answer: The final answer for the task
'''
"""

def main(task: str):
    searcher = Search(log=lambda x: print(f"* {x}"))
    tools = [Tool(
        name="search",
        input_description="The query used to search wikipedia",
        tool_description="Used to search wikipedia",
    )]
    system_prompt = buildSystemPrompt(task, tools)
    ReactRunner(
        actions={
            "search": lambda query: searcher.search(query),
        },
        log=lambda x: print(f"> {x}"),
        system_prompt=system_prompt,
        max_iterations=10,
    ).run()

if len(sys.argv) < 2:
    print("A task must be specified")
    exit(1)

task = ""
for i in range(1, len(sys.argv)):
    task += sys.argv[i] + " "

main(task)
