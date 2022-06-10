%global pypi_name hudman

%global _description %{expand:
This package provides a HUD Manager implementation.

HUD Manager is a simple tool for creating a local HUD mirror. Can be used
together with the SRC Repair project.

This product can operate in two modes: anonymous and authorized.
Please read manpage for additional information.}

Name: python-%{pypi_name}
Version: 5.0.0
Release: 1%{?dist}

# Main code - GPLv3+.
# Icon - CC-BY-SA.
License: GPLv3+ and CC-BY-SA
Summary: HUD Manager
URL: https://github.com/xvitaly/%{pypi_name}
Source0: %{url}/archive/v%{version}/%{pypi_name}-%{version}.tar.gz
BuildArch: noarch

BuildRequires: doxygen
BuildRequires: pandoc
BuildRequires: python3-devel

%description %_description

%package -n python3-%{pypi_name}
Summary: %{summary}

%description -n python3-%{pypi_name} %_description

%package doc
Summary: Documentation for the %{name}

%description doc
This package provides auto-generated by Doxygen documentation for
the %{name} package.

%prep
%autosetup -n %{pypi_name}-%{version} -p1

%generate_buildrequires
%pyproject_buildrequires -r

%build
%pyproject_wheel
doxygen
pandoc packaging/assets/manpage.md -s -t man > packaging/assets/%{pypi_name}.1

%install
%pyproject_install
%pyproject_save_files %{pypi_name}
install -D -p -m 0644 packaging/assets/%{pypi_name}.1 %{buildroot}%{_mandir}/man1/%{pypi_name}.1

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE licenses/*
%doc README.md
%{_bindir}/%{pypi_name}
%{_mandir}/man1/%{pypi_name}.1*

%files doc
%doc docs/html/*

%changelog
* Fri Jun 10 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 5.0.0-1
- Updated to version 5.0.0.
