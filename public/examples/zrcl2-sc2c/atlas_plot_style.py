"""Formatting and export for the accompanying Atlas data plots.

Call install() before plotting. The helper never edits x/y/z values, limits,
normalization, colour-map limits, error bars, fit results or the source files.
Each save creates a readable PNG/SVG and a separate 183 mm vector PDF.
The PDF uses 5–7 pt text (8 pt panel letters); the web files use larger text.
Arial/Helvetica is preferred, with DejaVu Sans as an explicit fallback.
"""
from pathlib import Path
import os
import textwrap

import matplotlib as mpl
from matplotlib import font_manager
from matplotlib.figure import Figure
from matplotlib.text import Text

PALETTE = ['#0072b2', '#d55e00', '#009e73', '#cc79a7',
           '#e69f00', '#56b4e9', '#222222']
_original_save = Figure.savefig
_installed = False


def _family():
    available = {entry.name for entry in font_manager.fontManager.ttflist}
    preferred = next((name for name in ('Arial', 'Helvetica') if name in available), 'DejaVu Sans')
    return [preferred, 'DejaVu Sans'] if preferred != 'DejaVu Sans' else ['DejaVu Sans']


def _format(fig, paper=False):
    family = _family()
    web_scale = max(1., fig.get_figwidth() / 8.)
    for ax in fig.axes:
        # High-symmetry separators, zero lines and physical thresholds are
        # ordinary artists and remain intact; only decorative grid is hidden.
        ax.grid(False, which='both')
        if hasattr(ax, 'zaxis'):
            ax.grid(False)
        for spine in ax.spines.values():
            spine.set_linewidth(.65)
            spine.set_color('#111111')
        ax.tick_params(axis='both', which='major', direction='out', width=.65,
                       length=3, colors='#111111')
        ax.tick_params(axis='both', which='minor', direction='out', width=.5,
                       length=1.8, colors='#111111')
        legend = ax.get_legend()
        if legend is not None:
            legend.get_frame().set_linewidth(0)
            legend.get_frame().set_facecolor('white')
            legend.get_frame().set_alpha(.95)
    for text in fig.findobj(match=Text):
        text.set_fontfamily(family)
        text.set_color('#111111')
        original = getattr(text, '_atlas_original_size', text.get_fontsize())
        text._atlas_original_size = original
        if paper:
            value = max(5.5, min(7.0, original * .65))
            if text.get_text() in tuple('abcdefghi') and text.get_fontweight() in ('bold', 700):
                value = 8
        else:
            value = max(9.0, min(12.0, original)) * web_scale
        text.set_fontsize(value)
    for ax in fig.axes:
        title = ax.title
        original = getattr(title, '_atlas_original_text', title.get_text())
        title._atlas_original_text = original
        if '$' not in original:
            width = 46 if ax.get_position().width > .6 else 34
            title.set_text('\n'.join(textwrap.fill(line, width=width) for line in original.split('\n')))


def _panels(fig):
    if getattr(fig, '_atlas_panels_added', False):
        return
    axes, positions = [], []
    for ax in fig.axes:
        if ax.get_label() == '<colorbar>' or hasattr(ax, '_colorbar'):
            continue
        box = tuple(round(x, 3) for x in ax.get_position().bounds)
        if box in positions:
            continue
        positions.append(box)
        axes.append(ax)
    if 1 < len(axes) <= 9:
        for ax, letter in zip(axes, 'abcdefghi'):
            if any(t.get_text() == letter for t in ax.texts):
                continue
            method = ax.text2D if hasattr(ax, 'text2D') else ax.text
            method(-.18, 1.0, letter, transform=ax.transAxes,
                   fontsize=12, fontweight='bold', ha='left', va='bottom', clip_on=False)
    fig._atlas_panels_added = True


def _export(fig, fname, *args, **kwargs):
    if not isinstance(fname, (str, os.PathLike)):
        return _original_save(fig, fname, *args, **kwargs)
    path = Path(fname)
    if path.suffix.lower() not in ('.png', '.svg', '.pdf'):
        return _original_save(fig, fname, *args, **kwargs)
    path.parent.mkdir(parents=True, exist_ok=True)
    original_size = fig.get_size_inches().copy()
    fig.canvas.draw()
    _panels(fig)
    # Remember the requested typography once; repeat saves must not shrink it.
    for text in fig.findobj(match=Text):
        if not hasattr(text, '_atlas_original_size'):
            text._atlas_original_size = text.get_fontsize()
    with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42,
                         'svg.fonttype': 'none', 'font.family': _family()}):
        # Keep the data geometry and the author's panel arrangement. Web export
        # is independent from the publication-size PDF export below.
        _format(fig, paper=False)
        web_options = dict(kwargs, dpi=240, facecolor='white', bbox_inches='tight', pad_inches=.06)
        web_options.pop('format', None)
        for suffix in ('.png', '.svg'):
            _original_save(fig, path.with_suffix(suffix), *args, **web_options)
        # A proportional resize preserves axes positions and aspect ratios.
        # No tight bounding-box crop: the PDF is exactly 183 mm wide.
        paper_width = 183 / 25.4
        paper_height = min(170 / 25.4, paper_width * original_size[1] / original_size[0])
        fig.set_size_inches(paper_width, paper_height, forward=False)
        fig.canvas.draw()
        _format(fig, paper=True)
        paper_options = dict(kwargs, dpi=450, facecolor='white', bbox_inches=None)
        paper_options.pop('format', None)
        _original_save(fig, path.with_suffix('.pdf'), *args, **paper_options)
    fig.set_size_inches(original_size, forward=False)
    _format(fig, paper=False)


def install():
    global _installed
    if _installed:
        return
    mpl.rcParams.update({
        'font.family': _family(), 'font.size': 10, 'axes.labelsize': 10,
        'axes.titlesize': 11, 'legend.fontsize': 9,
        'axes.linewidth': .65, 'axes.grid': False,
        'axes.prop_cycle': mpl.cycler(color=PALETTE),
        'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none',
        'savefig.facecolor': 'white', 'figure.facecolor': 'white',
    })
    Figure.savefig = _export
    _installed = True
