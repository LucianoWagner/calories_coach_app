# AI Nutrition Coach

El **AI Nutrition Coach** es una aplicación web interactiva que permite a los usuarios tomar decisiones dietéticas informadas mediante el uso de inteligencia artificial. La aplicación analiza imágenes de alimentos subidas por el usuario para identificar los ingredientes, estimar las calorías y ofrecer un desglose nutricional completo y sugerencias personalizadas de salud.

Esta versión está optimizada para ejecutarse localmente utilizando la API de **Groq Cloud** con el modelo **Llama 4 Scout (multimodal)**, ofreciendo una inferencia extremadamente rápida.

---

## Características Clave

### 1. Identificación de Alimentos y Estimación de Calorías
Permite subir imágenes de comidas. La IA identifica los platos y estima de forma rápida el contenido calórico de cada alimento, eliminando la necesidad de registros manuales tediosos.

### 2. Desglose Nutricional
Proporciona un desglose detallado de macronutrientes:
*   **Proteínas**
*   **Carbohidratos**
*   **Grasas**
*   **Vitaminas y Minerales**

### 3. Consejos Nutricionales Personalizados
Ofrece recomendaciones y sugerencias dietéticas basadas en la composición de la comida analizada para ayudar a los usuarios a cumplir sus objetivos de salud.

---

## Guía Rápida de Instalación y Ejecución

Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno local.

### Prerrequisitos
*   Tener instalado [Python 3.8+](https://www.python.org/downloads/).
*   Una API Key de Groq Cloud. Puedes obtenerla gratis en [Groq Console](https://console.groq.com/keys).

---

### Paso 1: Clonar o Descargar el Proyecto
Si estás descargando el proyecto para subirlo a tu propio repositorio de GitHub, puedes inicializar tu repositorio local con:
```bash
git init
```

---

### Paso 2: Crear el Entorno Virtual (venv)
Abre tu terminal en la carpeta raíz del proyecto y ejecuta el comando según tu sistema operativo:

*   **En Windows (Command Prompt o PowerShell):**
    ```bash
    python -m venv venv
    ```
*   **En macOS / Linux:**
    ```bash
    python3 -m venv venv
    ```

---

### Paso 3: Activar el Entorno Virtual
Activa el entorno virtual creado antes de instalar las dependencias:

*   **En Windows (PowerShell):**
    ```powershell
    .\venv\Scripts\Activate.ps1
    ```
*   **En Windows (Símbolo del Sistema / CMD):**
    ```cmd
    .\venv\Scripts\activate.bat
    ```
*   **En macOS / Linux:**
    ```bash
    source venv/bin/activate
    ```

Una vez activado, verás `(venv)` al inicio de la línea de comandos en tu terminal.

---

### Paso 4: Instalar las Dependencias
Con el entorno virtual activado, ejecuta el siguiente comando para instalar todas las librerías necesarias:
```bash
pip install -r requirements.txt
```

Esto instalará automáticamente:
*   `Flask` (Servidor web local)
*   `groq` (SDK oficial para interactuar con Groq Cloud)
*   `python-dotenv` (Para cargar las variables de configuración del archivo `.env`)
*   `Pillow` (Librería de procesamiento de imágenes)
*   `requests` (Para llamadas HTTP auxiliares)

---

### Paso 5: Configurar las Variables de Entorno
1. Localiza el archivo `.env` en la raíz del proyecto.
2. Abre el archivo y reemplaza el valor de `GROQ_API_KEY` por tu clave de API de Groq:
   ```env
   GROQ_API_KEY=gsk_tu_clave_de_groq_aqui
   ```
3. (Opcional) Puedes cambiar el modelo en `GROQ_MODEL` si prefieres utilizar otra versión compatible de Groq (por defecto usa `meta-llama/llama-4-scout-17b-16e-instruct`).

*Nota: El archivo `.env` está configurado en `.gitignore` para que tus claves privadas nunca se suban a GitHub.*

---

### Paso 6: Ejecutar la Aplicación
Inicia el servidor local ejecutando:
```bash
python app.py
```

La consola te indicará que el servidor se está ejecutando. Abre tu navegador web e ingresa a:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

¡Listo! Sube una imagen de tu comida y haz una pregunta para recibir asesoramiento nutricional instantáneo.