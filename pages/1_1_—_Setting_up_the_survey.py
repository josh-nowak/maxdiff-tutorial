import streamlit as st
from utils.MaxDiff import MaxDiffSurvey
import math

st.set_page_config(
    page_title="MaxDiff Tutorial | Setting up the Survey",
    page_icon=":material/bar_chart:",
)

st.title("Setting up the survey")

# Initialize session state variables
if "survey" not in st.session_state:
    st.session_state.survey = None
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 0
if "survey_name" not in st.session_state:
    st.session_state.survey_name = "Product feature prioritization"
if "items_to_compare" not in st.session_state:
    st.session_state.items_to_compare = ""  # because "items" is taken
if "question_phrasing" not in st.session_state:
    st.session_state.question_phrasing = {
        "question_text": "Which of these are most and least important for you?",
        "low_response_option": "Least important",
        "high_response_option": "Most important",
    }
if "n_items_total" not in st.session_state:
    st.session_state.n_items_total = None
if "n_items_per_question" not in st.session_state:
    st.session_state.n_items_per_question = None
if "n_questions_per_participant" not in st.session_state:
    st.session_state.n_questions_per_participant = None
if "n_participants" not in st.session_state:
    st.session_state.n_participants = None
if "seed" not in st.session_state:
    st.session_state.seed = None
if "input_error" not in st.session_state:
    st.session_state.input_error = None


@st.cache_data
def load_demo_items():
    with open("./utils/demo_items.txt", "r") as f:
        return f.read().splitlines()


if st.session_state.wizard_step > 0 and st.session_state.wizard_step <= 7:
    st.markdown(f"**:grey[Step {st.session_state.wizard_step} of 7]**")

if st.session_state.wizard_step == 0 and st.session_state.survey is None:
    st.write(
        "Set up a brand new survey by defining the items to be compared and a few key parameters."
    )
    if st.button("Set up a survey", type="primary", icon=":material/assignment:"):
        st.session_state.wizard_step = 1
        st.rerun()

    st.write("")
    st.write("If you'd like to skip this, load the demo survey below.")
    if st.button("Load demo survey", type="secondary"):
        with open("./utils/demo_items.txt", "r") as f:
            items = f.read().splitlines()
        st.session_state.survey = MaxDiffSurvey(
            items=items,
            n_items_per_question=5,
            n_questions_per_participant=20,
            n_participants=100,
            survey_name="Hiking app feature prioritization",
            question_text="Which of these features are most and least important for you in our hiking app?",
            low_response_option="Least important",
            high_response_option="Most important",
        )
        st.session_state.wizard_step = 100
        st.rerun()

if st.session_state.wizard_step == 1:
    st.header("What should the survey be called?")
    survey_name = st.text_input(
        "Survey name",
        value=st.session_state.survey_name,
    )

    if st.session_state.input_error:
        st.error(st.session_state.input_error)

    if st.button("Next", type="primary"):
        if survey_name == "":
            st.session_state.input_error = "Please enter a survey name."
            st.rerun()
        else:
            st.session_state.survey_name = survey_name
            st.session_state.input_error = None
            st.session_state.wizard_step += 1
            st.rerun()

    if st.button("Back", type="secondary"):
        st.session_state.input_error = None
        st.session_state.wizard_step -= 1
        st.rerun()

if st.session_state.wizard_step == 2:
    st.header("How should your survey question and response options be phrased?")
    question_text = st.text_input(
        "Question",
        value=st.session_state.question_phrasing["question_text"],
    )
    col1, col2 = st.columns(2)
    with col1:
        low_response_option = st.text_input(
            "Low response option",
            value=st.session_state.question_phrasing["low_response_option"],
        )
    with col2:
        high_response_option = st.text_input(
            "High response option",
            value=st.session_state.question_phrasing["high_response_option"],
        )

    if st.session_state.input_error:
        st.error(st.session_state.input_error)

    if st.button("Next", type="primary"):
        if (
            question_text == ""
            or low_response_option == ""
            or high_response_option == ""
        ):
            st.session_state.input_error = (
                "Please enter a question and both response options."
            )
            st.rerun()
        else:
            st.session_state.question_phrasing = {
                "question_text": question_text,
                "low_response_option": low_response_option,
                "high_response_option": high_response_option,
            }
            st.session_state.input_error = None
            st.session_state.wizard_step += 1
            st.rerun()

    if st.button("Back", type="secondary"):
        st.session_state.input_error = None
        st.session_state.wizard_step -= 1
        st.rerun()


if st.session_state.wizard_step == 3:
    st.header("Which items do you want participants to compare?")
    st.write(
        "Add between 6 and 30 items that participants should compare (e.g., product features, user needs)."
    )
    items = st.text_area(
        "Items (one per line)",
        placeholder="Live tracking\nOffline mode\nEnd-to-end encryption\nDark theme\n...",
        value="\n".join(st.session_state.items_to_compare),
        height=150,
    )

    if st.session_state.input_error:
        st.error(st.session_state.input_error)

    if st.button("Add example items", type="secondary"):
        items = load_demo_items()
        st.session_state.items_to_compare = items
        st.session_state.input_error = None
        st.rerun()

    if st.button("Next", type="primary"):
        st.session_state.items_to_compare = [
            item.strip() for item in items.split("\n") if item.strip()
        ]
        if len(st.session_state.items_to_compare) < 6:
            st.session_state.input_error = (
                "Please enter at least 6 items, one per line."
            )
            st.rerun()
        elif len(st.session_state.items_to_compare) > 30:
            st.session_state.input_error = "Please enter at most 30 items."
            st.rerun()
        else:
            st.session_state.n_items_total = len(st.session_state.items_to_compare)
            st.session_state.input_error = None
            st.session_state.wizard_step += 1
            st.rerun()

    if st.button("Back", type="secondary"):
        st.session_state.input_error = None
        st.session_state.wizard_step -= 1
        st.rerun()


if st.session_state.wizard_step == 4:
    st.header("How many items do you want participants to compare in each question?")

    if st.session_state.n_items_total < 12:
        recommended_n_items_per_question = math.floor(
            st.session_state.n_items_total / 2
        )
    else:
        recommended_n_items_per_question = 5

    st.write(
        "Select between 3 and 6 items per question. Participants will choose their most and least preferred item in each question."
    )

    if st.session_state.n_items_total <= 12:
        st.info(
            f"**Since you have only {st.session_state.n_items_total} items in total, it's recommended to set this to {recommended_n_items_per_question}.** It's best not to show more than half of the total number of items per question."
        )

    n_items_per_question = st.number_input(
        "Number of items per question",
        value=recommended_n_items_per_question,
        min_value=3,
        max_value=6,
    )

    if st.session_state.input_error:
        st.error(st.session_state.input_error)

    if st.button("Next", type="primary"):
        if n_items_per_question < 3 or n_items_per_question > 6:
            st.session_state.input_error = "Please enter a number between 3 and 6."
            st.rerun()
        else:
            st.session_state.n_items_per_question = n_items_per_question
            st.session_state.input_error = None
            st.session_state.wizard_step += 1
            st.rerun()

    if st.button("Back", type="secondary"):
        st.session_state.input_error = None
        st.session_state.wizard_step -= 1
        st.rerun()

if st.session_state.wizard_step == 5:
    st.header("How many questions do you want each participant to answer in total?")

    min_recommended_n_questions_per_participant = 3 * math.ceil(
        st.session_state.n_items_total / st.session_state.n_items_per_question
    )
    max_recommended_n_questions_per_participant = 5 * math.ceil(
        st.session_state.n_items_total / st.session_state.n_items_per_question
    )
    n_questions_per_participant_default_value = math.ceil(
        (
            min_recommended_n_questions_per_participant
            + max_recommended_n_questions_per_participant
        )
        / 2
    )
    st.write(
        f"For your survey with {st.session_state.n_items_total} items in total and {st.session_state.n_items_per_question} items per question, it's recommended to have **between {min_recommended_n_questions_per_participant} and {max_recommended_n_questions_per_participant} questions per participant**. That's because we want each item to appear in about 3 to 5 questions on average."
    )

    n_questions_per_participant = st.number_input(
        "Number of questions per participant",
        value=n_questions_per_participant_default_value,
        min_value=1,
        max_value=100,
    )
    with st.expander("Source"):
        st.markdown(
            'This is based on [Sawtooth Software\'s recommendation](https://sawtoothsoftware.com/resources/maxdiff-calculator) that the number of questions should be "_from $3K/k$ to $5K/k$, where $K$ is the total number of items and $k$ is the number of items shown per set_".'
        )

    if st.button("Next", type="primary"):
        st.session_state.n_questions_per_participant = n_questions_per_participant
        st.session_state.wizard_step += 1
        st.rerun()

    if st.button("Back", type="secondary"):
        st.session_state.input_error = None
        st.session_state.wizard_step -= 1
        st.rerun()

if st.session_state.wizard_step == 6:
    st.header("How many participants do you expect to have at most?")
    st.write(
        "For each participant, a randomized question set will be generated. **When in doubt, choose a larger number here.** You can discard unused question sets later."
    )
    n_participants = st.number_input(
        "Number of participants",
        value=100,
        min_value=1,
        max_value=10000,
    )

    if st.session_state.input_error:
        st.error(st.session_state.input_error)

    if st.button("Next", type="primary"):
        if n_participants < 1 or n_participants > 10000:
            st.session_state.input_error = "Please enter a number between 1 and 10000."
            st.rerun()
        else:
            st.session_state.n_participants = n_participants
            st.session_state.input_error = None
            st.session_state.wizard_step += 1
            st.rerun()

    if st.button("Back", type="secondary"):
        st.session_state.input_error = None
        st.session_state.wizard_step -= 1
        st.rerun()

if st.session_state.wizard_step == 7:
    st.header("What is your lucky number?")
    st.write(
        "For reproducibility, you can **set the seed number for random number generation**. This is useful if you want to be able to reproduce the same randomized question sets later."
    )
    st.write("Feel free to leave this as is.")
    seed = st.number_input("Seed", value=42, min_value=0, max_value=1000000)

    if st.session_state.input_error:
        st.error(st.session_state.input_error)

    if st.button("Finish and create survey", type="primary"):
        if seed < 0 or seed > 1000000:
            st.session_state.input_error = (
                "Please enter a number between 0 and 1000000."
            )
            st.rerun()
        else:
            st.session_state.seed = seed
            st.session_state.survey = MaxDiffSurvey(
                items=st.session_state.items_to_compare,
                n_items_per_question=st.session_state.n_items_per_question,
                n_questions_per_participant=st.session_state.n_questions_per_participant,
                n_participants=st.session_state.n_participants,
                seed=st.session_state.seed,
                survey_name=st.session_state.survey_name,
                question_text=st.session_state.question_phrasing["question_text"],
                low_response_option=st.session_state.question_phrasing[
                    "low_response_option"
                ],
                high_response_option=st.session_state.question_phrasing[
                    "high_response_option"
                ],
            )
            st.session_state.wizard_step = 100
            st.session_state.input_error = None
            st.rerun()

    if st.button("Back", type="secondary"):
        st.session_state.input_error = None
        st.session_state.wizard_step -= 1
        st.rerun()

if st.session_state.wizard_step == 100 or st.session_state.survey is not None:
    st.success(
        "You successfully set up your survey. Find an overview below.",
        icon=":material/check_circle:",
    )
    st.subheader(f'Survey overview: "{st.session_state.survey.survey_name}"')

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(
            "<span style='margin-top: 0; font-size: 1.2em; font-weight: 600;'>Question phrasing</span>",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f'''"_{st.session_state.survey.question_text}_"  
             Options: "_{st.session_state.survey.low_response_option}_" and "_{st.session_state.survey.high_response_option}_"'''
        )

    st.write("")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(
            "<span style='margin-top: 0; font-size: 1.2em; font-weight: 600;'>Survey parameters</span>",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
- **{len(st.session_state.survey.items)}** items to compare in total  
- **{st.session_state.survey.n_items_per_question}** items per question  
- **{st.session_state.survey.n_questions_per_participant}** questions per participant  
- **{st.session_state.survey.n_participants}** participants"""
        )

    st.write("")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(
            "<span style='margin-top: 0; font-size: 1.2em; font-weight: 600;'>Items to compare</span>",
            unsafe_allow_html=True,
        )

    with col2:
        formatted_items = "\n".join(
            [f"- {item}" for item in st.session_state.survey.items]
        )
        st.markdown(
            f"""
{formatted_items}
"""
        )

    st.subheader("How is the survey generated?")
    st.write(
        f"Each respondent will receive a different set of {st.session_state.survey.n_questions_per_participant} questions, in which they are asked to pick their most and least preferred option. Each question contains {st.session_state.survey.n_items_per_question} randomly selected items from the list of {len(st.session_state.survey.items)} items. In the randomization process, it's ensured that each possible pair of items appears in at least one question for each respondent."
    )
    st.write(
        f"The dataset was already initialized (without responses), so you can get a sense of the randomization below. The columns `item1`, `item2`, etc. determine the items shown to a respondent in a given question. In your case, there are {st.session_state.survey.n_items_per_question} of these `item` columns, because there are {st.session_state.survey.n_items_per_question} items per question. The respondent's choices will be captured in the columns `lowest` and `highest`."
    )
    st.write(st.session_state.survey._responses)

    st.write(
        "Head over to the next section to see what the survey looks like for respondents."
    )
    st.page_link(
        "./pages/2_2_—_Collecting_responses.py",
        label="**:blue-background[Go to step 2 — Collecting responses]**",
        icon="👉",
    )
    st.write("")

    def clear_session_state():
        for key in st.session_state.keys():
            del st.session_state[key]

    st.button(
        "Delete survey and start over",
        type="secondary",
        on_click=clear_session_state,
        icon=":material/delete:",
    )
