# Xplored
# An app to keep track of all countries ever visited, with user profiles and saving.
# To run: streamlit run Xplored_app_prod.py


import pandas as pd
import pycountry as pc
import streamlit as st
import plotly.express as px
import json
import os
import pipreqs

#pipreqs '/Users/petraszabolcsi/PycharmProjects/PythonProject'
pip freeze
#Username database
DATA_FILE = "users_data.json"

# Initialize session variables
if "user" not in st.session_state:
    st.session_state.user = None
if "xplored" not in st.session_state:
    st.session_state.xplored = []


# Set background image using CSS
def set_background(image_url):
    page_bg = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("{image_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    [data-testid="stSidebar"] {{
        background-color: rgba(255, 255, 255, 0.8);
    }}
    [data-testid="stHeader"] {{
        background: rgba(255, 255, 255, 0.5);
    }}
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)


if st.session_state.user is None:
    set_background("https://images.unsplash.com/photo-1506744038136-46273834b3fb")
else:
    set_background("https://images.unsplash.com/photo-1506744038136-46273834b3fb")

#Using my pic: set_background("background.jpg")


# Load or initialize user data
def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {}


def save_user_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# Load existing users
user_data = load_user_data()
existing_users = list(user_data.keys())


# --- Page 1: User selection / creation ---
if st.session_state.user is None:
    st.title("🌍 Xplored — Track Your Travels")

    st.write("Select your user profile or create a new one below.")

    col1, col2 = st.columns(2)
    with col2:
        selected_user = st.selectbox("Select existing user", [""] + existing_users)
        if selected_user:
            if st.button("Login"):
                st.session_state.user = selected_user
                st.session_state.xplored = user_data.get(selected_user, [])
                st.rerun()

    with col1:
        new_user = st.text_input("Create new user")
        if new_user:
            if new_user in existing_users:
                st.warning("This username already exists. Choose another one.")
            else:
                if st.button("Create"):
                    st.session_state.user = new_user
                    st.session_state.xplored = []
                    user_data[new_user] = []
                    save_user_data(user_data)
                    st.success(f"User '{new_user}' created successfully!")
                    st.rerun()

else:
    # --- Page 2: Main app for selected user ---
    st.sidebar.title(f"👤 {st.session_state.user}'s Explorer")

    countries = sorted([country.name for country in pc.countries])
    with st.sidebar:
        selected = st.selectbox("Countries", countries)
        add_item = st.button("Add")
        show_map = st.button("Show on map")


    # Add button
    if add_item:
        if selected not in st.session_state.xplored:
            st.session_state.xplored.append(selected)



    # Show current list
    with st.sidebar:
        st.write("Visited countries:")

        if st.session_state.xplored:
            df = pd.DataFrame(st.session_state.xplored, columns=["Country"])
            df["Remove"] = False

            edited_df = st.data_editor(df, key="editable_table", hide_index=True)

            to_remove = edited_df[edited_df["Remove"]].Country.tolist()
            if to_remove:
                if st.button("Remove Selected"):
                    st.session_state.xplored = [c for c in st.session_state.xplored if c not in to_remove]
                    st.rerun()
        else:
            st.info("No countries selected yet.")

        country_count = len(st.session_state.xplored)
        st.write("Countries explored:",country_count)

        save_btn = st.button("💾 Save progress")
        logout = st.button("🚪 Logout")

        # Save button
        if save_btn:
            user_data[st.session_state.user] = st.session_state.xplored
            save_user_data(user_data)
            st.success("Progress saved!")

        # Logout
        if logout:
            st.session_state.user = None
            st.session_state.xplored = []
            st.rerun()

    # Map display
    df_map = {
        "country": st.session_state["xplored"],
        "visited": [1] * len(st.session_state["xplored"]),
    }

    if show_map or st.session_state.xplored:
        if st.session_state.xplored:
            fig = px.choropleth(
                df_map,
                locations="country",
                locationmode="country names",
                color="visited",
                color_continuous_scale=[[0, "lightgray"], [1, "green"]],
                range_color=(0, 1),
                title=f"🌎 {st.session_state.user}'s Visited Countries",
            )

            fig.update_layout(
                geo=dict(showframe=False, showcoastlines=True),
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please add at least one country before showing the map.")
