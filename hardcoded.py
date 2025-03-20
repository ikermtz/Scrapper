from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import pandas as pd  
import requests
import argparse
import os
import csv
import subprocess
import wget
import cv2


# CREACION Y CONFIGURACION DEL DRIVER
def driverConfig():

    print("")
    print("Configuración de drivers en curso...")
    # Opciones de configuración para Chrome
    options = webdriver.ChromeOptions()

    # Cambiar el User-Agent
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

    # Ocultar que Chrome está siendo controlado por Selenium
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Desactivar el gestor de contraseñas y autocompletado de Chrome
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    options.add_experimental_option("prefs", prefs)

    # Inicializar el driver de Chrome con las opciones configuradas
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    print("Drivers correctamente configurados")
    print("")
    return driver


# TARDAR RANDOM ESCRIBIENDO
def typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.3, 1.8))  


# PETICION HTTP GET
def request(driver, url):
    driver.get(url)
    time.sleep(random.randint(1, 3))
    return driver


# GESTIONAR LAS COOKIES DE INICIO DE SESION
def manageCookies(driver):
    try:
        btn_cookies = driver.find_element(By.XPATH, "//button[contains(text(), 'Permitir todas las cookies')]")
        btn_cookies.click()
        print("Aceptamos correctamente las cookies")
        print("")
    except:
        print("No se han podido aceptar correctamente las cookies")

    return driver


# CREAR EL DIRECTORIO POR USUARIO SINO EXISTE
def createFolder(username):
    if not os.path.exists(f"Dataset/{username}"):
        os.makedirs(f"Dataset/{username}")
        print("Directorio correctamente creado")


# CREAR EL DIRECTORIO POR USUARIO SINO EXISTE
def createFolderForImages(username, i):
    if not os.path.exists(f"Dataset/{username}/Post_{i}"):
        os.makedirs(f"Dataset/{username}/Post_{i}")
        print(f"Directorio 'Dataset/{username}/Post_{i}' correctamente creado")


# GESTION DEL LOG IN 
def logIn(driver, usr, pwd):
    print("Ingresando las credenciales...")
    try:
        # Esperar a que aparezca el formulario de inicio de sesión
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
        time.sleep(1)

        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")

        typing(username_input, usr)
        time.sleep(random.uniform(0.5, 1.5))
        typing(password_input, pwd)

        # Enviar formulario
        password_input.send_keys(Keys.RETURN)

        # Descartar guardar info al iniciar sesión
        btn_ahora_no = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Ahora no')]")))
        btn_ahora_no.click()

        print("Inicio de sesión correcto")
        print("")

    except Exception as e:
        print(f"No se ha podido iniciar sesión: {e}")

    return driver


# BUSCAR PERFIL
def buscarPerfil(driver, usr):
    print("Buscando el perfil seleccionado...")
    try:
        # Verificar si hace falta crear su carpeta 
        createFolder(username=usr)

        driver.get("https://www.instagram.com/")
        time.sleep(2)

        search_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Búsqueda' or text()='Search']"))
        )
        search_icon.click()
        time.sleep(1)

        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
            By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div[2]/div/div/div[1]/div/div/input")))
        search_box.clear()
        search_box.click()
        time.sleep(random.randint(1, 3))

        print(f"Buscando a {usr}...")
        typing(search_box, usr)
        time.sleep(3)

        first_result = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '/{usr}/')]")))
        first_result.click()
        print(f"Perfil de {usr} encontrado con éxito.")
        print("")

        # Esperar a que se carguen los datos del perfil
        time.sleep(5)

        return driver

    except Exception as e:
        print("Error:", e)
        return None


# OBTENER INFORMACION DE UN PERFIL
def getInfo(driver, usr):

    time.sleep(random.randint(2,4))
    profile_url = f"https://www.instagram.com/{usr}/"
    print(f"Extrayendo informacion de {usr}...")
    # Obtener el número de seguidores y seguidos
    followers_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
        By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[3]/ul/li[2]/div/a/span/span/span")))
    following_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
        By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[3]/ul/li[3]/div/a/span/span/span")))

    # Obtener el nombre y la descripción
    nombre_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
        By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[4]/div/div[1]/span")))
    presentacion_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
        By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[4]/div/span/div/span")))

    # Dataframe con la información del perfil
    followers = followers_element.text
    following = following_element.text
    nombre = nombre_element.text
    presentacion = presentacion_element.text

    df = pd.DataFrame({
        'Usuario': [usr],
        'Seguidores': [followers],
        'Seguidos': [following],
        'Nombre': [nombre],
        'Presentacion': [presentacion]
    })

    print(df)

    # Variables auxiliares para scrappear
    post_urls = []
    post_captions = []
    post_comments = {}
    k = 1
    max_images = 10


    # VERSION PASO A PASO CON UN POST UNICO SIN ITERAR                                                                         
    #Post del feed en el que se ven 3 posts por linea                                                                          *      *
    post_infeed_xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[2]/div/div/div[2]/div[2]/a"

    #Etiqueta alt que da instagram a cada post:                                                                             *      *
    caption_xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[2]/div/div/div[2]/div[2]/a/div[1]/div[1]/img"

    #Verificador de que no es un video:                                                                                   *      *
    video_xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[2]/div/div/div[2]/div[2]/a/div[2]/div/div/svg"

    # Source                                                                                                              *      *
    source_xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[2]/div/div/div[2]/div[2]/a/div[1]/div[1]/img"

    #Numero de likes
    likes_xpath = "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/section[2]/div/div[2]/span/a/span"
    likes_xpath_2 = "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/section[2]/div/div/span/a/span"

    #Pie de foto
    pie_foto_xpath = "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[1]/li/div/div/div[2]/div[1]/h1"

    #Comentarios                                                                                                                                      *
    comentario_xpath = "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/div[2]/ul/div/li/div/div/div[2]/div[1]/span"

    #Likes comentario                                                                                                                                   *
    likescomment_xpath = "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/div[2]/ul/div/li/div/div/div[2]/div[2]/span/button[1]/span"

    time.sleep(random.randint(1,3))

    # Verificar si es video o no
    try:
        driver.find_element(By.XPATH, video_xpath)
        print("El elemento es un video, omitiendo")
        #continue  # Saltar al siguiente elemento
    except:
        pass  # No es un video, continuar

    time.sleep(random.randint(1,3))

    # CAPTION
    try:
        # Obtenemos el caption del post
        print("Caption:")
        post_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, caption_xpath)))
        caption_text = post_element.get_attribute("alt")
        print(caption_text)
    except Exception as e:
        # No se encuentra el objeto pie de foto
        print(f"Error obteniendo caption: {e}")

    time.sleep(random.randint(1,3))

    # SOURCE
    try:
        print("Image source:")
        openPost_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, source_xpath)))
        img_src = openPost_element.get_attribute("src")
        print(img_src)
    except Exception as e:
        # No se encuentra el objeto post
        print(f"Error obteniendo el source: {e}")

    time.sleep(random.randint(1,3))

    # CLICK EN EL POST
    try:
        # Buscar el elemento post
        print("Click in the post")
        post_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, post_infeed_xpath)))
        post_element.click()
        time.sleep(random.randint(2,4))
    except Exception as e:
        # No se encuentra el objeto post
        print(f"Error clickando post: {e}")

    time.sleep(random.randint(1,3))

    # LIKES DEL POST
    try:
        print("Likes")
        # Intentamos con el primer XPath
        try:
            likes_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, likes_xpath_2)))
        # Si falla, probamos con el segundo XPath
        except Exception:
            likes_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, likes_xpath)))
        
        # Si alguno de los XPath funcionó
        likes = likes_element.text
        print(likes)

    except Exception as e:
        # Si ambos XPath fallan
        print(f"Error obteniendo los likes: {e}")

    time.sleep(random.randint(1,3))

    # PIE DE FOTO DEL POST
    try:
        print("Pie de foto")
        piefoto_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, pie_foto_xpath)))
        piefoto = piefoto_element.text
        print(piefoto)
    except Exception as e:
        # No se encuentra el objeto post
        print(f"Error obteniendo el pie de foto: {e}")

    time.sleep(random.randint(1,3))

    # COMENTARIO Y SUS LIKES
    try:
        print("Comentario")
        comment_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, comentario_xpath)))
        comment = comment_element.text
        print(comment)
        
        # Verificación de likes después de obtener el comentario
        try:
            likes_element = driver.find_element(By.XPATH, likescomment_xpath)
            if likes_element.text:
                print(f"Likes del comentario: {likes_element.text}")
            else:
                print("El comentario tiene 0 likes")
        except NoSuchElementException:
            print("El comentario no tiene likes")
        
    except Exception as e:
        print(f"Error obteniendo el comentario: {e}")

    time.sleep(random.randint(1,3))

# Main function
def main():
    # Credenciales de inicio de sesión
    my_user = "manolomountaineer"
    my_pwd = "I1k3e0r1&"
    usr = "cbum"
    usr_2 = "davidlaid"
    usr_3 = "cristiano"
    usr_4 = "rafamoratete"

    driver = driverConfig()
    driver = request(driver=driver, url='https://www.instagram.com/accounts/login/')
    driver = manageCookies(driver=driver)
    driver = logIn(driver=driver, usr=my_user, pwd=my_pwd)

    createFolder(usr)
    driver = buscarPerfil(driver=driver, usr=usr)
    getInfo(driver=driver, usr=usr)

    driver.quit()


if __name__ == "__main__":
    main()
