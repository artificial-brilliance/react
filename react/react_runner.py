
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
    # The actions (i.e. tools) that the LLM can perform/run
    # The key is the name of the tool and the value is the callable
    # to run for that tool
    actions: Dict[str, Callable[[str], str]]
    # The system prompt that describes what the LLM should do
    system_prompt: str
    # A callable that is called whenever a log statement is made
    log: Callable[[str], None]
    # The max number of react loops that will be performed
    # This helps prevent infinite loops
    max_iterations: int

    def run(self, text: Optional[str] = None) -> Optional[str]:
        """
        Starts the ReAct loop with the optional initial text.
        """
        chatbot = Chatbot(self.system_prompt)
        message = text or ''
        for _ in range(self.max_iterations):
            # Get the response from the LLM
            # This should be of the form:
            #
            # Thought: ...
            # Action: ...
            # Action Input: ...
            # Observation: ...
            self.log(message)
            response = chatbot.process(message)

            # Parses the output from LLM into key-value pairs
            self.log(f'Response:\n{response}\n')
            parsed_output = parseOutput(response)

            # If the FINAL_ANSWER key is in the output return the result
            if FINAL_ANSWER in parsed_output:
                return parsed_output[FINAL_ANSWER]

            # If the ACTION key is not in the output specify an observation
            # that the model didn't provide an action to give it a hint
            # for future loops to provide an action
            if ACTION not in parsed_output:
                message = "Observation: I didn't specify an action to perform"
                continue

            # Similar to above, if the ACTION_INPUT is not in the output,
            # use an observation to let the LLM know
            if ACTION_INPUT not in parsed_output:
                message = "Observation: I specified an action, but not an input for it"
                continue

            action = parsed_output[ACTION]
            action_input = parsed_output[ACTION_INPUT]

            # Also similar to above, if the action given is invalid,
            # uses an observation that tells the LLM so that, in future
            # loops, it might correct itself
            if action not in self.actions:
                message = f"Observation: I specified an unrecognized {action}"
                continue

            # Invoke the action and have the next message in the
            # conversation to be an observation whose value is the
            # result of the action's tool
            self.log(f"Running: {action} {action_input}")
            observation = self.actions[action](action_input)
            message = f"Observation: {observation}"

        # If this point is reached, it means a FINAL_ANSWER key was
        # never found and max iterations were reached.  Thus, there
        # is not an answer.
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
