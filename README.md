Installation
============

First, download and install Anaconda python distribution suitable for your OS.
We recommend using [miniconda](https://docs.conda.io/en/latest/miniconda.html) since
we won't need the preinstalled packages coming with the main distribution.


Full installation
-----------------
Download data processing scripts + set up virtual environment with dependencies

### Linux
In terminal navigate to directory you want to work from, i.e.
```bash
cd ~/Projects
```
And run the commands below.
Note that environment name (`--name metacog` argument) can be changed to your likings.
```bash
git clone https://github.com/dmalt/metacognition.git
cd metacognition
cd setup
conda env create -n meg1 -f environment.yml
pip install -e .
```


### Windows
Open Anaconda prompt and [install `git` package](https://anaconda.org/anaconda/git).
Follow instructions for Linux using Anaconda prompt

Setting up conda environment only
---------------------------------
Don't download the scripts for now, just set up the virtual environment.

### Windows
In Anaconda prompt run the following (note that env name `--name metacog` can be changed):
```bash
conda install -c anaconda curl
curl --remote-name https://raw.githubusercontent.com/dmalt/metacognition/master/environment.yml
conda env create --name metacog -f environment.yml
```

**To test the installation**
1. change `metacog` to your env name if you set the custom name with `--name` at the installation step
2. run the following:
```bash
conda activate metacog
python -c "import mne; mne.sys_info()"
```
This should display some system information along with the versions of MNE-Python and its dependencies.


Doit
====

Doit documentation can be found [here](https://pydoit.org/contents.html)

Running the pipeline
--------------------

To run the whole pipeline, first make sure you've changed the current directory
for your terminal to the `metacog` folder. This folder includes tasks configuration file `dodo.py`

To run the whole pipeline simply execute

```bash
doit
```

Doit then will run every tasks listed in `dodo.py`, making sure that the tasks order is
aligned with tasks dependencies.

### Running separate tasks and subtasks

In our project each data preprocessing script corresponds to `doit` task, which is specified in `dodo.py`. To list all the available tasks, run

```bash
doit list
```
Here's the sample output:
```
add_associated_emptyrooms   DISABLED! Add emptyroom path to sidecar json
compute_head_position       Compute head position for maxfilter
mark_bads_maxfilter         Manually mark bad channels and segments and for maxfilter
apply_maxfilter             Apply maxfilter to raw data; interpolate bad channels in process
concat_filter_resample      Concatenate runs, bandpass-filter and downsample data
...
```

You can run any task from this list separately with
```bash
doit <task>
```

Doit automatically checks if all the dependencies of `<task>` are up-to-date and if
not **it will first run the parent scripts**

For example, to run `apply_maxfilter` you should run
```bash
doit apply_maxfilter
```
Since `apply_maxfilter` depends on `mark_bads_maxfilter`, it will first run
`mark_bads_maxfilter` but only if necessary.

#### Subtasks

In the processing pipeline each task produces a number of subtasks, usually one
subtask for each processed file. To print the full list of subtasks for a task `<task>`
run
```bash
doit list --all <task>
```

For example, to get a full list of subtasks for `apply_maxfilter`, run
```
doit list --all apply_maxfilter
```
The sample output would look similar to this:
```
apply_maxfilter                                        Apply maxfilter to raw data; interp
olate bad channels in process
apply_maxfilter:sub-01_task-questions_run-01_meg.fif
apply_maxfilter:sub-01_task-rest_meg.fif
apply_maxfilter:sub-03_task-practice_meg.fif
apply_maxfilter:sub-03_task-questions_run-01_meg.fif
apply_maxfilter:sub-03_task-questions_run-02_meg.fif
apply_maxfilter:sub-03_task-questions_run-03_meg.fif
apply_maxfilter:sub-03_task-rest_meg.fif
apply_maxfilter:sub-04_task-practice_meg.fif
apply_maxfilter:sub-04_task-questions_run-01_meg.fif
apply_maxfilter:sub-04_task-questions_run-02_meg.fif
...
```

This list can be used to run doit for a specific file instead of running all the subtasks.
To run a selected subtask run `doit` with a full subtask name. For example, to run `apply_maxfilter` only for `sub-01_task-questions_run-01_meg.fif`, run:
```bash
doit apply_maxfilter:sub-05_task-questions_run-01_meg.fif
```
Output:
```
.  mark_bads_maxfilter:sub-05_task-questions_run-01_meg.fif
100%|██████████| Filtering : 73808/73808 [00:05<00:00, 13418.30it/s]]
.  apply_maxfilter:sub-05_task-questions_run-01_meg.fif
100%|██████████| Filtering : 73808/73808 [00:05<00:00, 13407.42it/s]]
preproc/03-apply_maxfilter.py:59: RuntimeWarning: Acquisition skips detected but did not fit e
venly into output buffer_size, will be written as zeroes.
  raw_sss.save(maxfilt_path, overwrite=True)
```


#### Useful commands

```bash
doit reset-dep
```
https://pydoit.org/cmd_other.html#reset-dep


```bash
doit forget
```


```
doit clean
```


Dataset structure
=================
```
.
|-- meta_bids
    |-- code
    |   |-- 01-compute_head_pos.py
    |   |-- ...
    |   |-- config.py
    |   `-- ...
    |-- dataset_description.json
    |-- derivatives
    |   |-- 01-head_positon
    |   `-- ...
    |-- participants.json
    |-- participants.tsv
    |-- SSS_data
    |   |-- ct_sparse.fif
    |   `-- sss_cal.dat
    |-- sub-01
    |   |-- anat
    |   |-- beh
    |   |-- meg
    |   `-- sub-01_scans.tsv
    |-- sub-02
    |   `-- ...
    |-- ...
    `-- sub-emptyroom
        |-- ses-20200229
        `-- ...
```
