#!/usr/bin/env python
"""Run this to recreate output for all themes."""

import os
import argparse


def rebuild(theme):
    # create html files in output dir
    os.system("PELICAN_THEME={0} make html".format(theme))


def rst(themes):
    out = ''
    for t in themes:
        title = '`{0} <http://www.svenkreiss.com/pelican-theme-validator/{0}/output/>`_'.format(t)
        out += title+'\n'
        out += '+'*len(title)+'\n'
        out += '.. image:: https://travis-ci.org/svenkreiss/pelican-theme-validator.svg?branch={0}\n'.format(t)
        out += '    :target: https://travis-ci.org/svenkreiss/pelican-theme-validator/branches\n'
        out += '\n'
    return out


def rst_write(themes):
    # process THEMES.rst
    with open("THEMES.rst", 'w') as f:
        f.write(rst(themes))

    # process README.rst
    readme = open('README.rst', 'r').readlines()
    # cut old list
    begin_marker = readme.index('.. include-list-of-themes\n')
    end_marker = readme.index('.. end-list-of-themes\n')
    if begin_marker and end_marker:
        readme = readme[:begin_marker+1] + readme[end_marker:]
    # write new README and insert new list
    with open('README.rst', 'w') as f_readme:
        for l in readme:
            f_readme.write(l)
            if '.. include-list-of-themes' in l:
                f_readme.write(rst(themes))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("themes", help="path to clone of pelican-themes")
    args = parser.parse_args()

    themes = os.listdir(args.themes)
    # filter out invisibles
    themes = [t for t in themes if t[0] != '.']
    # check it is a directory
    themes = [t for t in themes if os.path.isdir(args.themes+t)]
    print(themes)

    # for tests, just do one
    # themes = themes[0:1]

    rst_write(themes)

    for t in themes:
        print('--- '+t+' ---')
        rebuild(args.themes+t)
        # copy for gh-pages
        os.system('mkdir -p output_all/'+t)
        os.system('cp -r output output_all/'+t)
        # cp the travis file
        os.system('cp travis_for_theme_branches.yml output/.travis.yml')
        # import into branch and git push
        os.system('ghp-import -b {0} {1}'.format(t, 'output/'))
        os.system('git push origin {0}'.format(t))

    os.system('ghp-import -b gh-pages output_all')
    os.system('git push origin gh-pages')


if __name__ == "__main__":
    main()
