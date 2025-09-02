import streamlit as st
import mysql.connector, bcrypt, time

LABELS = {
    'Form name': {'English': 'Reset Password', 'Korean': '비밀번호 변경', 'Spanish': 'Restablecer contraseña', 'Japanese': 'パスワードをリセットする'},
    'Current password': {'English': 'Current password', 'Korean': '현재 비밀번호', 'Spanish': 'Contraseña actual', 'Japanese': '現在のパスワード'},
    'New password': {'English': 'New password', 'Korean': '새로운 비밀번호', 'Spanish': 'Nueva contraseña', 'Japanese': '新しいパスワード'},
    'Repeat password': {'English': 'Repeat password', 'Korean': '새로운 비밀번호 확인', 'Spanish': 'Repetir contraseña', 'Japanese': 'パスワードを繰り返す'},
    'Reset': {'English': 'Reset', 'Korean': '변경', 'Spanish': 'Restablecer', 'Japanese': 'リセット'},
    'Change success': {'English': 'Password has been successfully changed.', 'Korean': '비밀번호가 성공적으로 변경되었습니다.', 'Spanish': 'La contraseña se ha cambiado correctamente.', 'Japanese': 'パスワードが正常に変更されました.'},
    'Password unmatch': {'English': 'New passwords do not match.', 'Korean': '새로운 비밀번호가 일치하지 않습니다.', 'Spanish': 'Las nuevas contraseñas no coinciden.', 'Japanese': '新しいパスワードが一致しません。'},
    'Password incorrect': {'English': 'Current password is incorrect.', 'Korean': '현재 비밀번호가 잘못되었습니다.', 'Spanish': 'La contraseña actual es incorrecta.', 'Japanese': '現在のパスワードが間違っています。'},
}

def get_current_password(username):
    try:
        connection = mysql.connector.connect(
            user=st.session_state.config['authentication']['user'],
            password=st.session_state.config['authentication']['password'],
            host=st.session_state.config['authentication']['host'],
            database=st.session_state.config['authentication']['database']
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"SELECT password FROM {st.session_state.config['authentication']['table']} WHERE username = %s", (username,))
            result = cursor.fetchone()
            cursor.close()
            return result['password'] if result else None
    except mysql.connector.Error as e:
        st.error(f"Error connecting to MySQL database: {e}")
    finally:
        if connection.is_connected():
            connection.close()

def update_mysql(username, new_password_hash):
    try:
        connection = mysql.connector.connect(
            user=st.session_state.config['authentication']['user'],
            password=st.session_state.config['authentication']['password'],
            host=st.session_state.config['authentication']['host'],
            database=st.session_state.config['authentication']['database']
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute(f"UPDATE {st.session_state.config['authentication']['table']} SET password = %s WHERE username = %s", (new_password_hash, username))
            connection.commit()
            cursor.close()
    except mysql.connector.Error as e:
        st.error(f"Error connecting to MySQL database: {e}")
    finally:
        if connection.is_connected():
            connection.close()

def main():
    st.header(LABELS['Form name'][st.session_state.language])

    with st.form(key='reset_password_form'):
        current_password = st.text_input(LABELS['Current password'][st.session_state.language], type="password")
        new_password = st.text_input(LABELS['New password'][st.session_state.language], type="password")
        repeat_password = st.text_input(LABELS['Repeat password'][st.session_state.language], type="password")
        submit_button = st.form_submit_button(LABELS['Reset'][st.session_state.language])

    if submit_button:
        current_password_mysql = get_current_password(st.session_state.username)
        if current_password == current_password_mysql:
            if new_password == repeat_password:
                new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                update_mysql(st.session_state.username, new_password_hash)
                st.success(LABELS['Change success'][st.session_state.language])
                time.sleep(3)
                st.switch_page('src/chatbot.py')
            else:
                st.error(LABELS['Password unmatch'][st.session_state.language])
        elif bcrypt.checkpw(current_password.encode('utf-8'), current_password_mysql.encode('utf-8')):
            if new_password == repeat_password:
                new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                update_mysql(st.session_state.username, new_password_hash)
                st.success(LABELS['Change success'][st.session_state.language])
                time.sleep(3)
                st.switch_page('src/chatbot.py')
            else:
                st.error(LABELS['Password unmatch'][st.session_state.language])
        else:
            st.error(LABELS['Password incorrect'][st.session_state.language])

if __name__ == "__main__":
    main()
