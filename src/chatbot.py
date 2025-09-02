import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
import extra_streamlit_components as stx
import streamlit_openai
from streamlit_openai.chat import Chat, FILE_SEARCH_EXTENSIONS, CODE_INTERPRETER_EXTENSIONS, VISION_EXTENSIONS
import openai, os, datetime, xlrd, openpyxl, boto3
from pathlib import Path

LABELS = {
    'New chat': {'English': 'New chat', 'Korean': '새 대화', "Spanish": "Nuevo chat", "Japanese": "新しいチャット"},
    'Reasoning toggle label': {'English': 'Activate reasoning', 'Korean': '추론 활성화', "Spanish": "Activar razonamiento", "Japanese": "推論を有効化"},
    'Temp toggle label': {'English': 'Temporary mode', 'Korean': '임시 모드', "Spanish": "Modo temporal", "Japanese": "一時モード"},
    'Chat list': {'English': 'Chats', 'Korean': '대화 목록', "Spanish": "Chats", "Japanese": "チャット"},
}

INSTRUCTIONS = """
You are 'Macrogen Office', an AI assistant developed by Macrogen Inc. 
Macrogen is a global genetic testing and sequencing company headquartered in Seoul, South Korea, providing clinical genomic analysis, 
personal genome services, research sequencing, and customized genetic tests to clients worldwide.
You should be able to accurately interpret and explain domain-specific terms such as NGS (Next-Generation Sequencing),
CES (Clinical Exome Sequencing), RNAseq (RNA Sequencing), multiplexing, reads, coverage, and library preparation in a genomics context.
User questions may be in Korean, English, Spanish, or Japanese. You should detect the language of the query and respond in the same language.
Users may upload documents or data (e.g., Excel sheets, PDFs, CSVs) that contain information on orders, test results, or experimental plans etc.
You must treat any uploaded files or shared information as confidential internal company data.
Do not reveal or share this information outside the current conversation.
"""

class MacrogenOfficeChat(Chat):
    def handle_files(self, uploaded_files) -> None:
        """Handles uploaded files with conversion of unsupported file types."""
        if uploaded_files is None:
            return
        else:
            for uploaded_file in uploaded_files:
                if uploaded_file.file_id in [x.uploaded_file.file_id for x in self._tracked_files if isinstance(x, UploadedFile)]:
                    continue

                file_name = uploaded_file.name
                file_path = Path(self._temp_dir.name)/file_name
                file_extension = file_path.suffix.lower()

                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                WHISPER_EXTENSIONS = ['.m4a', '.mp3', '.webm', '.mp4', '.mpga', '.wav', '.mpeg']
                if file_extension in (FILE_SEARCH_EXTENSIONS + CODE_INTERPRETER_EXTENSIONS + VISION_EXTENSIONS + WHISPER_EXTENSIONS):
                    pass
                else:
                    if file_extension == '.xls':
                        wb1 = xlrd.open_workbook(file_path)
                        wb2 = openpyxl.Workbook()
                        for sheet_name in wb1.sheet_names():
                            sheet1 = wb1.sheet_by_name(sheet_name)
                            sheet2 = wb2.create_sheet(title=sheet_name)
                            for row in range(sheet1.nrows):
                                for col in range(sheet1.ncols):
                                    sheet2.cell(row=row+1, column=col+1, value=sheet1.cell_value(row, col))
                        del wb2['Sheet'] # Remove the default empty sheet
                        file_path = file_path.with_suffix(".xlsx")
                        wb2.save(file_path)
                    elif file_extension == '.hwp':
                        original_path = file_path
                        file_path = file_path.with_suffix(".html")
                        os.system(f'hwp5html "{original_path}" --output "{file_path}" --html')
                    else:
                        raise ValueError(f"Unsupported file type: {file_name}")
                self.track(str(file_path))

def create_functions():
    api_key = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=api_key)

    # Web Search
    def web_search_handler(prompt):
        response = client.chat.completions.create(
            model="gpt-4o-search-preview",
            web_search_options={},
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    
    search_web = streamlit_openai.CustomFunction(
        name="search_web",
        description="Search the web using a query.",
        parameters={
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Search query.",
                }
            },
            "required": ["prompt"]
        },
        handler=web_search_handler
    )

    # Audio Transcription
    def transcribe_audio_handler(audio_file):
        response = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=open(audio_file, "rb"),
        )
        return response.text
    
    transcribe_audio = streamlit_openai.CustomFunction(
        name="transcribe_audio",
        description="Convert speech to text.",
        parameters={
            "type": "object",
            "properties": {
                "audio_file": {
                    "type": "string",
                    "description": "The audio file to transcribe.",
                }
            },
            "required": ["audio_file"]
        },
        handler=transcribe_audio_handler
    )

    return search_web, transcribe_audio

def initialize_chatbot():
    st.session_state.pop('chat_name', None)
    
    placeholder_dict = {
        'English': 'How can I help you?',
        'Korean': '무엇을 도와드릴까요?',
        'Spanish': '¿En qué puedo ayudarte?',
        'Japanese': '何かお手伝いできることはありますか?'
    }
    welcome_message_dict = {
        'gpt': {
            'English': f"""Hello, {st.session_state.name}. I'm Macrogen Office. I support tasks like chatting, file search, code explanation, image generation, and web browsing. How can I help you?""",
            'Korean': f"""안녕하세요, {st.session_state.name}님. 저는 마크로젠 오피스입니다. 저는 대화, 파일 검색, 코드 해석, 이미지 생성, 웹 탐색 등의 작업을 지원합니다. 무엇을 도와드릴까요?""",
            'Spanish': f"""Hola, {st.session_state.name}. Soy Macrogen Office. Puedo ayudarte con tareas como chatear, buscar archivos, explicar código, generar imágenes y navegar por la web. ¿En qué puedo ayudarte?""",
            'Japanese': f"""こんにちは、{st.session_state.name}さん。私はマクロジェンオフィスです。会話、ファイル検索、コードの説明、画像生成、ウェブ閲覧などの作業をサポートします。どのようにお手伝いできますか？"""
        },
        'reasoning': {
            'English': f"""Hello, {st.session_state.name}. I'm Macrogen Office, currently running in reasoning mode. I'm optimized for data analysis, logic tasks, and structured problem solving. How can I help you?""",
            'Korean': f"""안녕하세요, {st.session_state.name}님. 저는 마크로젠 오피스입니다. 현재 추론 모드로 실행 중으로, 데이터 분석, 논리 작업, 구조적 문제 해결에 특화되어 있습니다. 무엇을 도와드릴까요?""",
            'Spanish': f"""Hola, {st.session_state.name}. Soy Macrogen Office, actualmente funcionando en modo de razonamiento. Estoy optimizado para el análisis de datos, tareas lógicas y la resolución estructurada de problemas. ¿En qué puedo ayudarte?""",
            'Japanese': f"""こんにちは、{st.session_state.name}さん。私はマクロジェンオフィスです。現在、推論モードで稼働中で、データ分析、論理的タスク、構造的な問題解決を得意としています。どうお手伝いできますか？"""
        }
    }
    example_messages_dict = {
        "gpt": {
            "Q1": {
                "English": ":money_with_wings: Translate \"please send the purchase order within a week\" into Korean",
                "Korean": ":money_with_wings: \"구입 주문서를 일주일 내로 보내주세요\"를 영어로 번역해주세요.",
                "Spanish": ":money_with_wings: Traduce \"por favor envíe la orden de compra dentro de una semana\" al inglés.",
                "Japanese": ":money_with_wings: 「購入注文書を一週間以内に送ってください」を英語に翻訳してください。",
            },
            "Q2": {
                "English": ":newspaper: Find the top news headlines about genetic testing today.",
                "Korean": ":newspaper: 오늘의 유전자 검사 관련 주요 뉴스를 찾아주세요.",
                "Spanish": ":newspaper: Busca los principales titulares de noticias sobre pruebas genéticas de hoy.",
                "Japanese": ":newspaper: 今日の遺伝子検査に関する主なニュースの見出しを探してください。"
            },
            "Q3": {
                "English": ":bar_chart: Visualize the uploaded data using graphs.",
                "Korean": ":bar_chart: 업로드한 데이터를 그래프로 시각화해주세요.",
                "Spanish": ":bar_chart: Visualiza los datos subidos con gráficos.",
                "Japanese": ":bar_chart: アップロードされたデータをグラフで可視化してください。"
            },
            "Q4": {
                "English": ":test_tube: How many reads are needed to generate 6 Gb of data for exome sequencing at 100x coverage?",
                "Korean": ":test_tube: 엑솜 시퀀싱에서 100x 커버리지를 위해 6기가베이스 데이터를 생성하려면 몇 개의 리드가 필요하나요?",
                "Spanish": ":test_tube: ¿Cuántas lecturas se necesitan para generar 6 Gb de datos en una secuenciación del exoma con una cobertura de 100x?",
                "Japanese": ":test_tube: エクソームシーケンシングで100xのカバレッジを得るには、6Gbのデータを生成するのに何本のリードが必要ですか?"
            }
        },
        "reasoning": {
            "Q1": {
                "English": ":microbe: Propose an in-depth digital marketing strategy for a DTC microbiome test entering the US market.",
                "Korean": ":microbe: DTC 마이크로바이옴 검사의 미국 진출을 위한 심층 디지털 마케팅 전략 제안서를 작성해주세요.",
                "Spanish": ":microbe: Propón una estrategia digital detallada para lanzar un test DTC de microbioma en EE. UU.",
                "Japanese": ":microbe: DTCマイクロバイオーム検査の米国市場進出に向けた詳細なデジタルマーケティング戦略提案書を作成してください。"
            },
            "Q2": {
                "English": ":dna: Write a grant proposal for developing a personalized disease prediction model, and explain the key decisions.",
                "Korean": ":dna: 개인 맞춤형 질병 예측 모델 개발을 위한 연구비 제안서를 작성하고, 주요 결정을 설명해 주세요.",
                "Spanish": ":dna: Propón una propuesta para un modelo de predicción personalizada de enfermedades y explica las decisiones clave.",
                "Japanese": ":dna: 個別化疾患予測モデルの開発に関する助成金申請書を作成し、主要な判断について説明してください。"
            },
            "Q3": {
                "English": ":clipboard: Draft a SOP excerpt for handling patient samples in a CLIA-certified lab for genomic testing.",
                "Korean": ":clipboard: CLIA 인증 실험실에서 유전자 검사를 위한 환자 샘플 취급에 대한 표준 운영 절차(SOP) 초안을 작성해주세요.",
                "Spanish": ":clipboard: Redacta un extracto de SOP para manejar muestras de pacientes en un laboratorio CLIA.",
                "Japanese": ":clipboard: CLIA認定の実験室でのゲノム検査のための患者サンプル取り扱いに関するSOPの抜粋を作成してください。"
            },
            "Q4": {
                "English": ":mag: Review the uploaded dataset for potential QC issues and recommend follow-up checks.",
                "Korean": ":mag: 업로드된 데이터를 분석하여 QC 관련 이상 징후를 점검하고, 후속 검토 사항을 권장해주세요.",
                "Spanish": ":mag: Revisa el conjunto de datos para detectar problemas de QC y recomienda seguimientos.",
                "Japanese": ":mag: データセットを確認し、QC上の問題を特定して、推奨されるフォローアップを提案してください。"
            }
        }
    }

    placeholder = placeholder_dict[st.session_state.language]
    welcome_message = welcome_message_dict[st.session_state.model][st.session_state.language]
    example_messages = [
        example_messages_dict[st.session_state.model]['Q1'][st.session_state.language],
        example_messages_dict[st.session_state.model]['Q2'][st.session_state.language],
        example_messages_dict[st.session_state.model]['Q3'][st.session_state.language],
        example_messages_dict[st.session_state.model]['Q4'][st.session_state.language]
    ]
    search_web, transcribe_audio = create_functions()
        
    st.session_state.chat = MacrogenOfficeChat(
        model='o3' if st.session_state.model == 'reasoning' else 'gpt-4o',
        instructions=INSTRUCTIONS,
        temperature=None if st.session_state.model == 'reasoning' else 0,
        functions=[search_web, transcribe_audio] if st.session_state.model == 'reasoning' else [transcribe_audio],
        placeholder=placeholder,
        welcome_message=welcome_message,
        example_messages=example_messages,
        allow_web_search=False if st.session_state.model == 'reasoning' else True
    )
        
def display_chats(s3, bucket, s3_folder):
    response = s3.list_objects(Bucket=bucket, Prefix=f"{s3_folder}/")
    file_list = []
    for obj in response.get('Contents', []):
        s3_key = Path(obj['Key'])
        last_modified = obj['LastModified']
        if s3_key.suffix == '.zip':
            file_list.append({'file': s3_key.name, 'last_modified': last_modified})
    file_list.sort(key=lambda x: x['last_modified'], reverse=True)

    def load_chat(file):
        local_file = Path.cwd()/f'{file}.zip'
        s3.download_file(bucket, f'{s3_folder}/{file}.zip', str(local_file))

        st.session_state.chat_name = file
        st.session_state.chat = st.session_state.chat.load(local_file.name)
        st.session_state.model = 'reasoning' if st.session_state.chat.model == 'o3' else 'gpt'
        local_file.unlink()
        st.session_state.reasoning_toggle = (st.session_state.model == 'reasoning')
        st.session_state.temp_toggle = False

    st.subheader(LABELS['Chat list'][st.session_state.language])
    with st.container(border=True, height=350):
        file_names = [Path(x['file']).stem for x in file_list]
        for file in file_names:
            st.button(
                label=file.split('_')[0],
                on_click=lambda f=file: load_chat(f),
                use_container_width=True,
                key=f"chat_{file}"
            )

def autosave_chat(s3, bucket, s3_folder):
    if len(st.session_state.chat._sections) <= 1:
        return

    chat_name = st.session_state.get('chat_name', None)
    rerun_needed = False

    if chat_name is None:
        summary = st.session_state.chat.summary
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        if summary == 'New Chat':
            st.session_state.chat_name = f'New Chat_{timestamp}'
        else:
            st.session_state.chat_name = f'{summary}_{timestamp}'
        rerun_needed = True
    elif chat_name.startswith('New Chat'):
        summary = st.session_state.chat.summary
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        if summary == 'New Chat':
            pass # Keep using 'New Chat_timestamp'
        else:
            st.session_state.chat_name = f'{summary}_{timestamp}'
            s3.delete_object(Bucket=bucket, Key=f'{s3_folder}/{chat_name}.zip')
            rerun_needed = True
    else:
        pass # Keep using 'summary_timestamp'

    temp_file = Path(st.session_state.chat._temp_dir.name)/f'{st.session_state.chat_name}.zip'
    st.session_state.chat.save(str(temp_file))
    s3.upload_file(str(temp_file), bucket, f'{s3_folder}/{temp_file.name}')

    if rerun_needed:
        st.rerun()
        
def main():
    cookie_manager = stx.CookieManager()
    expires_at = datetime.datetime.now() + datetime.timedelta(days=30) # default: 1 day
    cookie_consent = cookie_manager.get(cookie="cookie_consent")
    if cookie_consent == "yes":
        cookie_manager.set("cookie_userinfo", {"username":st.session_state.username, "name":st.session_state.name}, expires_at=expires_at)

    s3 = boto3.client('s3')
    bucket = st.session_state.config['history']['bucket']
    s3_folder = f"{st.session_state.config['history']['users_dir']}/{st.session_state.username}"

    if 'chat' not in st.session_state:
        initialize_chatbot()

    with st.sidebar:
        if st.button(LABELS['New chat'][st.session_state.language], icon=':material/add:', use_container_width=True):
            st.session_state.pop('chat', None)
            st.session_state.pop('chat_name', None)
            st.rerun()

        def change_model():
            st.session_state.model = 'reasoning' if st.session_state.reasoning_toggle else 'gpt'
            initialize_chatbot()

        col1, col2 = st.columns(2)
        col1.toggle(LABELS['Reasoning toggle label'][st.session_state.language], on_change=change_model, key='reasoning_toggle')
        col2.toggle(LABELS['Temp toggle label'][st.session_state.language], on_change=initialize_chatbot, key='temp_toggle')

        display_chats(s3, bucket, s3_folder)

    st.session_state.chat.run()
    if not st.session_state.temp_toggle:
        autosave_chat(s3, bucket, s3_folder)

if __name__ == "__main__":
    main()
