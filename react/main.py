
import sys

from prompt import buildSystemPrompt, Tool
from react_runner import ReactRunner
from search import Search

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
