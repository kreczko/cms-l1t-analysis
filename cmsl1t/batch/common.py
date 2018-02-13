class Status:
    CREATED = 'CREATED'
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    FAILED = 'FAILED'
    FINISHED = 'FINISHED'
    UNKNOWN = 'UNKNOWN'


class Batch:
    lsf = 'LSF'
    condor = 'HTCondor'
