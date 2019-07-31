import sys

import logging
import numpy as np
import six
import uproot

import ROOT
from rootpy.tree import TreeChain


from cmsl1t.utils.root_glob import glob
from cmsl1t.utils.module import load_L1TNTupleLibrary

load_L1TNTupleLibrary()
logger = logging.getLogger(__name__)
sumTypes = ROOT.l1t.EtSum


def _get_input_files(paths):
    # TODO: move this replacement into cmsl1t.config
    input_files = []
    for p in paths:
        if '*' in p:
            input_files.extend(glob(p))
        else:
            input_files.append(p)
    return input_files


def _create_alias_map(ntuple_map):
    '''
        Translates the ntuple_map into a format that can more easily processed
        for creating event attributes, e.g.
        content:
            <tree path>:
                branches:
                  <branchname>.<leafname>:
                    aliases:
                      - event.myAlias
        to
        {'myAlias': (<tree path>, <branchname>.<leafname>)}

    '''
    # TODO: move this replacement into cmsl1t.config
    aliasMap = {}
    trees = ntuple_map['content']
    for treeName, content in trees.items():
        for branchName, branchContent in content['branches'].items():
            for alias in branchContent['aliases']:
                tidyAlias = alias.replace('event.', '')
                aliasMap[tidyAlias] = (treeName, branchName)
    return aliasMap


class EventReader(object):

    def __init__(self, input_files, ntuple_map, nevents=-1, vectorized=False, batch_size=1):
        '''
            Reads ntuple_info as defined by bin/create-map-file
        '''
        self._treeNames = ntuple_map['content'].keys()
        self._aliasMap = _create_alias_map(ntuple_map)
        self.input_files = _get_input_files(input_files)
        self.nevents = nevents
        self._trees = {}

        self._used_arrays = vectorized
        self._used_trees = not vectorized
        self._passed_events = 0
        self._batch_size = batch_size

        self._numentries = uproot.numentries(
            self.input_files,
            list(self._treeNames)[0],
            total=False,
        )

    def _load_trees(self, input_file):
        for treeName in self._treeNames:
            try:
                self._trees[treeName] = TreeChain(
                    treeName,
                    [input_file],
                    cache=True,
                    events=self.nevents,
                )
                logger.debug("Successfully loaded {0}".format(treeName))
            except RuntimeError as e:
                logger.warning("Cannot find tree: {0} in input file".format(treeName))
                logger.error(e)
                if treeName in self._trees:
                    logger.warning('DELETING TREE')
                    del self._trees[treeName]
                continue

    def _load_arrays(self, input_file):
        for treeName in self._treeNames:
            try:
                self._trees[treeName] = uproot.iterate(
                    [input_file],
                    treeName,
                    entrysteps=self._batch_size,
                )
                logger.debug("Successfully loaded {0}".format(treeName))
            except RuntimeError as e:
                logger.warning(
                    "Cannot find tree: {0} in input file".format(treeName))
                logger.error(e)
                if treeName in self._trees:
                    logger.warning('DELETING TREE')
                    del self._trees[treeName]
                continue

    def __contains__(self, name):
        return name in self._aliasMap.keys()

    def __iter__(self):
        # event loop
        for input_file in self.input_files:
            nevents = self._numentries[input_file]
            logger.info('Opening file {} ({} events)'.format(input_file, nevents))
            if self._used_arrays:
                self._load_arrays(input_file)
            else:
                self._load_trees(input_file)
            try:
                eventGenerator = self.new_event
                if self._used_arrays:
                    eventGenerator = self.new_uproot_event
                for event in eventGenerator():
                    yield event
            except Exception as e:
                logger.critical("Error when reading data from ROOT file: {}".format(e))
                sys.exit(-1)
            logger.info('Closing file {}'.format(input_file))

    def new_event(self):
        for trees in six.moves.zip(*six.itervalues(self._trees)):
            yield Event(self._trees, self._aliasMap)

    def new_uproot_event(self):
        for treeGen in six.moves.zip(*six.itervalues(self._trees)):
            data = dict(six.moves.zip(self._trees, treeGen))
            yield UprootEvent(data, self._aliasMap, batch_size=self._batch_size)
            self._passed_events += self._batch_size
            if self.nevents > 0 and self._passed_events >= self.nevents:
                break

    @property
    def numentries(self):
        return sum([x for x in self._numentries.values()])


class UprootEvent(object):

    def __init__(self, data, mapping, batch_size=1):
        self._data = data
        self._map = mapping
        self._cache = {}
        self._isPy3 = sys.version_info[0] == 3
        self._batch_size = batch_size
        self.is_vectorized = batch_size > 1
        self._mask = None

    def _contruct_cache(self):
        pass

    def __getattr__(self, name):
        if name in object.__getattribute__(self, '_cache'):
            return object.__getattribute__(self, '_cache')[name]

        if name not in object.__getattribute__(self, '_map'):
            return object.__getattribute__(self, name)

        treeName, treeAttr = object.__getattribute__(self, '_map')[name]
        if treeName not in self._data:
            raise RuntimeError("Cannot find tree {0}".format(treeName))

        if treeAttr not in self._data[treeName]:
            treeAttr = treeAttr.split('.')[-1]
            if self._isPy3:
                treeAttr = bytes(treeAttr, 'utf-8')
            if treeAttr not in self._data[treeName]:
                raise RuntimeError("Cannot find branch {0} in tree {1}".format(treeAttr, treeName))

        data = self._data[treeName][treeAttr]
        if self._batch_size == 1:
            data = data[0]
        object.__getattribute__(self, '_cache')[name] = data
        return data

    def __getitem__(self, name):
        return object.__getattribute__(self, '__getattr__')(name)

    def mask(self, mask):
        mask_size = np.size(mask)
        if mask_size != self._batch_size:
            msg = 'Event mask size mismatch: expected {}, got {}'.format(self._batch_size, mask_size)
            logger.error(msg)
            raise ValueError(msg)

        if mask_size > 1:
            for tree, attributes in self._data.items():
                for attr in attributes:
                    self._data[tree][attr] = self._data[tree][attr][mask]
            return self
        if mask:
            return self
        return None


class Event(object):

    def __init__(self, trees, mapping):
        self._map = mapping
        self._trees = trees
        self._cache = {}
        self.is_vectorized = False

    def __getattr__(self, name):
        if name in object.__getattribute__(self, '_cache'):
            return object.__getattribute__(self, '_cache')[name]

        if name not in object.__getattribute__(self, '_map'):
            return object.__getattribute__(self, name)
        treeName, treeAttr = object.__getattribute__(self, '_map')[name]
        tree = object.__getattribute__(self, '_trees')[treeName]
        obj = tree
        for attr in treeAttr.split('.'):
            obj = getattr(obj, attr)
        object.__getattribute__(self, '_cache')[name] = obj
        return obj

    def __getitem__(self, name):
        return object.__getattribute__(self, '__getattr__')(name)

    def mask(self, mask):
        if np.size(mask) > 1:
            msg = 'Event class does not support vectorized filters'
            logger.error(msg)
            raise ValueError(msg)
        if mask:
            return self
        return None
