# SignatureApp: System Bezpiecznego Podpisu Elektronicznego z Weryfikacją Biometryczną AI

> **Projekt Inżynierski (Praca Dyplomowa)**  
> **Autor:** Stanisław Gołębiewski  
> **Uczelnia:** Wojskowa Akademia Techniczna (WAT), Wydział Cybernetyki  
> **Kierunek:** Informatyka  

---

## 📌 O Projekcie

**SignatureApp** to nowoczesny, wielodostępny system informatyczny (SaaS) służący do bezpiecznego składania i weryfikacji podpisów elektronicznych na dokumentach. Rozwiązanie integruje zaawansowaną kryptografię asymetryczną z weryfikacją tożsamości opartą na sztucznej inteligencji (sieci konwolucyjne CNN w trybie *One-Shot Learning*).

System został zaprojektowany w oparciu o paradygmat **Privacy by Design** oraz wytyczne unijnego rozporządzenia **eIDAS**.

---

## 🚀 Kluczowe Cechy i Architektura

### 1. 🤖 Biometryczna Weryfikacja Podpisu (Deep Learning)
- Zastosowanie głębokiej konwolucyjnej sieci neuronowej (**SigNet / SigVer**) do analizy odręcznego podpisu graficznego.
- **One-Shot Learning**: Model ekstrakcji wektorów cech (embeddings) pozwala na skuteczne porównanie próbki podpisu z zarejestrowanym wzorcem użytkownika bez konieczności ponownego trenowania sieci.
- Preprocessing obrazu: normalizacja wymiarów, centrowanie masy, inwersja barwna i wygładzanie szumów.
- Pozytywna weryfikacja biometryczna warunkuje odblokowanie dostępu do klucza prywatnego użytkownika.

### 2. 🏢 Architektura Wielodostępności (Multi-Tenancy SaaS)
- Pełna separacja danych poszczególnych organizacji (Tenants) na poziomie **schematów bazy danych PostgreSQL** (`django-tenants`).
- Dedykowane domeny i subdomeny dla każdego najemcy (np. `organizacja1.localhost:8000`).
- Współdzielona baza publiczna dla zarządzania najemcami oraz izolowane schematy dla wrażliwych danych operacyjnych i dokumentów.

### 3. 🔐 Kryptografia i Privacy by Design
- **Kryptografia asymetryczna RSA-PSS**: Wykorzystanie schematu podpisu z dopełnieniem probabilistycznym (PSS) o wyższym poziomie bezpieczeństwa dowodowego niż klasyczne PKCS#1 v1.5.
- **Lokalne hashowanie dokumentów (SHA-256)**: Treść poufnych dokumentów **nie opuszcza przeglądarki użytkownika**. Na serwer przesyłany jest wyłącznie skrót kryptograficzny SHA-256 wyliczony po stronie klienta, co gwarantuje pełną poufność danych.

---

## 🛠️ Stos Technologiczny

| Warstwa | Technologie |
| :--- | :--- |
| **Backend & API** | Python 3, Django, Django REST Framework, `django-tenants` |
| **Sztuczna Inteligencja** | PyTorch, Torchvision, OpenCV (`cv2`), NumPy, SciPy |
| **Frontend** | Vue 3 (Vite), JavaScript, HTML5 Canvas API (rejestracja trajektorii podpisu) |
| **Baza Danych** | PostgreSQL (izolacja schematowa multi-tenant) |
| **Konteneryzacja** | Docker, Docker Compose |

---

## 🏗️ Diagram Przepływu Podpisu

```text
[ Użytkownik ]
      |
      | 1. Rysuje podpis na Canvasie & wybiera plik PDF
      v
[ Frontend (Vue 3 SPA) ]
      |
      |--- 2. Wylicza SHA-256 pliku lokalnie (plik NIE leci na serwer)
      |--- 3. Wysyła próbkę podpisu (raster) + SHA-256
      v
[ Backend (Django API) ]
      |
      v
[ Moduł AI (SigNet CNN) ]
      |--- 4. Ekstrakcja cech & porównanie z wektorem wzorcowym
      v
  Biometria zgodna?
    /         \
  (NIE)       (TAK)
    |           |
    v           v
  Odrzucenie   Odblokowanie klucza prywatnego & złożenie podpisu RSA-PSS
                |
                v
               Wygenerowanie certyfikatu / metadanych podpisu
```

---

## ⚡ Instrukcja Uruchomienia

### Wymagania wstępne
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose

### 1. Budowa i start kontenerów
```bash
docker-compose up -d --build
```

### 2. Migracje bazy i schematów
Zainicjalizuj współdzielony schemat publiczny oraz schematy najemców:
```bash
docker-compose exec web python manage.py migrate_schemas --shared
```

### 3. Utworzenie pierwszego Najemcy (Tenanta)
```bash
docker-compose exec web python manage.py create_tenant
```

### 4. Utworzenie konta administratora dla Tenanta
```bash
docker-compose exec web python manage.py create_tenant_superuser
```

### 5. Dostęp do panelu administracyjnego
Panel administracyjny Django dostępny jest pod adresem URL przypisanym do danego Tenanta:
`http://<twoj-tenant>.localhost:8000/admin`

---


---

## 📚 Źródła i Wykorzystane Modele AI (Attribution & Credits)

W module biometrycznej weryfikacji podpisu zaimplementowano podejście oparte na transferze wiedzy (*Transfer Learning*) oraz ekstrakcji wektorów cech (Feature Embeddings):
- **Implementacja SigNet i wagi pre-trained (SigVer):** W module `ai_module` wykorzystano architekturę sieci SigNet, wagi (`signet.pkl`) oraz algorytmy preprocessingu podpisu (normalizacja rozmiaru płótna `(952, 1360)`, centrowanie środka masy, binaryzacja Otsu) pochodzące bezpośrednio z otwartoźródłowego projektu badawczego **[SigVer (luizgh/sigver)](https://github.com/luizgh/sigver)**.
- **Publikacja naukowa:**  
  *Luiz G. Hafemann, Robert Sabourin, Luiz S. Oliveira* – ["Learning Features for Offline Handwritten Signature Verification using Deep Convolutional Neural Networks"](https://arxiv.org/abs/1705.05787) (Pattern Recognition, 2017).
- **Ekstrakcja cech wizualnych (PyTorch):** Wykorzystano model ResNet-18 (`torchvision.models.resnet18`) ze ściętą warstwą klasyfikującą jako bazowy ekstraktor cech dla wektorów embeddingu.

**Autorski wkład własny projektu:**
- Zaprojektowanie i budowa wielodostępnej architektury SaaS w oparciu o separację schematów bazy danych (`django-tenants`),
- Realizacja paradygmatu *Privacy by Design* (obliczanie skrótu SHA-256 w przeglądarce, uniemożliwiające wyciek treści dokumentu na serwer),
- Mechanizm bezpiecznego warunkowania podpisu kryptograficznego **RSA-PSS** na podstawie progu podobieństwa wektorów cech AI,
- Aplikacja frontendowa Vue 3 SPA z interaktywnym canvasem HTML5 do składania podpisu oraz pełna konteneryzacja środowiska w Dockerze.

## 📄 Publikacja & Prawa Autorskie
Projekt stanowi część pracy dyplomowej inżynierskiej obronionej na Wydziale Cybernetyki Wojskowej Akademii Technicznej w Warszawie.
