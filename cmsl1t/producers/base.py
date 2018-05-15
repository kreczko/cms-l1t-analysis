import logging
logger = logging.getLogger(__name__)


def _check_inputs(inputs, expected_input_order):
    for i, o in zip(inputs, expected_input_order):
        if not i.lower().endswith(o.lower()):
            return False
    return True


class BaseProducer(object):

    def __init__(self, inputs, outputs, params):
        self._inputs = inputs
        self._params = params
        self._outputs = outputs
        self._checked_content = False

        if not _check_inputs(self._inputs, self._expected_input_order):
            msg = 'Unexpected input order.' + \
            '\n\tExpected order: ' +', '.join(self._expected_input_order) + \
            '\n\tGot: ' + ', '.join(self._inputs)
            logger.error(msg)
            raise ValueError('Unexpected input order in {}'.format(
                self.__class__.__name__))

    def produce(self, event):
        raise NotImplementedError(
            'Producer does not have a "produce(self, event)" method!')
