import mysql.connector
import random
import schedule
import time
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    Updater,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext,
)

# Configuración de la base de datos MySQL
db = mysql.connector.connect(
    host="localhost",
    user="tu_usuario",
    password="tu_contraseña",
    database="tu_base_de_datos",
)

# Token de tu bot de Telegram
bot_token = "TU_TOKEN_DE_BOT"

# Lista de IDs de administradores
admin_ids = [123456789, 987654321]  # Reemplaza con los IDs de tus administradores

# Lista de IDs de grupos o canales donde se publicarán los anuncios
canal_ids = [-100123456789, -100987654321]  # Reemplaza con los IDs de tus canales o grupos

# Crea un objeto de bot de Telegram
bot = Bot(token=bot_token)

# Constantes para el manejo de la conversación
WAITING_FOR_TEXT = 1
WAITING_FOR_CONFIRMATION = 2

# Función para manejar el comando /start
def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # Verifica si el usuario ya tiene un anuncio registrado
    tiene_anuncio, mensaje = tiene_anuncio_guardado(user_id)

    if tiene_anuncio:
        opciones = [
            [InlineKeyboardButton("Editar Anuncio", callback_data="editar_anuncio")],
            [InlineKeyboardButton("Eliminar Anuncio", callback_data="eliminar_anuncio")],
            [InlineKeyboardButton("Publicar Anuncio", callback_data="publicar_anuncio")],
        ]

        reply_markup = InlineKeyboardMarkup(opciones)
        update.message.reply_text(f"¡Bienvenido de nuevo! Tu anuncio actual:\n{mensaje}\n\n¿Qué deseas hacer?",
                                  reply_markup=reply_markup)
    else:
        update.message.reply_text("¡Bienvenido! Parece que no tienes un anuncio registrado. "
                                  "Por favor, envía tu anuncio o mensaje para registrarlo.")

        return WAITING_FOR_TEXT

# Función para manejar mensajes de texto
def handle_text(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    mensaje = update.message.text

    # Guarda el mensaje del usuario en la base de datos sin cambios
    guardar_actualizar_anuncio(user_id, mensaje)

    opciones = [
        [InlineKeyboardButton("Editar Anuncio", callback_data="editar_anuncio")],
        [InlineKeyboardButton("Eliminar Anuncio", callback_data="eliminar_anuncio")],
        [InlineKeyboardButton("Publicar Anuncio", callback_data="publicar_anuncio")],
    ]

    reply_markup = InlineKeyboardMarkup(opciones)
    update.message.reply_text("Tu anuncio ha sido registrado. ¿Qué deseas hacer a continuación?", reply_markup=reply_markup)

    return WAITING_FOR_TEXT

# Función para manejar archivos adjuntos (fotos o videos)
def handle_media(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    media = update.message.photo[-1] if update.message.photo else update.message.video
    archivo_id = media.file_id if media else None

    if not archivo_id:
        update.message.reply_text("Por favor, envía una foto o video válido como anuncio.")
        return

    # Guarda o actualiza el mensaje del usuario y el archivo adjunto en la base de datos
    guardar_actualizar_anuncio(user_id, None, archivo_id)

    opciones = [
        [InlineKeyboardButton("Editar Anuncio", callback_data="editar_anuncio")],
        [InlineKeyboardButton("Eliminar Anuncio", callback_data="eliminar_anuncio")],
        [InlineKeyboardButton("Publicar Anuncio", callback_data="publicar_anuncio")],
    ]

    reply_markup = InlineKeyboardMarkup(opciones)
    update.message.reply_text("Tu anuncio ha sido registrado. ¿Qué deseas hacer a continuación?", reply_markup=reply_markup)

    return WAITING_FOR_TEXT

# Función para verificar si un usuario ya tiene un anuncio registrado y obtener el mensaje
def tiene_anuncio_guardado(user_id):
    cursor = db.cursor()
    cursor.execute("SELECT mensaje FROM anuncios WHERE user_id = %s", (user_id,))
    resultado = cursor.fetchone()
    cursor.close()
    return (resultado is not None, resultado[0]) if resultado else (False, None)

# Función para obtener el mensaje exacto del anuncio pendiente de un usuario
def obtener_anuncio_pendiente(user_id):
    cursor = db.cursor()
    cursor.execute("SELECT mensaje FROM anuncios WHERE user_id = %s", (user_id,))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado[0] if resultado else None

# Función para guardar o actualizar un anuncio en la base de datos
def guardar_actualizar_anuncio(user_id, mensaje, archivo_id=None):
    cursor = db.cursor()
    cursor.execute("INSERT INTO anuncios (user_id, mensaje, archivo_id) VALUES (%s, %s, %s) "
                   "ON DUPLICATE KEY UPDATE mensaje = VALUES(mensaje), archivo_id = VALUES(archivo_id)",
                   (user_id, mensaje, archivo_id))
    db.commit()
    cursor.close()

# Función para eliminar un anuncio de un usuario
def eliminar_anuncio(user_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM anuncios WHERE user_id = %s", (user_id,))
    db.commit()
    cursor.close()

# Función para confirmar la publicación de un anuncio
def confirmar_publicar_anuncio(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == "confirmar_publicar_anuncio":
        # Obtener el mensaje exacto del anuncio pendiente del usuario
        mensaje_pendiente = obtener_anuncio_pendiente(user_id)

        if mensaje_pendiente:
            # Publica el anuncio pendiente en los canales
            for canal_id in canal_ids:
                bot.send_message(chat_id=canal_id, text=mensaje_pendiente)

            query.answer("Anuncio publicado con éxito en los canales.")
        else:
            query.answer("No se encontró un anuncio pendiente para publicar.")
    else:
        query.answer("Publicación de anuncio cancelada.")

    return ConversationHandler.END

# Función para editar un anuncio registrado por el usuario
def editar_anuncio(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user.id
    mensaje_actual = obtener_anuncio_pendiente(user_id)

    if mensaje_actual:
        context.user_data["mensaje_actual"] = mensaje_actual
        update.callback_query.answer("Por favor, envía el nuevo contenido de tu anuncio para editarlo o /cancelar para cancelar.")
        return WAITING_FOR_TEXT
    else:
        update.callback_query.answer("No se encontró un anuncio para editar.")
        return ConversationHandler.END

# Función para manejar la edición de anuncios
def editar_anuncio_texto(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    nuevo_mensaje = update.message.text

    if "mensaje_actual" in context.user_data:
        mensaje_actual = context.user_data["mensaje_actual"]
        if nuevo_mensaje != "/cancelar":
            guardar_actualizar_anuncio(user_id, nuevo_mensaje)
            update.message.reply_text("Tu anuncio ha sido actualizado con éxito.")
        else:
            update.message.reply_text("Edición de anuncio cancelada.")

        del context.user_data["mensaje_actual"]
    else:
        update.message.reply_text("No se encontró un anuncio para editar.")

    return ConversationHandler.END

# Función para eliminar un anuncio registrado por el usuario
def eliminar_anuncio_usuario(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user.id
    eliminar_anuncio(user_id)
    update.callback_query.answer("Anuncio eliminado con éxito.")
    return ConversationHandler.END

# Función para revisar y aprobar anuncios pendientes por los administradores
def revisar_anuncios_pendientes(update: Update, context: CallbackContext):
    if update.message.from_user.id in admin_ids:
        anuncios_pendientes = obtener_anuncios_pendientes()
        if anuncios_pendientes:
            for user_id, mensaje in anuncios_pendientes:
                keyboard = [
                    [InlineKeyboardButton("Aprobar", callback_data=f"aprobar_anuncio_{user_id}"),
                     InlineKeyboardButton("Rechazar", callback_data=f"rechazar_anuncio_{user_id}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(f"Usuario {user_id}:\n{mensaje}", reply_markup=reply_markup)
        else:
            update.message.reply_text("No hay anuncios pendientes por revisar.")
    else:
        update.message.reply_text("No tienes permiso para revisar anuncios pendientes.")

# Función para obtener anuncios pendientes por los administradores
def obtener_anuncios_pendientes():
    cursor = db.cursor()
    cursor.execute("SELECT user_id, mensaje FROM anuncios WHERE aprobado = 0")
    resultados = cursor.fetchall()
    cursor.close()
    return resultados

# Función para aprobar un anuncio pendiente por los administradores
def aprobar_anuncio(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = int(query.data.split("_")[2])

    # Marcar el anuncio como aprobado en la base de datos
    cursor = db.cursor()
    cursor.execute("UPDATE anuncios SET aprobado = 1 WHERE user_id = %s", (user_id,))
    db.commit()
    cursor.close()

    query.answer(f"Anuncio de usuario {user_id} aprobado con éxito.")

# Función para rechazar un anuncio pendiente por los administradores
def rechazar_anuncio(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = int(query.data.split("_")[2])

    # Eliminar el anuncio rechazado de la base de datos
    eliminar_anuncio(user_id)

    query.answer(f"Anuncio de usuario {user_id} rechazado y eliminado con éxito.")

# Función para programar la publicación automática de anuncios
def programar_publicacion_anuncios():
    schedule.every(1).minutes.do(publicar_anuncio_programado)

# Función para publicar un anuncio programado
def publicar_anuncio_programado():
    # Obtener un anuncio aleatorio y enviarlo a un canal
    mensaje = obtener_anuncio_aleatorio()
    canal_id = random.choice(canal_ids)
    bot.send_message(chat_id=canal_id, text=mensaje)

def main():
    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # Configura el manejador de conversación para /start
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_FOR_TEXT: [MessageHandler(Filters.text & ~Filters.command, handle_text)],
            WAITING_FOR_CONFIRMATION: [CallbackQueryHandler(confirmar_publicar_anuncio, pattern='^confirmar_publicar_anuncio$')],
        },
        fallbacks=[],
    )

    dispatcher.add_handler(conv_handler)

    # Agrega un manejador de archivos adjuntos (fotos o videos)
    dispatcher.add_handler(MessageHandler(Filters.photo | Filters.video, handle_media))

    # Agrega comandos para editar y eliminar anuncios
    dispatcher.add_handler(CallbackQueryHandler(editar_anuncio, pattern='^editar_anuncio$'))
    dispatcher.add_handler(CallbackQueryHandler(eliminar_anuncio_usuario, pattern='^eliminar_anuncio$'))

    # Agrega comandos para revisar y aprobar anuncios pendientes por administradores
    dispatcher.add_handler(CommandHandler('revisar', revisar_anuncios_pendientes))
    dispatcher.add_handler(CallbackQueryHandler(aprobar_anuncio, pattern='^aprobar_anuncio'))
    dispatcher.add_handler(CallbackQueryHandler(rechazar_anuncio, pattern='^rechazar_anuncio'))

    # Inicia la programación para publicar anuncios automáticamente
    programar_publicacion_anuncios()

    # Manejo de errores
    def error(update, context):
        print(f"Error: {context.error}")

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
