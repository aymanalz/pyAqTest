import plotly.graph_objects as go


# Example coordinates
def add_schematic_drawing():
    well_x = 0
    ground_surface = 100
    water_table = 85
    screen_top = 70
    screen_bottom = 60
    bedrock = 50  # bedrock elevation

    fig = go.Figure()

    # Ground surface
    fig.add_trace(
        go.Scatter(
            x=[-50, 50],
            y=[ground_surface, ground_surface],
            mode="lines",
            name="Ground Surface",
            line=dict(color="saddlebrown", width=3),
        )
    )

    # Water table
    fig.add_trace(
        go.Scatter(
            x=[-50, 50],
            y=[water_table, water_table],
            mode="lines",
            name="Water Table",
            line=dict(color="blue", dash="dash", width=2),
        )
    )

    # Bedrock
    fig.add_trace(
        go.Scatter(
            x=[-50, 50],
            y=[bedrock, bedrock],
            mode="lines",
            name="Bedrock",
            line=dict(color="gray", dash="dot", width=3),
        )
    )

    # Well casing
    rw = 1
    fig.add_trace(
        go.Scatter(
            x=[well_x - rw, well_x + rw, well_x + rw, well_x - rw, well_x - rw],
            y=[
                ground_surface,
                ground_surface,
                screen_bottom,
                screen_bottom,
                ground_surface,
            ],
            mode="lines",
            name="Well Casing",
            line=dict(color="black", width=2),
        )
    )

    # Screen interval
    fig.add_trace(
        go.Scatter(
            x=[well_x - 1, well_x + 1, well_x + 1, well_x - 1, well_x - 1],
            y=[screen_top, screen_top, screen_bottom, screen_bottom, screen_top],
            fill="toself",
            name="Screen Interval",
            fillcolor="lightgreen",
            line=dict(color="green"),
        )
    )

    # Layout settings
    fig.update_layout(
        title="Well Cross Section",
        xaxis=dict(title="Distance (m)", range=[-60, 60], zeroline=False),
        yaxis=dict(title="Elevation (m)", range=[45, 105]),
        showlegend=True,
        width=700,
        height=500,
    )

    fig.show()
