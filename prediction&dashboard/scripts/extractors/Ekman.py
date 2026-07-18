from utils import extract_variable

def extract_ekman(ekman_ds, df):

    df = extract_variable(
        ekman_ds,
        "M_x",
        df,
        "Ekman_X"
    )

    df = extract_variable(
        ekman_ds,
        "M_y",
        df,
        "Ekman_Y"
    )

    return df