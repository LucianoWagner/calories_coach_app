import requests
import re
import base64
import os
from dotenv import load_dotenv
from groq import Groq
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, flash

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)
# Clave secreta: utiliza la variable de entorno, o genera una aleatoria y segura en memoria si no está definida
app.secret_key = os.getenv("FLASK_SECRET_KEY") or os.urandom(24).hex()

# Inicializar el cliente de Groq
groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

# Modelo por defecto para el procesamiento visual
model_id = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

# Cantidad máxima de tokens en la respuesta
max_tokens_val = int(os.getenv("GROQ_MAX_TOKENS", "1024"))

def input_image_setup(uploaded_file):
    """
    Encodes the uploaded image file into a base64 string to be used with AI models.

    Parameters:
    - uploaded_file: File-like object uploaded via a file uploader (Streamlit or other frameworks)

    Returns:
    - encoded_image (str): Base64 encoded string of the image data
    """
    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.read()

        # Encode the image to a base64 string
        encoded_image = base64.b64encode(bytes_data).decode("utf-8")

        return encoded_image
    else:
        raise FileNotFoundError("No file uploaded")

def format_response(response_text):
    """
    Formats the model response to display headings, bold text, lists, and paragraphs
    properly using HTML elements.
    """
    # 1. Clean extra whitespace
    response_text = response_text.strip()
    
    # 2. Convert markdown headers (### or ## or #) to HTML headings
    response_text = re.sub(r"(?m)^###\s*(.*)", r"<h3>\1</h3>", response_text)
    response_text = re.sub(r"(?m)^##\s*(.*)", r"<h3>\1</h3>", response_text)
    response_text = re.sub(r"(?m)^#\s*(.*)", r"<h2>\1</h2>", response_text)
    
    # 3. Convert markdown bold (**text**) to HTML <strong> (without wrapping in <p> to prevent line breaks)
    response_text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", response_text)
    
    # 4. Convert bullet points (* or -) and numbered lists (1., 2.) to HTML list items <li>
    response_text = re.sub(r"(?m)^\s*[-*]\s+(.*)", r"<li>\1</li>", response_text)
    response_text = re.sub(r"(?m)^\s*\d+\.\s+(.*)", r"<li>\1</li>", response_text)
    
    # 5. Group contiguous <li> items into <ul> lists
    response_text = re.sub(r"(<li>.*?</li>)+", lambda match: f"<ul>{match.group(0)}</ul>", response_text, flags=re.DOTALL)
    
    # 6. Process paragraphs for remaining non-HTML lines
    lines = response_text.split('\n')
    processed_lines = []
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        
        # If the line already contains block-level or list HTML tags, keep it as is
        if any(tag in line_str for tag in ['<ul>', '</ul>', '<li>', '</li>', '<h2', '</h2>', '<h3', '</h3>']):
            processed_lines.append(line_str)
        else:
            # Wrap plain text in paragraph tags
            processed_lines.append(f"<p>{line_str}</p>")
            
    return "\n".join(processed_lines)


def generate_model_response(encoded_image, user_query, assistant_prompt):
    """
    Sends an image and a query to the model and retrieves the description or answer.
    Formats the response using HTML elements for better presentation.
    """
    # Validar si se ha configurado la API Key de Groq antes de hacer la solicitud
    if not os.getenv("GROQ_API_KEY"):
        return (
            "<p style='color:#721c24; background-color:#f8d7da; padding:15px; border-radius:4px; border:1px solid #f5c6cb;'>"
            "<strong>Error de Configuración:</strong> No se ha detectado la variable <code>GROQ_API_KEY</code> en tu archivo <code>.env</code>. "
            "Por favor, obtén una clave en la consola de Groq y configúrala para poder analizar la imagen.</p>"
        )

    # Crear el objeto de mensajes para Groq con soporte multimodal
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": assistant_prompt + "\n\n" + user_query},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_image}"
                    }
                }
            ]
        }
    ]

    try:
        # Enviar la solicitud de chat completion a la API de Groq
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model_id,
            temperature=0.7,
            max_tokens=max_tokens_val
        )
        raw_response = chat_completion.choices[0].message.content

        # Darle formato HTML a la respuesta cruda del modelo
        formatted_response = format_response(raw_response)
        return formatted_response
    except Exception as e:
        print(f"Error in generating response: {e}")
        return f"<p style='color:#721c24; background-color:#f8d7da; padding:15px; border-radius:4px; border:1px solid #f5c6cb;'><strong>Error en la API de Groq:</strong> {str(e)}</p>"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Retrieve user inputs
        user_query = request.form.get("user_query")
        uploaded_file = request.files.get("file")

        if uploaded_file:
            # Process the uploaded image
            encoded_image = input_image_setup(uploaded_file)

            if not encoded_image:
                flash("Error processing the image. Please try again.", "danger")
                return redirect(url_for("index"))

            # Assistant prompt (can be customized)
            assistant_prompt = """
            You are an expert nutritionist. Your task is to analyze the food items displayed in the image and provide a detailed nutritional assessment using the following format:

        1. **Identification**: List each identified food item clearly, one per line.
        2. **Portion Size & Calorie Estimation**: For each identified food item, specify the portion size and provide an estimated number of calories. Use bullet points with the following structure:
        - **[Food Item]**: [Portion Size], [Number of Calories] calories

        Example:
        *   **Salmon**: 6 ounces, 210 calories
        *   **Asparagus**: 3 spears, 25 calories

        3. **Total Calories**: Provide the total number of calories for all food items.

        Example:
        Total Calories: [Number of Calories]

        4. **Nutrient Breakdown**: Include a breakdown of key nutrients such as **Protein**, **Carbohydrates**, **Fats**, **Vitamins**, and **Minerals**. Use bullet points, and for each nutrient provide details about the contribution of each food item.

        Example:
        *   **Protein**: Salmon (35g), Asparagus (3g), Tomatoes (1g) = [Total Protein]

        5. **Health Evaluation**: Evaluate the healthiness of the meal in one paragraph.

        6. **Disclaimer**: Include the following exact text as a disclaimer:

        The nutritional information and calorie estimates provided are approximate and are based on general food data. 
        Actual values may vary depending on factors such as portion size, specific ingredients, preparation methods, and individual variations. 
        For precise dietary advice or medical guidance, consult a qualified nutritionist or healthcare provider.

        Format your response exactly like the template above to ensure consistency.

        """

            # Generate the model's response
            response = generate_model_response(encoded_image, user_query, assistant_prompt)

            # Render the result
            return render_template("index.html", user_query=user_query, response=response)

        else:
            flash("Please upload an image file.", "danger")
            return redirect(url_for("index"))

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)