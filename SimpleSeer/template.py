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
        tgt_brunch = path(output_dir) / vars['package'] / 'brunch_src'

        # Copy vendor directory
        src_vendor = src_brunch / 'vendor'
        tgt_vendor = tgt_brunch / 'vendor'
        if tgt_vendor.exists():
            tgt_vendor.rmtree()
        src_vendor.copytree(tgt_vendor)

        # Copy app directory
        src_app = src_brunch / 'app'
        tgt_app = tgt_brunch / 'app'
        if tgt_app.exists():
            tgt_app.rmtree()
        src_app.copytree(tgt_app)

        # Read the base package.json
        package = json.loads((src_brunch / 'package.json').text())
        package['name'] = vars['package']
        (tgt_brunch / 'package.json').write_text(
            json.dumps(package, indent=2))

        # Link the app
        with tgt_brunch:
            print subprocess.check_output(
                ['npm', 'link'])
