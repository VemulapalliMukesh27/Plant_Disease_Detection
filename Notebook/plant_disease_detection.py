# -*- coding: utf-8 -*-
"""Plant_DIsease_Detection.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18LPECKxoAMxMXybkSoq_0d05CU-S2jYe
"""
!pip install tensorflow
#set  seeds  for reproductivity
import random
random.seed(0)
import numpy as np
np.random.seed(0)


import tensorflow as tf
tf.random.set_seed(0)

import os
import json
from zipfile import ZipFile
from PIL import Image
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers,models

!pip install kaggle

kaggle_credentials=json.load(open("kaggle.json"))
os.environ['KAGGLE_USERNAME']=kaggle_credentials['username']
os.environ['KAGGLE_KEY']=kaggle_credentials['key']


!kaggle datasets download -d abdallahalidev/plantvillage-dataset

!ls

from zipfile import ZipFile
with ZipFile("plantvillage-dataset.zip","r") as zip:
  zip.extractall()
  print("Done")

print(os.listdir("plantvillage dataset"))
print(len(os.listdir("plantvillage dataset/segmented")))
print(len(os.listdir("plantvillage dataset/grayscale")))
print(len(os.listdir("plantvillage dataset/color")))
print(os.listdir("plantvillage dataset/color"))
print(os.listdir("plantvillage dataset/grayscale"))
print(os.listdir("plantvillage dataset/segmented"))


print(len(os.listdir("plantvillage dataset/color/Apple___Apple_scab")))
print(len(os.listdir("plantvillage dataset/color/Apple___Black_rot")))
print(len(os.listdir("plantvillage dataset/color/Apple___Cedar_apple_rust")))
print(len(os.listdir("plantvillage dataset/color/Apple___healthy")))
print(len(os.listdir("plantvillage dataset/color/Blueberry___healthy")))
print(len(os.listdir("plantvillage dataset/color/Cherry_(including_sour)___Powdery_mildew")))
print(len(os.listdir("plantvillage dataset/color/Cherry_(including_sour)___healthy")))
print(len(os.listdir("plantvillage dataset/color/Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot")))
print(len(os.listdir("plantvillage dataset/color/Corn_(maize)___Northern_Leaf_Blight")))
print(len(os.listdir("plantvillage dataset/color/Corn_(maize)___healthy")))
print(len(os.listdir("plantvillage dataset/color/Potato___Early_blight")))
print(len(os.listdir("plantvillage dataset/color/Potato___healthy")))


dir="plantvillage dataset/color"

img='/content/plantvillage dataset/color/Apple___Black_rot/0090d05d-d797-4c99-abd4-3b9cb323a5fd___JR_FrgE.S 8727.JPG'
img=mpimg.imread(img)
print(img.shape)
plt.imshow(img)
plt.show()

img_size=224
batch_size=32
data_gen=ImageDataGenerator(rescale=1./255,
                            validation_split=0.2)

train_generator=data_gen.flow_from_directory(dir,
                                             target_size=(img_size,img_size),
                                             batch_size=batch_size,
                                             subset="training",
                                             class_mode='categorical')

valid_generator=data_gen.flow_from_directory(dir,
                                             target_size=(img_size,img_size),
                                             batch_size=batch_size,
                                             subset="validation",
                                             class_mode='categorical')

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam

# Define the model
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(img_size, img_size, 3)),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Conv2D(256, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Conv2D(512, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Flatten(),
    Dense(1024, activation='relu'),
    Dropout(0.5),
    Dense(512, activation='relu'),
    Dropout(0.5),
    Dense(train_generator.num_classes, activation='softmax')
])

# Compile the model
optimizer = Adam(lr=0.001)
model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
history = model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // batch_size,
    epochs=50,
    validation_data=valid_generator,
    validation_steps=valid_generator.samples // batch_size
)

# Evaluate the model
val_loss, val_accuracy = model.evaluate(valid_generator, steps=valid_generator.samples // batch_size)
print("Validation Accuracy:", val_accuracy * 100)
print("Validation Loss:", val_loss)


plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')
plt.show()


#load and process image using pilllow
def load_and_preprocess_image(image_path,target_size=(224,224)):
  img=Image.open(image_path)
  img=img.resize(target_size)
  img_array=np.array(img)
  image_batch=np.expand_dims(img_array,axis=0)
  img_array=image_batch.astype('float32')/255.0
  return img_array


def predict_image_class(model,image_path,class_indices):
  preprocessed_image=load_and_preprocess_image(image_path)
  prediction=model.predict(preprocessed_image)
  predicted_class_index=np.argmax(prediction)
  predicted_class_name=class_indices[predicted_class_index]
  return predicted_class_name

class_indices={V:k for k,V in train_generator.class_indices.items()}
class_indices

#saving class names as json file
json.dump(class_indices ,open("class_indices.json","w"))

img_path="/content/plantvillage dataset/color/Corn_(maize)___Northern_Leaf_Blight/005318c8-a5fa-4420-843b-23bdda7322c2___RS_NLB 3853 copy.jpg"
predicted_class=predict_image_class(model,img_path,class_indices)
print(predicted_class)

model.save('drive/MyDrive/Trained_Models/Plant_Disease_Detection.h5')