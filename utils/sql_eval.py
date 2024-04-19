import itertools
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal
from typing import Tuple


def query_solver(quary:str) -> pd.DataFrame:
    """
    Won't work, just for replacement until an appropriate answer by the client is given
    """
    pass

# find start and end index of { } in a string. return (start, end) if found, else return (-1, -1)
def find_bracket_indices(s: str, start_index: int = 0) -> tuple[int, int]:
    start = s.find("{", start_index)
    end = s.find("}", start + 1)
    if start == -1 or end == -1:
        return (-1, -1)
    return (start, end)

def normalize_table(
    df: pd.DataFrame, query: str
) -> pd.DataFrame:
    """
    Normalizes a dataframe by:
    1. sorting columns in alphabetical order
    2. sorting rows using values from first column to last (if query_category is not 'order_by' and question does not ask for ordering)
    3. resetting index
    """
    # sort columns in alphabetical order
    sorted_df = df.reindex(sorted(df.columns), axis=1)
    
    # check if query_category is 'order_by' and if question asks for ordering
    if "order_by" not in query.lower():
        # sort rows using values from first column to last
        sorted_df = sorted_df.sort_values(by=list(sorted_df.columns))
    # reset index
    sorted_df = sorted_df.reset_index(drop=True)
    return sorted_df


# extrapolate all possible queries from a query with { } in it
def get_all_minimal_queries(query: str) -> list[str]:
    start, end = find_bracket_indices(query, 0)
    if (start, end) == (-1, -1):
        return [query]

    # get all possible column subsets
    column_options = query[start + 1 : end].split(",")
    column_combinations = list(
        itertools.chain.from_iterable(
            itertools.combinations(column_options, r)
            for r in range(1, len(column_options) + 1)
        )
    )
    queries = []
    for column_tuple in column_combinations:
        left = query[:start]
        column_str = ", ".join(column_tuple)
        right = query[end + 1 :]
        # change group by size dynamically if necessary
        if right.find("GROUP BY {}"):
            right = right.replace("GROUP BY {}", f"GROUP BY {column_str}")
        queries.append(left + column_str + right)
    return queries


def subset_df(
    df_sub: pd.DataFrame,
    query_sub: str,
    df_super: pd.DataFrame,
    query_super: str
) -> Tuple[bool,None|str]:
    """
    Checks if df_sub is a subset of df_super
    """
    if df_sub.empty:
        return [True,None]  # trivial case
    # make a copy of df_super so we don't modify the original while keeping track of matches
    df_super_temp = df_super.copy(deep=True)
    matched_columns = []
    assertion_errors = []
    for col_sub_name in df_sub.columns:
        col_match = False
        for col_super_name in df_super_temp.columns:
            col_sub = df_sub[col_sub_name].sort_values().reset_index(drop=True)
            col_super = (
                df_super_temp[col_super_name].sort_values().reset_index(drop=True)
            )
            try:
                assert_series_equal(
                    col_sub, col_super, check_dtype=False, check_names=False
                )
                col_match = True
                matched_columns.append(col_super_name)
                # remove col_super_name to prevent us from matching it again
                df_super_temp = df_super_temp.drop(columns=[col_super_name])
                break
            except AssertionError as e:
                assertion_errors.append(e)
                continue
        if col_match == False:
            errors = "".join([str(error) for error in assertion_errors])
            return [False,errors]
    df_sub_normalized = normalize_table(df_sub, query_sub)

    # get matched columns from df_super, and rename them with columns from df_sub, then normalize
    df_super_matched = df_super[matched_columns].rename(
        columns=dict(zip(matched_columns, df_sub.columns))
    )
    df_super_matched = normalize_table(df_super_matched, query_super)

    try:
        assert_frame_equal(df_sub_normalized, df_super_matched, check_dtype=False)
        return [True,None]
    except AssertionError as e:
        return [False,e]


def compare_query_results(
    query_gold: str,
    query_gen: str,
) -> Tuple[bool,None|str]:
    """
    Compares the results of two queries and returns a tuple of booleans, where the first element is
    whether the queries produce exactly the same result, and the second element is whether the
    result of the gold query is a subset of the result of the generated query (still correct).
    We bubble up exceptions (mostly from query_postgres_db) to be handled in the runner.
    """
    queries_gold = get_all_minimal_queries(query_gold)
    results_gen = query_solver(query_gen)
    for q in queries_gold:
        results_gold = query_solver(q)
        if results_gen.shape[1]>= results_gold.shape[1]:
            result = subset_df(results_gold, query_gold, results_gen, query_gen)
            return result
        elif results_gen.shape[1] < results_gold.shape[1]:
            result = subset_df(results_gen, query_gen, results_gold, query_gold)
            return result


#testing
dfs_gold = [
    pd.DataFrame({"uid": [1,2], "likes_movies": [True, False]}),
    pd.DataFrame({"name": ["alice", "bob"], "likes_movies": [True, False]}),
    pd.DataFrame({"uid": [1,2],"name": ["alice", "bob"], "likes_movies": [True, False]})
]

df_generated = pd.DataFrame({"likes_movies": [True, False],"uid": [1, 2]})
for i in range(len(dfs_gold)):
    result = subset_df(dfs_gold[i], 'SELECT u.id, u.likes_movies FROM users u ORDER BY', df_generated, 'SELECT u.id, u.likes_movies FROM users u order by')
    for j in result:
        if j != None:
            print(j)
    print("___________________________________________________________________________________________________________")
