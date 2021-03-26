from utils import setup_logging, SubjectRenamer
from config import subj_ids_file, dirs

logger = setup_logging(__file__)

subj_paths = [
    p for p in dirs.raw.iterdir() if p.is_dir() and p != dirs.beh_raw
]
registrator = SubjectRenamer(subj_ids_file)
registrator.add(subj_paths)
registrator.dump()
