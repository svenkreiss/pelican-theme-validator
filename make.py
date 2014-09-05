#!/usr/bin/env python
"""Run this to recreate output for all themes."""

import os
import git
import time
import argparse


def rebuild(theme):
    # create html files in output dir
    os.system("PELICAN_THEME={0} make html".format(theme))


def rst_git_info(location):
    repo = git.Repo(location)
    headcommit = repo.heads[0].commit
    out = 'Based on commit ``'+headcommit.id_abbrev+'`` from ' + \
          time.strftime('%a, %d %b %Y %H:%M', headcommit.committed_date) + \
          '.\n\n'
    return out


def rst(themes):
    out = ''
    for t in themes:
        title = '`{0} <http://www.svenkreiss.com/pelican-theme-validator/{0}/output/>`_'.format(t)
        out += '------\n'
        out += '\n'
        out += title+'\n'
        out += '+'*len(title)+'\n'
        out += '.. image:: http://www.svenkreiss.com/pelican-theme-validator/{0}/status.svg\n'.format(t)
        out += '    :target: http://www.svenkreiss.com/pelican-theme-validator/{0}/html5validator.txt\n'.format(t)
        out += '\n'
        out += '`preview <http://www.svenkreiss.com/pelican-theme-validator/{0}/output/>`_,\n'.format(t)
        out += '`source on GitHub <http://github.com/getpelican/pelican-themes/tree/master/{0}/>`_,\n'.format(t)
        out += '`html5validator output <http://www.svenkreiss.com/pelican-theme-validator/{0}/html5validator.txt>`_\n'.format(t)
        out += '\n'
        out += '.. image:: http://www.svenkreiss.com/pelican-theme-validator/{0}/screen_capture.png\n'.format(t)
        out += '    :target: http://www.svenkreiss.com/pelican-theme-validator/{0}/output/\n'.format(t)
        out += '    :alt: preview of theme {0}\n'.format(t)
        out += '\n'
    return out


def rst_write(themes, location):
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
    # get new info (if anything goes wrong, this does not overwrite the README)
    info = rst_git_info(location)
    themes_list = rst(themes)
    # write new README and insert new list
    with open('README.rst', 'w') as f_readme:
        for l in readme:
            f_readme.write(l)
            if '.. include-list-of-themes' in l:
                f_readme.write(info)
                f_readme.write(themes_list)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("themes", help="path to clone of pelican-themes")
    parser.add_argument("--skip_validation",
                        action="store_true", default=False,
                        help="skip validation and git pushes on individual "
                        "branches")
    parser.add_argument("--skip_screen_captures",
                        action="store_true", default=False,
                        help="skip taking screen captures")
    args = parser.parse_args()

    themes = os.listdir(args.themes)
    # filter out invisibles
    themes = [t for t in themes if t[0] != '.']
    # check it is a directory
    themes = [t for t in themes if os.path.isdir(args.themes+t)]
    print(themes)

    # for tests, just do one
    # themes = themes[0:1]

    rst_write(themes, args.themes)

    for t in themes:
        print('--- '+t+' ---')
        rebuild(args.themes+t)
        # copy for gh-pages
        os.system('mkdir -p output_all/'+t)
        os.system('cp -r output output_all/'+t)

        if not args.skip_validation:
            s = os.system('html5validator --root=output_all/'+t+'/output/ --blacklist=templates &> output_all/'+t+'/html5validator.txt')
            if s == 0:
                os.system('cp badges/HTML5-valid-green.svg output_all/'+t+'/status.svg')
            else:
                os.system('cp badges/HTML5-invalid-red.svg output_all/'+t+'/status.svg')

    if not args.skip_screen_captures:
        # create screen captures with phantomjs
        os.system('phantomjs screen_captures.js')

    # push gh-pages branch
    os.system('ghp-import -b gh-pages output_all')
    os.system('git push origin gh-pages')


if __name__ == "__main__":
    main()
