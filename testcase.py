from abc import ABC, abstractmethod
from pprint import pprint
from jsonschema import validate, ValidationError
import json
import traceback

class TestCase(ABC):
    def __init__(self, testcase_id, testsuite_id):
        self.testcase_id = testcase_id
        self.testsuite_id = testsuite_id
    def __str__(self):
        return json.dumps(self.__dict__)
    
class UnitASRTestCase(TestCase):
    def __init__(self, testcase_id, testsuite_id, audio_file_path, script_file_path, src_lang):
        super().__init__(testcase_id, testsuite_id)
        self.audio_file_path = audio_file_path
        self.script_file_path = script_file_path
        self.src_lang = src_lang

class UnitMTTestCase(TestCase):
    def __init__(self, testcase_id, testsuite_id, src_lang, dst_lang, src_text_file_path, ref_text_file_paths):
        super().__init__(testcase_id, testsuite_id)
        self.src_lang = src_lang
        self.dst_lang = dst_lang
        self.src_text_file_path = src_text_file_path
        self.ref_text_file_paths = ref_text_file_paths

class IntTestCase(TestCase):
    def __init__(self, testcase_id, testsuite_id, src_lang, dest_lang, src_text_file_path, ref_text_file_paths, audio_file_path):
        super().__init__(testcase_id, testsuite_id)
        self.src_lang = src_lang
        self.dest_lang = dest_lang
        self.src_text_file_path = src_text_file_path
        self.ref_text_file_paths = ref_text_file_paths
        self.audio_file_path = audio_file_path

class TestCaseBuilder:
    def __init__(self, test_suite_filepath, test_plan_filepath, test_suite_scheme_filepath, test_plan_schem_filepath):
        self.test_suite_filepath = test_suite_filepath
        self.test_plan_filepath = test_plan_filepath
        self.test_suite_scheme_filepath = test_suite_scheme_filepath
        self.test_plan_schem_filepath = test_plan_schem_filepath
        self.test_cases = {}
        self.tc_id = 1
                
    def __loadwithvalidate(self, file_path, scheme_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        with open(scheme_path, 'r', encoding='utf-8') as f:
            scheme = json.load(f)
        for d in data:
            validate(instance=d, schema=scheme)
        return data

    def __make_test_case_id(self, test_type, eut):
        id = self.tc_id
        self.tc_id += 1
        return f"{test_type}-{eut}-{id:04}"
    
    def __build_unittestcases(self, test_suites, eut):
        test_cases = []
        attrs = []
        for suite in test_suites:
            testcase_id = self.__make_test_case_id()
        return test_cases

    def __build_inttcases_mt(self, test_suites):
        test_cases = []
        attrs = []
        for suite in test_suites:
            pass # TODO
        return test_cases
    
    def build_testcases(self) -> dict[str:TestCase]:
        try:
            # test suite , test plan 로딩
            suites = self.__loadwithvalidate(self.test_suite_filepath, self.test_suite_scheme_filepath)
            plan = self.__loadwithvalidate(self.test_plan_filepath, self.test_plan_schem_filepath)[0]

            # plan 에 있는 suite id 제외            
            valid_suites = [suite for suite in suites if suite['id'] not in plan['suites-excluded']]

            # plan : euts , result-analysis, suites-excluded, type-types
            # ASR : testcase-id, testsuite-id, audio-file-path, script-file-path, src-lang
            # MT : testcase-id, testsuite-id,src-lang, dst-lang, src-text-file-path, ref-text-file-paths
            for suite in valid_suites:
                if 'UNIT' in plan['test-types']:
                    if 'ASR-FULL' in plan['euts']:
                        testcase_id = self.__make_test_case_id('UNIT','ASR-FULL')
                        testsuite_id = suite['id']
                        audio_file_path = suite['voice']['file_path']
                        script_file_path = suite['script']['file_path']
                        src_lang = suite['script']['language']
                        testcase = UnitASRTestCase(testcase_id, testsuite_id, audio_file_path, script_file_path, src_lang)
                        self.test_cases[testcase_id] = testcase
                    if 'MT' in plan['euts']:
                        testcase_id = self.__make_test_case_id('UNIT','MT')
                        testsuite_id = suite['id']
                        src_lang = suite['script']['language']
                        dst_lang = suite['translations'][0]['language']
                        src_text_file_path = suite['script']['file_path']
                        ref_text_file_paths =[tr['file_path'] for tr in suite['translations']]
                        testcase = UnitMTTestCase(testcase_id, testsuite_id, src_lang, dst_lang, src_text_file_path, ref_text_file_paths)
                        self.test_cases[testcase_id] = testcase
            return self.test_cases
        except FileNotFoundError as fe:
            print("File path is invalid. Error:", fe)
            traceback.print_exc()
        except json.JSONDecodeError as ve:
            print("JSON data is invalid. Error:", ve)
            traceback.print_exc()
        except Exception as ee:
            print("Error:", ve)
            traceback.print_exc()
        return None

testsuite_path = 'testsuite-sample.json'
testsuite_sheme_path = './schema/testsuite-schema.json'

testplan_path = 'testplan-sample.json'
testplan_sheme_path = './schema/testplan-schema.json'

tcbuilder = TestCaseBuilder(test_plan_filepath=testplan_path, 
                            test_plan_schem_filepath=testplan_sheme_path,
                            test_suite_filepath=testsuite_path, 
                            test_suite_scheme_filepath=testsuite_sheme_path)

testcases = tcbuilder.build_testcases()
for testcase_id, testcase in testcases.items():
    print(testcase_id)
    print(testcase)