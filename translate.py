import pandas as pd
import openai, time, re
from IPython.display import display

openai.api_key = 'YOUR_API_KEY'

def translate_sentences(sentences, model="gpt-4.0-turbo", max_tokens=100):
    pre_prompt = (
        "I am a highly skilled translator fluent in English and Korean."
        "My goal is to provide accurate and natural translations for each English sentence into Korean, "
        "maintaining the original tone and meaning. "
        "I'll request several korean setentences, "
        "and you you need to generate three translated sentences for each korean sentence." 
        "The sentence number for the translated should be matched with the sentence to translate." 
        "For example, the sequence numbers for the sentence '1' should be '1.1' , '1.2', '2.3'. The below is exmple."
        "(Example)" 
        "Korean :"
        "1. This is the 1st sample sentence to translate into english"
        "2. This is the 2nd sample sentence to translate into english"
        "3. This is the 3rd sample sentence to translate into english"
        "English :"
        "1.1 This is the translated sentence for the 1st"
        "1.2 This is the translated sentence for the 1st"
        "1.3 This is the translated sentence for the 1st"
        "2.1 This is the translated sentence for the 2nd"
        "2.2 This is the translated sentence for the 2nd"
        "2.3 This is the translated sentence for the 2nd"
        "3.1 This is the translated sentence for the 3rd"
        "3.2 This is the translated sentence for the 3rd"
        "3.3 This is the translated sentence for the 3rd"
    )
    prompt = pre_prompt + "Translate the following sentences:\n" + "\n".join(sentences)

    # 재시도를 위한 다단계 대기 시간 설정
    retry_delays = [15, 30, 60, 120]  # 각 재시도마다 대기할 시간 (초)
    for attempt, delay in enumerate(retry_delays, start=1):
        try:
            response = openai.Completion.create(model=model, prompt=prompt, max_tokens=max_tokens)
            translated_text = response.choices[0].text.strip()
            translated_sentences = translated_text.split('\n')

            # 번역된 문장의 개수 확인
            if len(translated_sentences) >= len(sentences):
                return '\n'.join([f"Translated {i+1}: {sentence}" for i, sentence in enumerate(translated_sentences) if sentence.strip()])
            else:
                print(f"Attempt {attempt}: Not all sentences were translated. Retrying in {delay} seconds...")
        except openai.error.RateLimitError:
            print(f"Attempt {attempt}: Rate limit exceeded. Retrying in {delay} seconds...")
        except openai.error.OpenAIError as e:
            print(f"Attempt {attempt}: OpenAI error occurred: {e}. Retrying in {delay} seconds...")
        except Exception as e:
            print(f"Attempt {attempt}: Unexpected error occurred: {e}. Retrying in {delay} seconds...")

        time.sleep(delay)

    print("Maximum retry attempts reached. Unable to complete the request.")
    return None


file_path = 'path_to_your_file.txt'  # 파일 경로 설정
batch_size = 50  # 한 번에 처리할 문장 수

# idf columns
# ['client_id', 'path', 'sentence', 'up_votes', 'down_votes', 'age',
# 'gender', 'accents', 'variant', 'locale', 'segment']
idf = pd.read_csv('./cv-corpus-15.0-2023-09-08/ko/validated.tsv', sep='\t')

with open('translate.txt', 'r') as f:
    translated = f.readlines()

sentences = idf['sentence'].iloc[1:16].to_list()
translated = [re.sub(r"\d+\.\d+", '', t).replace('"','').replace('\n','') for t in translated]

ns = []
for s in sentences:
    ns.append(s)
    ns.append(s)
    ns.append(s)
sentences = ns

# for i in range(len(sentences)):
#     print(sentences[i] , " : ", translated[i])

idf = idf.iloc[1:16].copy()
tdf = pd.DataFrame({'sentence':sentences, 'translated':translated})

mdf = pd.merge(left=idf, right=tdf, how='inner', left_on='sentence', right_on='sentence')

mdf.to_excel('output.xlsx')

# odf = pd.DataFrame({'translated':translated})
# idf = idf.iloc[1:16]

# idf_copy = idf.copy()
# for i in range(len(idf)):
#     copied_row = idf.iloc[i].copy()
#     idf_copy = pd.concat([idf_copy.iloc[:i+1], copied_row.to_frame().T, idf_copy.iloc[i+1:]]).reset_index(drop=True)
#     idf_copy = pd.concat([idf_copy.iloc[:i+1], copied_row.to_frame().T, idf_copy.iloc[i+1:]]).reset_index(drop=True)

# # print(idf)
# # print(idf_copy['path'].value_counts())

# df = pd.concat([idf_copy, odf], axis=1)

# print(df.sort_values(by='sentence')[['sentence','translated']])