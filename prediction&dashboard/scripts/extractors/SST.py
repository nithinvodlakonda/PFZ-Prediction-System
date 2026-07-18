from utils import extract_variable

def extract_sst(sst_ds, df):

    df = extract_variable(
        sst_ds,
        "analysed_sst",
        df,
        "SST"
    )

    # Kelvin → Celsius
    df["SST"] = df["SST"] - 273.15

    return df