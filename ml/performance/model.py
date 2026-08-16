from sklearn.ensemble import RandomForestRegressor


def create_performance_model():
    """
    Create the machine learning model used
    to predict student academic performance.
    """

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        max_depth=10,
        min_samples_split=4,
        min_samples_leaf=2
    )

    return model