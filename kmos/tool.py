#!/usr/bin/env python

#    Copyright 2009-2012 Max J. Hoffmann (mjhoffmann@gmail.com)
#    This file is part of kmos.
#
#    kmos is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    kmos is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with kmos.  If not, see <http://www.gnu.org/licenses/>.

import optparse
import os
import sys

usage = {}
usage['all'] = """kmos help all
    Display documentation for all commands.
                """
usage['benchmark'] = """kmos benchmark
    Run 1 mio. kMC steps on model in current directory
    and report runtime.
                     """

usage['build'] = """kmos build
    Build kmc_model.so from *f90 files in the
    current directory.
                 """
usage['help'] = """kmos help <command>
    Print usage information for the given command.
                """
usage['export'] = """kmos export <xml-file> [<export-path>]
    Take a kmos xml-file and export all generated
    source code to the export-path. There try to
    build the kmc_model.so.
                    """
usage['export-settings'] = """kmos export-settings <xml-file> [<export-path>]
    Take a kmos xml-file and export kmc_settings.py
    to the export-path.
                    """
usage['export-view'] = """kmos export-view <xml-file>
    Export an XML file, compile and run the simulation.
                        """
usage['edit'] = """kmos edit <xml-file>
    Open the kmos xml-file in a GUI to edit
    the model.
                """
usage['import'] = """kmos import <xml-file>
    Take a kmos xml-file and open an ipython shell
    with the project_tree imported as pt.
                  """
usage['rebuild'] = """kmos rebuild
    Export code and rebuild binary module from XML
    information included in kmc_settings.py in
    current directory.
                    """

usage['run'] = """kmos run
    Open an interactive shell and create a KMC_Model in it
               """

usage['view'] = """kmos view
    Take a kmc_model.so and kmc_settings.py in the
    same directory and start to simulate the
    model visually.
                 """


def main():
    import os
    parser = optparse.OptionParser(
        'Usage: %prog [help] ('
        + '|'.join(sorted(usage.keys()))
        + ') [options]')

    parser.add_option('-s', '--source-only',
                      dest='source_only',
                      action='store_true',
                      default=False)

    parser.add_option('-p', '--path-to-f2py',
                      dest='path_to_f2py',
                      default='f2py')

    parser.add_option('-f', '--fcompiler',
                     dest='fcompiler',
                     default=os.environ.get('F2PY_FCOMPILER', 'gfortran'))

    options, args = parser.parse_args()

    if len(args) < 1:
        parser.error('Command expected')

    if args[0] == 'benchmark':
        from sys import path
        path.append(os.path.abspath(os.curdir))
        nsteps = 1000000
        from time import time
        from kmos.run import KMC_Model
        model = KMC_Model(print_rates=False, banner=False)
        time0 = time()
        model.do_steps(nsteps)
        print('%s steps took %.2f seconds' % (nsteps, time() - time0))
    elif args[0] == 'build':
        from kmos.utils import build
        build(options)
    elif args[0] == 'edit':
        from kmos.gui import main
        main()
    elif args[0] == 'export-settings':
        import kmos.types
        import kmos.io
        from kmos.utils import build
        from glob import glob
        import shutil
        from kmos.io import ProcListWriter

        if len(args) < 2:
            parser.error('XML file and export path expected.')
        if len(args) < 3:
            out_dir = os.path.splitext(args[1])[0]
            print('No export path provided. Exporting to %s' % out_dir)
            args.append(out_dir)

        xml_file = args[1]
        export_dir = args[2]
        project = kmos.types.Project()
        project.import_xml_file(xml_file)

        writer = ProcListWriter(project, export_dir)
        writer.write_settings()

    elif args[0] == 'export':
        import kmos.types
        import kmos.io
        from kmos.utils import build
        from glob import glob
        import shutil
        if len(args) < 2:
            parser.error('XML file and export path expected.')
        if len(args) < 3:
            out_dir = os.path.splitext(args[1])[0]
            print('No export path provided. Exporting to %s' % out_dir)
            args.append(out_dir)

        xml_file = args[1]
        export_dir = os.path.join(args[2], 'src')

        project = kmos.types.Project()
        project.import_xml_file(xml_file)

        kmos.io.export_source(project, export_dir)

        cwd = os.path.abspath(os.curdir)
        if ((os.name == 'posix'
           and os.uname()[0] == 'Linux')
           or os.name == 'nt') \
           and not options.source_only:
            os.chdir(export_dir)
            build(options)
            for out in glob('kmc_*'):
                if os.path.exists('../%s' % out):
                    overwrite = raw_input(('Should I overwrite existing %s ?'
                                           '[y/N]  ') % out).lower()
                    if overwrite.startswith('y'):
                        os.remove('../%s' % out)
                        shutil.move(out, '..')
                else:
                    shutil.move(out, '..')

    elif args[0] == 'export-settings':
        import kmos.io
        import os
        pt = kmos.io.import_xml_file(args[1])
        if len(args) < 3:
            out_dir = os.path.splitext(args[1])[0]
            print('No export path provided. Exporting kmc_settings.py to %s'
                   % out_dir)
            args.append(out_dir)

        if not os.path.exists(args[2]):
            os.mkdir(args[2])
        elif not os.path.isdir(args[2]):
            raise UserWarning("Cannot overwrite %s; Exiting;" % args[2])
        writer = kmos.io.ProcListWriter(pt, args[2])
        writer.write_settings()

    elif args[0] == 'export-view':
        out_dir = os.path.splitext(args[1])[0]
        print('No export path provided. Exporting to %s' % out_dir)
        args.append(out_dir)
        os.system('kmos-export-program %s %s' % (args[1], args[2]))
        os.chdir(out_dir)
        os.system('kmos-view')

    elif args[0] == 'help':
        if len(args) < 2:
            parser.error('Which help do you  want?')
        if args[1] == 'all':
            for command in sorted(usage):
                print(usage[command])
        elif args[1] in usage:
            print('Usage: %s\n' % usage[args[1]])
        else:
            print("Command not known or not documented.")

    elif args[0] == 'import':
        import kmos.io
        try:
            import numpy as np
        except:
            pass
        pt = kmos.io.import_xml_file(args[1])
        import IPython
        if hasattr(IPython, 'release') and \
           map(int, IPython.release.version.split('.')) >= [0, 11]:
            from IPython.frontend.terminal.embed \
                import InteractiveShellEmbed as sh
        else:
            from IPython.Shell import IPShellEmbed as sh
        sh(banner='Note: pt = kmos.io.import_xml(\'%s\')' % args[1])()

    elif args[0] == 'rebuild':
        from tempfile import mktemp
        if not os.path.exists('kmc_model.so'):
            print('No kmc_model.so found, exiting.')
            exit()

        if not os.path.exists('kmc_settings.py'):
            print('No kmc_settings.py found, exiting.')
            exit()

        from kmos.run import KMC_Model

        model = KMC_Model(print_rates=False, banner=False)

        tempfile = mktemp()
        f = file(tempfile, 'w')
        f.write(model.xml())
        f.close()

        os.system('rm kmc_*')
        os.system('kmos export %s .' % tempfile)
        os.remove(tempfile)

    elif args[0] == 'run':
        from kmos.run import KMC_Model
        model = KMC_Model(print_rates=False)
        import IPython
        if hasattr(IPython, 'release') and \
           map(int, IPython.release.version.split('.')) >= [0, 11]:
            from IPython.frontend.terminal.embed \
                import InteractiveShellEmbed as sh
        else:
            from IPython.Shell import IPShellEmbed as sh
        sh(banner='Note: model = KMC_Model(print_rates=False)')()

    elif args[0] == 'view':
        from sys import path
        path.append(os.path.abspath(os.curdir))
        from kmos.view import main
        main()

    else:
        parser.error('Command not understood.')
