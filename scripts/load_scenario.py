import json

from pycasting.dataclasses.predictions import Scenario

if __name__ == "__main__":
    with open("../examples/example_scenario.json") as f:
        data = json.load(f)

    sample = Scenario(**data)

    print(sample)
