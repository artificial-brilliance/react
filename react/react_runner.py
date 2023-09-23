
import re

from dataclasses import dataclass
from typing import Callable, Optional, Dict

from cortex import Cortex

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
        cortex = Cortex(self.system_prompt)
        message = text or ''
        for _ in range(self.max_iterations):
            self.log(message)
            response = cortex.process(message)

            self.log(f'Processing:\n{response}\n')
            parsed_output = parseOutput(response)

            if FINAL_ANSWER in parsed_output:
                return parsed_output[FINAL_ANSWER]
            
            if ACTION not in parsed_output:
                message = "Observation: Action not specified"
                continue

            if ACTION_INPUT not in parsed_output:
                message = "Observation: No input to action specified"
                continue

            action = parsed_output[ACTION]
            action_input = parsed_output[ACTION_INPUT]

            if action not in self.actions:
                message = f"Observation: Unrecognized action {action}"
                continue

            self.log(f"Running: {action} {action_input}")
            observation = self.actions[action](action_input)
            message = f"Observation: {observation}"

        return None

def parseOutput(output: str) -> Dict[str, str]:
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
