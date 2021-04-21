from collections import defaultdict

BIDS_ROOT = "/home/dmalt/Data/metacog_social/"

DATASET_NAME = "metacognition"
AUTHORS = (
    [
        "Beatriz Martin Luengo",
        "Maria Alekseeva",
        "Dmitrii Altukhov",
        "Yuri Shtyrov",
    ],
)


all_subjects = [
    "01",
    "02",
    "03",
]


tasks = ["go", "CE", "OE"]
subj_tasks = defaultdict(lambda: tasks)

all_subjects = [
    "01",
]

bad_subjects = ["02", "20", "07"]
subjects = [s for s in all_subjects if s not in bad_subjects]


runs = ["01", "02", "03"]
subj_runs = defaultdict(lambda: runs)
subj_runs["01"] = ["01"]  # first subj has everything in one file

er_sessions = []
