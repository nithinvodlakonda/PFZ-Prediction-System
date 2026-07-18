from utils import extract_variable


def extract_chl(chl_ds, df):

    return extract_variable(
        chl_ds,
        "CHL",
        df,
        "CHL"
    )