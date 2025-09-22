from graphviz import Digraph

# Create a flowchart for slug test method selection
dot = Digraph("SlugTestMethods", format="png")
dot.attr(rankdir="TB", size="8")

# Nodes
dot.node("A", "Slug Test Data", shape="box", style="rounded,filled", fillcolor="lightblue")
dot.node("B", "Aquifer Type / Well Conditions?", shape="diamond", style="filled", fillcolor="lightgrey")

# Methods
dot.node("C1", "Hvorslev (1951)\nLow-K aquifers", shape="box", style="rounded,filled", fillcolor="lightyellow")
dot.node("C2", "Bouwer & Rice (1976)\nUnconfined, partial penetration", shape="box", style="rounded,filled", fillcolor="lightyellow")
dot.node("C3", "Cooper–Bredehoeft–Papadopulos (1967)\nConfined, wellbore storage", shape="box", style="rounded,filled", fillcolor="lightyellow")
dot.node("C4", "Butler (1998+) / Curve Fitting\nAnisotropy, modern extensions", shape="box", style="rounded,filled", fillcolor="lightyellow")

# Edges
dot.edge("A", "B")
dot.edge("B", "C1", label="Low-K")
dot.edge("B", "C2", label="Unconfined,\npartial screen")
dot.edge("B", "C3", label="Confined,\nwell storage")
dot.edge("B", "C4", label="Complex/\nmodern analysis")

# Render to file
output_path = "slug_test_methods_flowchart"
dot.render(output_path)

output_path + ".png"
