#!/usr/bin/env python

"""
THIS IS A SCRIPT TO UPDATE THE CODE IN THE ALWAYSDATA HOSTING SERVER. PLEASE DON'T USE IT
ANYWHERE ELSE!

PLACE THIS FILE IN /home/alfanou/ AND USE IT LIKE THIS:
$python update.py dev

IF THE DIRECTORY EXISTS, IT WILL ASSUME IT HAS AN OLDER VERSION OF THE CODE, AND IT WILL
UPDATE IT. IF THE DIRECTORY DOESN'T EXIST, IT WILL CREATE IT AND PREPARE EVERYTHING FOR YOU.
"""

import gzip
import os, sys, tarfile, urllib2
from StringIO import StringIO

# dir constants
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = 'src/'
DJANGO_DIR = os.path.join(SRC_DIR, 'alfanous-django')
DEFAULT_DIR = 'default/'
PUBLIC_DIR = 'public/'
STATIC_DIR = 'static/'
MEDIA_DIR = 'media/'

# git
GIT_URL = 'https://github.com/Alfanous-team/alfanous.git'

# pyparsing
PYP_URL = 'http://cheeseshop.python.org/packages/source/p/pyparsing/pyparsing-2.0.1.tar.gz'
PYP_DIR = 'pyparsing-2.0.1/'
PYP_FILE = 'pyparsing.py'

# default
FILES_TO_LINK = {
  os.path.join(DEFAULT_DIR, PUBLIC_DIR, 'django.fcgi'): os.path.join(PUBLIC_DIR, 'django.fcgi'),
  os.path.join(DEFAULT_DIR, PUBLIC_DIR, '.htaccess'  ): os.path.join(PUBLIC_DIR, '.htaccess'),
  os.path.join(DEFAULT_DIR, PUBLIC_DIR, 'robots.txt' ): os.path.join(PUBLIC_DIR, 'robots.txt'),
  os.path.join(DEFAULT_DIR, 'settings_prod.py'): os.path.join(DJANGO_DIR, 'settings_prod.py'),
}

# messages
USAGE = 'Usage: %s <DIR>'
NO_DIR = 'Directory `%s` doesn\'t exist!'

GIT_CLONING = '== Cloning git repo `%s` into `%s`'
GIT_PULLING = '== Pulling from git repo into `%s`'

PYP_DOWNLOADING = '== Downloading the pyparsing package from `%s` ...'
PYP_DECOMPRESSING = 'Decompressing the pyparsing package..'
PYP_PLACED = '`%s` placed successfully in `%s`'

BUILDING = '== Building...'
UPDATING_QURANIC_CORPUS = '== Updating the Quranic corpus...'
INDEXING_WORDS = '== Indexing words...'
COMPILING_LOCAL = '== Compiling localization PO files...'

LINKING_TO_DEFAULTS = '== Linking to default files:'
LINKING_FILE = '`%s` => `%s`'

COLLECTING_STATIC = '== Collecting static files...'



def ensure_dir(dir_path):
  if not os.path.exists(dir_path):
    os.makedirs(dir_path)

def ensure_file_dir(file_path):
  ensure_dir(os.path.dirname(file_path))



def git_clone(dir):
  os.makedirs(os.path.join(ROOT_DIR, dir))
  print GIT_CLONING % (GIT_URL, dir)
  os.system('git clone %s %s' % (GIT_URL, dir))

def git_pull(dir):
  os.chdir(os.path.join(ROOT_DIR, dir))
  print GIT_PULLING % dir
  os.system('git pull')


def pyp(dir):
  print PYP_DOWNLOADING % PYP_URL,
  package = urllib2.urlopen(PYP_URL)
  print 'Done!'

  pkg_data = StringIO(package.read())
  pkg_data.seek(0)

  # ungzip then untar
  print PYP_DECOMPRESSING
  tar_file = tarfile.TarFile(fileobj=gzip.GzipFile(fileobj=pkg_data))
  pyp_path = os.path.join(ROOT_DIR, dir, SRC_DIR, PYP_FILE)
  print pyp_path
  with open(pyp_path, 'w+') as pyp_file:
    pyp_file.write(tar_file.extractfile(PYP_DIR + PYP_FILE).read())
    print PYP_PLACED % (PYP_FILE, pyp_path)


def build(dir):
  os.chdir(os.path.join(ROOT_DIR, dir))

  # Enable the steps that you need
  print BUILDING; os.system('make build')
  print UPDATING_QURANIC_CORPUS; os.system('make update_quranic_corpus')
  # print INDEXING_WORDS; os.system('make index_word')

def compile_local(dir):
  os.chdir(os.path.join(ROOT_DIR, dir))

  # Compile localization files
  print COMPILING_LOCAL; os.system('make local_mo_compile')


# link to default files from the project
def default(dir):
  print LINKING_TO_DEFAULTS
  for default_path, dest_path in FILES_TO_LINK.iteritems():
    def_abs_path = os.path.join(ROOT_DIR, default_path)
    abs_path = os.path.join(ROOT_DIR, dir, dest_path)
    print LINKING_FILE % (abs_path, def_abs_path)
    ensure_file_dir(abs_path)
    os.system('ln -s "%s" "%s"' % (
      def_abs_path,
      abs_path,
    ))

def static(dir):
  print COLLECTING_STATIC

  # Make sure public static and public media dirs exist.
  ensure_dir(os.path.join(ROOT_DIR, dir, PUBLIC_DIR, STATIC_DIR))
  ensure_dir(os.path.join(ROOT_DIR, dir, PUBLIC_DIR, MEDIA_DIR))

  os.chdir(os.path.join(ROOT_DIR, dir, DJANGO_DIR))
  # TODO: explore the "--link" option. It may save us some disk space.
  os.system('python manage.py collectstatic --noinput --clear')



if __name__ == '__main__':
  args = sys.argv[1:]
  if len(args) != 1:
    print USAGE % sys.argv[0]
    exit(-1)

  dir = args[0]
  absdir = os.path.join(ROOT_DIR, dir)
  if os.path.isdir(absdir):
    # if a local repo already exists => pull
    git_pull(dir)
    print '-' * 30
    compile_local(dir)
    print '-' * 30
    static(dir)

  else:
    # if there is no local repo => clone + get pyparsing + build
    git_clone(dir)
    print '-' * 30
    pyp(dir)
    print '-' * 30
    build(dir)
    print '-' * 30
    default(dir)
    print '-' * 30
    compile_local(dir)
    print '-' * 30
    static(dir)
