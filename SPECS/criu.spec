%global py_prefix python3
%global py_binary %{py_prefix}

# With annobin enabled, CRIU does not work anymore. It seems CRIU's
# parasite code breaks if annobin is enabled.
%undefine _annotated_build

Name: criu
Version: 3.15
Release: 4%{?dist}
Provides: crtools = %{version}-%{release}
Obsoletes: crtools <= 1.0-2
Summary: Tool for Checkpoint/Restore in User-space
License: GPLv2
URL: http://criu.org/
Source0: http://download.openvz.org/criu/criu-%{version}.tar.bz2
Source1: criu-tmpfiles.conf
# Fix to work on CPUs with larger XSAVE area (Sapphire Rapids)
# backported to CRIU 3.15
Patch0: almost-d739260c57576c636759afb312340fa3827312f6.patch
BuildRequires: gcc
BuildRequires: systemd
BuildRequires: libnet-devel
BuildRequires: protobuf-devel protobuf-c-devel %{py_prefix}-devel libnl3-devel libcap-devel
BuildRequires: asciidoc xmlto
BuildRequires: perl-interpreter
BuildRequires: libselinux-devel
BuildRequires: gnutls-devel
BuildRequires: nftables-devel
BuildRequires: make
# Checkpointing containers with a tmpfs requires tar
Recommends: tar

# user-space and kernel changes are only available for x86_64, arm,
# ppc64le, aarch64 and s390x
# https://bugzilla.redhat.com/show_bug.cgi?id=902875
ExclusiveArch: x86_64 %{arm} ppc64le aarch64 s390x

%description
criu is the user-space part of Checkpoint/Restore in User-space
(CRIU), a project to implement checkpoint/restore functionality for
Linux in user-space.

%package devel
Summary: Header files and libraries for %{name}
Requires: %{name} = %{version}-%{release}
Requires: criu-libs = %{version}-%{release}

%description devel
This package contains header files and libraries for %{name}.

%package libs
Summary: Libraries for %{name}
Requires: %{name} = %{version}-%{release}

%description libs
This package contains the libraries for %{name}

%package -n %{py_prefix}-%{name}
%{?python_provide:%python_provide %{py_prefix}-%{name}}
Summary: Python bindings for %{name}
Requires: %{py_prefix}-protobuf
Obsoletes: python2-criu < 3.10-1

%description -n %{py_prefix}-%{name}
%{py_prefix}-%{name} contains Python bindings for %{name}.

%package -n crit
Summary: CRIU image tool
Requires: %{py_prefix}-%{name} = %{version}-%{release}

%description -n crit
crit is a tool designed to decode CRIU binary dump files and show
their content in human-readable form.

%prep
%setup -q
%patch -P 0 -p1

%build
# %{?_smp_mflags} does not work
# -fstack-protector breaks build
CFLAGS+=`echo %{optflags} | sed -e 's,-fstack-protector\S*,,g'` make V=1 WERROR=0 PREFIX=%{_prefix} RUNDIR=/run/criu PYTHON=%{py_binary}
make docs V=1

%install
make install-criu DESTDIR=$RPM_BUILD_ROOT PREFIX=%{_prefix} LIBDIR=%{_libdir}
make install-lib DESTDIR=$RPM_BUILD_ROOT PREFIX=%{_prefix} LIBDIR=%{_libdir} PYTHON=%{py_binary}
make install-man DESTDIR=$RPM_BUILD_ROOT PREFIX=%{_prefix} LIBDIR=%{_libdir}
mkdir -p %{buildroot}%{_tmpfilesdir}
install -m 0644 %{SOURCE1} %{buildroot}%{_tmpfilesdir}/%{name}.conf
install -d -m 0755 %{buildroot}/run/%{name}/

# remove static libs
rm $RPM_BUILD_ROOT%{_libdir}/*.a
rm -rf $RPM_BUILD_ROOT%{_libexecdir}/%{name}

%files
%{_sbindir}/%{name}
%{_mandir}/man8/criu.8*
%{_mandir}/man1/compel.1*
%dir /run/%{name}
%{_tmpfilesdir}/%{name}.conf
%doc README.md COPYING

%files devel
%{_includedir}/criu
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc

%files libs
%{_libdir}/*.so.*

%files -n %{py_prefix}-%{name}
%{python3_sitelib}/pycriu/*
%{python3_sitelib}/*egg-info

%files -n crit
%{_bindir}/crit
%doc %{_mandir}/man1/crit.1*

%changelog
* Fri Jun 09 2023 Adrian Reber <areber@redhat.com> - 3.15.4
- added patch to support CRIU on Sapphire Rapids
- Resolves: #2203296

* Fri Aug 06 2021 Jindrich Novy <jnovy@redhat.com> - 3.15-3
- add Requires: criu-libs = %%{version}-%%{release} in criu-devel
- add gating tests
- Related: #1934415

* Tue Jul 20 2021 Jindrich Novy <jnovy@redhat.com> - 3.15-2
- add -devel and -libs subpackages
- Resolves: #1971718

* Wed Nov 04 2020 Jindrich Novy <jnovy@redhat.com> - 3.15-1
- update to https://github.com/checkpoint-restore/criu/releases/tag/v3.15
- Related: #1883490

* Mon May 25 2020 Jindrich Novy <jnovy@redhat.com> - 3.14-2
- fix "Need to fix bugs found by coverity."
- Related: #1821193

* Tue May 12 2020 Jindrich Novy <jnovy@redhat.com> - 3.14-1
- synchronize containter-tools 8.3.0 with 8.2.1
- Related: #1821193

* Mon May 13 2019 Adrian Reber <adrian@lisas.de> - 3.12-9
- Added additional fixup patches for the socket labelling

* Sat May 04 2019 Adrian Reber <adrian@lisas.de> - 3.12-8
- Patch for socket labelling has changed upstream

* Mon Apr 29 2019 Adrian Reber <adrian@lisas.de> - 3.12-4
- Applied patch to correctly restore socket()s

* Sat Apr 27 2019 Adrian Reber <adrian@lisas.de> - 3.12-3
- Correctly exclude libs and devel for RHEL

* Thu Apr 25 2019 Adrian Reber <adrian@lisas.de> - 3.12-2
- Updated to official 3.12

* Tue Apr 23 2019 Adrian Reber <adrian@lisas.de> - 3.12-0.1
- Updated to 3.12 (pre-release)
- Create libs subpackage
- Build against SELinux (Fedora and RHEL8)
- Build against libbsd (Fedora)

* Thu Feb 14 2019 Adrian Reber <areber@redhat.com> -  3.11-2
- Updated to 3.11
- Removed upstreamed patches
- Added patch for gcc-9

* Tue Dec 11 2018 Adrian Reber <adrian@lisas.de> - 3.10-7
- Fix 'criu check --feature link_nsid' with more than 10 interfaces (#1652442)

* Tue Dec 11 2018 Adrian Reber <adrian@lisas.de> - 3.10-6
- Make sure no iptables rules are left after restore (#1652471)

* Tue Oct 30 2018 Adrian Reber <adrian@lisas.de> - 3.10-5
- Added Recommends: tar
  It is necessary when checkpointing containers with a tmpfs

* Mon Jul 16 2018 Adrian Reber <adrian@lisas.de> - 3.10-4
- Add patch to fix errors with read-only runc

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.10-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Jul 11 2018 Adrian Reber <adrian@lisas.de> - 3.10-2
- Disable annobin as it seems to break CRIU

* Tue Jul 10 2018 Adrian Reber <adrian@lisas.de> - 3.10-1
- Update to 3.10 (#1599710)
- Switch to python3

* Wed Jun 06 2018 Adrian Reber <adrian@lisas.de> - 3.9-2
- Simplify ExclusiveArch now that there is no more F26

* Fri Jun 01 2018 Adrian Reber <adrian@lisas.de> - 3.9-1
- Update to 3.9

* Tue Apr 03 2018 Adrian Reber <adrian@lisas.de> - 3.8.1-1
- Update to 3.8.1

* Thu Mar 22 2018 Adrian Reber <adrian@lisas.de> - 3.8-2
- Bump release for COPR

* Wed Mar 14 2018 Adrian Reber <adrian@lisas.de> - 3.8-1
- Update to 3.8

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.7-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Feb 03 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 3.7-4
- Switch to %%ldconfig_scriptlets

* Fri Jan 12 2018 Adrian Reber <adrian@lisas.de> - 3.7-3
- Fix python/python2 dependencies accross all branches

* Wed Jan 03 2018 Merlin Mathesius <mmathesi@redhat.com> - 3.7-2
- Cleanup spec file conditionals

* Sat Dec 30 2017 Adrian Reber <adrian@lisas.de> - 3.7-1
- Update to 3.7

* Fri Dec 15 2017 Iryna Shcherbina <ishcherb@redhat.com> - 3.6-2
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Thu Oct 26 2017 Adrian Reber <adrian@lisas.de> - 3.6-1
- Update to 3.6

* Wed Oct 18 2017 Adrian Reber <adrian@lisas.de> - 3.5-5
- Added patch to fix build on Fedora rawhide aarch64

* Tue Oct 10 2017 Adrian Reber <areber@redhat.com> - 3.5-4
- Upgrade imported manpages to 3.5

* Mon Oct 09 2017 Adrian Reber <areber@redhat.com> - 3.5-3
- Fix ExclusiveArch on RHEL

* Mon Oct 02 2017 Adrian Reber <adrian@lisas.de> - 3.5-2
- Merge RHEL and Fedora spec file

* Thu Sep 28 2017 Adrian Reber <adrian@lisas.de> - 3.5-1
- Update to 3.5 (#1496614)

* Sun Aug 27 2017 Adrian Reber <adrian@lisas.de> - 3.4-1
- Update to 3.4 (#1483774)
- Removed upstreamed patches
- Added s390x (#1475719)

* Sat Aug 19 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 3.3-5
- Python 2 binary package renamed to python2-criu
  See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Jul 20 2017 Adrian Reber <adrian@lisas.de> - 3.3-2
- Added patches to handle changes in glibc

* Wed Jul 19 2017 Adrian Reber <adrian@lisas.de> - 3.3-1
- Update to 3.3

* Fri Jun 30 2017 Adrian Reber <adrian@lisas.de> - 3.2.1-2
- Added patches to handle unified hierarchy and new glibc

* Wed Jun 28 2017 Adrian Reber <adrian@lisas.de> - 3.2.1-1
- Update to 3.2.1-1

* Tue Jun 13 2017 Orion Poplawski <orion@cora.nwra.com> - 3.1-2
- Rebuild for protobuf 3.3.1

* Mon May 22 2017 Adrian Reber <adrian@lisas.de> - 3.1-1
- Update to 3.1

* Tue Apr 25 2017 Adrian Reber <adrian@lisas.de> - 3.0-1
- Update to 3.0

* Thu Mar 09 2017 Adrian Reber <adrian@lisas.de> - 2.12-1
- Update to 2.12

* Fri Feb 17 2017 Adrian Reber <adrian@lisas.de> - 2.11.1-1
- Update to 2.11.1

* Thu Feb 16 2017 Adrian Reber <adrian@lisas.de> - 2.11-1
- Update to 2.11

* Mon Feb 13 2017 Adrian Reber <adrian@lisas.de> - 2.10-4
- Added patch to fix build on ppc64le

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.10-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Jan 23 2017 Orion Poplawski <orion@cora.nwra.com> - 2.10-2
- Rebuild for protobuf 3.2.0

* Mon Jan 16 2017 Adrian Reber <adrian@lisas.de> - 2.10-1
- Update to 2.10

* Mon Dec 12 2016 Adrian Reber <adrian@lisas.de> - 2.9-1
- Update to 2.9
- Added crit manpage to crit subpackage

* Sat Nov 19 2016 Orion Poplawski <orion@cora.nwra.com> - 2.8-2
- Rebuild for protobuf 3.1.0

* Tue Nov 15 2016 Adrian Reber <adrian@lisas.de> - 2.8-1
- Update to 2.8
- Dropped 'mount_resolve_path()' patch

* Wed Oct 19 2016 Adrian Reber <adrian@lisas.de> - 2.7-2
- Added upstream patch to fix #1381351
  ("criu: mount_resolve_path(): criu killed by SIGSEGV")

* Wed Oct 19 2016 Adrian Reber <adrian@lisas.de> - 2.7-1
- Update to 2.7

* Tue Sep 13 2016 Adrian Reber <adrian@lisas.de> - 2.6-1
- Update to 2.6

* Tue Aug 30 2016 Adrian Reber <adrian@lisas.de> - 2.5-1
- Update to 2.5

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Tue Jul 12 2016 Adrian Reber <adrian@lisas.de> - 2.4-1
- Update to 2.4

* Tue Jun 14 2016 Adrian Reber <areber@redhat.com> - 2.3-1
- Update to 2.3
- Copy man-page from Fedora 24 for RHEL

* Mon May 23 2016 Adrian Reber <adrian@lisas.de> - 2.2-1
- Update to 2.2

* Tue Apr 12 2016 Adrian Reber <adrian@lisas.de> - 2.1-2
- Remove crtools symbolic link

* Mon Apr 11 2016 Adrian Reber <adrian@lisas.de> - 2.1-1
- Update to 2.1

* Wed Apr 06 2016 Adrian Reber <areber@redhat.com> - 2.0-2
- Merge changes from Fedora

* Thu Mar 10 2016 Andrey Vagin <avagin@openvz.org> - 2.0-1
- Update to 2.0

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Dec 07 2015 Adrian Reber <adrian@lisas.de> - 1.8-1
- Update to 1.8

* Mon Nov 02 2015 Adrian Reber <adrian@lisas.de> - 1.7.2-1
- Update to 1.7.2

* Mon Sep 7 2015 Andrey Vagin <avagin@openvz.org> - 1.7-1
- Update to 1.7

* Thu Sep 3 2015 Andrey Vagin <avagin@openvz.org> - 1.6.1-3
- Build only for power64le

* Thu Sep 3 2015 Andrey Vagin <avagin@openvz.org> - 1.6.1-2
- Build for aarch64 and power64

* Thu Aug 13 2015 Adrian Reber <adrian@lisas.de> - 1.6.1-1
- Update to 1.6.1
- Merge changes for RHEL packaging

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Jun 09 2015 Adrian Reber <areber@redhat.com> - 1.6-1.1
- adapt to RHEL7

* Mon Jun 01 2015 Andrew Vagin <avagin@openvz.org> - 1.6-1
- Update to 1.6

* Thu Apr 30 2015 Andrew Vagin <avagin@openvz.org> - 1.5.2-2
- Require protobuf-python and python-ipaddr for python-criu

* Tue Apr 28 2015 Andrew Vagin <avagin@openvz.org> - 1.5.2
- Update to 1.5.2

* Sun Apr 19 2015 Nikita Spiridonov <nspiridonov@odin.com> - 1.5.1-2
- Create python-criu and crit subpackages

* Tue Mar 31 2015 Andrew Vagin <avagin@openvz.org> - 1.5.1
- Update to 1.5.1

* Sat Dec 06 2014 Adrian Reber <adrian@lisas.de> - 1.4-1
- Update to 1.4

* Tue Sep 23 2014 Adrian Reber <adrian@lisas.de> - 1.3.1-1
- Update to 1.3.1 (#1142896)

* Tue Sep 02 2014 Adrian Reber <adrian@lisas.de> - 1.3-1
- Update to 1.3
- Dropped all upstreamed patches
- included pkgconfig file in -devel

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Aug 07 2014 Andrew Vagin <avagin@openvz.org> - 1.2-4
- Include inttypes.h for PRI helpers

* Thu Aug 07 2014 Andrew Vagin <avagin@openvz.org> - 1.2-3
- Rebuilt for https://bugzilla.redhat.com/show_bug.cgi?id=1126751

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Feb 28 2014 Adrian Reber <adrian@lisas.de> - 1.2-1
- Update to 1.2
- Dropped all upstreamed patches

* Tue Feb 04 2014 Adrian Reber <adrian@lisas.de> - 1.1-4
- Create -devel subpackage

* Wed Dec 11 2013 Andrew Vagin <avagin@openvz.org> - 1.0-3
- Fix the epoch of crtools

* Tue Dec 10 2013 Andrew Vagin <avagin@openvz.org> - 1.0-2
- Rename crtools to criu #1034677

* Wed Nov 27 2013 Andrew Vagin <avagin@openvz.org> - 1.0-1
- Update to 1.0

* Thu Oct 24 2013 Andrew Vagin <avagin@openvz.org> - 0.8-1
- Update to 0.8

* Tue Sep 10 2013 Andrew Vagin <avagin@openvz.org> - 0.7-1
- Update to 0.7

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 24 2013 Andrew Vagin <avagin@openvz.org> - 0.6-3
- Delete all kind of -fstack-protector gcc options

* Wed Jul 24 2013 Andrew Vagin <avagin@openvz.org> - 0.6-3
- Added arm macro to ExclusiveArch

* Wed Jul 03 2013 Andrew Vagin <avagin@openvz.org> - 0.6-2
- fix building on ARM
- fix null pointer dereference

* Tue Jul 02 2013 Adrian Reber <adrian@lisas.de> - 0.6-1
- updated to 0.6
- upstream moved binaries to sbin
- using upstream's make install

* Tue May 14 2013 Adrian Reber <adrian@lisas.de> - 0.5-1
- updated to 0.5

* Fri Feb 22 2013 Adrian Reber <adrian@lisas.de> - 0.4-1
- updated to 0.4

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Jan 22 2013 Adrian Reber <adrian@lisas.de> - 0.3-3
- added ExclusiveArch blocker bug

* Fri Jan 18 2013 Adrian Reber <adrian@lisas.de> - 0.3-2
- improved Summary and Description

* Mon Jan 14 2013 Adrian Reber <adrian@lisas.de> - 0.3-1
- updated to 0.3
- fix building Documentation/

* Tue Aug 21 2012 Adrian Reber <adrian@lisas.de> - 0.2-2
- remove macros like %%{__mkdir_p} and %%{__install}
- add comment why it is only x86_64

* Tue Aug 21 2012 Adrian Reber <adrian@lisas.de> - 0.2-1
- initial release
