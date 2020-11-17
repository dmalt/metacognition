from utils import setup_logging, SubjectRenamer
from config import subj_ids_file, RAW_DIR, BEH_RAW_DIR

logger = setup_logging(__file__)

subj_paths = [p for p in RAW_DIR.iterdir() if p.is_dir() and p != BEH_RAW_DIR]
registrator = SubjectRenamer(subj_ids_file)
registrator.add(subj_paths)
registrator.dump()
