project('norkaxt',
          version: '0.1.0',
    meson_version: '>= 0.62.0',
          license: 'MIT',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

dependency('glib-2.0', version: '>= 2.66')
dependency('gio-2.0', version: '>= 2.66')
dependency('gdk-pixbuf-2.0')
dependency('gtk4', version: '>= 4.5.0')
dependency('libadwaita-1', version: '>=1.3.0')
dependency('webkitgtk-6.0', version: '>= 2.40.0')


if get_option('profile') == 'development'
  profile = 'Devel'
  app_id_suffix = '.Devel'
  name_suffix = ' (Development)'
  vcs_tag = run_command('git', 'rev-parse', '--short', 'HEAD').stdout().strip()
  if vcs_tag == ''
    version_suffix = '-devel'
  else
    version_suffix = '-@0@'.format (vcs_tag)
  endif
else
  profile = ''
  app_id_suffix = ''
  name_suffix = ''
  version_suffix = ''
endif

application_id = 'com.tenderowl.norka@0@'.format(app_id_suffix)

i18n = import('i18n')
gnome = import('gnome')
python = import('python')
py_installation = python.find_installation('python3')

prefix = get_option('prefix')  # should be /usr
bindir = get_option('bindir')  # should be bin
datadir = get_option('datadir')  # should be /usr/share
pkgdatadir = join_paths(prefix, datadir, meson.project_name())
pythondir = py_installation.get_install_dir()
localedir = join_paths(prefix, get_option('localedir'))


install_subdir(meson.project_name(), install_dir: pythondir)
subdir('bin')
subdir('data')
subdir('po')

gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)
