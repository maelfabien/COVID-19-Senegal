# COVID-19 au Senegal

Ce repo contient une base de données mise à jour **quotidiennement** des cas de COVID-19 au Sénégal. La table de donnée CSV a été contruite à partir des tweets du Ministère de la Santé et de l'Action Sociale du Sénégal. La source peut être trouvée ici: https://twitter.com/MinisteredelaS1

Le lien suivant peut être utilisé comme source de données dynamique:
https://raw.githubusercontent.com/maelfabien/COVID-19-Senegal/master/COVID_Senegal.csv

Sur [ce site](https://covid-sn.onrender.com/) : https://covid-sn.onrender.com/, vous retrouverez l'application d'analyse de ces données.

![image](demo.png)

## Que contient ce repo?

- Le notebook `COVID_Senegal.ipynb` contient une analyse de ces données.
- Le dossier `app` contient l'application. Les technologies utilisées sont les suivantes:
	- Python
	- Bokeh
	- Altair
	- Streamlit	

## Comment utiliser ce repo?

- Utilisez le lien vers le set de données CSV (séparé par des ";") pour vos analyses
- Utilisez l'application:

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

L'application est déployée en utilisant [Render.com](https://render.com/)
