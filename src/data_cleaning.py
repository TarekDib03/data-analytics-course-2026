"""
Reusable data cleaning utilities.

Import these functions into any notebook rather than redefining fill logic
each time:

    from src.data_cleaning import fill_vars, fill_missing_values
"""

import pandas as pd


def fill_missing_values(df: pd.DataFrame, fill_map: dict) -> pd.DataFrame:
    """
    Fill missing values (NaN) across multiple columns, each with its own
    specified replacement value.

    This is the general-purpose version: use it whenever different columns
    need different fill values in a single call. For the common case where
    several columns all share the same fill value, see `fill_vars` below,
    which is a thin convenience wrapper around this function.

    Intended for categorical columns where missingness itself carries
    meaning (e.g., "no test was performed", "value not recorded"), rather
    than columns where missing values should be statistically imputed or
    where the affected rows should be dropped instead.

    Args:
        df (pd.DataFrame): The DataFrame containing the columns to fill.
        fill_map (dict): Mapping of {column_name: replacement_value}.
            Each column is filled independently with its own value.

    Returns:
        pd.DataFrame: A new DataFrame with missing values filled according
        to fill_map. The original DataFrame is not modified in place.

    Example:
        >>> fill_map = {
        ...     "max_glu_serum": "Not tested",
        ...     "A1Cresult": "Not tested",
        ...     "payer_code": "Unknown",
        ...     "medical_specialty": "Unknown",
        ...     "race": "Unknown",
        ...     "diag_2": "None recorded",
        ...     "diag_3": "None recorded",
        ... }
        >>> diabetic_df_cleaned = fill_missing_values(diabetic_df, fill_map)
    """
    return df.fillna(value=fill_map)


def fill_vars(df: pd.DataFrame, vars_list: list, replaced_val: str) -> pd.DataFrame:
    """
    Fill missing values (NaN) in one or more columns with the SAME
    replacement value.

    Convenience wrapper around `fill_missing_values` for the common case
    where a group of columns should all be filled identically (e.g., every
    clinical test-result column should become "Not tested"). If different
    columns need different fill values, use `fill_missing_values` directly
    with a full {column: value} mapping instead.

    Args:
        df (pd.DataFrame): The DataFrame containing the columns to fill.
        vars_list (list[str]): Column names to apply the fill to. All
            columns in this list receive the same replacement value.
        replaced_val (str): The value used to replace NaN in each column.

    Returns:
        pd.DataFrame: A new DataFrame with missing values filled in the
        specified columns. The original DataFrame is not modified in place.

    Example:
        >>> clinical_variables = ["max_glu_serum", "A1Cresult"]
        >>> diabetic_df_cleaned = fill_vars(diabetic_df_cleaned, clinical_variables, "Not tested")

        >>> admin_variables = ["payer_code", "medical_specialty"]
        >>> diabetic_df_cleaned = fill_vars(diabetic_df_cleaned, admin_variables, "Unknown")
    """
    fill_map = {var: replaced_val for var in vars_list}
    return fill_missing_values(df, fill_map)
