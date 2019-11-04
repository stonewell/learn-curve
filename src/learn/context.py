import pandas as pd


class LearnContext(object):
    def __init__(self):
        self.features_ = []

    def handle_asset_data(self, context, asset, data, is_buy):
        for f in self.features_:
            f.handle_asset_data(context, asset, data, is_buy)

    def finalize_learning_data(self):
        for f in self.features_:
            f.finalize_learning_data()

    def get_learning_data(self):
        data = []

        for f in self.features_:
            data.append(f.get_learning_data())

        return pd.concat(data, axis=1)

    def add_feature(self, feature):
        self.features_.append(feature)
