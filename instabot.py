import os
import random
import string
import time
import requests
from datetime import datetime
from instapy import InstaPy
from termcolor import colored

print(colored("     ██╗███╗   ██╗███████╗████████╗ █████╗ ██████╗  ██████╗ ████████╗", 'cyan'))
print(colored("     ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝", 'cyan'))
print(colored("     ██║██╔██╗ ██║███████╗   ██║   ███████║██████╔╝██║   ██║   ██║   ", 'cyan'))
print(colored("     ██║██║╚██╗██║╚════██║   ██║   ██╔══██║██╔══██╗██║   ██║   ██║   ", 'cyan'))
print(colored("     ██║██║ ╚████║███████║   ██║   ██║  ██║██████╔╝╚██████╔╝   ██║   ", 'cyan'))
print(colored("     ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═════╝  ╚═════╝    ╚═╝   ", 'cyan'))
print(colored("     Created By DrK0 ScripT's 2023 ~ Https://drk.tyronsur.es", 'cyan'))
time.sleep(2)                                                   
print("")

# Preguntas
usernames = input("Ingrese los nombres de usuario de Instagram a seguir (separados por espacios): ")
repeats = int(input("Ingrese el numero de repeticiones antes de finalizar el script"))
times = int(input("Ingrese los segundos para comenzar una nueva cuenta"))


# Convertir la respuesta del usuario en una lista
usernames_list = usernames.split()

# Arrancando el Script
print("> Importando Bibliotecas...")


# Importar la biblioteca de proxy o VPN
time.sleep(2)                                                   
print("")
print("> Importando Proxys...")

# Obtener la ruta de la carpeta de proxies
proxies_folder = "proxies"

# Obtener todos los archivos .txt en la carpeta de proxies
proxy_files = [f for f in os.listdir(proxies_folder) if f.endswith(".txt")]

# Imprimir la lista de archivos .txt en la carpeta de proxies
for i, proxy_file in enumerate(proxy_files):
    print(f"{i+1}. {proxy_file}")

# Pedir al usuario que seleccione los archivos de proxy a utilizar
selected_files = input("Ingrese los números de los archivos de proxy a utilizar (separados por espacios): ")

# Convertir la respuesta del usuario en una lista
selected_files_list = selected_files.split()

# Convertir la respuesta del usuario en el nombre del archivo
selected_files_list = [proxy_files[int(i)-1] for i in selected_files_list]

# Abrir los archivos de proxy seleccionados y agregar los proxies a una lista
proxies_list = []
for proxy_file in selected_files_list:
    with open(os.path.join(proxies_folder, proxy_file)) as f:
        proxies_list.extend(f.readlines())

# Iterar sobre la lista de proxies
for proxy in proxies_list:
    # Eliminar el carácter de nueva línea al final de cada proxy
    proxy = proxy.strip()
    # Asignar el proxy a la variable 'proxies'
    proxies = {
        'http': 'http://' + proxy,
        'https': 'https://' + proxy
    }

while True:
    # Generar un nombre de usuario y contraseña al azar
    username = ''.join(random.choices(string.ascii_letters + string.digits, k=11))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=11))
    email = ''.join(random.choices(string.ascii_letters + string.digits, k=11)) + '@gmail.com'

    session = InstaPy()
    # Crear una nueva cuenta de Instagram
    session.set_up(username=username, password=password, email=email)
    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")
    print("(" + current_time + ") [Usuario: "+username+" - Correo: "+email+" - Contrasena: "+password+"] -> Se ha Registrado el BOT.")
    # Iniciar sesión en la nueva cuenta
    session.login()
    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")
    print("(" + current_time + ") ["+username+"] -> Se ha autenticado el BOT.")
    
    # Seguir a un usuario específico
    session.follow_users(username_list)
    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")
    print("(" + current_time + ") ["+username+"] -> Follow Reconocido.")
    
    # Dar Me gusta a todas las publicaciones del usuario específico
    session.like_by_users(username_list, amount=10)
    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")
    print("(" + current_time + ") ["+username+"] -> Likes Completados.")

    # Guardar todas las publicaciones del usuario específico
    session.save_user_photos(username_list, amount=10)
    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")
    print("(" + current_time + ") ["+username+"] -> Publicaciones Guardadas.")

    # Compartir la ultima publicacion del usuario específico
    session.share_user_posts(username_list, amount=1)
    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")
    print("(" + current_time + ") ["+username+"] -> Story Share Completado.")
    # Finalizar la sesión
    session.end()
    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")
    print("(" + current_time + ") ["+username+"] -> Sesion Finalizada, agregando linea al log de cuentas de BOT.")
    
    
    # Cambiar la dirección IP utilizando el servicio de proxy o VPN
    session.set_use_proxy(True, proxies)
    
    # Esperar los minutos ajustados antes de volver a crear una nueva cuenta
    time.sleep(times)
