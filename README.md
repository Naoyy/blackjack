# Blackjack 
Ce projet contient deux versions du jeu Blackjack :

* [Version Web (GUI)](https://blackjack-gui-naoyy.streamlit.app/): branche `main`
* Version CLI: branche `feature/cli-version`

---

## Installation

Créer un venv et installer les requirements :

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Jouer à la version GUI
Il est possible de jouer directement ici [blackjack-gui-naoyy.streamlit.app](https://blackjack-gui-naoyy.streamlit.app/)

```
git clone https://github.com/Naoyy/blackjack.git
cd blackjack
streamlit run src\main.py
```

---


## Jouer à la version CLI

Pour accéder à la version CLI du jeu :

```
git clone https://github.com/Naoyy/blackjack.git
cd blackjack
git checkout feature/cli-version
```

```
python src/main.py
```

---


## Notes

* Python (3.10+)

* Attention:
* Faire blackjack donne des gains arrondis (en misant 5 on gagne 7 au lieu de 7.5 normalement)
* On ne joue qu'avec 1 paquet de cartes contrairement aux casinos (libre à vous de compter les cartes)

- 1 paquet = 52 cartes 
- 13 cartes par couleurs
- 4 couleurs