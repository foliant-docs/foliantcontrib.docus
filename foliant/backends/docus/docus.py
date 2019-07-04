import shutil
import json

from pathlib import Path, PosixPath
from subprocess import run, PIPE, STDOUT, CalledProcessError
from pkg_resources import resource_filename

from foliant.utils import spinner
from foliant.backends.base import BaseBackend

from .sidebars import generate_sidebars
from .index import INDEX_HTML


def flatten_seq(seq):
    """convert a sequence of embedded sequences into a plain list"""
    result = []
    vals = seq.values() if type(seq) == dict else seq
    for i in vals:
        if type(i) in (dict, list):
            result.extend(flatten_seq(i))
        else:
            result.append(i)
    return result


class FlatChapters:
    """
    Helper class converting chapter list of complicated structure
    into a plain list of chapter names or path to actual md files
    in the src dir.
    """

    def __init__(self,
                 chapters: list,
                 parent_dir: PosixPath = Path('src')):
        self._chapters = chapters
        self._parent_dir = parent_dir

    def __len__(self):
        return len(self.flat)

    def __getitem__(self, ind: int):
        return self.flat[ind]

    def __contains__(self, item: str):
        return item in self.flat

    def __iter__(self):
        return iter(self.flat)

    @property
    def flat(self):
        """Flat list of chapter file names"""
        return flatten_seq(self._chapters)

    @property
    def list(self):
        """Original chapters list"""
        return self._chapters

    @property
    def paths(self):
        """Flat list of PosixPath objects relative to project root."""
        return (self._parent_dir / chap for chap in self.flat)


class Backend(BaseBackend):
    targets = ('site', 'docus')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._docus_config = self.config.get('backend_config', {}).get('docus', {})
        self._cachedir = Path(self._docus_config.get('cache_dir', '.docuscache'))
        self._srcdir = self.project_path / self.config['src_dir']
        self._docus_site_dir_name = f'{self._docus_config.get("slug", self.get_slug())}.docus'

        self._docus_project_dir_name = f'{self._docus_site_dir_name}.src'

        # self.required_preprocessors_after = {
        #     'mkdocs': {
        #         'mkdocs_project_dir_name': self._mkdocs_project_dir_name
        #     }
        # },

        self.logger = self.logger.getChild('docus')

        self.logger.debug(f'Backend inited: {self.__dict__}')

    def _create_cache_dir(self):
        if self._cachedir.exists() and\
                (self._cachedir / 'docs').exists() and\
                (self._cachedir / 'website').exists():
            return  # docus project already inited
        else:
            self._cachedir.mkdir(exist_ok=True)
            try:
                run(
                    'docusaurus-init',
                    shell=True,
                    check=True,
                    stdout=PIPE,
                    stderr=STDOUT,
                    cwd=str(self._cachedir)
                )
                return
            except CalledProcessError as exception:
                raise RuntimeError(f'Build failed: {exception.output.decode()}')

    def _sync_docs(self):
        # preparing docs
        docs_path = self._cachedir / 'docs'
        shutil.rmtree(docs_path, ignore_errors=True)  # cleaning docs
        docs_path.mkdir()

        title = self.config.get('title', 'main')

        chapters = FlatChapters(self.config['chapters'])
        for chapter in chapters:
            file_to_copy = self._srcdir / chapter
            dest_folder = (docs_path / chapter).parent
            if not dest_folder.exists():
                dest_folder.mkdir(parents=True)
            shutil.copy(str(file_to_copy), str(dest_folder))

        # genereate sidebars.json
        sidebars = generate_sidebars(title,
                                     self.config['chapters'])
        with open(self._cachedir / 'website' / 'sidebars.json',
                  'w', encoding='utf8') as f:
            json.dump(sidebars.as_obj(), f)

        # replace #siteConfig.js
        shutil.copyfile(resource_filename(__name__,
                                          'assets/siteConfig.js'),
                        self._cachedir / 'website/siteConfig.js')
        config = {'title': title, **self._docus_config}

        # generate siteConf.json
        with open(self._cachedir / 'website' / 'siteConf.json', 'w') as f:
            json.dump(config, f)

        # clean up pages
        pages_path = self._cachedir / 'website' / 'pages'
        shutil.rmtree(pages_path, ignore_errors=True)
        pages_path.mkdir()

        # add new redirect index page
        with open(self._cachedir / 'website' / 'static' / 'index.html', 'w') as f:
            f.write(INDEX_HTML.format(title=title, doc_id='index'))

    def make(self, target: str) -> str:
        with spinner(f'Making {target} with Docusaurus', self.logger, self.quiet, self.debug):
            try:
                self._create_cache_dir()
                self._sync_docs()
                if target == 'docus':
                    shutil.rmtree(self._docus_project_dir_name, ignore_errors=True)
                    shutil.copytree(self._cachedir, self._docus_project_dir_name)

                    return self._docus_project_dir_name

                elif target == 'site':
                    try:
                        shutil.rmtree(self._docus_site_dir_name, ignore_errors=True)
                        run(
                            'docusaurus-build',
                            shell=True,
                            check=True,
                            stdout=PIPE,
                            stderr=STDOUT,
                            cwd=str(self._cachedir / 'website')
                        )
                        shutil.copytree(self._cachedir / 'website' / 'build',
                                        self._docus_site_dir_name)

                        return self._docus_site_dir_name

                    except CalledProcessError as exception:
                        raise RuntimeError(f'Build failed: {exception.output.decode()}')
                else:
                    raise ValueError(f'Docusaurus cannot make {target}')

            except Exception as exception:
                raise type(exception)(f'Build failed: {exception}')
