import logging
logger = logging.getLogger(__name__)


def _check_inputs(inputs, expected_input_order):
    for i, o in zip(inputs, expected_input_order):
        if not i.endswith(o):
            return False
    return True


class BaseProducer(object):

    def __init__(self, inputs, outputs, params):
        self._inputs = inputs
        self._params = params
        self._outputs = outputs
        self._checked_content = False

        if not _check_inputs(self._inputs, self._expected_input_order):
            logger.error('Unexpected input order.')
            logger.error('Expected order' +
                         ','.join(self._expected_input_order))
            logger.error('Got' + ','.join(self._inputs))
            raise ValueError('Unexpected input order in {}'.format(
                self.__class__.__name__))

    def produce(self, event):
        raise NotImplementedError(
            'Producer does not have a "produce(self, event)" method!')
