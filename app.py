import streamlit as st
import requests
import base64
from streamlit import switch_page

API_URL = "https://subashdvorak-brainstroming-fast-api.hf.space"

st.set_page_config(page_title="AI Business Ideation Platform", layout="wide")
st.header("Welcome to RT-GENAI")

# Initialize session state
defaults = {
    'business_details': {},
    'details_completed': False,
    'final_ideation': [],
    'human_interactions': [],
    'brainstorm_response': {},
    'final_story': "",
    'generated_image': "",
    'selected_topics': [],
    'selected_from_brainstorm': [],
    'story': "",
    'brainstorming_topics': [],
    'topics_to_pass': [],
    'base64_images': [],
    'history': [],
    'history_index': -1,
    'trigger_brainstorm': False
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Step 1: Context Analysis or Orchestration
st.subheader("How can I help you?")
msg = st.text_input("")

uploaded_files = st.file_uploader("\U0001F4C2 Upload reference images (optional)", type=['png', 'jpg', 'jpeg'], key="initial_image_uploader")
if uploaded_files:
    base64_images = []
    for file in uploaded_files:
        try:
            file_bytes = file if isinstance(file, bytes) else file.read()
            base64_str = base64.b64encode(file_bytes).decode('utf-8')
            base64_images.append(base64_str)
        except Exception as e:
            st.warning(f"Failed to process file: {file}. Error: {e}")
    st.session_state.base64_images = base64_images
else:
    print("No file uploaded.")

if st.button("Submit"):
    if not st.session_state.details_completed:
        with st.spinner("Analyzing your business context..."):
            resp = requests.post(f"{API_URL}/context-analysis", json={"message": msg})
            if resp.ok:
                response = resp.json()
                st.markdown(response.get('response'))
                if response.get('complete'):
                    st.session_state.details_completed = True
                    st.session_state.business_details = response.get("business_details", {})
                    st.success("Context analysis completed. Now you can interact freely.")
            else:
                st.error("Context analysis failed.")

    else:
        with st.spinner("Analyzing your request and deciding the next step..."):
            resp = requests.post(f"{API_URL}/orchestration", json={"message": msg, "image_base64": st.session_state.base64_images})
            if resp.ok:
                response = resp.json()
                tool = response.get("tool_response")
                message = response.get("message_response")
                image_caption = response.get("image_caption")
                st.write('Tool response:', tool)

                # ========== Tool Handling ==========
                if "ideation" in tool:
                    with st.spinner("Generating ideas for your business..."):
                        resp = requests.post(f"{API_URL}/ideation")
                        if resp.ok:
                            st.session_state.final_ideation = resp.json()["response"]["improver_response"][-1]
                            if len(st.session_state.final_ideation) > 0:
                                st.markdown(f"*Idea:1* - {eval(st.session_state.final_ideation)[0]}")
                                st.markdown(f"*Idea:2* - {eval(st.session_state.final_ideation)[1]}")
                                st.markdown(f"*Idea:3* - {eval(st.session_state.final_ideation)[2]}")
                                st.markdown(f"*Idea:4* - {eval(st.session_state.final_ideation)[3]}")
                            st.success("Ideas generated successfully.")

                elif "human-idea-refining" in tool:
                    with st.spinner("Refining your ideas based on your feedback..."):
                        resp = requests.post(f"{API_URL}/human-idea-refining", json={"query": message})
                        if resp.ok:
                            refined = resp.json()['response']
                            st.session_state.human_interactions.append(refined)
                            st.markdown(st.session_state.human_interactions[-1])
                            st.success("Ideas refined.")

                elif "generate-story" in tool:
                    st.info("Redirecting to brainstorming page...")
                    switch_page("pages/brainstorm.py")

                elif "generate-ultimate-story" in tool:
                    with st.spinner("Generating your final story..."):
                        resp = requests.post(f"{API_URL}/generate-final-story")
                        if resp.ok:
                            st.session_state.final_story = resp.json()["response"]
                            st.markdown(st.session_state.final_story)
                            st.success("Final story generated.")

                elif "generate-image" in tool:
                    with st.spinner("Generating image based on your story..."):
                        resp = requests.post(f"{API_URL}/generate-image")
                        if resp.ok:
                            st.session_state.generated_image = resp.json()["response"]
                            st.image(f"data:image/png;base64,{st.session_state.generated_image}", use_column_width=True)
                            st.success("Image generated.")

                else:
                    st.markdown(f"\U0001F916 {message}")
                    if image_caption and "no any information" not in image_caption.lower():
                        st.markdown(f"\U0001F916 {image_caption}")
            else:
                st.error("Orchestration failed.")
