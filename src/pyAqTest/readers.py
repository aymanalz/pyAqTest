""" A module that provides helpers to read slug test data"""
import pandas as pd
from bs4 import BeautifulSoup

#
# def read_table(fn, num_skip_rows=0, delimiter=" ", time_col=0, displace_col=1):
#     pass


def extract_table_from_insitu_html_file(html_file_path):
    """
    Extracts a table from an HTML file and returns it as a Pandas DataFrame.

    Parameters:
    - html_file_path (str): Path to the HTML file.
    - table_index (int): Index of the table to extract (default is 0 for the first table).

    Returns:
    - pd.DataFrame: Extracted table as a DataFrame.
    """
    with open(html_file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # get table header
    row = soup.find("tr", class_="dataHeader")
    header = [td.get_text(strip=True) for td in row.find_all("td")]

    # get data
    rows = soup.find_all("tr", class_="data")
    df = []
    for row in rows:
        val = [td.get_text(strip=True) for td in row.find_all("td")]
        df.append(val)

    df = pd.DataFrame(df, columns=header)
    df["Date Time"] = pd.to_datetime(df["Date Time"])

    for col in df.columns:
        for word in ["Pressure", "Temperature", "Depth"]:
            if word in col:
                df[col] = df[col].astype(float)
                break

    return df


if __name__ == "__main__":

    # flags to run simple tests
    TEST_EXTRACT_TABLE_FROM_HTML = True

    # read insitu html file
    if TEST_EXTRACT_TABLE_FROM_HTML:
        HTML_FILE_PATH  = (
            r"C:\workspace\projects\pump_tests\6173_Slug Test XD Data\\"
            r"VuSitu_2023-10-02_11-46-04_PM-test_Log_Well1-wet-test.htm"
        )
        extract_table_from_insitu_html_file(HTML_FILE_PATH)
