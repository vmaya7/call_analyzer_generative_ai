import pandas as pd
import openai
import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
import urllib.request
openai.api_key  = os.getenv('OPENAI_API_KEY')
import json
import seaborn as sns
import boto3

import string
import matplotlib.pyplot as plt
import mplcyberpunk
plt.style.use("cyberpunk")

s3Client = boto3.client('s3')
s3 = boto3.resource('s3')

def get_completion(prompt, model="gpt-3.5-turbo",temperature=0): # Andrew mentioned that the prompt/ completion paradigm is preferable for this class
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def format_phrase(x, num= 5):
    x = x.split(' ')
    len_x = len(x)
    txt = ''
    for i, palabra in enumerate(x):
        if i == 0:
            txt = palabra + ' '
        elif i%num == 0:
            txt = txt + '\n' + palabra
        else:
            txt = txt + ' ' + palabra
    print(txt)
    return txt


def lambda_handler(event, context):
    """Lambda handler or main"""
    # print("Received event: " + json.dumps(event, indent=2))

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    response = s3Client.get_object(Bucket=bucket, Key=key)
    data = response['Body'].read()
    data = json.loads(data)
    print(data)
    # print(response['Body'].read())
    df = pd.DataFrame(data['results']['items'])
    df['confidence'] = df.alternatives.map(lambda x: x[0]['confidence'])
    df['content'] = df.alternatives.map(lambda x: x[0]['content'])
    df_s0 = df[df['speaker_label'] == 'spk_0'].reset_index()
    scam_text = ' '.join(df.content).replace(' .', '.').replace(' ,', ',').replace(' ?', '?').replace(' !', '!')
    print(f"scam_text {scam_text}")
    formato_json = """
        {json:
        {
          "score": ,
          "frases_clave_scam": [
            {
              "phrase": ,
              "score_scam": ,
              "justificacion": ,
              "recomendacion": ,
              "sentimiento": ,
            },
            {
              "phrase": ,
              "score_scam": ,
              "justificacion": ,
              "sentimiento": ,

            }
          ],
        },
        markdown: ]"""
    prompt = f"""
    Imagina que eres un modelo de inteligencia artificial de "scam detector". Évalua el siguiente texto entre comillas simples '{scam_text}' y realiza las siguientes tareas:
    1. Identifica y extrae las frases potencialmente estafadoras dentro del texto sin modificar el texto original. Para cada una de las frases, haz las siguientes acciones: 
      1.1 Genera un score de estafa de un solo número con rango del 1 al 100 
      1.2 Justifica el score asignado en 10 palabras. 
      1.3 Agrega recomendiaciones particulares para cada frase.
      1.4 Agrega el sentimiento de cada frase en "Positivo", "Negativo"
    2- Muestras los resultados en formato json con este formato: {formato_json}, en español.
    """
    response = get_completion(prompt)
    print(response)


    prompt = f"""
    Eres un experto en fraude telefónico, tu tarea es generar un reporte especializado en fraude utilizando la información encontrada en el siguiente json entre comillas simples '{response}'.
    La salida debe ser código en Marckdownm con texto en español. El documento tiene que tener la siguiente información:
    1. Título: 'ScamReport - ScamBusters'
    3. Score de fraude de la llamada
    4. No coloques introducción
    4. Análisis de Frases Clave de Estafas Telefónicas
        - Frase fraudulenta
        - Score
        - Justificación
        - Recomendación
    """
    response_md = get_completion(prompt)
    print(response_md)
    s3object = s3.Object('wizeline-generative-hackaton-results', f"{key}.md")
    result = s3object.put(
        Body=(response_md)
    )
    out = json.loads(response)
    score = out['score']
    phrases= pd.DataFrame(out['frases_clave_scam'])
    print(phrases)
    phrases['start_word'] = phrases.phrase.map(lambda x: x.split(' ')[0])
    phrases['end_word'] = phrases.phrase.map(lambda x: x.split(' ')[-1])
    print(phrases)
    df_s0.content = df_s0.content.str.lower()
    phrases['start_time'] = None
    phrases['end_time'] = None
    times = []
    for index_phrase, phrase in enumerate(phrases.phrase):
        print('******** ',phrase)
        words = phrase.split(' ')
        first_word = words[0].lower()
        next_word = words[1].lower()
        nn_word  = words[2].lower()
        nnn_word  = words[3].lower()
        last_word  = words[-1].lower()
        temp_df = df_s0[df_s0.content == first_word]
        x= [first_word, next_word, nn_word]
        print('x: ', x)
        for i in temp_df.index: # Por cada frase
            print('y', df_s0.loc[i, 'content'], df_s0.loc[i +1, 'content'], df_s0.loc[i + 2, 'content'])
            sum = (df_s0.loc[i, 'content'] in x)  + (df_s0.loc[i +1, 'content'] in x)  +(df_s0.loc[i +2, 'content'] in x)  +(df_s0.loc[i + 3, 'content'] in x) 
            if sum >2 :
                print('yes')
                
                time  = df_s0.loc[i, 'start_time']
                print('++++time yest: ', time)
                if time not in times:
                    phrases.loc[index_phrase, 'start_time'] = time
                else:
                    print('++++time no: ', time)
                    times.append(time)
    phrases['score_scam'] = phrases['score_scam'].astype(float)
    phrases['start_time'] = phrases['start_time'].astype(float)
    phrases['emoji'] = phrases['sentimiento'].map(lambda x: '😃' if x == 'feliz' else '☹️' )

    phrases.phrase = phrases.phrase.map(lambda x: format_phrase(x))
    df_temp = phrases.copy()
    df_temp.loc[len(df_temp.index)] = df_temp.iloc[-1]
    df_temp.loc[len(df_temp.index) - 1, 'start_time'] = df_temp.loc[len(df_temp.index) - 1, 'end_time']
    plot = sns.lineplot(data=df_temp, x = 'start_time', y = 'score_scam', color = 'r').set(title='Scam Score')
    for i in phrases.index:
        x = float(phrases.loc[i, 'start_time'])
        y = float(phrases.loc[i, 'score_scam'])
        text = phrases.loc[i, 'emoji']
        phrase = phrases.loc[i, 'phrase']

        _ = plt.annotate(phrase, xy=(x,y), xytext=(x, y - 40),
                arrowprops=dict(facecolor='black', shrink=0.05, headwidth=10, width=2, color = 'white'))
        
        _ = plt.annotate(text, xy=(x,y), xytext=(x, y - 45),
                fontname='Segoe UI Emoji', # this is the param added
            fontsize=20)
    plt.xlabel("Score")
    plt.xlabel("Time [s]")
    mplcyberpunk.add_glow_effects(gradient_fill=True)
    plt.savefig('/tmp/out.png', bbox_inches='tight')

    s3Client.upload_file('/tmp/out.png', "wizeline-generative-hackaton-results", "out.png",
               ExtraArgs=dict(ContentType='image/png'))
    print("Results uploaded!")

if __name__ == "__main__":
    lambda_handler(None, None)
