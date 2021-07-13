%global _use_internal_dependency_generator 0
%global debug_package %{nil}

%define __spec_install_post \
  %{?__debug_package:%{__debug_install_post}} \
  %{__arch_install_post} \
  %{__os_install_post} \
  %{__mod_compress_install_post}

%define __mod_compress_install_post find %{buildroot}/lib/modules -type f -name \*.ko -exec xz \{\} \\;

%define pkg wireguard

%define kernel_version 4.18.0-305.el8

Name:             kmod-%{pkg}
Version:          1.0.20210424
Release:          1%{?dist}
Summary:          Fast, modern, secure VPN tunnel

License:          GPLv2
URL:              https://www.wireguard.com/

Source0:          https://git.zx2c4.com/%{pkg}-linux-compat/snapshot/%{pkg}-linux-compat-%{version}.tar.xz

ExclusiveArch:    x86_64 aarch64

BuildRequires:    elfutils-libelf-devel
BuildRequires:    kernel-devel = %{kernel_version}
BuildRequires:    kernel-rpm-macros
BuildRequires:    kmod
BuildRequires:    redhat-rpm-config
BuildRequires:    xz

Supplements:      kernel = %{kernel_version}

Requires:         (kernel = %{kernel_version} if kernel)
Requires(post):   /usr/sbin/depmod
Requires(postun): /usr/sbin/depmod

Provides:         kernel-modules = %{kernel_version}.%{_arch}
Provides:         %{name} = %{?epoch:%{epoch}:}%{version}-%{release}


BuildRequires:    gcc
BuildRequires:    make

Supplements:      wireguard-tools


%description
WireGuard is an extremely simple yet fast and modern VPN that utilizes
state-of-the-art cryptography. It aims to be faster, simpler, leaner, and more
useful than IPsec, while avoiding the massive headache. It intends to be
considerably more performant than OpenVPN. WireGuard is designed as a general
purpose VPN for running on embedded interfaces and super computers alike, fit
for many different circumstances.


%prep
%autosetup -p1 -n %{pkg}-linux-compat-%{version}


%build
pushd src
%{__make} -C /usr/src/kernels/%{kernel_version}.%{_arch} %{?_smp_mflags} M=$PWD modules
popd


%install
%{__install} -D -t %{buildroot}/lib/modules/%{kernel_version}.%{_arch}/extra/drivers/net/%{pkg} src/%{pkg}.ko

# Temporarily executable for stripping
find %{buildroot}/lib/modules -type f -name \*.ko -exec chmod u+x \{\} \+


%clean
%{__rm} -rf %{buildroot}


%post
/usr/sbin/depmod -aeF /lib/modules/%{kernel_version}.%{_arch}/System.map %{kernel_version}.%{_arch}


%postun
/usr/sbin/depmod -aeF /lib/modules/%{kernel_version}.%{_arch}/System.map %{kernel_version}.%{_arch}


%files
%defattr(644,root,root,755)
/lib/modules/%{kernel_version}.%{_arch}
%license COPYING
%doc README.md


%changelog
