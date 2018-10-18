import sys
import json
 
from keras.applications.resnet50 import preprocess_input
from keras.models import load_model
from keras.preprocessing import image
import numpy as np

# 1) Two trained models
# keras model
model = load_model('models/model_resnet_rebalanced_best.hdf5')
isLesionModel = load_model('models/model_islesion.hdf5')

# 2) Labels CNN outputs 
LABEL_STRS = ["AKIEC", "BCC", "BKL", "DF", "MEL", "NV", "VASC"]
LABEL_FULL = ["Actinic Keratosis", "Basal Cell Carcinoma",  "Benign Keratosos", "Dermatofibroma", "Melanoma", "Nevus", "Vascular Lesion"]
ISMALIGNANT = [True, True, False, False, True, False, False]

# 3) Await ids input from CNN server
for line in sys.stdin:

    # 3.1) Extract id from JSON string from server and load image with id
    id = json.loads(line)['id']
    PATH = "tmp/" + id
    img = np.array([preprocess_input(image.img_to_array(image.load_img(PATH)))])
    
    # 3.2) Run the image through the premilnary CNN to check if image contains lesion.
    pred = isLesionModel.predict([img])
    score = round(max(pred[0]) * 100.0,2) #score
    idx = pred.argmax(axis=-1)[0] #label index 

    # 3.3) if image is good, run the diagnosis CNN, else report back with badImage label
    if idx == 0:
        result = {'badImage': True, 'id': id}
        print(json.dumps(result))
    else:
        pred = model.predict([img])
        score = round(max(pred[0]) * 100.0,2) #score
        idx = pred.argmax(axis=-1)[0] #label index 
        result = {'score': score, 'isMalignant': ISMALIGNANT[idx], 'label': LABEL_FULL[idx], 'id': id}
        print(json.dumps(result))

