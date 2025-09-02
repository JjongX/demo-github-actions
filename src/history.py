import streamlit as st
from pathlib import Path
from src.chatbot import initialize_chatbot
import boto3, tempfile, zipfile, datetime

LABELS = {
    'Save chat header': {'English': 'Save Current Chat', 'Korean': '현재 대화 저장', 'Spanish': 'Guardar chat actual', 'Japanese': '現在のチャットを保存する'},
    'Name input label': {'English': 'Enter a name for the current chat.', 'Korean': '현재 대화의 이름을 입력하세요.', 'Spanish': 'Ingrese un nombre para el chat actual.', 'Japanese': '現在のチャットの名前を入力してください。'},
    'Save button': {'English': 'Save', 'Korean': '저장', 'Spanish': 'Guardar', 'Japanese': '保存'},
    'Manage chat header': {'English': 'Manage Past Chats', 'Korean': '과거 대화 관리', 'Spanish': 'Administrar chats pasados', 'Japanese': '過去のチャットを管理する'},
    'Load chat header': {'English': 'Load Past Chats', 'Korean': '과거 대화 불러오기/삭제하기', 'Spanish': 'Cargar/Eliminar chats pasados', 'Japanese': '過去のチャットをロード/削除する'},
    'Selectbox label': {'English': 'Select a chat to load or delete.', 'Korean': '불러오거나 삭제할 대화를 선택하세요.', 'Spanish': 'Seleccione un chat para cargar o eliminar.', 'Japanese': 'ロードまたは削除するチャットを選択してください。'},
    'Load button': {'English': 'Load', 'Korean': '불러오기', 'Spanish': 'Cargar', 'Japanese': 'ロード'},
    'Rename button': {'English': 'Rename', 'Korean': '이름 바꾸기', 'Spanish': 'Renombrar', 'Japanese': '名前を変更'},
    'Rename input label': {'English': 'Enter a new name for the chat.', 'Korean': '대화의 새 이름을 입력하세요.', 'Spanish': 'Ingrese un nuevo nombre para el chat.', 'Japanese': 'チャットの新しい名前を入力してください。'},
    'Slash error': {'English': 'The name cannot contain a slash (/).', 'Korean': '이름에 / 문자를 포함할 수 없습니다.', 'Spanish': 'El nombre no puede contener una barra (/).', 'Japanese': '名前に /  を含めることはできません。'},
    'Delete button': {'English': 'Delete', 'Korean': '삭제하기', 'Spanish': 'Eliminar', 'Japanese': '削除'},
}

def manage_chats(s3, bucket, s3_folder):
    st.header(LABELS['Manage chat header'][st.session_state.language])

    response = s3.list_objects(Bucket=bucket, Prefix=f"{s3_folder}/")
    file_list = []
    for obj in response.get('Contents', []):
        s3_key = Path(obj['Key'])
        last_modified = obj['LastModified']
        if s3_key.suffix == '.zip':
            file_list.append({'file': s3_key.name, 'last_modified': last_modified})
    file_list.sort(key=lambda x: x['last_modified'], reverse=True)

    container = st.container(border=True)
    with container:
        file_names = [Path(x['file']).stem for x in file_list]
        selected_file = st.selectbox(LABELS['Selectbox label'][st.session_state.language], file_names, format_func=lambda name: name.split('_')[0])
        col1, col2, col3 = st.columns(3, gap='medium')
        with col1:
            if selected_file and st.button(LABELS['Load button'][st.session_state.language], use_container_width=True):
                local_file = Path.cwd()/f'{selected_file}.zip'
                s3.download_file(bucket, f'{s3_folder}/{selected_file}.zip', str(local_file))

                st.session_state.chat_name = selected_file
                st.session_state.chat = st.session_state.chat.load(local_file.name)
                st.session_state.model = 'reasoning' if st.session_state.chat.model == 'o3' else 'gpt'
                local_file.unlink()
                st.session_state.reasoning_toggle = (st.session_state.model == 'reasoning')
                st.session_state.temp_toggle = False
                st.switch_page('src/chatbot.py')
        with col2:
            if 'rename_mode' not in st.session_state:
                st.session_state.rename_mode = False

            def change_mode():
                st.session_state.rename_mode = not st.session_state.rename_mode

            if selected_file:
                st.button(LABELS['Rename button'][st.session_state.language], on_click=change_mode, use_container_width=True)
            
            if st.session_state.rename_mode:
                with container.form(key='rename_chat_form', clear_on_submit=True, border=False):
                    date = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                    new_name = f"{st.text_input(LABELS['Rename input label'][st.session_state.language])}_{date}"
                    col4, _, _ = st.columns(3, gap='medium')
                    submitted = col4.form_submit_button(LABELS['Save button'][st.session_state.language], use_container_width=True)
                    if submitted:
                        if '/' in new_name:
                            st.error(LABELS['Slash error'][st.session_state.language])
                        else:
                            zip_old = Path(tempfile.gettempdir())/f"{selected_file}.zip"
                            zip_new = Path(tempfile.gettempdir())/f"{new_name}.zip"

                            s3.download_file(bucket, f'{s3_folder}/{selected_file}.zip', str(zip_old))
                            with tempfile.TemporaryDirectory() as extract_dir:
                                with zipfile.ZipFile(zip_old, 'r') as zip_ref:
                                    zip_ref.extractall(extract_dir)
                                temp_old = next(Path(extract_dir).iterdir())
                                temp_new = Path(extract_dir)/new_name
                                temp_old.rename(temp_new)

                                with zipfile.ZipFile(zip_new, 'w', zipfile.ZIP_DEFLATED) as zipf:
                                    for file in temp_new.rglob('*'):
                                        if file.is_file():
                                            zipf.write(file, file.relative_to(temp_new.parent))

                            s3.upload_file(str(zip_new), bucket, f"{s3_folder}/{new_name}.zip")
                            s3.delete_object(Bucket=bucket, Key=f"{s3_folder}/{selected_file}.zip")
                            st.session_state.rename_mode = False
                            st.rerun()
        with col3:
            if selected_file and st.button(LABELS['Delete button'][st.session_state.language], use_container_width=True):
                s3.delete_object(Bucket=bucket, Key=f"{s3_folder}/{selected_file}.zip")
                st.rerun()

def main():
    s3 = boto3.client('s3')
    bucket = st.session_state.config['history']['bucket']
    s3_folder = f"{st.session_state.config['history']['users_dir']}/{st.session_state.username}"

    if "chat" not in st.session_state:
        initialize_chatbot()

    manage_chats(s3, bucket, s3_folder)

if __name__ == "__main__":
    main()
