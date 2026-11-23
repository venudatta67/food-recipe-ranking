
import pandas as pd
import ast


def load_recipe_data(recipes_path):
    """
    Load the raw Food.com recipe dataset.

    Parameters
    ----------
    recipes_path : str
        Path to the raw recipe CSV file.

    Returns
    -------
    pandas.DataFrame
        Loaded recipe dataset.
    """

    recipes = pd.read_csv(recipes_path)

    return recipes



def clean_recipe_data(recipes):
    """
    Clean the Food.com recipe dataset.

    Cleaning operations:
    1. Remove recipes with missing or blank names.
    2. Convert zero cooking times to missing values.
    3. Convert submission dates to datetime format.
    4. Reset the DataFrame index.

    Parameters
    ----------
    recipes : pandas.DataFrame
        Raw recipe dataset.

    Returns
    -------
    pandas.DataFrame
        Cleaned recipe dataset.
    """

    # Create a copy to protect the original DataFrame
    cleaned_recipes = recipes.copy()

    # Remove recipes with missing or blank names
    cleaned_recipes = cleaned_recipes[
        cleaned_recipes['name'].notna()
        & cleaned_recipes['name'].str.strip().ne('')
    ].copy()

    # Treat zero cooking times as missing values
    cleaned_recipes.loc[
        cleaned_recipes['minutes'] == 0,
        'minutes'
    ] = pd.NA

    # Convert submission dates to datetime
    cleaned_recipes['submitted'] = pd.to_datetime(
        cleaned_recipes['submitted'],
        errors='coerce'
    )

    # Reset index after cleaning
    cleaned_recipes = cleaned_recipes.reset_index(drop=True)

    return cleaned_recipes


def process_nutrition_data(recipes):
    """
    Convert the nutrition column from string lists
    into separate numerical columns.

    The nutrition list contains seven values:
    calories, total fat, sugar, sodium, protein,
    saturated fat, and carbohydrates.

    Returns
    -------
    pandas.DataFrame
        Recipe dataset with separate nutrition columns.
    """

    # Create a copy to protect the original DataFrame
    processed_recipes = recipes.copy()

    # Convert string representations into Python lists
    nutrition_values = processed_recipes['nutrition'].apply(
        ast.literal_eval
    )

    # Define nutrition column names
    nutrition_columns = [
        'calories',
        'total_fat_pdv',
        'sugar_pdv',
        'sodium_pdv',
        'protein_pdv',
        'saturated_fat_pdv',
        'carbohydrates_pdv'
    ]

    # Convert lists into separate DataFrame columns
    nutrition_df = pd.DataFrame(
        nutrition_values.tolist(),
        columns=nutrition_columns,
        index=processed_recipes.index
    )

    # Convert nutrition values to numeric types
    nutrition_df = nutrition_df.apply(
        pd.to_numeric,
        errors='coerce'
    )

    # Add nutrition columns to recipe dataset
    processed_recipes = pd.concat(
        [processed_recipes, nutrition_df],
        axis=1
    )

    # Remove original nutrition string column
    processed_recipes = processed_recipes.drop(
        columns=['nutrition']
    )

    return processed_recipes


def process_list_columns(recipes):
    """
    Convert tags, ingredients, and steps columns
    from string representations into Python lists.

    Returns
    -------
    pandas.DataFrame
        Recipe dataset with properly processed list columns.
    """

    # Create a copy to protect the original DataFrame
    processed_recipes = recipes.copy()

    # Columns containing string representations of lists
    list_columns = [
        'tags',
        'ingredients',
        'steps'
    ]

    # Convert each string representation into a Python list
    for column in list_columns:
        processed_recipes[column] = processed_recipes[column].apply(
            ast.literal_eval
        )

    return processed_recipes


def create_recipe_features(recipes):
    """
    Create additional useful features for each recipe.

    Features:
    - ingredient_count
    - tag_count
    - step_count

    Returns
    -------
    pandas.DataFrame
        Recipe dataset with additional features.
    """

    # Create a copy to protect the original DataFrame
    featured_recipes = recipes.copy()

    # Count ingredients in each recipe
    featured_recipes['ingredient_count'] = (
        featured_recipes['ingredients'].apply(len)
    )

    # Count tags associated with each recipe
    featured_recipes['tag_count'] = (
        featured_recipes['tags'].apply(len)
    )

    # Count cooking instructions in each recipe
    featured_recipes['step_count'] = (
        featured_recipes['steps'].apply(len)
    )

    return featured_recipes


def save_processed_data(recipes, output_path):
    """
    Save the processed recipe dataset as a CSV file.

    Parameters
    ----------
    recipes : pandas.DataFrame
        Fully processed recipe dataset.

    output_path : str
        Destination path for the processed CSV file.

    Returns
    -------
    None
    """

    # Save the processed dataset without the DataFrame index
    recipes.to_csv(
        output_path,
        index=False
    )

    print(f"Processed recipe data saved successfully: {output_path}")


def load_processed_data(input_path):
    """
    Load the saved processed recipe dataset.

    Restore list columns and submission dates
    to their appropriate Python data types.

    Parameters
    ----------
    input_path : str
        Path to the processed recipe CSV file.

    Returns
    -------
    pandas.DataFrame
        Loaded and restored recipe dataset.
    """

    # Load the processed CSV file
    recipes = pd.read_csv(input_path)

    # Restore columns containing Python lists
    list_columns = [
        'tags',
        'ingredients',
        'steps'
    ]

    for column in list_columns:
        recipes[column] = recipes[column].apply(
            ast.literal_eval
        )

    # Restore submission dates to datetime
    recipes['submitted'] = pd.to_datetime(
        recipes['submitted'],
        errors='coerce'
    )

    return recipes


# Interactions dataset processing functions
def clean_interaction_data(interactions):
    """
    Clean the Food.com user interaction dataset.

    - Creates a copy of the original dataset.
    - Converts the date column to datetime.
    - Preserves all interaction records, including zero ratings
      and missing reviews.
    """

    # Create a copy to protect the original dataset
    interactions = interactions.copy()

    # Convert date column to datetime
    interactions["date"] = pd.to_datetime(
        interactions["date"],
        errors="coerce"
    )

    return interactions
