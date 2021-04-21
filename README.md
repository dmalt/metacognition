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
conda env create --name metacog -f environment.yml
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

**Useful commands**

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
