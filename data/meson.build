pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'norkaxt')
gnome = import('gnome')

blueprints = custom_target('blueprints',
  input: files(
    'ui/help-overlay.blp',
    'ui/window.blp',
    'ui/content_page.blp',
    'ui/note_view_column.blp',
    'ui/notes_list_column.blp',
    'ui/sidebar.blp',
    'ui/sidebar_column.blp',
    'ui/folders_list.blp',
    'ui/notes_list.blp',
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('norkaxt',
  'norkaxt.gresource.xml',
  gresource_bundle: true,
  dependencies: blueprints,
  install: true,
  install_dir: pkgdatadir,
)

desktop_file = i18n.merge_file(
        input: 'com.tenderowl.norka.desktop.in',
       output: 'com.tenderowl.norka.desktop',
         type: 'desktop',
       po_dir: '../po',
      install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils, args: [desktop_file])
endif

appstream_file = i18n.merge_file(
        input: 'com.tenderowl.norka.appdata.xml.in',
       output: 'com.tenderowl.norka.appdata.xml',
       po_dir: '../po',
      install: true,
  install_dir: join_paths(get_option('datadir'), 'appdata')
)

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test('Validate appstream file', appstream_util, args: ['validate', appstream_file])
endif

install_data('com.tenderowl.norka.gschema.xml',
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file',
       compile_schemas,
       args: ['--strict', '--dry-run', meson.current_source_dir()])
endif

subdir('icons')
