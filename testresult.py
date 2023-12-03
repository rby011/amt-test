from testcase import TestCase
class TestResult:
    def __init__(self, testcase:TestCase) -> None:
        self.testcase = testcase
        self.output = None
        self.metric = {str:float} # metric name : metric value