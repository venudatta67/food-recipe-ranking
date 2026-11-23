
from pathlib import Path
import sys

import streamlit as st
import base64

# PROJECT CONFIGURATION
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from src.data_processing import load_processed_data
from src.ranking import (
    calculate_recipe_statistics,
    rank_by_simple_average,
    rank_by_weighted_average,
    rank_by_bayesian
)


# --------------------------------------------------
# DATASET PATHS
# --------------------------------------------------

RECIPES_PATH = PROJECT_ROOT / "data" / "processed" / "processed_recipes.csv"

INTERACTIONS_PATH = PROJECT_ROOT / "data" / "raw" / "RAW_interactions.csv"


# --------------------------------------------------
# DATA LOADING FUNCTIONS
# --------------------------------------------------

@st.cache_data
def load_recipes():
    """Load the processed recipe dataset."""

    return load_processed_data(RECIPES_PATH)


@st.cache_data
def load_rating_statistics():
    """Calculate recipe-level rating statistics."""

    return calculate_recipe_statistics(INTERACTIONS_PATH)


@st.cache_data
def load_combined_data():

    recipes = load_recipes()

    recipe_stats = load_rating_statistics()

    combined_data = recipes.merge(
        recipe_stats,
        left_on="id",
        right_index=True,
        how="left",
        validate="one_to_one"
    )

    return combined_data


# --------------------------------------------------
# STREAMLIT PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Rate My Recipe",
    page_icon="🍽️",
    layout="wide"
)


# --------------------------------------------------
# APPLICATION BACKGROUND
# --------------------------------------------------

with open("assets/recipe_background_optimized.jpg", "rb") as image_file:
    background_image = base64.b64encode(image_file.read()).decode()

st.markdown(
    f"""
    <style>
    .stApp {{
        background:
            linear-gradient(
                rgba(255, 255, 255, 0.78),
                rgba(255, 255, 255, 0.78)
            ),
            url("data:image/jpeg;base64,{background_image}");

        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)



# --------------------------------------------------
# APPLICATION HEADER
# --------------------------------------------------

st.title("🍽️ Rate My Recipe")

st.subheader("Food.com Recipe Ranking System")

st.write(
    """
    Discover highly rated recipes using different ranking methods.

    This application compares Simple Average, Weighted Average,
    and Empirical Bayesian ranking approaches to identify
    recipes with strong user ratings and reliable feedback.
    """
)

st.divider()

st.info(
    "Welcome! Explore recipes, compare ranking methods, "
    "and discover insights from the Food.com dataset."
)

# --------------------------------------------------
# DATASET OVERVIEW
# --------------------------------------------------

st.header("Dataset Overview")

with st.spinner("Loading recipe data and calculating rating statistics..."):

    recipe_data = load_combined_data()

st.success("Recipe data loaded successfully!")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Recipes",
    f"{len(recipe_data):,}"
)

col2.metric(
    "Recipes With Ratings",
    f"{recipe_data['rating_count'].notna().sum():,}"
)

col3.metric(
    "Mean of Recipe Average Ratings",
    f"{recipe_data['average_rating'].mean():.2f}"
)

st.subheader("Sample Recipe Data")

display_columns = [
    "id",
    "name",
    "minutes",
    "rating_count",
    "average_rating"
]

st.dataframe(
    recipe_data[display_columns].head(10),
    use_container_width=True
)


# --------------------------------------------------
# RECIPE RANKING
# --------------------------------------------------

st.header("Recipe Rankings")

st.write(
    "Choose a ranking method to discover the highest-rated recipes."
)

ranking_method = st.selectbox(
    "Select Ranking Method",
    [
        "Simple Average",
        "Weighted Average",
        "Empirical Bayesian"
    ]
)

top_n = st.slider(
    "Number of Top Recipes",
    min_value=5,
    max_value=50,
    value=20,
    step=5
)

ranking_data = recipe_data.set_index("id")
ranking_data.index.name = "recipe_id"

# Apply the selected ranking method

if ranking_method == "Simple Average":
    ranked_recipes = rank_by_simple_average(
        ranking_data,
        top_n=top_n
    )
    score_column = "average_rating"

elif ranking_method == "Weighted Average":
    ranked_recipes = rank_by_weighted_average(
        ranking_data,
        m=10,
        top_n=top_n
    )
    score_column = "weighted_rating"

else:
    ranked_recipes = rank_by_bayesian(
        ranking_data,
        prior_strength=6.999735,
        top_n=top_n
    )
    score_column = "bayesian_rating"


# Display ranking results
st.subheader(f"Top {top_n} Recipes – {ranking_method}")

ranking_columns = [
    "rank",
    "name",
    "rating_count",
    "average_rating"
]

# Add the ranking score only if it is a different column
if score_column not in ranking_columns:
    ranking_columns.append(score_column)



st.dataframe(
    ranked_recipes[ranking_columns],
    use_container_width=True,
    hide_index=True
)

# RECIPE EXPLORER

st.header("Recipe Explorer")
st.write("Search for recipes by entering a recipe name.")

search_query = st.text_input(
    "Search Recipe Name",
    placeholder="Example: chicken, pasta, chocolate..."
)

# Filter recipes based on the search query
if search_query:
    search_results = recipe_data[
        recipe_data["name"].str.contains(
            search_query,
            case=False,
            na=False
        )
    ]
else:
    search_results = recipe_data

# COOKING TIME FILTER
st.subheader("Filter by Cooking Time")

max_cooking_time = st.slider(
    "Maximum Cooking Time (minutes)",
    min_value=1,
    max_value=120,
    value=60,
    step=5
)

search_results = search_results[
    search_results["minutes"].notna()
    & (search_results["minutes"] > 0)
    & (search_results["minutes"] <= max_cooking_time)
]

# MINIMUM AVERAGE RATING FILTER
st.subheader("Filter by Minimum Average Rating")

minimum_rating = st.slider(
    "Minimum Average Rating",
    min_value=1.0,
    max_value=5.0,
    value=3.0,
    step=0.5
)

search_results = search_results[
    search_results["average_rating"].notna()
    & (search_results["average_rating"] >= minimum_rating)
]

# INGREDIENT COUNT FILTER
st.subheader("Filter by Number of Ingredients")

max_ingredients = st.slider(
    "Maximum Number of Ingredients",
    min_value=1,
    max_value=20,
    value=10,
    step=1
)

search_results = search_results[
    search_results["n_ingredients"].notna()
    & (search_results["n_ingredients"] <= max_ingredients)
]

# Display search results
st.write("Matching recipes:", len(search_results))

if not search_results.empty:

    display_results = search_results[
        ["id", "name", "minutes", "n_ingredients", "rating_count", "average_rating"]
    ].head(100).copy()

    display_results["average_rating"] = display_results["average_rating"].round(2)
    display_results["rating_count"] = display_results["rating_count"].fillna("Not Rated")
    display_results["average_rating"] = display_results["average_rating"].fillna("Not Rated")

    st.dataframe(
        display_results,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("No recipes found matching your search and filter criteria. Try changing your search or filters.")

# RECIPE DETAILS

st.header("Recipe Details")
st.write("Search and select a recipe to explore its complete information.")



# Search for a recipe
recipe_search_query = st.text_input(
    "Search Recipe Name",
    placeholder="Example: hawaiian chicken, jamaican chicken..."
)

if recipe_search_query:


    matching_recipes = recipe_data[
        recipe_data["name"].str.contains(
            recipe_search_query,
            case=False,
            na=False
        )
    ]


    recipe_options = matching_recipes[
        ["id", "name"]
        ].drop_duplicates(subset="id").copy()

    recipe_options["display_name"] = (
            recipe_options["name"]
            + " (ID: "
            + recipe_options["id"].astype(str)
            + ")"
    )

    if not recipe_options.empty:

        selected_recipe_label = st.selectbox(
        "Select a Recipe",
        options=recipe_options["display_name"].tolist()
        )

        selected_recipe_id = recipe_options.loc[
        recipe_options["display_name"] == selected_recipe_label,
        "id"].iloc[0]

        selected_recipe = recipe_data[
        recipe_data["id"] == selected_recipe_id
        ].iloc[0]

        st.subheader(selected_recipe["name"])
        st.write("Recipe ID:", selected_recipe["id"])

        # COOKING INFORMATION
        st.subheader("Cooking Information")

        cooking_col1, cooking_col2 = st.columns(2)

        if pd.notna(selected_recipe["minutes"]) and selected_recipe["minutes"] > 0:
            cooking_col1.metric(
            "Cooking Time",
            f"{int(selected_recipe['minutes']):,} minutes"
        )
        else:
            cooking_col1.metric("Cooking Time", "Not Available")

        if pd.notna(selected_recipe["n_ingredients"]):
            cooking_col2.metric(
            "Number of Ingredients",
            int(selected_recipe["n_ingredients"])
        )
        else:
            cooking_col2.metric("Number of Ingredients", "Not Available")

        # RECIPE RATING INFORMATION

        st.subheader("Rating Information")

        rating_col1, rating_col2 = st.columns(2)

        if pd.notna(selected_recipe["rating_count"]):
            rating_col1.metric(
                "Number of Ratings",
                f"{int(selected_recipe['rating_count']):,}"
            )
        else:
            rating_col1.metric("Number of Ratings", "Not Rated")

        if pd.notna(selected_recipe["average_rating"]):
            rating_col2.metric(
                "Average Rating",
                f"{selected_recipe['average_rating']:.2f} / 5"
            )
        else:
            rating_col2.metric("Average Rating", "Not Rated")

        # INGREDIENT LIST

        st.subheader("Ingredients")

        if isinstance(selected_recipe["ingredients"], list):
            for ingredient in selected_recipe["ingredients"]:
                st.write(f"• {ingredient}")
        else:
            st.info("Ingredient information is not available.")

        # RECIPE INSTRUCTIONS
        st.subheader("Cooking Instructions")

        if isinstance(selected_recipe["steps"], list) and selected_recipe["steps"]:
            for step_number, instruction in enumerate(
                selected_recipe["steps"],
                start=1
            ):
                st.write(f"**Step {step_number}:** {instruction}")
        else:
            st.info("Cooking instructions are not available.")

    else:
        st.warning("No matching recipes found. Try another search.")

else:
    st.info("Enter a recipe name to find and select a recipe.")
