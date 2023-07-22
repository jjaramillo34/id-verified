import streamlit as st
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import idanalyzer
from io import BytesIO, StringIO
import time

fake_names = [
    ("Luis Martínez", "Gerente de Ventas"),
    ("María Rodríguez", "Especialista en Marketing"),
    ("Javier García", "Analista de Datos"),
    ("Carolina López", "Coordinadora de Recursos Humanos"),
    ("Ricardo Hernández", "Desarrollador de Software"),
    ("Isabel Pérez", "Diseñadora Gráfica"),
    ("Diego González", "Ingeniero de Proyectos"),
    ("Valentina Ramírez", "Asistente Administrativo"),
    ("Andrés Morales", "Consultor Financiero"),
    ("Camila Silva", "Ejecutiva de Ventas")
]

st.title("ID Analyzer")

img_file_buffer = st.camera_input("Take a picture")

CORE_API = st.secrets["CORE_API"]

opciones = ["Cedula", "Pasaporte", "Licencia de Conducir"]
st.sidebar.title("Opciones")
st.sidebar.subheader("Tipo de Documento")
st.sidebar.selectbox("Tipo de Documento", opciones)


if img_file_buffer is not None:
    st.warning("Image uploaded")
    # Convert the file to an opencv image.
    img = Image.open(img_file_buffer)

    # Now do something with the image! For example, let's display it:
    converted = np.array(img.convert('RGB'))

    st.image(converted, caption="Uploaded Image.", use_column_width=True)

    # save converted image to a file
    cv2.imwrite("id_front_test.jpeg", converted)
    # wait couple seconds for file to be saved
    time.sleep(5)

    try:
        coreapi = idanalyzer.CoreAPI(CORE_API, "US")
        # Initialize Core API with your api key and region (US/EU)
        # Raise exceptions for API level errors
        coreapi.throw_api_exception(True)
        # enable document authentication using quick module
        coreapi.enable_authentication(True, 'quick')
        # enable check for document age (18-120)
        coreapi.verify_age("18-120")  # check if person is above 18
        # enable vault cloud storage to store document information and image
        coreapi.enable_vault(True, False, False, False)
        # perform scan
        response = coreapi.scan(document_primary="id_front_test.jpeg")
        # dual-side scan
        # response = coreapi.scan(document_primary="id_front.jpeg")
        # video biometric verification
        # response = coreapi.scan(document_primary="id_front.jpg", biometric_video="face_video.mp4", biometric_video_passcode="1234")
        # All the information about this ID will be returned in response dictionary
        print(response)
        # Print document holder name
        cols = st.columns(2)
        if response.get('result'):
            data_result = response['result']
            with st.form(key='my_form'):
                cedula = cols[0].text_input(
                    "Cedula", data_result['documentNumber'])
                nombre = cols[0].text_input("Nombre", data_result['firstName'])
                apellido = cols[1].text_input(
                    "Apellido", data_result['lastName'])
                perfil = cols[1].selectbox(
                    "Perfil", [x[1] for x in fake_names])
                tiempo = cols[1].text_input("Tiempo", "1 año")

                submit_button = st.form_submit_button(label='Submit')
                if submit_button:
                    st.success("Submitted")
                    st.balloons()
                    st.stop()

        # Parse document authentication results
        # if response.get('authentication'):
            # authentication_result = response['authentication']
            # if authentication_result['score'] > 0.5:
            # print("The document uploaded is authentic")
            # elif authentication_result['score'] > 0.3:
            # print("The document uploaded looks little bit suspicious")
            # else:
            # print("The document uploaded is fake")
        # Parse biometric verification results
        # if response.get('face'):
            # face_result = response['face']
            # if face_result['isIdentical']:
            # print("Face verification PASSED!")
            # else:
            # print("Face verification FAILED!")
            # print("Confidence Score: "+face_result['confidence'])
        # check if age verification passed
        # if response.get('age'):
            # age_result = response['age']
            # if age_result['isMatch']:
            # print("Age verification PASSED!")
            # else:
            # print("Age verification FAILED!")
    except idanalyzer.APIError as e:
        # If API returns an error, catch it
        details = e.args[0]
        print("API error code: {}, message: {}".format(
            details["code"], details["message"]))
    except Exception as e:
        print("Error: {}".format(e))


else:
    st.success("Image not uploaded")
