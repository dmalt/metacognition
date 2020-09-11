Dataset structure
=================
.
|-- meta_bids
|   |-- code
|   |   |-- 00-prepare_bids.py
|   |   |-- 01-compute_head_pos.py
|   |   |-- 02-mark_bads_maxfilter.py
|   |   |-- 03-apply_maxfilter.py
|   |   |-- 04-concat_filter_resample.py
|   |   |-- 05-compute_ica.py
|   |   |-- 06-apply_ica.py
|   |   |-- 07-make_epochs.py
|   |   |-- 08-erp.py
|   |   |-- 99-make_reports.py
|   |   |-- config.py
|   |   |-- environment.yml
|   |   |-- logs
|   |   |-- Metamemory sensor-level analysis.ipynb
|   |   |-- pics
|   |   |-- README.md
|   |   `-- utils.py
|   |-- dataset_description.json
|   |-- derivatives
|   |   |-- 01-head_positon
|   |   |-- 02-maxfilter_bads
|   |   |-- 03-maxfilter
|   |   |-- 04-concat_filter_resample
|   |   |-- 05-compute_ica
|   |   |-- 06-apply_ica
|   |   |-- 07-make_epochs
|   |   `-- 99-reports
|   |-- participants.json
|   |-- participants.tsv
|   |-- SSS_data
|   |   |-- ct_sparse.fif
|   |   `-- sss_cal.dat
|   |-- sub-01
|   |   |-- beh
|   |   |-- meg
|   |   `-- sub-01_scans.tsv
|   |-- sub-02
|   |   |-- ...
|   |-- ...
|   `-- sub-emptyroom
|       |-- ses-20200229
|       `-- ...
`-- raw
    |-- behavioral_data
    |   |-- Andreev_Konstantin_06.xlsx
    |   `-- ...
    |-- CHANGES
    |-- ct_sparse.fif
    |-- sss_cal.dat
    |-- sub-andreev_konstantin
    |   `-- 200311
    `-- ...
