
import re

from dataclasses import dataclass
from typing import Callable, Optional, Dict

from react.chatbot import Chatbot

KEY_VALUE_REGEX = re.compile("^([\\w ]+):(.*)$")

FINAL_ANSWER = "Final Answer"
ACTION = "Action"
ACTION_INPUT = "Action Input"
OBSERVATION = "Observation"

@dataclass
class ReactRunner(object):
    actions: Dict[str, Callable[[str], str]]
    system_prompt: str
    log: Callable[[str], None]
    max_iterations: int

    def run(self, text: Optional[str] = None) -> Optional[str]:
        chatbot = Chatbot(self.system_prompt)
        message = text or ''
        for _ in range(self.max_iterations):
            self.log(message)
            response = chatbot.process(message)

            self.log(f'Response:\n{response}\n')
            parsed_output = parseOutput(response)

            if FINAL_ANSWER in parsed_output:
                return parsed_output[FINAL_ANSWER]
            
            if ACTION not in parsed_output:
                message = "Observation: I didn't specify an action to perform"
                continue

            if ACTION_INPUT not in parsed_output:
                message = "Observation: I specified an action, but not an input for it"
                continue

            action = parsed_output[ACTION]
            action_input = parsed_output[ACTION_INPUT]

            if action not in self.actions:
                message = f"Observation: I specified an unrecognized {action}"
                continue

            self.log(f"Running: {action} {action_input}")
            observation = self.actions[action](action_input)
            message = f"Observation: {observation}"

        return None

def parseOutput(output: str) -> Dict[str, str]:
    """
    Used to parse the output from an LLM and identify keys and
    values in text that looks like the following:
    ```
    Thought: some thought
    Action: some action
    Action Input: some action input
    Observation: some observation
    ```
    For that input, the output from this function will be:
    ```
    {
      "Thought": "some thought",
      "Action": "some action",
      "Action Input": "some action input",
      "Observation": "some observation"
    }
    ```
    Note: If the input has repeated keys, the last value is used,
    i.e. given the input:
    ```
    Some Key: some value 1
    Some Key: some value 2
    ```
    then the output is:
    ```
    {
      "Some Key": "some value 2"
    }
    ```
    """

    result = {}
    lines = output.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1
        regexMatch = KEY_VALUE_REGEX.match(line)
        if not regexMatch:
            continue
        key, value = regexMatch.groups()
        text = value
        while i < len(lines) and KEY_VALUE_REGEX.match(lines[i]) is None:
            text += '\n' + lines[i]
            i += 1
        result[key] = text.strip()
    return result
