from abc import ABC, abstractmethod
from pprint import pprint
from jsonschema import validate, ValidationError
import json
import traceback

class TestCase(ABC):
    def __init__(self, testcase_id, testsuite_id, test_level, test_module):
        self.testcase_id = testcase_id
        self.testsuite_id = testsuite_id
        self.test_level = test_level
        self.test_module = test_module

    def list_attributes(self):
        pprint(self.__dict__)
    
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
    
    def __loadwithvalidate(self, file_path, scheme_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        with open(scheme_path, 'r', encoding='utf-8') as f:
            scheme = json.load(f)
        for d in data:
            validate(instance=d, schema=scheme)
        return data

    def __build_unittestcases_asr(self, test_suites):
        test_cases = []
        attrs = []
        for suite in test_suites:
            
            continue
        return test_cases
    
    def build_testcases(self):
        try:
            # test suite , test plan 로딩
            suites = self.__loadwithvalidate(self.test_suite_filepath, self.test_suite_scheme_filepath)
            plan = self.__loadwithvalidate(self.test_plan_filepath, self.test_plan_schem_filepath)[0]

            # plan 에 있는 suite id 제외            
            valid_suites = [suite for suite in suites if suite['id'] not in plan['suites-excluded']]
            
            # eut 별로 Unit Test Case 생성
            
            # Integration Test Case 생성            
            
            # {'euts': ['MT', 'ASR-FULL'],
            #  'result-analysis': ['BASIC'],
            #  'suites-excluded': ['851053494477425262-wa-MC-noisy_environment'],
            #  'test-types': ['UNIT', 'INTEGRATION']}            
            # pprint(plan)                
                        
                      
        except FileNotFoundError as fe:
            print("File path is invalid. Error:", fe)
            traceback.print_exc()
            return
        except json.JSONDecodeError as ve:
            print("JSON data is invalid. Error:", ve)
            traceback.print_exc()
            return
        except Exception as ee:
            print("Error:", ve)
            traceback.print_exc()
            return
        
testsuite_path = 'testsuite-sample.json'
testsuite_sheme_path = './schema/testsuite-schema.json'

testplan_path = 'testplan-sample.json'
testplan_sheme_path = './schema/testplan-schema.json'

tcbuilder = TestCaseBuilder(test_plan_filepath=testplan_path, 
                            test_plan_schem_filepath=testplan_sheme_path,
                            test_suite_filepath=testsuite_path, 
                            test_suite_scheme_filepath=testsuite_sheme_path)

tcbuilder.build_testcases()
