import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import streamlit as st

load_dotenv()
GOOGLE_API_KEY ="AIzaSyAiBv3N7PiYSQl9__F51N7cWwVldZYYW3k"

genai.configure(api_key=GOOGLE_API_KEY)


def get_gemini_response(input_text, image=None, prompt=""):
    """Generate recipe details using the Gemini Vision API."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        # If image data is provided, include it in the input
        if image:
            response = model.generate_content([image[0], prompt + input_text])
        else:
            response = model.generate_content([input_text + prompt])
        return response.text
    except Exception as e:
        st.error("An error occurred while generating the recipe. Please try again.")
        raise RuntimeError(f"Error generating recipe: {e}")


def input_image_setup(uploaded_file):
    """Prepare the image data for the Gemini API."""
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{"mime_type": uploaded_file.type, "data": bytes_data}]
        return image_parts
    else:
        return None


def reset_input():
    """Reset input text."""
    st.session_state["input"] = ""
    st.session_state["file_uploader_key"] += 1


if "input" not in st.session_state:
    st.session_state["input"] = ""
if "file_uploader_key" not in st.session_state:
    st.session_state["file_uploader_key"] = 0

# Streamlit app setup
st.set_page_config(page_title="Recipe Generator")

st.header("Recipe Generator")
st.subheader(
    "Upload an image of ingredients or a dish, or simply enter a prompt and the app will generate a recipe for you!"
)
input_text = st.text_input("Enter ingredients or dish description: ", key="input")

use_camera = st.checkbox("Use Camera")
uploaded_file = (
    st.camera_input("Take a photo of ingredients")
    if use_camera
    else st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_container_width=True)

input_prompt = """
You are a culinary expert and nutritionist. Based on the provided input, generate a complete recipe with these specific sections.
- **Recipe Title**
- **Ingredients with Quantities** - Assume ingredient quantities based on a typical serving size if they are not specified.
- **Step-by-Step Cooking Instructions** - Suggest a cooking method and make assumptions if any details are missing.
- **Nutritional Information** - Provide an approximate breakdown of calories, fats, carbohydrates, and proteins.
- **Health Analysis** - Assess if the dish is healthy, and suggest possible modifications for a healthier version.
- **Tips & Notes** - Suggest possible spices, sauces, or flavoring options, and provide any extra advice for enhancing the dish.

If any information (such as cuisine type, spices, or cooking method) is missing, use your best judgment to create a flavorful recipe based on common culinary practices.
"""

col1, col2 = st.columns(2)
generate_button = col1.button("Generate Recipe")
reset_button = col2.button("Reset", on_click=reset_input)

if generate_button:
    try:
        image_data = input_image_setup(uploaded_file)

        with st.spinner("Generating recipe..."):
            # If no image, use text input alone
            if image_data is None and not input_text.strip():
                st.error(
                    "Please provide an image or enter a description of ingredients."
                )
            else:
                response = get_gemini_response(input_text, image_data, input_prompt)
                st.subheader("The Recipe:")
                st.markdown(response)
    except FileNotFoundError:
        st.error("No file uploaded. Please upload an image.")
    except RuntimeError as e:
        st.error("Error: " + str(e))
    except Exception as e:
        st.error("An unexpected error occurred. Please try again later.")
