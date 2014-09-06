#!/usr/bin/env python
"""Run this to recreate output for all themes."""

import os
import git
import time
import argparse
import subprocess


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


def repo_link(theme_location, remote='origin'):
    """This is a hack to extract an html link from 'git remote -v'."""
    o = subprocess.check_output(['git', 'remote', '-v'],
                                cwd=theme_location).split('\n')
    for l in o:
        if remote in l and '(fetch)' in l:
            url = l.replace(remote, '').replace('(fetch)', '').strip()
            if url.endswith('.git'):
                url = url[:-4]
            if url.startswith('git:'):
                url = 'https:'+url[4:]
            return url


def src_link(theme_name, location):
    url = repo_link(location+'/'+theme_name)

    # if it is from the main pelican-themes repo
    if url == 'https://github.com/getpelican/pelican-themes':
        url += '/tree/master/'+theme_name

    return url


def rst(themes, location):
    out = ''
    for t in themes:
        title = '`{0} <http://www.svenkreiss.com/pelican-theme-validator/{0}/output/>`_'.format(t)
        out += '------\n'
        out += '\n'
        out += title+'\n'
        out += '+'*len(title)+'\n'
        out += '`live preview <http://www.svenkreiss.com/pelican-theme-validator/{0}/output/>`_,\n'.format(t)
        out += '`source on GitHub <{0}>`_,\n'.format(src_link(t, location))
        out += '`html5validator output <http://www.svenkreiss.com/pelican-theme-validator/{0}/html5validator.txt>`_\n'.format(t)
        out += '\n'
        out += '.. image:: http://www.svenkreiss.com/pelican-theme-validator/{0}/status.svg\n'.format(t)
        out += '    :target: http://www.svenkreiss.com/pelican-theme-validator/{0}/html5validator.txt\n'.format(t)
        out += '\n'
        out += '.. image:: http://www.svenkreiss.com/pelican-theme-validator/{0}/screen_capture.png\n'.format(t)
        out += '    :target: http://www.svenkreiss.com/pelican-theme-validator/{0}/output/\n'.format(t)
        out += '    :alt: preview of theme {0}\n'.format(t)
        out += '\n'
    return out


def rst_write(themes, location):
    readme = open('README.rst', 'r').readlines()
    # cut old list
    begin_marker = readme.index('.. include-list-of-themes\n')
    end_marker = readme.index('.. end-list-of-themes\n')
    if begin_marker and end_marker:
        readme = readme[:begin_marker+1] + readme[end_marker:]
    # get new info (if anything goes wrong, this does not overwrite the README)
    info = rst_git_info(location)
    themes_list = rst(themes, location)
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
    parser.add_argument("--skip_rebuild",
                        action="store_true", default=False,
                        help="skip rebuild")
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
        if not args.skip_rebuild:
            rebuild(args.themes+t)
            # copy for gh-pages
            os.system('mkdir -p output_all/'+t)
            os.system('cp -r output output_all/'+t)

        if not args.skip_validation:
            s = os.system('html5validator --root=output_all/'+t+'/output/ --blacklist=templates &> output_all/'+t+'/html5validator.txt')
            # update valid/invalid badge
            if s == 0:
                os.system('cp badges/HTML5-valid-green.svg output_all/'+t+'/status.svg')
            else:
                os.system('cp badges/HTML5-invalid-red.svg output_all/'+t+'/status.svg')

    if not args.skip_rebuild:
        # push gh-pages branch
        os.system('ghp-import -b gh-pages output_all')
        os.system('git push origin gh-pages')

    if not args.skip_screen_captures:
        # Create screen captures with phantomjs (but uses the publicly
        # served websites, so it can only be done at the very end).
        # It have to be the public ones (or at least something starting
        # with https:) for themes that use CDNs and hrefs with '//someurl'.
        os.system('phantomjs screen_captures.js')
        if not args.skip_rebuild:
            # push gh-pages branch
            os.system('ghp-import -b gh-pages output_all')
            os.system('git push origin gh-pages')


if __name__ == "__main__":
    main()
