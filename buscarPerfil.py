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
    return driver


# TARDAR RANDOM ESCRIBIENDO
def typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.5, 1.8))  # Reduced time for typing


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
    except:
        print("No se han podido aceptar correctamente las cookies")

    return driver


# CREAR EL DIRECTORIO POR USUARIO SINO EXISTE
def createFolder(folder_name):
    if not os.path.exists(f"Dataset/{folder_name}"):
        os.makedirs(f"Dataset/{folder_name}")


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

    except Exception as e:
        print(f"No se ha podido iniciar sesión: {e}")

    return driver


# BUSCAR PERFIL
def buscarPerfil(driver, usr):
    print("Buscando el perfil seleccionado...")
    try:
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

        # Esperar a que se carguen los datos del perfil
        time.sleep(5)

        return driver

    except Exception as e:
        print("Error:", e)
        return None



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

    driver.quit()


if __name__ == "__main__":
    main()
