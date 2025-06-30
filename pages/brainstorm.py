import streamlit as st
import requests
import base64
API_URL = "https://subashdvorak-brainstroming-fast-api.hf.space"  # Replace with your FastAPI URL

st.set_page_config(page_title="AI Business Ideation Platform", layout="wide")

# Store responses across user interactions
if 'business_details' not in st.session_state:
    st.session_state.business_details = {}
if 'final_ideation' not in st.session_state:
    st.session_state.final_ideation = []
if 'human_interactions' not in st.session_state:
    st.session_state.human_interactions = []
if 'brainstorm_response' not in st.session_state:
    st.session_state.brainstorm_response = {}
if 'final_story' not in st.session_state:
    st.session_state.final_story = ""
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = ""




# ---------------------- BRAINSTORM ----------------------
st.subheader("Story Boarding with brainstorming")

defaults = {
    "selected_topics": [],
    "selected_from_brainstorm": [],
    "story": "",
    "brainstorming_topics": [],
    "topics_to_pass":[],
    "base64_images": [],
    "history": [],
    "history_index": -1,  # -1 means no history yet
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

uploaded_files = st.file_uploader("📂 Upload reference images (optional)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    base64_images = []
    for file in uploaded_files:
        base64_images.append(base64.b64encode(file.read()).decode('utf-8'))
    st.session_state.base64_images = base64_images

def call_brainstorming_api():
    print('Selected topics:', st.session_state.topics_to_pass)
    response = requests.post(
        f"{API_URL}/brainstrom",  # Replace with your actual endpoint
        params={"thread_id": "my-session"},
        json={
            "preferred_topics": st.session_state.topics_to_pass,
            "image_base64_list": st.session_state.base64_images
        }
    )
    if response.ok:
        result_json = response.json()
        data = result_json.get("response", {})
        st.session_state.story = data.get("stories", [""])[-1]
        st.session_state.brainstorming_topics = data.get("brainstroming_topics", [])
    else:
        st.error("❌ API call failed.")
        st.write(response.text)

if st.button("🚀 Start Brainstorm"):
    with st.spinner('Generating story with brainstorming....'):
        # Truncate future if we're not at the end
        if st.session_state.history_index < len(st.session_state.history) - 1:
            st.session_state.history = st.session_state.history[:st.session_state.history_index + 1]

        # Save current state to history
        current_state = {
            "selected_topics": st.session_state.selected_topics.copy(),
            "selected_from_brainstorm": st.session_state.selected_from_brainstorm.copy(),
            "story": st.session_state.story,
            "brainstorming_topics": st.session_state.brainstorming_topics.copy()
        }
        st.session_state.history.append(current_state)
        st.session_state.history_index += 1

        # Update current state
        st.session_state.selected_topics.extend(st.session_state.selected_from_brainstorm)
        st.session_state.selected_from_brainstorm = []

        call_brainstorming_api()
        st.rerun()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📖 Story")
    st.text_area("Generated Story", st.session_state.story, height=300)

# with col2:
#     st.subheader("Brainstorming Topics (Click to Select)")
#     if st.session_state.brainstorming_topics:
#         topics_dict = st.session_state.brainstorming_topics[-1]
#         selected = set(st.session_state.selected_from_brainstorm)
#         for label, topic in topics_dict.items():
#             if st.checkbox(topic, key=topic, value=topic in selected):
#                 selected.add(topic)
#             else:
#                 selected.discard(topic)
#         st.session_state.topics_to_pass = list(selected)
#         st.session_state.selected_from_brainstorm = list(selected)
with col2:
    st.subheader("Brainstorming Topics (Click to Select / Edit)")
    if st.session_state.brainstorming_topics:
        topics_dict = st.session_state.brainstorming_topics[-1]
        selected = set(st.session_state.selected_from_brainstorm)
        updated_topics = {}

        for label, topic in topics_dict.items():
            col_a, col_b = st.columns([0.1, 0.9])
            with col_a:
                # Use a blank label and keep checkbox aligned
                checked = st.checkbox("", key=f"check_{label}", value=topic in selected)
            with col_b:
                edited_topic = st.text_input("", value=topic, key=f"edit_{label}")

            if checked:
                selected.add(edited_topic)
            else:
                selected.discard(edited_topic)

            updated_topics[label] = edited_topic

        st.session_state.topics_to_pass = list(selected)
        st.session_state.selected_from_brainstorm = list(selected)

    else:
        st.info("No brainstorming topics yet. Click 'Generate Brainstorm' to start.")

if st.button("🔙 Back"):
    if st.session_state.history_index > 0:
        st.session_state.history_index -= 1
        state = st.session_state.history[st.session_state.history_index]
        st.session_state.selected_topics = state["selected_topics"]
        st.session_state.selected_from_brainstorm = state["selected_from_brainstorm"]
        st.session_state.story = state["story"]
        st.session_state.brainstorming_topics = state["brainstorming_topics"]
        st.rerun()
    else:
        st.warning("You're at the first step.")

if st.button("🔜 Forward"):
    if st.session_state.history_index < len(st.session_state.history) - 1:
        st.session_state.history_index += 1
        state = st.session_state.history[st.session_state.history_index]
        st.session_state.selected_topics = state["selected_topics"]
        st.session_state.selected_from_brainstorm = state["selected_from_brainstorm"]
        st.session_state.story = state["story"]
        st.session_state.brainstorming_topics = state["brainstorming_topics"]
        st.rerun()
    else:
        st.warning("You're at the most recent step.")

st.markdown("---")