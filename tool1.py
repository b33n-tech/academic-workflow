import streamlit as st
import uuid
import json
from docx import Document
from io import BytesIO
import streamlit.components.v1 as components

st.set_page_config(page_title='Outil 1 – Architecture du mémoire', layout='wide')

# --- Config ---
LEVELS = [
    'Titre 1: I.',
    'Titre 2: I.1.',
    'Titre 3: I.1.a.',
    'Titre 4: I.1.a.1.',
    'Titre 5: I.1.a.1.a'
]
LLM_OPTIONS = [
    'https://claude.ai/',
    'https://chat.deepseek.com/',
    'https://chatgpt.com/',
    'https://www.perplexity.ai/'
]

# --- Session ---
if 'blocks' not in st.session_state:
    st.session_state.blocks = []
if 'selected' not in st.session_state:
    st.session_state.selected = None
if 'history' not in st.session_state:
    st.session_state.history = []

# --- Helpers ---
def push_history():
    st.session_state.history.append(json.dumps(st.session_state.blocks))
    if len(st.session_state.history) > 30:
        st.session_state.history.pop(0)

def undo():
    if st.session_state.history:
        last = st.session_state.history.pop()
        st.session_state.blocks = json.loads(last)

def new_block():
    return {
        'id': str(uuid.uuid4()),
        'title': '',
        'level': LEVELS[0],
        'pitch': '',
        'summary': '',
        'comments': []
    }

def export_json():
    return json.dumps(st.session_state.blocks, ensure_ascii=False, indent=2)

def export_docx():
    doc = Document()
    for b in st.session_state.blocks:
        lvl = LEVELS.index(b['level']) + 1
        doc.add_heading(b['title'] or 'Sans titre', level=min(lvl, 4))
        if b['pitch']:
            doc.add_paragraph('Pitch : ' + b['pitch'])
        if b['summary']:
            doc.add_paragraph(b['summary'])
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- UI Header ---
header = st.container()
col1, col2, col3, col4 = header.columns([1,1,5,2])
with col1:
    if st.button('➕ Ajouter un bloc'):
        push_history()
        st.session_state.blocks.append(new_block())
with col2:
    if st.button('🗑️ Supprimer le bloc sélectionné'):
        if st.session_state.selected:
            push_history()
            st.session_state.blocks = [b for b in st.session_state.blocks if b['id'] != st.session_state.selected]
            st.session_state.selected = None
with col4:
    st.session_state.selected_llm = st.selectbox('LLM', LLM_OPTIONS, index=0)

# --- Upload Archive ---
uploaded = st.file_uploader('📂 Charger une archive JSON', type=['json'])
if uploaded:
    try:
        data = json.load(uploaded)
        if isinstance(data, list):
            push_history()
            st.session_state.blocks = data
            st.success('Archive chargée ✅')
        else:
            st.error('Le fichier JSON doit contenir une liste de blocs.')
    except Exception as e:
        st.error(f'Erreur lors du chargement : {e}')

st.markdown('---')

# --- Blocks display ---
st.subheader('🧩 Structure du mémoire')

if not st.session_state.blocks:
    st.info('Clique sur **"Ajouter un bloc"** pour commencer.')

for i, b in enumerate(st.session_state.blocks):
    with st.container():
        st.markdown('---')
        block_header = st.columns([6,1,1,1])
        with block_header[0]:
            st.markdown(f"### {b['title'] or 'Sans titre'}")
        with block_header[1]:
            if st.button('⬆️', key=f'up_{b["id"]}') and i > 0:
                push_history()
                st.session_state.blocks[i], st.session_state.blocks[i-1] = st.session_state.blocks[i-1], st.session_state.blocks[i]
                st.experimental_rerun()
        with block_header[2]:
            if st.button('⬇️', key=f'down_{b["id"]}') and i < len(st.session_state.blocks)-1:
                push_history()
                st.session_state.blocks[i], st.session_state.blocks[i+1] = st.session_state.blocks[i+1], st.session_state.blocks[i]
                st.experimental_rerun()
        with block_header[3]:
            if st.button('✏️ Éditer', key=f'sel_{b["id"]}'):
                st.session_state.selected = b['id']

        if st.session_state.selected == b['id']:
            st.text_input('Titre', key=f'title_{b["id"]}', value=b['title'], on_change=lambda k=b['id']: st.session_state.blocks.__setitem__(i, {**b, 'title': st.session_state[f'title_{k}']}))
            st.selectbox('Niveau de titre', LEVELS, index=LEVELS.index(b['level']), key=f'level_{b["id"]}', on_change=lambda k=b['id']: st.session_state.blocks.__setitem__(i, {**b, 'level': st.session_state[f'level_{k}']}))
            st.text_input('Pitch / Sujet rapide', value=b['pitch'], key=f'pitch_{b["id"]}', on_change=lambda k=b['id']: st.session_state.blocks.__setitem__(i, {**b, 'pitch': st.session_state[f'pitch_{k}']}))
            st.text_area('Résumé long', value=b['summary'], key=f'sum_{b["id"]}', on_change=lambda k=b['id']: st.session_state.blocks.__setitem__(i, {**b, 'summary': st.session_state[f'sum_{k}']}))
            st.markdown('**Commentaires :**')
            for c in b.get('comments', []):
                st.write(f"- {c['text']}")
            new_comment = st.text_input('Ajouter un commentaire', key=f'com_{b["id"]}')
            if st.button('💬 Ajouter', key=f'addcom_{b["id"]}') and new_comment.strip():
                push_history()
                b.setdefault('comments', []).append({'text': new_comment})
                st.experimental_rerun()

# --- Sidebar Pad ---
st.sidebar.title('🧭 Pad de travail')
st.sidebar.markdown('Utilise ce pad pour exporter ou annuler une action.')

if st.sidebar.button('↩️ Annuler (Undo)'):
    undo()
    st.experimental_rerun()

st.sidebar.download_button('💾 Télécharger JSON', data=export_json(), file_name='architecture.json')

if st.sidebar.button('📄 Exporter DOCX'):
    docx_data = export_docx()
    st.sidebar.download_button('Télécharger DOCX', data=docx_data, file_name='architecture.docx')

if st.sidebar.button('📤 Push LLM (Copier titres hiérarchisés)'):
    titles = '\n'.join([b['title'] for b in st.session_state.blocks if b['title']])
    components.html(f"<textarea id='t' style='width:100%;height:200px;'>{titles}</textarea><br><button onclick=\"navigator.clipboard.writeText(document.getElementById('t').value)\">Copier</button>", height=250)

st.markdown('---')
st.caption("💡 Astuce : clique sur ✏️ pour éditer un bloc. Utilise les flèches pour réordonner.")
