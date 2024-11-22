import streamlit as st
import pandas as pd
import random
from utils.MaxDiff import MaxDiffSurvey

st.set_page_config(
    page_title="MaxDiff Tutorial | Collecting responses",
    page_icon=":material/bar_chart:",
)

if "survey" not in st.session_state:
    st.session_state.survey = None
if "current_participant" not in st.session_state:
    st.session_state.current_participant = 1
if "previous_participant" not in st.session_state:
    st.session_state.previous_participant = 1
if "current_question" not in st.session_state:
    st.session_state.current_question = 1
if "randomly_generated" not in st.session_state:
    st.session_state.randomly_generated = False

st.title("Collecting responses")

if st.session_state.survey is None:
    st.info("Nothing to see here! You need to create a survey first.")
    st.page_link(
        "./pages/1_1_—_Setting_up_the_survey.py",
        label="**:blue-background[Go to step 1 — Creating the survey]**",
        icon="👉",
    )

if st.session_state.survey is not None:

    st.write(
        "Your survey is ready to collect responses. You can answer a few questions yourself, and then generate random responses to speed things up. Since this is a tutorial and not an actual survey tool (quite yet), you can't send a survey link to respondents at this point."
    )

    st.info(
        f"""
        **Your survey: {st.session_state.survey.survey_name}**  
        Planned respondents: {st.session_state.survey.n_participants}  
        Completed responses: {st.session_state.survey._responses['highest'].notna().sum() // st.session_state.survey.n_questions_per_participant}
        """,
        icon=":material/assignment:",
    )

    st.subheader("Take your survey")
    st.write(
        "Enter a few responses manually to get a sense of how a MaxDiff survey works."
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        participant = st.number_input(
            f"Participant ID (1 to {st.session_state.survey.n_participants})",
            value=st.session_state.current_participant,
            min_value=1,
            max_value=st.session_state.survey.n_participants,
        )
        st.session_state.current_participant = participant
        question = st.session_state.current_question

    if st.session_state.current_participant != st.session_state.previous_participant:
        st.session_state.current_question = 1
        st.session_state.previous_participant = st.session_state.current_participant
        st.rerun()

    question_items = st.session_state.survey._question_sets[participant][question - 1]

    with st.container(border=True):
        st.caption(
            f"{st.session_state.current_question} of {st.session_state.survey.n_questions_per_participant}"
        )
        st.markdown(
            f"""**{st.session_state.survey.question_text}**  
                 :grey[Choose the two respective items from the options below.]"""
        )

        # Display items and capture responses
        for i, item in enumerate(question_items):
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.markdown(f"{st.session_state.survey._items_dict[item]}")

            with col2:
                btn_selected = (
                    st.session_state.survey._responses.loc[
                        (participant, question), f"item_{i+1}"
                    ]
                    == st.session_state.survey._responses.loc[
                        (participant, question), "lowest"
                    ]
                )
                if st.button(
                    f"{st.session_state.survey.low_response_option}",
                    key=f"low_{i}",
                    type=f"{'primary' if btn_selected else 'secondary'}",
                ):
                    st.session_state.survey._responses.loc[
                        (participant, question), "lowest"
                    ] = item
                    st.rerun()

            with col3:
                btn_selected = (
                    st.session_state.survey._responses.loc[
                        (participant, question), f"item_{i+1}"
                    ]
                    == st.session_state.survey._responses.loc[
                        (participant, question), "highest"
                    ]
                )
                if st.button(
                    f"{st.session_state.survey.high_response_option}",
                    key=f"high_{i}",
                    type=f"{'primary' if btn_selected else 'secondary'}",
                ):
                    st.session_state.survey._responses.loc[
                        (participant, question), "highest"
                    ] = item
                    st.rerun()

        participant_completed_all_questions = (
            st.session_state.survey._responses.loc[participant, ["lowest", "highest"]]
            .notnull()
            .all()
            .all()
        )
        if participant_completed_all_questions:
            st.success(
                "All questions are answered for this participant.",
                icon=":material/check_circle:",
            )

        if (
            st.session_state.survey._responses.loc[(participant, question), "highest"]
            == st.session_state.survey._responses.loc[(participant, question), "lowest"]
            and st.session_state.survey._responses.loc[
                (participant, question), "highest"
            ]
            is not None
        ):
            st.error(
                f'You can\'t choose the same item as "{st.session_state.survey.high_response_option.lower()}" and "{st.session_state.survey.low_response_option.lower()}"!',
                icon=":material/error:",
            )
        col4, col5, col6 = st.columns([1, 1, 1])
        with col4:
            if st.button(
                "Previous question",
                type="secondary",
                disabled=st.session_state.current_question == 1,
                icon=":material/arrow_back_ios:",
            ):
                st.session_state.current_question -= 1
                st.rerun()

        with col5:
            if st.button(
                "Next question",
                type="secondary",
                disabled=question
                == st.session_state.survey.n_questions_per_participant,
                icon=":material/arrow_forward_ios:",
            ):
                st.session_state.current_question += 1
                st.rerun()

    st.subheader("Generate random responses")

    st.write("Speed things up by generating the remaining responses randomly.")

    if st.session_state.randomly_generated:
        st.success(
            f"You have randomly generated the remaining responses.",
            icon=":material/check_circle:",
        )
    else:
        if st.button(
            "Generate remaining responses randomly",
            type="primary",
            icon=":material/shuffle:",
        ):
            st.session_state.survey.generate_random_responses()
            st.session_state.randomly_generated = True
            st.rerun()

    all_responses_completed = (
        st.session_state.survey._responses.loc[:, ["lowest", "highest"]]
        .notnull()
        .all()
        .all()
    )
    if all_responses_completed:
        st.subheader("Move on to analysis")
        st.write(
            f"Now that you collected all {st.session_state.survey.n_participants} responses, move on to analyzing the data."
        )
        st.page_link(
            "./pages/3_3_—_Analzying_the_results.py",
            label="**:blue-background[Go to step 3 — Analyzing the results]**",
            icon="👉",
        )

    st.write("---")

    def delete_responses():
        st.session_state.survey.delete_all_responses()
        st.session_state.randomly_generated = False

    st.button(
        "Delete all responses",
        type="secondary",
        on_click=delete_responses,
        icon=":material/playlist_remove:",
    )
