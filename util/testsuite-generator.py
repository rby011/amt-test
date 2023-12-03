import json
import random
import re
import string
import os
import shutil
import exrex

def generate_sample_value(field):
    if field["type"] == "string":
        if "pattern" in field:
            return exrex.getone(field["pattern"])
        elif "enum" in field:
            return random.choice(field["enum"])
    elif field["type"] == "number":
        return float(random.randint(1, 100))
    elif field["type"] == "integer":
        return random.randint(1, 100)
    elif field["type"] == "object":
        return {k: generate_sample_value(v) for k, v in field["properties"].items()}
    elif field["type"] == "array":
        return [generate_sample_value(field["items"]) for _ in range(field.get("minItems", 1))]

def generate_sample_json(schema, num_instances):
    return [generate_sample_value(schema) for _ in range(num_instances)]

sample_dir_path = None
def generate_sample_testfiles(data, sample_root):
    global sample_dir_path
    for key, value in data.items():
        if isinstance(value, dict):
            generate_sample_testfiles(value, sample_root)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    generate_sample_testfiles(item, sample_root)
        else:
            if(key == 'id'):
                print(f"{key}: {value}")
                sample_dir_path = os.path.join(sample_root,value)
                os.makedirs(os.path.join(sample_root,value))
            if(key == 'file_path'):
                print(f"\t{key}: {str(value).rjust(20)}")
                with open(os.path.join(sample_dir_path, value), 'w') as f:
                    f.write(f'this is {key} for test') 
                    

# sample 만들기
schema_meta_testsuite_file = './schema/testsuite-schema.json'
schema_meta_testplan_file = './schema/testplan-schema.json'
sample_root = 'sample'
sample_testsuite_file = 'testsuite-sample.json' 
sample_testplan_file = 'testplan-sample.json' 

# sample 폴더 밑에 다 지우기
if os.path.exists(sample_root):
    shutil.rmtree(sample_root)
os.mkdir(sample_root)

# sample testsuite 생성하기 (with meta)
with open(schema_meta_testsuite_file, 'r', encoding='utf-8') as f:
    schema = json.load(f)
sample_json = generate_sample_json(schema, 10)
with open(os.path.join(sample_root, sample_testsuite_file), 'w') as f:
    json.dump(sample_json, f, ensure_ascii=False, indent=4)

# sample testsuite 에 정의된 file 생성하기 (with concrete testsuite)
with open(os.path.join(sample_root, sample_testsuite_file), 'r', encoding='utf-8') as f:
    schema = json.load(f)
for data in schema:
    generate_sample_testfiles(data, sample_root)

# sample testplan 생성하기 (with meta)
with open(schema_meta_testplan_file, 'r', encoding='utf-8') as f:
    schema = json.load(f)
sample_json = generate_sample_json(schema, 1)
with open(os.path.join(sample_root, sample_testplan_file), 'w') as f:
    json.dump(sample_json, f, ensure_ascii=False, indent=4)