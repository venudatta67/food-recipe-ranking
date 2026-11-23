
import pandas as pd

def calculate_recipe_statistics(
    interactions_path,
    chunksize=100000
):
    """
    Calculate valid rating statistics for every recipe.

    Only ratings between 1 and 5 are considered.
    """

    all_parts = []

    # Read interaction data in chunks
    for chunk in pd.read_csv(
        interactions_path,
        usecols=['recipe_id', 'rating'],
        chunksize=chunksize
    ):

        # Exclude zero and invalid ratings
        valid = chunk[
            chunk['rating'].between(1, 5)
        ]

        # Calculate recipe-level statistics
        part = valid.groupby('recipe_id')['rating'].agg(
            rating_count='count',
            rating_sum='sum',
            rating_squared_sum=lambda x: (x ** 2).sum(),
            minimum_rating='min',
            maximum_rating='max'
       )

        all_parts.append(part)

    # Combine statistics from all chunks
    recipe_stats = (
        pd.concat(all_parts)
        .groupby(level=0)
        .agg({
            'rating_count': 'sum',
            'rating_sum': 'sum',
            'rating_squared_sum': 'sum',
            'minimum_rating': 'min',
            'maximum_rating': 'max'
        })
    )

    # Calculate average rating
    recipe_stats['average_rating'] = (
        recipe_stats['rating_sum'] /
        recipe_stats['rating_count']
    )

    return recipe_stats



def calculate_rating_correlations(recipe_stats):
    """
    Calculate Pearson and Spearman correlations between
    recipe rating count and average rating.

    Parameters
    ----------
    recipe_stats : pandas.DataFrame
        Recipe-level statistics containing rating_count
        and average_rating.

    Returns
    -------
    pandas.Series
        Number of recipes analysed, Pearson correlation,
        and Spearman correlation.
    """

    # Verify that the required columns exist
    required_columns = ['rating_count', 'average_rating']

    missing_columns = [
        column for column in required_columns
        if column not in recipe_stats.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Select required variables and remove missing values
    correlation_data = recipe_stats[
        required_columns
    ].dropna()

    # Ensure sufficient observations are available
    if len(correlation_data) < 2:
        raise ValueError(
            "At least two valid observations are required."
        )

    # Calculate Pearson correlation
    pearson_corr = correlation_data[
        'rating_count'
    ].corr(
        correlation_data['average_rating'],
        method='pearson'
    )

    # Calculate Spearman correlation using ranked values
    ranked_data = correlation_data.rank()

    spearman_corr = ranked_data[
    'rating_count'
    ].corr(
    ranked_data['average_rating'],
    method='pearson'
    )

    # Return results
    return pd.Series({
        'number_of_recipes': len(correlation_data),
        'pearson_correlation': pearson_corr,
        'spearman_correlation': spearman_corr
    })


# Ranking using a simple average rating, which does not account for the number of ratings or prior weight.
def rank_by_simple_average(recipe_stats, top_n=20):
    """
    Rank recipes using simple average ratings.

    Recipes with higher average ratings appear first.
    """

    ranked_recipes = (
        recipe_stats
        .reset_index()
        .sort_values(
    ['average_rating', 'rating_count', 'recipe_id'],
    ascending=[False, False, True]
    )
        .reset_index(drop=True)
    )

    # Add ranking position
    ranked_recipes.insert(
        0,
        'rank',
        range(1, len(ranked_recipes) + 1)
    )

    return ranked_recipes.head(top_n)


# Ranking using a weighted average rating, which accounts for the number of ratings and a prior weight.
def rank_by_weighted_average(
    recipe_stats,
    m=10,
    top_n=20
):
    """
    Rank recipes using a weighted average rating.

    m represents the prior weight.
    C represents the global average rating.
    """

    ranked_recipes = recipe_stats.reset_index().copy()

    # Calculate the overall average rating
    global_average = (
        ranked_recipes['rating_sum'].sum() /
        ranked_recipes['rating_count'].sum()
    )

    # Calculate weighted average rating
    ranked_recipes['weighted_rating'] = (
        (
            ranked_recipes['rating_count'] *
            ranked_recipes['average_rating']
        ) +
        (m * global_average)
    ) / (
        ranked_recipes['rating_count'] + m
    )

    # Sort recipes by weighted rating
    ranked_recipes = ranked_recipes.sort_values(
        ['weighted_rating', 'recipe_id'],
        ascending=[False, True]
    ).reset_index(drop=True)

    # Assign ranking positions
    ranked_recipes.insert(
        0,
        'rank',
        range(1, len(ranked_recipes) + 1)
    )

    return ranked_recipes.head(top_n)

# Ranking using Empirical Bayes with data-estimated prior strength.
def rank_by_bayesian(
    recipe_stats,
    prior_strength=6.999735,
    top_n=20
):
    """
    Rank recipes using an Empirical Bayes approach.

    prior_strength represents the estimated prior weight.
    The prior mean is calculated from the global average rating.

    The prior strength is estimated using:
    within-recipe variance / between-recipe variance.
    """

    # Create a copy of recipe statistics
    ranked_recipes = recipe_stats.reset_index().copy()

    # Calculate the global average rating
    global_average = (
        ranked_recipes['rating_sum'].sum() /
        ranked_recipes['rating_count'].sum()
    )

    # Calculate Bayesian-adjusted rating
    ranked_recipes['bayesian_rating'] = (
        (
            ranked_recipes['rating_count'] *
            ranked_recipes['average_rating']
        ) +
        (prior_strength * global_average)
    ) / (
        ranked_recipes['rating_count'] + prior_strength
    )

    # Sort recipes by Bayesian-adjusted rating
    ranked_recipes = ranked_recipes.sort_values(
        ['bayesian_rating', 'recipe_id'],
        ascending=[False, True]
    ).reset_index(drop=True)

    # Assign ranking positions
    ranked_recipes.insert(
        0,
        'rank',
        range(1, len(ranked_recipes) + 1)
    )

    return ranked_recipes.head(top_n)
