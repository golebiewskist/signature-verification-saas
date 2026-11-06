from ai_module.normalize import preprocess_signature
import ai_module.signet as signet
from ai_module.cnn_model import CNNModel

# Maximum signature size (required for the SigNet models):
canvas_size = (952, 1360)

# Load the model
model_weight_path = 'signet.pkl'
model = CNNModel(signet, model_weight_path)

def get_feature_vector(image):
    processed = preprocess_signature(image, canvas_size)
    return model.get_feature_vector(processed)