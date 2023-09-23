import unittest

from react.react_runner import parseOutput

class ReactRunnerTest(unittest.TestCase):
    def testParsedOutput(self):
        self.assertEqual(parseOutput("""
Line that should not be in parsed output
Thought: some
thought
Action: some action
and more

Observation: some observation
Empty:
"""), {
    "Thought": "some\nthought",
    "Action": "some action\nand more",
    "Observation": "some observation",
    "Empty": "",
})
