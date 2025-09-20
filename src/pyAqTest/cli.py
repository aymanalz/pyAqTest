import os
import shutil
from os import mkdir

import pandas as pd
import typer
from rich.console import Console
from rich.text import Text
from rich.table import Table

import pyAqTest.utils
from art import *

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Show banner."""
    clear_screen()
    banner_text = Text("Slug Test Analysis", style="bold magenta", justify="center")
    tit = text2art("AqTest", font="tarty1")
    indent = 50
    for line in tit.splitlines():
        console.print(" " * indent + line)

    console.rule("[bold green]AqTest")
    console.print(banner_text)
    console.rule()

    # get folder of htm files
    #while True:
        # batch_file = typer.prompt(
        #     "📂 Enter the path to the configuration file:"
        # )
        # if os.path.isdir(batch_file):
        #     console.print(f"[bold green]✅ file found:[/] {batch_file}")
        #     # htm_files = os.listdir(batch_file)
        #     # htm_files = [f for f in htm_files if f.endswith(".htm")]
        #     # console.print(f"📄 Number of files found is {len(htm_files)} ...")
        #     break
        # else:
        #     console.print(
        #         f"[bold red]❌ Error:[/] file not found at [yellow]{batch_file}[/]"
        #     )
        #     console.print("Try again ...")

    # # get units
    # while True:
    #     length_unit = typer.prompt("  - Enter length unit (m or ft):")
    #     if length_unit.lower() in ["m", "ft"]:
    #         console.print(f"[bold green]✅ Length unit set to:[/] {length_unit}")
    #         break
    # while True:
    #     time_unit = typer.prompt("  - Enter time unit (s, min, or hr):")
    #     if time_unit.lower() in ["s", "min", "hr"]:
    #         console.print(f"[bold green]✅ Time unit set to:[/] {time_unit}")
    #         break

    # # get output folder
    # while True:
    #     output_dir = typer.prompt(
    #         "\n\nEnter the path for the folder where the analysis results will be saved.. "
    #     )
    #     if os.path.isdir(output_dir):
    #         console.print(f"Folder exists:{output_dir}, Do you want to remove it❓")
    #         yes_no = typer.prompt("y|n?")
    #         if "n" in yes_no:
    #             continue
    #         if "y" in yes_no:
    #             shutil.rmtree(output_dir)
    #             console.print(f"Folder {output_dir} removed successfully..")

    #     os.makedirs(output_dir)
    #     console.print(
    #         f"Empty Folder {output_dir}  is created at {os.path.abspath(output_dir)}"
    #     )
    #     break

    # extract csv from html
    # console.print("\n\n⏳ Working on extracting slug test recovery data... ")
    # slug_csv_dir = os.path.join(output_dir, "test_csv_files")
    # mkdir(slug_csv_dir)
    # skip_word = "DRY"
    # pyAqTest.utils.in_situ_tests_to_csv(
    #     input_folder=batch_file,
    #     output_folder=output_dir,
    #     skip_word=skip_word,
    #     file_extension="htm",
    #     slug_data_folder=slug_csv_dir,
    # )
    # n_csv_files = len(os.listdir(slug_csv_dir))
    # console.print(
    #     f" 🟢 {n_csv_files} csv files with slug recovery data were generated at {slug_csv_dir}"
    # )
    # console.print("\n\n" + 25 * " " + 30 * " ░░░", style="sandy_brown")

    # # Batch file entry
    # console.print(
    #     "\n\n📦 To implement batch slug processing, you will need a csv file with tests information needed."
    # )
    # console.print("📦 Here is an example ...\n\n")
    # get_slug_data_example()

    #
    while True:
        ini_filename = typer.prompt("\n\nEnter the configuration file .. ")
        if not (os.path.isfile(ini_filename)):
            console.print("❌File does not exist ...")
            continue
        if ini_filename.lower().endswith(".ini"):
            break
        else:
            print("This is NOT an ini file.")
            continue

    batch = pyAqTest.Batch_Processing(config_obj=ini_filename)
    console.print("\n\n ⚙️ Batch slug test settings ...")
    console.print("------------------------------------------")
    console.print(f"Configuration file: {ini_filename}")
    console.print(f"Batch data file: {batch.batch_data_file}")
    console.print(f"Output folder: {batch.output_folder}")    
    console.print(f"Time unit: {batch.time_unit}")
    console.print(f"Length unit: {batch.length_unit}")
    console.print(f"Number of tests: {batch.df_batch.shape[1]}")
    batch_dataCopy = batch.df_batch[["field", "1", "2", "3"]].copy()
    batch_dataCopy.set_index("field", inplace=True)
    table2console(
        console,
        batch_dataCopy,
        title="First three tests in the batch processing table!",
    )

   

    console.print("\n\n 🔄 Running the slug test analysis ...")
    batch.run_batch()

    # #output_dir_slug = os.path.join(output_dir, "fit_results")
    # batch_data = pd.read_csv(batch_file)

    # mask = batch_data["field"] == "test_data_file"
    # for col in batch_data.columns:
    #     if "field" in col:
    #         continue
    #     nm = batch_data.loc[mask, col].values[0]
    #     nm = os.path.join(slug_csv_dir, nm)
    #     batch_data.loc[mask, col] = nm

    # table2console(
    #     console,
    #     batch_data.set_index("field")[["1", "2", "3"]],
    #     title="First three tests in the batch processing table!",
    # )
    # batch_data = batch_data.set_index("field").transpose()
    # df_results = pyAqTest.run_batch(
    #     batch_data=batch_data,
    #     output_dir=output_dir,
    #     time_unit=time_unit,
    #     length_unit=length_unit,
    # )
    console.print("\n\n 📊 Done! Results can be found at: ...")
    res_out = os.path.join(batch.output_folder, "estimated_conductivity.csv")
    fn_plots = os.path.join(batch.output_folder, "fit_plots")
    recovery_splits = os.path.join(batch.output_folder, "recovery_splits")
    console.print("   (1) Estimated Parameters: ", res_out)
    console.print("   (2) Fit plots: ", fn_plots)
    console.print("   (3) Splitting Recovery Plots: ", recovery_splits)   

    

    console.print("\n\n✅ Analysis completed ...")
    # console.print(f"✅ Estimated Parameters can be found at {fn_results}...")
    # console.print(f"✅ Fitting plots can be found at {fn_plots}...")
    # console.print("[bold blue]Estimated Parameters :[/bold blue]")
    # pd.set_option("display.float_format", "{:.2f}".format)
    # table2console(
    #     console,
    #     df_results.set_index("test_name"),
    #     title="Estimated Parameters & fit metrics",
    # )


def table2console(console, df: pd.DataFrame, title):
    """
    Prints a Pandas DataFrame to the console using the Rich library for enhanced
    and formatted output. The index is included and styled in light blue.
    """
    if not isinstance(df, pd.DataFrame):
        console.print("[red]Error: Input must be a Pandas DataFrame.[/red]")
        return

    console.print(f"\n[bold green]{title}:[/bold green]")

    # Create the Rich table
    table = Table(
        show_header=True, header_style="bold magenta", row_styles=["none", "dim"]
    )

    # Add index column first
    table.add_column("Index", style="bright_blue", no_wrap=True)

    # Add the rest of the DataFrame columns
    for col in df.columns:
        table.add_column(str(col), justify="left")

    # Add rows with index
    for idx, row in df.iterrows():
        index_str = f"[bright_blue]{idx}[/bright_blue]"
        table.add_row(
            index_str, *[str(adaptive_format(item, 3)) for item in row.values]
        )

    console.print(table)


def adaptive_format(x, decimals=2):
    """Format float adaptively: fixed decimals or scientific if too small."""
    if isinstance(x, str):
        return x  # Skip strings
    if abs(x) >= 10**-decimals:
        return f"{x:.{decimals}f}"
    else:
        return f"{x:.1e}"


def get_slug_data_example():
    columns = [
        "test_id",
        "test_type",
        "aquifer_name",
        "aquifer_type",
        "aquifer_thickness",
        "anisotropy",
        "water_table_depth",
        "well_name",
        "well_radius",
        "casing_radius",
        "screen_length",
        "screen_top_depth",
        "test_data_file",
        "ground_surface_elevation",
        "slug_volume",
    ]

    data = [
        {
            "test_id": "test_1",
            "test_type": "slug",
            "aquifer_name": "Aquifer_1",
            "aquifer_type": "unconfined",
            "aquifer_thickness": "50.6",
            "anisotropy": "1",
            "water_table_depth": "10",
            "well_name": "Well_1",
            "well_radius": "0.125",
            "casing_radius": "0.064",
            "screen_length": "1.52",
            "screen_top_depth": "28.54",
            "test_data_file": "test_1.csv",
            "ground_surface_elevation": "100",
            "slug_volume": "",
        },
        {
            "test_id": "test_2",
            "test_type": "slug",
            "aquifer_name": "Aquifer_1",
            "aquifer_type": "unconfined",
            "aquifer_thickness": "50.6",
            "anisotropy": "1",
            "water_table_depth": "10",
            "well_name": "Well_2",
            "well_radius": "0.125",
            "casing_radius": "0.064",
            "screen_length": "1.52",
            "screen_top_depth": "28.54",
            "test_data_file": "test_2.csv",
            "ground_surface_elevation": "100",
            "slug_volume": "",
        },
        {
            "test_id": "test_3",
            "test_type": "slug",
            "aquifer_name": "Aquifer_1",
            "aquifer_type": "unconfined",
            "aquifer_thickness": "50.6",
            "anisotropy": "1",
            "water_table_depth": "10",
            "well_name": "Well_3",
            "well_radius": "0.125",
            "casing_radius": "0.064",
            "screen_length": "1.52",
            "screen_top_depth": "28.54",
            "test_data_file": "test_3.csv",
            "ground_surface_elevation": "100",
            "slug_volume": "",
        },
    ]

    # Create table with first column as field names
    table = Table(title="Slug Test Example", title_style="bold blue")

    # Add first column: field names
    table.add_column(" ", style="cyan", no_wrap=True)

    # Add one column per data record, use test_id for header
    for iid, d in enumerate(data):
        table.add_column(str(iid + 1), style="white")

    # For each field (column in original), add a row with field name and all values
    for field in columns:
        row = [field]  # first cell is the field name
        for d in data:
            row.append(str(d.get(field, "")))
        table.add_row(*row)

    console.print(table)


def clear_screen():
    """Clears the console screen."""
    # For Windows
    if os.name == "nt":
        _ = os.system("cls")
    # For macOS and Linux (Unix-like systems)
    else:
        _ = os.system("clear")




if __name__ == "__main__":
    app()
