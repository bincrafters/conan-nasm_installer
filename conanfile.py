#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import shutil


class NASMInstallerConan(ConanFile):
    name = "nasm_installer"
    version = "2.13.02"
    url = "https://github.com/bincrafters/conan-nasm_installer"
    description = "The Netwide Assembler, NASM, is an 80x86 and x86-64 assembler designed for portability " \
                  "and modularity"
    license = "http://repo.or.cz/nasm.git/blob/HEAD:/INSTALL"
    exports_sources = ["LICENSE"]
    settings = "os_build", "arch_build", "compiler"

    def source(self):
        source_url = "http://www.nasm.us/pub/nasm/releasebuilds/%s/nasm-%s.tar.bz2" % (self.version, self.version)
        tools.get(source_url)
        extracted_dir = "nasm-" + self.version
        os.rename(extracted_dir, "sources")

    def build_vs(self):
        with tools.chdir('sources'):
            with tools.vcvars(self.settings, arch=str(self.settings.arch_build), force=True):
                self.run('nmake /f Mkfiles\\msvc.mak')
                # some libraries look for nasmw (e.g. libmp3lame)
                shutil.copy('nasm.exe', 'nasmw.exe')
                shutil.copy('ndisasm.exe', 'ndisasmw.exe')

    def build_configure(self):
        with tools.chdir('sources'):
            cc = os.environ.get('CC', 'gcc')
            cxx = os.environ.get('CXX', 'g++')
            if self.settings.arch_build == 'x86':
                cc = cc + ' -m32'
                cxx = cxx + ' -m32'
            elif self.settings.arch_build == 'x86_64':
                cc = cc + ' -m64'
                cxx = cxx + ' -m64'
            with tools.environment_append({'CC': cc, 'CXX': cxx}):
                args = ['--prefix=%s' % self.package_folder]
                env_build = AutoToolsBuildEnvironment(self)
                env_build.configure(args=args)
                env_build.make()
                env_build.make(args=['install'])

    def build(self):
        if self.settings.os_build == 'Windows':
            self.build_vs()
        else:
            self.build_configure()

    def package(self):
        self.copy(pattern="LICENSE", src='sources')
        if self.settings.os_build == 'Windows':
            self.copy(pattern='*.exe', src='sources', dst='bin', keep_path=False)

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, 'bin'))

    def package_id(self):
        self.info.settings.compiler = 'Any'
