import streamlit as st
import plotly.graph_objects as go
import pandas as pd


st.set_page_config(
    page_title="MaxDiff Tutorial | Analyzing the results",
    page_icon=":material/bar_chart:",
)

if "survey" not in st.session_state:
    st.session_state.survey = None

st.title("Analyzing the results")

if st.session_state.survey is None:
    st.info("Nothing to see here! You need to create a survey first.")
    st.page_link(
        "./pages/1_1_—_Setting_up_the_survey.py",
        label="**:blue-background[Go to step 1 — Setting up the survey]**",
        icon="👉",
    )
elif st.session_state.survey._responses["highest"].notna().sum() == 0:
    st.info("No responses yet! Please enter some responses or generate them randomly.")
    st.page_link(
        "./pages/2_2_—_Collecting_responses.py",
        label="**:blue-background[Go to step 2 — Collecting responses]**",
        icon="👉",
    )

elif st.session_state.survey._responses["highest"].notna().sum() > 0:
    st.write("Your survey has responses! Let's analyze them.")
    with st.expander("View responses"):
        st.write(st.session_state.survey._responses)

    st.subheader("1. Absolute counts and net value")
    item_counts = st.session_state.survey.get_item_counts()
    st.write(
        'For a first look at the preferences, we can plot the amount of times that each item was chosen as the highest vs. the lowest option. We can then subtract the two values (sum of highest - sum of lowest) to get a "net value" per item. If you generated most responses randomly, you won\'t see much of a difference between items — but you get the idea!'
    )
    st.write(
        "The main problem here is that this simple analysis does not consider the context in which the individual items were considered by the respondents (i.e., the alternative items shown in the question)."
    )

    item_counts_fig = st.session_state.survey.plot_item_counts()
    # Display the plot
    st.plotly_chart(item_counts_fig)

    st.subheader("2. Multinomial logit model & utilities")
    st.write(
        "Using a multinomial logit model, we can estimate the **utilities** of the items. These utilities represent the relative preferences for each item — in other words: the estimated probability of choosing a particular item over others in a set."
    )
    with st.expander("See details"):
        st.write(
            "The [multinomial logit model](https://en.wikipedia.org/wiki/Multinomial_logistic_regression) is a generalized form of logistic regression where the outcome variable has more than two discrete outcomes. This is needed for MaxDiff surveys because we are typically looking at choices among a set of 4–5 items."
        )
        st.markdown(
            "The model's **predictors** (independent variables) are the items presented in each question."
        )
        st.markdown(
            "The **dependent variable** is the item that the participant selected as their most preferred option."
        )
        st.markdown(
            'The model also uses a **grouping variable** to account for the specific question in which the choice was made (i.e., the "choice context"). This makes it a **conditional** logit model.'
        )
        st.markdown(
            r"""
The probability $P_i$ of choosing item $i$ is determined by its utility relative to all other items in the choice set, as reflected by the following formula:

$$
P_i = \frac{e^{U_i}}{\sum_j e^{U_j}}
$$  
  

Where:
- $U_i$ is the **utility** of item $i$,
- $j$ indexes all the items in the choice set (e.g., the set of 4–5 items),
- $e^{U_j}$ is the exponentiation of the utility of each item.
"""
        )
        st.markdown(
            "Note: Although the **least preferred option** is also captured in MaxDiff surveys, it does not seem to be included when estimating utilities."
        )

    if st.session_state.survey._multinomial_logit_model is None:
        with st.spinner("Running multinomial logit model..."):
            st.session_state.survey.run_multinomial_logit()
    item_utilities_fig = st.session_state.survey.plot_item_utilities()
    st.plotly_chart(item_utilities_fig)

    st.subheader("")

st.write("---")

st.write("That's all there is to this tutorial so far! Thanks for stopping by.")
st.write(
    "If you have any feedback, please reach out: [hi@jonowak.eu](mailto:hi@jonowak.eu)"
)
