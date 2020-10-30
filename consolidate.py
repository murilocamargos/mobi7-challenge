import pandas as pd


def get_data():
    """Get all data from the CSV files.

    Returns
    -------
    pos : pd.DataFrame
        A data frame with the available position and state measurements
        from all vehicles.

    poi : pd.DataFrame
        A data frame with all positions of interest with name, radius and
        coordinates.
    """
    pos = pd.read_csv('data/posicoes.csv')
    poi = pd.read_csv('data/base_pois_def.csv')
    return pos, poi


if __name__ == '__main__':
    pos, poi = get_data()
    print(pos, poi)
