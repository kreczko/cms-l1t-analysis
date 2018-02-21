class Status:
    CREATED = 'CREATED'
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    FAILED = 'FAILED'
    FINISHED = 'FINISHED'
    UNKNOWN = 'UNKNOWN'
    HELD = 'HELD'


class Batch:
    lsf = 'LSF'
    condor = 'HTCondor'
