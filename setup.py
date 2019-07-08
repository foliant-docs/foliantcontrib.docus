from setuptools import setup


SHORT_DESCRIPTION = 'Docusaurus backend for Foliant documentation generator.'

try:
    with open('README.md', encoding='utf8') as readme:
        LONG_DESCRIPTION = readme.read()

except FileNotFoundError:
    LONG_DESCRIPTION = SHORT_DESCRIPTION


setup(
    name='foliantcontrib.docus',
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    version='0.1.0',
    author='Daniil Minukhin',
    author_email='moigagoo@live.com',
    url='https://github.com/foliant-docs/foliantcontrib.docus',
    packages=['foliant.backends.docus', 'foliant.preprocessors'],
    package_data={'foliant.backends.docus': ['assets/*']},
    license='MIT',
    platforms='any',
    install_requires=[
        'foliant>=1.0.8',
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Documentation",
        "Topic :: Utilities",
    ]
)
