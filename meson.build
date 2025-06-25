project('norka',
          version: '0.1.0',
    meson_version: '>= 1.0.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)


author = 'tenderowl'
domain = 'com'
gitrepo = 'https://github.com/'+author+'/'+meson.project_name()
website = 'https://tenderowl.com'
app_id = '.'.join([domain, author, meson.project_name()])

i18n = import('i18n')
gnome = import('gnome')
pymod = import('python')

python = pymod.find_installation('python3')
pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / meson.project_name()
gnome = import('gnome')
pythondir = get_option('prefix') / python.get_install_dir()

if get_option('profile') == 'development'
  profile = 'Devel'
  vcs_tag = run_command(
    ['git', 'rev-parse', '--short', 'HEAD'],
    check: false
  ).stdout().strip()
  if vcs_tag == ''
    version_suffix = '-devel'
  else
    version_suffix = '-@0@'.format (vcs_tag)
  endif
else
  profile = ''
  version_suffix = ''
endif

subdir('bin')
subdir('data')
subdir('po')

install_subdir(
  meson.project_name(),
  install_dir: pythondir
)

gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)
