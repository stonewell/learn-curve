class LearnFeature(object):

    def __init__(self, name):
        self.name_ = name

    def handle_asset_data(self, context, asset, data, is_buy):
        pass

    def finalize_learning_data(self):
        pass

    def get_learning_data(self):
        raise NotImplementedError

    def __get_name(self):
        return self.name_

    def __set_name(self, name):
        self.name_ = name

    name = property(__get_name, __set_name)
