# ScamDetector

ScamDetector es una aplicación que utiliza inteligencia artificial para analizar grabaciones de llamadas telefónicas y determinar la probabilidad de que sean estafas. Proporciona un informe con una puntuación del 0 al 100, así como frases clave que indican posibles estafas, junto con recomendaciones y explicaciones detalladas sobre por qué se considera fraudulenta cada frase.

![scamdetector_logo-removebg-preview](https://github.com/vmaya7/call_analyzer_generative_ai/assets/47407743/4045bcab-9f91-4261-adfa-056606efff28)


## Cómo funciona

1. Se toma una grabación de llamada telefónica y se transcribe utilizando AWS Transcribe.
2. La transcripción se pasa a través de un prompt de ChatGPT especializado, que proporciona un archivo JSON con la información de puntuacion, frases clave, puntuación de las frases y explicaciones asociadas.
3. Los datos se procesan y se generan gráficas que representan el score de las frases a lo largo del tiempo, el sentimiento de cada frase a lo largo del tiempo y la representación visual de las frases.

## Instalación

Para utilizar ScamDetector, sigue estos pasos:

1. Clona el repositorio de ScamDetector en tu máquina local:

```
git clone https://github.com/vmaya7/call_analyzer_generative_ai
```

2. Instala todas las dependencias necesarias:

```
pip install -r requirements.txt
```


3. Configura AWS siguiendo los pasos [AQUI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html)


## Uso

1. Coloca las grabaciones de llamadas telefónicas en la carpeta `recordings`.
2. Ejecuta el script principal:

```
python main.py
```

3. Se generará un informe en formato Markdown con los datos de puntuación, frases clave y explicaciones en el directorio `output`.

## Contribuir

Si deseas contribuir a ScamDetector, sigue estos pasos:

1. Haz un fork del repositorio ScamDetector.
2. Crea una rama con la nueva funcionalidad o corrección de errores: 

```
git checkout -b nueva-funcionalidad
```

3. Realiza tus cambios y realiza commits descriptivos:

```
git commit -m "Añadir nueva funcionalidad"
```

4. Envía tus cambios al repositorio remoto:

```
git push origin nueva-funcionalidad
```

5. Crea una pull request en GitHub para que podamos revisar tus cambios.

## Créditos

ScamDetector ha sido desarrollado por ScamBusters.

## Licencia

Este proyecto se encuentra bajo la Licencia MIT. Consulta el archivo [LICENSE](https://github.com/vmaya7/call_analyzer_generative_ai/edit/main/LICENSE) para obtener más información.
