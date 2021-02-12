from doit.tools import config_changed

from config import (
    SUBJECTS_DIR,
    subjects,
    COREG_DIR,
    bp_anat,
    fsf_config,
    fwd_config,
    fwd_path,
)
from utils import disable


@disable
def task_freesurfer():
    for subj in subjects:
        bp_anat.update(subject=subj)
        yield dict(
            name=f"sub-{subj}",
            file_dep=[bp_anat.fpath],
            actions=[
                f"recon-all -i {bp_anat.fpath} -s sub-{subj} -all -sd"
                f" {SUBJECTS_DIR} -parallel -openmp {fsf_config['openmp']}"
            ],
            targets=[SUBJECTS_DIR / f"sub-{subj}"],
            verbosity=2,
        )


def task_make_scalp_surfaces():
    for subj in subjects:
        subj = f"sub-{subj}"
        yield dict(
            name=subj,
            uptodate=[True],
            actions=[
                f"mne make_scalp_surfaces -o -f -s {subj} -d {SUBJECTS_DIR}"
            ],
            targets=[
                SUBJECTS_DIR / subj / "bem" / f"{subj}-head-dense.fif",
                SUBJECTS_DIR / subj / "bem" / f"{subj}-head-medium.fif",
                SUBJECTS_DIR / subj / "bem" / f"{subj}-head-sparse.fif",
            ],
        )


def task_make_bem_surfaces():
    for subj in subjects:
        subj = f"sub-{subj}"
        yield dict(
            name=subj,
            uptodate=[True],
            actions=[f"mne watershed_bem -o -s {subj} -d {SUBJECTS_DIR}"],
            targets=[
                SUBJECTS_DIR / subj / "bem" / f"{subj}-head.fif",
                SUBJECTS_DIR / subj / "bem" / "outer_skin.surf",
                SUBJECTS_DIR / subj / "bem" / "inner_skull.surf",
                SUBJECTS_DIR / subj / "bem" / "outer_skull.surf",
                SUBJECTS_DIR / subj / "bem" / "brain.surf",
            ],
        )


def task_coregister():
    for subj in subjects:
        prefix = SUBJECTS_DIR / f"sub-{subj}" / "bem"
        yield dict(
            name=subj,
            file_dep=[
                prefix / f"sub-{subj}-head-dense.fif",
                prefix / f"sub-{subj}-head-medium.fif",
                prefix / f"sub-{subj}-head-sparse.fif",
            ],
            targets=[COREG_DIR / f"sub-{subj}-trans.fif"],
            actions=[f"python 10-coregister.py {subj}"],
        )


def task_compute_forward():
    for subj in subjects:
        subj_bids = f"sub-{subj}"
        yield dict(
            name=subj_bids,
            uptodate=[config_changed(fwd_config)],
            file_dep=[
                SUBJECTS_DIR / subj_bids / "bem" / f"{subj_bids}-head.fif",
                SUBJECTS_DIR / subj_bids / "bem" / "outer_skin.surf",
                SUBJECTS_DIR / subj_bids / "bem" / "inner_skull.surf",
                SUBJECTS_DIR / subj_bids / "bem" / "outer_skull.surf",
                SUBJECTS_DIR / subj_bids / "bem" / "brain.surf",
            ],
            targets=[fwd_path.format(subject=subj)],
            actions=[f"python 11-compute_forward.py {subj}"],
        )


# def task_compute_sources():
#     for subj_path in sorted(SUBJECTS_DIR.glob("sub-*")):
#         subj_id = subj_path.name
#         yield dict(
#             name=subj_id,
#             file_dep=[
#                 "compute_sources.py",
#                 FORWARDS_DIR / f"sub-{subj_id}_spacing-{fwd_config['spacing']}-fwd.fif",
#             ],
#             targets=[SUBJECTS_DIR / subj_id],
#             actions=[f"python compute_sources.py {subj_id}"],
#         )
