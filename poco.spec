
%global poco_src_version 1.4.2p1
%global poco_doc_version 1.4.2p1
%global poco_rpm_release 2

# build without tests on s390 (runs out of memory during linking due the 2 GB address space)
%ifnarch s390
%bcond_without tests
%else
%bcond_with tests
%endif
%bcond_without samples

Name:             poco
Version:          %{poco_src_version}
Release:          %{poco_rpm_release}%{?dist}
Summary:          C++ class libraries for network-centric applications

Group:            Development/Libraries
License:          Boost
URL:              http://www.pocoproject.org

Source0:          http://downloads.sourceforge.net/poco/poco-%{version}-all.tar.bz2
Source1:          http://downloads.sourceforge.net/poco/poco-%{poco_doc_version}-all-doc.tar.gz

BuildRequires:    openssl-devel
BuildRequires:    libiodbc-devel
BuildRequires:    mysql-devel
BuildRequires:    zlib-devel
BuildRequires:    pcre-devel
BuildRequires:    sqlite-devel
BuildRequires:    expat-devel

%description
The POCO C++ Libraries (POCO stands for POrtable COmponents) 
are open source C++ class libraries that simplify and accelerate the 
development of network-centric, portable applications in C++. The 
POCO C++ Libraries are built strictly on standard ANSI/ISO C++, 
including the standard library.

%prep
%setup -q -n poco-%{version}-all -a1
/bin/chmod -R a-x+X poco-%{poco_doc_version}-all-doc
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
rm -f Foundation/src/pcre.h
rm -f Foundation/src/pcre_chartables.c
rm -f Foundation/src/pcre_compile.c
rm -f Foundation/src/pcre_exec.c
rm -f Foundation/src/pcre_fullinfo.c
rm -f Foundation/src/pcre_globals.c
rm -f Foundation/src/pcre_maketables.c
rm -f Foundation/src/pcre_newline.c
rm -f Foundation/src/pcre_ord2utf8.c
rm -f Foundation/src/pcre_study.c
rm -f Foundation/src/pcre_try_flipped.c
rm -f Foundation/src/pcre_valid_utf8.c
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
./configure --prefix=%{_prefix} --unbundled %{?poco_tests} %{?poco_samples} --include-path=%{_includedir}/libiodbc --library-path=%{_libdir}/mysql
make %{?_smp_mflags} STRIP=/bin/true

%install
make install DESTDIR=%{buildroot}
rm -f %{buildroot}%{_prefix}/include/Poco/Config.h.orig

%package          foundation
Summary:          The Foundation POCO component
Group:            System Environment/Libraries

%description foundation
This package contains the Foundation component of POCO. (POCO is a set 
of C++ class libraries for network-centric applications.)

%post foundation -p /sbin/ldconfig

%postun foundation -p /sbin/ldconfig

%files foundation
%defattr(-, root, root, -)
%{_libdir}/libPocoFoundation.so.*

%package          xml
Summary:          The XML POCO component
Group:            System Environment/Libraries

%description xml
This package contains the XML component of POCO. (POCO is a set of C++ 
class libraries for network-centric applications.)

%post xml -p /sbin/ldconfig

%postun xml -p /sbin/ldconfig

%files xml
%defattr(-, root, root, -)
%{_libdir}/libPocoXML.so.*

%package          util
Summary:          The Util POCO component
Group:            System Environment/Libraries

%description util
This package contains the Util component of POCO. (POCO is a set of C++ 
class libraries for network-centric applications.)

%post util -p /sbin/ldconfig

%postun util -p /sbin/ldconfig

%files util
%defattr(-, root, root, -)
%{_libdir}/libPocoUtil.so.*

%package          net
Summary:          The Net POCO component
Group:            System Environment/Libraries

%description net
This package contains the Net component of POCO. (POCO is a set of C++ 
class libraries for network-centric applications.)

%post net -p /sbin/ldconfig

%postun net -p /sbin/ldconfig

%files net
%defattr(-, root, root, -)
%{_libdir}/libPocoNet.so.*

%package          crypto
Summary:          The Crypto POCO component
Group:            System Environment/Libraries

%description crypto
This package contains the Crypto component of POCO. (POCO is a set of 
C++ class libraries for network-centric applications.)

%post crypto -p /sbin/ldconfig

%postun crypto -p /sbin/ldconfig

%files crypto
%defattr(-, root, root, -)
%{_libdir}/libPocoCrypto.so.*

%package          netssl
Summary:          The NetSSL POCO component
Group:            System Environment/Libraries

%description netssl
This package contains the NetSSL component of POCO. (POCO is a set of 
C++ class libraries for network-centric applications.)

%post netssl -p /sbin/ldconfig

%postun netssl -p /sbin/ldconfig

%files netssl
%defattr(-, root, root, -)
%{_libdir}/libPocoNetSSL.so.*

%package          data
Summary:          The Data POCO component
Group:            System Environment/Libraries

%description data
This package contains the Data component of POCO. (POCO is a set of 
C++ class libraries for network-centric applications.)

%post data -p /sbin/ldconfig

%postun data -p /sbin/ldconfig

%files data
%defattr(-, root, root, -)
%{_libdir}/libPocoData.so.*

%package          sqlite
Summary:          The Data/SQLite POCO component
Group:            System Environment/Libraries

%description sqlite
This package contains the Data/SQLite component of POCO. (POCO is a set 
of C++ class libraries for network-centric applications.)

%post sqlite -p /sbin/ldconfig

%postun sqlite -p /sbin/ldconfig

%files sqlite
%defattr(-, root, root, -)
%{_libdir}/libPocoDataSQLite.so.*

%package          odbc
Summary:          The Data/ODBC POCO component
Group:            System Environment/Libraries

%description odbc
This package contains the Data/ODBC component of POCO. (POCO is a set 
of C++ class libraries for network-centric applications.)

%post odbc -p /sbin/ldconfig

%postun odbc -p /sbin/ldconfig

%files odbc
%defattr(-, root, root, -)
%{_libdir}/libPocoDataODBC.so.*

%package          mysql
Summary:          The Data/MySQL POCO component
Group:            System Environment/Libraries

%description mysql
This package contains the Data/MySQL component of POCO. (POCO is a set 
of C++ class libraries for network-centric applications.)

%post mysql -p /sbin/ldconfig

%postun mysql -p /sbin/ldconfig

%files mysql
%defattr(-, root, root, -)
%{_libdir}/libPocoDataMySQL.so.*

%package          zip
Summary:          The Zip POCO component
Group:            System Environment/Libraries

%description zip
This package contains the Zip component of POCO. (POCO is a set of C++ 
class libraries for network-centric applications.)

%post zip -p /sbin/ldconfig

%postun zip -p /sbin/ldconfig

%files zip
%defattr(-, root, root, -)
%{_libdir}/libPocoZip.so.*

%package          pagecompiler
Summary:          The PageCompiler POCO component
Group:            System Environment/Libraries

%description pagecompiler
This package contains the PageCompiler component of POCO. (POCO is a 
set of C++ class libraries for network-centric applications.)

%files pagecompiler
%defattr(-, root, root, -)
%{_bindir}/cpspc
%{_bindir}/f2cpsp

%package          debug
Summary:          Debug builds of the POCO libraries
Group:            Development/Libraries

%description debug
This package contains the debug builds of the POCO libraries for 
application testing purposes.

%post debug -p /sbin/ldconfig

%postun debug -p /sbin/ldconfig

%files debug
%defattr(-, root, root, -)
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
%{_bindir}/cpspcd
%{_bindir}/f2cpspd

%package          devel
Summary:          Headers for developing programs that will use POCO
Group:            Development/Libraries

Requires:         poco-debug = %{version}-%{release}
Requires:         poco-foundation = %{version}-%{release}
Requires:         poco-xml = %{version}-%{release}
Requires:         poco-util = %{version}-%{release}
Requires:         poco-net = %{version}-%{release}
Requires:         poco-crypto = %{version}-%{release}
Requires:         poco-netssl = %{version}-%{release}
Requires:         poco-data = %{version}-%{release}
Requires:         poco-sqlite = %{version}-%{release}
Requires:         poco-odbc = %{version}-%{release}
Requires:         poco-mysql = %{version}-%{release}
Requires:         poco-zip = %{version}-%{release}
Requires:         poco-pagecompiler = %{version}-%{release}

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
%defattr(-, root, root, -)
%doc README NEWS LICENSE CONTRIBUTORS CHANGELOG doc/*
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
%defattr(-, root, root, -)
%doc poco-%{poco_doc_version}-all-doc/*

%changelog
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

