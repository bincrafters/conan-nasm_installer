#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class NASMInstallerConan(ConanFile):
    name = "nasm_installer"
    version = "2.13.02"
    url = "https://github.com/bincrafters/conan-nasm_installer"
    description = "The Netwide Assembler, NASM, is an 80x86 and x86-64 assembler designed for portability " \
                  "and modularity"
    license = "http://repo.or.cz/nasm.git/blob/HEAD:/INSTALL"
    exports_sources = ["LICENSE"]
    settings = "os", "arch", "compiler", "build_type"

    def source(self):
        source_url = "http://www.nasm.us/pub/nasm/releasebuilds/%s/nasm-%s.tar.bz2" % (self.version, self.version)
        tools.get(source_url)
        extracted_dir = "nasm-" + self.version
        os.rename(extracted_dir, "sources")

    def build_vs(self):
        with tools.chdir('sources'):
            vcvars = tools.vcvars_command(self.settings)
            self.run('%s && nmake /f Mkfiles\\msvc.mak' % vcvars)

    def build_configure(self):
        with tools.chdir('sources'):
            args = ['--prefix=%s' % self.package_folder]
            if self.settings.build_type == 'Debug':
                args.append('--disable-optimization')
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args)
            env_build.make()
            env_build.make(args=['install'])

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            self.build_vs()
        else:
            self.build_configure()

    def package(self):
        self.copy(pattern="LICENSE", src='sources')
        if self.settings.compiler == 'Visual Studio':
            self.copy(pattern='*.exe', src='sources', dst='bin', keep_path=False)

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, 'bin'))
