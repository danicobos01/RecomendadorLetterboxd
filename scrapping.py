import requests
from bs4 import BeautifulSoup
import cchardet as chardet
from concurrent.futures import ThreadPoolExecutor
import json

user = 'danicpppp'
prefix = "https://letterboxd.com"
numpag = 1

# Inicializar una lista vacia para almacenar informacion sobre las peliculas
movies = []

# Funcion que traduce un string de estrellas en una valoracion numerica
def starsToNumber(valoracion):
    cont = 0
    for i in range(0, len(valoracion)):
        if valoracion[i] == '★': cont += 2
        elif valoracion[i] == '½': cont += 1
    return cont


# Devuelve el año de estreno de una pelicula
def getYear(link):
    url = prefix + link
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    y = soup.find("small", class_ = "number")
    year = y.get_text()
    return year

# Devuelve generos de una pelicula
def getGenres(link): 
    url = prefix + link + "genres"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    g = soup.find("section", class_ = "section").find("div", {"id": "tab-genres"})\
        .find("div", class_="text-sluglist").find_all("a", class_="text-slug")
    genres = []
    for genre in g: 
        genres.append(genre.get_text())
    return genres

# Devuelve año y generos de la pelicula
def getInfoMovie(link):
    y = getYear(link)
    g = getGenres(link)
    return {"year_release" : y, "genres" : g}
    

# Para cada entrada de pelicula extrae toda la informacion importante
def funcion(entry):
    info = entry.find("div") 
    dic = getInfoMovie(info["data-film-slug"]) # data-film-slug contiene el link
    title = entry.find("img")
    print(title["alt"])
    rating = entry.find("span", class_="rating")
    if rating is not None: 
        valoracion = starsToNumber(rating.get_text())
    else: 
        valoracion = 0
    # Agregar un diccionario con la informacion de la pelicula a la lista
    dicMovies = {"title": title["alt"], "rating": valoracion}
    dicMovies.update(dic)
    movies.append(dicMovies)
    print(dicMovies)


next = True
while next:
    url = f"{prefix}/{user}/films/page/{numpag}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    movie_entries = soup.find_all("li", class_="poster-container")
    with  ThreadPoolExecutor(max_workers=len(movie_entries)) as executor:
        for entry in movie_entries:
            executor.submit(funcion, entry)
    
    if soup.find("a", class_="next") is None: 
        next = False
    else: 
        numpag += 1


# Imprimir en un json todas las peliculas del usuario 
with open(r'C:\Users\danic\Python Projects\Letterboxd Recomendador\pelis.json', 'w') as j:
        json.dump(movies, j, indent=2, separators=(",", ":"))


