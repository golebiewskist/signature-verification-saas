import torch
import torch.nn as nn
from torchvision import models, transforms
import numpy as np


class CNNModel:
    def __init__(self, model_architecture=None, model_weight_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Inicjalizacja modelu AI na urządzeniu: {self.device}")

        # Ładujemy nowoczesny model ResNet18 wytrenowany na ImageNet
        # To świetny ogólny ekstraktor cech, który działa dobrze dla podpisów w MVP
        weights = models.ResNet18_Weights.IMAGENET1K_V1
        self.model = models.resnet18(weights=weights)

        self.model = nn.Sequential(*list(self.model.children())[:-1])

        self.model.to(self.device)
        self.model.eval()

        self.preprocess = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])

    def get_feature_vector(self, image_np):
        """
        Argument:
            image_np: Obraz jako tablica NumPy (grayscale lub RGB)
        Zwraca:
            numpy array: Wektor cech (embedding)
        """
        # 1. Konwersja obrazu do formatu zgodnego z ResNet (RGB)
        # Jeśli obraz jest w skali szarości (2D), konwertujemy na RGB (3D)
        if len(image_np.shape) == 2:
            image_np = np.stack((image_np,) * 3, axis=-1)

        # 2. Preprocessing (Resize, Normalize, ToTensor)
        input_tensor = self.preprocess(image_np)

        # 3. Dodanie wymiaru batcha (1, 3, 224, 224)
        input_batch = input_tensor.unsqueeze(0).to(self.device)

        # 4. Ekstrakcja cech
        with torch.no_grad():
            output = self.model(input_batch)

        # 5. Spłaszczenie wyniku do wektora (512 elementów)
        feature_vector = output.squeeze().cpu().numpy()

        return feature_vector