import os
import json
import shutil
import subprocess

import pkg_resources
from path import path
from paste.script.templates import Template, var
here = os.getcwd()

class SimpleSeerProjectTemplate(Template):
    _template_dir = 'paster_templates/seer_project'
    summary = 'SimpleSeer Installation Template'
    vars = [
        var('version', 'Version (like 0.1)',
            default='0.1'),
        var('description', 'One-line description of the package',
            default='SimpleSeer Project'),
        var('long_description', 'Multi-line description (in reST)',
            default='SimpleSeer Project'),
        var('keywords', 'Space-separated keywords/tags',
            default=''),
        var('author', 'Author name', default=''),
        var('author_email', 'Author email', default=''),
        var('url', 'URL of homepage', default=''),
        var('license_name', 'License name', default='Apache'),
        var('zip_safe', 'True/False: if the package can be distributed as a .zip file',
            default=False),
        ]

    def pre(self, command, output_dir, vars):
        base = pkg_resources.resource_filename(
            'SimpleSeer', 'static')
        base_esc = base.replace('/', '\\/')
        static = json.dumps({
                '/': (path(output_dir) / vars['package'] / 'static').abspath()})

        vars.update(
            brunch_base=base,
            brunch_base_app_regex='/^%s\/app/' % base_esc,
            brunch_base_vendor_regex='/^%s\/vendor/' % base_esc,
            static=static)

    def post(self, command, output_dir, vars):
        src_brunch = path(pkg_resources.resource_filename(
            'SimpleSeer', 'static'))
        src_public = path(pkg_resources.resource_filename(
            'SimpleSeer', 'static/public'))
        tgt_brunch = (path(output_dir) / vars['package'] / 'brunch_src').abspath()
        tgt_public = (path(output_dir) / vars['package'] / 'static').abspath()

        # Ensure that brunch build has been run in the source
        with src_brunch:
            print subprocess.check_output(['brunch', 'build'])

        # Create package.json
        package = json.loads((src_brunch / 'package.json').text())
        package['name'] = vars['package']
        (tgt_brunch / 'package.json').write_text(
            json.dumps(package, indent=2))

        # Copy (built) seer.js & seer.css
        overwrite(
            src_public / 'javascripts/seer.js',
            tgt_brunch / 'vendor/javascripts/seer.js')
        overwrite(
            src_public / 'stylesheets/seer.css',
            tgt_brunch / 'vendor/stylesheets/seer.css')

        # Link the app
        with tgt_brunch:
            print subprocess.check_output(
                ['npm', 'link'])

        # Ensure that brunch build has been run in the target
        with tgt_brunch:
            print subprocess.check_output(['brunch', 'build'])


def overwrite(src, dst):
    if dst.exists(): dst.remove()
    src.copy(dst)

def overlay(src, dst, force=False):
    for src_fn in src.walk():
        rel_fn = src.relpathto(src_fn)
        dst_fn = dst / rel_fn
        if src_fn.isdir():
            dst_fn.mkdir_p()
            continue
        if overwrite:
            overwrite(src_fn, dst_fn)
        else:
            src_fn.copy(dst_fn)
