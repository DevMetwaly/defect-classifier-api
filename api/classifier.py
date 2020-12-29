# *************** PYTHON FUNCTIONS *******************

# import libraries
from fastai.vision import *
import json

def classifier(image_path):
    learn = load_learner('model')
    img = open_image(image_path)
    prediction = learn.predict(img)
    print("hereeeree: " ,prediction[0])
    return(str(prediction[0]))
    # return prediction

def predict(image_path):
    prediction = classifier(image_path)
    print(prediction)
    print(type(prediction))
    res = {
        "Category" : prediction
    }
    print("in predict function = ", res)
    return res