import re
import os
import shutil
import yaml
from pathlib import Path
from uuid import uuid1

from foliant.preprocessors.base import BasePreprocessor
from foliant.backends.docus.docus import ASSETS_DIR_NAME


YFM_PATTERN = re.compile(r'^\s*---(?P<yaml>.+?\n)---', re.DOTALL)


class Preprocessor(BasePreprocessor):
    defaults = {'docus_cachedir': Path('.docuscache')}

    _image_pattern = re.compile(r'\!\[(?P<caption>.*)\]\((?P<path>((?!:\/\/).)+)\)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # cleaning assets
        self.assets_dir = \
            self.working_dir / ASSETS_DIR_NAME
        shutil.rmtree(self.assets_dir, ignore_errors=True)
        self.assets_dir.mkdir()

        self.logger = self.logger.getChild('docus')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    def _collect_images(self, content: str, md_file_path: Path) -> str:
        '''Find images, copy them into the docs/assets, and replace the paths
        in the source.

        This is necessary because Docusaurus only allows non-md files to be in
        docs/assets dir.

        :param content: Markdown content
        :param md_file_path: Path to the Markdown file with content ``content``

        :returns: Markdown content with image paths pointing within the source directory
        '''

        self.logger.debug(f'Looking for images in {md_file_path}.')

        def _sub(image):
            image_caption = image.group('caption')
            image_path = (md_file_path.parent / Path(image.group('path'))).resolve()

            self.logger.debug(f'Detected image: caption="{image_caption}", path={image_path}')
            new_name = str(uuid1()) + os.path.splitext(image_path)[1]
            new_path = self.assets_dir / new_name
            shutil.copy(image_path, new_path)
            self.logger.debug(f'Image copied to {new_path}')
            img_ref = f'![{image_caption}](assets/{new_name})'
            self.logger.debug(f'Replacing with: {img_ref}')
            return img_ref

        return self._image_pattern.sub(_sub, content)

    def _cleanup_yfm(self, content: str):
        '''Clean up YAML Front Matter оf the markdown-file.

        Docusaurus shoots warnings if sees unsupported fields in yfm section.
        '''
        ALLOWED = ['id', 'title', 'hide_title', 'sidebar_label',
                   'original_id', 'custom_edit_url']

        def _sub(match):
            old_yfm = yaml.load(match.group('yaml'), yaml.Loader)
            new_yfm = {k: v for k, v in old_yfm.items() if k in ALLOWED}
            if new_yfm:
                yfm_string = yaml.dump(new_yfm,
                                       default_flow_style=False,
                                       allow_unicode=True).strip()
                return f'---\n{yfm_string}\n---'
            else:
                return ''
        return YFM_PATTERN.sub(_sub, content)

    def apply(self):
        for markdown_file_path in self.working_dir.rglob('*.md'):
            with open(markdown_file_path, encoding='utf8') as markdown_file:
                content = markdown_file.read()

            processed_content = self._collect_images(content, markdown_file_path)
            processed_content = self._cleanup_yfm(content)

            if processed_content:
                with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                    markdown_file.write(processed_content)
