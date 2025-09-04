import plotly.graph_objects as go
import plotly.io as pio
from datetime import date

def make_schematic_plot():
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

    # Layout settings with minimal space above the figure
    fig.update_layout(
        xaxis=dict(title="Distance (m)", range=[-60, 60], zeroline=False),
        yaxis=dict(
            title="Elevation (m)",
            range=[45, 105],
            automargin=False,
            title_standoff=0,
            fixedrange=True,
            showline=True,
            ticks="outside",
            ticklen=5,
            tickwidth=1,
            tickcolor="#444",
        ),
        margin=dict(l=40, r=20, t=10, b=40),  # minimal top margin
        showlegend=True,
        width=700,
        height=400,
        modebar=dict(orientation='v')
    )

    return fig


def XXgenerate_report_old(report_data):
    Analysis_date = date.today()
    well_nmae = "well #1"
    aquifer_name = "aquifer #1"
    aquifer_type = "confined"
    estimated_k = 10
    k_units = "m/day"
    test_type = "Slug Test"
    solution_type = "Butler"
    # --- Example Table Data ---
    table1 = go.Figure(
        data=[
            go.Table(
                header=dict(values=["Col A", "Col B"]),
                cells=dict(values=[[1, 2, 3], [4, 5, 6]]),
            )
        ]
    )
    table2 = go.Figure(
        data=[
            go.Table(
                header=dict(values=["X", "Y"]),
                cells=dict(values=[[10, 20, 30], [40, 50, 60]]),
            )
        ]
    )

    # --- Example Figures ---
    fig1 = go.Figure(data=[go.Scatter(y=[2, 1, 3])])
    fig2 = go.Figure(data=[go.Bar(y=[4, 7, 3])])
    fig_schematic = make_schematic_plot()

    # Convert each Plotly object to HTML fragments
    table1_html = pio.to_html(table1, include_plotlyjs=False, full_html=False)
    fig1_html = pio.to_html(fig1, include_plotlyjs=False, full_html=False)
    table2_html = pio.to_html(table2, include_plotlyjs=False, full_html=False)
    fig2_html = pio.to_html(fig2, include_plotlyjs=False, full_html=False)
    fig_schematic = pio.to_html(fig_schematic, include_plotlyjs=False, full_html=False)

    # Full HTML template with UTF-8 encoding and styled title bar
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Static Report</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
            }}
            .title-bar {{
                background-color: #2c3e50;
                color: white;
                text-align: center;
                font-size: 28px;
                font-weight: bold;
                padding: 20px 0;
            }}
            .container {{
                display: flex;
                justify-content: space-between;
                padding: 20px;
            }}
            .column {{
                width: 48%;
            }}
            .list-above-plot {{
                margin: 15px 0;
                background: #ecf0f1;
                padding: 10px;
                border-radius: 8px;
            }}
            .list-above-plot h3 {{
                margin: 0 0 10px 0;
                font-size: 16px;
                color: blue;
            }}
            .plot-container {{
                margin-top: 20px;
            }}
            .list-above-plot h3.blue-heading {{
            color: #007BFF;
        }}
        </style>
    </head>
    <body>
        <div class="title-bar"> 📉 Slug Test Analysis Report</div>
        <div class="container">
            <!-- Column 1 -->
            <div class="column">


                <!-- List above the first plot -->
                <div class="list-above-plot">
                     <h3 class="blue-heading"> Well Info</h3>
                    <hr>
                    <ul>
                        <li>Well Name : {well_nmae} </li>
                        <li>Aquifer Name : {aquifer_name} </li>
                        <li>Aquifer Type : {aquifer_type} </li>
                        <li>Test Type : {test_type} </li>

                    </ul>
                </div>
                <div class="list-above-plot">
                    <h3 class="blue-heading"> Solution & Parameters</h3>
                    <hr>
                    <ul>
                        <li>Analysis Date: {Analysis_date} </li>
                        <li>Solution Type : {solution_type} </li>
                        <li> K : {estimated_k} {k_units} </li>
                    </ul>
                </div>
                <div class="table-container">{table1_html}</div>
                <div class="plot-container">{fig1_html}</div>
            </div>

            <!-- Column 2 -->
            <div class="column">
                <h3 style="color: blue;">Test Settings</h3>
                <hr>
                <div class="plot-container">{fig_schematic}</div>
                <div class="table-container">{table2_html}</div>
                <div class="plot-container">{fig2_html}</div>
            </div>
        </div>
    </body>
    </html>
    """

    # Save file with UTF-8 encoding to avoid Unicode errors
    with open("trash/report.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def gererate_report(components, fn):
    # components is a list of items.
    # each item can contain one or more subitems (tuples)
    # the item has a tuple (type, content)
    # the type can be "header", "list", "table", "image", "figure"
    # the content is the actual content to be rendered

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Slug Test Analysis Report</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f4f4f4;
            }
            .title-bar {
                background-color: #2c3e50;
                color: white;
                text-align: center;
                font-size: 28px;
                font-weight: bold;
                padding: 20px 0;
                margin-bottom: 20px;
            }
            .section {
                background: white;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .row {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
            }
            .cell {
                flex: 1 1 0;
                min-width: 0;
                margin-right: 0;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            h1, h2 {
                color: #007BFF;
                margin-top: 0;
            }
            ul {
                list-style-type: disc;
                padding-left: 20px;
            }
            .plot-container {
                margin-top: 20px;
            }
            .table-container, .image-container {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100%;
                min-height: 200px;
            }
            img {
                max-width: 100%;
                height: auto;
                display: block;
                margin: 20px 0;
            }
            .list-title, .table-title, .image-title {
                font-weight: bold;
                color: #007BFF;
                font-size: 1.15em;
                margin-bottom: 5px;
                margin-top: 0;
                display: block;
            }
            .list-title-hr, .table-title-hr, .image-title-hr {
                border: none;
                border-top: 2px solid #007BFF;
                margin: 2px 0 10px 0;
                width: 100%;
            }
        </style>                

    </head>
    <body>
        <div class="title-bar"> 📉 Slug Test Analysis Report</div>
    """
    # Process each component and add to HTML
    for section in components:
        html_content += '<div class="section">\n'
        if len(section) > 1:
            html_content += '<div class="row">\n'
        for comp in section:
            # Support optional third element for list/table/image title
            if isinstance(comp, tuple) and len(comp) == 3:
                ctype, content, custom_title = comp
            else:
                ctype = comp[0]
                content = comp[1]
                custom_title = None

            cell_wrap = len(section) > 1
            if cell_wrap:
                html_content += '<div class="cell">\n'

            if ctype == "header1":
                html_content += f"<h1>{content}</h1>\n"
            elif ctype == "header2":
                html_content += f"<h2>{content}</h2>\n"
            elif ctype == "list":
                if custom_title:
                    html_content += f'<div class="list-title">{custom_title}</div>\n'
                    html_content += f'<hr class="list-title-hr"/>\n'
                html_content += "<ul>\n"
                for item in content:
                    html_content += f'  <li style="margin-bottom:4px;"><pre style="font-size:1.15em; margin:0;">{item}</pre></li>\n'
                html_content += "</ul>\n"
            elif ctype == "table":
                if custom_title:
                    html_content += f'<div class="table-title">{custom_title}</div>\n'
                    html_content += f'<hr class="table-title-hr"/>\n'
                import pandas as pd
                if isinstance(content, pd.DataFrame):
                    table_html = content.to_html(
                        classes="pretty-table dataframe",
                        border=0,
                        index=False,
                        escape=False
                    )
                else:
                    table_html = pio.to_html(
                        content, include_plotlyjs=False, full_html=False
                    )
                # Add custom CSS for pretty tables
                html_content += """
                <style>
                .pretty-table {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 10px 0 20px 0;
                    font-size: 1em;
                    background: #fafbfc;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                }
                .pretty-table th, .pretty-table td {
                    border: 1px solid #e1e4e8;
                    padding: 8px 12px;
                    text-align: left;
                }
                .pretty-table th {
                    background-color: #007BFF;
                    color: white;
                    font-weight: bold;
                }
                .pretty-table tr:nth-child(even) {
                    background-color: #f2f6fa;
                }
                </style>
                """
                html_content += f'<div class="table-container">{table_html}</div>\n'
            elif ctype == "figure":
                fig_html = pio.to_html(content, include_plotlyjs=False, full_html=False)
                html_content += f'<div class="plot-container">{fig_html}</div>\n'
            elif ctype == "image":
                if custom_title:
                    html_content += f'<div class="image-title">{custom_title}</div>\n'
                    html_content += f'<hr class="image-title-hr"/>\n'
                html_content += f'<div class="image-container"><img src="{content}" alt="Image"/></div>\n'

            if cell_wrap:
                html_content += '</div>\n'
        if len(section) > 1:
            html_content += '</div>\n'
        html_content += "</div>\n"

    # write to file
    html_content += """
    </body>
    </html>
    """
    with open(fn, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Dynamic report generated:{fn}")
