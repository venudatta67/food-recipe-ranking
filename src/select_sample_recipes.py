
from collections import Counter, defaultdict

import pandas as pd


INTERACTIONS_PATH = "data/raw/RAW_interactions.csv"
RECIPES_PATH = "data/raw/RAW_recipes.csv"

CHUNK_SIZE = 100_000
SAMPLE_PER_GROUP = 250
RANDOM_SEED = 42

# Special recipes verified in the previous stage
SPECIAL_RECIPE_IDS = [5289, 261647, 176767]


print("Scanning interactions and collecting recipe candidates...")

interaction_counts = Counter()
valid_rating_counts = Counter()
rating_recipe_ids = defaultdict(set)
missing_review_recipe_ids = set()

for chunk_number, chunk in enumerate(
    pd.read_csv(INTERACTIONS_PATH, chunksize=CHUNK_SIZE),
    start=1
):
    interaction_counts.update(
        chunk["recipe_id"].value_counts().to_dict()
    )

    valid = chunk[chunk["rating"].between(1, 5)]

    valid_rating_counts.update(
        valid["recipe_id"].value_counts().to_dict()
    )

    for rating in range(6):
        ids = chunk.loc[
            chunk["rating"] == rating, "recipe_id"
        ].unique()

        rating_recipe_ids[rating].update(ids)

    missing_ids = chunk.loc[
        chunk["review"].isna(), "recipe_id"
    ].unique()

    missing_review_recipe_ids.update(missing_ids)

    print(f"Processed chunk {chunk_number}")


# Create the five valid-rating-count groups
rating_groups = {
    "1-5": [],
    "6-10": [],
    "11-50": [],
    "51-100": [],
    "101+": []
}

for recipe_id, count in valid_rating_counts.items():
    if 1 <= count <= 5:
        rating_groups["1-5"].append(recipe_id)
    elif 6 <= count <= 10:
        rating_groups["6-10"].append(recipe_id)
    elif 11 <= count <= 50:
        rating_groups["11-50"].append(recipe_id)
    elif 51 <= count <= 100:
        rating_groups["51-100"].append(recipe_id)
    else:
        rating_groups["101+"].append(recipe_id)


# Use a fixed seed to make the selection reproducible
selected_ids = set()

for group_name, recipe_ids in rating_groups.items():
    sampled = (
        pd.Series(recipe_ids)
        .sample(
            n=SAMPLE_PER_GROUP,
            random_state=RANDOM_SEED
        )
        .tolist()
    )

    selected_ids.update(sampled)

    print(
        f"Selected {len(sampled)} recipes "
        f"from group {group_name}"
    )


# Add verified special recipes
selected_ids.update(SPECIAL_RECIPE_IDS)


# Ensure every rating value from 0 to 5 is represented
for rating in range(6):
    if not any(
        recipe_id in selected_ids
        for recipe_id in rating_recipe_ids[rating]
    ):
        selected_ids.add(
            min(rating_recipe_ids[rating])
        )


# Ensure at least one recipe with a missing review
if not selected_ids.intersection(missing_review_recipe_ids):
    selected_ids.add(min(missing_review_recipe_ids))


# Ensure at least one recipe with interactions but no valid ratings
no_valid_rating_ids = (
    set(interaction_counts) - set(valid_rating_counts)
)

if not selected_ids.intersection(no_valid_rating_ids):
    selected_ids.add(min(no_valid_rating_ids))


# Check that every selected ID exists in the recipe dataset
recipes = pd.read_csv(
    RECIPES_PATH,
    usecols=["id"]
)

available_recipe_ids = set(recipes["id"])

missing_from_recipes = selected_ids - available_recipe_ids


print("\n========== SELECTION SUMMARY ==========")
print(f"Base sample target: {SAMPLE_PER_GROUP * 5:,}")
print(f"Total unique selected IDs: {len(selected_ids):,}")
print(f"Selected IDs missing from recipes dataset: {len(missing_from_recipes)}")

print("\nSPECIAL RECIPE INCLUSION")

for recipe_id in SPECIAL_RECIPE_IDS:
    print(
        f"Recipe {recipe_id}: "
        f"{'Included' if recipe_id in selected_ids else 'Missing'}"
    )

print("\nRATING VALUE COVERAGE")

for rating in range(6):
    covered = selected_ids.intersection(
        rating_recipe_ids[rating]
    )

    print(
        f"Rating {rating}: "
        f"{'Covered' if covered else 'NOT COVERED'}"
    )

print("\nMISSING REVIEW COVERAGE")
print(
    "Covered:",
    bool(selected_ids.intersection(missing_review_recipe_ids))
)

print("\nNO VALID RATING COVERAGE")
print(
    "Covered:",
    bool(selected_ids.intersection(no_valid_rating_ids))
)

print("\nSelection completed successfully.")


from pathlib import Path

# Create the sample output directory
SAMPLE_DIR = Path("data/sample")
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

RECIPES_OUTPUT = SAMPLE_DIR / "sample_recipes.csv"
INTERACTIONS_OUTPUT = SAMPLE_DIR / "sample_interactions.csv"

print("\n========== GENERATING SAMPLE CSV FILES ==========")

# Convert selected IDs to a set for efficient filtering
selected_id_set = set(selected_ids)

# Extract selected recipes from the original recipe dataset
sample_recipes = pd.read_csv(RECIPES_PATH)

sample_recipes = sample_recipes[
    sample_recipes["id"].isin(selected_id_set)
].copy()

# Sort by recipe ID for consistent output
sample_recipes = sample_recipes.sort_values("id")

sample_recipes.to_csv(
    RECIPES_OUTPUT,
    index=False
)

print(f"Sample recipes saved: {len(sample_recipes):,} rows")


# Extract ALL interactions for the selected recipe IDs
interaction_chunks = []

for chunk_number, chunk in enumerate(
    pd.read_csv(INTERACTIONS_PATH, chunksize=CHUNK_SIZE),
    start=1
):
    matching_rows = chunk[
        chunk["recipe_id"].isin(selected_id_set)
    ]

    if not matching_rows.empty:
        interaction_chunks.append(matching_rows)

    print(f"Filtered interaction chunk {chunk_number}")


sample_interactions = pd.concat(
    interaction_chunks,
    ignore_index=True
)

sample_interactions.to_csv(
    INTERACTIONS_OUTPUT,
    index=False
)

print(
    f"Sample interactions saved: "
    f"{len(sample_interactions):,} rows"
)

print("\nCSV generation completed.")

