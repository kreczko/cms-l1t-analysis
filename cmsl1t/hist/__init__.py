

class BaseHistogram(object):

    def __init__(self, name, title):
        self.name = name
        self.title = title
        self.n_axes = None

    def set_n_axes(self, n_axes):
        self.n_axes = n_axes

    def fill(self, *vargs):
        raise NotImplementedError()
