%if 0%{?fedora}
  %bcond_without   wheels
  %bcond_with      python2
  %bcond_with      python3
%else
  %bcond_with      wheels
  %if 0%{?rhel} > 7
    %bcond_with    python2
    %bcond_without python3
  %else
    %bcond_without python2
    %bcond_with    python3
  %endif
%endif

%bcond_without check


%global sum()   Build manual page from %* ArgumentParser object
%global desc \
Generate manual page an automatic way from ArgumentParser object, so the \
manpage 1:1 corresponds to the automatically generated --help output.  The \
manpage generator needs to known the location of the object, user can \
specify that by (a) the module name or corresponding python filename and \
(b) the object name or the function name which returns the object. \
There is a limited support for (deprecated) optparse objects, too.


Name:           argparse-manpage
Version:        @VERSION@
Release:        @RELEASE@%{?dist}
Summary:        %{sum Python}
BuildArch:      noarch

License:        ASL 2.0
URL:            https://github.com/praiskup/%{name}
Source0:        https://github.com/praiskup/%{name}/archive/v%{version}/%{name}-%{version}.tar.gz

%if %{with python2}
BuildRequires: python2-setuptools python2-devel
%if %{with check}
%if 0%{?rhel} && 0%{?rhel} == 7
BuildRequires: pytest
%else
BuildRequires: python2-pytest
%endif
%endif
%endif

%if %{with python3}
BuildRequires: python3-setuptools python3-devel
%if %{with check}
BuildRequires: python3-pytest
%endif
%endif

%if %{with wheels}
BuildRequires:  python3-devel
BuildRequires:  python3-pytest
%endif

%if %{with python3} || %{with wheels}
Requires: python3-%name = %version-%release
%else
Requires: python2-%name = %version-%release
%endif

%description
%desc


%package -n     python2-%name
Summary:        %{sum Python 2}

%description -n python2-%name
%{desc}


%package -n     python3-%name
Summary:        %{sum Python 3}

%description -n python3-%name
%{desc}


%prep
%setup -q

%if %{with wheels}
%generate_buildrequires
%pyproject_buildrequires
%endif


%build
%if %{with python2}
%py2_build
%endif
%if %{with python3}
%py3_build
%endif
%if %{with wheels}
%pyproject_wheel
%endif


%install
%if %{with python2}
%py2_install
%endif
%if %{with python3}
%py3_install
%endif
%if %{with wheels}
%pyproject_install
%endif



%if %{with check}
%check
%if %{with python2}
PYTHONPATH=%buildroot%python2_sitearch %__python2 -m pytest
%endif
%if %{with python3}
PYTHONPATH=%buildroot%python3_sitearch %__python3 -m pytest
%endif
%if %{with wheels}
%pytest
%endif
%endif


%files
%license LICENSE
%{_bindir}/argparse-manpage
%_mandir/man1/argparse-manpage.1.*
%if %{with python3} || %{with wheels}
%python3_sitelib/build_manpages/cli
%else
%python2_sitelib/build_manpages/cli
%endif


%if %{with python2}
%files -n python2-%name
%license LICENSE
%python2_sitelib/build_manpages
%python2_sitelib/argparse_manpage-%{version}*.egg-info
%exclude %python2_sitelib/build_manpages/cli
%endif


%if %{with python3} || %{with wheels}
%files -n python3-%name
%license LICENSE
%python3_sitelib/build_manpages
%if %{with wheels}
%python3_sitelib/argparse_manpage-*dist-info
%else
%python3_sitelib/argparse_manpage-%{version}*.egg-info
%endif
%exclude %python3_sitelib/build_manpages/cli
%endif


%changelog
* @DATE@ Pavel Raiskup <praiskup@redhat.com> - @VERSION@-@RELEASE@
- built from upstream, changelog ignored
