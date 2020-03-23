"""Tools for bids dataset manipulation"""


def dict_from_bids_fname(fname):
    fname = fname[:-len("_meg.fif")]
    bids_dict = {f.split("-")[0]: f.split("-")[1] for f in fname.split("_")}
    return bids_dict
