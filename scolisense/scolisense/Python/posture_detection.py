import serial
import numpy as np
import tensorflow as tf
from time import sleep
import re
from twilio.rest import Client

# === Twilio Config ===
account_sid = 'AC6ca714bdfceab592b802db709b8c397f'
auth_token = '49d41639c3fb2dfb7fef1409d31afb2f'
twilio_whatsapp_number = 'whatsapp:+14155238886'  # Numéro sandbox Twilio
parent_number = 'whatsapp:+212706450547'  # Numéro du parent
client = Client(account_sid, auth_token)

# === Charger le modèle Keras (.h5) ===
model = tf.keras.models.load_model("C:\\Users\\PC\\Downloads\\scolisense\\posture_model.h5")

# === Initialiser la communication série ===
ser = serial.Serial('COM15', 38400)
sleep(2)

# === Lire les données série ===
def read_serial_data():
    while True:
        line = ser.readline().decode('utf-8').strip()
        if 'Initializing MPU' in line or not line:
            continue
        try:
            numbers = re.findall(r'-?\d+', line)
            if len(numbers) >= 6:
                data = np.array([float(val) for val in numbers[:6]])
                print(f"Valeurs lues du capteur : {data}")
                return data
            else:
                print("Erreur : Pas assez de valeurs numériques.")
        except ValueError:
            print("Erreur : Impossible de convertir les données.")
            continue

# === Prédiction de la posture ===
def predict_posture(sensor_data):
    sensor_data = sensor_data.reshape(1, -1)
    prediction = model.predict(sensor_data, verbose=0)[0]  # verbose=0 supprime l'affichage
    posture_type = np.argmax(prediction)
    confidence = prediction[posture_type]
    types = ["Corset non porté", "Mauvaise posture", "Bonne posture"]
    print(f"\nType prédit : {types[posture_type]} (confiance : {confidence:.2f})")
    return types[posture_type]

# === Boucle principale ===
while True:
    try:
        data = read_serial_data()
        result = predict_posture(data)

        if result == "Corset non porté":
            print("Envoi du message WhatsApp aux parents...")
            message = client.messages.create(
                body="Le corset a été retiré par votre enfant.",
                from_=twilio_whatsapp_number,
                to=parent_number
            )
            print("Message WhatsApp envoyé :", message.sid)
            sleep(30)  # Attente de 30 secondes
        else:
            sleep(2)  # Vérifier plus souvent si posture correcte/mauvaise

    except KeyboardInterrupt:
        print("Arrêt du programme.")
        break
