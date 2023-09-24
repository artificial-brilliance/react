
import os
import json
import requests

from dataclasses import dataclass
from pathlib import Path
from typing import cast, Callable, Dict

API_KEY = os.environ["VALUE_SERP_API_KEY"]

@dataclass
class Search(object):
    log: Callable[[str], None]

    def search(self, query: str) -> str:
      cache_file = os.path.join(Path.home(), '.search_cache')
      if not os.path.exists(cache_file):
          Path(cache_file).write_text('{}')

      with open(cache_file, 'r') as f:
          cache = cast(Dict[str, str], json.load(f))
      
      if query in cache:
          self.log(f'Cache hit for query "{query}"')
          return cache[query]

      self.log(f'Cache miss for query "{query}"')
      params = {
          "api_key": API_KEY,
          "q": query,
      }

      response = requests.get('https://api.valueserp.com/search', params).json()

      result = None
      if 'answer_box' in response:
        answer_box = response['answer_box']
        if 'answers' in answer_box:
            answers = answer_box['answers']
            if len(answers) > 0:
                first = answers[0]
                if 'answer' in first:
                    result = first['answer']

      if result is None:
          if 'organic_results' in response:
              organic_results = response['organic_results']
              if len(organic_results) > 0:
                  first = organic_results[0]
                  if 'snippet' in first:
                      result = first['snippet']

      if result is None:
          result = 'Not found'

      cache[query] = result

      with open(cache_file, 'w') as f:
          json.dump(cache, f)

      return result
