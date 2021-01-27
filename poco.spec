%global cmake_build_dir cmake-build
%global cmake_debug_dir cmake-debug

# build without tests on s390 (runs out of memory during linking due the 2 GB address space)
%ifnarch s390
%bcond_without tests
%endif

%bcond_without samples

# mongodb still available only on little endian arches
%ifarch aarch64 %{arm} %{ix86} x86_64 ppc64le
%bcond_without mongodb
%endif

%if 0%{?fedora} > 27
%global mysql_devel_pkg mariadb-connector-c-devel
%global mysql_lib_dir %{_libdir}/mariadb
%else
%global mysql_devel_pkg mysql-devel
%global mysql_lib_dir %{_libdir}/mysql
%endif

Name:             poco
Version:          1.10.1
Release:          5%{?dist}
Summary:          C++ class libraries for network-centric applications

License:          Boost
URL:              https://pocoproject.org

Source0:          https://github.com/pocoproject/%{name}/archive/%{name}-%{version}-release.tar.gz#/%{name}-%{version}.tar.gz

# Disable the tests that will fail under Koji (mostly network)
Patch0:           disable-tests.patch
# Generated a new test certificate (the old one uses a weak algorithm which
# is rejected by current OpenSSL) using:
# openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 3650
Patch1:           fix-old-test-cert.patch

BuildRequires: make
BuildRequires:    cmake
BuildRequires:    gcc-c++
BuildRequires:    openssl-devel
BuildRequires:    libiodbc-devel
BuildRequires:    %{mysql_devel_pkg}
BuildRequires:    zlib-devel
BuildRequires:    pcre-devel
BuildRequires:    sqlite-devel
BuildRequires:    expat-devel
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
%autosetup -p1 -n %{name}-%{name}-%{version}-release

/bin/sed -i.orig -e 's|$(INSTALLDIR)/lib\b|$(INSTALLDIR)/%{_lib}|g' Makefile
/bin/sed -i.orig -e 's|ODBCLIBDIR = /usr/lib\b|ODBCLIBDIR = %{_libdir}|g' Data/ODBC/Makefile Data/ODBC/testsuite/Makefile
/bin/sed -i.orig -e 's|flags=""|flags="%{optflags}"|g' configure
/bin/sed -i.orig -e 's|SHAREDOPT_LINK  = -Wl,-rpath,$(LIBPATH)|SHAREDOPT_LINK  =|g' build/config/Linux
/bin/sed -i.orig -e 's|"Poco/zlib.h"|<zlib.h>|g' Zip/src/ZipStream.cpp
/bin/sed -i.orig -e 's|PDF|Data/SQLite PDF|' travis/runtests.sh
/bin/sed -i.orig -e 's|#endif|#define POCO_UNBUNDLED 1\n\n#endif|g' Foundation/include/Poco/Config.h

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
%if %{with tests}
  %global poco_tests -DENABLE_TESTS=ON
%endif
%if %{without samples}
  %global poco_samples --no-samples
%endif
%if %{without mongodb}
  %global poco_mongodb -DENABLE_MONGODB=OFF
%endif
%cmake -DPOCO_UNBUNDLED=ON %{?poco_tests} %{?poco_mongodb} -DENABLE_REDIS=OFF -DODBC_INCLUDE_DIR=%{_includedir}/libiodbc -B %{cmake_build_dir}
%make_build -C %{cmake_build_dir}
%cmake -DPOCO_UNBUNDLED=ON %{?poco_tests} %{?poco_mongodb} -DENABLE_REDIS=OFF -DODBC_INCLUDE_DIR=%{_includedir}/libiodbc -DCMAKE_BUILD_TYPE=Debug -B %{cmake_debug_dir}
%make_build -C %{cmake_debug_dir}

%install
%make_install -C %{cmake_debug_dir}
rm -f %{buildroot}%{_prefix}/include/Poco/Config.h.orig
%make_install -C %{cmake_build_dir}
rm -f %{buildroot}%{_prefix}/include/Poco/Config.h.orig

%check
%if %{with tests}
export POCO_BASE="$(pwd)"
pushd %{cmake_build_dir}
ctest -V %{?_smp_mflags} -E "MongoDB|Redis|DataMySQL|DataODBC"
popd
%endif

# -----------------------------------------------------------------------------
%package          foundation
Summary:          The Foundation POCO component

%description foundation
This package contains the Foundation component of POCO. (POCO is a set 
of C++ class libraries for network-centric applications.)
%files foundation
%{_libdir}/libPocoFoundation.so.*


# -----------------------------------------------------------------------------
%package          xml
Summary:          The XML POCO component

%description xml
This package contains the XML component of POCO. (POCO is a set of C++ 
class libraries for network-centric applications.)
%files xml
%{_libdir}/libPocoXML.so.*

# -----------------------------------------------------------------------------
%package          util
Summary:          The Util POCO component

%description util
This package contains the Util component of POCO. (POCO is a set of C++ 
class libraries for network-centric applications.)
%files util
%{_libdir}/libPocoUtil.so.*

# -----------------------------------------------------------------------------
%package          net
Summary:          The Net POCO component

%description net
This package contains the Net component of POCO. (POCO is a set of C++ 
class libraries for network-centric applications.)
%files net
%{_libdir}/libPocoNet.so.*

# -----------------------------------------------------------------------------
%package          crypto
Summary:          The Crypto POCO component

%description crypto
This package contains the Crypto component of POCO. (POCO is a set of 
C++ class libraries for network-centric applications.)
%files crypto
%{_libdir}/libPocoCrypto.so.*

# -----------------------------------------------------------------------------
%package          netssl
Summary:          The NetSSL POCO component

%description netssl
This package contains the NetSSL component of POCO. (POCO is a set of 
C++ class libraries for network-centric applications.)
%files netssl
%{_libdir}/libPocoNetSSL.so.*

# -----------------------------------------------------------------------------
%package          data
Summary:          The Data POCO component

%description data
This package contains the Data component of POCO. (POCO is a set of 
C++ class libraries for network-centric applications.)
%files data
%{_libdir}/libPocoData.so.*

# -----------------------------------------------------------------------------
%package          sqlite
Summary:          The Data/SQLite POCO component

%description sqlite
This package contains the Data/SQLite component of POCO. (POCO is a set 
of C++ class libraries for network-centric applications.)
%files sqlite
%{_libdir}/libPocoDataSQLite.so.*

# -----------------------------------------------------------------------------
%package          odbc
Summary:          The Data/ODBC POCO component

%description odbc
This package contains the Data/ODBC component of POCO. (POCO is a set 
of C++ class libraries for network-centric applications.)
%files odbc
%{_libdir}/libPocoDataODBC.so.*

# -----------------------------------------------------------------------------
%package          mysql
Summary:          The Data/MySQL POCO component

%description mysql
This package contains the Data/MySQL component of POCO. (POCO is a set 
of C++ class libraries for network-centric applications.)
%files mysql
%{_libdir}/libPocoDataMySQL.so.*

# -----------------------------------------------------------------------------
%package          zip
Summary:          The Zip POCO component

%description zip
This package contains the Zip component of POCO. (POCO is a set of C++ 
class libraries for network-centric applications.)
%files zip
%{_libdir}/libPocoZip.so.*

# -----------------------------------------------------------------------------
%package          json
Summary:          The JSON POCO component

%description json
This package contains the JSON component of POCO. (POCO is a set of C++
class libraries for network-centric applications.)
%files json
%{_libdir}/libPocoJSON.so.*

# -----------------------------------------------------------------------------
%if %{with mongodb}
%package          mongodb
Summary:          The MongoDB POCO component

%description mongodb
This package contains the MongoDB component of POCO. (POCO is a set of C++
class libraries for network-centric applications.)
%files mongodb
%{_libdir}/libPocoMongoDB.so.*
%endif

# -----------------------------------------------------------------------------
%package          pagecompiler
Summary:          The PageCompiler POCO component

%description pagecompiler
This package contains the PageCompiler component of POCO. (POCO is a 
set of C++ class libraries for network-centric applications.)
%files pagecompiler
%{_bindir}/cpspc
%{_bindir}/f2cpsp

# -----------------------------------------------------------------------------
%package          encodings
Summary:          The Encodings POCO component

%description encodings
This package contains the Encodings component of POCO. (POCO is a set of C++
class libraries for network-centric applications.)
%files encodings
%{_libdir}/libPocoEncodings.so.*

# -----------------------------------------------------------------------------
%package          jwt
Summary:          The JWT POCO component

%description jwt
This package contains the JWT component of POCO. (POCO is a set of C++
class libraries for network-centric applications.)
%files jwt
%{_libdir}/libPocoJWT.so.*

# -----------------------------------------------------------------------------
%package          debug
Summary:          Debug builds of the POCO libraries

%description debug
This package contains the debug builds of the POCO libraries for 
application testing purposes.
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
%if %{with mongodb}
%{_libdir}/libPocoMongoDBd.so.*
%endif
%{_libdir}/libPocoEncodingsd.so.*
%{_libdir}/libPocoJWTd.so.*

# -----------------------------------------------------------------------------
%package          devel
Summary:          Headers for developing programs that will use POCO

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
%if %{with mongodb}
Requires:         poco-mongodb%{?_isa} = %{version}-%{release}
%endif
Requires:         poco-pagecompiler%{?_isa} = %{version}-%{release}
Requires:         poco-encodings%{?_isa} = %{version}-%{release}
Requires:         poco-jwt%{?_isa} = %{version}-%{release}

Requires:         zlib-devel
Requires:         expat-devel
Requires:         openssl-devel

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
%if %{with mongodb}
%{_libdir}/libPocoMongoDB.so
%{_libdir}/libPocoMongoDBd.so
%endif
%{_libdir}/libPocoEncodings.so
%{_libdir}/libPocoEncodingsd.so
%{_libdir}/libPocoJWT.so
%{_libdir}/libPocoJWTd.so
%{_libdir}/cmake/Poco

# -----------------------------------------------------------------------------
%package          doc
Summary:          The POCO API reference documentation

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
* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.10.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Thu Jul 30 2020 Scott Talbert <swt@techie.net> - 1.10.1-4
- Adapt to cmake out-of-source build changes
- Replace old SSL testsuite cert which was rejected by OpenSSL (#1865242)

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.10.1-3
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.10.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Feb 18 2020 Scott Talbert <swt@techie.net> - 1.10.1-1
- Update to new upstream release 1.10.1 (#1803758)

* Thu Feb 06 2020 Scott Talbert <swt@techie.net> - 1.10.0-1
- Update to new upstream release 1.10.0 (#1795299)

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.9.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Sep 19 2019 Scott Talbert <swt@techie.net> - 1.9.4-1
- Update to new upstream release 1.9.4 (#1753136)

* Wed Aug 21 2019 Scott Talbert <swt@techie.net> - 1.9.3-1
- Update to new upstream release 1.9.3 (#1743851)

* Mon Aug 05 2019 Scott Talbert <swt@techie.net> - 1.9.2-1
- Update to new upstream release 1.9.2

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.9.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.9.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Tue Aug 28 2018 Scott Talbert <swt@techie.net> - 1.9.0-4
- Switch build to use cmake and include cmake files (#1587836)

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.9.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Jun 29 2018 Scott Talbert <swt@techie.net> - 1.9.0-2
- Remove ldconfig scriptlets (no longer needed on F28+)

* Tue Mar 13 2018 Scott Talbert <swt@techie.net> - 1.9.0-1
- New upstream release 1.9.0
- Add subpackage for new Encodings component

* Mon Feb 19 2018 Scott Talbert <swt@techie.net> - 1.8.1-3
- Add missing BR for gcc-c++

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Jan 11 2018 Scott Talbert <swt@techie.net> - 1.8.1-1
- New upstream release 1.8.1
- Remove patches that have been incorporated upstream

* Thu Nov 16 2017 Scott Talbert <swt@techie.net> - 1.8.0.1-1
- New upstream release 1.8.0.1

* Tue Nov 14 2017 Scott Talbert <swt@techie.net> - 1.8.0-1
- New upstream release 1.8.0

* Wed Nov 08 2017 Scott Talbert <swt@techie.net> - 1.7.9p2-1
- New upstream release 1.7.9p2

* Fri Sep 22 2017 Scott Talbert <swt@techie.net> - 1.7.9-2
- Switch from mysql-devel to mariadb-connector-c-devel (#1493654)

* Tue Sep 12 2017 Scott Talbert <swt@techie.net> - 1.7.9-1
- New upstream release 1.7.9

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.7.8p3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Jun 28 2017 Scott Talbert <swt@techie.net> - 1.7.8p3-1
- New upstream release 1.7.8p3

* Thu May 25 2017 Scott Talbert <swt@techie.net> - 1.7.8p2-3
- Add patch from upstream to resolve s390x build failures

* Tue May 23 2017 Scott Talbert <swt@techie.net> - 1.7.8p2-2
- Add openssl-devel as a dependency of poco-devel (#1454462)

* Mon May 08 2017 Scott Talbert <swt@techie.net> - 1.7.8p2-1
- New upstream release 1.7.8p2

* Sun Feb 19 2017 Francis ANDRE <zosrothko@orange.fr> - 1.7.7-2
- Add ignored-tests.patch to ignore failing tests on ppce and armv7hl

* Sat Feb 18 2017 Scott Talbert <swt@techie.net> - 1.7.7-1
- New upstream release 1.7.7

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.7.3-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jun 23 2016 Francis ANDRE <zosrothko@orange.fr> - 1.7.3-5
- Restore POCO_UNBUNDLED definition in Foundation/include/Poco/Config.h
so that user's code compiles without having to define POCO_UNBUNDLED.

* Wed Jun 22 2016 Francis ANDRE <zosrothko@orange.fr> - 1.7.3-4
- Restore POCO_UNBUNDLED definition in Foundation/include/Poco/Config.h

* Fri May 27 2016 Francis ANDRE <zosrothko@orange.fr> - 1.7.3-3
- Restore removal of bundled sources

* Thu May 26 2016 Francis ANDRE <zosrothko@orange.fr> - 1.7.3-3
- Exclude Data/SQLite from testing.

 Wed May 25 2016 Dan Horák <dan[at]danny.cz> - 1.7.3-2
- conditionalize mongodb support

* Sat May 14 2016 Francis ANDRE <zosrothko@orange.fr> - 1.7.3-1
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

