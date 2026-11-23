
from ranking import (
    calculate_recipe_statistics,
    rank_by_simple_average,
    rank_by_weighted_average,
    rank_by_bayesian
)


# Dataset path
interactions_path = "data/raw/RAW_interactions.csv"


# Calculate recipe statistics once
recipe_stats = calculate_recipe_statistics(
    interactions_path=interactions_path
)


# 1. Simple average ranking
simple_results = rank_by_simple_average(
    recipe_stats,
    top_n=20
)


# 2. Weighted average ranking
weighted_results = rank_by_weighted_average(
    recipe_stats,
    m=10,
    top_n=20
)


# 3. Empirical Bayes ranking
bayesian_results = rank_by_bayesian(
    recipe_stats,
    prior_strength=6.999735,
    top_n=20
)


# Display simple average results
print("\nTOP 20 - SIMPLE AVERAGE RANKING")
print("-" * 90)

print(
    simple_results[
        ['rank', 'recipe_id', 'rating_count', 'average_rating']
    ].to_string(index=False)
)


# Display weighted average results
print("\nTOP 20 - WEIGHTED AVERAGE RANKING")
print("-" * 90)

print(
    weighted_results[
        [
            'rank',
            'recipe_id',
            'rating_count',
            'average_rating',
            'weighted_rating'
        ]
    ].to_string(index=False)
)


# Display Bayesian results
print("\nTOP 20 - EMPIRICAL BAYES RANKING")
print("-" * 90)

print(
    bayesian_results[
        [
            'rank',
            'recipe_id',
            'rating_count',
            'average_rating',
            'bayesian_rating'
        ]
    ].to_string(index=False)
)


# Compare recipe overlap across methods
simple_ids = set(simple_results['recipe_id'])
weighted_ids = set(weighted_results['recipe_id'])
bayesian_ids = set(bayesian_results['recipe_id'])


print("\nTOP 20 RANKING OVERLAP ANALYSIS")
print("-" * 90)

print(
    "Simple vs Weighted:",
    len(simple_ids & weighted_ids)
)

print(
    "Simple vs Bayesian:",
    len(simple_ids & bayesian_ids)
)

print(
    "Weighted vs Bayesian:",
    len(weighted_ids & bayesian_ids)
)


# Recipes appearing in all three top 20 lists
common_recipes = (
    simple_ids & weighted_ids & bayesian_ids
)

print(
    "\nRecipes appearing in all three top 20 lists:",
    len(common_recipes)
)


# Identify recipes that differ between Weighted and Bayesian rankings

weighted_only = weighted_ids - bayesian_ids
bayesian_only = bayesian_ids - weighted_ids

print("\nRECIPES ONLY IN WEIGHTED TOP 20")
print("-" * 90)

weighted_only_details = weighted_results[
    weighted_results['recipe_id'].isin(weighted_only)
][
    ['rank', 'recipe_id', 'rating_count', 'average_rating', 'weighted_rating']
]

print(weighted_only_details.to_string(index=False))


print("\nRECIPES ONLY IN BAYESIAN TOP 20")
print("-" * 90)

bayesian_only_details = bayesian_results[
    bayesian_results['recipe_id'].isin(bayesian_only)
][
    ['rank', 'recipe_id', 'rating_count', 'average_rating', 'bayesian_rating']
]

print(bayesian_only_details.to_string(index=False))


print("\nDIFFERENCE SUMMARY")
print("-" * 90)

print("Recipes only in Weighted top 20:", len(weighted_only))
print("Recipes only in Bayesian top 20:", len(bayesian_only))

print("\nCOMPARISON COMPLETED")
