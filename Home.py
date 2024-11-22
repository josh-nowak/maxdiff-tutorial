import streamlit as st

st.set_page_config(
    page_title="MaxDiff Tutorial | Home", page_icon=":material/bar_chart:"
)

st.title("MaxDiff Tutorial")
st.write(
    "Welcome! This is an interactive intro to MaxDiff surveys with a focus on the technical setup and analysis."
)

st.write(
    "There are three parts to this, which you can access from the sidebar or these links:"
)

st.page_link(
    "./pages/1_1_—_Setting_up_the_survey.py",
    label="**:blue-background[Step 1 — Setting up the survey]**",
    icon="🌱",
)
st.page_link(
    "./pages/2_2_—_Collecting_responses.py",
    label="**:blue-background[Step 2 — Collecting responses]**",
    icon="✍️",
)
st.page_link(
    "./pages/3_3_—_Analzying_the_results.py",
    label="**:blue-background[Step 3 — Analyzing the results]**",
    icon="📊",
)

st.write("---")

st.write(
    "If you're new to MaxDiff, find answers to common questions below to get started."
)

with st.expander("What are MaxDiff surveys?"):
    st.write(
        "Maximum Difference Scaling (MaxDiff) is a survey method that helps you understand people's preferences within a given set of items. Instead of asking survey respondents to rank a long list of items, MaxDiff presents small sets of options and asks people to choose only the **most and least preferred** in each set. This approach yields more reliable preference data and can be easier for participants to complete."
    )

with st.expander("When can MaxDiff surveys be used?"):
    st.markdown(
        """MaxDiff surveys can be considered for many common objectives in market and user research, where a set of items or aspects need to prioritized. You can investigate anything from user needs to product features, satisfaction or motivation drivers, value propositions, and more."""
    )

with st.expander("How do MaxDiff questions work?"):
    st.markdown(
        """
This should get clearer throughout the tutorial, but here's a heads-up:

In a MaxDiff survey, participants see a series of questions where each presents 4-5 items from the total set of items to be prioritized. For each question:

1. Participants select the item they find **most** important or preferrable
2. They then select the item they find **least** important or preferrable

Each question includes a different combinations of items. You can then calculate relative preference scores for all items. 

For example, if studying 20 phone features, a single question might show 4 of them:

* Camera quality
* Battery life
* Screen size
* Storage capacity

The participant picks their most and least important features from this set."""
    )

st.write("---")

st.write(
    "Find the code for this app on [github.com/josh-nowak/maxdiff-tutorial](https://github.com/josh-nowak/maxdiff-tutorial)."
)
st.write("Please share bugs and other feedback at hi@jonowak.eu")
