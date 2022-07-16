"""The script to visualize the problem"""
from dataclasses import dataclass
from pathlib import Path
import problem
import sys

OUT_FILE = Path("visual.svg")

@dataclass
class VisualizationConfig:
    size: int = 700
    city_color: str = "rgb(0, 0, 0)"
    convexal_city_color: str = "rgb(0, 0, 255)"

def create_visual(problem_file):
    with Path(problem_file).open("r") as f:
        p = problem.Problem.parse(f.readlines())
        svg = p.visualize_convexal_as_svg(VisualizationConfig())
    with OUT_FILE.open("w") as f:
        f.write(str(svg))

if __name__ == "__main__":
    create_visual(sys.argv[1])
