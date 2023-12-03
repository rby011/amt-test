from abc import ABC, abstractmethod
from pprint import pprint
from jsonschema import validate, ValidationError
import json
import traceback
import os

class TestCase(ABC):
    def __init__(self, testcase_id:str, testsuite:dict, script:dict, sample_dir:str):
        try:
            self.testcase_id = testcase_id
            self.testsuite_id = testsuite['id']
            self.usage_scenario = testsuite['usage_scenario']
            self.src_lang = testsuite['src_lang']
            self.dst_lang = testsuite['dst_lang']
            self.sample_dir = sample_dir
            
            fpath = os.path.join(self.sample_dir, self.testsuite_id)
            fpath = os.path.join(fpath, script['file_path'])
            with open(fpath,'r') as f:
                txt_lines = f.readlines()
            self.src_text = txt_lines
            for key, value in script.items():
                if key == 'file_path':
                    continue
                setattr(self, key, value)
        except FileNotFoundError as fe:
            print("File path is invalid. Error:", fe)
            traceback.print_exc()
            raise

    def __str__(self):
        return json.dumps(self.__dict__)
    
class UnitASRTestCase(TestCase):
    def __init__(self, testcase_id:str, testsuite:dict, script:dict, voice:dict, sample_dir:str):
        super().__init__(testcase_id, testsuite, script, sample_dir)
        for key, value in voice.items():
            setattr(self, key, value)

    # TODO : 말하는 속도, 배경 소음 수준 등 음원을 읽어서 동적으로 정의할 수 있는 속성 추가
    # TODO : wav 는 sampling rate 가능 , pcm 은 header 가 없어서 불가능

class UnitMTTestCase(TestCase):
    def __init__(self, testcase_id:str, testsuite:dict, script:dict, translations:dict, sample_dir:str):
        try:
            super().__init__(testcase_id, testsuite, script, sample_dir)
            
            # 참조 번역쌍
            ref_texts = []
            for translation in translations:
                fpath = os.path.join(self.sample_dir, self.testsuite_id)
                fpath = os.path.join(fpath, translation['file_path'])
                with open(fpath,'r') as f:
                    txt_lines = f.readline()
                ref_texts.append(txt_lines)
            self.ref_texts = ref_texts
        except FileNotFoundError as fe:
            print("File path is invalid. Error:", fe)
            traceback.print_exc()
            raise
        
class IntTestCase(TestCase):
    def __init__(self, testcase_id, testsuite:dict):
        super().__init__(testcase_id, testsuite)
        
        # 음원 파일 속성
        for key, value in testsuite['voice'].items():
            setattr(self, key, value)
        
        # 참조 번역쌍
        ref_texts = []
        for key, value in testsuite['translations'].items():
            if key == 'file_path':
                with open(key,'r') as f:
                    txt_lines = f.readline()
                ref_texts.append(txt_lines)
            self.ref_texts = ref_texts
    
    def __init__(self, testcase_id, testsuite_id, src_lang, dest_lang, src_text_file_path, ref_text_file_paths, audio_file_path):
        super().__init__(testcase_id, testsuite_id)
        self.src_lang = src_lang
        self.dest_lang = dest_lang
        self.src_text_file_path = src_text_file_path
        self.ref_text_file_paths = ref_text_file_paths
        self.audio_file_path = audio_file_path

class TestCaseBuilder:
    def __init__(self, testsuite_filepath, testplan_filepath, testsuite_scheme_filepath, testplan_schem_filepath):
        self.testsuite_filepath = testsuite_filepath
        self.testplan_filepath = testplan_filepath
        self.testsuite_scheme_filepath = testsuite_scheme_filepath
        self.testplan_schem_filepath = testplan_schem_filepath
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
    
    def build_testcases(self, sample_dir:str) -> dict[str:TestCase]:
        try:
            # test suite , test plan 로딩
            suites = self.__loadwithvalidate(self.testsuite_filepath, self.testsuite_scheme_filepath)
            plan = self.__loadwithvalidate(self.testplan_filepath, self.testplan_schem_filepath)[0]

            # plan 에 있는 suite id 제외            
            valid_suites = [suite for suite in suites if suite['id'] not in plan['suites-excluded']]

            # build testcases 
            for suite in valid_suites:
                if 'UNIT' in plan['test-types']:
                    if 'ASR-FULL' in plan['euts']:
                        testcase_id = self.__make_test_case_id('UNIT','ASR-FULL')
                        testcase = UnitASRTestCase(testcase_id, suite, suite['script'], suite['voice'], sample_dir)
                        self.test_cases[testcase_id] = testcase
                    if 'MT' in plan['euts']:
                        testcase_id = self.__make_test_case_id('UNIT','MT')
                        
                        pprint(suite['translations'])
                        
                        testcase = UnitMTTestCase(testcase_id, suite, suite['script'], suite['translations'], sample_dir)
                        self.test_cases[testcase_id] = testcase
            
            return self.test_cases 
        except json.JSONDecodeError as ve:
            print("JSON data is invalid. Error:", ve)
            traceback.print_exc()
        except Exception as ee:
            print("Error:", ve)
            traceback.print_exc()
        return None

#
# simple test
#
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
