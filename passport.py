"""
Passport uses the Tornado template engine to render files, injecting values
from Consul services and kv pairs.

"""
import argparse
from os import path
import sys

from consulate import api
from tornado import template

__version__ = '0.1.0'


class ConsulLoader(template.Loader):

    def __init__(self, root_directory='/', session=None, **kwargs):
        super(ConsulLoader, self).__init__(root_directory, **kwargs)
        self.root = root_directory
        self.session = session

    def _create_template(self, name):
        value = self.session.kv.get(path.join(self.root, name), None)
        if value:
            return template.Template(value, name=name, loader=self)
        else:
            raise KeyError


class Passport(object):

    def __init__(self,
                 host=api.DEFAULT_HOST,
                 port=api.DEFAULT_PORT,
                 dc=None,
                 key=None,
                 template_path=None):
        self.session = api.Consulate(host, port, dc)
        if template_path:
            template_path = path.realpath(template_path)
        self.template = key or template_path
        if key:
            self.loader = ConsulLoader(session=self.session)
        else:
            self.loader = template.Loader('/')

    def render(self):
        t = self.loader.load(self.template)
        namespace = {'consul': self.session}
        return t.generate(**namespace)

    def process(self, destination):
        try:
            value = self.render()
        except KeyError:
            sys.stderr.write('[passport] Error: Key not found: %s\n' %
                             self.template)
            return False
        except IOError:
            sys.stderr.write('[passport] Error: File not found: %s\n' %
                             self.template)
            return False
        with open(destination, 'wb') as handle:
            handle.write(value)
        return True


def main():
    parser = argparse.ArgumentParser(description='Render templates from Consul')

    parser.add_argument('--host',
                        default=api.DEFAULT_HOST,
                        help='IP to the Consul agent. Default: %s' %
                             api.DEFAULT_HOST)
    parser.add_argument('--port',
                        type=int,
                        default=api.DEFAULT_PORT,
                        help='Port of the Consul agent. Default: %s' %
                             api.DEFAULT_PORT)
    parser.add_argument('--datacenter',
                        help='Specify a datacenter')

    source = parser.add_subparsers(help='Specify the template source')

    kv = source.add_parser('kv', help='Fetch the template from Consul KV')
    kv.add_argument('key', type=str, help='The key in the Consul KV store')

    fp = source.add_parser('file',
                           help='Fetch the template from the filesystem')
    fp.add_argument('path', type=str, help='The path to the template file')

    parser.add_argument('destination',
                        help='The path to write the rendered template to')

    args = parser.parse_args()

    if not hasattr(args, 'key') and not hasattr(args, 'path'):
        sys.stderr.write('\nError: you must specify a key or template path\n')
        parser.print_help()
        sys.exit(1)


    passport = Passport(args.host, args.port, args.datacenter,
                        getattr(args, 'key', None),
                        getattr(args, 'path', None))

    if passport.process(args.destination):
        sys.stdout.write('[passport] generated %s\n' % args.destination)


if __name__ == '__main__':
    main()
