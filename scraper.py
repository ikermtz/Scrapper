from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from PIL import Image
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
import shutil


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
    if not os.path.exists(f"Apuestas/{username}"):
        os.makedirs(f"Apuestas/{username}")
        print("Directorio correctamente creado")


# CREAR EL DIRECTORIO POR USUARIO SINO EXISTE
def createFolderForImages(username, i):
    if not os.path.exists(f"Apuestas/{username}/Post_{i}"):
        os.makedirs(f"Apuestas/{username}/Post_{i}")
        print(f"Directorio 'Apuestas/{username}/Post_{i}' correctamente creado")


# POST ES VIDEO O FOTO
def es_video(driver):
    try:
        audio_icon = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Activar o desactivar audio']")))       
        print(audio_icon)
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
            By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div/div[2]/div/div/div[1]/div/div/input")))
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
    numposts_xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[3]/ul/li[1]/div/span/span/span"
    followers_xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[3]/ul/li[2]/div/a/span/span/span"
    following_xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[3]/ul/li[3]/div/a/span/span/span"
    # Obtener el nombre y la descripción
    nombre_xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[4]/div/div[1]/span"
    presentacion_xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[4]/div/span/div/span"

    try:
        print("  Obteniendo numero de posts...")
        # Obtenemos numero de posts
        numposts_element = driver.find_element(By.XPATH, numposts_xpath)
        numposts = numposts_element.text
        print(f"  Numero de posts: {numposts}")
    except Exception as e:
        # No se encuentra el objeto 
        numposts = 0
        print("Error obteniendo numero de posts")

    try:
        print("  Obteniendo numero de followers...")
        # Obtenemos el numero de followers
        followers_element = driver.find_element(By.XPATH, followers_xpath)
        followers = followers_element.text
        print(f"  Numero de followers: {followers}")
    except Exception as e:
        # No se encuentra el objeto 
        followers = 0
        print("Error obteniendo numero de followers")

    try:
        print("  Obteniendo numero de following...")
        # Obtenemos el following
        following_element = driver.find_element(By.XPATH, following_xpath)
        following = following_element.text
        print(f"  Numero de followers: {following}")
    except Exception as e:
        # No se encuentra el objeto 
        following = 0
        print("Error obteniendo numero de following")

    try:
        print("  Obteniendo nombre...")
        # Obtenemos el nombre
        nombre_element = driver.find_element(By.XPATH, nombre_xpath)
        nombre = nombre_element.text
        print(f"  Nombre: {nombre}")
    except Exception as e:
        # No se encuentra el objeto 
        nombre = "null"
        print("Error obteniendo nombre")
    
    try:
        print("  Obteniendo presentacion...")
        # Obtenemos presentacion
        presentacion_element = driver.find_element(By.XPATH, presentacion_xpath)
        presentacion = presentacion_element.text
        print(f"  Presentacion: {presentacion}")
    except Exception as e:
        # No se encuentra el objeto 
        presentacion = "null"
        print("Error obteniendo presentacion")

    df = pd.DataFrame({
        'Usuario': [usr],
        'Posts': [numposts],
        'Seguidores': [followers],
        'Seguidos': [following],
        'Nombre': [nombre],
        'Presentacion': [presentacion]
    })

    print(f"Guardando información del perfil en: Apuestas/{usr}/info.csv")
    df.to_csv(f"Apuestas/{usr}/info.csv", index=False)
    print("")

    print("Vamos a scrapear la informacion de este perfil")
    print("")

    # Variables auxiliares para scrappear
    n = 1
    max_posts = 12
    max_rows = 4
    maxComents = 100

    # Bucle para recorrer los XPaths dinámicamente
    for i in range(1, max_rows):  
        for j in range(1, 4):    

            post_comments = []
            print(f"Analizando post de la fila {i} y la columna {j}")  

            #Post del feed en el que se ven 3 posts por linea                                                                                *        *
            post_infeed_xpath = f"/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[2]/div/div/div/div[{i}]/div[{j}]/a"

            #Etiqueta alt que da instagram a cada post:                                                                                  *        *
            caption_xpath = f"/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[2]/div/div/div/div[{i}]/div[{j}]/a/div[1]/div[1]/img"
                                 
            # Source                                                                                                                    *        *
            source_xpath = f"/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[2]/div/div/div/div[{i}]/div[{j}]/a/div[1]/div[1]/img"

            #Numero de likes
            likes_xpath = f"/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/section[2]/div/div[2]/span/a/span/span"
            likes_xpath_2 = f"/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/section[2]/div/div/span/a/span/span"
            likes_xpath_3 = f"/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/section[2]/div/div[2]/span/a/span/span"
            likes_xpath_4 = f"/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/section[2]/div/div/span/a/span/span"

            #Pie de foto
            pie_foto_xpath = "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[1]/li/div/div/div[2]/div[1]/h1"
            pie_foto_xpath_2 = "/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[1]/li/div/div/div[2]/div[1]/h1"

            #Botón más comentarios
            mascoments_xpath = "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/li/div/button"
            mascoments_xpath_2 = "/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/li/div/button"


            # CAPTION
            try:
                print("  Obteniendo caption...")
                # Obtenemos el caption del post
                post_element = driver.find_element(By.XPATH, caption_xpath)
                caption_text = post_element.get_attribute("alt")
                print(caption_text)                    
                print("")
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
                print("")
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
            
            except Exception:
                # No se encuentra el objeto post
                print("Error clickando post")
            
            
            # SCRAPEAR VIDEOS
            if es_video(driver=driver):

                print("  Post de tipo video")

                # RECORTES
                div_xpath_1 = "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[1]"
                div_xpath_2 = "/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[1]"

                try:
                    try:
                        mydiv = driver.find_element(By.XPATH, div_xpath_1)
                    except Exception:
                        mydiv = driver.find_element(By.XPATH, div_xpath_2)

                    # Coordenadas y tamaño
                    location = mydiv.location
                    size = mydiv.size

                    x = int(location['x'])
                    y = int(location['y'])
                    width = int(size['width'])
                    height = int(size['height'])

                    image_files = []
                    segundos = 15
                    framesSeg = 5

                    print("     Procediendo a hacer las capturas")

                    for i in range(segundos * framesSeg):
                        timestamp = time.time()

                        # Captura pantalla completa
                        driver.save_screenshot('Capturas/pagina_completa.png')

                        # Recorta el div
                        imagen = Image.open('Capturas/pagina_completa.png')
                        imagen_recortada = imagen.crop((x, y, x + width, y + height))
                        
                        # Guarda la imagen recortada
                        image_path = f'Capturas/captura_div_{i + 1}.png'
                        imagen_recortada.save(image_path)
                        image_files.append(image_path)

                        # Espera ~0.2 segundos para hacer 5 capturas por segundo
                        espera = time.time() - timestamp
                        time.sleep(max(0, 1/framesSeg - espera))
                    
                    print("     Construyendo video...")

                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec para .mp4
                    video_path = 'Capturas/video.mp4'
                    video_writer = cv2.VideoWriter(video_path, fourcc, framesSeg, (width, height))

                    # Añadir las imágenes al video
                    for image_file in image_files:
                        frame = cv2.imread(image_file)
                        video_writer.write(frame)

                    # Liberar el objeto de video
                    video_writer.release()

                    print("  Video obtenido")

                except Exception as e:
                    print("No se ha podido acceder al elemento de video")

                time.sleep(random.randint(1,3))

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
                    print("")
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
                    print("")
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
                    #Comentarios                                                                                                                                        *
                    comentario_xpath = f"/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/div[{k}]/ul/div/li/div/div/div[2]/div[1]/span"
                    comentario_xpath_2 = f"/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/div[{k}]/ul/div/li/div/div/div[2]/div[1]/span"
                    comentario_xpath_3 = f"/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[2]/div/div/div[{k}]/ul/div/li/div/div/div[2]/div[1]/span"
                    comentario_xpath_4 = f"/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[2]/div/div/div[{k}]/ul/div/li/div/div/div[2]/div[1]/span"

                    # User del comentario                                                                                                                            *
                    userCom_xpath = f"/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/div[{k}]/ul/div/li/div/div/div[2]/h3/div/span/span/div/a"
                                    
                    #Likes comentario                                                                                                                                     *
                    likescomment_xpath = f"/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/div[{k}]/ul/div/li/div/div/div[2]/div[2]/span/button[1]/span"
                    likescomment_xpath_2 = f"/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/div[{k}]/ul/div/li/div/div/div[2]/div[2]/span/button[1]/span"
                    
                    # COMENTARIOS DEL POST
                    try:

                        # USUARIO DELCOMENTARIO
                        try:
                            usr_element = driver.find_element(By.XPATH, userCom_xpath)
                            usrCom = usr_element.text
                            print(f"Usuario del comentario {k}: {usrCom}")
                            post_comments.append(usrCom)
                            
                        except Exception:
                            print(f"No se pudo obtener el usuario del comentario {k}")

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
                    
                        # LIKES DEL COMENTARIO
                        try:
                            try:
                                com_likes_element = driver.find_element(By.XPATH, likescomment_xpath)
                                com_likes = com_likes_element.text
                                if com_likes:
                                    post_comments.append(com_likes)
                                    print(f"     Numero de likes del comentario: {com_likes}")
                            except Exception:
                                com_likes_element = driver.find_element(By.XPATH, likescomment_xpath_2)
                                com_likes = com_likes_element.text
                                if com_likes:
                                    if com_likes == "Responder":
                                        com_likes = "0 Me gusta"
                                    post_comments.append(com_likes)
                                    print(f"     Numero de likes del comentario: {com_likes}")
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
                
                # MOVER VIDEO DE CAPTURAS/ A APUESTAS/{USR}/POST_{N}/
                path_inicio = 'Capturas'
                video = None

                # Comprobar si la carpeta Capturas existe
                if os.path.exists(path_inicio) and os.path.isdir(path_inicio):
                    # Buscar el archivo .mp4 en Capturas/
                    for archivo in os.listdir(path_inicio):
                        if archivo.endswith('.mp4'):
                            video = archivo
                            break

                    if video:
                        ruta_origen = os.path.join(path_inicio, video)
                        ruta_destino = os.path.join('Apuestas', usr, f'Post_{n}')
                        os.makedirs(ruta_destino, exist_ok=True)  # Crear carpeta destino si no existe
                        
                        # Mover el archivo .mp4
                        shutil.move(ruta_origen, ruta_destino)
                        
                        # Eliminar todos los archivos en Capturas/
                        for archivo in os.listdir(path_inicio):
                            ruta_archivo = os.path.join(path_inicio, archivo)
                            if os.path.isfile(ruta_archivo):
                                os.remove(ruta_archivo)
                        print(f"  Archivo {video} movido a {ruta_destino} y carpeta Capturas limpiada.")
                    else:
                        print("No se encontró archivo .mp4 en la carpeta Capturas.")
                else:
                    print(f"La carpeta {path_inicio} no existe.")

                # Comentarios
                try:
                    file_name = f"comentarios_post_{n}.txt"
                    file_path = os.path.join(f"Apuestas/{usr}/Post_{n}", file_name)

                    with open(file_path, "w", encoding="utf-8") as file:
                        for linea in post_comments:
                            file.write(linea + "\n")
                    print(f"  Contenido descargado y guardada en {file_path}")
                except Exception:
                    print(f"Error al guardar la informacion del post {n}")
                
                print(f"  Post numero {n} analizado")
                n += 1
                print(post_comments)


            # SCRAPEAR FOTOS
            else:

                print("  Post de tipo foto")

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
                    print("")
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
                    print("")
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
                    #Comentarios                                                                                                                                        *
                    comentario_xpath = f"/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/div[{k}]/ul/div/li/div/div/div[2]/div[1]/span"
                    comentario_xpath_2 = f"/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/div[{k}]/ul/div/li/div/div/div[2]/div[1]/span"
                    comentario_xpath_3 = f"/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[2]/div/div/div[{k}]/ul/div/li/div/div/div[2]/div[1]/span"
                    comentario_xpath_4 = f"/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[2]/div/div/div[{k}]/ul/div/li/div/div/div[2]/div[1]/span"
                
                    # User del comentario                                                                                                                            *
                    userCom_xpath = f"/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/div[{k}]/ul/div/li/div/div/div[2]/h3/div/span/span/div/a"
                                                
                    #Likes comentario                                                                                                                                     *
                    likescomment_xpath = f"/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/div[{k}]/ul/div/li/div/div/div[2]/div[2]/span/button[1]/span"
                    likescomment_xpath_2 = f"/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[3]/div/div/div[{k}]/ul/div/li/div/div/div[2]/div[2]/span/button[1]/span"
                    
                    # COMENTARIOS DEL POST
                    try:

                        # USUARIO DEL COMENTARIO
                        try:
                            usr_element = driver.find_element(By.XPATH, userCom_xpath)
                            usrCom = usr_element.text
                            print(f"Usuario del comentario {k}: {usrCom}")
                            post_comments.append(usrCom)
                            
                        except Exception:
                            print(f"No se pudo obtener el usuario del comentario {k}")

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
                                    if com_likes == "Responder":
                                        com_likes = "0 Me gusta"
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

                    print("")

                # GUARDAR INFORMACION
                createFolderForImages(usr, n)
                # Guardar imagen
                try:
                    # Descargar la imagen
                    response = requests.get(img_src)
                    response.raise_for_status()   # Verifica si hubo algún error en la solicitud

                    # Guardar la imagen en su carpeta correspondiente
                    image_name = f"post_{n}_image.jpg"
                    image_path = os.path.join(f"Apuestas/{usr}/Post_{n}", image_name)

                    with open(image_path, "wb") as file:
                        file.write(response.content)
                    
                    print(f"  Imagen descargada y guardada en {image_path}")

                except Exception:
                    print(f"Error al obtener la imagen del post {n}")


                # Comentarios
                try:
                    file_name = f"comentarios_post_{n}.txt"
                    file_path = os.path.join(f"Apuestas/{usr}/Post_{n}", file_name)

                    with open(file_path, "w", encoding="utf-8") as file:
                        for linea in post_comments:
                            file.write(linea + "\n")
                    print(f"  Contenido descargado y guardada en {file_path}")
                except Exception:
                    print(f"Error al guardar la informacion del post {n}")
                
                print(f"  Post numero {n} analizado")
                n += 1
                print(post_comments)

            time.sleep(random.randint(3,5))

            # PASAR DE POST
            try:
                driver = request(driver=driver, url=profile_url)
                print("Pasamos al siguiente post")
                time.sleep(random.uniform(2.5,4.5))

            except Exception as e:
                # Si no se encuentra el elemento, pasar al siguiente
                print(f"Error saliendo del post")

            # Paramos el bucle al llegar a max_posts
            if n > max_posts:  
                break

        if n > max_posts:  
            break
    
    print(f"Extracción de informacion de {usr} completada")    
    return driver
  

# Main function
def main():
    # Credenciales de inicio de sesión
    #my_user = "srcherchesov"
    #my_pwd = "I1k3e0r1&"
    my_user = "juanirpuerta"
    my_pwd = "juani52!"
    username = "footballtipstter"

    driver = driverConfig()
    driver = request(driver=driver, url='https://www.instagram.com/accounts/login/')
    driver = manageCookies(driver=driver)
    driver = logIn(driver=driver, usr=my_user, pwd=my_pwd)

    createFolder(username)
    driver = buscarPerfil(driver=driver, usr=username)
    driver = getInfo(driver=driver, usr=username)

    driver.quit()


if __name__ == "__main__":
    main()
