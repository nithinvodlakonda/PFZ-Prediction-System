from global_land_mask import globe


def remove_land(df):
    """
    Remove land points using global_land_mask.
    """

    before = len(df)

    # True = land, False = ocean
    land = globe.is_land(
        df["Latitude"].values,
        df["Longitude"].values
    )

    df = df[~land].reset_index(drop=True)

    after = len(df)

    print(f"Removed {before-after:,} land points")
    print(f"Remaining ocean points: {after:,}")

    return df