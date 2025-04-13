import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical

# === Charger les données avec un encodage spécifique ===
train_data = pd.read_csv("C:\\Users\\PC\\Downloads\\scolisense (3)\\scolisense\\scolisense\\Python\\posture_data_MPU.csv", encoding='ISO-8859-1')

# === Supprimer la colonne 'Timestamp' ===
train_data = train_data.drop(columns=['Timestamp'])

# === Séparer les features et les labels ===
X_train = train_data.select_dtypes(include=[np.number])  # On récupère toutes les colonnes numériques
y_train = train_data['Posture']  # Colonne cible qui contient 3 valeurs (textuelles)

# === Convertir les valeurs textuelles en valeurs numériques ===
# Remplacer les catégories textuelles par des valeurs numériques (par exemple, 'Bonne posture' -> 0, 'Corset non porté' -> 1, 'Mauvaise posture' -> 2)
y_train = y_train.replace({'Bonne posture': 0, 'Corset non porté': 1, 'Mauvaise posture': 2})

# ===  Convertir les données en types numériques ===
X_train = X_train.apply(pd.to_numeric, errors='coerce')  # Convertit les valeurs en numérique
y_train = pd.to_numeric(y_train, errors='coerce')          # Convertit les labels en numérique

# === Traiter les valeurs manquantes ===
X_train = X_train.fillna(X_train.mean())  # Remplacer les NaN par la moyenne de chaque colonne
y_train = y_train.fillna(y_train.mean())  # Remplacer les NaN dans y_train par la moyenne

# === Supprimer les NaN dans y_train ===
y_train = y_train.dropna()  # Supprimer les valeurs manquantes dans y_train

# === Encoder les labels en one-hot pour 3 classes ===
y_train = to_categorical(y_train, num_classes=4)  # Maintenant, on a 4 classes : Bonne posture, Corset non porté, Mauvaise posture

# === Créer et entraîner un modèle de réseau de neurones avec TensorFlow ===
model = Sequential()
# Définir la couche d'entrée en fonction du nombre de features
model.add(Input(shape=(X_train.shape[1],)))
# Ajouter une couche cachée avec 64 neurones et la fonction d'activation ReLU
model.add(Dense(64, activation='relu'))
# Ajouter une deuxième couche cachée avec 32 neurones et ReLU
model.add(Dense(32, activation='relu'))
# Couche de sortie avec 4 neurones (une pour chaque classe) et la fonction d'activation Softmax pour obtenir des probabilités
model.add(Dense(4, activation='softmax'))

# Compiler le modèle avec l'optimiseur Adam et la fonction de perte pour classification multi-classes
model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])

# Entraîner le modèle sur 40 epochs avec des batches de 32 exemples
model.fit(X_train, y_train, epochs=40, batch_size=32, verbose=1)

# === 10. Sauvegarder le modèle entraîné ===
model.save('posture_model.h5')

# === 11. Charger le modèle sauvegardé et prédire sur de nouvelles données ===
loaded_model = tf.keras.models.load_model('posture_model.h5')

# Données brutes (sans normalisation, à adapter selon tes prétraitements)
new_data = np.array([[0.19, -0.08, 1.1, -2.27, -1.34, -0.47]])

# Réaliser la prédiction
prediction = loaded_model.predict(new_data)
# Extraire la classe prédite : c'est l'indice du neurone avec la plus forte probabilité
predicted_class = np.argmax(prediction, axis=1)[0]
# Récupérer les probabilités pour chacune des classes
prediction_proba = prediction[0]

# Afficher les résultats
print("\nPrédiction sur de nouvelles données:")
print(f"Valeurs: {new_data[0]}")
print(f"Classe prédite: {predicted_class}")  # Affiche 0, 1, 2 ou 3
print(f"Probabilités: {prediction_proba}")

# === 12. Sauvegarder les résultats dans un fichier texte ===
with open('data.txt', 'w') as f:
    f.write(f"Valeurs: {new_data[0]}\n")
    f.write(f"Classe prédite: {predicted_class}\n")
    f.write(f"Probabilités: {prediction_proba}\n")
