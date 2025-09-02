import streamlit as st
import extra_streamlit_components as stx
import yaml, mysql.connector, bcrypt, datetime, time

LABELS = {
    'Form name': {'English': 'Login', 'Korean': '로그인', 'Spanish': 'Inicio de sesión', 'Japanese': 'ログイン'},
    'Username': {'English': 'Username', 'Korean': '아이디', 'Spanish': 'Nombre de usuario', 'Japanese': 'ユーザー名'},
    'Password': {'English': 'Password', 'Korean': '비밀번호', 'Spanish': 'Contraseña', 'Japanese': 'パスワード'},
    'Login': {'English': 'Login', 'Korean': '로그인', 'Spanish': 'Iniciar sesión', 'Japanese': 'ログイン'},
    'Incorrect credential': {'English': 'The ID or password is incorrect.', 'Korean': '아이디 또는 비밀번호가 잘못되었습니다.', 'Spanish': 'El ID o la contraseña son incorrectos.', 'Japanese': 'IDまたはパスワードが間違っています.'},
}

def get_userinfo(username, password):
    try:
        connection = mysql.connector.connect(
            user=st.session_state.config['authentication']['user'],
            password=st.session_state.config['authentication']['password'],
            host=st.session_state.config['authentication']['host'],
            database=st.session_state.config['authentication']['database']
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"SELECT username, password, name FROM {st.session_state.config['authentication']['table']} WHERE username=%s", (username,))
            result = cursor.fetchone()
            if result:
                stored_password = result['password']
                if stored_password == "123":
                    if password == '123':
                        return True, result['username'], result['name']
                else:
                    if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                        return True, result['username'], result['name']
            return False, None, None
    except mysql.connector.Error as e:
        st.error(f"Error retrieving user data: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def setup_login_page():
    user_preference=st.session_state.language
    mapping = {'한국어': 'Korean', 'English': 'English', 'Español': 'Spanish', '日本語': 'Japanese'}
    
    languages = list(mapping.keys())
    reverse_mapping = {v: k for k, v in mapping.items()}
    preferred_language = reverse_mapping[user_preference]
    index = languages.index(preferred_language)
    selected_language = st.selectbox("NONE", languages, index=index, label_visibility="collapsed")

    language = mapping[selected_language]
    st.session_state.language = language

    with st.form(key='login_form'):
        username = st.text_input(LABELS['Username'][st.session_state.language])
        password = st.text_input(LABELS['Password'][st.session_state.language], type="password")
        submit_button = st.form_submit_button(LABELS['Login'][st.session_state.language])

    if submit_button:
        auth_result = get_userinfo(username, password)
        if auth_result[0] == True:
            st.session_state.username = auth_result[1]
            st.session_state.name = auth_result[2]
            st.rerun()
        else:
            st.error(LABELS['Incorrect credential'][st.session_state.language])

@st.dialog("Cookie Preferences")
def ask_cookie_consent():
    st.write("We use cookies to enhance your browsing experience. By clicking 'Accept All', you consent to our use of cookies.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Accept All", type="primary"):
            st.session_state.cookie_consent = "yes"
            st.session_state.cookie_action = "yes"
            st.rerun()
    with col2:
        if st.button("Reject All"):
            st.session_state.cookie_consent = "no"
            st.session_state.cookie_action = "yes"
            st.rerun()

def check_auto_login():
    cookie_manager = stx.CookieManager()
    # Streamlit will rerun the script until stx.CookieManager() creates the field _streamlit_xsrf.
    # Before creating the filed _streamlit_xsrf, the cookie information cannot be retrieved correctly.
    cookie_status = cookie_manager.get(cookie="_streamlit_xsrf")
    cookie_consent = cookie_manager.get(cookie="cookie_consent")
    cookie_action = cookie_manager.get(cookie="cookie_action")
    cookie_language = cookie_manager.get(cookie="language")
    cookie_userinfo = cookie_manager.get(cookie="cookie_userinfo")
    expires_at = datetime.datetime.now() + datetime.timedelta(days=30) # default: 1 day

    if "cookie_consent" not in st.session_state:
        st.session_state.cookie_consent = "no"
    if "cookie_action" not in st.session_state:
        st.session_state.cookie_action = None
    if "auto_login" not in st.session_state:
        st.session_state.auto_login = True

    if cookie_status is None: # Ensures _streamlit_xsrf is set first
        pass
    elif cookie_consent is None:
        cookie_manager.set("cookie_consent", "no", expires_at=expires_at)
        time.sleep(1) # Hold to give time for cookie to set 
        cookie_consent = cookie_manager.get(cookie="cookie_consent")

    if cookie_consent is None: # Ensures cookie_consent is set to "no"
        pass
    elif cookie_consent == "yes":
        if st.session_state.auto_login:
            st.session_state.language = cookie_language if cookie_language in ['English', 'Spanish', 'Japanese'] else 'Korean'
            if cookie_userinfo is None:
                setup_login_page()
                cookie_manager.set("language", st.session_state.language, expires_at=expires_at)
            else:
                st.session_state.username = cookie_userinfo["username"]
                st.session_state.name = cookie_userinfo["name"]
                st.rerun()
        else: # When logout button is clicked
            try:
                cookie_manager.delete("cookie_userinfo")
            except:
                pass
            finally:
                setup_login_page()
                cookie_manager.set("language", st.session_state.language, expires_at=expires_at)
    else: 
        if cookie_action == "yes":
            setup_login_page()
        else:
            if st.session_state.cookie_action == "yes":
                cookie_manager.set("cookie_action", "yes", expires_at=expires_at, key="0")
                cookie_manager.set("cookie_consent", st.session_state.cookie_consent, expires_at=expires_at, key="1")
                setup_login_page()
                if st.session_state.cookie_consent == "yes":
                    cookie_manager.set("language", st.session_state.language, expires_at=expires_at, key="2")
            else:
                if st.session_state.cookie_action == "pending": # Handling the language selectbox
                    setup_login_page()
                else: # Cookie preference has not been asked
                    setup_login_page()
                    ask_cookie_consent()
                    st.session_state.cookie_action = "pending"

def logout():
    for key in st.session_state:
        if key not in ['config', 'language', 'cookie_consent', 'cookie_action', 'auto_login']:
            del st.session_state[key]
    
    st.session_state.auto_login = False
    
    st.rerun()

def main():
    st.set_page_config(page_title="Macrogen Office", page_icon='macrogen_favicon.png')
    
    if 'config' not in st.session_state:
        with open('config.yaml', 'r') as file:
            st.session_state.config = yaml.safe_load(file)
    if 'language' not in st.session_state:
        st.session_state.language = 'Korean'
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'model' not in st.session_state:
        st.session_state.model = 'gpt'
    if 'reasoning_toggle' in st.session_state:
        st.session_state.reasoning_toggle = st.session_state.reasoning_toggle
    if 'temp_toggle' in st.session_state:
        st.session_state.temp_toggle = st.session_state.temp_toggle

    st.logo('macrogen_logo.png', icon_image='macrogen_favicon.png')
    css = """
        img.stLogo {
            height: 4rem;
        }
    """
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

    pages = [
        st.Page('src/chatbot.py', title='Macrogen Office', icon=':material/chat_bubble:'),
        st.Page('src/history.py', title='Chat History', icon=':material/forum:'),
        st.Page('src/profile.py', title='Reset Password', icon=':material/person:'),
        st.Page('src/faq.py', title='FAQ', icon=':material/help:'),
        st.Page('src/changelog.py', title='Changelog', icon=':material/overview:'),
        st.Page(logout, title='Logout', icon=':material/logout:')
    ]

    if not st.session_state.username:
        st.title("Macrogen Office")
        page_navigation = st.navigation([st.Page(check_auto_login)])
    else:
        page_navigation = st.navigation(pages, position='sidebar')
    page_navigation.run()

if __name__ == "__main__":
    main()
