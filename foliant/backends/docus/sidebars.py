class Document:
    def __init__(self, name: str):
        self.name = name

    def as_obj(self):
        return self.name


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


class Category:
    def __init__(self, name: str):
        self.name = name
        self.items = []

    def add_item(self, item: Document or SubCategory):
        self.items.append(item)

    def as_obj(self):
        obj = {self.name: [i.as_obj() for i in self.items]}
        return obj


class SideBar:
    def __init__(self, name: str):
        self.categories = []

    def add_category(self, category: Category):
        self.categories.append(category)

    def as_obj(self):
        obj = {}
        for cat in self.categories:
            obj.update(cat.as_obj())
        return obj


class SideBars:
    def __init__(self):
        self.sidebars = []

    def add_sidebar(self, sidebar: SideBar):
        self.sidebars.append(sidebar)

    def as_obj(self):
        obj = {}
        counter = 0
        for sb in self.sidebars:
            counter += 1
            obj[f'sb{counter}'] = sb.as_obj()
        return obj


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


def generate_sidebars(title: str, chapters: list):
    if not isinstance(chapters, list):
        raise RuntimeError('chapters should be list!')
    sidebars = SideBars()
    if all(isinstance(c, dict) for c in chapters):  # multi-sidebar syntax
        for sidebar_name, items in chapters.items():
            sidebars.add_sidebar(generate_one_sidebar(sidebar_name, items))
    else:  # implicit one-sidebar syntax
        sidebars.add_sidebar(generate_one_sidebar(title, chapters))
    return sidebars


def generate_one_sidebar(name: str, chapters: list):
    if not isinstance(chapters, list):
        raise RuntimeError('chapters should be list!')
    sidebar = SideBar(name=name)
    if all(isinstance(c, dict) for c in chapters):  # multi-category syntax
        for category_name, chapters_list in chapters.items():
            category = Category(name=category_name)
            fillup_category_items(category, chapters_list)
            sidebar.add_category(category)
    else:  # implicit one-category syntax
        main_category = Category(name)
        fillup_category_items(main_category, chapters)
        sidebar.add_category(main_category)
    return sidebar


def fillup_category_items(category: Category, chapters: list):
    for chapter in chapters:
        if isinstance(chapter, str):
            item = Document(name=chapter)
        elif isinstance(chapter, dict):
            item = SubCategory(name=chapter.keys()[0])
            for subchapter in flatten_seq(chapter.values()[0]):
                SubCategory.add_item(Document(subchapter))
        category.add_item(item)
