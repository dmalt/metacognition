import json
from warnings import catch_warnings, simplefilter

from doit.tools import config_changed
from mne_bids import make_dataset_description

from metacog import bp
from metacog.config_parser import cfg
from metacog.paths import dirs
from metacog.dataset_specific_utils import iter_files
from metacog.utils import disable

# DOIT_CONFIG = {
#     "default_tasks": [
#         # "prepare_bids",
#         # "make_dataset_description",
#         # "register_subjects",
#         "compute_ica",
#         "inspect_ica",
#     ]
# }


def task_make_dataset_description():
    """Create dataset_description.json"""
    return {
        "actions": [
            (
                make_dataset_description,
                [],
                {
                    "path": dirs.bids_root,
                    "name": cfg.DATASET_NAME,
                    "authors": cfg.AUTHORS,
                    "overwrite": True,
                },
            )
        ],
        "targets": ["dataset_description.json"],
    }


@disable
def task_add_associated_emptyrooms():
    """Add emptyroom path to sidecar json"""
    script = "preproc/add_associated_emptyroom.py"
    for subj, task, run, _ in iter_files(cfg.subjects):
        raw = bp.root.fpath(subject=subj, task=task, run=run, session=None)
        json_path = bp.root_json.fpath(subject=subj, task=task, run=run)
        yield dict(
            name=raw.name,
            file_dep=[raw],
            actions=[f"python {script} {subj} {task} -r {run}"],
            targets=[json_path],
        )


def task_compute_head_position():
    """Compute head position for maxfilter"""
    script = "preproc/01-compute_head_pos.py"
    for subj, task, run, ses in iter_files(cfg.subjects):
        raw = bp.root.fpath(subject=subj, task=task, run=run, session=ses)
        hp = bp.headpos.fpath(subject=subj, task=task, run=run)
        yield dict(
            name=raw.name,
            file_dep=[raw],
            actions=[f"python {script} {subj} {task} -r {run}"],
            targets=[hp],
        )


# @disable
def task_mark_bads_maxfilter():
    """Manually mark bad channels and segments and for maxfilter"""
    script = "preproc/02-mark_bads_maxfilter.py"
    for subj, task, run, ses in iter_files(["emptyroom"] + cfg.subjects):
        raw = bp.root.fpath(subject=subj, task=task, run=run, session=ses)
        bads = bp.bads.fpath(subject=subj, task=task, run=run, session=ses)
        annot = bp.annot.fpath(subject=subj, task=task, run=run, session=ses)
        yield dict(
            name=raw.name,
            file_dep=[raw],
            actions=[f"python {script} {subj} {task} -r {run} -s {ses}"],
            targets=[bads, annot],
        )


def task_apply_maxfilter():
    """Apply maxfilter to raw data; interpolate bad channels in process"""
    script = "preproc/03-apply_maxfilter.py"
    for subj, task, run, ses in iter_files(["emptyroom"] + cfg.subjects):
        raw = bp.root.fpath(subject=subj, task=task, run=run, session=ses)
        bads = bp.bads.fpath(subject=subj, task=task, run=run, session=ses)
        annot = bp.annot.fpath(subject=subj, task=task, run=run, session=ses)
        maxfilt = bp.maxfilt.fpath(
            subject=subj, task=task, run=run, session=ses
        )

        yield dict(
            name=raw.name,
            uptodate=[config_changed(cfg.maxfilt_config)],
            clean=True,
            file_dep=[raw, bads, annot],
            actions=[f"python {script} {subj} {task} -r {run} -s {ses}"],
            targets=[maxfilt],
        )


def task_concat_filter_resample():
    """Concatenate runs, bandpass-filter and downsample data"""
    script = "preproc/04-concat_filter_resample.py"
    for subj, task, runs, ses in iter_files(
        ["emptyroom"] + cfg.subjects, "joint"
    ):

        bp.maxf_subj = bp.maxfilt.update(subject=subj, task=task, session=ses)
        filt = bp.filt.fpath(subject=subj, task=task, session=ses)

        if task == cfg.subj_tasks[subj][0]:
            maxfilt = [bp.maxf_subj.fpath(run=r) for r in runs]
        else:
            maxfilt = [bp.maxf_subj.fpath(run=None)]
        name = maxfilt[0].name

        yield dict(
            name=name,
            uptodate=[config_changed(cfg.concat_config)],
            file_dep=maxfilt,
            actions=[f"python {script} {subj} {task} -s {ses}"],
            targets=[filt],
            clean=True,
        )


def task_compute_ica():
    """Compute ICA solution for filtered and resampled data. Skip emptyroom."""
    script = "preproc/05-compute_ica.py"
    for subj, task, _ in iter_files(cfg.subjects, None):
        filt = bp.filt.fpath(subject=subj, task=task, session=None)
        ica_sol = bp.ica_sol.fpath(subject=subj, task=task)

        yield dict(
            name=filt.name,
            uptodate=[config_changed(cfg.ica_config)],
            file_dep=[filt],
            actions=[f"python {script} {subj} {task}"],
            targets=[ica_sol],
        )


# @disable
def task_inspect_ica():
    """Remove artifacts with precomputed ICA solution."""
    script = "preproc/06-inspect_ica.py"
    for subj, task, ses in iter_files(cfg.subjects, None):
        filt = bp.filt.fpath(subject=subj, task=task, session=None)
        ica_sol = bp.ica_sol.fpath(subject=subj, task=task)
        ica_bads = bp.ica_bads.fpath(subject=subj, task=task)

        yield dict(
            name=filt.name,
            file_dep=[filt, ica_sol],
            actions=[f"python {script} {subj} {task}"],
            targets=[ica_bads],
        )


def task_apply_ica():
    """
    Remove bad ICA components from data

    """
    script = "preproc/07-apply_ica.py"
    for subj, task, ses in iter_files(cfg.subjects, None):
        filt = bp.filt.fpath(subject=subj, task=task, session=None)
        ica_sol = bp.ica_sol.fpath(subject=subj, task=task)
        ica_bads = bp.ica_bads.fpath(subject=subj, task=task)
        cleaned_fif = bp.ica.fpath(subject=subj, task=task)

        yield dict(
            name=filt.name,
            file_dep=[filt, ica_sol, ica_bads],
            actions=[f"python {script} {subj} {task}"],
            targets=[cleaned_fif],
            clean=True,
        )


def task_mark_bad_segments():
    """Manually mark bad segments after ICA"""
    script = "preproc/08-mark_bad_segments.py"
    for subj, task, ses in iter_files(cfg.subjects, None):
        cleaned_fif = bp.ica.fpath(subject=subj, task=task)
        annot = bp.annot_final.fpath(subject=subj, task=task)
        yield dict(
            name=cleaned_fif.name,
            file_dep=[cleaned_fif],
            actions=[f"python {script} {subj} {task}"],
            targets=[annot],
        )


def task_make_epochs():
    """Create epochs ignoring bad segments"""
    script = "preproc/09-make_epochs.py"
    for subj, task, ses in iter_files(cfg.subjects, None):
        if task in cfg.subj_tasks[subj][1:]:
            continue
        cleaned_fif = bp.ica.fpath(subject=subj, task=task)
        annot = bp.annot_final.fpath(subject=subj, task=task)
        beh = bp.beh.fpath(subject=subj)
        epochs = bp.epochs.fpath(subject=subj)
        yield dict(
            name=cleaned_fif.name,
            uptodate=[config_changed(cfg.epochs_config)],
            file_dep=[cleaned_fif, annot, beh],
            actions=[f"python {script} {subj}"],
            targets=[epochs],
            clean=True,
        )


@disable
def task_freesurfer():
    for subj in cfg.subjects:
        anat = bp.anat.fpath(subject=subj)
        yield dict(
            name=f"sub-{subj}",
            file_dep=[bp.anat],
            actions=[
                f"recon-all -i {anat} -s sub-{subj} -all -sd"
                f" {dirs.fsf_subjects} -parallel -openmp {cfg.fsf_config['openmp']}"
            ],
            targets=[dirs.fsf_subjects / f"sub-{subj}"],
            verbosity=2,
        )


def task_make_scalp_surfaces():
    for subj in cfg.subjects:
        subj = f"sub-{subj}"
        yield dict(
            name=subj,
            uptodate=[True],
            actions=[
                f"mne make_scalp_surfaces -o -f -s {subj} -d {dirs.fsf_subjects}"
            ],
            targets=[
                dirs.fsf_subjects / subj / "bem" / f"{subj}-head-dense.fif",
                dirs.fsf_subjects / subj / "bem" / f"{subj}-head-medium.fif",
                dirs.fsf_subjects / subj / "bem" / f"{subj}-head-sparse.fif",
            ],
        )


def task_make_bem_surfaces():
    for subj in cfg.subjects:
        subj = f"sub-{subj}"
        yield dict(
            name=subj,
            uptodate=[True],
            actions=[f"mne watershed_bem -o -s {subj} -d {dirs.fsf_subjects}"],
            targets=[
                dirs.fsf_subjects / subj / "bem" / f"{subj}-head.fif",
                dirs.fsf_subjects / subj / "bem" / "outer_skin.surf",
                dirs.fsf_subjects / subj / "bem" / "inner_skull.surf",
                dirs.fsf_subjects / subj / "bem" / "outer_skull.surf",
                dirs.fsf_subjects / subj / "bem" / "brain.surf",
            ],
        )


def task_coregister():
    for subj in cfg.subjects:
        prefix = dirs.fsf_subjects / f"sub-{subj}" / "bem"
        yield dict(
            name=subj,
            file_dep=[
                prefix / f"sub-{subj}-head-dense.fif",
                prefix / f"sub-{subj}-head-medium.fif",
                prefix / f"sub-{subj}-head-sparse.fif",
            ],
            targets=[bp.trans.fpath(subject=subj)],
            actions=[f"python 10-coregister.py {subj}"],
        )


def task_compute_forward():
    """Compute forward solution"""
    for subj in cfg.subjects:
        subj_bids = f"sub-{subj}"
        yield dict(
            name=subj_bids,
            uptodate=[config_changed(cfg.fwd_config)],
            file_dep=[
                bp.trans.fpath(subject=subj),
                dirs.fsf_subjects
                / subj_bids
                / "bem"
                / f"{subj_bids}-head.fif",
                dirs.fsf_subjects / subj_bids / "bem" / "outer_skin.surf",
                dirs.fsf_subjects / subj_bids / "bem" / "inner_skull.surf",
                dirs.fsf_subjects / subj_bids / "bem" / "outer_skull.surf",
                dirs.fsf_subjects / subj_bids / "bem" / "brain.surf",
            ],
            targets=[bp.fwd.fpath(subject=subj)],
            actions=[f"python 11-compute_forward.py {subj}"],
        )


# def task_compute_inverse():
#     """Compute inverse solution"""
#     script = "preproc/12-compute_inverse.py"
#     for subj in cfg.subjects:
#         subj_bids = f"sub-{subj}"
#         with catch_warnings():
#             simplefilter("ignore")
#             json_path = bp.root_json.fpath(subject=subj, task="rest", run=None)
#             with open(json_path, "r") as f:
#                 er_relpath = json.load(f)["AssociatedEmptyRoom"]
#             er_path = dirs.bids_root / er_relpath
#         yield dict(
#             name=subj_bids,
#             file_dep=[bp.fwd.fpath(subject=subj), er_path],
#             targets=[bp.inv.fpath(subject=subj)],
#             actions=[f"python {script} {subj}"],
#         )


def task_compute_sources():
    """Project epochs to source space"""
    script = "preproc/13-compute_sources.py"
    for subj in cfg.subjects:
        subj_bids = f"sub-{subj}"
        fwd_path = bp.fwd.fpath(subject=subj)
        inv_path = bp.inv.fpath(subject=subj)
        epochs_path = bp.epochs.fpath(subject=subj)

        yield dict(
            name=subj_bids,
            file_dep=[fwd_path, inv_path, epochs_path],
            targets=[dirs.sources / subj_bids],
            actions=[f"python {script} {subj}"],
            clean=True,
        )


def task_compute_tfr_epochs():
    """Compute time-frequency for epochs"""
    script = "preproc/15-compute_tfr_epochs.py"
    for subj in cfg.subjects:
        subj_bids = f"sub-{subj}"
        epochs_path = bp.epochs.fpath(subject=subj)
        tfr_path = bp.tfr.fpath(subject=subj)

        yield dict(
            name=subj_bids,
            uptodate=[config_changed(cfg.tfr_config)],
            file_dep=[epochs_path],
            targets=[tfr_path],
            actions=[f"python {script} {subj}"],
            clean=True,
        )


def task_average_tfr():
    """Compute inverse solution"""
    script = "preproc/16-average_tfr.py"
    for subj in cfg.subjects:
        subj_bids = f"sub-{subj}"
        tfr_path = bp.tfr.fpath(subject=subj)
        av_tfr_paths = [
            bp.tfr_av.fpath(subject=subj, acquisition=b)
            for b in cfg.target_bands
        ]

        yield dict(
            name=subj_bids,
            file_dep=[tfr_path],
            targets=av_tfr_paths,
            actions=[f"python {script} {subj}"],
            clean=True,
        )


# def task_compute_sources():
#     for subj_path in sorted(dirs.fsf_subjects.glob("sub-*")):
#         subj_id = subj_path.name
#         yield dict(
#             name=subj_id,
#             file_dep=[
#                 "compute_sources.py",
#                 dirs.forwards / f"sub-{subj_id}_spacing-{fwd_config['spacing']}-fwd.fif",
#             ],
#             targets=[dirs.fsf_subjects / subj_id],
#             actions=[f"python compute_sources.py {subj_id}"],
#         )
