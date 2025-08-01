#
# Conditional build:
%bcond_without	apidocs		# Doxygen based API documentation
%bcond_without	static_libs	# static library
#
Summary:	Application Binary Interface Generic Analysis and Instrumentation Library
Summary(pl.UTF-8):	Biblioteka do ogólnej analizy i porównywania ABI
Name:		libabigail
Version:	2.8
Release:	1
License:	Apache v2.0 with LLVM Exception
Group:		Libraries
Source0:	ftp://sourceware.org/pub/libabigail/%{name}-%{version}.tar.xz
# Source0-md5:	4d2b5b555fd4d097d00753d815b16c80
Patch0:		%{name}-info.patch
URL:		http://www.sourceware.org/libabigail/
BuildRequires:	autoconf >= 2.63
BuildRequires:	automake >= 1:1.11.1
# libctf
BuildRequires:	binutils-devel
BuildRequires:	cpio
%{?with_apidocs:BuildRequires:	doxygen}
BuildRequires:	elfutils-devel >= 0.165
BuildRequires:	libbpf-devel
BuildRequires:	libstdc++-devel >= 6:5
BuildRequires:	libtool >= 2:2.2
BuildRequires:	libxml2-devel >= 1:2.6.22
# for zip-archive (disabled by default)
#BuildRequires:	libzip-devel >= 0.10.1
BuildRequires:	pkgconfig
BuildRequires:	python >= 1:2.6.6
BuildRequires:	python3 >= 1:3.9
BuildRequires:	python3-git
BuildRequires:	python3-libarchive-c
# zstd payload support
BuildRequires:	rpm >= 1:4.16
BuildRequires:	rpm-utils >= 1:4.16
BuildRequires:	sed >= 4.0
%{?with_apidocs:BuildRequires:	sphinx-pdg}
BuildRequires:	tar >= 1:1.22
BuildRequires:	texinfo
BuildRequires:	xxHash-devel >= 0.8.0
BuildRequires:	xz-devel >= 1:5.2.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This is the Application Binary Interface Generic Analysis and
Instrumentation Library.

It aims at constructing, manipulating, serializing and de-serializing
ABI-relevant artifacts.

The set of artifacts of interest is made of quantities like types,
variable, functions and declarations of a given library or program.
For a given library or program this set of quantities is called an
ABI corpus.

This library aims at (among other things) providing a way to compare
two ABI Corpora (plural of corpus), provide detailed information about
their differences, and help build tools to infer interesting
conclusions about these differences.

%description -l pl.UTF-8
Ten pakiet zawiera bibliotekę ABIGAIL (Application Binary Interface
Generic Analysis and Instrumentation Library), służącą do analizy i
porównywania binarnych interfejsów aplikacji (ABI).

Celem jest konstruowanie, operowanie, serializacja i deserializacja
artefaktów związanych z ABI.

Zbiór artefaktów, o których tu mowa, powstaje z wielkości takich jak
typy, zmienne, funkcje i deklaracje z danej biblioteki czy programu.
Dla danej biblioteki czy programu ten zbiór wielkości jest nazywany
ogółem ABI.

Celem biblioteki jest (m.in.) zapewnienie sposobu porównywania dwóch
ogółów ABI, udostępnianie szczegółowych informacji o różnicach oraz
pomoc w tworzeniu narzędzi, potrafiących wysnuwać interesujące wnioski
w oparciu o te różnice.

%package -n bash-completion-libabigail
Summary:	Bash completion for ABIGAIL commands
Summary(pl.UTF-8):	Bashowe uzupełnianie parametrów poleceń ABIGAIL
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	bash-completion >= 2.0

%description -n bash-completion-libabigail
Bash completion for ABIGAIL commands.

%description -n bash-completion-libabigail -l pl.UTF-8
Bashowe uzupełnianie parametrów poleceń ABIGAIL.

%package devel
Summary:	Header files for ABIGAIL library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki ABIGAIL
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	libxml2-devel >= 1:2.6.22

%description devel
Header files for ABIGAIL library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki ABIGAIL.

%package static
Summary:	Static ABIGAIL library
Summary(pl.UTF-8):	Statyczna biblioteka ABIGAIL
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static ABIGAIL library.

%description static -l pl.UTF-8
Statyczna biblioteka ABIGAIL.

%package apidocs
Summary:	API documentation for ABIGAIL library
Summary(pl.UTF-8):	Dokumentacja API biblioteki ABIGAIL 
Group:		Documentation
BuildArch:	noarch

%description apidocs
API documentation for ABIGAIL library.

%description apidocs -l pl.UTF-8
Dokumentacja API biblioteki ABIGAIL.

%prep
%setup -q
%patch -P0 -p1

%{__sed} -i -e '1s,/usr/bin/env python3$,%{__python3},' tools/abidb

%build
# must rebuild, supplied libtool contains RH-specific hack (-specs=/usr/lib/rpm/redhat/redhat-hardened-ld)
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	PYTHON=%{__python} \
	%{?with_apidocs:--enable-apidoc} \
	--enable-bash-completion \
	--enable-cxx11 \
	--enable-deb \
	--disable-fedabipkgdiff \
	--enable-manual \
	--enable-rpm \
	--disable-silent-rules \
	%{!?with_static_libs:--disable-static} \
	--enable-tar
%{__make}

%if %{with apidocs}
%{__make} -C doc apidoc-html-doxygen
%endif

%{__make} -C doc/manuals info man
# generated by Sphinx with no way to align, so do it now
# (summary should start at 41st column)
%{__sed} -i -e 's/\.info//;s/ <SPACER>/\t\t\t/' doc/manuals/texinfo/abigail.info

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# obsoleted by pkg-config
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libabigail.la

# not covered by make install
%{__make} -C doc/manuals install-man-and-info-doc \
	DESTDIR=$RPM_BUILD_ROOT

# install disabled in makefiles (as of 1.6)
install -d $RPM_BUILD_ROOT%{bash_compdir}
cp -p bash-completion/abi* $RPM_BUILD_ROOT%{bash_compdir}

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/postshell
-/sbin/ldconfig
-/usr/sbin/fix-info-dir -c %{_infodir}

%postun	-p /sbin/postshell
-/sbin/ldconfig
-/usr/sbin/fix-info-dir -c %{_infodir}

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog LICENSE.txt NEWS README
%attr(755,root,root) %{_bindir}/abicompat
%attr(755,root,root) %{_bindir}/abidb
%attr(755,root,root) %{_bindir}/abidiff
%attr(755,root,root) %{_bindir}/abidw
%attr(755,root,root) %{_bindir}/abilint
%attr(755,root,root) %{_bindir}/abipkgdiff
%attr(755,root,root) %{_bindir}/kmidiff
%attr(755,root,root) %{_libdir}/libabigail.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libabigail.so.7
%dir %{_libdir}/libabigail
%{_libdir}/libabigail/default.abignore
%{_infodir}/abigail.info*
%{_mandir}/man1/abicompat.1*
%{_mandir}/man1/abidb.1*
%{_mandir}/man1/abidiff.1*
%{_mandir}/man1/abidw.1*
%{_mandir}/man1/abilint.1*
%{_mandir}/man1/abipkgdiff.1*
%{_mandir}/man7/libabigail.7*

%files -n bash-completion-libabigail
%defattr(644,root,root,755)
%{bash_compdir}/abicompat
%{bash_compdir}/abidiff
%{bash_compdir}/abidw
%{bash_compdir}/abilint
%{bash_compdir}/abinilint
%{bash_compdir}/abipkgdiff
%{bash_compdir}/abisym

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libabigail.so
%{_includedir}/libabigail
%{_pkgconfigdir}/libabigail.pc
%{_aclocaldir}/abigail.m4

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libabigail.a
%endif

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
%doc doc/api/html/{search,*.css,*.html,*.js,*.png,*.svg}
%endif
