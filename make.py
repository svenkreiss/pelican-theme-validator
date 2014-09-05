#!/usr/bin/env python
"""Run this to recreate output for all themes."""

import os
import argparse


def rebuild(theme):
    # create html files in output dir
    os.system("PELICAN_THEME={0} make html".format(theme))


def rst(themes, output="THEMES.rst"):
    with open(output, 'w') as f:
        for t in themes:
            f.write(t+'\n')
            f.write('+'*len(t)+'\n')
            f.write('.. image:: https://travis-ci.org/svenkreiss/pelican-theme-validator.svg?branch={0}\n'.format(t))
            f.write('\n')


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
    themes = themes[10:11]

    rst(themes)

    for t in themes:
        print('--- '+t+' ---')
        rebuild(args.themes+t)
        # cp the travis file
        os.system("cp travis_for_theme_branches.yml output/.travis.yml")
        # import into branch and git push
        os.system("ghp-import -b {0} {1}".format(t, "output/"))
        os.system("git push origin {0}".format(t))


if __name__ == "__main__":
    main()
