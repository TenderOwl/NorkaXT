pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)
conf.set('profile', profile)

configure_file(
  input: 'norkaxt.in',
  output: 'norkaxt',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr--r--'
)
