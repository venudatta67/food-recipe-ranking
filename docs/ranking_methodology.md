# Ranking Methodology

## 1. Introduction

The objective of this project is to develop and compare different recipe-ranking methods using the Food.com Recipes and User Interactions dataset.

The ranking system evaluates recipes using user ratings and compares three approaches:

1. Simple Average Rating
2. Weighted Average Rating
3. Empirical Bayesian Average Rating

The main motivation is to investigate whether ranking recipes exclusively by their average ratings produces reliable results, particularly when recipes have received very different numbers of ratings.

## 2. Data Used for Ranking

The ranking calculations use the Food.com user interaction dataset.

| Description | Count |
|---|---:|
| Total interactions | 1,132,367 |
| Valid ratings (1–5) | 1,071,520 |
| Zero ratings excluded | 60,847 |
| Recipes with valid ratings | 226,590 |

Only recipes with at least one valid rating (1–5) are included in the ranking calculations.

### Rating-handling decision

Ratings in the range 1–5 are treated as valid ratings for ranking calculations.

Rating 0 is excluded from:

- Average rating calculations.
- Rating counts.
- Weighted-average calculations.
- Bayesian ranking calculations.

All 60,847 zero-rated interactions contain written reviews. However, a zero rating is not treated as a numerical rating when calculating recipe rankings.

## 3. Method 1 – Simple Average Rating

### 3.1 Concept

Simple Average Rating is the baseline ranking method.

It calculates the arithmetic mean of all valid ratings received by each recipe.

### 3.2 Mathematical Formula

Average Rating = Sum of Valid Ratings / Number of Valid Ratings

Where:

- Sum of Valid Ratings: Total of all ratings between 1 and 5 received by a recipe.
- Number of Valid Ratings: Total number of valid ratings received by that recipe.

### 3.3 Example Calculation

Suppose a recipe receives the following ratings:

5, 4, 5, 3, 5

Average Rating = (5 + 4 + 5 + 3 + 5) / 5

Average Rating = 22 / 5 = 4.4

Therefore, the recipe receives an average rating of 4.4 out of 5.

### 3.4 Ranking Results and Observations

The Simple Average method produced the following observations:

- All 20 recipes in the top-20 ranking had an average rating of 5.0.
- Their rating counts varied considerably.
- Some recipes had received only one rating, while others had received multiple ratings.

This demonstrates that recipes with very few ratings can achieve perfect average scores and appear at the top of the ranking.

### 3.5 Limitations

The Simple Average method considers only the observed average rating. It does not account for the amount of rating evidence supporting that average.

For example:

| Recipe | Rating Count | Average Rating |
|---|---:|---:|
| Recipe A | 1 | 5.0 |
| Recipe B | 100 | 4.8 |
| Recipe C | 500 | 4.7 |

Simple Average ranks Recipe A first, even though its perfect score is based on just one rating.

### 3.6 Tie-Breaking Rule

Recipes are ranked using the following sorting order:

Average rating in descending order (higher ratings first).

Rating count in descending order (recipes with more ratings first when average ratings are equal).

Recipe ID in ascending order (lower recipe IDs first when both average rating and rating count are equal).

This ensures that recipes with the same average rating are further ordered by rating count, with recipe ID providing a consistent final tie-breaker.

## 4. Method 2 – Weighted Average Rating

### 4.1 Concept

Weighted Average Rating considers two factors:

1. The recipe's own average rating.
2. The overall average rating across all valid recipe ratings.

Unlike Simple Average, this method adjusts a recipe's observed average towards the overall average. The adjustment is stronger for recipes with fewer ratings and weaker for recipes with more ratings.

### 4.2 Mathematical Formula

WR = (v × R + m × C) / (v + m)

Where:

| Symbol | Meaning |
|---|---|
| WR | Weighted rating |
| R | Recipe's average rating |
| v | Number of valid ratings for the recipe |
| C | Overall average rating across all valid ratings |
| m | Prior weight |

### 4.3 Parameter Selection

For the initial Weighted Average experiment, the prior weight was manually selected as:

m = 10

This is an exploratory parameter selected for comparison. It is not a statistically established minimum rating count.

The overall average rating calculated from the dataset was:

C = 4.661499

### 4.4 Example Calculation

Consider Recipe A:

- Average rating (R) = 5.0
- Rating count (v) = 1
- Overall average (C) = 4.6 (rounded for illustration)
- Prior weight (m) = 10

WR = [(1 × 5.0) + (10 × 4.6)] / (1 + 10)

WR = 51 / 11

WR = 4.636

The weighted score moves closer to the overall average because the recipe has received only one rating.

Now consider Recipe B:

- Average rating (R) = 4.8
- Rating count (v) = 100
- Overall average (C) = 4.6
- Prior weight (m) = 10

WR = [(100 × 4.8) + (10 × 4.6)] / (100 + 10)

WR = 526 / 110

WR = 4.782

Recipe B retains a score close to its original average because it has considerably more rating evidence.

### 4.5 Ranking Results and Observations

The Weighted Average method produced a different top-20 ranking compared with Simple Average.

The method reduces the advantage of recipes with very few ratings by adjusting their scores towards the overall average.

The top-20 overlap between Simple Average and Weighted Average was:

10 out of 20 recipes (50%).

This demonstrates that incorporating rating counts can materially change which recipes appear at the top of the ranking.

### 4.6 Limitations

The Weighted Average method improves upon Simple Average by considering rating counts.

However, its prior weight is manually selected. Different values of m can produce different ranking results.

Therefore, the choice of prior weight introduces a parameter-selection decision into the ranking methodology.

### 4.7 Tie-Breaking Rule

Recipes are ranked by weighted rating in descending order. When two or more recipes have the same weighted rating, recipe ID is used as the tie-breaker in ascending order (lower recipe ID first).

Unlike Simple Average ranking, rating count is not used as an additional tie-breaker after the weighted rating has been calculated.

## 5. Method 3 – Empirical Bayesian Average Rating

### 5.1 Concept

Empirical Bayesian ranking improves upon simple average ranking by considering both:

1. The recipe's observed average rating.
2. The number of valid ratings received by the recipe.

It uses the overall average rating as a prior and adjusts individual recipe averages towards that prior.

Unlike the previous Weighted Average experiment, the prior strength is estimated from the dataset's rating variance rather than manually selected.

### 5.2 Mathematical Formula

BR = (n × R̄ + m × C) / (n + m)

Where:

| Parameter | Meaning | Value |
|---|---|---:|
| BR | Bayesian rating | Calculated for each recipe |
| n | Number of valid ratings | Recipe-specific |
| R̄ | Recipe's average rating | Recipe-specific |
| m | Estimated prior strength | 6.999735 |
| C | Global average rating | 4.661499 |

### 5.3 Estimating the Prior Strength

The prior strength is estimated using a variance-based method-of-moments approach.

First, the pooled within-recipe variance is calculated by combining the squared deviations of individual ratings from their respective recipe averages and dividing by the total within-recipe degrees of freedom. This estimates how much individual ratings vary within recipes.

Next, the between-recipe variance is estimated using the between-recipe mean square, the pooled within-recipe variance, and an effective average group size (n₀). This method accounts for differences in the number of ratings available for each recipe.

The estimated variances are:

- Within-recipe variance (σ²): 0.4574566057
- Between-recipe variance (τ²): 0.0653534138

The prior strength is calculated as:

m = σ² / τ² = 6.999735

This means the prior contributes approximately seven equivalent ratings to the Bayesian adjustment.

The prior strength was estimated during the variance validation stage and is supplied as the default parameter in the `rank_by_bayesian()` function. It is not recalculated automatically each time the ranking function runs. The prior mean, however, is calculated from the global average of valid ratings when the function executes.

### 5.4 Interpretation

The estimated prior strength indicates how strongly individual recipe averages are adjusted towards the global average.

- Recipes with fewer ratings receive stronger adjustment.
- Recipes with more ratings receive weaker adjustment.
- The global average provides the common reference point.

The method effectively uses the equivalent of approximately seven ratings at the global average when calculating the adjusted score.

These are mathematical prior contributions, not additional user ratings added to the dataset.

### 5.5 Why Empirical Bayes?

The initial Weighted Average method used a manually selected prior strength of 10.

The Empirical Bayesian method estimates the prior strength from the dataset's variance structure.

This makes the adjustment data-driven rather than dependent on an arbitrary manual parameter choice.

### 5.6 Ranking Results

The empirical Bayesian method produced a top-20 ranking that differed from Simple Average but was very similar to Weighted Average.

The observed top-20 overlaps were:

- Simple Average vs Empirical Bayes: 12 out of 20.
- Weighted Average vs Empirical Bayes: 18 out of 20.

These results show that both shrinkage-based methods select many of the same recipes, while Simple Average produces more different selections.

### 5.7 Tie-Breaking Rule

Recipes are ranked by Bayesian-adjusted rating in descending order. When two or more recipes have the same Bayesian-adjusted rating, recipe ID is used as the tie-breaker in ascending order (lower recipe ID first).

Rating count is not used as an additional tie-breaker after the Bayesian-adjusted rating has been calculated.

## 6. Comparison of the Three Ranking Methods

### 6.1 Comparison of Methodology

| Criterion | Simple Average | Weighted Average | Empirical Bayes |
|---|---|---|---|
| Considers average rating | Yes | Yes | Yes |
| Uses rating count in the ranking score | No | Yes | Yes |
| Adjusts low-count averages | No | Yes | Yes |
| Prior strength | None | Manual (10) | Estimated (6.999735) |
| Data-driven prior adjustment | No | No | Yes |

Although Simple Average does not include rating count in its score, it uses rating count as a secondary tie-breaker when average ratings are equal.

### 6.2 Top-20 Ranking Overlap

The overlap between the top-20 recipe lists was calculated to understand how the choice of ranking method affects recipe selection.

| Comparison | Common Recipes | Interpretation |
|---|---:|---|
| Simple Average vs Weighted Average | 10/20 | Considerable ranking changes |
| Simple Average vs Empirical Bayes | 12/20 | Considerable ranking changes |
| Weighted Average vs Empirical Bayes | 18/20 | Very similar selections |
| Common to all three methods | 10/20 | Consistently selected recipes |

### 6.3 Key Findings

**Finding 1 – Simple Average favours perfect observed scores**

The Simple Average top-20 list contained recipes with perfect average ratings of 5.0, despite substantial differences in their rating counts.

This demonstrates that a perfect average based on very few ratings can receive the same score as a perfect average supported by considerably more ratings.

**Finding 2 – Weighted Average changes recipe selection**

The Weighted Average method adjusts recipe scores towards the global average using a manually selected prior weight of 10.

This reduces the influence of recipes with relatively few ratings.

**Finding 3 – Empirical Bayes provides a data-estimated adjustment**

The Empirical Bayesian method estimates its prior strength from the dataset's variance structure.

The estimated prior strength was approximately 7, compared with the manually selected value of 10 in the Weighted Average experiment.

**Finding 4 – Weighted Average and Empirical Bayes produce similar selections**

The two methods shared 18 out of 20 recipes in their top-20 lists.

This similarity is expected because both methods use the same mathematical shrinkage formula, but with different prior strengths.

### 6.4 Overall Conclusion

The analysis demonstrates that ranking recipes exclusively by their average ratings can favour recipes with limited rating evidence.

Weighted Average and Empirical Bayesian ranking address this limitation by considering both the recipe's observed average rating and its rating count.

The Empirical Bayesian method offers an additional advantage by estimating prior strength from the dataset rather than requiring manual selection.

The comparison does not establish that one method is universally superior. Instead, it demonstrates how different ranking assumptions influence recipe selection and provides a transparent basis for choosing a ranking approach.

## 7. Implementation

The ranking calculations are implemented in the reusable Python module:

`src/ranking.py`

The comparison script is:

`src/compare_ranking_methods.py`

The Streamlit application uses these ranking functions to allow users to explore and compare the three methods interactively.
