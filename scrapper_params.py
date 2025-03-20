from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
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


# POST ES VIDEO O FOTO
def es_video(driver):
    try:
        audio_icon = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Activar o desactivar audio']")))       
        print(audio_icon)
        print("Es video, omitiendo...")
        return True
    except Exception as e:
        return False


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
    # Obtener número de posts, seguidores y seguidos 
    numposts_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
        By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[3]/ul/li[1]/div/span/span/span")))    
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
    numposts = numposts_element.text
    followers = followers_element.text
    following = following_element.text
    nombre = nombre_element.text
    presentacion = presentacion_element.text

    df = pd.DataFrame({
        'Usuario': [usr],
        'Posts': [numposts],
        'Seguidores': [followers],
        'Seguidos': [following],
        'Nombre': [nombre],
        'Presentacion': [presentacion]
    })

    print(f"Guardando información del perfil en: Dataset/{usr}/info.csv")
    df.to_csv(f"Dataset/{usr}/info.csv", index=False)

    # Variables auxiliares para scrappear
    n = 1
    max_images = 10
    max_rows = 10
    maxComents = 100

    # Bucle para recorrer los XPaths dinámicamente
    for i in range(1, max_rows):  
        for j in range(1, 4):    

            post_comments = []
            print(f"Analizando post de la fila {i} y la columna {j}")  

            #Post del feed en el que se ven 3 posts por linea                                                                            *        *
            post_infeed_xpath = f"/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[2]/div/div/div[{i}]/div[{j}]/a"

            #Etiqueta alt que da instagram a cada post:                                                                              *        *
            caption_xpath = f"/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[2]/div/div/div[{i}]/div[{j}]/a/div[1]/div[1]/img"

            #Verificador de que no es un video:                                                                                   *         *
            video_xpath = f"/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[2]/div/div/div[{i}]/div[{j}]/a/div[2]/div/div/svg"

            # Source                                                                                                                *        *
            source_xpath = f"/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[2]/div/div/div[{i}]/div[{j}]/a/div[1]/div[1]/img"

            #Numero de likes
            likes_xpath = f"  /html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/section[2]/div/div[2]/span/a/span/span"
            likes_xpath_2 = f"/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/section[2]/div/div/span/a/span/span"
            likes_xpath_3 = f"/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/section[2]/div/div[2]/span/a/span/span"
            likes_xpath_4 = f"/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/section[2]/div/div/span/a/span/span"

            #Pie de foto
            pie_foto_xpath = "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[1]/li/div/div/div[2]/div[1]/h1"
            pie_foto_xpath_2 = "/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[1]/li/div/div/div[2]/div[1]/h1"

            #Botón más comentarios
            mascoments_xpath = "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/li/div/button"
            mascoments_xpath_2 = "/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/li/div/button"

            time.sleep(random.randint(1,3))

            # CAPTION
            try:
                print("  Obteniendo caption...")
                # Obtenemos el caption del post
                post_element = driver.find_element(By.XPATH, caption_xpath)
                caption_text = post_element.get_attribute("alt")
                print(caption_text)
            except Exception as e:
                # No se encuentra el objeto pie de foto
                caption_text = "null"
                print("Error obteniendo caption")

            time.sleep(random.randint(1,3))

            # SOURCE
            try:
                print("  Obteniendo source...")
                openPost_element = driver.find_element(By.XPATH, source_xpath)
                img_src = openPost_element.get_attribute("src")
                print(img_src)
            except Exception as e:
                # No se encuentra el objeto post
                img_src = "null"
                print("Error obteniendo el source")

            time.sleep(random.randint(1,3))

            # CLICK EN EL POST
            try:
                print("  Clickando en el post...")
                # Buscar el elemento post
                post_element = driver.find_element(By.XPATH, post_infeed_xpath)
                post_element.click()
                time.sleep(random.randint(4, 6))
            except Exception as e:
                # No se encuentra el objeto post
                print("Error clickando post")

            time.sleep(random.randint(3,5))

            # VERIFICACIÓN DE VIDEO POR VOLUMEN
            if not es_video(driver=driver):

                # LIKES DEL POST
                try:
                    print("  Obteniendo likes...")
                    # Intentamos con el primer XPath
                    try:
                        likes_element = driver.find_element(By.XPATH, likes_xpath)
                    # Si falla, probamos con el segundo XPath
                    except Exception:
                        try:
                            likes_element = driver.find_element(By.XPATH, likes_xpath_2)
                        # Si falla, probamos con el tercer XPath
                        except Exception:
                            try:
                                likes_element = driver.find_element(By.XPATH, likes_xpath_3)
                            # Si falla, probamos con el cuarto XPath
                            except Exception:
                                likes_element = driver.find_element(By.XPATH, likes_xpath_4)
                    # Si alguno de los XPath funcionó
                    likes = likes_element.text
                    print(likes)
                except Exception as e:
                    # Si todos los XPath fallan
                    likes = "null"
                    print("Error obteniendo los likes")

                time.sleep(random.randint(1,3))

                # PIE DE FOTO DEL POST
                try:
                    print("  Obteniendo pie de foto...")
                    try:
                        # Intentamos con el primer XPath
                        piefoto_element = driver.find_element(By.XPATH, pie_foto_xpath)
                    except Exception:
                        # Si falla, probamos con el segundo XPath
                        piefoto_element = driver.find_element(By.XPATH, pie_foto_xpath_2)                    
                    piefoto = piefoto_element.text
                    print(piefoto)
                except Exception as e:
                    # No se encuentra el objeto post
                    piefoto = "null"
                    print("Error obteniendo el pie de foto")

                time.sleep(random.uniform(4.5,6.5))

                # CARGAR MAS COMENTARIOS
                for l in range(1, 10):
                    try:
                        # Intentamos con el primer XPath
                        try:
                            mascoments_element = driver.find_element(By.XPATH, mascoments_xpath)
                            mascoments_element.click()
                            time.sleep(random.uniform(4.5,6.5))
                        # Si falla probamos con el segundo
                        except Exception:
                            mascoments_element = driver.find_element(By.XPATH, mascoments_xpath_2)
                            mascoments_element.click()
                            time.sleep(random.uniform(4.5,6.5))
                    except Exception:
                        print("Error cargando mas comentarios")

                post_comments.append(f"POST NUMERO {n}")
                post_comments.append("")
                if caption_text:
                    post_comments.append("*** CAPTION ***")
                    post_comments.append(caption_text)
                    post_comments.append("")

                if likes:
                    post_comments.append("*** LIKES ***")
                    post_comments.append(likes)
                    post_comments.append("")

                if piefoto:
                    post_comments.append("*** PIE DE FOTO ***")
                    post_comments.append(piefoto)
                    post_comments.append("")

                post_comments.append("*** COMENTARIOS ***")

                print("  Obteniendo comentarios...")
                for k in range(1, maxComents):
                    # COMENTARIO Y SUS LIKES
                    #Comentarios                                                                                                                                          *
                    comentario_xpath = f"  /html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/div[{k}]/ul/div/li/div/div/div[2]/div[1]/span"
                    comentario_xpath_2 = f"/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/div[{k}]/ul/div/li/div/div/div[2]/div[1]/span"
                    comentario_xpath_3 = f"/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[2]/div/div/div[{k}]/ul/div/li/div/div/div[2]/div[1]/span"
                    comentario_xpath_3 = f"/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[2]/div/div/div[{k}]/ul/div/li/div/div/div[2]/div[1]/span"

                    #Likes comentario                                                                                                                                     *
                    likescomment_xpath = f"/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/div[{k}]/ul/div/li/div/div/div[2]/div[2]/span/button[1]/span"
                    likescomment_xpath_2 = f"/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/div[{k}]/ul/div/li/div/div/div[2]/div[2]/span/button[1]/span"

                    # LIKES DEL POST
                    try:
                        # Intentamos con el primer XPath
                        try:
                            comment_element = driver.find_element(By.XPATH, comentario_xpath)
                        # Si falla, probamos con el segundo XPath
                        except Exception:
                            try:
                                comment_element = driver.find_element(By.XPATH, comentario_xpath_2)
                            # Si falla, probamos con el tercer XPath
                            except Exception:
                                try:
                                    comment_element = driver.find_element(By.XPATH, comentario_xpath_3)
                                # Si falla, probamos con el cuarto XPath
                                except Exception:
                                    comment_element = driver.find_element(By.XPATH, comentario_xpath_4)
                        # Si alguno de los XPath funcionó
                        comment = comment_element.text
                        print(comment)
                        post_comments.append(comment)
                    except Exception as e:
                        # Si todos los XPath fallan
                        print(f"Error obteniendo el comentario numero {k}")
                        
                        # Verificación de likes después de obtener el comentario
                        try:
                            try:
                                com_likes_element = driver.find_element(By.XPATH, likescomment_xpath)
                                com_likes = com_likes_element.text
                                if com_likes:
                                    post_comments.append(com_likes)
                                    print(f"     Numero de likes del comentario {k}: {com_likes}")
                            except Exception:
                                com_likes_element = driver.find_element(By.XPATH, likescomment_xpath_2)
                                com_likes = com_likes_element.text
                                if com_likes:
                                    post_comments.append(com_likes)
                                    print(f"     Numero de likes del comentario {k}: {com_likes}")
                        except NoSuchElementException:
                            post_comments.append("0 Me gusta")
                            print("El comentario no tiene likes")
                        
                    except Exception as e:
                        print(f"    Error obteniendo el comentario numero {k}, es probable que sea un gif")
                        
                    if k % 15 == 0:
                        time.sleep(3)
                    else:
                        time.sleep(1)

                # GUARDAR INFORMACION
                createFolderForImages(usr, n)
                # Guardar imagen
                try:
                    # Descargar la imagen
                    response = requests.get(img_src)
                    response.raise_for_status()   # Verifica si hubo algún error en la solicitud

                    # Guardar la imagen en su carpeta correspondiente
                    image_name = f"post_{n}_image.jpg"
                    image_path = os.path.join(f"Dataset/{usr}/Post_{n}", image_name)

                    with open(image_path, "wb") as file:
                        file.write(response.content)
                    
                    print(f"Imagen descargada y guardada en {image_path}")

                except Exception:
                    print(f"Error al obtener la imagen del post {n}")


                # Comentarios
                try:
                    file_name = f"comentarios_post_{n}.txt"
                    file_path = os.path.join(f"Dataset/{usr}/Post_{n}", file_name)

                    with open(file_path, "w", encoding="utf-8") as file:
                        for linea in post_comments:
                            file.write(linea + "\n")
                    print(f"Contenido descargado y guardada en {file_path}")
                except Exception:
                    print(f"Error al guardar la informacion del post {n}")
                
                n += 1
                print(post_comments)

            # PASAR DE POST
            try:
                driver = request(driver=driver, url=profile_url)
                print("Pasamos al siguiente post")
                time.sleep(random.uniform(2.5,4.5))

            except Exception as e:
                # Si no se encuentra el elemento, pasar al siguiente
                print(f"Error saliendo del post")

            # Paramos el bucle al llegar a 10 posts
            if n > max_images:  
                break

        if n > max_images:  
            break

    print(f"Extracción de informacion de {usr} completada")    
    return driver
  

# Main function
def main():

    parser = argparse.ArgumentParser()

    # Añadir los argumentos esperados
    parser.add_argument('-u', '--user', required=True, help='Nombre de usuario')
    parser.add_argument('-p', '--password', required=True, help='Contraseña')
    parser.add_argument('-n', '--name', required=True, help='Nombre')

    # Analizar los argumentos
    args = parser.parse_args()
    user = args.user
    print(f"usuario: {user}")
    pwd = args.password
    username = args.name
    print(f"nombre de usuario a scrapear: {username}")

    driver = driverConfig()
    driver = request(driver=driver, url='https://www.instagram.com/accounts/login/')
    driver = manageCookies(driver=driver)
    driver = logIn(driver=driver, usr=user, pwd=pwd)
    createFolder(username)
    driver = buscarPerfil(driver=driver, usr=username)
    driver = getInfo(driver=driver, usr=username)


if __name__ == "__main__":
    main()