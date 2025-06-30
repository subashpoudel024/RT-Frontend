import streamlit as st
import requests
import base64
from streamlit import switch_page

API_URL = "https://subashdvorak-brainstroming-fast-api.hf.space"  # Replace with your FastAPI URL

st.set_page_config(page_title="AI Business Ideation Platform", layout="wide")
st.header("Welcome to RT-GENAI")

# Initialize session state
session_defaults = {
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
for key, val in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Step 1: Context Analysis or Orchestration
st.subheader("How can I help you?")
msg = st.text_input("")


uploaded_files = st.file_uploader("📂 Upload reference images (optional)", type=['png', 'jpg', 'jpeg'], key="initial_image_uploader")

if uploaded_files:
    base64_images = []
    for file in uploaded_files:
        base64_images.append(base64.b64encode(file.read()).decode('utf-8'))
    st.session_state.base64_images = base64_images
    print('Base 64 image:',base64_images)

else:
    print('File not uploaded')


if st.button("Submit"):
    if not st.session_state.details_completed:
    # if st.session_state.details_completed == True:
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
        resp = requests.post(f"{API_URL}/orchestration", json={"message": msg,"image_base64": st.session_state.base64_images})
        if resp.ok:
            response = resp.json()
            tool = response.get("tool_response")
            message = response.get("message_response")
            image_caption = response.get("image_caption")
            st.write('Tool response:', tool)

            # ========== Tool Handling ==========
            if "ideation" in tool:
                resp = requests.post(f"{API_URL}/ideation")
                if resp.ok:
                    st.session_state.final_ideation = resp.json()["response"]["improver_response"][-1]

                    if len(st.session_state.final_ideation)>0:
                        # st.subheader("Final Ideations")
                        st.markdown(f"*Idea:1* - {eval(st.session_state.final_ideation)[0]}")
                        st.markdown(f"*Idea:2* - {eval(st.session_state.final_ideation)[1]}")
                        st.markdown(f"*Idea:3* - {eval(st.session_state.final_ideation)[2]}")
                        st.markdown(f"*Idea:4* - {eval(st.session_state.final_ideation)[3]}")
                    st.success("Ideas generated successfully.")

            elif "human-idea-refining" in tool:
                resp = requests.post(f"{API_URL}/human-idea-refining", json={"query": message})
                if resp.ok:
                    refined = resp.json()['response']
                    st.session_state.human_interactions.append(refined)
                    st.markdown(st.session_state.human_interactions[-1])
                    st.success("Ideas refined.")

            elif "generate-story" in tool:
                switch_page("pages/brainstorm.py")
                # def call_brainstorming_api():
                #     response = requests.post(
                #         f"{API_URL}/brainstorm",
                #         params={"thread_id": "my-session"},
                #         json={
                #             "preferred_topics": st.session_state.topics_to_pass,
                #             "image_base64_list": st.session_state.base64_images
                #         }
                #     )
                #     if response.ok:
                #         result_json = response.json()
                #         data = result_json.get("response", {})
                #         st.session_state.story = data.get("stories", [""])[-1]
                #         st.session_state.brainstorming_topics = data.get("brainstroming_topics", [])
                #     else:
                #         st.error("❌ API call failed.")
                #         st.write(response.text)

                # call_brainstorming_api()

                # uploaded_files = st.file_uploader("📂 Upload reference images (optional)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, key="brainstorm_image_uploader")
                # if uploaded_files:
                #     base64_images = [base64.b64encode(f.read()).decode('utf-8') for f in uploaded_files]
                #     st.session_state.base64_images = base64_images



                # # Triggered Brainstorming
                # if st.session_state.trigger_brainstorm:
                #     st.session_state.trigger_brainstorm = False  # reset flag
                #     # Save history
                #     if st.session_state.history_index < len(st.session_state.history) - 1:
                #         st.session_state.history = st.session_state.history[:st.session_state.history_index + 1]
                #     st.session_state.history.append({
                #         "selected_topics": st.session_state.selected_topics.copy(),
                #         "selected_from_brainstorm": st.session_state.selected_from_brainstorm.copy(),
                #         "story": st.session_state.story,
                #         "brainstorming_topics": st.session_state.brainstorming_topics.copy()
                #     })
                #     st.session_state.history_index += 1

                #     # Update selection
                #     st.session_state.selected_topics.extend(st.session_state.selected_from_brainstorm)
                #     st.session_state.selected_from_brainstorm = []

                #     st.rerun()

                # col1, col2 = st.columns(2)
                # with col1:
                #     st.subheader("📖 Story")
                #     st.text_area("Generated Story", st.session_state.story, height=300)

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
                #     else:
                #         st.info("No brainstorming topics yet. Click 'Brainstorm' to start.")

                # if st.button("🚀 Brainstorm"):
                #     st.session_state.trigger_brainstorm = True
                #     st.rerun()

                # if st.button("🔙 Back"):
                #     if st.session_state.history_index > 0:
                #         st.session_state.history_index -= 1
                #         state = st.session_state.history[st.session_state.history_index]
                #         st.session_state.selected_topics = state["selected_topics"]
                #         st.session_state.selected_from_brainstorm = state["selected_from_brainstorm"]
                #         st.session_state.story = state["story"]
                #         st.session_state.brainstorming_topics = state["brainstorming_topics"]
                #         st.rerun()
                #     else:
                #         st.warning("You're at the first step.")

                # if st.button("🔜 Forward"):
                #     if st.session_state.history_index < len(st.session_state.history) - 1:
                #         st.session_state.history_index += 1
                #         state = st.session_state.history[st.session_state.history_index]
                #         st.session_state.selected_topics = state["selected_topics"]
                #         st.session_state.selected_from_brainstorm = state["selected_from_brainstorm"]
                #         st.session_state.story = state["story"]
                #         st.session_state.brainstorming_topics = state["brainstorming_topics"]
                #         st.rerun()
                #     else:
                #         st.warning("You're at the most recent step.")

            elif "generate-ultimate-story" in tool:
                resp = requests.post(f"{API_URL}/generate-final-story")
                if resp.ok:
                    st.session_state.final_story = resp.json()["response"]
                    st.markdown(st.session_state.final_story)
                    st.success("Final story generated.")

            elif "generate-image" in tool:
                resp = requests.post(f"{API_URL}/generate-image")
                if resp.ok:
                    st.session_state.generated_image = resp.json()["response"]
                    st.image(f"data:image/png;base64,{st.session_state.generated_image}", use_column_width=True)
                    st.success("Image generated.")

            else:
                st.markdown(f"🤖 {message}")
                if "no any information" not in image_caption.lower():
                    st.markdown(f"🤖 {image_caption}")
        else:
            st.error("Orchestration failed.")