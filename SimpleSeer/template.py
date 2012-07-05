import os
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

