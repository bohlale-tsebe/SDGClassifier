from matplotlib import pyplot as plt
from matplotlib_venn import venn3
from matplotlib_venn import venn3_unweighted
import requests
import streamlit as st
import pandas as pd
import json


if "yearly_report" not in st.session_state:
    st.session_state.yearly_report = {}  # {year: DataFrame}

def classify_text(text):
    url = "https://aurora-sdg.labs.vu.nl/classifier/classify/elsevier-sdg-multi"
    payload = json.dumps({"text": text})
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=payload)
    return response.json()

def display_sdg_grid(sdg_group, title):
    st.subheader(title)
    cols = st.columns(4)  # Adjust number of columns as needed
    for i, sdg in enumerate(sdg_group):
        with cols[i % 4]:
            st.image(sdg["icon"], width=80)
            st.caption(f"{sdg['code']}: {sdg['name']}")

st.title("SDG Classifier")

sdg_list = [
{"code": "1", "name": "No poverty", "icon": "https://www.un.org/sustainabledevelopment/wp-content/uploads/2019/08/E-Goal-01-1024x1024.png"},
{"code": "2", "name": "Zero hunger", "icon": "https://www.un.org/sustainabledevelopment/wp-content/uploads/2019/08/E-Goal-02-1024x1024.png"},
{"code": "3", "name": "Good health and well-being", "icon": "https://www.un.org/sustainabledevelopment/wp-content/uploads/2019/08/E-Goal-03-1024x1024.png"},
{"code": "4", "name": "Quality education", "icon": "https://www.un.org/sustainabledevelopment/wp-content/uploads/2019/08/E-Goal-04-1024x1024.png"},
{"code": "5", "name": "Gender equality", "icon": "https://www.un.org/sustainabledevelopment/wp-content/uploads/2019/08/E-Goal-05-1024x1024.png"},
{"code": "6", "name": "Clean water and sanitation", "icon": "https://www.un.org/sustainabledevelopment/wp-content/uploads/2019/08/E-Goal-06-1024x1024.png"},
{"code": "7", "name": "Affordable and clean energy", "icon": "https://www.un.org/sustainabledevelopment/wp-content/uploads/2019/08/E-Goal-07-1024x1024.png"},
{"code": "8", "name": "Decent work and economic growth", "icon": "https://www.un.org/sustainabledevelopment/wp-content/uploads/2019/08/E-Goal-08-1024x1024.png"},
{"code": "9", "name": "Industry, innovation and infrastructure", "icon": "https://www.un.org/sustainabledevelopment/wp-content/uploads/2019/08/E-Goal-09-1024x1024.png"},
{"code": "10", "name": "Reduced inequalities", "icon": "https://www.un.org/sustainabledevelopment/wp-content/uploads/2019/08/E-Goal-10-1024x1024.png"},
{"code": "11", "name": "Sustainable cities and communities", "icon": "https://www.un.org/sustainabledevelopment/wp-content/uploads/2019/08/E-Goal-11-1024x1024.png"},
{"code": "12", "name": "Responsible consumption and production", "icon": "https://www.un.org/sustainabledevelopment/wp-content/uploads/2019/08/E-Goal-12-1024x1024.png"},
{"code": "13", "name": "Climate action", "icon": "https://www.un.org/sustainabledevelopment/wp-content/uploads/2019/08/E-Goal-13-1024x1024.png"},
{"code": "14", "name": "Life below water (Not Relevant)", "icon": "https://www.un.org/sustainabledevelopment/wp-content/uploads/2019/08/E-Goal-14-1024x1024.png"},
{"code": "15", "name": "Life on land", "icon": "https://www.un.org/sustainabledevelopment/wp-content/uploads/2019/08/E-Goal-15-1024x1024.png"},
{"code": "16", "name": "Peace, justice and strong institutions (Not Relevant)", "icon": "https://www.un.org/sustainabledevelopment/wp-content/uploads/2019/08/E-Goal-16-1024x1024.png"},
{"code": "17", "name": "Partnerships for the goals", "icon": "https://www.un.org/sustainabledevelopment/wp-content/uploads/2019/08/E-Goal-17-1024x1024.png"}
]

env_sdgs = {"13","14","15","17","7","12","11","6"}
soc_sdgs = {"1","5","4","8","10","17","2","3","16","11","6"}
ecn_sdgs = {"9","1","5","4","8","10","17","7","12"}

year = st.selectbox("Select The Year Of The Report You Are Uploading", list(range(2022, 2026)))
uploaded_file = st.file_uploader("Upload your report (TXT)", type=["txt"])
if uploaded_file:
    lines = uploaded_file.read().decode("utf-8").splitlines()
    summary = []
    achieved_sdgs = []
    for line in lines:
        if line.strip():
            result = classify_text(line)
            predictions = result.get("predictions", [])
            if predictions:
                top = max(predictions, key=lambda p: p["prediction"])
                achieved_sdgs.append(top["sdg"]["code"])
                summary.append({
                    "Text": line.strip(),
                    "SDG Code": top["sdg"]["code"],
                    "SDG Name": top["sdg"]["name"],
                })
    
    dfs = pd.DataFrame(summary)

    st.session_state.yearly_report[year] = dfs

selected_year = st.selectbox("View data for year", sorted(st.session_state.yearly_report.keys()))

if selected_year in st.session_state.yearly_report:
    df = st.session_state.yearly_report[selected_year]
    st.subheader(f"Top SDG Match per Line — {selected_year}")
    st.dataframe(df)
    
    matched_sdgs = df["SDG Name"].unique().tolist()
    accomplished_sdgs = [sdg for sdg in sdg_list if sdg["name"] in matched_sdgs]
    outstanding_sdgs = [sdg for sdg in sdg_list if sdg["name"] not in matched_sdgs]


    display_sdg_grid(accomplished_sdgs, "✅ Accomplished SDGs")

    achieved_sdgs = set(achieved_sdgs)

    econ_achieved = ecn_sdgs & achieved_sdgs
    env_achieved = env_sdgs & achieved_sdgs
    soc_achieved = soc_sdgs & achieved_sdgs

    fig = plt.figure()
    venn3_unweighted(
        subsets=(econ_achieved, env_achieved, soc_achieved),
        set_labels=('Economic', 'Environmental', 'Social')
    )
    plt.title("Achieved SDGs by Sustainability Dimension")
    
    st.pyplot(fig)

    display_sdg_grid(outstanding_sdgs, "🚧 Outstanding SDGs")








