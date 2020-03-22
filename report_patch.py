from mne.utils import logger, warn

import os.path as op


def _iterate_files(report, fnames, info, cov, baseline, sfreq, on_error,
                   image_format):
    """Parallel process in batch mode."""
    htmls, report_fnames, report_sectionlabels = [], [], []

    def _update_html(html, report_fname, report_sectionlabel):
        """Update the lists above."""
        htmls.append(html)
        report_fnames.append(report_fname)
        report_sectionlabels.append(report_sectionlabel)

    for fname in fnames:
        logger.info("Rendering : %s"
                    % op.join('...' + report.data_path[-20:],
                              fname))
        try:
            if fname.endswith(('raw.fif', 'raw.fif.gz',
                               'sss.fif', 'sss.fif.gz', 'meg.fif')):  # FIX
                html = report._render_raw(fname)
                report_fname = fname
                report_sectionlabel = 'raw'
            elif fname.endswith(('-fwd.fif', '-fwd.fif.gz')):
                html = report._render_forward(fname)
                report_fname = fname
                report_sectionlabel = 'forward'
            elif fname.endswith(('-inv.fif', '-inv.fif.gz')):
                html = report._render_inverse(fname)
                report_fname = fname
                report_sectionlabel = 'inverse'
            elif fname.endswith(('-ave.fif', '-ave.fif.gz')):
                if cov is not None:
                    html = report._render_whitened_evoked(fname, cov, baseline,
                                                          image_format)
                    report_fname = fname + ' (whitened)'
                    report_sectionlabel = 'evoked'
                    _update_html(html, report_fname, report_sectionlabel)

                html = report._render_evoked(fname, baseline, image_format)
                report_fname = fname
                report_sectionlabel = 'evoked'
            elif fname.endswith(('-eve.fif', '-eve.fif.gz')):
                html = report._render_eve(fname, sfreq, image_format)
                report_fname = fname
                report_sectionlabel = 'events'
            elif fname.endswith(('-epo.fif', '-epo.fif.gz')):
                html = report._render_epochs(fname, image_format)
                report_fname = fname
                report_sectionlabel = 'epochs'
            elif (fname.endswith(('-cov.fif', '-cov.fif.gz')) and
                  report.info_fname is not None):
                html = report._render_cov(fname, info, image_format)
                report_fname = fname
                report_sectionlabel = 'covariance'
            elif (fname.endswith(('-trans.fif', '-trans.fif.gz')) and
                  report.info_fname is not None and report.subjects_dir
                  is not None and report.subject is not None):
                html = report._render_trans(fname, report.data_path, info,
                                            report.subject,
                                            report.subjects_dir)
                report_fname = fname
                report_sectionlabel = 'trans'
            else:
                html = None
                report_fname = None
                report_sectionlabel = None
        except Exception as e:
            if on_error == 'warn':
                warn('Failed to process file %s:\n"%s"' % (fname, e))
            elif on_error == 'raise':
                raise
            html = None
            report_fname = None
            report_sectionlabel = None
        _update_html(html, report_fname, report_sectionlabel)

    return htmls, report_fnames, report_sectionlabels


def _get_toc_property(fname):
    """Assign class names to TOC elements to allow toggling with buttons."""
    if fname.endswith(('-eve.fif', '-eve.fif.gz')):
        div_klass = 'events'
        tooltip = fname
        text = op.basename(fname)
    elif fname.endswith(('-ave.fif', '-ave.fif.gz')):
        div_klass = 'evoked'
        tooltip = fname
        text = op.basename(fname)
    elif fname.endswith(('-cov.fif', '-cov.fif.gz')):
        div_klass = 'covariance'
        tooltip = fname
        text = op.basename(fname)
    elif fname.endswith(('raw.fif', 'raw.fif.gz',
                         'sss.fif', 'sss.fif.gz', 'meg.fif')):  # FIX
        div_klass = 'raw'
        tooltip = fname
        text = op.basename(fname)
    elif fname.endswith(('-trans.fif', '-trans.fif.gz')):
        div_klass = 'trans'
        tooltip = fname
        text = op.basename(fname)
    elif fname.endswith(('-fwd.fif', '-fwd.fif.gz')):
        div_klass = 'forward'
        tooltip = fname
        text = op.basename(fname)
    elif fname.endswith(('-inv.fif', '-inv.fif.gz')):
        div_klass = 'inverse'
        tooltip = fname
        text = op.basename(fname)
    elif fname.endswith(('-epo.fif', '-epo.fif.gz')):
        div_klass = 'epochs'
        tooltip = fname
        text = op.basename(fname)
    elif fname.endswith(('.nii', '.nii.gz', '.mgh', '.mgz')):
        div_klass = 'mri'
        tooltip = 'MRI'
        text = 'MRI'
    elif fname.endswith(('bem')):
        div_klass = 'mri'
        tooltip = 'MRI'
        text = 'MRI'
    elif fname.endswith('(whitened)'):
        div_klass = 'evoked'
        tooltip = fname
        text = op.basename(fname[:-11]) + '(whitened)'
    else:
        div_klass = fname.split('-#-')[1]
        tooltip = fname.split('-#-')[0]
        text = fname.split('-#-')[0]

    return div_klass, tooltip, text


