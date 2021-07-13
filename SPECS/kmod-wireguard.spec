%{!?kernel_module_package_buildreqs:%{error: "Missing kernel-rpm-macros package!"}}

%global kmodname wireguard

# Signing kernel modules requires certs, which should be defined in the build environment
%bcond_with modsign
%{!?modsign_privkey:%global modsign_privkey %{nil}}
%{!?modsign_pubkey:%global modsign_pubkey %{nil}}

%if %{with modsign}
# XXX: For the moment, signing kmods and debuginfo are incompatible
#      https://bugzilla.redhat.com/show_bug.cgi?id=1967291
%global debug_package %{nil}
%endif


# FIXME:
#  do we gain anything against the elrepo layout?

Name:           %{kmodname}-kmod-src
Version:        1.0.20210606
Release:        0%{?dist}.1
Summary:        Kernel module (kmod) for WireGuard

License:        GPLv2
URL:            https://wireguard.com/
Source0:        https://git.zx2c4.com/wireguard-linux-compat/snapshot/wireguard-linux-compat-%{version}.tar.xz
Patch0001:      0001-compat-account-for-latest-c8s-backports.patch

# For kmodtool
Source10:       kmod-wireguard.spec.preamble

# required to use autosetup git_am
BuildRequires:  git-core

# kernel module package macros were split out sometime after EL7...
BuildRequires:  kernel-rpm-macros
# kmod dependencies
BuildRequires:  %{kernel_module_package_buildreqs}
# listed for completeness
BuildRequires:  gcc make

# this macro expands into a dynamic spec file for our kmod
%{?kernel_module_package:%kernel_module_package -n %{kmodname} -p %{S:10}}

# this description appears on the source rpm only
%description
WireGuard is a novel VPN that runs inside the Linux Kernel and utilizes
state-of-the-art cryptography. It aims to be faster, simpler, leaner,
and more useful than IPSec, while avoiding the massive headache. It intends
to be considerably more performant than OpenVPN. WireGuard is designed as a
general purpose VPN for running on embedded interfaces and super computers
alike, fit for many different circumstances. It runs over UDP.




%prep
%autosetup -n wireguard-linux-compat-%{version} -S git_am


%build
mkdir kmodbuild
for flavor in %{flavors_to_build}; do
    cp -a src kmodbuild/$flavor
    %make_build -C %{kernel_source $flavor} modules M=$PWD/kmodbuild/$flavor
%if %{with modsign} && "%{modsign_privkey}" != "%{nil}" && "%{modsign_pubkey}" != "%{nil}"
    for kmod in $PWD/kmodbuild/$flavor/*.ko; do
        %{kernel_source $flavor}/scripts/sign-file -p sha256 %{modsign_privkey} %{modsign_pubkey} $kmod
    done
%endif
done


%install
export INSTALL_MOD_PATH=%{buildroot}
for flavor in %{flavors_to_build}; do
    %{__make} V=1 -C %{kernel_source $flavor} modules_install M=$PWD/kmodbuild/$flavor
done




%changelog

