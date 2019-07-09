import os
import re
import yaml
from pathlib import PosixPath


YFM_PATTERN = re.compile(r'^\s*---(?P<yaml>.+?\n)---', re.DOTALL)


class Document:
    def __init__(self, name: str, root: PosixPath):
        self.name = name

        # getting ID from YAML Fornt Matter
        with open(root / name, encoding='utf8') as f:
            yfm_match = YFM_PATTERN.match(f.read())
        yfm = yaml.load(yfm_match.group('yaml'), yaml.Loader) if yfm_match else {}
        self.id = yfm.get('id', os.path.splitext(self.name)[0])

    def as_obj(self):
        return self.id


class SubCategory:
    def __init__(self, label: str):
        self.label = label
        self.items = []

    def add_item(self, item: Document):
        self.items.append(item)

    def as_obj(self):
        obj = dict(type='subcategory',
                   label=self.label,
                   ids=[i.as_obj() for i in self.items])
        return obj

    def get_first_doc(self):
        return self.items[0]


class Category:
    def __init__(self, name: str):
        self.name = name
        self.items = []

    def add_item(self, item: Document or SubCategory):
        self.items.append(item)

    def as_obj(self):
        obj = {self.name: [i.as_obj() for i in self.items]}
        return obj

    def get_first_doc(self):
        first = self.items[0]
        if isinstance(first, SubCategory):
            return first.get_first_doc()
        else:
            return first


class SideBar:
    def __init__(self, name: str):
        self.categories = []
        self.name = name

    def add_category(self, category: Category):
        self.categories.append(category)

    def as_obj(self):
        obj = {}
        for cat in self.categories:
            obj.update(cat.as_obj())
        return obj

    def get_first_doc(self):
        return self.categories[0].get_first_doc()


class SideBars:
    def __init__(self):
        self.sidebars = []

    def __iter__(self):
        return iter(self.sidebars)

    def add_sidebar(self, sidebar: SideBar):
        self.sidebars.append(sidebar)

    def as_obj(self):
        obj = {}
        counter = 0
        for sb in self.sidebars:
            counter += 1
            obj[f'sb{counter}'] = sb.as_obj()
        return obj

    def get_first_doc(self):
        return self.sidebars[0].get_first_doc()


def to_list(item):
    result = item
    if isinstance(item, str):
        result = [item]
    elif isinstance(item, dict):
        result = [{k: v} for k, v in item.items()]
    return result


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


def generate_sidebars(title: str, chapters: list, chapters_root: PosixPath):
    chapters = to_list(chapters)
    sidebars = SideBars()
    if all(isinstance(c, dict) for c in chapters):  # multi-sidebar syntax
        for sb_dict in chapters:
            sb_name = list(sb_dict.keys())[0]
            items = list(sb_dict.values())[0]
            sidebars.add_sidebar(generate_one_sidebar(sb_name, items, chapters_root))
    else:  # implicit one-sidebar syntax
        sidebars.add_sidebar(generate_one_sidebar(title, chapters, chapters_root))
    return sidebars


def generate_one_sidebar(name: str, chapters: list, chapters_root: PosixPath):
    chapters = to_list(chapters)
    sidebar = SideBar(name=name)
    if all(isinstance(c, dict) for c in chapters):  # multi-category syntax
        for ctg_dict in chapters:
            ctg_name = list(ctg_dict.keys())[0]
            items = list(ctg_dict.values())[0]
            category = Category(name=ctg_name)
            fillup_category_items(category, items, chapters_root)
            sidebar.add_category(category)
    else:  # implicit one-category syntax
        main_category = Category(name)
        fillup_category_items(main_category, chapters, chapters_root)
        sidebar.add_category(main_category)
    return sidebar


def fillup_category_items(category: Category,
                          chapters: list,
                          chapters_root: PosixPath):
    chapters = to_list(chapters)
    for chapter in chapters:
        if isinstance(chapter, str):
            item = Document(name=chapter, root=chapters_root)
        elif isinstance(chapter, dict):
            item = SubCategory(label=list(chapter.keys())[0])
            for subchapter in flatten_seq(to_list(list(chapter.values())[0])):
                item.add_item(Document(subchapter, root=chapters_root))
        category.add_item(item)
