import streamlit as st
import streamlit.components.v1 as components

# Streamlit 앱의 제목 설정
# st.title("Streamlit with JavaScript Example")
# #
# # # 버튼을 클릭하면 JavaScript alert 메시지를 표시하는 Python 코드
# if st.button("Click me"):
#     html_string = """
#         <script>
#             alert("Hello from JavaScript!");
#         </script>
#     """
#
#     components.html(html_string)
#     st.markdown(html_string, unsafe_allow_html=True)

# https://stackoverflow.com/questions/67977391/can-i-display-custom-javascript-in-streamlit-web-app
# import streamlit as st
# import streamlit.components.v1 as components
#
# html_string = '''
# <h1>HTML string in RED</h1>
#
# <script language="javascript">
#   document.querySelector("h1").style.color = "red";
#   console.log("Streamlit runs JavaScript");
#   alert("Streamlit runs JavaScript");
# </script>
# '''
#
# components.html(html_string)  # JavaScript works
#
# st.markdown(html_string, unsafe_allow_html=True)  # JavaScript doesn't work


# import streamlit as st
# from streamlit.components.v1 import html
#
# # Define your javascript
# my_js = """
# alert("Hola mundo");
# """
#
# # Wrapt the javascript as html code
# my_html = f"<script>{my_js}</script>"
#
# # Execute your app
# st.title("Javascript example")
# html(my_html)

# import streamlit as st
# import time
# from datetime import datetime
#
# st.title('Dynamic Time Display')
#
# # Display the current time
# current_time = datetime.now().strftime("%H:%M:%S")
# st.write(f"Current Time: {current_time}")
#
# # Add a hint about the rerun
# st.write("This app will rerun in 5 seconds...")
#
# # Sleep for 5 seconds before rerunning
# time.sleep(5)
# st.rerun()

# https://github.com/thunderbug1/streamlit-javascript
import streamlit as st
from streamlit_javascript import st_javascript
from my_script import script as html_script

st.subheader("Javascript API call")

return_value = st_javascript("""await fetch("https://reqres.in/api/products/3").then(function(response) {
    return response.json();
}) """)

# return_value = st_javascript(html_script)
st.markdown(f"Return value was: {return_value}")
print(f"Return value was: {return_value}")