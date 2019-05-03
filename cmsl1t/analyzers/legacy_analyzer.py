"""
Study the MET distibutions and various PUS schemes
"""
from contextlib import contextmanager
import logging
import os

import ROOT

from .BaseAnalyzer import BaseAnalyzer

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.environ.get('PROJECT_ROOT')
NTUPLE_CFG_FILE = os.path.join(
    PROJECT_ROOT, 'legacy', 'Config', 'ntuple_cfg.h')
EXTERNAL_PATH = os.path.join(PROJECT_ROOT, 'external')

ROOT.gROOT.ProcessLine('.include {0}'.format(EXTERNAL_PATH))
if 'L1TAnalysisDataformats.so' not in ROOT.gSystem.GetLibraries():
    path_to_lib = os.path.join(
        PROJECT_ROOT, 'build', 'L1TAnalysisDataformats.so')
    ROOT.gSystem.Load(path_to_lib)


@contextmanager
def adjust_ntuple_cfg(input_files, output_folder):
    logger.info(">> Adjusting legacy config")
    with open(NTUPLE_CFG_FILE) as f:
        content = f.read()
    data = ','.join(['"{0}"'.format(path) for path in input_files])
    logger.debug('Input files:', data)
    new_content = content.replace('"{{BENCHMARK_DATA}}"', data)
    new_content = new_content.replace(
        '{{BENCHMARK_OUTPUT_FOLDER}}', output_folder)
    new_content = new_content.replace(
        'return singleMuRun276243();', 'return benchmark_cfg();')
    with open(NTUPLE_CFG_FILE, 'w') as f:
        f.write(new_content)
    yield
    logger.info(">> Restoring legacy config")
    with open(NTUPLE_CFG_FILE, 'w') as f:
        f.write(content)


def compile_macro(macro):
    library = macro.split('/')[-1].replace('.cxx', '')
    library_path = os.path.join(PROJECT_ROOT, 'build', library)
    ROOT.gSystem.CompileMacro(macro, 'kOs', library_path)
    return getattr(ROOT, library)


class Analyzer(BaseAnalyzer):
    """
        Analyzer to encapsulate legacy macros and to produce output
        similar to the new analyzers
    """

    def __init__(self, **kwargs):
        super(Analyzer, self).__init__(**kwargs)
        self.compiled_macro = None
        self.input_files = self.params['input_files']

    def prepare_for_events(self, reader):
        '''
            adjust_ntuple_cfg
            compile_macros
        '''
        logger.info('Compiling macro')
        macro = os.path.abspath(self.params['macro'])

        with adjust_ntuple_cfg(self.input_files, self.output_folder):
            self.compiled_macro = compile_macro(macro)
        return True

    def process_event(self, entry, event):
        logger.info('Processing events with legacy macro')

        n_chunks = 0  # it is not what you think it is
        n_jobs = 1
        combine = False
        nevents = entry

        # returns no error code, how to check for errors?
        self.compiled_macro(n_chunks, n_jobs, nevents, combine)

        return True

    def reload_histograms(self, input_file):
        return True

    def fill_histograms(self, entry, event):
        return True

    def write_histograms(self):
        return True

    def make_plots(self):
        # Something like this needs to be implemented still
        # self.efficiencies.draw_plots(self.output_folder, "png")
        return True
