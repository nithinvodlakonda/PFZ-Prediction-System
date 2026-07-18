from utils import extract_variable


def extract_sss(sss_ds, df):

    return extract_variable(
        sss_ds,
        "sos",
        df,
        "SSS"
    )