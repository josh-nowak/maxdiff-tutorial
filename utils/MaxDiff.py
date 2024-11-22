import random
import itertools
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.discrete.conditional_models import ConditionalLogit


class MaxDiffSurvey:
    def __init__(
        self,
        items: list[str],
        n_items_per_question: int = 4,
        n_questions_per_participant: int = 10,
        n_participants: int = 1,
        survey_name: str = "",
        question_text: str = "Which of these are most and least important for you?",
        low_response_option: str = "Least important",
        high_response_option: str = "Most important",
        seed: int = 42,
    ):
        # Survey parameters
        self.items = items
        self.n_items_per_question = n_items_per_question
        self.n_questions_per_participant = n_questions_per_participant
        self.n_participants = n_participants
        self.survey_name = survey_name
        self.question_text = question_text
        self.low_response_option = low_response_option
        self.high_response_option = high_response_option
        self.seed = seed

        # Internal state
        self._items_dict = {i + 1: item for i, item in enumerate(items)}
        self._participant_ids = [i + 1 for i in range(n_participants)]
        self._question_sets = self._generate_all_sets()
        self._responses = self._initialize_responses()
        self._multinomial_logit_model = None

    # Generate the question sets for a single participant
    def _generate_sets_for_participant(self, participant_id: int) -> list[list[int]]:
        random.seed(self.seed + participant_id)
        sets = []
        item_counts = {item: 0 for item in self._items_dict.keys()}

        # Define a target number of appearances for each item
        target_appearances = (
            self.n_questions_per_participant
            * self.n_items_per_question
            // len(self.items)
        )

        # Generate each question set
        for _ in range(self.n_questions_per_participant):

            # Available items are those that haven't reached the target number of appearances yet
            available_items = [
                item
                for item in self._items_dict.keys()
                if item_counts[item] < target_appearances
            ]

            # If there are not enough available items to fill the question, add from remaining items
            if len(available_items) < self.n_items_per_question:
                remaining_items = [
                    item
                    for item in self._items_dict.keys()
                    if item not in available_items
                ]
                # Choose least used remaining items first
                additional_items = sorted(remaining_items, key=lambda x: item_counts[x])
                available_items.extend(
                    additional_items[: self.n_items_per_question - len(available_items)]
                )

            # Sample the available items to fill the question
            set_items = random.sample(available_items, self.n_items_per_question)

            # Add the set to the list of sets
            sets.append(set_items)

            # Update the item counts
            for item in set_items:
                item_counts[item] += 1

        # Ensure all items appear at least once
        unused_items = [item for item, count in item_counts.items() if count == 0]
        for item in unused_items:
            least_used_set = min(sets, key=lambda s: sum(item_counts[i] for i in s))
            replace_index = random.randint(0, self.n_items_per_question - 1)
            least_used_set[replace_index] = item
            item_counts[item] += 1
            item_counts[least_used_set[replace_index]] -= 1

        # Ensure each pair of items appears together at least once
        item_pairs = set(itertools.combinations(self._items_dict.keys(), 2))
        for i, set_items in enumerate(sets):
            for pair in itertools.combinations(set_items, 2):
                if pair in item_pairs:
                    item_pairs.remove(pair)
                elif (pair[1], pair[0]) in item_pairs:
                    item_pairs.remove((pair[1], pair[0]))

        # If there are still pairs that haven't appeared together, modify sets to include them
        for pair in item_pairs:
            for i, set_items in enumerate(sets):
                if pair[0] in set_items or pair[1] in set_items:
                    if pair[0] not in set_items:
                        replace_index = random.randint(0, self.n_items_per_question - 1)
                        sets[i][replace_index] = pair[0]
                    elif pair[1] not in set_items:
                        replace_index = random.randint(0, self.n_items_per_question - 1)
                        sets[i][replace_index] = pair[1]
                    break
            else:
                # If there is no set with either item, replace two items in a random set
                random_set = random.choice(sets)
                replace_indices = random.sample(range(self.n_items_per_question), 2)
                random_set[replace_indices[0]] = pair[0]
                random_set[replace_indices[1]] = pair[1]

        return sets

    # Generate the question sets for all participants
    def _generate_all_sets(self) -> dict[int, list[list[int]]]:
        return {
            pid: self._generate_sets_for_participant(pid)
            for pid in self._participant_ids
        }

    def _initialize_responses(self) -> pd.DataFrame:
        index = pd.MultiIndex.from_product(
            [
                self._participant_ids,
                [i + 1 for i in range(self.n_questions_per_participant)],
            ],
            names=["participant_id", "question_number"],
        )
        columns = [f"item_{i+1}" for i in range(self.n_items_per_question)] + [
            "lowest",
            "highest",
        ]

        df = pd.DataFrame(index=index, columns=columns).astype("object")

        # Add items from self._question_sets to the item columns
        for pid in self._participant_ids:
            for q_num, question_items in enumerate(self._question_sets[pid]):
                for i, item in enumerate(question_items):
                    df.loc[(pid, q_num + 1), f"item_{i+1}"] = item

        return df

    # Add a response for a single question and participant
    def add_response(
        self, participant_id: int, question_number: int, response: tuple[int, int]
    ):
        if participant_id not in self._participant_ids:
            raise ValueError(f"Participant {participant_id} not found")

        if question_number > self.n_questions_per_participant:
            raise ValueError(f"Question number {question_number} is out of range")

        if len(response) != 2:
            raise ValueError(f"Response must be a tuple of two integers (item ids)")

        if response[0] == response[1]:
            raise ValueError(
                f"Response must be a pair of different integers (item ids)"
            )

        for item in response:
            if item not in self._question_sets[participant_id][question_number - 1]:
                raise ValueError(
                    f"Response {item} is not a valid item for this question and participant"
                )

        self._responses.loc[
            (participant_id, question_number), ("lowest", "highest")
        ] = response

    def get_responses(self) -> pd.DataFrame:
        return self._responses

    def generate_random_responses(self, overwrite=False):
        for participant_id in self._participant_ids:
            for question_number in [
                i + 1 for i in range(self.n_questions_per_participant)
            ]:
                has_response = (
                    self._responses.loc[
                        (participant_id, question_number), ["lowest", "highest"]
                    ]
                    .notnull()
                    .all()
                    .all()
                )
                if not has_response:
                    random_response = random.sample(
                        sorted(
                            self._question_sets[participant_id][question_number - 1]
                        ),
                        2,
                    )
                    self.add_response(participant_id, question_number, random_response)
                elif overwrite:
                    self.add_response(participant_id, question_number, random_response)

        # TODO: Add option to generate responses in a specific style/pattern

    def delete_all_responses(self):
        self._responses[["lowest", "highest"]] = None

    def get_item_counts(self) -> pd.DataFrame:

        value_counts_lowest = self._responses["lowest"].value_counts().sort_index()
        value_counts_highest = self._responses["highest"].value_counts().sort_index()

        out = pd.concat([value_counts_lowest, value_counts_highest], axis=1)
        out.columns = ["lowest", "highest"]
        out.fillna(0, inplace=True)
        out = out.astype(int)
        out["net"] = out["highest"] - out["lowest"]
        out.index.name = "item_id"
        out.sort_index(inplace=True)

        return out

    def plot_item_counts(self):
        item_counts = self.get_item_counts()
        plot_data = pd.DataFrame(
            {
                "Item": [self._items_dict[i] for i in item_counts.index],
                "Highest": item_counts["highest"],
                "Lowest": -item_counts["lowest"],
                "Net": item_counts["net"],
            }
        ).sort_values(
            "Net", ascending=True
        )  # Sort by net value

        # Create the horizontal bar chart
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                y=plot_data["Item"],
                x=plot_data["Highest"],
                orientation="h",
                name="Highest",
                marker_color="lightgreen",
            )
        )
        fig.add_trace(
            go.Bar(
                y=plot_data["Item"],
                x=plot_data["Lowest"],
                orientation="h",
                name="Lowest",
                marker_color="lightcoral",
            )
        )
        fig.add_trace(
            go.Scatter(
                y=plot_data["Item"],
                x=plot_data["Net"],
                mode="markers",
                name="Net",
                marker=dict(color="black", size=7),
            )
        )

        # Update layout
        fig.update_layout(
            title="Count analysis",
            xaxis_title="Count",
            yaxis_title="Item",
            height=800,
            width=800,
            margin=dict(l=200),  # Increase left margin to accommodate long item names
            barmode="relative",  # Change to relative mode for side-by-side bars
            xaxis=dict(
                zeroline=True, zerolinewidth=1, zerolinecolor="black"
            ),  # Add zero line
        )

        return fig

    def run_multinomial_logit(self):
        # Reshape reponse data so that every row contains a single choice
        # (1 for the highest, -1 for the lowest, 0 otherwise)
        choices = []
        question_id = 1
        for _, row in self._responses.iterrows():
            items_in_question = row[:-2]  # items in this question
            for item in items_in_question:
                choice = (
                    1
                    if row["highest"] == item
                    else (-1 if row["lowest"] == item else 0)
                )
                participant_id = row.name[0]
                question_number = row.name[1]
                question_id = "_".join([str(participant_id), str(question_number)])
                choices.append(
                    {
                        "participant_id": participant_id,
                        "question_id": question_id,
                        "item_id": item,
                        "choice": choice,
                    }
                )

        df = pd.DataFrame(choices)

        # Remove "lowest" choices
        df.loc[df["choice"] == -1, "choice"] = 0

        # Create dummy variable for item,
        # dropping one item to avoid multicollinearity
        X = pd.get_dummies(df["item_id"], drop_first=True)

        y = df["choice"]

        question_id = df["question_id"]

        model = ConditionalLogit(endog=y, exog=X, groups=question_id)

        result = model.fit()

        # Calculate item utilities
        item_utilities = np.squeeze(result.params)
        item_utilities = np.insert(
            item_utilities, 0, 0
        )  # add dropped item back in with a 0 utility (relative to the others)

        item_utilities = pd.Series(item_utilities, index=self._items_dict.keys())

        # Calculate rescaled item utilities
        exp_item_utilities = np.exp(item_utilities)
        rescaled_item_utilities = exp_item_utilities / exp_item_utilities.sum()

        self._multinomial_logit_model = {
            "result": result,
            "item_utilities": item_utilities,
            "rescaled_item_utilities": rescaled_item_utilities,
        }

    def plot_item_utilities(self):
        item_utilities = self._multinomial_logit_model["rescaled_item_utilities"]
        plot_data = pd.DataFrame(
            {
                "Item": [self._items_dict[i] for i in item_utilities.index],
                "Utility": item_utilities.values * 100,  # Convert to percentage
            }
        ).sort_values("Utility", ascending=True)

        # Create the horizontal bar chart
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                y=plot_data["Item"],
                x=plot_data["Utility"],
                orientation="h",
                name="Utility",
                marker_color="royalblue",
                text=[
                    f"{x:.1f}%" for x in plot_data["Utility"]
                ],  # Add percentage labels
                textposition="outside",
            )
        )

        # Update layout
        fig.update_layout(
            title="Utilities from multinomial logit model",
            xaxis_title="Utility (%)",
            yaxis_title="Item",
            height=800,
            width=800,
            margin=dict(l=200),  # Increase left margin to accommodate long item names
            xaxis=dict(
                zeroline=True,
                zerolinewidth=1,
                zerolinecolor="black",
                tickformat=".1f",  # Format x-axis ticks as percentages
                ticksuffix="%",
            ),
        )

        return fig


# DEBUGGING
if __name__ == "__main__":
    survey = MaxDiffSurvey(
        items=[
            "apples",
            "bananas",
            "pears",
            "peaches",
            "cherries",
            "grapes",
            "lemons",
            "oranges",
            "melons",
            "blueberries",
            "raspberries",
        ],
        n_participants=20,
    )

    survey._initialize_responses()
    survey.generate_random_responses()
    survey.run_multinomial_logit()
    # print(survey._multinomial_logit_model["item_utilities"])
    # print(survey._multinomial_logit_model["rescaled_item_utilities"])
    # print(np.sum(survey._multinomial_logit_model["rescaled_item_utilities"]))

    # Count items for each participant
    if False:
        for participant_id, sets in survey._question_sets.items():
            item_counts = {}
            for set_items in sets:
                for item in set_items:
                    item_counts[item] = item_counts.get(item, 0) + 1

            print(f"Participant {participant_id} item counts:")
            for item, count in sorted(item_counts.items()):
                print(f"  {item}: {count}")
            print()
