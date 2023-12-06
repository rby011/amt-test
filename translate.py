import pandas as pd
from pandas import DataFrame
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

####################################################
#                      UTIL
####################################################


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

idf = idf.iloc[1:16].copy()
tdf = pd.DataFrame({'sentence':sentences, 'ref':translated})

mdf = pd.merge(left=idf, right=tdf, how='inner', left_on='sentence', right_on='sentence')

####################################################
#                      UTIL
####################################################

mdf['transcript'] = None
mdf['wer'] = None
mdf['script_file'] = None
mdf['ref_file'] = None
mdf['bleu'] = None

# import os
# from pydub import AudioSegment
# clip_root = './cv-corpus-15.0-2023-09-08/ko/clips'
# for mp3 in mdf['path'].to_list():
#     mp3_file = os.path.join(clip_root, mp3)
#     wav_file = os.path.join(clip_root, 'wav')
#     audio = AudioSegment.from_mp3(mp3_file)
#     audio.export(wav_file, format='wav')
# audio = AudioSegment.from_mp3('audio.mp3')
# audio.export('audio.wav', format='wav')


####################################################
#                    ASR UNIT Test
####################################################

# CONVERT INTO WAV

# for each wav file

## ENGINE CALL & LOG PARSING

## MEASURE

## SAVE TRANSCRIP FOR INTEGRATION


####################################################
#                    MT UNIT Test
####################################################
n_grp = 5
n_ref = 3
n_sentence = mdf['sentence'].nunique()
setences = []
refs = []
mdf = mdf.sort_values(by='sentence').reset_index(drop=True)
for i in range(n_sentence//n_grp): # 반드시 배수여야 함
    sidx = i * n_grp * n_ref
    eidx = sidx + n_grp * n_ref - 1
    pdf = mdf.loc[sidx:eidx]
    
    # record history
    script_file = f'{i}_mt_script.txt'
    ref_file = f'{i}_ref_script.txt'
    mdf.loc[sidx:eidx, 'script_file'] = script_file
    mdf.loc[sidx:eidx, 'ref_file'] = ref_file
    
    # file generation
    with open(script_file,'w') as f:
        print('\n'.join(pdf['sentence'].unique().tolist()))
        # write file
    with open(ref_file, 'w') as f:
        print('\n'.join(pdf['ref'].unique().tolist()))
        # write file

    # ENGINE CALL & LOG PARSING → 2.0
    
    mdf.loc[sidx:eidx, 'bleu'] = 2.0 + i


####################################################
#                 INTEGRATION TEST
####################################################

# MT CALL WITH TRANSCRIPTED BY SAME GROUPING WITH UNIT


####################################################
#                      ANALYSIS
####################################################
