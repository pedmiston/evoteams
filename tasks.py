import sys
from glob import glob

from invoke import task
from unipath import Path

import graphdb


PROJ = Path(__file__).absolute().parent
R_PKG = Path(PROJ, 'data')
REPORTS = Path(PROJ, 'reports')
TOTEMS = Path(PROJ, 'experiment')
ITEM_IMAGES = Path(R_PKG, 'inst/extdata/items')
TOTEMS_RAW_DATA = Path(R_PKG, 'data-raw/totems')


@task
def load(ctx):
    """Load the neo4j graph db with totems data."""
    graphdb.load(delete_first=True)

@task
def install(ctx):
    """Install the totems R package."""
    ctx.run('cd {} && Rscript -e "devtools::install()"'.format(R_PKG))

@task
def make(ctx, name, reset_before=False, open_after=False, verbose=False):
    """Compile RMarkdown documents.

    Examples:

      $ inv make list      # see available reports
      $ inv make all       # run all reports
      $ inv make totems -o # make totems.Rmd and open output after

    """
    if name == 'list':
        print('Available docs:')
        available_docs = get_available_docs()
        for rmd in available_docs:
            print(' - %s' % rmd.stem)
        sys.exit()

    docs = get_available_docs(name)
    failed = []

    cmd = 'Rscript -e "rmarkdown::render({!r})"'
    for doc in docs:
        if reset_before:
            # Run prerequisite task
            reset(ctx, doc, verbose=verbose)

        result = ctx.run(cmd.format(str(doc)), echo=verbose, warn=True)

        if not result.ok:
            failed.append(str(doc))

        if open_after and result.ok:
            output_file = Path(doc.parent, '{}.html'.format(doc.stem))
            ctx.run('open {}'.format(output_file), echo=verbose)

    print('The following docs had errors:')
    for doc in failed:
        print(' - {}'.format(doc))

@task
def reset(ctx, name, verbose=False):
    """Clear the cache and outputs of RMarkdown reports."""
    docs = get_available_docs(name)

    for doc in docs:
        cache_dir = Path(doc.parent, '.cache.{}/'.format(doc.stem))
        if cache_dir.isdir():
            cache_dir.rmtree()

        figs_dir = Path(doc.parent, '{}-figs'.format(doc.stem))
        if figs_dir.isdir():
            figs_dir.rmtree()

        code_str = Path(doc.parent, 'code*')
        ctx.run('rm -rf {} {} {}'.format(cache_dir, figs_dir, code_str),
                echo=verbose)


@task(help=dict(name='If name is "list", list available figure names.'))
def img(ctx, name, output=None, ext='png', dpi=300):
    """Create an image and put it in the "img/" dir."""
    EXTDATA = Path(R_PKG, 'inst/extdata/')
    if name == 'list':
        print('\n'.join(EXTDATA.listdir('*.gv', names_only=True)))
        return
    src = Path(EXTDATA, '{}.gv'.format(name))
    dst = Path('img/{}.{}'.format(output or name, ext))
    ctx.run('dot -T{} -Gdpi={} -o {} {}'.format(ext, dpi, dst, src))


def get_available_docs(name=''):
    available_docs = [Path(rmd) for rmd in
                      glob('{proj}/docs/**/*.Rmd'.format(proj=PROJ),
                           recursive=True)
                      if Path(rmd).isfile()]

    if name == '':
        rmds = available_docs
    elif Path(name).isfile():
        rmds = [Path(name)]
    else:
        # name is a glob
        rmds = [Path(rmd) for rmd in
                glob('{proj}/docs/**/{name}*.Rmd'.format(proj=PROJ, name=name),
                     recursive=True)
                if Path(rmd).isfile()]

    return rmds
