# build without tests on s390 (runs out of memory during linking due the 2 GB address space)
%ifnarch s390
%bcond_without tests
%else
%bcond_with tests
%endif
%bcond_without samples

Name:             poco
Version:          1.7.3
Release:          1%{?dist}
Summary:          C++ class libraries for network-centric applications

Group:            Development/Libraries
License:          Boost
URL:              http://pocoproject.org

Source0:          http://pocoproject.org/releases/poco-%{version}/poco-%{version}-all.tar.gz

# Some of the samples need to link with the JSON library
Patch0:           samples-link-json.patch
# Disable the tests that will fail under Koji (mostly network)
Patch1:           disable-tests.patch
# Older versions of SQLite don't have SQLITE_BUSY_SNAPSHOT so ifdef it out
Patch2:           sqlite-no-busy-snapshot.patch
# Support PPC64LE
Patch3:           ppc64le.patch

BuildRequires:    openssl-devel
BuildRequires:    libiodbc-devel
BuildRequires:    mysql-devel
BuildRequires:    zlib-devel
BuildRequires:    pcre-devel
BuildRequires:    sqlite-devel
BuildRequires:    expat-devel
BuildRequires:    mongodb-devel
BuildRequires:    libtool-ltdl-devel

# We build poco to unbundle as much as possible, but unfortunately, it uses
# some internal functions of pcre so there are a few files from pcre that are
# still bundled.  See https://github.com/pocoproject/poco/issues/120.
Provides:         bundled(pcre) = 8.35

%description
The POCO C++ Libraries (POCO stands for POrtable COmponents) 
are open source C++ class libraries that simplify and accelerate the 
development of network-centric, portable applications in C++. The 
POCO C++ Libraries are built strictly on standard ANSI/ISO C++, 
including the standard library.

%prep
%setup -q -n poco-%{version}-all
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
/bin/sed -i.orig -e 's|$(INSTALLDIR)/lib\b|$(INSTALLDIR)/%{_lib}|g' Makefile
/bin/sed -i.orig -e 's|ODBCLIBDIR = /usr/lib\b|ODBCLIBDIR = %{_libdir}|g' Data/ODBC/Makefile Data/ODBC/testsuite/Makefile
/bin/sed -i.orig -e 's|flags=""|flags="%{optflags}"|g' configure
/bin/sed -i.orig -e 's|SHAREDOPT_LINK  = -Wl,-rpath,$(LIBPATH)|SHAREDOPT_LINK  =|g' build/config/Linux
/bin/sed -i.orig -e 's|#endif|#define POCO_UNBUNDLED 1\n\n#endif|g' Foundation/include/Poco/Config.h
/bin/sed -i.orig -e 's|"Poco/zlib.h"|<zlib.h>|g' Zip/src/ZipStream.cpp
rm -f Foundation/src/MSG00001.bin
rm -f Foundation/include/Poco/zconf.h
rm -f Foundation/include/Poco/zlib.h
rm -f Foundation/src/adler32.c
rm -f Foundation/src/compress.c
rm -f Foundation/src/crc32.c
rm -f Foundation/src/crc32.h
rm -f Foundation/src/deflate.c
rm -f Foundation/src/deflate.h
rm -f Foundation/src/gzguts.h
rm -f Foundation/src/gzio.c
rm -f Foundation/src/infback.c
rm -f Foundation/src/inffast.c
rm -f Foundation/src/inffast.h
rm -f Foundation/src/inffixed.h
rm -f Foundation/src/inflate.c
rm -f Foundation/src/inflate.h
rm -f Foundation/src/inftrees.c
rm -f Foundation/src/inftrees.h
rm -f Foundation/src/trees.c
rm -f Foundation/src/trees.h
rm -f Foundation/src/zconf.h
rm -f Foundation/src/zlib.h
rm -f Foundation/src/zutil.c
rm -f Foundation/src/zutil.h
# PCRE files that can't be removed due to still being bundled:
#   pcre.h pcre_config.h pcre_internal.h pcre_tables.c pcre_ucd.c
rm -f Foundation/src/pcre_byte_order.c
rm -f Foundation/src/pcre_chartables.c
rm -f Foundation/src/pcre_compile.c
rm -f Foundation/src/pcre_config.c
rm -f Foundation/src/pcre_dfa_exec.c
rm -f Foundation/src/pcre_exec.c
rm -f Foundation/src/pcre_fullinfo.c
rm -f Foundation/src/pcre_get.c
rm -f Foundation/src/pcre_globals.c
rm -f Foundation/src/pcre_jit_compile.c
rm -f Foundation/src/pcre_maketables.c
rm -f Foundation/src/pcre_newline.c
rm -f Foundation/src/pcre_ord2utf8.c
rm -f Foundation/src/pcre_refcount.c
rm -f Foundation/src/pcre_string_utils.c
rm -f Foundation/src/pcre_study.c
rm -f Foundation/src/pcre_try_flipped.c
rm -f Foundation/src/pcre_valid_utf8.c
rm -f Foundation/src/pcre_version.c
rm -f Foundation/src/pcre_xclass.c
rm -f Data/SQLite/src/sqlite3.h
rm -f Data/SQLite/src/sqlite3.c
rm -f XML/include/Poco/XML/expat.h
rm -f XML/include/Poco/XML/expat_external.h
rm -f XML/src/ascii.h
rm -f XML/src/asciitab.h
rm -f XML/src/expat_config.h
rm -f XML/src/iasciitab.h
rm -f XML/src/internal.h
rm -f XML/src/latin1tab.h
rm -f XML/src/nametab.h
rm -f XML/src/utf8tab.h
rm -f XML/src/xmlparse.cpp
rm -f XML/src/xmlrole.c
rm -f XML/src/xmlrole.h
rm -f XML/src/xmltok.c
rm -f XML/src/xmltok.h
rm -f XML/src/xmltok_impl.c
rm -f XML/src/xmltok_impl.h
rm -f XML/src/xmltok_ns.c

%build
%if %{without tests}
  %global poco_tests --no-tests
%endif
%if %{without samples}
  %global poco_samples --no-samples
%endif
./configure --prefix=%{_prefix} --unbundled %{?poco_tests} %{?poco_samples} --include-path=%{_includedir}/libiodbc --library-path=%{_libdir}/mysql --everything
make -s %{?_smp_mflags} STRIP=/bin/true

%install
make install DESTDIR=%{buildroot}
rm -f %{buildroot}%{_prefix}/include/Poco/Config.h.orig

%check
%if %{with tests}
LIBPATH="$(pwd)/lib/Linux/$(uname -m)"
POCO_BASE="$(pwd)"
for COMPONENT in $(cat components); do
    TESTPATH="$COMPONENT/testsuite/bin/Linux/$(uname -m)"
    if [ -x "$TESTPATH/testrunner" ]; then
	pushd "$TESTPATH"
	LD_LIBRARY_PATH="$LIBPATH:." POCO_BASE="$POCO_BASE" ./testrunner -all
	popd
    fi
done
%endif

# -----------------------------------------------------------------------------
%package          foundation
Summary:          The Foundation POCO component
Group:            System Environment/Libraries

%description foundation
This package contains the Foundation component of POCO. (POCO is a set 
of C++ class libraries for network-centric applications.)
%post foundation -p /sbin/ldconfig
%postun foundation -p /sbin/ldconfig
%files foundation
%{_libdir}/libPocoFoundation.so.*


# -----------------------------------------------------------------------------
%package          xml
Summary:          The XML POCO component
Group:            System Environment/Libraries

%description xml
This package contains the XML component of POCO. (POCO is a set of C++ 
class libraries for network-centric applications.)
%post xml -p /sbin/ldconfig
%postun xml -p /sbin/ldconfig
%files xml
%{_libdir}/libPocoXML.so.*

# -----------------------------------------------------------------------------
%package          util
Summary:          The Util POCO component
Group:            System Environment/Libraries

%description util
This package contains the Util component of POCO. (POCO is a set of C++ 
class libraries for network-centric applications.)
%post util -p /sbin/ldconfig
%postun util -p /sbin/ldconfig
%files util
%{_libdir}/libPocoUtil.so.*

# -----------------------------------------------------------------------------
%package          net
Summary:          The Net POCO component
Group:            System Environment/Libraries

%description net
This package contains the Net component of POCO. (POCO is a set of C++ 
class libraries for network-centric applications.)
%post net -p /sbin/ldconfig
%postun net -p /sbin/ldconfig
%files net
%{_libdir}/libPocoNet.so.*

# -----------------------------------------------------------------------------
%package          crypto
Summary:          The Crypto POCO component
Group:            System Environment/Libraries
%description crypto
This package contains the Crypto component of POCO. (POCO is a set of 
C++ class libraries for network-centric applications.)
%post crypto -p /sbin/ldconfig
%postun crypto -p /sbin/ldconfig
%files crypto
%{_libdir}/libPocoCrypto.so.*

# -----------------------------------------------------------------------------
%package          netssl
Summary:          The NetSSL POCO component
Group:            System Environment/Libraries

%description netssl
This package contains the NetSSL component of POCO. (POCO is a set of 
C++ class libraries for network-centric applications.)
%post netssl -p /sbin/ldconfig
%postun netssl -p /sbin/ldconfig
%files netssl
%{_libdir}/libPocoNetSSL.so.*

# -----------------------------------------------------------------------------
%package          data
Summary:          The Data POCO component
Group:            System Environment/Libraries

%description data
This package contains the Data component of POCO. (POCO is a set of 
C++ class libraries for network-centric applications.)
%post data -p /sbin/ldconfig
%postun data -p /sbin/ldconfig
%files data
%{_libdir}/libPocoData.so.*

# -----------------------------------------------------------------------------
%package          sqlite
Summary:          The Data/SQLite POCO component
Group:            System Environment/Libraries

%description sqlite
This package contains the Data/SQLite component of POCO. (POCO is a set 
of C++ class libraries for network-centric applications.)
%post sqlite -p /sbin/ldconfig
%postun sqlite -p /sbin/ldconfig
%files sqlite
%{_libdir}/libPocoDataSQLite.so.*

# -----------------------------------------------------------------------------
%package          odbc
Summary:          The Data/ODBC POCO component
Group:            System Environment/Libraries

%description odbc
This package contains the Data/ODBC component of POCO. (POCO is a set 
of C++ class libraries for network-centric applications.)
%post odbc -p /sbin/ldconfig
%postun odbc -p /sbin/ldconfig
%files odbc
%{_libdir}/libPocoDataODBC.so.*

# -----------------------------------------------------------------------------
%package          mysql
Summary:          The Data/MySQL POCO component
Group:            System Environment/Libraries

%description mysql
This package contains the Data/MySQL component of POCO. (POCO is a set 
of C++ class libraries for network-centric applications.)
%post mysql -p /sbin/ldconfig
%postun mysql -p /sbin/ldconfig
%files mysql
%{_libdir}/libPocoDataMySQL.so.*

# -----------------------------------------------------------------------------
%package          zip
Summary:          The Zip POCO component
Group:            System Environment/Libraries

%description zip
This package contains the Zip component of POCO. (POCO is a set of C++ 
class libraries for network-centric applications.)
%post zip -p /sbin/ldconfig
%postun zip -p /sbin/ldconfig
%files zip
%{_libdir}/libPocoZip.so.*

# -----------------------------------------------------------------------------
%package          json
Summary:          The JSON POCO component
Group:            System Environment/Libraries

%description json
This package contains the JSON component of POCO. (POCO is a set of C++
class libraries for network-centric applications.)
%post json -p /sbin/ldconfig
%postun json -p /sbin/ldconfig
%files json
%{_libdir}/libPocoJSON.so.*

# -----------------------------------------------------------------------------
%package          mongodb
Summary:          The MongoDB POCO component
Group:            System Environment/Libraries

%description mongodb
This package contains the MongoDB component of POCO. (POCO is a set of C++
class libraries for network-centric applications.)
%post mongodb -p /sbin/ldconfig
%postun mongodb -p /sbin/ldconfig
%files mongodb
%{_libdir}/libPocoMongoDB.so.*

# -----------------------------------------------------------------------------
%package          pagecompiler
Summary:          The PageCompiler POCO component
Group:            System Environment/Libraries

%description pagecompiler
This package contains the PageCompiler component of POCO. (POCO is a 
set of C++ class libraries for network-centric applications.)
%files pagecompiler
%{_bindir}/cpspc
%{_bindir}/f2cpsp

# -----------------------------------------------------------------------------
%package          debug
Summary:          Debug builds of the POCO libraries
Group:            Development/Libraries

%description debug
This package contains the debug builds of the POCO libraries for 
application testing purposes.
%post debug -p /sbin/ldconfig
%postun debug -p /sbin/ldconfig
%files debug
%{_libdir}/libPocoFoundationd.so.*
%{_libdir}/libPocoXMLd.so.*
%{_libdir}/libPocoUtild.so.*
%{_libdir}/libPocoNetd.so.*
%{_libdir}/libPocoCryptod.so.*
%{_libdir}/libPocoNetSSLd.so.*
%{_libdir}/libPocoDatad.so.*
%{_libdir}/libPocoDataSQLited.so.*
%{_libdir}/libPocoDataODBCd.so.*
%{_libdir}/libPocoDataMySQLd.so.*
%{_libdir}/libPocoZipd.so.*
%{_libdir}/libPocoJSONd.so.*
%{_libdir}/libPocoMongoDBd.so.*
%{_bindir}/cpspcd
%{_bindir}/f2cpspd

# -----------------------------------------------------------------------------
%package          devel
Summary:          Headers for developing programs that will use POCO
Group:            Development/Libraries

Requires:         poco-debug%{?_isa} = %{version}-%{release}
Requires:         poco-foundation%{?_isa} = %{version}-%{release}
Requires:         poco-xml%{?_isa} = %{version}-%{release}
Requires:         poco-util%{?_isa} = %{version}-%{release}
Requires:         poco-net%{?_isa} = %{version}-%{release}
Requires:         poco-crypto%{?_isa} = %{version}-%{release}
Requires:         poco-netssl%{?_isa} = %{version}-%{release}
Requires:         poco-data%{?_isa} = %{version}-%{release}
Requires:         poco-sqlite%{?_isa} = %{version}-%{release}
Requires:         poco-odbc%{?_isa} = %{version}-%{release}
Requires:         poco-mysql%{?_isa} = %{version}-%{release}
Requires:         poco-zip%{?_isa} = %{version}-%{release}
Requires:         poco-json%{?_isa} = %{version}-%{release}
Requires:         poco-mongodb%{?_isa} = %{version}-%{release}
Requires:         poco-pagecompiler%{?_isa} = %{version}-%{release}

Requires:         zlib-devel
Requires:         expat-devel

%description devel
The POCO C++ Libraries (POCO stands for POrtable COmponents) 
are open source C++ class libraries that simplify and accelerate the 
development of network-centric, portable applications in C++. The 
POCO C++ Libraries are built strictly on standard ANSI/ISO C++, 
including the standard library.

This package contains the header files needed for developing 
POCO applications.

%files devel
%{_includedir}/Poco
%{_libdir}/libPocoFoundation.so
%{_libdir}/libPocoFoundationd.so
%{_libdir}/libPocoXML.so
%{_libdir}/libPocoXMLd.so
%{_libdir}/libPocoUtil.so
%{_libdir}/libPocoUtild.so
%{_libdir}/libPocoNet.so
%{_libdir}/libPocoNetd.so
%{_libdir}/libPocoCrypto.so
%{_libdir}/libPocoCryptod.so
%{_libdir}/libPocoNetSSL.so
%{_libdir}/libPocoNetSSLd.so
%{_libdir}/libPocoData.so
%{_libdir}/libPocoDatad.so
%{_libdir}/libPocoDataSQLite.so
%{_libdir}/libPocoDataSQLited.so
%{_libdir}/libPocoDataODBC.so
%{_libdir}/libPocoDataODBCd.so
%{_libdir}/libPocoDataMySQL.so
%{_libdir}/libPocoDataMySQLd.so
%{_libdir}/libPocoZip.so
%{_libdir}/libPocoZipd.so
%{_libdir}/libPocoJSON.so
%{_libdir}/libPocoJSONd.so
%{_libdir}/libPocoMongoDB.so
%{_libdir}/libPocoMongoDBd.so

# -----------------------------------------------------------------------------
%package          doc
Summary:          The POCO API reference documentation
Group:            Documentation

%description doc
The POCO C++ Libraries (POCO stands for POrtable COmponents) 
are open source C++ class libraries that simplify and accelerate the 
development of network-centric, portable applications in C++. The 
POCO C++ Libraries are built strictly on standard ANSI/ISO C++, 
including the standard library.

This is the complete POCO class library reference documentation in 
HTML format.

%files doc
%doc README NEWS LICENSE CONTRIBUTORS CHANGELOG doc/*

%changelog
* Tue, 10 May 2016 Francis ANDRE <zosrothko@orange.fr> - 1.7.3-1
- New upstream release 1.7.3

* Mon Mar 28 2016 Scott Talbert <swt@techie.net> - 1.7.2-1
- New upstream release 1.7.2

* Sun Mar 20 2016 Scott Talbert <swt@techie.net> - 1.7.1-1
- New upstream release 1.7.1
- Remove patches that have been incorporated upstream

* Thu Feb 04 2016 Scott Talbert <swt@techie.net> - 1.6.1-2
- Add patch for SQLite on EL7
- Add patch for PPC64LE

* Sat Jan 30 2016 Scott Talbert <swt@techie.net> - 1.6.1-1
- New upstream release 1.6.1 (#917362)
- Removed AArch64 patch as it has been incorporated upstream
- Removed superfluous %%defattrs
- Add patches to fix partial PCRE unbundling issues
- Add patch to fix sample linking issues with JSON library
- Enable running of tests in %%check
- Add JSON and MongoDB subpackages

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.2p1-2.10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 1.4.2p1-2.9
- Rebuilt for GCC 5 C++11 ABI change

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.2p1-2.8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Jul 08 2014 Yaakov Selkowitz <yselkowi@redhat.com> - 1.4.2p1-2.7
- Add support for AArch64

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.2p1-2.6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.2p1-2.5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.2p1-2.4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.2p1-2.3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Feb 10 2012 Petr Pisar <ppisar@redhat.com> - 1.4.2p1-2.2
- Rebuild against PCRE 8.30

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.2p1-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sun Dec 18 2011 Dan Horák <dan@danny.cz> - 1.4.p1-2
- build without tests on s390

* Wed Sep 28 2011 Maxim Udushlivy <udushlivy@mail.ru> - 1.4.2p1-1
- Updated for POCO 1.4.2p1. Obsoleted .spec directives were removed.

* Wed Mar 23 2011 Dan Horák <dan@danny.cz> - 1.4.1p1-1.1
- rebuilt for mysql 5.5.10 (soname bump in libmysqlclient)

* Thu Feb 10 2011 Maxim Udushlivy <udushlivy@mail.ru> - 1.4.1p1-1
- Updated for POCO 1.4.1p1.

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.1-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Feb 01 2011 Maxim Udushlivy <udushlivy@mail.ru> - 1.4.1-1
- Updated for POCO 1.4.1.

* Fri Jan 21 2011 Maxim Udushlivy <udushlivy@mail.ru> - 1.4.0-1
- Updated for POCO 1.4.0. The "syslibs" patch was removed.
- This release enables a small part of the PCRE library to be 
compiled-in, which is unavoidable since POCO uses some internal PCRE 
functions for Unicode classification and manipulation.

* Wed Jun 02 2010 Maxim Udushlivy <udushlivy@mail.ru> - 1.3.6p2-2
- Missing dependencies on system header files were fixed.
- Options were added to build POCO without tests and samples.

* Fri May 07 2010 Maxim Udushlivy <udushlivy@mail.ru> - 1.3.6p2-1
- The package was upgraded for the use of POCO version 1.3.6p2.

* Wed Dec 23 2009 Maxim Udushlivy <udushlivy@mail.ru> - 1.3.6p1-1
- The package was upgraded for the use of POCO version 1.3.6p1.
- A new binary package (poco-pagecompiler) is now produced by the 
rpmbuild process.
- The syslibs patch was considerably simplified (based on a new 
"configure" script option which was introduced by POCO developers for 
the maintainers of the POCO Debian package).

* Tue Nov 17 2009 Maxim Udushlivy <udushlivy@mail.ru> - 1.3.5-8
- The "make" invocation command in the %%build section was modified to 
skip premature symbol stripping from retail libraries.

* Mon Nov 16 2009 Maxim Udushlivy <udushlivy@mail.ru> - 1.3.5-7
- A removal of the "Foundation/src/MSG00001.bin" binary file was added 
to the "%%prep" section.
- Values for the top "Summary", "Group" and "%%description" were 
restored.
- A "BuildRoot" tag was added.

* Fri Nov 13 2009 Maxim Udushlivy <udushlivy@mail.ru> - 1.3.5-6
- The generation of the "poco" metapackage is now suppressed.
- A comment for the patch was added.
- The usage of %% symbol in the %%changelog section was fixed.

* Wed Nov 11 2009 Maxim Udushlivy <udushlivy@mail.ru> - 1.3.5-5
- A patch "poco-1.3.5-syslibs.patch" was added. The build process now 
does not use bundled versions of the system libraries (zlib, pcre, 
sqlite and expat).

* Fri Nov 06 2009 Maxim Udushlivy <udushlivy@mail.ru> - 1.3.5-4
- The name of "poco-testing" subpackage was reverted to "poco-debug".
- The "Release" field was fixed to use "%%{?dist}".
- The ".*DS_Store" files removal was moved to the %%prep section.
- Fedora compilation flags (%%{optflags}) are now injected into the 
"configure" script.

* Wed Nov 04 2009 Maxim Udushlivy <udushlivy@mail.ru> - 1.3.5-3
- Each POCO component is now put in its own binary package. The "poco" 
package is now a meta package.
- Option "-s" was removed from the "make" invocation commands.
- "perl" was replaced by "sed" for string substitutions in Makefile's.

* Tue Jun 23 2009 Maxim Udushlivy <udushlivy@mail.ru> - 1.3.5-2
- The "poco-extra" subpackage was split into separate "poco-odbc", 
"poco-mysql" and "poco-zip".
- The "poco-debug" subpackage was renamed to "poco-testing".
- The "poco-doc" subpackage with the API reference documentation 
was added.

* Sat Jun 20 2009 Maxim Udushlivy <udushlivy@mail.ru> - 1.3.5-1
- The first version.

