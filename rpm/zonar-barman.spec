%global pybasever 2.7
%global zonar_python_installs /opt/zonar/python
%global __python %{zonar_python_installs}/python-%{pybasever}/bin/python%{pybasever}

%{!?pybasever: %define pybasever %(%{__python} -c "import sys;print(sys.version[0:3])")}
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

# The original name from upstream sources.
%global original_name barman

Summary:	Backup and Recovery Manager for PostgreSQL
Name:		zonar-barman%{pybasever}
Version:	1.2.1
Release:	z4%{?dist}
License:	GPLv3
Group:		Applications/Databases
Url:		http://www.pgbarman.org/
Source0:    zonar-barman-%{version}.tar.gz
BuildRoot: 	%{_tmppath}/%{name}-%{version}-%{release}-buildroot-%(%{__id_u} -n)
BuildArch:	noarch
Vendor:		2ndQuadrant Italia (Devise.IT S.r.l.) <info@2ndquadrant.it>
BuildRequires: zonar-python%{pybasever}
Requires:   zonar-python%{pybasever}, zonar-python-psycopg%{pybasever}, zonar-python-argh%{pybasever} >= 0.21.2, zonar-python-argcomplete%{pybasever}, zonar-python-dateutil%{pybasever}, zonar-python-fabric%{pybasever}
Provides:   zonar-barman%{pybasever}

%description
Barman (backup and recovery manager) is an administration
tool for disaster recovery of PostgreSQL servers written in Python.
It allows to perform remote backups of multiple servers
in business critical environments and help DBAs during the recovery phase.
Barman's most wanted features include backup catalogs, retention policies,
remote recovery, archiving and compression of WAL files and backups.
Barman is written and maintained by PostgreSQL professionals 2ndQuadrant.

%prep
%setup -n zonar-barman-%{version} -q

%build
%{__python} setup.py build
cat > barman.cron << EOF
# m h  dom mon dow   user     command
  * *    *   *   *   barman   [ -x %{_bindir}/barman ] && %{_bindir}/barman -q cron
EOF
cat > barman.logrotate << EOF
/var/log/barman/barman.log {
    missingok
    notifempty
    create 0600 barman barman
}
EOF

%install
%{__python} setup.py install -O1 --skip-build --root %{buildroot} --record=INSTALLED_FILES
mkdir -p %{buildroot}%{_sysconfdir}/bash_completion.d
mkdir -p %{buildroot}%{_sysconfdir}/cron.d/
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d/
mkdir -p %{buildroot}/var/lib/barman/
mkdir -p %{buildroot}/var/log/barman/
mkdir -p %{buildroot}%{_mandir}/man1/
mkdir -p %{buildroot}%{_mandir}/man5/
mkdir -p %{buildroot}%{_bindir}
gzip doc/barman.1
gzip doc/barman.5
gzip doc/barman_run_backups.1
install -pm 644 doc/barman.1.gz %{buildroot}%{_mandir}/man1/barman.1.gz
install -pm 644 doc/barman.5.gz %{buildroot}%{_mandir}/man5/barman.5.gz
install -pm 644 doc/barman_run_backups.1.gz %{buildroot}%{_mandir}/man1/barman_run_backups.1.gz
install -pm 644 doc/barman.conf %{buildroot}%{_sysconfdir}/barman.conf
install -pm 644 scripts/barman.bash_completion %{buildroot}%{_sysconfdir}/bash_completion.d/barman
install -pm 644 barman.cron %{buildroot}%{_sysconfdir}/cron.d/barman
install -pm 644 barman.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/barman
install -pm 755 scripts/barman_run_backups %{buildroot}%{_bindir}/barman_run_backups
touch %{buildroot}/var/log/barman/barman.log

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES
%defattr(-,root,root)
%doc INSTALL NEWS README
%doc %{_mandir}/man1/%{original_name}.1.gz
%doc %{_mandir}/man5/%{original_name}.5.gz
%doc %{_mandir}/man1/barman_run_backups.1.gz
%config(noreplace) %{_sysconfdir}/bash_completion.d/
%config(noreplace) %{_sysconfdir}/%{original_name}.conf
%config(noreplace) %{_sysconfdir}/cron.d/%{original_name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{original_name}
%attr(700,barman,barman) %dir /var/lib/%{original_name}
%attr(755,barman,barman) %dir /var/log/%{original_name}
%attr(600,barman,barman) %ghost /var/log/%{original_name}/%{original_name}.log
%attr(755,root,root) %{_bindir}/barman_run_backups

%pre
# puppet should handle creating the barman user and group,
# including home directory, .pgpass, etc. Just make sure the
# user exists.
getent passwd barman > /dev/null || exit 1

%post
ln -sf %{zonar_python_installs}/python-%{pybasever}/bin/barman %{_bindir}/barman

%postun
rm %{_bindir}/barman

%changelog
* Thu May 16 2013 - Kevin Hochhalter <kevin.hochhalter@zonarsystems.com> 1.2.1-z4
- Add ssh_host option.

* Wed May 10 2013 - Kevin Hochhalter <kevin.hochhalter@zonarsystems.com> 1.2.1-z3
- Set keepalive in Ssh class to 30 seconds.
- Update run method to allow an arbitrary tuple of valid return codes.

* Wed Apr 17 2013 - Kevin Hochhalter <kevin.hochhalter@zonarsystems.com> 1.2.1-z1
- New Zonar release 1.2.1
- Use fabric for remote commands.

* Thu Jan 31 2013 - Marco Neciarini <marco.nenciarini@2ndquadrant.it> 1.2.0-1
- New release 1.2.0
- Depend on python-argh >= 0.21.2 and python-argcomplete

* Thu Nov 29 2012 - Marco Neciarini <marco.nenciarini@2ndquadrant.it> 1.1.2-1
- New release 1.1.2

* Tue Oct 16 2012 - Marco Neciarini <marco.nenciarini@2ndquadrant.it> 1.1.1-1
- New release 1.1.1

* Fri Oct 12 2012 - Marco Neciarini <marco.nenciarini@2ndquadrant.it> 1.1.0-1
- New release 1.1.0
- Some improvements from Devrim Gunduz <devrim@gunduz.org>

* Fri Jul  6 2012 - Marco Neciarini <marco.nenciarini@2ndquadrant.it> 1.0.0-1
- Open source release

* Thu May 17 2012 - Marco Neciarini <marco.nenciarini@2ndquadrant.it> 0.99.0-5
- Fixed exception handling and documentation

* Thu May 17 2012 - Marco Neciarini <marco.nenciarini@2ndquadrant.it> 0.99.0-4
- Fixed documentation

* Tue May 15 2012 - Marco Neciarini <marco.nenciarini@2ndquadrant.it> 0.99.0-3
- Fixed cron job

* Tue May 15 2012 - Marco Neciarini <marco.nenciarini@2ndquadrant.it> 0.99.0-2
- Add cron job

* Wed May 9 2012 - Marco Neciarini <marco.nenciarini@2ndquadrant.it> 0.99.0-1
- Update to version 0.99.0

* Tue Dec 6 2011 - Marco Neciarini <marco.nenciarini@2ndquadrant.it> 0.3.1-1
- Initial packaging.
