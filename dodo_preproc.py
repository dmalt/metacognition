from doit.tools import config_changed
from mne_bids import make_dataset_description
from config import (
    BIDS_ROOT,
    DATASET_NAME,
    AUTHORS,
    subjects,
    bp_root,
    bp_headpos,
    bp_bads,
    bp_annot,
    bp_maxfilt,
    bp_filt,
    bp_ica_sol,
    bp_ica,
    bp_ica_bads,
    bp_annot_final,
    bp_epochs,
    iter_files,
    maxfilt_config,
    concat_config,
    ica_config,
)
from utils import update_bps, disable

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
                    "path": BIDS_ROOT,
                    "name": DATASET_NAME,
                    "authors": AUTHORS,
                    "overwrite": True,
                },
            )
        ],
        "targets": ["dataset_description.json"],
    }


def task_compute_head_position():
    """Compute head position for maxfilter"""
    for subj, task, run, ses in iter_files(subjects):
        src_bp, dest_bp = update_bps(
            [bp_root, bp_headpos], subject=subj, task=task, run=run
        )
        yield dict(
            name=src_bp.basename,
            file_dep=[src_bp.fpath],
            actions=[f"python 01-compute_head_pos.py {subj} {task} -r {run}"],
            targets=[dest_bp.fpath],
        )


@disable
def task_mark_bads_maxfilter():
    """Manually mark bad channels and segments and for maxfilter"""
    script = "02-mark_bads_maxfilter.py"
    for subj, task, run, ses in iter_files(["emptyroom"] + subjects):
        src_bp, dest_bp_bads, dest_bp_annot = update_bps(
            [bp_root, bp_bads, bp_annot],
            subject=subj,
            session=ses,
            task=task,
            run=run,
        )
        yield dict(
            name=src_bp.basename,
            file_dep=[src_bp.fpath],
            actions=[f"python {script} {subj} {task} -r {run} -s {ses}"],
            targets=[dest_bp_bads.fpath, dest_bp_annot.fpath],
        )


def task_apply_maxfilter():
    """Apply maxfilter to raw data; interpolate bad channels in process"""
    script = "03-apply_maxfilter.py"
    for subj, task, run, ses in iter_files(["emptyroom"] + subjects):
        (
            src_bp,
            src_bp_bads,
            src_bp_annot,
            src_bp_hp,
            dest_bp_maxfilt,
        ) = update_bps(
            [bp_root, bp_bads, bp_annot, bp_headpos, bp_maxfilt],
            subject=subj,
            session=ses,
            task=task,
            run=run,
        )
        aux_deps = [src_bp_bads.fpath, src_bp_annot.fpath]
        if subj != "emptyroom":
            aux_deps.append(src_bp_hp.fpath)
        yield dict(
            name=src_bp.basename,
            uptodate=[config_changed(maxfilt_config)],
            clean=True,
            file_dep=[src_bp.fpath] + aux_deps,
            actions=[f"python {script} {subj} {task} -r {run} -s {ses}"],
            targets=[dest_bp_maxfilt.fpath],
        )


@disable
def task_concat_filter_resample():
    """Concatenate runs, bandpass-filter and downsample data"""
    script = "04-concat_filter_resample.py"
    for subj, task, runs, ses in iter_files(["emptyroom"] + subjects, "joint"):
        bp_src, bp_dest = update_bps(
            [bp_maxfilt, bp_filt],
            subject=subj,
            task=task,
            run=None,
            session=ses,
        )
        bp_dest.update(run=None)
        name = bp_src.basename
        if task == "questions":
            bp_src = [bp_src.copy().update(run=int(r)) for r in runs]
        else:
            bp_src = [bp_src]
        yield dict(
            name=name,
            uptodate=[config_changed(concat_config)],
            file_dep=[b.fpath for b in bp_src],
            actions=[f"python {script} {subj} {task} -s {ses}"],
            targets=[bp_dest.fpath],
            clean=True,
        )


def task_compute_ica():
    """Compute ICA solution for filtered and resampled data. Skip emptyroom."""
    script = "05-compute_ica.py"
    for subj, task, ses in iter_files(subjects, None):
        bp_src, bp_dest = update_bps(
            [bp_filt, bp_ica_sol],
            subject=subj,
            task=task,
            session=ses,
        )
        yield dict(
            name=bp_src.basename,
            uptodate=[config_changed(ica_config)],
            file_dep=[bp_src.fpath],
            actions=[f"python {script} {subj} {task} -s {ses}"],
            targets=[bp_dest.fpath],
        )


@disable
def task_inspect_ica():
    """Remove artifacts with precomputed ICA solution."""
    script = "06-inspect_ica.py"
    for subj, task, ses in iter_files(subjects, None):
        bp_src_filt, bp_src_ica_sol, bp_dest = update_bps(
            [bp_filt, bp_ica_sol, bp_ica_bads],
            subject=subj,
            task=task,
            session=ses,
        )
        yield dict(
            name=bp_src_filt.basename,
            file_dep=[bp_src_filt.fpath, bp_src_ica_sol.fpath],
            actions=[f"python {script} {subj} {task} -s {ses}"],
            targets=[bp_dest.fpath],
        )


def task_apply_ica():
    """
    Remove bad ICA components from data

    """
    script = "07-apply_ica.py"
    for subj, task, ses in iter_files(subjects, None):
        bp_src_filt, bp_src_ica_sol, bp_dest = update_bps(
            [bp_filt, bp_ica_sol, bp_ica],
            subject=subj,
            task=task,
            session=ses,
        )
        yield dict(
            name=bp_src_filt.basename,
            file_dep=[bp_src_filt.fpath, bp_src_ica_sol.fpath],
            actions=[f"python {script} {subj} {task} -s {ses}"],
            targets=[bp_dest.fpath],
            clean=True,
        )


def task_mark_bad_segments():
    """Manually mark bad segments after ICA"""
    script = "08-mark_bad_segments.py"
    for subj, task, ses in iter_files(subjects, None):
        src_bp, dest_bp_annot = update_bps(
            [bp_ica, bp_annot_final],
            subject=subj,
            session=ses,
            task=task,
        )
        yield dict(
            name=src_bp.basename,
            file_dep=[src_bp.fpath],
            actions=[f"python {script} {subj} {task} -s {ses}"],
            targets=[dest_bp_annot.fpath],
        )


def task_make_epochs():
    """Create epochs ignoring bad segments"""
    script = "09-make_epochs.py"
    for subj, task, ses in iter_files(subjects, None):
        if task in ("rest", "noise", "practice"):
            continue
        src_bp_ica, src_bp_annot, bp_dest = update_bps(
            [bp_ica, bp_annot_final, bp_epochs],
            subject=subj,
            task=task,
            session=ses,
        )
        yield dict(
            name=src_bp_ica.basename,
            file_dep=[src_bp_ica.fpath, src_bp_annot.fpath],
            actions=[f"python {script} {subj} {task} -s {ses}"],
            targets=[bp_dest.fpath],
            clean=True,
        )
