from abc import ABC, abstractmethod
from typing import List,Set
from testresult import TestResult
from testcase import TestCase, UnitASRTestCase, UnitMTTestCase
import string, random, subprocess

class Engine(ABC):
    def __init__(self, command:str, args:Set[str:str]): 
        self.command = command
        self.args = args
        self.full_command = None
    
    # 코멘드
    @abstractmethod
    def get_full_command() -> str:
        pass

    # Engine 의 출력(console 또는 file)을 문자열로 변환하여 반환
    @abstractmethod
    def run() -> str: 
        pass

class TestExecutor(ABC):
    def __init__(self, engine:Engine)->None:
        self.engine = engine
    
    @abstractmethod
    def execute(self, testcases:Set[TestCase]) -> List[TestResult]:
        pass
    @abstractmethod
    def execute(self, testcases:TestCase) -> TestResult:
        pass

    @abstractmethod
    def process_metric() -> float:
        pass
    
    @abstractmethod
    def process_output() -> str:
        pass

    @abstractmethod
    def process_log() -> str:
        pass

class DummyASREngine(Engine):
    def get_full_command(self) -> str:
        f_command = self.command
        for option, value in self.args.items():
            f_command.join([' ', option, ' ' ,value])
        return f_command
    
    def run(self) -> str:
        f_command = self.get_full_command()
        return subprocess.run(f_command, capture_output=True, text=True)

class DummyASRTestExecutor(TestExecutor):
    def __init(self, engine:Engine):
        self.engine = engine
                
    def execute(self, testcases: Set[TestCase]) -> List[TestResult]:
        results = []
        for testcase in testcases:
            if(isinstance(testcase, UnitASRTestCase)):
                result = self.execute(testcase)
                results.append(result)
        return results

    def execute(self, testcase: TestCase) -> TestResult:
        if(isinstance(testcase, UnitMTTestCase)):
            raise ValueError("Invalid TestCase Type")
        result = TestResult()
        result.output = ''.join(random.choices(string.ascii_letters + string.digits, k=30))
        result.metric['BLEU'] = random.random()
        return result

    def measure_metric(self) -> float:
        return random.random()

    def process_output() -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=30))


    
class DummyMTTestExecutor(TestExecutor):
    def execute(self, testcases: Set[TestCase]) -> List[TestResult]:
        results = []
        for testcase in testcases:
            if(isinstance(testcase, UnitMTTestCase)):
                result = self.execute(testcase)
                results.append(result)
        return results

    def execute(self, testcase: TestCase) -> TestResult:
        if(isinstance(testcase, UnitMTTestCase)):
            raise ValueError("Invalid TestCase Type")
        result = TestResult()
        result.output = ''.join(random.choices(string.ascii_letters + string.digits, k=30))
        result.metric['BLEU'] = random.random()
        return result

#
# simple test
#
from testcase import TestCaseBuilder
import json

testsuite_path = 'testsuite-sample.json'
testsuite_sheme_path = './schema/testsuite-schema.json'

testplan_path = 'testplan-sample.json'
testplan_sheme_path = './schema/testplan-schema.json'

tcbuilder = TestCaseBuilder(testplan_filepath=testplan_path, 
                            testplan_schem_filepath=testplan_sheme_path,
                            testsuite_filepath=testsuite_path, 
                            testsuite_scheme_filepath=testsuite_sheme_path)

testcases = tcbuilder.build_testcases('sample')
for testcase_id, testcase in testcases.items():
    print(testcase_id, isinstance(testcase, UnitMTTestCase))
    print(json.dumps(testcase.__dict__,indent=4))

