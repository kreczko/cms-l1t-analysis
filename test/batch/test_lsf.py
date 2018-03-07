import unittest
from cmsl1t.batch import Status
from cmsl1t.batch.lsf import _parse_bsub_output, _parse_bjobs_output

test_bsub_output = "Job <145417932> is submitted to default queue <8nm>."

bjobs_test_out = """
JOBID     USER    STAT  QUEUE      FROM_HOST   EXEC_HOST   JOB_NAME   SUBMIT_TIME
113     user1   PEND  normal     hostA                   myjob     Jun 17 16:15
111     user2   RUN   normal     hostA       hostA       myjob     Jun 14 15:13
110     user1   RUN   normal     hostB       hostA       myjob     Jun 12 05:03
104     user3   RUN   normal     hostA       hostC       myjob     Jun 11 13:18
"""


class TestLSFBatch(unittest.TestCase):

    def test_parse_bsub_output(self):
        job_id = _parse_bsub_output(test_bsub_output)
        self.assertEqual(job_id, 145417932)

    def test_parse_bjobs_output(self):
        job_id, status = _parse_bjobs_output(bjobs_test_out)
        self.assertEqual(job_id, 113)
        self.assertEqual(status, Status.PENDING)
