Summary: The Linux kernel (the core of the Linux operating system)

# What parts do we want to build?  We must build at least one kernel.
# These are the kernels that are built IF the architecture allows it.
# All should default to 1 (enabled) and be flipped to 0 (disabled)
# by later arch-specific checks

# The following build options are enabled by default.
# Use either --without <opt> in your rpmbuild command or force values
# to 0 in here to disable them
#
# standard kernel
%define with_up        %{?_without_up:        0} %{?!_without_up:        1}
# kernel-PAE (only valid for i686)
%define with_pae       %{?_without_pae:       0} %{?!_without_pae:       1}
# kernel-xen (only valid for i686, x86_64 and ia64)
%define with_xen       %{?_without_xen:       0} %{?!_without_xen:       1}
# kernel-kdump (only valid for ppc64)
%define with_kdump     %{?_without_kdump:     0} %{?!_without_kdump:     1}
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     1}
# kernel-doc
%define with_doc       %{?_without_doc:       0} %{?!_without_doc:       1}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}

# Control whether we perform a compat. check against published ABI.
%define with_kabichk   %{?_without_kabichk:   0} %{?!_without_kabichk:   1}
# Control whether we perform a compat. check against published ABI.
%define with_fips      %{?_without_fips:      0} %{?!_without_fips:      1}

# Additional options for user-friendly one-off kernel building:
#
# Only build the base kernel (--with baseonly):
%define with_baseonly  %{?_with_baseonly:     1} %{?!_with_baseonly:     0}
# Only build the xen kernel (--with xenonly):
%define with_xenonly   %{?_with_xenonly:      1} %{?!_with_xenonly:      0}
# Only build the debug kernel (--with dbgonly):
%define with_dbgonly   %{?_with_dbgonly:      1} %{?!_with_dbgonly:      0}

# Whether to apply the Xen patches -- leave this enabled.
%define includexen 0
#disable xen
%define with_xen 0

# Set debugbuildsenabled to 1 for production (build separate debug kernels)
#  and 0 for rawhide (all kernels are debug kernels).
# See also 'make debug' and 'make release'.
%define debugbuildsenabled 1

# Ensure srpms are created using algos that the stock RHEL5-era rpm
# knows how to work with (enables srpm creation on Fedora or newer RHEL).
%define _source_filedigest_algorithm 0
%define _binary_filedigest_algorithm 0

# Versions of various parts

# After branching, please hardcode these values as the
# %dist and %rhel tags are not reliable in rhel5-era rpm
# For example dist -> .el5 and rhel -> 5
%define dist .el5
%define rhel 5

# Values used for RHEL version info in version.h
%define rh_release_major %{rhel}
%define rh_release_minor 8

#
# Polite request for people who spin their own kernel rpms:
# please modify the "buildid" define in a way that identifies
# that the kernel isn't the stock distribution kernel, for example,
# by setting the define to ".local" or ".bz123456"
#
% define buildid ".grsec1"
#
%define sublevel 18
%define stablerev 4
%define revision 308.13.1
%define kversion 2.6.%{sublevel}.%{stablerev}
%define rpmversion 2.6.%{sublevel}
%define release %{revision}%{dist}%{?buildid}
%define signmodules 0
%define xen_hv_cset 15502
%define xen_abi_ver 3.1
%define make_target bzImage
%define kernel_image x86
%define xen_flags verbose=y crash_debug=y XEN_VENDORVERSION=-%{release}
%define xen_target vmlinuz
%define xen_image vmlinuz

%define TAR_VER %{kversion}
%if "%{TAR_VER}" != "%{kversion}"
%define XEN_VER %{TAR_VER}
%endif

%define KVERREL %{rpmversion}-%{release}
%define hdrarch %_target_cpu

%if !%{debugbuildsenabled}
%define with_debug 0
%endif

%if !%{with_debuginfo}
%define _enable_debug_packages 0
%endif
%define debuginfodir /usr/lib/debug

# if requested, only build base kernel
%if %{with_baseonly}
%define with_pae 0
%define with_xen 0
%define with_kdump 0
%define with_debug 0
%endif

# if requested, only build xen kernel
%if %{with_xenonly}
%define with_up 0
%define with_pae 0
%define with_kdump 0
%define with_debug 0
%endif

# if requested, only build debug kernel
%if %{with_dbgonly}
%define with_up 0
%define with_pae 0
%define with_xen 0
%define with_kdump 0
%endif

# if building without xen, we can skip including the xen tarball to save time
%if !%{with_xen}
%define include_xen_tarball 0
%else
%define include_xen_tarball 1
%endif

# groups of related archs
# We don't build 586 kernels for RHEL.
%define all_x86 i386 i686

# we differ here b/c of the reloc patches
%ifarch i686 x86_64
%define with_kdump 0
%endif

# Overrides for generic default options

# pae is only valid on i686
%ifnarch i686
%define with_pae 0
%endif

# xen only builds on i686, x86_64 and ia64
%ifnarch i686 x86_64 ia64
%define with_xen 0
%endif

# only build kernel-kdump on i686, x86_64 and ppc64
%ifnarch i686 x86_64 ppc64 ppc64iseries s390x
%define with_kdump 0
%endif

# only package docs noarch
%ifnarch noarch
%define with_doc 0
%endif

# no need to build headers again for these arches,
# they can just use i386 and ppc64 headers
%ifarch i586 i686 ppc64iseries
%define with_headers 0
%endif

# obviously, don't build noarch kernels or headers
%ifarch noarch
%define with_up 0
%define with_headers 0
%define with_debug 0
%define all_arch_configs kernel-%{rpmversion}-*.config
%endif

# Per-arch tweaks

%ifarch %{all_x86}
%define all_arch_configs kernel-%{rpmversion}-i?86*.config
%define image_install_path boot
%define signmodules 1
%define hdrarch i386
%endif

%ifarch i686
# we build always xen i686 HV with pae
%define xen_flags verbose=y crash_debug=y pae=y XEN_VENDORVERSION=-%{release}
%endif

%ifarch x86_64
%define all_arch_configs kernel-%{rpmversion}-x86_64*.config
%define image_install_path boot
%define signmodules 1
%define xen_flags verbose=y crash_debug=y max_phys_cpus=256 XEN_VENDORVERSION=-%{release}
%endif

%ifarch ppc64 ppc64iseries
%define all_arch_configs kernel-%{rpmversion}-ppc64*.config
%define image_install_path boot
%define signmodules 1
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%define hdrarch powerpc
%endif

%ifarch s390
%define all_arch_configs kernel-%{rpmversion}-s390*.config
%define image_install_path boot
%define make_target image
%define kernel_image arch/s390/boot/image
%endif

%ifarch s390x
%define all_arch_configs kernel-%{rpmversion}-s390x*.config
%define image_install_path boot
%define signmodules 1
%define make_target image
%define kernel_image arch/s390/boot/image
%define hdrarch s390
%endif

%ifarch sparc
%define all_arch_configs kernel-%{rpmversion}-sparc.config
%define make_target image
%define kernel_image image
%endif

%ifarch sparc64
%define all_arch_configs kernel-%{rpmversion}-sparc64*.config
%define make_target image
%define kernel_image image
%endif

%ifarch ppc
%define all_arch_configs kernel-%{rpmversion}-ppc.config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%define hdrarch powerpc
%endif

%ifarch ia64
%define all_arch_configs kernel-%{rpmversion}-ia64*.config
%define image_install_path boot/efi/EFI/redhat
%define signmodules 1
%define make_target compressed
%define kernel_image vmlinux.gz
# ia64 xen HV doesn't build with debug=y at the moment
%define xen_flags verbose=y crash_debug=y XEN_VENDORVERSION=-%{release}
%define xen_target compressed
%define xen_image vmlinux.gz
%endif

# To temporarily exclude an architecture from being built, add it to
# %nobuildarches. Do _NOT_ use the ExclusiveArch: line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
# Which is a BadThing(tm).

# We don't build a kernel on i386 or s390x or ppc -- we only do kernel-headers there.
%define nobuildarches i386 s390 ppc

%ifarch %nobuildarches
%define with_up 0
%define with_pae 0
%define with_xen 0
%define with_kdump 0
%define with_debug 0
%define with_debuginfo 0
%define _enable_debug_packages 0
%endif

#
# Three sets of minimum package version requirements in the form of Conflicts:
# to versions below the minimum
#

#
# First the general kernel 2.6 required versions as per
# Documentation/Changes
#
%define kernel_dot_org_conflicts  ppp < 2.4.3-3, isdn4k-utils < 3.2-32, nfs-utils < 1.0.7-12, e2fsprogs < 1.37-4, util-linux < 2.12, jfsutils < 1.1.7-2, reiserfs-utils < 3.6.19-2, xfsprogs < 2.6.13-4, procps < 3.2.5-6.3, oprofile < 0.9.1-2

#
# Then a series of requirements that are distribution specific, either
# because we add patches for something, or the older versions have
# problems with the newer kernel or lack certain things that make
# integration in the distro harder than needed.
#
%define package_conflicts initscripts < 7.23, udev < 063-6, iptables < 1.3.2-1, ipw2200-firmware < 2.4, selinux-policy-targeted < 1.25.3-14, ecryptfs-utils < 44, cpuspeed < 1.2.1-5

#
# The ld.so.conf.d file we install uses syntax older ldconfig's don't grok.
#
%define xen_conflicts glibc < 2.3.5-1, xen < 3.0.1

#
# Make the RPM build on later Fedora systems
#
%define _default_patch_fuzz 2

#
# Packages that need to be installed before the kernel is, because the %post
# scripts use them.
#
%define kernel_prereq  fileutils, module-init-tools, initscripts >= 8.11.1-1, mkinitrd >= 4.2.21-1

Name: kernel
Group: System Environment/Kernel
License: GPLv2
URL: http://www.kernel.org/
Version: %{rpmversion}
Release: %{release}
# DO NOT CHANGE THIS LINE TO TEMPORARILY EXCLUDE AN ARCHITECTURE BUILD.
# SET %nobuildarches (ABOVE) INSTEAD
ExclusiveArch: noarch %{all_x86} x86_64 ppc ppc64 ia64 sparc sparc64 s390 s390x
ExclusiveOS: Linux
Provides: kernel = %{version}
Provides: kernel-drm = 4.3.0
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{release}
Requires(pre): %{kernel_prereq}
Conflicts: %{kernel_dot_org_conflicts}
Conflicts: %{package_conflicts}
# We can't let RPM do the dependencies automatic because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function
AutoReq: no
AutoProv: yes


#
# List the packages used during the kernel build
#
BuildRequires: module-init-tools, patch >= 2.5.4, bash >= 2.03, sh-utils, tar
BuildRequires: bzip2, findutils, gzip, m4, perl, make >= 3.78, diffutils
%if %{signmodules}
BuildRequires: gnupg
%endif
BuildRequires: gcc >= 3.4.2, binutils >= 2.12, redhat-rpm-config
%if %{with_headers}
BuildRequires: unifdef
%endif
%if %{with_fips}
BuildRequires: hmaccalc
%endif
BuildConflicts: rhbuildsys(DiskFree) < 500Mb


Source0: ftp://ftp.kernel.org/pub/linux/kernel/v2.6/linux-%{TAR_VER}.tar.bz2
%if %{include_xen_tarball}
Source1: xen-%{xen_hv_cset}.tar.bz2
Source2: Config.mk
%endif

Source10: COPYING.modules
Source11: genkey
Source12: kabitool
Source14: find-provides
Source15: merge.pl

Source20: kernel-%{version}-i586.config
Source21: kernel-%{version}-i686.config
Source22: kernel-%{version}-i686-debug.config
Source23: kernel-%{version}-i686-PAE.config

Source24: kernel-%{version}-x86_64.config
Source25: kernel-%{version}-x86_64-debug.config

Source26: kernel-%{version}-ppc.config
Source27: kernel-%{version}-ppc64.config
Source28: kernel-%{version}-ppc64-debug.config
Source29: kernel-%{version}-ppc64-kdump.config

Source30: kernel-%{version}-s390.config
Source31: kernel-%{version}-s390x.config
Source32: kernel-%{version}-s390x-debug.config
Source33: kernel-%{version}-s390x-kdump.config

Source34: kernel-%{version}-ia64.config
Source35: kernel-%{version}-ia64-debug.config

Source36: kernel-%{version}-i686-xen.config
Source37: kernel-%{version}-x86_64-xen.config
Source38: kernel-%{version}-ia64-xen.config

Source80: config-rhel-generic
Source82: config-rhel-ppc64-generic
Source83: config-rhel-x86_64-generic

Source100: kabi_whitelist_i686
Source101: kabi_whitelist_i686PAE
Source102: kabi_whitelist_i686xen
Source103: kabi_whitelist_ia64
Source104: kabi_whitelist_ia64xen
Source105: kabi_whitelist_ppc64
Source106: kabi_whitelist_ppc64kdump
Source107: kabi_whitelist_s390x
Source108: kabi_whitelist_x86_64
Source109: kabi_whitelist_x86_64xen

Source120: Module.kabi_i686
Source121: Module.kabi_i686PAE
Source122: Module.kabi_i686xen
Source123: Module.kabi_ia64
#Source124: Module.kabi_ia64xen
Source125: Module.kabi_ppc64
Source126: Module.kabi_ppc64kdump
Source127: Module.kabi_s390x
Source128: Module.kabi_x86_64
Source129: Module.kabi_x86_64xen

Source130: check-kabi

#nnewton finish
#Patch1: grsecblahblah
#Patch1: kernel-2.6.18-redhat.patch
#Patch2: xen-config-2.6.18-redhat.patch
#Patch3: xen-2.6.18-redhat.patch

# empty final patch file to facilitate testing of kernel patches
#Patch99999: linux-kernel-test.patch

BuildRoot: %{_tmppath}/kernel-%{KVERREL}-root

# Override find_provides to use a script that provides "kernel(symbol) = hash".
# Pass path of the RPM temp dir containing kabideps to find-provides script.
%global _use_internal_dependency_generator 0
%define _kabidir %{_sourcedir}
%define __find_provides %{_kabidir}/find-provides %{_tmppath}
%define __find_requires /usr/lib/rpm/redhat/find-requires kernel
%define _hmacdir /usr/bin

%ifarch x86_64
Obsoletes: kernel-smp
%endif
Obsoletes: kernel-modules-rhel5-0
Obsoletes: kernel-modules-rhel5-1
Obsoletes: kernel-modules-rhel5-2

%description
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

%package devel
Summary: Development package for building kernel modules to match the kernel.
Group: System Environment/Kernel
AutoReqProv: no
Provides: kernel-devel-%{_target_cpu} = %{rpmversion}-%{release}
Requires(pre): /usr/bin/find

%description devel
This package provides kernel headers and makefiles sufficient to build modules
against the kernel package.


%package doc
Summary: Various documentation bits found in the kernel source.
Group: Documentation

%description doc
This package contains documentation files from the kernel
source. Various bits of information about the Linux kernel and the
device drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to Linux kernel modules at load time.

%package headers
Summary: Header files for the Linux kernel for use by glibc
Group: Development/System
Obsoletes: glibc-kernheaders
Provides: glibc-kernheaders = 3.0-46

%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package PAE
Summary: The Linux kernel compiled for PAE capable machines.

Group: System Environment/Kernel
Provides: kernel = %{version}
Provides: kernel-drm = 4.3.0
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{release}PAE
Requires(pre): %{kernel_prereq}
Conflicts: %{kernel_dot_org_conflicts}
Conflicts: %{package_conflicts}
Obsoletes: kernel-smp < 2.6.17
Obsoletes: kernel-modules-rhel5-0
Obsoletes: kernel-modules-rhel5-1
Obsoletes: kernel-modules-rhel5-2
# We can't let RPM do the dependencies automatic because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function
AutoReq: no
AutoProv: yes

%description PAE
This package includes a version of the Linux kernel with support for up to
16GB of high memory. It requires a CPU with Physical Address Extensions (PAE).
The non-PAE kernel can only address up to 4GB of memory.
Install the kernel-PAE package if your machine has more than 4GB of memory.

%package PAE-devel
Summary: Development package for building kernel modules to match the PAE kernel.
Group: System Environment/Kernel
Provides: kernel-PAE-devel-%{_target_cpu} = %{rpmversion}-%{release}
Provides: kernel-devel-%{_target_cpu} = %{rpmversion}-%{release}PAE
Provides: kernel-devel = %{rpmversion}-%{release}PAE
AutoReqProv: no
Requires(pre): /usr/bin/find

%description PAE-devel
This package provides kernel headers and makefiles sufficient to build modules
against the PAE kernel package.

%package debug
Summary: The Linux kernel compiled with extra debugging enabled.
Group: System Environment/Kernel
Provides: kernel = %{version}
Provides: kernel-drm = 4.3.0
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{release}-debug
Requires(pre): %{kernel_prereq}
Conflicts: %{kernel_dot_org_conflicts}
Conflicts: %{package_conflicts}
AutoReq: no
AutoProv: yes
%description debug
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.

%package debug-debuginfo
Summary: Debug information for package %{name}-debug
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{KVERREL}
Provides: %{name}-debug-debuginfo-%{_target_cpu} = %{KVERREL}
%description debug-debuginfo
This package provides debug information for package %{name}-debug

%package debug-devel
Summary: Development package for building kernel modules to match the kernel.
Group: System Environment/Kernel
AutoReqProv: no
Requires(pre): /usr/bin/find
%description debug-devel
This package provides kernel headers and makefiles sufficient to build modules
against the kernel package.

%package xen
Summary: The Linux kernel compiled for Xen VM operations

Group: System Environment/Kernel
Provides: kernel = %{version}
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{release}xen
Provides: xen-hypervisor-abi = %{xen_abi_ver}
Requires(pre): %{kernel_prereq}
Conflicts: %{kernel_dot_org_conflicts}
Conflicts: %{package_conflicts}
Conflicts: %{xen_conflicts}
Obsoletes: kernel-modules-rhel5-0
Obsoletes: kernel-modules-rhel5-1
Obsoletes: kernel-modules-rhel5-2
# We can't let RPM do the dependencies automatic because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function
AutoReq: no
AutoProv: yes

%description xen
This package includes a Xen hypervisor and a version of the Linux kernel which
can run Xen VMs for privileged hosts and unprivileged paravirtualized hosts.

%package xen-devel
Summary: Development package for building kernel modules to match the kernel.
Group: System Environment/Kernel
AutoReqProv: no
Provides: kernel-xen-devel-%{_target_cpu} = %{rpmversion}-%{release}
Provides: kernel-devel-%{_target_cpu} = %{rpmversion}-%{release}xen
Provides: kernel-devel = %{rpmversion}-%{release}xen
Requires(pre): /usr/bin/find

%description xen-devel
This package provides kernel headers and makefiles sufficient to build modules
against the kernel package.

%package kdump
Summary: A minimal Linux kernel compiled for kernel crash dumps.

Group: System Environment/Kernel
Provides: kernel = %{version}
Provides: kernel-drm = 4.3.0
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{release}kdump
Requires(pre): %{kernel_prereq}
Conflicts: %{kernel_dot_org_conflicts}
Conflicts: %{package_conflicts}
Obsoletes: kernel-modules-rhel5-0
Obsoletes: kernel-modules-rhel5-1
Obsoletes: kernel-modules-rhel5-2
# We can't let RPM do the dependencies automatic because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function
AutoReq: no
AutoProv: yes

%description kdump
This package includes a kdump version of the Linux kernel. It is
required only on machines which will use the kexec-based kernel crash dump
mechanism.

%package kdump-devel
Summary: Development package for building kernel modules to match the kdump kernel.
Group: System Environment/Kernel
Provides: kernel-kdump-devel-%{_target_cpu} = %{rpmversion}-%{release}
Provides: kernel-devel-%{_target_cpu} = %{rpmversion}-%{release}kdump
Provides: kernel-devel = %{rpmversion}-%{release}kdump
AutoReqProv: no
Requires(pre): /usr/bin/find

%description kdump-devel
This package provides kernel headers and makefiles sufficient to build modules
against the kdump kernel package.


%prep
# do a few sanity-checks for --with *only builds
%if %{with_baseonly}
%if !%{with_up}
echo "Cannot build --with baseonly, up build is disabled"
exit 1
%endif
%endif

%if %{with_xenonly}
%if !%{with_xen}
echo "Cannot build --with xenonly, xen build is disabled"
exit 1
%endif
%endif

# First we unpack the kernel tarball.
# If this isn't the first make prep, we use links to the existing clean tarball
# which speeds things up quite a bit.
if [ ! -d kernel-%{version}/vanilla-%{kversion} ]; then
  # Ok, first time we do a make prep.
  rm -f pax_global_header
%setup -q -n %{name}-%{version} -c
  mv linux-%{TAR_VER} vanilla-%{kversion}
else
  # We already have a vanilla-%{kversion} dir.
  cd kernel-%{version}
  if [ -d linux-%{KVERREL}.%{_target_cpu} ]; then
     # Just in case we ctrl-c'd a prep already
     rm -rf deleteme
     # Move away the stale away, and delete in background.
     mv linux-%{KVERREL}.%{_target_cpu} deleteme
     rm -rf deleteme &
  fi
fi
cp -rl vanilla-%{kversion} linux-%{KVERREL}.%{_target_cpu}

cd linux-%{KVERREL}.%{_target_cpu}

#%patch1 -p1 -E

# conditionally applied test patch for debugging convenience
%if %([ -s %{PATCH99999} ] && echo 1 || echo 0)
%patch99999 -p1
%endif

cp %{SOURCE10} Documentation/

mkdir configs

for cfg in %{all_arch_configs}; do
  cp -f $RPM_SOURCE_DIR/$cfg .
done

#if a rhel kernel, apply the rhel config options
%if 0%{?rhel}
  for i in %{all_arch_configs}
  do
    mv $i $i.tmp
    $RPM_SOURCE_DIR/merge.pl $RPM_SOURCE_DIR/config-rhel-generic $i.tmp > $i
    rm $i.tmp
  done
%ifarch x86_64 noarch
  for i in kernel-%{version}-x86_64*.config
  do
    mv $i $i.tmp
    $RPM_SOURCE_DIR/merge.pl $RPM_SOURCE_DIR/config-rhel-x86_64-generic $i.tmp > $i
    rm $i.tmp
  done
%endif
%ifarch ppc64 noarch
  #CONFIG_FB_MATROX is disabled for rhel generic but needed for ppc64 rhel
  for i in kernel-%{version}-ppc64*.config
  do
    mv $i $i.tmp
    $RPM_SOURCE_DIR/merge.pl $RPM_SOURCE_DIR/config-rhel-ppc64-generic $i.tmp > $i
    rm $i.tmp
  done
%endif
%endif


%if 0%{?rhel}
# don't need these for relocatable kernels
rm -f kernel-%{version}-{i686,x86_64}-kdump.config
# don't need these in general
rm -f kernel-%{version}-i586.config
%endif

%if !%{with_debug}
rm -f kernel-%{version}-*-debug.config
%endif

# now run oldconfig over all the config files
for i in *.config
do
  mv $i .config
  Arch=`head -1 .config | cut -b 3-`
  make ARCH=$Arch nonint_oldconfig > /dev/null
  echo "# $Arch" > configs/$i
  cat .config >> configs/$i
done

# If we don't have many patches to apply, sometimes the deleteme
# trick still hasn't completed, and things go bang at this point
# when find traverses into directories that get deleted.
# So we serialise until the dir has gone away.
cd ..
while [ -d deleteme ];
do
	sleep 1
done

# get rid of unwanted files resulting from patch fuzz
find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null


###
### build
###
%build
#
# Create gpg keys for signing the modules
#

%if %{signmodules}
gpg --homedir . --batch --gen-key %{SOURCE11}
gpg --homedir . --export --keyring ./kernel.pub Red > extract.pub
make linux-%{KVERREL}.%{_target_cpu}/scripts/bin2c
linux-%{KVERREL}.%{_target_cpu}/scripts/bin2c ksign_def_public_key __initdata < extract.pub > linux-%{KVERREL}.%{_target_cpu}/crypto/signature/key.h
%endif

BuildKernel() {
    MakeTarget=$1
    KernelImage=$2
    Flavour=$3

    # Pick the right config file for the kernel we're building
    if [ -n "$Flavour" ] ; then
      Config=kernel-%{version}-%{_target_cpu}-$Flavour.config
      DevelDir=/usr/src/kernels/%{KVERREL}-$Flavour-%{_target_cpu}
      DevelLink=/usr/src/kernels/%{KVERREL}$Flavour-%{_target_cpu}
    else
      Config=kernel-%{version}-%{_target_cpu}.config
      DevelDir=/usr/src/kernels/%{KVERREL}-%{_target_cpu}
      DevelLink=
    fi

    KernelVer=%{version}-%{release}$Flavour
    echo BUILDING A KERNEL FOR $Flavour %{_target_cpu}...

    # make sure EXTRAVERSION says what we want it to say
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}$Flavour/" Makefile

    # and now to start the build process

    make -s mrproper
    cp configs/$Config .config

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

    if [ "$KernelImage" == "x86" ]; then
       KernelImage=arch/$Arch/boot/bzImage
    fi
    if [ "$Arch" == "s390" -a "$Flavour" == "kdump" ]; then
      pushd arch/s390/boot
      gcc -static -o zfcpdump zfcpdump.c
      popd
    fi

    make -s ARCH=$Arch nonint_oldconfig > /dev/null
    make -s ARCH=$Arch %{?_smp_mflags} $MakeTarget
    if [ "$Arch" != "s390" -o "$Flavour" != "kdump" ]; then
      make -s ARCH=$Arch %{?_smp_mflags} modules || exit 1
    fi

    # Start installing the results

%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/boot
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/%{image_install_path}
%endif
    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}
    install -m 644 .config $RPM_BUILD_ROOT/boot/config-$KernelVer
    install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$KernelVer
    touch $RPM_BUILD_ROOT/boot/initrd-$KernelVer.img
    cp $KernelImage $RPM_BUILD_ROOT/%{image_install_path}/vmlinuz-$KernelVer
    if [ -f arch/$Arch/boot/zImage.stub ]; then
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/%{image_install_path}/zImage.stub-$KernelVer || :
    fi

%if %{with_fips}
    #hmac sign the kernel for FIPS
    echo "Creating hmac file: $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac" &&
    pushd $RPM_BUILD_ROOT
    %_hmacdir/sha512hmac %{image_install_path}/vmlinuz-$KernelVer > \
	%{image_install_path}/.vmlinuz-$KernelVer.hmac || (echo "sha512hmac signing failed" && exit 1)
    popd
%endif

    if [ "$Flavour" == "kdump" -a "$Arch" != "s390" ]; then
        cp vmlinux $RPM_BUILD_ROOT/%{image_install_path}/vmlinux-$KernelVer
        rm -f $RPM_BUILD_ROOT/%{image_install_path}/vmlinuz-$KernelVer

%if %{with_fips}
	#hmac sign the kernel for FIPS
	test -f $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac &&
            rm -f $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac
	echo "Creating hmac file: $RPM_BUILD_ROOT/%{image_install_path}/.vmlinux-$KernelVer.hmac" &&
	pushd $RPM_BUILD_ROOT
	%_hmacdir/sha512hmac %{image_install_path}/vmlinux-$KernelVer > \
	    %{image_install_path}/.vmlinux-$KernelVer.hmac || (echo "sha512hmac signing failed" && exit 1)
	popd
%endif
    fi

    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
    if [ "$Arch" != "s390" -o "$Flavour" != "kdump" ]; then
      make -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=$KernelVer
    else
      touch Module.symvers
      touch Module.markers
    fi

    # Create the kABI metadata for use in packaging
    echo "**** GENERATING kernel ABI metadata ****"
    gzip -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-$KernelVer.gz

%if %{with_kabichk}
    chmod 0755 %{_kabidir}/kabitool
    if [ ! -e %{_kabidir}/kabi_whitelist_%{_target_cpu}$Flavour ]; then
        echo "**** No KABI whitelist was available during build ****"
        %{_kabidir}/kabitool -b $RPM_BUILD_ROOT/$DevelDir -k $KernelVer -l $RPM_BUILD_ROOT/kabi_whitelist
    else
	cp %{_kabidir}/kabi_whitelist_%{_target_cpu}$Flavour $RPM_BUILD_ROOT/kabi_whitelist
    fi
    rm -f %{_tmppath}/kernel-$KernelVer-kabideps
    %{_kabidir}/kabitool -b . -d %{_tmppath}/kernel-$KernelVer-kabideps -k $KernelVer -w $RPM_BUILD_ROOT/kabi_whitelist

    echo "**** kABI checking is enabled in kernel SPEC file. ****"
    chmod 0755 %{_kabidir}/check-kabi
    if [ -e %{_kabidir}/Module.kabi_%{_target_cpu}$Flavour ]; then
	cp %{_kabidir}/Module.kabi_%{_target_cpu}$Flavour $RPM_BUILD_ROOT/Module.kabi
	%{_kabidir}/check-kabi -k $RPM_BUILD_ROOT/Module.kabi -s Module.symvers || exit 1
    else
	echo "**** NOTE: Cannot find reference Module.kabi file. ****"
    fi
%endif
    # Ensure the kabideps file always exists for the RPM ProvReq scripts
    touch %{_tmppath}/kernel-$KernelVer-kabideps

    # And save the headers/makefiles etc for building modules against
    #
    # This all looks scary, but the end result is supposed to be:
    # * all arch relevant include/ files
    # * all Makefile/Kconfig files
    # * all script/ files

    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/source
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    (cd $RPM_BUILD_ROOT/lib/modules/$KernelVer ; ln -s build source)
    # dirs for additional modules per module-init-tools, kbuild/modules.txt
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/extra
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/updates
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/weak-updates
    # first copy everything
    cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp Module.symvers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp Module.markers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

%if %{with_kabichk}
    mv $RPM_BUILD_ROOT/kabi_whitelist $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -e $RPM_BUILD_ROOT/Module.kabi ]; then
	mv $RPM_BUILD_ROOT/Module.kabi $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    fi
    cp symsets-$KernelVer.tar.gz $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
%endif

    # then drop all but the needed Makefiles/Kconfig files
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Documentation
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    cp .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -d arch/%{_arch}/scripts ]; then
      cp -a arch/%{_arch}/scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch} || :
    fi
    if [ -f arch/%{_arch}/*lds ]; then
      cp -a arch/%{_arch}/*lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch}/ || :
    fi
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*.o
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*/*.o
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    cd include
    cp -a acpi config keys linux math-emu media mtd net pcmcia rdma rxrpc scsi sound trace video asm asm-generic crypto $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    cp -a `readlink asm` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    if [ "$Arch" = "x86_64" ]; then
      cp -a asm-i386 $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    fi
    if [ "$Arch" = "i386" ]; then
      cp -a asm-x86_64 $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    fi
    # While arch/powerpc/include/asm is still a symlink to the old
    # include/asm-ppc{64,} directory, include that in kernel-devel too.
    if [ "$Arch" = "powerpc" -a -r ../arch/powerpc/include/asm ]; then
      cp -a `readlink ../arch/powerpc/include/asm` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
      mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/$Arch/include
      pushd $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/$Arch/include
      ln -sf ../../../include/asm-ppc* asm
      popd
    fi

    # Make sure the Makefile and version.h have a matching timestamp so that
    # external modules can be built
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/linux/version.h
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/linux/autoconf.h
    # Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
    cp $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf
    cd ..

    #
    # save the vmlinux file for kernel debugging into the kernel-debuginfo rpm
    #
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
    cp vmlinux $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
%endif

    find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name "*.ko" -type f >modnames

    # gpg sign the modules
%if %{signmodules}
    gcc -o scripts/modsign/mod-extract scripts/modsign/mod-extract.c -Wall
    KEYFLAGS="--no-default-keyring --homedir .."
    KEYFLAGS="$KEYFLAGS --secret-keyring ../kernel.sec"
    KEYFLAGS="$KEYFLAGS --keyring ../kernel.pub"
    export KEYFLAGS

    for i in `cat modnames`
    do
      sh ./scripts/modsign/modsign.sh $i Red
      mv -f $i.signed $i
    done
    unset KEYFLAGS
%endif

    # mark modules executable so that strip-to-file can strip them
    for i in `cat modnames`
    do
      chmod u+x $i
    done

    # detect missing or incorrect license tags
    for i in `cat modnames`
    do
      echo -n "$i "
      /sbin/modinfo -l $i >> modinfo
    done
    cat modinfo |\
      grep -v "^GPL" |
      grep -v "^Dual BSD/GPL" |\
      grep -v "^Dual MPL/GPL" |\
      grep -v "^GPL and additional rights" |\
      grep -v "^GPL v2" && exit 1
    rm -f modinfo
    rm -f modnames
    # remove files that will be auto generated by depmod at rpm -i time
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.*

    # Move the devel headers out of the root file system
    mkdir -p $RPM_BUILD_ROOT/usr/src/kernels
    mv $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/$DevelDir
    ln -sf ../../..$DevelDir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    [ -z "$DevelLink" ] || ln -sf `basename $DevelDir` $RPM_BUILD_ROOT/$DevelLink

	# Temporary fix for upstream "make prepare" bug.
#	pushd $RPM_BUILD_ROOT/$DevelDir > /dev/null
#	if [ -f Makefile ]; then
#		make prepare
#	fi
#	popd > /dev/null
}

###
# DO it...
###

# prepare directories
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/boot

cd linux-%{KVERREL}.%{_target_cpu}

%if %{with_up}
BuildKernel %make_target %kernel_image
%endif

%if %{with_pae}
BuildKernel %make_target %kernel_image PAE
%endif

%if %{with_kdump}
BuildKernel %make_target %kernel_image kdump
%endif

%if %{with_debug}
BuildKernel %make_target %kernel_image debug
%endif

###
### Special hacks for debuginfo subpackages.
###

# This macro is used by %%install, so we must redefine it before that.
%define debug_package %{nil}

%if %{with_debuginfo}
%ifnarch noarch
%global __debug_package 1
%package debuginfo-common
Summary: Kernel source files used by %{name}-debuginfo packages
Group: Development/Debug
Provides: %{name}-debuginfo-common-%{_target_cpu} = %{KVERREL}

%description debuginfo-common
This package is required by %{name}-debuginfo subpackages.
It provides the kernel source files common to all builds.

%files debuginfo-common
%defattr(-,root,root)
/usr/src/debug/%{name}-%{version}/linux-%{KVERREL}.%{_target_cpu}
%if %{includexen}
%if %{with_xen}
/usr/src/debug/%{name}-%{version}/xen%{?XEN_VER}
%endif
%endif
%dir /usr/src/debug
%dir %{debuginfodir}
%dir %{debuginfodir}/%{image_install_path}
%dir %{debuginfodir}/lib
%dir %{debuginfodir}/lib/modules
%dir %{debuginfodir}/usr/src/kernels
%endif
%endif

###
### install
###

%install

cd linux-%{KVERREL}.%{_target_cpu}
%ifnarch %nobuildarches noarch
mkdir -p $RPM_BUILD_ROOT/etc/modprobe.d
cat > $RPM_BUILD_ROOT/etc/modprobe.d/blacklist-firewire << \EOF
# Comment out the next line to enable the firewire drivers
blacklist firewire-ohci
EOF
%endif

%if %{with_doc}
mkdir -p $RPM_BUILD_ROOT/usr/share/doc/kernel-doc-%{version}/Documentation

# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a+r *
# copy the source over
tar cf - Documentation | tar xf - -C $RPM_BUILD_ROOT/usr/share/doc/kernel-doc-%{version}
%endif

%if %{with_headers}
# Install kernel headers
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

# Manually go through the 'headers_check' process for every file, but
# don't die if it fails
chmod +x scripts/hdrcheck.sh
echo -e '*****\n*****\nHEADER EXPORT WARNINGS:\n*****' > hdrwarnings.txt
for FILE in `find $RPM_BUILD_ROOT/usr/include` ; do
    scripts/hdrcheck.sh $RPM_BUILD_ROOT/usr/include $FILE >> hdrwarnings.txt || :
done
echo -e '*****\n*****' >> hdrwarnings.txt
if grep -q exist hdrwarnings.txt; then
   sed s:^$RPM_BUILD_ROOT/usr/include/:: hdrwarnings.txt
   # Temporarily cause a build failure if header inconsistencies.
   exit 1
fi

# glibc provides scsi headers for itself, for now
rm -rf $RPM_BUILD_ROOT/usr/include/scsi
rm -f $RPM_BUILD_ROOT/usr/include/asm*/atomic.h
rm -f $RPM_BUILD_ROOT/usr/include/asm*/io.h
rm -f $RPM_BUILD_ROOT/usr/include/asm*/irq.h
%endif
###
### clean
###

%clean
rm -rf $RPM_BUILD_ROOT
rm -f %{_tmppath}/kernel-%{version}-%{release}*-kabideps

###
### scripts
###

%post
if [ `uname -i` == "x86_64" -o `uname -i` == "i386" ]; then
  if [ -f /etc/sysconfig/kernel ]; then
    /bin/sed -i -e 's/^DEFAULTKERNEL=kernel-smp$/DEFAULTKERNEL=kernel/' /etc/sysconfig/kernel || exit $?
  fi
fi
/sbin/new-kernel-pkg --package kernel --mkinitrd --depmod --install %{KVERREL} || exit $?
if [ -x /sbin/weak-modules ]
then
    /sbin/weak-modules --add-kernel %{KVERREL} || exit $?
fi

%post devel
if [ -f /etc/sysconfig/kernel ]
then
    . /etc/sysconfig/kernel || exit $?
fi
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ] ; then
  pushd /usr/src/kernels/%{KVERREL}-%{_target_cpu} > /dev/null
  /usr/bin/find . -type f | while read f; do hardlink -c /usr/src/kernels/*FC*/$f $f ; done
  popd > /dev/null
fi

%post PAE
if [ -f /etc/sysconfig/kernel ]; then
    /bin/sed -i -e 's/^DEFAULTKERNEL=kernel-smp$/DEFAULTKERNEL=kernel-PAE/' /etc/sysconfig/kernel
fi
/sbin/new-kernel-pkg --package kernel-PAE --mkinitrd --depmod --install %{KVERREL}PAE || exit $?
if [ -x /sbin/weak-modules ]
then
    /sbin/weak-modules --add-kernel %{KVERREL}PAE || exit $?
fi

%post PAE-devel
if [ -f /etc/sysconfig/kernel ]
then
    . /etc/sysconfig/kernel || exit $?
fi
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ] ; then
  pushd /usr/src/kernels/%{KVERREL}-PAE-%{_target_cpu} > /dev/null
  /usr/bin/find . -type f | while read f; do hardlink -c /usr/src/kernels/*FC*/$f $f ; done
  popd > /dev/null
fi

%post debug
/sbin/new-kernel-pkg --package kernel-debug --mkinitrd --depmod --install %{KVERREL}debug || exit $?
if [ -x /sbin/weak-modules ]
then
    /sbin/weak-modules --add-kernel %{KVERREL}debug || exit $?
fi

%post debug-devel
if [ -f /etc/sysconfig/kernel ]
then
    . /etc/sysconfig/kernel || exit $?
fi
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ] ; then
  pushd /usr/src/kernels/%{KVERREL}-debug-%{_target_cpu} > /dev/null
  /usr/bin/find . -type f | while read f; do hardlink -c /usr/src/kernels/*FC*/$f $f ; done
  popd > /dev/null
fi

%post xen
if [ `uname -i` == "x86_64" -o `uname -i` == "i386" ]; then
  if [ -f /etc/sysconfig/kernel ]; then
    /bin/sed -i -e 's/^DEFAULTKERNEL=kernel-xen[0U]/DEFAULTKERNEL=kernel-xen/' /etc/sysconfig/kernel || exit $?
  fi
fi
if [ -e /proc/xen/xsd_kva -o ! -d /proc/xen ]; then
	/sbin/new-kernel-pkg --package kernel-xen --mkinitrd --depmod --install --multiboot=/%{image_install_path}/xen.gz-%{KVERREL} %{KVERREL}xen || exit $?
else
	/sbin/new-kernel-pkg --package kernel-xen --mkinitrd --depmod --install %{KVERREL}xen || exit $?
fi
if [ -x /sbin/ldconfig ]
then
    /sbin/ldconfig -X || exit $?
fi
if [ -x /sbin/weak-modules ]
then
    /sbin/weak-modules --add-kernel %{KVERREL}xen || exit $?
fi

%post xen-devel
if [ -f /etc/sysconfig/kernel ]
then
    . /etc/sysconfig/kernel || exit $?
fi
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ] ; then
  pushd /usr/src/kernels/%{KVERREL}-xen-%{_target_cpu} > /dev/null
  /usr/bin/find . -type f | while read f; do hardlink -c /usr/src/kernels/*FC*/$f $f ; done
  popd > /dev/null
fi

%post kdump
%ifarch s390x
    ln -sf /boot/vmlinuz-%{KVERREL}kdump /boot/zfcpdump
%else
    /sbin/new-kernel-pkg --package kernel-kdump --mkinitrd --depmod --install %{KVERREL}kdump || exit $?
    if [ -x /sbin/weak-modules ]
    then
        /sbin/weak-modules --add-kernel %{KVERREL}kdump || exit $?
    fi
%endif

%post kdump-devel
if [ -f /etc/sysconfig/kernel ]
then
    . /etc/sysconfig/kernel || exit $?
fi
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ] ; then
  pushd /usr/src/kernels/%{KVERREL}-kdump-%{_target_cpu} > /dev/null
  /usr/bin/find . -type f | while read f; do hardlink -c /usr/src/kernels/*FC*/$f $f ; done
  popd > /dev/null
fi

%preun
/sbin/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVERREL} || exit $?
if [ -x /sbin/weak-modules ]
then
    /sbin/weak-modules --remove-kernel %{KVERREL} || exit $?
fi

%preun PAE
/sbin/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVERREL}PAE || exit $?
if [ -x /sbin/weak-modules ]
then
    /sbin/weak-modules --remove-kernel %{KVERREL}PAE || exit $?
fi

%preun kdump
%ifnarch s390x
    /sbin/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVERREL}kdump || exit $?
    if [ -x /sbin/weak-modules ]
    then
        /sbin/weak-modules --remove-kernel %{KVERREL}kdump || exit $?
    fi
%endif

%preun debug
/sbin/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVERREL}debug || exit $?
if [ -x /sbin/weak-modules ]
then
    /sbin/weak-modules --remove-kernel %{KVERREL}debug || exit $?
fi

%preun xen
/sbin/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVERREL}xen || exit $?
if [ -x /sbin/weak-modules ]
then
    /sbin/weak-modules --remove-kernel %{KVERREL}xen || exit $?
fi

%postun kdump
%ifarch s390x
    # Create softlink to latest remaining kdump kernel.
    # If no more kdump kernel is available, remove softlink.
    if [ "$(readlink /boot/zfcpdump)" == "/boot/vmlinuz-%{KVERREL}kdump" ]
    then
        vmlinuz_next=$(ls /boot/vmlinuz-*kdump 2> /dev/null | sort | tail -n1)
        if [ $vmlinuz_next ]
        then
            ln -sf $vmlinuz_next /boot/zfcpdump
        else
            rm -f /boot/zfcpdump
        fi
    fi
%endif

###
### file lists
###

# This is %{image_install_path} on an arch where that includes ELF files,
# or empty otherwise.
%define elf_image_install_path %{?kernel_image_elf:%{image_install_path}}

%if %{with_up}
%if %{with_debuginfo}
%ifnarch noarch
%package debuginfo
Summary: Debug information for package %{name}
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{KVERREL}
Provides: %{name}-debuginfo-%{_target_cpu} = %{KVERREL}
%description debuginfo
This package provides debug information for package %{name}
This is required to use SystemTap with %{name}-%{KVERREL}.
%files debuginfo
%defattr(-,root,root)
%if "%{elf_image_install_path}" != ""
%{debuginfodir}/%{elf_image_install_path}/*-%{KVERREL}.debug
%endif
%{debuginfodir}/lib/modules/%{KVERREL}
%{debuginfodir}/usr/src/kernels/%{KVERREL}-%{_target_cpu}
%endif
%endif

%files
%defattr(-,root,root)
/%{image_install_path}/vmlinuz-%{KVERREL}
%if %{with_fips}
/%{image_install_path}/.vmlinuz-%{KVERREL}.hmac
%endif
/boot/System.map-%{KVERREL}
/boot/symvers-%{KVERREL}.gz
/boot/config-%{KVERREL}
%dir /lib/modules/%{KVERREL}
/lib/modules/%{KVERREL}/kernel
/lib/modules/%{KVERREL}/build
/lib/modules/%{KVERREL}/source
/lib/modules/%{KVERREL}/extra
/lib/modules/%{KVERREL}/updates
/lib/modules/%{KVERREL}/weak-updates
%ghost /boot/initrd-%{KVERREL}.img
%config(noreplace) /etc/modprobe.d/blacklist-firewire

%files devel
%defattr(-,root,root)
%dir /usr/src/kernels
%verify(not mtime) /usr/src/kernels/%{KVERREL}-%{_target_cpu}
%endif

%if %{with_headers}
%files headers
%defattr(-,root,root)
/usr/include/*
%endif

%if %{with_pae}
%if %{with_debuginfo}
%ifnarch noarch
%package PAE-debuginfo
Summary: Debug information for package %{name}-PAE
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{KVERREL}
Provides: %{name}-%PAE-debuginfo-%{_target_cpu} = %{KVERREL}
%description PAE-debuginfo
This package provides debug information for package %{name}-PAE
This is required to use SystemTap with %{name}-PAE-%{KVERREL}.
%files PAE-debuginfo
%defattr(-,root,root)
%if "%{elf_image_install_path}" != ""
%{debuginfodir}/%{elf_image_install_path}/*-%{KVERREL}PAE.debug
%endif
%{debuginfodir}/lib/modules/%{KVERREL}PAE
%{debuginfodir}/usr/src/kernels/%{KVERREL}-PAE-%{_target_cpu}
%endif
%endif

%files PAE
%defattr(-,root,root)
/%{image_install_path}/vmlinuz-%{KVERREL}PAE
%if %{with_fips}
/%{image_install_path}/.vmlinuz-%{KVERREL}PAE.hmac
%endif
/boot/System.map-%{KVERREL}PAE
/boot/symvers-%{KVERREL}PAE.gz
/boot/config-%{KVERREL}PAE
%dir /lib/modules/%{KVERREL}PAE
/lib/modules/%{KVERREL}PAE/kernel
/lib/modules/%{KVERREL}PAE/build
/lib/modules/%{KVERREL}PAE/source
/lib/modules/%{KVERREL}PAE/extra
/lib/modules/%{KVERREL}PAE/updates
/lib/modules/%{KVERREL}PAE/weak-updates
%ghost /boot/initrd-%{KVERREL}PAE.img
%config(noreplace) /etc/modprobe.d/blacklist-firewire

%files PAE-devel
%defattr(-,root,root)
%dir /usr/src/kernels
%verify(not mtime) /usr/src/kernels/%{KVERREL}-PAE-%{_target_cpu}
/usr/src/kernels/%{KVERREL}PAE-%{_target_cpu}
%endif

%if %{with_debug}
%if %{with_debuginfo}
%ifnarch noarch
%files debug-debuginfo
%defattr(-,root,root)
%if "%{elf_image_install_path}" != ""
%{debuginfodir}/%{elf_image_install_path}/*-%{KVERREL}debug.debug
%endif
%{debuginfodir}/lib/modules/%{KVERREL}debug
%{debuginfodir}/usr/src/kernels/%{KVERREL}-debug-%{_target_cpu}
%endif
%endif

%files debug
%defattr(-,root,root)
/%{image_install_path}/vmlinuz-%{KVERREL}debug
%if %{with_fips}
/%{image_install_path}/.vmlinuz-%{KVERREL}debug.hmac
%endif
/boot/System.map-%{KVERREL}debug
/boot/symvers-%{KVERREL}debug.gz
/boot/config-%{KVERREL}debug
%dir /lib/modules/%{KVERREL}debug
/lib/modules/%{KVERREL}debug/kernel
/lib/modules/%{KVERREL}debug/build
/lib/modules/%{KVERREL}debug/source
/lib/modules/%{KVERREL}debug/extra
/lib/modules/%{KVERREL}debug/updates
/lib/modules/%{KVERREL}debug/weak-updates
%ghost /boot/initrd-%{KVERREL}debug.img
%config(noreplace) /etc/modprobe.d/blacklist-firewire

%files debug-devel
%defattr(-,root,root)
%dir /usr/src/kernels
%verify(not mtime) /usr/src/kernels/%{KVERREL}-debug-%{_target_cpu}
/usr/src/kernels/%{KVERREL}debug-%{_target_cpu}
%endif

%if %{includexen}
%if %{with_xen}
%if %{with_debuginfo}
%ifnarch noarch
%package xen-debuginfo
Summary: Debug information for package %{name}-xen
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{KVERREL}
Provides: %{name}-xen-debuginfo-%{_target_cpu} = %{KVERREL}
%description xen-debuginfo
This package provides debug information for package %{name}-xen
This is required to use SystemTap with %{name}-xen-%{KVERREL}.
%files xen-debuginfo
%defattr(-,root,root)
%if "%{elf_image_install_path}" != ""
%{debuginfodir}/%{elf_image_install_path}/*-%{KVERREL}xen.debug
%endif
%{debuginfodir}/lib/modules/%{KVERREL}xen
%{debuginfodir}/usr/src/kernels/%{KVERREL}-xen-%{_target_cpu}
%{debuginfodir}/boot/xen*-%{KVERREL}.debug
%endif
%endif

%files xen
%defattr(-,root,root)
/%{image_install_path}/vmlinuz-%{KVERREL}xen
%if %{with_fips}
/%{image_install_path}/.vmlinuz-%{KVERREL}xen.hmac
%endif
/boot/System.map-%{KVERREL}xen
/boot/symvers-%{KVERREL}xen.gz
/boot/config-%{KVERREL}xen
/%{image_install_path}/xen.gz-%{KVERREL}
/boot/xen-syms-%{KVERREL}
%dir /lib/modules/%{KVERREL}xen
/lib/modules/%{KVERREL}xen/kernel
%verify(not mtime) /lib/modules/%{KVERREL}xen/build
/lib/modules/%{KVERREL}xen/source
/etc/ld.so.conf.d/kernelcap-%{KVERREL}.conf
/lib/modules/%{KVERREL}xen/extra
/lib/modules/%{KVERREL}xen/updates
/lib/modules/%{KVERREL}xen/weak-updates
%ghost /boot/initrd-%{KVERREL}xen.img
%config(noreplace) /etc/modprobe.d/blacklist-firewire

%files xen-devel
%defattr(-,root,root)
%dir /usr/src/kernels
%verify(not mtime) /usr/src/kernels/%{KVERREL}-xen-%{_target_cpu}
/usr/src/kernels/%{KVERREL}xen-%{_target_cpu}
%endif

%endif

%if %{with_kdump}
%if %{with_debuginfo}
%ifnarch noarch
%package kdump-debuginfo
Summary: Debug information for package %{name}-kdump
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{KVERREL}
Provides: %{name}-kdump-debuginfo-%{_target_cpu} = %{KVERREL}
%description kdump-debuginfo
This package provides debug information for package %{name}-kdump
This is required to use SystemTap with %{name}-kdump-%{KVERREL}.
%files kdump-debuginfo
%defattr(-,root,root)
%ifnarch s390x
%if "%{image_install_path}" != ""
%{debuginfodir}/%{image_install_path}/*-%{KVERREL}kdump.debug
%endif
%else
%if "%{elf_image_install_path}" != ""
%{debuginfodir}/%{elf_image_install_path}/*-%{KVERREL}kdump.debug
%endif
%endif
%{debuginfodir}/lib/modules/%{KVERREL}kdump
%{debuginfodir}/usr/src/kernels/%{KVERREL}-kdump-%{_target_cpu}
%endif
%endif

%files kdump
%defattr(-,root,root)
%ifnarch s390x
/%{image_install_path}/vmlinux-%{KVERREL}kdump
%if %{with_fips}
/%{image_install_path}/.vmlinux-%{KVERREL}kdump.hmac
%endif
%else
/%{image_install_path}/vmlinuz-%{KVERREL}kdump
%if %{with_fips}
/%{image_install_path}/.vmlinuz-%{KVERREL}kdump.hmac
%endif
%endif
/boot/System.map-%{KVERREL}kdump
/boot/symvers-%{KVERREL}kdump.gz
/boot/config-%{KVERREL}kdump
%dir /lib/modules/%{KVERREL}kdump
/lib/modules/%{KVERREL}kdump/build
/lib/modules/%{KVERREL}kdump/source
%ifnarch s390x
/lib/modules/%{KVERREL}kdump/kernel
/lib/modules/%{KVERREL}kdump/extra
/lib/modules/%{KVERREL}kdump/updates
/lib/modules/%{KVERREL}kdump/weak-updates
%endif
%ghost /boot/initrd-%{KVERREL}kdump.img
%config(noreplace) /etc/modprobe.d/blacklist-firewire

%files kdump-devel
%defattr(-,root,root)
%dir /usr/src/kernels
%verify(not mtime) /usr/src/kernels/%{KVERREL}-kdump-%{_target_cpu}
/usr/src/kernels/%{KVERREL}kdump-%{_target_cpu}
%endif

# only some architecture builds need kernel-doc

%if %{with_doc}
%files doc
%defattr(-,root,root)
%{_datadir}/doc/kernel-doc-%{version}/Documentation/*
%dir %{_datadir}/doc/kernel-doc-%{version}/Documentation
%dir %{_datadir}/doc/kernel-doc-%{version}
%endif

%changelog
* Thu Jul 26 2012 Alexander Gordeev <agordeev@redhat.com> [2.6.18-308.13.1.el5]
- [net] e1000e: Cleanup logic in e1000_check_for_serdes_link_82571 (Dean Nelson) [841370 771366]
- [net] e1000e: Correct link check logic for 82571 serdes (Dean Nelson) [841370 771366]
- [mm] NULL pointer dereference in __vm_enough_memory (Jerome Marchand) [840077 836244]
- [fs] dlm: fix slow rsb search in dir recovery (David Teigland) [838140 753244]
- [fs] autofs: propogate LOOKUP_DIRECTORY flag only for last comp (Ian Kent) [830264 814418]
- [fs] ext4: properly dirty split extent nodes (Eric Sandeen) [840946 839770]
- [scsi] don't offline devices with a reservation conflict (David Jeffery) [839196 835660]
- [fs] ext4: Fix overflow caused by missing cast in ext4_fallocate (Lukas Czerner) [837226 830351]
- [net] dl2k: Clean up rio_ioctl (Weiping Pan) [818822 818823] {CVE-2012-2313}
- [x86] sched: Avoid unnecessary overflow in sched_clock (Prarit Bhargava) [835450 834562]
- [net] tg3: Fix TSO handling (John Feeney) [833182 795672]
- [input] evdev: use after free from open/disconnect race (David Jeffery) [832448 822166]

* Fri Jul 13 2012 Alexander Gordeev <agordeev@redhat.com> [2.6.18-308.12.1.el5]
- [fs] nfs: Don't allow multiple mounts on same mntpnt with -o noac (Sachin Prabhu) [839806 839753]

* Fri Jun 15 2012 Alexander Gordeev <agordeev@redhat.com> [2.6.18-308.11.1.el5]
- [net] ixgbe: remove flow director stats (Andy Gospodarek) [832169 830226]
- [net] ixgbe: fix default return value for ixgbe_cache_ring_fdir (Andy Gospodarek) [832169 830226]
- [net] ixgbe: reverting setup redirection table for multiple packet buffers (Andy Gospodarek) [832169 830226]

* Thu Jun 14 2012 Alexander Gordeev <agordeev@redhat.com> [2.6.18-308.10.1.el5]
- [xen] x86_64: check address on trap handlers or guest callbacks (Paolo Bonzini) [813430 813431] {CVE-2012-0217}
- [xen] x86_64: Do not execute sysret with a non-canonical return address (Paolo Bonzini) [813430 813431] {CVE-2012-0217}
- [xen] x86: prevent hv boot on AMD CPUs with Erratum 121 (Laszlo Ersek) [824969 824970] {CVE-2012-2934}
- [scsi] qla2xxx: Use ha->pdev->revision in 4Gbps MSI-X check. (Chad Dupuis) [816373 800653]
- [fs] sunrpc: do array overrun check in svc_recv before page alloc (J. Bruce Fields) [820358 814626]
- [fs] knfsd: fix an NFSD bug with full size non-page-aligned reads (J. Bruce Fields) [820358 814626]
- [fs] sunrpc: fix oops due to overrunning server's page array (J. Bruce Fields) [820358 814626]
- [fs] epoll: clear the tfile_check_list on -ELOOP (Jason Baron) [829670 817131]
- [x86_64] sched: Avoid unnecessary overflow in sched_clock (Prarit Bhargava) [824654 818787]
- [net] sunrpc: Don't use list_for_each_entry_safe in rpc_wake_up (Steve Dickson) [817571 809937]
- [s390] qeth: add missing wake_up call (Hendrik Brueckner) [829059 790900]

* Wed Jun 06 2012 Alexander Gordeev <agordeev@redhat.com> [2.6.18-308.9.1.el5]
- [fs] jbd: clear b_modified before moving the jh to a different transaction (Josef Bacik) [827205 563247]

* Fri May 04 2012 Alexander Gordeev <agordeev@redhat.com> [2.6.18-308.8.1.el5]
- [net] sock: validate data_len before allocating skb in sock_alloc_send_pskb() (Jason Wang) [816290 816106] {CVE-2012-2136}
- [net] tg3: Fix VLAN tagging assignments (John Feeney) [817691 797011]
- [net] ixgbe: do not stop stripping VLAN tags in promiscuous mode (Andy Gospodarek) [809791 804800]
- [s390] zcrypt: Fix parameter checking for ZSECSENDCPRB ioctl (Hendrik Brueckner) [810123 808489]
- [x86] unwind information fix for the vsyscall DSO (Prarit Bhargava) [807930 805799]

* Mon Apr 30 2012 Alexander Gordeev <agordeev@redhat.com> [2.6.18-308.7.1.el5]
- [fs] epoll: Don't limit non-nested epoll paths (Jason Baron) [809380 804778]

* Fri Apr 27 2012 Alexander Gordeev <agordeev@redhat.com> [2.6.18-308.6.1.el5]
- [scsi] fc class: fix scanning when devs are offline (Mike Christie) [816684 799530]
- [md] dm-multipath: delay retry of bypassed pg (Mike Christie) [816684 799530]
- [net] bonding: properly unset current_arp_slave on slave link up (Veaceslav Falico) [811927 800575]
- [net] bonding: remove {master,vlan}_ip and query devices instead (Andy Gospodarek) [810321 772216]

* Tue Apr 17 2012 Alexander Gordeev <agordeev@redhat.com> [2.6.18-308.5.1.el5]
- [scsi] skip sense logging for some ATA PASS-THROUGH cdbs (David Milburn) [807265 788777]

* Wed Mar 28 2012 Alexander Gordeev <agordeev@redhat.com> [2.6.18-308.4.1.el5]
- [net] ipv6: fix skb double free in xfrm6_tunnel (Jiri Benc) [752305 743375] {CVE-2012-1583}

* Thu Mar 22 2012 Alexander Gordeev <agordeev@redhat.com> [2.6.18-308.3.1.el5]
- [net] be2net: cancel be_worker during EEH recovery (Ivan Vecera) [805462 773735]
- [net] be2net: add vlan/rx-mode/flow-control config to be_setup (Ivan Vecera) [805462 773735]
- [x86] disable TSC synchronization when using kvmclock (Marcelo Tosatti) [805460 799170]
- [fs] vfs: fix LOOKUP_DIRECTORY not propagated to managed_dentry (Ian Kent) [801726 798809]
- [fs] vfs: fix d_instantiate_unique (Ian Kent) [801726 798809]
- [fs] nfs: allow high priority COMMITs to bypass inode commit lock (Jeff Layton) [799941 773777]
- [fs] nfs: don't skip COMMITs if system under is mem pressure (Jeff Layton) [799941 773777]
- [scsi] qla2xxx: Read the HCCR register to flush any PCIe writes (Chad Dupuis) [798748 772192]
- [scsi] qla2xxx: Complete mbox cmd timeout before next reset cycle (Chad Dupuis) [798748 772192]
- [s390] qdio: wrong buffers-used counter for ERROR buffers (Hendrik Brueckner) [801724 790840]
- [net] bridge: Reset IPCB when entering IP stack (Herbert Xu) [804721 749813]
- [fs] procfs: add hidepid= and gid= mount options (Jerome Marchand) [770649 770650]
- [fs] procfs: parse mount options (Jerome Marchand) [770649 770650]

* Tue Feb 21 2012 Alexander Gordeev <agordeev@redhat.com> [2.6.18-308.2.1.el5]
- [fs] nfs: nfs_fhget should wait on I_NEW instead of I_LOCK (Sachin Prabhu) [795664 785062]

* Fri Feb 17 2012 Alexander Gordeev <agordeev@redhat.com> [2.6.18-308.1.1.el5]
- Revert: [scsi] qla2xxx: avoid SCSI host_lock dep in queuecommand (Chad Dupuis) [790907 782790]
- Revert: [scsi] qla2xxx: fix IO failure during chip reset (Chad Dupuis) [790907 782790]
- [net] tg3: Fix 4k tx and recovery code (John Feeney) [790910 782677]
- [net] bnx2x: make bnx2x_close static again (Michal Schmidt) [790912 782124]
- [net] bnx2x: add fan failure event handling (Michal Schmidt) [790912 782124]
- [usb] cdc-acm: make lock use interrupt safe (Bryn M. Reeves) [790778 789067]
- [kernel] sysctl: restrict write access to dmesg_restrict (Phillip Lougher) [749246 749247]
- [net] igb: reset PHY after recovering from PHY power down (Stefan Assmann) [786168 783043]
- [fs] prevent lock contention in shrink_dcache_sb via private list (Lachlan McIlroy) [789369 746122]

* Fri Jan 27 2012 Jarod Wilson <jarod@redhat.com> [2.6.18-308.el5]
- [scsi] lpfc: Update lpfc version for 8.2.0.108.4p driver release (Rob Evers) [784073]
- [scsi] lpfc: Fix FCP EQ memory check init w/single int vector (Rob Evers) [784073]

* Tue Jan 24 2012 Jarod Wilson <jarod@redhat.com> [2.6.18-307.el5]
- [s390] crypto: Reset sha2 index after processing partial block (David Howells) [677860]
- Revert: [fs] xfs: implement ->dirty_inode to fix timestamp (Eric Sandeen) [653215]

* Tue Jan 24 2012 Jarod Wilson <jarod@redhat.com> [2.6.18-306.el5]
- [s390] pfault: ignore leftover completion interrupts (Jarod Wilson) [753194]
- [cpufreq] powernow-k8: Fix indexing issue (Frank Arnold) [782773]
- [scsi] device_handler: optimize transition retries (Rob Evers) [733635]
- [net] qlge: fix size of external list for TX address descriptors (Chad Dupuis) [772696]
- [net] igmp: Avoid zero delay when rx'ing odd mix of IGMP queries (Jiri Pirko) [772869]
- [net] be2net: create RSS rings even in multi-channel configs (Ivan Vecera) [773114]
- [net] ipv6: track device renames in snmp6 (Andy Gospodarek) [758923]
- [fs] jbd2: clear BH_Delay & BH_Unwritten in journal_unmap_buffer (Eric Sandeen) [783284] {CVE-2011-4086}
- [fs] epoll: workarounds to preserve kernel ABI (Jason Baron) [681692] {CVE-2011-1083}
- [fs] epoll: limit paths (Jason Baron) [681692] {CVE-2011-1083}
- [fs] epoll: prevent creating circular epoll structures (Jason Baron) [681692] {CVE-2011-1083}
- [fs] epoll: add ep_call_nested() (Jason Baron) [681692] {CVE-2011-1083}
- [fs] gfs2: additional fix for inode allocation error path (Robert S Peterson) [767377]
- [fs] gfs2: Revert clean up fsync changes (Robert S Peterson) [767377]
- [fs] ext4: ignore EXT4_INODE_JOURNAL_DATA flag with delalloc (Lukas Czerner) [769386]
- [mm] filemap: Make write(2) interruptible by a fatal signal (Lukas Czerner) [740898]
- [mm] Make task in balance_dirty_pages killable (Lukas Czerner) [740898]
- [fs] ext4: fix the deadlock in mpage_da_map_and_submit (Lukas Czerner) [740898]
- [fs] ext4: fix deadlock in ext4_ordered_write_end (Lukas Czerner) [740898]
- [fs] ext4: mark multi-page IO complete on mapping failure (Lukas Czerner) [740898]
- [fs] ext4: make invalidate pages handle page range properly (Lukas Czerner) [740898]
- [fs] ext4: call mpage_da_submit_io from mpage_da_map_blocks (Lukas Czerner) [740898]
- [fs] nfsd: Avoid excess stack usage in svc_tcp_recvfrom (J. Bruce Fields) [765751]
- [fs] nfsd: Replace two page lists in struct svc_rqst with one (J. Bruce Fields) [765751]

* Mon Jan 16 2012 Jarod Wilson <jarod@redhat.com> [2.6.18-305.el5]
- [edac] i5000: don't crash before showing the edac error (Mauro Carvalho Chehab) [713034]
- [Documentation] Add pci=noseg to kernel-parameters.txt (Prarit Bhargava) [743168]
- [net] ipv6: fix tcp_v6_conn_request (Jiri Benc) [714670]
- [redhat] update RHEL_MINOR to 8 for 5.8 release (Jarod Wilson) [773033]
- [misc] Move exit_robust_list to mm_release, null lists on cleanup (Laszlo Ersek) [750283] {CVE-2012-0028}
- [fs] nfs: Fix an O_DIRECT Oops (Jeff Layton) [754620] {CVE-2011-4325}
- [xen] x86: fix a few 32-on-64 compat mode issues (Igor Mammedov) [700752]

* Mon Jan 09 2012 Jarod Wilson <jarod@redhat.com> [2.6.18-304.el5]
- [fs] gfs2: Fix inode allocation error path (Robert S Peterson) [767377]
- [fs] gfs2: Clean up fsync (Robert S Peterson) [767377]
- [misc] fix list_head userspace export regression error (Jarod Wilson) [772663]
- [block] disable SG_IO ioctls on virtio-blk devices (Paolo Bonzini) [771592]
- [net] cxgb4: fix firmware corruption (Neil Horman) [756661]
- [net] be2net: remove incorrect calls to netif_carrier_off (Ivan Vecera) [771391]
- [scsi] lpfc: Update lpfc version for 8.2.0.108.3p driver release (Rob Evers) [769385]
- [scsi] lpfc: Fix panic during EEH recovery on SLI4 FC port (Rob Evers) [769385]
- [scsi] lpfc: Fix a crash while deleting 256 vports (Rob Evers) [769385]
- [scsi] lpfc: Fixed OCM failing *_OBJECT mailbox pass-through (Rob Evers) [769385]
- [scsi] lpfc: Fixed firmware download regression (Rob Evers) [769385]
- [scsi] lpfc: Fix system crash when LPe16000 fails to initialize (Rob Evers) [769385]

* Tue Jan 03 2012 Jarod Wilson <jarod@redhat.com> [2.6.18-303.el5]
- [scsi] qla2xxx: Update FC-transport port_state translation matrix (Chad Dupuis) [765866]
- [scsi] qla2xxx: Don't call alloc_fw_dump for ISP82XX (Chad Dupuis) [765866]
- [scsi] qla2xxx: Remove qla2x00_wait_for_loop_ready function (Chad Dupuis) [765866]
- [scsi] qla2xxx: Display FCP_CMND priority on update (Chad Dupuis) [765866]
- [scsi] qla2xxx: Check for SCSI status on underruns (Chad Dupuis) [765866]
- [scsi] qla4xxx: v5.02.04.02.05.08-d0 (Chad Dupuis) [769019]
- [scsi] qla4xxx: clear the RISC interrupt bit during firmware init (Chad Dupuis) [769019]
- [scsi] qla4xxx: v5.02.04.01.05.08-d0 (Chad Dupuis) [758762]
- [scsi] qla4xxx: Fix panic due to incorrect tag_value_stride (Chad Dupuis) [758762]
- [fs] xfs: implement ->dirty_inode to fix timestamp handling (Carlos Maiolino) [653215]
- [net] drop_monitor: return -EAGAIN on duplicate state changes (Neil Horman) [688791]
- [net] ipv6: make disable_ipv6 work (Weiping Pan) [760199]
- [net] bnx2x: fix failure to bring link up on BCM57810 (Michal Schmidt) [751025]
- [scsi] isci: link speeds default to gen2 (David Milburn) [768151]
- [fs] jbd: fix race in buffer processing in commit code (Josef Bacik) [756643]
- [s390] kernel: cpu hotplug vs missing pfault completion interrupt (Hendrik Brueckner) [753194]
- [block] loop: Don't call loop_unplug on non-configured device (Veaceslav Falico) [617668]
- [virt] xen/netback: Clear IFF_TX_SKB_SHARING flags (Neil Horman) [753173]
- [scsi] sd: fix 32-on-64 block device ioctls (Paolo Bonzini) [752386] {CVE-2011-4127}
- [md] dm: do not forward ioctls from LVs to the underlying devices (Paolo Bonzini) [752386] {CVE-2011-4127}
- [block] fail SCSI passthrough ioctls on partition devices (Paolo Bonzini) [752386] {CVE-2011-4127}
- [block] add and use scsi_blk_cmd_ioctl (Paolo Bonzini) [752386] {CVE-2011-4127}

* Mon Dec 19 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-302.el5]
- [redhat] configs: Include generic ppc64 opts on all ppc64 configs (Alexander Gordeev) [748426]
- [fs] xfs: don't block on buffer read errors (Boris Ranto) [709223]
- [fs] nfs: Display lookupcache option in /proc/mounts (Sachin Prabhu) [706305]
- [net] bonding: Don't allow mode change via sysfs w/slaves present (Veaceslav Falico) [768208]
- [net] be2net: Fix disabling multicast promiscuous mode (Ivan Vecera) [751998]
- [net] be2net: Fix endian issue in RX filter command (Ivan Vecera) [751998]
- [net] be2net: Changing MAC Address of a VF was broken (Ivan Vecera) [751998]
- [net] be2net: don't create multiple rings in multi channel mode (Ivan Vecera) [751998]
- [net] be2net: Making die temperature ioctl call async (Ivan Vecera) [751998]
- [net] be2net: Fix Endian issues in response read log length field (Ivan Vecera) [751998]
- [net] be2net: Change data type of on die temperature stat (Ivan Vecera) [751998]
- [net] be2net: Add 60 second delay for dump on recovery from EEH (Ivan Vecera) [751998]
- [net] be2net: Show newly flashed FW ver in ethtool (Ivan Vecera) [751998]
- [net] be2net: increase FW update completion timeout (Ivan Vecera) [751998]
- [net] be2net: Fix race in posting rx buffers (Ivan Vecera) [751998]
- [net] be2net: Store vid from grp5 event instead of vlan_tag (Ivan Vecera) [751998]
- [net] be2net: drop pkts that do not belong to the port (Ivan Vecera) [751998]
- [fs] ext4: fix BUG_ON() in ext4_ext_insert_extent() (Lukas Czerner) [747946] {CVE-2011-3638}

* Tue Dec 13 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-301.el5]
- [net] e1000e: Avoid wrong check on TX hang (Dean Nelson) [746272]
- [net] tg3: Fix TSO loopback test (John Feeney) [755202]
- [net] ipvs: Fix memory leak when using one packet scheduler (Thomas Graf) [757882]
- [net] ipv6: Defer device init until valid qdisc specified (Neil Horman) [758736]
- [block] nbd: prevent sock_xmit from attempting to use NULL socket (Jeff Moyer) [676491]
- [net] tg3: Scale back code that modifies MRRS (John Feeney) [758882]
- [fs] xfs: Fix memory corruption in xfs_readlink (Carlos Maiolino) [749160] {CVE-2011-4077}
- [net] cxgb3: key cxgb3 driver to work based on NETIF_F_GRO (Neil Horman) [754709]
- [net] cxgb3: fix vfree BUG halt in rcu calback (Neil Horman) [756410]
- [net] ipv4: fix IN_DEV_ACCEPT_LOCAL() (Weiping Pan) [758993]
- [misc] cpu: Fix APIC calibration issues on VMware (Prarit Bhargava) [743368]
- [net] igb: Loopback functionality support for i350 devices (Stefan Assmann) [758059]

* Thu Dec 01 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-300.el5]
- [pci] intel-iommu: Default to non-coherent for unattached domains (Don Dutile) [753924]
- [scsi] bfa: update driver embedded firmware to 3.0.0.0 (Rob Evers) [752972]
- [scsi] bnx2i: Fix endian on TTT for NOP out transmission (Mike Christie) [752626]
- [input] evdev: Fix spin lock context in evdev_pass_event() (Don Zickus) [734900]
- [net] bnx2x: Add new PHY BCM54616 (Michal Schmidt) [733889]
- [scsi] ipr: add definitions for additional adapter (Steve Best) [753910]
- [scsi] ipr: Fix BUG on adapter dump timeout (Steve Best) [753910]
- [scsi] ipr: Add support to flash FPGA and flash back DRAM images (Steve Best) [753910]
- [scsi] ipr: Stop reading adapter dump prematurely (Steve Best) [753910]
- [char] rtc: fix reported IRQ rate for when HPET is enabled (Prarit Bhargava) [740299]
- [block] cciss: add Smart Array 5i to the kdump blacklist (Tomas Henzl) [752690]
- [scsi] qla4xxx: Update version number to V5.02.04.00.05.08-d0 (Chad Dupuis) [714214]
- [scsi] qla4xxx: Do not recover adapter if in FAILED state (Chad Dupuis) [714214]
- [scsi] qla4xxx: Fix duplicate targets in BIOS do not show up (Chad Dupuis) [714214]
- [scsi] qla4xxx: Fix rmmod kernel trace with ql4xdontresethba=1 (Chad Dupuis) [714214]
- [scsi] qla4xxx: Add ql4xmaxcmds Command Line Parameter (Chad Dupuis) [714214]
- [scsi] qla4xxx: Correct the locking mechanism (Chad Dupuis) [714214]
- [scsi] qla4xxx: Minidump implementation (Chad Dupuis) [714214]
- [scsi] qla4xxx: Device quiescent and loopback changes (Chad Dupuis) [714214]
- [scsi] qla4xxx: Add new FLT firmware region (Chad Dupuis) [714214]
- [scsi] qla4xxx: Prevent CPU lockups when ql4xdontresethba is set (Chad Dupuis) [714214]
- [scsi] qla4xxx: Updated the reset sequence for ISP82xx (Chad Dupuis) [714214]
- [scsi] qla4xxx: set set_ddb_entry with correct dma buffer (Chad Dupuis) [714214]
- [scsi] qla4xxx: Reset retry_relogin_timer to trigger a relogin (Chad Dupuis) [714214]
- [scsi] qla4xxx: Update ddb_entry on fw_ddb_index changes (Chad Dupuis) [714214]
- [scsi] qla4xxx: BFS issue when same target devices added twice (Chad Dupuis) [714214]
- [scsi] qla4xxx: mark device missing in recover adapter (Chad Dupuis) [714214]
- [scsi] qla4xxx: Perform context resets on context failures (Chad Dupuis) [714214]
- [scsi] qla4xxx: show hardware/firmware regs for more debug info (Chad Dupuis) [714214]
- [scsi] qla4xxx: Pass correct fw_ddb_index to abort_task (Chad Dupuis) [714214]
- [scsi] qla4xxx: check command already completed when abort issued (Chad Dupuis) [714214]
- [scsi] qla4xxx: Use os_target_id to identify a session (Chad Dupuis) [714214]
- [fs] dcache: Fix dentry loop detection deadlock (David Howells) [717959]
- [net] cxgb4: fix ability to disable tx cksum and change tso (Neil Horman) [754711]
- [fs] nfs: when attempting dir open, fall back on normal lookup (Jeff Layton) [740162]
- [fs] nfs: remove BUG() from encode_share_access() (Jeff Layton) [754901]
- [fs] epoll: use up all the timeout (Jason Baron) [705138]
- [s390] qdio: avoid race leading to stall if CQ is used (Hendrik Brueckner) [753193]
- [scsi] libsas: disable scanning lun > 0 on ata devices (David Milburn) [749309]
- [scsi] isci: atapi support (David Milburn) [749309]
- [scsi] isci: initial sgpio write support (David Milburn) [743965]
- [scsi] isci: fix sgpio register definitions (David Milburn) [743965]
- [scsi] isci: export phy events via ->lldd_control_phy() (David Milburn) [747670]
- [scsi] isci: port state should be set to stopping on last phy (David Milburn) [747670]
- [scsi] isci: fix decode of DONE_CRC_ERR TC completion status (David Milburn) [747670]
- [scsi] isci: SATA/STP I/O only returned in normal path to libsas (David Milburn) [747670]
- [scsi] isci: fix support for large smp requests (David Milburn) [747670]
- [scsi] isci: fix missed unlock in apc_agent_timeout() (David Milburn) [747670]
- [scsi] isci: fix event-get pointer increment (David Milburn) [747670]
- [scsi] isci: add version number (David Milburn) [747670]
- [scsi] isci: dynamic interrupt coalescing (David Milburn) [747670]
- [scsi] isci: fix sata response handling (David Milburn) [747670]
- [scsi] isci: Leave requests alone if already terminating (David Milburn) [747670]
- [misc] irq: Check for spurious IRQ only on disabled IRQs (Prarit Bhargava) [756412]
- [net] sctp: Fix another race during accept/peeloff (Thomas Graf) [714870]
- [net] bonding: change slave->speed from u16 to u32 (Weiping Pan) [747547]
- [scsi] bnx2i: set PF_NOFREEZE in IO thread (Mike Christie) [753729]
- [fs] hfs: add sanity check for file name length (Eric Sandeen) [755433] {CVE-2011-4330}
- [fs] aio: remove upper bound on retries (Jeff Moyer) [753271]

* Wed Nov 23 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-299.el5]
- [scsi] be2iscsi: Move driver Version to 4.1.239.0 (Mike Christie) [744343]
- [scsi] be2iscsi: memset wrb for ring create (Mike Christie) [744343]
- [scsi] be2iscsi: Fix for when task->sc was cleaned up earlier (Mike Christie) [744343]
- [scsi] be2iscsi: Fix for wrong dmsg setting in wrb (Mike Christie) [744343]
- [scsi] be2iscsi: Fix for kdump failure (Mike Christie) [744343]
- [net] ethtool: Support large register dumps (Neil Horman) [753200]
- [fs] proc: Fix select on /proc files without ->poll (David Howells) [751214]
- [net] igb: bump version to reflect RHEL5.8 updates (Stefan Assmann) [754359]
- [fs] dcache: Log ELOOP rather than creating a loop (David Howells) [717959]
- [fs] dcache: Fix loop checks in d_materialise_unique (David Howells) [717959]
- [fs] nfs: Ensure we mark inode as dirty if early exit from commit (Jeff Layton) [714020]
- [scsi] qla2xxx: Update the 4G and 8G firmware to 5.06.03 (Chad Dupuis) [750362]
- [x86] apic: ack all pending irqs when crashed/on kexec (hiro muneda) [742079]
- [net] cxgb3: Fix VLAN over Jumbo frames (Neil Horman) [753053]
- [net] cxgb3: Fix out of bounds index of adapter_info (Neil Horman) [753044]

* Tue Nov 15 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-298.el5]
- [security] keys: Fix NULL deref in user-defined key type (David Howells) [751301] {CVE-2011-4110}
- [fs] dlm: delayed reply message warning (David Teigland) [677413]
- [virt] kvm: fix regression w/ 32 bit KVM clock (Rik van Riel) [731599 751742]
- [net] bonding: update speed/duplex for NETDEV_CHANGE (Weiping Pan) [747547]

* Mon Nov 14 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-297.el5]
- [scsi] megaraid_sas: add workaround for PERC5/1068 kdump panic (Tomas Henzl) [745964]
- [fs] jbd/jbd2: validate sb->s_first in journal_get_superblock (Eryu Guan) [706810]
- [net] tg3: Remove 5719 jumbo frames and TSO blocks (John Feeney) [743117]
- [net] tg3: Break larger frags into 4k chunks for 5719 (John Feeney) [743117]
- [net] tg3: Add tx BD budgeting code (John Feeney) [743117]
- [net] tg3: Consolidate code that calls tg3_tx_set_bd() (John Feeney) [743117]
- [net] tg3: Add partial fragment unmapping code (John Feeney) [743117]
- [net] tg3: Generalize tg3_skb_error_unmap() (John Feeney) [743117]
- [net] tg3: Simplify tx bd assignments (John Feeney) [743117]
- [net] tg3: Reintroduce tg3_tx_ring_info (John Feeney) [743117]
- [net] tg3: Add TSO loopback test (John Feeney) [743117]
- [net] tg3: Cleanup transmit error path (John Feeney) [743117]
- [scsi] lpfc: Update lpfc version for 8.2.0.108.2p driver release (Rob Evers) [747348]
- [scsi] lpfc: Fix kernel build warnings (Rob Evers) [747348]
- [scsi] lpfc: Fix crash when cfg_fcp_eq_count is zero (Rob Evers) [747348]
- [scsi] lpfc: Fix COMMON_GET_CNTL_ATTR mbox cmd failure (Rob Evers) [747348]
- [scsi] lpfc: Fix SLI4 device detecting physical port name (Rob Evers) [747348]
- [scsi] lpfc: Fix reporting of firmware versions that contain an X (Rob Evers) [747348]
- [scsi] lpfc: Fix kernel crash during boot with SLI4 card (Rob Evers) [747348]
- [scsi] lpfc: Fixed RPI leaks in ELS protocol handling (Rob Evers) [747348]
- [scsi] lpfc: Properly clean up EQ and CQ child lists (Rob Evers) [747348]
- [scsi] lpfc: Fixed NPIV FDISC failure on SLI4 if-type 2 ports (Rob Evers) [747348]
- [scsi] lpfc: Fixed failure to do IP reset on SLI4 error (Rob Evers) [747348]
- [scsi] lpfc: Fixed fcp underrun reporting (Rob Evers) [747348]
- [scsi] lpfc: Fix sysfs lists fabric name for disconnected port (Rob Evers) [747348]
- [scsi] lpfc: change SLI_CONFIG mailbox cmd timeout to 300 seconds (Rob Evers) [747348]
- [scsi] lpfc: Fix handling IP reset when PCI read return error (Rob Evers) [747348]
- [scsi] lpfc: Fixed casting problem (Rob Evers) [747348]
- [scsi] lpfc: Fix error code return for management API (Rob Evers) [747348]
- [scsi] lpfc: Fix sli4 mailbox status code (Rob Evers) [747348]
- [scsi] lpfc: Fixed incomplete scsi messages displayed (Rob Evers) [747348]
- [net] igb: Fix for Alt MAC Address feature on 82580 and later (Stefan Assmann) [748792]
- [net] igb: enable link power down (Stefan Assmann) [742514]
- [net] netfilter: Search all chains if drop due to max conntrack (Thomas Graf) [713222]
- [x86] hwmon: enable i5k_amb driver to get memory resource (Dean Nelson) [736032]
- [xen] ia64: fix compile warning added by watchdog timers (Laszlo Ersek) [742880]

* Thu Nov 03 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-296.el5]
- [net] bonding: Have bond_check_dev_link examine netif_running (Ivan Vecera) [736172]
- [net] be2net: enable NETIF_F_LLTX and add own locking of Tx path (Ivan Vecera) [731806]
- [net] be2net: fix multicast filter programming (Ivan Vecera) [731806]
- [net] be2net: fix cmd-rx-filter not notifying MCC (Ivan Vecera) [731806]
- [net] be2net: use RX_FILTER cmd to program multicast addresses (Ivan Vecera) [731806]
- [fs] cifs: fix wrong buffer length returned by SendReceive (Sachin Prabhu) [720363]
- [net] ipv6: allow DAD to be disabled (Jiri Benc) [709271]
- [xen] Watchdog timers for domains (Laszlo Ersek) [742880]

* Tue Nov 01 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-295.el5]
- [net] tg3: put back 5717_PLUS for 5719 and 5720 (John Feeney) [749866]
- [s390] qdio: EQBS retry after CCQ 96 (Hendrik Brueckner) [749058]
- [fs] nfs: re-add call to filemap_fdatawrite (David Jeffery) [748999]
- [x86] Add missing CPU feature flags for AMD Bulldozer (Frank Arnold) [712517]
- [usb] input/wacom: add support for Bamboo MTE-450A (Aristeu Rozanski) [710066]
- [fs] gfs2: Add readahead to sequential directory traversal (Robert S Peterson) [681902]
- [fs] gfs2: Cache dir hash table in a contiguous buffer (Robert S Peterson) [681902]

* Tue Oct 25 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-294.el5]
- [misc] modsign: Clean up canonlist properly during sig verify (Jiri Olsa) [485173]
- [virt] kvm: fix lost tick accounting for 32 bit kvm-clock (Rik van Riel) [731599]
- [fs] epoll: fix integer overflow warning (Jason Baron) [705138]
- [net] bonding: allow all slave speeds (Jiri Pirko) [699661]
- [net] bonding: fix string comparison errors (Andy Gospodarek) [680332]
- [fs] vfs: fix automount should ignore LOOKUP_FOLLOW (Ian Kent) [560103]
- [fs] proc: fix oops on invalid /proc/<pid>/maps access (Johannes Weiner) [747699] {CVE-2011-3637}
- [fs] file: do not kfree vmalloc'd file table arrays (Johannes Weiner) [738238]
- [net] bnx2x: fix bad pointer arithmetic causing memory corruption (Michal Schmidt) [747579]
- [net] bnx2x: restore bnx2x/cnic/bnx2i update (Jarod Wilson) [715383 715388 715604]
- [misc] remove div_long_long_rem (Prarit Bhargava) [732614] {CVE-2011-3209}
- [net] bridge: fix use after free in __br_deliver (Amerigo Wang) [703045] {CVE-2011-2942}

* Thu Oct 20 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-293.el5]
- [redhat] configs: Increase the maximum allowed number of UART's (Mauro Carvalho Chehab) [684874]
- [net] igb: add entropy support option (Stefan Assmann) [605703]
- [net] bnx2x: revert bnx2x/cnic/bnx2i update (Jarod Wilson) [715383 715388 715604]
- [virt] xen/netback: disable features not supported by netfront (Paolo Bonzini) [746225]
- [fs] jbd: Fix forever sleeping process in do_get_write_access (Harshula Jayasuriya) [745345]
- [fs] jbd2: Fix forever sleeping process in do_get_write_access (Harshula Jayasuriya) [745345]
- [s390] crypto: Toleration for ap bus devices with device type 10 (Hendrik Brueckner) [744859]
- [cpufreq] powernow-k8: add missing unregister_cpu_notifier (Prarit Bhargava) [743961]
- [misc] cpu: make set_mtrr disable interrupts before sending IPI (Shyam Iyer) [739631]
- [net] cxgb3: Update to latest upstream for rhel5.8 (Neil Horman) [717807]
- [infiniband] cxgb3: backport upstream fixes for rhel5.8 (Neil Horman) [717433]
- [net] mlx4: remove duplicate rounddown_pow_of_two (Jarod Wilson) [714232]
- [x86] Fix suspend/resume on AMD IOMMUs (Matthew Garrett) [712296]
- [acpi] Backport pm_qos support to rhel5 (Matthew Garrett) [691954]
- [ipc] shm: add RSS and swap size information to /proc/sysvipc/shm (Jerome Marchand) [638652]
- [ipc] shm: fix 32-bit truncation of segment sizes (Jerome Marchand) [638652]
- [usb] host: slow down ehci ITD reuse (Don Zickus) [571737]
- [usb] host: Fix EHCI ISO transfer bug (Don Zickus) [571737]
- [usb] host: fix bug in ehci Iso scheduling (Don Zickus) [571737]
- [usb] host: ehci completes high speed ISO URBs sooner (Don Zickus) [571737]
- [xen] x86: introduce cpuid whitelist (Andrew Jones) [526862 711070]

* Wed Oct 19 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-292.el5]
- [scsi] megaraid: fix FastPath and update to v5.40 (Tomas Henzl) [717698]
- [net] netxen: Add pcie fw load perf drop workaround (Chad Dupuis) [714239]
- [net] netxen: add vlan LRO support (Chad Dupuis) [714239]
- [net] netxen: add fw version compatibility check (Chad Dupuis) [714239]
- [net] netxen: Remove casts of void * (Chad Dupuis) [714239]
- [net] netxen: fix race in skb->len access (Chad Dupuis) [714239]
- [net] netxen: Remove unnecessary semicolons (Chad Dupuis) [714239]
- [net] netxen: suppress false lro warning messages (Chad Dupuis) [714239]
- [net] netxen: Fix common misspellings (Chad Dupuis) [714239]
- [net] netxen: Add support for VLAN RX HW acceleration (Chad Dupuis) [714239]
- [scsi] qla2xxx: Update the 4G and 8G firmware to 5.06.01 (Chad Dupuis) [714236]
- [scsi] qla2xxx: Updated the driver version to 8.03.07.09.05.08-k. (Chad Dupuis) [714206]
- [scsi] qla2xxx: properly set the port number. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Check for marker IOCB during response queue processing. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Retrun sysfs error codes appropriate to conditions (Chad Dupuis) [714206]
- [scsi] qla2xxx: Handle MPI timeout indicated by AE8002 (Chad Dupuis) [714206]
- [scsi] qla2xxx: Use port number to compute nvram/vpd parameter offsets. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Change from irq to irqsave with host_lock (Chad Dupuis) [714206]
- [scsi] qla2xxx: Check for golden firmware and show version if available. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Issue mailbox command only when firmware hung bit is reset for ISP82xx. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Correct inadvertent loop state transitions during port-update handling. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Update to the beacon implementation. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Add support for ISP82xx to capture dump (minidump) on failure. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Check for marker IOCB during response queue processing. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Fix qla24xx revision check while enabling interrupts. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Check to see if a request has completed before calling qla2x00_block_error_handler() in the abort handler. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Acquire hardware lock while manipulating dsd list. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Double check for command completion if abort mailbox command fails. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Fix array out of bound warning. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Prevent CPU lockups when  module param is set. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Provide method for updating I2C attached VPD. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Enable write permission to some debug related module parameters to be changed dynamically. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Implemented beacon on/off for ISP82XX. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Check alterante 'reason' code during GPSC status handling. (Chad Dupuis) [714206]
- [scsi] qla2xxx: During loopdown perform Diagnostic loopback. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Refactor call to qla2xxx_read_sfp for thermal temperature. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Unify the read/write sfp mailbox command routines (Chad Dupuis) [714206]
- [scsi] qla2xxx: Correct read sfp single byte mailbox register. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Clear complete initialization control block. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Allow an override of the registered maximum LUN. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Add host number in reset and quiescent message logs. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Correct buffer start in edc sysfs debug print. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Correction to sysfs edc interface. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Improve logging of exception conditions when creating NPIV ports. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Log if firmware fails to load from flash for ISP82xx. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Add test for valid loop id on fabric relogin. (Chad Dupuis) [714206]
- [scsi] qla2xxx: Don't wait for active mailbox command completion when firmware is hung. (Chad Dupuis) [714206]
- [misc] dcache: exclude new automount functions from kabi (Ian Kent) [560103]
- [fs] autofs4: rename follow_down_one to follow_down for kabi (Ian Kent) [560103]
- [fs] autofs4: rename d_managed to d_mounted to preserve kabi (Ian Kent) [560103]
- [fs] vfs: remove LOOKUP_NO_AUTOMOUNT flag (Ian Kent) [560103]
- [fs] vfs: Fix the remaining automounter semantics regressions (Ian Kent) [560103]
- [fs] vfs: Add LOOKUP_AUTOMOUNT flag for pathname lookup (Ian Kent) [560103]
- [fs] vfs: automount should ignore LOOKUP_FOLLOW (Ian Kent) [560103]
- [fs] vfs: Fix automount for negative autofs dentries (Ian Kent) [560103]
- [fs] vfs: Remove a further kludge from __do_follow_link (Ian Kent) [560103]
- [fs] autofs4: bump version (Ian Kent) [560103]
- [fs] autofs4: reinstate last used update on access (Ian Kent) [560103]
- [fs] autofs4: add v4 pseudo direct mount support (Ian Kent) [560103]
- [fs] autofs4: fix wait validation (Ian Kent) [560103]
- [fs] autofs4: cleanup autofs4_free_ino (Ian Kent) [560103]
- [fs] autofs4: cleanup dentry operations (Ian Kent) [560103]
- [fs] autofs4: cleanup inode operations (Ian Kent) [560103]
- [fs] autofs4: removed unused code (Ian Kent) [560103]
- [fs] autofs4: add d_manage dentry operation (Ian Kent) [560103]
- [fs] autofs4: add d_automount dentry operation (Ian Kent) [560103]
- [fs] vfs: Make follow_down handle d_manage (Ian Kent) [560103]
- [fs] vfs: Make d_mounted a more general field for special functs (Ian Kent) [560103]
- [fs] vfs: Add AT_NO_AUTOMOUNT flag to suppress terminal automount (Ian Kent) [560103]
- [fs] cifs: Use d_automount rather than abusing follow_link (Ian Kent) [560103]
- [fs] nfs: Use d_automount rather than abusing follow_link (Ian Kent) [560103]
- [fs] namei: Add dentry op for automount, don't use follow_link (Ian Kent) [560103]
- [fs] namei: rename struct path to vfs_path (Ian Kent) [560103]
- [fs] autofs4: rename dentry to expiring in _lookup_expiring (Ian Kent) [560103]
- [fs] autofs4: rename dentry to active in autofs4_lookup_active() (Ian Kent) [560103]
- [fs] autofs4: eliminate d_unhashed in path walk checks (Ian Kent) [560103]
- [fs] autofs4: cleanup active and expire lookup (Ian Kent) [560103]
- [fs] autofs4: rename unhashed to active in autofs4_lookup() (Ian Kent) [560103]
- [fs] autofs4: use autofs_info for pending flag (Ian Kent) [560103]
- [fs] autofs4: use helper for need mount check (Ian Kent) [560103]
- [fs] autofs4: use helpers for expiring list (Ian Kent) [560103]
- [fs] autofs4: use helpers for active list handling (Ian Kent) [560103]

* Tue Oct 18 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-291.el5]
- [fs] nfs: don't redirty inodes with no outstanding commits (Jeff Layton) [739665]
- [edac] i7core_edac: Init memory name with cpu, channel, bank (Mauro Carvalho Chehab) [731824]
- [message] mptsas: upgrade version string to 3.04.20rh (Tomas Henzl) [717707]
- [message] mptsas: Fix device offline from aggressive HBA reset (Tomas Henzl) [717707]
- [message] mptsas: Better handling of DEAD IOC PCI-E Link down err (Tomas Henzl) [717707]
- [message] mptsas: Set max_sector count from module parameter (Tomas Henzl) [717707]
- [message] mptsas: check SILI bit in READ_6 CDB for DATA UNDERRUN (Tomas Henzl) [717707]
- [message] mptsas: Fix annoying warning (Tomas Henzl) [717707]
- [message] mptsas: Remove debug print from mptscsih_qcmd() (Tomas Henzl) [717707]
- [message] mptsas: do not check serial_number in the abort handler (Tomas Henzl) [717707]
- [scsi] lpfc: Update version for 8.2.0.108.1p driver release (Rob Evers) [714290]
- [scsi] lpfc: Fix stall when fw reset to port without privs (Rob Evers) [714290]
- [scsi] lpfc: Fix uninit local var portstat_reg compiler warning (Rob Evers) [714290]
- [scsi] lpfc: Fix request fw support for little endian systems (Rob Evers) [714290]
- [scsi] lpfc: Fix default adapter name for the OCe15100 (Rob Evers) [714290]
- [scsi] lpfc: Fix proper error code return value for hba resets (Rob Evers) [714290]
- [scsi] lpfc: Fix cable pull failure on intf type 2 SLI-4 adapters (Rob Evers) [714290]
- [scsi] lpfc: Fix omission of fcf priority failover sysfs entry (Rob Evers) [714290]
- [scsi] lpfc: Fix SLI port recovery error attention with RN set (Rob Evers) [714290]
- [scsi] lpfc: Fix crashes when unsolicted ELS ECHO_CMD received (Rob Evers) [714290]
- [scsi] lpfc: Fix direct connect not coming up for SLI4 FC ports (Rob Evers) [714290]
- [scsi] lpfc: Update version for 8.2.0.108 driver release (Rob Evers) [714290]
- [scsi] lpfc: Fix fw update to match new firmware image format (Rob Evers) [714290]
- [scsi] lpfc: Fix SLI4 CT handling for sequences > 4K (Rob Evers) [714290]
- [scsi] lpfc: Fixed handling of unsolicited frames for vports (Rob Evers) [714290]
- [scsi] lpfc: Fixed crash when aborting els IOs (Rob Evers) [714290]
- [scsi] lpfc: Fixed handling of CVL for vports (Rob Evers) [714290]
- [scsi] lpfc: Fix up CT and oxid/rxid for unsol rcv frames (Rob Evers) [714290]
- [scsi] lpfc: Fix duplicate log numbers caused by merge (Rob Evers) [714290]
- [scsi] lpfc: Fixed compiler warning with file_operations struct (Rob Evers) [714290]
- [scsi] lpfc: Added fcf priority record selection for fcf failover (Rob Evers) [714290]
- [scsi] lpfc: Fix excess memory on stack compiler warning (Rob Evers) [714290]
- [scsi] lpfc: Update version for 8.2.0.107 driver release (Rob Evers) [714290]
- [scsi] lpfc: Fix listhbas stall w/remote initiators in zone (Rob Evers) [714290]
- [scsi] lpfc: Fix not building in debugfs if CONFIG_DEBUG_FS=y (Rob Evers) [714290]
- [scsi] lpfc: Fix FC/FCoE Async Receive CQE not scaling (Rob Evers) [714290]
- [scsi] lpfc: iDiag added SLI4 PCI BAR reigster access methods (Rob Evers) [714290]
- [scsi] lpfc: iDiag cmd structure indexing by using macro defines (Rob Evers) [714290]
- [scsi] lpfc: iDiag multi-buffer mbox command capture and dump ext (Rob Evers) [714290]
- [scsi] lpfc: SLI4 loopback test and link diagnostic support (Rob Evers) [714290]
- [scsi] lpfc: FLOGI payload has Multiple IDs on enable_npiv clear (Rob Evers) [714290]
- [scsi] lpfc: log when writeable parameters are changed (Rob Evers) [714290]
- [scsi] lpfc: Fix ASIC SYSFS failed multi-buffer fw download (Rob Evers) [714290]
- [scsi] lpfc: Fix mbox cmd release memory leak (Rob Evers) [714290]
- [scsi] lpfc: merge debugfs ASIC extents info into iDiag framework (Rob Evers) [714290]
- [scsi] lpfc: wait for port status reg for ready after fw reset (Rob Evers) [714290]
- [scsi] lpfc: Consolidated duplicating macro definitions (Rob Evers) [714290]
- [scsi] lpfc: Remove sharp define from codebase (Rob Evers) [714290]
- [scsi] lpfc: Implement debugfs support for resource extents (Rob Evers) [714290]
- [scsi] lpfc: iDiag r/w bitset/clear access to new ASIC ctl regs (Rob Evers) [714290]
- [scsi] lpfc: Fix mbox command failure with multiple large buffers (Rob Evers) [714290]
- [scsi] lpfc: iDiag endian explicit dumping (Rob Evers) [714290]
- [scsi] lpfc: iDiag debugfs method for dumping mbox from SLI4 (Rob Evers) [714290]
- [scsi] lpfc: request PCI reset to support EEH recover on P7 (Rob Evers) [714290]
- [scsi] lpfc: iDiag debugfs inline mbox cmd capture and dump (Rob Evers) [714290]
- [scsi] lpfc: Fix enabling of PCIe AER (Rob Evers) [714290]
- [scsi] lpfc: Fix EEH recovery to save state after SLI4 PCI reset (Rob Evers) [714290]
- [scsi] lpfc: INIT_LIST_HEAD to lpfc_mgmt_issue_sli_cfg_ext_mbox (Rob Evers) [714290]
- [scsi] lpfc: new ASIC mgmt pass-through mbox multi-buffer ext (Rob Evers) [714290]
- [scsi] lpfc: Fix FC Port swap on SLI3 adapters (Rob Evers) [714290]
- [scsi] lpfc: Fix Virtual link loss during failover test (Rob Evers) [714290]
- [scsi] lpfc: Fix vpi initialization in lpfc_init_vfi (Rob Evers) [714290]
- [scsi] lpfc: show 16 Gbit in FC host supported_speeds sysfs entry (Rob Evers) [714290]
- [scsi] lpfc: support reseting firmware and device from sysfs entry (Rob Evers) [714290]
- [scsi] lpfc: support firmware dump obj file to flash filesystem (Rob Evers) [714290]
- [scsi] lpfc: Add firmware upgrade code to driver (Rob Evers) [714290]
- [scsi] lpfc: add delay following IF_TYPE_2 function reset (Rob Evers) [714290]
- [scsi] lpfc: Fragment ELS & SCSI SGE lists via Extent regions (Rob Evers) [714290]
- [scsi] lpfc: Fixed potential missed SLI4 init failure conditions (Rob Evers) [714290]
- [scsi] lpfc: Add model names for new hardware (Rob Evers) [714290]
- [scsi] lpfc: Set max SGE size to 0x80000000 where possible (Rob Evers) [714290]
- [scsi] lpfc: Fix discovery failure in private loop (Rob Evers) [714290]
- [scsi] lpfc: Fix SLI3 and non-NPIV crashes with new extent code (Rob Evers) [714290]
- [scsi] lpfc: Refactor lpfc_sli4_alloc_extent some more (Rob Evers) [714290]
- [scsi] lpfc: Restore mbox can fail as nonerror functionality (Rob Evers) [714290]
- [scsi] lpfc: Fix build warnings in 8.2.0.102 (Rob Evers) [714290]
- [scsi] lpfc: Use HDRR bit to determine if RPI headers are needed (Rob Evers) [714290]
- [scsi] lpfc: Don't post RPI Headers if port supports extents (Rob Evers) [714290]
- [scsi] lpfc: ASIC mgmt multi-buffer mbox passthrough support (Rob Evers) [714290]
- [scsi] lpfc: Update version for 8.2.0.102 driver release (Rob Evers) [714290]
- [scsi] lpfc: Add MAILBOX_MGMT_MAX define (Rob Evers) [714290]
- [scsi] lpfc: Refactor code in lpfc_sli4_alloc_extent (Rob Evers) [714290]
- [scsi] lpfc: start new ASIC device management support work (Rob Evers) [714290]
- [scsi] lpfc: Fix port capabilities and get parameters mbox calls (Rob Evers) [714290]
- [scsi] lpfc: Fix SLI2 crashes with new extent code (Rob Evers) [714290]
- [scsi] lpfc: Fix mbox processing to not overwrite status codes (Rob Evers) [714290]
- [scsi] lpfc: enumerate members starting from none zero value (Rob Evers) [714290]
- [scsi] lpfc: Remove workaround for extents endian issue (Rob Evers) [714290]
- [scsi] lpfc: Call correct mbox cleanup routine after extent alloc (Rob Evers) [714290]
- [scsi] lpfc: extent block list cleanup and free memory resources (Rob Evers) [714290]
- [scsi] lpfc: Fix memory leak in extent block lists (Rob Evers) [714290]
- [scsi] lpfc: Modified variables for XRIs to be unsigned variable (Rob Evers) [714290]
- [scsi] lpfc: support for nonembedded Extent mailbox IOCTLs (Rob Evers) [714290]
- [scsi] lpfc: Fixed compilation error/warning in sli code (Rob Evers) [714290]
- [scsi] lpfc: Rework SLI4 Extents code (Rob Evers) [714290]
- [scsi] lpfc: Update version for 8.2.0.101 driver release (Rob Evers) [714290]
- [scsi] lpfc: Fixed mask size for the wq_id mask (Rob Evers) [714290]
- [scsi] lpfc: Fix Port Error detected during POST (Rob Evers) [714290]
- [scsi] lpfc: Apply dropped patch from initial new ASIC bring up (Rob Evers) [714290]
- [scsi] lpfc: Rework SLI4 Extents code (Rob Evers) [714290]
- [scsi] lpfc: Reorganize CQ and EQ usage to comply with SLI4 Specs (Rob Evers) [714290]
- [scsi] lpfc: Fix KERN levels on log messages 3008, 2903, 0383 (Rob Evers) [714290]
- [scsi] lpfc: Initial checkin of SLI4 Extents code (Rob Evers) [714290]
- [scsi] lpfc: Fix ASIC mbox queue id collision with work queue id (Rob Evers) [714290]
- [scsi] lpfc: work on systems with Page Size Larger than 4k (Rob Evers) [714290]
- [scsi] lpfc: set constant sysfs passthrough mbox cmd maximum size (Rob Evers) [714290]
- [scsi] lpfc: Fix FCFI incorrect on received unsolicited frames (Rob Evers) [714290]
- [scsi] lpfc: Update version for 8.2.0.100 driver release (Rob Evers) [714290]
- [scsi] lpfc: Add LOG_ELS message to NPIV LOGO (Rob Evers) [714290]
- [scsi] lpfc: move multi-buffer macros into shared IOCTL header (Rob Evers) [714290]
- [scsi] lpfc: Update version for 8.2.0.99 driver release (Rob Evers) [714290]
- [scsi] lpfc: Fix build warning in debugfs code (Rob Evers) [714290]
- [scsi] lpfc: iDiag debugfs SLI4 doorbell reigster access methods (Rob Evers) [714290]
- [scsi] lpfc: Fix RQ_CREATE version 1 fails (Rob Evers) [714290]
- [scsi] lpfc: Add Temporary RPI field to the ELS request WQE (Rob Evers) [714290]
- [scsi] lpfc: Allow SLI4 with FCOE_MODE not set on new FC adapters (Rob Evers) [714290]
- [scsi] lpfc: only look at BAR2 or BAR4 only for if_type 0 (Rob Evers) [714290]
- [scsi] lpfc: iDiag debugfs SLI4 display index info in decimal (Rob Evers) [714290]
- [scsi] lpfc: iDiag debugfs SLI4 device queue entry access methods (Rob Evers) [714290]
- [scsi] lpfc: Update copyright date for all changed files (Rob Evers) [714290]
- [scsi] lpfc: Update version for 8.2.0.98 driver release (Rob Evers) [714290]
- [scsi] lpfc: Fixed the compiler warning in current code (Rob Evers) [714290]
- [scsi] lpfc: handle PCI Link drop detection failure (Rob Evers) [714290]
- [scsi] lpfc: Add selective reset jump table entry (Rob Evers) [714290]
- [scsi] lpfc: Update version for 8.2.0.97 driver release (Rob Evers) [714290]
- [scsi] lpfc: lower stack use in lpfc_fc_frame_check (Rob Evers) [714290]
- [scsi] lpfc: fix comment typo diable -> disable (Rob Evers) [714290]
- [scsi] lpfc: fix comment/printk typos (Rob Evers) [714290]
- [scsi] lpfc: Add new Queue create Mailbox versions for new ASIC (Rob Evers) [714290]
- [scsi] lpfc: Place LPFC driver module parameters in sysfs (Rob Evers) [714290]
- [scsi] lpfc: Fix compile warning for iDiag (Rob Evers) [714290]
- [scsi] lpfc: Performance Hints support (Rob Evers) [714290]
- [scsi] lpfc: Add new driver interfaces for encryption products (Rob Evers) [714290]
- [scsi] lpfc: iDiag driver support debugfs queue information get (Rob Evers) [714290]
- [scsi] lpfc: iDiag debugfs PCI cfg reg bits set/clear methods (Rob Evers) [714290]
- [scsi] lpfc: iDiag debugfs framework and r/w PCI cfg space regs (Rob Evers) [714290]
- [block] cciss: bump driver version (Tomas Henzl) [714129]
- [block] cciss: need to delay after a PCI Power Management reset (Tomas Henzl) [714129]
- [block] cciss: auto engage scsi susbsystem (Tomas Henzl) [714129]
- [block] cciss: store pdev in hba struct (Tomas Henzl) [714129]
- [block] cciss: use consistent variable names (Tomas Henzl) [714129]
- [block] cciss: add a commandline switch for simple mode (Tomas Henzl) [714129]
- [fs] proc: close race with exec in mem_read() (Johannes Weiner) [692042] {CVE-2011-1020}
- [mm] implement access_remote_vm (Johannes Weiner) [692042] {CVE-2011-1020}
- [mm] factor out main logic of access_process_vm (Johannes Weiner) [692042] {CVE-2011-1020}
- [mm] use mm_struct to resolve gate vma's in __get_user_pages (Johannes Weiner) [692042] {CVE-2011-1020}
- [mm] make in_gate_area take mm_struct instead of a task_struct (Johannes Weiner) [692042] {CVE-2011-1020}
- [mm] make get_gate_vma take mm_struct instead of task_struct (Johannes Weiner) [692042] {CVE-2011-1020}
- [x86_64] mark assoc mm when running task in 32 bit compat mode (Johannes Weiner) [692042] {CVE-2011-1020}
- [misc] sched: add ctx tag to mm running task in ia32 compat mode (Johannes Weiner) [692042] {CVE-2011-1020}
- [fs] proc: require the target to be tracable (or yourself) (Johannes Weiner) [692042] {CVE-2011-1020}
- [fs] proc: close race in /proc/*/environ (Johannes Weiner) [692042] {CVE-2011-1020}
- [fs] proc: report errors in /proc/*/*map* sanely (Johannes Weiner) [692042] {CVE-2011-1020}
- [fs] proc: shift down_read(mmap_sem) to the caller (Johannes Weiner) [692042] {CVE-2011-1020}
- [fs] detect exec transition phase with new mm but old creds (Johannes Weiner) [692042] {CVE-2011-1020}
- [net] tg3: call netif_carrier_off to initialize operstate value (John Feeney) [635982]
- [net] tg3: Update to plus (John Feeney) [715409]
- [net] tg3: Update to 3.119 (John Feeney) [715409]
- [net] tg3: Update to 3.118 (John Feeney) [683393 699545]
- [net] tg3: Update to 3.117 (John Feeney) [715409]
- [xen] make test_assign_device domctl dependent on intremap hw (Laszlo Ersek) [740203]
- [xen] Propagate target dom within XEN_DOMCTL_test_assign_device (Laszlo Ersek) [740203]

* Fri Oct 14 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-290.el5]
- [net] e1000: don't enable dma rx until after dma address setup (Dean Nelson) [714318]
- [net] e1000: save skb counts in TX to avoid cache misses (Dean Nelson) [714318 742124]
- [net] e1000: Fix driver to be used on PA RISC C8000 workstations (Dean Nelson) [714318]
- [net] e1000: repair missing flush operations (Dean Nelson) [714318]
- [net] e1000: always do e1000_check_for_link on e1000_ce4100 MACs (Dean Nelson) [714318]
- [scsi] be2iscsi: Add pci_disable device (Mike Christie) [714292]
- [scsi] be2iscsi: Adding a shutdown Routine (Mike Christie) [713816 714292]
- [scsi] be2iscsi: Fix /proc/interrupts problem (Mike Christie) [714292]
- [scsi] be2iscsi: remove host and session casts (Mike Christie) [714292]
- [scsi] be2iscsi: Use struct scsi_lun in iscsi structs (Mike Christie) [714292]
- [scsi] be2iscsi: fix chip cleanup (Mike Christie) [714292]
- [scsi] be2iscsi: fix boot hang due to interrupts not rearmed (Mike Christie) [714292]
- [scsi] be2iscsi: Fix for proper setting of FW (Mike Christie) [714292]
- [scsi] be2iscsi: Set a timeout to FW (Mike Christie) [714292]
- [scsi] be2iscsi: remove extra semicolons (Mike Christie) [714292]
- [scsi] be2iscsi: Fix common misspellings (Mike Christie) [714292]
- [scsi] be2iscsi: tmp revert Fix MSIX interrupt names fix (Mike Christie) [714292]
- [infiniband] cxgb4: Fail RDMA initialization on unsupported cards (Steve Best) [713943]
- [infiniband] cxgb4: Couple of abort fixes (Steve Best) [713943]
- [infiniband] cxgb4: Don't truncate MR lengths (Steve Best) [713943]
- [infiniband] cxgb4: Don't exceed hw IQ depth limit for user CQs (Steve Best) [713943]
- [hwmon] lm78: Make ISA interface depend on CONFIG_ISA (Dean Nelson) [713815]
- [hwmon] lm78: Avoid forward declarations (Dean Nelson) [713815]
- [hwmon] lm78: Stop abusing struct i2c_client for ISA devices (Dean Nelson) [713815]
- [hwmon] lm78: Detect alias chips (Dean Nelson) [713815]
- [hwmon] don't build drivers for ppc that touch ISA addresses (Dean Nelson) [713815]
- [char] CONFIG_TELCLOCK depends on X86 (Dean Nelson) [713815]
- [misc] add oprofile support for Sandy Bridge (John Villalovos) [713666]
- [net] ixgbe: update to upstream version 3.4.8-k (Andy Gospodarek) [713110 714013 714314]
- [net] e1000e: fix WoL on 82578DM and 82567V3 (Andy Gospodarek) [712773]
- [fs] gfs2: Call gfs2_meta_wipe for directory hash blocks (Abhijith Das) [706616]
- [net] bonding: resolve failover problems related to jiffy wrap (Andy Gospodarek) [693258]
- [fs] nfs: Don't call iput holding nfs_access_cache_shrinker lock (Steve Dickson) [585935]
- [block] improve detail in I/O error messages (Mike Snitzer) [516170]
- [md] dm-mpath: propagate target errors immediately (Mike Snitzer) [516170]
- [scsi] Correctly handle thin provisioning write error (Mike Snitzer) [516170]
- [md] dm-mpath: sync pushback code with upstream (Mike Snitzer) [516170]
- [scsi] Add detailed SCSI I/O errors (Mike Snitzer) [516170]
- [scsi] Fix sense key MEDIUM ERROR processing and retry (Mike Snitzer) [516170]
- [scsi] fix error propagation (Mike Snitzer) [516170]
- [scsi] fix recovered error handling (Mike Snitzer) [516170]
- [scsi] simplify scsi_io_completion() (Mike Snitzer) [516170]
- [scsi] fix barrier failure and error propagation issues (Mike Snitzer) [516170]

* Wed Oct 12 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-289.el5]
- [scsi] libsas: amend device gone notification in sas_deform_port (David Milburn) [742356]
- [scsi] libsas: fix up device gone notification in sas_deform_port (David Milburn) [742356]
- [scsi] libsas: fix loopback topology bug during discovery (David Milburn) [742356]
- [scsi] libsas: fix SATA NCQ error (David Milburn) [742356]
- [scsi] libsas: fix ATAPI check condition termination (David Milburn) [742356]
- [net] fix low throughput when using vlan over bonding (Flavio Leitner) [742318]
- [net] core/netpoll: clean skb->next before pushing it down (Flavio Leitner) [741374]
- [net] sfc: Use MCDI RX_BAD_FCS_PKTS count as MAC rx_bad count (Michal Schmidt) [739077]
- [md] raid5: fix raid6 resync corruption bug (Doug Ledford) [738984]
- [scsi] scsi_lib: pause between error retries (Rob Evers) [736809]
- [md] return an error code when we don't fail a drive (Doug Ledford) [736697]
- [fs] nfs: update nfs4_fattr_bitmap_maxsz (Steve Dickson) [735477]
- [net] ipv6: fix refcnt problem related to POSTDAD state (Weiping Pan) [723411]
- [net] bnx2x: update FW to 7.0.23 (Michal Schmidt) [715383 715388 715604]
- [scsi] bnx2i: driver update for 5.8 (Michal Schmidt) [715383 715388 715604]
- [net] cnic: driver update for 5.8, part 2 (Michal Schmidt) [715383 715388 715604]
- [net] bnx2x: fix undesired VLAN stripping (Michal Schmidt) [715383 715388 715604]
- [net] bnx2x: driver update for 5.8, part 3 (Michal Schmidt) [715383 715388 715604]
- [net] bnx2x: 57712 parity handling (Michal Schmidt) [715383 715388 715604]
- [net] bnx2x, cnic, bnx2i: New 7.0 Firmware (Michal Schmidt) [715383 715388 715604]
- [net] bnx2x: driver update for 5.8, part 2 (Michal Schmidt) [715383 715388 715604]
- [net] cnic: driver update for 5.8, part 1 (Michal Schmidt) [715383 715388 715604]
- [net] bnx2x, cnic: Disable iSCSI if DCBX negotiation succeeds (Michal Schmidt) [715383 715388 715604]
- [net] bnx2x: driver update for 5.8, part 1 (Michal Schmidt) [715383 715388 715604]
- [net] bnx2x: temporarily revert BCM57710 bringup fix (Michal Schmidt) [715383 715388 715604]
- [misc] ethtool: Add 20G bit definitions (Michal Schmidt) [715383 715388 715604]
- [net] e1000: Add necessary <linux/prefetch.h> include (Dean Nelson) [714318]
- [net] ixgbevf: update to upstream version 2.1.0-k (Andy Gospodarek) [714317]
- [net] e1000e: update to upstream version 1.4.4 (Andy Gospodarek) [714315]
- [net] bna: Multiple Definition and Interface Setup Fix (Ivan Vecera) [714019]
- [net] bna: Driver Version changed to 3.0.2.2 (Ivan Vecera) [714019]
- [net] bna: Add Callback to Fix RXQ Stop (Ivan Vecera) [714019]
- [net] bna: PLL Init Fix and Add Stats Attributes (Ivan Vecera) [714019]
- [net] bna: Brocade 1860 HW Enablement (Ivan Vecera) [714019]
- [net] bna: new firmware for new hardware (Ivan Vecera) [714019]
- [net] bna: Implement FW Download for New HW (Ivan Vecera) [714019]
- [net] bna: Capability Map and MFG Block Changes for New HW (Ivan Vecera) [714019]
- [net] bna: Brocade 1860 IOC PLL, Reg Defs and ASIC Mode Changes (Ivan Vecera) [714019]
- [net] bna: PCI Probe Conf Lock Fix (Ivan Vecera) [714019]
- [net] bna: Semaphore Lock Fix (Ivan Vecera) [714019]
- [net] bna: Set Ring Param Fix (Ivan Vecera) [714019]
- [net] bna: Eliminate Small Race Condition Window in RX Path (Ivan Vecera) [714019]
- [net] bna: make function tables cont (Ivan Vecera) [714019]
- [net] bna: Driver Version changed to 3.0.2.1 (Ivan Vecera) [714019]
- [net] bna: MBOX IRQ Flag Check after Locking (Ivan Vecera) [714019]
- [net] bna: Initialization and Locking Fix (Ivan Vecera) [714019]
- [net] bna: Ethtool Enhancements and Fix (Ivan Vecera) [714019]
- [net] bna: Async Mode Tx Rx Init Fix (Ivan Vecera) [714019]
- [net] bna: Formatting and Code Cleanup (Ivan Vecera) [714019]
- [net] bna: TX Path and RX Path Changes (Ivan Vecera) [714019]
- [net] bna: Interrupt Polling and NAPI Init Changes (Ivan Vecera) [714019]
- [net] bna: PCI Probe Fix (Ivan Vecera) [714019]
- [net] bna: Naming Change and Minor Macro Fix (Ivan Vecera) [714019]
- [net] bna: off by one in bfa_msgq_rspq_pi_update() (Ivan Vecera) [714019]
- [net] bna: unlock on error path in pnad_pci_probe() (Ivan Vecera) [714019]
- [net] bna: Driver Version changed to 3.0.2.0 (Ivan Vecera) [714019]
- [net] bna: Remove Obsolete Files (Ivan Vecera) [714019]
- [net] bna: Remove Unused Code (Ivan Vecera) [714019]
- [net] bna: firmware update for new (v3) bna driver (Ivan Vecera) [714019]
- [net] bna: ENET and Tx Rx Redesign Enablement (Ivan Vecera) [714019]
- [net] bna: Add New HW Defs (Ivan Vecera) [714019]
- [net] bna: Tx and Rx Redesign (Ivan Vecera) [714019]
- [net] bna: Introduce ENET as New Driver and FW Interface (Ivan Vecera) [714019]
- [net] bna: MSGQ Implementation (Ivan Vecera) [714019]
- [net] bna: Remove Obsolete File bfi_ctreg.h (Ivan Vecera) [714019]
- [net] bna: Consolidated HW Registers for Supported HWs (Ivan Vecera) [714019]
- [net] bna: Remove get_regs Ethtool Support (Ivan Vecera) [714019]
- [net] bna: HW Interface Init Update (Ivan Vecera) [714019]
- [net] bna: Remove Unnecessary CNA Check (Ivan Vecera) [714019]
- [net] bna: Header File Consolidation (Ivan Vecera) [714019]
- [net] bna: HW Error Counter Fix (Ivan Vecera) [714019]
- [net] bna: Add HW Semaphore Unlock Logic (Ivan Vecera) [714019]
- [net] bna: IOC Event Name Change (Ivan Vecera) [714019]
- [net] bna: Mboxq Flush When IOC Disabled (Ivan Vecera) [714019]
- [net] bna: Minor IRQ Index and Definition Change (Ivan Vecera) [714019]
- [net] bna: State Machine Fault Handling Cleanup (Ivan Vecera) [714019]
- [net] bna: IOC Event Notification Enhancement (Ivan Vecera) [714019]
- [net] bna: CheckPatch Cleanup (Ivan Vecera) [714019]
- [net] bna: Print Driver Version (Ivan Vecera) [714019]
- [net] bna: Separate irq type flags from request_irq variable (Ivan Vecera) [714019]
- [net] bna: use netdev_alloc_skb_ip_align() (Ivan Vecera) [714019]
- [net] bna: Fix bad kzalloc call with interrupts disabled (Ivan Vecera) [714019]
- [net] bna: Remove casts of void * (Ivan Vecera) [714019]
- [net] bna: fix warning bfa_ioc_smem_pgoff defined but not used (Ivan Vecera) [714019]
- [net] bna: Fix set-but-unused variables (Ivan Vecera) [714019]
- [net] bna: convert to hw_features (Ivan Vecera) [714019]
- [scsi] bfa: update firmware to version 3.0.2.2 (Rob Evers) [714017]
- [scsi] bfa: Update the driver version to 3.0.2.2 (Rob Evers) [714017]
- [scsi] bfa: Add support to store driver configuration in flash (Rob Evers) [714017]
- [scsi] bfa: Added support to configure QOS and collect stats (Rob Evers) [714017]
- [scsi] bfa: Added support to collect and reset fcport stats (Rob Evers) [714017]
- [scsi] bfa: Add support for IO profiling (Rob Evers) [714017]
- [scsi] bfa: Check supported speed based on port mode (Rob Evers) [714017]
- [scsi] bfa: Update RME interrupt handling (Rob Evers) [714017]
- [scsi] bfa: Add FC-transport Async Event Notification support (Rob Evers) [714017]
- [scsi] bfa: Update the driver version to 3.0.2.1 (Rob Evers) [714017]
- [scsi] bfa: Driver enhancements (Rob Evers) [714017]
- [scsi] bfa: Added support to query PHY (Rob Evers) [714017]
- [scsi] bfa: Added HBA diagnostics support (Rob Evers) [714017]
- [scsi] bfa: Added support for flash configuration (Rob Evers) [714017]
- [scsi] bfa: Added support to obtain SFP info (Rob Evers) [714017]
- [scsi] bfa: Added support for CEE info and stats query (Rob Evers) [714017]
- [scsi] bfa: Add IOCFC enable cbfn and stats changes (Rob Evers) [714017]
- [scsi] bfa: FCS bug fixes (Rob Evers) [714017]
- [scsi] bfa: DMA memory allocation enhancement (Rob Evers) [714017]
- [scsi] bfa: Brocade-1860 Fabric Adapter vHBA support (Rob Evers) [714017]
- [scsi] bfa: Brocade-1860 Fabric Adapter PLL init fixes (Rob Evers) [714017]
- [scsi] bfa: Added Fabric Assigned Address(FAA) support (Rob Evers) [714017]
- [scsi] bfa: IOC bug fixes (Rob Evers) [714017]
- [scsi] bfa: Enable ASIC block configuration and query (Rob Evers) [714017]
- [scsi] bfa: Update the driver version to 3.0.2.0 (Rob Evers) [714017]
- [scsi] bfa: Driver initialization and model description fix (Rob Evers) [714017]
- [scsi] bfa: Enhancement for fcpim and IO tag handling (Rob Evers) [714017]
- [scsi] bfa: FC credit recovery and misc bug fixes (Rob Evers) [714017]
- [scsi] bfa: 1860 Adapter 16Gbs support and flash controller fixes (Rob Evers) [714017]
- [scsi] bfa: IOC and PLL init changes for Brocade-1860 Adapter (Rob Evers) [714017]
- [scsi] bfa: support vport disable and enable operations (Rob Evers) [714017]
- [scsi] bfa: Brocade-1860 Fabric Adapter Hardware Enablement (Rob Evers) [714017]
- [scsi] bfa: Add pbc port disable check and fix LPS message name (Rob Evers) [714017]
- [scsi] bfa: Introduce IOC event notification mechanism (Rob Evers) [714017]
- [scsi] bfa: add generic address len pair for DMA memory chunk (Rob Evers) [714017]
- [scsi] bfa: Move debugfs initialization before bfa init (Rob Evers) [714017]
- [net] cxgb4: driver update for RHEL5.8 (Neil Horman) [713905]
- [net] enic: update driver to version 2.1.1.24 (Stefan Assmann) [713536]
- [edac] i7300_edac: Fix error cleanup logic (Mauro Carvalho Chehab) [712948]
- [usb] input/hid: backport hidraw support (Aristeu Rozanski) [705453]
- [fs] eventpoll: fix epoll_wait overly constraining wait times (Jason Baron) [705138]
- [md] update superblocks properly when adding a spare (Doug Ledford) [668529]
- [scsi] Fix out of spec CD-ROM problem with media change (Don Zickus) [664653]
- [net] sctp: encode PROTOCOL VIOLATION error cause correctly (Thomas Graf) [636828]
- [xen] vmx: Print advanced features during boot (Paolo Bonzini) [712440]

* Mon Oct 10 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-288.el5]
- [scsi] mpt2sas: Bump version 09.100.00.00 (Tomas Henzl) [717581]
- [scsi] mpt2sas: add missing mpt2sas_base_detach to scsih_remove (Tomas Henzl) [717581]
- [scsi] mpt2sas: fix WarpDrive Infinite command retries on bad cmd (Tomas Henzl) [717581]
- [scsi] mpt2sas: Adding support for customer specific branding (Tomas Henzl) [717581]
- [scsi] mpt2sas: set DID_NO_CONNECT on remove and avoid shutdown (Tomas Henzl) [717581]
- [scsi] mpt2sas: fix broadcast AEN and task management issue (Tomas Henzl) [717581]
- [scsi] mpt2sas: Set max_sector count from module parameter (Tomas Henzl) [717581]
- [scsi] mpt2sas: MPI next revision header update (Tomas Henzl) [717581]
- [scsi] mpt2sas: Fixed Big Endian Issues on 32 bit PPC (Tomas Henzl) [717581]
- [scsi] mpt2sas: do not check serial_number in the abort handler (Tomas Henzl) [717581]
- [scsi] mpt2sas: remove flush_scheduled_work usages (Tomas Henzl) [717581]
- [net] ipv6: Do not assign non-valid address on interface (Jiri Benc) [741511]
- [fs] cifs: always do is_path_accessible check in cifs_mount (Jeff Layton) [738300] {CVE-2011-3363}
- [fs] cifs: add fallback in is_path_accessible for old servers (Jeff Layton) [738300] {CVE-2011-3363}
- [md] raid1: don't retry recovery when the last drive fails (Doug Ledford) [736693]
- [input] evdev: disable interrupts when processing events (Don Zickus) [734900]
- [char] tpm: Zero buffer after copying to userspace (Jiri Benc) [732631] {CVE-2011-1162}
- [md] bitmap: fix BUG triggered due to slow devices (Doug Ledford) [725358]
- [char] sysrq: Fix panic executing 'echo f > /proc/sysrq-trigger' (Larry Woodman) [718645]
- [scsi] isci: fix 32-bit operation when CONFIG_HIGHMEM64G=n (David Milburn) [713904]
- [scsi] isci: Remove reserved device IDS from isci_id_table (David Milburn) [718341]
- [scsi] isci: fix checkpatch errors (David Milburn) [718341]
- [scsi] isci: Device reset should request sas_phy_reset(phy, true) (David Milburn) [718341]
- [scsi] isci: pare back error messsages (David Milburn) [718341]
- [scsi] isci: cleanup silicon revision detection (David Milburn) [718341]
- [scsi] isci: refactor scu_unsolicited_frame.h (David Milburn) [718341]
- [scsi] isci: merge sata.[ch] into request.c (David Milburn) [718341]
- [scsi] isci: kill 'get/set' macros (David Milburn) [718341]
- [scsi] isci: retire scic_sds_ and scic_ prefixes (David Milburn) [718341]
- [scsi] isci: unify isci_host and scic_sds_controller (David Milburn) [718341]
- [scsi] isci: unify isci_remote_device and scic_sds_remote_device (David Milburn) [718341]
- [scsi] isci: unify isci_port and scic_sds_port (David Milburn) [718341]
- [scsi] isci: fix scic_sds_remote_device_terminate_requests (David Milburn) [718341]
- [scsi] isci: unify isci_phy and scic_sds_phy (David Milburn) [718341]
- [scsi] isci: unify isci_request and scic_sds_request (David Milburn) [718341]
- [scsi] isci: rename / clean up scic_sds_stp_request (David Milburn) [718341]
- [scsi] isci: preallocate requests (David Milburn) [718341]
- [scsi] isci: combine request flags (David Milburn) [718341]
- [scsi] isci: unify can_queue tracking on the tci_pool (David Milburn) [718341]
- [scsi] isci: Terminate dev requests on FIS err bit rx in NCQ (David Milburn) [718341]
- [scsi] isci: fix frame received locking (David Milburn) [718341]
- [scsi] isci: fix buffer overflow in isci_parse_oem_parameters (David Milburn) [718341]
- [scsi] isci: fix isci_task_execute_tmf completion (David Milburn) [718341]
- [scsi] isci: fix support for arbitrarily large smp requests (David Milburn) [718341]
- [scsi] isci: fix dma_unmap_sg usage (David Milburn) [718341]
- [scsi] isci: fix smp response frame overrun (David Milburn) [718341]
- [scsi] isci: kill device_sequence (David Milburn) [718341]
- [scsi] isci: kill isci_remote_device_change_state() (David Milburn) [718341]
- [scsi] isci: atomic device lookup and reference counting (David Milburn) [718341]
- [scsi] isci: fix ssp response iu buffer size in isci_tmf (David Milburn) [718341]
- [scsi] isci: cleanup request allocation (David Milburn) [718341]
- [scsi] isci: cleanup/optimize queue increment macros (David Milburn) [718341]
- [scsi] isci: cleanup tag macros (David Milburn) [718341]
- [scsi] isci: cleanup/optimize pool implementation (David Milburn) [718341]
- [scsi] isci: Disable link layer hang detection (David Milburn) [718341]
- [scsi] isci: Hard reset failure link resets all phys in the port (David Milburn) [718341]
- [scsi] isci: decode remote node ready and suspended states (David Milburn) [718341]
- [scsi] isci: fix isci_terminate_pending() list management (David Milburn) [718341]
- [scsi] isci: Handle timed-out request terminations correctly (David Milburn) [718341]
- [scsi] isci: Requests that do not start must be set to complete (David Milburn) [718341]
- [scsi] isci: Add decode for SMP request retry error condition (David Milburn) [718341]
- [scsi] isci: filter broadcast change notifications on phy resets (David Milburn) [718341]
- [scsi] isci: Move reset delay after remote node resumption (David Milburn) [718341]
- [scsi] isci: remove 'min memory' infrastructure (David Milburn) [718341]
- [scsi] isci: Added support for C0 to SCU Driver (David Milburn) [718341]
- [scsi] isci: additional state machine cleanup (David Milburn) [718341]
- [scsi] isci: state machine cleanup (David Milburn) [718341]
- [scsi] isci: Removing unused variables compiler warnings (David Milburn) [718341]
- [scsi] isci: removing the kmalloc in smp request construct (David Milburn) [718341]
- [scsi] isci: remove isci_timer interface (David Milburn) [718341]
- [scsi] isci: Remove tmf timeout_timer (David Milburn) [718341]
- [scsi] isci: convert phy_startup_timer to sci_timer (David Milburn) [718341]
- [scsi] isci: convert scic_timeout_timer to sci_timer (David Milburn) [718341]
- [scsi] isci: convert power control timer to sci_timer (David Milburn) [718341]
- [scsi] isci: convert phy sata_timeout_timer to sci_timer (David Milburn) [718341]
- [scsi] isci: convert port config agent timer to sci_timer (David Milburn) [718341]
- [scsi] isci: replace isci_timer list with proper embedded timers (David Milburn) [718341]
- [scsi] isci: add some type safety to the state machine interface (David Milburn) [718341]
- [scsi] isci: unify rnc start{io|task} handlers (David Milburn) [718341]
- [scsi] isci: unify rnc destruct handlers (David Milburn) [718341]
- [scsi] isci: unify rnc destruct handlers (David Milburn) [718341]
- [scsi] isci: unify rnc event handlers (David Milburn) [718341]
- [scsi] isci: unify port start_io and complete_io handlers (David Milburn) [718341]
- [scsi] isci: unify port link_up and link_down handlers (David Milburn) [718341]
- [scsi] isci: remove port frame and event handlers (David Milburn) [718341]
- [scsi] isci: unify port reset, add_phy, and remove_phy handlers (David Milburn) [718341]
- [scsi] isci: remove port destruct handler (David Milburn) [718341]
- [scsi] isci: unify port stop handlers (David Milburn) [718341]
- [scsi] isci: remove port start handler (David Milburn) [718341]
- [scsi] isci: merge port ready substates into main state machine (David Milburn) [718341]
- [scsi] isci: c99 port state handlers (David Milburn) [718341]
- [scsi] isci: clarify phy to port lookups (David Milburn) [718341]
- [scsi] isci: unify phy consume_power handlers (David Milburn) [718341]
- [scsi] isci: unify phy event handlers (David Milburn) [718341]
- [scsi] isci: unify phy frame handlers (David Milburn) [718341]
- [scsi] isci: remove phy destruct handlers (David Milburn) [718341]
- [scsi] isci: unify phy reset handlers (David Milburn) [718341]
- [scsi] isci: unify phy stop handlers (David Milburn) [718341]
- [scsi] isci: unify phy start handlers (David Milburn) [718341]
- [scsi] isci: merge phy substates (David Milburn) [718341]
- [scsi] isci: remove the completion and event state handlers (David Milburn) [718341]
- [scsi] isci: remove request task context completion state handler (David Milburn) [718341]
- [scsi] isci: unify request frame handlers (David Milburn) [718341]
- [scsi] isci: unify request start handlers (David Milburn) [718341]
- [scsi] isci: unify request abort handlers (David Milburn) [718341]
- [scsi] isci: merge stp req substates into primary state machine (David Milburn) [718341]
- [scsi] isci: merge smp req substates into primary state machine (David Milburn) [718341]
- [scsi] isci: merge stp req substates into primary state machine (David Milburn) [718341]
- [scsi] isci: uplevel port infrastructure (David Milburn) [718341]
- [scsi] isci: uplevel phy infrastructure (David Milburn) [718341]
- [scsi] isci: uplevel request infrastructure (David Milburn) [718341]
- [scsi] isci: uplevel state machine (David Milburn) [718341]
- [scsi] isci: uplevel reg hw data structs and frame handling (David Milburn) [718341]
- [scsi] isci: move core/controller to host (David Milburn) [718341]
- [scsi] isci: unify constants (David Milburn) [718341]
- [scsi] isci: unify request data structures (David Milburn) [718341]
- [scsi] isci: make command/response iu explicit req object members (David Milburn) [718341]
- [scsi] isci: move task context alignment to compile time (David Milburn) [718341]
- [scsi] isci: make sgl explicit/aligned request object member (David Milburn) [718341]
- [scsi] isci: move stp request info to scic_sds_request (David Milburn) [718341]
- [scsi] isci: unify phy data structures (David Milburn) [718341]
- [scsi] isci: unify phy data structures (David Milburn) [718341]
- [scsi] isci: rnc state machine table c99 conversion (David Milburn) [718341]
- [scsi] isci: remove scic_sds_port_increment_request_count (David Milburn) [718341]
- [scsi] isci: kill scic_controller_get_port_handle function (David Milburn) [718341]
- [scsi] isci: Removing unnecessary functions in request.c (David Milburn) [718341]
- [scsi] isci: unify isci_host data structures (David Milburn) [718341]
- [scsi] isci: implement I_T_nexus_reset (David Milburn) [718341]
- [scsi] isci: fix ata locking (David Milburn) [718341]
- [scsi] isci: removing intel_*.h headers (David Milburn) [718341]
- [scsi] isci: Using Linux SSP frame header (David Milburn) [718341]
- [scsi] isci: Remove SCIC_SWAP_DWORD() (David Milburn) [718341]
- [scsi] isci: fixup SAS iaf protocols data structure (David Milburn) [718341]
- [scsi] isci: remove redundant copies of IAF (David Milburn) [718341]
- [scsi] isci: Converting smp_response to Linux native smp_resp (David Milburn) [718341]
- [scsi] isci: Fixup of smp request (David Milburn) [718341]
- [scsi] isci: Convert of sci_ssp_response_iu to ssp_response_iu (David Milburn) [718341]
- [scsi] isci: Fixup SSP command IU and task IU (David Milburn) [718341]
- [scsi] isci: renaming sas_capabilities to scic_phy_cap (David Milburn) [718341]
- [scsi] isci: Collapsing of phy_type data structure (David Milburn) [718341]
- [scsi] isci: Convert SAS identify address frame to native format (David Milburn) [718341]
- [scsi] isci: Convert ATA defines to Linux native defines (David Milburn) [718341]
- [scsi] isci: Convert SATA fis data structures to Linux native (David Milburn) [718341]
- [scsi] isci: remove compile-time (Kconfig) silicon configuration (David Milburn) [718341]
- [scsi] isci: Removing unused define SCIC_SDS_4_ENABLED (David Milburn) [718341]
- [scsi] isci: kill scic_sds_remote_device.state_handlers (David Milburn) [718341]
- [scsi] isci: unify remote_device frame_handlers (David Milburn) [718341]
- [scsi] isci: unify remote_device event_handlers (David Milburn) [718341]
- [scsi] isci: kill remote_device resume_handler (David Milburn) [718341]
- [scsi] isci: unify remote_device suspend_handlers (David Milburn) [718341]
- [scsi] isci: kill remote_device complete_task_handler (David Milburn) [718341]
- [scsi] isci: unify remote_device start_task_handlers (David Milburn) [718341]
- [scsi] isci: kill remote_device continue_io_handler (David Milburn) [718341]
- [scsi] isci: unify remote_device complete_io_handlers (David Milburn) [718341]
- [scsi] isci: unify remote_device start_io_handlers (David Milburn) [718341]
- [scsi] isci: unify remote_device reset_complete_handlers (David Milburn) [718341]
- [scsi] isci: unify remote_device reset_handlers (David Milburn) [718341]
- [scsi] isci: unify remote_device destruct_handlers (David Milburn) [718341]
- [scsi] isci: kill remote_device fail_handler (David Milburn) [718341]
- [scsi] isci: unify remote_device stop_handlers (David Milburn) [718341]
- [scsi] isci: unify remote_device start_handlers (David Milburn) [718341]
- [scsi] isci: fix remote_device start_io regressions (David Milburn) [718341]
- [scsi] isci: kill scic_remote_device_get_connection_rate (David Milburn) [718341]
- [scsi] isci: merge remote_device substates into one state machine (David Milburn) [718341]
- [scsi] isci: Removed sci_object.h from project (David Milburn) [718341]
- [scsi] isci: Removed sci_base_object from scic_sds_request (David Milburn) [718341]
- [scsi] isci: no sci_base_object in scic_sds_remote_node_context (David Milburn) [718341]
- [scsi] isci: Removed sci_base_object from scic_sds_remote_device (David Milburn) [718341]
- [scsi] isci: Removed sci_base_object from scic_sds_port (David Milburn) [718341]
- [scsi] isci: Removed sci_base_object from scic_sds_phy (David Milburn) [718341]
- [scsi] isci: Removed sci_base_object from scic_sds_controller (David Milburn) [718341]
- [scsi] isci: Removed struct sci_base_object from state machine (David Milburn) [718341]
- [scsi] isci: Implement SCU AFE recipe 10. (David Milburn) [718341]
- [scsi] isci: Remove excessive log noise with expander hot-unplug (David Milburn) [718341]
- [scsi] isci: removing non-working ATAPI code (David Milburn) [718341]
- [scsi] isci: remove scic_sds_remote_device_get_port_index (David Milburn) [718341]
- [scsi] isci: remove sci_sas_address in scic_sds_remote_device (David Milburn) [718341]
- [scsi] isci: kill smp_discover_response (David Milburn) [718341]
- [scsi] isci: kill smp_discover_response_protocols (David Milburn) [718341]
- [scsi] isci: cleanup remote device construction and comments (David Milburn) [718341]
- [scsi] isci: move remote_device handling out of the core (David Milburn) [718341]
- [scsi] isci: unify remote_device data structures (David Milburn) [718341]
- [scsi] isci: remove rnc->device back pointer (David Milburn) [718341]
- [scsi] isci: make remote_node_context member of remote_device (David Milburn) [718341]
- [scsi] isci: rely on irq core for intx muxing, silence screamer (David Milburn) [718341]
- [scsi] isci: give this_* and the_* vars more meaningful names (David Milburn) [718341]
- [scsi] isci: audit usage of BUG_ON macro in isci driver (David Milburn) [718341]
- [scsi] isci: sparse warnings cleanup (David Milburn) [718341]
- [scsi] isci: replace sci_sas_link_rate with sas_linkrate (David Milburn) [718341]
- [scsi] isci: remove base_phy abstraction (David Milburn) [718341]
- [scsi] isci: remove base_port abstraction (David Milburn) [718341]
- [scsi] isci: remove base_remote_device abstraction (David Milburn) [718341]
- [scsi] isci: remove scic_controller state handlers (David Milburn) [718341]
- [scsi] isci: simplify dma coherent allocation (David Milburn) [718341]
- [scsi] isci: simplify request state handlers (David Milburn) [718341]
- [scsi] isci: kill dead data structurs in scic_io_request.h (David Milburn) [718341]
- [scsi] isci: remove base_request abstraction (David Milburn) [718341]
- [scsi] isci: remove base_controller abstraction (David Milburn) [718341]
- [misc] kernel: add BUILD_BUG_ON_NOT_POWER_OF_2 (David Milburn) [718341]
- [misc] jiffies: add time_is_after_jiffies (David Milburn) [718341]
- [net] igbvf: driver update for RHEL5.8 (Stefan Assmann) [714316]
- [net] igb: driver update for RHEL5.8 (Stefan Assmann) [714313]
- [net] qlge: Version change to v1.00.00.29 (Chad Dupuis) [714242]
- [net] qlge: Adding LICENSE file for qlge (Chad Dupuis) [714242]
- [net] qlge: Fix printk prio so fatal errors always reported (Chad Dupuis) [714242]
- [net] qlge: Fix crash caused by mailbox execution on wedged chip (Chad Dupuis) [714242]
- [net] qlge: make nic_operations struct const (Chad Dupuis) [714242]
- [net] qlge: Fix incorrect use of modparams and netdev msg level (Chad Dupuis) [714242]
- [net] qlge: Remove unnecessary casts of netdev_priv (Chad Dupuis) [714242]
- [net] qlge: Generate the coredump to ethtool user buffer (Chad Dupuis) [714242]
- [net] qlcnic: Change CDRP function (Chad Dupuis) [714232]
- [net] qlcnic: Added error logging for firmware abort (Chad Dupuis) [714232]
- [net] qlcnic: add beacon test support (Chad Dupuis) [714232]
- [net] qlcnic: fix cdrp race condition (Chad Dupuis) [714232]
- [net] qlcnic: Change debug messages in loopback path (Chad Dupuis) [714232]
- [net] qlcnic: Add FLT entry for CO cards FW image region (Chad Dupuis) [714232]
- [net] qlcnic: detect fan failure (Chad Dupuis) [714232]
- [net] qlcnic: Add NETIF_F_VLAN_SG flag (Chad Dupuis) [714232]
- [net] qlcnic: fix ethtool link status (Chad Dupuis) [714232]
- [net] qlcnic: Added debug info (Chad Dupuis) [714232]
- [net] qlcnic: Move get template from probe to start fw (Chad Dupuis) [714232]
- [net] qlcnic: Fix delay in reset path (Chad Dupuis) [714232]
- [net] qlcnic: FW dump related changes (Chad Dupuis) [714232]
- [net] qlcnic: Fix env var for udev event during FW dump (Chad Dupuis) [714232]
- [net] qlcnic: change capture mask for FW dump (Chad Dupuis) [714232]
- [net] qlcnic: define error code for loopback test (Chad Dupuis) [714232]
- [net] qlcnic: fix race in skb->len access (Chad Dupuis) [714232]
- [net] qlcnic: enable mac-learning in promiscous mode (Chad Dupuis) [714232]
- [net] qlcnic: updated supported cards information (Chad Dupuis) [714232]
- [net] qlcnic: fix chip reset logic (Chad Dupuis) [714232]
- [net] qlcnic: add external loopback support through sysfs (Chad Dupuis) [714232]
- [net] qlcnic: multi protocol internal loopback support added (Chad Dupuis) [714232]
- [net] qlcnic: Add support to enable/disable FW dump capability (Chad Dupuis) [714232]
- [net] qlcnic: fix default operating state of interface (Chad Dupuis) [714232]
- [net] qlcnic: fix initial number of msix entries in adapter (Chad Dupuis) [714232]
- [net] qlcnic: Add code to tune FW dump (Chad Dupuis) [714232]
- [net] qlcnic: Remove holding api lock while taking the dump (Chad Dupuis) [714232]
- [net] qlcnic: Add capability to take FW dump deterministically (Chad Dupuis) [714232]
- [net] qlcnic: Added sysfs node support (Chad Dupuis) [714232]
- [net] qlcnic: Remove casts of void * (Chad Dupuis) [714232]
- [net] qlcnic: Avoid double free of skb in tx path (Chad Dupuis) [714232]
- [net] qlcnic: Fix bug in FW queue dump (Chad Dupuis) [714232]
- [net] qlcnic: Bumped up version number to 5.0.18 (Chad Dupuis) [714232]
- [net] qlcnic: FW dump support (Chad Dupuis) [714232]
- [net] qlcnic: Support for GBE port settings (Chad Dupuis) [714232]
- [net] qlcnic: configure number of RSS rings using sysfs (Chad Dupuis) [714232]
- [net] qlcnic: Update version number to 5.0.16 (Chad Dupuis) [714232]
- [net] qlcnic: Fix LRO disable (Chad Dupuis) [714232]
- [net] qlcnic: Use flt method to determine flash fw region (Chad Dupuis) [714232]
- [net] qlcnic: Remove unused code (Chad Dupuis) [714232]
- [net] qlcnic: Code optimization patch (Chad Dupuis) [714232]
- [net] qlcnic: Cleanup patch (Chad Dupuis) [714232]
- [net] qlcnic: Memory leak fix (Chad Dupuis) [714232]
- [net] qlcnic: Make PCI info available in all modes (Chad Dupuis) [714232]
- [misc] Add rounddown_pow_of_two routine to log2.h (Chad Dupuis) [714232]
- [pci] add latency tolerance reporting enable/disable support (Myron Stowe) [714171]
- [pci] Assign values to pci_obff_signal_type enumeration (Myron Stowe) [714171]
- [pci] add OBFF enable/disable support (Myron Stowe) [714171]
- [pci] add ID-based ordering enable/disable support (Myron Stowe) [714171]
- [pci] introduce pci_is_pcie (Myron Stowe) [714171]
- [pci] introduce pci_pcie_cap (Myron Stowe) [714171]
- [sound] hda: ALSA Panther Point Audio Support (Jaroslav Kysela) [713663]
- [sound] hda: Enable snoop bit for AMD controllers (Jaroslav Kysela) [713366]
- [fs] hfs: fix hfs_find_init() sb->ext_tree NULL ptr oops (Phillip Lougher) [712776]
- [fs] nfs: return error in callback if encode/decode fails (Dave Wysochanski) [709515]
- [net] tcp: Shrink syncookie_secret by 8 bytes (Thomas Graf) [705484]
- [scsi] device_handler: Attach to UNAVAILABLE/OFFLINE AAS devices (Mike Christie) [700082]
- [net] cxgb3: Apply interrupt coalescing settings to all queues (Neil Horman) [694583]
- [mm] page-writeback: fix calculation of oldest_jif in wb_kupdate (Jarod Wilson) [691087]
- [block] nbd: add a user-settable timeout for I/O (Jeff Moyer) [676491]
- [net] ipv6: ignore looped-back NA while dad is running (Thomas Graf) [668027]
- [net] sctp: Set correct error cause value for missing parameters (Thomas Graf) [629938]
- [net] Prevent pktgen from sending shared skbs (Neil Horman) [575938]
- [md] raid10: fix far resync data corruptor (Doug Ledford) [468379]
- [xen] x86: Clear IRQ_GUEST when setting action to NULL (Igor Mammedov) [713221]
- [xen] x86: check for NULL desc->action when unbinding guest pirq (Igor Mammedov) [713221]
- [xen] x86: fix msi_free_irq (Igor Mammedov) [713221]
- [xen] x86: teardown_msi_irq is not needed (Igor Mammedov) [713221]
- [xen] x86: irq removal rewrite (Igor Mammedov) [713221]
- [xen] x86: Move interrupt vector management to irq.c (Igor Mammedov) [713221]

* Thu Oct 06 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-287.el5]
- [parport] Enable StarTech PEX1P Parallel Port (Prarit Bhargava) [739758]
- [crypto] padlock: Fix spurious ECB page fault (Milan Broz) [739468]
- [fs] gfs2: speed up large file delete/unlink (Robert S Peterson) [738440]
- [virt] xen: don't hardcode is_running_on_xen for PV-on-HVM (Laszlo Ersek) [734708]
- [s390] kernel: remove code to handle topology interrupts (Hendrik Brueckner) [732736]
- [net] cxgb3: Fix NULL pointer dereference in t3_l2t_get (Neil Horman) [721173]
- [misc] kernel: plug taskstats io infoleak (Jerome Marchand) [716846] {CVE-2011-2494}
- [x86_64] io_apic: only scan the root bus in early PCI quirks (Dave Maley) [716552]
- [net] bnx2: Update to latest upstream version 2.1.11 (Neil Horman) [715392]
- [usb] Make device reset stop retrying after disconnect (Don Zickus) [709699]
- [acpi] Call _PDC before retrieving CPU information (Matthew Garrett) [707642]
- [net] tg3: Fix io failures after chip reset (John Feeney) [702346 731098]
- [net] ipv6: properly use ICMP6MSGOUT_INC_STATS in ndisc_send_skb (Jiri Pirko) [698728]
- [net] sctp: Mark tsn as received after all allocations finish (Max Matveev) [696430]
- [scsi] Reduce error recovery time by reducing use of TURs (Mike Christie) [694625]
- [scsi] don't fail scans when host is in recovery (Rob Evers) [657345]
- [video] radeonfb: block use of low refresh 800x600-43 on pseries (Dave Airlie) [638576]

* Wed Sep 21 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-286.el5]
- [net] benet: Add missing comma between constant string array (Ivan Vecera) [714291]
- [net] be2net: create/destroy rx-queues on interface open/close (Ivan Vecera) [714291]
- [net] be2net: fix initialization of vlan_prio_bmap (Ivan Vecera) [714291]
- [net] be2net: Remove casts of void pointers (Ivan Vecera) [714291]
- [net] be2net: Fix Rx pause counter for lancer (Ivan Vecera) [714291]
- [net] be2net: use older opcode if MCC_CREATE_EXT not supported (Ivan Vecera) [714291]
- [net] be2net: fix set but unused var in lancer_fw_download (Ivan Vecera) [714291]
- [net] be2net: Enable SR-IOV for Lancer hardware (Ivan Vecera) [714291]
- [net] be2net: FW download for Lancer hardware (Ivan Vecera) [714291]
- [net] be2net: implement stats for Lancer hardware (Ivan Vecera) [714291]
- [net] be2net: Support for version 1 of stats for BE3 (Ivan Vecera) [714291]
- [net] be2net: fix mbox polling for signal reception (Ivan Vecera) [714291]
- [net] be2net: handle signal reception while waiting for POST (Ivan Vecera) [714291]
- [net] be2net: Fix to prevent flooding of TX queue (Ivan Vecera) [714291]
- [net] be2net: In case of UE, do not dump registers for Lancer (Ivan Vecera) [714291]
- [net] be2net: Disable coalesce water mark mode of CQ for Lancer (Ivan Vecera) [714291]
- [net] be2net: Handle error completion in Lancer (Ivan Vecera) [714291]
- [net] be2net: fix bugs related to PVID (Ivan Vecera) [714291]
- [net] be2net: fix wrb reuse and misc bugs in be_cmd_get_regs (Ivan Vecera) [714291]
- [net] be2net: pass domain id to be_cmd_link_status_query (Ivan Vecera) [714291]
- [net] be2net: fix be_mcc_compl_process to id eth_get_stat command (Ivan Vecera) [714291]
- [net] be2net: display nic speeds other than 1Gbps/10Gbps (Ivan Vecera) [714291]
- [net] be2net: allow register dump only for PFs (Ivan Vecera) [714291]
- [net] be2net: Fix unused-but-set variables (Ivan Vecera) [714291]
- [net] be2net: Use netdev_alloc_skb_ip_align (Ivan Vecera) [714291]
- [net] be2net: call FLR after setup wol in be_shutdown (Ivan Vecera) [714291]
- [net] be2net: dynamically allocate adapter->vf_cfg (Ivan Vecera) [714291]
- [net] be2net: fix to get max VFs supported from adapter (Ivan Vecera) [714291]
- [net] be2net: use common method to check for sriov function type (Ivan Vecera) [714291]
- [net] be2net: Fix a potential crash during shutdown (Ivan Vecera) [714291]
- [net] be2net: remove one useless line (Ivan Vecera) [714291]
- [net] be2net: cancel be_worker on shutdown even when i/f is down (Ivan Vecera) [714291]
- [net] be2net: remove redundant code in be_worker (Ivan Vecera) [714291]
- [net] be2net: parse vid/vtm rx-compl fields only if vlanf bit set (Ivan Vecera) [714291]
- [net] be2net: refactor code that decides adapter->num_rx_queues (Ivan Vecera) [714291]
- [net] be2net: add ethtool FAT dump retrieval support (Ivan Vecera) [714291]
- [mm] s390: fix first time swap use results in heavy swapping (Hendrik Brueckner) [722482]
- [mm] fix rotate_reclaimable_page deadlock and clean up (Jerome Marchand) [699549]

* Wed Sep 14 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-285.el5]
- [ata] ahci: Add missing Panther Point SATA RAID DeviceID (Prarit Bhargava) [735369]
- [scsi] megaraid: remove obsolete megaraid_sas.c (Tomas Henzl) [735120]
- [net] Compute protocol seq numbers and fragment IDs using MD5 (Jiri Pirko) [732663]
- [crypto] Move md5_transform to lib/md5.c (Jiri Pirko) [732663]
- [s390] kernel: fix NSS creation with initrd (Hendrik Brueckner) [730779]
- [virt] xen: fix GFP mask handling in dma_alloc_coherent (Laszlo Ersek) [730247]
- [fs] nfs: Fix client not honoring nosharecache mount option (David Jeffery) [730097]
- [pci] check pm support before looking at individual power states (Stefan Assmann) [716834]
- [mm] avoid wrapping vm_pgoff in mremap and stack expansion (Jerome Marchand) [716544] {CVE-2011-2496}
- [md] bitmap: protect against bitmap removal while being updated (Stanislaw Gruszka) [711536]
- [scsi] scsi_dh_rdac: link HBA and storage to support partitions (Mike Snitzer) [710014]
- [scsi] scsi_dh_rdac: use WWID from C8 page to identify storage (Mike Snitzer) [710014]
- [x86] nmi: make NMI_NONE default watchdog in x86_64 hvm guests (Laszlo Ersek) [707966]
- [mm] Fix incorrect off-by-one centisec dirty values (Larry Woodman) [691087]
- [net] bnx2x: fix bringup of BCM57710 (Michal Schmidt) [680411]
- [fs] ext{2,3}: fix file date underflow on fs on 64 bit systems (Eric Sandeen) [655174]
- [xen] fix nodes' memory parsing with future-hotplug memory range (Laszlo Ersek) [543064]

* Thu Sep 01 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-284.el5]
- [net] be2net: request native mode each time the card is reset (Ivan Vecera) [720501]
- [net] be2net: fix the ethtool op to set Tx CSUM (Ivan Vecera) [718187]
- [net] be2net: remove bogus unlikely on vlan check (Ivan Vecera) [730239]
- [net] be2net: non-member vlan pkts not received in promisc mode (Ivan Vecera) [730239]
- [net] be2net: Use NTWK_RX_FILTER command for promiscous mode (Ivan Vecera) [730239]
- [net] be2net: fix crash receiving non-member VLAN packets (Ivan Vecera) [730239]
- [virt] xen/netfront: no disable s/g when renegotiating features (Paolo Bonzini) [733416]
- [fs] ecryptfs: Add mount option to check uid of mounting device (Eric Sandeen) [731174] {CVE-2011-1833}
- [s390] kernel: fix system hang if hangcheck timer expires (Hendrik Brueckner) [730313]
- [s390] qeth: fix wrong number of output queues for HiperSockets (Hendrik Brueckner) [730319]
- [scsi] qla2xxx: Re-add checks for null fcport references (Chad Dupuis) [728219]
- [fs] aio: fix aio+dio completion path regression w/3rd-party bits (Jeff Moyer) [727504]
- [net] ipv6: make fragment identifications less predictable (Jiri Pirko) [723431]
- [net] ipv6: Remove unused skb argument of ipv6_select_ident (Jiri Pirko) [723431]
- [s390] dasd: fix bug in dasd initialization cleanup (Hendrik Brueckner) [723491]
- [virt] xen: attach host CD-ROM to PV guest as vbd (Laszlo Ersek) [717434]
- [misc] taskstats: don't allow duplicate entries in listener mode (Jerome Marchand) [715450] {CVE-2011-2484}
- [scsi] ipr: bump the version number (Steve Best) [714258]
- [scsi] ipr: remove unneeded volatile declarations (Steve Best) [714258]
- [scsi] ipr: fix synchronous request flags for better performance (Steve Best) [714258]
- [scsi] ipr: fix buffer overflow (Steve Best) [714258]
- [s390] qdio: reset error states immediately (Hendrik Brueckner) [709712]
- [usb] fix interface sysfs file-creation bug (Don Zickus) [637930]
- [usb] don't touch sysfs stuff when altsetting is unchanged (Don Zickus) [637930]
- [base] Fix potential deadlock in driver core (Don Zickus) [637930]
- [virt] xen: more informative messages after resize (Laszlo Ersek) [618317]
- [virt] xen: support online dynamic resize of guest virtual disks (Laszlo Ersek) [618317]
- [virt] xen: Move definition of struct backend_info to common spot (Laszlo Ersek) [618317]
- [net] bonding: fix panic if initialization fails (Andy Gospodarek) [608156]
- [net] gro: Only reset frag0 when skb can be pulled (Herbert Xu) [679682] {CVE-2011-2723}
- [net] sctp: fix memory reclaim and panic in sctp_sock_rfree (Thomas Graf) [714870] {CVE-2011-2482}
- [xen] lower BOOT_TRAMPOLINE, sync early stack & trampoline_gdt (Laszlo Ersek) [716788]
- [xen] x86_64: bump default NR_CPUS to 256 and trim debug log spam (Laszlo Ersek) [714053]
- [xen] passthrough: block VT-d MSI trap injection (Paolo Bonzini) [716302]
- [xen] hvm/svm: fix task switch (Paolo Bonzini) [720936]
- [xen] hvm: exclude VMX_PROCBASED_CTL2 from MSRs guest can access (Paolo Bonzini) [732752]
- [xen] iommu: disable bus-mastering on hw that causes IOMMU fault (Laszlo Ersek) [730343] {CVE-2011-3131}
- [xen] x86_emulate: Fix SAHF emulation (Igor Mammedov) [718884] {CVE-2011-2519}
- [xen] fix off-by-one shift in x86_64 __addr_ok (Laszlo Ersek) [719850] {CVE-2011-2901}

* Thu Aug 25 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-283.el5]
- [fs] nfsd: don't allow fl_break callback to sleep (Jeff Layton) [721200]
- [fs] locks: move lease lock alloc earlier in generic_setlease (Jeff Layton) [721200]
- [fs] locks: when unlocking lease, skip locking-related steps (Jeff Layton) [721200]
- [fs] locks: fix a lease return-value mixup (Jeff Layton) [721200]
- [fs] locks: Fix potential OOPS in generic_setlease (Jeff Layton) [721200]
- [usb] auerswald: fix buffer overflow (Don Zickus) [722396] {CVE-2009-4067}
- [fs] cifs: fix possible memory corruption in CIFSFindNext (Jeff Layton) [732471]
- [fs] cifs: revert special handling for matching krb5 sessions (Jeff Layton) [697396]
- [fs] cifs: check for NULL session password (Jeff Layton) [697396]
- [fs] cifs: fix NULL pointer dereference in cifs_find_smb_ses (Jeff Layton) [697396]
- [fs] cifs: clean up cifs_find_smb_ses (Jeff Layton) [697396]
- [net] be2net: account for skb allocation failures (Ivan Vecera) [730108]
- [fs] mbcache: Limit the maximum number of cache entries (Eric Sandeen) [729261]
- [net] bnx2x: downgrade Max BW error message to debug (Michal Schmidt) [727614]
- [net] sock: do not change prot->obj_size (Jiri Pirko) [725713]
- [net] be2net: Fix Tx stall issue (Ivan Vecera) [722549]
- [net] be2net: rx-dropped wraparound fix (Ivan Vecera) [722302]
- [net] be2net: fix netdev_stats_update (Ivan Vecera) [722302]
- [net] bonding: make 802.3ad use latest lacp_rate (Jiri Pirko) [718641]
- [net] bonding: Rename rx_machine_lock to state_machine_lock (Jiri Pirko) [718641]
- [net] bonding: Fix 802.3ad state machine locking (Jiri Pirko) [718641]
- [net] bonding: add missing xmit_hash_policy=layer2+3 info (Weiping Pan) [717850]
- [powerpc] eeh: Display eeh error location for bus and device (Steve Best) [712418]
- [powerpc] eeh: Handle functional reset on non-PCIe device (Steve Best) [712418]
- [powerpc] eeh: Propagate needs_freset flag to device at PE (Steve Best) [712418]
- [powerpc] eeh: Add support for ibm, configure-pe RTAS call (Steve Best) [712418]
- [fs] cifs: don't allow cifs_reconnect exit w/NULL socket pointer (Jeff Layton) [704921]
- [fs] cifs: clarify the meaning of tcpStatus == CifsGood (Jeff Layton) [704921]
- [fs] cifs: split posix open/mkdir from legacy mkdir in stats (Jeff Layton) [706339]
- [virt] xen: plug leaks in netfront::setup_device (Laszlo Ersek) [703150]
- [virt] xen: ensure dynamic IRQ allocation success (Laszlo Ersek) [703150]
- [net] vlan: correct pkt_type if it matches changed mac (Weiping Pan) [698928]
- [virt] xen: Allow arbitrary mtu size until frontend connected (Paolo Bonzini) [697021]
- [fs] proc: Fix procfs race vs rmmod or hot-remove (David Howells) [675781]
- [virt] xen: empty stale MSI-X vector set when resetting device (Laszlo Ersek) [688673]
- [virt] xen: msi cleanup after destroyed domain (Laszlo Ersek) [688673]
- [xen] unsigned int corrections (Laszlo Ersek) [648596]

* Mon Aug 22 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-282.el5]
- Fix infrastructure error that led to recent xen patches not applying

* Sun Aug 21 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-281.el5]
- Bump NVR due to buildsystem problems during prior build

* Fri Aug 19 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-280.el5]
- Revert: [virt] xen/netback: Remove auto/premature netif queue (Jarod Wilson) [714283]

* Tue Aug 16 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-279.el5]
- [char] tpm: Fix uninitialized usage of data buffer (Stanislaw Gruszka) [684673] {CVE-2011-1160}
- [serial] 8250: Fix capabilities when changing the port type (Steve Best) [707051]
- [serial] 8250_pci: EEH support for IBM/Digi PCIe 2-port Adapter (Steve Best) [707051]
- [serial] 8250_pci: add support for Digi/IBM PCIe 2-port Adapter (Steve Best) [707051]
- [misc] hypervisor: fix race in interrupt hook code (Prarit Bhargava) [692966]
- [sound] alsa: enable snoop for Intel Cougar Point in hda_intel (Prarit Bhargava) [699451]
- [char] watchdog: TCO Watchdog support for Intel Panther Point PCH (Prarit Bhargava) [699451]
- [i2c] i2c-i801: SMBus support for Intel Panther Point DeviceIDs (Prarit Bhargava) [699451]
- [ata] ahci: AHCI mode for Intel Panther Point Device IDs (Prarit Bhargava) [699451]
- [ata] ata_piix: IDE mode for Intel Panther Point Device IDs (Prarit Bhargava) [699451]
- [misc] irq and pci_ids for Intel DH89xxCC DeviceIDs (Prarit Bhargava) [699451]
- [misc] Identify IBM x3850 as multi-chassis (Prarit Bhargava) [700886]
- [net] cnic, bnx2: Check iSCSI support early in bnx2_init_one (Neil Horman) [710272]
- [virt] xen/netback: Remove auto/premature netif queue restart (Laszlo Ersek) [714283]
- [fs] ext4: Fix max size and logical block counting of extent file (Lukas Czerner) [722563] {CVE-2011-2695}
- [fs] nfs: don't use d_move in nfs_async_rename_done (Jeff Layton) [729446]
- [fs] nfs: have nfs_flush_list issue FLUSH_SYNC writes in parallel (Jeff Layton) [728508]
- [s390] crypto: fix prng error in initial seed calculation (Hendrik Brueckner) [709711]
- [fs] nfsd: fix auto-sizing of nfsd request/reply buffers (J. Bruce Fields) [691927]
- [fs] nfsd: Allow max size of NFSd payload to be configured (J. Bruce Fields) [691927]
- [fs] nfsd: Prep knfsd to support rsize/wsize of 1MB, over TCP (J. Bruce Fields) [691927]
- [misc] svcrpc: prepare svc_rqst for kabi-safe modification (J. Bruce Fields) [691927]
- [xen] amd-iommu: Fix an interrupt remapping issue (Frank Arnold) [717976]
- [xen] hvm: Fix possible guest tick losing after save/restore (Paolo Bonzini) [674663]
- [xen] mm: fix race with ept_entry management (Andrew Jones) [729529]

* Wed Aug 10 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-278.el5]
- [scsi] ipr: increase the dump size for 64 bit adapters (Steve Best) [710324]
- [scsi] ipr: fix possible false positive detected stuck interrupt (Steve Best) [710324]
- [scsi] ipr: improve interrupt service routine performance (Steve Best) [710324]
- [scsi] ipr: add definitions for a new adapter (Steve Best) [710324]
- [scsi] ipr: fix array error logging (Steve Best) [710324]
- [net] igb: fix WOL on 2nd port on i350 (Stefan Assmann) [718988]
- [misc] irq: fix interrupt handling for kdump under high load (Stefan Assmann) [720212]
- [fs] xfs: fix overflow in xfs_growfs_data_private (Eric Sandeen) [652494]
- [fs] ext4: Don't error out fs if user tries to make file too big (Eric Sandeen) [715501]
- [x86_64] vdso: Fix possible sign extension/overflow (Prarit Bhargava) [703505]
- [x86_64] Revert ACPI APIC mode test (Prarit Bhargava) [721361]
- [net] ipv6: configure bond slaves to allow NA frames on failover (Neil Horman) [694435]
- [virt] xen: plug evtchn leak in PV-on-HVM device detach (Laszlo Ersek) [697927]
- [virt] xen/netback: wait for hotplug complete before Connected (Laszlo Ersek) [720347]
- [virt] xen: Partially revert the netback side of 14bee682 (Laszlo Ersek) [720347]
- [fs] ext4: Allow indirect-block file to grow to max file size (Lukas Czerner) [715493]
- [fs] nfs: Fix nfs_compat_user_ino64 with high bits set in fileid (Jeff Layton) [664829]
- [fs] nfs: Open O_CREAT fails existing files on non writable dirs (J. Bruce Fields) [683372]
- [xen] vmx: Accelerate VLAPIC EOI writes (Paolo Bonzini) [720986]
- [xen] x86/hvm: fix off-by-one errors in vcpuid range checks (Paolo Bonzini) [712441]
- [xen] x86: extend debug key t to collect useful clock skew info (Paolo Bonzini) [712439]
- [xen] svm: Reported SS.DPL must equal CPL, as assumed by HVM (Paolo Bonzini) [605617]
- [xen] hvm: support more opcodes for MMIO (Paolo Bonzini) [723755]
- [xen] x86: Disable writeback if BSF/BSR are passed zero input (Igor Mammedov) [713702]
- [xen] x86: BT instruction does not write to its dest operand (Igor Mammedov) [713702]
- [xen] x86: INS/OUTS need Mov attribute to force writeback (Igor Mammedov) [713702]
- [xen] x86: Fix IMUL r/m8 emulation (Igor Mammedov) [713702]
- [xen] x86: Fix MUL emulation (Igor Mammedov) [713702]
- [xen] x86: fix side-effect macro call (Igor Mammedov) [713702]
- [xen] x86: Fix CLTS emulation (Igor Mammedov) [713702]
- [xen] x86: Near JMP (Grp5 /3) shouldn't write back to its operand (Igor Mammedov) [713702]
- [xen] x86: Certain opcodes are only valid with a memory operand (Igor Mammedov) [713702]
- [xen] x86: Correct RIP-relative addr offset w/immediate byte op (Igor Mammedov) [713702]

* Wed Aug 03 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-277.el5]
- [net] sctp: reset packet information after packet transmit (Thomas Graf) [725573]
- [fs] block: initialise bd_super in bdget (Lachlan McIlroy) [707425]
- [fs] nfs: Remove bogus call to nfs4_drop_state_owner (Jeff Layton) [724923]
- [net] be2net: hash key for rss-config cmd not set (Ivan Vecera) [714244]
- [net] be2net: enable SG, CSO and TSO with VLAN offloading (Ivan Vecera) [714272]
- [net] be2net: clear interrupt bit in be_probe (Ivan Vecera) [713703]
- [net] be2net: remove certain cmd failure logging (Ivan Vecera) [716821]

* Fri Jul 22 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-276.el5]
- [wireless] nl80211: check for valid SSID size in scan operation (Stanislaw Gruszka) [718155] {CVE-2011-2517}
- [fs] xfs: handle NULL mount struct in error reports (Eric Sandeen) [720551]
- [fs] proc: restrict access to /proc/PID/io (Oleg Nesterov) [716828] {CVE-2011-2495}
- [fs] lockd: don't use file's credentials on RPCSEC_GSS mounts (Max Matveev) [701574]
- [fs] xfs: add a missing mutex_unlock to a dio error path (Jeff Moyer) [718232]
- [net] sunrpc: Don't hang forever on NLM unlock requests (Jeff Layton) [709547] {CVE-2011-2491}
- [fs] gfs2: force a log flush when invalidating the rindex glock (Benjamin Marzinski) [713229]
- [x86] io_apic: Convert tick to interrupt when checking timer irq (Amos Kong) [698842]
- [x86] io_apic: Make kernel option 'no_timer_check' always work (Amos Kong) [698842]
- [x86] io_apic: Compare jiffies with other values by time_after (Amos Kong) [698842]
- [xen] Fix x86_emulate handling of imul with immediate operands (Igor Mammedov) [700565]

* Mon Jul 11 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-275.el5]
- [fs] Fix wrongly vfree'ing a kmalloc'ed area (Larry Woodman) [719495]
- [fs] dlm: bump default hash table and maximum allocatable sizes (Bryn M. Reeves) [715603]
- [net] tipc: Overhaul of socket locking logic (Max Matveev) [704192]

* Fri Jul 08 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-274.el5]
- [xen] svm: fix invlpg emulator regression (Paolo Bonzini) [719894]

* Mon Jul 04 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-273.el5]
- Revert: [fs] proc: Fix rmmod/read/write races in /proc entries (Jarod Wilson) [717068]
- [xen] disregard trailing bytes in an invalid page (Paolo Bonzini) [717742]
- [xen] prep __get_instruction_length_from_list for partial buffers (Paolo Bonzini) [717742]
- [xen] remove unused argument to __get_instruction_length (Paolo Bonzini) [717742]
- [xen] let __get_instruction_length always read into own buffer (Paolo Bonzini) [717742]

* Tue Jun 28 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-272.el5]
- [xen] x86: spinlock support for up to 255 CPUs (Laszlo Ersek) [713123]
- [xen] remove block scope mtrr identifiers shadowing file scope (Laszlo Ersek) [713123]
- [xen] Actually hold back MTRR init while booting secondary CPUs (Laszlo Ersek) [713123]
- [xen] remove unused mtrr_bp_restore (Laszlo Ersek) [713123]
- [xen] x86: Fix crash on amd iommu systems (Igor Mammedov) [714275]

* Mon Jun 27 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-271.el5]
- [net] igmp: ip_mc_clear_src only when we no users of ip_mc_list (Veaceslav Falico) [707179]
- [scsi] cxgb3i: fix programing of dma page sizes (Neil Horman) [710498]
- [xen] hvm: secure vmx cpuid (Andrew Jones) [706325] {CVE-2011-1936}
- [xen] hvm: secure svm_cr_access (Andrew Jones) [703716] {CVE-2011-1780}
- [xen] hvm: svm support cleanups (Andrew Jones) [703716] {CVE-2011-1780}

* Thu Jun 23 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-270.el5]
- [fs] proc: fix compile warning in pdeaux addition (Jarod Wilson) [675781]
- [net] bluetooth: l2cap and rfcomm: fix info leak to userspace (Thomas Graf) [703021]
- [net] inet_diag: fix inet_diag_bc_audit data validation (Thomas Graf) [714539] {CVE-2011-2213}
- [misc] signal: fix kill signal spoofing issue (Oleg Nesterov) [690031] {CVE-2011-1182}
- [fs] proc: fix signedness issue in next_pidmap (Oleg Nesterov) [697827] {CVE-2011-1593}
- [char] agp: fix OOM and buffer overflow (Jerome Marchand) [699010] {CVE-2011-1746}
- [char] agp: fix arbitrary kernel memory writes (Jerome Marchand) [699006] {CVE-2011-1745 CVE-2011-2022}
- [net] be2net: fix queue creation order and pci error recovery (Ivan Vecera) [711653]
- [infiniband] core: Handle large number of entries in poll CQ (Jay Fenlason) [668371] {CVE-2010-4649 CVE-2011-1044}
- [infiniband] core: fix panic in ib_cm:cm_work_handler (Jay Fenlason) [679996] {CVE-2011-0695}
- [fs] validate size of EFI GUID partition entries (Anton Arapov) [703026] {CVE-2011-1776}

* Tue Jun 21 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-269.el5]
- [mm] only throttle page dirtying for specially marked BDIs (Jeff Layton) [711450]
- Revert: [base] Fix potential deadlock in driver core (Don Zickus) [703084]
- [fs] proc: Fix rmmod/read/write races in /proc entries (David Howells) [675781]
- [scsi] qla4xxx: Update driver version to V5.02.04.01.05.07-d0 (Chad Dupuis) [704153]
- [scsi] qla4xxx: clear SCSI COMPLETION INTR bit during F/W init (Chad Dupuis) [704153]
- [usb] wacom: add support for DTU-2231 (Aristeu Rozanski) [683549]
- [xen] fix MAX_EVTCHNS definition (Laszlo Ersek) [701243] {CVE-2011-1763}

* Tue Jun 14 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-268.el5]
- [net] sctp: fix calc of INIT/INIT-ACK chunk length to set (Thomas Graf) [695385] {CVE-2011-1573}
- [scsi] ibmvfc: Fix Virtual I/O failover hang (Steve Best) [710477]
- [kernel] irq: Note and disable spurious interrupts on kexec (Prarit Bhargava) [611407]
- [net] bnx2x: Update firmware to 6.2.9 (Michal Schmidt) [711079]
- [net] bnx2x: Update bnx2x_firmware.h to version 6.2.9 (Michal Schmidt) [711079]
- [net] xt_hashlimit: fix race between htable_destroy and htable_gc (Jiri Pirko) [705905]
- [fs] cifs: clear write bits if ATTR_READONLY is set (Justin Payne) [700263]
- [net] bna: clear some statistics before filling them (Ivan Vecera) [711990]
- [net] ixgbe: Disable RSC by default (Herbert Xu) [703416]
- [scsi] isci: fix scattergather list handling for smp commands (David Milburn) [710584]
- [net] netconsole: prevent setup netconsole on a slave device (Amerigo Wang) [698873]

* Wed Jun 08 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-267.el5]
- [fs] xfs: prevent leaking uninit stack memory in FSGEOMETRY_V1 p2 (Phillip Lougher) [677266] {CVE-2011-0711}
- [fs] xfs: prevent leaking uninit stack memory in FSGEOMETRY_V1 (Phillip Lougher) [677266] {CVE-2011-0711}
- [net] core: Fix memory leak/corruption on VLAN GRO_DROP (Herbert Xu) [691565] {CVE-2011-1576}

* Tue Jun 07 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-266.el5]
- [scsi] megaraid: update to driver version 5.38-rh1 (Tomas Henzl) [706244]
- [block] cciss: fix mapping of config table (Tomas Henzl) [695493]
- [block] cciss: fix dev_info null pointer deref after freeing h (Tomas Henzl) [695493]
- [block] cciss: do not call request_irq with spinlocks held (Tomas Henzl) [695493]
- [block] cciss: prototype cciss_sent_reset to fix error (Tomas Henzl) [695493]
- [block] cciss: mark functions as dev_init to clean up warnings (Tomas Henzl) [695493]
- [block] cciss: timeout if soft reset fails (Tomas Henzl) [695493]
- [block] cciss: use cmd_alloc for kdump (Tomas Henzl) [695493]
- [block] cciss: Use cciss not hpsa in init_driver_version (Tomas Henzl) [695493]
- [block] cciss: reduce stack usage a reset verifying code (Tomas Henzl) [695493]
- [block] cciss: do not store pci state on stack (Tomas Henzl) [695493]
- [block] cciss: no PCI power management reset method if known bad (Tomas Henzl) [695493]
- [block] cciss: increase timeouts for post-reset no-ops (Tomas Henzl) [695493]
- [block] cciss: remove superfluous sleeps around reset code (Tomas Henzl) [695493]
- [block] cciss: do soft reset if hard reset is broken (Tomas Henzl) [695493]
- [block] cciss: flush writes in interrupt mask setting code (Tomas Henzl) [695493]
- [block] cciss: clarify messages around reset behavior (Tomas Henzl) [695493]
- [block] cciss: increase time to wait for board reset to start (Tomas Henzl) [695493]
- [block] cciss: get rid of message related magic numbers (Tomas Henzl) [695493]
- [block] cciss: factor out irq request code (Tomas Henzl) [695493]
- [block] cciss: factor out scatterlist allocation functions (Tomas Henzl) [695493]
- [block] cciss: factor out command pool allocation functions (Tomas Henzl) [695493]
- [block] cciss: Define print_cmd even without tape support (Tomas Henzl) [695493]
- [block] cciss: do not use bit 2 doorbell reset (Tomas Henzl) [695493]
- [block] cciss: use new doorbell-bit-5 reset method (Tomas Henzl) [695493]
- [block] cciss: improve controller reset failure detection (Tomas Henzl) [695493]
- [block] cciss: wait longer after resetting controller (Tomas Henzl) [695493]
- [infiniband] cxgb4: Use completion objects for event blocking (Steve Best) [708081]
- [fs] ext4: fix quota deadlock (Eric Sandeen) [702197]
- [fs] ext3, ext4: update ctime when changing permission by setfacl (Eric Sandeen) [709224]
- [scsi] bfa: properly reinitialize adapter during kdump (Rob Evers) [710300]
- [scsi] lpfc: Update for 8.2.0.96.2p release (Rob Evers) [707336]
- [scsi] lpfc: Fix back to back Flogis sent without logo (Rob Evers) [707336]
- [scsi] lpfc: Fix not updating wwnn and wwpn after name change (Rob Evers) [707336]
- [scsi] lpfc: Fix CT command never completing on Big Endian host (Rob Evers) [707336]
- [scsi] lpfc: Revert fix that introduced a race condition (Rob Evers) [707336]
- [scsi] lpfc: Fix crash in rpi clean when driver load fails (Rob Evers) [707336]
- [scsi] lpfc: fix limiting RPI Count to a minimum of 64 (Rob Evers) [707336]
- [scsi] lpfc: fix overriding CT field for SLI4 IF type 2 (Rob Evers) [707336]
- [scsi] lpfc: force retry in queuecommand when port transitioning (Rob Evers) [707336]
- [scsi] lpfc: Update version for 8.2.0.96.1p release (Rob Evers) [698432]
- [scsi] lpfc: Fix double byte swap on received RRQ (Rob Evers) [698432]
- [scsi] lpfc: Fix Vports not sending FDISC after lips (Rob Evers) [698432]
- [scsi] lpfc: Fix system crash during driver unload (Rob Evers) [698432]
- [scsi] lpfc: Fix FCFI incorrect on received unsolicited frames (Rob Evers) [698432]
- [scsi] lpfc: Fix driver sending FLOGI to a disconnected FCF (Rob Evers) [698432]
- [scsi] lpfc: Fix bug with incorrect BLS Response to BLS Abort (Rob Evers) [698432]
- [scsi] lpfc: Fix adapter on Powerpc unable to login into Fabric (Rob Evers) [698432]
- [pci] export msi_desc struct and msi_desc array (Prarit Bhargava) [697666]
- [net] bonding: prevent deadlock on slave store with alb mode (Neil Horman) [706414]
- [net] mlx4: Fix dropped promiscuity flag (Michael S. Tsirkin) [592370]
- [edac] amd64_edac: Fix NULL pointer on Interlagos (Mauro Carvalho Chehab) [705040 709529]
- [scsi] ses: fix ses_set_fault() to set the fault LED function (James Takahashi) [682351]
- [redhat] configs: config file changes for SES Enablement (James Takahashi) [682351]
- [misc] enclosure: return ERR_PTR() on error (James Takahashi) [682351]
- [misc] enclosure: fix oops while iterating enclosure_status array (James Takahashi) [682351]
- [scsi] ses: fix VPD inquiry overrun (James Takahashi) [682351]
- [scsi] ses: Fix timeout (James Takahashi) [682351]
- [scsi] ses: fix data corruption (James Takahashi) [682351]
- [scsi] ses: fix memory leaks (James Takahashi) [682351]
- [scsi] ses: add new Enclosure ULD (James Takahashi) [682351]
- [misc] enclosure: add support for enclosure services (James Takahashi) [682351]
- [net] tg3: Include support for Broadcom 5719/5720 (John Feeney) [654956 696182 707299]
- [misc] module: remove over-zealous check in __module_get() (Jon Masters) [616125]
- [redhat] kabi: Add pci_ioremap_bar and pci_reset_function to kABI (Jon Masters) [677683]
- [redhat] kabi: Add dm_put to kABI (Jon Masters) [707003]
- [redhat] kabi: Add compat_alloc_user_space to kABI (Jon Masters) [703167]
- [redhat] kabi: Add random32 and srandom32 to kABI (Jon Masters) [668815]
- [redhat] kabi: Add cancel_work_sync to kABI (Jon Masters) [664991]
- [net] bna: add r suffix to the driver version (Ivan Vecera) [709951]
- [net] bna: fix for clean fw re-initialization (Ivan Vecera) [709951]
- [net] bna: fix memory leak during RX path cleanup (Ivan Vecera) [709951]
- [net] bridge: Disable multicast snooping by default (Herbert Xu) [506630]
- [net] bonding: fix block_netpoll_tx imbalance (Andy Gospodarek) [704426]
- [scsi] qla2xxx: Fix virtual port login failure after chip reset (Chad Dupuis) [703879]
- [scsi] qla2xxx: fix dsd_list_len for dsd_chaining in cmd type 6 (Chad Dupuis) [703879]
- [net] force new skbs to allocate a minimum of 16 frags (Amerigo Wang) [694308]
- [pci] intel-iommu: Flush unmaps at domain_exit (Alex Williamson) [705455]
- [pci] intel-iommu: Only unlink device domains from iommu (Alex Williamson) [705455]

* Tue May 31 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-265.el5]
- [scsi] be2iscsi: Fix MSIX interrupt names (Prarit Bhargava) [704735]
- [misc] signal: fix SIGPROF keeps large task from completing fork (Oleg Nesterov) [645528]
- [fs] gfs2: fix processes waiting on already-available inode glock (Robert S Peterson) [694669]
- Revert: [pci] msi: remove infiniband compat code (Prarit Bhargava) [636260]
- Revert: [pci] msi: use msi_desc save areas in drivers/pci code (Prarit Bhargava) [636260]
- Revert: [pci] msi: use msi_desc save areas in msi state functions (Prarit Bhargava) [636260]
- Revert: [pci] msi: remove pci_save_msi|x_state() functions (Prarit Bhargava) [636260]
- [s390] mm: diagnose 10 does not release memory above 2GB (Hendrik Brueckner) [701275]
- [input] evdev: implement proper locking (Marc Milgram) [680561]
- [input] evdev: rename list to client in handlers (Marc Milgram) [680561]
- [net] netpoll: disable netpoll when enslave a device (Amerigo Wang) [698873]
- [net] disable lro on phys device when dev is a vlan (Neil Horman) [696374]
- [scsi] qla2xxx: Update version number to 8.03.07.03.05.07-k (Chad Dupuis) [686462]
- [scsi] qla2xxx: Free firmware PCB on logout request (Chad Dupuis) [686462]
- [scsi] qla2xxx: dump registers for more info about ISP82xx errors (Chad Dupuis) [686462]
- [scsi] qla2xxx: Updated the reset sequence for ISP82xx (Chad Dupuis) [686462]
- [scsi] qla2xxx: Update copyright banner (Chad Dupuis) [686462]
- [scsi] qla2xxx: Perform FCoE context reset before adapter reset (Chad Dupuis) [686462]
- [scsi] qla2xxx: Limit logs in case device state does not change (Chad Dupuis) [686462]
- [scsi] qla2xxx: Abort pending commands for faster reset recovery (Chad Dupuis) [686462]
- [scsi] qla2xxx: Check for match before setting FCP-priority info (Chad Dupuis) [686462]
- [scsi] qla2xxx: Display PortID info during FCP command-status (Chad Dupuis) [686462]

* Tue May 24 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-264.el5]
- [misc] Introduce pci_map_biosrom, kernel-xen variant (David Milburn) [651837]

* Mon May 23 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-263.el5]
- [misc] vsyscall: remove code changing syscall instructions to nop (Ulrich Obergfell) [689546]
- [scsi] mpt2sas: move fault event handling into process context (Tomas Henzl) [705398]
- [scsi] ibmvscsi: Improve CRQ reset reliability (Steve Best) [704963]
- [infiniband] cxgb4: Reset wait condition atomically (Steve Best) [703925]
- [infiniband] cxgb4: fix driver hang on EEH error (Steve Best) [703925]
- [fs] xfs: serialise unaligned direct IOs (Eric Sandeen) [689830]
- [fs] ext4: serialize unaligned asynchronous DIO (Eric Sandeen) [689830]
- [misc] Add printk_timed_ratelimit (Eric Sandeen) [689830]
- [fs] set stat's st_blksize to fs blocksize not page size (Eric Sandeen) [695168]
- [pci] Disable PCI MSI/X on portable hardware (Prarit Bhargava) [703340]
- [usb] ehci: Disable disconnect/connect wakeups (Matthew Garrett) [703344]
- [fs] cifs: fix cifsConvertToUCS for the mapchars case (Jeff Layton) [705324]
- [fs] nfs: set d_op on newly allocated dentries in nfs_rename (Jeff Layton) [702533]
- [fs] nfs: Fix build break with CONFIG_NFS_V4=n (Harshula Jayasuriya) [702355]
- [scsi] isci: enable building driver (David Milburn) [651837]
- [scsi] libsas: flush initial device discovery before completing (David Milburn) [651837]
- [scsi] libsas: fix up device gone notification in sas_deform_port (David Milburn) [651837]
- [scsi] libsas: fix runaway error handler problem (David Milburn) [651837]
- [scsi] isci: validate oem parameters early, and fallback (David Milburn) [651837]
- [scsi] isci: fix oem parameter header definition (David Milburn) [651837]
- [scsi] isci: fix fragile/conditional isci_host lookups (David Milburn) [651837]
- [scsi] isci: cleanup isci_remote_device[_not]_ready interface (David Milburn) [651837]
- [scsi] isci: Qualify when lock managed for STP/SATA callbacks (David Milburn) [651837]
- [scsi] isci: Fix use of SATA soft reset state machine (David Milburn) [651837]
- [scsi] isci: Free lock for abort escalation at submit time (David Milburn) [651837]
- [scsi] isci: Properly handle requests in aborting state (David Milburn) [651837]
- [scsi] isci: Remove screaming data types (David Milburn) [651837]
- [scsi] isci: remove unused remote_device_started (David Milburn) [651837]
- [scsi] isci: namespacecheck cleanups (David Milburn) [651837]
- [scsi] isci: kill some long macros (David Milburn) [651837]
- [scsi] isci: reorder init to cleanup unneeded declarations (David Milburn) [651837]
- [scsi] isci: Remove event_* calls as they are just wrappers (David Milburn) [651837]
- [scsi] isci: fix apc mode definition (David Milburn) [651837]
- [scsi] isci: Revert task gating change handled by libsas (David Milburn) [651837]
- [scsi] isci: reset hardware at init (David Milburn) [651837]
- [scsi] isci: Revert unneeded error path fixes (David Milburn) [651837]
- [scsi] isci: misc fixes (David Milburn) [651837]
- [scsi] isci: add firmware support (David Milburn) [651837]
- [scsi] isci: lldd support (David Milburn) [651837]
- [scsi] isci: add core common definitions and utility functions (David Milburn) [651837]
- [scsi] isci: add core base state machine and memory descriptors (David Milburn) [651837]
- [scsi] isci: add core unsolicited frame handling and registers (David Milburn) [651837]
- [scsi] isci: add core request support (David Milburn) [651837]
- [scsi] isci: add core stp support (David Milburn) [651837]
- [scsi] isci: add core remote node context support (David Milburn) [651837]
- [scsi] isci: add core remote device support (David Milburn) [651837]
- [scsi] isci: add core port support (David Milburn) [651837]
- [scsi] isci: add core phy support (David Milburn) [651837]
- [scsi] isci: add core controller support (David Milburn) [651837]
- [scsi] isci: BZ 651837 Introduce pci_map_biosrom() (David Milburn) [651837]
- [scsi] qla4xxx: update version to V5.02.04.00.05.07-d0 (Chad Dupuis) [660388]
- [scsi] qla4xxx: set status_srb NULL if sense_len is 0 (Chad Dupuis) [660388]
- [scsi] qla4xxx: Initialize host fw_ddb_index_map list (Chad Dupuis) [660388]
- [scsi] qla4xxx: reuse qla4xxx_mailbox_premature_completion (Chad Dupuis) [660388]
- [scsi] qla4xxx: check for all reset flags (Chad Dupuis) [660388]
- [scsi] qla4xxx: added new function qla4xxx_relogin_all_devices (Chad Dupuis) [660388]
- [scsi] qla4xxx: add support for ql4xkeepalive module parameter (Chad Dupuis) [660388]
- [scsi] qla4xxx: Add support for ql4xmaxqdepth module parameter (Chad Dupuis) [660388]
- [scsi] qla4xxx: skip core clock so firmware can increase clock (Chad Dupuis) [660388]
- [scsi] qla4xxx: copy ipv4 opts and address state to host struct (Chad Dupuis) [660388]
- [scsi] qla4xxx: check AF_FW_RECOVERY flag for 8022 adapter only (Chad Dupuis) [660388]
- [scsi] qla4xxx: Change hard coded values to macros (Chad Dupuis) [660388]
- [scsi] qla4xxx: Change hard coded value of Sense buffer (Chad Dupuis) [660388]
- [scsi] qla4xxx: Remove stale references to ISP3031 and NetXen (Chad Dupuis) [660388]
- [scsi] qla4xxx: Correct file header for iscsi (Chad Dupuis) [660388]
- [scsi] qla4xxx: Add scsi_{,un}block_request while reading flash (Chad Dupuis) [660388]
- [scsi] qla4xxx: Remove unused code from qla4xxx_send_tgts (Chad Dupuis) [660388]
- [scsi] qla4xxx: Add proper locking around cmd->host_scribble (Chad Dupuis) [660388]
- [scsi] qla4xxx: use return status DID_TRANSPORT_DISRUPTED (Chad Dupuis) [660388]
- [scsi] qla4xxx: remove unused functions and struct parameters (Chad Dupuis) [660388]
- [scsi] qla4xxx: change char string to static char (Chad Dupuis) [660388]
- [scsi] qla4xxx: change spin_lock to spin_lock_irqsave (Chad Dupuis) [660388]
- [scsi] qla4xxx: change hard coded value to a macro (Chad Dupuis) [660388]
- [scsi] qla4xxx: move qla4xxx_free_ddb_list and scsi_remove_host (Chad Dupuis) [660388]
- [scsi] qla4xxx: get status from initialize_adapter (Chad Dupuis) [660388]
- [scsi] qla4xxx: remove extra pci_disable_device call (Chad Dupuis) [660388]
- [scsi] qla4xxx: Remove unused argument from function prototype (Chad Dupuis) [660388]
- [scsi] qla4xxx: call qla4xxx_mark_all_devices_missing (Chad Dupuis) [660388]
- [scsi] qla4xxx: call scsi_scan_target only if AF_ONLINE set (Chad Dupuis) [660388]
- [scsi] qla4xxx: call scsi_block_request before clearing AF_ONLINE (Chad Dupuis) [660388]
- [scsi] qla4xxx: Add timer debug print (Chad Dupuis) [660388]
- [scsi] qla4xxx: use iscsi class session state check ready (Chad Dupuis) [660388]
- [scsi] qla4xxx: set device state missing only if non-dead state (Chad Dupuis) [660388]
- [scsi] libiscsi: fix shutdown (Chad Dupuis) [660388]
- [scsi] qla4xxx: Change function prototype to static (Chad Dupuis) [660388]
- [scsi] qla4xxx: Fix panic while loading with corrupted 4032 card (Chad Dupuis) [660388]
- [scsi] qla4xxx: no other port reinit during remove_adapter (Chad Dupuis) [660388]
- [scsi] qla4xxx: unblock iscsi session before scsi_scan_target (Chad Dupuis) [660388]
- [scsi] qla4xxx: Fix for dropping of AENs during init time (Chad Dupuis) [660388]
- [scsi] qla4xxx: Free allocated memory only once (Chad Dupuis) [660388]
- [scsi] qla4xxx: ignore existing interrupt during mailbox command (Chad Dupuis) [660388]
- [scsi] qla4xxx: Check connection active before unblocking session (Chad Dupuis) [660388]
- [scsi] qla4xxx: Poll for Disable Interrupt Mailbox Completion (Chad Dupuis) [660388]
- [scsi] qla4xxx: fix request_irq to avoid spurious interrupts (Chad Dupuis) [660388]
- [net] bridge: make bridge address settings sticky (Amerigo Wang) [705997]
- [net] bridge: allow changing hardware addr to any valid address (Amerigo Wang) [705997]
- [xen] hvm: build guest timers on monotonic system time (Paolo Bonzini) [705725]
- [xen] hvm: explicitly use the TSC as the base for the hpet (Paolo Bonzini) [705725]
- [xen] x86: allow Dom0 to drive PC speaker (Igor Mammedov) [501314]
- [xen] vtd: Fix resource leaks on error paths in intremap code (Igor Mammedov) [704497]

* Mon May 16 2011 Jiri Pirko <jpirko@redhat.com> [2.6.18-262.el5]
- [block] cciss: reading a write only register causes a hang (Tomas Henzl) [696153]

* Thu May 12 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-261.el5]
- [message] mptfusion: inline data padding support for TAPE drives (Tomas Henzl) [698073]
- [powerpc] fix VDSO gettimeofday called with NULL struct timeval (Steve Best) [700203]
- [fs] gfs2: fix resource group bitmap corruption (Robert S Peterson) [690555]
- [fs] gfs2: Add dlm callback owed glock flag (Robert S Peterson) [703213]
- [net] cxgb4: fix some backport bugs (Neil Horman) [700947]
- [scsi] fnic: fix stats memory leak (Mike Christie) [688459]
- [block]: fix missing bio back/front segment size setting (Milan Broz) [700546]
- [net] mlx4: Add CX3 PCI IDs (Jay Fenlason) [660671]
- [pci] SRIOV: release VF BAR resources when device is hot unplug (Don Dutile) [698879]
- [virtio] virtio_ring: Decrement avail idx on buffer detach (Amit Shah) [699426]
- [virtio] virtio_pci: fix double-free of pci regions on unplug (Amit Shah) [701918]
- Revert: [virtio] console: no device_destroy on port device (Amit Shah) [701918]
- [xen] hvm: provide param to disable HPET in HVM guests (Paolo Bonzini) [702652]
- [xen] vtd: Free unused interrupt remapping table entry (Don Dugger) [571410]

* Fri May 06 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-260.el5]
- [scsi] mpt2sas: prevent heap overflows and unchecked access (Tomas Henzl) [694527] {CVE-2011-1494 CVE-2011-1495}
- [block] cciss: fix export resettable host attribute fix (Tomas Henzl) [690511]
- [fs] gfs2: Tag all metadata with jid of last node to change it (Steven Whitehouse) [701577]
- [fs] nfsd: permit unauthenticated stat of export root (Steve Dickson) [491740]
- [net] myri10ge: add dynamic LRO disabling (Stanislaw Gruszka) [688897]
- [wireless] ath5k: disable ASPM L0s for all cards (Stanislaw Gruszka) [666866]
- [net] igb: work-around for 82576 EEPROMs reporting invalid size (Stefan Assmann) [693934]
- [pci] aerdrv: use correct bits and add delay to aer_root_reset (Stefan Assmann) [700386]
- [fs] jbd: fix write_metadata_buffer and get_write_access race (Eric Sandeen) [494927 696843]
- [x86_64] Disable Advanced RAS/MCE on newer Intel processors (Prarit Bhargava) [697508]
- [x86_64] vdso: fix gettimeofday segfault when tv == NULL (Prarit Bhargava) [700782]
- [x86_64] Ignore spurious IPIs left over from crash kernel (Myron Stowe) [692921]
- [i386] Ignore spurious IPIs left over from crash kernel (Myron Stowe) [692921]
- [scsi] iscsi_tcp: fix iscsi's sk_user_data access (Mike Christie) [677703]
- [edac] i7core_edac: return -ENODEV if no MC is found (Mauro Carvalho Chehab) [658418]
- [char] vcs: hook sysfs devices to object lifetime (Mauro Carvalho Chehab) [622542]
- [char] vt_ioctl: fix VT ioctl race (Mauro Carvalho Chehab) [622542]
- [fs] avoid vmalloc space error opening many files on x86 (Larry Woodman) [681586]
- [fs] nfs: Tighten up the attribute update code (Jeff Layton) [672981]
- [net] bna: Avoid kernel panic in case of FW heartbeat failure (Ivan Vecera) [700488]
- [net] benet: increment work_counter in be_worker (Ivan Vecera) [695197]
- [net] benet: be_poll_tx_mcc_compat should always return zero (Ivan Vecera) [690755]
- [net] benet: Fix be_get_stats_count return value (Ivan Vecera) [690755]
- [net] tcp: Fix tcp_prequeue to get correct rto_min value (Herbert Xu) [696411]
- [net] bonding: unshare skbs prior to calling pskb_may_pull (Andy Gospodarek) [607114]
- [misc] x86: Sync CPU feature flag additions from Xen (Frank Arnold) [687994]
- [misc] mark various drivers/features as tech preview (Don Zickus) [701722]
- [hwmon] i5k_amb: Fix compile warning (Dean Nelson) [603345]
- [hwmon] i5k_amb: Load automatically on all 5000/5400 chipsets (Dean Nelson) [603345]
- [hwmon] i5k_amb: provide labels for temperature sensors (Dean Nelson) [603345]
- [hwmod] i5k_amb: support Intel 5400 chipset (Dean Nelson) [603345]
- [net] bridge/netfilter: fix ebtables information leak (Don Howard) [681326] {CVE-2011-1080}
- [net] bluetooth: fix sco information leak to userspace (Don Howard) [681311] {CVE-2011-1078}
- [fs] gfs2: make sure fallocate bytes is a multiple of blksize (Benjamin Marzinski) [699741]
- [fs] fix corrupted GUID partition table kernel oops (Jerome Marchand) [695980] {CVE-2011-1577}
- [xen] x86: Enable K8 NOPS for future AMD CPU Families (Frank Arnold) [687994]
- [xen] x86: Blacklist new AMD CPUID bits for PV domains (Frank Arnold) [687994]
- [xen] x86: Handle new AMD CPUID bits for HVM guests (Frank Arnold) [687994]
- [xen] x86: Update AMD CPU feature flags (Frank Arnold) [687994]
- [xen] x86/domain: fix error checks in arch_set_info_guest (Laszlo Ersek) [688582] {CVE-2011-1166}

* Thu Apr 28 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-259.el5]
- [net] bridge: fix initial packet flood if !STP (Jiri Pirko) [695369]
- [edac] amd64_edac: Fix potential memleak (Mauro Carvalho Chehab) [610235]
- [edac] amd64_edac, amd64_mce: Revert printk changes (Mauro Carvalho Chehab) [610235]
- [x86] amd: Fix init_amd build warnings (Frank Arnold) [610235]
- [edac] amd64_edac: Enable PCI dev detection on F15h (Frank Arnold) [610235]
- [edac] amd64_edac: Fix decode_syndrome types (Frank Arnold) [610235]
- [edac] amd64_edac: Fix DCT argument type (Frank Arnold) [610235]
- [edac] amd64_edac: Fix ranges signedness (Frank Arnold) [610235]
- [edac] amd64_edac: Drop local variable (Frank Arnold) [610235]
- [edac] amd64_edac: Fix PCI config addressing types (Frank Arnold) [610235]
- [edac] amd64_edac: Fix DRAM base macros (Frank Arnold) [610235]
- [edac] amd64_edac: Fix node id signedness (Frank Arnold) [610235]
- [edac] amd64_edac: Enable driver on F15h (Frank Arnold) [610235]
- [edac] amd64_edac: Adjust ECC symbol size to F15h (Frank Arnold) [610235]
- [edac] amd64_edac: Improve DRAM address mapping (Frank Arnold) [610235]
- [edac] amd64_edac: Sanitize ->read_dram_ctl_register (Frank Arnold) [610235]
- [edac] amd64_edac: fix up chip select conversion routine to F15h (Frank Arnold) [610235]
- [edac] amd64_edac: Beef up early exit reporting (Frank Arnold) [610235]
- [edac] amd64_edac: Revamp online spare handling (Frank Arnold) [610235]
- [edac] amd64_edac: Fix channel interleave removal (Frank Arnold) [610235]
- [edac] amd64_edac: Correct node interleaving removal (Frank Arnold) [610235]
- [edac] amd64_edac: Add support for interleaved region swapping (Frank Arnold) [610235]
- [edac] amd64_edac: Unify get_error_address (Frank Arnold) [610235]
- [edac] amd64_edac: Simplify decoding path (Frank Arnold) [610235]
- [edac] amd64_edac: Adjust channel counting to F15h (Frank Arnold) [610235]
- [edac] amd64_edac: Cleanup old defines cruft (Frank Arnold) [610235]
- [edac] amd64_edac: Cleanup NBSH cruft (Frank Arnold) [610235]
- [edac] amd64_edac: Cleanup NBCFG handling (Frank Arnold) [610235]
- [edac] amd64_edac: Cleanup NBCTL code (Frank Arnold) [610235]
- [edac] amd64_edac: Cleanup DCT Select Low/High code (Frank Arnold) [610235]
- [edac] amd64_edac: Cleanup Dram Configuration registers handling (Frank Arnold) [610235]
- [edac] amd64_edac: Cleanup DBAM handling (Frank Arnold) [610235]
- [edac] amd64_edac: Replace huge bitmasks with a macro (Frank Arnold) [610235]
- [edac] amd64_edac: Sanitize f10_get_base_addr_offset (Frank Arnold) [610235]
- [edac] amd64_edac: Sanitize channel extraction (Frank Arnold) [610235]
- [edac] amd64_edac: Cleanup chipselect handling (Frank Arnold) [610235]
- [edac] amd64_edac: Cleanup DHAR handling (Frank Arnold) [610235]
- [edac] amd64_edac: Remove DRAM base/limit subfields caching (Frank Arnold) [610235]
- [edac] amd64_edac: Add support for F15h DCT PCI config accesses (Frank Arnold) [610235]
- [edac] amd64_edac: Fix DIMMs per DCTs output (Frank Arnold) [610235]
- [edac] amd64_edac: Remove two-stage initialization (Frank Arnold) [610235]
- [edac] amd64_edac: Check ECC capabilities initially (Frank Arnold) [610235]
- [edac] amd64_edac: Carve out ECC-related hw settings (Frank Arnold) [610235]
- [edac] amd64_edac: Allocate driver instances dynamically (Frank Arnold) [610235]
- [edac] amd64_edac: Rework printk macros (Frank Arnold) [610235]
- [edac] amd64_edac: Rename CPU PCI devices (Frank Arnold) [610235]
- [edac] amd64_edac: Concentrate per-family init even more (Frank Arnold) [610235]
- [edac] amd64_edac: Cleanup the CPU PCI device reservation (Frank Arnold) [610235]
- [edac] amd64_edac: Add per-family init function (Frank Arnold) [610235]
- [edac] amd64_edac: Remove F11h support (Frank Arnold) [610235]
- [edac] amd64_edac: Fix interleaving check (Frank Arnold) [610235]
- [edac] amd64_edac: Fix DCT base address selector (Frank Arnold) [610235]
- [edac] amd64_edac: Sanitize syndrome extraction (Frank Arnold) [610235]
- [edac] amd64_edac: fix forcing module load/unload (Frank Arnold) [610235]
- [edac] amd64_edac: add memory types strings for debugging (Frank Arnold) [610235]
- [edac] amd64_edac: remove unneeded extract_error_address wrapper (Frank Arnold) [610235]
- [edac] amd64_edac: rename StinkyIdentifier (Frank Arnold) [610235]
- [edac] amd64_edac: remove superfluous dbg printk (Frank Arnold) [610235]
- [edac] amd64_edac: cleanup f10_early_channel_count (Frank Arnold) [610235]
- [edac] amd64_edac: dump DIMM sizes on K8 too (Frank Arnold) [610235]
- [edac] amd64_edac: cleanup rest of amd64_dump_misc_regs (Frank Arnold) [610235]
- [edac] amd64_edac: cleanup DRAM cfg low debug output (Frank Arnold) [610235]
- [edac] amd64_edac: wrap-up pci config read error handling (Frank Arnold) [610235]
- [edac] amd64_edac: make DRAM regions output more human-readable (Frank Arnold) [610235]
- [edac] amd64_edac: clarify DRAM CTL debug reporting (Frank Arnold) [610235]
- [edac] mce_amd: Fix NB error formatting (Frank Arnold) [659693]
- [edac] mce_amd: Use BIT_64() to eliminate warnings on 32-bit (Frank Arnold) [659693]
- [edac] mce_amd: Enable MCE decoding on F15h (Frank Arnold) [659693]
- [edac] mce_amd: Shorten error report formatting (Frank Arnold) [659693]
- [edac] mce_amd: Overhaul error fields extraction macros (Frank Arnold) [659693]
- [edac] mce_amd: Add F15h FP MCE decoder (Frank Arnold) [659693]
- [edac] mce_amd: Add F15 EX MCE decoder (Frank Arnold) [659693]
- [edac] mce_amd: Add an F15h NB MCE decoder (Frank Arnold) [659693]
- [edac] mce_amd: No F15h LS MCE decoder (Frank Arnold) [659693]
- [edac] mce_amd: Add F15h CU MCE decoder (Frank Arnold) [659693]
- [edac] mce_amd: Add F15h IC MCE decoder (Frank Arnold) [659693]
- [edac] mce_amd: Add F15h DC MCE decoder (Frank Arnold) [659693]
- [edac] mce_amd: Select extended error code mask (Frank Arnold) [659693]
- [edac] mce_amd: Fix shift warning on 32-bit (Frank Arnold) [659693]
- [edac] mce_amd: Add a BIT_64() macro (Frank Arnold) [659693]
- [edac] mce_amd: Enable MCE decoding on F12h (Frank Arnold) [659693]
- [edac] mce_amd: Add F12h NB MCE decoder (Frank Arnold) [659693]
- [edac] mce_amd: Add F12h IC MCE decoder (Frank Arnold) [659693]
- [edac] mce_amd: Add F12h DC MCE decoder (Frank Arnold) [659693]
- [edac] mce_amd: Add support for F11h MCEs (Frank Arnold) [659693]
- [edac] mce_amd: Enable MCE decoding on F14h (Frank Arnold) [659693]
- [edac] mce_amd: Fix FR MCEs decoding (Frank Arnold) [659693]
- [edac] mce_amd: Complete NB MCE decoders (Frank Arnold) [659693]
- [edac] mce_amd: Warn about LS MCEs on F14h (Frank Arnold) [659693]
- [edac] mce_amd: Adjust IC decoders to F14h (Frank Arnold) [659693]
- [edac] mce_amd: Adjust DC decoders to F14h (Frank Arnold) [659693]
- [edac] mce_amd: Rename files (Frank Arnold) [659693]
- [edac] mce_amd: Pass complete MCE info to decoders (Frank Arnold) [659693]
- [edac] mce_amd: Sanitize error codes (Frank Arnold) [659693]
- [edac] mce_amd: Remove unused function parameter (Frank Arnold) [659693]
- [edac] mce_amd: Do not report error overflow as a separate error (Frank Arnold) [659693]
- [edac] mce_amd: Limit MCE decoding to current families for now (Frank Arnold) [659693]
- [edac] mce_amd: Fix wrong mask and macro usage (Frank Arnold) [659693]
- [edac] mce_amd: Filter out invalid values (Frank Arnold) [659693]
- [edac] mce_amd: silence GART TLB errors (Frank Arnold) [659693]
- [edac] mce_amd: correct corenum reporting (Frank Arnold) [659693]
- [edac] mce_amd: update AMD F10h revD check (Frank Arnold) [659693]
- [edac] mce_amd: Use an atomic notifier for MCEs decoding (Frank Arnold) [659693]
- [edac] mce_amd: carve out AMD MCE decoding logic (Frank Arnold) [659693]
- [edac] mce_amd: Fix MCE decoding callback logic (Frank Arnold) [659693]

* Tue Apr 26 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-258.el5]
- [block] cciss: fix lost command problem (Tomas Henzl) [696153]
- [block] cciss: export resettable host attribute (Tomas Henzl) [690511]
- [powerpc] mm/numa: Disable VPNH feature on pseries (Steve Best) [696328]
- [wireless] iwlagn: re-enable MSI on resume (Prarit Bhargava) [694672]
- [fs] cifs: clean up various nits in unicode routines (Jeff Layton) [659715]
- [fs] cifs: fix unaligned accesses in cifsConvertToUCS (Jeff Layton) [659715]
- [fs] cifs: clean up unaligned accesses in cifs_unicode.c (Jeff Layton) [659715]
- [fs] cifs: fix unaligned access in check2ndT2 and coalesce_t2 (Jeff Layton) [659715]
- [fs] cifs: clean up unaligned accesses in validate_t2 (Jeff Layton) [659715]
- [fs] cifs: use get/put_unaligned functions to access ByteCount (Jeff Layton) [659715]
- [net] bridge: fix build warning in br_device (Jarod Wilson) [556811]
- [scsi] arcmsr: fix broken CONFIG_XEN conditional (Jarod Wilson) [635992]
- [net] cxgb4: clean up dma_mapping_error usage (Jarod Wilson) [567446]
- [fs] dcache: Close a race-opportunity in d_splice_alias (David Howells) [646359]
- [md] dm-crypt: support more encryption modes (Milan Broz) [660368]
- [crypto] add XTS blockcipher mode support (Danny Feng) [553411]
- [s390] dasd: fix race between open and offline (Hendrik Brueckner) [695357]
- [net] netxen: limit skb frags for non tso packet (Chad Dupuis) [672368]
- [net] qlcnic: limit skb frags for non tso packet (Bob Picco) [695490]

* Fri Apr 15 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-257.el5]
- [char] ipmi: don't poll non-existant IPMI Event Message Buffer (Tony Camuso) [578913]
- [char] ipmi: fix platform return check (Tony Camuso) [578913]
- [fs] gfs: Never try to deallocate an inode on a read-only mount (Steven Whitehouse) [689943]
- [infiniband] cxgb4: Initial import of driver to RHEL5 (Steve Best) [567449]
- [net] cxgb4: Initial import of driver to RHEL5 (Neil Horman) [567446]
- [net] bond: fix link up after restart (Neil Horman) [659558]
- [infiniband] cxgb3: Don't free skbs on NET_XMIT_* from LLD (Neil Horman) [516956]
- [infiniband] cxgb3: Wait 1+ schedule cycle during device removal (Neil Horman) [516956]
- [infiniband] cxgb3: Mark device with CXIO_ERROR_FATAL on remove (Neil Horman) [516956]
- [infiniband] cxgb3: Don't allocate the SW queue for user mode CQs (Neil Horman) [516956]
- [infiniband] cxgb3: Increase the max CQ depth (Neil Horman) [516956]
- [infiniband] cxgb3: Doorbell overflow avoidance and recovery (Neil Horman) [516956]
- [infiniband] cxgb3: Remove BUG_ON() on CQ rearm failure (Neil Horman) [516956]
- [infiniband] cxgb3: Fix error paths in post_send and post_recv (Neil Horman) [516956]
- [infiniband] cxgb3: Handle NULL inetdev ptr in iwch_query_port (Neil Horman) [516956]
- [infiniband] cxgb3: Clean up properly on FW mismatch failures (Neil Horman) [516956]
- [infiniband] cxgb3: Don't ignore insert_handle() failures (Neil Horman) [516956]
- [infiniband] cxgb3: Wake up any waiters on peer close/abort (Neil Horman) [516956]
- [infiniband] cxgb3: Don't free endpoints early (Neil Horman) [516956]
- [net] cxgb3: Handle port events properly (Mike Christie) [516956]
- [fs] cifs: prevent infinite recursion in cifs_reconnect_tcon (Jeff Layton) [667454]
- [fs] cifs: consolidate reconnect logic in smb_init routines (Jeff Layton) [667454]
- [fs] dcache: allow __d_obtain_alias to return unhashed dentries (J. Bruce Fields) [613736]

* Thu Apr 07 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-256.el5]
- [scsi] mpt2sas: fix _scsih_is_raid test in _scsih_qcmd (Tomas Henzl) [683806]
- [scsi] megaraid_sas: add a reset_devices condition (Tomas Henzl) [692099]
- [net] add socket API recvmmsg, receive multiple messages (Thomas Graf) [582653]
- [scsi] device_handler: fix ref counting in error path (Mike Snitzer) [645343]
- [scsi] device_handler: propagate SCSI device deletion (Mike Snitzer) [645343]
- [net] 8021q: fix VLAN RX stats counting (Stefan Assmann) [579858]
- [x86_64] vdso: Fix typo in vclock_gettime code (Prarit Bhargava) [691735]
- [firmware] dmi_scan: Display system information in dmesg (Prarit Bhargava) [692860]
- [fs] debugfs: Implement debugfs_remove_recursive (Neil Horman) [692946]
- [redhat] configs: enable building CXGB4_ISCSI (Mike Christie) [567452]
- [scsi] cxgbi: get rid of gl_skb in cxgbi_ddp_info (Mike Christie) [567452]
- [scsi] cxgbi: set ulpmode only if digest is on (Mike Christie) [567452]
- [scsi] cxgb4i: ignore informational act-open-rpl message (Mike Christie) [567452]
- [scsi] cxgb4i: connection and ddp setting update (Mike Christie) [567452]
- [scsi] cxgb3i: fixed connection over vlan (Mike Christie) [567452]
- [scsi] libcxgbi: pdu read fixes (Mike Christie) [567452]
- [scsi] cxgbi: rename alloc_cpl to alloc_wr (Mike Christie) [567452]
- [scsi] cxgb3i: change cxgb3i to use libcxgbi (Mike Christie) [567452]
- [scsi] cxgbi: add cxgb4i iscsi driver (Mike Christie) [567452]
- [net] bonding: re-read speed and duplex when interface goes up (Andy Gospodarek) [677902]
- [net] ipv4/tcp_timer: honor sysctl tcp_syn_retries (Flavio Leitner) [688989]
- [usb] fix usbfs isochronous data transfer regression (Don Zickus) [688926]
- [fs] partitions: Fix corrupted OSF partition table parsing (Danny Feng) [688023]
- [misc] add param to change default coredump_filter setup (Dave Anderson) [488840]
- Revert: [md] dm-crypt: support more encryption modes (Jarod Wilson) [660368]
- [xen] allow delivery of timer interrupts to VCPU != 0 (Paolo Bonzini) [418501]
- [xen] x86/hvm: Enable delivering 8259 interrupts to VCPUs != 0 (Paolo Bonzini) [418501]
- [xen] get rid of the vcpu state in HPET (Paolo Bonzini) [418501]
- [xen] add accessors for arch/x86/hvm/hpet.c (Paolo Bonzini) [418501]

* Fri Apr 01 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-255.el5]
- [net] htb: Make HTB scheduler work with TSO (Thomas Graf) [481546]
- [fs] cifs: map NT_STATUS_ERROR_WRITE_PROTECTED to -EROFS (Jeff Layton) [516102]
- [pci] Ensure devices are resumed on system resume (Matthew Garrett) [644440]
- [fs] ext2, ext3: copy i_flags to inode flags on write (Eric Sandeen) [431738]
- [fs] gfs2: fix filesystem hang caused by incorrect lock order (Robert S Peterson) [656032]
- [fs] gfs2: restructure reclaiming of unlinked dinodes (Robert S Peterson) [656032]
- [fs] gfs2: unlock on gfs2_trans_begin error (Robert S Peterson) [656032]
- [pci] Add HP BL620c G7 to pci=bfsort whitelist (Prarit Bhargava) [680946]
- [pci] msi: simplify the msi irq limit policy (Prarit Bhargava) [652799]
- [scsi] scsi_dh: allow scsi_dh_detach to detach when attached (Mike Christie) [666304]
- [net] bonding: fix test for presence of VLANs (Jiri Pirko) [654878]
- [net] 8021q: VLAN 0 should be treated as no vlan tag (Jiri Pirko) [654878]
- [kernel] module: add sysctl to block module loading (Jerome Marchand) [645221]
- [fs] nfs: Make close(2) async when closing O_DIRECT files (Jeff Layton) [626977]
- [fs] nfs: Optimise NFS close() (Jeff Layton) [626977]
- [fs] nfs: Fix nfsv4 atomic open for execute... (Jeff Layton) [626977]
- [misc] pm: add comment explaining is_registered kabi work-around (Don Zickus) [637930]
- [misc] sunrpc: only call get_seconds once in sunrpc_invalidate (David Howells) [589512]

* Wed Mar 30 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-254.el5]
- [scsi] mpt2sas: Added customer specific display support (Tomas Henzl) [684842]
- [scsi] mpt2sas: Add support for WarpDrive SSS-6200 (Tomas Henzl) [683806]
- [scsi] megaraid: update driver to v5.34 (Tomas Henzl) [660728]
- [scsi] arcmsr: driver update for RHEL5.7 (Tomas Henzl) [635992]
- [scsi] scsi_dh_alua: add scalable ONTAP lun to dev list (Mike Snitzer) [667660]
- [pci] Enable pci=bfsort by default on future Dell systems (Shyam Iyer) [689047]
- [net] enic: update driver to 2.1.1.9 (Stefan Assmann) [661306]
- [scsi] bfa: rebase for RHEL5.7 to current scsi-misc version (Rob Evers) [660545]
- [pci] Enable PCI bus rescan for PPC64 only (Prarit Bhargava) [683461]
- [net] enable VLAN SG on additional drivers (Paolo Bonzini) [668934]
- [net] add ethtool -k sg off support for vlans (Paolo Bonzini) [668934]
- [net] explicitly enable VLAN SG when already in use (Paolo Bonzini) [668934]
- [net] enable SG on vlan devices if supported on the NIC (Paolo Bonzini) [668934]
- [net] fix NETIF_F_GSO_MASK to exclude VLAN features (Paolo Bonzini) [668934]
- [ata] ata_piix: honor ide=disable (Paolo Bonzini) [460821]
- [scsi] be2iscsi: update driver version string (Mike Christie) [691899]
- [scsi] be2iscsi: fix null ptr when accessing task hdr (Mike Christie) [660392]
- [scsi] be2iscsi: fix gfp use in alloc_pdu (Mike Christie) [660392]
- [scsi] be2iscsi: allow more time for FW to respond (Mike Christie) [660392]
- [net] ixgbe: restore erratum 45 fix and whitespace (Andy Gospodarek) [568312 568557 570366 571254 651467 653236 653359 653469 655022]
- [usb] ehci: AMD periodic frame list table quirk (Don Zickus) [651333]
- [scsi] qla2xxx: Upgrade 24xx and 25xx firmware to 5.03.16 (Chad Dupuis) [682305]
- [fs] nfsd: fix auth_domain reference leak on nlm operations (J. Bruce Fields) [589512]
- [net] sunrpc: ensure cache_check caller sees updated entry (J. Bruce Fields) [589512]
- [net] sunrpc: take lock on turning entry NEGATIVE in cache_check (J. Bruce Fields) [589512]
- [net] sunrpc: move cache validity check into helper function (J. Bruce Fields) [589512]
- [net] sunrpc: modifying valid sunrpc cache entries is racy (J. Bruce Fields) [589512]
- [fs] nfs: extract some common sunrpc_cache code from nfsd (J. Bruce Fields) [589512]
- [pci] return correct value when writing to reset attribute (Alex Williamson) [689860]
- [pci] expose function reset capability in sysfs (Alex Williamson) [689860]

* Tue Mar 29 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-253.el5]
- [media] sn9c102: fix world-wirtable sysfs files (Don Howard) [679305]
- [scsi] scsi_dh_rdac: Add two new IBM devices to rdac_dev_list (Rob Evers) [691460]
- [misc] support for marking code as tech preview (Don Zickus) [645431]
- [misc] taint: Add taint padding (Don Zickus) [645431]
- [scsi] lpfc: Update version for 8.2.0.96 driver release (Rob Evers) [660396]
- [scsi] lpfc: Update version for 8.2.0.95 driver release (Rob Evers) [660396]
- [scsi] lpfc: Fix rrq cleanup for vport delete (Rob Evers) [660396]
- [scsi] lpfc: don't ignore lpfc_suppress_link_up on SLI-4 (Rob Evers) [660396]
- [scsi] lpfc: LOGO completion must invalidate both RPI and D_ID (Rob Evers) [660396]
- [scsi] lpfc: adds a comment (Rob Evers) [660396]
- [scsi] lpfc: Do not take lock when clearing rrq active (Rob Evers) [660396]
- [scsi] lpfc: Fix non-empty nodelist after sli3 driver remove (Rob Evers) [660396]
- [scsi] lpfc: Save IRQ level when taking host_lock in findnode_did (Rob Evers) [660396]
- [scsi] lpfc: Fixed hang in lpfc_get_scsi_buf_s4 (Rob Evers) [660396]
- [scsi] lpfc: Fix xri lookup for received rrq (Rob Evers) [660396]
- [scsi] lpfc: Fix setting of RRQ active for target aborted IOs (Rob Evers) [660396]
- [scsi] lpfc: Modified lpfc_delay_discovery implementation (Rob Evers) [660396]
- [scsi] lpfc: Fix bug with fc_vport symbolic_name not being generated (Rob Evers) [660396]
- [scsi] lpfc: Update lpfc for 8.2.0.94 driver release (Rob Evers) [660396]
- [scsi] lpfc: Fixed fdisc sent with invalid VPI (Rob Evers) [660396]
- [scsi] lpfc: warn if the link_speed is not supported by this adapter (Rob Evers) [660396]
- [scsi] lpfc: Fixed UE error on UCNA BE2 hba during reboot (Rob Evers) [660396]
- [scsi] lpfc: Update version for 8.2.0.93 driver release (Rob Evers) [660396]
- [scsi] lpfc: Added support for clean address bit (Rob Evers) [660396]
- [scsi] lpfc: Fixed XRI reuse issue (Rob Evers) [660396]
- [scsi] lpfc: Update version for 8.2.0.92 driver release (Rob Evers) [660396]
- [scsi] lpfc: Unreg login when PLOGI received from logged in port (Rob Evers) [660396]
- [scsi] lpfc: Fixed crashes for NULL vport dereference (Rob Evers) [660396]
- [scsi] lpfc: Update version for 8.2.0.91 driver release (Rob Evers) [660396]
- [scsi] lpfc: Fix for kmalloc failures in lpfc_workq_post_event (Rob Evers) [660396]
- [scsi] lpfc: Adjust lengths for sli4_config mailbox commands (Rob Evers) [660396]
- [scsi] lpfc: set parity and serr bits on after performing sli4 reset (Rob Evers) [660396]
- [scsi] lpfc: VPI for ALL ELS commands and alloc RPIs at node creation (Rob Evers) [660396]
- [scsi] lpfc: Correct bit-definitions in SLI4 data structures (Rob Evers) [660396]
- [scsi] lpfc: Update version for 8.2.0.90 driver release (Rob Evers) [660396]
- [scsi] lpfc: new SLI4 initialization procedures based on if_type (Rob Evers) [660396]
- [scsi] lpfc: Implement FC and SLI async event handlers (Rob Evers) [660396]
- [scsi] lpfc: Fix management command context setting (Rob Evers) [660396]
- [scsi] lpfc: Fix panic in __lpfc_sli_get_sglq (Rob Evers) [660396]
- [scsi] lpfc: Update version for 8.2.0.89 driver release (Rob Evers) [660396]
- [scsi] lpfc: Fix compiler warning (Rob Evers) [660396]
- [scsi] lpfc: Added support for ELS RRQ command (Rob Evers) [660396]
- [scsi] lpfc: Init VFI and VPI for physical port (Rob Evers) [660396]
- [scsi] lpfc: Update version for 8.2.0.88 driver release (Rob Evers) [660396]
- [scsi] lpfc: add READ_TOPOLOGY mailbox command and new speed definition (Rob Evers) [660396]
- [scsi] lpfc: Modified return status of unsupport ELS commands (Rob Evers) [660396]
- [scsi] lpfc: Implement doorbell register changes for new hardware (Rob Evers) [660396]
- [scsi] lpfc: Implement new SLI 4 SLI_INTF register definitions (Rob Evers) [660396]
- [scsi] lpfc: Add PCI ID definitions for new hardware support (Rob Evers) [660396]
- [scsi] lpfc: Add new SLI4 WQE support (Rob Evers) [660396]
- [net] myri10ge: update to 1.5.2 (Stanislaw Gruszka) [481629]
- [pci] make pcie_get_readrq visible in pci.h (Stanislaw Gruszka) [481629]
- [net] igb: AER fix recover from PCIe Uncorrectable Error (Stefan Assmann) [568211]
- [net] igb: driver update for RHEL5.7 (Stefan Assmann) [653238]
- [fs] quota: do not allow setting quota limits too high (Eric Sandeen) [594609]
- [fs] block: fix submit_bh discarding barrier flag on sync write (Lukas Czerner) [667673]
- [net] netfilter/ipt_CLUSTERIP: fix buffer overflow (Jiri Pirko) [689340]
- [net] netfilter: ip6_tables: fix infoleak to userspace (Jiri Pirko) [689349] {CVE-2011-1172}
- [net] netfilter/ip_tables: fix infoleak to userspace (Jiri Pirko) [689332] {CVE-2011-1171}
- [net] netfilter/arp_tables: fix infoleak to userspace (Jiri Pirko) [689323] {CVE-2011-1170}
- [sound] alsa: hda driver update for RHEL5.7 (Jaroslav Kysela) [688539]
- [sound] alsa: add snd-aloop driver (Jaroslav Kysela) [647094]
- [mmc] sdhci: Add support for O2Micro Card Reader (John Feeney) [659318]
- [base] Fix potential deadlock in driver core (Don Zickus) [637930]
- Revert: [crypto] add XTS blockcipher mode support (Jarod Wilson) [553411]

* Fri Mar 25 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-252.el5]
- [scsi] add new Dell Powervault controllers to RDAC device list (Shyam Iyer) [688981]
- [ata] ahci: AHCI mode for Intel Patsburg SATA RAID controller (David Milburn) [684361]
- [md] dm-crypt: support more encryption modes (Milan Broz) [660368]
- [crypto] add XTS blockcipher mode support (Danny Feng) [553411]
- [virt] hypervisor: Overflow fix for clocks > 4GHz (Zachary Amsden) [673242]
- [net] tg3: Restrict phy ioctl access (John Feeney) [660397]
- [net] tg3: Update version to 3.116 (John Feeney) [660397]
- [net] tg3: Minor EEE code tweaks (John Feeney) [660397]
- [net] tg3: Relax EEE thresholds (John Feeney) [660397]
- [net] tg3: Fix 57765 EEE support (John Feeney) [660397]
- [net] tg3: Move EEE definitions into mdio.h (John Feeney) [660397]
- [net] tg3: Enable phy APD for 5717 and later asic revs (John Feeney) [660397]
- [net] tg3: use dma_alloc_coherent() instead of pci_alloc_consistent() (John Feeney) [660397]
- [net] tg3: Reenable TSS for 5719 (John Feeney) [660397]
- [net] tg3: Enable mult rd DMA engine on 5719 (John Feeney) [660397]
- [net] tg3: Always turn on APE features in mac_mode reg (John Feeney) [660397]
- [net] tg3: Don't check for vlan group before vlan_tx_tag_present (John Feeney) [660397]
- [net] tg3: Update version to 3.115 (John Feeney) [660397]
- [net] tg3: Report invalid link from tg3_get_settings() (John Feeney) [660397]
- [net] tg3: Don't allocate jumbo ring for 5780 class devs (John Feeney) [660397]
- [net] tg3: Cleanup tg3_alloc_rx_skb() (John Feeney) [660397]
- [net] tg3: Add EEE support (John Feeney) [660397]
- [net] tg3: Add clause 45 register accessor methods (John Feeney) [660397]
- [net] tg3: Disable unused transmit rings (John Feeney) [660397]
- [net] tg3: Add support for selfboot format 1 v6 (John Feeney) [660397]
- [net] tg3: Update version to 3.114 (John Feeney) [660397]
- [net] tg3: Add extend rx ring sizes for 5717 and 5719 (John Feeney) [660397]
- [net] tg3: Prepare for larger rx ring sizes (John Feeney) [660397]
- [net] tg3: Futureproof the loopback test (John Feeney) [660397]
- [net] tg3: Cleanup missing VPD partno section (John Feeney) [660397]
- [net] tg3: Remove 5724 device ID (John Feeney) [660397]
- [net] tg3: return operator cleanup (John Feeney) [660397]
- [net] tg3: phy tmp variable roundup (John Feeney) [660397]
- [net] tg3: Dynamically allocate VPD data memory (John Feeney) [660397]
- [net] tg3: Use skb_is_gso_v6() (John Feeney) [660397]
- [net] tg3: Move producer ring struct to tg3_napi (John Feeney) [660397]
- [net] tg3: Clarify semantics of TG3_IRQ_MAX_VECS (John Feeney) [660397]
- [net] tg3: Disable TSS (John Feeney) [660397]
- [net] tg3: Update version to 3.113 (John Feeney) [660397]
- [net] tg3: Migrate tg3_flags to phy_flags (John Feeney) [660397]
- [net] tg3: Create phy_flags and migrate phy_is_low_power (John Feeney) [660397]
- [net] tg3: Add phy-related preprocessor constants (John Feeney) [660397]
- [net] tg3: Add error reporting to tg3_phydsp_write() (John Feeney) [660397]
- [net] tg3: Improve small packet performance (John Feeney) [660397]
- [net] tg3: Remove 5720, 5750, and 5750M (John Feeney) [660397]
- [net] tg3: Restrict ASPM workaround devlist (John Feeney) [660397]
- [net] tg3: Manage gphy power for CPMU-less devs only (John Feeney) [660397]
- [net] tg3: Disable TSS also during tg3_close() (John Feeney) [660397]
- [net] tg3: Add 5784 ASIC rev to earlier PCIe MPS fix (John Feeney) [660397]
- [net] tg3: Update version to 3.112 (John Feeney) [660397]
- [net] tg3: Fix some checkpatch errors (John Feeney) [660397]
- [net] tg3: Revert PCIe tx glitch fix (John Feeney) [660397]
- [net] tg3: Report driver version to firmware (John Feeney) [660397]
- [net] tg3: Relax 5717 serdes restriction (John Feeney) [660397]
- [net] tg3: Fix single MSI-X vector coalescing (John Feeney) [660397]
- [net] tg3: Update version to 3.111 (John Feeney) [660397]
- [net] tg3: Allow 5717 serdes link via parallel detect (John Feeney) [660397]
- [net] tg3: Allow single MSI-X vector allocations (John Feeney) [660397]
- [net] tg3: Update version to 3.110 (John Feeney) [660397]
- [net] tg3: Remove function errors flagged by checkpatch (John Feeney) [660397]
- [net] tg3: Unify max pkt size preprocessor constants (John Feeney) [660397]
- [net] tg3: Re-inline VLAN tags when appropriate (John Feeney) [660397]
- [net] tg3: Optimize rx double copy test (John Feeney) [660397]
- [net] tg3: Update version to 3.109 (John Feeney) [660397]
- [net] tg3: Remove tg3_dump_state() (John Feeney) [660397]
- [net] tg3: Cleanup if codestyle (John Feeney) [660397]
- [net] tg3: The case of switches (John Feeney) [660397]
- [net] tg3: Whitespace, constant, and comment updates (John Feeney) [660397]
- [net] tg3: Use VPD fw version when present (John Feeney) [660397]
- [net] tg3: Prepare FW version code for VPD versioning (John Feeney) [660397]
- [net] tg3: Fix message 80 char violations (John Feeney) [660397]
- [net] tg3: netdev_err() => dev_err() (John Feeney) [660397]
- [net] tg3: Replace pr_err with sensible alternatives (John Feeney) [660397]
- [net] tg3: change field used with TG3_FLAG_10_100_ONLY constant (John Feeney) [660397]
- [net] tg3: Remove now useless VPD code (John Feeney) [660397]
- [net] tg3: use helper to search for VPD keywords (John Feeney) [660397]
- [net] tg3: use VPD information field helper functions (John Feeney) [660397]
- [net] tg3: use helper to find VPD resource data type (John Feeney) [660397]
- [net] tg3: Add large and small resource data type code (John Feeney) [660397]
- [net] tg3: Add PCI LRDT tag size and section size (John Feeney) [660397]
- [net] tg3: convert to use netdev_for_each_mc_addr, part6 (John Feeney) [660397]
- [net] tg3: Use (pr|netdev)_<level> macro helpers (John Feeney) [660397]
- [net] bna: Include embedded firmware for RHEL5 (Ivan Vecera) [475690]
- [net] bna: use device model DMA API (Ivan Vecera) [475690]
- [net] bna: Remove unnecessary memset 0 (Ivan Vecera) [475690]
- [net] bna: Update the driver version to 2.3.2.3 (Ivan Vecera) [475690]
- [net] bna: IOC failure auto recovery fix (Ivan Vecera) [475690]
- [net] bna: Restore VLAN filter table (Ivan Vecera) [475690]
- [net] bna: Removed unused code (Ivan Vecera) [475690]
- [net] bna: IOC uninit check and misc cleanup (Ivan Vecera) [475690]
- [net] bna: Fix for TX queue (Ivan Vecera) [475690]
- [net] bna: Enable pure priority tagged packet reception and rxf uninit cleanup fix (Ivan Vecera) [475690]
- [net] bna: Fix ethtool register dump and reordered an API (Ivan Vecera) [475690]
- [net] bna: Port enable disable sync and txq priority fix (Ivan Vecera) [475690]
- [net] bna: TxRx and datapath fix (Ivan Vecera) [475690]
- [net] bna: scope and dead code cleanup (Ivan Vecera) [475690]
- [net] bna: fix interrupt handling (Ivan Vecera) [475690]
- [net] bna: off by one (Ivan Vecera) [475690]
- [net] bna: Check for NULL before deref in bnad_cb_tx_cleanup (Ivan Vecera) [475690]
- [net] bna: fix lock imbalance (Ivan Vecera) [475690]
- [net] bna: fix stats handling (Ivan Vecera) [475690]
- [net] bna: Fixed build break for allyesconfig (Ivan Vecera) [475690]
- [net] bna: Brocade 10Gb Ethernet device driver (Ivan Vecera) [475690]
- [s390] tape: deadlock on global work queue (Hendrik Brueckner) [681329]
- [s390] qeth: remove needless IPA-commands in offline (Hendrik Brueckner) [679120]
- [s390] qeth: allow channel path changes in recovery (Hendrik Brueckner) [678073]
- [s390] qeth: wrong MAC-address displayed in error message (Hendrik Brueckner) [675747]
- [s390] dasd: Improve handling of stolen DASD reservation (Hendrik Brueckner) [651141]
- [s390] dasd: provide a Sense Path Group ID ioctl (Hendrik Brueckner) [651135]
- [s390] qeth: tolerate OLM-limitation (Hendrik Brueckner) [651161]
- [s390] sclp_vt220: console message may cause deadlock (Hendrik Brueckner) [675751]
- [s390] uaccess: missing sacf in uaccess error handling (Hendrik Brueckner) [670234]
- [x86_64] nmi_watchdog: modify default to perf counter 1 (Don Zickus) [633196 659816]
- [net] qlcnic: Remove validation for max tx and max rx queues (Chad Dupuis) [660390]
- [net] qlcnic: fix checks for auto_fw_reset (Chad Dupuis) [660390]
- [net] qlcnic: change module parameter permissions (Chad Dupuis) [660390]
- [net] qlcnic: fix ethtool diagnostics test (Chad Dupuis) [660390]
- [net] qlcnic: fix flash fw version read (Chad Dupuis) [660390]
- [net] qlcnic: Use static const (Chad Dupuis) [660390]
- [net] qlcnic: reset pci function unconditionally during probe (Chad Dupuis) [660390]
- [net] qlcnic: fix ocm window register offset calculation (Chad Dupuis) [660390]
- [net] qlcnic: fix LED test when interface is down. (Chad Dupuis) [660390]
- [net] qlcnic: Updated driver version to 5.0.13 (Chad Dupuis) [660390]
- [net] qlcnic: LICENSE file for qlcnic (Chad Dupuis) [660390]
- [net] qlcnic: validate eswitch config values for PF (Chad Dupuis) [660390]
- [net] qlcnic: Disable loopback support (Chad Dupuis) [660390]
- [net] qlcnic: Bumped up driver version to 5.0.12 (Chad Dupuis) [660390]
- [net] qlcnic: lro module parameter (Chad Dupuis) [660390]
- [net] qlcnic: Fix driver hang while using qcc application (Chad Dupuis) [660390]
- [net] qlcnic: lro off message log from set rx checsum (Chad Dupuis) [660390]
- [net] qlcnic: Add description for CN1000Q adapter (Chad Dupuis) [660390]
- [net] qlcnic: Allow minimum bandwidth of zero (Chad Dupuis) [660390]
- [net] qlcnic: fix panic on load (Chad Dupuis) [660390]
- [net] qlcnic: define valid vlan id range (Chad Dupuis) [660390]
- [net] qlcnic: reduce rx ring size (Chad Dupuis) [660390]
- [net] qlcnic: fix mac learning (Chad Dupuis) [660390]
- [net] qlcnic: update ethtool stats (Chad Dupuis) [660390]
- [net] qlcnic: update driver version 5.0.11 (Chad Dupuis) [660390]
- [net] qlcnic: change all P3 references to P3P (Chad Dupuis) [660390]
- [net] qlcnic: fix promiscous mode for VF (Chad Dupuis) [660390]
- [net] qlcnic: fix board description (Chad Dupuis) [660390]
- [net] qlcnic: remove private LRO flag (Chad Dupuis) [660390]
- [net] qlcnic: support quiescent mode (Chad Dupuis) [660390]
- [net] qlcnic: remove dead code (Chad Dupuis) [660390]
- [net] qlcnic: set mtu lower limit (Chad Dupuis) [660390]
- [net] qlcnic: cleanup port mode setting (Chad Dupuis) [660390]
- [net] qlcnic: sparse warning fixes (Chad Dupuis) [660390]
- [net] qlcnic: fix vlan TSO on big endian machine (Chad Dupuis) [660390]
- [net] qlcnic: fix endianess for lro (Chad Dupuis) [660390]
- [net] qlcnic: fix diag register (Chad Dupuis) [660390]
- [net] qlcnic: fix eswitch stats (Chad Dupuis) [660390]
- [net] qlcnic: fix internal loopback test (Chad Dupuis) [660390]
- [net] qlcnic: return operator cleanup (Chad Dupuis) [660390]
- [net] qlcnic: dont set skb->truesize (Chad Dupuis) [660390]
- [net] qlcnic: dont assume NET_IP_ALIGN is 2 (Chad Dupuis) [660390]
- [net] qlcnic: update version 5.0.10 (Chad Dupuis) [660390]
- [net] qlcnic: remove fw version check (Chad Dupuis) [660390]
- [net] qlcnic: vlan lro support (Chad Dupuis) [660390]
- [net] qlcnic: vlan gro support (Chad Dupuis) [660390]
- [net] qlcnic: support vlan rx accleration (Chad Dupuis) [660390]
- [net] qlcnic: add cksum flag (Chad Dupuis) [660390]
- [net] qlcnic: mac vlan learning support (Chad Dupuis) [660390]
- [net] qlcnic: support mac learning (Chad Dupuis) [660390]
- [net] qlcnic: fix mac override capability (Chad Dupuis) [660390]
- [net] qlcnic: fix panic while using eth_hdr (Chad Dupuis) [660390]
- [net] qlcnic: fix mac anti spoof policy (Chad Dupuis) [660390]
- [net] qlcnic: fix for setting default eswitch config (Chad Dupuis) [660390]
- [net] qlcnic: fix mac addr read (Chad Dupuis) [660390]
- [net] qlcnic: add api version in reg dump (Chad Dupuis) [660390]
- [net] qlcnic: backout firmware initialization update (Chad Dupuis) [660390]
- [net] qlnic: fix a race in qlcnic_get_stats (Chad Dupuis) [660390]
- [net] qlcnic: PCI ID addition (Chad Dupuis) [660390]
- [net] qlcnic: Fix driver load issue in FW hang (Chad Dupuis) [660390]
- [net] qlcnic: change reg name (Chad Dupuis) [660390]
- [net] qlcnic: fix fw recovery for PF (Chad Dupuis) [660390]
- [net] qlcnic: support port vlan id (Chad Dupuis) [660390]
- [net] qlcnic: eswitch config fixes (Chad Dupuis) [660390]
- [net] qlcnic: update version 5.0.8 (Chad Dupuis) [660390]
- [net] qlcnic: rom lock recovery (Chad Dupuis) [660390]
- [net] qlcnic: firmware initialization update (Chad Dupuis) [660390]
- [net] qlcnic: fix endiness in eswitch statistics (Chad Dupuis) [660390]
- [net] qlcnic: mark device state as failed (Chad Dupuis) [660390]
- [net] qlcnic: fix npar state (Chad Dupuis) [660390]
- [net] qlcnic: support anti mac spoofing (Chad Dupuis) [660390]
- [net] qlcnic: configure offload setting on eswitch (Chad Dupuis) [660390]
- [net] qlcnic: configure port on eswitch (Chad Dupuis) [660390]
- [net] qlcnic: replace magic numbers with defines (Chad Dupuis) [660390]
- [net] qlcnic: remove unused code (Chad Dupuis) [660390]
- [net] qlcnic: fix inconsistent lock state (Chad Dupuis) [660390]
- [net] qlcnic: Use available error codes (Chad Dupuis) [660390]
- [net] qlcnic: turn off lro when rxcsum is disabled (Chad Dupuis) [660390]
- [net] qlcnic: fix link diag test (Chad Dupuis) [660390]
- [net] qlcnic: fix link status message (Chad Dupuis) [660390]
- [net] qlcnic: add eswitch statistics support (Chad Dupuis) [660390]
- [net] qlcnic: fix for setting function modes (Chad Dupuis) [660390]
- [net] qlcnic: device state management fixes for virtual func (Chad Dupuis) [660390]
- [net] qlcnic: fix aer for virtual func (Chad Dupuis) [660390]
- [net] qlcnic: using too much stack (Chad Dupuis) [660390]
- [net] qlcnic: clean up qlcnic_init_pci_info (Chad Dupuis) [660390]
- [net] qlcnic: fix copyright for pci searching function (Chad Dupuis) [660390]
- [net] netxen: support for GbE port settings (Chad Dupuis) [660437]
- [net] netxen: Notify firmware of Flex-10 interface down (Chad Dupuis) [660437]
- [net] netxen: update driver version 4.0.75 (Chad Dupuis) [660437]
- [net] netxen: enable LRO based on NETIF_F_LRO (Chad Dupuis) [660437]
- [net] netxen: update module description (Chad Dupuis) [660437]
- [net] netxen: Use static const (Chad Dupuis) [660437]
- [net] netxen: remove unused firmware exports (Chad Dupuis) [660437]
- [net] netxen: Fix tx queue manipulation bug in netxen_nic_probe (Chad Dupuis) [660437]
- [net] netxen: make local function static (Chad Dupuis) [660437]
- [net] netxen: mask correctable error (Chad Dupuis) [660437]
- [net] netxen: fix race in tx stop queue (Chad Dupuis) [660437]
- [net] netxen: return operator cleanup (Chad Dupuis) [660437]
- [net] netxen: dont set skb->truesize (Chad Dupuis) [660437]

* Wed Mar 23 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-251.el5]
- [net] benet: Bump up the version number (Ivan Vecera) [660389]
- [net] benet: Copyright notice change. Update to Emulex instead of ServerEngines (Ivan Vecera) [660389]
- [net] benet: Fix UDP packet detected status in RX compl (Ivan Vecera) [660389]
- [net] benet: changes for BE3 native mode support (Ivan Vecera) [660389]
- [net] benet: Add multicast filter capability for Lancer (Ivan Vecera) [660389]
- [net] benet: Disarm CQ and EQ to disable interrupt in Lancer (Ivan Vecera) [660389]
- [net] benet: Remove TX Queue stop in close (Ivan Vecera) [660389]
- [net] benet: Change f/w command versions for Lancer (Ivan Vecera) [660389]
- [net] benet: Add error recovery during load for Lancer (Ivan Vecera) [660389]
- [net] benet: Checksum field valid only for TCP/UDP (Ivan Vecera) [660389]
- [net] benet: Remove ERR compl workaround for Lancer (Ivan Vecera) [660389]
- [net] benet: use GFP_KERNEL allocations when possible (Ivan Vecera) [660389]
- [net] benet: use hba_port_num instead of port_num (Ivan Vecera) [660389]
- [net] benet: add code to display temperature of ASIC (Ivan Vecera) [660389]
- [net] benet: fix to ignore transparent vlan ids wrongly indicated by NIC (Ivan Vecera) [660389]
- [net] benet: variable name change (Ivan Vecera) [660389]
- [net] benet: fixes in ethtool selftest (Ivan Vecera) [660389]
- [net] benet: add new counters to display via ethtool stats (Ivan Vecera) [660389]
- [net] benet: restrict WOL to PFs only. (Ivan Vecera) [660389]
- [net] benet: detect a UE even when a interface is down. (Ivan Vecera) [660389]
- [net] benet: gracefully handle situations when UE is detected (Ivan Vecera) [660389]
- [net] benet: fix be_suspend/resume/shutdown (Ivan Vecera) [660389]
- [net] benet: pass proper hdr_size while flashing redboot. (Ivan Vecera) [660389]
- [net] benet: Fix broken priority setting when vlan tagging is enabled. (Ivan Vecera) [660389]
- [net] benet: Allow VFs to call be_cmd_reset_function. (Ivan Vecera) [660389]
- [net] benet: pass domain numbers for pmac_add/del functions (Ivan Vecera) [660389]
- [net] benet: For the VF MAC, use the OUI from current MAC address (Ivan Vecera) [660389]
- [net] benet: Cleanup the VF interface handles (Ivan Vecera) [660389]
- [net] benet: call be_vf_eth_addr_config() after register_netdev (Ivan Vecera) [660389]
- [net] benet: Initialize and cleanup sriov resources only if pci_enable_sriov has succeeded. (Ivan Vecera) [660389]
- [net] benet: Use domain id when be_cmd_if_destroy is called. (Ivan Vecera) [660389]
- [net] benet: Avoid null deref in be_cmd_get_seeprom_data (Ivan Vecera) [660389]
- [net] benet: use device model DMA API (Ivan Vecera) [660389]
- [net] benet: remove netif_stop_queue being called before register_netdev. (Ivan Vecera) [660389]
- [net] benet: fix a crash seen during insmod/rmmod test (Ivan Vecera) [660389]
- [net] benet: Use static const (Ivan Vecera) [660389]
- [net] benet: use mutex instead of spin lock for mbox_lock (Ivan Vecera) [660389]
- [net] benet: Handle out of buffer completions for lancer (Ivan Vecera) [660389]
- [net] benet: FW init cmd fix for lancer (Ivan Vecera) [660389]
- [net] benet: Fix be_dev_family_check() return value check (Ivan Vecera) [660389]
- [net] benet: Fix too optimistic NETIF_F_HW_CSUM features (Ivan Vecera) [660389]
- [net] benet: adding support for Lancer family of CNAs (Ivan Vecera) [660389]
- [net] benet: remove dead code (Ivan Vecera) [660389]
- [net] benet: Changes to use only priority codes allowed by f/w (Ivan Vecera) [660389]
- [net] benet: add multiple RX queue support (Ivan Vecera) [660389]
- [net] benet: fix tx completion polling (Ivan Vecera) [660389]
- [net] benet: use Rx and Tx queues like upstream (Ivan Vecera) [660389]
- [net] benet: return operator cleanup (Ivan Vecera) [660389]
- [net] benet: fix a bug in UE detection logic (Ivan Vecera) [660389]
- [net] benet: fix net-snmp error because of wrong packet stats (Ivan Vecera) [660389]
- [net] benet: stats for packets received due to internal switching in ASIC. (Ivan Vecera) [660389]
- [net] benet: fix to avoid sending get_stats request if one is already being processed. (Ivan Vecera) [660389]
- [net] benet: change to show correct physical link status (Ivan Vecera) [660389]
- [net] benet: add code to dump registers for debug (Ivan Vecera) [660389]
- [net] benet: bump the driver version number (Ivan Vecera) [660389]
- [net] benet: variable name changes (Ivan Vecera) [660389]
- [net] benet: supress printing error when mac query fails for VF (Ivan Vecera) [660389]
- [net] benet: Patch to determine if function is VF while running in guest OS. (Ivan Vecera) [660389]
- [net] benet: enable ipv6 tso support (Ivan Vecera) [660389]
- [net] benet: fix typos concerning management (Ivan Vecera) [660389]
- [net] benet: Remove unnecessary returns from void functions (Ivan Vecera) [660389]
- [net] benet: use skb_headlen() (Ivan Vecera) [660389]
- [net] benet: clarify promiscuous cmd with a comment (Ivan Vecera) [660389]
- [net] benet: Fix compile warnnings in drivers/net/benet/be_ethtool.c (Ivan Vecera) [660389]
- [net] ixgbe: update to upstream version 3.2.9-k2 (Andy Gospodarek) [568312 568557 570366 571254 651467 653236 653359 653469 655022]
- [misc] vlan: Add function to get EtherType from vlan packets (Andy Gospodarek) [568312 568557 570366 571254 651467 653236 653359 653469 655022]
- [net] support for NETIF_F_HIGHDMA on vlan interfaces (Andy Gospodarek) [568312 568557 570366 571254 651467 653236 653359 653469 655022]
- [scsi] bnx2i: Updated to version 2.6.2.3 (Mike Christie) [660406]
- [scsi] bnx2i: Updated version to 2.6.2.2 (Mike Christie) [660406]
- [scsi] bnx2i: Added iSCSI text pdu support for iSCSI offload (Mike Christie) [660406]
- [scsi] bnx2i: Added jumbo MTU support for the no shost case (Mike Christie) [660406]
- [scsi] bnx2i: Added support for the 57712(E) devices (Mike Christie) [660406]
- [scsi] bnx2i: Added handling for unsupported iSCSI offload hba (Mike Christie) [660406]
- [scsi] bnx2i: Fixed the 32-bit swapping of the LUN field for nopouts for 5771X (Mike Christie) [660406]
- [scsi] bnx2i: Allow ep CONNECT_FAILED condition to go through proper cleanup (Mike Christie) [660406]
- [scsi] bnx2i: Added reconnect fix connecting against Lefthand targets (Mike Christie) [660406]
- [scsi] bnx2i: Cleaned up various error conditions in ep_connect/disconnect (Mike Christie) [660406]
- [scsi] bnx2i: Added return code check for chip kwqe submission request (Mike Christie) [660406]
- [scsi] bnx2i: Modified the bnx2i stop path to compensate for in progress ops (Mike Christie) [660406]
- [scsi] bnx2i: Removed the dynamic registration of CNIC (Mike Christie) [660406]
- [scsi] bnx2i: Added mutex lock protection to conn_get_param (Mike Christie) [660406]
- [net] cnic: Fix lost interrupt on bnx2x (Mike Christie) [660430]
- [net] cnic: Prevent status block race conditions with hardware (Mike Christie) [660430]
- [net] bnx2x, cnic: Consolidate iSCSI/FCoE shared mem logic in bnx2x (Mike Christie) [660430]
- [net] cnic: Fix the type field in SPQ messages (Mike Christie) [660430]
- [net] cnic: Do not call bnx2i when bnx2i is calling cnic_unregister_driver() (Mike Christie) [660430]
- [net] cnic: Do not allow iSCSI and FCoE on bnx2x multi-function mode (Mike Christie) [660430]
- [net] cnic: fix mem leak on alloc fail in cnic_alloc_uio_rings (Mike Christie) [660430]
- [net] cnic: Add FCoE support on 57712 (Mike Christie) [660430]
- [net] cnic: Add kcq2 support on 57712 (Mike Christie) [660430]
- [net] cnic: Call cm_connect_complete() immediately on error (Mike Christie) [660430]
- [net] cnic: Check device state before reading the kcq pointer in IRQ (Mike Christie) [660430]
- [net] cnic: Support NIC Partition mode (Mike Christie) [660430]
- [net] cnic: Use proper client and connection IDs on iSCSI ring (Mike Christie) [660430]
- [net] cnic: Improve ->iscsi_nl_msg_send() (Mike Christie) [660430]
- [net] cnic: Prevent "scheduling while atomic" when calling ->cnic_init() (Mike Christie) [660430]
- [net] cnic: Fix iSCSI TCP port endian order. (Mike Christie) [660430]
- [net] cnic: Remove unnecessary semicolons (Mike Christie) [660430]
- [net] cnic: Add support for 57712 device (Mike Christie) [660430]
- [net] cnic: Decouple uio close from cnic shutdown (Mike Christie) [660430]
- [net] cnic: Add cnic_uio_dev struct (Mike Christie) [660430]
- [net] cnic: Add cnic_free_uio() (Mike Christie) [660430]
- [net] cnic: Defer iscsi connection cleanup (Mike Christie) [660430]
- [net] cnic: Add cnic_bnx2x_destroy_ramrod() (Mike Christie) [660430]
- [net] cnic: Convert ctx_flags to bit fields (Mike Christie) [660430]
- [net] cnic: Add common cnic_request_irq() (Mike Christie) [660430]
- [net] bnx2x, cnic: Fix SPQ return credit (Mike Christie) [660430]
- [char] Enable and extend Legacy PTY support for 4096 device pairs (Mauro Carvalho Chehab) [582776]
- [fs] ioctl: make fiemap map at least a blocksize amount (Josef Bacik) [663041]
- [net] forcedeth/r8169: call netif_carrier_off at end of probe (Ivan Vecera) [664705 664707]
- [net] ixgbevf: update to upstream version 2.0.0-k2 (Andy Gospodarek) [653237]
- [net] e1000e: update to upstream version 1.3.10 (Andy Gospodarek) [653242 653548]
- [x86] amd: Extend support to future families (Frank Arnold) [682835]
- [x86] smpboot: Use compute unit info to determine thread siblings (Frank Arnold) [682835]
- [x86] amd: Extract compute unit information for AMD CPUs (Frank Arnold) [682835]
- [x86] amd: Add support for CPUID topology extension of AMD CPUs (Frank Arnold) [682835]
- [x86] cpufeature: Update AMD CPUID feature bits (Frank Arnold) [682835]
- [x86_64] Support NMI watchdog on newer AMD CPU families (Frank Arnold) [682835]
- [net] ixgbe: fix for 82599 erratum on Header Splitting (Andy Gospodarek) [680531]
- [net] ixgbe: limit VF access to network traffic (Andy Gospodarek) [680531]
- [net] igbvf driver update for RHEL5.7 (Stefan Assmann) [653241]
- [fs] ext3: Always set dx_node's fake_dirent explicitly (Eric Sandeen) [662838]
- [virt] xen/netback: signal front-end close event via udev (Paolo Bonzini) [661985]
- [net] bnx2x: fix swap of rx-ticks and tx-ticks parameters in interrupt coalescing flow (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: fix MaxBW configuration (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: (NPAR) prevent HW access in D3 state (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: fix link notification (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: fix non-pmf device load flow (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: update driver version to 1.62.00-6 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: properly calculate lro_mss (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: perform statistics "action" before state transition. (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: properly configure coefficients for MinBW algorithm (NPAR mode). (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Fix ethtool -t link test for MF (non-pmf) devices. (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Fix nvram test for single port devices. (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: (NPAR mode) Fix FW initialization (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Add a missing bit for PXP parity register of 57712. (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Duplication in promisc mode (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: multicasts in NPAR mode (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Update bnx2x version to 1.62.00-5 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Fix potential link loss in multi-function mode (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Fix port swap for BCM8073 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Fix LED blink rate on BCM84823 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Remove setting XAUI low-power for BCM8073 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Update bnx2x version to 1.62.00-4 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Fix AER setting for BCM57712 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Fix BCM84823 LED behavior (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Mark full duplex on some external PHYs (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Fix BCM8073/BCM8727 microcode loading (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: LED fix for BCM8727 over BCM57712 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Common init will be executed only once after POR (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Swap BCM8073 PHY polarity if required (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: fix typos (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Fix the race on bp->stats_pending. (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Move to D0 before clearing MSI/MSI-X configuration. (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: registers dump fixes (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Don't prevent RSS configuration in INT#x and MSI interrupt modes. (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: adding dcbnl support (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Use static const (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: remove bogus check (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: update version to 1.62.00-2 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: update firmware to 6.2.5.0 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: bnx2x_request_firmware update for 6.2.5.0 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: replace FW to 6.2.5 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Add DCB/PFC support - link layer (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: add DCB support (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Disable FCoE ring, NETDEV_HW_ADDR_T_SAN for RHEL5.7. (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: add FCoE ring (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Update version number and a date. (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Fixed a compilation warning (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Use dma_alloc_coherent() semantics for ILT memory allocation (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: LSO code was broken on BE platforms (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Add Nic partitioning mode (57712 devices) (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Use helpers instead of direct access to the shinfo(skb) fields (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Do interrupt mode initialization and NAPIs adding before register_netdev() (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Disable local BHes to prevent a dead-lock situation (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: fix error value sign (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Remove unnecessary semicolons (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Update version number (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Reset 8073 phy during common init (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Do not enable CL37 BAM unless it is explicitly enabled (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Fix resetting BCM8726 PHY during common init (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Clear latch indication on link reset (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Fix port selection in case of E2 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Fix waiting for reset complete on BCM848x3 PHYs (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Restore appropriate delay during BMAC reset (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: make local function static and remove dead code (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: remove BCM_VLAN (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Don't check for vlan group before vlan_tx_tag_present. (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: update version to 1.60.00-3 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: prevent false parity error in MSI-X memory of HC block (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: fix possible deadlock in HC hw block (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: update version to 1.60.00-2 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: remove unnecessary FUNC_FLG_RSS flag and related (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Use correct FW constant for header padding (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: do not deal with power if no capability (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: remove redundant commands during error handling (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Optimized the branching in the bnx2x_rx_int() (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Fixing a typo: added a missing RSS enablement (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: update version to 1.60.00-1 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: properly initialize FW stats (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: code beautify (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Fix SPQ return credit (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: move msix table initialization to probe() (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: use L1_CACHE_BYTES instead of magic number (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: remove unused fields in main driver structure (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: remove unused parameter in reuse_rx_skb() (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Add 57712 support (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: change type of spq_left to atomic (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Protect statistics ramrod and sequence number (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: rename MF related fields (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: firmware naming from upstream (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: whitespaces like in upstream, remove some #if0 lines (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: use netdev_for_each_mc_addr (Michal Schmidt) [629609 651546 653357 656360]
- [misc] netdevice.h: add netdev_mc_count (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: use trivial wrappers around get_sset_count (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: remove a few pointless differences from upstream (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: bnx2x_alloc_napi cleanup, caller more similar to upstream (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: remove bnx2x_init_values.h (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x, cnic, bnx2i: use new FW/HSI (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Moved enabling of MSI to the bnx2x_set_num_queues() (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Use netif_set_real_num_{rx, tx}_queues() (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: return operator cleanup (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Spread rx buffers between allocated queues (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: use ARRAY_SIZE macro in bnx2x_main.c (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Update bnx2x version to 1.52.53-6 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Change LED scheme for dual-media (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Add dual-media changes (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Organize PHY functions (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Apply logic changes for the new scheme (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Move common function into aggregated function (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Adjust flow-control with the new scheme (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Adjust alignment of split PHY functions (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Split PHY functions (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Unify PHY attributes (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: avoid skb->ip_summed initialization (Michal Schmidt) [629609 651546 653357 656360]
- [net] skbuff: add skb_checksum_none_assert (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Update version to 1.52.53-5 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Add BCM84823 to the supported PHYs (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Change BCM848xx LED configuration (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Remove unneeded setting of XAUI low power to BCM8727 (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Change BCM848xx configuration according to IEEE (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Reset link before any new link settings (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Fix potential link issue In BCM8727 based boards (Michal Schmidt) [629609 651546 653357 656360]
- [net] bnx2x: Fix potential link issue of BCM8073/BCM8727 (Michal Schmidt) [629609 651546 653357 656360]
- Revert: [net] bnx2x: force interrupt mode for iscsi unset mac (Michal Schmidt) [629609 651546 653357 656360]
- [net] ipv4: make accept_local writeable for loopback (Neil Horman) [672570]
- [net] bnx2: Update to latest upstream for RHEL5.7 (Neil Horman) [651438 660375]
- [pci] backport common vpd support functions (Neil Horman) [683978]
- [net] e1000: fix sparse warning (Dean Nelson) [571889 653248 653546]
- [net] e1000: add support for Marvell Alaska M88E1118R PHY (Dean Nelson) [571889 653248 653546]
- [net] e1000: Add support for the CE4100 reference platform (Dean Nelson) [571889 653248 653546]
- [net] e1000: fix return value not set on error (Dean Nelson) [571889 653248 653546]
- [net] e1000: fix Tx hangs by disabling 64-bit DMA (Dean Nelson) [571889 653248 653546]
- [net] e1000: allow option to limit number of descriptors down to 48 per ring (Dean Nelson) [571889 653248 653546]
- [net] e1000: Use new function for copybreak tests (Dean Nelson) [571889 653248 653546]
- [net] e1000: do not modify tx_queue_len on link speed change (Dean Nelson) [571889 653248 653546]
- [net] e1000: Fix DMA mapping error handling on RX (Dean Nelson) [571889 653248 653546]
- [net] e1000: call pci_save_state after pci_restore_state (Dean Nelson) [571889 653248 653546]
- [net] e1000: don't use small hardware rx buffers (Dean Nelson) [571889 653248 653546]
- [fs] gfs2: directly write blocks past i_size (Benjamin Marzinski) [684371]
- [fs] gfs2: fix block allocation check for fallocate (Benjamin Marzinski) [684024]
- [redhat] spec: trim srpm size and vastly improve prep time (Jarod Wilson) [687950]

* Mon Mar 21 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-250.el5]
- [block] cciss: use short tags where supported (Tomas Henzl) [656343]
- [block] cciss: Fix memory leak in cciss_sysfs_stat_inquiry (Tomas Henzl) [656343]
- [block] cciss: do not reorder commands in internal queue (Tomas Henzl) [656343]
- [block] cciss: add another controller 0x103C3356 (Tomas Henzl) [656343]
- [block] cciss: fix panic in cciss_revalidate (Tomas Henzl) [656343]
- [block] cciss: Do not remove /proc entry if we never created it (Tomas Henzl) [656343]
- [block] cciss: do not leak stack to userland (Tomas Henzl) [656343]
- [block] cciss: catch kmalloc failure of h->scatter_list (Tomas Henzl) [656343]
- [block] cciss: fix missed command status value CMD_UNABORTABLE (Tomas Henzl) [656343]
- [block] cciss: remove ifdef'ed out interrupt_not_for_us (Tomas Henzl) [656343]
- [block] cciss: change printks to dev_warn (Tomas Henzl) [656343]
- [block] cciss: use consistent variable names (Tomas Henzl) [656343]
- [block] cciss: mark performant mode function as __devinit (Tomas Henzl) [656343]
- [block] cciss: cleanup some debug ifdefs (Tomas Henzl) [656343]
- [block] cciss: fix leak of ioremapped memory in init error path (Tomas Henzl) [656343]
- [block] cciss: Fix panic in multipath configurations (Tomas Henzl) [656343]
- [message] mptfusion: version update to 3.04.18rh (Tomas Henzl) [662160]
- [message] mptfusion: Incorrect return value in mptscsih_dev_reset (Tomas Henzl) [662160]
- [message] mptfusion: remove bus reset (Tomas Henzl) [662160]
- [message] mptfusion: 3gbps - 6gbps (Tomas Henzl) [662160]
- [message] mptfusion: sysfs sas addr handle (Tomas Henzl) [662160]
- [message] mptfusion: Fix 32 bit platforms with 64 bit resources (Tomas Henzl) [662160]
- [message] mptfusion: use module_param correctly (Tomas Henzl) [662160]
- [message] mptfusion: Adjust confusing if indentation (Tomas Henzl) [662160]
- [message] mptfusion: print Doorbell reg on hard reset and timeout (Tomas Henzl) [662160]
- [message] mptfusion: Cleanup some duplicate calls in mptbase.c (Tomas Henzl) [662160]
- [message] mptfusion: Extra DMD error handling debug prints (Tomas Henzl) [662160]
- [message] mptfusion: block errors if deleting devices or DMD (Tomas Henzl) [662160]
- [message] mptfusion: add ioc_reset_in_progress reset in SoftReset (Tomas Henzl) [662160]
- [message] mptfusion: handle SATA hotplug failure (Tomas Henzl) [662160]
- [message] mptfusion: schedule_target_reset from all Reset context (Tomas Henzl) [662160]
- [message] mptfusion: sanity check for device before adding to OS (Tomas Henzl) [662160]
- [message] mptfusion: fix declaration of device_missing_delay (Tomas Henzl) [662160]
- [message] mptfusion: DID_TRANSPORT_DISRUPTED, not DID_BUS_BUSY (Tomas Henzl) [662160]
- [message] mptfusion: Set fw_events_off to 1 at driver load time (Tomas Henzl) [662160]
- [scsi] mpt2sas: version change to 08.101.00.00 (Tomas Henzl) [662153]
- [scsi] mpt2sas: Call _scsih_ir_shutdown before reporting to OS (Tomas Henzl) [662153]
- [scsi] mpt2sas: Basic Code Cleanup in mpt2sas_base (Tomas Henzl) [662153]
- [scsi] mpt2sas: fix access to freed memory from port enable (Tomas Henzl) [662153]
- [scsi] mpt2sas: Fix race between broadcast asyn event (Tomas Henzl) [662153]
- [scsi] mpt2sas: support for Customer specific branding messages (Tomas Henzl) [662153]
- [scsi] mpt2sas: Revision P MPI Header Update (Tomas Henzl) [662153]
- [scsi] mpt2sas: Correct resizing calculation for max_queue_depth (Tomas Henzl) [662153]
- [scsi] mpt2sas: device reset event not supported on old firmware (Tomas Henzl) [662153]
- [scsi] mpt2sas: fix device removal handshake with vacant bit set (Tomas Henzl) [662153]
- [scsi] mpt2sas: Debug string changes from target to device (Tomas Henzl) [662153]
- [scsi] mpt2sas: Remove code for TASK_SET_FULL from driver (Tomas Henzl) [662153]
- [scsi] mpt2sas: MPI2.0 Header updated (Tomas Henzl) [662153]
- [scsi] mpt2sas: Modify code to support Expander switch (Tomas Henzl) [662153]
- [scsi] mpt2sas: create pool of chain buffers for IO (Tomas Henzl) [662153]
- [scsi] mpt2sas: add loadtime params for IOMissingDelay and params (Tomas Henzl) [662153]
- [scsi] mpt2sas: add sanity check for cb_idx and smid access (Tomas Henzl) [662153]
- [scsi] mpt2sas: remov compiler warnnings when logging is disabled (Tomas Henzl) [662153]
- [scsi] mpt2sas: Copy message frame before releasing (Tomas Henzl) [662153]
- [scsi] mpt2sas: Copy sense buffer to work on it (Tomas Henzl) [662153]
- [scsi] mpt2sas: Add message to error escalation callback (Tomas Henzl) [662153]
- [scsi] mpt2sas: Add check for responding volumes after Host Reset (Tomas Henzl) [662153]
- [scsi] mpt2sas: add ENOMEM return type when allocation fails (Tomas Henzl) [662153]
- [scsi] mpt2sas: device event handling using pd_handles per HBA (Tomas Henzl) [662153]
- [scsi] mpt2sas: Tie a log info message to a specific PHY (Tomas Henzl) [662153]
- [scsi] mpt2sas: print level KERN_DEBUG is replaced by KERN_INFO (Tomas Henzl) [662153]
- [scsi] mpt2sas: add sysfs support for tracebuffer (Tomas Henzl) [662153]
- [scsi] mpt2sas: MPI header version N is updated (Tomas Henzl) [662153]
- [scsi] mpt2sas: add sysfs counter for ioc reset (Tomas Henzl) [662153]
- [scsi] mpt2sas: add expander phy control support (Tomas Henzl) [662153]
- [scsi] mpt2sas: add expander phy counter support (Tomas Henzl) [662153]
- [scsi] mpt2sas: add disable_discovery module parameter (Tomas Henzl) [662153]
- [scsi] mpt2sas: don't reset when another reset is in progress (Tomas Henzl) [662153]
- [net] ip_conntrack_ftp: fix tracking of sequence numbers (Thomas Graf) [642388]
- [fs] gfs2: add missing unlock_page in gfs2_write_begin (Steven Whitehouse) [684795]
- [powerpc] numa: improved kABI breakage fix in paca struct (Steve Best) [651167]
- [fs] gfs2: Make delayed workqueues submit immediately if delay 0 (Robert S Peterson) [650494]
- [fs] gfs2: improve performance with bouncing locks in a cluster (Robert S Peterson) [650494]
- [net] s2io: rx_ring_sz bounds checking (Michal Schmidt) [491786]
- [net] s2io: resolve statistics issues (Michal Schmidt) [598650]
- [scsi] iscsi: use kmap instead of kmap_atomic (Mike Christie) [672115]
- [block] reduce stack footprint of blk_recount_segments() (Jeff Moyer) [638988]
- [block] fix nr_phys_segments miscalculation bug (Jeff Moyer) [638988]
- [block] raid fixups for removal of bi_hw_segments (Jeff Moyer) [638988]
- [block] drop vmerge accounting (Jeff Moyer) [638988]
- [block] drop virtual merging accounting (Jeff Moyer) [638988]
- [block] Introduce rq_for_each_segment replacing rq_for_each_bio (Jeff Moyer) [638988]
- [block] Merge blk_recount_segments into blk_recalc_rq_segments (Jeff Moyer) [638988]
- [fs] Fix over-zealous flush_disk changing device size (Jeff Moyer) [678359]
- [fs] lockd: make lockd_down wait for lockd to come down (Jeff Layton) [653286]
- [net] sunrpc: Don't disconnect if connection in progress (Jeff Layton) [680329]
- [fs] fix block based fiemap (Josef Bacik) [675986]
- [fs] proc: protect mm start_/end_code in /proc/pid/stat (Eugene Teo) [684571] {CVE-2011-0726}
- [net] dccp: fix oops in dccp_rcv_state_process (Eugene Teo) [682956] {CVE-2011-1093}
- [scsi] libsas: fix bug for vacant phy (David Milburn) [676423]
- [scsi] libsas: do not set res = 0 in sas_ex_discover_dev (David Milburn) [676423]
- [scsi] libsas: fix wide port hotplug issues (David Milburn) [676423]
- [scsi] libsas: fixup kABI breakage (David Milburn) [676423]
- [scsi] libsas: no commands to hot-removed devices (David Milburn) [676423]
- [scsi] libsas: transport-level facility to req SAS addrs (David Milburn) [676423]
- [scsi] libsas: misc fixes to the eh path (David Milburn) [676423]
- [scsi] libsas: correctly flush LU queue on error recovery (David Milburn) [676423]
- [scsi] libsas: fix error handling (David Milburn) [676423]
- [scsi] libsas: fix sense_buffer overrun (David Milburn) [676423]
- [scsi] libsas: reuse orig port hotplugging phys wide port (David Milburn) [676423]
- [scsi] libsas: fix NCQ mixing with non-NCQ (David Milburn) [676423]
- [scsi] libsas: fix endianness bug in sas_ata (David Milburn) [676423]
- [scsi] libsas: don't use made up error codes (David Milburn) [676423]
- [net] bluetooth: fix bnep buffer overflow (Don Howard) [681319] {CVE-2011-1079}
- [pci] intel-iommu: Fix get_domain_for_dev() error path (Alex Williamson) [688646]
- [pci] intel-iommu: Unlink domain from iommu (Alex Williamson) [688646]
- [redhat] spec: assorted cleanup and streamlining

* Wed Mar 16 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-249.el5]
- [md] dm-mpath: avoid storing private suspended state (Mike Snitzer) [678670]
- [md] dm-mpath: reject messages when device is suspended (Mike Snitzer) [678670]
- [md] dm: export suspended state to targets (Mike Snitzer) [678670]
- [md] dm: rename dm_suspended to dm_suspended_md (Mike Snitzer) [678670]
- [md] dm: swap postsuspend call and setting suspended flag (Mike Snitzer) [678670]
- [md] dm-ioctl: retrieve status from inactive table (Mike Snitzer) [678670]
- [md] dm: rename dm_get_table to dm_get_live_table (Mike Snitzer) [678670]
- [md] dm-stripe: avoid div by 0 with invalid stripe count (Mike Snitzer) [678670]
- [md] dm-ioctl: forbid messages to devices being deleted (Mike Snitzer) [678670]
- [md] dm: add dm_deleting_md function (Mike Snitzer) [678670]
- [md] dm: dec_pending needs locking to save error value (Mike Snitzer) [678670]
- [md] dm-raid1: keep retrying alloc if mempool_alloc fails (Mike Snitzer) [678670]
- [md] dm-table: fix upgrade mode race (Mike Snitzer) [678670]
- [md] dm-io: respect BIO_MAX_PAGES limit (Mike Snitzer) [678670]
- [md] dm-ioctl: validate name length when renaming (Mike Snitzer) [678670]
- [md] dm-log: fix dm_io_client leak on error paths (Mike Snitzer) [678670]
- [md] dm: avoid destroying table in dm_any_congested (Mike Snitzer) [678670]
- [md] dm-raid1: fix leakage (Mike Snitzer) [678670]
- [md] dm-mpath: validate hw_handler argument count (Mike Snitzer) [678670]
- [md] dm-mpath: validate table argument count (Mike Snitzer) [678670]
- [md] dm-mpath: fix NULL deref when path parameter missing (Mike Snitzer) [673058]
- [md] dm-mpath: wait for pg_init completion on suspend (Mike Snitzer) [673058]
- [md] dm-mpath: hold io until all pg_inits completed (Mike Snitzer) [673058]
- [md] dm-mpath: skip activate_path for failed paths (Mike Snitzer) [673058]
- [md] dm-mpath: pass struct pgpath to pg init done (Mike Snitzer) [673058]
- [md] dm-mpath: prevent io from work queue while suspended (Mike Snitzer) [673058]
- [md] dm-mpath: add mutex to sync adding and flushing work (Mike Snitzer) [673058]
- [md] dm-mpath: flush workqueues before suspend completes (Mike Snitzer) [673058]
- [powerpc] numa: Fix kABI breakage in paca struct (Steve Best) [651167]
- [powerpc] Disable VPHN polling during a suspend operation (Steve Best) [651167]
- [powerpc] mm: Poll VPA for topo changes, update NUMA maps (Steve Best) [651167]
- [powerpc] Add VPHN firmware feature (Steve Best) [651167]
- [fs] jbd2: fix /proc/fs/jbd2/<dev> with external journal (Lukas Czerner) [652321]
- [fs] nfs: wait for COMMIT RPC complete before task put (Jeff Layton) [441730]
- [fs] nfs: ->flush and ->fsync should use FLUSH_SYNC (Jeff Layton) [441730]
- [net] sunrpc: fix race in __rpc_wait_for_completion_task (Jeff Layton) [441730]
- [fs] nfs: Ensure proper cleanup on rpc_run_task fail (Jeff Layton) [441730]
- [fs] nfs: clean up the unstable write code (Jeff Layton) [441730]
- [fs] nfs: Don't use ClearPageUptodate if writeback fails (Jeff Layton) [441730]
- [fs] nfs: Fix an unstable write data integrity race (Jeff Layton) [441730]
- [fs] nfs: make sure WRITE and COMMIT are uninterruptible (Jeff Layton) [441730]
- [fs] nfs: change how FLUSH_STABLE flag is used (Jeff Layton) [441730]
- [mm] writeback: fix queue handling in blk_congestion_wait (Jeff Layton) [516490]
- [fs] nfs: clean up nfs congestion control (Jeff Layton) [516490]
- [block] Add real API for dealing with blk_congestion_wait (Jeff Layton) [516490]
- [fs] nfs: kswapd must not block in nfs_release_page (Jeff Layton) [516490]
- [fs] nfs: Prevent another deadlock in nfs_release_page (Jeff Layton) [516490]
- [fs] nfs: Try commit unstable writes in nfs_release_page (Jeff Layton) [516490]
- [fs] nfs: Add debugging facility for NFS aops (Jeff Layton) [516490]
- [fs] nfs: Fix race in nfs_release_page() (Jeff Layton) [516490]
- [fs] nfs: Fix nfs_release_page (Jeff Layton) [516490]
- [fs] nfs: reduce number of unnecessary commit calls (Jeff Layton) [516490]
- [fs] nfs: nfs_writepages() cleanup (Jeff Layton) [516490]

* Mon Mar 14 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-248.el5]
- [virt] xen: make more room for event channel IRQs (Paolo Bonzini) [650838]
- [message] mptfusion: fix msgContext in mptctl_hp_hostinfo (Tomas Henzl) [646513]
- [net] ipv6: Add GSO support on forwarding path (Thomas Graf) [648572]
- [net] tc: Ignore noqueue_qdisc default qdisc when dumping (Thomas Graf) [627850]
- [serial] 8250_pci: add support for PowerPC PLX 8250 (Steve Best) [651431]
- [scsi] ibmveth: Free irq on error path (Steve Best) [651872]
- [scsi] ibmveth: Cleanup error handling in ibmveth_open (Steve Best) [651872]
- [scsi] ibmveth: Remove some unnecessary include files (Steve Best) [651872]
- [scsi] ibmveth: Convert driver specific assert to BUG_ON (Steve Best) [651872]
- [scsi] ibmveth: Return -EINVAL on all ->probe errors (Steve Best) [651872]
- [scsi] ibmveth: Some formatting fixes (Steve Best) [651872]
- [scsi] ibmveth: Remove redundant function prototypes (Steve Best) [651872]
- [scsi] ibmveth: Convert to netdev_alloc_skb (Steve Best) [651872]
- [scsi] ibmveth: Remove dupe checksum offload setup code (Steve Best) [651872]
- [scsi] ibmveth: Add optional flush of rx buffer (Steve Best) [651872]
- [scsi] ibmveth: Add scatter-gather support (Steve Best) [651872]
- [scsi] ibmveth: Add rx_copybreak (Steve Best) [651872]
- [scsi] ibmveth: Add tx_copybreak (Steve Best) [651872]
- [scsi] ibmveth: Remove LLTX (Steve Best) [651872]
- [scsi] ibmveth: batch rx buffer replacement (Steve Best) [651872]
- [scsi] ibmveth: Remove integer divide caused by modulus (Steve Best) [651872]
- [fs] gfs2: creating large files suddenly slow to a crawl (Robert S Peterson) [683155]
- [virt] xen: performance improvement for 32-bit domains (Paolo Bonzini) [390451]
- [fs] nfs: fix use of slab alloc'd pages in skb frag list (Neil Horman) [682643] {CVE-2011-1090}
- [net] af_packet: allow multicast traffic on bond ORIGDEV (Jiri Pirko) [579000]
- [net] af_packet: option to return orig_dev to userspace (Jiri Pirko) [579000]
- [fs] nfs: back out the FS-Cache patches (Jeff Layton) [631950]
- [x86_64]: fix section mismatches in kernel setup (Frank Arnold) [683078]
- [char] tty_audit: fix live lock on audit disabled (Danny Feng) [679563]
- [s390] remove task_show_regs (Danny Feng) [677853] {CVE-2011-0710}
- [scsi] qla2xxx: Query proper reg bits to determine state (Chad Dupuis) [537277]
- [scsi] qla2xxx: update version to 8.03.07.00.05.07 (Chad Dupuis) [660386]
- [scsi] qla2xxx: online ISP82XX for commands completion (Chad Dupuis) [660386]
- [scsi] qla2xxx: fix tagging modifier while executing IOs (Chad Dupuis) [660386]
- [scsi] qla2xxx: fix FCP_RSP response-info check after TMF (Chad Dupuis) [660386]
- [scsi] qla2xxx: no reset/fw-dump on CT/ELS pt req timeout (Chad Dupuis) [660386]
- [scsi] qla2xxx: return all loopback mbox out regs to API (Chad Dupuis) [660386]
- [scsi] qla2xxx: fix IO failure during chip reset (Chad Dupuis) [660386]
- [scsi] qla2xxx: show mbox reg 4 in 8012 AEN on ISP82XX (Chad Dupuis) [660386]
- [scsi] qla2xxx: show more mailbox regs during AEN handle (Chad Dupuis) [660386]
- [scsi] qla2xxx: no BIG_HAMMER if 0x20 cmd fails on CNAs (Chad Dupuis) [660386]
- [scsi] qla2xxx: Remove redundant modparam permission bits (Chad Dupuis) [660386]
- [scsi] qla2xxx: set right ret val in qla2xxx_eh_abort (Chad Dupuis) [660386]
- [scsi] qla2xxx: set FCP prio info to firmware before IOs (Chad Dupuis) [660386]
- [scsi] qla2xxx: Memory wedge with peg_halt test in loop (Chad Dupuis) [660386]
- [scsi] qla2xxx: populate FCP_PRIO loc for no flt case (Chad Dupuis) [660386]
- [scsi] qla2xxx: avoid SCSI host_lock dep in queuecommand (Chad Dupuis) [660386]
- [scsi] qla2xxx: drop srb ref before wait for completion (Chad Dupuis) [660386]
- [scsi] qla2xxx: log FCP priority data messages (Chad Dupuis) [660386]
- [scsi] qla2xxx: add sysfs node for board temperature (Chad Dupuis) [660386]
- [scsi] qla2xxx: fix check for need quiescence state (Chad Dupuis) [660386]
- [scsi] qla2xxx: clear local rport refs on timeout from FC (Chad Dupuis) [660386]
- [scsi] qla2xxx: remove unwanted check for bad spd (Chad Dupuis) [660386]
- [scsi] qla2xxx: no continuous log when dontreset is set (Chad Dupuis) [660386]
- [scsi] qla2xxx: quiescence mode support for ISP82xx (Chad Dupuis) [660386]
- [virtio] console: no device_destroy on port device (Amit Shah) [681179]
- [virtio] console: don't access vqs if device unplugged (Amit Shah) [681179]
- [virtio] pci: fix config change oops w/no driver loaded (Amit Shah) [681179]
- [xen] hap: preserve domain context (Radim Krcmar) [678571]

* Mon Mar 07 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-247.el5]
- [mm] set barrier and send tlb flush to all affected cpus (Prarit Bhargava) [675793]
- [misc] vdso: export wall_to_monotonic (Prarit Bhargava) [675727]
- [mm] add vzalloc and vzalloc_node helpers (Neil Horman) [681303]
- [fs] add lockd endianness annotations (Jeff Layton) [526829]
- [misc] add key_revoke() dummy for KEYS=n (Jeff Layton) [640891]
- [fs] nfs: Fix a use-after-free case in nfs_async_rename() (Jeff Layton) [511901]
- [fs] nfs: make sillyrename an async operation (Jeff Layton) [511901]
- [fs] nfs: move nfs_sillyrename to unlink.c (Jeff Layton) [511901]
- [fs] nfs: standardize the rename response container (Jeff Layton) [511901]
- [fs] nfs: standardize the rename args container (Jeff Layton) [511901]
- [scsi] scsi_dh_emc: Set request flags consistently (Dave Wysochanski) [670367]
- [i2c] i2c-i801: Add PCI idents for Patsburg 'IDF' devices (David Milburn) [651513]
- [i2c] i2c-i801: Handle multiple instances properly (David Milburn) [651513]
- [i2c] i2c-i801: Don't use block buffer for block writes (David Milburn) [651513]
- [i2c] i2c-i801: Fix handling of error conditions (David Milburn) [651513]
- [i2c] i2c-i801: Rename local variable temp to status (David Milburn) [651513]
- [i2c] i2c-i801: Properly report bus arbitration loss (David Milburn) [651513]
- [i2c] i2c-i801: Remove verbose debugging messages (David Milburn) [651513]
- [i2c] i2c-i801: Implement I2C block read support (David Milburn) [651513]
- [i2c] i2c-i801: Clear special mode bits as needed (David Milburn) [651513]
- [i2c] i2c-i801: More explicit names for chip features (David Milburn) [651513]
- [i2c] i2c-i801: Use the internal 32-byte buffer on ICH4+ (David Milburn) [651513]
- [i2c] i2c-i801: Various cleanups (David Milburn) [651513]
- [fs] xfs: disable CONFIG_XFS_DEBUG on kernel-debug (Dave Chinner) [658012]
- [fs] xfs: remove cmn_err log buffer and lock (Dave Chinner) [658012]
- [fs] fix select/poll timeout overflow (Bob Picco) [591607]
- [x86_64] Use u32, not long, to set reset vector back to 0 (Don Zickus) [675258]
- [net] sctp: fix race allowing access before full init (Neil Horman) [465876]
- [xen] gdbsx: hypervisor part backport (Radim Krcmar) [678618]
- [xen] add arch/x86/debug.c, debugger routines (Radim Krcmar) [678618]
- [xen] x86/vmx: making TRAP_debug and TRAP_int3 useful (Radim Krcmar) [678618]

* Tue Mar 01 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-246.el5]
- [net] bridge: restore ebt ksym versions (Herbert Xu) [626659]
- [net] bridge: Fix mglist corruption (Herbert Xu) [506630]
- [net] Fix IGMP3 report parsing (Herbert Xu) [506630]
- [net] bridge: Fix IGMPv3 report parsing (Herbert Xu) [506630]
- [net] bridge: Fix skb leak in multicast TX parse fail (Herbert Xu) [506630]
- [net] bridge: Fix OOM crash in deliver_clone (Herbert Xu) [506630]
- [net] bridge: Make first arg to deliver_clone const (Herbert Xu) [506630]
- [net] bridge: Fix build error w/IGMP_SNOOPING not enabled (Herbert Xu) [506630]
- [net] bridge: Add multicast count/interval sysfs entries (Herbert Xu) [506630]
- [net] bridge: Add hash elasticity/max sysfs entries (Herbert Xu) [506630]
- [net] bridge: Add multicast_snooping sysfs toggle (Herbert Xu) [506630]
- [net] bridge: Add multicast_router sysfs entries (Herbert Xu) [506630]
- [net] bridge: Add multicast data-path hooks (Herbert Xu) [506630]
- [net] bridge: Add multicast start/stop hooks (Herbert Xu) [506630]
- [net] bridge: Add multicast forwarding functions (Herbert Xu) [506630]
- [net] bridge: Move NULL mdb check into br_mdb_ip_get (Herbert Xu) [506630]
- [net] bridge: ensure br_multicast_query error path unlock (Herbert Xu) [506630]
- [net] bridge: Fix RCU race in br_multicast_stop (Herbert Xu) [506630]
- [net] bridge: Use RCU list primitive in __br_mdb_ip_get (Herbert Xu) [506630]
- [net] bridge: cleanup: remove unneed check (Herbert Xu) [506630]
- [net] bridge: depends on INET (Herbert Xu) [506630]
- [net] bridge: Make IGMP snooping depend upon BRIDGE. (Herbert Xu) [506630]
- [net] bridge: Add core IGMP snooping support (Herbert Xu) [506630]
- [net] bridge: Fix br_forward crash in promiscuous mode (Herbert Xu) [506630]
- [net] bridge: Split may_deliver/deliver_clone out (Herbert Xu) [506630]
- [net] bridge: Use BR_INPUT_SKB_CB on xmit path (Herbert Xu) [506630]
- [net] bridge: Avoid unnecessary clone on forward path (Herbert Xu) [506630]
- [net] bridge: Allow tail-call on br_pass_frame_up (Herbert Xu) [506630]
- [net] bridge: Do br_pass_frame_up after other ports (Herbert Xu) [506630]
- [net] bridge: Kill clone argument to br_flood_* (Herbert Xu) [506630]
- [net] Add netdev_alloc_skb_ip_align() helper (Herbert Xu) [506630]
- [fs] partitions: Validate map_count in Mac part tables (Danny Feng) [679284] {CVE-2011-1010}
- [fs] nfs: Only increment seqid for cmds seen by server (Sachin Prabhu) [651409]
- [scsi] ipr: fix a race on multiple configuration changes (Steve Best) [651429]
- [misc] vmware: increase apic_calibration_diff to 10000 (Prarit Bhargava) [665197]
- [net] tun: introduce tun_file (Michael S. Tsirkin) [672619]
- [virt] xen blktap: bump MAX_TAP_DEV from 100 to 256 (Laszlo Ersek) [452650]
- [fs] nfs: Too many GETATTR/ACCESS calls after direct I/O (Jeff Layton) [626974]
- [net] bonding: fix add/remove of slaves when master down (Flavio Leitner) [671238]
- [net] sctp: make sctp_ctl_sock_init try IPv4 if v6 fails (Jiri Pirko) [674175]
- [net] Fix netdev_run_todo dead-lock (Jiri Pirko) [679487]
- [net] niu: Fix races between up/down and get_stats (Jiri Pirko) [679407]
- [misc] introduce ACCESS_ONCE (Jiri Pirko) [679407]
- [x86] fix AMD family 0x15 guest boot issue on 64-bit host (Frank Arnold) [667234]
- [sound] alsa: cache mixer values on usb-audio devices (Don Zickus) [678074]
- [xen] prevent cross-vendor migration of HVM domains (Paolo Bonzini) [621916]
- [xen] new domctl to get 1 record from HVM save context (Michal Novotny) [674514]

* Fri Feb 18 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-245.el5]
- [block] cciss: version bump (Tomas Henzl) [635143]
- [block] cciss: add option to enforce simple mode (Tomas Henzl) [635143]
- [block] cciss: patch to make kdump work in rhel5 (Tomas Henzl) [635143]
- [block] cciss: cleanup warnings (Tomas Henzl) [635143]
- [block] cciss: patch to support kdump on new controllers (Tomas Henzl) [635143]
- [block] cciss: factor out code to find max commands (Tomas Henzl) [635143]
- [block] cciss: split out cciss_defs (Tomas Henzl) [635143]
- [block] cciss: scsi tape updates (Tomas Henzl) [635143]
- [block] cciss: remove fail_all_cmds (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_passthru (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_getdrivver (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_getfirmver (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_getbustypes (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_getheartbeat (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_setnodename (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_getnodename (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_setintinfo (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_getintinfo (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_getpciinfo (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_reset_devices (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_find_cfg_addrs (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_wait_for_mode_change_ack (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_p600_dma_prefetch_quirk (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_enable_scsi_prefetch (Tomas Henzl) [635143]
- [block] cciss: factor out CISS_signature_present (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_find_board_params (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_find_cfgtables (Tomas Henzl) [635143]
- [block] cciss: factor out wait_for_board_ready (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_find_memory_BAR (Tomas Henzl) [635143]
- [block] cciss: remove board_id from cciss_interrupt_mode (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_board_disabled (Tomas Henzl) [635143]
- [block] cciss: factor out cciss_lookup_board_id (Tomas Henzl) [635143]
- [block] cciss: save off pdev struct early (Tomas Henzl) [635143]
- [block] cciss: add performant mode support (Tomas Henzl) [635143]
- [block] cciss: new controller support (Tomas Henzl) [635143]
- [block] cciss: remove generic sa support (Tomas Henzl) [635143]
- [block] cciss: copyright update (Tomas Henzl) [635143]
- [x86_64] vdso: fix gtod via export of sysctl_vsyscall (Prarit Bhargava) [673616]
- [pci] msi: remove infiniband compat code (Prarit Bhargava) [636260]
- [pci] msi: remove pci_save_msi|x_state() functions (Prarit Bhargava) [636260]
- [pci] msi: use msi_desc save areas in msi state functions (Prarit Bhargava) [636260]
- [pci] msi: use msi_desc save areas in drivers/pci code (Prarit Bhargava) [636260]
- [misc] kdump: fixup mcp55 quick to skip non HT devices (Neil Horman) [477032]
- [security] selinux: properly handle empty tty_files list (Lachlan McIlroy) [674226]
- [fs] xfs: fix double free of log tickets (Lachlan McIlroy) [657166]
- [fs] ext4: protect inode bitmap clearing w/ spinlock (Lukas Czerner) [663563]
- [fs] procfs: fix numbering in /proc/locks (Jerome Marchand) [622647]
- [fs] seq_file: Introduce the seq_open_private() (Jerome Marchand) [622647]
- [fs] Rework /proc/locks w/seq_files and seq_list helpers (Jerome Marchand) [622647]
- [fs] common helpers for seq_files working with list_heads (Jerome Marchand) [622647]
- [fs] nfs: Remove incorrect do_vfs_lock message (Jeff Layton) [632399]
- [fs] nfs: allow redirtying of a completed unstable write (Jeff Layton) [648657]
- [fs] nfsd4: fix seqid on lock req incompat w/open mode (Jeff Layton) [517629]
- [net] sunrpc: a better way to set tcp_slot_table_entries (Harshula Jayasuriya) [654293]
- [x86] Convert BUG() to use unreachable() (Dean Nelson) [677396]
- [s390] Convert BUG() to use unreachable() (Dean Nelson) [677396]
- [powerpc] Convert BUG() to use unreachable() (Dean Nelson) [677396]
- [misc] add support for __builtin_unreachable (Dean Nelson) [677396]
- [fs] xfs: more swap extent fixes for dynamic fork offsets (Dave Chinner) [661300]
- [fs] xfs: handle dynamic fork offsets in xfs_swap_extents (Dave Chinner) [661300]
- [lib] fix vscnprintf() if @size is == 0 (Anton Arapov) [667327]
- [net] netpoll: fix use after free (Amerigo Wang) [556811]
- [net] netpoll: fix a softirq warning (Amerigo Wang) [556811]
- [net] netconsole: Introduce netconsole netdev notifier (Amerigo Wang) [556811]
- [net] bridge: support netpoll over bridge (Amerigo Wang) [556811]
- [net] netconsole: Use netif_running() in write_msg() (Amerigo Wang) [556811]
- [net] netconsole: Simplify boot/module option setup logic (Amerigo Wang) [556811]
- [net] netconsole: Remove bogus check (Amerigo Wang) [556811]
- [net] netconsole: Cleanups, codingstyle, prettyfication (Amerigo Wang) [556811]
- [net] netpoll: setup error handling (Amerigo Wang) [556811]
- [char] virtio_console: fix memory leak (Amit Shah) [656836]
- [media] dvb: fix av7110 negative array offset (Mauro Carvalho Chehab) [672402] {CVE-2011-0521}

* Mon Feb 14 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-244.el5]
- [message] mptfusion: add required mptctl_release call (Tomas Henzl) [660871]
- [fs] gfs2: no exclusive glocks on mmapped read-only fs (Steven Whitehouse) [672724]
- [scsi] ibmvfc: Driver version 1.0.9 (Steve Best) [651885]
- [scsi] ibmvfc: Handle Virtual I/O Server reboot (Steve Best) [651885]
- [scsi] ibmvfc: Log link up/down events (Steve Best) [651885]
- [scsi] ibmvfc: Fix rport add/delete race oops (Steve Best) [651885]
- [scsi] ibmvfc: Remove stale param to ibmvfc_init_host (Steve Best) [651885]
- [scsi] ibmvfc: Fix locking in ibmvfc_remove (Steve Best) [651885]
- [scsi] ibmvfc: Fixup TMF response handling (Steve Best) [651885]
- [fs] nfs: pure nfs client performance using odirect (Jeff Layton) [643441]
- [mm] fix install_special_mapping skips security_file_mmap (Frantisek Hrbata) [662197] {CVE-2010-4346}
- [virt] xen: setup memory zones the same way as native (Andrew Jones) [525898]
- [s390] qeth: wait for recovery finish in open function (Hendrik Brueckner) [668844]
- [s390] cio: fix unuseable device after offline operation (Hendrik Brueckner) [668842]
- [s390] qdio: use proper QEBSM operand for SIGA-{R,S} (Hendrik Brueckner) [668464]
- [s390] qdio: zfcp stall with > 63 active qdio devices (Hendrik Brueckner) [662134]
- [s390] qeth: enable VIPA add/remove for offline devices (Hendrik Brueckner) [661106]
- [s390] hvc_iucv: no iucv_unregister if register failed (Hendrik Brueckner) [661021]
- [s390] qeth: l3 add vlan hdr in passthru frames (Hendrik Brueckner) [659822]
- [s390] cio: suppress chpid event in case of config error (Hendrik Brueckner) [668838]
- [xen] x86: fix guest memmove in __pirq_guest_unbind (Yufang Zhang) [659642]

* Mon Feb 07 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-243.el5]
- [scsi] device_handler: fix alua_rtpg port group id check (Mike Snitzer) [669961]
- [net] cnic: fix big endian bug with device page tables (Steve Best) [669527]
- [fs] only return EIO once on msync/fsync after IO failure (Rik van Riel) [652369]
- [net] bonding: convert netpoll tx blocking to a counter (Neil Horman) [659594]
- [net] conntrack: fix oops specify hashsize module option (Neil Horman) [667810]
- [misc] mce: reduce thermal throttle message severity (Matthew Garrett) [666972]
- [acpi] reduce the number of resched IPIs (Matthew Garrett) [653398]
- [virt] xen: make netfront driver return info to ethtool (Laszlo Ersek) [643292]
- [virt] xen: synch arch/i386/pci/irq-xen.c (Laszlo Ersek) [623979]
- [virt] netback: take lock when removing entry from list (Laszlo Ersek) [648854]
- [virt] xen: make netloop permanent (Laszlo Ersek) [567540]
- [net] virtio: add get_drvinfo support to virtio_net (Laszlo Ersek) [645646]
- [virt] xen: implement get_drvinfo for netloop driver (Laszlo Ersek) [643872]
- [virt] xen: implement get_drvinfo for netback driver (Laszlo Ersek) [643872]
- [net] virtio_net: update trans_start properly (Jiri Olsa) [653828]
- [net] gro: reset dev pointer on reuse (Andy Gospodarek) [600350]
- [net] atl1e: add new Atheros GbE NIC driver (Bob Picco) [465379]
- [fs] gfs2: support for growing a full filesytem (Benjamin Marzinski) [661904]
- [fs] gfs2: reserve more blocks for transactions (Benjamin Marzinski) [637970]
- [fs] gfs2: add fallocate support (Benjamin Marzinski) [626585]
- [fs] nfs: break nfsd v4 lease on unlink, link, and rename (J. Bruce Fields) [610093]
- [fs] nfs: break lease on nfsd v4 setattr (J. Bruce Fields) [610093]
- [net] ipv6: add missing support for local_reserved_ports (Amerigo Wang) [669603]
- [misc] add ignore_loglevel kernel parameter (Amerigo Wang) [662102]
- [misc] add bootmem_debug kernel parameter (Amerigo Wang) [662102]
- [xen] unmask ISVM bit on SVM guests (Paolo Bonzini) [665972]
- [xen] add MSR_IA32_THERM_CONTROL for dom0 CPU throttling (Laszlo Ersek) [614007]

* Mon Jan 31 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-242.el5]
- [net] be2net: fix missing trans_start update (Ivan Vecera) [671595]
- [message] mptfusion: release resources in error path (Tomas Henzl) [648413]
- [fs] gfs2: fix recovery stuck on transaction lock (Robert S Peterson) [553803]
- [net] fix unix socket local dos (Neil Horman) [656760] {CVE-2010-4249}
- [net] core: clear allocs for privileged ethtool actions (Jiri Pirko) [672433] {CVE-2010-4655}
- [net] limit socket backlog add operation to prevent DoS (Jiri Pirko) [657309] {CVE-2010-4251}
- [block] fix accounting bug on cross partition merges (Jerome Marchand) [646816]
- [fs] nfs: fix units bug causing hang on nfsv4 recovery (J. Bruce Fields) [659243]
- [fs] nfs: set source addr when v4 callback is generated (J. Bruce Fields) [659255]
- [char] virtio: Wake console outvq on host notifications (Amit Shah) [673459]
- [net] ipv4: fix IGMP behavior on v2/v3 query responses (Jiri Pirko) [634276]
- [net] ipv6: honor SO_BINDTODEVICE parameter when routing (Jiri Olsa) [568881]

* Tue Jan 25 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-241.el5]
- [net] tcp: fix shrinking windows with window scaling (Jiri Pirko) [627496]
- [virt] xen: no enable extended PCI cfg space via IOports (Don Dutile) [661478]
- [fs] gfs2: remove iopen glocks from cache on delete fail (Benjamin Marzinski) [666080]
- [char] virtio: make console port names a KOBJ_ADD event (Amit Shah) [669909]
- [net] e1000: Avoid unhandled IRQ (Dean Nelson) [651512]
- [net] e1000: fix screaming IRQ (Dean Nelson) [651512]

* Wed Jan 19 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-240.el5]
- [acpi] bus: check if list is empty before kfree()ing it (Matthew Garrett) [670373]
- [net] ipv6: fragment local tunnel IPSec6 pkts if needed (Herbert Xu) [661110]
- [block] cciss: fix null pointer problem in tur usage (Tomas Henzl) [664592]

* Tue Jan 04 2011 Jarod Wilson <jarod@redhat.com> [2.6.18-239.el5]
- [scsi] megaraid: give FW more time to recover from reset (Tomas Henzl) [665427]
- [fs] gfs2: fix statfs error after gfs2_grow (Robert S Peterson) [660661]
- [mm] prevent file lock corruption using popen(3) (Larry Woodman) [664931]
- [net] sctp: fix panic from bad socket lock on icmp error (Neil Horman) [665477] {CVE-2010-4526}

* Sun Dec 19 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-238.el5]
- [net] bnx2: remove extra call to pci_map_page (John Feeney) [663509]
- [fs] nfs: set lock_context field in nfs_readpage_sync (Jeff Layton) [663853]

* Mon Dec 13 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-237.el5]
- [block] fully zeroize request struct in rq_init (Rob Evers) [662154]
- [scsi] qla4xxx: update to 5.02.04.02.05.06-d0 (Chad Dupuis) [656999]
- [scsi] qla4xxx: make get_sys_info function return void (Chad Dupuis) [656999]
- [scsi] qla4xxx: don't default device to FAILED state (Chad Dupuis) [656999]
- [scsi] qla4xxx: mask bits in F/W Options during init (Chad Dupuis) [656999]
- [scsi] qla4xxx: update to 5.02.04.01.05.06-d0 (Chad Dupuis) [661768]
- [scsi] qla4xxx: disable irq instead of req pci_slot_reset (Chad Dupuis) [661768]
- [scsi] qla4xxx: no device add until scsi_add_host success (Chad Dupuis) [661768]
- [fs] nfs: set lock_context field in nfs_writepage_sync (Jeff Layton) [660580]
- [scsi] bfa: fix crash reading driver sysfs statistics (Rob Evers) [659880] {CVE-2010-4343}
- [misc] cpufeature: avoid corrupting cpuid vendor id (Matthew Garrett) [568751]
- [char] drm: don't set signal blocker on master process (Dave Airlie) [570604]
- [fs] nfs: remove problematic calls to nfs_clear_request (Jeff Layton) [656492]
- [fs] nfs: handle alloc failures in nfs_create_request (Jeff Layton) [656492]
- [fs] nfs: clean up nfs_create_request (Jeff Layton) [656492]
- [net] forcedeth: fix race condition in latest backport (Ivan Vecera) [658434]
- [net] cxgb3: fix read of uninitialized stack memory (Jay Fenlason) [633155] {CVE-2010-3296}
- [net] tg3: increase jumbo flag threshold (John Feeney) [660506]
- [net] s2io: fix netdev initialization failure (Bob Picco) [654948]
- [net] igb: only use vlan_gro_receive if vlans registered (Stefan Assmann) [660190] {CVE-2010-4263}
- [net] ipv6: try all routers with unknown reachable state (Thomas Graf) [661393]
- [misc] kernel: fix address limit override in OOPS path (Dave Anderson) [659571] {CVE-2010-4258}

* Mon Dec 06 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-236.el5]
- [powerpc] support DLPAR remove operations (Steve Best) [655089]
- [net] igb: fix tx packet count (Stefan Assmann) [658801]
- [usb] serial: new driver MosChip MCS7840 (Stefan Assmann) [574507]
- [fs] exec: copy fixes into compat_do_execve paths (Oleg Nesterov) [625694] {CVE-2010-4243}
- [fs] exec: make argv/envp memory visible to oom-killer (Oleg Nesterov) [625694] {CVE-2010-4243}
- [misc] binfmts: kill bprm->argv_len (Oleg Nesterov) [625694] {CVE-2010-4243}
- [mm] backport upstream stack guard page /proc reporting (Larry Woodman) [643426]
- [mm] add guard page for stacks that grow upwards (Johannes Weiner) [630563]
- [net] tipc: fix information leak to userland (Jiri Pirko) [649892] {CVE-2010-3877}
- [sound] ALSA: fix sysfs unload and OSS mixer mutex issues (Jaroslav Kysela) [652165]
- [net] tg3: fix 5719 bugs (John Feeney) [657097]
- [net] bnx2: update firmware to 6.0.x (John Feeney) [644438]
- [redhat] configs: add CONFIG_SECURITY_DMESG_RESTRICT (Frantisek Hrbata) [653250]
- [misc] kernel: restrict unprivileged access to dmesg (Frantisek Hrbata) [653250]
- [virt] xen: don't allow blkback virtual CDROM device (Andrew Jones) [635638] {CVE-2010-4238}
- Revert: [xen] cd-rom drive does not recognize new media (Andrew Jones) [635638] {CVE-2010-4238}
- [net] qlge: fix deadlock when interface is going down (Chad Dupuis) [654420]
- [net] qlge: reset chip before freeing buffers (Chad Dupuis) [654420]
- [net] qlge: restore vlan setting during ql_adapter_up (Chad Dupuis) [654420]
- [scsi] qla4xxx: Update version to V5.02.04.00.05.06-d0 (Chad Dupuis) [656999]
- [scsi] qla4xxx: Document Driver Versioning Scheme (Chad Dupuis) [656999]
- [scsi] qla4xxx: Updated the Copyright header to 2010 (Chad Dupuis) [656999]
- [scsi] qla4xxx: don't process devices untill probe done (Chad Dupuis) [656999]
- [scsi] qla4xxx: free DDB when application calls for it (Chad Dupuis) [656999]
- [scsi] qla4xxx: memory wedge with peg_halt test in loop (Chad Dupuis) [656999]
- [scsi] qla4xxx: clear AF_FW_RECOVERY flag after reset (Chad Dupuis) [656999]
- [scsi] qla4xxx: fix new IP address caching (Chad Dupuis) [656999]
- [scsi] qla4xxx: replace hard coded values with macros (Chad Dupuis) [656999]
- [scsi] qla4xxx: mark dev FAILED on 82XX init failure (Chad Dupuis) [656999]
- [scsi] qla4xxx: fail init if pci mem write fails (Chad Dupuis) [656999]
- [scsi] qla4xxx: ensure proper qla4xxx_conn_start state (Chad Dupuis) [656999]
- [scsi] qla4xxx: do not process interrupts unconditionally (Chad Dupuis) [656999]
- [scsi] qla4xxx: fix add w/iscsi2_create_conn not done yet (Chad Dupuis) [656999]
- [scsi] qla4xxx: no fw hung if reset retry is in progress (Chad Dupuis) [656999]
- [scsi] qla4xxx: correct use of cmd->host_scribble (Chad Dupuis) [656999]
- [scsi] qla4xxx: msi init request_irq parameter usage fix (Chad Dupuis) [656999]
- [scsi] qla4xxx: cleanup qla4xxx_wait_for_hba_online (Chad Dupuis) [656999]
- [scsi] qla4xxx: grab hardware_lock before accessing srb (Chad Dupuis) [656999]
- [scsi] qla4xxx: remove unwanted check for bad spd (Chad Dupuis) [656999]
- [scsi] qla4xxx: update AER support for ISP82XX (Chad Dupuis) [656999]
- [scsi] qla4xxx: clear rom lock if firmware died holding (Chad Dupuis) [656999]
- [scsi] qla4xxx: CRB Register for Request Queue in-pointer (Chad Dupuis) [656999]
- [scsi] qla4xxx: dump mailbox registers on System Error (Chad Dupuis) [656999]
- [scsi] qla4xxx: add support for 8130/8131 AENs (Chad Dupuis) [656999]
- [scsi] qla4xxx: fix seconds_since_last_heartbeat reset (Chad Dupuis) [656999]
- [scsi] qla4xxx: no wait for outstanding command complete (Chad Dupuis) [656999]
- [scsi] qla4xxx: free_irqs on failed initialize_adapter (Chad Dupuis) [656999]
- [virt] xen: fix netback hotplug regression in xenbus fix (Laszlo Ersek) [635999]
- [xen] fix 64-bit PV guest user mode segv crashing host (Paolo Bonzini) [658354] {CVE-2010-4255}

* Wed Dec 01 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-235.el5]
- [net] filter: fix backport error in prior filter fix (Jarod Wilson) [651703]

* Tue Nov 30 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-234.el5]
- [s390] vmlogrdr: purge after recording is switched off (Hendrik Brueckner) [653479]
- [wireless] ieee80211: fix deauthentication (Stanislaw Gruszka) [644367]
- [wireless] zd1211rw: fix associate after disassociate (Stanislaw Gruszka) [644367]
- [fs] proc: fix NULL ->i_fop oops (Steve Best) [655083]
- [scsi] lpfc: Update version to 8.2.0.87.1p (Rob Evers) [655119]
- [scsi] lpfc: set heartbeat timer off by default (Rob Evers) [655119]
- [scsi] lpfc: fix NULL deref duing allocation failure (Rob Evers) [655119]
- [scsi] lpfc: fix remote SLI4 firmware download data bug (Rob Evers) [655119]
- [scsi] lpfc: fix FDMI_DID login failure after link bounce (Rob Evers) [655119]
- [scsi] lpfc: handle CVL after nameserver PLOGI timeouts (Rob Evers) [655119]
- [scsi] lpfc: cleanup mbox cmds in mboxq_cmpl if CVL rcvd (Rob Evers) [655119]
- [misc] posix-cpu-timers: workaround for mt exec problems (Oleg Nesterov) [656266]
- [fs] setup_arg_pages: diagnose excessive argument size (Oleg Nesterov) [645227]
- [net] bnx2x: force interrupt mode for iscsi unset mac (Michal Schmidt) [655885]
- [scsi] bnx2i: allow to abort connect if request times out (Mike Christie) [653991]
- [scsi] bnx2i: fix remote TCP RST handling for 570X (1g) (Mike Christie) [653991]
- [scsi] bnx2i: fix a cid leak issue for 5771X (10g) (Mike Christie) [653991]
- [scsi] bnx2i: fix endian bug in TMF LUN cmd send (Mike Christie) [653991]
- [misc] prevent divide by 0 in the kernel during boot (Larry Woodman) [508140]
- [net] filter: make sure filters don't read uninit memory (Jiri Pirko) [651703] {CVE-2010-4158}
- [net] inet_diag: make sure we run audited bytecode (Jiri Pirko) [651267]
- [net] limit sendto/recvfrom/iovec total length to INT_MAX (Jiri Pirko) [645872] {CVE-2010-3859}
- [bluetooth] hci_ldisc: fix missing NULL check (Jarod Wilson) [655666]
- [net] be2net: avoid firmware update if interface not open (Ivan Vecera) [651948]
- [ipc] shm: fix information leak to userland (Danny Feng) [648687] {CVE-2010-4072}
- [ipc] initialize struct memory to 0 for compat functions (Danny Feng) [648693] {CVE-2010-4073}
- [net] netxen: don't use reset_devices, it may go away (Chad Dupuis) [643254]
- [net] netxen: fix kdump (Chad Dupuis) [643254]
- [net] qlcnic: avoid reset_devices, it may become obsolete (Chad Dupuis) [656008]
- [net] qlcnic: fix for kdump (Chad Dupuis) [656008]
- [pci] block on access to temporarily unavailable device (Chad Dupuis) [656008]
- [serial] serial_core: clean data before filling it (Mauro Carvalho Chehab) [648701] {CVE-2010-4075}
- [edac] i7core_edac: return -ENODEV if dev already probed (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: properly terminate pci_dev_table (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: fix PCI refcounting on reloads (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: fix refcount error at PCI devices (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: safe to unregister mci when mci NULL (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: fix an oops at i7core probe (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: remove unused member in i7core_pvt (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: remove unused arg in get_dimm_config (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: reduce args of i7core_register_mci (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: use saved pointers (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: check probe counter in i7core_remove (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: call pci_dev_put on alloc failure (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: fix error path of i7core_register_mci (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: fix line order in i7core_register_mci (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: always do get/put for all devices (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: ensure edac pci handler release (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: introduce free_i7core_dev (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: introduce alloc_i7core_dev (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: reduce args of i7core_get_onedevice (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: fix the logic in i7core_remove (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: don't do legacy PCI probe by default (Mauro Carvalho Chehab) [651869]
- [edac] edac_core: print debug messages at release calls (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: remove PCI devices from devices list (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: MCE NMI handling should stop first (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: improve debug register/remove errors (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: move #if PAGE_SHIFT to edac_core.h (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: terminate the group of udimm counters (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: mark const static vars as such (Mauro Carvalho Chehab) [651869]
- [edac] i7core_edac: move static vars to the top of file (Mauro Carvalho Chehab) [651869]
- [virt] xen: add bounds req-process loop in blkback/blktap (Laszlo Ersek) [654546] {CVE-2010-4247}
- [virt] xen: don't leak dev refs on bad xenbus transitions (Laszlo Ersek) [635999] {CVE-2010-3699}
- [mm] fix possible integer overflow in mm/fremap.c (Larry Woodman) [637047]
- [misc] futex: replace LOCK_PREFIX in futex.h (Jiri Pirko) [633176] {CVE-2010-3086}

* Mon Nov 22 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-233.el5]
- [scsi] mpt2sas: use sas device list for enclosure id (Tomas Henzl) [652284]
- [scsi] ipr: fix mailbox register definition and add delay (Steve Best) [654446]
- [scsi] ipr: fix lun assignment and comparison (Steve Best) [654446]
- [powerpc] add AT_BASE_PLATFORM to Aux Vector and power7 (Steve Best) [652279]
- [infiniband] ehea: use shca_list_lock spinlock (Steve Best) [613797]
- [powerpc] kdump: CPUs assume context of oopsing CPU (Steve Best) [509792]
- [scsi] lpfc: Update version for 8.2.0.87 driver release (Rob Evers) [649489]
- [scsi] lpfc: add handling SLI4 unsolicted ELS RTV (Rob Evers) [649489]
- [scsi] lpfc: add handling ECHO response support (Rob Evers) [649489]
- [scsi] lpfc: add handling of SLI4 unsolicted ELS (Rob Evers) [649489]
- [scsi] lpfc: fix locking for security mailbox commands (Rob Evers) [649489]
- [scsi] lpfc: abort I/Os and wait on XRI in SLI4 unload (Rob Evers) [649489]
- [scsi] lpfc: handle devloss timeout in FIP engine (Rob Evers) [649489]
- [scsi] lpfc: fix crashes on NULL pnode dereference (Rob Evers) [649489]
- [net] cnic: Add cnic_free_uio (Mike Christie) [651287]
- [net] cnic: Add cnic_uio_dev struct (Mike Christie) [651287]
- [net] cnic: Add cnic_free_uio (Mike Christie) [651287]
- [net] cnic: Fine-tune ring init code (Mike Christie) [651287]
- [misc] fix dirty_bytes sysctl name (Larry Woodman) [635782]
- [fs] procfs: acquire inode mutex around llseek operation (Lachlan McIlroy) [644726]
- [virt] netfront: default to copying instead of flipping (Laszlo Ersek) [653262]
- [virt] netback: don't balloon up for copying receivers (Laszlo Ersek) [653501]
- [net] rds: fix rds_iovec page count overflow (Jiri Pirko) [647422]
- [net] virtio_net: add link status handling (Jason Wang) [649573]
- [net] be2net: Update be2net to version 2.102.512r (Ivan Vecera) [647259]
- [char] watchdog: another LPC Controller ID for Patsburg (David Milburn) [570868]
- [misc] another LPC Controller ID for Intel Patsburg PCH (David Milburn) [570868]
- [i2c] i2c-i801: Add Intel Patsburg device ID (David Milburn) [570868]
- [misc] pci: update Intel Patsburg defines (David Milburn) [570868]
- [misc] x86/PCI irq and pci_ids for Intel Patsburg Devices (David Milburn) [570868]
- [sound] ALSA HD Audio for Intel Patsburg DeviceIDs (David Milburn) [570868]
- [char] watchdog: TCO Watchdog for Intel Patsburg Devices (David Milburn) [570868]
- [ata] ahci: AHCI and RAID mode for Intel Patsburg Devices (David Milburn) [570868]
- [ata] ata_piix: IDE Mode SATA for Intel Patsburg Devices (David Milburn) [570868]
- [net] fix deadlock in sock_queue_rcv_skb (Danny Feng) [652537]
- [scsi] qla2xxx: check null fcport in _queuecommands (Chad Dupuis) [644863]
- [net] qlcnic: Fix missing error codes (Chad Dupuis) [637194]
- [usb] wacom: add support for Cintiq 21UX2 (Aristeu Rozanski) [652731]
- [xen] hvm: add HVMOP_get_time hypercall (Paolo Bonzini) [638082]

* Mon Nov 15 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-232.el5]
- [scsi] mpt2sas: use correct pci_resource_flag for compare (Tomas Henzl) [649885]
- [sound] rme9652: prevent reading uninitialized stack mem (Stanislaw Gruszka) [648709 648714] {CVE-2010-4080 CVE-2010-4081}
- [net] packet: fix information leak to userland (Jiri Pirko) [649898]
- [ipc] sys_semctl: fix kernel stack leakage (Danny Feng) [648722] {CVE-2010-4083}
- [misc] kernel: remove yield from stop_machine paths (Oleg Nesterov) [634454]
- [fs] dlm: reduce cond_resched during send (David Teigland) [604139]
- [fs] dlm: use TCP_NODELAY (David Teigland) [604139]
- [fs] nfs: fix a referral error Oops (Steve Dickson) [556886]
- [fs] gfs2: fix race in unlinked inode deallocation (Robert S Peterson) [643165]
- [scsi] retry on DID_REQUEUE errors (Mike Christie) [627836]
- [net] sctp: do not reset packet during sctp_packet_config (Jiri Pirko) [637867]
- [net] bnx2: add AER support (John Feeney) [617024]
- [net] bonding: no lock on copy/clear VLAN list on slave (Andy Gospodarek) [627974]
- [scsi] gdth: prevent integer overflow in ioc_general (Frantisek Hrbata) [651176]

* Mon Nov 08 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-231.el5]
- [scsi] scsi_dh_alua: remove IBM Power Virtual SCSI ALUA (Steve Best) [567292]
- [fs] gfs2: flock (LOCK_EX|LOCK_NB) blocks (Robert S Peterson) [648602]
- [scsi] lpfc: update version for 8.2.0.86 driver release (Rob Evers) [645881]
- [scsi] lpfc: fix race sending FDISC to un-init VPI (Rob Evers) [645881]
- [scsi] lpfc: fix mailbox handling for UNREG_RPI_ALL case (Rob Evers) [645881]
- [kernel] add stop_machine barrier to fix lock contention (Prarit Bhargava) [634454]
- [scsi] bnx2i: fix ip address formatting and oops (Mike Christie) [646708]
- [scsi] be2iscsi: remove premature free of cid (Mike Christie) [640029]
- [fs] proc: make proc pid limits world readable (Jiri Olsa) [611535]
- [ide] atiixp: fix locking hang in ide layer ATIIXP driver (James Leddy) [586482]
- [security] only check mmap_min_addr perms for write (Eric Paris) [623519]
- [ata] sata_sil24: add DID for another adaptec flavor (David Milburn) [640586]
- [s390] cio: prevent panic in I/O cancel function (Hendrik Brueckner) [647807]
- [s390] cio: prevent panic after unexpected I/O interrupt (Hendrik Brueckner) [647502]

* Thu Oct 28 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-230.el5]
- [fs] nfs: fix regression in NFS Direct I/O path (Steve Dickson) [647297]
- [fs] nfs: allow different protocol mounts to same server (Steve Dickson) [460659]
- [scsi] lpfc: update version for 8.2.0.85 driver release (Rob Evers) [639028]
- [scsi] lpfc: fix a BUG_ON in lpfc_abort_handler (Rob Evers) [639028]
- [scsi] lpfc: use pci reset function on driver unload (Rob Evers) [639028]
- [scsi] lpfc: replace some spin_lock_irqs w/spin_locks (Rob Evers) [639028]
- [scsi] lpfc: fail io w/lost frame and target check cond (Rob Evers) [639028]
- [scsi] lpfc: fix abort WQEs for FIP frames (Rob Evers) [639028]
- [scsi] lpfc: update version for 8.2.0.84 driver release (Rob Evers) [639028]
- [scsi] lpfc: unreg all rpi mbox command before unreg vpi (Rob Evers) [639028]
- [scsi] lpfc: make all error values negative (Rob Evers) [639028]
- [scsi] lpfc: remove duplicate code from lpfc_els_retry (Rob Evers) [639028]
- [scsi] lpfc: fix circular spinlock dep w/scsi midlayer (Rob Evers) [639028]
- [scsi] lpfc: update version for 8.2.0.83 driver release (Rob Evers) [639028]
- [scsi] lpfc: fix FLOGI issue with McData4700 FC switch (Rob Evers) [639028]
- [scsi] lpfc: fix possible roundrobin failover failure (Rob Evers) [639028]
- [scsi] lpfc: fix unregister of unused FCF on timeout (Rob Evers) [639028]
- [scsi] lpfc: fix heartbeat timeout during pause test (Rob Evers) [639028]
- [scsi] lpfc: update version for 8.2.0.82 driver release (Rob Evers) [639028]
- [scsi] lpfc: fix lpfc_els_retry delay/retry for PLOGI (Rob Evers) [639028]
- [scsi] lpfc: streamline some spin locks (Rob Evers) [639028]
- [scsi] lpfc: fix lpfc_initial_flogi return on failure (Rob Evers) [639028]
- [scsi] lpfc: fix stray state update issue with new FCF (Rob Evers) [639028]
- [scsi] lpfc: treat FCF prop with different index as error (Rob Evers) [639028]
- [scsi] lpfc: fix misc auth issues on EmulexSecure FC HBA (Rob Evers) [639028]
- [scsi] lpfc: update version for 8.2.0.81 driver release (Rob Evers) [639028]
- [scsi] lpfc: move unload flag earlier in vport delete (Rob Evers) [639028]
- [scsi] lpfc: fix IOCB leak on FDISC completion (Rob Evers) [639028]
- [scsi] lpfc: fix possible crash on non-SLI4 hba (Rob Evers) [639028]
- [scsi] mpt2sas: fix panic w/direct attached SEP (Jarod Wilson) [641086]
- [redhat] spec: clean up rpmbuild kabideps detritus (Jarod Wilson) [644129]
- [net] bnx2: Increase max rx ring size from 1K to 2K (Andy Gospodarek) [640026]
- [net] bnx2: fixup broken NAPI accounting (Andy Gospodarek) [640026]
- [s390] qeth: portno 1 support for OSM-device insufficient (Hendrik Brueckner) [644008]

* Tue Oct 26 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-229.el5]
- [pci] include DL580 G7 in bfsort whitelist (Tony Camuso) [644879]
- [net] igb: fix TX hang when loading igb with max_vfs > 7 (Stefan Assmann) [645284]
- [virt] fix timekeeping_use_tsc check in init_tsc_timer (Prarit Bhargava) [643926]
- [net] bonding: support netconsole over bonded link (Neil Horman) [235343]
- [virt] xen: increase txqueuelen of netback vif devices (Miroslav Rezanina) [539626]
- [sound] core: prevent heap corruption in snd_ctl_new (Jerome Marchand) [638484] {CVE-2010-3442}
- [net] updated drivers need version string updates too (Andy Gospodarek) [635027]
- [misc] softlockup: increase timeout to 60 seconds (Don Zickus) [643707]
- [virt] xen: fix vdso failure under xen pv environment (Danny Feng) [644860]
- [scsi] qla2xxx: fix zero test on array in ql_fc_loopback (Chad Dupuis) [644136]
- [usb] net/catc: change NIC's TX_MAX_BURST, fixes probe (Bob Picco) [637826]
- [virt] console: don't block guest if host doesn't read (Amit Shah) [644735]
- [media] video: remove compat code for VIDIOCSMICROCODE (Mauro Carvalho Chehab) [642471] {CVE-2010-2963}
- [xen] vtd: let IOMMU use another IRQ without conflict (Don Dugger) [575790]
- [net] bonding: correctly process non-linear skbs (Andy Gospodarek) [619070]
- [net] rds: fix local privilege escalation (Eugene Teo) [642898] {CVE-2010-3904}

* Mon Oct 18 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-228.el5]
- [char] tpm: pay attention to IRQ info from PNP in tpm_tis (Stefan Assmann) [636760]
- [misc] cpufreq: add missing cpufreq_cpu_put (Prarit Bhargava) [643080]
- [md] fix softlockup issue waiting for resync to finish (James Paradis) [573106]
- [s390] dasd_eckd: remove PSF order/suborder ioctl check (John Feeney) [565973]
- [fs] xfs: fix speculative allocation beyond eof (Dave Chinner) [638753]

* Tue Oct 12 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-227.el5]
- [net] ixgbe: add option to control interrupt mode (Andy Gospodarek) [571495]
- [md] raid0: fix data corruption on 32-bit w/large storage (Stanislaw Gruszka) [573185]
- [scsi] fix write buffer length in scsi_req_map_sg (Steve Best) [637235]
- [scsi] ipr: back out isr optimization changes (Steve Best) [634213]
- [scsi] ipr: fix rsrc addr format and add attr for dev ID (Steve Best) [634213]
- [fs] jbd2: properly align sized slab caches (Eric Sandeen) [638961]
- [fs] ext4: don't scan/accumulate too many pages (Eric Sandeen) [572930]
- [fs] gfs2: fix fatal filesystem consistency error (Robert S Peterson) [529914]
- [scsi] lpfc: update version for 8.2.0.80 driver release (Rob Evers) [619917]
- [scsi] lpfc: add Security Crypto support to CONFIG_PORT (Rob Evers) [619917]
- [scsi] lpfc: remove unused variables (Rob Evers) [619917]
- [scsi] lpfc: log msg 0318 is a warning, not an error (Rob Evers) [619917]
- [scsi] lpfc: fix bug w/cable swap and non-empty nodelist (Rob Evers) [619917]
- [scsi] lpfc: fix a failure to roundrobin on all FCFs (Rob Evers) [619917]
- [scsi] lpfc: fix heartbeat timeout during fabric reconfig (Rob Evers) [619917]
- [scsi] lpfc: update version for 8.2.0.79 driver release (Rob Evers) [619917]
- [scsi] lpfc: fix a Clear Virtual Link recovery failure (Rob Evers) [619917]
- [scsi] lpfc: clear VFI_REGISTERED flag after UNREG_VFI (Rob Evers) [619917]
- [scsi] lpfc: ignore failure of REG_VPI mbox w/UPD bit set (Rob Evers) [619917]
- [scsi] lpfc: fix ioctl using inactive ndlp for ct resp (Rob Evers) [619917]
- [scsi] lpfc: fix bug w/ndlp not activated post-cable swap (Rob Evers) [619917]
- [scsi] lpfc: add support UPD bit of REG_VPI mailbox cmd (Rob Evers) [619917]
- [scsi] lpfc: fix driver discovery issue after link bounce (Rob Evers) [619917]
- [scsi] lpfc: fix VLAN ID 0xFFF set to reg_fcfi mbox cmd (Rob Evers) [619917]
- [scsi] lpfc: update version for 8.2.0.78 driver release (Rob Evers) [619917]
- [scsi] lpfc: fix race condition causing >1 FLOGI commands (Rob Evers) [619917]
- [scsi] lpfc: enhance round-robin FCF failover algorithm (Rob Evers) [619917]
- [scsi] lpfc: clear Ignore Reg Login when purging mailbox (Rob Evers) [619917]
- [scsi] lpfc: fix for ELS commands stuck on txq (Rob Evers) [619917]
- [scsi] lpfc: added target queuedepth module parameter (Rob Evers) [619917]
- [scsi] lpfc: fix RoundRobin FCF failover issue (Rob Evers) [619917]
- [scsi] re-enable transistions from OFFLINE to RUNNING (Mike Christie) [641193]
- [edac] i7300_edac: properly init per-csrow memory size (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: better initialize page counts (Mauro Carvalho Chehab) [487428]
- [redhat] configs: enable edac debugging debug kernels (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: backport driver to RHEL5.6 codebase (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: add appropriate MAINTAINERS info (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: coding style cleanups (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: improve inline comments/documentation (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: reorganize file contents (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: properly detect channel on CE errors (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: enrich FBD info for corrected errors (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: enrich FBD error info for fatal errors (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: pre-allocate buffer for error messages (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: fix MTR x4/x8 detection logic (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: make debug messages consistent (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: remove stale get_error_info logic (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: add error registers cleanup support (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: add support for reporting FBD errors (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: properly detect error correction type (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: detect if device is in single mode (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: add detection of enhanced scrub mode (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: clear error bit after reading (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: add error detection for global errors (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: better PCI device names (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: Add FIXME about error correction type (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: add global error registers (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: display info if ECC is enabled or not (Mauro Carvalho Chehab) [487428]
- [edac] i7300_edac: new driver for Intel i7300 chipset (Mauro Carvalho Chehab) [487428]
- [mm] kswapd: don't get stuck in D state w/fragmented mem (Larry Woodman) [609668]
- [misc] x86_64: fix hang at Booting processor 1/8 APIC (John Villalovos) [639851]
- [misc] oprofile: add backtraces for compat mode processes (Jiri Olsa) [622024]
- [net] tg3: re-enable 5717 B0 support (John Feeney) [634320]
- [net] tg3: fix 5717/57765/5719 memory leak (John Feeney) [631963]
- [net] tg3: display FW version, handle FW events correctly (John Feeney) [634325]
- [net] bnx2: improve tx fast path performance (John Feeney) [632057]
- [net] enic: update to upstream version 1.4.1.2 (Andy Gospodarek) [568111]
- [net] ixgbe: fix 82598 link issue and panic w/shared irq (Andy Gospodarek) [637331]
- [net] mlx4: bump max log_mtts_per_seg memory reservation (Jay Fenlason) [636198]
- [usb] net: add support for CDC EEM (Don Zickus) [572519]
- [scsi] qla2xxx: clear post-uncorrectable non-fatal errors (Chad Dupuis) [572258]
- [net] qlcnic: fix poll implementation (Chad Dupuis) [625084]
- [net] qlcnic: TSO feature added for vlan devices (Chad Dupuis) [625084]
- [net] qlcnic: fix diag resource allocation (Chad Dupuis) [625084]
- [net] qlcnic: fix loopback test (Chad Dupuis) [625084]
- [net] qlcnic: fix bandwidth check (Chad Dupuis) [625084]
- [net] qlcnic: fix gro support (Chad Dupuis) [625084]
- [s390] kernel: fix fork vs /proc/stat race (Hendrik Brueckner) [627298]
- [misc] amd_iommu: fix kdump OOM issue seen with iommu=pt (Bhavna Sarathy) [627663]
- [fs] execve: fix interactivity and response to SIGKILL (Dave Anderson) [629176]
- [virt] virtio_console: fix userspace NULL buffer submits (Amit Shah) [636046]
- [virt] virtio_console: fix poll blocking when data ready (Amit Shah) [636020]
- [virt] virtio_console: send SIGIO as needed for host evts (Amit Shah) [636053]
- [virt] virtio_console: make hot-unplug safe (Amit Shah) [628828]
- [net] virtio_net: defer skb allocation in receive path (Anthony Liguori) [565560]
- [misc] increase logbuf size to 512K (Don Zickus) [563535]
- [xen] hvm: correct accuracy of pmtimer (Andrew Jones) [633028]
- [xen] fix guest crash on non-EPT machine may crash host (Paolo Bonzini) [621430] {CVE-2010-2938}

* Thu Oct 07 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-226.el5]
- [net] bonding: fix IGMP report on slave during failover (Flavio Leitner) [637764]

* Mon Sep 27 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-225.el5]
- [usb] serial/pl2303: add id for HP LD220-HP POS display (Don Zickus) [580698]

* Sun Sep 26 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-224.el5]
- [scsi] mpt2sas: recover from injected PCIe bus errors (Tomas Henzl) [568281]
- [message] fusion: remove unnecessary printk flooding logs (Tomas Henzl) [629081]
- [scsi] scsi_dh_alua: handle transitioning state correctly (Mike Snitzer) [619361]
- [scsi] lpfc: fix ioctl crash in lpfc_nlp_put (Rob Evers) [625841]
- [net] trace: fix sk_buff typo in network tracepoints (Neil Horman) [568614]
- [net] sched: fix info leak in traffic policing (Neil Horman) [636392]
- [md] dm: fix deadlock with fsync vs. resize in lvm (Mikulas Patocka) [624068]
- [misc] amd_iommu: fix slab corruption with iommu enabled (Larry Woodman) [530619]
- [mm] add dirty_background_bytes and dirty_bytes sysctls (Larry Woodman) [635782]
- [scsi] add scsi_dispatch_* tracepoints (Jiri Olsa) [568290]
- [misc] oprofile: support Intel CPU Family 6, Model 22, 29 (Jiri Olsa) [493047]
- [fs] aio: fix flush_workqueue deadlock (Jeff Moyer) [546700]
- [net] be2net: use generated MAC addr for VFs, fix BUG_ON (Ivan Vecera) [630680]
- [fs] sysfs: add labeling support for sysfs (Eric Paris) [582374]
- [selinux] inode_*secctx hooks to access security ctx info (Eric Paris) [582374]
- [fs] xattr: refactor vfs_setxattr for SELinux hook use (Eric Paris) [582374]
- [redhat] configs: compile TCG modules for kernel-xen (Andrew Jones) [636100]
- [net] netxen: fix poll implementation (Chad Dupuis) [625079]
- [net] netxen: fix a race in netxen_nic_get_stats() (Chad Dupuis) [625079]
- [net] netxen: update version 4.0.74 (Chad Dupuis) [625079]
- [net] netxen: fix feature setting for vlan devices (Chad Dupuis) [625079]
- [net] netxen: fix tx csum setting (Chad Dupuis) [625079]
- [scsi] qla2xxx: recover on mmio_enable function for 82XX (Chad Dupuis) [613134]
- [scsi] qla2xxx: add AER support for 82XX (Chad Dupuis) [613134]
- [misc] amd_iommu: change default to passthrough mode (Bhavna Sarathy) [628018]
- [misc] amd_iommu: add passthrough mode support (Bhavna Sarathy) [561127]
- [misc] amd: don't use mwait_idle on AMD CPUs (Bhavna Sarathy) [610199]
- [misc] amd: show L3 cache info for all CPU families (Bhavna Sarathy) [610199]
- [misc] amd: unify L3 cache index disable checking (Bhavna Sarathy) [610199]
- [misc] amd: avoid dupe sysfs bits for thresholding banks (Bhavna Sarathy) [610199]
- [misc] amd: remove superfluous CPU family/model check (Bhavna Sarathy) [610199]
- [misc] fix race in pid generation causing immediate reuse (Dave Anderson) [634850]

* Mon Sep 20 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-223.el5]
- [redhat] kabi: add net symbols for RHEL5.6 (Jon Masters) [547689 555708 558999 568558 569606 613193]
- [redhat] kabi: add Block and SCSI symbols for RHEL5.6 (Jon Masters) [547689 558999 566767 569606 574557]
- [redhat] kabi: add PCI kernel symbols for RHEL5.6 (Jon Masters) [547689 555708 566767 568558 569606 597143 613193]
- [redhat] kabi: add core kernel symbols for RHEL5.6 (Jon Masters) [545218 562242]
- [net] ipvs: add one-packet scheduler (Thomas Graf) [578836]
- [pci] fix pci_mmcfg_init making some memory uncacheable (Shyam Iyer) [581933]
- [virt] xen: fix crashing of x86 hvm guest on x86_64 (Radim Krcmar) [605697]
- [scsi] fix disk spinup for shorter path restore times (Rob Evers) [608109]
- [scsi] aacraid: fix file system falsely going read-only (Rob Evers) [523920]
- [misc] x86: fix cpuid_level on Intel pre-model 13 cpus (Prarit Bhargava) [606851]
- [net] cxgb3: alt buffer freeing strategy when xen dom0 (Paolo Bonzini) [488882]
- [net] bonding: enable output slave selection (Neil Horman) [516289]
- [md] dm-raid1: fix data lost at mirror log failure (Mikulas Patocka) [555197]
- [md] kcopyd: dm snapshot performance improvement (Mikulas Patocka) [466088]
- [scsi] increase sync cache timeout (Mike Christie) [592322]
- [scsi] log msg when getting Unit Attention (Mike Christie) [585431]
- [virt] xen: add dummy mwait for xen to make it compile (Luming Yu) [573514]
- [x86_64] use apic as main timer if non-stop-apic timer (Luming Yu) [573514]
- [acpi] cpu: use MWAIT for C-state (Luming Yu) [573514]
- [net] ipv4/defrag: check socket type before reference (Jiri Olsa) [632266]
- [net] ipv4: prevent chained skb destined to UFO device (Jiri Olsa) [633450]
- [block] cfq: no merges for queues w/no process references (Jeff Moyer) [605265]
- [fs] aio: check for multiplication overflow in io_submit (Jeff Moyer) [629449] {CVE-2010-3067}
- [misc] make compat_alloc_user_space incorporate access_ok (Don Howard) [634464] {CVE-2010-3081}
- [fs] xfs: prevent reading uninitialized stack memory (Dave Chinner) [630807] {CVE-2010-3078}
- [fs] aio: fix cleanup in io_submit_one (Jeff Moyer) [631721] {CVE-2010-3066}

* Wed Sep 15 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-222.el5]
- [cpufreq] powernow-k8: fix per core frequency control (Bhavna Sarathy) [502397]
- [misc] uid/gid: fix integer overflow in groups_search (Jerome Marchand) [629626]
- [virt] xen: remove dead code (Paolo Bonzini) [507846]
- [virt] xen: don't give up ballooning under mem pressure (Paolo Bonzini) [507846]
- [net] ipv4: fix oops in writing to forwarding sysctl (Neil Horman) [629638]
- [net] trace: backport some networking tracepoints (Neil Horman) [568614]
- [misc] rename topology_*_cpumask back to *_siblings (Michal Schmidt) [633388]
- [scsi] 3w_sas: add new 3ware SAS driver (Tomas Henzl) [572011]
- [scsi] 3w-9xxx: update to 2.26.08.007-2.6.18RH (Tomas Henzl) [572004]
- [scsi] megaraid: fix suspend function (Tomas Henzl) [630927]
- [net] ipv6: add modes to do RA/RS when in forwarding mode (Thomas Graf) [614064]
- [fs] nfsv4: fix bug when server returns NFS4ERR_RESOURCE (Steve Dickson) [620502]
- [fs] nfsv4: ensure lockowners are labelled correctly (Steve Dickson) [620502]
- [fs] nfsv4: add support for RELEASE_LOCKOWNER operation (Steve Dickson) [620502]
- [fs] nfsv4: clean up for lockowner XDR encoding (Steve Dickson) [620502]
- [fs] nfsv4: ensure we track lock state in r/w requests (Steve Dickson) [620502]
- [scsi] qla4xxx: add PCIe AER support (Chad Dupuis) [624710]
- [scsi] qla4xxx: update version to 5.02.03.00.05.06-d1 (Chad Dupuis) [623675]
- [scsi] qla4xxx: resolve name space error with qla2xxx (Chad Dupuis) [623675]
- [net] qlcnic: add AER support and miscellaneous fixes (Chad Dupuis) [614281]
- [net] qlcnic: add NIC partitioning and other misc fixes (Chad Dupuis) [614281]
- [net] qlcnic: misc upstream fixes for RHEL5.6 (Chad Dupuis) [614281]
- [net] ipv4: fix buffer overflow in icmpmsg_put (Frantisek Hrbata) [601391]
- [proc] allow access to /proc/$PID/fd after setuid (Danny Feng) [617707]
- [fs] xfs: fix missing untrusted inode lookup tag (Dave Chinner) [607032]
- [wireless] fixes from 2.6.32.18 (Stanislaw Gruszka) [621105]
- [wireless] fixes from 2.6.32.17 (Stanislaw Gruszka) [621105]
- [wireless] fixes from 2.6.32.16 (Stanislaw Gruszka) [621105]
- [wireless] fixes from 2.6.32.14 (Stanislaw Gruszka) [621105]
- [wireless] fixes from 2.6.32.13 (Stanislaw Gruszka) [621105]
- [wireless] fixes from 2.6.32.12 (Stanislaw Gruszka) [621105]
- [wireless] fixes from 2.6.32.11 (Stanislaw Gruszka) [621105]
- [wireless] fixes from 2.6.32.10 (Stanislaw Gruszka) [621105]
- [wireless] fixes from 2.6.32.9 (Stanislaw Gruszka) [621105]
- [wireless] fixes from 2.6.32.8 (Stanislaw Gruszka) [621105]
- [xen] emulate task switching (Paolo Bonzini) [625903]
- [xen] introduce hvm_set_cr3 (Paolo Bonzini) [625903]
- [xen] introduce hvm_virtual_to_linear_addr (Paolo Bonzini) [625903]
- [xen] introduce hvm_set_segment_register (Paolo Bonzini) [625903]
- [xen] hvm: big cleanups and fixes to event deliver logic (Paolo Bonzini) [625903]
- [xen] vmx: simplify event-injection logic (Paolo Bonzini) [625903]
- [xen] xm trigger NMI support for HVM guests (Paolo Bonzini) [625902]
- [xen] virtual NMI support (Paolo Bonzini) [625902]
- [xen] emulate injection of guest NMI (Paolo Bonzini) [625902]
- [xen] introduce get_isa_irq_vector and is_isa_irq_masked (Paolo Bonzini) [625902]
- [xen] hvm: fix UP suspend/resume/migration w/PV drivers (Miroslav Rezanina) [629773]

* Mon Sep 13 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-221.el5]
- [acpi] check _PPC state on cpufreq start (Matthew Garrett) [581037]
- [fs] aio: bump i_count instead of using igrab (Jeff Moyer) [626963]
- [redhat] don't generate kABI deps when building w/o kABI (Jon Masters) [456765]
- [watchdog] support for iTCO on Ibex Peak and Cougar Point (John Villalovos) [534152]
- [edac] amd64_edac: whitespace cleanups (Bhavna Sarathy) [568576]
- [edac] amd64_edac: minor formatting fix (Bhavna Sarathy) [568576]
- [edac] amd64_edac: fix operator precedence error (Bhavna Sarathy) [568576]
- [edac] amd64_edac: fix syndrome calculation on K8 (Bhavna Sarathy) [568576]
- [edac] amd64_edac: simplify ECC override handling (Bhavna Sarathy) [568576]
- [edac] amd64_edac: do not falsely trigger kerneloops (Bhavna Sarathy) [568576]
- [edac] amd64_edac: restrict PCI config space access (Bhavna Sarathy) [568576]
- [edac] amd64_edac: fix forcing module load/unload (Bhavna Sarathy) [568576]
- [edac] amd64_edac: fix driver instance freeing (Bhavna Sarathy) [568576]
- [edac] amd64_edac: fix k8 chip select reporting (Bhavna Sarathy) [568576]
- [edac] amd64_edac: add leaner syndrome decoding algorithm (Bhavna Sarathy) [568576]
- [scsi] bnx2i: link hba and cnic device before device reg (Mike Christie) [578005]
- [scsi] bnx2i: make fw use statsn field to build header (Mike Christie) [578005]
- [net] cnic: select bug fixes from upstream for RHEL5.6 (Mike Christie) [595548 619767]
- [scsi] bnx2i: update version to bnx2i-2.1.3 (Mike Christie) [568606]
- [scsi] bnx2i: add chip cleanup for remove module path (Mike Christie) [568606]
- [scsi] bnx2i: rebind CFC cleanup to cm_abort/close comp (Mike Christie) [568606]
- [scsi] bnx2i: add support for additional TMFs (Mike Christie) [568606]
- [scsi] bnx2i: fix protocol violation on nopout responses (Mike Christie) [568606]
- [scsi] bnx2i: fix response panic on unsolicited NOP-In (Mike Christie) [568606]
- [scsi] bnx2i: fix bugs in handling of unsolicited NOP-Ins (Mike Christie) [568606]
- [scsi] bnx2i: add host param ISCSI_HOST_PARAM_IPADDRESS (Mike Christie) [568606]
- [scsi] bnx2i: fix TCP graceful termination initiation (Mike Christie) [568606]
- [scsi] bnx2i: fine tune misc destroy timeout values (Mike Christie) [568606]
- [scsi] bnx2i: optimize bnx2i_stop connection clean up (Mike Christie) [568606]
- [scsi] bnx2i: create active linklist holding endpoints (Mike Christie) [568606]
- [scsi] bnx2i: split hardware cleanup from ep_disconnect (Mike Christie) [568606]
- [fs] dlm: fix try 1cb failure, part 2 (Abhijith Das) [504188]
- [fs] dlm: no node callback when try 1cb lock req fails (David Teigland) [504188]
- [misc] crypto: add Intel x86_64 hardware CRC32 support (Prarit Bhargava) [626018]
- [net] bnx2: update to v2.0.8+ with new 5709 firmware j15 (John Feeney) [568601]
- [net] tg3: update to 3.108+ and add 5718 B0, 5719 support (John Feeney) [567462]
- [misc] move dev_name to device.h (John Feeney) [568551]
- [misc] add WARN_ONCE macro (John Feeney) [568551]
- [dma_v3] update I/O AT and DCA drivers (John Feeney) [568551]
- [net] forcedeth: update to latest upstream for RHEL5.6 (Ivan Vecera) [628831]
- [net] e1000e: update to upstream version 1.2.7-k2 (Andy Gospodarek) [566021]
- [net] qla2xxx: fix display of link down state (Chad Dupuis) [627612]
- [scsi] qla2xxx: rom lock recover if fw hangs holding lock (Chad Dupuis) [619814]
- [scsi] qla2xxx: update AER support, do early abort cmds (Chad Dupuis) [619814]
- [scsi] qla2xxx: add IS_QLA82XX check in update_fw_options (Chad Dupuis) [619814]
- [scsi] qla2xxx: cover UNDERRUN case where SCSI status set (Chad Dupuis) [619814]
- [scsi] qla2xxx: fix set fw hung and complete waiting mbx (Chad Dupuis) [619814]
- [scsi] qla2xxx: fix seconds_since_last_heartbeat reset (Chad Dupuis) [619814]
- [scsi] qla2xxx: correct extended sense-data handling (Chad Dupuis) [619814]
- [scsi] qla2xxx: don't {s,g}et port MBC if invalid port id (Chad Dupuis) [619814]
- [scsi] qla2xxx: stop firmware before doing init firmware (Chad Dupuis) [619814]
- [xen] oprofile: force use of architectural perfmon (Don Dugger) [538564]
- [xen] oprofile: support Intel's arch perfmon registers (Don Dugger) [538564]
- [xen] oprofile: add support for Core i7 and Atom (Don Dugger) [538564]

* Fri Sep 10 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-220.el5]
- [block] cciss: version string to 3.6.22.RH1 (Tomas Henzl) [568830]
- [block] cciss: bus_unregister_once not once per hba (Tomas Henzl) [568830]
- [block] cciss: rename cciss_sector_size (Tomas Henzl) [568830]
- [block] cciss: make log_unit_to_scsi3addr an inline (Tomas Henzl) [568830]
- [block] cciss: fix enxio weirdness (Tomas Henzl) [568830]
- [block] cciss: reorder functions (Tomas Henzl) [568830]
- [block] cciss: fix raid level sysfs permissions (Tomas Henzl) [568830]
- [block] cciss: make device attributes static (Tomas Henzl) [568830]
- [block] cciss: make cciss_seq_show handle drv_array holes (Tomas Henzl) [568830]
- [block] cciss: add via_ioctl param to rebuild_lun_table (Tomas Henzl) [568830]
- [block] cciss: add support for multi-lun tape devices (Tomas Henzl) [568830]
- [block] cciss: notify scsi midlayer of device changes (Tomas Henzl) [568830]
- [block] cciss: fix scatter-gather on scsi side (Tomas Henzl) [568830]
- [block] cciss: add more commands for tapes (Tomas Henzl) [568830]
- [block] cciss: factor out scsi dma code (Tomas Henzl) [568830]
- [block] cciss: eliminate unnecessary pointer use (Tomas Henzl) [568830]
- [block] cciss: don't use void pointer for hba (Tomas Henzl) [568830]
- [block] cciss: detect bad alignment (Tomas Henzl) [568830]
- [block] cciss: factor out sg chain block mapping code (Tomas Henzl) [568830]
- [block] cciss: fix DMA direction kludge (Tomas Henzl) [568830]
- [block] cciss: simplify scatter gather code (Tomas Henzl) [568830]
- [block] cciss: factor out scatter gather alloc and free (Tomas Henzl) [568830]
- [block] cciss: enhanced scatter-gather support (Tomas Henzl) [568830]
- [block] cciss: remove the scan thread (Tomas Henzl) [568830]
- [block] cciss: fix scsi status typo (Tomas Henzl) [568830]
- [block] cciss: remove sendcmd (Tomas Henzl) [568830]
- [block] cciss: clean up code in cciss_shutdown (Tomas Henzl) [568830]
- [block] cciss: retry driver cmds with unit attention cond (Tomas Henzl) [568830]
- [block] cciss: no pci_release_regions on regions not held (Tomas Henzl) [568830]
- [block] cciss: fix memory leak in cciss_init_one (Tomas Henzl) [568830]
- [block] cciss: dynamically allocate drive info struct (Tomas Henzl) [568830]
- [block] cciss: fix raid label related magic number (Tomas Henzl) [568830]
- [block] cciss: no check busy initializing in cciss open (Tomas Henzl) [568830]
- [block] cciss: add usage_count attribute to logical drive (Tomas Henzl) [568830]
- [block] cciss: add raid_level attribute to logical drives (Tomas Henzl) [568830]
- [block] cciss: add lunid attribute to log drives in /sys (Tomas Henzl) [568830]
- [block] cciss: dont call putdisk excessively (Tomas Henzl) [568830]
- [block] cciss: zero out drive info on removal (Tomas Henzl) [568830]
- [block] cciss: handle special case for /dev/cciss/c0d0 (Tomas Henzl) [568830]
- [block] cciss: handle cases when cciss_add_disk fails (Tomas Henzl) [568830]
- [block] cciss: fix and rearrange logical drive sysfs code (Tomas Henzl) [568830]
- [block] cciss: dynamic allocate struct device for logical (Tomas Henzl) [568830]
- [block] cciss: Use helper functions to access drive_data (Tomas Henzl) [568830]
- [block] cciss: remove withirq parameter where possible (Tomas Henzl) [568830]
- [block] cciss: remove sysfs entries during driver cleanup (Tomas Henzl) [568830]
- [block] cciss: add cciss_sysfs_stat_inquiry function (Tomas Henzl) [568830]
- [block] cciss: add CTLR_LUNID define (Tomas Henzl) [568830]
- [block] cciss: Remove unused was_only_controller_node (Tomas Henzl) [568830]
- [block] cciss: fix problem with LUN addressing (Tomas Henzl) [568830]
- [block] cciss: fix problem with SG_IO completions (Tomas Henzl) [568830]
- [block] cciss: retry commands from within sendcmd_withirq (Tomas Henzl) [568830]
- [block] cciss: change SCSI error handling code (Tomas Henzl) [568830]
- [block] cciss: remove sendcmd reject processing (Tomas Henzl) [568830]
- [block] cciss: let scsi error handling work w/interrupts (Tomas Henzl) [568830]
- [block] cciss: factor out error processing code (Tomas Henzl) [568830]
- [block] cciss: factor out target status code (Tomas Henzl) [568830]
- [block] cciss: simplify device addressing methods (Tomas Henzl) [568830]
- [block] cciss: factor out sendcmd_withirq core (Tomas Henzl) [568830]
- [block] cciss: use uninterruptible timeout when waiting (Tomas Henzl) [568830]
- [block] cciss: fix lun reset code (Tomas Henzl) [568830]
- [block] cciss: factor out sendcmd core for sane interface (Tomas Henzl) [568830]
- [block] cciss: remove double setting of h->busy (Tomas Henzl) [568830]
- [block] cciss: disable scan thread, it prevents rmmod (Tomas Henzl) [568830]
- [net] netxen: fix inconsistent lock state (Chad Dupuis) [562937]
- [net] netxen: protect tx timeout recovery by rtnl lock (Chad Dupuis) [562937]
- [net] netxen: fix for kdump (Chad Dupuis) [562937]
- [net] netxen: fix caching window register (Chad Dupuis) [562937]
- [net] netxen: fix rcv buffer leak (Chad Dupuis) [562937]
- [net] netxen: fix memory leaks in error path (Chad Dupuis) [562937]
- [net] netxen: remove unnecessary returns (Chad Dupuis) [562937]
- [net] netxen: handle queue manager access (Chad Dupuis) [562937]
- [net] netxen: to fix onchip memory access. (Chad Dupuis) [562937]
- [net] netxen: remove unnecessary size checks (Chad Dupuis) [562937]
- [net] netxen: fix register usage (Chad Dupuis) [562937]
- [net] netxen: fix deadlock in aer (Chad Dupuis) [562937]
- [net] netxen: fix interrupt for NX2031 (Chad Dupuis) [562937]
- [net] netxen: fix fw load from file (Chad Dupuis) [562937]
- [net] netxen: validate unified romimage (Chad Dupuis) [562937]
- [net] netxen: fix corner cases of firmware recovery (Chad Dupuis) [562937]
- [net] netxen: update version to 4.0.73 (Chad Dupuis) [562937]
- [net] netxen: fix tx csum status (Chad Dupuis) [562937]
- [net] netxen: added sanity check for pci map (Chad Dupuis) [562937]
- [net] netxen: fix warning in ioaddr for NX3031 chip (Chad Dupuis) [562937]
- [net] netxen: fix bios version calculation (Chad Dupuis) [562937]
- [net] netxen: disable on NX_P3_B1 hardware (Chad Dupuis) [562937]
- [net] netxen: protect resource cleanup by rtnl lock (Chad Dupuis) [562937]
- [net] netxen: fix tx timeout recovery for NX2031 chip (Chad Dupuis) [562937]
- [net] netxen: fix sparse warning (Chad Dupuis) [562937]
- [net] netxen: fix license header (Chad Dupuis) [562937]
- [net] netxen: fix endianness intr coalesce (Chad Dupuis) [562937]
- [net] netxen: fix endianness read mac address (Chad Dupuis) [562937]
- [net] netxen: use DEFINE_PCI_DEVICE_TABLE() (Chad Dupuis) [562937]
- [net] netxen: update version to 4.0.72 (Chad Dupuis) [562937]
- [net] netxen: fix set mac addr (Chad Dupuis) [562937]
- [net] netxen: fix smatch warning (Chad Dupuis) [562937]
- [net] netxen: fix tx ring memory leak (Chad Dupuis) [562937]
- [net] netxen: fix ethtool link test (Chad Dupuis) [562937]
- [net] netxen: move && and || to end of previous line (Chad Dupuis) [562937]
- [net] netxen: fix ethtool register dump (Chad Dupuis) [562937]
- [net] netxen: fix unified fw size check (Chad Dupuis) [562937]
- [net] netxen: support pci error handlers (Chad Dupuis) [562937]
- [net] netxen: fix tx timeout recovery (Chad Dupuis) [562937]
- [net] netxen: minor suspend resume fixes (Chad Dupuis) [562937]
- [net] netxen: use module parameter correctly (Chad Dupuis) [562937]
- [net] netxen: fix firmware type check (Chad Dupuis) [562937]
- [net] netxen: fix napi intr enable check (Chad Dupuis) [562937]
- [net] netxen: protect device reset by rtnl_lock (Chad Dupuis) [562937]
- [net] netxen: fix failure cases for fw hang recovery (Chad Dupuis) [562937]
- [net] netxen: fix debug tools access for NX2031 (Chad Dupuis) [562937]
- [misc] clone: fix race between copy_process and de_thread (Jiri Olsa) [590864]
- [s390] dasd: let recovery cqr get flags from failed cqr (Hendrik Brueckner) [628838]
- [net] ipv4: fix leak, rcu and length in route cache gc (Thomas Graf) [541224]
- [net] tcp: zero out rx_opt in tcp_disconnect (Thomas Graf) [539560]
- [net] ipv6: Update Neighbor Cache when IPv6 RA received (Thomas Graf) [560870]
- [net] ipv6: Plug sk_buff leak in ipv6_rcv (Thomas Graf) [574913]
- [redhat] configs: enable building k10temp sensor driver (Michal Schmidt) [443745]
- [hwmon] add k10temp sensor driver (Michal Schmidt) [443745]
- [pci] add AMD 10h, 11h PCI IDs to pci_ids.h (Michal Schmidt) [443745]
- [net] vxge: fix multicast issues (Michal Schmidt) [608598]
- [net] vxge: show startup message with KERN_INFO (Michal Schmidt) [608598]
- [net] vxge: fix memory leak in vxge_alloc_msix error path (Michal Schmidt) [608598]
- [net] vxge: fix checkstack warning in vxge_probe (Michal Schmidt) [608598]
- [net] vxge: remove unnecessary returns from void functs (Michal Schmidt) [608598]
- [net] vxge: version update (Michal Schmidt) [608598]
- [net] vxge: pass correct number of VFs value to sriov (Michal Schmidt) [608598]
- [net] vxge: allow load for all enumerated pci functions (Michal Schmidt) [608598]
- [net] vxge: fix possible memory leak in device init (Michal Schmidt) [608598]
- [net] vxge: add missing vlan_rx_kill_vid method (Michal Schmidt) [594404 608598]
- [net] vxge: remove trailing space in messages (Michal Schmidt) [608598]
- [net] vxge: use pci_dma_mapping_error to test return val (Michal Schmidt) [608598]
- [net] vxge: use DEFINE_PCI_DEVICE_TABLE (Michal Schmidt) [608598]
- [net] vxge: use DMA_BIT_MASK instead of plain values (Michal Schmidt) [608598]
- [net] vxge: move && and || to end of previous line (Michal Schmidt) [608598]
- [net] bnx2x: fix wrong return from bnx2x_trylock_hw_lock (Michal Schmidt) [572012]
- [net] bnx2x: small fix in stats handling (Michal Schmidt) [572012]
- [net] bnx2x: update bnx2x version to 1.52.53-4 (Michal Schmidt) [572012]
- [net] bnx2x: fix PHY locking problem (Michal Schmidt) [572012]
- [net] bnx2x: adjust confusing if indentation (Michal Schmidt) [572012]
- [net] bnx2x: load firmware in open instead of probe (Michal Schmidt) [572012]
- [net] bnx2x: fix net/ip6_checksum.h include (Michal Schmidt) [572012]
- [net] bnx2x: update driver version to 1.52.53-3 (Michal Schmidt) [572012]
- [net] bnx2x: move statistics handling code to own files (Michal Schmidt) [572012]
- [net] bnx2x: create separate file for ethtool routines (Michal Schmidt) [572012]
- [net] bnx2x: create bnx2x_cmn.* files (Michal Schmidt) [572012]
- [net] bnx2x: main netdev does not need ->poll, ->weight (Michal Schmidt) [572012]
- [net] bnx2x: move global variable load_count to bnx2x.h (Michal Schmidt) [572012]
- [net] bnx2x: store module parameters in main structure (Michal Schmidt) [572012]
- [net] bnx2x: create separate folder for bnx2x driver (Michal Schmidt) [572012]
- [net] bnx2x: set RXHASH for LRO packets (Michal Schmidt) [572012]
- [net] bnx2x: return -EINVAL for unsupported flags (Michal Schmidt) [572012]
- [net] bnx2x: fail when trying to setup unsupported features (Michal Schmidt) [572012]
- [net] bnx2x: fix link problem with some DACs (Michal Schmidt) [572012]
- [net] bnx2x: protect a SM state change (Michal Schmidt) [572012]
- [net] bnx2x: avoid TX timeout when stopping device (Michal Schmidt) [572012]
- [net] bnx2x: fix check to get RX hash (Michal Schmidt) [572012]
- [net] bnx2x: remove two unneeded prefetch calls (Michal Schmidt) [572012]
- [net] bnx2x: add support for receive hashing (Michal Schmidt) [572012]
- [net] bnx2x: update date and version to 1.52.53-1 (Michal Schmidt) [572012]
- [net] bnx2x: don't report link down if already down (Michal Schmidt) [572012]
- [net] bnx2x: rework power state handling code (Michal Schmidt) [572012]
- [net] bnx2x: use register mask to avoid parity error (Michal Schmidt) [572012]
- [net] bnx2x: fix MSI-X enabling flow (Michal Schmidt) [572012]
- [net] bnx2x: add new statistics (Michal Schmidt) [572012]
- [net] bnx2x: white space and formatting fixups (Michal Schmidt) [572012]
- [net] bnx2x: protect code with NOMCP (Michal Schmidt) [572012]
- [net] bnx2x: increase DMAE max write size for 57711 (Michal Schmidt) [572012]
- [net] bnx2x: add skeleton VPD firmware version read code (Michal Schmidt) [572012]
- [net] bnx2x: parity error handling for 57710 and 57711 (Michal Schmidt) [572012]
- [net] bnx2x: use DEFINE_PCI_DEVICE_TABLE() (Michal Schmidt) [572012]
- [net] bnx2x: move && and || to end of previous line (Michal Schmidt) [572012]
- [net] bnx2x: remove trailing space in messages (Michal Schmidt) [572012]
- [net] bnx2x: clean up debug prints (Michal Schmidt) [572012]
- [net] bnx2x: use macro for phy address (Michal Schmidt) [572012]
- [net] bnx2x: convert more to %pM (Michal Schmidt) [572012]
- [net] bnx2x: use pci_ioremap_bar (Michal Schmidt) [572012]
- [net] bnx2x: make NAPI poll routine closer to upstream (Michal Schmidt) [572012]
- [net] bnx2x: typo fixes (Michal Schmidt) [572012]
- [net] bnx2x: use (pr|netdev|netif)_<level> macro helpers (Michal Schmidt) [572012]
- [net] bnx2x: use DMA_BIT_MASK(64) over DMA_64BIT_MASK (Michal Schmidt) [572012]
- [net] sfc: update to upstream version 2.6.36-rc1 code (Michal Schmidt) [556476]
- [net] sfc: undo now unnecessary RHEL workqueue changes (Michal Schmidt) [556476]
- [net] netdevice: add netdev_for_each_mc_addr (Michal Schmidt) [556476]
- [misc] add round_jiffies_up and related routines (Michal Schmidt) [556476]
- [net] core: bug fix for vlan + gro issue (Michal Schmidt) [556476]
- [net] vlan/bridge: fix skb_pull_rcsum fatal exception (Michal Schmidt) [556476]
- [fs] proc: add file position and flags info in /proc (Jerome Marchand) [498081]
- [net] e100*/igb*/ixgb*: add missing read memory barrier (Andy Gospodarek) [629761]
- [net] igb/igbvf: turn on TSO for VLAN interfaces (Andy Gospodarek) [629457]
- [net] vlan: control vlan device TSO status with ethtool (Andy Gospodarek) [629457]
- [xen] vtd: fix parameter iommu=no-intremap (Paolo Bonzini) [576478]

* Thu Sep 09 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-219.el5]
- [net] udp: fix bogus UFO packet generation (Jarod Wilson) [632266]
- [virt] xen: fix xennet driver to not corrupt data (Neil Horman) [630129]
- [virt] fix 64-bit compile issue in VMWare TSC update (Prarit Bhargava) [538022]

* Wed Sep 08 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-218.el5]
- [net] tcp: prevent sending past receiver window with TSO (Thomas Graf) [494400]
- [misc] netdevice: add printk helpers for net drivers (Michal Schmidt) [629634]
- [misc] drivers: remove private definitions of pr_* macros (Michal Schmidt) [629634]
- [misc] kernel: add pr_* family of printk helper macros (Michal Schmidt) [629634]
- [infiniband] iw_cxgb3: always define states[] (Michal Schmidt) [629634]
- [net] ifb: fix syntax error in pr_debug usage (Michal Schmidt) [629634]
- [net] tg3: disable PME bit during resume (John Feeney) [598530]
- [net] netfilter: fix crashes caused by fragment jumps (Jiri Pirko) [617268]
- [virt] update VMWare TSC code (Prarit Bhargava) [538022]

* Tue Sep 07 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-217.el5]
- [time] implement fine grained accounting for PM timer (Ulrich Obergfell) [586285]
- [time] initialize tick_nsec based on kernel parameters (Ulrich Obergfell) [586285]
- [time] introduce 'pmtimer_fine_grained' kernel parameter (Ulrich Obergfell) [586285]
- [scsi] ibmvfc: Fix terminate_rport_io (Steve Best) [628615]
- [fs] ext3: flush disk caches on fsync when needed (Eric Sandeen) [592961]
- [fs] ext4: move aio completion after unwritten extent con (Eric Sandeen) [617690]
- [fs] xfs: move aio completion after unwritten extent conv (Eric Sandeen) [617690]
- [fs] direct-io: move aio_complete into ->end_io (Eric Sandeen) [617690]
- [fs] ext4: quota updates for RHEL5.6 (Eric Sandeen) [457153]
- [fs] ext4: quota infrastructure updates for RHEL5.6 (Eric Sandeen) [457153]
- [fs] ext4: core updates for RHEL5.6 (Eric Sandeen) [457153]
- [fs] ext4: add new kernel helpers for RHEL5.6 (Eric Sandeen) [457153]
- [infiniband] sync iser driver with upstream for RHEL5.6 (Mike Christie) [623595]
- [net] cxgb3: don't flush workqueue if called from wq (Doug Ledford) [630124]
- [net] cxgb3: get fatal parity error status on interrupt (Doug Ledford) [630124]
- [net] cxgb3: clear fatal parity error register on init (Doug Ledford) [630124]
- [net] cxgb3: add define for fatal parity error bit (Doug Ledford) [630124]
- [net] qlge: update driver version to 1.00.00.25 (Chad Dupuis) [567402]
- [net] qlge: fix a eeh handler to not add a pending timer (Chad Dupuis) [567402]
- [net] qlge: update driver version to 1.00.00.24 (Chad Dupuis) [567402]
- [net] qlge: remove error pkt flags, enable net csum error (Chad Dupuis) [567402]
- [net] qlge: restore promiscuous setting in ql_adapter_up (Chad Dupuis) [567402]
- [net] qlge: change cpu_to_be16 to htons for udp checksum (Chad Dupuis) [567402]
- [net] qlge: remove firmware dependency for MPI coredump (Chad Dupuis) [567402]
- [net] qlge: adding ndev->last_rx = jiffies (Chad Dupuis) [567402]
- [net] qlge: fix pktgen issue reported by Cisco (Chad Dupuis) [567402]
- [virtio] fix balloon without VIRTIO_BALLOON_F_STATS_VQ (Amit Shah) [601692]
- [virtio] fix sched while atomic in virtio_balloon stats (Amit Shah) [601692]
- [virtio] add memory stat reporting to balloon driver (Amit Shah) [601692]

* Fri Sep 03 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-216.el5]
- [net] hashlimit: check allocation before freeing memory (Wade Mealing) [615229]
- [net] clusterip: check allocation before freeing memory (Wade Mealing) [615227]
- [ia64] mca: save I-resources when INIT is sent (Takao Indoh) [471136]
- [scsi] mpt2sas: update to 05.101.00.02 (Tomas Henzl) [568281]
- [scsi] ipr: bump the version number and date (Steve Best) [626566]
- [scsi] ipr: fix resource type update and add attributes (Steve Best) [626566]
- [scsi] ipr: fix transition to operational on new adapters (Steve Best) [626566]
- [scsi] ipr: change endian swap key for hw spec change (Steve Best) [626566]
- [scsi] ipr: add support for Obsidian-E embedded adapter (Steve Best) [626566]
- [scsi] ipr: add MMIO write for BIST on 64-bit adapters (Steve Best) [626566]
- [scsi] ipr: move setting of allow_restart flag (Steve Best) [626566]
- [scsi] ipr: add writeq definition if needed (Steve Best) [626566]
- [scsi] ipr: add endian swap enable for 64-bit adapters (Steve Best) [626566]
- [scsi] ipr: fix resource path display and formatting (Steve Best) [626566]
- [scsi] ipr: improve interrupt service routine performance (Steve Best) [626566]
- [scsi] ipr: set data list length in request control block (Steve Best) [626566]
- [scsi] ipr: fix register read address on 64-bit adapters (Steve Best) [626566]
- [scsi] ipr: add resource path to IOA status area struct (Steve Best) [626566]
- [scsi] ipr: implement fixes for 64-bit adapter support (Steve Best) [626566]
- [scsi] ipr: fix compile warning (Steve Best) [626566]
- [fs] ext4: allocate ->s_blockgroup_lock separately (Eric Sandeen) [614957]
- [pci] xen: disable broken msi/msix on ia64 xen (Radim Krcmar) [518463]
- [misc] fix non-CONFIG_NUMA x86_64 compile (Prarit Bhargava) [583673]
- [pnp] ignore both UNSET and DISABLED ioresources (Prarit Bhargava) [560540]
- [pnp] reserve system board iomem and ioport resources (Prarit Bhargava) [560540]
- [net] ipv4: add IP_NODEFRAG option for IPv4 socket (Jiri Olsa) [562220]
- [nfs] sunrpc: cancel task_cleanup work in xprt_destroy (Jeff Layton) [611938]
- [fs] nfs: fix file create failure with HPUX client (Jeff Layton) [605720]
- [net] ixgbe: update to upstream version 2.0.84-k2 (Andy Gospodarek) [568602]
- [net] vlan: add VLAN bitfield defines (Andy Gospodarek) [566027]
- [net] igb: actually support self_test ethtool command (Andy Gospodarek) [593862]
- [net] ixgbe: actually support self_test ethtool command (Andy Gospodarek) [593862]
- [net] ixgbevf: update to version 1.0.0-k1 (Andy Gospodarek) [566027]
- [net] bonding: fix ALB mode to balance traffic on VLANs (Andy Gospodarek) [578531]
- [net] igb: do register dump just before resetting adapter (Andy Gospodarek) [568602]
- [kernel] nmi_watchdog: output count during check on boot (Don Zickus) [613667]
- [misc] nmi: fix bogus nmi watchdog stuck messages (Don Zickus) [455323]
- [virt] nmi: don't print NMI stuck messages on guests (Don Zickus) [455323]
- [misc] nmi_watchdog: add /proc/sys/kernel/nmi_watchdog (Don Zickus) [455323]
- [misc] scripts: use system python instead of env (Don Zickus) [521878]
- [pci] sr-iov: fix broken resource alignment calculations (Don Dutile) [523341]
- [pci] clean up resource alignment management (Don Dutile) [523341]
- [pci] sr-iov: assign pci resources earlier (Don Dutile) [523341]
- [net] vxge: update version to reflect RHEL5.6 changes (Bob Picco) [580413]
- [net] vxge: set func_id 0 as privileged for normal func (Bob Picco) [580413]
- [net] vxge: fix MSIX interrupt configuration (Bob Picco) [580413]
- [net] vxge: fix ethtool -d output (Bob Picco) [580413]
- [net] vxge: align tmemory only if misaligned (Bob Picco) [580413]
- [net] vxge: fix hw buffer starvation from short packets (Bob Picco) [580413]
- [net] vxge: fix receive stall w/ driver/chip out-of-sync (Bob Picco) [580413]
- [cpufreq] add APERF/MPERF support for AMD processors (Bhavna Sarathy) [621335]
- [xen] vmx: fix handling of FS/GS base MSRs (Michal Novotny) [613187]
- [xen] hv: improve backtrace support on ia64 (Andrew Jones) [499553]
- [xen] support new AMD family 0x15 CPU and NB hardware (Bhavna Sarathy) [619092]
- [xen] allow dom0 to control core performance boost (Bhavna Sarathy) [568771]
- [xen] add support for dom0 to access APERF/MPERF for AMD (Bhavna Sarathy) [568772]

* Tue Aug 31 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-215.el5]
- [sound] ALSA HDA driver update for RHEL5.6 (Jaroslav Kysela) [592199]
- [net] igbvf: update to latest upstream for RHEL5.6 (Stefan Assmann) [566028]
- [net] igb: update igb driver to support Portville ACS (Stefan Assmann) [566024]
- [net] igb: fix error in igb AER code (Stefan Assmann) [612212]
- [ata] libata: fix suspend/resume for ATA SEMB devices (David Milburn) [622559]
- [ata] sata_mv: msi masking fix (David Milburn) [554872]
- [ata] sata_mv: Properly initialize main irq mask (David Milburn) [554872]
- [ata] sata_mv: remove bogus nsect restriction (David Milburn) [554872]
- [ata] sata_mv: don't read hc_irq_cause (David Milburn) [554872]
- [ata] sata_mv: add the Gen IIE flag to the SoC devices (David Milburn) [554872]
- [ata] sata_mv: don't issue two DMA commands concurrently (David Milburn) [554872]
- [ata] sata_mv: safer logic for limit warnings (David Milburn) [554872]
- [ata] sata_mv: warn on PIO with multiple DRQs (David Milburn) [554872]
- [ata] sata_mv: enable async_notify for 60x1 Rev.C0 and up (David Milburn) [554872]
- [s390] zfcp: Do not print bit mask as link speed (Hendrik Brueckner) [619857]
- [s390] dasd: force online does not work (Hendrik Brueckner) [619466]
- [s390] dasd: allocate fallback cqr for reserve/release (Hendrik Brueckner) [619465]
- [s390] qeth: wait for finished recovery (Hendrik Brueckner) [619456]
- [s390] qeth: avoid loop if ipa command response missing (Hendrik Brueckner) [619451]
- [s390] zfcp: no force close when port is already closed (Hendrik Brueckner) [612263]
- [s390] zfcp: Do not unblock rport from REOPEN_PORT_FORCED (Hendrik Brueckner) [612266]
- [s390] zfcp: Fail erp after timeout (Hendrik Brueckner) [612261]
- [message] fusion: update to 3.4.15 (Tomas Henzl) [568292]
- [net] ipv6: reroute packets after netfilter mangling (Thomas Graf) [517327]
- [scsi] lpfc: update driver from 8.2.0.76.1p to 8.2.0.77 (Rob Evers) [603806]
- [virt] xenbus: avoid deadlock unregistering xenbus watch (Paolo Bonzini) [429102]
- [ia64] kdump: prevent hang on INIT interrupt during boot (Neil Horman) [506694]
- [net] qla3xxx: fix oops on too-long netdev priv structure (Neil Horman) [620508]
- [kprobes] kretprobe: set status to fix fault handling (Josh Stone) [615121]
- [net] bonding: fix a race in calls to slave MII ioctls (Flavio Leitner) [621280]
- [virt] xen-kernel: improve backtrace support on ia64 (Andrew Jones) [499553]
- [acpi] thinkpad-acpi: lock down video output state access (Don Howard) [607037]
- [fs] xfs: fix untrusted inode number lookup (Dave Chinner) [624862]

* Fri Aug 27 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-214.el5]
- [mm] accept an abutting stack segment (Jiri Pirko) [607858] {CVE-2010-2240}
- [fs] fix dcache accounting bug (Josef Bacik) [596548]
- [scsi] mptsas: enable TLR for SSP TAPE drives (Tomas Henzl) [599420]
- [scsi] sas: add transport layer retry support (Tomas Henzl) [599420]
- [scsi] fix potential kmalloc failure in scsi_get_vpd_page (Tomas Henzl) [599420]
- [scsi] fix bugs in scsi_vpd_inquiry (Tomas Henzl) [599420]
- [scsi] add VPD helper (Tomas Henzl) [599420]
- [x86_64] implement vDSO randomization (Danny Feng) [459763]
- [virt] xen: don't adjust time for ntp clock slowing (Bretislav Kabele) [553407]
- [net] ibmveth: fix lost IRQ that leads to service loss (Steve Best) [626841]
- [scsi] cxgb3i: sync driver with upstream for RHEL5.6 (Mike Christie) [567444]
- [net] sched: fix some kernel memory leaks (Jiri Pirko) [624638] {CVE-2010-2942}
- [tpm] autoload tpm_tis driver (John Feeney) [530123]
- [usb] fix usbfs information leak (Eugene Teo) [566629] {CVE-2010-1083}
- [virtio] console: Backport driver for RHEL 5.6 (Amit Shah) [620037]
- [virtio] add virtqueue_ vq_ops wrappers (Amit Shah) [620037]
- [virtio] initialize vq->data entries to NULL (Amit Shah) [620037]
- [virtio] add ability to detach unused buffers from vrings (Amit Shah) [620037]
- [virtio] make add_buf return capacity remaining (Amit Shah) [620037]
- [virtio] find_vqs/del_vqs virtio operations (Amit Shah) [620037]
- [virtio] add names to virtqueue struct (Amit Shah) [620037]
- [virtio] more neatening of virtio_ring macros (Amit Shah) [620037]
- [virtio] fix BAD_RING, START_US and END_USE macros (Amit Shah) [620037]

* Fri Aug 20 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-213.el5]
- [mm] pass correct mm when growing stack (Jiri Pirko) [607858] {CVE-2010-2240}
- [mm] fix up some user-visible effects of stack guard page (Jiri Pirko) [607858] {CVE-2010-2240}
- [mm] fix page table unmap for stack guard page properly (Jiri Pirko) [607858] {CVE-2010-2240}
- [mm] fix missing unmap for stack guard page failure case (Jiri Pirko) [607858] {CVE-2010-2240}
- [mm] keep a guard page below a grow-down stack segment (Jiri Pirko) [607858] {CVE-2010-2240}
- [net] tcp: fix div by zero in congestion control protos (Neil Horman) [608641]
- [net] tcp: tcp_vegas ssthresh bug fix (Thomas Graf) [612709]
- [net] tcp: tcp_vegas cong avoid fix (Thomas Graf) [612709]
- [net] tcp: fix overflow bug in Vegas (Thomas Graf) [612709]
- [net] tcp: fix Vegas bug in disabling slow start (Thomas Graf) [612709]
- [net] tcp: increase Vegas default alpha and beta params (Thomas Graf) [612709]
- [net] tcp: tcp_hybla zero congestion window growth fix (Thomas Graf) [612709]
- [net] tcp: htcp last_cong bug fix (Thomas Graf) [612709]
- [net] tcp: TCP cubic v2.2 (Thomas Graf) [612709]
- [net] tcp: faster cube root (Thomas Graf) [612709]
- [net] tcp: backport cubic update for net-2.6.22 (Thomas Graf) [612709]
- [net] tcp: set Cubic and BIC default thresholds to zero (Thomas Graf) [612709]
- [net] tcp: congestion control initialization (Thomas Graf) [612709]
- [net] tcp: uninline tcp_is_cwnd_limited (Thomas Graf) [612709]
- [net] tcp: move prior_in_flight collect to better spot (Thomas Graf) [612709]
- [fs] ext4: consolidate in_range definitions (Eric Sandeen) [624332] {CVE-2010-3015}
- [net] don't double count UDP_INERRORS (Neil Horman) [618818]
- [scsi] be2iscsi: sync with upstream for RHEL5.6 (Mike Christie) [569643]
- [mmc] sdhci: fix system cannot enter S4 with SD card (Matthew Garrett) [606899]
- [cpufreq] powernow-k8: support AMD Core Performance Boost (Matthew Garrett) [568751]
- [fs] cifs: remove force parm from cifs_unix_info_to_inode (Jeff Layton) [619112]
- [fs] nfs: fix NFS4ERR_FILE_OPEN handling in Linux/NFS (Jeff Layton) [604044]
- [usb] fix test of wrong variable in create_by_name (Don Howard) [594635]
- [s390] cio: fix cause of unexpected recovery actions (Hendrik Brueckner) [621330]

* Wed Aug 11 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-212.el5]
- [ipmi] add parameter to limit CPU usage in kipmid (Takao Indoh) [494680]
- [net] bnx2x: Added GRO support (Stanislaw Gruszka) [573114]
- [net] bnx2x: fix memory barriers (Stanislaw Gruszka) [569370]
- [ppc] partition hibernation support (Steve Best) [565570]
- [ppc] Add resume handler to powerpc time management code (Steve Best) [565570]
- [scsi] ibmvscsi: Fix soft lockup on resume (Steve Best) [565570]
- [scsi] ibmvfc: Fix soft lockup on resume (Steve Best) [565570]
- [scsi] ibmvfc: Add suspend/resume support (Steve Best) [565570]
- [scsi] ibmvscsi: Add suspend/resume support (Steve Best) [565570]
- [net] ibmveth: Add suspend/resume support (Steve Best) [565570]
- [ppc] vio: add power management support (Steve Best) [565570]
- [ppc] add hooks to put CPU in appropriate offline state (Steve Best) [565570]
- [virt] xen: fix passthrough of SR-IOV VF (Paolo Bonzini) [582886]
- [mm] add option to skip ZERO_PAGE mmap of /dev/zero (Larry Woodman) [619541]
- [net] bonding: check if clients MAC addr has changed (Flavio Leitner) [610234]
- [virt] xen: fix pud_present compile warnings (Don Zickus) [590760]
- [xen] CPU synchronization during MTRR register update (Don Dugger) [594546]

* Fri Aug 06 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-211.el5]
- [pci] fix remove of proc entry for hotplug devices (Wade Mealing) [618114]
- [ide]: atiixp: no pio autotune on AMD Hudson2 (Prarit Bhargava) [618075]
- [pci] msi: add option for lockless interrupt mode (Prarit Bhargava) [599295]
- [virt] xenbus: implement O_NONBLOCK (Paolo Bonzini) [470801]
- [net] ip4v/tcp: no additional reset on closed sockets (Neil Horman) [605259]
- [misc] xen: fix migration using xen-vnif in smp hvm guest (Miroslav Rezanina) [555910]
- [edac] fix i7core_edac in multi-socket systems (Mauro Carvalho Chehab) [468877]
- [net] arp_tables: fix unaligned accesses (Jiri Pirko) [582268]
- [fs] ext3: handle journal_start failure properly (Josef Bacik) [588599]
- [misc] handle dead hung uninterruptible tasks correctly (Jerome Marchand) [582237]
- [fs] ecryptfs: fix ecryptfs_uid_hash buffer overflow (Jerome Marchand) [611387] {CVE-2010-2492}
- [infiniband] check local reserved ports (Jerome Marchand) [557884]
- [infiniband] randomize local port allocation (Jerome Marchand) [557884]
- [net] reserve ports for apps using fixed port numbers (Jerome Marchand) [557884]
- [kernel] sysctl: add proc_do_large_bitmap (Jerome Marchand) [557884]
- [scsi] lpfc: use kernel-provided random32 (Jarod Wilson) [605816]
- [lib] make tausworthe random32 generator available to all (Jarod Wilson) [605816]
- [net] be2net: increase POST timeout for EEH recovery (Ivan Vecera) [616512]
- [hwmon] coretemp: get TjMax value from MSR (Dean Nelson) [580699]
- [hwmon] coretemp: detect the thermal sensors by CPUID (Dean Nelson) [580699]
- [fs] xfs: rename XFS_IGET_BULKSTAT to XFS_IGET_UNTRUSTED (Dave Chinner) [607032]
- [fs] xfs: validate untrusted inode numbers during lookup (Dave Chinner) [607032]
- [fs] xfs: always use iget in bulkstat (Dave Chinner) [607032]
- [s390] qeth: support for OSA CHPID types OSX and OSM (Hendrik Brueckner) [599644]
- [s390] qeth: don't allow layer switch with open interface (Hendrik Brueckner) [612195]
- [s390] zfcp: fix reference counting on adisc (Hendrik Brueckner) [610089]
- [s390] kernel: initrd vs bootmem bitmap (Hendrik Brueckner) [610837]
- [s390] hypfs: fix high cpu time output (Hendrik Brueckner) [589282]
- [s390] dasd: fix race between tasklet and dasd_sleep_on (Hendrik Brueckner) [593756]
- [s390] cmm: fix module unload handling (Hendrik Brueckner) [598549]
- [fs] gfs: clean up stuffed file data copy handling (Abhijith Das) [580867]

* Sat Jul 31 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-210.el5]
- [scsi] ips driver sleeps while holding spin_lock (Steve Best) [616961]
- [net] fix lockups and dupe addresses w/bonding and ipv6 (Shyam Iyer) [516985]
- [scsi] megaraid_sas: update driver to version 4.31 (Tomas Henzl) [564249]
- [scsi] megaraid_sas: update driver to version 4.27 (Rob Evers) [564249]
- [net] nat: avoid rerouting packets if only key changed (Jiri Pirko) [566144]
- [fs] cifs: remove bogus check in NTLM session setup code (Jeff Layton) [479418]
- [ata] ahci: add em_buffer attribute for AHCI hosts (David Milburn) [568364]
- [scsi] qla4xxx: add support for ISP82XX (Chad Dupuis) [546592]
- [scsi] qla4xxx: Fixes from upstream for 5.6 (Chad Dupuis) [546592]
- [scsi] qla2xxx: more upstream updates for RHEL 5.6 (Chad Dupuis) [567428]
- [scsi] qla2xxx: add support for ISP82XX (Chad Dupuis) [567428]
- [scsi] qla2xxx: more updates from upstream for RHEL 5.6 (Chad Dupuis) [567428]
- [scsi] qla2xxx: update to 8.03.01.05.05.06-k (Chad Dupuis) [567428]
- [xen] correct bitsize calculation for 32-on-64 (Andrew Jones) [616827]

* Mon Jul 26 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-209.el5]
- [net] r8169: fix for broken register writes (Ivan Vecera) [581654]
- [serial] remove contact info for ite887x chip support (Dean Nelson) [563271]
- [serial] fix modpost warning in ite887x driver (Dean Nelson) [563271]
- [serial] add support for ite887x chips (Dean Nelson) [563271]
- [parport] increase ite887x's I/O port range (Dean Nelson) [563271]
- [scsi] qla2xxx: update firmware to version 5.03.02 (Chad Dupuis) [578444 598946]
- [fs] cifs: reject DNS upcall add_key req from userspace (Jeff Layton) [612171] {CVE-2010-2524}
- [security] keys: new key flag for add_key from userspace (Jeff Layton) [612171] {CVE-2010-2524}

* Thu Jul 22 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-208.el5]
- [fs] gfs2: fix rename causing kernel oops (Robert S Peterson) [602025]
- [misc] io_apic: skip timer_irq_works check when on VMware (Prarit Bhargava) [575309]
- [scsi] be2iscsi: fix for 64k data length sge (Mike Christie) [608801]
- [mm] fix excessive memory reclaim from zones w/lots free (Larry Woodman) [604779]
- [mm] properly release all hugepages on database shutdown (Larry Woodman) [593131]
- [net] fix accept_local handling for dev with no xattrs (Jiri Olsa) [601370]
- [fs] nfs: i_nlinks changes must set NFS_INO_INVALID_ATTR (Jeff Layton) [601800]
- [fs] nfs: fix resolution in nfs_inode_attrs_need_update (Jeff Layton) [601800]
- [fs] nfs: fix compiler warnings introduced recently (Jeff Layton) [601800]
- [fs] nfs: fix attribute updates even more (Jeff Layton) [601800]
- [fs] nfs: fix the NFS attribute update (Jeff Layton) [601800]
- [fs] nfs: clean up inode handling functions (Jeff Layton) [601800]
- [fs] nfs: nfs_refresh_inode should clear cache_validity (Jeff Layton) [601800]
- [fs] nfs: use nfs_refresh_inode in __nfs_revalidate_inode (Jeff Layton) [601800]
- [ata] ahci, pata_marvell: fixup competition for PATA port (David Milburn) [237372]
- [net] qlcnic: Add QLCNIC to Kconfig and Makefile (Chad Dupuis) [562723]
- [net] qlcnic: enable building driver module (Chad Dupuis) [562723]
- [net] qlcnic: remove extra space from board names (Chad Dupuis) [562723]
- [net] qlcnic: fix bios version check (Chad Dupuis) [562723]
- [net] qlcnic: validate unified fw image (Chad Dupuis) [562723]
- [net] qlcnic: fix multicast handling (Chad Dupuis) [562723]
- [net] qlcnic: additional driver statistics. (Chad Dupuis) [562723]
- [net] qlcnic: fix tx csum status (Chad Dupuis) [562723]
- [net] qlcnic: add loopback diagnostic test (Chad Dupuis) [562723]
- [net] qlcnic: add interrupt diagnostic test (Chad Dupuis) [562723]
- [net] qlcnic: support LED blink for device identification (Chad Dupuis) [562723]
- [net] qlcnic: protect resoruce cleanup by rtnl lock (Chad Dupuis) [562723]
- [net] qlcnic: clear device reset state after fw recovery (Chad Dupuis) [562723]
- [net] qlcnic: add ethernet identifier in board info (Chad Dupuis) [562723]
- [net] qlcnic: use DEFINE_PCI_DEVICE_TABLE (Chad Dupuis) [562723]
- [net] qlcnic: add Qlogic ethernet driver for CNA devices (Chad Dupuis) [562723]
- Revert: [fs] cifs: reject DNS upcall add_key req from userspace (Jeff Layton) [612171] {CVE-2010-2524}
- Revert: [security] keys: new key flag for add_key from userspace (Jeff Layton) [612171] {CVE-2010-2524}

* Thu Jul 15 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-207.el5]
- [usb] uhci: fix oops in uhci_scan_schedule (Pete Zaitcev) [516851]
- [wireless] rtl818x: use cancel_work_sync (Stanislaw Gruszka) [582191]
- [wireless] iwlwifi: use cancel_work_sync (Stanislaw Gruszka) [582191]
- [wireless] ath9k: use cancel_work_sync (Stanislaw Gruszka) [582191]
- [wireless] rt2x00: use cancel_work_sync (Stanislaw Gruszka) [582191]
- Revert: [wireless] rt2x00: fix work cancel race condition (Stanislaw Gruszka) [582191]
- [wireless] use cancel_work_sync in mac80211 and core (Stanislaw Gruszka) [582191]
- [misc] workqueue: add cancel_work_sync to include (Stanislaw Gruszka) [582191]
- [net] igb: drop support for UDP hashing w/ RSS (Stefan Assmann) [613780]
- [misc] signals: avoid unnecessary credentials check (Oleg Nesterov) [459901]
- [acpi] tell platformthat we support fixed hw T-states (Matthew Garrett) [569590]
- [edac] i7core_edac: Backport driver to RHEL5 (Mauro Carvalho Chehab) [468877]
- [edac] i7core_edac: add driver for new Nehalem (Mauro Carvalho Chehab) [468877]
- [x86_64] mce: fix misplaced `continue' in mce.c (Mauro Carvalho Chehab) [468877]
- [pci] Add a probing code that seeks for an specific bus (Mauro Carvalho Chehab) [468877]
- [edac] add support for DDR3 at EDAC core (Mauro Carvalho Chehab) [468877]
- [wireless] Kconfig: select WIRELESS_COMPAT as needed (John Linville) [583767]
- [i386] oprofile: fix detection of Intel CPU family 6 (John Villalovos) [581919]
- [misc] intel: support for Intel Cougar Point Chipset (John Villalovos) [566854]
- [fs] xfs: don't let swapext operate on write-only files (Jiri Pirko) [605161] {CVE-2010-2226}
- [fs] nfs: fix bug in nfsd4 read_buf (Jiri Olsa) [612035] {CVE-2010-2521}
- [fs] nfsd: add lockdep annotation to nfsd4 recover code (Jeff Layton) [567092]
- [fs] nfs: wait for close before silly-renaming (Jeff Layton) [565974]
- [fs] cifs: enable CONFIG_CIFS_STATS (Jeff Layton) [574795]
- [net] sunrpc: translate an -ENETUNREACH to -ENOTCONN (Jeff Layton) [481372]
- [fs] cifs: merge CIFSSMBQueryEA with CIFSSMBQAllEAs (Jeff Layton) [527268]
- [fs] cifs: verify lengths of QueryAllEAs reply (Jeff Layton) [527268]
- [fs] cifs: increase maximum buffer size in CIFSSMBQAllEAs (Jeff Layton) [527268]
- [fs] cifs: rename name_len to list_len in CIFSSMBQAllEAs (Jeff Layton) [527268]
- [fs] cifs: clean up indentation in CIFSSMBQAllEAs (Jeff Layton) [527268]
- [fs] cifs: reject DNS upcall add_key req from userspace (Jeff Layton) [612171] {CVE-2010-2524}
- [fs] cifs: add parens around smb_var in BCC macros (Jeff Layton) [527268]
- [security] keys: new key flag for add_key from userspace (Jeff Layton) [612171] {CVE-2010-2524}
- [specfile] skip xen tarball and patching if building w/o xen (Jarod Wilson)
- [specfile] replace ancient and deprecated rpm syntax (Jarod Wilson)
- [virt] xen: remove sysdata hack from irq-xen.c (Paolo Bonzini) [561390]
- [xen] msi fixmap cleanup and vector teardown (Don Dugger) [516236]

* Thu Jul 08 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-206.el5]
- [x86] kprobes: introduce kprobes jump optimization (Masami Hiramatsu) [516313]
- [x86] add x86_64 alternatives_text_reserved interface (Masami Hiramatsu) [516313]
- [x86_64] kprobes: upstream update for rhel5.6 (Masami Hiramatsu) [516313]
- [x86_64] add instruction decoder API (Masami Hiramatsu) [516313]
- [fusion] mpt: fix deregister calls in exit path (hiro muneda) [581523]
- [net] cxgb3: wait longer for control packets on init (Steve Best) [587670]
- [scsi] scsi_dh_alua: add IBM Power Virtual SCSI ALUA dev (Steve Best) [567292]
- [fs] gfs2: fix stuck in inode wait, no glocks stuck (Robert S Peterson) [595397]
- [message] mptsas: fix disk add failing due to timeout (Rob Evers) [542892]
- [scsi] lpfc: update from 8.2.0.73.1p to 8.2.0.76.1p (Rob Evers) [591674]
- [scsi] lpfc: update from 8.2.0.63.p3 to 8.2.0.73.1p (Rob Evers) [571862]
- [i2c] fix exports types for recently added i2c symbols (Prarit Bhargava) [611774]
- [virt] xen: fix 32-bit syscalls on 64-bit kernel (Paolo Bonzini) [561394]
- [virt] xen: add tracepoint for kernel pagefault event (Paolo Bonzini) [561385]
- [security] selinux: fix race with re-parenting (Oleg Nesterov) [556675]
- [net] sctp: fix length checks (Neil Horman) [605305]
- [acpi] intel: avoid skipping ARB_DISABLE on model 0x0e (Matthew Garrett) [602846]
- [block] cfq-iosched: fix bad locking in changed_ioprio (Jeff Moyer) [582435]
- [block] cfq-iosched: kill cfq_exit_lock (Jeff Moyer) [582435]
- [fs] cifs: fix kernel BUG with remote OS/2 server (Jeff Layton) [608588] {CVE-2010-2248}
- [fs] cifs: don't try busy-file rename unless in same dir (Jeff Layton) [603706]
- [fs] nfsd: don't break lease while servicing COMMIT call (Jeff Layton) [575817]
- [fs] force target reval when following LAST_BIND symlinks (Jeff Layton) [571518]
- [net] be2net: update to v2.102.348r with SR-IOV support (Ivan Vecera) [568388]
- [net] virtio_net: add set_multicast_list (Herbert Xu) [552574]
- [net] gro: fix bogus gso_size on the first fraglist entry (Herbert Xu) [588015]
- [time] fix softlockups in RHEL5 virt guests (Glauber Costa) [607443]
- [time] count ticks when loss gt cycle_accounted_limit (Glauber Costa) [584679]
- [net] e1000e: don't inadvertently re-set INTX_DISABLE (Dean Nelson) [496127]
- [scsi] fixup size on read capacity failure (David Milburn) [569654]
- [s390] smsgiucv: add missing check for z/VM (Hendrik Brueckner) [590737]
- [s390] zcore: fix reipl device detection (Hendrik Brueckner) [587027]
- [s390] zcrypt: print error message for 8/72 error (Hendrik Brueckner) [563545]
- [s390] kernel: fix dump indicator (Hendrik Brueckner) [546288]
- [net] bluetooth: fix possible bad memory access via sysfs (Mauro Carvalho Chehab) [576021] {CVE-2010-1084}

* Thu Jul 01 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-205.el5]
- [scsi] ipr: adds PCI ID definitions for new adapters (Steve Best) [563589]
- [scsi] ipr: add support for new IOASCs (Steve Best) [563589]
- [scsi] ipr: add support for multiple stages of init (Steve Best) [563589]
- [scsi] ipr: implement shutdown changes (Steve Best) [563589]
- [scsi] ipr: hardware assisted smart dump functionality (Steve Best) [563589]
- [scsi] ipr: add error handling updates for next gen chip (Steve Best) [563589]
- [scsi] ipr: update the config table for next gen chip (Steve Best) [563589]
- [scsi] ipr: define register offsets for next gen chip (Steve Best) [563589]
- [scsi] ipr: add command structures for next gen chip (Steve Best) [563589]
- [scsi] ipr: differentiate pci-x and pci-e based adapters (Steve Best) [563589]
- [scsi] ipr: add test for MSI interrupt support (Steve Best) [563589]
- [scsi] ipr: add message to error table (Steve Best) [563589]
- [scsi] ipr: handle logically bad block write errors (Steve Best) [563589]
- [scsi] ipr: convert to use the data buffer accessors (Steve Best) [563589]
- [scsi] ipr: add some defines that are missing in RHEL5.5 (Steve Best) [563589]
- [scsi] ipr: add workaround for MSI interrupts on P7 (Steve Best) [572333]
- [net] tcp: fix rcv mss estimate for lro (Stanislaw Gruszka) [593801]
- [virt] xen netback: copy skbuffs if head crosses pages (Paolo Bonzini) [578259]
- [virt] xen: handle softirqs at end of event processing (Paolo Bonzini) [564523]
- [virt] fix tsccount clocksource under kvm guests (Glauber Costa) [581396]
- [net] benet: compat header cleanups, part 2 (Ivan Vecera) [546740]
- [net] benet: compat header cleanups, part 1 (Prarit Bhargava) [546740]
- [net] bnx2: compat header cleanups (Prarit Bhargava) [546740]
- [net] e1000/e1000e: compat header cleanup (Prarit Bhargava) [546740]
- [net] enic: compat header cleanup (Prarit Bhargava) [546740]
- [net] forcedeth: compat header cleanup (Prarit Bhargava) [546740]
- [net] igb: compat header cleanups (Prarit Bhargava) [546740]
- [net] ixgbe: compat header cleanups (Prarit Bhargava) [546740]
- [net] myri10ge: compat header cleanups (Prarit Bhargava) [546740]
- [net] netxen: compat header cleanup (Prarit Bhargava) [546740]
- [net] niu: compat header cleanup (Prarit Bhargava) [546740]
- [net] qlge: compat header cleanup (Prarit Bhargava) [546740]
- [net] r8169: compat header cleanups, part 2 (Ivan Vecera) [546740]
- [net] r8169: compat header cleanups, part 1 (Prarit Bhargava) [546740]
- [net] sfc: compat header cleanups (Prarit Bhargava) [546740]
- [net] sky2: compat header cleanup (Prarit Bhargava) [546740]
- [net] tg3: compat header cleanup (Prarit Bhargava) [546740]
- [net] bonding: compat header cleanup (Prarit Bhargava) [546740]
- [net] move compat header file contents to proper includes (Prarit Bhargava) [546740]
- [net] ethernet: compat header cleanups (Prarit Bhargava) [546740]
- [net] chelsio: compat header cleanups (Prarit Bhargava) [546740]
- [net] s2io: compat header cleanups (Prarit Bhargava) [546740]
- [net] vxge: compat header cleanup (Prarit Bhargava) [546740]
- [infiniband] compat header cleanups (Prarit Bhargava) [546740]
- [scsi] compat header cleanups (Prarit Bhargava) [546740]
- [misc] readq/writeq compat header cleanup (Prarit Bhargava) [546740]
- [pci] compat header cleanups (Prarit Bhargava) [546740]
- [misc] compat.h cleanup: add cancel_delayed_work_sync (Prarit Bhargava) [546740]
- [i2c] compat header cleanups (Prarit Bhargava) [546740]
- [fs] nfs: fix memory leak when using -onolock on nfs v2/3 (Jeff Layton) [592908]

* Wed Jun 23 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-204.el5]
- [fs] gfs2: fix ordering of ordered writes (Steven Whitehouse) [581013]
- [net] cnic: fix bnx2x panic w/multiple interfaces enabled (Stanislaw Gruszka) [602402]
- [x86_64] unify apic mapping code (Prarit Bhargava) [573858]
- [virt] xen: fix Connected state after netback dev closed (Paolo Bonzini) [591548]
- [net] ipv4: add sysctl to accept packets w/local source (Jiri Olsa) [601370]
- [nfs] fix unitialized list head on error exit in recovery (Jeff Layton) [569342]
- [virt] virtio_blk: add support for cache flushes (Christoph Hellwig) [571735]
- [xen] ia64: unset be from the task psr (Andrew Jones) [587477] {CVE-2010-2070}

* Thu Jun 10 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-203.el5]
- [misc] permit larger than 2TB USB and FW drives (Pete Zaitcev) [503864]
- [net] cnic: fix panic when nl msg rcvd when device down (Stanislaw Gruszka) [595862]
- [infiniband] ehca: require in_wc in process_mad (Steve Best) [571517]
- [net] igb: Add support for pci-e Advanced Error Reporting (Stefan Assmann) [568221]
- [fs] ext4: MOVE_EXT can't overwrite append-only files (Eric Sandeen) [601008] {CVE-2010-2066}
- [net] wireless: convert reg_regdb_search_lock to mutex (John Linville) [597334]
- [net] tcp: don't send keepalive probes if receiving data (Flavio Leitner) [593040]
- [hwmon] add support for additional CPU models to coretemp (Dean Nelson) [559228]
- [fs] gfs2: use -EUSERS when mounting w/o enough journals (Abhijith Das) [600387]
- [misc] workqueue: make cancel_work_sync EXPORT_SYMBOL_GPL (Oleg Nesterov) [596626]

* Fri Jun 04 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-202.el5]
- [fs] gfs2: fix permissions checking for setflags ioctl (Steven Whitehouse) [595399] {CVE-2010-1641}
- [mm] clear page errors when issuing a fresh read of page (Rik van Riel) [590763]
- [misc] keys: do not find already freed keyrings (Vitaly Mayatskikh) [585100] {CVE-2010-1437}
- [misc] workqueue: silence kabi checker (Stanislaw Gruszka) [596626]
- [misc] workqueue: implement cancel_work_sync (Oleg Nesterov) [596626]
- [misc] workqueue: implement try_to_grab_pending (Oleg Nesterov) [596626]
- [misc] workqueue: prep flush_cpu_workqueue for additions (Oleg Nesterov) [596626]
- [misc] workqueue: implement wait_on_work (Oleg Nesterov) [596626]
- [misc] workqueue: add set_wq_data and get_wq_data helpers (Oleg Nesterov) [596626]
- [misc] workqueue: cwq instead of wq where appropriate (Oleg Nesterov) [596626]
- [misc] workqueue: initial prep for cancel_work_sync (Oleg Nesterov) [596626]
- [net] sctp: file must be valid before setting timeout (Jiri Pirko) [578261]
- [net] tg3: fix panic in tg3_interrupt (John Feeney) [569106]
- [net] e1000/e1000e: implement simple interrupt moderation (Andy Gospodarek) [586416]
- [virt] don't compute pvclock adjustments if we trust tsc (Glauber Costa) [570824]
- [virt] add a global synchronization point for pvclock (Glauber Costa) [570824]
- [virt] enable pvclock flags in vcpu_time_info structure (Glauber Costa) [570824]
- [misc] add atomic64_cmpxcgh to x86_64 include files (Glauber Costa) [570824]
- [x86] grab atomic64 types from upstream (Glauber Costa) [570824]
- [pci] cleanup error return for pcix get/set mmrbc calls (Dean Nelson) [578492]
- [pci] fix pcix access of PCI_X_CMD get/set mmrbc calls (Dean Nelson) [578492]
- [pci] fix return value from pcix_get_max_mmrbc() (Dean Nelson) [578492]
- [pci] prepare for backport of upstream fixes and cleanup (Dean Nelson) [578492]
- [net] ipv6: fix more memory leaks when ndisc_init fails (Amerigo Wang) [555338]
- [xen] bring back VMXE/SVME flags (Andrew Jones) [570091]

* Thu May 27 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-201.el5]
- [s390] qdio: continue polling for buffer state ERROR (Hendrik Brueckner) [565531]
- [pci] acpiphp: fix missing acpiphp_glue_exit (Prarit Bhargava) [515556]
- [net] cnic: Fix crash during bnx2x MTU change (Stanislaw Gruszka) [582367]
- [net] bxn2x: add dynamic lro disable support (Stanislaw Gruszka) [582367]
- [net] implement dev_disable_lro api for RHEL5 (Stanislaw Gruszka) [582367]

* Fri May 21 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-200.el5]
- [fs] getrusage: fill ru_maxrss value (Amerigo Wang) [466157]
- [net] bonding: fix broken multicast with round-robin mode (Andy Gospodarek) [570645]
- [usb] input: fix keyboard LEDs on all the time (Pete Zaitcev) [513934]
- [x86_64] fix time drift due to faulty lost tick tracking (Ulrich Obergfell) [579711]
- [cciss] remove extraneous printk (Tomas Henzl) [582465]
- [sunrpc] fix AUTH_SYS using sec=sys export option (Sachin Prabhu) [573652]
- [misc] fix itimers periodic tics precision (Stanislaw Gruszka) [441134]
- [net] tg3: fix INTx fallback when MSI fails (Steve Best) [587666]
- [fs] quota: fix possible infinite loop in quota code (Eric Sandeen) [546060]
- [misc] add {thread,core}_siblings_list to /sys (Prarit Bhargava) [570610]
- [misc] add /sys/devices/system/node/nodeX/cpulist files (Prarit Bhargava) [572285]
- [net] tun: orphan an skb on tx (Michael S. Tsirkin) [584412]
- [edac] fix panic when a corrected error happens on i5000 (Mauro Carvalho Chehab) [533391]
- [net] iwlwifi: re-enable IWLWIFI_LEDS (John Linville) [582003]
- [net] calc TCP's connection closethreshold as time value (Jiri Pirko) [582722]
- [net] sched: fix SFQ qdisc crash w/limit of 2 packets (Jiri Pirko) [579774]
- [net] missed and reordered checks in {arp,ip,ip6}_tables (Jiri Pirko) [554563]
- [net] neigh: fix state transitions via Netlink request (Jiri Pirko) [485903]
- [net] route: fix BUG_ON in rt_secret_rebuild_oneshot (Jiri Olsa) [566104]
- [net] netfilter: fix vmalloc ENOMEM caused by iptables (Jiri Olsa) [570491]
- [block] cciss: fix multi-line printk log level (Jerome Marchand) [556921]
- [nfs] revert retcode check in nfs_revalidate_mapping() (Jeff Layton) [557423]
- [nfs] don't decode GETATTR if DELEGRETURN returned error (Jeff Layton) [551028]
- [md] dm-log: fix bad log status after failure (Jonathan E Brassow) [570583]
- [net] igmp: fix ip_mc_sf_allow race (Flavio Leitner) [552886]
- [hwmon] add 0x prefix to hex coretemp module output (Dean Nelson) [571864]
- [net] e1000e: fix WoL init when WoL disabled in EEPROM (Dean Nelson) [568562]
- [ata] libata: handle semb signature (David Milburn) [533093]
- [ata] libata-acpi: missing _SDD is not an error (David Milburn) [559815]
- [scsi] sg: rate limit warning (Doug Ledford) [536937]
- [net] tun: check supplemental groups in TUN/TAP driver (Danny Feng) [540786]
- [s390] nss: add missing .previous call to asm function (Hendrik Brueckner) [581522]
- [misc] lockdep: dump stack when hitting a limit (Amerigo Wang) [546554]
- [net] ipv6: don't panic when kmem_cache_create fails (Amerigo Wang) [555338]
- [misc] ipc: HARD_MSGMAX should be higher on 64bit (Amerigo Wang) [548334]
- [fs] gfs2: make quota file size a multiple of gfs2_quota (Abhijith Das) [546455]

* Fri May 14 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-199.el5]
- [mm] fix hugepage corruption using vm.drop_caches (Larry Woodman) [579469]
- [misc] taskstats: enable CONFIG_TASK_XACCT (Jiri Olsa) [516961]
- [misc] taskstats: new structure/cmd to avoid KABI break (Jiri Olsa) [516961]
- [misc] taskstats: common fix for KABI breakage (Jiri Olsa) [516961]
- [misc] taskstats: upgrade to version 4 (Jiri Olsa) [516961]
- [misc] futex: handle futex value corruption gracefully (Jerome Marchand) [480396] {CVE-2010-0622}
- [misc] futex: handle user space corruption gracefully (Jerome Marchand) [480396] {CVE-2010-0622}
- [misc] futex: fix fault handling in futex_lock_pi (Jerome Marchand) [480396] {CVE-2010-0622}
- [x86] utrace: block-step fix (Jerome Marchand) [463950]
- [nfs] don't unhash dentry in nfs_lookup_revalidate (Jeff Layton) [582321]
- [net] sunrpc: fix panic when reloading rpcsec_gss_krb5 (Harshula Jayasuriya) [570044]
- [net] bonding: fix updating of speed/duplex changes (Andy Gospodarek) [567604]
- [net] e1000: fix WoL init when WoL disabled in EEPROM (Dean Nelson) [568561]
- [ata] ahci: support FIS-based switching (David Milburn) [474294]
- [audit] make sure filterkey rules are reported (Alexander Viro) [579479]
- [audit] clean up rule ordering, part 2 (Alexander Viro) [579479]
- [audit] clean up rule ordering, part 1 (Alexander Viro) [579479]
- [audit] fix selinux_audit_rule_update w/audit_inode_hash (Alexander Viro) [579479]
- [virtio] fix GFP flags passed by virtio balloon driver (Amit Shah) [584683]
- [net] sctp: fix skb_over_panic w/too many unknown params (Neil Horman) [584658] {CVE-2010-1173}
- [xen] arpl on MMIO area crashes the guest (Paolo Bonzini) [572982] {CVE-2010-0730}

* Sat May 01 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-198.el5]
- [acpi] warn on hot-add of memory exceeding 4G boundary (Prarit Bhargava) [571544]
- [net] tipc: fix various oopses in uninitialized code (Neil Horman) [558693] {CVE-2010-1187}
- [acpi] fix WARN on unregister in power meter driver (Matthew Garrett) [576246]
- [block] cfq-iosched: fix IOPRIO_CLASS_IDLE accounting (Jeff Moyer) [574285]
- [block] cfq-iosched: async queue allocation per priority (Jeff Moyer) [574285]
- [block] cfq-iosched: fix async queue behaviour (Jeff Moyer) [574285]
- [block] cfq-iosched: propagate down request sync flag (Jeff Moyer) [574285]
- [block] introduce the rq_is_sync macro (Jeff Moyer) [574285]
- [fs] vfs: fix LOOKUP_FOLLOW on automount symlinks (Jeff Layton) [567816] {CVE-2010-1088}
- [nfs] fix an oops when truncating a file (Jeff Layton) [567195] {CVE-2010-1087}
- [net] bnx2: fix lost MSI-X problem on 5709 NICs (John Feeney) [511368]
- [misc] make the keyring quotas controllable via /proc/sys (Amerigo Wang) [441243]
- [fs] fix kernel oops while copying from ext3 to gfs2 (Abhijith Das) [555754] {CVE-2010-1436}

* Tue Apr 20 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-197.el5]
- [cpu] fix boot crash in 32-bit install on AMD cpus (Bhavna Sarathy) [575799]

* Tue Apr 13 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-196.el5]
- [mm] fix boot on s390x after bootmem overlap patch (Amerigo Wang) [550974]
- [net] bnx2: avoid restarting cnic in some contexts (Andy Gospodarek) [554706]
- [misc] add missing CVE labels for entries in 2.6.18-195.el5 (Jarod Wilson)

* Sat Apr 10 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-195.el5]
- [redhat] make sha512hmac sig failure more obvious (Jarod Wilson)
- [mm] keep get_unmapped_area_prot functional (Danny Feng) [556710] {CVE-2010-0291}
- [mm] switch do_brk to get_unmapped_area (Danny Feng) [556710] {CVE-2010-0291}
- [mm] take arch_mmap_check into get_unmapped_area (Danny Feng) [556710] {CVE-2010-0291}
- [mm] get rid of open-coding in ia64_brk (Danny Feng) [556710] {CVE-2010-0291}
- [mm] unify sys_mmap* functions (Danny Feng) [556710] {CVE-2010-0291}
- [mm] kill ancient cruft in s390 compat mmap (Danny Feng) [556710] {CVE-2010-0291}
- [mm] fix pgoff in have to relocate case of mremap (Danny Feng) [556710] {CVE-2010-0291}
- [mm] fix the arch checks in MREMAP_FIXED case (Danny Feng) [556710] {CVE-2010-0291}
- [mm] fix checks for expand-in-place mremap (Danny Feng) [556710] {CVE-2010-0291}
- [mm] add new vma_expandable helper function (Danny Feng) [556710] {CVE-2010-0291}
- [mm] move MREMAP_FIXED into its own header (Danny Feng) [556710] {CVE-2010-0291}
- [mm] move locating vma code and checks on it (Danny Feng) [556710] {CVE-2010-0291}
- [iscsi] fix slow failover times (Mike Christie) [570681]
- [misc] kernel: fix elf load DoS on x86_64 (Danny Feng) [560553] {CVE-2010-0307}
- [netlink] connector: delete buggy notification code (Jiri Olsa) [561685] {CVE-2010-0410}
- [sound] hda_intel: avoid divide by zero in azx devices (Jaroslav Kysela) [567172] {CVE-2010-1085}
- [dvb] fix endless loop when decoding ULE at dvb-core (Mauro Carvalho Chehab) [569242] {CVE-2010-1086}
- [scsi] fnic: fix tx queue handling (Mike Christie) [576709]
- [fusion] mptsas: fix event_data alignment (Tomas Henzl) [570000]
- [edac] fix internal error message in amd64_edac driver (Bhavna Sarathy) [569938]
- [fs] remove unneccessary f_ep_lock from fasync_helper (Lachlan McIlroy) [567479]
- [x86_64] fix floating point state corruption after signal (Oleg Nesterov) [560891]
- [mm] don't let reserved memory overlap bootmem_map (Amerigo Wang) [550974]
- [s390] kernel: correct TLB flush of page table entries (Hendrik Brueckner) [545527]
- [xen] iommu: clear IO-APIC pins on boot and shutdown (Paolo Bonzini) [548201]
- [xen] vtd: fix ioapic pin array (Don Dugger) [563546]
- [xen] set hypervisor present CPUID bit (Paolo Bonzini) [573771]

* Tue Mar 16 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-194.el5]
- [net] mlx4: pass attributes down to vlan interfaces (Doug Ledford) [573098]
- [block] cfq-iosched: fix sequential read perf regression (Jeff Moyer) [571818]

* Mon Mar 15 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-193.el5]
- [fs] gfs2: locking fix for potential dos (Steven Whitehouse) [572390] {CVE-2010-0727}
- [acpi] power_meter: avoid oops on driver load (Matthew Garrett) [566575]
- [net] r8169: fix assignments in backported net_device_ops (Ivan Vecera) [568040]
- [net] virtio_net: refill rx buffer on out-of-memory (Herbert Xu) [554078]

* Tue Mar 09 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-192.el5]
- [cpu] fix amd l3 cache disable functionality (Jarod Wilson) [517586]
- [misc] backport upstream strict_strto* functions (Jarod Wilson) [517586]
- [wireless] rt2x00: fix work cancel race conditions (Stanislaw Gruszka) [562972]
- [net] igb: fix DCA support for 82580 NICs (Stefan Assmann) [513712]
- Revert: [ia64] kdump: fix a deadlock while redezvousing (Neil Horman) [506694]
- [block] cfq: kick busy queues w/o waiting for merged req (Jeff Moyer) [570814]
- [fs] cifs: max username len check in setup does not match (Jeff Layton) [562947]
- [fs] cifs: CIFS shouldn't make mountpoints shrinkable (Jeff Layton) [562947]
- [fs] cifs: fix dentry hash for case-insensitive mounts (Jeff Layton) [562947]
- [fs] cifs: fix len for converted unicode readdir names (Jeff Layton) [562947]
- [x86_64] xen: fix missing 32-bit syscalls on 64-bit Xen (Christopher Lalancette) [559410]
- [fs] gfs2: fix kernel BUG when using fiemap (Abhijith Das) [569610]
- [net] sctp: backport cleanups for ootb handling (Neil Horman) [555667] {CVE-2010-0008}
- [xen] vtd: ignore unknown DMAR entries (Don Dugger) [563900]

* Mon Mar 01 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-191.el5]
- [wireless] iwlwifi: fix dual band N-only use on 5x00 (Stanislaw Gruszka) [566696]
- [net] be2net: critical bugfix from upstream (Ivan Vecera) [567718]
- [net] tg3: fix 5717 and 57765 asic revs panic under load (John Feeney) [565964]
- [net] bnx2x: use single tx queue (Stanislaw Gruszka) [567979]
- [net] igb: fix WoL initialization when disabled in eeprom (Stefan Assmann) [564102]
- [net] igb: fix warning in igb_ethtool.c (Stefan Assmann) [561076]
- [net] s2io: restore ability to tx/rx vlan traffic (Neil Horman) [562732]
- [net] ixgbe: stop unmapping DMA buffers too early (Andy Gospodarek) [568153]
- [net] e1000e: disable NFS filtering capabilites in ICH hw (Andy Gospodarek) [558809]
- [net] bnx2: update firmware and version to 2.0.8 (Andy Gospodarek) [561578]
- [net] mlx4: fix broken SRIOV code (Doug Ledford) [567730]
- [net] mlx4: pass eth attributes down to vlan interfaces (Doug Ledford) [557109]
- [x86_64] fix missing 32 bit syscalls on 64 bit (Wade Mealing) [559410]
- [s390] zcrypt: Do not remove coprocessor on error 8/72 (Hendrik Brueckner) [561067]
- [misc] usb-serial: add support for Qualcomm modems (Pete Zaitcev) [523888]
- [scsi] mpt2sas: fix missing initialization (Tomas Henzl) [565637]
- [i386] mce: avoid deadlocks during MCE broadcasts (Prarit Bhargava) [562862]
- [x86_64] k8: do not mark early_is_k8_nb as __init (Paolo Bonzini) [567275]
- [ia64] kdump: fix a deadlock while redezvousing (Neil Horman) [506694]
- [dm] raid45: constructor error path oops fix (Heinz Mauelshagen) [565494]
- [mm] prevent severe performance degradation hang fix (Dave Anderson) [544448]
- [net] cxgb3: memory barrier addition fixup (Steve Best) [561957]

* Mon Feb 22 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-190.el5]
- [x86_64] mce: avoid deadlocks during MCE broadcasts (Prarit Bhargava) [562866]
- [scsi] device_handler: add netapp to alua dev list (Mike Christie) [562080]
- [misc] wacom: add Intuos4 support (Don Zickus) [502708]
- [scsi] be2iscsi: fix eh bugs and enable new hw support (Mike Christie) [564145]
- [net] ixgbe: initial support of ixgbe PF and VF drivers (Andy Gospodarek) [525577]
- [fs] ext4: avoid divide by 0 when mounting corrupted fs (Eric Sandeen) [547253]
- [net] bnx2x: update to 1.52.1-6 firmware (Stanislaw Gruszka) [560556]
- [net] bnx2x: update to 1.52.1-6 (Stanislaw Gruszka) [560556]
- [misc] hvc_iucv: alloc send/receive buffers in DMA zone (Hendrik Brueckner) [566202]
- [net] ixgbe: prevent speculatively processing descriptors (Steve Best) [566309]
- [fs] fix randasys crashes x86_64 systems regression (Peter Bogdanovic) [562857]
- [scsi] fix bugs in fnic and libfc (Mike Christie) [565594]
- [net] tg3: fix 57765 LED (John Feeney) [566016]
- [net] tg3: fix race condition with 57765 devices (John Feeney) [565965]
- [fs] gfs2: use correct GFP for alloc page on write (Steven Whitehouse) [566221]
- [scsi] lpfc: update version for 8.2.0.63.3p release (Rob Evers) [564506]
- [scsi] lpfc: fix driver build issues in rhel5.5 (Rob Evers) [564506]
- [scsi] lpfc: relax event queue field checking (Rob Evers) [564506]
- [scsi] lpfc: implement the PORT_CAPABITIES mailbox cmd (Rob Evers) [564506]
- [scsi] lpfc: fix a merge issue (Rob Evers) [564506]
- [scsi] lpfc: Add support for new SLI features (Rob Evers) [564506]
- [scsi] lpfc: Add support for 64-bit PCI BAR region 0 (Rob Evers) [564506]
- [nfs] fix a deadlock in the sunrpc code (Steve Dickson) [548846]
- [fs] ecryptfs: fix metadata in xattr feature regression (Eric Sandeen) [553670]
- [scsi] qla2xxx: return FAILED if abort command fails (Rob Evers) [559972]
- [virtio] fix module loading for virtio-balloon module (Anthony Liguori) [564361]
- [mm] xen: make mmap() with PROT_WRITE (Andrew Jones) [562761]
- [hwmon] w83627hf: fix data to platform_device_add_data (Dean Nelson) [557172]
- [hwmon] smsc47m1: fix data to platform_device_add_data (Dean Nelson) [560944]
- [hwmon] it87: fix sio_data to platform_device_add_data (Dean Nelson) [559950]
- [hwmon] f71805f: fix sio_data to platform_device_add_data (Dean Nelson) [564399]
- [base] make platform_device_add_data accept const pointer (Dean Nelson) [557172 559950 560944 564399]
- [net] forcedeth: fix putting system into S4 (Matthew Garrett) [513203]
- [net] netfilter: allow changing queue length via netlink (Steve Best) [562945]
- [mm] i386: fix iounmap's use of vm_struct's size field (Danny Feng) [549465]
- [ppc] fix sched while atomic error in alignment handler (Steve Best) [543637]
- [pci] aer: disable advanced error reporting by default (Prarit Bhargava) [559978]
- [s390] qeth: set default BLKT settings by OSA hw level (Hendrik Brueckner) [559621]
- [net] e1000e: fix deadlock unloading module on some ICH8 (Andy Gospodarek) [555818]
- [misc] rwsem: fix a bug in rwsem_is_locked() (Amerigo Wang) [526092]
- [s390] clear high-order bits after switch to 64-bit mode (Hendrik Brueckner) [546302]

* Tue Feb 16 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-189.el5]
- [net] wireless fixes from 2.6.32.7 (John Linville) [559711]
- [net] wireless fixes from 2.6.32.4 (John Linville) [559711]
- [net] wireless fixes through 2.6.32.3 (John Linville) [559711]
- [net] wireless fixes from 2.6.32.2 (John Linville) [559711]

* Mon Feb 15 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-188.el5]
- [net] be2net: latest bugfixes from upstream for rhel5.5 (Ivan Vecera) [561322]
- [infiniband] fix bitmask handling from QP control block (Steve Best) [561953]
- [infiniband] fix issue w/sleep in interrupt ehca handler (Steve Best) [561952]
- [char] ipmi: fix ipmi_watchdog deadlock (Tony Camuso) [552675]
- [net] cnic: additional fixes for rhel5.5 update (Mike Christie) [517378]
- [net] cxgb3: add memory barriers (Steve Best) [561957]
- [fs] nfsv4: distinguish expired from stale stateid (Wade Mealing) [514654]
- [net] igb: fix msix_other interrupt masking (Stefan Assmann) [552348]
- [net] niu: fix deadlock when using bonding (Andy Gospodarek) [547943]
- [x86] xen: invalidate dom0 pages before starting guest (Christopher Lalancette) [466681]
- [cpufreq] powernow-k8: fix crash on AMD family 0x11 procs (Bhavna Sarathy) [555180]
- [misc] ptrace: PTRACE_KILL hangs in 100% cpu loop (Vitaly Mayatskikh) [544138]
- [scsi] megaraid: fix 32-bit apps on 64-bit kernel (Tomas Henzl) [518243]
- [misc] fix APIC and TSC reads for guests (Prarit Bhargava) [562006]
- [mm] fix sys_move_pages infoleak (Eugene Teo) [562590] {CVE-2010-0415}
- [fs] aio: fix .5% OLTP perf regression from eventfd (Jeff Moyer) [548565]
- [net] sky2: fix initial link state errors (Andy Gospodarek) [559329]
- [x86_64] wire up compat sched_rr_get_interval (Danny Feng) [557092]
- [net] netfilter: enforce CAP_NET_ADMIN in ebtables (Danny Feng) [555243] {CVE-2010-0007}
- [misc] fix kernel info leak with print-fatal-signals=1 (Danny Feng) [554584] {CVE-2010-0003}
- [fs] gfs2: don't withdraw on partial rindex entries (Benjamin Marzinski) [553447]
- [net] ipv6: fix OOPS in ip6_dst_lookup_tail (Thomas Graf) [552354]
- [misc] khungtaskd: set PF_NOFREEZE flag to fix suspend (Amerigo Wang) [550014]
- [block] loop: fix aops check for GFS (Josef Bacik) [549397]

* Mon Feb 08 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-187.el5]
- [misc] EDAC driver fix for non-MMCONFIG systems (Bhavna Sarathy) [550123]
- [misc] audit: fix breakage and leaks in audit_tree.c (Alexander Viro) [549750]
- [mm] prevent hangs during memory reclaim on large systems (Larry Woodman) [546428]
- [usb] support more Huawei modems (Pete Zaitcev) [517454]
- [x86] fix AMD M-C boot inside xen on pre-5.5 hypervisor (Paolo Bonzini) [560013]
- [kvm] pvclock on i386 suffers from double registering (Glauber Costa) [557095]
- [md] fix kernel panic releasing bio after recovery failed (Takahiro Yasui) [555171]
- [md] fix deadlock at suspending mirror device (Takahiro Yasui) [555120]
- [pci] VF can't be enabled in dom0 (Don Dutile) [547980]
- [acpi] fix NULL pointer panic in acpi_run_os (Prarit Bhargava) [547733]
- [kvm] kvmclock won't restore properly after resume (Glauber Costa) [539521]
- [x86_64] export additional features in cpuinfo for xen (Prarit Bhargava) [517928]
- [fs] proc: make smaps readable even after setuid (Dave Anderson) [322881]
- [net] iptables: fix routing of REJECT target packets (Jiri Olsa) [548079]
- [net] niu: fix the driver to be functional with vlans (Jiri Pirko) [538649]
- [mm] prevent performance hit for 32-bit apps on x86_64 (Larry Woodman) [544448]
- [mm] mmap: don't ENOMEM when mapcount is temp exceeded (Danny Feng) [552648]
- [fs] proc: make errno values consistent when race occurs (Danny Feng) [556545]
- [net] igb: update driver to support End Point DCA (Stefan Assmann) [513712]
- [scsi] qla2xxx: FCP2 update, dpc bug, fast mailbox read (Rob Evers) [550286]
- [scsi] qla2xxx: fix timeout value for CT passthru cmds (Rob Evers) [552327]
- [scsi] lpfc: update to version 8.2.0.63.p2 (Rob Evers) [557792]
- [scsi] lpfc: update driver to version 8.2.0.63.1p FC/FCoE (Rob Evers) [555604]
- [scsi] be2iscsi: upstream driver refresh for rhel5.5 (Mike Christie) [554545]
- [pci] add ids for intel b43 graphics controller (John Villalovos) [523637]
- [misc] support new Nehalem processors in Oprofile (John Villalovos) [521992]
- [scsi] scsi_dh: make rdac hw handler's activate() async (Rob Evers) [537514]
- [scsi] scsi_dh: change scsidh_activate interface to async (Rob Evers) [537514]
- [alsa] support Creative X-Fi EMU20K1 and EMU20K2 chips (Jaroslav Kysela) [523786]
- [net] tg3: update to version 3.106 for 57765 asic support (John Feeney) [545135]
- [net] bonding: fix alb mode locking regression (Andy Gospodarek) [533496]
- [scsi] stex: don't try to scan a nonexistent lun (David Milburn) [531488]
- [scsi] bnx2i: additional fixes for rhel5.5 update (Mike Christie) [517378]
- [misc] hpilo: fix build warning in ilo_isr (Tony Camuso) [515010]
- [scsi] qla2xxx: add AER support (Rob Evers) [513927]
- [x86] relocate initramfs so we can increase vmalloc space (Neil Horman) [499253]
- [mm] memory mapped files not updating timestamps (Peter Staubach) [452129]

* Wed Jan 27 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-186.el5]
- [net] emergency route cache flushing fixes (Thomas Graf) [545663] {CVE-2009-4272}
- [fs] fasync: split 'fasync_helper()' into separate add/remove functions (Danny Feng) [548657] {CVE-2009-4141}
- [scsi] qla2xxx: NPIV vport management pseudofiles are world writable (Tom Coughlan) [537318] {CVE-2009-3556}
- [net] ipv6: fix ipv6_hop_jumbo remote system crash (Amerigo Wang) [548643] {CVE-2007-4567}
- [net] e1000e: fix broken wol (Andy Gospodarek) [557974]
- [net] r8169: add missing hunk from frame length filtering fix (Jarod Wilson) [552438]

* Thu Jan 14 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-185.el5]
- [net] e1000e: fix rx length check errors (Amerigo Wang) [551223] {CVE-2009-4538}
- [net] e1000: fix rx length check errors (Neil Horman) [552138] {CVE-2009-4536}
- [net] r8169: improved frame length filtering (Neil Horman) [550915] {CVE-2009-4537}
- kabi: fix dma_async_register symbol move (Jarod Wilson) [526342]
- [kabi] add {napi,vlan}_gro_receive and intel dca symbols (Jon Masters) [526342]
- Revert: amd64_edac: fix access to pci conf space type 1 (Jarod Wilson) [479070]

* Wed Jan 13 2010 Jarod Wilson <jarod@redhat.com> [2.6.18-184.el5]
- [scsi] lpfc: Update lpfc to version 8.2.0.63 driver release (Rob Evers) [549763]
- [scsi] lpfc: Fix single SCSI buffer not handled on SLI4 (Rob Evers) [549763]
- [scsi] lpfc: Fix Dead FCF not triggering discovery others (Rob Evers) [549763]
- [scsi] lpfc: Fix vport->fc_flag set outside of lock fail (Rob Evers) [549763]
- [scsi] lpfc: Fix processing of failed read fcf record (Rob Evers) [549763]
- [scsi] lpfc: Fix fc header seq_count checks (Rob Evers) [549763]
- [scsi] lpfc: Update to version 8.2.0.62 driver release (Rob Evers) [549763]
- [scsi] lpfc: Fix hbq buff only for sli4 (Rob Evers) [549763]
- [scsi] lpfc: Fix hbq buff adds to receive queue (Rob Evers) [549763]
- [scsi] lpfc: Fix multi-frame sequence response frames (Rob Evers) [549763]
- [scsi] lpfc: Fix adapter reset and off/online stress test (Rob Evers) [549763]
- [scsi] lpfc: Update to version 8.2.0.61 driver release (Rob Evers) [549763]
- [scsi] lpfc: Fix vport register VPI after devloss timeout (Rob Evers) [549763]
- [scsi] lpfc: Fix crash during unload and sli4 abort cmd (Rob Evers) [549763]
- [scsi] lpfc: Blocked all SCSI I/O requests from midlayer (Rob Evers) [549763]
- [scsi] lpfc: Made TigerShark set up and use single FCP EQ (Rob Evers) [549763]
- [scsi] lpfc: Update to 8.2.0.60 driver release (Rob Evers) [549763]
- [scsi] lpfc: Fix vport not logging out when being deleted (Rob Evers) [549763]
- [net] fixup problems with vlans and bonding (Andy Gospodarek) [526976]
- [net] ixgbe: upstream update to include 82599-KR support (Andy Gospodarek) [513707]
- [net] enic: update to upstream version 1.1.0.241a (Andy Gospodarek) [550148]
- [net] be2net: multiple bug fixes (Ivan Vecera) [549460]
- [net] virtio_net: fix tx wakeup race condition (Herbert Xu) [524651]
- [net] add send/receive tracepoints (Neil Horman) [475457]
- [iscsi] fix install panic w/xen iSCSI boot device (Miroslav Rezanina) [512991]
- Revert: [mm] SRAT and NUMA fixes for span and/or is disc (Larry Woodman) [474097]
- [misc] oprofile support for nehalme ep processors (John Villalovos) [498624]
- [scsi] fix duplicate libiscsi symbol and kabi warnings (Jarod Wilson) [515284]
- [edac] amd64_edac: fix access to pci conf space type 1 (Bhavna Sarathy) [479070]
- [misc] do not evaluate WARN_ON condition twice (Hendrik Brueckner) [548653]
- [xen] fix cpu frequency scaling on Intel procs (Christopher Lalancette) [553324]
- [xen] passthrough MSI-X mask bit acceleration V3 (Don Dugger) [537734]
- [xen] change interface of hvm_mmio_access V3 (Don Dugger) [537734]
- [xen] fix msix table fixmap allocation V3 (Don Dugger) [537734]

* Mon Dec 21 2009 Jarod Wilson <jarod@redhat.com> [2.6.18-183.el5]
- [kabi] add scsi_dma_{,un}map (Jon Masters) [533489]
- [kabi] add scsi_nl_{send_vendor_msg,{add,remove}_driver} (Jon Masters) [515812]
- [kabi] add do_settimeofday and __user_walk_fd (Jon Masters) [486205]
- [kabi] add pci_domain_nr (Jon Masters) [450121]
- [sound] alsa hda driver update for rhel5.5 (Jaroslav Kysela) [525390]
- Revert: [pci] avoid disabling acpi to use non-core PCI (Mauro Carvalho Chehab) [504330 547898]
- [net] wireless: fix build when using O=objdir (John Linville) [546712]
- [pci] remove msi-x vector allocation limitation (Stefan Assmann) [531266]
- [net] vxge: avoid netpoll<->NAPI race (Michal Schmidt) [453683]
- [scsi] update fcoe for rhel5.5 (Mike Christie) [526259]
- [net] update tg3 driver to version 3.100 (John Feeney) [515312]
- [block] fix rcu accesses in partition statistics code (Jerome Marchand) [493517]
- [pci] enable acs p2p upstream forwarding (Chris Wright) [518305]
- [net] e1000e: support for 82567V-3 and MTU fixes (Andy Gospodarek) [513706]
- [pci] aer hest disable support (Prarit Bhargava) [547762]
- [pci] aer hest firmware first support (Prarit Bhargava) [547762]
- [block] iosched: fix batching fairness (Jeff Moyer) [462472]
- [block] iosched: reset batch for ordered requests (Jeff Moyer) [462472]
- [net] bonding: allow arp_ip_targets on separate vlan from bond device (Andy Gospodarek) [526976]
- [firewire] ohci: handle receive packets with zero data (Jay Fenlason) [547242] {CVE-2009-4138}
- [drm] intel: add IRONLAKE support to AGP/DRM drivers (Dave Airlie) [547908]
- [xen] mask AMD's Node ID MSR (Andrew Jones) [547518]
- Revert: [xen] fix msi-x table fixmap allocation (Don Dugger) [537734]
- Revert: [xen] change interface of hvm_mmio_access (Don Dugger) [537734]
- Revert: [xen] passthrough msi-x mask bit acceleration (Don Dugger) [537734]

* Tue Dec 15 2009 Don Zickus <dzickus@redhat.com> [2.6.18-182.el5]
- [x86_64] disable vsyscall in kvm guests (Glauber Costa) [542612]
- [fs] ext3: replace lock_super with explicit resize lock (Eric Sandeen) [525100]
- [net] bonding: add debug module option (Jiri Pirko) [546624]
- [fs] respect flag in do_coredump (Danny Feng) [544189] {CVE-2009-4036}
- [md] fix a race in dm-raid1 (Mikulas Patocka) [502927]
- [misc] timer: add tracepoints (Jason Baron) [534178]
- [net] ipv4: fix possible invalid memory access (Prarit Bhargava) [541213]
- [x86] support AMD L3 cache index disable (Bhavna Sarathy) [517586]
- [scsi] add emc clariion support to scsi_dh modules (Mike Christie) [437107]
- [infiniband] fix iser sg aligment handling (Mike Christie) [540686]
- [scsi] qla2xxx: CT passthrough and link data rate fixes (Marcus Barrow) [543057]
- [scsi] qla2xxx: update to 8.03.01.04.05.05-k (Marcus Barrow) [542834]
- [net] s2io: update driver to current upstream version (Michal Schmidt) [513942]
- [ia64] export cpu_core_map (like i386 and x86_64) (Michal Schmidt) [448856]
- [net] sfc: additional fixes for rhel5.5 (Michal Schmidt) [448856]
- [redhat] configs: enable building of the sfc driver (Michal Schmidt) [448856]
- [net] sfc: add the sfc (Solarflare) driver (Michal Schmidt) [448856]
- [net] vxge: driver update to 2.0.6 (Michal Schmidt) [453683]
- [scsi] ibmvscsi: upstream multipath enhancements for 5.5 (Kevin Monroe) [512203]

* Mon Dec 14 2009 Don Zickus <dzickus@redhat.com> [2.6.18-181.el5]
- [vfs] DIO write returns -EIO on try_to_release_page fail (Jeff Moyer) [461100]
- [wireless] enable use of internal regulatory database (John Linville) [546712]
- [wireless] add wireless regulatory rules database (John Linville) [546712]
- [wireless] use internal regulatory database infrastructure (John Linville) [546712]
- [wireless] update old static regulatory domain rules (John Linville) [543723]
- [net] wireless: report reasonable bitrate for 802.11n (John Linville) [546281]
- [net] mac80211: report correct signal for non-dBm values (John Linville) [545899]
- [net] wireless: kill some warning spam (John Linville) [545121]
- [net] mac80211: avoid uninit ptr deref in ieee80211 (John Linville) [545121]
- [net] wireless: avoid deadlock when enabling rfkill (John Linville) [542593]
- [wireless] configuration changes for updates (John Linville) [456943 474328 514661 516859]
- [net] ath9k: backport driver from 2.6.32 (John Linville) [456943]
- [net] wireless: updates of mac80211 etc from 2.6.32 (John Linville) [474328 514661 516859]
- [net] wireless support updates from 2.6.32 (John Linville) [456943 474328 514661 516859]
- [net] bnx2: update to version 2.0.2 (John Feeney) [517377]
- [usb] support lexar expresscard (Pete Zaitcev) [511374]
- [net] cnic: update driver for RHEL5.5 (Stanislaw Gruszka) [517378]
- [net] bnx2x: update to 1.52.1-5 (Stanislaw Gruszka) [515716 522600]
- [net] bnx2x: add mdio support (Stanislaw Gruszka) [515716 522600]
- [net] bnx2x: add firmware version 5.2.7.0 (Stanislaw Gruszka) [515716 522600]
- [net] bnx2x: update to 1.52.1 (Stanislaw Gruszka) [515716 522600]
- [fs] make NR_OPEN tunable (Eric Sandeen) [507159]
- [net] mdio: add mdio module from upstream (Michal Schmidt) [448856]
- [net] ethtool: add more defines for mdio to use (Michal Schmidt) [448856]
- [pci] add and export pci_clear_master (Michal Schmidt) [448856]
- [mm] SRAT and NUMA fixes for span and/or is discontig mem (Larry Woodman) [474097]
- [fs] eventfd: remove fput call from possible IRQ context (Jeff Moyer) [493101]
- [fs] eventfd: kaio integration fix (Jeff Moyer) [493101]
- [fs] eventfd: sanitize anon_inode_getfd() (Jeff Moyer) [493101]
- [fs] eventfd: should #include <linux/syscalls.h> (Jeff Moyer) [493101]
- [fs] eventfd: clean compile when CONFIG_EVENTFD=n (Jeff Moyer) [493101]
- [s390] wire up signald, timerfd and eventfd syscalls (Jeff Moyer) [493101]
- [fs] eventfd: use waitqueue lock (Jeff Moyer) [493101]
- [ppc] wire up eventfd syscalls (Jeff Moyer) [493101]
- [ia64] wire up {signal, timer, event}fd syscalls (Jeff Moyer) [493101]
- [fs] aio: KAIO eventfd support example (Jeff Moyer) [493101]
- [fs] eventfd: wire up x86 arches (Jeff Moyer) [493101]
- [fs] add eventfd core (Jeff Moyer) [493101]
- [net] r8169: update to latest upstream for rhel5.5 (Ivan Vecera) [540582]
- [net] benet: update driver to latest upstream for rhel5.5 (Ivan Vecera) [515269]
- [net] e1000e: update and fix WOL issues (Andy Gospodarek) [513706 513930 517593 531086]
- [net] e1000: update to latest upstream for rhel5.5 (Dean Nelson) [515524]
- [net] mlx4: update to recent version with SRIOV support (Doug Ledford) [503113 512162 520674 527499 529396 534158]
- [md] raid: deal with soft lockups during resync (Doug Ledford) [501075]
- [x86] amd: add node ID MSR support (Bhavna Sarathy) [530181]
- [net] ipv4: fix an unexpectedly freed skb in tcp (Amerigo Wang) [546402]

* Fri Dec 11 2009 Don Zickus <dzickus@redhat.com> [2.6.18-180.el5]
- [fs] ext4: fix insufficient checks in EXT4_IOC_MOVE_EXT (Eric Sandeen) [546105] {CVE-2009-4131}
- [fs] fix possible inode corruption on unlock (Eric Sandeen) [545612]
- [fs] xfs: fix fallocate error return sign (Eric Sandeen) [544349]
- [net] bnx2: fix frags index (Flavio Leitner) [546326]
- [pci] implement public pci_ioremap_bar function (Prarit Bhargava) [546244]
- [trace] add coredump tracepoint (Masami Hiramatsu) [517115]
- [trace] add signal tracepoints (Masami Hiramatsu) [517121]
- [trace] add itimer tracepoints (Jason Baron) [534178]
- [gfs2] make O_APPEND behave as expected (Steven Whitehouse) [544342]
- [gfs2] fix rename locking issue (Steven Whitehouse) [538484]
- [usb] add quirk for iso on amd sb800 (Pete Zaitcev) [537433]
- [mm] add kernel pagefault tracepoint for x86 & x86_64 (Larry Woodman) [517133]
- [ia64] dma_get_required_mask altix workaround (George Beshers) [517192]
- [misc] sysctl: require CAP_SYS_RAWIO to set mmap_min_addr (Amerigo Wang) [534018]
- [pci] intel-iommu: no pagetable validate in passthru mode (Don Dutile) [518103]
- [pci] intel-iommu: set dmar_disabled when DMAR at zero (Don Dutile) [516811 518103]
- [pci] dmar: rhsa entry decode (Don Dutile) [516811 518103]
- [pci] intel-iommu: add hot (un)plug support (Don Dutile) [516811 518103]
- [pci] inte-iommu: alloc_coherent obey coherent_dma_mask (Don Dutile) [516811 518103]
- [pci] dmar: check for DMAR at zero BIOS error earlier (Don Dutile) [516811 518103]
- [pci] intel-iommu: fix for isoch dmar w/no tlb space (Don Dutile) [516811 518103]
- [pci] intel-iommu: add 2.6.32-rc4 sw and hw pass-through (Don Dutile) [516811 518103]
- [pci] intel-iommu: IOTLB flushing mods & ATSR support (Don Dutile) [516811 518103]
- [aio] implement request batching (Jeff Moyer) [532769]
- [net] netxen: further p3 updates for rhel5.5 (Marcus Barrow) [542746]
- [net] netxen: driver updates from 2.6.32 (Marcus Barrow) [516833]
- [net] netxen: driver updates from 2.6.31 (Marcus Barrow) [516833]
- [xen] passthrough msi-x mask bit acceleration (Don Dugger) [537734]
- [xen] change interface of hvm_mmio_access (Don Dugger) [537734]
- [xen] fix msi-x table fixmap allocation (Don Dugger) [537734]
- [xen] fix w/sata set to ide combined mode on amd (Bhavna Sarathy) [544021]
- [xen] domU irq ratelimiting (Don Dugger) [524747]

* Thu Dec 10 2009 Don Zickus <dzickus@redhat.com> [2.6.18-179.el5]
- [scsi] st: display current settings of option bits (Tom Coughlan) [501030]
- [pci] AER: prevent errors being reported multiple times (Prarit Bhargava) [544923]
- [cifs] NULL out pointers when chasing DFS referrals (Jeff Layton) [544417]
- [fbfront] xenfb: don't recreate thread on every restore (Christopher Lalancette) [541325]
- [net] igb: update igb driver to support barton hills (Stefan Assmann) [513710]
- [fs] hfs: fix a potential buffer overflow (Amerigo Wang) [540741] {CVE-2009-4020}
- [fuse] prevent fuse_put_request on invalid pointer (Danny Feng) [538737] {CVE-2009-4021}
- [scsi] lpfc: update version from 8.2.0.58 to 8.2.0.59 (Rob Evers) [529244]
- [scsi] lpfc: update version from 8.2.0.55 to 8.2.0.58 (Rob Evers) [516541 529244]
- [scsi] lpfc: update version from 8.2.0.52 to 8.2.0.55 (Rob Evers) [529244]
- [scsi] pmcraid: minor driver update for rhel5.5 (Rob Evers) [529979]
- [scsi] add pmcraid driver (Rob Evers) [529979]
- [scsi] bfa: brocade bfa fibre-channel/fcoe driver (Rob Evers) [475695]
- [md] support origin size < chunk size (Mikulas Patocka) [502965]
- [md] lock snapshot while reading status (Mikulas Patocka) [543307]
- [md] fix deadlock in device mapper multipath (Mikulas Patocka) [543270]
- [md] raid5: mark cancelled readahead bios with -EIO (Eric Sandeen) [512552]
- [fs] ext2: convert to new aops (Josef Bacik) [513136]
- [fs] jbd: fix race in slab creation/deletion (Josef Bacik) [496847]
- [net] enic: update to upstream version 1.1.0.100 (Andy Gospodarek) [519086]
- [scsi] megaraid: make driver legacy I/O port free (Tomas Henzl) [515863]
- [scsi] megaraid: upgrade to version 4.17-RH1 (Tomas Henzl) [518243]
- [net] ipvs: synchronize closing of connections (Danny Feng) [492942]
- [fs] dlm: fix connection close handling (David Teigland) [521093]
- [hwmon] add support for syleus chip to fschmd driver (Dean Nelson) [513101]
- [s390] dasd: fix DIAG access for read-only devices (Hendrik Brueckner) [537859]
- [acpi] backport support for ACPI 4.0 power metering (Matthew Garrett) [514923]
- [scsi] mpt2sas: use selected regions (Tomas Henzl) [516702]
- [scsi] mpt2sas: upgrade to 01.101.06.00 (Tomas Henzl) [516702]
- [block] blktrace: only tear down our own debug/block (Eric Sandeen) [498489]
- Revert: [scsi] fix inconsistent usage of max_lun (David Milburn) [531488]

* Wed Dec 09 2009 Don Zickus <dzickus@redhat.com> [2.6.18-178.el5]
- [x86] fix stale data in shared_cpu_map cpumasks (Prarit Bhargava) [541953]
- [mm] call vfs_check_frozen after unlocking the spinlock (Amerigo Wang) [541956]
- [md] fix data corruption with different chunksizes (Mikulas Patocka) [210490]
- [md] fix snapshot crash on invalidation (Mikulas Patocka) [461506]
- [net] cxgb3: fix port index issue (Doug Ledford) [516948]
- [net] cxgb3: correct hex/decimal error (Doug Ledford) [516948]
- [net] mlx4_en: add a pci id table (Doug Ledford) [508770]
- [infiniband] null out skb pointers on error (Doug Ledford) [531784]
- [infiniband] init neigh->dgid.raw on bonding events (Doug Ledford) [538067]
- [nfs] add an nfsiod workqueue (Ian Kent) [489931]
- [nfs] nfsiod: ensure the asynchronous RPC calls complete (Ian Kent) [489931]
- [nfs] sunrpc: allow rpc_release() CB run on another workq (Ian Kent) [489931]
- [nfs] fix a deadlock with lazy umount -2 (Ian Kent) [489931]
- [nfs] fix a deadlock with lazy umount (Ian Kent) [489931]
- [fs] ext3/4: free journal buffers (Eric Sandeen) [506217]
- [net] resolve issues with vlan creation and filtering (Andy Gospodarek) [521345]
- [scsi] stex: update driver for RHEL-5.5 (David Milburn) [516881]
- [scsi] be2iscsi: add driver to generic config (Mike Christie) [515284]
- [scsi] add be2iscsi driver (Mike Christie) [515284]
- [fs] ext4: update to 2.6.32 codebase (Eric Sandeen) [528054]
- [scsi] disable state transition from OFFLINE to RUNNING (Takahiro Yasui) [516934]
- [scsi] fusion: update mpt driver to 3.4.13rh (Tomas Henzl) [516710]
- [net] gro: fix illegal merging of trailer trash (Herbert Xu) [537876]

* Thu Dec 03 2009 Don Zickus <dzickus@redhat.com> [2.6.18-177.el5]
- [scsi] gdth: prevent negative offsets in ioctl (Amerigo Wang) [539421] {CVE-2009-3080}
- [net] ixgbe: add and enable CONFIG_IXGBE_DCA (Andy Gospodarek) [514306]
- [net] ixgbe: update to upstream version 2.0.44-k2 (Andy Gospodarek) [513707 514306 516699]
- [cifs] duplicate data on appending to some samba servers (Jeff Layton) [500838]
- [s390] kernel: fix single stepping on svc0 (Hendrik Brueckner) [540527]
- [fs] gfs2: fix glock ref count issues (Steven Whitehouse) [539240]
- [vbd] xen: fix crash after ballooning (Christopher Lalancette) [540811]
- [block] cfq-iosched: get rid of cfqq hash (Jeff Moyer) [427709 448130 456181]
- [scsi] devinfo update for hitachi entries for RHEL5.5 (Takahiro Yasui) [430631]
- [net] call cond_resched in rt_run_flush (Amerigo Wang) [517588]
- [cifs] update cifs version number (Jeff Layton) [500838]
- [cifs] avoid invalid kfree in cifs_get_tcp_session (Jeff Layton) [500838]
- [cifs] fix broken mounts when a SSH tunnel is used (Jeff Layton) [500838]
- [cifs] fix memory leak in ntlmv2 hash calculation (Jeff Layton) [500838]
- [cifs] fix potential NULL deref in parse_DFS_referrals (Jeff Layton) [500838]
- [cifs] fix read buffer overflow (Jeff Layton) [500838]
- [cifs] free nativeFileSystem before allocating new one (Jeff Layton) [500838]
- [cifs] add addr= mount option alias for ip= (Jeff Layton) [500838]
- [cifs] copy struct *after* setting port, not before (Jeff Layton) [500838]
- [cifs] fix artificial limit on reading symlinks (Jeff Layton) [500838]
- [scsi] megaraid: fix sas permissions in sysfs (Casey Dahlin) [537313] {CVE-2009-3889 CVE-2009-3939}
- [cpufreq] avoid playing with cpus_allowed in powernow-k8 (Alex Chiang) [523505]
- [cpufreq] change cpu freq arrays to per_cpu variables (Alex Chiang) [523505]
- [cpufreq] powernow-k8: get drv data for correct cpu (Alex Chiang) [523505]
- [cpufreq] x86: change NR_CPUS arrays in powernow-k8 (Alex Chiang) [523505]
- [cifs] fix error handling in mount-time dfs referral code (Jeff Layton) [513410]
- [cifs] add loop check when mounting dfs tree (Jeff Layton) [513410]
- [cifs] fix some build warnings (Jeff Layton) [513410]
- [cifs] fix build when dfs support not enabled (Jeff Layton) [513410]
- [cifs] remote dfs root support (Jeff Layton) [513410]
- [cifs] enable dfs submounts to handle remote referrals (Jeff Layton) [513410]
- [edac] i3200_edac: backport driver to RHEL 5.5 (Mauro Carvalho Chehab) [469976]
- [edac] add upstream i3200_edac driver (Mauro Carvalho Chehab) [469976]
- [cifs] no CIFSGetSrvInodeNumber in is_path_accessible (Jeff Layton) [529431]
- [block] blktrace: correctly record block to and from devs (Jason Baron) [515551]
- [sched] enable CONFIG_DETECT_HUNG_TASK support (Amerigo Wang) [506059]
- [xen] fix SRAT check for discontiguous memory (Christopher Lalancette) [519225]
- [xen] implement fully preemptible page table teardown (Christopher Lalancette) [510037]

* Tue Dec 01 2009 Don Zickus <dzickus@redhat.com> [2.6.18-176.el5]
- [xen] mask extended topo cpuid feature (Andrew Jones ) [533292]
- [fs] pipe.c null pointer dereference (Jeff Moyer ) [530939] {CVE-2009-3547}
- [xen] cd-rom drive does not recognize new media (Miroslav Rezanina ) [221676]
- [nfs] fix stale nfs_fattr passed to nfs_readdir_lookup (Harshula Jayasuriya ) [531016]
- [spec] s390: enable kernel module signing (Don Zickus ) [483665]
- [nfs] bring nfs4acl into line with mainline code (Jeff Layton ) [479870 530575]
- [ia64] kdump: restore registers in the stack on init (Takao Indoh ) [515753]
- [nfs] nfsd4: do exact check of attribute specified (Jeff Layton ) [512361]
- [net] igb: add support for 82576ns serdes adapter (Stefan Assmann ) [517063]
- [s390] zfcp_scsi: dynamic queue depth adjustment param (Pete Zaitcev ) [508355]
- [scsi] fix inconsistent usage of max lun (David Milburn ) [531488]
- [ipmi] fix ipmi_si modprobe hang (Tony Camuso ) [507402]
- [x86] kvm: don't ask HV for tsc khz if not using kvmclock (Glauber Costa ) [531268]
- [net] qlge: updates and fixes for RHEL-5.5 (Marcus Barrow ) [519453]
- [net] igb: fix kexec with igb controller (Stefan Assmann ) [527424]
- [net] qlge: fix crash with kvm guest device passthru (Marcus Barrow ) [507689]
- [misc] hpilo: add polling mechanism (Tony Camuso ) [515010]
- [misc] hpilo: add interrupt handler (Tony Camuso ) [515010]
- [misc] hpilo: staging for interrupt handling (Tony Camuso ) [515010]
- [edac] amd64_edac: enable driver in kernel config (Bhavna Sarathy ) [479070]
- [edac] amd64_edac: remove early hardware probe (Bhavna Sarathy ) [479070]
- [edac] amd64_edac: detect ddr3 support (Bhavna Sarathy ) [479070]
- [edac] amd64_edac: add ddr3 support (Bhavna Sarathy ) [479070]
- [edac] add amd64_edac driver (Bhavna Sarathy ) [479070]
- [net] igb: set vf rlpml must take vlan tag into account (Don Dugger ) [515602]
- [misc] hibernate: increase timeout (Matthew Garrett ) [507331]
- [nfs] make sure dprintk() macro works everywhere (Jeff Layton ) [532701]
- [acpi] include core wmi support and dell-wmi driver (Matthew Garrett ) [516623]
- [powerpc] fix to handle SLB resize during migration (Kevin Monroe ) [524112]
- [mm] oom killer output should display UID (Larry Woodman ) [520419]
- [net] fix race in data receive/select (Amerigo Wang ) [509866]
- [net] augment raw_send_hdrinc to validate ihl in user hdr (Neil Horman ) [500924]
- [i2c] include support for Hudson-2 SMBus controller (Stanislaw Gruszka ) [515125]
- [net] bonding: introduce primary_reselect option (Jiri Pirko ) [471532]
- [net] bonding: ab_arp use std active slave select code (Jiri Pirko ) [471532]
- [net] use netlink notifications to track neighbour states (Danny Feng ) [516589]
- [net] introduce generic function __neigh_notify (Danny Feng ) [516589]
- [fs] skip inodes w/o pages to free in drop_pagecache_sb (Larry Woodman ) [528070]

* Fri Nov 20 2009 Don Zickus <dzickus@redhat.com> [2.6.18-175.el5]
- [net] bnx2x: add support for bcm8727 phy (Stanislaw Gruszka ) [515716]
- [net] sched: fix panic in bnx2_poll_work (John Feeney ) [526481]
- [acpi] prevent duplicate dirs in /proc/acpi/processor (Matthew Garrett ) [537395]
- [mm] conditional flush in flush_all_zero_pkmaps (Eric Sandeen ) [484683]
- [fs] ecryptfs: copy lower attrs before dentry instantiate (Eric Sandeen ) [489774]
- [ppc] fix compile warnings in eeh code (Prarit Bhargava ) [538407]
- [md] multiple device failure renders dm-raid1 unfixable (Jonathan E Brassow ) [498532]
- [scsi] ibmvscsi: FCoCEE NPIV support (Steve Best ) [512192]
- [fs] gfs2: fix potential race in glock code (Steven Whitehouse ) [498976]
- [kvm] balloon driver for guests (Peter Bogdanovic ) [522629]
- [sctp] assign tsns earlier to avoid reordering (Neil Horman ) [517504]
- [x86] fix boot crash with < 8-core AMD Magny-cours system (Bhavna Sarathy) [522215]
- [x86] support amd magny-cours power-aware scheduler fix (Bhavna Sarathy ) [513685]
- [x86] cpu: upstream cache fixes needed for amd m-c (Bhavna Sarathy ) [526315]
- [x86_64] set proc id and core id before calling fixup_dcm (Bhavna Sarathy) [526315]
- [x86] disable NMI watchdog on CPU remove (Prarit Bhargava ) [532514]
- [nfsd] don't allow setting ctime over v4 (Jeff Layton ) [497909]
- [acpi] bm_check and bm_control update (Luming Yu ) [509422]
- [x86_64] amd: iommu system management erratum 63 fix (Bhavna Sarathy ) [531469]
- [net] bnx2i/cnic: update driver version for RHEL5.5 (Mike Christie ) [516233]
- [x86] fix L1 cache by adding missing break (Bhavna Sarathy ) [526770]
- [x86] amd: fix hot plug cpu issue on 32-bit magny-cours (Bhavna Sarathy ) [526770]
- [acpi] disable ARB_DISABLE on platforms where not needed (Luming Yu ) [509422]
- [s390] do not annotate cmdline as __initdata (Hendrik Brueckner ) [506898]
- [x86_64] fix 32-bit process register leak (Amerigo Wang ) [526798]
- [misc] don't call printk while crashing (Mauro Carvalho Chehab ) [497195]
- [x86] mce_amd: fix up threshold_bank4 creation (Bhavna Sarathy ) [526315]
- [pci] fix SR-IOV function dependency link problem (Don Dugger ) [503837]
- [xen] fix numa on magny-cours systems (Bhavna Sarathy ) [526051]
- [xen] add two HP ProLiant DMI quirks to the hypervisor (Paolo Bonzini ) [536677]
- [xen] hook sched rebalance logic to opt_hardvirt (Christopher Lalancette ) [529271]
- [xen] crank the correct stat in the scheduler (Christopher Lalancette ) [529271]
- [xen] whitespace fixups in xen scheduler (Christopher Lalancette ) [529271]
- [xen] fix crash with memory imbalance (Bhavna Sarathy ) [526785]

* Mon Nov 16 2009 Don Zickus <dzickus@redhat.com> [2.6.18-174.el5]
- [fs] private dentry list to avoid dcache_lock contention (Lachlan McIlroy ) [526612]
- [gfs2] drop rindex glock on grows (Benjamin Marzinski ) [482756]
- [acpi] run events on cpu 0 (Matthew Garrett ) [485016]
- [cpufreq] add option to avoid smi while calibrating (Matthew Garrett ) [513649]
- [acpi] support physical cpu hotplug on x86_64 (Stefan Assmann ) [516999]
- [scsi] qla2xxx: enable msi-x correctly on qlogic 2xxx series (Marcus Barrow ) [531593]
- [apic] fix server c1e spurious lapic timer events (Bhavna Sarathy ) [519422]
- [pci] aer: fix ppc64 compile - no msi support (Prarit Bhargava ) [514442 517093]
- [pci] aer: config changes to enable aer support (Prarit Bhargava ) [514442 517093]
- [pci] aer: fix NULL pointer in aer injection code (Prarit Bhargava ) [514442 517093]
- [pci] aer: add domain support to aer_inject (Prarit Bhargava ) [514442 517093]
- [pci] aer: backport acpi osc functions (Prarit Bhargava ) [517093]
- [pci] aer: pcie support and compile fixes (Prarit Bhargava ) [517093]
- [pci] aer: changes required to compile in RHEL5 (Prarit Bhargava ) [514442 517093]
- [pci] aer: base aer driver support (Prarit Bhargava ) [514442 517093]
- [kvm] use upstream kvm_get_tsc_khz (Glauber Costa ) [531025]
- [cifs] turn oplock breaks into a workqueue job (Jeff Layton ) [531005]
- [cifs] fix oplock request handling in posix codepath (Jeff Layton ) [531005]
- [cifs] have cifsFileInfo hold an extra inode reference (Jeff Layton ) [531005]
- [cifs] take GlobalSMBSes_lock as read-only (Jeff Layton ) [531005]
- [cifs] remove cifsInodeInfo.oplockPending flag (Jeff Layton ) [531005]
- [cifs] replace wrtPending with a real reference count (Jeff Layton ) [531005]
- [cifs] clean up set_cifs_acl interfaces (Jeff Layton ) [531005]
- [cifs] reorganize get_cifs_acl (Jeff Layton ) [531005]
- [cifs] protect GlobalOplock_Q with its own spinlock (Jeff Layton ) [531005]
- [scsi] qla2xxx: updates and fixes for RHEL-5.5 (Marcus Barrow ) [519447]
- [net] vlan: silence multicast debug messages (Danny Feng ) [461442]
- [fs] fix inode_table test in ext{2,3}_check_descriptors (Eric Sandeen ) [504797]
- [net] netlink: fix typo in initialization (Jiri Pirko ) [527906]
- [mm] prevent tmpfs from going readonly during oom kills (Larry Woodman ) [497257]
- [x86] set cpu_llc_id on AMD CPUs (Bhavna Sarathy ) [513684]
- [x86] fix up threshold_bank4 support on AMD Magny-cours (Bhavna Sarathy ) [513684]
- [x86] fix up L3 cache information for AMD Magny-cours (Bhavna Sarathy ) [513684]
- [x86] amd: fix CPU llc_shared_map information (Bhavna Sarathy ) [513684]
- [fs] trim instantiated file blocks on write errors (Eric Sandeen ) [515529]
- [s390] optimize storage key operations for anon pages (Hans-Joachim Picht ) [519977]
- [net] cxgb3: bug fixes from latest upstream version (Doug Ledford ) [510818]
- [misc] saner FASYNC handling on file close (Paolo Bonzini ) [510746]
- [wireless] mac80211: fix reported wireless extensions version (John Linville ) [513430]
- [mm] don't oomkill when hugepage alloc fails on node (Larry Woodman ) [498510]
- [xen] iommu-amd: extend loop ctr for polling completion wait (Bhavna Sarathy ) [518474 526766]
- [xen] iommu: add passthrough and no-intremap parameters (Bhavna Sarathy ) [518474 526766]
- [xen] iommu: enable amd iommu debug at run-time (Bhavna Sarathy ) [518474 526766]
- [xen] support interrupt remapping on M-C (Bhavna Sarathy ) [518474 526766]
- [xen] iommu: move iommu_setup() to setup ioapic correctly (Bhavna Sarathy ) [518474 526766]

* Mon Nov 09 2009 Don Zickus <dzickus@redhat.com> [2.6.18-173.el5]
- [acpi] thinkpad_acpi: disable ecnvram brightness on some (Matthew Garrett ) [522745]
- [block] cfq-iosched: don't delay queue kick for merged req (Jeff Moyer ) [456181 448130 427709]
- [block] cfq-iosched: fix idling interfering with plugging (Jeff Moyer ) [456181 448130 427709]
- [block] cfq: separate merged cfqqs if they stop cooperating (Jeff Moyer ) [456181 448130 427709]
- [block] cfq: change the meaning of the cfqq_coop flag (Jeff Moyer ) [456181 448130 427709]
- [block] cfq: merge cooperating cfq_queues (Jeff Moyer ) [456181 448130 427709]
- [block] cfq: calc seek_mean per cfq_queue not per cfq_io_context (Jeff Moyer ) [456181 448130 427709]
- [block] cfq-iosched: cache prio_tree root in cfqq->p_root (Jeff Moyer ) [456181 448130 427709]
- [block] cfq-iosched: fix aliased req & cooperation detect (Jeff Moyer ) [456181 448130 427709]
- [block] cfq-iosched: default seek when not enough samples (Jeff Moyer ) [456181 448130 427709]
- [block] cfq-iosched: make seek_mean converge more quick (Jeff Moyer ) [456181 448130 427709]
- [block] cfq-iosched: add close cooperator code (Jeff Moyer ) [456181 448130 427709]
- [block] cfq-iosched: development update (Jeff Moyer ) [456181 448130 427709]
- [gfs2] careful unlinking inodes (Steven Whitehouse ) [519049]
- [scsi] arcmsr: add missing parameter (Tomas Henzl ) [521203]
- [nfs] v4: fix setting lock on open file with no state (Jeff Layton ) [533115] {CVE-2009-3726}
- [misc] futex priority based wakeup (Jon Thomas ) [531552]
- [dlm] use GFP_NOFS on all lockspaces (David Teigland ) [530537]
- [gfs2] improve statfs and quota usability (Benjamin Marzinski ) [529796]
- [net] forcedeth: let phy power down when IF is down (Ivan Vecera ) [513692]
- [drm] r128: check for init on all ioctls that require it (Danny Feng ) [529603] {CVE-2009-3620}
- [scsi] htpiop: RocketRAID driver update v1.0 -> v1.6 (Rob Evers ) [519076]
- [ipmi] add HP message handling (Tony Camuso ) [507402]
- [mm] prevent hangs/long pauses when zone_reclaim_mode=1 (Larry Woodman ) [507360]
- [s390] ipl: vmhalt, vmpanic, vmpoff, vmreboot don't work (Hans-Joachim Picht ) [518229]
- [nfs] bring putpubfh handling inline with upstream (Wade Mealing ) [515405]

* Mon Nov 02 2009 Don Zickus <dzickus@redhat.com> [2.6.18-172.el5]
- [fs] dio: don't zero out pages array inside struct dio (Jeff Moyer ) [488161]
- [cifs] libfs: sb->s_maxbytes casts to a signed value (Jeff Layton ) [486092]
- [serial] power7: support the single-port serial device (Kevin Monroe ) [525812]
- [kABI] add pci_{enable,disable}_msi{,x} (Jon Masters ) [521081]
- [scsi] mpt: errata 28 fix on LSI53C1030 (Tomas Henzl ) [518689]
- [scsi] panic at .ipr_sata_reset after device reset (Kevin Monroe ) [528175]
- [scsi] lpfc: update to 8.2.0.52 FC/FCoE (Rob Evers ) [515272]
- [x86] add ability to access Nehalem uncore config space (John Villalovos ) [504330]
- [net] sunrpc: remove flush_workqueue from xs_connect (Jeff Layton ) [495059]
- [xen] ia64: command-line arg to increase the heap size (Paolo Bonzini ) [521865]

* Mon Oct 26 2009 Don Zickus <dzickus@redhat.com> [2.6.18-171.el5]
- [security] require root for mmap_min_addr (Eric Paris ) [518143] {CVE-2009-2695}
- [ata] ahci: add AMD SB900 controller device IDs (David Milburn ) [515114]
- [net] lvs: adjust sync protocol handling for ipvsadm -2 (Neil Horman ) [524129]
- Revert: [net] lvs: fix sync protocol handling for timeout values (Neil Horman ) [524129]
- [net] AF_UNIX: deadlock on connecting to shutdown socket (Jiri Pirko ) [529631] {CVE-2009-3621}
- [fs] inotify: remove debug code (Danny Feng ) [499019]
- [fs] inotify: fix race (Danny Feng ) [499019]

* Tue Oct 20 2009 Don Zickus <dzickus@redhat.com> [2.6.18-170.el5]
- [net] lvs: fix sync protocol handling for timeout values (Neil Horman ) [524129]
- [net] igb: return PCI_ERS_RESULT_DISCONNECT on failure (Dean Nelson ) [514250]
- [net] e100: return PCI_ERS_RESULT_DISCONNECT on failure (Dean Nelson ) [514250]
- [nfs] knfsd: query fs for v4 getattr of FATTR4_MAXNAME (Jeff Layton ) [469689]
- [block] blkfront: respect elevator=xyz cmd line option (Paolo Bonzini ) [498461]
- [firewire] fw-ohci: fix IOMMU resource exhaustion (Jay Fenlason ) [513827]
- [scsi] cciss: ignore stale commands after reboot (Tomas Henzl ) [525440]
- [scsi] cciss: version change (Tomas Henzl ) [525440]
- [scsi] cciss: switch to using hlist (Tomas Henzl ) [525440]
- [x86] support always running Local APIC (John Villalovos ) [496306]
- [x86_64] fix hugepage memory tracking (Jim Paradis ) [518671]
- [net] bnx2: apply BROKEN_STATS workaround to 5706/5708 (Flavio Leitner ) [527748]
- [pci] pci_dev->is_enabled must be set (Prarit Bhargava ) [527496]
- [audit] dereferencing krule as if it were an audit_watch (Alexander Viro ) [526819]
- [mm] fix spinlock performance issue on large systems (John Villalovos ) [526078]
- [misc] hotplug: add CPU_DYING notifier (Eduardo Habkost ) [510814]
- [misc] hotplug: use cpuset hotplug callback to CPU_DYING (Eduardo Habkost ) [510814]
- [misc] define CPU_DYING and CPU_DYING_FROZEN (Eduardo Habkost ) [510814]
- [misc] hotplug: adapt thermal throttle to CPU_DYING (Eduardo Habkost ) [510814]
- [fs] file truncations when both suid and write perms set (Amerigo Wang ) [486975]
- [x86] finish sysdata conversion (Danny Feng ) [519633]
- [misc] pipe: fix fd leaks (Amerigo Wang ) [509625]
- [x86_64] PCI space below 4GB forces mem remap above 1TB (Larry Woodman ) [523522]
- [pci] pciehp: fix PCIe hotplug slot detection (Michal Schmidt ) [521731]
- [net] syncookies: support for TCP options via timestamps (jolsa@redhat.com ) [509062]
- [net] tcp: add IPv6 support to TCP SYN cookies (jolsa@redhat.com ) [509062]
- [xen] blkfront: check for out-of-bounds array accesses (Paolo Bonzini ) [517238]
- [xen] fix timeout with PV guest and physical CDROM (Paolo Bonzini ) [506899]
- [net] e1000e: return PCI_ERS_RESULT_DISCONNECT on fail (Dean Nelson ) [508387]
- [x86_64] vsmp: fix bit-wise operator and compile issue (Prarit Bhargava ) [515408]
- [net] e100: add support for 82552 (Dean Nelson ) [475610]
- [net] netfilter: honour source routing for LVS-NAT (Jiri Pirko ) [491010]
- [misc] hwmon: update to latest upstream for RHEL-5.5 (Prarit Bhargava ) [467994 250561 446061]
- [xen] panic in msi_msg_read_remap_rte with acpi=off (Miroslav Rezanina ) [525467]
- [xen] mask out xsave for hvm guests (Andrew Jones ) [524052]
- [xen] allow booting with broken serial hardware (Chris Lalancette ) [518338]
- [xen] mask out more CPUID bits for PV guests (Chris Lalancette ) [502826]
- [xen] x86: fix wrong asm (Paolo Bonzini ) [510686]
- [xen] always inline memcmp (Paolo Bonzini) [510686]
- [xen] i386: handle x87 opcodes in TLS segment fixup (Paolo Bonzini ) [510225]

* Mon Oct 12 2009 Don Zickus <dzickus@redhat.com> [2.6.18-169.el5]
- [scsi] export symbol scsilun_to_int (Tomas Henzl ) [528153]
- [fs] eCryptfs: prevent lower dentry from going negative (Eric Sandeen ) [527835] {CVE-2009-2908}
- [nfs] v4: reclaimer thread stuck in an infinite loop (Sachin S. Prabhu ) [526888]
- [scsi] scsi_dh_rdac: changes for rdac debug logging (Rob Evers ) [524335]
- [scsi] scsi_dh_rdac: collect rdac debug info during init (Rob Evers ) [524335]
- [scsi] scsi_dh_rdac: move init code around (Rob Evers ) [524335]
- [scsi] scsi_dh_rdac: return correct mode select cmd info (Rob Evers ) [524335]
- [scsi] scsi_dh_rdac: add support for Dell PV array (Rob Evers ) [524335]
- [scsi] scsi_dh_rdac: add support for SUN devices (Rob Evers ) [524335]
- [scsi] scsi_dh_rdac: support ST2500, ST2510 and ST2530 (Rob Evers ) [524335]
- [s390] cio: boot through XAUTOLOG with conmode 3270 (Hans-Joachim Picht ) [508934]
- [x86] add smp_call_function_many/single functions (Prarit Bhargava ) [526043]
- [s390] iucv: fix output register in iucv_query_maxconn (Hans-Joachim Picht ) [524251]
- [s390] set preferred s390 console based on conmode (Hans-Joachim Picht ) [520461]
- [s390] dasd: add large volume support (Hans-Joachim Picht ) [511972]
- [s390] dasd: fail requests when dev state is not ready (Hans-Joachim Picht ) [523219]
- [s390] cio: failing set online/offline processing (Hans-Joachim Picht ) [523323]
- [x86] oprofile: support arch perfmon (John Villalovos ) [523479]
- [x86] oprofile: fix K8/core2 on multiple cpus (John Villalovos ) [523479]
- [x86] oprofile: utilize perf counter reservation (John Villalovos ) [523479]
- [gfs2] genesis stuck writing to unlinked file (Abhijith Das ) [505331]
- [net] r8169: avoid losing MSI interrupts (Ivan Vecera ) [514589]
- [s390] cio: set correct number of internal I/O retries (Hans-Joachim Picht ) [519814]
- [net] e1000: return PCI_ERS_RESULT_DISCONNECT on fail (Dean Nelson ) [508389]
- [net] ixgbe: return PCI_ERS_RESULT_DISCONNECT on fail (Dean Nelson ) [508388]
- [crypto] s390: enable ansi_cprng config option (Jarod Wilson ) [504667]
- [s390] dasd: dev attr to disable blocking on lost paths (Hans-Joachim Picht ) [503222]
- [s390] qeth: handle VSwitch Port Isolation error codes (Hans-Joachim Picht ) [503232]
- [s390] qeth: improve no_checksumming handling for layer3 (Hans-Joachim Picht ) [503238]
- [gfs2] smbd proccess hangs with flock call (Abhijith Das ) [502531]
- [input] psmouse: reenable mouse on shutdown (Prarit Bhargava ) [501025]
- [xen] x86: make NMI detection work (Miroslav Rezanina ) [494120]

* Mon Oct 05 2009 Don Zickus <dzickus@redhat.com> [2.6.18-168.el5]
- [gfs2] mount option: -o errors=withdraw|panic (Bob Peterson ) [518106]
- [net] bonding: set primary param via sysfs (Jiri Pirko ) [499884]
- [scsi] fusion: re-enable mpt_msi_enable option (Tomas Henzl ) [520820]
- [x86] xen: add 'ida' flag (Prarit Bhargava ) [522846]
- [net] ipt_recent: sanity check hit count (Amerigo Wang ) [523982]
- [acpi] fix syntax in ACPI debug statement (Stefan Assmann ) [524787]
- [s390] AF_IUCV SOCK_SEQPACKET support (Hans-Joachim Picht ) [512006]
- [x86] fix nosmp option (Prarit Bhargava ) [509581]
- [nfs] nfsd4: idmap upcalls should use unsigned uid/gid (Jeff Layton ) [519184]
- [ia64] fix ppoll and pselect syscalls (Prarit Bhargava ) [520867]
- [net] ipv4: ip_append_data handle NULL routing table (Jiri Pirko ) [520297]
- [net] fix drop monitor to not panic on null dev (Neil Horman ) [523279]
- [gfs2] gfs2_delete_inode failing on RO filesystem (Abhijith Das ) [501359]
- [nfs] statfs error-handling fix (Jeff Layton ) [519112]
- [pci] avoid disabling acpi to use non-core PCI devices (Mauro Carvalho Chehab ) [504330]
- [nfs] fix regression in nfs_open_revalidate (Jeff Layton ) [511278]
- [nfs] fix cache invalidation problems in nfs_readdir (Jeff Layton ) [511170]
- [fs] sanitize invalid partition table entries (Stefan Assmann ) [481658]
- [char] fix corrupted intel_rng kernel messages (Jerome Marchand ) [477778]
- [net] ipv6: do not fwd pkts with the unspecified saddr (Jiri Pirko ) [517899]
- [ata] ahci: add device ID for 82801JI sata controller (David Milburn ) [506200]
- [misc] support Intel multi-APIC-cluster systems (Prarit Bhargava ) [507333]
- [ext3] fix online resize bug (Josef Bacik ) [515759]
- [xen] netback: call netdev_features_changed (Herbert Xu ) [493092]
- [net] igbvf: recognize failure to set mac address (Stefan Assmann ) [512469]
- [misc] documentation: fix file-nr definition in fs.txt (Danny Feng ) [497200]
- [misc] cpufreq: don't set policy for offline cpus (Prarit Bhargava ) [511211]
- [net] sunrpc client: IF for binding to a local address (Jeff Layton ) [500653]
- [fs] nlm: track local address and bind to it for CBs (Jeff Layton ) [500653]
- [net] sunrpc: set rq_daddr in svc_rqst on socket recv (Jeff Layton ) [500653]
- [cpufreq] P-state limit: limit can never be increased (Stanislaw Gruszka ) [489566]
- [crypto] s390: permit weak keys unless REQ_WEAK_KEY set (Jarod Wilson ) [504667]
- [fs] procfs: fix fill all subdirs as DT_UNKNOWN (Danny Feng ) [509713]
- [block] ll_rw_blk: more flexable read_ahead_kb store (Danny Feng ) [510257]
- [audit] correct the record length of execve (Amerigo Wang ) [509134]
- [net] tcp: do not use TSO/GSO when there is urgent data (Danny Feng ) [502572]
- [net] vxge: new driver for Neterion 10Gb Ethernet (Michal Schmidt ) [453683]
- [net] vxge: Makefile, Kconfig and config additions (Michal Schmidt ) [453683]
- [pci] add PCI Express link status register definitions (Michal Schmidt ) [453683]
- [net] 8139too: RTNL and flush_scheduled_work deadlock (Jiri Pirko ) [487346]
- [x86] suspend-resume: work on large logical CPU systems (John Villalovos ) [499271]
- [gfs2] '>>' does not update ctime,mtime on the file (Abhijith Das ) [496716]
- [net] icmp: fix icmp_errors_use_inbound_ifaddr sysctl (Jiri Pirko ) [502822]
- [nfs] fix stripping SUID/SGID flags when chmod/chgrp dir (Peter Staubach ) [485099]
- [net] bonding: allow bond in mode balance-alb to work (Jiri Pirko ) [487763]
- [x86] fix mcp55 apic routing (Neil Horman ) [473404]
- [net] rtl8139: set mac address on running device (Jiri Pirko ) [502491]
- [net] tun: allow group ownership of TUN/TAP devices (Jiri Pirko ) [497955]
- [net] tcp: do not use TSO/GSO when there is urgent data (Jiri Olsa ) [497032]
- [misc] undefined reference to `__udivdi3' (Amerigo Wang ) [499063]

* Wed Sep 30 2009 Don Zickus <dzickus@redhat.com> [2.6.18-167.el5]
- [scsi] st.c: memory use after free after MTSETBLK ioctl (David Jeffery ) [520192]
- [nfs] knfsd: fix NFSv4 O_EXCL creates (Jeff Layton ) [524521] {CVE-2009-3286}
- [net] r8169: balance pci_map/unmap pair, use hw padding (Ivan Vecera ) [515857]
- [net] tc: fix unitialized kernel memory leak (Jiri Pirko ) [520863]
- [misc] kthreads: kthread_create vs kthread_stop() race (Oleg Nesterov ) [440273]
- [net] fix unbalance rtnl locking in rt_secret_reschedule (Neil Horman ) [510067]

* Sat Sep 19 2009 Don Zickus <dzickus@redhat.com> [2.6.18-166.el5]
- [x86_64] kvm: bound last_kvm to prevent backwards time (Glauber Costa ) [524076]
- [x86] kvm: fix vsyscall going backwards (Glauber Costa ) [524076]
- [misc] fix RNG to not use first generated random block (Neil Horman ) [522860]
- [x86] kvm: mark kvmclock_init as cpuinit (Glauber Costa ) [523450]
- [x86_64] kvm: allow kvmclock to be overwritten (Glauber Costa ) [523447]
- [x86] kvmclock: fix bogus wallclock value (Glauber Costa ) [519771]
- [scsi] scsi_dh_rdace: add more sun hardware (mchristi@redhat.com ) [518496]
- [misc] cprng: fix cont test to be fips compliant (Neil Horman ) [523259]
- [net] bridge: fix LRO crash with tun (Andy Gospodarek ) [483646]
- Revert: [net] atalk/irda: memory leak to user in getname (Don Zickus ) [519310] {CVE-2009-3001 CVE-2009-3002}
- Revert: [x86_64] fix gettimeoday TSC overflow issue - 1 (Don Zickus ) [467942]

* Thu Sep 03 2009 Don Zickus <dzickus@redhat.com> [2.6.18-165.el5]
- [net] sky2: revert some phy power refactoring changes (Neil Horman ) [509891]
- [net] atalk/irda: memory leak to user in getname (Danny Feng ) [519310] {CVE-2009-3001 CVE-2009-3002}
- [x86_64] fix gettimeoday TSC overflow issue - 1 (Prarit Bhargava ) [467942]
- [md] prevent crash when accessing suspend_* sysfs attr (Danny Feng ) [518136] {CVE-2009-2849}
- [nfs] nlm_lookup_host: don't return invalidated nlm_host (Sachin S. Prabhu ) [507549]
- [net] bonding: tlb/alb: set active slave when enslaving (Jiri Pirko ) [499884]
- [nfs] r/w I/O perf degraded by FLUSH_STABLE page flush (Peter Staubach ) [498433]
- [SELinux] allow preemption b/w transition perm checks (Eric Paris ) [516216]
- [scsi] scsi_transport_fc: fc_user_scan correction (David Milburn ) [515176]
- [net] tg3: refrain from touching MPS (John Feeney ) [516123]
- [net] qlge: fix hangs and read performance (Marcus Barrow ) [517893]
- [scsi] qla2xxx: allow use of MSI when MSI-X disabled (Marcus Barrow ) [517922]
- [net] mlx4_en fix for vlan traffic (Doug Ledford ) [514141]
-  [net] mlx4_en device multi-function patch (Doug Ledford ) [500346]
- [net] mlx4_core: fails to load on large systems (Doug Ledford ) [514147]
- [x86] disable kvmclock by default (Glauber Costa ) [476075]
- [x86] disable kvmclock when shuting the machine down (Glauber Costa ) [476075]
- [x86] re-register clock area in prepare_boot_cpu (Glauber Costa ) [476075]
- [x86] kvmclock smp support (Glauber Costa ) [476075]
- [x86] use kvm wallclock (Glauber Costa ) [476075]
- [x86_64] kvm clocksource's implementation (Glauber Costa ) [476075]
- [x86] kvm: import kvmclock.c (Glauber Costa ) [476075]
- [x86] kvm: import pvclock.c and headers (Glauber Costa ) [476075]
- [x86] export additional cpu flags in /proc/cpuinfo (Prarit Bhargava ) [517928]
- [x86] detect APIC clock calibration problems (Prarit Bhargava ) [503957]
- [fs] cifs: new opts to disable overriding of ownership (Jeff Layton ) [515252]
- [x86] pnpacpi: fix serial ports on IBM Point-of-Sale HW (Kevin Monroe ) [506799]

* Tue Aug 18 2009 Don Zickus <dzickus@redhat.com> [2.6.18-164.el5]
- [misc] information leak in sigaltstack (Vitaly Mayatskikh ) [515396]
- [misc] execve: must clear current->clear_child_tid (Oleg Nesterov ) [515429]
- [net] igb: set lan id prior to configuring phy (Stefan Assmann ) [508870]
- [net] udp: socket NULL ptr dereference (Vitaly Mayatskikh ) [518043] {CVE-2009-2698}

* Fri Aug 14 2009 Don Howard <dhoward@redhat.com> [2.6.18-163.el5]
- [net] make sock_sendpage use kernel_sendpage (Danny Feng ) [516955] {CVE-2009-2692}

* Tue Aug 04 2009 Don Zickus <dzickus@redhat.com> [2.6.18-162.el5]
- [x86_64] Intel IOMMU: Pass Through Support (Don Dutile ) [504363]

* Mon Aug 03 2009 Don Zickus <dzickus@redhat.com> [2.6.18-161.el5]
- [dlm] free socket in error exit path (David Teigland ) [508829]
- [net] tg3: fix concurrent migration of VM clients (John Feeney ) [511918]
- [scsi] mptfusion: revert to pci_map (Tomas Henzl ) [514049]
- [scsi] bnx2i: fix conn disconnection bugs (mchristi@redhat.com ) [513802]
- [scsi] qla2xxx: unable to destroy npiv HBA ports (Marcus Barrow ) [514352]
- [scsi] ALUA: send STPG if explicit and implicit (mchristi@redhat.com ) [482737]
- [scsi] megaraid: fix the tape drive issue (Tomas Henzl ) [510665]
- [scsi] cxgb3i: fix skb allocation (mchristi@redhat.com ) [514073]
- [fs] __bio_clone: don't calculate hw/phys segment counts (Milan Broz ) [512387]
- [fs] ecryptfs: check tag 11 packet data buffer size (Eric Sandeen ) [512863] {CVE-2009-2406}
- [fs] ecryptfs: check tag 3 packet encrypted key size (Eric Sandeen ) [512887] {CVE-2009-2407}
- [xen] amd iommu: crash with pass-through on large memory (Bhavna Sarathy ) [514910]

* Mon Jul 27 2009 Don Zickus <dzickus@redhat.com> [2.6.18-160.el5]
- [scsi] mptsas: fix max_id initialization (mchristi@redhat.com ) [455678]
- [ata] ahci: add IDs for Ibex Peak ahci controllers (David Milburn ) [513067]
- [scsi] lpfc: update to 8.2.0.48.2p, fix multiple panics (Rob Evers ) [512266]
- [gfs2] remove dcache entries for remote deleted inodes (Benjamin Marzinski ) [505548]
- [alsa] add native support for IbexPeak audio (Jaroslav Kysela ) [509526]
- [alsa] IbexPeak related patches for codec auto-config (Jaroslav Kysela ) [509526]
- [scsi] cciss: call bus_unregister in cciss_remove_one (Rob Evers ) [513070]
- [scsi] cciss: add driver sysfs entries (Rob Evers ) [513070]
- [net] e1000e/igb: make sure wol can be configured (Andy Gospodarek ) [513032]
- [fs] xfs: only compile for x86_64 (Eric Sandeen ) [512827]
- [ahci] add SATA GEN3 related messages (David Milburn ) [512086]
- [net] tun/tap: open /dev/net/tun and then poll() it fix (Danny Feng ) [512286] {CVE-2009-1897}
- [net] mlx4_en: problem with LRO that segfaults KVM host (Doug Ledford ) [510789]
- [openib] mthca: fix over sized kmalloc usage (Doug Ledford ) [508902]
- [s390] zcrypt: request gets timed out under high load (Hans-Joachim Picht ) [511289]

* Mon Jul 20 2009 Don Zickus <dzickus@redhat.com> [2.6.18-159.el5]
- [scsi] cciss: fix sysfs broken symlink regression (Rob Evers ) [510178]
- [kabi] add consume_skb (Jon Masters ) [479200]
- [net] ipv6: fix incorrect disable_ipv6 behavior (jolsa@redhat.com ) [512258]
- [net] ipv6: fix BUG when disabled module is unloaded (jolsa@redhat.com ) [512258]
- [net] ipv6: add 'disable' module parameter support (jolsa@redhat.com ) [512258]
- Revert: [mm] fix swap race in fork-gup patch group (Larry Woodman ) [508919]
- [scsi] mptfusion: fix OOPS in failover path (Rob Evers ) [504835]
- [scsi] stex: minimize DMA coherent allocation (David Milburn ) [486466]
- [misc] personality handling: fix PER_CLEAR_ON_SETID (Vitaly Mayatskikh ) [508842]
- [misc] build with -fno-delete-null-pointer-checks (Eugene Teo ) [511181]
- [scsi] qla2xxx: provide reset capability for EEH (Marcus Barrow ) [511141]
- [scsi] bnx2i: fix host setup and libiscsi abort locking (mchristi@redhat.com ) [511096]
- [xen] ia64: fix rmmod of PCI devices (Chris Lalancette ) [507520]
- [pci] kvm: PCI FLR support for device assignment (Don Dutile ) [510805]
- [gfs2] don't put unlikely reclaim glocks on reclaim list (Benjamin Marzinski ) [504335]

* Mon Jul 13 2009 Don Zickus <dzickus@redhat.com> [2.6.18-158.el5]
- [s390] add missing kernel option CONFIG_SHARED_KERNEL (Hans-Joachim Picht ) [506947]
- [gfs2] fix incorrent statfs_slow consistency check (Benjamin Marzinski ) [505171]
- [net] be2net: fix msix performance regression (Andy Gospodarek ) [510008]
- [gfs2] umount.gfs2 hangs eating CPU (Abhijith Das ) [508876]
- [block] protect the per-gendisk partition array with rcu (Jeff Moyer ) [495866]
- [net] igb: fix panic when assigning device to guest (Andy Gospodarek ) [507173]
- [ia64] xen: dom0 get/set_address_size (Chris Lalancette ) [510069]
- [x86] fix suspend/resume issue on SB800 chipset (Bhavna Sarathy ) [498135]
- [scsi] cciss: fix spinlock (Tomas Henzl ) [509818]
- [scsi] qla2xxx: NPIV broken for PPC, endian fix (Marcus Barrow ) [510268]
- [scsi] qla2xxx: prevent hangs in extended error handling (Marcus Barrow ) [470510]
- [mm] prevent softlockups in copy_hugetlb_page_range (Larry Woodman ) [508919]
- [scsi] cxgb3i: fix vlan support (mchristi@redhat.com ) [508409]
- [net] bnx2i: RHEL-5.4 code cleanups (mchristi@redhat.com ) [504181]
- [x86_64] import asm/svm.h and asm/vmx.h (Eduardo Habkost ) [507483]
- [x86_64] import asm/virtext.h (Eduardo Habkost ) [507483]
- [x86_64] add MSR_VM_* defines (Eduardo Habkost ) [507483]
- [x86_64] disable VMX and SVM on machine_crash_shutdown (Eduardo Habkost ) [507483]
- [x86_64] add EFER_SVME define (Eduardo Habkost ) [507483]
- [x86_64] define X86_CR4_VMXE (Eduardo Habkost ) [507483]
- [net] qlge: rhel-5.4 cleanups (Marcus Barrow ) [509647]
- [scsi] lpfc: fix ctx_idx increase and update version (Rob Evers ) [509010]
- [scsi] lpfc: move pointer ref. inside alloc check in (Rob Evers ) [509010]
- [scsi] lpfc: update to version 8.2.0.48 (Rob Evers ) [509010]
- [mm] fix re-read performance regression (Josef Bacik ) [506511]
- [net] ipsec: add missing braces to fix policy querying (Herbert Xu ) [462731]
- [net] tg3: 5785F and 50160M support (Andy Gospodarek ) [506205]
- [pci] intel-iommu: fix iommu address space allocation (Chris Wright ) [509207]
- [xen] virtio: do not statically allocate root device (Mark McLoughlin ) [501468]
- [xen] virtio: add PCI device release function (Mark McLoughlin ) [501468]
- [misc] driver core: add root_device_register (Mark McLoughlin ) [501468]
- [block] blktrace: fix recursive block remap tracepoint (Jason Baron ) [502573]
- [scsi] qla2xxx: rhel-5.4 fixes and cleanups (Marcus Barrow ) [507246]
- [xen] HV: remove high latency spin_lock (Chris Lalancette ) [459410]
- [xen] ia64: add get/set_address_size support (Chris Lalancette ) [510069]

* Mon Jul 06 2009 Don Zickus <dzickus@redhat.com> [2.6.18-157.el5]
- [mm] readv: sometimes returns less than it should (Amerigo Wang ) [500693]
- [net] be2net: fix races in napi and interrupt handling (Andy Gospodarek ) [508839]
- [net] be2net: fix deadlock with bonding (Andy Gospodarek ) [508871]
- [xen] quiet printk on FV guest shutdown (Don Dutile ) [501474]
- [fs] fuse: enable building the subsystem (Josef Bacik ) [457975]
- [gfs2] fix panic in glock memory shrinker (Benjamin Marzinski ) [508806]
- [net] rt2x00: use mac80211-provided workqueue (John W. Linville ) [506845]
- [pci] quirk: disable MSI on VIA VT3364 chipsets (Dean Nelson ) [501374]
- [net] undo vlan promiscuity count when unregistered (Neil Horman ) [481283]
- [net] be2net: crash on PPC with LRO and jumbo frames (Andy Gospodarek ) [508404]
- [net] RTNL: assertion failed due to bonding notify (Stanislaw Gruszka ) [508297]
- [scsi] ibmvfc: process async events before cmd responses (AMEET M. PARANJAPE ) [508127]
- [scsi] ibmvfc: fix endless PRLI loop in discovery (AMEET M. PARANJAPE ) [508127]
- [scsi] ibmvfc: improve LOGO/PRLO ELS handling (AMEET M. PARANJAPE ) [508127]
- [net] iucv: provide second per-cpu cmd parameter block (Hans-Joachim Picht ) [503240]
- [net] sky2: /proc/net/dev statistics are broken (Flavio Leitner ) [507932]
- [scsi] qla2xxx: prevent I/O stoppage (Marcus Barrow ) [507620]
- [scsi] qla2xxx: updates 24xx firmware to 4.04.09 (Marcus Barrow ) [507398]
- [scsi] qla2xxx: updates 25xx firmware to 4.04.09 (Marcus Barrow ) [507398]
- [scsi] qla4xxx: extended sense data errors, cleanups (Marcus Barrow ) [506981]
- [char] tty: prevent an O_NDELAY writer from blocking (Mauro Carvalho Chehab ) [506806]
- [xen] allow msi reconfigure for pt_bind_irq (ddugger@redhat.com ) [507970]

* Mon Jun 29 2009 Don Zickus <dzickus@redhat.com> [2.6.18-156.el5]
- [misc] kdump: make mcp55 chips work (Neil Horman ) [462519]
- [ide] enable VX800 to use UDMA mode (John Feeney ) [504121]
- [misc] wacom: reset state when tool is not in proximity (Aristeu Rozanski ) [499870]
- [scsi] lpfc: update to version 8.2.0.46 (Rob Evers ) [506792]
- [mm] prevent panic in copy_hugetlb_page_range (Larry Woodman ) [507860]
- [gfs2] keep statfs info in sync on grows (Benjamin Marzinski ) [494885]
- [gfs2] always queue work after after setting GLF_LOCK (Benjamin Marzinski ) [506140]
- [scsi] cxgb3i: use kref to track ddp, support page sizes (mchristi@redhat.com ) [506151]
- [security] drop mmap_min_addr to 4096 (Eric Paris ) [507017]
- [misc] hrtimer: fix a soft lockup (Amerigo Wang ) [418071] {CVE-2007-5966}
- [net] backport net_rx_action tracepoint (Neil Horman ) [506138]
- [gfs2] fix truncate buffered/direct I/O issue (Steven Whitehouse ) [504676]
- [xen] x86: fix IRQ problem on legacy hardware (ddugger@redhat.com ) [505491]
- [xen] disable 2MB support on PAE kernels (Bhavna Sarathy ) [503737]

* Fri Jun 19 2009 Don Zickus <dzickus@redhat.com> [2.6.18-155.el5]
- [mm] fix swap race condition in fork-gup-race patch (Andrea Arcangeli ) [506684]
- [net] e1000e: stop unnecessary polling when using msi-x (Andy Gospodarek ) [506841]

* Wed Jun 17 2009 Don Zickus <dzickus@redhat.com> [2.6.18-154.el5]
- [kABI] add smp_send_reschedule and get_user_pages_fast (Jon Masters ) [504038]
- [scsi] lpfc: update to version 8.2.0.45 (Rob Evers ) [505445]
- [fs] ext4: fix prealloc vs truncate corruption (Eric Sandeen ) [505601]
- [net] r8169: fix crash when large packets are received (Ivan Vecera ) [504732] {CVE-2009-1389}
- [pci] fix pcie save restore patch (Don Dutile ) [505541]
- [scsi] ibmvscsi: add 16 byte CDB support (AMEET M. PARANJAPE ) [502944]
- [infiniband] iw_cxgb3: add final fixups for 1.4.1 (Doug Ledford ) [504906]
- [infiniband] mlx4_en: hand remove XRC support (Doug Ledford ) [506097]
- [infiniband] cxgb3: update firmware from 7.1 to 7.4 (Doug Ledford ) [504955]
- [infiniband] ofed: backports from ofed 1.4.1 final bits (Doug Ledford ) [506097]
- [infiniband] RDS: Update to ofed 1.4.1 final bits (Doug Ledford ) [506097]
- [infiniband] mthca: update to ofed 1.4.1 final bits (Doug Ledford ) [506097]
- [net] cxgb3: support two new phys and page mapping fix (Doug Ledford ) [504955]
- [infiniband] ipoib/sdp: update to ofed 1.4.1 final bits (Doug Ledford ) [506097]
- [infiniband] OFED: back out XRC patch, not ready yet (Doug Ledford ) [506097]
- [infiniband] mlx4_en: update to ofed 1.4.1 final bits (Doug Ledford ) [506097]
- [infiniband] iw_nes: update to ofed 1.4.1 final bits (Doug Ledford ) [506097]
- [infiniband] OFED: fix broken switch statement (Doug Ledford ) [506097]
- [infiniband] OFED: removes this backport and all callers (Doug Ledford ) [506097]
- [infiniband] iw_cxgb3: update to ofed 1.4.1 final bits (Doug Ledford ) [506097]
- [infiniband] mlx4_ib: update to ofed 1.4.1 final bits (Doug Ledford ) [506097]
- [infiniband] remove duplicate definition (Doug Ledford ) [500368]
- [net] be2net: add intial support (Andy Gospodarek ) [490074]
- [net] ixgbe: backport fixups and bugfixes for 82599 (Andy Gospodarek ) [505653]
- [md] increase pg_init_in_progress only if work is queued (Jesse Larrew ) [489582]
- [x86_64] AMD IOMMU: fix GLX issue in bare metal (Bhavna Sarathy ) [504010]
- [scsi] libsas: use the supplied address for SATA devices (David Milburn ) [494658]
- [x86_64] amd iommu: fix kdump unknown partition table (Bhavna Sarathy ) [504751]
- [char] TPM: get_event_name stack corruption (Dean Nelson ) [503905]
- [net] e1000e: update to upstream version 1.0.2-k2 (Andy Gospodarek ) [480241]
- [crypto] add continuous test to hw rng in FIPS mode (Neil Horman ) [504218]
- [net] ehea: fix invalid pointer access (AMEET M. PARANJAPE ) [504679]
- [x86_64] amd iommu: fix spinlock imbalance (Bhavna Sarathy ) [501571]
- [x86_64] iommu: protect against broken IVRS ACPI table (Bhavna Sarathy ) [501571]
- [x86_64] amd iommu: fix flag masks (Bhavna Sarathy ) [501571]
- [x86_64] iommu: fix the handling of device aliases (Bhavna Sarathy ) [501571]
- [x86_64] amd iommu: fix an off-by-one error (Bhavna Sarathy ) [501571]
- [xen] x86: give dom0 access to machine e820 map (ddugger@redhat.com ) [503818]
- [pci] fix sr-iov regression with PCI device class (ddugger@redhat.com ) [503826]
- [scsi] qla4xxx: extended sense data errors (Marcus Barrow ) [489389]
- [scsi] qla4xxx: remove some dead code (Marcus Barrow ) [459449]
- [net] qla2xxx, ql8xxx : support for 10 GigE (Marcus Barrow ) [479288]

* Wed Jun 10 2009 Don Zickus <dzickus@redhat.com> [2.6.18-153.el5]
- [s390x] zfcpdump: move zfcpdump kernel removal to %post (Don Zickus ) [499629]
- [x86_64] kvm: fix libvirt based device assignment issue (Bhavna Sarathy ) [504165]
- [gfs2] get gfs2meta superblock correctly (Benjamin Marzinski ) [504086]
- [ptrace] fix do_coredump vs ptrace_start() deadlock (Oleg Nesterov ) [504157] {CVE-2009-1388}
- [scsi] ipr: fix PCI permanent error handler (AMEET M. PARANJAPE ) [503960]
- [scsi] IPR: adapter taken offline after first EEH error (AMEET M. PARANJAPE ) [504675]
- [scsi] lpfc: update to version 8.2.0.44 (Rob Evers ) [503248]
- [net] skb_seq_read: wrong offset/len for page frag data (mchristi@redhat.com ) [501308]
- [xen] netback: change back to a flipping interface (Chris Lalancette ) [479754]
- [fs] autofs4: remove hashed check in validate_wait (Ian Kent ) [490078]
- [ppc64] resolves issues with pcie-save-restore-state (AMEET M. PARANJAPE ) [504198]
- [net] gso: stop fraglists from escaping (Herbert Xu ) [499347]
- [tun] use non-linear packets where possible (Herbert Xu ) [503309]
- [net] skb_copy_datagram_from_iovec (Herbert Xu ) [503309]
- [net] tun: only wake up writers (Herbert Xu ) [503191]
- Re-apply: [net] tun: add packet accounting (Don Zickus ) [495863]
- [sched] fix cond_resched_softirq() offset (Jesse Larrew ) [496935]
- [ata] sata_sx4: fixup interrupt and exception handling (David Milburn ) [503827]
- Revert: [net] avoid extra wakeups in wait_for_packet (Don Zickus ) [497897]
- [net] e1000: fix skb_over_panic (Neil Horman ) [503441] {CVE-2009-1385}

* Wed Jun 03 2009 Don Zickus <dzickus@redhat.com> [2.6.18-152.el5]
- [x86_64] kvm: export symbols to allow building (john cooper ) [504038]
- [misc] s390 zfcpdump: check for another image on removal (Hans-Joachim Picht ) [499629]
- [net] ixgbe: fix MSI-X allocation on 8+ core systems (Andy Gospodarek ) [500857]
- [s390] dasd: add EMC ioctl to the driver (Christoph Hellwig ) [461288]
- [net] ixgbe: fix polling saturates CPU (Andy Gospodarek ) [503559]
- [misc] core dump: wrong thread info in core dump file (Amerigo Wang ) [503553]
- [crypto] testmgr: check all test vector lengths (Jarod Wilson ) [503091]
- [net] igb and igbvf: return from napi poll correctly (Andy Gospodarek ) [503215]
- [crypto] testmgr: dynamically allocate xbuf and axbuf (Jarod Wilson ) [503091]
- [fs] vfs: skip I_CLEAR state inodes in drop_pagecache_sb (Eric Sandeen ) [500164]
- Revert: [net] tun: add packet accounting (Herbert Xu ) [495863]
- [net] netxen: add GRO Support (Herbert Xu ) [499347]
- [nfs] v4: 'r'/'w' perms for user do not work on client (Peter Staubach ) [502244]
- [x86] nmi: add Intel cpu 0x6f4 to perfctr1 workaround (Prarit Bhargava ) [500892]
- [dm] raid45 target: kernel oops in constructor (Heinz Mauelshagen ) [503070]
- [net] sky2: fix sky2 stats (Neil Horman ) [503080]
- [acpi] check _PSS frequency to prevent cpufreq crash (Prarit Bhargava ) [500311]
- [scsi] mvsas: sync w/ appropriate upstream changes (Rob Evers ) [485126]
- [scsi] mvsas: comment cleanup (Rob Evers ) [485126]
- [scsi] mvsas: correct bit-map implementation (Rob Evers ) [485126]
- [scsi] mvsas: initial patch submission (Rob Evers ) [485126]
- [net] add broadcom cnic driver (mchristi@redhat.com ) [441979]
- [scsi] add bnx2i iscsi driver (mchristi@redhat.com ) [441979]
- [scsi] add netlink msg to iscsi IF to support offload (mchristi@redhat.com ) [441979]
- [misc] add UIO framework from upstream (mchristi@redhat.com ) [441979]
- [net] add cnic support to bnx2 (mchristi@redhat.com ) [441979]
- [powerpc] pass the PDN to check_msix_entries (AMEET M. PARANJAPE ) [502906]
- [fs] proc: avoid info leaks to non-privileged processes (Amerigo Wang ) [499541]
- [net] ixgbe: add GRO suppport (Herbert Xu ) [499347]
- [net] igb: add GRO suppport (Herbert Xu ) [499347]
- [net] cxgb3: add GRO suppport (Herbert Xu ) [499347]
- [net] vlan: add GRO interfaces (Herbert Xu ) [499347]
- [net] tcp6: add GRO support (Herbert Xu ) [499347]
- [net] ipv6: add GRO support (Herbert Xu ) [499347]
- [net] ethtool: add GGRO and SGRO ops (Herbert Xu ) [499347]
- [net] tcp: add GRO support (Herbert Xu ) [499347]
- [net] add skb_gro_receive (Herbert Xu ) [499347]
- [net] ipv4: add GRO infrastructure (Herbert Xu ) [499347]
- [net] add Generic Receive Offload infrastructure (Herbert Xu ) [499347]
- [net] add frag_list support to GSO (Herbert Xu ) [499347]
- [net] add frag_list support to skb_segment (Herbert Xu ) [499347]
- [net] skbuff: add skb_release_head_state (Herbert Xu ) [499347]
- [net] skbuff: merge code copy_skb_header and skb_clone (Herbert Xu ) [499347]
- [netfilter] nf_conntrack: add __nf_copy to copy members (Herbert Xu ) [499347]
- [net] skbuff: add skb_cow_head (Herbert Xu ) [499347]
- [net] netpoll: backport netpoll_rx_on (Herbert Xu ) [499347]
- [net] gro: Optimise Ethernet header comparison (Herbert Xu ) [499347]
- [net] backport csum_replace4/csum_replace2 (Herbert Xu ) [499347]
- [net] backport csum_unfold without sparse annotations (Herbert Xu ) [499347]
- [net] sky2: fix eeprom reads (Neil Horman ) [501050]
- [nfs] v4: client handling of MAY_EXEC in nfs_permission (Peter Staubach ) [500302] {CVE-2009-1630}
- [net] forcedeth: restore power up snippet (Ivan Vecera ) [479740]
- [md] dm: I/O failures when running dm-over-md with xen (Mikulas Patocka ) [223947]
- [selinux] warn on nfs mounts with same SB but diff opts (Eric Paris ) [466701]

* Wed May 27 2009 Don Zickus <dzickus@redhat.com> [2.6.18-151.el5]
- [alsa] hda: improve init for ALC262_HP_BPC model (Jaroslav Kysela ) [473949]
- [ppc] LPAR hang on multipath device with FCS v2 (AMEET M. PARANJAPE ) [498927]
- [fs] nfsd: fix setting the nfsv4 acls (Steve Dickson ) [403021]
- [scsi] fnic: compile on x86 too (mchristi@redhat.com ) [501112]
- [net] avoid extra wakeups in wait_for_packet (Neil Horman ) [497897]
- [x86] xen: fix local denial of service (Chris Lalancette ) [500951]
- [scsi] ibmvfc: wait on adapter init before starting scan (AMEET M. PARANJAPE ) [501560]
- [net] bnx2x: update to 1.48.105 (Stanislaw Gruszka ) [475481]
- [xen] add Credit Scheduler Fairness and hard virt (Justin M. Forbes ) [432700]
- [xen] deadlock between libvirt and xentop (Miroslav Rezanina ) [499013]
- [xen] sched: remove printk introduced with hard virt (Justin M. Forbes ) [501475]

* Wed May 20 2009 Don Zickus <dzickus@redhat.com> [2.6.18-150.el5]
- [kabi] add cmirror symbols to kABI (Jon Masters ) [500745]
- Revert: [sched] accurate task runtime accounting (Linda Wang ) [297731] {CVE-2007-3719}
- [alsa] hda: add missing comma in ad1884_slave_vols (Jeff Burke ) [500626]
- [x86] remove xtime_lock from time_cpufreq_notifier (Prarit Bhargava ) [501178]
- [fs] cifs: fix pointer and checks in cifs_follow_symlink (Jeff Layton ) [496577] {CVE-2009-1633}
- [fs] ext4: corruption fixes (Eric Sandeen ) [501082]
- [lockdep] don't omit lock_set_subclass (Aristeu Rozanski ) [462248]
- [ppc] cell: make ptcal more reliable (AMEET M. PARANJAPE ) [501356]
- [x86] include asm-x86_64 in i686-devel package (Don Zickus ) [491775]
- [misc] compile: add -fwrapv to gcc CFLAGS (Don Zickus ) [491266]
- [trace] mm: eliminate extra mm tracepoint overhead (Larry Woodman ) [501013]
- [dlm] use more NOFS allocation (Abhijith Das ) [460218]
- [dlm] connect to nodes earlier (Abhijith Das ) [460218]
- [wireless] mac80211: freeze when ath5k IF brought down (Michal Schmidt ) [499999]
- [audit] watch: fix removal of AUDIT_DIR rule on rmdir (Alexander Viro ) [501321]
- [trace] sunrpc: adding trace points to status routines v2 (Steve Dickson ) [499008]
- [misc] random: make get_random_int more random (Amerigo Wang ) [499776]
- [md] retry immediate in 2 seconds (Jesse Larrew ) [489582]
- [scsi] retry for NOT_READY condition (Jesse Larrew ) [489582]
- [md] handle multiple paths in pg_init (Jesse Larrew ) [489582]
- [scsi] fix compilation error (Jesse Larrew ) [489582]
- [scsi] add LSI storage IDs (Jesse Larrew ) [489582]
- [scsi] handle quiescence in progress (Jesse Larrew ) [489582]
- [scsi] retry IO on unit attention (Jesse Larrew ) [489582]
- [scsi] handle unit attention in mode select (Jesse Larrew ) [489582]
- [scsi] make the path state active by default (Jesse Larrew ) [471426]
- [scsi] Retry mode select in rdac device handler (Jesse Larrew ) [489582]

* Mon May 18 2009 Don Zickus <dzickus@redhat.com> [2.6.18-149.el5]
- [acpi] updated dock driver for RHEL-5.4 (Matthew Garrett ) [485181]
- [infiniband] ib_core: use weak ordering for user memory (AMEET M. PARANJAPE ) [501004]
- [mm] fork-o_direct-race v3 (aarcange@redhat.com ) [471613]
- [nfs] make nfsv4recoverydir proc file readable (Evan McNabb ) [499840]
- [pci] remove pci-stub driver from -xen kernels (Don Dutile ) [500568]
- [pci] IOMMU phys_addr cleanup (Don Dutile ) [500901]
- [pci] missed fix to pci_find_upstream_pcie_bridge (Don Dutile ) [500901]
- [misc] IOMMU MSI header cleanup (Don Dutile ) [500901]
- [scsi] megaraid: update megasas to 4.08-RH1 (Tomas Henzl ) [475574]
- [fs] nfs: fix an f_mode/f_flags confusion in write.c (Jeff Layton ) [490181]
- [fs] cifs: renaming don't try to unlink negative dentry (Jeff Layton ) [500839]
- [fs] cifs: fix error handling in parse_DFS_referrals (Jeff Layton ) [496577] {CVE-2009-1633}
- [scsi] aacraid: update to 1.1.5-2461 (Rob Evers ) [475559]
- [md] dm raid45: don't clear the suspend flag on recovery (Heinz Mauelshagen ) [499406]
- [net] cxgb3: update driver for RHEL-5.4 (mchristi@redhat.com ) [439518]
- [scsi] add cxgb3i iscsi driver (mchristi@redhat.com ) [439518]
- [scsi] port upstream offload code to RHEL-5.4 (mchristi@redhat.com ) [439518]
- [scsi] force retry of IO when port/session is changing (mchristi@redhat.com ) [498281]
- [net] igbvf: new driver, support 82576 virtual functions (Andy Gospodarek ) [480524]
- [net] ehea: fix circular locking problem (AMEET M. PARANJAPE ) [493359]
- [s390] appldata: vtimer bug with cpu hotplug (Hans-Joachim Picht ) [497207]

* Thu May 14 2009 Don Zickus <dzickus@redhat.com> [2.6.18-148.el5]
- Revert: [mm] fork vs fast gup race fix (Andrea Arcangeli ) [471613]

* Wed May 13 2009 Don Zickus <dzickus@redhat.com> [2.6.18-147.el5]
- Revert: [scsi] marvell sas: initial patch submission (Rob Evers ) [485126]
- Revert: [scsi] marvell sas: correct bit-map implementation (Rob Evers ) [485126]
- Revert: [scsi] marvell sas: comment cleanup (Rob Evers ) [485126]
- [misc] FIPS: create checksum for verification at bootup (Don Zickus ) [444632]
- [md] dm: raid45 target oops on mapping table reload (Heinz Mauelshagen ) [500387]
- [md] dm: raid45 target doesn't create parity as expected (Heinz Mauelshagen ) [499406]
- [net] igb: correctly free multiqueue netdevs (Andy Gospodarek ) [500446]
- [misc] lockdep: fix large lock subgraph traversal (Aristeu Rozanski ) [462248]
- [crypto] make tcrypt stay loaded on success (Jarod Wilson ) [499646]
- [crypto] block use of non-fips algs in fips mode (Jarod Wilson ) [499646]
- [crypto] mark algs allowed in fips mode (Jarod Wilson ) [499646]
- [x86_64] 32-bit ptrace emulation mishandles 6th arg (Jiri Olsa ) [495125]
- [fs] cifs: buffer overruns when converting strings (Jeff Layton ) [496577]
- [scsi] lpfc: update from version 8.2.0.41 to 8.2.0.43 (Rob Evers ) [498524]
- [cpufreq] xen: powernow identifies wrong number of procs (Miroslav Rezanina ) [456437]
- [scsi] MPT fusion: remove annoying debug message v2 (Tomas Henzl ) [475455]
- [scsi] MPT fusion: make driver legacy I/O port free v2 (Tomas Henzl ) [475451]
- [scsi] MPT fusion: update version 3.04.07rh v2 (Tomas Henzl ) [475455]
- [ia64] fix regression in nanosleep syscall (Prarit Bhargava ) [499289]
- [md] s390: I/O stall when performing random CHPID off/on (Mikulas Patocka ) [500729]
- [crypto] add hmac and hmac(sha512) test vectors (Jarod Wilson ) [499463]
- [sched] accurate task runtime accounting (Peter Zijlstra ) [297731] {CVE-2007-3719}
- [sched] rq clock (Peter Zijlstra ) [297731] {CVE-2007-3719}
- [x86] scale cyc_2_nsec according to CPU frequency (Peter Zijlstra ) [297731] {CVE-2007-3719}
- [i386] untangle xtime_lock vs update_process_times (Peter Zijlstra ) [297731] {CVE-2007-3719}
- [x86_64] clean up time.c (Peter Zijlstra ) [297731] {CVE-2007-3719}
- [net] tun: add packet accounting (Herbert Xu ) [495863]
- [kabi] add pcie_set_readrq (Jon Masters ) [479200]
- [kabi] add Kernel Virtual Machine kABI symbols (Jon Masters ) [466961]
- [crypto] add ctr test vectors (Jarod Wilson ) [497888]
- [crypto] print self-test success notices in fips mode (Jarod Wilson ) [497885]
- [mm] fork vs fast gup race fix (Andrea Arcangeli ) [471613]
- [mm] support for lockless get_user_pages (aarcange@redhat.com ) [474913]
- Revert: [mm] fork vs gup race fix (aarcange@redhat.com ) [471613]
- [net] r8169: reset IntrStatus after chip reset (Ivan Vecera ) [500740]
- Revert: [net] forcedeth: power down phy when IF is down (Ivan Vecera ) [479740]
- [misc] add AMD IOMMU support to KVM (Bhavna Sarathy ) [481026]
- [misc] VT-d: backport of Intel VT-d support to RHEL5 (Don Dutile ) [480411]
- [misc] VT-d: add clflush_cache_range function (Don Dutile ) [480411]
- [misc] VT-d: add DMAR-related timeout definition (Don Dutile ) [480411]
- [misc] VT-d: add DMAR ACPI table support (Don Dutile ) [480411]
- [misc] VT-d: add pci_find_upstream_pcie_bridge (Don Dutile ) [480411]
- [misc] VT-d: move common MSI defines to msi.h (Don Dutile ) [480411]
- [trace] blk tracepoints (Arnaldo Carvalho de Melo ) [493454]
- [pci] enable CONFIG_PCI_IOV (ddugger@redhat.com ) [493152]
- [pci] save and restore PCIe 2.0 registers (ddugger@redhat.com ) [493152]
- [pci] restore PCI-E capability registers after PM event (ddugger@redhat.com ) [493152]
- [pci] add SR-IOV API for Physical Function driver (ddugger@redhat.com ) [493152]
- [pci] centralize device setup code (ddugger@redhat.com ) [493152]
- [pci] reserve bus range for SR-IOV device (ddugger@redhat.com ) [493152]
- [pci] restore saved SR-IOV state (ddugger@redhat.com ) [493152]
- [pci] initialize and release SR-IOV capability (ddugger@redhat.com ) [493152]
- [pci] add a new function to map BAR offsets (ddugger@redhat.com ) [493152]
- [pci] allow pci_alloc_child_bus to handle a NULL bridge (ddugger@redhat.com ) [493152]
- [pci] enhance pci_ari_enabled (ddugger@redhat.com ) [493152]
- [pci] fix ARI code to be compatible with mixed systems (ddugger@redhat.com ) [493152]
- [pci] support PCIe ARI capability (ddugger@redhat.com ) [493152]
- [pci] export __pci_read_base (ddugger@redhat.com ) [493152]
- [pci] fix 64-vbit prefetchable memory resource BARs (ddugger@redhat.com ) [493152]
- [pci] handle 64-bit resources better on 32-bit machines (ddugger@redhat.com ) [493152]
- [pci] rewrite PCI BAR reading code (ddugger@redhat.com ) [493152]
- [xen] add Credit Scheduler Fairness and hard virt (Justin M. Forbes ) [432700]
- [xen] x86_64: add 1GB page table support (Bhavna Sarathy ) [251982]

* Mon May 11 2009 Don Zickus <dzickus@redhat.com> [2.6.18-146.el5]
- [fs] vfs freeze: use vma->v_file to get to superblock (Eric Sandeen ) [476148]
- [net] tg3: allow 5785 to work when running at 10Mbps (Andy Gospodarek ) [469772]
- [net] af_iucv: race when queuing incoming iucv messages (Hans-Joachim Picht ) [499626]
- [trace] sunrpc: adding trace points to status routines (Steve Dickson ) [499008]
- [gfs2] fix glock ref count issue (Steven Whitehouse ) [485098]
- [kabi] add acpi_bus_register_driver (Jon Masters ) [462911]
- [kabi] add nobh_truncate_page and kernel_read (Jon Masters ) [497276]
- [usb] support Huawei's mode switch in kernel (Pete Zaitcev ) [485182]
- [scsi] ibmvscsi: LPAR hang on a multipath device (AMEET M. PARANJAPE ) [498927]
- [wireless] mac80211: scanning related fixes (John W. Linville ) [498719]
- [fs] ecryptfs: remove ecryptfs_unlink_sigs warnings (Eric Sandeen ) [499171]
- [fs] ext4: re-fix warning on x86 build (Eric Sandeen ) [499202]
- [ppc64] adjust oprofile_cpu_type detail (AMEET M. PARANJAPE ) [496709]
- [nfs] SELinux can copy off the top of the stack (Eric Paris ) [493144]
- [xen] x86: explicitly zero CR[1] in getvcpucontext (Miroslav Rezanina ) [494876]
- [xen] x86: fix overflow in the hpet code (Rik van Riel ) [449346]
- [xen] x86: fixes to the 'no missed-tick accounting' code (Rik van Riel ) [449346]
- [xen] introduce 'no missed-tick accounting' (Rik van Riel ) [449346]
- [xen] x86: misc fixes to the timer code (Rik van Riel ) [449346]
- [xen] x86: initialize vlapic->timer_last_update (Rik van Riel ) [449346]

* Thu May 07 2009 Don Zickus <dzickus@redhat.com> [2.6.18-145.el5]
- [ia64] xen: switch from flipping to copying interface (Chris Lalancette ) [479754]
- [scsi] fnic: init retry counter (Mike Christie ) [484438]
- [misc] add some long-missing capabilities to CAP_FS_MASK (Eric Paris ) [499076 497272] {CVE-2009-1072}
- [crypto] add ansi_cprng test vectors (Jarod Wilson ) [497891]
- [crypto] add rng self-test infra (Jarod Wilson ) [497891]
- [md] bitmap merge feature (Doug Ledford ) [481226]
- [md] fix lockup on read error (Doug Ledford ) [465781]
- [md] dm-raid45: corrupt data and premature end of synch (Heinz Mauelshagen ) [480733 479383]
- [fs] generic freeze ioctl interface (Eric Sandeen ) [476148]
- [scsi] add mpt2sas driver (Tomas Henzl ) [475665]
- [misc] kprobes: fix deadlock issue (John Villalovos ) [210555]
- [block] disable iostat collection in gendisk (Jerome Marchand ) [484158]
- [block] fix request flags (Jerome Marchand ) [484158]
- [misc] fix blktrace api breakage (Hans-Joachim Picht ) [475334]
- [fs] fuse: update for RHEL-5.4 (Josef Bacik ) [457975]

* Tue May 05 2009 Don Zickus <dzickus@redhat.com> [2.6.18-144.el5]
- Revert: [scsi] MPT Fusion: update to version 3.04.07rh (Tomas Henzl ) [475455]
- Revert: [scsi] make fusion MPT driver legacy I/O port free (Tomas Henzl ) [475451]
- Revert: [scsi] MPT fusion: remove annoying debug message (Tomas Henzl ) [475455]
- [openib] ehca: fix performance during creation of QPs (AMEET M. PARANJAPE ) [498527]
- [scsi] qla4xxx: fix driver fault recovery (Marcus Barrow ) [497478]
- [misc] make bus_find_device more robust, match upstream (Don Dutile ) [492488]
- [md] dm snapshot: refactor __find_pending_exception (Mikulas Patocka ) [496100]
- [md] race conditions in snapshots (Mikulas Patocka ) [496100]
- [md] dm-raid1: switch read_record from kmalloc to slab (Mikulas Patocka ) [496101]
- [md] dm-raid1/mpath: partially completed request crash (Mikulas Patocka ) [496101]
- [md] snapshot: store damage (Mikulas Patocka ) [496102]
- [scsi] cciss: change in discovering memory bar (Tomas Henzl ) [474392]
- [scsi] cciss: version change for RHEL-5.4 (Tomas Henzl ) [474392]
- [scsi] cciss: thread to detect config changes on MSA2012 (Tomas Henzl ) [474392]
- [scsi] cciss: changes in config functions (Tomas Henzl ) [474392]
- [openib] update all the backports for the code refresh (Doug Ledford ) [476301]
- [openib] add support for XRC queues (Doug Ledford ) [476301]
- [openib] RDS: add the RDS protocol (Doug Ledford ) [477065]
- [openib] IPoIB: update to OFED 1.4.1-rc3 (Doug Ledford ) [434779 466086]
- [openib] SRP: update to OFED 1.4.1-rc3 (Doug Ledford ) [476301]
- [openib] SDP: update to OFED 1.4.1-rc3 (Doug Ledford ) [476301]
- [openib] qlgc_vnic: update to OFED 1.4.1-rc3 (Doug Ledford ) [476301]
- [openib] cxgb3: update driver to OFED 1.4.1-rc3 (Doug Ledford ) [476301]
- [openib] iw_nes: update NES iWARP to OFED 1.4.1-rc3 (Doug Ledford ) [476301]
- [openib] mthca: update driver to OFED 1.4.1-rc3 (Doug Ledford ) [476301]
- [openib] ipath: update driver to OFED 1.4.1-rc3 (Doug Ledford ) [230035 480696]
- [openib] ehca: update driver for RHEL-5.4 (Doug Ledford ) [466086]
- [openib] core: disable lock dep annotation (Don Zickus ) [476301]
- [openib] core: update core code to OFED 1.4.1-rc3 (Doug Ledford ) [476301]
- [openib] rmda: update rdma headers to OFED 1.4.1-rc3 (Doug Ledford ) [476301]
- [openib] mlx4: Update mlx4_ib and mlx4_core, add mlx4_en (Doug Ledford ) [456525 477065]
- [openib] enable mlx4_en and rds, disable iw_c2 (Doug Ledford ) [476301]
- [mm] add tracepoints (Larry Woodman ) [493444]

* Fri May 01 2009 Don Zickus <dzickus@redhat.com> [2.6.18-143.el5]
- [net] bonding: ignore updelay param when no active slave (Jiri Pirko ) [495318]
- [net] ipv6: fix incoming packet length check (Jiri Pirko ) [492972]
- [misc] drivers fix dma_get_required_mask (Tomas Henzl ) [475455]
- [gfs2] NFSv2 support (Steven Whitehouse ) [497954]
- [ppc64] set error_state to pci_channel_io_normal (AMEET M. PARANJAPE ) [496872]
- [mm] allow tuning of MAX_WRITEBACK_PAGES (Larry Woodman ) [479079]
- [trace] add 'success' to sched_wakeup/sched_wakeup_new (Jason Baron ) [497414]
- [scsi] update iscsi layer and drivers for RHEL-5.4 (mchristi@redhat.com ) [436791 484455]
- [crypto] fips: panic box when module validation fails (Neil Horman ) [497228]
- [scsi] st: option to use SILI in variable block reads (Tom Coughlan ) [457970]
- [net] bonding: support for bonding of IPoIB interfaces (Andy Gospodarek ) [430758]
- [net] bonding: update to upstream version 3.4.0 (Andy Gospodarek ) [462632]
- [scsi] add md3000 and md3000i entries to rdac_dev_list (John Feeney ) [487293]
- [trace] tracepoints for page cache (KII Keiichi ) [475719]
- [trace] tracepoints for network socket (KII Keiichi ) [475719]
- [scsi] stex: support promise 6Gb sas raid controller (David Milburn ) [492022]
- [scsi] add ALUA scsi device handler (mchristi@redhat.com ) [482737]
- [scsi] update fnic fcoe driver for RHEL-5.4 (mchristi@redhat.com ) [484438]
- [scsi] update libfc/fcoe for RHEL-5.4 (mchristi@redhat.com ) [484438]
- [video] efifb: driver update (Brian Maly ) [488820]
- [fs] fix softlockup in posix_locks_deadlock (Josef Bacik ) [476659]
- [fs] cifs: unicode alignment and buffer sizing problems (Jeff Layton ) [494280] {CVE-2009-1439}
- [mm] vmscan: bail out of direct reclaim after max pages (Rik van Riel ) [495442]
- [crypto] add self-tests for rfc4309 (Jarod Wilson ) [472386]
- [crypto] handle ccm dec test vectors expected to fail (Jarod Wilson ) [472386]
- [crypto] fix rfc4309 deadlocks (Jarod Wilson ) [472386]
- [scsi] marvell sas: comment cleanup (Rob Evers ) [485126]
- [scsi] marvell sas: correct bit-map implementation (Rob Evers ) [485126]
- [scsi] marvell sas: initial patch submission (Rob Evers ) [485126]
- [acpi] CPU P-state limits ignored by OS (Stanislaw Gruszka ) [494288]
- [net] provide a generic SIOETHTOOL ETHTOOL_GPERMADDR (Flavio Leitner ) [462352]
- [scsi] lpfc: update to version 8.2.0.41 (Rob Evers ) [476738]
- [scsi] lpfc: update to version 8.2.0.40 (Rob Evers ) [476738]
- [scsi] lpfc: update to version 8.2.0.39 (Rob Evers ) [476738]
- [scsi] lpfc: update to version 8.2.0.38 (Rob Evers ) [476738]

* Tue Apr 28 2009 Don Zickus <dzickus@redhat.com> [2.6.18-142.el5]
- [net] ipv4: remove uneeded bh_lock/unlock from udp_rcv (Neil Horman ) [484590]
- [net] ixgbe: update to upstream version 2.0.8-k2 (Andy Gospodarek ) [472547]
- [net] igb: update to upstream version 1.3.16-k2 (Andy Gospodarek ) [484102 474881]
- [mm] vmalloc: don't pass __GFP_ZERO to slab (Jiri Olsa ) [491685]
- [agp] zero pages before sending to userspace (Jiri Olsa ) [497026] {CVE-2009-1192}
- [net] e1000: enable TSO6 via ethtool with correct hw (Andy Gospodarek ) [449175]
- [net] tg3: update to version 3.96 (Andy Gospodarek ) [481715 469772]
- [x86] apic: rollover in calibrate_APIC_clock (Brian Maly ) [456938]
- [alsa] handle subdevice_mask in snd_pci_quirk_lookup (Jaroslav Kysela ) [473949 483594]
- [ia64] altix: performance degradation in PCI mode (George Beshers ) [497136]
- [misc] I/O AT: config file changes (John Feeney ) [436048]
- [misc] I/O AT: new ioat*.c (John Feeney ) [436048]
- [misc] I/O AT: new dmaengine_v3.c (John Feeney ) [436048]
- [misc] I/O AT: new include files (John Feeney ) [436048]
- [misc] I/O AT: add drivers/dca (John Feeney ) [436048]
- [misc] I/O AT: update network changes (John Feeney ) [436048]
- [misc] I/O AT: update existing files (John Feeney ) [436048]
- [misc] I/O AT: update include files (John Feeney ) [436048]
- [mm] tweak vm diry_ratio to prevent stalls on some DBs (Larry Woodman ) [295291]
- [nfs] setacl not working over NFS (Peter Staubach ) [496903]
- [fs] ext4: update config options (Eric Sandeen ) [485315]
- [fs] ext4: post-2.6.29 fixes (Eric Sandeen ) [485315]
- [fs] backport patch for 2.6.29 ext4 (Eric Sandeen ) [485315]
- [fs] rebase ext4 and jbd2 to 2.6.29 codebase (Eric Sandeen ) [485315 487933 487940 487944 487947] {CVE-2009-0745  CVE-2009-0746  CVE-2009-0747  CVE-2009-0748}
- [fs] update write_cache_pages (Eric Sandeen ) [485315]
- [fs] export set_task_ioprio (Eric Sandeen ) [485315]
- [scsi] qla2xxx : updates and fixes from upstream, part 4 (Marcus Barrow ) [496126]
- [scsi] MPT fusion: remove annoying debug message (Tomas Henzl ) [475455]
- [scsi] make fusion MPT driver legacy I/O port free (Tomas Henzl ) [475451]
- [scsi] MPT Fusion: update to version 3.04.07rh (Tomas Henzl ) [475455]
- [x86] add MAP_STACK mmap flag (Larry Woodman ) [459321]
- [scsi] sym53c8xx_2: fix up hotplug support (mchristi@redhat.com ) [461006]
- [scsi] qla2xxx : updates and fixes from upstream, part 3 (Marcus Barrow ) [495094]
- [scsi] qla2xxx : updates and fixes from upstream, part 2 (Marcus Barrow ) [495092]
- [scsi] qla2xxx : updates and fixes from upstream, part 1 (Marcus Barrow ) [480204]
- [nfs] memory leak when reading files wth option 'noac' (Peter Staubach ) [493045]
- [x86] powernow-k8: export module parameters via sysfs (Prarit Bhargava ) [492010]
- [misc] IO accounting: tgid accounting (Jerome Marchand ) [461636]
- [misc] IO accounting: read accounting nfs fix (Jerome Marchand ) [461636]
- [misc] IO accounting: read accounting (Jerome Marchand ) [461636]
- [misc] IO accounting: write cancel accounting (Jerome Marchand ) [461636]
- [misc] IO accounting: report in procfs (Jerome Marchand ) [461636]
- [misc] IO accounting: account for direct-io (Jerome Marchand ) [461636]
- [misc] IO accounting: set CONFIG_TASK_IO_ACCOUNTING (Jerome Marchand ) [461636]
- [misc] IO accounting: write accounting (Jerome Marchand ) [461636]
- [misc] IO accounting: core statistics (Jerome Marchand ) [461636]
- [misc] IO accounting: read accounting cifs fix (Jerome Marchand ) [461636]
- [misc] auxiliary signal structure: signal_struct_aux (Jerome Marchand ) [461636]
- [misc] auxiliary signal structure: preparation (Jerome Marchand ) [461636]
- [xen] x86: fix MSI eoi handling for HVM passthru (Gerd Hoffmann ) [477261]

* Fri Apr 24 2009 Don Zickus <dzickus@redhat.com> [2.6.18-141.el5]
- [x86_64] more cpu_khz to tsc_khz conversions (Prarit Bhargava ) [483300]
- [gfs2] unaligned access in gfs2_bitfit (Abhijith Das ) [485226]
- [gfs2] remove scand & glockd kernel processes (Benjamin Marzinski ) [273001]
- [x86] fix tick divider with clocksource=pit (Chris Lalancette ) [427588]
- [fs] autofs4: fix incorect return in autofs4_mount_busy (Ian Kent ) [496766]
- [x86] fix cpuid.4 instrumentation (Brian Maly ) [454981]
- [md] dm-mpath: propagate ioctl error codes (Benjamin Marzinski ) [461469]
- [fs] aio: race in aio_complete leads to process hang (Jeff Moyer ) [475814]
- [s390] enable raw devices (Jeff Moyer ) [452534]
- [net] bnx2: update to latest upstream - 1.9.3 (Ivan Vecera ) [475567 476897 489519]
- [net] forcedeth: update to upstream version 0.62 (Ivan Vecera ) [479740]
- [net] r8169: don't update stats counters when IF is down (Ivan Vecera ) [490162]
- [net] r8169: fix RxMissed register access (Ivan Vecera ) [474334]
- [x86] prevent boosting kprobes on exception address (Masami Hiramatsu ) [493088]
- [gfs2] add fiemap support (Steven Whitehouse ) [476626]
- [net] e1000e: fix false link detection (Michal Schmidt ) [492270]
- [ppc] pseries: set error_state to pci_channel_io_normal (AMEET M. PARANJAPE ) [496872]
- [nfs] large writes rejected when sec=krb5i/p specified (Peter Staubach ) [486756]
- [wireless] iwlwifi: problems switching b/w WPA and WEP (John W. Linville ) [474699]
- [net] ipv6: assume loopback address in link-local scope (Jiri Pirko ) [487233]
- [fs] keep eventpoll from locking up the box (Josef Bacik ) [487585]
- [ppc64] adjust oprofile_cpu_type (AMEET M. PARANJAPE ) [496709]
- [fs] jbd: properly dispose of unmapped data buffers (Josef Bacik ) [479296]
- [fs] ext3: dir_index: error out on corrupt dx dirs (Josef Bacik ) [454942]
- [fs] ext3: don't resize if no reserved gdt blocks left (Josef Bacik ) [443541]
- [agp] add pci ids for new video cards (John Villalovos ) [474513]
- [ata] sata_mv: fix chip type for RocketRaid 1740/1742 (David Milburn ) [496338]
- [misc] exit_notify: kill the wrong capable check (Oleg Nesterov ) [494271] {CVE-2009-1337}
- [ipmi] fix platform crash on suspend/resume (peterm@redhat.com ) [475536]
- [ipmi] fix some signedness issues (peterm@redhat.com ) [475536]
- [ipmi] hold ATTN until upper layer is ready (peterm@redhat.com ) [475536]
- [ipmi] allow shared interrupts (peterm@redhat.com ) [475536]
- [scsi] add missing SDEV_DEL state if slave_alloc fails (Tomas Henzl ) [430170]
- [net] eHEA: mutex_unlock missing in eHEA error path (AMEET M. PARANJAPE ) [482796]
- [misc] xen: change PVFB not to select abs. pointer (Markus Armbruster ) [492866]
- [pci] pci-stub module to reserve pci device (Mark McLoughlin ) [491842]
- [pci] add remove_id sysfs entry (Mark McLoughlin ) [491842]
- [pci] use proper call to driver_create_file (Mark McLoughlin ) [491842]
- [pci] fix __pci_register_driver error handling (Mark McLoughlin ) [491842]
- [misc] add /sys/bus/*/driver_probe (Mark McLoughlin ) [491842]
- [misc] backport new ramdisk driver (Don Howard ) [480663]
- [x86] general pci_scan_bus fix for baremetal and xen (Prarit Bhargava ) [494114]
- [misc] add HP xw460c to bf sort pci list (Prarit Bhargava ) [490068]
- [mm] enable dumping of hugepages into core dumps (Dave Anderson ) [470411]
- [misc] hrtimer: check relative timeouts for overflow (AMEET M. PARANJAPE ) [492230]
- [acpi] add T-state notification support (Luming Yu ) [487567]
- [x86_64] copy_user_c can zero more data than needed (Vitaly Mayatskikh ) [490938]
- [misc] hpilo: backport bugfixes and updates for RHEL-5.4 (tcamuso@redhat.com ) [488964]
- [pci] do not clear PREFETCH register (Prarit Bhargava ) [486185]
- [misc] waitpid reports stopped process more than once (Vitaly Mayatskikh ) [481199]
- [scsi] ipr: enhance driver to support MSI-X interrupt (AMEET M. PARANJAPE ) [475717]
- [specfile] add ability to build only debug kernel (Jeff Layton ) [469707]
- [xen] clear X86_FEATURE_APIC in cpuid when apic disabled (ddugger@redhat.com ) [496873]
- [xen] enable systems without APIC (ddugger@redhat.com ) [496873]
- [xen] vt-d: workaround for Mobile Series 4 Chipset (ddugger@redhat.com ) [496873]
- [xen] pci: fix definition of PCI_PM_CTRL_NO_SOFT_RESET (ddugger@redhat.com ) [496873]
- [xen] utilise the GUEST_PAT and HOST_PAT vmcs area (ddugger@redhat.com ) [496873]
- [xen] VT-d: enhance MTRR/PAT virtualization (ddugger@redhat.com ) [496873]
- [xen] fix interrupt remapping on AMD systems (Bhavna Sarathy ) [477261]
- [xen] enable AMD IOMMU Xen driver (Bhavna Sarathy ) [477261]
- [xen] add AMD IOMMU Xen driver (Bhavna Sarathy ) [477261]
- [xen] live migration failure due to fragmented memory (Jiri Denemark ) [469130]

* Sun Apr 19 2009 Don Zickus <dzickus@redhat.com> [2.6.18-140.el5]
- [fs] xfs: add fiemap support (Josef Bacik ) [296951]
- [net] add DSCP netfilter target (Thomas Graf ) [481652]
- [gfs2] blocked after recovery (Abhijith Das ) [483541]
- [net] remove misleading skb_truesize_check (Thomas Graf ) [474883]
- [mm] 100% time spent under NUMA when zone_reclaim_mode=1 (Larry Woodman ) [457264]
- [mm] msync does not sync data for a long time (Larry Woodman ) [479079]
- [md] dm: fix OOps in mempool_free when device removed (Milan Broz ) [495230]
- [net] bonding: clean up resources upon removing a bond (Masahiro Matsuya ) [463244]
- [fs] nfs: convert to new aops (Jeff Layton ) [476224]
- [fs] cifs: update CIFS for RHEL5.4 (Jeff Layton ) [465143]
- [misc] types: add fmode_t typedef (Jeff Layton ) [465143]
- [misc] keys: key facility changes for AF_RXRPC (Jeff Layton ) [465143]
- [misc] xen: bump max_phys_cpus to 256 (Chris Lalancette ) [477206]
- [misc] fork: CLONE_PARENT && parent_exec_id interaction (Don Howard ) [479964]
- [wireless] iwlagn: make swcrypto/swcrypto50=1 default (John W. Linville ) [474699]
- [wireless] mac80211: avoid null deref (John W. Linville ) [482990]
- [net] fix out of bound access to hook_entries (Thomas Graf ) [484036]
- [net] sctp: allow sctp_getladdrs to work for IPv6 (Neil Horman ) [492633]
- [x86] xen: fix interaction between dom0 and NTP (Rik van Riel ) [494879]
- [ata] sata_mv: fix 8-port timeouts on 508x/6081 chips (David Milburn ) [493451]
- [net] fixed tcp_ack to properly clear ->icsk_probes_out (Jiri Olsa ) [494427]
- [x86] xen: crash when specifying mem= (Chris Lalancette ) [240429]
- [scsi] qla2xxx: reduce DID_BUS_BUSY failover errors (Marcus Barrow ) [244967]
- [ata] libata: ahci enclosure management bios workaround (David Milburn ) [488471]
- [scsi] aic7xxx: increase max IO size (mchristi@redhat.com ) [493448]
- [nfs] v4: client crash on file lookup with long names (Sachin S. Prabhu ) [493942]
- [mm] fix prepare_hugepage_range to check offset (Larry Woodman ) [488260]
- [misc] make sure fiemap.h is installed in headers pkg (Josef Bacik ) [296951]
- [fs] generic block based fiemap (Josef Bacik ) [296951]
- [fs] add fiemap interface (Josef Bacik ) [296951]
- [trace] use unregister return value (Jason Baron ) [465543]
- [trace] change rcu_read_sched -> rcu_read (Jason Baron ) [465543]
- [trace] introduce noupdate apis (Jason Baron ) [465543]
- [trace] simplify rcu usage (Jason Baron ) [465543]
- [trace] fix null pointer dereference (Jason Baron ) [465543]
- [trace] tracepoints fix reentrancy (Jason Baron ) [465543]
- [trace] make tracepoints use rcu sched (Jason Baron ) [465543]
- [trace] use TABLE_SIZE macro (Jason Baron ) [465543]
- [trace] remove kernel-trace.c (Jason Baron ) [465543]
- [trace] remove prototype from tracepoint name (Jason Baron ) [465543]
- [x86] use CPU feature bits to skip tsc_unstable checks (Chris Lalancette ) [463573]
- [x86] vmware: disable softlock processing on tsc systems (Chris Lalancette ) [463573]
- [x86] vmware lazy timer emulation (Chris Lalancette ) [463573]
- [x86] xen: improve KVM timekeeping (Chris Lalancette ) [463573]
- [x86_64] xen: implement a minimal TSC based clocksource (Chris Lalancette ) [463573]
- [x86] use cpu_khz for loops_per_jiffy calculation (Chris Lalancette ) [463573]
- [x86] vmware: look for DMI string in product serial key (Chris Lalancette ) [463573]
- [x86] VMware: Fix vmware_get_tsc code (Chris Lalancette ) [463573]
- [x86] xen: add X86_FEATURE_HYPERVISOR feature bit (Chris Lalancette ) [463573]
- [x86] xen: changes timebase calibration on Vmware (Chris Lalancette ) [463573]
- [x86] add a synthetic TSC_RELIABLE feature bit (Chris Lalancette ) [463573]
- [x86] hypervisor: detection and get tsc_freq (Chris Lalancette ) [463573]
- [x86] fdiv bug detection fix (Chris Lalancette ) [463573]
- [misc] printk: add KERN_CONT (Chris Lalancette ) [463573]
- [s390] add additional card IDs to CEX2C and CEX2A (Hans-Joachim Picht ) [488496]
- [gfs2] merge upstream uevent patches into RHEL 5.4 (Steven Whitehouse ) [476707]
- [xen] x86: GDT: replace single page with one page/CPU (Chris Lalancette ) [477206]
- [xen] x86: VPID: free resources (ddugger@redhat.com ) [464821]
- [xen] x86: VPID: implement feature (ddugger@redhat.com ) [464821]
- [xen] fix 32-on-64 PV oops in xen_set_pud (Chris Lalancette ) [467698]

* Tue Apr 14 2009 Don Zickus <dzickus@redhat.com> [2.6.18-139.el5]
- [pci] xen dom0: hook PCI probe and remove callbacks (ddugger@redhat.com ) [484227]
- [misc] xen dom0: add hypercall for add/remove PCI device (ddugger@redhat.com ) [484227]
- [pci] xen: dom0/domU MSI support using PHSYDEV_map_irq (ddugger@redhat.com ) [484227]
- [mm] mmu_notifier: kabi workaround support (john cooper ) [485718]
- [mm] mmu_notifier: set CONFIG_MMU_NOTIFIER to y (john cooper ) [485718]
- [mm] mmu-notifier: optimized ability to admin host pages (john cooper ) [485718]
- [mm] mmu-notifiers: add mm_take_all_locks operation (john cooper ) [485718]
- [misc] introduce list_del_init_rcu (john cooper ) [485718]
- [ppc] spufs: fix incorrect buffer offset in regs write (AMEET M. PARANJAPE ) [493426]
- [ppc] spufs: check offset before calculating write size (AMEET M. PARANJAPE ) [493426]
- [net] add dropmonitor protocol (Neil Horman ) [470539]
- [ppc] reject discontiguous MSI-X requests (AMEET M. PARANJAPE ) [492580]
- [ppc] implement a quota system for MSIs (AMEET M. PARANJAPE ) [492580]
- [ppc] return req#msi(-x) if request is larger (AMEET M. PARANJAPE ) [492580]
- [ppc] msi: return the number of MSIs we could allocate (AMEET M. PARANJAPE ) [492580]
- [ppc] check for MSI-X also in rtas_msi_pci_irq_fixup() (AMEET M. PARANJAPE ) [492580]
- [ppc] add support for ibm,req#msi-x (AMEET M. PARANJAPE ) [492580]
- [ppc] fix MSI-X interrupt querying (AMEET M. PARANJAPE ) [492580]
- [ppc] msi: return the number of MSI-X available (AMEET M. PARANJAPE ) [492580]
- [trace] add include/trace dir to -devel (Jason Baron ) [489096]
- [mm] xen: 'ptwr_emulate' messages when booting PV guest (Chris Lalancette ) [490567]
- [fs] lockd: reference count leaks in async locking case (Jeff Layton ) [471254]
- [s390] kernel: cpcmd with vmalloc addresses (Hans-Joachim Picht ) [487697]
- [s390] af_iucv: error handling in iucv_callback_txdone (Hans-Joachim Picht ) [487697]
- [s390] af_iucv: broken send_skb_q result in endless loop (Hans-Joachim Picht ) [487697]
- [s390] af_iucv: free iucv path/socket in path_pending cb (Hans-Joachim Picht ) [487697]
- [s390] af_iucv: avoid left over IUCV connections (Hans-Joachim Picht ) [487697]
- [s390] af_iucv: new error return codes for connect (Hans-Joachim Picht ) [487697]
- [s390] af_iucv: hang if recvmsg is used with MSG_PEEK (Hans-Joachim Picht ) [487703]
- [net] ixgbe: stop double counting frames and bytes (Andy Gospodarek ) [487213]
- [net] netfilter: x_tables: add connlimit match (Jiri Pirko ) [483588]
- [nfs] only set file_lock.fl_lmops if stateowner is found (Jeff Layton ) [479323]
- [dlm] init file_lock before copying conflicting lock (Jeff Layton ) [479323]
- [nfs] nfsd: ensure nfsv4 calls the fs on LOCKT (Jeff Layton ) [479323]
- [net] allow for on demand emergency route cache flushing (Neil Horman ) [461655]
- [xen] x86: update the earlier APERF/MPERF patch (Chris Lalancette ) [493557]
- [xen] fix evtchn exhaustion with 32-bit HVM guest (Chris Lalancette ) [489274]
- [xen] ia64: fix HVM guest kexec (Chris Lalancette ) [418591]
- [xen] ia64: fix whitespace error in vmx.h (Chris Lalancette ) [477098]
- [xen] add hypercall for adding and removing PCI devices (ddugger@redhat.com ) [484227]
- [xen] HVM MSI passthrough support (ddugger@redhat.com ) [484227]
- [xen] VT-d2: enable interrupt remapping for MSI/MSI-x (ddugger@redhat.com ) [484227]
- [xen] MSI support interface (ddugger@redhat.com ) [484227]
- [xen] MSI supprt internal functions (ddugger@redhat.com ) [484227]
- [xen] convert pirq to per-domain (ddugger@redhat.com ) [484227]
- [xen] rename evtchn_lock to event_lock (ddugger@redhat.com ) [484227]
- [xen] sync VT-d2 code with xen-unstable (ddugger@redhat.com ) [484227]
- [xen] VT-d2: support interrupt remapping (ddugger@redhat.com ) [484227]
- [xen] VT-d2: support queue invalidation (ddugger@redhat.com ) [484227]
- [xen] x86: emulate accesses to PCI window regs cf8/cfc (ddugger@redhat.com ) [484227]
- [xen] vtd: avoid redundant context mapping (ddugger@redhat.com ) [484227]
- [xen] x86: fix EPT for VT-d (ddugger@redhat.com ) [484227]
- [xen] x86: add domctl interfaces for VT-d (ddugger@redhat.com ) [484227]
- [xen] x86: memory changes for VT-d (ddugger@redhat.com ) [484227]
- [xen] x86: intercept I/O for assigned device (ddugger@redhat.com ) [484227]
- [xen] x86: IRQ injection changes for VT-d (ddugger@redhat.com ) [484227]
- [xen] add VT-d specific files (ddugger@redhat.com ) [484227]
- [xen] some system changes for VT-d (ddugger@redhat.com ) [484227]
- [xen] add VT-d public header files (ddugger@redhat.com ) [484227]
- [xen] ia64: add pci definitions and access functions (ddugger@redhat.com ) [484227]

* Fri Apr 03 2009 Don Zickus <dzickus@redhat.com> [2.6.18-138.el5]
- [nfs] remove bogus lock-if-signalled case (Bryn M. Reeves ) [456288]
- [gfs2] fix uninterruptible quotad sleeping (Steven Whitehouse ) [492943]
- [net] iptables NAT port randomisation (Thomas Graf ) [459943]
- [gfs2] tar off gfs2 broken - truncated symbolic links (Steven Whitehouse ) [492911]
- [net] skip redirect msg if target addr is not link-local (Thomas Graf ) [481209]
- [scsi] lpfc: remove duplicate pci* functions from driver (Prarit Bhargava ) [442007]
- [net] igb: make driver ioport free (Prarit Bhargava ) [442007]
- [net] e1000: make driver ioport free (Prarit Bhargava ) [442007]
- [net] e1000e: make driver ioport free (Prarit Bhargava ) [442007]
- [pci] add pci*_selected_region/pci_enable_device_io|mem (Prarit Bhargava ) [442007]
- [x86] NONSTOP_TSC in tsc clocksource (Luming Yu ) [474091]
- [ppc] keyboard not recognized on bare metal (Justin Payne ) [455232]
- [fs] writeback: fix persistent inode->dirtied_when val (Jeff Layton ) [489359]
- [fs] xfs: misc upstream fixes (Eric Sandeen ) [470845]
- [fs] xfs: fix compat ioctls (Eric Sandeen ) [470845]
- [fs] xfs: new aops interface (Eric Sandeen ) [470845]
- [fs] xfs: backport to rhel5.4 kernel (Eric Sandeen ) [470845]
- [fs] xfs:  update to 2.6.28.6 codebase (Eric Sandeen ) [470845]
- [fs] d_obtain_alias helper (Eric Sandeen ) [470845]
- [fs] d_add_ci helper (Eric Sandeen ) [470845]
- [misc] completion helpers (Eric Sandeen ) [470845]
- [fs] block_page_mkwrite helper (Eric Sandeen ) [470845]
- [mm] generic_segment_checks helper (Eric Sandeen ) [470845]
- [i2c] add support for SB800 SMBus (Bhavna Sarathy ) [488746]
- [i2c] i2c-piix4: support for the Broadcom HT1100 chipset (Flavio Leitner ) [474240]
- [s390] hvc_iucv: z/VM IUCV hypervisor console support (Hans-Joachim Picht ) [475551]
- [s390] hvc_console: upgrade version of hvc_console (Hans-Joachim Picht ) [475551]
- [s390] iucv: locking free version of iucv_message_ (Hans-Joachim Picht ) [475551]
- [s390] set default preferred console device 'ttyS' (Hans-Joachim Picht ) [475551]
- [s390] kernel: shutdown action 'dump_reipl' (Hans-Joachim Picht ) [474688]
- [s390] splice: handle try_to_release_page failure (Hans-Joachim Picht ) [475334]
- [s390] blktrace: add ioctls to SCSI generic devices (Hans-Joachim Picht ) [475334]
- [s390] add FCP performance data collection (Hans-Joachim Picht ) [475334]
- [s390] extra kernel parameters via VMPARM (Hans-Joachim Picht ) [475530]
- [s390] kernel: extra kernel parameters via VMPARM (Hans-Joachim Picht ) [475530]
- [s390] z90crypt: add ap adapter interrupt support (Hans-Joachim Picht ) [474700]
- [s390] add Call Home data (Hans-Joachim Picht ) [475820]
- [s390] kernel: processor degredation support (Hans-Joachim Picht ) [475820]
- [s390] kernel: Shutdown Actions Interface (Hans-Joachim Picht ) [475563]
- [s390] provide service levels of HW & Hypervisor (Hans-Joachim Picht ) [475570]
- [s390] qeth: ipv6 support for hiper socket layer 3 (Hans-Joachim Picht ) [475572]
- [s390] kernel: NSS Support (Hans-Joachim Picht ) [474646]
- [acpi] donot evaluate _PPC until _PSS has been evaluated (Matthew Garrett ) [469105]
- [net] iwlwifi: enable LEDS Kconfig options (John W. Linville ) [486030]
- [spec] devel pkg: own the directories they write too (Don Zickus ) [481808]
- [crypto] bugfixes to ansi_cprng for fips compliance (Neil Horman ) [481175 469437]
- [scsi] qla2xxx: production FCoE firmware (Marcus Barrow ) [471900]
- [scsi] qla2xxx: production FCoE support (Marcus Barrow ) [471900]
- [fs] add compat_sys_ustat (Eric Sandeen ) [472426]
- [x86_64] panic if AMD cpu_khz is wrong (Prarit Bhargava ) [472523]
- [x86] fix calls to pci_scan_bus (Prarit Bhargava ) [470202]

* Fri Mar 27 2009 Don Zickus <dzickus@redhat.com> [2.6.18-137.el5]
- [fs] HFS: mount memory leak (Dave Anderson ) [488048]
- [docs] document netdev_budget (Stanislaw Gruszka ) [463249]
- [net] netfilter: nfmark IPV6 routing in OUTPUT (Anton Arapov ) [470059]
- [gfs2] use ->page_mkwrite for mmap() (Benjamin Marzinski ) [315191]
- [fs] ecryptfs: fix memory leak into crypto headers (Eric Sandeen ) [491256]
- [x86] add nonstop_tsc flag in /proc/cpuinfo (Luming Yu ) [474091]
- [alsa] HDA: update for RHEL-5.4 (Jaroslav Kysela ) [483594]
- [fs] autofs4: fix lookup deadlock (Ian Kent ) [490078]
- [fs] autofs4: make autofs type usage explicit (Ian Kent ) [452120]
- [fs] autofs4: add miscelaneous device for ioctls (Ian Kent ) [452120]
- [fs] autofs4: devicer node ioctl docoumentation (Ian Kent ) [452120]
- [fs] autofs4: track uid and gid of last mount requester (Ian Kent ) [452120]
- [nfs] memory corruption in nfs3_xdr_setaclargs (Sachin S. Prabhu ) [479432]
- [misc] cpuset: attach_task fixes (KII Keiichi ) [471634]
- [s390] dasd: fix race in dasd timer handling (Hans-Joachim Picht ) [490128]
- [x86] use [ml]fence to synchronize rdtsc (Chris Lalancette ) [448588]
- [xen] silence MMCONFIG warnings (Chris Lalancette ) [462572]
- [xen] fix occasional deadlocks in Xen netfront (Chris Lalancette ) [480939]
- [xen] fix crash when modprobe xen-vnif in a KVM guest (Chris Lalancette ) [487691]
- [xen] xen reports bogus LowTotal (Chris Lalancette ) [428892]
- [xen] wait 5 minutes for device connection (Chris Lalancette ) [396621]
- [xen] only recover connected devices on resume (Chris Lalancette ) [396621]
- [xen] ia64: fix bad mpa messages (Chris Lalancette ) [288511]
- [net] handle non-linear packets in skb_checksum_setup (Herbert Xu ) [477012]
- [fs] fix __page_symlink to be kabi friendly (Josef Bacik ) [445433]
- [fs] ext3: convert to new aops (Josef Bacik ) [445433]
- [mm] make new aops kABI friendly (Josef Bacik ) [445433]
- [fs] fix symlink allocation context (Josef Bacik ) [445433]
- [mm] iov_iter_advance fix, don't go off the end (Josef Bacik ) [445433]
- [mm] fix infinite loop with iov_iter_advance (Josef Bacik ) [445433]
- [mm] restore the KERNEL_DS optimisations (Josef Bacik ) [445433]
- [gfs2] remove generic aops stuff (Josef Bacik ) [445433]
- [fs] new cont helpers (Josef Bacik ) [445433]
- [mm] introduce new aops, write_begin and write_end (Josef Bacik ) [445433]
- [fs] splice: dont do readpage (Josef Bacik ) [445433]
- [fs] splice: don't steal pages (Josef Bacik ) [445433]
- [gfs2] remove static iov iter stuff (Josef Bacik ) [445433]
- [mm] iov_iter helper functions (Josef Bacik ) [445433]
- [mm] fix pagecache write deadlocks (Josef Bacik ) [445433]
- [mm] write iovec cleanup (Josef Bacik ) [445433]
- [mm] fix other users of __grab_cache_page (Josef Bacik ) [445433]
- [mm] cleanup page caching stuff (Josef Bacik ) [445433]
- [mm] cleanup error handling (Josef Bacik ) [445433]
- [mm] clean up buffered write code (Josef Bacik ) [445433]
- [mm] revert deadlock on vectored write fix (Josef Bacik ) [445433]
- [mm] kill the zero-length iovec segments handling (Josef Bacik ) [445433]
- [mm] revert KERNEL_DS buffered write optimisation (Josef Bacik ) [445433]
- [mm] clean up pagecache allocation (Josef Bacik ) [445433]
- [x86] move pci_video_fixup to later in boot (Prarit Bhargava ) [467785]
- [usb] net: dm9601: upstream fixes for 5.4 (Ivan Vecera ) [471800]
- [xen] ia64: fix FP emulation in a PV domain (Chris Lalancette ) [477098]
- [xen] ia64: make sure guest pages don't change (Chris Lalancette ) [477098]
- [xen] improve handle_fpu_swa (Chris Lalancette ) [477098]
- [xen] ia64: fix windows 2003 BSOD (Chris Lalancette ) [479923]
- [xen] x86: fix dom0 panic when using dom0_max_vcpus (Chris Lalancette ) [485119]
- [xen] x86: silence WRMSR warnings (Chris Lalancette ) [470035]

* Fri Mar 20 2009 Don Zickus <dzickus@redhat.com> [2.6.18-136.el5]
- Revert: [x86_64] fix gettimeoday TSC overflow issue (Prarit Bhargava ) [467942]
- [ptrace] audit_syscall_entry to use right syscall number (Jiri Pirko ) [488002] {CVE-2009-0834}
- [md] dm: check log bitmap will fit within the log device (Milan Broz ) [471565]
- [nfs] add 'lookupcache' mount option for nfs shares (Sachin S. Prabhu ) [489285]
- [nfs] add fine grain control for lookup cache in nfs (Sachin S. Prabhu ) [489285]
- [net] tulip: MTU problems with 802.1q tagged frames (Ivan Vecera ) [484796]
- [net] rtnetlink: fix sending message when replace route (Jiri Pirko ) [462725]
- [s390] sclp: handle zero-length event buffers (Hans-Joachim Picht ) [487695]
- [s390] dasd: DASDFMT not operating like CPFMTXA (Hans-Joachim Picht ) [484836]
- [xen] fix blkfront bug with overflowing ring (Chris Lalancette ) [460693]
- [net] ipv6: disallow IPPROTO_IPV6-level IPV6_CHECKSUM (Jiri Pirko ) [486204]
- [ide] fix interrupt flood at startup w/ESB2 (James Paradis ) [438979]
- [s390] cio: Properly disable not operational subchannel (Hans-Joachim Picht ) [487701]
- [misc] kernel-headers: add serial_reg.h (Don Zickus ) [463538]

* Fri Mar 13 2009 Don Zickus <dzickus@redhat.com> [2.6.18-135.el5]
- [s390] iucv: failing cpu hot remove for inactive iucv (Hans-Joachim Picht ) [485412]
- [s390] dasd: fix waitqueue for sleep_on_immediatly (Hans-Joachim Picht ) [480161]
- [ide] increase timeouts in wait_drive_not_busy (Stanislaw Gruszka ) [464039]
- [x86_64] mce: do not clear an unrecoverable error status (Aristeu Rozanski ) [489692]
- [wireless] iwlwifi: booting with RF-kill switch enabled (John W. Linville ) [482990]
- [net] put_cmsg: may cause application memory overflow (Jiri Pirko ) [488367]
- [x86_64] fix gettimeoday TSC overflow issue (Prarit Bhargava ) [467942]
- [net] ipv6: check hop limit setting in ancillary data (Jiri Pirko ) [487406]
- [net] ipv6: check outgoing interface in all cases (Jiri Pirko ) [486215]
- [acpi] disable GPEs at the start of resume (Matthew Garrett ) [456302]
- [crypto] include crypto headers in kernel-devel (Neil Horman ) [470929]
- [net] netxen: rebase for RHEL-5.4 (tcamuso@redhat.com ) [485381]
- [misc] signal: modify locking to handle large loads (AMEET M. PARANJAPE ) [487376]
- [kexec] add ability to dump log from vmcore file (Neil Horman ) [485308]
- [fs] ext3: handle collisions in htree dirs (Eric Sandeen ) [465626]
- [acpi] use vmalloc in acpi_system_read_dsdt (Prarit Bhargava ) [480142]
- [misc] make ioctl.h compatible with userland (Jiri Pirko ) [473947]
- [nfs] sunrpc: add sv_maxconn field to svc_serv (Jeff Layton ) [468092]
- [nfs] lockd: set svc_serv->sv_maxconn to a better value (Jeff Layton ) [468092]
- [mm] decrement reclaim_in_progress after an OOM kill (Larry Woodman ) [488955]
- [misc] sysrq-t: display backtrace for runnable processes (Anton Arapov ) [456588]

* Fri Mar 06 2009 Don Zickus <dzickus@redhat.com> [2.6.18-134.el5]
- [dlm] fix length calculation in compat code (David Teigland ) [487672]
- [net] ehea: remove adapter from list in error path (AMEET M. PARANJAPE ) [488254]
- [x86] reserve low 64k of memory to avoid BIOS corruption (Matthew Garrett ) [471851]
- [nfs] fix hung clients from deadlock in flush_workqueue (David Jeffery ) [483627]
- [net] fix a few udp counters (Neil Horman ) [483266]
- [ia64] use current_kernel_time/xtime in hrtimer_start() (Prarit Bhargava ) [485323]
- [sata] libata: ahci withdraw IGN_SERR_INTERNAL for SB800 (David Milburn ) [474301]
- [ata] libata: iterate padded atapi scatterlist (David Milburn ) [446086]
- [x86] TSC keeps running in C3+ (Luming Yu ) [474091]
- [acpi] fix C-states less efficient on certain machines (Luming Yu ) [484174]
- [net] ipv6: fix getsockopt for sticky options (Jiri Pirko ) [484105 483790]
- [ppc64] cell spufs: update to the upstream for RHEL-5.4 (AMEET M. PARANJAPE ) [475620]
- [ppc64] cell: fix npc setting for NOSCHED contexts (AMEET M. PARANJAPE ) [467344]
- [ppc64] handle null iommu dma-window property correctly (AMEET M. PARANJAPE ) [393241]
- [net] e1000, bnx2: enable entropy generation (Ivan Vecera ) [439898]
- Revert: [xen] console: make LUKS passphrase readable (Bill Burns ) [475986]
- [gfs2] add UUID to gfs2 super block (Steven Whitehouse ) [242696]
- [x86] consistent time options for x86_64 and i386 (Prarit Bhargava ) [475374]
- [xen] allow > 4GB EPT guests on i386 (Chris Lalancette ) [478522]
- [xen] clear screen to make LUKS passphrase visible (Bill Burns ) [475986]

* Tue Mar 03 2009 Don Zickus <dzickus@redhat.com> [2.6.18-133.el5]
- [net] fix oops when using openswan (Neil Horman ) [484590]
- [net] bonding: fix arp_validate=3 slaves behaviour (Jiri Pirko ) [484304]
- [serial] 8250: fix boot hang when using with SOL port (Mauro Carvalho Chehab ) [467124]
- [usb] sb600/sb700: workaround for hang (Pete Zaitcev ) [471972]
- [gfs2] make quota mount option consistent with gfs (Bob Peterson ) [486168]
- [xen] pv-block: remove anaconda workaround (Don Dutile ) [477005]
- [ppc64] power7: fix /proc/cpuinfo cpus info (AMEET M. PARANJAPE ) [486649]
- [net] skfp_ioctl inverted logic flaw (Eugene Teo ) [486540] {CVE-2009-0675}
- [net] memory disclosure in SO_BSDCOMPAT gsopt (Eugene Teo ) [486518] {CVE-2009-0676}
- [net] enic: upstream update to version 1.0.0.933 (Andy Gospodarek ) [484824]
- [mm] cow vs gup race fix (Andrea Arcangeli ) [471613]
- [mm] fork vs gup race fix (Andrea Arcangeli ) [471613]
- [gfs2] parsing of remount arguments incorrect (Bob Peterson ) [479401]
- [ppc64] eeh: disable/enable LSI interrupts (AMEET M. PARANJAPE ) [475696]
- [x86] limit max_cstate to use TSC on some platforms (Tony Camuso ) [470572]
- [ptrace] correctly handle ptrace_update return value (Jerome Marchand ) [483814]
- [dlm] fix plock notify callback to lockd (David Teigland ) [470074]
- [input] wacom: 12x12 problem while using lens cursor (Aristeu Rozanski ) [484959]
- [wireless] ath5k: update to F10 version (Michal Schmidt ) [479049]
- [xen] disable suspend in kernel (Justin M. Forbes ) [430928]
- [net] ipv6: update setsockopt to support RFC 3493 (Jiri Pirko ) [484971]
- [net] ipv6: check length of users's optval in setsockopt (Jiri Pirko ) [484977]
- [scsi] handle work queue and shost_data setup failures (mchristi@redhat.com ) [450862]
- [net] skbuff: fix oops in skb_seq_read (mchristi@redhat.com ) [483285]
- [net] sky2: update driver for RHEL-5.4 (Neil Horman ) [484712]
- [net] ipv6: Hop-by-Hop options header returned bad value (Jiri Pirko ) [483793]
- [pci] fix MSI descriptor leak during hot-unplug (James Paradis ) [484943]
- [net] improve udp port randomization (Vitaly Mayatskikh ) [480951]
- [misc] ia64, s390: add kernel version to panic output (Prarit Bhargava ) [484403]
- [x86-64] fix int $0x80 -ENOSYS return (Vitaly Mayatskikh ) [481682]
- [net] don't add NAT extension for confirmed conntracks (Herbert Xu ) [481076]
- [xen] fbfront dirty race (Markus Armbruster ) [456893]
- [net] ehea: improve behaviour in low mem conditions (AMEET M. PARANJAPE ) [483148]
- [net] fix icmp_send and icmpv6_send host re-lookup code (Jiri Pirko ) [439670]
- [scsi] ibmvscsi: N-Port-ID support on ppc64 (AMEET M. PARANJAPE ) [474701]
- [xen] guest crash when host has >= 64G RAM (Rik van Riel ) [448115]
- [ppc] cell: add support for power button on blades (AMEET M. PARANJAPE ) [475658]
- [ppc64] serial_core: define FIXED_PORT flag (AMEET M. PARANJAPE ) [475621]
- [s390] cio: I/O error after cable pulls 2 (Hans-Joachim Picht ) [479878]
- [misc] ptrace, utrace: fix blocked signal injection (Jerome Marchand ) [451849]
- [xen] irq: remove superfluous printk (Rik van Riel ) [456095]
- [s390] qeth: print HiperSocket version on z9 and later (Hans-Joachim Picht ) [479881]
- [s390] qeth: crash in case of layer mismatch for VSWITCH (Hans-Joachim Picht ) [476205]
- [s390] qdio: only 1 buffer in INPUT_PROCESSING state (Hans-Joachim Picht ) [479867]
- [s390] disable cpu topology support by default (Hans-Joachim Picht ) [475797]
- [s390] qeth: unnecessary support ckeck in sysfs route6 (Hans-Joachim Picht ) [474469]
- [s390] cio: ccwgroup online vs. ungroup race condition (Hans-Joachim Picht ) [479879]
- [s390] dasd: dasd_device_from_cdev called from interrupt (Hans-Joachim Picht ) [474806]
- [misc] minor signal handling vulnerability (Oleg Nesterov ) [479964] {CVE-2009-0028}

* Fri Feb 20 2009 Don Zickus <dzickus@redhat.com> [2.6.18-132.el5]
- [firmware] dell_rbu: prevent oops (Don Howard ) [482942]
- [fs] lockd: improve locking when exiting from a process (Peter Staubach ) [448929]
- [misc] backport RUSAGE_THREAD support (Jerome Marchand ) [451063]
- [gfs2] panic in debugfs_remove when unmounting (Abhijith Das ) [483617]
- [nfs] memory corruption in nfs3_xdr_setaclargs (Sachin S. Prabhu ) [479432]
- [nfs] fix hangs during heavy write workloads (Peter Staubach ) [469848]
- [pci] msi: set 'En' bit for devices on HT-based platform (Andy Gospodarek ) [290701]
- [net] ipt_REJECT: properly handle IP options (Ivan Vecera ) [473504]
- [ppc] cell: fix GDB watchpoints (AMEET M. PARANJAPE ) [480239]
- [edac] add i5400 driver (Mauro Carvalho Chehab ) [462895]
- [xen] fix disappearing PCI devices from PV guests (Bill Burns ) [233801]
- [net] s2io: flush statistics when changing the MTU (AMEET M. PARANJAPE ) [459514]
- [scsi] no-sense msgs, data corruption, but no i/o errors (Rob Evers ) [468088]
- [powerpc] wait for a panic_timeout > 0 before reboot (AMEET M. PARANJAPE ) [446120]
- [ppc64] cell: axon-msi: Retry on missing interrupt (AMEET M. PARANJAPE ) [472405]
- [ppc] MSI interrupts are unreliable on IBM QS21 and QS22 (AMEET M. PARANJAPE ) [472405]
- [crypto] des3_ede: permit weak keys unless REQ_WEAK_KEY (Jarod Wilson ) [474394]
- [ata] JMB361 only has one port (Prarit Bhargava ) [476206]
- [net] r8169: disable the ability to change MAC address (Ivan Vecera ) [475867]
- [misc] futex.h: remove kernel bits for userspace header (Anton Arapov ) [475790]
- [fs] inotify: send IN_ATTRIB event on link count changes (Eric Paris ) [471893]
- [misc] ppc64: large sends fail with unix domain sockets (Larry Woodman ) [461312]
- [audit] misc kernel fixups (Alexander Viro ) [475330]
- [audit] records for descr created by pipe and socketpair (Alexander Viro ) [475278]
- [audit] control character detection is off-by-one (Alexander Viro ) [475150]
- [audit] fix kstrdup error check (Alexander Viro ) [475149]
- [audit] assorted audit_filter_task panics on ctx == NULL (Alexander Viro ) [475147]
- [audit] increase AUDIT_MAX_KEY_LEN (Alexander Viro ) [475145]
- [nfs] race with nfs_access_cache_shrinker() and umount (Peter Staubach ) [469225]
- [nfs] lockd: handle long grace periods correctly (Peter Staubach ) [474590]
- [crypto] ansi_cprng: fix inverted DT increment routine (Jarod Wilson ) [471281]
- [crypto] ansi_cprng: extra call to _get_more_prng_bytes (Jarod Wilson ) [471281]
- [fs] proc: Proportional Set Size calculation and display (Larry Woodman ) [471969]
- [video] avoid writing outside shadow.bytes array (Mauro Carvalho Chehab ) [471844]
- [fs] need locking when reading /proc/<pid>/oom_score (Larry Woodman ) [470459]
- [x86] memmap=X$Y does not yield new map (Prarit Bhargava ) [464500]
- [s390] qeth: avoid problems after failing recovery (Hans-Joachim Picht ) [468019]
- [s390] qeth: avoid skb_under_panic for bad inbound data (Hans-Joachim Picht ) [468075]
- [s390] sclp: incorrect softirq disable/enable (Hans-Joachim Picht ) [468021]
- [crypto] export DSA_verify as a gpl symbol (Jarod Wilson ) [470111]
- [s390] lcs: output request completion with zero cpa val (Hans-Joachim Picht ) [463165]
- [s390] dasd: oops when Hyper PAV alias is set online (Hans-Joachim Picht ) [458155]
- [s390] ipl: file boot then boot from alt dev won't work (Hans-Joachim Picht ) [458115]
- [s390] zfcp: remove messages flooding the kernel log (Hans-Joachim Picht ) [455260]
- [snd] fix snd-sb16.ko compile (Prarit Bhargava ) [456698]

* Fri Feb 06 2009 Don Zickus <dzickus@redhat.com> [2.6.18-131.el5]
- [scsi] libata: sas_ata fixup sas_sata_ops (David Milburn ) [483171]
- [fs] ecryptfs: readlink flaw (Eric Sandeen ) [481607] {CVE-2009-0269}
- [crypto] ccm: fix handling of null assoc data (Jarod Wilson ) [481031]
- [misc] fix leap second hang (Prarit Bhargava ) [479765]
- [qla2xxx] correct endianness during flash manipulation (Marcus Barrow ) [481691]
- [net] gso: ensure that the packet is long enough (Jiri Pirko ) [479927]
- [audit] remove bogus newlines in EXECVE audit records (Jiri Pirko ) [479412]
- [ppc] don't reset affinity for secondary MPIC on boot (AMEET M. PARANJAPE ) [480801]
- [nfs] knfsd: alloc readahead cache in individual chunks (Jeff Layton ) [459397]
- [nfs] knfsd: read-ahead cache, export table corruption (Jeff Layton ) [459397]
- [nfs] knfsd: replace kmalloc/memset with kcalloc (Jeff Layton ) [459397]
- [nfs] knfsd: make readahead params cache SMP-friendly (Jeff Layton ) [459397]
- [crypto] fix sha384 blocksize definition (Neil Horman ) [469167]

* Fri Jan 30 2009 Don Zickus <dzickus@redhat.com> [2.6.18-130.el5]
- [security] keys: introduce missing kfree (Jiri Pirko ) [480598] {CVE-2009-0031}
- [net] ixgbe: frame reception and ring parameter issues (Andy Gospodarek ) [475625]
- [net] tcp-lp: prevent chance for oops (Ivan Vecera ) [478638]
- [misc] fix memory leak during pipe failure (Benjamin Marzinski ) [478643]
- [block] enforce a minimum SG_IO timeout (Eugene Teo ) [475406] {CVE-2008-5700}
- [x86] pci domain: re-enable support on blacklisted boxes (Prarit Bhargava ) [474891]
- [fs] link_path_walk sanity, stack usage optimization (Anton Arapov ) [470139]
- [x86_64] incorrect cpu_khz calculation for AMD processor (Prarit Bhargava ) [467782]
- [crypto] fips: panic kernel if we fail crypto self tests (Neil Horman ) [462909]
- [genkey] increase signing key length to 1024 bits (Neil Horman ) [413241]
- [x86] kdump: lockup when crashing with console_sem held (Neil Horman ) [456934]
-  [fs] ext[234]: directory corruption DoS (Eugene Teo ) [459604] {CVE-2008-3528}

* Fri Jan 23 2009 Don Zickus <dzickus@redhat.com> [2.6.18-129.el5]
- [gfs2] mount attempt hangs if no more journals available (Bob Peterson ) [475312]
- [sched] fix clock_gettime monotonicity (Peter Zijlstra ) [477763]
- [nfs] create rpc clients with proper auth flavor (Jeff Layton ) [465456]
- [nfs] handle attribute timeout and u32 jiffies wrap (Jeff Layton ) [460133]
- [net] deadlock in Hierarchical token bucket scheduler (Neil Horman ) [474797]
- [net] sctp: overflow with bad stream ID in FWD-TSN chunk (Eugene Teo ) [478805] {CVE-2009-0065}
- [md] fix oops with device-mapper mirror target (Heinz Mauelshagen ) [472558]
- [openib] restore traffic in connected mode on HCA (AMEET M. PARANJAPE ) [477000]
- [net] add preemption point in qdisc_run (Jiri Pirko ) [471398] {CVE-2008-5713}
- [wireless] iwl: fix BUG_ON in driver (Neil Horman ) [477671]
- [x86_64] copy_user_c assembler can leave garbage in rsi (Larry Woodman ) [456682]
- [misc] setpgid returns ESRCH in some situations (Oleg Nesterov ) [472433]
- [s390] zfcp: fix hexdump data in s390dbf traces (Hans-Joachim Picht ) [470618]
- [fs] hfsplus: fix buffer overflow with a corrupted image (Anton Arapov ) [469638] {CVE-2008-4933}
- [fs] hfsplus: check read_mapping_page return value (Anton Arapov ) [469645] {CVE-2008-4934}
- [fs] hfs: fix namelength memory corruption (Anton Arapov ) [470773] {CVE-2008-5025}
- [net] netlink: fix overrun in attribute iteration (Eugene Teo ) [462283]

* Wed Dec 17 2008 Don Zickus <dzickus@redhat.com> [2.6.18-128.el5]
- [cifs] cifs_writepages may skip unwritten pages (Jeff Layton ) [470267]

* Mon Dec 15 2008 Don Zickus <dzickus@redhat.com> [2.6.18-127.el5]
- Revert: [i386]: check for dmi_data in powernow_k8 driver (Prarit Bhargava ) [476184]
- [xen] re-enable using xenpv in boot path for FV guests (Don Dutile ) [473899]
- [xen] pv_hvm: guest hang on FV save/restore (Don Dutile ) [475778]
- [openib] fix ipoib oops in unicast_arp_send (Doug Ledford ) [476005]
- [scsi] fnic: remove link down count processing (mchristi@redhat.com ) [474935]
- Revert: [x86] disable hpet on machine_crash_shutdown (Neil Horman ) [475652]
- [scsi] ibmvscsi: EH fails due to insufficient resources (AMEET M. PARANJAPE ) [475618]
- [x86_64] proc: export GART region through /proc/iomem (Neil Horman ) [475507]
- [acpi] add xw8600 and xw6600 to GPE0 block blacklist (Prarit Bhargava ) [475418]
- [net] cxgb3: fixup embedded firmware problems take 2 (Andy Gospodarek ) [469774]

* Mon Dec 08 2008 Don Zickus <dzickus@redhat.com> [2.6.18-126.el5]
- [scsi] mpt fusion: disable msi by default (Tomas Henzl ) [474465]
- [scsi] fcoe: update drivers (mchristi@redhat.com ) [474089]
- [scsi] fix error handler to call scsi_decide_disposition (Tom Coughlan ) [474345]
- [scsi] lpfc: fix cancel_retry_delay (Tom Coughlan ) [470610]
- [x86] disable hpet on machine_crash_shutdown (Neil Horman ) [473038]
- Revert [mm] keep pagefault from happening under pagelock (Don Zickus ) [473150]
- [net] enic: update to version 1.0.0.648 (Andy Gospodarek ) [473871]
- [scsi] qla4xxx: increase iscsi session check to 3-tuple (Marcus Barrow ) [474736]
- [agp] update the names of some graphics drivers (John Villalovos ) [472438]
- [net] atm: prevent local denial of service (Eugene Teo ) [473701] {CVE-2008-5079}
- [scsi] remove scsi_dh_alua (mchristi@redhat.com ) [471920]
- [scsi] qla2xx/qla84xx: occasional panic on loading (Marcus Barrow ) [472382]
- [net] cxgb3: eeh and eeprom fixups (Andy Gospodarek ) [441959]
- [net] cxgb3: fixup embedded firmware problems (Andy Gospodarek ) [469774]
- [wireless] iwlwifi/mac80211: various small fixes (John W. Linville ) [468967]
- [x86_64] fix AMD IOMMU boot issue (Joachim Deguara ) [473464]
- [x86_64] limit num of mce sysfs files removed on suspend (Prarit Bhargava ) [467725]
- [xen] console: make LUKS passphrase readable (Bill Burns ) [466240]
- [x86_64] Calgary IOMMU sysdata fixes (Prarit Bhargava ) [474047]
- [alsa] select 3stack-dig model for SC CELSIUS R670 (Jaroslav Kysela ) [470449]
- [ata] libata: lba_28_ok sector off by one (David Milburn ) [464868]
- [ppc64] fix system calls on Cell entered with XER.SO=1 (Jesse Larrew ) [474196]
- [block] fix max_segment_size, seg_boundary mask setting (Milan Broz ) [471639]
- [fs] jbd: alter EIO test to avoid spurious jbd aborts (Eric Sandeen ) [472276]
- [acpi] acpi_cpufreq: fix panic when removing module (Prarit Bhargava ) [472844]
- [openib] ehca: fix generating flush work completions (AMEET M. PARANJAPE ) [472812]
- [ata] libata: sata_nv hard reset mcp55 (David Milburn ) [473152]
- [misc] fix add return signal to ptrace_report_exec (AMEET M. PARANJAPE ) [471112]
- [misc] utrace: prevent ptrace_induce_signal() crash (Oleg Nesterov ) [469754]
- [misc] utrace: make ptrace_state refcountable (Oleg Nesterov ) [469754]
- [net] virtio_net: mergeable receive buffers (Mark McLoughlin ) [473120]
- [net] virtio_net: jumbo frame support (Mark McLoughlin ) [473114]
- [net] tun: jumbo frame support (Mark McLoughlin ) [473110]
- [net] fix unix sockets kernel panic (Neil Horman ) [470436] {CVE-2008-5029}
- [xen] x86: emulate movzwl with negative segment offsets (Chris Lalancette ) [471801]

* Mon Dec 01 2008 Don Zickus <dzickus@redhat.com> [2.6.18-125.el5]
- [net] cxgb3: embed firmware in driver (Andy Gospodarek ) [469774]
- [net] cxgb3: eeh, lro, and multiqueue fixes (Andy Gospodarek ) [441959]
- [misc] support for Intel's Ibex Peak (peterm@redhat.com ) [472961]
- [audit] race between inotify watch removal and unmount (Josef Bacik ) [472329] {CVE-2008-5182}
- [net] mlx4: panic when inducing pci bus error (AMEET M. PARANJAPE ) [472769]
- [s390] cio: DASD device driver times out (Hans-Joachim Picht ) [459803]
- [misc] hugepages: ia64 stack overflow and corrupt memory (Larry Woodman ) [472802]
- [net] niu: fix obscure 64-bit read issue (Andy Gospodarek ) [472849]
- [x86] nmi_watchdog: call do_nmi_callback from traps-xen (Aristeu Rozanski ) [471111]
- [GFS2] recovery stuck (Abhijith Das ) [465856]
- [misc] fix check_dead_utrace vs do_wait() race (Oleg Nesterov ) [466774]
- [scsi] cciss: add two new PCI IDs (Tom Coughlan ) [471679]
- [x86] fix memory-less NUMA node booting (Prarit Bhargava ) [471424]
- [pci] generic fix for EEH restore all registers (Jesse Larrew ) [470580]
- [net] e1000e: remove fix for EEH restore all registers (Jesse Larrew ) [470580]
- [agp] use contiguous memory to support xen (Rik van Riel ) [412691]
- [edac] i5000_edac: fix misc/thermal error messages (Aristeu Rozanski ) [471933]
- [alsa] fix PCM write blocking (Jaroslav Kysela ) [468202]
- [xen] build xen-platform-pci as a module (Don Dutile ) [472504]
- [scsi] qla2xx/qla84xx: failure to establish link (Marcus Barrow ) [472382]
- [acpi] add systems to GPE register blacklist (Prarit Bhargava ) [471341]
- [ia64] replace printk with mprintk in MCA/INIT context (Kei Tokunaga ) [471970]
- [usb] add support for dell keyboard 431c:2003 (Mauro Carvalho Chehab ) [471469]
- [net] e1000e: enable ECC correction on 82571 silicon (Andy Gospodarek ) [472095]
- [dlm] fix up memory allocation flags (David Teigland ) [471871]
- [xen] x86: fix highmem-xen.c BUG() (Chris Lalancette ) [452175]
- [xen] guest crashes if RTL8139 NIC is only one specified (Don Dutile ) [471110]
- [net] bnx2: fix oops on call to poll_controller (Neil Horman ) [470625]
- [scsi] update fcoe drivers (mchristi@redhat.com ) [436051]
- [net] bnx2: add support for 5716s (Andy Gospodarek ) [471903]
- [openib] IPoIB: fix oops on fabric events (Doug Ledford ) [471890]
- [libata] force sb600/700 ide mode into ahci on resume (David Milburn ) [466422]
- [xen] increase maximum DMA buffer size (Rik van Riel ) [412691]
- [xen] fix physical memory address overflow (Rik van Riel ) [412691]

* Mon Nov 17 2008 Don Zickus <dzickus@redhat.com> [2.6.18-124.el5]
- [s390] qeth: EDDP for large TSO skb fragment list (Hans-Joachim Picht ) [468068]
- [s390] missing bits for audit-fork (Alexander Viro ) [461831]
- [net] ixgbe: add support for 82598AT (Andy Gospodarek ) [454910]
- [libata] avoid overflow in ata_tf_read_block (David Milburn ) [471576]
- [md] dm-mpath: NULL ptr access in path activation code (Milan Broz ) [471393]
- [scsi] qla2xxx: no NPIV for loop connections (Marcus Barrow ) [471269]
- [ppc64] spufs: clean up page fault error checking (AMEET M. PARANJAPE ) [470301]
- [fs] cifs: corrupt data due to interleaved write calls (Jeff Layton ) [470267]
- [misc] lots of interrupts with /proc/.../hz_timer=0 (Hans-Joachim Picht ) [470289]
- [selinux] recognize addrlabel netlink messages (Thomas Graf ) [446063]
- [acpi] thinkpad: fix autoloading (Matthew Garrett ) [466816]
- [net] bnx2x: eeh, unload, probe, and endian fixes (Andy Gospodarek ) [468922]
- [firewire] various bug and module unload hang fixes (Jay Fenlason ) [469710 469711]

* Mon Nov 10 2008 Don Zickus <dzickus@redhat.com> [2.6.18-123.el5]
- [s390] cio: reduce cpu utilization during device scan (Hans-Joachim Picht ) [459793]
- [s390] cio: fix double unregistering of subchannels (Hans-Joachim Picht ) [456087]
- [video] uvc: buf overflow in format descriptor parsing (Jay Fenlason ) [470427] {CVE-2008-3496}
- [usb] add HID_QUIRK_RESET_LEDS to some keyboards (mchehab@infradead.org ) [434538]
- [acpi] always use 32 bit value for GPE0 on HP xw boxes (Prarit Bhargava ) [456638]
- [wireless] iwlagn/mac80211 IBSS fixes (John W. Linville ) [438388]
- [ppc64] cell: fix page fault error checking in spufs (AMEET M. PARANJAPE ) [470301]
- [input] atkbd: cancel delayed work before freeing struct (Jiri Pirko ) [461233]
- [openib] ehca: deadlock race when creating small queues (Jesse Larrew ) [470137]
- [openib] mthca: fix dma mapping leak (AMEET M. PARANJAPE ) [469902]
- [openib] ib_core: use weak ordering for user memory (AMEET M. PARANJAPE ) [469902]
- [ppc64] dma-mapping: provide attributes on cell platform (AMEET M. PARANJAPE ) [469902]
- [net] bnx2: prevent ethtool -r EEH event (AMEET M. PARANJAPE ) [469962]
- [net] bonding: update docs for arp_ip_target behavior (Andy Gospodarek ) [468870]
- [xen] uninitialized watch structure can lead to crashes (Don Dutile ) [465849]
- [openib] ehca: remove ref to QP if port activation fails (AMEET M. PARANJAPE ) [469941]
- [usb] fix locking for input devices (James Paradis ) [468915]
- [nfs] oops in direct I/O error handling (Steve Dickson ) [466164]
- [md] crash in device mapper if the user removes snapshot (Mikulas Patocka ) [468473]
- [openib] config update: enable some debugging (Doug Ledford ) [469410]
- [sata] libata is broken with large disks (David Milburn ) [469715]
- [md] dm-raid1: support extended status output (Jonathan Brassow ) [437177]
- [s390] qdio: repair timeout handling for qdio_shutdown (Hans-Joachim Picht ) [463164]
- [openib] race in ipoib_cm_post_receive_nonsrq (AMEET M. PARANJAPE ) [463485]
- [xen] remove contiguous_bitmap (Chris Lalancette ) [463500]
- [xen] ia64: backport check_pages_physically_contiguous (Chris Lalancette ) [463500]
- [ppc64] cell: corrupt SPU coredump notes (AMEET M. PARANJAPE ) [431881]
- [ppc64] spufs: missing context switch notification log-2 (AMEET M. PARANJAPE ) [462622]
- [ppc64] spufs: missing context switch notification log-1 (AMEET M. PARANJAPE ) [462622]
- [misc] spec: add generic Obsoletes for 3rd party drivers (Jon Masters ) [460047]
- [x86] vDSO: use install_special_mapping (Peter Zijlstra ) [460276] {CVE-2008-3527}
- [xen] limit node poking to available nodes (Joachim Deguara ) [449803]
- [xen] live migration of PV guest fails (Don Dutile ) [469230]

* Mon Nov 03 2008 Don Zickus <dzickus@redhat.com> [2.6.18-122.el5]
- [acpi] check common dmi tables on systems with acpi (Andy Gospodarek ) [469444]
- [scsi] qla3xxx, qla4xxx: update/use new version format (Marcus Barrow ) [469414]
- [md] dm-stripe.c: RAID0 event handling (Heinz Mauelshagen ) [437173]
- [md] dm-raid45.c: add target to makefile (Heinz Mauelshagen ) [437180]
- [md] dm-raid45.c: revert to RHEL5 dm-io kabi (Heinz Mauelshagen ) [437180]
- [wireless] iwlwifi: avoid sleep in softirq context (John W. Linville ) [467831]
- [net] bonding: allow downed interface before mod remove (Andy Gospodarek ) [467244]
- [acpi] fix boot hang on old systems without _CST methods (Matthew Garrett ) [467927]
- [scsi] qla2xxx: fix entries in class_device_attributes (Marcus Barrow ) [468873]
- [ppc64] clock_gettime is not incrementing nanoseconds (AMEET M. PARANJAPE ) [469073]
- [scsi] add fnic driver (mchristi@redhat.com ) [462385]
- [scsi] add libfc and software fcoe driver (mchristi@redhat.com ) [436051]
- [openib] ppc64: fix using SDP on 64K page systems (AMEET M. PARANJAPE ) [468872]
- [fs] ext4: delay capable checks to avoid avc denials (Eric Sandeen ) [467216]
- [fs] ext3: fix accessing freed memory in ext3_abort (Eric Sandeen ) [468547]
- [fs] autofs4: correct offset mount expire check (Ian Kent ) [468187]
- [fs] autofs4: cleanup autofs mount type usage (Ian Kent ) [468187]
- [openib] ehca: queue and completion pair setup problem (AMEET M. PARANJAPE ) [468237]
- [xen] PV: dom0 hang when device re-attached to in guest (Don Dutile ) [467773]
- [scsi] qla2xxx: correct Atmel flash-part handling (Marcus Barrow ) [468573]
- [scsi] qla2xxx: 84xx show FW VER and netlink code fixes (Marcus Barrow ) [464681]
- [scsi] qla2xxx: restore disable by default of MSI, MSI-X (Marcus Barrow ) [468555]
- [scsi] lpfc: Emulex RHEL-5.3 bugfixes (Tom Coughlan ) [461795]
- [s390] qdio: speedup multicast on full HiperSocket queue (Hans-Joachim Picht ) [463162]
- [ppc64] kexec/kdump: disable ptcal on QS21 (AMEET M. PARANJAPE ) [462744]
- [ppc64] ptcal has to be disabled to use kexec on QS21 (AMEET M. PARANJAPE ) [462744]
- [net] ixgbe: bring up device without crashing fix (AMEET M. PARANJAPE ) [467777]
- [fs] ecryptfs: storing crypto info in xattr corrupts mem (Eric Sandeen ) [468192]
- [misc] rtc: disable SIGIO notification on close (Vitaly Mayatskikh ) [465747]
- [net] allow rcv on inactive slaves if listener exists (Andy Gospodarek ) [448144]
- [net] e1000e: update driver to support recovery (AMEET M. PARANJAPE ) [445299]
- [xen] virtio_net: some relatively minor fixes (Mark McLoughlin ) [468034]
- [kabi] add dlm_posix_set_fsid (Jon Masters ) [468538]
- [wireless] iwlwifi: fix busted tkip encryption _again_ (John W. Linville ) [467831]
- [x86] make halt -f command work correctly (Ivan Vecera ) [413921]
- [ppc64] EEH PCI-E: recovery fails E1000; support MSI (AMEET M. PARANJAPE ) [445299]
- [x86_64] create a fallback for IBM Calgary (Pete Zaitcev ) [453680]
- [drm] i915 driver arbitrary ioremap (Eugene Teo ) [464509] {CVE-2008-3831}
- [xen] x86: allow the kernel to boot on pre-64 bit hw (Chris Lalancette ) [468083]

* Mon Oct 27 2008 Don Zickus <dzickus@redhat.com> [2.6.18-121.el5]
- [net] tun: fix printk warning (Mark McLoughlin ) [468536]
- [xen] FV: fix lockdep warnings when running debug kernel (Don Dutile ) [459876]
- [xen] fix crash on IRQ exhaustion (Bill Burns ) [442736]
- [net] ipv4: fix byte value boundary check (Jiri Pirko ) [468148]
- [ia64] fix ptrace hangs when following threads (Denys Vlasenko ) [461456]
- [net] tcp: let skbs grow over a page on fast peers (Mark McLoughlin ) [467845]
- [md] random memory corruption in snapshots (Mikulas Patocka ) [465825]
- [misc] ptrace: fix exec report (Jerome Marchand ) [455060]
- [gfs2] set gfp for data mappings to GFP_NOFS (Steven Whitehouse ) [467689]
- [nfs] remove recoverable BUG_ON (Steve Dickson ) [458774]
- [openib] ehca: attempt to free srq when none exists (AMEET M. PARANJAPE ) [463487]
- [fs] don't allow splice to files opened with O_APPEND (Eugene Teo ) [466710] {CVE-2008-4554}
- [fs] ext4: add missing aops (Eric Sandeen ) [466246]
- [ppc64] add missing symbols to vmcoreinfo (Neil Horman ) [465396]
- [net] sctp: INIT-ACK indicates no AUTH peer support oops (Eugene Teo ) [466082] {CVE-2008-4576}
- [ppc64] fix race for a free SPU (AMEET M. PARANJAPE ) [465581]
- [ppc64] SPUs hang when run with affinity-2 (AMEET M. PARANJAPE ) [464686]
- [ppc64] SPUs hang when run with affinity-1 (AMEET M. PARANJAPE ) [464686]
- [openib] ehca: add flush CQE generation (AMEET M. PARANJAPE ) [462619]
- [x86] PAE: limit RAM to 64GB/PAE36 (Larry Woodman ) [465373]
- [nfs] portmap client race (Steve Dickson ) [462332]
- [input] atkbd: delay executing of LED switching request (Jiri Pirko ) [461233]
- [x86] powernow_k8: depend on newer version of cpuspeed (Brian Maly ) [468764]
- [fs] ext4: fix warning on x86_64 build (Eric Sandeen ) [463277]
- [crypto] fix ipsec crash with MAC longer than 16 bytes (Neil Horman ) [459812]
- [fs] ecryptfs: depend on newer version of ecryptfs-utils (Eric Sandeen ) [468772]
- [ppc64] support O_NONBLOCK in /proc/ppc64/rtas/error_log (Vitaly Mayatskikh ) [376831]
- [xen] ia64: make viosapic SMP-safe by adding lock/unlock (Tetsu Yamamoto ) [466552]
- [xen] ia64: VT-i2 performance restoration (Bill Burns ) [467487]

* Fri Oct 17 2008 Don Zickus <dzickus@redhat.com> [2.6.18-120.el5]
- [misc] futex: fixup futex compat for private futexes (Peter Zijlstra ) [467459]
- [pci] set domain/node to 0 in PCI BIOS enum code path (Prarit Bhargava ) [463418]
- [scsi] qla2xxx: prevent NPIV conf for older hbas (Marcus Barrow ) [467153]
- [scsi] fix oops after trying to removing rport twice (Marcus Barrow ) [465945]
- [agp] re-introduce 82G965 graphics support (Prarit Bhargava ) [466307]
- [agp] correct bug in stolen size calculations (Dave Airlie ) [463853]
- [scsi] qla2xxx: merge errors caused initialize failures (Marcus Barrow ) [442946]
- [dm] mpath: moving path activation to workqueue panics (Milan Broz ) [465570]
- [scsi] aacraid: remove some quirk AAC_QUIRK_SCSI_32 bits (Tomas Henzl ) [453472]
- Revert: [ppc64] compile and include the addnote binary (Don Zickus ) [462663]
- [scsi] cciss: the output of LUN size and type wrong (Tomas Henzl ) [466030]
- [misc] posix-timers: event vs dequeue_signal() race (Mark McLoughlin ) [466167]
- [ata] libata: ahci enclosure management support (David Milburn ) [437190]
- [gfs2] fix jdata page invalidation (Steven Whitehouse ) [437803]
- [net] sky2: fix hang resulting from link flap (Neil Horman ) [461681]
- [ata] libata: ata_piix sata/ide combined mode fix (David Milburn ) [463716]
- [gfs2] fix for noatime support (Steven Whitehouse ) [462579]
- [fs] remove SUID when splicing into an inode (Eric Sandeen ) [464452]
- [fs] open() allows setgid bit when user is not in group (Eugene Teo ) [463687] {CVE-2008-4210}
- [dlm] add old plock interface (David Teigland ) [462354]
- [audit] fix NUL handling in TTY input auditing (Miloslav Trmač ) [462441]
- [xen] ia64: fix INIT injection (Tetsu Yamamoto ) [464445]

* Fri Oct 10 2008 Don Zickus <dzickus@redhat.com> [2.6.18-119.el5]
- [ppc64] compile and include the addnote binary (Don Zickus ) [462663]
- [scsi] qla2xxx: new version string defintion (Marcus Barrow ) [465023]
- [acpi] configs update for acpi-cpufreq driver (Matthew Garrett ) [449787]

* Sat Oct 04 2008 Don Zickus <dzickus@redhat.com> [2.6.18-118.el5]
- [scsi] fix QUEUE_FULL retry handling (mchristi@redhat.com ) [463709]
- [drm] support for Intel Cantiga and Eaglelake (Dave Airlie ) [438400]
- [agp] add support for Intel Cantiga and Eaglelake (Dave Airlie ) [463853]
- Revert: [mm] fix support for fast get user pages (Dave Airlie ) [447649]
- [ppc64] netboot image too large (Ameet Paranjape ) [462663]
- [scsi] scsi_error: retry cmd handling of transport error (mchristi@redhat.com ) [463206]
- [net] correct mode setting for extended sysctl interface (Neil Horman ) [463659]
- [net] e1000e: protect ICHx NVM from malicious write/erase (Andy Gospodarek ) [463503]
- [s390] qdio: fix module ref counting in qdio_free (Hans-Joachim Picht ) [458074]
- [scsi] qla2xxx: use the NPIV table to instantiate port (Marcus Barrow ) [459015]
- [scsi] qla2xxx: use the Flash Layout Table (Marcus Barrow ) [459015]
- [scsi] qla2xxx: use the Flash Descriptor Table (Marcus Barrow ) [459015]
- [net] enic: add new 10GbE device (Andy Gospodarek ) [462386]
- [net] ipt_CLUSTERIP: fix imbalanced ref count (Neil Horman ) [382491]
- [scsi] qla2xxx: update 24xx,25xx firmware for RHEL-5.3 (Marcus Barrow ) [442946]
- [net] bnx2: fix problems with multiqueue receive (Andy Gospodarek ) [441964]
- [net] e1000: add module param to set tx descriptor power (Andy Gospodarek ) [436966]
- [misc] preempt-notifier fixes (Eduardo Habkost ) [459838]
- [tty] termiox support missing mutex lock (aris ) [445211]
- [fs] ecryptfs: off-by-one writing null to end of string (Eric Sandeen ) [463478]
- [misc] add tracepoints to activate/deactivate_task (Jason Baron ) [461966]
- [scsi] qla2xxx: use rport dev loss timeout consistently (Marcus Barrow ) [462109]
- [ata] libata: rmmod pata_sil680 hangs (David Milburn ) [462743]
- [scsi] qla2xxx: support PCI Enhanced Error Recovery (Marcus Barrow ) [462416]
- [ppc64] subpage protection for pAVE (Brad Peters ) [439489]
- [ppc64] edac: enable for cell platform (Brad Peters ) [439507]

* Mon Sep 29 2008 Don Zickus <dzickus@redhat.com> [2.6.18-117.el5]
- [mm] filemap: fix iov_base data corruption (Josef Bacik ) [463134]
- Revert: [misc] create a kernel checksum file per FIPS140-2 (Don Zickus ) [444632]
- [x86_64] NMI wd: clear perf counter registers on P4 (Aristeu Rozanski ) [461671]
- [scsi] failfast bit setting in dm-multipath/multipath (mchristi@redhat.com ) [463470]
- [scsi] fix hang introduced by failfast changes (Mark McLoughlin ) [463416]
- [x86_64] revert time syscall changes (Prarit Bhargava ) [461184]

* Thu Sep 18 2008 Don Zickus <dzickus@redhat.com> [2.6.18-116.el5]
- [x86] mm: fix endless page faults in mount_block_root (Larry Woodman ) [455491]
- [mm] check physical address range in ioremap (Larry Woodman ) [455478]
- [scsi] modify failfast so it does not always fail fast (mchristi@redhat.com ) [447586]
- Revert: [mm] NUMA: system is slow when over-committing memory (Larry Woodman ) [457264]
- [docs] update kernel-parameters with tick-divider (Chris Lalancette ) [454792]
- [openib] add an enum for future RDS support (Doug Ledford ) [462551]
- [pci] allow multiple calls to pcim_enable_device (John Feeney ) [462500]
- [xen] virtio: include headers in kernel-headers package (Eduardo Pereira Habkost ) [446214]
- [scsi] libiscsi: data corruption when resending packets (mchristi@redhat.com ) [460158]
- [gfs2] glock deadlock in page fault path (Bob Peterson ) [458684]
- [gfs2] panic if you misspell any mount options (Abhijith Das ) [231369]
- [xen] allow guests to hide the TSC from applications (Chris Lalancette ) [378481] {CVE-2007-5907}

* Sat Sep 13 2008 Don Zickus <dzickus@redhat.com> [2.6.18-115.el5]
- [scsi] qla2xxx: additional residual-count correction (Marcus Barrow ) [462117]
- [audit] audit-fork patch (Alexander Viro ) [461831]
- [net] ipv6: extra sysctls for additional TAHI tests (Neil Horman ) [458270]
- [nfs] disable the fsc mount option (Steve Dickson ) [447474]
- [acpi] correctly allow WoL from S4 state (Neil Horman ) [445890]
- [ia64] procfs: show the size of page table cache (Takao Indoh ) [458410]
- [ia64] procfs: reduce the size of page table cache (Takao Indoh ) [458410]
- [fs] ecryptfs: disallow mounts on nfs, cifs, ecryptfs (Eric Sandeen ) [435115]
- [md] add device-mapper message parser interface (heinzm@redhat.com ) [437180]
- [md] add device-mapper RAID4/5 stripe locking interface (heinzm@redhat.com ) [437180]
- [md] add device-mapper dirty region hash file (heinzm@redhat.com ) [437180]
- [md] add device-mapper object memory cache interface (heinzm@redhat.com ) [437180]
- [md] add device-mapper object memory cache (heinzm@redhat.com ) [437180]
- [md] export dm_disk and dm_put (heinzm@redhat.com ) [437180]
- [md] add device-mapper RAID4/5 target (heinzm@redhat.com ) [437180]
- [md] add device-mapper message parser (heinzm@redhat.com ) [437180]
- [md] add device mapper dirty region hash (heinzm@redhat.com ) [437180]
- [md] add config option for dm RAID4/5 target (heinzm@redhat.com ) [437180]
- [scsi] qla2xxx: update 8.02.00-k5 to 8.02.00-k6 (Marcus Barrow ) [459722]
- [kabi] add vscnprintf, down_write_trylock to whitelist (Jon Masters ) [425341]
- [kabi] add dlm_posix_get/lock/unlock to whitelist (Jon Masters ) [456169]
- [kabi] add mtrr_add and mtrr_del to whitelist (Jon Masters ) [437129]
- [kabi] add iounmap to whitelist (Jon Masters ) [435144]
- [x86] make powernow_k8 a module (Brian Maly ) [438835]
- [fs] ecryptfs: delay lower file opens until needed (Eric Sandeen ) [429142]
- [fs] ecryptfs: unaligned access helpers (Eric Sandeen ) [457143]
- [fs] ecryptfs: string copy cleanup (Eric Sandeen ) [457143]
- [fs] ecryptfs: discard ecryptfsd registration messages (Eric Sandeen ) [457143]
- [fs] ecryptfs: privileged kthread for lower file opens (Eric Sandeen ) [457143]
- [fs] ecryptfs: propagate key errors up at mount time (Eric Sandeen ) [440413]
- [fs] ecryptfs: update to 2.6.26 codebase (Eric Sandeen ) [449668]
- Revert [misc] fix wrong test in wait_task_stopped (Anton Arapov ) [382211]

* Sat Sep 13 2008 Don Zickus <dzickus@redhat.com> [2.6.18-114.el5]
- [xen] cpufreq: fix Nehalem/Supermicro systems (Rik van Riel ) [458894]
- [net] enable TSO if supported by at least one device (Herbert Xu ) [461866]
- [crypto] fix panic in hmac self test (Neil Horman ) [461537]
- [scsi] qla2xxx/qla84xx: update to upstream for RHEL-5.3 (Marcus Barrow ) [461414]
- [misc] hpilo: cleanup device_create for RHEL-5.3 (tcamuso@redhat.com ) [437212]
- [misc] hpilo: update driver to 0.5 (tcamuso@redhat.com ) [437212]
- [misc] hpilo: update to upstream 2.6.27 (tcamuso@redhat.com ) [437212]
- [misc] futex: private futexes (Peter Zijlstra ) [460593]
- [misc] preempt-notifiers implementation (Eduardo Habkost ) [459838]
- [scsi] fusion: update to version 3.04.07 (Tomas Henzl ) [442025]
- [fs] ext4/vfs/mm: core delalloc support (Eric Sandeen ) [455452]
- [net] r8169: add support and fixes (Ivan Vecera ) [251252 441626 442635 443623 452761 453563 457892]
- [md] LVM raid-1 performance fixes (Mikulas Patocka ) [438153]
- [md] LVM raid-1 performance fixes (Mikulas Patocka ) [438153]
- [xen] kdump: ability to use makedumpfile with vmcoreinfo (Neil Horman ) [454498]
- [scsi] aic79xx: reset HBA on kdump kernel boot (Neil Horman ) [458620]
- [fs] implement fallocate syscall (Eric Sandeen ) [450566]
- [misc] better clarify package descriptions (Don Zickus ) [249726]
- [audit] audit TTY input (Miloslav Trmač ) [244135]
- [scsi] qla2xxx - mgmt. API for FCoE, NetLink (Marcus Barrow ) [456900]
- [scsi] qla2xxx - mgmt. API, CT pass thru (Marcus Barrow ) [455900]
-  [misc] hrtimer optimize softirq (George Beshers ) [442148]
- [misc] holdoffs in hrtimer_run_queues (George Beshers ) [442148]
- [xen] netfront xenbus race (Markus Armbruster ) [453574]
- [gfs2] NFSv4 delegations fix for cluster systems (Brad Peters ) [433256]
- [scsi] qla2xxx: update 8.02.00-k1 to 8.02.00.k4 (Marcus Barrow ) [455264]
- [scsi] qla2xxx: upstream changes from 8.01.07-k7 (Marcus Barrow ) [453685]
- [scsi] qla2xxx: add more statistics (Marcus Barrow ) [453441]
- [scsi] qla2xxx: add ISP84XX support (Marcus Barrow ) [442083]
- [ia64] set default max_purges=1 regardless of PAL return (Luming Yu ) [451593]
- [ia64] param for max num of concurrent global TLB purges (Luming Yu ) [451593]
- [ia64] multiple outstanding ptc.g instruction support (Luming Yu ) [451593]
- [scsi] ST: buffer size doesn't match block size panics (Ivan Vecera ) [443645]
- [scsi] fix medium error handling with bad devices (Mike Christie ) [431365]
- [xen] ia64: VT-i2 performance addendum (Bill Burns ) [437096]
- [xen] HV: ability to use makedumpfile with vmcoreinfo (Neil Horman ) [454498]
- [xen] ia64: vps save restore patch (Bill Burns ) [437096]

* Fri Sep 12 2008 Don Zickus <dzickus@redhat.com> [2.6.18-113.el5]
- [xen] remove /proc/xen*/* from bare-metal and FV guests (Don Dutile ) [461532]

* Fri Sep 12 2008 Don Zickus <dzickus@redhat.com> [2.6.18-112.el5]
- [fs] jbd: test BH_write_EIO to detect errors on metadata (Hideo AOKI ) [439581]
- [wireless] rt2x00: avoid NULL-ptr deref when probe fails (John W. Linville ) [448763]
- [x86_64] suspend to disk fails with >4GB of RAM (Matthew Garrett ) [459980]
- [char] add range_is_allowed check to mmap_mem (Eugene Teo ) [460857]
- [acpi] add 3.0 _TSD _TPC _TSS _PTC throttling support (Brian Maly ) [440099]
- [scsi] add scsi device handlers config options (Mike Christie ) [438761]
- [scsi] scsi_dh: add ALUA handler (mchristi@redhat.com ) [438761]
- [scsi] scsi_dh: add rdac handler (mchristi@redhat.com ) [438761]
- [md] dm-mpath: use SCSI device handler (mchristi@redhat.com ) [438761]
- [scsi] add infrastructure for SCSI Device Handlers (mchristi@redhat.com ) [438761]
- [misc] driver core: port bus notifiers (mchristi@redhat.com ) [438761]
- [fs] binfmt_misc: avoid potential kernel stack overflow (Vitaly Mayatskikh ) [459463]
- [CRYPTO] tcrypt: Change the XTEA test vectors (Herbert Xu ) [446522]
- [CRYPTO] skcipher: Use RNG instead of get_random_bytes (Herbert Xu ) [446526]
- [CRYPTO] rng: RNG interface and implementation (Herbert Xu ) [446526]
- [CRYPTO] api: Add fips_enable flag (Herbert Xu ) [444634]
- [CRYPTO] cryptomgr - Test ciphers using ECB (Herbert Xu ) [446522]
- [CRYPTO] api - Use test infrastructure (Herbert Xu ) [446522]
- [CRYPTO] cryptomgr - Add test infrastructure (Herbert Xu ) [446522]
- [CRYPTO] tcrypt - Add alg_test interface (Herbert Xu ) [446522]
- [CRYPTO] tcrypt: self test for des3_ebe cipher (Herbert Xu ) [446522]
- [CRYPTO] api: missing accessors for new crypto_alg field (Herbert Xu ) [446522]
- [CRYPTO] tcrypt: Abort and only log if there is an error (Herbert Xu ) [446522]
- [CRYPTO] tcrypt: Avoid using contiguous pages (Herbert Xu ) [446522]
- [CRYPTO] tcrpyt: Remove unnecessary kmap/kunmap calls (Herbert Xu ) [446522]
- [CRYPTO] tcrypt: Catch cipher destination mem corruption (Herbert Xu ) [446522]
- [CRYPTO] tcrypt: Shrink the tcrypt module (Herbert Xu ) [446522]
- [CRYPTO] tcrypt: AES CBC test vector from NIST SP800-38A (Herbert Xu ) [446522]
- [CRYPTO] tcrypt: Change the usage of the test vectors (Herbert Xu ) [446522]
- [CRYPTO] tcrypt: Shrink speed templates (Herbert Xu ) [446522]
- [CRYPTO] tcrypt: Group common speed templates (Herbert Xu ) [446522]
- [fs] jdb: fix error handling for checkpoint I/O (Hideo AOKI ) [439581]
- [fs] ext3: add checks for errors from jbd (Hideo AOKI ) [439581]
- [fs] jbd: fix commit code to properly abort journal (Hideo AOKI ) [439581]
- [fs] jbd: don't dirty original metadata buffer on abort (Hideo AOKI ) [439581]
- [fs] jdb: abort when failed to log metadata buffers (Hideo AOKI ) [439581]
- [fs] ext3: don't read inode block if buf has write error (Hideo AOKI ) [439581]
- [fs] jdb: add missing error checks for file data writes (Hideo AOKI ) [439581]
- [net] tun: add IFF_VNET_HDR, TUNGETFEATURES, TUNGETIFF (Herbert Xu ) [459719]
- [acpi] increase deep idle state residency on platforms-2 (Matthew Garrett ) [455449]
- [acpi] increase deep idle state residency on platforms (Matthew Garrett ) [455447]
- [acpi] cpufreq: update to upstream for RHEL-5.3 (Matthew Garrett ) [449787]
- [acpi] thinkpad_acpi: update to upstream for RHEL-5.3 (Matthew Garrett ) [457101]
- [xen] fix crash on IRQ exhaustion and increase NR_IRQS (Bill Burns ) [442736]
- [ide] enable DRAC4 (John Feeney ) [459197]
- [md] move include files to include/linux for exposure (Jonathan Brassow ) [429337]
- [md] expose dm.h macros (Jonathan Brassow ) [429337]
- [md] remove internal mod refs fields from interface (Jonathan Brassow ) [429337]
- [md] dm-log: move register functions (Jonathan Brassow ) [429337]
- [md] dm-log: clean interface (Jonathan Brassow ) [429337]
- [md] clean up the dm-io interface (Jonathan Brassow ) [429337]
- [md] dm-log: move dirty log into separate module (Jonathan Brassow ) [429337]
- [md] device-mapper interface exposure (Jonathan Brassow ) [429337]
- [cifs] enable SPNEGO and DFS upcalls in config-generic (Jeff Layton ) [453462]
- [fs] cifs: latest upstream for RHEL-5.3 (Jeff Layton ) [453462 431868 443395 445522 446142 447400]
- [fs] introduce a function to register iget failure (Jeff Layton ) [453462]
- [fs] proc: fix ->open'less usage due to ->proc_fops flip (Jeff Layton ) [453462]
- [security] key: fix lockdep warning when revoking auth (Jeff Layton ) [453462]
- [security] key: increase payload size when instantiating (Jeff Layton ) [453462]
- [fs] call flush_disk after detecting an online resize (Jeff Moyer ) [444964]
- [fs] add flush_disk to flush out common buffer cache (Jeff Moyer ) [444964]
- [fs] check for device resize when rescanning partitions (Jeff Moyer ) [444964]
- [fs] adjust block device size after an online resize (Jeff Moyer ) [444964]
- [fs] wrapper for lower-level revalidate_disk routines (Jeff Moyer ) [444964]
- [scsi] sd: revalidate_disk wrapper (Jeff Moyer ) [444964]
- [xen] virtio: add PV network and block drivers for KVM (Mark McLoughlin ) [446214]
- [misc] remove MAX_ARG_PAGES limit: var length argument (Jerome Marchand ) [443659]
- [misc] remove MAX_ARG_PAGES limit: rework execve audit (Jerome Marchand ) [443659]
- [misc] remove MAX_ARG_PAGES limit: independent stack top (Jerome Marchand ) [443659]
- [ia64] kprobes: support kprobe-booster (Masami Hiramatsu ) [438733]
- [audit] fix compile when CONFIG_AUDITSYSCALL is disabled (Prarit Bhargava ) [452577]
- [nfs] v4: handle old format exports gracefully (Brad Peters ) [427424]
- [xen] x86: fix building with max_phys_cpus=128 (Bill Burns ) [447958]
- [xen] Intel EPT 2MB patch (Bill Burns ) [426679]
- [xen] Intel EPT Migration patch (Bill Burns ) [426679]
- [xen] Intel EPT Patch (Bill Burns ) [426679]
- [xen] Intel pre EPT Patch (Bill Burns ) [426679]
- [xen] AMD 2MB backing pages support (Bhavna Sarathy ) [251980]

* Thu Sep 11 2008 Don Zickus <dzickus@redhat.com> [2.6.18-111.el5]
- [ia64] kabi: remove sn symbols from whitelist (Jon Masters ) [455308]
- [net] bnx2x: update to upstream version 1.45.21 (Andy Gospodarek ) [442026]
- [net] cxgb3: updates and lro fixes (Andy Gospodarek ) [441959]
- [net] niu: enable support for Sun Neptune cards (Andy Gospodarek ) [441416]
- [scsi] scsi_host_lookup: error returns and NULL pointers (Tom Coughlan ) [460195]
- [scsi] scsi_netlink: transport/LLD receive/event support (Tom Coughlan ) [460195]
- [misc] install correct kernel chksum file for FIPS140-2 (Chris Lalancette ) [444632]
- [net] ixgbe: update to version 1.3.18-k4 (Andy Gospodarek ) [436044]
- [dlm] fix address compare (David Teigland ) [459585]
- [net] bonding: fix locking in 802.3ad mode (Andy Gospodarek ) [457300]
- [openib] OFED-1.3.2-pre update (Doug Ledford ) [439565 443476 453110 458886 459052 458375 459052 230035 460623]
- [md] dm snapshot: use per device mempools (Mikulas Patocka ) [460846]
- [md] dm kcopyd: private mempool (Mikulas Patocka ) [460845]
- [md] deadlock with nested LVMs (Mikulas Patocka ) [460845]
- [net] skge: don't clear MC state on link down (Andy Gospodarek ) [406051]
- [net] sky2: re-enable 88E8056 for most motherboards (Andy Gospodarek ) [420961]
- [net] update myri10ge 10Gbs ethernet driver (Flavio Leitner ) [357191]
- [net] bnx2: update to upstream version 1.7.9 (Andy Gospodarek ) [441964]
- [net] e1000e: update to upstream version 0.3.3.3-k2 (Andy Gospodarek ) [436045]
- [net] tg3: update to upstream version 3.93 (Andy Gospodarek ) [441975 440958 436686]
- [net] igb: update to upstream version 1.2.45-k2 (Andy Gospodarek ) [436040]
- [misc] intel: new SATA, USB, HD Audio and I2C(SMBUS) ids (John Villalovos ) [433538]
- [net] bnx2x: update to upstream version 1.45.20 (Andy Gospodarek ) [442026]
- [net] ixgb: hardware support and other upstream fixes (Andy Gospodarek ) [441609]
- [x86] amd oprofile: support instruction based sampling (Bhavna Sarathy ) [438385]
- [scsi] cciss: support for sg_ioctl (Tomas Henzl ) [250483]
- [scsi] cciss: support for new controllers (Tomas Henzl ) [437497 447427]
- [net] pppoe: check packet length on all receive paths (Jiri Pirko ) [457013]
- [scsi] iscsi: fix nop timeout detection (mchristi@redhat.com ) [453969]
- [scsi] lpfc: update to version 8.2.0.30 (Tom Coughlan ) [441746]
- [md] fix handling of sense buffer in eh commands (Doug Ledford ) [441640]
- [md] fix error propogation in raid arrays (Doug Ledford ) [430984]
- [md] dm: reject barrier requests (Milan Broz ) [458936]
- [scsi] 3w-9xxx: update to version 2.26.08.003 (Tomas Henzl ) [451946]
- [scsi] 3w-xxxx: update to version 1.26.03.000 (Tomas Henzl ) [451945]
- [scsi] megaraid_sas: update to version 4.01-rh1 (Tomas Henzl ) [442913]
- [md] dm snapshot: fix race during exception creation (Mikulas Patocka ) [459337]
- [md] dm-snapshots: race condition and data corruption (Mikulas Patocka ) [459337]
- [md] dm crypt: use cond_resched (Milan Broz ) [459095]
- [md] dm mpath: fix bugs in error paths (Milan Broz ) [459092]
- [mm] fix support for fast get user pages (Ed Pollard ) [447649]
- [xen] ia64 PV: config file changes to add support (Don Dutile ) [442991]
- [xen] ia64 PV: Kconfig additions (Don Dutile ) [442991]
- [xen] ia64 PV: Makefile changes (Don Dutile ) [442991]
- [xen] ia64 PV: shared used header file changes (Don Dutile ) [442991]
- [IA64] Correct pernodesize calculation (George Beshers ) [455308]
- [IA64] Fix large MCA bootmem allocation (George Beshers ) [455308]
- [IA64] Disable/re-enable CPE interrupts on Altix (George Beshers ) [455308]
- [IA64] Don't set psr.ic and psr.i simultaneously (George Beshers ) [455308]
- [IA64] Support multiple CPUs going through OS_MCA (George Beshers ) [455308]
- [IA64] Remove needless delay in MCA rendezvous (George Beshers ) [455308]
- [IA64] Clean up CPE handler registration (George Beshers ) [455308]
- [IA64] CMC/CPE: Reverse fetching log and checking poll (George Beshers ) [455308]
- [IA64] Force error to surface in nofault code (George Beshers ) [455308]
- [IA64] Fix Altix BTE error return status (George Beshers ) [455308]
- [IA64] BTE error timer fix (George Beshers ) [455308]
- [IA64] Update processor_info features (George Beshers ) [455308]
- [IA64] More Itanium PAL spec updates (George Beshers ) [455308]
- [IA64] Add se bit to Processor State Parameter structure (George Beshers ) [455308]
- [IA64] Add dp bit to cache and bus check structs (George Beshers ) [455308]
- [IA64] PAL calls need physical mode, stacked (George Beshers ) [455308]
- [IA64] Cache error recovery (George Beshers ) [455308]
- [IA64] handle TLB errors from duplicate itr.d dropins (George Beshers ) [455308]
- [IA64] MCA recovery: Montecito support (George Beshers ) [455308]

* Tue Sep 09 2008 Don Zickus <dzickus@redhat.com> [2.6.18-110.el5]
- [x86_64] use strncmp for memmap=exactmap boot argument (Prarit Bhargava ) [450244]
- [wireless] compiler warning fixes for mac80211 update (John W. Linville ) [438391]
- [serial] 8250: support for DTR/DSR hardware flow control (Aristeu Rozanski ) [445215]
- [tty] add termiox support (Aristeu Rozanski ) [445211]
- [vt] add shutdown method (Aristeu Rozanski ) [239604]
- [tty] add shutdown method (Aristeu Rozanski ) [239604]
- [tty] cleanup release_mem (Aristeu Rozanski ) [239604]
- [mm] keep pagefault from happening under page lock (Josef Bacik ) [445433]
- [wireless] iwlwifi: post-2.6.27-rc3 to support iwl5x00 (John W. Linville ) [438388]
- [net] random32: seeding improvement (Jiri Pirko ) [458019]
- [usb] work around ISO transfers in SB700 (Pete Zaitcev ) [457723]
- [x86_64] AMD 8-socket APICID patches (Prarit Bhargava ) [459813]
- [misc] make printk more robust against kexec shutdowns (Neil Horman ) [458368]
- [fs] ext4: backport to rhel5.3 interfaces (Eric Sandeen ) [458718]
- [fs] ext4: Kconfig/Makefile/config glue (Eric Sandeen ) [458718]
- [fs] ext4: fixes from upstream pending patch queue (Eric Sandeen ) [458718]
- [fs] ext4: revert delalloc upstream mods (Eric Sandeen ) [458718]
- [fs] ext4: 2.6.27-rc3 upstream codebase (Eric Sandeen ) [458718]
- [fs] ext4: new s390 bitops (Eric Sandeen ) [459436]
- [usb] wacom: add support for Cintiq 20WSX (Aristeu Rozanski ) [248903]
- [usb] wacom: add support for Intuos3 4x6 (Aristeu Rozanski ) [370471]
- [usb] wacom: fix maximum distance values (Aristeu Rozanski ) [248903]
- [x86] hpet: consolidate assignment of hpet_period (Brian Maly ) [435726]
- [openib] lost interrupt after LPAR to LPAR communication (Brad Peters ) [457838]
- [firmware] fix ibft offset calculation (mchristi@redhat.com ) [444776]
- [block] performance fix for too many physical devices (Mikulas Patocka ) [459527]
- [ide] Fix issue when appending data on an existing DVD (Mauro Carvalho Chehab ) [457025]
- [misc] fix kernel builds on modern userland (Matthew Garrett ) [461540]
- [x86_64] AMD IOMMU driver support (Bhavna Sarathy ) [251970]
- [x86_64] GART iommu alignment fixes (Prarit Bhargava ) [455813]
- [firewire] latest upstream snapshot for RHEL-5.3 (Jay Fenlason ) [449520 430300 429950 429951]
- [net] ipv6: configurable address selection policy table (Neil Horman ) [446063]
- [fs] relayfs: support larger on-memory buffer (Masami Hiramatsu ) [439269]
- [xen] ia64: speed up hypercall for guest domain creation (Tetsu Yamamoto ) [456171]
- [xen] make last processed event channel a per-cpu var (Tetsu Yamamoto ) [456171]
- [xen] process event channel notifications in round-robin (Tetsu Yamamoto ) [456171]
- [xen] use unlocked_ioctl in evtchn, gntdev and privcmd (Tetsu Yamamoto ) [456171]
- [xen] disallow nested event delivery (Tetsu Yamamoto ) [456171]
- [ppc64] spu: add cpufreq governor (Ed Pollard ) [442410]
- [misc] cleanup header warnings and enable header check (Don Zickus ) [458360]
- [mm] NUMA: over-committing memory compiler warnings (Larry Woodman ) [457264]
- [misc] mmtimer: fixes for high resolution timers (George Beshers ) [442186]
- [x86_64] xen: local DOS due to NT bit leakage (Eugene Teo ) [457722] {CVE-2006-5755}
- [xen] ia64: mark resource list functions __devinit (Tetsu Yamamoto ) [430219]
- [xen] ia64: issue ioremap HC in pci_acpi_scan_root (Tetsu Yamamoto ) [430219]
- [xen] ia64: revert paravirt to ioremap /proc/pci (Tetsu Yamamoto ) [430219]
- [xen] ia64: disable paravirt to remap /dev/mem (Tetsu Yamamoto ) [430219]
- [x86_64] kprobe: kprobe-booster and return probe-booster (Masami Hiramatsu ) [438725]
- [xen] NUMA: extend physinfo sysctl to export topo info (Tetsu Yamamoto ) [454711]
- [xen] ia64: kludge for XEN_GUEST_HANDLE_64 (Tetsu Yamamoto ) [454711]
- [xen] ia64: NUMA support (Tetsu Yamamoto ) [454711]
- [misc] pipe support to /proc/sys/net/core_pattern (Neil Horman ) [410871]
- [xen] ia64: fix and cleanup move to psr (Tetsu Yamamoto ) [447453]
- [xen] ia64: turn off psr.i after PAL_HALT_LIGHT (Tetsu Yamamoto ) [447453]
- [xen] ia64: fix ia64_leave_kernel (Tetsu Yamamoto ) [447453]
- [xen] page scrub: serialise softirq with a new lock (Tetsu Yamamoto ) [456171]
- [xen] serialize scrubbing pages (Tetsu Yamamoto ) [456171]
- [xen] ia64: don't warn for EOI-ing edge triggered intr (Tetsu Yamamoto ) [430219]
- [xen] ia64: remove regNaT fault message (Tetsu Yamamoto ) [430219]
- [xen] ia64: suppress warning of __assign_domain_page (Tetsu Yamamoto ) [430219]
- [xen] ia64: remove annoying log message (Tetsu Yamamoto ) [430219]
- [xen] ia64: quieter Xen boot (Tetsu Yamamoto ) [430219]
- [xen] ia64: quiet lookup_domain_mpa when domain is dying (Tetsu Yamamoto ) [430219]
- [xen] ia64: fix XEN_SYSCTL_physinfo to handle NUMA info (Tetsu Yamamoto ) [454711]
- [xen] ia64: fixup physinfo (Tetsu Yamamoto ) [454711]

* Sun Sep 07 2008 Don Zickus <dzickus@redhat.com> [2.6.18-109.el5]
- [misc] cpufreq: fix format string bug (Vitaly Mayatskikh ) [459460]
- [x86_64] perfctr: dont use CCCR_OVF_PMI1 on Pentium 4 Ds (Aristeu Rozanski ) [447618]
- [wireless] iwlwifi: fix busted tkip encryption (John W. Linville ) [438388]
- [wireless] ath5k: fixup Kconfig mess from update (John W. Linville ) [445578]
- [fs] cifs: fix O_APPEND on directio mounts (Jeff Layton ) [460063]
- [ia64] oprofile: recognize Montvale cpu as Itanium2 (Dave Anderson ) [452588]
- [block] aoe: use use bio->bi_idx to avoid panic (Tom Coughlan ) [440506]
- [x86] make bare-metal oprofile recognize other platforms (Markus Armbruster ) [458441]
- [scsi] areca: update for RHEL-5.3 (Tomas Henzl ) [436068]
- [sata] prep work for rhel5.3 (David Milburn ) [439247 445727 450962 451586 455445]
- [sata] update driver to 2.6.26-rc5 (David Milburn ) [439247 442906 445727 450962 451586 455445 459197]
- [openib] race between QP async handler and destroy_qp (Brad Peters ) [446109]
- [mm] don't use large pages to map the first 2/4MB of mem (Larry Woodman ) [455504]
- [mm] holdoffs in refresh_cpu_vm_stats using latency test (George Beshers ) [447654]
- [ppc64] cell spufs: fix HugeTLB (Brad Peters ) [439483]
- [ppc64] cell spufs: update with post 2.6.25 patches (Brad Peters ) [439483]
- [xen] ia64 oprofile: recognize Montvale cpu as Itanium2 (Dave Anderson ) [452588]
- [xen] x86: make xenoprof recognize other platforms (Markus Armbruster ) [458441]

* Wed Sep 03 2008 Don Zickus <dzickus@redhat.com> [2.6.18-108.el5]
- [net] NetXen: remove performance optimization fix (Tony Camuso ) [457958]
- [net] NetXen: update to upstream 2.6.27 (tcamuso@redhat.com ) [457958]
- [net] NetXen: fixes from upstream 2.6.27 (tcamuso@redhat.com ) [457958]
- [net] NetXen: cleanups from upstream 2.6.27 (tcamuso@redhat.com ) [457958]
- [fs] anon_inodes implementation (Eduardo Habkost ) [459835]
- [x86] PCI domain support (Jeff Garzik ) [228290]
- [net] udp: possible recursive locking (Hideo AOKI ) [458909]
- [gfs2] multiple writer performance issue (Abhijith Das ) [459738]
- [alsa] asoc: double free and mem leak in i2c codec (Jaroslav Kysela ) [460103]
- [net] ibmveth: cluster membership problems (Brad Peters ) [460379]
- [net] ipv6: drop outside of box loopback address packets (Neil Horman ) [459556]
- [net] dccp_setsockopt_change integer overflow (Vitaly Mayatskikh ) [459235] {CVE-2008-3276}
- [x86] execute stack overflow warning on interrupt stack (Michal Schmidt ) [459810]
- [ppc] export LPAR CPU utilization stats for use by hv (Brad Peters ) [439516]
- [acpi] error attaching device data (peterm@redhat.com ) [459670]
- [md] fix crashes in iterate_rdev (Doug Ledford ) [455471]
- [utrace] signal interception breaks systemtap uprobes (Roland McGrath ) [459786]
- [misc] markers and tracepoints: config patch (jbaron@redhat.com ) [329821]
- [misc] markers and tracepoints: kabi fix-up patch (jbaron@redhat.com ) [329821]
- [misc] markers and tracepoints: probes (jbaron@redhat.com ) [329821]
- [misc] markers and tracepoints: sched patch (jbaron@redhat.com ) [329821]
- [misc] markers and tracepoints: irq patch (jbaron@redhat.com ) [329821]
- [misc] markers and tracepoints: create Module.markers (jbaron@redhat.com ) [329821]
- [misc] markers and tracepoints: markers docs (jbaron@redhat.com ) [329821]
- [misc] markers and tracepoints: markers samples (jbaron@redhat.com ) [329821]
- [misc] markers and tracepoints: markers (jbaron@redhat.com ) [329821]
- [misc] markers and tracepoints: tracepoint samples (jbaron@redhat.com ) [329821]
- [misc] markers and tracepoints: tracepoints (jbaron@redhat.com ) [329821]
- [misc] markers and tracepoints: samples patch (jbaron@redhat.com ) [329821]
- [misc] markers and tracepoints: rcu-read patch (jbaron@redhat.com ) [329821]
- [x86] nmi: fix disable and enable _timer_nmi_watchdog (Aristeu Rozanski ) [447618]
- [x86] nmi: disable LAPIC/IO APIC on unknown_nmi_panic (Aristeu Rozanski ) [447618]
- [x86] nmi: use lapic_adjust_nmi_hz (Aristeu Rozanski ) [447618]
- [x86] nmi: update check_nmi_watchdog (Aristeu Rozanski ) [447618]
- [x86] nmi: update reserve_lapic_nmi (Aristeu Rozanski ) [447618]
- [x86] nmi: use setup/stop routines in suspend/resume (Aristeu Rozanski ) [447618]
- [x86] nmi: change nmi_active usage (Aristeu Rozanski ) [447618]
- [x86] nmi: update nmi_watchdog_tick (Aristeu Rozanski ) [447618]
- [x86] nmi: introduce do_nmi_callback (Aristeu Rozanski ) [447618]
- [x86] nmi: introduce per-cpu wd_enabled (Aristeu Rozanski ) [447618]
- [x86] nmi: add perfctr infrastructure (Aristeu Rozanski ) [447618]
- [x86_64] nmi: add missing prototypes in xen headers (Aristeu Rozanski ) [447618]
- [x86_64] nmi: kill disable_irq calls (Aristeu Rozanski ) [447618]
- [x86_64] nmi: disable LAPIC/IO APIC on unknown_nmi_panic (Aristeu Rozanski ) [447618]
- [x86_64] nmi: use perfctr functions for probing (Aristeu Rozanski ) [447618]
- [x86_64] nmi: update check_nmi_watchdog (Aristeu Rozanski ) [447618]
- [x86_64] nmi: update reserve_lapic_nmi (Aristeu Rozanski ) [447618]
- [x86_64] nmi: use new setup/stop routines in suspend/resume (Aristeu Rozanski ) [447618]
- [x86_64] nmi: change nmi_active usage (Aristeu Rozanski ) [447618]
- [x86_64] nmi: update nmi_watchdog_tick (Aristeu Rozanski ) [447618]
- [x86_64] nmi: setup apic to handle both IO APIC and LAPIC (Aristeu Rozanski ) [447618]
- [x86_64] nmi: introduce do_nmi_callback (Aristeu Rozanski ) [447618]
- [x86_64] nmi: introduce per-cpu wd_enabled (Aristeu Rozanski ) [447618]
- [x86_64] nmi: add perfctr infrastructure (Aristeu Rozanski ) [447618]
- [mm] drain_node_page: drain pages in batch units (George Beshers ) [442179]
- [mm] optimize ZERO_PAGE in 'get_user_pages' and fix XIP (Anton Arapov ) [452668] {CVE-2008-2372}
- [x86_64] UEFI code support (Brian Maly ) [253295]

* Thu Aug 28 2008 Don Zickus <dzickus@redhat.com> [2.6.18-107.el5]
-  [scsi] mptscsi: check for null device in error handler (Doug Ledford ) [441832]
- [openib] ehca: local CA ACK delay has an invalid value (Brad Peters ) [458378]
- [gfs2] fix metafs (Abhijith Das ) [457798]
- [sound] HDMI Audio: new PCI device ID (Bhavna Sarathy ) [459221]
- [s390] cio: memory leak when ccw devices are discarded (Hans-Joachim Picht ) [459495]
- [openib] ehca: handle two completions for one work req (Brad Peters ) [459142]
- [scsi] cciss: possible race condition during init (Ivan Vecera ) [455663]
- [wireless] rtl818x: add driver from 2.6.26 (John W. Linville ) [448764]
- [wireless] rt2x00: add driver from 2.6.26 (John W. Linville ) [448763]
- [wireless] ath5k: add driver from 2.6.26 (John W. Linville ) [445578]
- [wireless] iwlwifi update to version from 2.6.26 (John W. Linville ) [438395]
- [wireless] mac80211 update to version from 2.6.26 (John W. Linville ) [438391 438464 446076]
- [wireless] infrastructure changes for mac80211 update (John W. Linville ) [438391]
- [xen] xennet: coordinate ARP with backend network status (Herbert Xu ) [458934]
- [x86] oprofile: enable additional perf counters (Markus Armbruster ) [426096]
- [wireless] update zd1211rw to last non-mac80211 version (John W. Linville ) [448762]
- [wireless] update bcm43xx driver to 2.6.25 (John W. Linville ) [448762]
- [wireless] update ipw2x00 driver to 2.6.25 (John W. Linville ) [448762]
- [wireless] update ieee80211 to 2.6.25 (John W. Linville ) [448762]
- [xen] hv: support up to 128 cpus (Bill Burns ) [447958]
- [gfs2] rm on multiple nodes causes panic (Bob Peterson ) [458289]
- [gfs2] d_rwdirectempty fails with short read (Benjamin Marzinski ) [456453]
- [sound] snd_seq_oss_synth_make_info info leak (Eugene Teo ) [458001] {CVE-2008-3272}
- Revert: [mm] add support for fast get user pages (Ed Pollard ) [447649]
- [xen] fix GDT allocation for 128 CPUs (Bill Burns ) [447958]
- [xen] fix building with max_phys_cpus=128 (Bill Burns ) [447958]
- [xen] limit dom0 to 32GB by default (Rik van Riel ) [453467]
- [xen] automatically make heap larger on large mem system (Rik van Riel ) [453467]

* Tue Aug 26 2008 Don Zickus <dzickus@redhat.com> [2.6.18-106.el5]
- [x86_64] resume from s3 in text mode with >4GB of mem (Matthew Garrett ) [452961]
- [x86] kdump: calgary iommu: use boot kernel's TCE tables (Tom Coughlan ) [239272]
- [net] neigh_destroy: call destructor before unloading (Brad Peters ) [449161]
- [usb] removing bus with an open file causes an oops (Pete Zaitcev ) [450786]
- [nfs] missing nfs_fattr_init in nfsv3 acl functions (Jeff Layton ) [453711]
- [xen] x86: fix endless loop when GPF (Chris Lalancette ) [457093]
- [dlm] user.c input validation fixes (David Teigland ) [458760]
- [serial] support for Digi PCI-E 4-8port Async IO adapter (Brad Peters ) [439443]
- [cpufreq] acpi: boot crash due to _PSD return-by-ref (John Villalovos ) [428909]
- [x86] io_apic: check timer with irq off (Brian Maly ) [432407]
- [nfs] v4: don't reuse expired nfs4_state_owner structs (Jeff Layton ) [441884]
- [nfs] v4: credential ref leak in nfs4_get_state_owner (Jeff Layton ) [441884]
- [xen] PVFB probe & suspend fixes fix (Markus Armbruster ) [459107]
- [x86] acpi: prevent resources from corrupting memory (Prarit Bhargava ) [458988]
- [mm] add support for fast get user pages (Ed Pollard ) [447649]
- [ipmi] control BMC device ordering (peterm@redhat.com ) [430157]
- [net] pppoe: fix skb_unshare_check call position (Jiri Pirko ) [459062]
-  [net] ipv6: use timer pending to fix bridge ref count (Jiri Pirko ) [457006]
- [nfs] v4: Poll aggressively when handling NFS4ERR_DELAY (Jeff Layton ) [441884]
- [net] ixgbe: fix EEH recovery time (Brad Peters ) [457466]
- [net] pppoe: unshare skb before anything else (Jiri Pirko ) [457018]
- [ppc64] EEH: facilitate vendor driver recovery (Brad Peters ) [457253]
- [ia64] fix to check module_free parameter (Masami Hiramatsu ) [457961]
- [video] make V4L2 less verbose (Mauro Carvalho Chehab ) [455230]
- [autofs4] remove unused ioctls (Ian Kent ) [452139]
- [autofs4] reorganize expire pending wait function calls (Ian Kent ) [452139]
- [autofs4] fix direct mount pending expire race (Ian Kent ) [452139]
- [autofs4] fix indirect mount pending expire race (Ian Kent ) [452139]
- [autofs4] fix pending checks (Ian Kent ) [452139]
- [autofs4] cleanup redundant readdir code (Ian Kent ) [452139]
- [autofs4] keep most direct and indirect dentrys positive (Ian Kent ) [452139]
- [autofs4] fix waitq memory leak (Ian Kent ) [452139]
- [autofs4] check communication pipe is valid for write (Ian Kent ) [452139]
- [autofs4] fix waitq locking (Ian Kent ) [452139]
- [autofs4] fix pending mount race (Ian Kent ) [452139]
- [autofs4] use struct qstr in waitq.c (Ian Kent ) [452139]
- [autofs4] use lookup intent flags to trigger mounts (Ian Kent ) [448869]
- [autofs4] hold directory mutex if called in oz_mode (Ian Kent ) [458749]
- [autofs4] use rehash list for lookups (Ian Kent ) [458749]
- [autofs4] don't make expiring dentry negative (Ian Kent ) [458749]
- [autofs4] fix mntput, dput order bug (Ian Kent ) [452139]
- [autofs4] bad return from root.c:try_to_fill_dentry (Ian Kent ) [452139]
- [autofs4] sparse warn in waitq.c:autofs4_expire_indirect (Ian Kent ) [452139]
- [autofs4] check for invalid dentry in getpath (Ian Kent ) [452139]
- [misc] create a kernel checksum file per FIPS140-2 (Don Zickus ) [444632]
- [net] h323: Fix panic in conntrack module (Thomas Graf ) [433661]
-  [misc] NULL pointer dereference in kobject_get_path (Jiri Pirko ) [455460]
- [audit] new filter type, AUDIT_FILETYPE (Alexander Viro ) [446707]
-  [ppc64] missed hw breakpoints across multiple threads (Brad Peters ) [444076]
- [net] race between neigh_timer_handler and neigh_update (Brad Peters ) [440555]
- [security] NULL ptr dereference in __vm_enough_memory (Jerome Marchand ) [443659]
- [ppc64] cell: spufs update for RHEL-5.3 (Brad Peters ) [439483]
- [misc] null pointer dereference in register_kretprobe (Jerome Marchand ) [452308]
- [alsa] HDA: update to 2008-07-22 (Jaroslav Kysela ) [456215]
- [ia64] xen: handle ipi case IA64_TIMER_VECTOR (Luming Yu ) [451745]
- [misc] batch kprobe register/unregister (Jiri Pirko ) [437579]
- [ia64] add gate.lds to Documentation/dontdiff (Prarit Bhargava ) [449948]
- [xen] fix netloop restriction (Bill Burns ) [358281]
- [nfs] revert to sync writes when background write errors (Jeff Layton ) [438423]
- [ia64] kdump: implement greater than 4G mem restriction (Doug Chapman ) [446188]
- [nfs] clean up short packet handling for NFSv4 readdir (Jeff Layton ) [428720]
- [nfs] clean up short packet handling for NFSv2 readdir (Jeff Layton ) [428720]
- [nfs] clean up short packet handling for NFSv3 readdir (Jeff Layton ) [428720]

* Thu Aug 14 2008 Don Zickus <dzickus@redhat.com> [2.6.18-105.el5]
- [misc] pnp: increase number of devices (Prarit Bhargava ) [445590]
- [ppc] PERR/SERR disabled after EEH error recovery (Brad Peters ) [457468]
- [ppc] eHEA: update from version 0076-05 to 0091-00 (Brad Peters ) [442409]
- [net] modifies inet_lro for RHEL (Brad Peters ) [442409]
- [net] adds inet_lro module (Brad Peters ) [442409]
- [ppc] adds crashdump shutdown hooks (Brad Peters ) [442409]
- [ppc] xmon: setjmp/longjmp code generically available (Brad Peters ) [442409]
- [xen] PV:  config file changes (Don Dutile ) [442991]
- [xen] PV: Makefile and Kconfig additions (Don Dutile ) [442991]
- [xen] PV: add subsystem (Don Dutile ) [442991]
- [xen] PV: shared used header file changes (Don Dutile ) [442991]
- [xen] PV: shared use of xenbus, netfront, blkfront (Don Dutile ) [442991]
- [fs] backport zero_user_segments and friends (Eric Sandeen ) [449668]
- [fs] backport list_first_entry helper (Eric Sandeen ) [449668]
- [ia64] fix boot failure on ia64/sn2 (Luming Yu ) [451745]
- [ia64] move SAL_CACHE_FLUSH check later in boot (Luming Yu ) [451745]
- [ia64] use platform_send_ipi in check_sal_cache_flush (Luming Yu ) [451745]
- [xen] avoid dom0 hang when tearing down domains (Chris Lalancette ) [347161]
- [xen] ia64: SMP-unsafe with XENMEM_add_to_physmap on HVM (Tetsu Yamamoto ) [457137]

* Tue Aug 12 2008 Don Zickus <dzickus@redhat.com> [2.6.18-104.el5]
- [crypto] IPsec memory leak (Vitaly Mayatskikh ) [455238]
- [ppc] edac: add support for Cell processor (Brad Peters ) [439507]
- [ppc] edac: add pre-req support for Cell processor (Brad Peters ) [439507]
- [scsi] DLPAR remove operation fails on LSI SCSI adapter (Brad Peters ) [457852]
- [net] bridge: eliminate delay on carrier up (Herbert Xu ) [453526]
-  [mm] tmpfs: restore missing clear_highpage (Eugene Teo ) [426083]{CVE-2007-6417}
- [scsi] aic94xx: update to 2.6.25 (Ed Pollard ) [439573]
- [fs] dio: lock refcount operations (Jeff Moyer ) [455750]
- [fs] vfs: fix lookup on deleted directory (Eugene Teo ) [457866]{CVE-2008-3275}
- [fs] jbd: fix races that lead to EIO for O_DIRECT (Brad Peters ) [446599]
- [fs] add percpu_counter_add & _sub (Eric Sandeen ) [443896]
- [xen] event channel lock and barrier (Markus Armbruster ) [457086]
- [ppc] adds DSCR support in sysfs (Brad Peters ) [439567]
- [ppc] oprofile: wrong cpu_type returned (Brad Peters ) [441539]
- [s390] utrace: PTRACE_POKEUSR_AREA corrupts ACR0 (Anton Arapov ) [431183]
- [pci] fix problems with msi interrupt management (Michal Schmidt ) [428696]
- [misc] fix wrong test in wait_task_stopped (Jerome Marchand ) [382211]
- [fs] ecryptfs: use page_alloc to get a page of memory (Eric Sandeen ) [457058]
- [misc]  serial: fix break handling for i82571 over LAN (Aristeu Rozanski ) [440018]
- [xen] blktap: expand for longer busids (Chris Lalancette ) [442723]
- [xen] fix blkfront to accept > 16 devices (Chris Lalancette ) [442723]
- [xen] expand SCSI majors in blkfront (Chris Lalancette ) [442077]
- [misc] core dump: remain dumpable (Jerome Marchand ) [437958]
- [fs] inotify: previous event should be last in list (Jeff Burke ) [453990]
- [block] Enhanced Partition Statistics: documentation (Jerome Marchand ) [224322]
- [block] Enhanced Partition Statistics: retain old stats (Jerome Marchand ) [224322]
- [block] Enhanced Partition Statistics: procfs (Jerome Marchand ) [224322]
- [block] Enhanced Partition Statistics: sysfs (Jerome Marchand ) [224322]
- [block] Enhanced Partition Statistics: cpqarray fix (Jerome Marchand ) [224322]
- [block] Enhanced Partition Statistics: cciss fix (Jerome Marchand ) [224322]
- [block] Enhanced Partition Statistics: aoe fix (Jerome Marchand ) [224322]
- [block] Enhanced Partition Statistics: update statistics (Jerome Marchand ) [224322]
- [block] Enhanced Partition Statistics: core statistics (Jerome Marchand ) [224322]
- [fs] add clear_nlink, drop_nlink (Eric Sandeen ) [443896]
- [fs] add buffer_submit_read and bh_uptodate_or_lock (Eric Sandeen ) [443896]
- [fs] noinline_for_stack attribute (Eric Sandeen ) [443896]
- [fs] i_version updates (Eric Sandeen ) [443896]
- [fs] add an ERR_CAST function (Eric Sandeen ) [443896]
- [fs] introduce is_owner_or_cap (Eric Sandeen ) [443896]
- [fs] add generic_find_next_le_bit (Eric Sandeen ) [443896]
- [fs] add le32_add_cpu and friends (Eric Sandeen ) [443896]
- [net] sctp: export needed data to implement RFC 3873 (Neil Horman ) [277111]
- [xen] x86: xenoprof enable additional perf counters (Markus Armbruster ) [426096]

* Thu Aug 07 2008 Don Zickus <dzickus@redhat.com> [2.6.18-103.el5]
- [fs] dio: use kzalloc to zero out struct dio (Jeff Moyer ) [439918]
- [x86] hugetlb: inconsistent get_user_pages (x86 piece) (Brad Peters ) [456449]
- [fs] fix softlockups when repeatedly dropping caches (Bryn M. Reeves ) [444961]
- [char] add hp-ilo driver (Tony Camuso ) [437212]
- [net] do liberal tracking for picked up connections (Anton Arapov ) [448328]
- [scsi] BusLogic: typedef bool to boolean for compiler (Chip Coldwell ) [445095]
- [misc] ioc4: fixes - pci_put_dev, printks, mem resource (Jonathan Lim ) [442424]

* Tue Aug 05 2008 Don Zickus <dzickus@redhat.com> [2.6.18-102.el5]
- [net] slow_start_after_idle influences cwnd validation (Thomas Graf ) [448918]
- [dlm] fix a couple of races (David Teigland ) [457569]
- [net] NetXen driver update to 3.4.18 (Ed Pollard ) [443619]
- [mm] NUMA: system is slow when over-committing memory (Larry Woodman ) [457264]
- [net] ixgbe: remove device ID for unsupported device (Andy Gospodarek ) [454910]
- [ppc] Event Queue overflow on eHCA adapters (Brad Peters ) [446713]
- [ppc] IOMMU Performance Enhancements (Brad Peters ) [439469]
- [ppc] RAS update for Cell (Brad Peters ) [313731]
- [ppc] fast little endian implementation for System p AVE (Brad Peters ) [439505]
- [net] proc: add unresolved discards stat to ndisc_cache (Neil Horman ) [456732]
- [x86_64] ia32: increase stack size (Larry Woodman ) [442331]
- [mm] fix PAE pmd_bad bootup warning (Larry Woodman ) [455434]
- [video] add uvcvideo module (Jay Fenlason ) [439899]
- [crypto] add tests for cipher types to self test module (Neil Horman ) [446514]
- [mm] fix debug printks in page_remove_rmap() (Larry Woodman ) [457458]
- [mm] fix /proc/sys/vm/lowmem_reserve_ratio (Larry Woodman ) [457471]
- [xen] add VPS sync read/write according to spec (Bill Burns ) [437096]
- [xen] use VPS service to take place of PAL call (Bill Burns ) [437096]
- [xen] enable serial console for new ia64 chip (Bill Burns ) [437096]

* Tue Jul 29 2008 Don Zickus <dzickus@redhat.com> [2.6.18-101.el5]
- [ipmi] restrict keyboard I/O port reservation (peterm@redhat.com ) [456300]
- [mm] xpmem: inhibit page swapping under heavy mem use (George Beshers ) [456574]
- [fs] vfs: wrong error code on interrupted close syscalls (Jeff Layton ) [455729]
- [misc] don't randomize when no randomize personality set (Bryn M. Reeves ) [444611]
- [ia64] holdoffs in sn_ack_irq when running latency tests (Jonathan Lim ) [447838]
- [xen] x86: new vcpu_op call to get physical CPU identity (Bhavana Nagendra ) [434548]
- [xen] HV: memory corruption with large number of cpus (Chris Lalancette ) [449945]
- [xen] save phys addr for crash utility (Bill Burns ) [443618]
- [xen] kexec: allocate correct memory reservation (Bill Burns ) [442661]

* Thu Jul 24 2008 Don Zickus <dzickus@redhat.com> [2.6.18-100.el5]
- [gfs2] glock dumping missing out some glocks (Steven Whitehouse ) [456334]
- [scsi] ibmvscsi: add tape device support (Brad Peters ) [439488]
- [misc] irq: reset stats when installing new handler (Eugene Teo ) [456218]
- [scsi] ibmvscsi: latest 5.3 fixes and enhancements (Brad Peters ) [439487]
- [selinux] prevent illegal selinux options when mounting (Eugene Teo ) [456052]
- [xen] remove blktap sysfs entries before shutdown (Chris Lalancette ) [250104]
- [xen] don't collide symbols with blktap (Chris Lalancette ) [250104]
- [xen] blktap: modify sysfs entries to match blkback (Chris Lalancette ) [250104]
- [xen] don't try to recreate sysfs entries (Chris Lalancette ) [250104]
- [xen] blktap: stats error cleanup (Chris Lalancette ) [250104]
- [xen] blktap: add statistics (Chris Lalancette ) [250104]
- [xen] rename blktap kernel threads to blktap.dom.blkname (Chris Lalancette ) [250104]
- [ia64] xen: incompatibility with HV and userspace tools (Tetsu Yamamoto ) [444589]
- [usb] add ids for WWAN cards (John Feeney ) [253137]
- [ia64] handle invalid ACPI SLIT table (Luming Yu ) [451591]
- [pci] mmconfig: use conf1 for access below 256 bytes (Tony Camuso ) [441615 251493]
- [pci] mmconfig: rm pci_legacy_ops and nommconf blacklist (Tony Camuso ) [441615 251493]
- [pci] mmconfig: remove pci_bios_fix_bus_scan_quirk (Tony Camuso ) [441615 251493]
- [fs] nlm: tear down RPC clients in nlm_shutdown_hosts (Jeff Layton ) [254195]
- [fs] nlm: don't reattempt GRANT_MSG with an inflight RPC (Jeff Layton ) [254195]
- [fs] nlm: canceled inflight GRANT_MSG shouldn't requeue (Jeff Layton ) [254195]
- [fs] potential race in mark_buffer_dirty (Mikulas Patocka ) [442577]

* Tue Jul 22 2008 Don Zickus <dzickus@redhat.com> [2.6.18-99.el5]
- [fs] lockd: nlmsvc_lookup_host called with f_sema held (Jeff Layton ) [453094]
- [x86] don't call MP_processor_info for disabled cpu (Prarit Bhargava ) [455425]
- [x86_64] don't call MP_processor_info for disabled cpu (Prarit Bhargava ) [455427]
- [x86] show apicid in /proc/cpuinfo (Prarit Bhargava ) [455424]
- [acpi] disable lapic timer on C2 states (John Villalovos ) [438409]
- [acpi] enable deep C states for idle efficiency (Matthew Garrett ) [443516]
- [fs] missing check before setting mount propagation (Eugene Teo ) [454393]
- [xen] pvfb: frontend mouse wheel support (Markus Armbruster ) [446235]
- [ppc] use ibm,slb-size from device tree (Brad Peters ) [432127]
- [mm] dio: fix cache invalidation after sync writes (Jeff Moyer ) [445674]
- [misc] fix UP compile in skcipher.h (Prarit Bhargava ) [453038]
- [ia64] softlock: prevent endless warnings in kdump (Neil Horman ) [453200]
- [net] s2io: fix documentation about intr_type (Michal Schmidt ) [450921]
- [net] make udp_encap_rcv use pskb_may_pull (Neil Horman ) [350281]
- [misc] fix compile when selinux is disabled (Prarit Bhargava ) [452535]
- [scsi] update aacraid to 1.1.5-2455 (Chip Coldwell ) [429862]
- [x86_64] ptrace: sign-extend orig_rax to 64 bits (Jerome Marchand ) [437882]
- [x86_64] ia32 syscall restart fix (Jerome Marchand ) [434998]
- [misc] optimize byte-swapping, fix -pedantic compile (Jarod Wilson ) [235699]
- [dm] snapshot: reduce default memory allocation (Milan Broz ) [436494]
- [dm] snapshot: fix chunksize sector conversion (Milan Broz ) [443627]
- [net] ip tunnel can't be bound to another device (Michal Schmidt ) [451196]
- [net] bnx2x: chip reset and port type fixes (Andy Gospodarek ) [441259]
- [audit] records sender of SIGUSR2 for userspace (Eric Paris ) [428277]
- [audit] deadlock under load and auditd takes a signal (Eric Paris ) [429941]
- [audit] send EOE audit record at end of syslog events (Eric Paris ) [428275]
- [x86] brk: fix RLIMIT_DATA check (Vitaly Mayatskikh ) [315681]
- [misc] fix ?!/!? inversions in spec file (Jarod Wilson ) [451008]
- [scsi] fix high I/O wait using 3w-9xxx (Tomas Henzl ) [444759]
- [net] ipv6: fix unbalanced ref count in ndisc_recv_ns (Neil Horman ) [450855]
- [fs] cifs: wait on kthread_stop before thread exits (Jeff Layton ) [444865]
- [net] fix the redirected packet if jiffies wraps (Ivan Vecera ) [445536]
- [nfs] pages of a memory mapped file get corrupted (Peter Staubach ) [435291]
- [net] sunrpc: memory corruption from dead rpc client (Jeff Layton ) [432867]
- [fs] debugfs: fix dentry reference count bug (Josef Bacik ) [445787]
- [acpi] remove processor module errors (John Feeney ) [228836]
- [fs] ext3: make fdatasync not sync metadata (Josef Bacik ) [445649]
- [pci] acpiphp_ibm: let ACPI determine _CID buffer size (Prarit Bhargava ) [428874]
- [fs] need process map reporting for swapped pages (Anton Arapov ) [443749]
- [misc] optional panic on softlockup warnings (Prarit Bhargava ) [445422]
- [net] sctp: support remote address table oid (Neil Horman ) [435110]
- [nfs] knfsd: revoke setuid/setgid when uid/gid changes (Jeff Layton ) [443043]
- [nfs] remove error field from nfs_readdir_descriptor_t (Jeff Layton ) [437479]

* Thu Jul 17 2008 Don Zickus <dzickus@redhat.com> [2.6.18-98.el5]
- [nfs] sunrpc: sleeping rpc_malloc might deadlock (Jeff Layton ) [451317]
- [gfs2] initial write performance very slow (Benjamin Marzinski ) [432826]
- [ia64] avoid unnecessary TLB flushes when allocating mem (Doug Chapman ) [435362]
- [gfs2] lock_dlm: deliver callbacks in the right order (Bob Peterson ) [447748]
- [sound] alsa: HDA driver update from upstream 2008-06-11 (Jaroslav Kysela ) [451007]
- [x86_64] xen: fix syscall return when tracing (Chris Lalancette ) [453394]
- [fs] ext3: lighten up resize transaction requirements (Eric Sandeen ) [425955]
- [xen] PVFB probe & suspend fixes (Markus Armbruster ) [434800]
- [nfs] ensure that options turn off attribute caching (Peter Staubach ) [450184]
- [x86_64] memmap flag results in bogus RAM map output (Prarit Bhargava ) [450244]
- [nfs] sunrpc: fix a race in rpciod_down (Jeff Layton ) [448754]
- [nfs] sunrpc: fix hang due to eventd deadlock (Jeff Layton ) [448754]
- [gfs2] d_doio stuck in readv waiting for pagelock (Bob Peterson ) [432057]
- [fs] ext3: fix lock inversion in direct io (Josef Bacik ) [439194]
- [fs] jbd: fix journal overflow issues (Josef Bacik ) [439193]
- [fs] jbd: fix typo in recovery code (Josef Bacik ) [447742]
- [openib] small ipoib packet can cause an oops (Doug Ledford ) [445731]
- [sched] domain range turnable params for wakeup_idle (Kei Tokunaga ) [426971]
- [edac] k8_edac: fix typo in user visible message (Aristeu Rozanski ) [446068]
- [net] ipv6: don't handle default routes specially (Neil Horman ) [426895 243526]
- [fs] ext3: unmount hang when quota-enabled goes error-RO (Eric Sandeen ) [429054]
- [net] ipv6: no addrconf for bonding slaves (Andy Gospodarek ) [236750]
- [misc] fix race in switch_uid and user signal accounting (Vince Worthington ) [441762 440830]
- [misc] /proc/pid/limits : fix duplicate array entries (Neil Horman ) [443522]
- [nfs] v4: fix ref count and signal for callback thread (Jeff Layton ) [423521]
- [mm] do not limit locked memory when using RLIM_INFINITY (Larry Woodman ) [442426]
- [xen] ia64: add srlz instruction to asm (Aron Griffis ) [440261]
- [nfs] fix transposed deltas in nfs v3 (Jeff Layton ) [437544]
- [x86_64] gettimeofday fixes for HPET, PMTimer, TSC (Prarit Bhargava ) [250708]
- [ia64] remove assembler warnings on head.S (Luming Yu ) [438230]
- [misc] allow hugepage allocation to use most of memory (Larry Woodman ) [438889]
- [edac] k8_edac: add option to report GART errors (Aristeu Rozanski ) [390601]
- [ia64] add TIF_RESTORE_SIGMASK and pselect/ppoll syscall (Luming Yu ) [206806]

* Tue Jul 15 2008 Don Zickus <dzickus@redhat.com> [2.6.18-97.el5]
-  [misc] signaling msgrvc() should not pass back error (Jiri Pirko ) [452533]
- [ia64] properly unregister legacy interrupts (Prarit Bhargava ) [445886]
- [s390] zfcp: status read locking race (Hans-Joachim Picht ) [451278]
- [s390] fix race with stack local wait_queue_head_t. (Hans-Joachim Picht ) [451279]
- [s390] cio: fix system hang with reserved DASD (Hans-Joachim Picht ) [451222]
- [s390] cio: fix unusable zfcp device after vary off/on (Hans-Joachim Picht ) [451223]
- [s390] cio: I/O error after cable pulls (Hans-Joachim Picht ) [451281]
- [s390] tape: race condition in tape block device driver (Hans-Joachim Picht ) [451277]
- [gfs2] cannot use fifo nodes (Steven Whitehouse ) [450276]
- [gfs2] bad subtraction in while-loop can cause panic (Bob Peterson ) [452004]
- [tux] crashes kernel under high load (Anton Arapov ) [448973]
- [dlm] move plock code from gfs2 (David Teigland ) [450138]
- [dlm] fix basts for granted CW waiting PR/CW (David Teigland ) [450137]
- [dlm] check for null in device_write (David Teigland ) [450136]
- [dlm] save master info after failed no-queue request (David Teigland ) [450135]
- [dlm] keep cached master rsbs during recovery (David Teigland ) [450133]
- [dlm] change error message to debug (David Teigland ) [450132]
- [dlm] fix possible use-after-free (David Teigland ) [450132]
- [dlm] limit dir lookup loop (David Teigland ) [450132]
- [dlm] reject normal unlock when lock waits on lookup (David Teigland ) [450132]
- [dlm] validate messages before processing (David Teigland ) [450132]
- [dlm] reject messages from non-members (David Teigland ) [450132]
- [dlm] call to confirm_master in receive_request_reply (David Teigland ) [450132]
- [dlm] recover locks waiting for overlap replies (David Teigland ) [450132]
- [dlm] clear ast_type when removing from astqueue (David Teigland ) [450132]
- [dlm] use fixed errno values in messages (David Teigland ) [450130]
- [dlm] swap bytes for rcom lock reply (David Teigland ) [450130]
- [dlm] align midcomms message buffer (David Teigland ) [450130]
- [dlm] use dlm prefix on alloc and free functions (David Teigland ) [450130]
- [s390] zfcp: memory handling for GID_PN (Hans-Joachim Picht ) [447727]
- [s390] zfcp: out-of-memory handling for status_read req (Hans-Joachim Picht ) [447726]
- [s390] zfcp: deadlock in slave_destroy handler (Hans-Joachim Picht ) [447329]
- [s390] dasd: fix timeout handling in interrupt handler (Hans-Joachim Picht ) [447316]
- [s390] zfcp: fix check for handles in abort handler (Hans-Joachim Picht ) [447331]
- [s390] aes_s390 decrypt may produce wrong results in CBC (Hans-Joachim Picht ) [446191]
- [s390x] CPU Node Affinity (Hans-Joachim Picht ) [447379]
- [gfs2] inode indirect buffer corruption (Bob Peterson ) [345401]
- [s390] cio: avoid machine check vs. not operational race (Hans-Joachim Picht ) [444082]
- [s390] qeth: avoid inconsistent lock state for inet6_dev (Hans-Joachim Picht ) [444077]
- [s390] qdio: missed inb. traffic with online FCP devices (Hans-Joachim Picht ) [444146]
- [s390] qeth: eddp skb buff problem running EDDP guestlan (Hans-Joachim Picht ) [444014]
- [s390] cio: kernel panic in cm_enable processing (Hans-Joachim Picht ) [442032]
- [fs] fix bad unlock_page in pip_to_file() error path (Larry Woodman ) [439917]
- [s390] zfcp: Enhanced Trace Facility (Hans-Joachim Picht ) [439482]
- [s390] dasd: add support for system information messages (Hans-Joachim Picht ) [439441]
- [s390] zcrypt: add support for large random numbers (Hans-Joachim Picht ) [439440]
- [s390] qeth: recovery problems with failing STARTLAN (Hans-Joachim Picht ) [440420]
- [s390] qdio: change in timeout handling during establish (Hans-Joachim Picht ) [440421]
- [s390] lcs: ccl-seq. numbers required for prot. 802.2 (Hans-Joachim Picht ) [440416]
- [s390] dasd: diff z/VM minidisks need a unique UID (Hans-Joachim Picht ) [440402]
- [s390] qeth: ccl-seq. numbers req for protocol 802.2 (Hans-Joachim Picht ) [440227]
- [s390] sclp: prevent console lockup during SE warmstart (Hans-Joachim Picht ) [436967]
- [s390] zcrypt: disable ap polling thread per default (Hans-Joachim Picht ) [435161]
- [s390] zfcp: hold lock on port/unit handle for task cmd (Hans-Joachim Picht ) [434959]
- [s390] zfcp: hold lock on port handle for ELS command (Hans-Joachim Picht ) [434955]
- [s390] zfcp: hold lock on port/unit handle for FCP cmd (Hans-Joachim Picht ) [433537]
- [s390] zfcp: hold lock when checking port/unit handle (Hans-Joachim Picht ) [434953]
- [s390] zfcp: handling of boxed port after physical close (Hans-Joachim Picht ) [434801]
- [s390] dasd: fix ifcc handling (Hans-Joachim Picht ) [431592]
- [s390] cio: introduce timed recovery procedure (Hans-Joachim Picht ) [430593]
- [s390] cio: sense id works with partial hw response (Hans-Joachim Picht ) [430787]
- [s390] zfcp: fix use after free bug (Hans-Joachim Picht ) [412881]
- [s390] cio: add missing reprobe loop end statement (Hans-Joachim Picht ) [412891]
- [s390] zfcp: imbalance in erp_ready_sem usage (Hans-Joachim Picht ) [412831]
- [s390] zfcp: zfcp_erp_action_dismiss will ignore actions (Hans-Joachim Picht ) [409091]
- [s390] zfcp: Units are reported as BOXED (Hans-Joachim Picht ) [412851]
- [s390] zfcp: Reduce flood on hba trace (Hans-Joachim Picht ) [415951]
- [s390] zfcp: Deadlock when adding invalid LUN (Hans-Joachim Picht ) [412841]
- [s390] pav alias disks not detected on lpar (Hans-Joachim Picht ) [416081]

* Thu Jul 10 2008 Don Zickus <dzickus@redhat.com> [2.6.18-96.el5]
- [net] randomize udp port allocation (Eugene Teo ) [454572]
- [tty] add NULL pointer checks (Aristeu Rozanski ) [453154]
- [misc] ttyS1 lost interrupt, stops transmitting v2 (Brian Maly ) [451157]
- [net] sctp: make sure sctp_addr does not overflow (David S. Miller ) [452483]
- [sys] sys_setrlimit: prevent setting RLIMIT_CPU to 0 (Neil Horman ) [437122]
- [net] sit: exploitable remote memory leak (Jiri Pirko ) [446039]
- [x86_64] zero the output of string inst on exception (Jiri Pirko ) [451276] {CVE-2008-2729}
- [net] dccp: sanity check feature length (Anton Arapov ) [447396] {CVE-2008-2358}
- [misc] buffer overflow in ASN.1 parsing routines (Anton Arapov ) [444465] {CVE-2008-1673}
- [x86_64] write system call vulnerability (Anton Arapov ) [433945] {CVE-2008-0598}

* Thu Jul 03 2008 Aristeu Rozanski <arozansk@redhat.com> [2.6.18-95.el5]
- [net] Fixing bonding rtnl_lock screwups (Fabio Olive Leite ) [450219]
- [x86_64]: extend MCE banks support for Dunnington, Nehalem (Prarit Bhargava ) [446673]
- [nfs] address nfs rewrite performance regression in RHEL5 (Eric Sandeen ) [436004]
- [mm] Make mmap() with PROT_WRITE on RHEL5 (Larry Woodman ) [448978]
- [i386]: Add check for supported_cpus in powernow_k8 driver (Prarit Bhargava ) [443853]
- [i386]: Add check for dmi_data in powernow_k8 driver (Prarit Bhargava ) [443853]
- [sata] update sata_svw (John Feeney ) [441799]
- [net] fix recv return zero (Thomas Graf ) [435657]
- [misc] kernel crashes on futex (Anton Arapov ) [435178]

* Wed Jun 04 2008 Don Zickus <dzickus@redhat.com> [2.6.18-94.el5]
- [misc] ttyS1 loses interrupt and stops transmitting (Simon McGrath ) [440121]

* Mon May 19 2008 Don Zickus <dzickus@redhat.com> [2.6.18-93.el5]
- [x86] sanity checking for read_tsc on i386 (Brian Maly ) [443435]
- [xen] netfront: send fake arp when link gets carrier (Herbert Xu ) [441716]
- [net] fix xfrm reverse flow lookup for icmp6 (Neil Horman ) [446250]
- [net] negotiate all algorithms when id bit mask zero (Neil Horman ) [442820]
- [net] 32/64 bit compat MCAST_ sock options support (Neil Horman ) [444582]
- [misc] add CPU hotplug support for relay functions (Kei Tokunaga ) [441523]

* Tue Apr 29 2008 Don Zickus <dzickus@redhat.com> [2.6.18-92.el5]
- [fs] race condition in dnotify (Alexander Viro ) [443440 439759] {CVE-2008-1669 CVE-2008-1375}

* Tue Apr 22 2008 Don Zickus <dzickus@redhat.com> [2.6.18-91.el5]
- [scsi] cciss: allow kexec to work (Chip Coldwell ) [230717]
- [xen] ia64: set memory attribute in inline asm (Tetsu Yamamoto ) [426015]
- [xen] fix VT-x2 FlexPriority (Bill Burns ) [252236]

* Tue Apr 15 2008 Don Zickus <dzickus@redhat.com> [2.6.18-90.el5]
- [x86_64] page faults from user mode are user faults (Dave Anderson ) [442101]
- [ia64] kdump: add save_vmcore_info to INIT path (Neil Horman ) [442368]
- [misc] infinite loop in highres timers (Michal Schmidt ) [440002]
- [net] add aes-ctr algorithm to xfrm_nalgo (Neil Horman ) [441425]
- [x86_64] 32-bit address space randomization (Peter Zijlstra ) [213483]
- Revert: [scsi] qla2xxx: pci ee error handling support (Marcus Barrow ) [441779]
- [pci] revert 'PCI: remove transparent bridge sizing' (Ed Pollard ) [252260]
- [ppc64] eHEA: fixes receive packet handling (Brad Peters ) [441364]

* Tue Apr 08 2008 Don Zickus <dzickus@redhat.com> [2.6.18-89.el5]
- [xen] memory corruption due to VNIF increase (Tetsu Yamamoto ) [441390]
- [crytpo] use scatterwalk_sg_next for xcbc (Thomas Graf ) [439874]
- [video] PWC driver DoS (Pete Zaitcev ) [308531]
- [s390] cio: fix vary off of paths (Hans-Joachim Picht ) [436106]
- [pci] fix MSI interrupts on HT1000 based machines (Doug Ledford ) [438776]
- [s390] cio: CHPID configuration event is ignored (Hans-Joachim Picht ) [431858]
- [x86_64] add phys_base to vmcoreinfo (Muuhh IKEDA ) [439304]
- [wd] disable hpwdt due to nmi problems (Prarit Bhargava ) [438741]
- [nfs] fix the fsid revalidation in nfs_update_inode (Steve Dickson ) [431166]
- [ppc64] SLB shadow buffer error cause random reboots (Brad Peters ) [440085]
- [xen] check num of segments in block backend driver (Bill Burns ) [378291]
- [sata] SB600: add 255-sector limit (Bhavana Nagendra ) [434741]
- [x86_64] fix unprivileged crash on %cs corruption (Jarod Wilson ) [439788]
- [scsi] qla4xxx: update driver version number (Marcus Barrow ) [439316]
- [acpi] only ibm_acpi.c should report bay events (Prarit Bhargava ) [439380]
- [x86] xen: fix SWIOTLB overflows (Stephen C. Tweedie ) [433554]
- [x86] fix mprotect on PROT_NONE regions (Stephen C. Tweedie ) [437412]
- [net] ESP: ensure IV is in linear part of the skb (Thomas Graf ) [427248]
- [x86] fix 4 bit apicid assumption (Geoff Gustafson ) [437820]
- [sata] SB700/SB800 64bit DMA support (Bhavana Nagendra ) [434741]

* Tue Apr 01 2008 Don Zickus <dzickus@redhat.com> [2.6.18-88.el5]
- [pci] hotplug: PCI Express problems with bad DLLPs (Kei Tokunaga ) [433355]
- [net] bnx2x: update 5.2 to support latest firmware (Andy Gospodarek ) [435261]
- [ipsec] use hmac instead of digest_null (Herbert Xu ) [436267]
- [utrace] race crash fixes (Roland McGrath ) [428693 245429 245735 312961]
- [x86_64] EXPORT smp_call_function_single (George Beshers ) [438720]
- [s390] FCP/SCSI write IO stagnates (Jan Glauber ) [437099]
- [net] ipv6: check ptr in ip6_flush_pending_frames (Neil Horman ) [439059]
- [nfs] stop sillyrenames and unmounts from racing (Steve Dickson ) [437302]
- [ppc64] oprofile: add support for Power5+ and later (Brad Peters ) [244719]
- [agp] add cantiga ids (Geoff Gustafson ) [438919]
- [x86] oprofile: support for Penryn-class processors (Geoff Gustafson ) [253056]
- [net] ipv6: fix default address selection rule 3 (Neil Horman ) [438429]
- [audit] fix panic, regression, netlink socket usage (Eric Paris ) [434158]
- [net] eHEA: checksum error fix (Brad Peters ) [438212]
- [s390] fix qeth scatter-gather (Jan Glauber ) [438180]
- [ata] fix SATA IDE mode bug upon resume (Bhavana Nagendra ) [432652]
- [openib] update ipath driver (Doug Ledford ) [253023]
- [openib] update the nes driver from 0.4 to 1.0 (Doug Ledford ) [253023]
- [openib] IPoIB updates (Doug Ledford ) [253023]
- [openib] cleanup of the xrc patch removal (Doug Ledford ) [253023]
- [openib] remove srpt and empty vnic driver files (Doug Ledford ) [253023]
- [openib] enable IPoIB connect mode support (Doug Ledford ) [253023]
- [openib] SDP accounting fixes (Doug Ledford ) [253023]
- [openib] add improved error handling in srp driver (Doug Ledford ) [253023]
- [openib] minor core updates between rc1 and final (Doug Ledford ) [253023]
- [openib] update ehca driver to version 0.25 (Doug Ledford ) [253023]
- [openib] remove xrc support (Doug Ledford ) [253023]
- [ppc64] hardware watchpoints: add DABRX init (Brad Peters ) [438259]
- [ppc64] hardware watchpoints: add DABRX definitions (Brad Peters ) [438259]
- [x86_64] address space randomization (Peter Zijlstra ) [222473]
- [ppc64] fixes removal of virtual cpu from dlpar (Brad Peters ) [432846]
- [mm] inconsistent get_user_pages and memory mapped (Brad Peters ) [408781]
- [s390] add missing TLB flush to hugetlb_cow (Hans-Joachim Picht ) [433799]
- [xen] HV ignoring extended cpu model field (Geoff Gustafson ) [439254]
- [xen] oprofile: support for Penryn-class processors (Geoff Gustafson ) [253056]
- [xen] ia64: HV messages are not shown on VGA console (Tetsu Yamamoto ) [438789]
- [xen] ia64: ftp stress test fixes between HVM/Dom0 (Tetsu Yamamoto ) [426015]
- [xen] ia64: fix kernel panic on systems w/<=4GB RAM (Jarod Wilson ) [431001]

* Tue Mar 25 2008 Don Zickus <dzickus@redhat.com> [2.6.18-87.el5]
- [scsi] qla4xxx: negotiation issues with new switches (Marcus Barrow ) [438032]
- [net] qla3xxx: have link SM use work threads (Marcus Barrow ) [409171]
- [scsi] qla4xxx: fix completion, lun reset code (Marcus Barrow ) [438214]
- [scsi] lpfc: update driver to 8.2.0.22 (Chip Coldwell ) [437050]
- [scsi] lpfc: update driver to 8.2.0.21 (Chip Coldwell ) [437050]
- [block] sg: cap reserved_size values at max_sectors (David Milburn ) [433481]
- Revert: [xen] idle=poll instead of hypercall block (Bill Burns ) [437252]
- [scsi] lpfc: update driver to 8.2.0.20 (Chip Coldwell ) [430600]
- [xen] add warning to 'time went backwards' message (Prarit Bhargava ) [436775]
- [x86] clear df flag for signal handlers (Jason Baron ) [436131]
- [usb] fix iaa watchdog notifications (Bhavana Nagendra ) [435670]
- [usb] new iaa watchdog timer (Bhavana Nagendra ) [435670]

* Tue Mar 18 2008 Don Zickus <dzickus@redhat.com> [2.6.18-86.el5]
- [sound] HDMI device IDs for AMD ATI chipsets (Bhavana Nagendra ) [435658]
- [scsi] fusion: 1078 corrupts data in 36GB mem region (Chip Coldwell ) [436210]
- [GFS2] gfs2_adjust_quota has broken unstuffing code (Abhijith Das ) [434736]
- [docs] add oom_adj and oom_score use to proc.txt (Larry Woodman ) [277151]
- [GFS2] optimise loop in gfs2_bitfit (Bob Peterson ) [435456]
- [crypto] fix SA creation with ESP encryption-only (Thomas Graf ) [436267]
- [crypto] fix SA creation with AH (Thomas Graf ) [435243]
- [ppc64] spufs: invalidate SLB then add a new entry (Brad Peters ) [436336]
- [ppc64] SLB: serialize invalidation against loading (Brad Peters ) [436336]
- [ppc64] cell: remove SPU_CONTEXT_SWITCH_ACTIVE flag (Brad Peters ) [434155]
- Revert: [net] sunrpc: fix hang due to eventd deadlock (Jeff Layton ) [438044]
- [ppc64] broken MSI on cell blades when IOMMU is on (Brad Peters ) [430949]
- [cpufreq] powernow: blacklist bad acpi tables (Chris Lalancette ) [430947]
- [firmware] ibft_iscsi: prevent misconfigured iBFTs (Konrad Rzeszutek ) [430297]
- [xen] HV inside a FV guest, crashes the host (Bill Burns ) [436351]

* Tue Mar 11 2008 Don Zickus <dzickus@redhat.com> [2.6.18-85.el5]
- [xen] ia64: fix kprobes slowdown on single step (Tetsu Yamamoto ) [434558]
- [xen] mprotect performance improvements (Rik van Riel ) [412731]
- [GFS2] remove assertion 'al->al_alloced' failed (Abhijith Das ) [432824]
- [misc] remove unneeded EXPORT_SYMBOLS (Don Zickus ) [295491]
- [net] e1000e: wake on lan fixes (Andy Gospodarek ) [432343]
- [sound] add support for HP-RP5700 model (Jaroslav Kysela ) [433593]
- [scsi] hptiop: fixes buffer overflow, adds pci-ids (Chip Coldwell ) [430662]
- [crypto] xcbc: fix IPsec crash with aes-xcbc-mac (Herbert Xu ) [435377]
- [misc] fix memory leak in alloc_disk_node (Jerome Marchand ) [395871]
- [net] cxgb3: rdma arp and loopback fixes (Andy Gospodarek ) [253449]
- [misc] fix range check in fault handlers with mremap (Vitaly Mayatskikh ) [428971]
- [ia64] fix userspace compile error in gcc_intrin.h (Doug Chapman ) [429074]
- [ppc64] fix xics set_affinity code (Brad Peters ) [435126]
- [scsi] sym53c8xx: use proper struct (Brad Peters ) [434857]
- [ppc64] permit pci error state recovery (Brad Peters ) [434857]
- [misc] fix ALIGN macro (Thomas Graf ) [434940]
- [x86] fix relocate_kernel to not overwrite pgd (Neil Horman ) [346431]
- [net] qla2xxx: wait for flash to complete write (Marcus Barrow ) [434992]
- [ppc64] iommu DMA alignment fix (Brad Peters ) [426875]
- [x86] add HP DL580 G5 to bfsort whitelist (Tony Camuso ) [434792]
- [video] neofb: avoid overwriting fb_info fields (Anton Arapov ) [430254]
- [x86] blacklist systems that need nommconf (Prarit Bhargava ) [433671]
- [sound] add support for AD1882 codec (Jaroslav Kysela ) [429073]
- [scsi] ibmvscsi: set command timeout to 60 seconds (Brad Peters ) [354611]
- [x86] mprotect performance improvements (Rik van Riel ) [412731]
- [fs] nlm: fix refcount leak in nlmsvc_grant_blocked (Jeff Layton ) [432626]
- [net] igb: more 5.2 fixes and backports (Andy Gospodarek ) [252004]
- [net] remove IP_TOS setting privilege checks (Thomas Graf ) [431074]
- [net] ixgbe: obtain correct protocol info on xmit (Andy Gospodarek ) [428230]
- [nfs] fslocations/referrals broken (Brad Peters ) [432690]
- [net] sctp: socket initialization race (Neil Horman ) [426234]
- [net] ipv6: fix IPsec datagram fragmentation (Herbert Xu ) [432314]
- [audit] fix bogus reporting of async signals (Alexander Viro ) [432400]
- [cpufreq] xen: properly register notifier (Bhavana Nagendra ) [430940]
- [x86] fix TSC feature flag check on AMD (Bhavana Nagendra ) [428479]

* Fri Feb 29 2008 Don Zickus <dzickus@redhat.com> [2.6.18-84.el5]
- [xen] x86: revert to default PIT timer (Bill Burns ) [428710]

* Thu Feb 21 2008 Don Zickus <dzickus@redhat.com> [2.6.18-83.el5]
- [xen] x86: fix change frequency hypercall (Bhavana Nagendra ) [430938]
- [xen] resync TSC extrapolated frequency (Bhavana Nagendra ) [430938]
- [xen] new vcpu lock/unlock helper functions (Bhavana Nagendra ) [430938]

* Tue Feb 19 2008 Don Zickus <dzickus@redhat.com> [2.6.18-82.el5]
- [ppc64] X fails to start (Don Zickus ) [433038]

* Tue Feb 12 2008 Don Zickus <dzickus@redhat.com> [2.6.18-81.el5]
- [gfs2] fix calling of drop_bh (Steven Whitehouse ) [432370]
- [nfs] potential file corruption issue when writing (Jeff Layton ) [429755]
- [nfs] interoperability problem with AIX clients (Steve Dickson ) [426804]
- [libata] sata_nv: un-blacklist hitachi drives (David Milburn ) [426044]
- [libata] sata_nv: may send cmds with duplicate tags (David Milburn ) [426044]

* Sun Feb 10 2008 Don Zickus <dzickus@redhat.com> [2.6.18-80.el5]
- [fs] check permissions in vmsplice_to_pipe (Alexander Viro ) [432253] {CVE-2008-0600}

* Fri Feb 08 2008 Don Zickus <dzickus@redhat.com> [2.6.18-79.el5]
- [net] sctp: add bind hash locking to migrate code (Aristeu Rozanski ) [426234]
- [net] ipsec: allow CTR mode use with AES (Aristeu Rozanski ) [430164]
- [net] ipv6: fixes to meet DoD requirements (Thomas Graf ) [431718]
- [module] fix module loader race (Jan Glauber ) [429909]
- [misc] ICH10 device IDs (Geoff Gustafson ) [251083]
- [sound] enable S/PDIF in Fila/Converse - fixlet (John Feeney ) [240783]
- [ide] ide-io: fail request when device is dead (Aristeu Rozanski ) [354461]
- [mm] add sysctl to not flush mmapped pages (Larry Woodman ) [431180]
- [net] bonding: locking fixes and version 3.2.4 (Andy Gospodarek ) [268001]
- [gfs2] reduce memory footprint (Bob Peterson ) [349271]
- [net] e1000e: tweak irq allocation messages (Andy Gospodarek ) [431004]
- [sched] implement a weak interactivity mode (Peter Zijlstra ) [250589]
- [sched] change the interactive interface (Peter Zijlstra ) [250589]
- [ppc] chrp: fix possible strncmp NULL pointer usage (Vitaly Mayatskikh ) [396831]
- [s390] dasd: fix loop in request expiration handling (Hans-Joachim Picht ) [430592]
- [s390] dasd: set online fails if initial probe fails (Hans-Joachim Picht ) [429583]
- [scsi] cciss: update procfs (Tomas Henzl ) [423871]
- [Xen] ia64: stop all CPUs on HV panic part3 (Tetsu Yamamoto ) [426129]

* Tue Feb 05 2008 Don Zickus <dzickus@redhat.com> [2.6.18-78.el5]
- [misc] enable i2c-piix4 (Bhavana Nagendra ) [424531]
- [ide] missing SB600/SB700 40-pin cable support (Bhavana Nagendra ) [431437]
- [isdn] i4l: fix memory overruns (Vitaly Mayatskikh ) [425181]
- [net] icmp: restore pskb_pull calls in receive func (Herbert Xu ) [431293]
- [nfs] reduce number of wire RPC ops, increase perf (Peter Staubach ) [321111]
- [xen] 32-bit pv guest migration can fail under load (Don Dutile ) [425471]
- [ppc] fix mmap of PCI resource with hack for X (Scott Moser ) [229594]
- [md] fix raid1 consistency check (Doug Ledford ) [429747]

* Thu Jan 31 2008 Don Zickus <dzickus@redhat.com> [2.6.18-77.el5]
- [xen] ia64: domHVM with pagesize 4k hangs part2 (Tetsu Yamamoto ) [428124]
- [scsi] qla2xxx: update RH version number (Marcus Barrow ) [431052]
- [ia64] fix unaligned handler for FP instructions (Luming Yu ) [428920]
- [fs] fix locking for fcntl (Ed Pollard ) [430596]
- [isdn] fix possible isdn_net buffer overflows (Aristeu Rozanski ) [392161] {CVE-2007-6063}
- [audit] fix potential SKB invalid truesize bug (Hideo AOKI ) [429417]
- [net] e1000e: disable hw crc stripping (Andy Gospodarek ) [430722]
- [firewire] more upstream fixes regarding rom (Jay Fenlason ) [370421]
- [scsi] qla25xx: incorrect firmware loaded (Marcus Barrow ) [430725]
- [scsi] qla2xxx: updated firmware for 25xxx (Marcus Barrow ) [430729]
- [gfs2] speed up read/write performance (Bob Peterson ) [253990]

* Tue Jan 29 2008 Don Zickus <dzickus@redhat.com> [2.6.18-76.el5]
- [Xen] gnttab: allow more than 3 VNIFs (Tetsu Yamamoto ) [297331]
- [xen] fix /sbin/init to use cpu_possible (Chris Lalancette ) [430310]
- [GFS2] install to root volume should work (Abhijith Das ) [220052]
- [scsi] iscsi: set host template (Mike Christie ) [430130]
- [selinux] harden against null ptr dereference bugs (Eric Paris ) [233021]

* Thu Jan 24 2008 Don Zickus <dzickus@redhat.com> [2.6.18-75.el5]
- [xen] ia64: stop all cpus on hv panic part2 (Tetsu Yamamoto ) [426129]
- [sata] combined mode fix for 5.2 (Peter Martuccelli ) [428945 428708]
- [net] bridge br_if: fix oops in port_carrier_check (Herbert Xu ) [408791]
- [misc] agp: add E7221 pci ids (Dave Airlie ) [216722]
- [ia64] kdump: slave CPUs drop to POD (Jonathan Lim ) [429956]

* Wed Jan 23 2008 Don Zickus <dzickus@redhat.com> [2.6.18-74.el5]
- Revert: [s390] qeth: create copy of skb for modification (Hans-Joachim Picht ) [354861]
- Revert: [xen] allow more than 3 VNIFs (Tetsu Yamamoto ) [297331]
- [nfs] discard pagecache data for dirs on dentry_iput (Jeff Layton ) [364351]
- [net] link_watch: always schedule urgent events (Herbert Xu ) [251527]
- [audit] ratelimit printk messages (Eric Paris ) [428701]
- [misc] kprobes: fix reentrancy (Dave Anderson ) [232489]
- [misc] kprobes: inatomic __get_user and __put_user (Dave Anderson ) [232489]
- [misc] kprobes: support kretprobe blacklist (Dave Anderson ) [232489]
- [misc] kprobes: make probe handler stack unwind correct (Dave Anderson ) [232489]
- [net] ipv6: use correct seed to compute ehash index (Neil Horman ) [248052]
- [scsi] areca: update to latest (Tomas Henzl ) [429877]
- [net] fix potential SKB invalid truesize bug (Hideo AOKI ) [429417]
- [ia64] enable CMCI on hot-plugged processors (Fabio Olive Leite ) [426793]
- [s390] system z large page support (Hans-Joachim Picht ) [318951]
- [mm] introduce more huge pte handling functions (Jan Glauber ) [318951]
- [mm] make page->private usable in compound pages (Jan Glauber ) [318951]
- [net] udp: update infiniband driver (Hideo AOKI ) [223593]
- [net] udp: add memory accounting (Hideo AOKI ) [223593]
- [net] udp: new accounting interface (Hideo AOKI ) [223593]
- [misc] support module taint flag in /proc/modules (Jon Masters ) [253476]
- [scsi] sym53c8xx: add PCI error recovery callbacks (Ed Pollard ) [207977]
- [usb] sierra MC8755: increase HSDPA performance (Ivan Vecera ) [232885]

* Wed Jan 23 2008 Don Zickus <dzickus@redhat.com> [2.6.18-73.el5]
- [xen] ia64: domHVM with pagesize 4k hangs (Tetsu Yamamoto ) [428124]
- [xen] ia64: guest has bad network performance (Tetsu Yamamoto ) [272201]
- [xen] ia64: create 100GB mem guest, HV softlockup (Tetsu Yamamoto ) [251353]
- [xen] ia64: create 100GB mem guest fixes (Tetsu Yamamoto ) [251353]
- [xen] x86-pae: support >4GB memory ia64 fixes (Bhavana Nagendra ) [316371]
- [xen] x86-pae: support >4GB memory (Bhavana Nagendra ) [316371]
- [kABI] RHEL-5.2 updates (Jon Masters ) [282881 284231 252994 371971 403821 264701 422321]
- [ia64] xen: create 100GB mem guest, fix softlockup#2 (Tetsu Yamamoto ) [251353]
- [ia64] xen: create 100GB mem guest, fix softlockup (Tetsu Yamamoto ) [251353]
- [acpi] backport video support from upstream (Dave Airlie ) [428326]
- [audit] break execve records into smaller parts (Eric Paris ) [429692]
- [scsi] qla2xxx fw: driver doesn't login to fabric (Marcus Barrow ) [253477]
- [x86] pci: use pci=norom to disable p2p rom window (Konrad Rzeszutek ) [426033]
- [s390] crypto: new CP assist functions (Hans-Joachim Picht ) [318961]
- [s390] OSA 2 Ports per CHPID support (Hans-Joachim Picht ) [318981]
- [s390] STSI change for capacity provisioning (Hans-Joachim Picht ) [318991]
- [s390] HiperSockets MAC layer routing support (Hans-Joachim Picht ) [319001]
- [scsi] aic94xx: version 1.0.2-2 (Konrad Rzeszutek ) [253301]
- [ppc64] cell: support for Performance Tools part4 (Scott Moser ) [253211]
- [ppc64] cell: support for Performance Tools part3 (Brad Peters ) [253211]
- [ppc64] cell: support for Performance Tools part2 (Scott Moser ) [253211]
- [ppc64] cell: support for Performance Tools part1 (Brad Peters ) [253211]

* Mon Jan 21 2008 Don Zickus <dzickus@redhat.com> [2.6.18-72.el5]
- [ppc64] backport PMI driver for cell blade (Scott Moser ) [279171]
- [fs] ecryptfs: fix dentry handling (Eric Sandeen ) [228341]
- [net] IPV6 SNMP counters fix (Ed Pollard ) [421401]
- [gfs2] lock the page on error (Bob Peterson ) [429168]
- [fs] manually d_move inside of rename() (Peter Staubach ) [427472]
- [dlm] validate lock name length (Patrick Caulfeld ) [409221]
- [net] IPv6 TAHI RH0 RFC5095 update (Thomas Graf ) [426904]
- [mm] using hugepages panics the kernel (Larry Woodman ) [429205]
- [sound] enable HDMI for AMD/ATI integrated chipsets (Bhavana Nagendra ) [428963]
- [net] wireless: introduce WEXT scan capabilities (John W. Linville ) [427528]
- [mm] hugepages: leak due to pagetable page sharing (Larry Woodman ) [428612]
- [nfs] acl support broken due to typo (Steve Dickson ) [429109]
- [ide] hotplug docking support for some laptops (Alan Cox ) [230541]
- [x86] cpufreq: unknown symbol fixes (Rik van Riel ) [427368]
- [mm] prevent cpu lockups in invalidate_mapping_pages (Larry Woodman ) [427798]
- [x86] mmconfig: call pcibios_fix_bus_scan (tcamuso@redhat.com ) [408551]
- [x86] mmconfig: introduce pcibios_fix_bus_scan (tcamuso@redhat.com ) [408551]
- [x86] mmconfig: init legacy pci conf functions (tcamuso@redhat.com ) [408551]
- [x86] mmconfig: add legacy pci conf functions (tcamuso@redhat.com ) [408551]
- [x86] mmconfig: introduce PCI_USING_MMCONF flag (tcamuso@redhat.com ) [408551]
- [x86] mmconfig: remove platforms from the blacklist (tcamuso@redhat.com ) [239673 253288 408551]
- [fs] hfs: make robust to deal with disk corruption (Eric Sandeen ) [213773]
- [acpi] improve reporting of power states (Brian Maly ) [210716]
- [net] e1000: update to lastest upstream (Andy Gospodarek ) [253128]
- [net] e1000e: update to latest upstream (Andy Gospodarek ) [252003]
- [xen] xenoprof: loses samples for passive domains (Markus Armbruster ) [426200]
- [cpufreq] ondemand governor update (Brian Maly ) [309311]
- [input] enable HP iLO2 virtual remote mouse (Alex Chiang ) [250288]
- [misc] ioat: support for 1.9 (John Feeney ) [209411]
- [ppc64] oprofile: power5+ needs unique entry (Scott Moser ) [244719]
- [ppc64] oprofile: distinguish 970MP from other 970s (Scott Moser ) [216458]
- [wd] hpwdt: initial support (pschoell ) [251063]
- [xen] x86: more improved TPR/CR8 virtualization (Bhavana Nagendra ) [251985]
- [xen] domain debugger for VTi (Tetsu Yamamoto ) [426362]
- [xen] virtualize ibr/dbr for PV domains (Tetsu Yamamoto ) [426362]

* Sat Jan 19 2008 Don Zickus <dzickus@redhat.com> [2.6.18-71.el5]
- [scsi] cciss: fix incompatibility with hpacucli (Tomas Henzl ) [426873]
- Revert: [net] udp: update infiniband driver (Hideo AOKI ) [223593]
- Revert: [net] udp: add memory accounting (Hideo AOKI ) [223593]
- Revert: [net] udp: new accounting interface (Hideo AOKI ) [223593]
- Revert: [misc] add a new /proc/modules_taint interface (Jon Masters ) [253476]

* Thu Jan 17 2008 Don Zickus <dzickus@redhat.com> [2.6.18-70.el5]
- [xen] move hvm_maybe_deassert_evtchn_irq early (Don Dutile ) [412721]
- [xen] hvm: tolerate intack completion failure (Don Dutile ) [412721]
- [xen] hvm: evtchn to fake pci interrupt propagation (Don Dutile ) [412721]
- [char] R500 drm support (Dave Airlie ) [429012]
- [x86] correct cpu cache info for Tolapai (Geoff Gustafson ) [426172]
- [ia64] xen: fix bogus IOSAPIC (Doug Chapman ) [246130]
- [misc] enabling a non-hotplug cpu should cause panic (Kei Tokunaga ) [426508]
- [cpufreq] booting with maxcpus=1 panics (Doug Chapman ) [428331]
- [net] fix missing defintions from rtnetlink.h (Neil Horman ) [428143]
- [xen] kdump: fix dom0 /proc/vmcore layout (Neil Horman ) [423731]
- [xen] ia64: access extended I/O spaces from dom0 (Jarod Wilson ) [249629]
- [net] udp: update infiniband driver (Hideo AOKI ) [223593]
- [net] udp: add memory accounting (Hideo AOKI ) [223593]
- [net] udp: new accounting interface (Hideo AOKI ) [223593]
- [xen] idle=poll instead of hypercall block (Markus Armbruster ) [416141]
- [net] get minimum RTO via tcp_rto_min (Anton Arapov ) [427205]
- [xen] fixes a comment only (Bill Burns ) [328321]
- [xen] make dma_addr_to_phys_addr static (Bill Burns ) [328321]
- [xen] allow sync on offsets into dma-mapped region (Bill Burns ) [328321]
- [xen] keep offset in a page smaller than PAGE_SIZE (Bill Burns ) [328321]
- [xen] handle sync invocations on mapped subregions (Bill Burns ) [328321]
- [xen] handle multi-page segments in dma_map_sg (Bill Burns ) [328321]
- [misc] add a new /proc/modules_taint interface (Jon Masters ) [253476]
- [scsi] iscsi: Boot Firmware Table tool support (Konrad Rzeszutek ) [307781]
- [mm] make zonelist order selectable in NUMA (Kei Tokunaga ) [251111]
- [ide] handle DRAC4 hotplug (John Feeney ) [212391]
- [xen] allow more than 3 VNIFs (Tetsu Yamamoto ) [297331]
- [misc] enable support for CONFIG_SUNDANCE (Andy Gospodarek ) [252074]
- [ia64] use thread.on_ustack to determine user stack (Luming Yu ) [253548]
- [xen] export cpu_llc_id as gpl (Rik van Riel ) [429004]
- [md] avoid reading past end of bitmap file (Ivan Vecera ) [237326]
- [acpi] Support external package objs as method args (Luming Yu ) [241899]

* Wed Jan 16 2008 Don Zickus <dzickus@redhat.com> [2.6.18-69.el5]
- [xen] incorrect calculation leads to wrong nr_cpus (Daniel P. Berrange ) [336011]
- [xen] ia64: hv hangs on Corrected Platform Errors (Tetsu Yamamoto ) [371671]
- [xen] ia64: warning fixes when checking EFI memory (Tetsu Yamamoto ) [245566]
- [Xen] ia64: stop all CPUs on HV panic (Tetsu Yamamoto ) [426129]
- [Xen] ia64: failed domHVM creation causes HV hang (Tetsu Yamamoto ) [279831]
- [xen] export NUMA topology info to domains (Bill Burns ) [235848]
- [xen] provide NUMA memory usage information (Bill Burns ) [235850]
- [xen] x86: barcelona hypervisor fixes (Bhavana Nagendra ) [421021]
- [xen] improve checking in vcpu_destroy_pagetables (Bill Burns ) [227614]
- [xen] domain address-size clamping (Bill Burns ) [227614]
- [xen] x86: fix continuation translation for large HC (Bill Burns ) [227614]
- [xen] x86: make HV respect the e820 map < 16M (Chris Lalancette ) [410811]
- [xen] x86: vTPR support and upper address fix (Bill Burns ) [252236]
- [xen] x86: fix hp management support on proliant (Bill Burns ) [415691]
- [xen] x86: improved TPR/CR8 virtualization (Bhavana Nagendra ) [251985]
- [xen] ia64: running java-vm causes dom0 to hang (Tetsu Yamamoto ) [317301]
- [xen] enable nested paging by default on amd-v (Bhavana Nagendra ) [247190]
- [fs] corruption by unprivileged user in directories (Vitaly Mayatskikh ) [428797] {CVE-2008-0001}
- [gfs2] Reduce gfs2 memory requirements (Bob Peterson ) [428291]
- [gfs2] permission denied on first attempt to exec (Abhijith Das ) [422681]
- [openib] OFED 1.3 support (Doug Ledford ) [253023 254027 284861]
- [scsi] qla2xxx: fix bad nvram kernel panic (Marcus Barrow ) [367201]
- [scsi] qla2xxx: fix for infinite-login-retry (Marcus Barrow ) [426327]
- [misc] increase softlockup timeout maximum (George Beshers ) [253124]
- [misc] firewire: latest upstream (Jay Fenlason ) [370421]
- [misc] pci rom: reduce number of failure messages (Jun'ichi "Nick" Nomura ) [217698]
- [s390] pte type cleanup (Hans-Joachim Picht ) [360701]
- [s390] qdio: output queue stall on FCP and net devs (Hans-Joachim Picht ) [354871]
- [s390] qdio: many interrupts on qdio-driven devices (Hans-Joachim Picht ) [360821]
- [s390] qdio: time calculation is wrong (Hans-Joachim Picht ) [360631]
- [s390] crash placing a kprobe on  instruction (Hans-Joachim Picht ) [253275]
- [s390] data corruption on DASD while toggling CHPIDs (Hans-Joachim Picht ) [360611]
- [s390] fix dump on panic for DASDs under LPAR (Hans-Joachim Picht ) [250352]
- [s390] qeth: crash during activation of OSA-cards (Hans-Joachim Picht ) [380981]
- [s390] qeth: hipersockets supports IP packets only (Hans-Joachim Picht ) [329991]
- [s390] cio: Disable chan path measurements on reboot (Hans-Joachim Picht ) [354801]
- [s390] zfcp: remove SCSI devices then adapter (Hans-Joachim Picht ) [382841]
- [s390] zfcp: error messages when LUN 0 is present (Jan Glauber ) [354811]
- [s390] qeth: drop inbound pkt with unknown header id (Hans-Joachim Picht ) [360591]
- [s390] qeth: recognize/handle RC=19 from Hydra 3 OSA (Hans-Joachim Picht ) [354891]
- [char] tpm: cleanups and fixes (Konrad Rzeszutek ) [184784]
- [s390] z/VM monitor stream state 2 (Hans-Joachim Picht ) [253026]
- [s390] support for z/VM DIAG 2FC (Hans-Joachim Picht ) [253034]
- [s390] Cleanup SCSI dumper code part 2 (Hans-Joachim Picht ) [253104]
- [s390] AF_IUCV Protocol support (Jan Glauber ) [228117]
- [s390] z/VM unit-record device driver (Hans-Joachim Picht ) [253121]
- [s390] cleanup SCSI dumper code (Hans-Joachim Picht ) [253104]
- [s390] qeth: skb sg support for large incoming msgs (Hans-Joachim Picht ) [253119]
- [ia64] /proc/cpuinfo of Montecito (Luming Yu ) [251089]

* Sun Jan 13 2008 Don Zickus <dzickus@redhat.com> [2.6.18-68.el5]
- [misc] offline CPU with realtime process running v2 (Michal Schmidt ) [240232]
- Revert: [misc] offlining a CPU with realtime process running (Don Zickus ) [240232]
- [x86] fix build warning for command_line_size (Prarit Bhargava ) [427423]
- [mm] show_mem: include count of pagecache pages (Larry Woodman ) [428094]
- [nfs] Security Negotiation (Steve Dickson ) [253019]
- [net] igb: update to actual upstream version (Andy Gospodarek ) [252004]
- [scsi] cciss: move READ_AHEAD to block layer (Tomas Henzl ) [424371]
- [scsi] cciss: update copyright information (Tomas Henzl ) [423841]
- [scsi] cciss: support new controllers (Tomas Henzl ) [423851]
- [scsi] cciss version change (Tomas Henzl ) [423831]
- [md] dm-mpath: send uevents for path fail/reinstate (dwysocha@redhat.com ) [184778]
- [md] dm-uevent: generate events (Dave Wysochanski ) [184778]
- [md] dm: add uevent to core (dwysocha@redhat.com ) [184778]
- [md] dm: export name and uuid (dwysocha@redhat.com ) [184778]
- [md] dm: kobject backport (Dave Wysochanski ) [184778]
- [sata] rhel5.2 driver update (Jeff Garzik ) [184884 307911]
- [sata] rhel5.2 general kernel prep (Jeff Garzik ) [184884 307911]
- [md] dm: auto loading of dm-mirror log modules (Jonathan Brassow ) [388661]
- [scsi] areca driver update rhel part (Tomas Henzl ) [363961]
- [scsi] areca driver update (Tomas Henzl ) [363961]
- [firewire] limit logout messages in the logs (Jay Fenlason ) [304981]
- - [net] add support for dm9601 (Ivan Vecera ) [251994]
- [ia64] ACPICA: allow Load tables (Luming Yu ) [247596]

* Fri Jan 11 2008 Don Zickus <dzickus@redhat.com> [2.6.18-67.el5]
- [xfrm] drop pkts when replay counter would overflow (Herbert Xu ) [427877]
- [xfrm] rfc4303 compliant auditing (Herbert Xu ) [427877]
- [ipsec] add ICMP host relookup support (Herbert Xu ) [427876]
- [ipsec] added xfrm reverse calls (Herbert Xu ) [427876]
- [ipsec] make xfrm_lookup flags argument a bit-field (Herbert Xu ) [427876]
- [ipv6] esp: discard dummy packets from rfc4303 (Herbert Xu ) [427872]
- [ipv4] esp: discard dummy packets from rfc4303 (Herbert Xu ) [427872]
- [ipsec] add support for combined mode algorithms (Herbert Xu ) [253051]
- [ipsec] allow async algorithms (Herbert Xu ) [253051]
- [ipsec] use crypto_aead and authenc in ESP (Herbert Xu ) [253051]
- [ipsec] add new skcipher/hmac algorithm interface (Herbert Xu ) [253051]
- [ipsec] add async resume support on input (Herbert Xu ) [253051]
- [crypto] aead: add authenc (Herbert Xu ) [253051]
- [ipsec] add async resume support on output (Herbert Xu ) [253051]
- [crypto] xcbc: new algorithm (Herbert Xu ) [253051]
- [crypto] ccm: added CCM mode (Herbert Xu ) [253051]
- [crypto] tcrypt: add aead support (Herbert Xu ) [253051]
- [crypto] ctr: add CTR  block cipher mode (Herbert Xu ) [253051]
- [crypto] hmac: add crypto template implementation (Herbert Xu ) [253051]
- [crypto] tcrypt: hmac template and hash interface (Herbert Xu ) [253051]
- [crypto] tcrypt: use skcipher interface (Herbert Xu ) [253051]
- [crypto] digest: added user api for new hash type (Herbert Xu ) [253051]
- [crypto] cipher: added block ciphers for CBC/ECB (Herbert Xu ) [253051]
- [crypto] cipher: added encrypt_one/decrypt_one (Herbert Xu ) [253051]
- [crypto] seqiv: add seq num IV generator (Herbert Xu ) [253051]
- [crypto] api: add aead crypto type (Herbert Xu ) [253051]
- [crypto] eseqiv: add encrypted seq num IV generator (Herbert Xu ) [253051]
- [crypto] chainiv: add chain IV generator (Herbert Xu ) [253051]
- [crypto] skcipher: add skcipher infrastructure (Herbert Xu ) [253051]
- [crypto] api: add cryptomgr (Herbert Xu ) [253051]
- [crypto] api: add new bottom-level crypto_api (Herbert Xu ) [253051]
- [crypto] api: add new top-level crypto_api (Herbert Xu ) [253051]
- [scsi] mpt fusion: set config_fusion_max=128 (Chip Coldwell ) [426533]
- [xen] ia64: fix ssm_i emulation barrier and vdso pv (Tetsu Yamamoto ) [426015]
- [xen] ia64: cannot create guest having 100GB memory (Tetsu Yamamoto ) [251353]
- [ia64] altix acpi iosapic warning cleanup (George Beshers ) [246130]
- [x86] add pci quirk to HT enabled systems (Neil Horman ) [336371]
- [fs] ecryptfs: check for existing key_tfm at mount (Eric Sandeen ) [228341]
- [fs] ecryptfs: redo dget,mntget on dentry_open fail (Eric Sandeen ) [228341]
- [fs] ecryptfs: upstream fixes (Eric Sandeen ) [228341]
- [fs] ecryptfs: connect sendfile ops (Eric Sandeen ) [228341]
- [fs] ecryptfs: backport to rhel5 netlink api (Eric Sandeen ) [228341]
- [fs] ecryptfs: backport to rhel5 scatterlist api (Eric Sandeen ) [228341]
- [fs] ecryptfs: backport to crypto hash api (Eric Sandeen ) [228341]
- [fs] ecryptfs: backport to rhel5 cipher api (Eric Sandeen ) [228341]
- [fs] ecryptfs: un-constify ops vectors (Eric Sandeen ) [228341]
- [fs] ecryptfs: convert to memclear_highpage_flush (Eric Sandeen ) [228341]
- [fs] ecryptfs: backport to rhel5 memory alloc api (Eric Sandeen ) [228341]
- [fs] ecryptfs: backport sysf API for kobjects/ksets (Eric Sandeen ) [228341]
- [fs] ecryptfs: backport generic_file_aio_read (Eric Sandeen ) [228341]
- [fs] ecryptfs: backport f_path to f_dentry (Eric Sandeen ) [228341]
- [fs] ecryptfs: convert to vfsmount/dentry (Eric Sandeen ) [228341]
- [fs] ecryptfs: stacking functions from upstream vfs (Eric Sandeen ) [228341]
- [fs] ecryptfs: backport from 2.6.24-rc4 (Eric Sandeen ) [228341]
- [firewire] fix uevent to handle hotplug (Jay Fenlason ) [302981]
- [cpufreq] fix non-smp compile and warning (Prarit Bhargava ) [413941]
- [net] r8169: support realtek 8111c and 8101e loms (Ivan Vecera ) [276421 251259 248534 247142 238187]
- specfile: xen - see more than 32 vpcus on x86_64 (Bill Burns) [228572]
- specfile: cleanups, add new build options (Jarod Wilson) [248753 232602 247118]

* Wed Jan 09 2008 Don Zickus <dzickus@redhat.com> [2.6.18-66.el5]
- Fixes: [lockdep] lockstat: core infrastructure (Peter Zijlstra ) [193729]

* Wed Jan 09 2008 Don Zickus <dzickus@redhat.com> [2.6.18-65.el5]
- [audit] add session id to easily correlate records (Eric Paris ) [242813]
- [audit] log uid, auid, and comm in obj_pid records (Eric Paris ) [284531]
- [net] cxgb3: update to latest upstream (Andy Gospodarek ) [253195]
- [net] bnx2x: support Broadcom 10GbE Hardware (Andy Gospodarek ) [253346]
- [misc] enable i2c-piix4 (Bhavana Nagendra ) [424531]
- [net] ixgbe: support for new Intel 10GbE Hardware (Andy Gospodarek ) [252005]
- [net] iwl4965 updates (John W. Linville ) [252981]
- [net] mac80211 updates (John W. Linville ) [253015]
- [net] cfg80211 updates to support mac80211/iwl4965 (John W. Linville ) [252981]
- [net] infrastructure updates to mac80211/iwl4965 (John W. Linville ) [252981 253015 253027 256001]
- [net] NULL dereference in iwl driver (Vitaly Mayatskikh ) [401431] {CVE-2007-5938}
- [scsi] iscsi_tcp update (Mike Christie ) [253989 245823]
- [aio] account for I/O wait properly (Jeff Moyer ) [253337]
- [alsa] disabling microphone in bios panics kernel (John Feeney ) [240783]
- [lockdep] make cli/sti annotation warnings clearer (Peter Zijlstra ) [193729]
- [lockdep] fixup mutex annotations (Peter Zijlstra ) [193729]
- [lockdep] mismatched lockdep_depth/curr_chain_hash (Peter Zijlstra ) [193729]
- [lockdep] avoid lockdep & lock_stat infinite output (Peter Zijlstra ) [193729]
- [lockdep] lockstat: documentation (Peter Zijlstra ) [193729]
- [lockdep] lockstat: better class name representation (Peter Zijlstra ) [193729]
- [lockdep] lockstat: measure lock bouncing (Peter Zijlstra ) [193729]
- [lockdep] fixup sk_callback_lock annotation (Peter Zijlstra ) [193729]
- [lockdep] various fixes (Peter Zijlstra ) [193729]
- [lockdep] lockstat: hook into the lock primitives (Peter Zijlstra ) [193729]
- [lockdep] lockstat: human readability tweaks (Peter Zijlstra ) [193729]
- [lockdep] lockstat: core infrastructure (Peter Zijlstra ) [193729]
- [lockdep] sanitise CONFIG_PROVE_LOCKING (Peter Zijlstra ) [193729]
- [misc] fix raw_spinlock_t vs lockdep (Peter Zijlstra ) [193729]
- [alsa] support for realtek alc888s (Brian Maly ) [251253]
- [xen] save/restore: pv oops when mmap prot_none (Chris Lalancette ) [294811]
- [net] dod ipv6 conformance (Neil Horman ) [253278]
- [audit] log eintr, not erestartsys (Eric Paris ) [234426]
- [misc] ipmi: panic handling enhancement (Geoff Gustafson ) [277121]
- [misc] fix softlockup warnings/crashes (Chris Lalancette ) [250994]
- [misc] core dump masking support (Takahiro Yasui ) [223616]
- [fs] executing binaries with >2GB debug info (Dave Anderson ) [224679]
- [sched] return first time_slice to correct process (Vitaly Mayatskikh ) [238035]

* Tue Jan 08 2008 Don Zickus <dzickus@redhat.com> [2.6.18-64.el5]
- Fixes: [kexec] fix vmcoreinfo patch that breaks kdump (Neil Horman ) [424511]
- Fixes: [fs] nfs: byte-range locking support for cfs (Konrad Rzeszutek ) [196318]

* Mon Jan 07 2008 Don Zickus <dzickus@redhat.com> [2.6.18-63.el5]
- [scsi] lpfc:  update to version 8.2.0.13 (Chip Coldwell ) [426281]
- [scsi] qla2xxx: rediscovering luns takes 5 min (Marcus Barrow ) [413211]
- [misc] edac: add support for intel 5000 mchs (Aristeu Rozanski ) [249335]
- [fs] ext3: error in ext3_lookup if corruption found (Eric Sandeen ) [181662]
- [scsi] stex: use resid for xfer len information (Prarit Bhargava ) [251557]
- [scsi] qla2xxx: msi-x hardware issues on platforms (Marcus Barrow ) [253629]
- [net] ipv6: ip6_mc_input: sense of promiscuous test (Neil Horman ) [390071]
- [x86] Add warning to nmi failure message (Prarit Bhargava ) [401631]
- [misc] enable s/pdif in fila/converse (John Feeney ) [240783]
- [scsi] qla2xxx: add support for npiv - firmware (Marcus Barrow ) [249618]
- [scsi] qla2xxx: pci ee error handling support (Marcus Barrow ) [253267]
- [scsi] qla2xxx: add support for npiv (Marcus Barrow ) [249618]
- [scsi] mpt fusion: fix sas hotplug (Chip Coldwell ) [253122]
- [misc] export radix-tree-preload (George Beshers ) [422321]
- [net] forcedeth: boot delay fix (Andy Gospodarek ) [405521]
- [kexec] fix vmcoreinfo patch that breaks kdump (Neil Horman ) [424511]
- Revert: [misc] add vmcoreinfo support to kernel (Neil Horman ) [253850]
- [scsi] mpt fusion: update to version 3.04.05+ (Chip Coldwell ) [253122]
- [scsi] mpt fusion: add accessor for version 3.04.05+ (Chip Coldwell ) [253122]
- [scsi] mpt fusion: pci ids for version 3.04.05+ (Chip Coldwell ) [253122]
- [misc] offlining a CPU with realtime process running (Michal Schmidt ) [240232]
- [misc] ioat dma: support unisys (Ivan Vecera ) [248767]
- [md] dm ioctl: fix 32bit compat layer (Milan Broz ) [360441]
- [ppc64] enable CONFIG_FB_RADEON (Scott Moser ) [281141]
- [audit] race checking audit_context and loginuid (Eric Paris ) [241728]
- [scsi] update megaraid_sas to version 3.15 (Tomas Henzl ) [243154]
- [x86_64] calioc2 iommu support (Konrad Rzeszutek ) [253302]
- [x86] cpuinfo: list dynamic acceleration technology (Geoff Gustafson ) [252229]
- [ppc64] unequal allocation of hugepages (Scott Moser ) [239790]
- [md] fix bitmap support (Doug Ledford ) [210178]
- [misc] tlclk driver for telco blade systems (Geoff Gustafson ) [233512]
- [fs] nfs: byte-range locking support for cfs (Konrad Rzeszutek ) [196318]
- [x86_64] nmi watchdog: incorrect logic for amd chips (Prarit Bhargava ) [391741]
- [x86] edac: add support for Intel i3000 (Aristeu Rozanski ) [295501]
- [mm] fix hugepage allocation with memoryless nodes (Scott Moser ) [239790]
- [mm] make compound page destructor handling explicit (Scott Moser ) [239790]
- [scsi] qla2xxx: more improvements and cleanups part2 (Marcus Barrow ) [253272]
- [scsi] qla2xxx: 8 GB/S support (Marcus Barrow ) [249796]
- [scsi] qla2xxx: upstream improvements and cleanups (Marcus Barrow ) [253272]
- [ppc64] ehea: sync with upstream (Scott Moser ) [253414]
- [ia64] fix kernel warnings from rpm prep stage (Luming Yu ) [208271]

* Thu Dec 20 2007 Don Zickus <dzickus@redhat.com> [2.6.18-62.el5]
- [xen] ia64: hvm guest memory range checking (Jarod Wilson ) [408711]
- [xen] x86: support for architectural pstate driver (Bhavana Nagendra ) [419171]
- [xen] disable cpu freq scaling when vcpus is small (Rik van Riel ) [251969]
- [xen] hv: cpu frequency scaling (Rik van Riel ) [251969]
- [xen] ia64: vulnerability of copy_to_user in PAL emu (Jarod Wilson ) [425939]
- [net] bonding: documentation update (Andy Gospodarek ) [235711]
- [net] bonding: update to upstream version 3.2.2 (Andy Gospodarek ) [251902 236750 268001]
- [misc] utrace: update for 5.2 (Roland McGrath ) [299941 309461 309551 309761]
- [ia64] ptrace: access to user register backing (Roland McGrath ) [237749]
- [ia64] utrace: forbid ptrace changes psr.ri to 3 (Roland McGrath ) [247174]
- [net] bnx2: update to upstream version 1.6.9 (Andy Gospodarek ) [251109]
- [net] tg3: update to upstream version 3.86 (Andy Gospodarek ) [253344]
- [net] sunrpc: make clients take ref to rpciod workq (Jeff Layton ) [246642]
- [scsi] aacraid: update to 1.1.5-2453 (Chip Coldwell ) [364371]
- [md] dm-mirror: write_callback might deadlock (Jonathan Brassow ) [247877]
- [md] dm-mirror: shedule_timeout call causes slowdown (Jonathan Brassow ) [358881]
- [md] mirror presuspend causing cluster mirror hang (Jonathan Brassow ) [358871]
- [acpi] docking/undocking: oops when _DCK eval fails (John Feeney ) [252214]
- [acpi] docking/undocking: check if parent is on dock (John Feeney ) [252214]
- [acpi] docking/undocking: error handling in init (John Feeney ) [252214]
- [acpi] docking/undocking: add sysfs support (John Feeney ) [252214]
- [acpi] docking/undocking support (John Feeney ) [252214]
- [xen] support for architectural pstate driver (Bhavana Nagendra ) [419171]
- [usb] wacom: fix 'side' and 'extra' mouse buttons (Aristeu Rozanski ) [249415]
- [audit] netmask on xfrm policy configuration changes (Eric Paris ) [410531]
- [xen] rapid block device plug/unplug leads to crash (Don Dutile ) [308971]
- [net] fix refcnt leak in optimistic dad handling (Neil Horman ) [423791]
- [net] ixgb: resync upstream and transmit hang fixes (Andy Gospodarek ) [252002]
- [xen] kernel: cpu frequency scaling (Rik van Riel ) [251969]
- [md] dm snapshot: excessive memory usage (Milan Broz ) [421451]
- [md] dm-crypt: possible max_phys_segments violation (Milan Broz ) [421441]
- [xen] xenbus has use-after-free (Don Dutile ) [249728]
- [fs] cifs: update CHANGES file and version string (Jeff Layton ) [417961]
- [fs] cifs: endian conversion problem in posix mkdir (Jeff Layton ) [417961]
- [fs] cifs: corrupt data with cached dirty page write (Jeff Layton ) [329431]
- [fs] cifs: missing mount helper causes wrong slash (Jeff Layton ) [417961]
- [fs] cifs: fix error message about packet signing (Jeff Layton ) [417961]
- [fs] cifs: shut down cifsd when signing mount fails (Jeff Layton ) [417961]
- [fs] cifs: reduce corrupt list in find_writable_file (Jeff Layton ) [417961]
- [fs] cifs: fix memory leak in statfs to old servers (Jeff Layton ) [417961]
- [fs] cifs: buffer overflow due to corrupt response (Jeff Layton ) [373001]
- [fs] cifs: log better errors on failed mounts (Jeff Layton ) [417961]
- [fs] cifs: oops on second mount to same server (Jeff Layton ) [373741]
- [fs] cifs: fix spurious reconnect on 2nd peek (Jeff Layton ) [417961]
- [fs] cifs: bad handling of EAGAIN on kernel_recvmsg (Jeff Layton ) [336501]
- [fs] cifs: small fixes to make cifs-1.50c compile (Jeff Layton ) [417961]
- [net] cifs: stock 1.50c import (Jeff Layton ) [417961]
- [nfs4] client: set callback address properly (Steve Dickson ) [264721]
- [sched] fair scheduler (Peter Zijlstra ) [250589]
- [net] s2io: correct VLAN frame reception (Andy Gospodarek ) [354451]
- [net] s2io: allow VLAN creation on interfaces (Andy Gospodarek ) [354451]
- [mm] soft lockups when allocing mem on large systems (Doug Chapman ) [281381]
- [md] dm mpath: hp retry if not ready (Dave Wysochanski ) [208261]
- [md] dm mpath: add retry pg init (Dave Wysochanski ) [208261]
- [md] dm mpath: add hp handler (Dave Wysochanski ) [208261]
- [x86] fix race with 'endflag' in NMI setup code (Prarit Bhargava ) [357391]
- [xen] fix behavior of invalid guest page mapping (Markus Armbruster ) [254208]
- [misc] tux: get rid of O_ATOMICLOOKUP (Michal Schmidt ) [358661]
- [misc] Denial of service with wedged processes (Jerome Marchand ) [229882]
- [x86_64] fix race conditions in setup_APIC_timer (Geoff Gustafson ) [251869]

* Sat Dec 15 2007 Don Zickus <dzickus@redhat.com> [2.6.18-61.el5]
- [net] sunhme: fix failures on x86 (John W. Linville ) [254234]
- [ppc64] power6 SPURR support (Scott Moser ) [253114]
- [usb] fix for error path in rndis (Pete Zaitcev ) [236719]
- [ipmi] legacy ioport setup changes (Peter Martuccelli ) [279191]
- [ipmi] add PPC SI support (Peter Martuccelli ) [279191]
- [ipmi] remove superfluous semapahore from watchdog (Peter Martuccelli ) [279191]
- [ipmi] do not enable interrupts too early (Peter Martuccelli ) [279191]
- [ipmi] fix memory leak in try_init_dmi (Peter Martuccelli ) [279191]
- [net] sunrpc: lockd recovery is broken (Steve Dickson ) [240976]
- [fs] core dump file ownership (Don Howard ) [397001]
- [cpufreq] don't take sem in cpufreq_quick_get (Doug Chapman ) [253416]
- [cpufreq] remove hotplug cpu cruft (Doug Chapman ) [253416]
- [cpufreq] governor: use new rwsem locking in work cb (Doug Chapman ) [253416]
- [cpufreq] ondemand governor restructure the work cb (Doug Chapman ) [253416]
- [cpufreq] rewrite lock to eliminate hotplug issues (Doug Chapman ) [253416]
- [ppc64] spufs: context destroy vs readdir race (Scott Moser ) [387841]
- [scsi] update lpfc driver to 8.2.0.8 (Chip Coldwell ) [252989]
- [ppc64] utrace: fix PTRACE_GETVRREGS data (Roland McGrath ) [367221]
- [scsi] ipr: add dual SAS RAID controller support (Scott Moser ) [253398]
- [net] backport of functions for sk_buff manipulation (Andy Gospodarek ) [385681]
- [gfs2] recursive locking on rgrp in gfs2_rename (Abhijith Das ) [404711]
- [gfs2] check kthread_should_stop when waiting (David Teigland ) [404571]
- [dlm] don't print common non-errors (David Teigland ) [404561]
- [dlm] tcp: bind connections from known local address (David Teigland ) [358841]
- [dlm] block dlm_recv in recovery transition (David Teigland ) [358821]
- [dlm] fix memory leak in dlm_add_member (David Teigland ) [358791]
- [dlm] zero unused parts of sockaddr_storage (David Teigland ) [358771]
- [dlm] dump more lock values (David Teigland ) [358751]
- [gfs2] remove permission checks from xattr ops (Ryan O'Hara ) [307431]
- [x86] report_lost_ticks fix up (Prarit Bhargava ) [394581]
- [ppc64] SLB shadow buffer support (Scott Moser ) [253112]
- [ppc64] handle alignment faults on new FP load/store (Scott Moser ) [253111]
- [xen] PVFB frontend can send bogus screen updates (Markus Armbruster ) [370341]
- [nfs] let rpciod finish sillyrename then umount (Steve Dickson ) [253663]
- [nfs] fix a race in silly rename (Steve Dickson ) [253663]
- [nfs] clean up the silly rename code (Steve Dickson ) [253663]
- [nfs] infrastructure changes for silly renames (Steve Dickson ) [253663]
- [nfs] introducde nfs_removeargs and nfs_removeres (Steve Dickson ) [253663]
- [xen] avoid dom0 hang when disabling pirq's (Chris Lalancette ) [372741]
- [ppc64] cell: support for msi on axon (Scott Moser ) [253212]
- [ppc64] cell: enable rtas-based ptcal for xdr memory (Scott Moser ) [253212]
- [ppc64] cell: ddr2 memory driver for axon (Scott Moser ) [253212]
- [ppc64] spu: add temperature and throttling support (Scott Moser ) [279171]
- [ppc64] sysfs: support for add/remove cpu sysfs attr (Scott Moser ) [279171]
- [ppc64] cbe_cpufreq: fixes from 2.6.23-rc7 (Scott Moser ) [279171]
- [ppc64] typo with mmio_read_fixup (Scott Moser ) [253208]
- [ppc64] spufs: feature updates (Scott Moser ) [253208]
- [ppc64] export last_pid (Scott Moser ) [253208]
- [ppc64] cell: support pinhole-reset on blades (Scott Moser ) [253208]
- [s390] use IPL CLEAR for reipl under z/VM (Hans-Joachim Picht ) [386991]
- [net] sunrpc: fix hang due to eventd deadlock (Jeff Layton ) [246642]
- [misc] : misrouted interrupts deadlocks (Dave Anderson ) [247379]
- [fs] ignore SIOCIFCOUNT ioctl calls (Josef Bacik ) [310011]
- [ppc64] fixes PTRACE_SET_DEBUGREG request (Roland McGrath ) [253117]
- [fs] dm crypt: memory leaks and workqueue exhaustion (Milan Broz ) [360621]
- [md] dm: panic on shrinking device size (Milan Broz ) [360151]
- [md] dm: bd_mount_sem counter corruption (Milan Broz ) [360571]
- [fs] udf: fix possible leakage of blocks (Eric Sandeen ) [221282]
- [fs] udf: Fix possible data corruption (Eric Sandeen ) [221282]
- [fs] udf: support files larger than 1G (Eric Sandeen ) [221282]
- [fs] udf: add assertions (Eric Sandeen ) [221282]
- [fs] udf: use get_bh (Eric Sandeen ) [221282]
- [fs] udf: introduce struct extent_position (Eric Sandeen ) [221282]
- [fs] udf: use sector_t and loff_t for file offsets (Eric Sandeen ) [221282]
- [misc] use touch_softlockup_watchdog when no nmi wd (Prarit Bhargava ) [367251]
- [misc] backport upstream softlockup_tick code (Prarit Bhargava ) [367251]
- [misc] pass regs struct to softlockup_tick (Prarit Bhargava ) [336541]
- [misc] fix bogus softlockup warnings (Prarit Bhargava ) [252360]
- [x86] use pci=bfsort for certain boxes (Michal Schmidt ) [242990]
- [x86] Change command line size to 2048 (Prarit Bhargava ) [247477]
- [misc] systemtap uprobes: access_process_vm export (Frank Ch. Eigler ) [424991]
- [nfs] fix ATTR_KILL_S*ID handling on NFS (Jeff Layton ) [222330]
- [mm] oom: prevent from killing several processes (Larry Woodman ) [392351]

* Fri Dec 14 2007 Don Zickus <dzickus@redhat.com> [2.6.18-60.el5]
- [xen] x86: suppress bogus timer warning (Chris Lalancette ) [317201]
- [xen] ia64: saner default mem and cpu alloc for dom0 (Jarod Wilson ) [248967]
- [xen] x86_64: add stratus hooks into memory (Kimball Murray ) [247833]
- [ia64] mm: register backing store bug (Luming Yu ) [310801]
- [serial] irq -1 assigned to serial port (Luming Yu ) [227728]
- [utrace] s390 regs fixes (Roland McGrath ) [325451]
- [x86] use pci=bfsort on Dell R900 (Michal Schmidt ) [242990]
- [nfs] server support 32-bit client and 64-bit inodes (Peter Staubach ) [253589]
- [nfs] support 32-bit client and 64-bit inode numbers (Peter Staubach ) [253589]
- [dlm] Don't overwrite castparam if it's NULL (Patrick Caulfield ) [318061]
- [s390] panic with lcs interface as dhcp server (Hans-Joachim Picht ) [350861]
- [s390] qeth: do not free memory on failed init (Hans-Joachim Picht ) [330211]
- [s390] qeth: default performace_stats attribute to 0 (Hans-Joachim Picht ) [248897]
- [s390] qeth: create copy of skb for modification (Hans-Joachim Picht ) [354861]
- [s390] qeth: up sequence number for incoming packets (Hans-Joachim Picht ) [354851]
- [s390] qeth: use correct MAC address on recovery (Hans-Joachim Picht ) [241276]
- [s390] cio: handle invalid subchannel setid in stsch (Hans-Joachim Picht ) [354831]
- [s390] cio: Dynamic CHPID reconfiguration via SCLP (Hans-Joachim Picht ) [253120]
- [s390] cio: fix memory leak when deactivating (Hans-Joachim Picht ) [213272]
- [s390] cio: Device status validity (Hans-Joachim Picht ) [354821]
- [s390] cio: reipl fails after channel path reset (Hans-Joachim Picht ) [231306]
- [usb] reset LEDs on Dell keyboards (Pete Zaitcev ) [228674]
- [x86] hotplug: PCI memory resource mis-allocation (Konrad Rzeszutek ) [252260]
- [ppc64] Make the vDSO handle C++ unwinding correctly (David Howells ) [420551]
- [ppc64] add AT_NULL terminator to auxiliary vector (Vitaly Mayatskikh ) [231442]
- [x86] Add Greyhound Event based Profiling support (Bhavana Nagendra ) [314611]
- [nfs] reset any fields set in attrmask (Jeff Layton ) [242482]
- [nfs] Set attrmask on NFS4_CREATE_EXCLUSIVE reply (Jeff Layton ) [242482]
- [fs] proc: add /proc/<pid>/limits (Neil Horman ) [253762]
- [xen] ia64: make ioremapping work (Jarod Wilson ) [240006]
- [ia64] bte_unaligned_copy transfers extra cache line (Luming Yu ) [218298]
- [xen] inteface with stratus platform op (Kimball Murray ) [247841]
- [mm] xen: export xen_create_contiguous_region (Kimball Murray ) [247839]
- [mm] xen: memory tracking cleanups (Kimball Murray ) [242514]

* Tue Dec 11 2007 Don Zickus <dzickus@redhat.com> [2.6.18-59.el5]
- [net] ipv6: backport optimistic DAD (Neil Horman ) [246723]
- [crypto] aes: Rename aes to aes-generic (Herbert Xu ) [245954]
- [xen] ia64: fix free_irq_vector: double free (Aron Griffis ) [208599]
- [selinux] don't oops when using non-MLS policy (Eric Paris ) [223827]
- [net] qla3xxx: new 4032 does not work with VLAN (Marcus Barrow ) [253785]
- [ide] SB700 contains two IDE channels (Bhavana Nagendra ) [314571]
- [edac] fix return code in e752x_edac probe function (Aristeu Rozanski ) [231608]
- [scsi] cciss: disable refetch on P600 (Aron Griffis ) [251563]
- [misc] Intel Tolapai SATA and I2C support (Ivan Vecera ) [251086]
- [net] ibmveth: Checksum offload support (Scott Moser ) [254035]
- [misc] Allow a hyphenated range for isolcpus (Jonathan Lim ) [328151]
- [misc] sched: force /sbin/init off isolated cpus (Jonathan Lim ) [328091]
- [ia64] contig: show_mem cleanup output (George Beshers ) [221612]
- [ia64] discontig: show_mem cleanup output (George Beshers ) [221612]
- [ia64] show_mem printk cleanup (George Beshers ) [221612]
- [net] ppp_mppe: avoid using a copy of interim key (Michal Schmidt ) [248716]
- [ppc64] mpstat reports wrong per-processor stats (Scott Moser ) [212234]
- [net] labeled: memory leak calling secid_to_secctx (Eric Paris ) [250442]
- [misc] /proc/<pid>/environ stops at 4k bytes (Anton Arapov ) [308391]
- [net] kernel needs to support TCP_RTO_MIN (Anton Arapov ) [303011]
- [x86_64] kdump: shutdown gart on k8 systems (Prarit Bhargava ) [264601]
- [input] psmouse: add support to 'cortps' protocol (Aristeu Rozanski ) [248759]
- [nfs] nfs_symlink: allocate page with GFP_HIGHUSER (Jeff Layton ) [245042]
- [ia64] enable kprobe's trap code on slot 1 (Masami Hiramatsu ) [207107]
- [misc] Fix relay read start in overwrite mode (Masami Hiramatsu ) [250706]
- [misc] Fix relay read start position (Masami Hiramatsu ) [250706]
- [x86_64] 'ide0=noprobe' crashes the kernel (Michal Schmidt ) [241338]
- [ia64] proc/iomem wiped out on non ACPI kernel (George Beshers ) [257001]
- [net] CIPSO packets generate kernel unaligned access (Luming Yu ) [242955]
- [ia64] ioremap: fail mmaps with incompat attributes (Jarod Wilson ) [240006]
- [ia64] ioremap: allow cacheable mmaps of legacy_mem (Jarod Wilson ) [240006]
- [ia64] ioremap: avoid unsupported attributes (Jarod Wilson ) [240006]
- [ia64] ioremap: rename variables to match i386 (Jarod Wilson ) [240006]
- [ia64] validate and remap mmap requests (Jarod Wilson ) [240006]
- [ia64] kdump: deal with empty image (Doug Chapman ) [249724]
- [net] NetXen: allow module to unload (Konrad Rzeszutek ) [245751]
- [net] clean up in-kernel socket api usage (Neil Horman ) [246851]
- [hotplug] slot poweroff problem on systems w/o _PS3 (Prarit Bhargava ) [410611]
- [PPC64] kdump: fix irq distribution on ppc970 (Jarod Wilson ) [208659]
- [serial] support PCI Express icom devices (Chris Snook ) [243806]
- [xen] Rebase HV to 15502 (Bill Burns) [318891]

* Wed Nov 27 2007 Don Zickus <dzickus@redhat.com> [2.6.18-58.el5]
- Updated: [net] panic when mounting with insecure ports (Anton Arapov ) [294881]
- [kabitool] - fail on missing symbols (Jon Masters)

* Wed Nov 21 2007 Don Zickus <dzickus@redhat.com> [2.6.18-57.el5]
- [misc] lockdep: fix seqlock_init (Peter Zijlstra ) [329851]
- [ppc64] Remove WARN_ON from disable_msi_mode() (Scott Moser ) [354241]
- [GFS2] sysfs  file should contain device id (Bob Peterson ) [363901]
- [x86_64] update IO-APIC dest field to 8-bit for xAPIC (Dave Anderson ) [224373]
- [ia64] add global ACPI OpRegion handler for fw calls (Doug Chapman ) [262281]
- [ia64] add driver for ACPI methods to call native fw (Doug Chapman ) [262281]
- [ppc64] eHEA: ibm,loc-code not unique (Scott Moser ) [271821]
- [ata] SB800 SATA/IDE LAN support (Bhavana Nagendra ) [252961]
- [net] ibmveth: enable large rx buf pool for large mtu (Scott Moser ) [250827]
- [net] ibmveth: h_free_logical_lan err on pool resize (Scott Moser ) [250827]
- [net] ibmveth: fix rx pool deactivate oops (Scott Moser ) [250827]
- [gfs2] Fix ordering of page lock and transaction lock (Steven Whitehouse ) [303351]
- [net] panic when mounting with insecure ports (Anton Arapov ) [294881]
- [ia64] fix vga corruption with term blanking disabled (Jarod Wilson ) [291421]
- [ppc64] panic on DLPAR remove of eHEA (Scott Moser ) [253767]
- [ppc64] boot Cell blades with >2GB memory (Scott Moser ) [303001]
- [x86_64] Add NX mask for PTE entry (Jarod Wilson ) [232748]
- [hotplug] acpiphp: System error during PCI hotplug (Konrad Rzeszutek ) [243003]
- [misc] softirq: remove spurious BUG_ON's (Jarod Wilson ) [221554]
- [audit] collect events for segfaulting programs (Eric Paris ) [239061]
- [misc] cfq-iosched: fix deadlock on nbd writes (Jarod Wilson ) [241540]
- [scsi] stale residual on write following BUSY retry (Jonathan Lim ) [300871]
- ext3: orphan list check on destroy_inode (Eric Sandeen ) [269401]
- [scsi] always update request data_len with resid (George Beshers ) [282781]
- [misc] add vmcoreinfo support to kernel (Neil Horman ) [253850]
- [ia64] remove stack hard limit (Aron Griffis ) [251043]
- [fs] Fix unserialized task->files changing (Vitaly Mayatskikh ) [253866]
- [ide] allow disabling of drivers (Gerd Hoffmann ) [247982]
- [net] fail multicast with connection oriented socket (Anton Arapov ) [259261]
- [net] fix race condition in netdev name allocation (Neil Horman ) [247128]
- [char] tty: set pending_signal on return -ERESTARTSYS (Aristeu Rozanski ) [253873]
- [fs] aio: account for I/O wait properly (Jeff Moyer ) [253337]
- [x86_64] Switching to vsyscall64 causes oops (Jeff Burke ) [224541]
- [net] lvs syncdaemon causes high avg load on system (Anton Arapov ) [245715]
- [i2c] SB600/700/800 use same SMBus controller devID (Bhavana Nagendra ) [252286]
- [acpi] sbs: file permissions set incorrectly (Vitaly Mayatskikh ) [242565]
- [net] ipv6: support RFC4193 local unicast addresses (Neil Horman ) [252264]
- [misc] serial: fix console hang on HP Integrity (Doug Chapman ) [244054]
- [tux] fix crashes during shutdown (Ernie Petrides ) [244439]
- [usb] Support for EPiC-based io_edgeport devices (Jarod Wilson ) [249760]
- [misc] Prevent NMI watchdog triggering during sysrq-T (Konrad Rzeszutek ) [248392]
- [hotplug] acpiphp: 'cannot get bridge info' with PCIe (Konrad Rzeszutek ) [248571]
- [misc] serial: assert DTR for serial console devices (Michal Schmidt ) [244728]
- [net] sctp: rewrite receive buffer management code (Neil Horman ) [246722]
- [net] NetXen: MSI: failed interrupt after fw enabled (Konrad Rzeszutek ) [246019]
- [cifs] make demux thread ignore signals from userspace (Jeff Layton ) [245674]
- [ia64] misc DBS cleanup (Luming Yu ) [245217]
- [misc] Remove non-existing SB600 raid define (Prarit Bhargava ) [244038]

* Tue Nov 13 2007 Don Zickus <dzickus@redhat.com> [2.6.18-56.el5]
- [fs] missing dput in do_lookup error leaks dentries (Eric Sandeen ) [363491] {CVE-2007-5494}
- [ppc] System cpus stuck in H_JOIN after migrating (Scott Moser ) [377901]
- [scsi] ibmvSCSI: Unable to continue migrating lpar after errors (Scott Moser ) [377891]
- [scsi] ibmvSCSI: client can't handle deactive/active device from server (Scott Moser ) [257321]
- [audit] still allocate contexts when audit is disabled (Alexander Viro ) [360841]

* Tue Nov 06 2007 Don Zickus <dzickus@redhat.com> [2.6.18-55.el5]
- Revert [misc] Denial of service with wedged processes (Jerome Marchand ) [229882] {CVE-2006-6921}
- [autofs4] fix race between mount and expire (Ian Kent ) [354621]
- [net] ieee80211: off-by-two integer underflow (Anton Arapov ) [346401] {CVE-2007-4997}
- [fs] sysfs: fix race condition around sd->s_dentry (Eric Sandeen ) [243728] {CVE-2007-3104}
- [fs] sysfs: fix condition check in sysfs_drop_dentry() (Eric Sandeen ) [243728] {CVE-2007-3104}
- [fs] sysfs: store inode nrs in s_ino (Eric Sandeen ) [243728] {CVE-2007-3104}
- [nfs] v4: umounts oops in shrink_dcache_for_umount (Steve Dickson ) [254106]
- [net] tg3: Fix performance regression on 5705 (Andy Gospodarek ) [330181]
- [net] forcedeth: MSI interrupt bugfix (Andy Gospodarek ) [353281]
- [ppc] kexec/kdump kernel hung on Power5+ and Power6 (Scott Moser ) [245346]

* Mon Oct 22 2007 Don Zickus <dzickus@redhat.com> [2.6.18-54.el5]
- [misc] Denial of service with wedged processes (Jerome Marchand ) [229882] {CVE-2006-6921}
- [alsa] Convert snd-page-alloc proc file to use seq_file (Jerome Marchand ) [297771] {CVE-2007-4571}
- [x86] Fixes for the tick divider patch (Chris Lalancette ) [315471]
- [mm] ia64: flush i-cache before set_pte (Luming Yu ) [253356]
- [fs] jbd: wait for t_sync_datalist buffer to complete (Eric Sandeen ) [250537]
- [audit] improper handling of audit_log_start return values (Eric Paris ) [335731]
- [cifs] fix memory corruption due to bad error handling (Jeff Layton ) [336501]
- [net] bnx2: Add PHY workaround for 5709 A1 (Andy Gospodarek ) [317331]

* Wed Oct 10 2007 Don Zickus <dzickus@redhat.com> [2.6.18-53.el5]
- [GFS2] handle multiple demote requests (Wendy Cheng ) [295641]
- [scsi] megaraid_sas: kabi fix for /proc entries (Chip Coldwell ) [323231]
- [sound] allow creation of null parent devices (Brian Maly ) [323771]

* Wed Sep 26 2007 Don Zickus <dzickus@redhat.com> [2.6.18-52.el5]
- [net] iwlwifi: avoid BUG_ON in tx cmd queue processing (John W. Linville ) [306831]
- [GFS2] Get super block a different way (Steven Whitehouse ) [306621]

* Tue Sep 25 2007 Don Zickus <dzickus@redhat.com> [2.6.18-51.el5]
- [GFS2] dlm: schedule during recovery loops (David Teigland ) [250464]
- Revert: [pata] IDE (siimage) panics when DRAC4 reset (John Feeney ) [212391]

* Mon Sep 24 2007 Don Zickus <dzickus@redhat.com> [2.6.18-50.el5]
- Revert: [net] bonding: convert timers to workqueues (Andy Gospodarek ) [210577]
- [pata] enable IDE (siimage) DRAC4 (John Feeney ) [212391]
- [GFS2] gfs2_writepage(s) workaround (Wendy Cheng ) [252392]
- [scsi] aacraid: Missing ioctl() permission checks (Vitaly Mayatskikh ) [298381] {CVE-2007-4308}
- [GFS2] Solve journaling/{release|invalidate}page issues (Steven Whitehouse ) [253008]
- [x86_64] syscall vulnerability (Anton Arapov ) [297881] {CVE-2007-4573}
- [GFS2] Fix i_cache stale entry (Wendy Cheng ) [253756]
- [GFS2] deadlock running revolver load with lock_nolock (Benjamin Marzinski ) [288581]
- [net] s2io: check for error_state in ISR (more) (Scott Moser ) [276871]

* Thu Sep 20 2007 Don Zickus <dzickus@redhat.com> [2.6.18-49.el5]
- [sata] libata probing fixes and other cleanups (Jeff Garzik ) [260281]
- [net] cxgb3: backport fixups and sysfs corrections (Andy Gospodarek ) [252243]

* Mon Sep 17 2007 Don Zickus <dzickus@redhat.com> [2.6.18-48.el5]
- [net] s2io: check for error_state in ISR (Scott Moser ) [276871]
- [fs] ext3: ensure do_split leaves enough free space in both blocks (Eric Sandeen ) [286501]
- [kabi] whitelist GFS2 export symbols to allow driver updates (Jon Masters) [282901]
- [gfs2] allow process to handle multiple flocks on a file (Abhijith Das ) [272021]
- [gfs2] operations hang after mount--RESEND (Bob Peterson ) [276631]
- [scsi] qlogic: fix nvram/vpd update memory corruptions (Marcus Barrow ) [260701]
- [fs] Reset current->pdeath_signal on SUID binary execution (Peter Zijlstra) [251119] {CVE-2007-3848}
- [gfs2] mount hung after recovery (Benjamin Marzinski ) [253089]
- [GFS2] Move inode delete logic out of blocking_cb (Wendy Cheng ) [286821]
- [dlm] Make dlm_sendd cond_resched more (Patrick Caulfield ) [250464]
- [x86_64] fix 32-bit ptrace access to debug registers (Roland McGrath ) [247427]
- [autofs4] fix deadlock during directory create (Ian Kent ) [253231]
- [nfs] enable 'nosharecache' mounts fixes (Steve Dickson ) [243913]
- [usb] usblcd: Locally triggerable memory consumption (Anton Arapov ) [276011] {CVE-2007-3513}
- [misc] Bounds check ordering issue in random driver (Anton Arapov ) [275971] {CVE-2007-3105}

* Tue Sep 11 2007 Don Zickus <dzickus@redhat.com> [2.6.18-47.el5]
- [ppc64] Fix SPU slb size and invalidation on hugepage faults (Scott Moser ) [285981]
- [s390] qdio: Refresh buffer states for IQDIO Asynch output queue (Hans-Joachim Picht ) [222181]
- [scsi] fusion: allow VMWare's emulator to work again (Chip Coldwell ) [279571]

* Mon Sep 10 2007 Don Zickus <dzickus@redhat.com> [2.6.18-46.el5]
- [XEN] x86: 32-bit ASID mode hangs dom0 on AMD (Chris Lalancette ) [275371]
- [scsi] megaraid_sas: intercept cmd timeout and throttle io (Chip Coldwell ) [245184 247581]
- [s390] hypfs: inode corruption due to missing locking (Brad Hinson ) [254169]
- [Xen] Allow 32-bit Xen to kdump >4G physical memory (Stephen C. Tweedie ) [251341]
- [ptrace] NULL pointer dereference triggered by ptrace (Anton Arapov ) [275991] {CVE-2007-3731}
- [XEN] ia64: allocating with GFP_KERNEL in interrupt context fix (Josef Bacik ) [279141]

* Tue Sep 04 2007 Don Zickus <dzickus@redhat.com> [2.6.18-45.el5]
- [XEN] Update spec file to provide specific xen ABI version (Stephen C. Tweedie ) [271981]
- [scsi] qla2xxx: nvram/vpd updates produce soft lockups and system hangs (Marcus Barrow ) [260701]
- [scsi] iscsi: borked kmalloc  (Mike Christie ) [255841]
- [net] qla3xxx: Read iSCSI target disk fail (Marcus Barrow ) [246123]
- [net] igmp: check for NULL when allocating GFP_ATOMIC skbs (Neil Horman ) [252404]
- [mm] madvise call to kernel loops forever (Konrad Rzeszutek ) [263281]

* Mon Aug 27 2007 Don Zickus <dzickus@redhat.com> [2.6.18-44.el5]
- [misc] re-export some symbols as EXPORT_SYMBOL_GPL (Jon Masters ) [252377]
- [xen] ia64: set NODES_SHIFT to 8 (Doug Chapman ) [254050]
- [xen] Fix privcmd to remove nopage handler (Chris Lalancette ) [249409]
- [xen] increase limits to boot on large ia64 platforms (Doug Chapman ) [254062]
- [autofs] autofs4 - fix race between mount and expire (Ian Kent ) [236875]
- [nfs] NFS4: closes and umounts are racing (Steve Dickson ) [245062]
- [GFS2] Fix lock ordering of unlink (Steven Whitehouse ) [253609]
- [openib] Fix two ipath controllers on same subnet (Doug Ledford ) [253005]
- [net] tg3: update to fix suspend/resume problems (Andy Gospodarek ) [253988]
- [GFS2] distributed mmap test cases deadlock (Benjamin Marzinski ) [248480]
- [GFS2] Fix inode meta data corruption (Wendy Cheng ) [253590]
- [GFS2] bad mount option causes panic with NULL superblock pointer (Abhijith Das ) [253921]
- [fs] hugetlb: fix prio_tree unit (Konrad Rzeszutek ) [253930]
- [misc] Microphone stops working (John Feeney ) [240716]
- [GFS2] glock dump dumps glocks for all file systems (Abhijith Das ) [253238]
- [scsi] qla2xxx: disable MSI-X by default (Marcus Barrow ) [252410]

* Tue Aug 21 2007 Don Zickus <dzickus@redhat.com> [2.6.18-43.el5]
- [XEN] remove assumption first numa node discovered is node0 (Jarod Wilson ) [210078]

* Mon Aug 20 2007 Don Zickus <dzickus@redhat.com> [2.6.18-42.el5]
- [GFS2] More problems unstuffing journaled files (Bob Peterson ) [252191]
- [DLM] Reuse connections rather than freeing them (Patrick Caulfield ) [251179]
- [ppc] EEH: better status string detection (Scott Moser ) [252405]
- [scsi] cciss: set max command queue depth (Tomas Henzl ) [251167]
- [audit] Stop multiple messages from being printed (Eric Paris ) [252358]
- [scsi] uninitialized field in gdth.c (Chip Coldwell ) [245550]
- [scsi] SATA RAID 150-4/6 do not support 64-bit DMA (Chip Coldwell ) [248327]
- [gfs2] fix truncate panic (Wendy Cheng ) [251053]
- [gfs2] panic after can't parse mount arguments  (Benjamin Marzinski ) [253289]
- [fs] CIFS: fix deadlock in cifs_get_inode_info_unix (Jeff Layton ) [249394]
- [sound] support ad1984 codec (Brian Maly ) [252373]
- [scsi] fix iscsi write handling regression (Mike Christie ) [247827]
- [ppc] Fix detection of PCI-e based devices (Doug Ledford ) [252085]
- [gfs2] unstuff quota inode (Abhijith Das ) [250772]
- [net] fix DLPAR remove of eHEA logical port (Scott Moser ) [251370]
- [gfs2] hang when using a large sparse quota file (Abhijith Das ) [235299]
- [x86_64] Fix MMIO config space quirks (Bhavana Nagendra ) [252397]
- [misc] Convert cpu hotplug notifiers to use raw_notifier (Peter Zijlstra ) [238571]
- [sound] fix panic in hda_codec (Brian Maly ) [251854]
- [mm] separate mapped file and anonymous pages in show_mem() output. (Larry Woodman ) [252033]
- [misc] Fix broken AltSysrq-F (Larry Woodman ) [251731]
- [scsi] cciss: increase max sectors to 2048 (Tomas Henzl ) [248121]
- Revert [gfs2] remounting w/o acl option leaves acls enabled (Bob Peterson ) [245663]

* Thu Aug 16 2007 Don Zickus <dzickus@redhat.com> [2.6.18-41.el5]
- Revert [ia64] validate and remap mmap requests (Jarod Wilson ) [240006]

* Tue Aug 14 2007 Don Zickus <dzickus@redhat.com> [2.6.18-40.el5]
- [net] s2io: update to driver version 2.0.25.1 (Andy Gospodarek ) [223033]
- [XEN] ia64: use panic_notifier list (Kei Tokunaga ) [250456]
- [XEN] ia64: support nvram (Kei Tokunaga ) [250203]
- [XEN] Allow dom0 to boot with greater than 2 vcpus (Kei Tokunaga ) [250441]
- [XEN] Fix MCE errors on AMD-V (Bhavana Nagendra ) [251435]
- [XEN] set correct paging bit identifier when NP enabled (Chris Lalancette ) [250857]
- [XEN] ia64: fix for hang when running gdb (Doug Chapman ) [246482]
- [XEN] AMD-V fix for W2k3 guest w/ Nested paging (Bhavana Nagendra ) [250850]
- [XEN] blktap tries to access beyond end of disk (Kei Tokunaga ) [247696]
- [ia64] fsys_gettimeofday leaps days if it runs with nojitter (Luming Yu ) [250825]
- [x86] Blacklist for HP DL585G2 and HP dc5700 (Tony Camuso ) [248186]
- [misc] Missing critical phys_to_virt in lib/swiotlb.c (Anton Arapov ) [248102]
- [mm] Prevent the stack growth into hugetlb reserved regions (Konrad Rzeszutek ) [247658]
- [scsi] fix qla4xxx underrun and online handling (Mike Christie ) [242828]
- [sound] Audio playback does not work (John Feeney ) [250269]
- [XEN] ia64: allow guests to vga install (Jarod Wilson ) [249076]
- [net] forcedeth: optimize the tx data path (Andy Gospodarek ) [252034]
- [agp] 945/965GME: bridge id, bug fix, and cleanups (Geoff Gustafson ) [251166]
- [net] tg3: pci ids missed during backport (Andy Gospodarek ) [245135]
- [misc] workaround for qla2xxx vs xen swiotlb (Rik van Riel ) [219216]
- [XEN] netfront: Avoid deref'ing skb after it is potentially freed. (Herbert Xu ) [251905]
- [ia64] validate and remap mmap requests (Jarod Wilson ) [240006]
- [ppc] DLPAR REMOVE I/O resource failed (Scott Moser ) [249617]
- [XEN] ia64: Cannot use e100 and IDE controller (Kei Tokunaga ) [250454]
- [wireless] iwlwifi: update to version 1.0.0 (John W. Linville ) [223560 250675]
- [ppc] make eHCA driver use remap_4k_pfn in 64k kernel (Scott Moser ) [250496]
- [audit] sub-tree signal handling fix (Alexander Viro ) [251232]
- [audit] sub-tree memory leaks (Alexander Viro ) [251160]
- [audit] sub-tree cleanups (Alexander Viro ) [248416]
- [GFS2] invalid metadata block (Bob Peterson ) [248176]
- [XEN] use xencons=xvc by default on non-x86 (Aron Griffis ) [249100]
- [misc] i915_dma: fix batch buffer security bit for i965 chipsets (Aristeu Rozanski ) [251188] {CVE-2007-3851}
- [Xen] Fix restore path for 5.1 PV guests (Chris Lalancette ) [250420]
- [x86] Support mobile processors in fid/did to frequency conversion (Bhavana Nagendra ) [250833]
- [dlm] fix basts for granted PR waiting CW (David Teigland ) [248439]
- [scsi] PCI shutdown for cciss driver (Chip Coldwell ) [248728]
- [scssi] CCISS support for P700m (Chip Coldwell ) [248735]
- [net] forcedeth: fix nic poll (Herbert Xu ) [245191]
- [ppc] 4k page mapping support for userspace 	in 64k kernels (Scott Moser ) [250144]
- [net] tg3: small update for kdump fix (Andy Gospodarek ) [239782]
- [ppc] Cope with PCI host bridge I/O window not starting at 0 (Scott Moser ) [242937]
- [ata]: Add additional device IDs for SB700 (Prarit Bhargava ) [248109]
- [fs] - fix VFAT compat ioctls on 64-bit systems (Eric Sandeen ) [250666] {CVE-2007-2878}
- [fs] - Move msdos compat ioctl to msdos dir (Eric Sandeen ) [250666]

* Thu Aug 09 2007 Don Zickus <dzickus@redhat.com> [2.6.18-39.el5]
- [net] e1000: add support for Bolton NICs (Bruce Allan ) [251221]
- [net] e1000: add support for HP Mezzanine cards (Bruce Allan ) [251214]
- [net] igb: initial support for igb netdriver (Andy Gospodarek ) [244758]
- [net] e1000e: initial support for e1000e netdriver (Andy Gospodarek ) [240086]

* Fri Aug 03 2007 Don Zickus <dzickus@redhat.com> [2.6.18-38.el5]
- [ppc] No Boot/Hang response for PCI-E errors (Scott Moser ) [249667]
- [GFS2] Reduce number of gfs2_scand processes to one (Steven Whitehouse ) [249905]
- [scsi] Adaptec: Add SC-58300 HBA PCI ID (Konrad Rzeszutek ) [249275]
- [GFS2] Fix bug relating to inherit_jdata flag on inodes (Steven Whitehouse ) [248576]
- [ppc] Disable PCI-e completion timeouts on I/O Adapters (Scott Moser ) [232004]
- [x86] Fix tscsync frequency transitions (Bhavana Nagendra ) [245082]
- [CIFS] respect umask when unix extensions are enabled (Jeff Layton ) [246667]
- [CIFS] fix signing sec= mount options (Jeff Layton ) [246595]
- [XEN] netloop: Do not clobber cloned skb page frags (Herbert Xu ) [249683]

* Mon Jul 30 2007 Don Zickus <dzickus@redhat.com> [2.6.18-37.el5]
- [net] Using mac80211 in ad-hoc mode can result in a kernel panic (John W. Linville ) [223558]
- [ppc] Axon memory does not handle double bit errors (Scott Moser ) [249910]
- [xen] x86: HV workaround for invalid PAE PTE clears (Chris Lalancette ) [234375]
- [scsi] Update stex driver (Jeff Garzik ) [241074]
- [scsi] cciss: Re-add missing kmalloc (Prarit Bhargava ) [249104]
- [GFS2] Fix an oops in the glock dumping code (Steven Whitehouse ) [248479]
- [GFS2] locksmith/revolver deadlocks (Steven Whitehouse ) [249406]
- [xen] race loading xenblk.ko and scanning for LVM partitions (Richard Jones ) [247265]

* Fri Jul 20 2007 Don Zickus <dzickus@redhat.com> [2.6.18-36.el5]
- [NFS] Re-enable force umount (Steve Dickson ) [244949]
- [sata] regression in support for third party modules (Jeff Garzik ) [248382]
- [utrace] set zombie leader to EXIT_DEAD before release_task (Roland McGrath ) [248621]

* Wed Jul 18 2007 Don Zickus <dzickus@redhat.com> [2.6.18-35.el5]
- [XEN] fix time going backwards in gettimeofday (Rik van Riel ) [245761]
- [GFS2] soft lockup in rgblk_search (Bob Peterson ) [246114]
- [DLM] fix NULL reference in send_ls_not_ready (David Teigland ) [248187]
- [DLM] Clear othercon pointers when a connection is closed (David Teigland ) [220538]

* Thu Jul 12 2007 Don Zickus <dzickus@redhat.com> [2.6.18-34.el5]
- [wireless] iwlwifi: add driver (John W. Linville ) [223560]
- [XEN] make crashkernel=foo@16m work (Gerd Hoffmann ) [243880]
- [XEN] ia64: HV built with crash_debug=y does not boot on NUMA machine (Kei Tokunaga ) [247843]
- [edac] allow edac to panic with memory corruption on non-kdump kernels (Don Zickus ) [237950]
- [GFS2] Mounted file system won't suspend (Steven Whitehouse ) [192082]
- [GFS2] soft lockup detected in databuf_lo_before_commit (Bob Peterson ) [245832]
- [sata] Add Hitachi HDS7250SASUN500G 0621KTAWSD to NCQ blacklist (Prarit Bhargava ) [247627]
- [PCI] unable to reserve mem region on module reload (Scott Moser ) [247701 247400]
- [PPC] eHEA driver can cause kernel panic on recv of VLAN packets (Scott Moser ) [243009]
- [PPC] Fix 64K pages with kexec on native hash table (Scott Moser ) [242550]
- Reverts: Mambo driver on ppc64 [208320]

* Mon Jul 09 2007 Don Zickus <dzickus@redhat.com> [2.6.18-33.el5]
- [XEN] ia64: Windows guest cannot boot with debug mode (Kei Tokunaga ) [245668]
- [XEN] ia64: SMP Windows guest boot fails sometimes (Kei Tokunaga ) [243870]
- [XEN] ia64: Dom0 boot fails on NUMA hardware (Kei Tokunaga ) [245275]
- [XEN] ia64: Windows guest sometimes panic by incorrect ld4.s emulation (Kei Tokunaga ) [243865]
- [XEN] ia64: boot 46 GuestOS makes Dom0 hang (Kei Tokunaga ) [245667]
- [XEN] ia64: HVM guest hangs on vcpu migration (Kei Tokunaga ) [233971]
- [XEN] ia64: Cannot create guest domain due to rid problem (Kei Tokunaga ) [242040]
- [XEN] ia64: HVM domain creation panics if xenheap is not enough. (Kei Tokunaga ) [240108]
- [XEN] ia64: DomU panics by save/restore (Kei Tokunaga ) [243866]
- [XEN] ia64: Guest OS hangs on IPF montetito (Kei Tokunaga ) [245637]
- [xen] Guest access to MSR may cause system crash/data corruption (Bhavana Nagendra ) [245186]
- [xen] Windows HVM guest image migration causes blue screen (Bhavana Nagendra ) [245169]
- [xen] ia64: enable blktap driver (Jarod Wilson ) [216293]
- [scsi] check portstates before invoking target scan (David Milburn ) [246023]
- [nfs] NFSd oops when exporting krb5p mount (Steve Dickson ) [247120]
- [misc] Overflow in CAPI subsystem (Anton Arapov ) [231072] {CVE-2007-1217}
- [dlm] A TCP connection to DLM port blocks DLM operations (Patrick Caulfield ) [245892] {CVE-2007-3380}
- [dm] allow invalid snapshots to be activated (Milan Broz ) [244215]
- [gfs2] inode size inconsistency (Wendy Cheng ) [243136]
- [gfs2] Remove i_mode passing from NFS File Handle (Wendy Cheng ) [243136]
- [gfs2] Obtaining no_formal_ino from directory entry (Wendy Cheng ) [243136]
- [gfs2] EIO error from gfs2_block_truncate_page (Wendy Cheng ) [243136]
- [gfs2] remounting w/o acl option leaves acls enabled (Bob Peterson ) [245663]
- [GFS2] igrab of inode in wrong state (Steven Whitehouse ) [245646]
- [audit] subtree watching cleanups (Alexander Viro ) [182624]

* Mon Jun 25 2007 Don Zickus <dzickus@redhat.com> [2.6.18-32.el5]
- [ppc64] Data buffer miscompare (Konrad Rzeszutek ) [245332]
- [xen] fix kexec/highmem failure (Gerd Hoffmann ) [245585]
- [audit] kernel oops when audit disabled with files watched (Eric Paris ) [245164]
- [scsi] Update aic94xx and libsas to 1.0.3 (Ryan Powers ) [224694]
- [xen] ia64: kernel-xen panics when dom0_mem is specified(2) (Kei Tokunaga ) [217593]
- [md] fix EIO on writes after log failure (Jonathan Brassow ) [236271]
- [net] bonding: convert timers to workqueues (Andy Gospodarek ) [210577]
- [scsi] cciss driver updates (Tomas Henzl ) [222852]
- [sata] combined mode regression fix (Jeff Garzik ) [245052]
- Reverts: [audit] protect low memory from user mmap operations (Eric Paris ) [233021]

* Thu Jun 21 2007 Don Zickus <dzickus@redhat.com> [2.6.18-31.el5]
- [firewire] New stack technology preview (Jay Fenlason ) [182183]
- [xen] kdump/kexec support (Gerd Hoffmann ) [212843]
- [xen] Add AMD-V support for domain live migration (Chris Lalancette ) [222131]
- [GFS2] assertion failure after writing to journaled file, umount (Bob Peterson ) [243899]
- [pata] IDE (siimage) panics when DRAC4 reset (John Feeney ) [212391]
- [agp] Fix AMD-64 AGP aperture validation (Bhavana Nagendra ) [236826]
- [x86_64] C-state divisor not functioning correctly  (Bhavana Nagendra ) [235404]
- [i2c] SMBus does not work on ATI/AMD SB700 chipset (Bhavana Nagendra ) [244150]
- [ide] Cannot find IDE device with ATI/AMD SB700 (Bhavana Nagendra ) [244150]
- [pci] PCI-X/PCI-Express read control interface (Bhavana Nagendra ) [234335]
- [pata] IDE hotplug support for Promise pata_pdc2027x (Scott Moser ) [184774]

* Thu Jun 21 2007 Don Zickus <dzickus@redhat.com> [2.6.18-30.el5]
- [md] add dm rdac hardware handler (Mike Christie ) [184635]
- [sound]  ALSA update (1.0.14) (Brian Maly ) [227671 240713 223133 238004 223142 244672]
- [xen] : AMD's ASID implementation  (Bhavana Nagendra ) [242932]
- [x86_64] Fix casting issue in tick divider patch (Prarit Bhargava ) [244861]
- [fs] setuid program unable to read own /proc/pid/maps file (Konrad Rzeszutek ) [221173]
- [x86_64] Fixes system panic during boot up with no memory in Node 0 (Bhavana Nagendra ) [218641]
- [nfs] closes and umounts are racing.  (Steve Dickson ) [225515]
- [security] allow NFS nohide and SELinux to work together (Eric Paris ) [219837]
- [ia64] Altix ACPI support (Greg Edwards ) [223577]
- [net] ixgb: update to driver version 1.0.126-k2 (Bruce Allan ) [223380]
- [net] Update netxen_nic driver to version 3.x.x (Konrad Rzeszutek ) [244711]
- [misc] utrace update (Roland McGrath ) [229886 228397 217809 210693]
- [misc] disable pnpacpi on IBM x460 (Brian Maly ) [243730]
- [gfs2] posix lock fixes (David Teigland ) [243195]
- [gfs2] panic in unlink (Steven Whitehouse ) [239737]
- [input] i8042_interrupt() race can deliver bytes swapped to serio_interrupt() (Markus Armbruster ) [240860]
- [s390] qdio: system hang with zfcp in case of adapter problems (Jan Glauber ) [241298]
- [net] Fix tx_checksum flag bug in qla3xxx driver (Marcus Barrow ) [243724]
- [openib] Update OFED code to 1.2 (Doug Ledford ) [225581]
- [openib] kernel backports for OFED 1.2 update (Doug Ledford ) [225581]
- [ppc64] donate cycles from dedicated cpu (Scott Moser ) [242762]
- [scsi] RAID1 goes 'read-only' after resync (Chip Coldwell ) [231040]
- [md] move fn call that could block outside spinlock (Jonathan Brassow ) [242069]
- [fs] FUSE: Minor vfs change (Eric Sandeen ) [193720]
- [net] s2io: Native Support for PCI Error Recovery (Scott Moser ) [228052]
- [xen] x86_64: Fix FS/GS registers for VT bootup (Rik van Riel ) [224671]
- [misc] Add RHEL version info to version.h (Konrad Rzeszutek ) [232534]
- Revert: [mm] memory tracking patch only partially applied to Xen kernel (Kimball Murray ) [242514]
- Revert: [x86_64] Set CONFIG_CALGARY_IOMMU_ENABLED_BY_DEFAULT=n (Konrad Rzeszutek ) [222035]
- Revert: [ppc64] Oprofile kernel module does not distinguish PPC 970MP  (Janice M. Girouard ) [216458]

* Mon Jun 18 2007 Don Zickus <dzickus@redhat.com> [2.6.18-29.el5]
- [xen] Expand VNIF number per guest domain to over four (Kei Tokunaga ) [223908]
- [xen] change interface version for 3.1 (Kei Tokunaga ) [242989]
- [xen] ia64: Fix PV-on-HVM driver (Kei Tokunaga ) [242144]
- [xen] ia64: use generic swiotlb.h header (Kei Tokunaga ) [242138]
- [xen] ia64: xm save/restore does not work (Kei Tokunaga ) [240858]
- [xen] ia64: Skip MCA setup on domU (Kei Tokunaga ) [242143]
- [xen] ia64: Cannot measure process time accurately (Kei Tokunaga ) [240107]
- [xen] Support new xm command: xm trigger (Kei Tokunaga ) [242140]
- [xen] ia64: Fix for irq_desc() missing in new upstream (Kei Tokunaga ) [242137]
- [xen] ia64: Set IRQ_PER_CPU status on percpu IRQs (Kei Tokunaga ) [242136]
- [xen] ia64: improve performance of system call (Kei Tokunaga ) 
- [xen] ia64: para domain vmcore does not work under crash (Kei Tokunaga ) [224047]
- [xen] ia64: kernel-xen panics when dom0_mem=4194304 is specified (Kei Tokunaga ) [217593]
- [xen] ia64: evtchn_callback fix and clean (Kei Tokunaga ) [242126]
- [xen] ia64: changed foreign domain page mapping semantic (Kei Tokunaga ) [242779]
- [xen] Change to new interrupt deliver mechanism (Kei Tokunaga ) [242125]
- [xen] ia64: Uncorrectable error makes hypervisor hung (MCA  support) (Kei Tokunaga ) [237549]
- [xen] Xen0 can not startX in tiger4 (Kei Tokunaga ) [215536]
- [xen] ia64: Fix xm mem-set hypercall on IA64 (Kei Tokunaga ) [241976]
- [xen] ia64: Fix HVM interrupts on IPF (Kei Tokunaga ) [242124]
- [xen] save/restore fix (Gerd Hoffmann ) [222128]
- [xen] blkback/blktap: fix id type (Gerd Hoffmann ) [222128]
- [xen] xen: blktap race #2 (Gerd Hoffmann ) [222128]
- [xen] blktap: race fix #1 (Gerd Hoffmann ) [222128]
- [xen] blktap: cleanups. (Gerd Hoffmann ) [242122]
- [xen] blktap: kill bogous flush (Gerd Hoffmann ) [222128]
- [xen] binmodal drivers: block backends (Gerd Hoffmann ) [222128]
- [xen] bimodal drivers, blkfront driver (Gerd Hoffmann ) [222128]
- [xen] bimodal drivers, pvfb frontend (Gerd Hoffmann ) [222128]
- [xen] bimodal drivers, protocol header (Gerd Hoffmann ) [222128]

* Fri Jun 15 2007 Don Zickus <dzickus@redhat.com> [2.6.18-28.el5]
- [net] netxen: initial support for NetXen 10GbE NIC (Andy Gospodarek ) [231724]
- [net] cxgb3: initial support for Chelsio T3 card (Andy Gospodarek ) [222453]
- [drm] agpgart and drm support for bearlake graphics (Geoff Gustafson ) [229091]
- [acpi] acpi_prt list incomplete (Kimball Murray ) [214439]
- [mm] memory tracking patch only partially applied to Xen kernel (Kimball Murray ) [242514]
- [x86_64] Fix TSC reporting for processors with constant TSC (Bhavana Nagendra ) [236821]
- [pci] irqbalance causes oops during PCI removal (Kimball Murray ) [242517]
- [net] Allow packet drops during IPSec larval state resolution (Vince Worthington ) [240902]
- [net] bcm43xx: backport from 2.6.22-rc1 (John W. Linville ) [213761]
- [net] softmac: updates from 2.6.21 (John W. Linville ) [240354]
- [net] e1000: update to driver version 7.3.20-k2 (Andy Gospodarek ) [212298]
- [net] bnx2: update to driver version 1.5.11 (Andy Gospodarek ) [225350]
- [net] ipw2[12]00: backports from 2.6.22-rc1 (John W. Linville ) [240868]
- [net] b44 ethernet driver update (Jeff Garzik ) [244133]
- [net] sky2: update to version 1.14 from 2.6.21 (John W. Linville ) [223631]
- [net] forcedeth: update to driver version 0.60 (Andy Gospodarek ) [221941]
- [net] bonding: update to driver version 3.1.2 (Andy Gospodarek ) [210577]
- [net] tg3: update to driver version 3.77 (Andy Gospodarek ) [225466 228125]
- [PPC] Update of spidernet to 2.0.A for Cell (Scott Moser ) [227612]
- [scsi] SPI DV fixup (Chip Coldwell ) [237889]
- [audit] audit when opening existing messege queue (Eric Paris ) [223919 ]
- [audit] audit=0 does not disable all audit messages (Eric Paris ) [231371]
- [net] mac80211 inclusion (John W. Linville ) [214982 223558]

* Fri Jun 15 2007 Don Zickus <dzickus@redhat.com> [2.6.18-27.el5]
- [sata] kabi fixes [203781]
- [audit] panic and kabi fixes [233021]

* Thu Jun 14 2007 Don Zickus <dzickus@redhat.com> [2.6.18-26.el5]
- [x86_64] sparsemem memmap allocation above 4G (grgustaf) [227426]
- [net] ip_conntrack_sctp: fix remotely triggerable panic (Don Howard ) [243244] {CVE-2007-2876}
- [usb] Strange URBs and running out IOMMU (Pete Zaitcev ) [230427]
- [audit] broken class-based syscall audit (Eric Paris ) [239887]
- [audit] allow audit filtering on bit & operations (Eric Paris ) [232967]
- [x86_64] Add L3 cache support to some processors (Bhavana Nagendra ) [236835]
- [x86_64] disable mmconf for HP dc5700 Microtower (Prarit Bhargava ) [219389]
- [misc] cpuset information leak (Prarit Bhargava ) [242811] {CVE-2007-2875}
- [audit] stop softlockup messages when loading selinux policy (Eric Paris ) [231392]
- [fs] nfs does not support leases, send correct error (Peter Staubach ) [216750]
- [dlm] variable allocation types (David Teigland ) [237558]
- [GFS2] Journaled data issues (Steven Whitehouse ) [238162]
- [ipsec] Make XFRM_ACQ_EXPIRES proc-tunable (Vince Worthington ) [241798]
- [GFS2] Missing lost inode recovery code (Steven Whitehouse ) [201012]
- [GFS2] Can't mount GFS2 file system on AoE device (Robert Peterson ) [243131]
- [scsi] update aacraid driver to 1.1.5-2437 (Chip Coldwell ) [197337]
- [scsi] cciss: ignore results from unsent commands on kexec boot (Neil Horman ) [239520]
- [scsi] update iscsi_tcp driver (Mike Christie ) [227739]
- [x86_64] Fix regression in kexec (Neil Horman ) [242648]
- [x86] rtc support for HPET legacy replacement mode (Brian Maly ) [220196]
- [scsi] megaraid_sas update (Chip Coldwell ) [225221]
- [fs] fix ext2 overflows on filesystems > 8T (Eric Sandeen ) [237188]
- [x86] MCE thermal throttling (Brian Maly ) [224187]
- [audit] protect low memory from user mmap operations (Eric Paris ) [233021]
- [scsi] Add FC link speeds. (Tom Coughlan ) [231888]
- [pci] I/O space mismatch with P64H2 (Geoff Gustafson ) [220511]
- [scsi] omnibus lpfc driver update (Chip Coldwell ) [227416]
- [scsi] Update qla2xxx firmware (Marcus Barrow ) [242534]
- [ide] Serverworks data corruptor (Alan Cox ) [222653]
- [scsi] update qla4xxx driver (Mike Christie ) [224435 223087 224203]
- [scsi] update iser driver (Mike Christie ) [234352]
- [dlm] fix debugfs ref counting problem (Josef Bacik ) [242807]
- [md] rh_in_sync should be allowed to block (Jonathan Brassow ) [236624]
- [md] unconditionalize log flush (Jonathan Brassow ) [235039]
- [GFS2] Add nanosecond timestamp feature  (Steven Whitehouse ) [216890]
- [GFS2] quota/statfs sign problem and cleanup _host structures (Steven Whitehouse ) [239686]
- [scsi] mpt adds DID_BUS_BUSY host status on scsi BUSY status (Chip Coldwell ) [228108]
- [scsi] fix for slow DVD drive (Chip Coldwell ) [240910]
- [scsi] update MPT Fusion to 3.04.04 (Chip Coldwell ) [225177]
- [GFS2] Fix calculation for spare log blocks with smaller block sizes (Steven Whitehouse ) [240435]
- [gfs2] quotas non-functional (Abhijith Das ) [201011]
- [gfs2] Cleanup inode number handling (Abhijith Das ) [242584]

* Wed Jun 13 2007 Don Zickus <dzickus@redhat.com> [2.6.18-25.el5]
- [s390] fix possible reboot hang on s390 (Jan Glauber ) [222181]
- [cifs] Update CIFS to version 1.48aRH (Jeff Layton ) [238597]
- [audit] Make audit config immutable in kernel (Eric Paris ) [223530]
- [dio] invalidate clean pages before dio write (Jeff Moyer ) [232715]
- [nfs] fixed oops in symlink code.  (Steve Dickson ) [218718]
- [mm] shared page table for hugetlb  page (Larry Woodman ) [222753]
- [nfs] Numerous oops, memory leaks and hangs found in upstream (Steve Dickson ) [242975]
- [misc] include taskstats.h in kernel-headers package (Don Zickus ) [230648]
- [ide] packet command error when installing rpm (John Feeney ) [229701]
- [dasd] export DASD status to userspace (Chris Snook ) [242681]
- [dasd] prevent dasd from flooding the console (Jan Glauber ) [229590]
- [s390] ifenslave -c causes kernel panic with VLAN and OSA Layer2 (Jan Glauber ) [219826]
- [s390] sclp race condition (Jan Glauber ) [230598]
- [audit] SAD/SPD flush have no security check (Eric Paris ) [233387]
- [audit] Add space in IPv6 xfrm audit record (Eric Paris ) [232524]
- [audit] Match proto when searching for larval SA (Eric Paris ) [234485]
- [audit] pfkey_spdget does not audit xrfm policy changes (Eric Paris ) [229720]
- [audit] collect audit inode information for all f*xattr commands (Eric Paris ) [229094]
- [audit] Initialize audit record sid information to zero (Eric Paris ) [223918]
- [audit] xfrm_add_sa_expire return code error (Eric Paris ) [230620]
- [net] NetLabel: Verify sensitivity level has a valid CIPSO mapping (Eric Paris ) [230255]
- [audit] pfkey_delete and xfrm_del_sa audit hooks wrong (Eric Paris ) [229732]
- [block] Fix NULL bio crash in loop worker thread (Eric Sandeen ) [236880]
- [x86]: Add Greyhound performance counter events (Bhavana Nagendra ) [222126]
- [dio] clean up completion phase of direct_io_worker() (Jeff Moyer ) [242116]
- [audit] add subtrees support (Alexander Viro ) [182624]
- [audit] AVC_PATH handling (Alexander Viro ) [224620]
- [audit] auditing ptrace (Alexander Viro ) [228384]
- [x86_64] Fix a cast in the lost ticks code (Prarit Bhargava ) [241781]
- [PPC64] DMA 4GB boundary protection  (Scott Moser ) [239569]
- [PPC64] MSI support for PCI-E (Scott Moser ) [228081]
- [ppc64] Enable DLPAR support for HEA (Scott Moser ) [237858]
- [ppc64] update ehea driver to latest version. (Janice M. Girouard ) [234225]
- [PPC64] spufs move to sdk2.1 (Scott Moser ) [242763]
- [PPC64] Cell SPE and Performance (Scott Moser ) [228128]
- [cpufreq] Identifies correct number of processors in powernow-k8 (Bhavana Nagendra ) [229716]

* Mon Jun 11 2007 Don Zickus <dzickus@redhat.com> [2.6.18-24.el5]
- [ipmi] update to latest (Peter Martuccelli ) [241928 212415 231436]
- [sata] super-jumbo update (Jeff Garzik ) [203781]
- [sata] move SATA drivers to drivers/ata (Jeff Garzik ) [203781]

* Fri Jun 08 2007 Don Zickus <dzickus@redhat.com> [2.6.18-23.el5]
- [dlm] Allow unprivileged users to create the default lockspace (Patrick Caulfield ) [241902]
- [dlm] fix queue_work oops (David Teigland ) [242070]
- [dlm] misc device removed when lockspace removal fails (David Teigland ) [241817]
- [dlm] dumping master locks (David Teigland ) [241821]
- [dlm] canceling deadlocked lock (David Teigland ) [238898]
- [dlm] wait for config check during join (David Teigland ) [206520]
- [dlm] fix new_lockspace error exit (David Teigland ) [241819]
- [dlm] cancel in conversion deadlock (David Teigland ) [238898]
- [dlm] add lock timeouts and time warning (David Teigland ) [238898]
- [dlm] block scand during recovery (David Teigland ) [238898]
- [dlm] consolidate transport protocols (David Teigland ) [219799]
- [audit] log targets of signals (Alexander Viro ) [228366]

* Thu Jun 07 2007 Don Zickus <dzickus@redhat.com> [2.6.18-22.el5]
- [scsi] Add kernel support for Areca RAID controllers (Tomas Henzl ) [205897]
- [s390] runtime switch for qdio performance statistics (Jan Glauber ) [228048]
- [nfs] enable 'nosharecache' mounts. (Steve Dickson ) [209964]
- [scsi] scsi_error.c - Fix lost EH commands (Chip Coldwell ) [227586]
- [s390] zfcp driver fixes (Jan Glauber ) [232002 232006]
- [misc] synclink_gt: fix init error handling  (Eric Sandeen) [210389]
- [edac] k8_edac: don't panic on PCC check (Aristeu Rozanski ) [237950]
- [mm] Prevent OOM-kill of unkillable children or siblings (Larry Woodman ) [222492]
- [aio] fix buggy put_ioctx call in aio_complete (Jeff Moyer ) [219497]
- [scsi] 3ware 9650SE not recognized by updated  3w-9xxx module (Chip Coldwell ) [223465]
- [scsi] megaraid: update version reported by  MEGAIOC_QDRVRVER (Chip Coldwell ) [237151]
- [nfs] NFS/NLM - Fix double free in __nlm_async_call (Steve Dickson ) [223248]
- [ppc] EEH is improperly enabled for some Power4  systems (Scott Moser ) [225481]
- [net] ixgb: update to 1.0.109 to add pci error recovery (Andy Gospodarek ) [211380]
- [ppc] Fix xmon=off and cleanup xmon initialization (Scott Moser ) [229593]
- [mm] reduce MADV_DONTNEED contention (Rik van Riel ) [237677]
- [x86_64] wall time is not compensated for lost timer ticks (Konrad Rzeszutek ) [232666]
- [PPC] handle <.symbol> lookup for kprobes (Scott Moser ) [238465]
- [pci] Dynamic Add and Remove of PCI-E (Konrad Rzeszutek ) [227727]
- [PPC64] Support for ibm,power-off-ups RTAS  call (Scott Moser ) [184681]

* Fri Jun 01 2007 Don Zickus <dzickus@redhat.com> [2.6.18-21.el5]
- [net] Re-enable and update the qla3xxx networking driver (Konrad Rzeszutek ) [225200]
- [misc] xen: kill sys_{lock,unlock} dependency on microcode driver (Gerd Hoffmann ) [219652]
- [acpi] Update ibm_acpi module (Konrad Rzeszutek ) [231176]
- [nfs] NFSv4: referrals support (Steve Dickson ) [230602]
- [misc] random: fix error in entropy extraction (Aristeu Rozanski ) [241718] {CVE-2007-2453}
- [net] fix DoS in PPPOE (Neil Horman ) [239581] {CVE-2007-2525}
- [GFS2] Fixes related to gfs2_grow (Steven Whitehouse ) [235430]
- [gfs2] Shrink size of struct gdlm_lock (Steven Whitehouse ) [240013]
- [misc] Bluetooth setsockopt() information leaks (Don Howard ) [234292] {CVE-2007-1353}
- [net] RPC/krb5 memory leak (Steve Dickson ) [223248]
- [mm] BUG_ON in shmem_writepage() is triggered (Michal Schmidt ) [234447]
- [nfs] protocol V3 :write procedure patch (Peter Staubach ) [228854]
- [fs] invalid segmentation violation during exec (Dave Anderson ) [230339]
- [md] dm io: fix panic on large request (Milan Broz ) [240751]
- [nfs] RPC: when downsizing response buffer, account for checksum (Jeff Layton ) [238687]
- [md] incorrect parameter to dm_io causes read failures (Jonathan Brassow ) [241006]
- [ia64] eliminate potential deadlock on XPC disconnects (George Beshers ) [223837]
- [md] dm crypt: fix possible data corruptions (Milan Broz ) [241272]
- [ia64] SN correctly update smp_affinity mask (luyu ) [223867]
- [mm]fix OOM wrongly killing processes through MPOL_BIND (Larry Woodman ) [222491]
- [nfs] add nordirplus option to NFS client  (Steve Dickson ) [240126]
- [autofs] fix panic on mount fail - missing autofs module (Ian Kent ) [240307]
- [scsi] Fix bogus warnings from SB600 DVD drive (Prarit Bhargava ) [238570]
- [acpi] _CID support for PCI Root Bridge  detection. (Luming Yu ) [230742]
- [ia64] platform_kernel_launch_event is a noop in non-SN kernel (Luming Yu ) [232657]
- [net] high TCP latency with small packets (Thomas Graf ) [229908]
- [misc] xen: fix microcode driver for new firmware (Gerd Hoffmann ) [237434]
- [GFS2] Bring GFS2 uptodate (Steven Whitehouse ) [239777]
- [scsi] update for new SAS RAID  (Scott Moser ) [228538]
- [md] dm: allow offline devices in table (Milan Broz ) [239655]
- [md] dm: fix suspend error path (Milan Broz ) [239645]
- [md] dm multipath: rr path order is inverted (Milan Broz ) [239643]
- [net] RPC: simplify data check, remove BUG_ON (Jeff Layton ) [237374]
- [mm] VM scalability issues (Larry Woodman ) [238901 238902 238904 238905]
- [misc] lockdep: annotate DECLARE_WAIT_QUEUE_HEAD (Chip Coldwell ) [209539]
- [mm] memory-less node support (Prarit Bhargava ) [228564]

* Thu May 17 2007 Don Howard <dhoward@redhat.com> [2.6.18-20.el5]
- [fs] prevent oops in compat_sys_mount (Jeff Layton ) [239767] {CVE-2006-7203}

* Thu May 10 2007 Don Zickus <dzickus@redhat.com> [2.6.18-19.el5]
- [ia64] MCA/INIT issues with printk/messages/console (Kei Tokunaga ) [219158]
- [ia64] FPSWA exceptions take excessive system time  (Erik Jacobson ) [220416]
- [GFS2] flush the glock completely in inode_go_sync (Steven Whitehouse ) [231910]
- [GFS2] mmap problems with distributed test cases (Steven Whitehouse ) [236087]
- [GFS2] deadlock running d_rwdirectlarge (Steven Whitehouse ) [236069]
- [GFS2] panic if you try to rm -rf the lost+found directory (Steven Whitehouse ) [232107]
- [misc] Fix softlockup warnings during sysrq-t (Prarit Bhargava ) [206366]
- [pty] race could lead to double idr index free (Aristeu Rozanski ) [230500]
- [v4l] use __GFP_DMA32 in videobuf_vm_nopage (Aristeu Rozanski ) [221478]
- [scsi] Update QLogic qla2xxx driver to 8.01.07-k6 (Marcus Barrow ) [225249]
- [mm] OOM killer breaks s390 CMM (Jan Glauber ) [217968]
- [fs] stack overflow with non-4k page size (Dave Anderson ) [231312]
- [scsi] scsi_transport_spi: sense buffer size error (Chip Coldwell ) [237889]
- [ppc64] EEH PCI error recovery  support (Scott Moser ) [207968]
- [mm] optimize kill_bdev() (Peter Zijlstra ) [232359]
- [x86] tell sysrq-m to poke the nmi watchdog (Konrad Rzeszutek ) [229563]
- [x86] Use CPUID calls to check for mce (Bhavana Nagendra ) [222123]
- [x86] Fix to nmi to support GH processors (Bhavana Nagendra ) [222123]
- [x86] Fix CPUID calls to support GH processors (Bhavana Nagendra ) [222123]
- [x86] Greyhound cpuinfo output cleanups (Bhavana Nagendra ) [222124]
- [misc] intel-rng: fix deadlock in smp_call_function (Prarit Bhargava ) [227696]
- [net] ixgb: fix early TSO completion (Bruce Allan ) [213642]

* Fri May 04 2007 Don Zickus <dzickus@redhat.com> [2.6.18-18.el5]
- [e1000] fix watchdog timeout panics (Andy Gospodarek ) [217483]
- [net] ipv6_fl_socklist is inadvertently shared (David S. Miller ) [233088] {CVE-2007-1592}
- [dlm] expose dlm_config_info fields in configfs (David Teigland ) [239040]
- [dlm] add config entry to enable log_debug (David Teigland ) [239040]
- [dlm] rename dlm_config_info fields (David Teigland ) [239040]
- [mm] NULL current->mm dereference in grab_swap_token causes oops (Jerome Marchand ) [231639]
- [net] Various NULL pointer dereferences in netfilter code (Thomas Graf ) [234287] {CVE-2007-1496}
- [net] IPv6 fragments bypass in nf_conntrack netfilter code (Thomas Graf ) [234288] {CVE-2007-1497}
- [net] disallow RH0 by default (Thomas Graf ) [238065] {CVE-2007-2242}
- [net] fib_semantics.c out of bounds check (Thomas Graf ) [236386]
- [misc] getcpu system call (luyu ) [233046]
- [ipc] bounds checking for shmmax (Anton Arapov ) [231168]
- [x86_64] GATT pages must be uncacheable (Chip Coldwell ) [238709]
- [gfs2] does a mutex_lock instead of a mutex_unlock (Josef Whiter ) [229376]
- [dm] failures when creating many snapshots (Milan Broz ) [211516 211525]
- [dm] kmirrord: deadlock when dirty log on mirror itself (Milan Broz ) [218068]
- [security] Supress SELinux printk for messages users don't care about (Eric Paris ) [229874]
- [serial] panic in check_modem_status on 8250 (Norm Murray ) [238394]
- [net] Fix user OOPS'able bug in FIB netlink (David S. Miller ) [237913]
- [misc] EFI: only warn on pre-1.00 version (Michal Schmidt ) [223282]
- [autofs4] fix race between mount and expire (Ian Kent ) [236875]
- [GFS2] gfs2_delete_inode: 13 (Steven Whitehouse ) [224480]
- [misc] k8temp (Florian La Roche ) [236205]

* Mon Apr 30 2007 Don Zickus <dzickus@redhat.com> [2.6.18-17.el5]
- [x86_64] Calgary IOMMU cleanups and fixes (Konrad Rzeszutek ) [222035]
- [GFS2] lockdump support (Robert Peterson ) [228540]
- [net] kernel-headers: missing include of types.h (Neil Horman ) [233934]
- [mm] unmapping memory range disturbs page referenced state (Peter Zijlstra ) [232359]
- [IA64] Fix stack layout issues when using ulimit -s (Jarod Wilson ) [234576]
- [CIFS] Windows server bad domain name null terminator fix (Jeff Layton ) [224359]
- [x86_64] Fix misconfigured K8 north bridge (Bhavana Nagendra ) [236759]
- [gfs2] use log_error before LM_OUT_ERROR (David Teigland ) [234338]
- [dlm] fix mode munging (David Teigland ) [234086]
- [dlm] change lkid format (David Teigland ) [237126]
- [dlm] interface for purge (David Teigland ) [237125]
- [dlm] add orphan purging code (David Teigland ) [237125]
- [dlm] split create_message function (David Teigland ) [237125]
- [dlm] overlapping cancel and unlock (David Teigland ) [216113]
- [dlm] zero new user lvbs (David Teigland ) [237124]
- [PPC64] Handle Power6 partition modes (2) (Janice M. Girouard ) [228091]
- [ppc64] Handle Power6 partition modes (Janice M. Girouard ) [228091]
- [mm] oom kills current process on memoryless node. (Larry Woodman ) [222491]
- [x86] Tick Divider (Alan Cox ) [215403]
- [GFS2] hangs waiting for semaphore (Steven Whitehouse ) [217356]
- [GFS2] incorrect flushing of rgrps (Steven Whitehouse ) [230143]
- [GFS2] Clean up of glock code (Steven Whitehouse ) [235349]
- [net] IPsec: panic when large security contexts in ACQUIRE (James Morris ) [235475]
- [ppc64] Cell Platform Base kernel support (Janice M. Girouard ) [228099]
- [s390] fix dasd reservations (Chris Snook ) [230171]
- [x86] Fix invalid write to nmi MSR (Prarit Bhargava ) [221671]

* Fri Apr 20 2007 Don Zickus <dzickus@redhat.com> [2.6.18-16.el5]
- [s390] crypto driver update (Jan Glauber ) [228049]
- [NMI] change watchdog timeout to 30 seconds (Larry Woodman ) [229563]
- [ppc64] allow vmsplice to work in 32-bit mode on ppc64 (Don Zickus ) [235184]
- [nfs] fix multiple dentries pointing to same directory inode (Steve Dickson ) [208862]
- [ipc] mqueue nested locking annotation (Eric Sandeen ) 
- [net] expand in-kernel socket api (Neil Horman ) [213287]
- [XEN] Better fix for netfront_tx_slot_available(). (Herbert Xu ) [224558]
- [fs] make static counters in new_inode and iunique be 32 bits (Jeff Layton ) [215356]
- [ppc64] remove BUG_ON() in hugetlb_get_unmapped_area() (Larry Woodman ) [222926]
- [dm] stalls on resume if noflush is used (Milan Broz ) [221330]
- [misc]: AMD/ATI SB600 SMBus support (Prarit Bhargava ) [232000]
- [mm] make do_brk() correctly return EINVAL for ppc64.   (Larry Woodman ) [224261]
- [agp] agpgart fixes and new pci ids (Geoff Gustafson ) [227391]
- [net] xfrm_policy delete security check misplaced (Eric Paris ) [228557]
- [x86]: Fix mtrr MODPOST warnings (Prarit Bhargava ) [226854]
- [elevator] move clearing of unplug flag  earlier (Eric Sandeen ) [225435]
- [net] stop leak in flow cache code (Eric Paris ) [229528]
- [ide] SB600 ide only has one channel (Prarit Bhargava ) [227908]
- [scsi] ata_task_ioctl should return ata registers (David Milburn ) [218553]
- [pcie]: Remove PCIE warning for devices with no irq pin (Prarit Bhargava ) [219318]
- [x86] ICH9 device IDs  (Geoff Gustafson ) [223097]
- [mm] Some db2 operations cause system to hang (Michal Schmidt ) [222031]
- [security] invalidate flow cache entries after selinux policy reload (Eric Paris ) [229527]
- [net] wait for IPSEC SA resolution in socket contexts. (Eric Paris ) [225328]
- [net] clean up xfrm_audit_log interface (Eric Paris ) [228422]
- [ipv6]: Fix routing regression. (David S. Miller ) [222122]
- [tux] date overflow fix (Jason Baron ) [231561]
- [cifs] recognize when a file is no longer read-only (Jeff Layton ) [231657]
- [module] MODULE_FIRMWARE support (Jon Masters ) [233494]
- [misc] some apps cannot use IPC msgsnd/msgrcv larger than 64K (Jerome Marchand ) [232012]
- [xen] Fix netfront teardown (Glauber de Oliveira Costa ) [219563]

* Fri Apr 13 2007 Don Zickus <dzickus@redhat.com> [2.6.18-15.el5] 
- [x86_64] enable calgary support for x86_64 system (Neil Horman ) [221593]
- [s390] pseudo random number generator (Jan Glauber ) [184809]
- [ppc64] Oprofile kernel module does not distinguish PPC 970MP  (Janice M. Girouard ) [216458]
- [GFS2] honor the noalloc flag during block allocation (Steven Whitehouse ) [235346]
- [GFS2] resolve deadlock when writing and accessing a file (Steven Whitehouse ) [231380]
- [s390] dump on panic support (Jan Glauber ) [228050, 227841]
- [pci] include devices in NIC ordering patch and fix whitespace (Andy Gospodarek ) [226902]
- [ext3] handle orphan inodes vs. readonly snapshots (Eric Sandeen ) [231553]
- [fs] - Fix error handling in check_partition(), again (Eric Sandeen ) [231518]
- [ipv6] /proc/net/anycast6 unbalanced inet6_dev refcnt (Andy Gospodarek ) [231310]
- [s390] kprobes breaks BUG_ON (Jan Glauber ) [231155]
- [edac] add support for revision F processors (Aristeu Rozanski ) [202622]
- [scsi] blacklist touch-up (Chip Coldwell ) [232074]
- [gfs2] remove an incorrect assert (Steven Whitehouse ) [229873]
- [gfs2] inconsistent inode number lookups (Wendy Cheng ) [229395]
- [gfs2] NFS cause recursive locking (Wendy Cheng ) [229349]
- [gfs2] NFS v2 mount failure (Wendy Cheng ) [229345]
- [s390] direct yield for spinlocks on s390 (Jan Glauber ) [228869]
- [s390] crypto support for 3592 tape devices (Jan Glauber ) [228035]
- [cpu-hotplug] make and module insertion script cause a panic (Konrad Rzeszutek ) [217583]
- [s390] runtime switch for dasd erp logging (Jan Glauber ) [228034]
- [suspend] Fix x86_64/relocatable kernel/swsusp breakage. (Nigel Cunningham ) [215954]
- [ext3] buffer: memorder fix (Eric Sandeen ) [225172]
- [scsi] fix incorrect last scatg length (David Milburn ) [219838]
- [usb]: airprime driver corrupts ppp session for EVDO card (Jon Masters ) [222443]
- [misc] Fix race in efi variable delete code (Prarit Bhargava ) [223796]
- [ext3] return ENOENT from ext3_link when racing with unlink (Eric Sandeen ) [219650]
- [scsi] Missing PCI Device in aic79xx driver (Chip Coldwell ) [220603]
- [acpi]: Fix ACPI PCI root bridge querying time (Prarit Bhargava ) [218799]
- [kdump]: Simple bounds checking for crashkernel args (Prarit Bhargava ) [222314]
- [misc] longer CD timeout (Erik Jacobson ) [222362]
- [nfs] Disabling protocols when starting NFS server is broken. (Steve Dickson ) [220894]
- [s390] page_mkclean causes data corruption on s390 (Jan Glauber ) [235373]

* Wed Apr 04 2007 Don Zickus <dzickus@redhat.com> [2.6.18-14.el5]
- [ppc] reduce num_pmcs to 6 for Power6 (Janice M. Girouard ) [220114]
- [sched] remove __cpuinitdata from cpu_isolated_map (Jeff Burke ) [220069]
- [gfs2] corrrectly display revalidated directories (Robert Peterson ) [222302]
- [gfs2] fix softlockups (Josef Whiter ) [229080]
- [gfs2] occasional panic in gfs2_unlink while running bonnie++ (Steven Whitehouse ) [229831]
- [gfs2] Shrink gfs2 in-core inode size (Steven Whitehouse ) [230693]
- [GFS2] Fix list corruption in lops.c (Steven Whitehouse ) [226994]
- [gfs2] fix missing unlock_page() (Steven Whitehouse ) [224686]
- [dlm] make lock_dlm drop_count tunable in sysfs (David Teigland ) [224460]
- [dlm] increase default lock limit (David Teigland ) [224460]
- [dlm] can miss clearing resend flag (David Teigland ) [223522]
- [dlm] fix master recovery (David Teigland ) [222307]
- [dlm] fix user unlocking (David Teigland ) [219388]
- [dlm] saved dlm message can be dropped (David Teigland ) [223102]

* Tue Mar 27 2007 Don Zickus <dzickus@redhat.com> [2.6.18-13.el5]
- [x86_64] Don't leak NT bit into next task (Dave Anderson ) [213313]
- [mm] Gdb does not accurately output the backtrace. (Dave Anderson ) [222826]
- [net] IPV6 security holes in ipv6_sockglue.c - 2 (David S. Miller ) [231517] {CVE-2007-1000}
- [net] IPV6 security holes in ipv6_sockglue.c (David S. Miller ) [231668] {CVE-2007-1388}
- [audit] GFP_KERNEL allocations in non-blocking context fix (Alexander Viro ) [228409]
- [NFS] version 2 over UDP is not working properly (Steve Dickson ) [227718]
- [x86] Fix various data declarations in cyrix.c (Prarit Bhargava ) [226855]
- [sound] Fix various data declarations in sound/drivers (Prarit Bhargava ) [227839]
- [mm] remove __initdata from initkmem_list3 (Prarit Bhargava ) [226865]

* Wed Mar 14 2007 Don Zickus <dzickus@redhat.com> [2.6.18-12.el5]
- [xen] move xen sources out of kernel-xen-devel (Don Zickus ) [212968]
- [net] __devinit & __devexit cleanups for de2104x driver (Prarit Bhargava ) [228736]
- [video] Change rivafb_remove to __deviexit (Prarit Bhargava ) [227838]
- [x86] Reorganize smp_alternatives sections in vmlinuz (Prarit Bhargava ) [226876]
- [atm] Fix __initdata declarations in drivers/atm/he.c (Prarit Bhargava ) [227830]
- [video] Change nvidiafb_remove to __devexit (Prarit Bhargava ) [227837]
- [usb] __init to __devinit in isp116x_probe (Prarit Bhargava ) [227836]
- [rtc] __init to __devinit in rtc drivers' probe functions (Prarit Bhargava ) [227834]
- [x86] remove __init from sysenter_setup (Prarit Bhargava ) [226852]
- [irq] remove __init from noirqdebug_setup (Prarit Bhargava ) [226851]
- [x86] remove __init from efi_get_time (Prarit Bhargava ) [226849]
- [x86] Change __init to __cpuinit data in SMP code (Prarit Bhargava ) [226859]
- [x86] apic probe __init fixes (Prarit Bhargava ) [226875]
- [x86] fix apci related MODPOST warnings (Prarit Bhargava ) [226845]
- [serial] change serial8250_console_setup to __init (Prarit Bhargava ) [226869]
- [init] Break init() into two parts to avoid MODPOST warnings (Prarit Bhargava ) [226829]
- [x86] declare functions __init to avoid  compile warnings (Prarit Bhargava ) [226858]
- [x86] cpu hotplug/smpboot misc MODPOST warning fixes (Prarit Bhargava ) [226826]
- [x86] Fix boot_params and .pci_fixup warnings (Prarit Bhargava ) [226824 226874]
- [xen] Enable Xen booting on machines with > 64G (Chris Lalancette ) [220592]
- [utrace] exploit and unkillable cpu fixes (Roland McGrath ) [229886]
- [pcmcia] buffer overflow in omnikey cardman driver    (Don Howard ) [227478]

* Fri Feb 23 2007 Don Zickus <dzickus@redhat.com> [2.6.18-10.el5]
- [cpufreq] Remove __initdata from tscsync (Prarit Bhargava ) [223017]
- [security] Fix key serial number collision problem (David Howells ) [227497] {CVE-2007-0006}
- [fs] core dump of read-only binarys (Don Howard ) [228886] {CVE-2007-0958}

* Thu Feb 23 2007 Don Zickus <dzickus@redhat.com> [2.6.18-9.el5]
- enable debug options

* Thu Jan 25 2007 Don Zickus <dzickus@redhat.com> [2.6.18-8.el5]
- quiet down the console_loglevel (Don Zickus) [224613]

* Thu Jan 25 2007 Don Zickus <dzickus@redhat.com> [2.6.18-7.el5]
- xen: fix TLB flushing in shadow pagetable mode (Rik van Riel ) [224227]

* Tue Jan 23 2007 Don Zickus <dzickus@redhat.com> [2.6.18-6.el5]
- Update: xen: Add PACKET_AUXDATA cmsg (Herbert Xu ) [223505]

* Tue Jan 23 2007 Don Zickus <dzickus@redhat.com> [2.6.18-5.el5]
- x86: /proc/mtrr interface MTRR bug fix (Bhavana Nagendra ) [223821]
- Revert: bonding: eliminate rtnl assertion spew (Andy Gospodarek ) [210577]
- ia64: Check for TIO errors on shub2 Altix (George Beshers ) [223529]
- nfs: Unable to mount more than 1 Secure NFS mount (Steve Dickson ) [220649]

* Wed Jan 17 2007 Don Zickus <dzickus@redhat.com> [2.6.18-4.el5]
- IPSec: incorrect return code in xfrm_policy_lookup (Eric Paris ) [218591]
- more kabi whitelist updates (Jon Masters)

* Tue Jan 16 2007 Don Zickus <dzickus@redhat.com> [2.6.18-3.el5]
- scsi: fix EX8350 panic (stex.ko) (Jun'ichi Nick Nomura ) [220783]
- Audit: Mask upper bits on 32 bit syscall auditing on ppc64 (Eric Paris ) [213276]

* Mon Jan 15 2007 Don Zickus <dzickus@redhat.com> [2.6.18-2.el5]
- mm: handle mapping of memory without a struct page backing it (Erik Jacobson ) [221029]
- rng: check to see if bios locked device (Erik Jacobson ) [221029]
- sata: support legacy IDE mode of SB600 SATA (Bhavana Nagendra ) [221636]
- xen: quick fix for Cannot allocate memory (Steven Rostedt ) [217056]
- XEN: Register PIT handlers to the correct domain (Herbert Xu ) [222520]
- SATA AHCI: support AHCI class code (Jeff Garzik ) [222674]
- fix vdso in core dumps (Roland McGrath ) [211744]

* Fri Jan 12 2007 Don Zickus <dzickus@redhat.com> [2.6.18-1.3014.el5]
- XEN: Replace inappropriate domain_crash_synchronous use (Herbert Xu ) [221239]
- SATA timeout boot message  (Peter Martuccelli ) [222108]
- Netlabel: off by one and init bug in netlbl_cipsov4_add_common (Eric Paris ) [221648]
- NetLabel: fix locking issues (Eric Paris ) [221504]
- mm: fix statistics in vmscan.c (Peter Zijlstra ) [222030]
- usb: Sun/AMI virtual floppy issue (Pete Zaitcev ) [219628]
- bonding: eliminate rtnl assertion spew (Andy Gospodarek ) [210577]
- Xen: Make HVM hypercall table NR_hypercalls entries big. (Herbert Xu ) [221818]
- xen: Add PACKET_AUXDATA cmsg (Herbert Xu ) [219681]

* Wed Jan 10 2007 Don Zickus <dzickus@redhat.com> [2.6.18-1.3002.el5]
- ppc64: initialization of hotplug memory fixes (Janice M. Girouard ) [220065]
- GFS2: return error for NULL inode (Russell Cattelan ) [217008]
- scsi: prevent sym53c1510 from claiming the wrong pci id (Chip Coldwell ) [218623]
- net: Disable the qla3xxx network driver. (Tom Coughlan ) [221328]
- xen: Disable CONFIG_IDE_GENERIC (Jarod Wilson ) [220099]
- sound: add support for STAC9205 codec (John Feeney ) [219494]
- ipv6: panic when bringing up multiple interfaces (Thomas Graf ) [218039]
- XFRM Audit: correct xfrm auditing panic (Eric Paris ) [222033]
- edac: fix /proc/bus/pci/devices to allow X to start (John Feeney ) [219288]
- x86_64: clear_kernel_mapping: mapping has been split. will leak memory. (Larry Woodman ) [218543]
- xen: >4G guest fix (Steven Rostedt ) [217770]
-  fs: listxattr syscall can corrupt user space programs (Eric Sandeen ) [220119]
- CacheFiles: Fix object struct recycling (David Howells ) [215599]
- Remove capability requirement to reading cap-bound (Eric Paris ) [219230]
- disable building ppc64iseries (Don Zickus) [219185]
- update: utrace fixes (Roland McGrath) [214405 215052 216150 209118]
- PPC config file changes for IPMI and DTLK (Peter Martuccelli ) [210214]
- update: Xen: emulate PIT channels for vbios support (Stephen C. Tweedie ) [215647]
- net: qla3xxx panics when eth1 is sending pings (Konrad Rzeszutek ) [220246]
- s390: inflate spinlock kabi (Jan Glauber ) [219871]
- x86: Add panic on unrecovered NMI (Prarit Bhargava ) [220829]
- ppc64: fix booting kdump env. w/maxcpus=1 on power5 (Jarod Wilson ) [207300]
- netfilter: iptables stop fails because ip_conntrack cannot unload. (Thomas Graf ) [212839]
- gfs: Fix gfs2_rename lock ordering (for local filesystem) (Wendy Cheng ) [221237]
- GFS2: Fix ordering of page disposal vs. glock_dq (Steven Whitehouse ) [220117]
- xen: fix nosegneg detection (Rik van Riel ) [220675]
- mm: Fix for shmem_truncate_range() BUG_ON() (Larry Woodman ) [219821]
- x86_64: enabling lockdep hangs the system (Don Zickus ) [221198]
- dlm: change some log_error to log_debug (David Teigland ) [221326]
- dlm: disable debugging output (David Teigland ) [221326]
- fs: ext2_check_page denial of service (Eric Sandeen ) [217018]
- CPEI - prevent relocating hotplug irqs (Kei Tokunaga ) [218520]
- Networking: make inet->is_icsk assignment binary (Eric Paris ) [220482]
- net: b44: phy reset problem that leads to link flap  (Neil Horman ) [216338]
- autofs - fix panic on mount fail - missing autofs module update (Ian Kent ) [221118]
- net: act_gact: division by zero (Thomas Graf ) [218348]
- ppc64: Avoid panic when taking altivec exceptions from userspace. (David Woodhouse ) [220586]

* Wed Jan 03 2007 Don Zickus <dzickus@redhat.com> [2.6.18-1.2961.el5]
- new set of kabi whitelists (Jon Masters) [218682]
- x86: remove unwinder patches from x86/x86_64 (Don Zickus ) [220238]
- usb: disable ub and libusual (Pete Zaitcev ) [210026]
- NetLabel: stricter configuration checking (Eric Paris ) [219393]
- scsi: fix iscsi sense len handling (Mike Christie ) [217933]
- Xen: emulate PIT channels for vbios support (Stephen C. Tweedie ) [215647]
- VM: Fix nasty and subtle race in shared mmap'ed page writeback (Eric Sandeen ) [220963]
- Audit: Add type for 3rd party, emit key for audit events (Eric Paris ) [217958]
- NFS: system stall on NFS stress under high memory  pressure (Steve Dickson ) [213137]
- netfilter: IPv6/IP6Tables Vulnerabilities (Thomas Graf ) [220483]
- acpi: increase ACPI_MAX_REFERENCE_COUNT (Doug Chapman ) [217741]
- Race condition in mincore can cause ps -ef to hang (Doug Chapman ) [220480]
- Call init_timer() for ISDN PPP CCP reset state timer (Marcel Holtmann ) [220163]
- Race condition concerning VLAPIC interrupts (Bhavana Nagendra ) [213858]

* Tue Jan 02 2007 Don Zickus <dzickus@redhat.com> [2.6.18-1.2943.el5]
- CIFS: Explicitly set stat->blksize (Steve Dickson ) [210608]
- FS-Cache: dueling read/write processes fix (Steve Dickson ) [212831]
- xen: Use swiotlb mask for coherent mappings too (Herbert Xu ) [216472]
- ia64: Kexec, Kdump on SGI IA64 NUMA machines fixes (George Beshers ) [219091]
- splice : Must fully check for fifos (Don Zickus ) [214289]
- Xen: Fix potential grant entry leaks on error (Herbert Xu ) [217993]
- e1000: truncated TSO TCP header with 82544, workaround (Herbert Xu ) [206540]
- scsi: fix bus reset in qla1280 driver (George Beshers ) [219819]
- scsi: add qla4032 and fix some bugs (Mike Christie ) [213807]
- XFRM: Config Change Auditing (Eric Paris ) [209520]
- Xen: ia64 guest networking finally works (Jarod Wilson ) [218895]
- scsi structs for future known features and fixes (Mike Christie ) [220458]
- squashfs fixup (Steve Grubb ) [219534]
- ppc64: DLPAR virtual CPU removal failure - cppr bits (Janice M. Girouard ) [218058]
- ia64: allow HP ZX1 systems to initalize swiotlb in kdump (Neil Horman ) [220064]
- export tasklist_lock (David Howells ) [207992]
- gfs2: Initialization of security/acls (Steven Whitehouse ) [206126]
- x86: handle _PSS object range corectly in speedstep-centrino (Brian Maly ) [211690]
- GFS2 change nlink panic (Wendy Cheng ) [215088]
- scsi: fix oops in iscsi packet transfer path (Mike Christie ) [215381]
- Fix Emulex lpfc ioctl on PPC (Tom Coughlan ) [219194]
- Xen: Fix agp on x86_64 under Xen (Stephen C. Tweedie ) [217715]
- Emulex lpfc update to 8.1.10.2 (Tom Coughlan ) [218243]
- bluetooth: Add packet size checks for CAPI messages (Marcel Holtmann ) [219139]
- x86_64: create Calgary boot knob (Konrad Rzeszutek ) [220078]
- cciss bugfixes (Tom Coughlan ) [185021]
- ia64: Do not call SN_SAL_SET_CPU_NUMBER twice on cpu 0 on booting (Erik Jacobson ) [219722]
- scsi: Empty /sys/class/scsi_host/hostX/config  file (Janice M. Girouard ) [210239]
- refresh: Reduce iommu page size to 4K on 64K page PPC systems (Janice M. Girouard) [212097]
- update: Xen netback: Reenable TX queueing and drop pkts after timeout (Herbert Xu ) [216441]

* Sun Dec 17 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2910.el5]
- xen: Update xen paravirt framebuffer to upstream protocol (fixes) (Stephen C. Tweedie ) [218048]
- xen: Update xen paravirt framebuffer to upstream protocol (Stephen C. Tweedie ) [218048]
- nfs: disable Solaris NFS_ACL version 2  (Steve Dickson ) [215073]
- xen: EXPORT_SYMBOL(zap_page_range) needs to be moved (Stephen C. Tweedie ) [218476]
- ppc64: disable unused drivers that cause oops on insmod/rmmod (Janice M. Girouard ) [206658]
- scsi: GoVault not accessible due to software reset. (Konrad Rzeszutek ) [215567]
- GFS2 fix DIO deadlock (Steven Whitehouse ) [212627]
- dlm: fix lost flags in stub replies (David Teigland ) [218525]
- CacheFiles: Improve/Fix reference counting (David Howells ) [212844]
- gfs2: Fails back to readpage() for stuffed files (Steven Whitehouse ) [218966]
- gfs2: Use try locks in readpages (Steven Whitehouse ) [218966]
- GFS2 Readpages fix (part 2) (Steven Whitehouse ) [218966]
- gfs2: Readpages fix  (Steven Whitehouse ) [218966]
- bonding: Don't release slaves when master is admin down (Herbert Xu ) [215887]
- x86_64: fix execshield randomization for heap (Brian Maly ) [214548]
- x86_64: check and enable NXbit support during resume (Vivek Goyal ) [215954]
- GPL export truncate_complete_page (Eric Sandeen ) [216545]
- mm: reject corrupt swapfiles earlier (Eric Sandeen ) [213118]
- QLogic qla2xxx - add missing PCI device IDs (Tom Coughlan ) [219350]
- mpt fusion bugfix and maintainability improvements (Tom Coughlan ) [213736]
- scsi: make fc transport removal of target configurable (Mike Christie ) [215797]
- gfs2: don't try to lockfs after shutdown (Steven Whitehouse ) [215962]
- xen: emulation for accesses faulting on a page boundary (Stephen C. Tweedie ) [219275]
- gfs2: dirent format compatible with gfs1 (Steven Whitehouse ) [219266]
- gfs2: Fix size caclulation passed to the allocator. (Russell Cattelan ) [218950]
- ia64: PAL_GET_PSTATE implementation (Prarit Bhargava ) [184896]
- CacheFiles: Handle ENOSPC on create/mkdir better (David Howells) [212844]
- connector: exessive unaligned access (Erik Jacobson ) [218882]
- revert: Audit: Add type for 3rd party, emit key for audit events (Eric Paris ) [217958]

* Wed Dec 13 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2876.el5]
- touch softdog during oops (Dave Jones ) [218109]
- selinux: allow quoted commas for certain catagories in context mounts (Eric Paris ) [211857]
- xen: oprofile on Intel CORE (Glauber de Oliveira Costa ) [213964]
- Xen: make ballooning work right (xen part) (Rik van Riel ) [212069]
- Xen: make ballooning work right (Rik van Riel ) [212069]
- Xen: HVM crashes on IA32e SMP (Glauber de Oliveira Costa ) [214774]
- gfs2: Fix uninitialised variable (Steven Whitehouse ) [219212]
- GFS2: Don't flush everything on fdatasync (Steven Whitehouse ) [218770]
- Disable PCI mmconf and segmentation on HP xw9300/9400 (Bhavana Nagendra ) [219159]
- Audit: Add type for 3rd party, emit key for audit events (Eric Paris ) [217958]
- Fix time skew on Intel Core 2 processors (Prarit Bhargava ) [213050]
- Xen : Fix for SMP Xen guest slow boot issue on AMD systems (Bhavana Nagendra ) [213138]
- GFS2: fix mount failure (Josef Whiter ) [218327]
- cramfs: fix zlib_inflate oops with corrupted image (Eric Sandeen ) [214705]
- xen: Fix xen swiotlb for b44 module (xen part) (Stephen C. Tweedie ) [216472]
- xen: Fix xen swiotlb for b44 module (Stephen C. Tweedie ) [216472]
- scsi: fix stex_intr signature (Peter Zijlstra ) [219370]
- GFS2: Fix recursive locking in gfs2_permission (Steven Whitehouse ) [218478]
- GFS2: Fix recursive locking in gfs2_getattr (Steven Whitehouse ) [218479]
- cifs: Fix mount failure when domain not specified (Steve Dickson ) [218322]
- GFS2: Fix memory allocation in glock.c (Steven Whitehouse ) [204364]
- gfs2: Fix journal flush problem (Steven Whitehouse ) [203705]
- gfs2: Simplify glops functions (Steven Whitehouse ) [203705]
- gfs2: Fix incorrect fs sync behaviour (Steven Whitehouse ) [203705]
- fix check_partition routines to continue on errors (David Milburn ) [210234]
- fix rescan_partitions to return errors properly (David Milburn ) [210234]
- gfs2: Tidy up bmap & fix boundary bug (Steven Whitehouse ) [218780]
- Fix bmap to map extents properly (Steven Whitehouse ) [218780]
- ide-scsi/ide-cdrom module load race fix (Alan Cox ) [207248]
- dlm: fix receive_request lvb copying (David Teigland ) [214595]
- dlm: fix send_args lvb copying (David Teigland ) [214595]
- device-mapper mirroring - fix sync status change (Jonathan Brassow ) [217582]
- Xen: Copy shared data before verification (Herbert Xu ) [217992]
- s390: common i/o layer fixes (Jan Glauber ) [217799]
- Spurious interrups from ESB2 in native mode (Alan Cox ) [212060]

* Wed Dec 06 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2839.el5]
- Xen: fix xen/ia64/vti panic when config sets maxmem (Aron Griffis ) [214161]
- Xen: ia64 making it work (Aron Griffis ) [210637]
- Xen: upstream patches to make Windows Vista work (Steven Rostedt) [214780]
- enable PCI express hotplug driver (Kei Tokunaga ) [207203]
- d80211: kABI pre-compatibility (John W. Linville ) [214982]
- Xen: ia64 kernel unaligned access (Aron Griffis ) [212505]
- Xen: getting ia64 working; kernel part (Aron Griffis) [210637]
- Xen: Properly close block frontend on non-existant file (Glauber de Oliveira Costa ) [218037]
- SHPCHP driver doesn't work if the system was under heavy load (Kei Tokunaga ) [215561]
- SHPCHP driver doesn't work in poll mode (Kei Tokunaga) [211679]
- pciehp: free_irq called twice (Kei Tokunaga ) [216940]
- pciehp: pci_disable_msi() called to early (Kei Tokunaga ) [216939]
- pciehp: parallel hotplug operations cause kernel panic (Kei Tokunaga ) [216935]
- pciehp: info messages are confusing (Kei Tokunaga ) [216932]
- pciehp: Trying to enable already enabled slot disables the slot (Kei Tokunaga ) [216930]
- CacheFiles: cachefiles_write_page() shouldn't indicate error twice (David Howells) [204570]
- IPMI - allow multiple Baseboard Management Centers (Konrad Rzeszutek ) [212572]
- nfs - set correct mode during create operation (Peter Staubach ) [215011]
- Xen: blkback: Fix potential grant entry leaks on error (Rik van Riel ) [218355]
- Xen: blkback: Copy shared data before verification (Rik van Riel) [217994]
- revert: Xen: fix SMP HVM guest timer irq delivery (Rik van Riel ) [213138]

* Tue Dec 05 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2817.el5]
- Adding in a kabi_whitelist (Jon Masters) [218402]
- Xen: AMD-V HVM fix for Windows hibernate (Bhavana Nagendra ) [217367]
- Xen: fix SMP HVM guest timer irq delivery (Rik van Riel ) [213138]
- NetLabel: bring current with upstream: cleanup/future work (Eric Paris ) [218097]
- NetLabel: bring current with upstream: performance (Eric Paris ) [218097]
- NetLabel: bring current with upstream: bugs (Eric Paris ) [218097]
- TG3 support Broadcom 5756M/5756ME  Controller (John Feeney ) [213204]
- tg3: BCM5752M crippled after reset (Andy Gospodarek ) [215765]
- sata ata_piix map values (Geoff Gustafson ) [204684]
- e1000: Reset all functions after a PCI error (Janice M. Girouard) [211694]
- prevent /proc/meminfo's HugePages_Rsvd from going negative. (Larry Woodman ) [217910]
- netlabel: disallow editing of ip options on packets with cipso options (Eric Paris ) [213062]
- xen netback: Fix wrap to zero in transmit credit scheduler. (Herbert Xu ) [217574]
- megaraid initialization fix for kdump (Jun'ichi Nick Nomura ) [208451]
- HFS: return error code in case of error (Eric Paris ) [217009]
- Xen: fix 2TB overflow in virtual disk driver (Rik van Riel ) [216556]
- e1000: fix garbled e1000 stats (Neil Horman ) [213939]
- dlm: use recovery seq number to discard old replies (David Teigland ) [215596]
- dlm: resend lock during recovery if master not ready (David Teigland ) [215596]
- dlm: check for incompatible protocol version (David Teigland ) [215596]
- NetLabel: Do not send audit messages if audit is off (Eric Paris ) [216244]
- selinux: give correct response to get_peercon() calls (Eric Paris ) [215006]
- SELinux: Fix oops with non-mls policies (Eric Paris ) [214397]
- Xen blkback: Fix first_sect check. (Rik van Riel ) [217995]
- allow the highest frequency if bios think so. (Dave Jones ) [218106]
- AGP corruption fixes. (Dave Jones ) [218107]

* Mon Dec 04 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2789.el5]
- Xen: fix vcpu hotplug statistics (Rik van Riel ) [209534]
- DLPAR and Hotplug not enabled (Janice M. Girouard ) [207732]
- Reduce iommu page size to 4K on 64K page PPC systems (Janice M. Girouard) [212097]
- e1000: add (2) device ids (Bruce Allan) [184864]
- power6: illegal instruction errors during install (Janice M. Girouard) [216972]
- update_flash is broken across PPC (Janice M. Girouard) [214690]
- write failure on swapout could corrupt data (Peter Zijlstra) [216194]
- IBM veth panic when buffer rolls over (Janice M. Girouard ) [214486]
- Make the x86_64 boot gdt limit exact (Steven Rostedt ) [214736]
- Xen: make netfront device permanent (Glauber de Oliveira Costa ) [216249]
- lockdep: fix ide/proc interaction (Peter Zijlstra ) [210678]
- Xen: fix iSCSI root oops on x86_64 xen domU (Rik van Riel ) [215581]
- Fix flowi clobbering (Chris Lalancette ) [216944]
- Enable netpoll/netconsole for ibmveth (Neil Horman ) [211246]
- dlm: fix size of STATUS_REPLY message (David Teigland ) [215430]
- dlm: fix add_requestqueue checking nodes list (David Teigland ) [214475]
- dlm: don't accept replies to old recovery messages (David Teigland ) [215430]
- x86_64: kdump mptable reservation fix  (Vivek Goyal ) [215417]
- Add Raritan KVM USB dongle to the USB HID blacklist (John Feeney ) [211446]
- Fix bogus warning in [un]lock_cpu_hotplug (Prarit Bhargava ) [211301]
- Xen: Avoid touching the watchdog when gone for too long (Glauber de Oliveira Costa ) [216467]
- add missing ctcmpc Makefile target (Jan Glauber ) [184608]
- remove microcode size check for i386 (Geoff Gustafson ) [214798]

* Thu Nov 30 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2769.el5]
- add the latest 2.6.18.4 security patches (Don Zickus) [217904]
- revert: mspec failures due to memory.c bad pte problem (Erik Jacobson ) [211854]

* Wed Nov 29 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2767.el5]
- disable W1 config (Dave Jones ) [216176]
- Xen netback: Reenable TX queueing and drop pkts after timeout (Herbert Xu ) [216441]
- Xen: fix profiling (Rik van Riel ) [214886]
- bnx2: update firmware to correct rx problem in promisc mode (Neil Horman ) [204534]
- sound-hda: fix typo in patch_realtek.c (John W. Linville) [210691]
- Fix sys_move_pages when a NULL node list is passed. (Dave Jones ) [214295]
- proc: readdir race fix (Nobuhiro Tachino ) [211682]
- device mapper: /sys/block/dm-* entries remain after removal (Milan Broz ) [214905]
- Fix 64k page table problems on ppc specific ehca driver (Doug Ledford ) [199765]
- configfs: mutex_lock_nested() fix (Eric Sandeen ) [211506]
- CIFS: Explicitly set stat->blksize (Eric Sandeen ) [214607]
- Compute checksum properly in netpoll_send_udp (Chris Lalancette ) [214542]
- Noisy stack trace by memory hotplug on memory busy system (Kei Tokunaga ) [213066]
- catch blocks beyond pagecache limit in __getblk_slow (Eric Sandeen ) [214419]
- xen privcmd: Range-check hypercall index. (Herbert Xu ) [213178]
- strange messages around booting and acpi-memory-hotplug (Kei Tokunaga) [212231]
- Fix panic in CPU hotplug on ia64 (Prarit Bhargava ) [213455]
- Fix spinlock bad magic when removing xennet device (Chris Lalancette ) [211684]
- netlabel: various error checking cleanups (Eric Paris ) [210425]
- mspec failures due to memory.c bad pte problem (Erik Jacobson ) [211854]
- Fix autofs creating bad dentries in NFS mount (David Howells ) [216178]

* Thu Nov 09 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2747.el5] 
- Set HZ to 1000 for kernel and 250 for Xen (Don Zickus) [198594] 
- Custom Diagnostics kernel module fails to load on RHEL5 (Janice Girouard) [213020] 
- kernel: FS-Cache: error from cache: -105 (2nd part) (Don Zickus) [214678] 
 
* Mon Nov 06 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2746.el5] 
- configure XPC as a loadable kernel module instead of static (Erik Jacobson) [213903] 
- kernel BUG at drivers/xen/core/evtchn.c:482! (Glauber de Oliveira Costa) [210672] 
- IPv6 MRT: 'lockdep' annotation is missing? (Thomas Graf) [209313] 
- sort PCI device list breadth-first (John Feeney) [209484] 
- reenable xen pae >4GB patch (Don Zickus) 
 
* Sun Nov 05 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2745.el5] 
- disable the xen-pae patch due to compile problems

* Sun Nov 05 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2744.el5] 
- Kernel Panic on Initial boot of guest (Steven Rostedt) [211633] 
- kernel unable to read partition (device busy) (Peter Zijlstra) [212191] 
- QEMU always crashes (Don Zickus) [212625] 
- kernel: FS-Cache: error from cache: -105 (Steve Dickson) [212831] 
- DLM oops in kref_put when umounting (Patrick Caulfield) [213005] 
- gfs umount hung, message size too big (Patrick Caulfield) [213289] 
- CPU hotplug doesn't work trying to BSP offline (Keiichiro Tokunaga) [213324] 
- status messages ping-pong between unmounted nodes (Dave Teigland) [213682] 
- res_recover_locks_count not reset when recover_locks is aborted (Dave Teigland) [213684] 
- disable CONFIG_ISA (Don Zickus) 
 
* Wed Nov 01 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2740.el5] 
- Remove support for ipw3945 driver (Don Zickus) [195534] 
- acpiphp will not load due to unknown symbols (Prarit Bhargava) [209506] 
- Can not install rhel5 b1 on ipr dasd. (Janice Girouard) [210851] 
- Can't make SCTP connections between Xen guests (Don Zickus) [212550] 
- eHEA update to support 64K pages for Power6 (Janice Girouard) [212041] 
- Failure to boot second kernel on HP hardware (Don Zickus) [212578] 
- dlm deadlock during simultaneous mount attempts (Dave Teigland) [211914] 
- CMT-eligible ipw2200/2915 driver (John W. Linville) [184862] 
- CVE-2006-5174 copy_from_user information leak on s390 (Jan Glauber) [213568] 
- NFSv4: fs_locations support (Steve Dickson) [212352] 
- [IPv6] irrelevant rules break ipv6 routing. (Thomas Graf) [209354] 
- [IPv6] blackhole and prohibit rule types not working (Thomas Graf) [210216] 
- [KEXEC] bad offset in icache instruction crashes Montecito systems (Jarod Wilson) [212643] 
- assertion "FALSE" failed in gfs/glock.c (Dave Teigland) [211622] 
- I/O DLPAR and Hotplug not enabled in RHEL5 (Janice Girouard) [207732] 
 
* Thu Oct 26 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2739.el5] 
- SHPCHP driver doesn't work (Keiichiro Tokunaga) [210478] 
- ext3/jbd panic (Eric Sandeen) [209647] 
- Oops in nfs_cancel_commit_list (Jeff Layton) [210679] 
- kernel Soft lockup detected on corrupted ext3 filesystem (Eric Sandeen) [212053] 
- CIFS doesn't work (Steve Dickson) [211070] 
 
* Thu Oct 26 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2738.el5] 
- need to convert bd_mount_mutex on gfs2 also (Peter Zijlstra)

* Wed Oct 25 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2737.el5] 
- Grant table operations unsuitable for guest domains (Rik van Riel) [210489] 
- AMD-V HVM windows guest boot menu timer issue (Steven Rostedt) [209001] 
- iflags.h is not upstream (Steve Whitehouse) [211583] 
- ACPIPHP doesn't work (Keiichiro Tokunaga) [209677] 
- IBMVSCSI does not correctly reenable the CRQ (Janice Girouard) [211304] 
- librdmacm-utils failures (Doug Ledford) [210711] 
- Badness in debug_mutex_unlock at kernel/mutex-debug.c:80 (Janice Girouard) [208500] 
- Stratus memory tracking functionality needed in RHEL5 (Kimball Murray) [209173, 211604] 
 
* Tue Oct 24 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2736.el5] 
- Can't unload gnbd module, 128 references (Peter Zijlstra) [211905]
- ddruid does not recognize dasd drives (Peter Zijlstra) [210030]
 
* Mon Oct 23 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2733.el5]
- disable x86_64 dirty page tracking, it breaks some machines (Don Zickus)

* Tue Oct 17 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2732.el5] 
- possible recursive locking detected: cachefilesd (David Howells) [204615] 
- Stratus memory tracking functionality needed in RHEL5 (Kimball Murray) [209173] 
- nfs handled rpc error incorrectly (Steve Dickson) [207040] 
- cachefiles: inode count maintance (Steve Dickson) [209434] 
- mkinitrd: iSCSI root requires crc32c module (Mike Christie) [210232] 
- implemented sysrq-w to dump all cpus (Larry Woodman) 
- enable panic_on_oops (Dave Anderson) 
- re-enable x86_64 stack unwinder fixes (Don Zickus) 
- disable kernel debug flags (Don Zickus) 
 
* Tue Oct 17 2006 Stephen C. Tweedie <sct@redhat.com>
- Fix up xen blktap merge to restore modular build

* Tue Oct 17 2006 Don Zickus <dzickus@redhat.com> 
- fix xen breakage from last night's incorrect commits

* Mon Oct 16 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2729.el5] 
- revert Kpobes backport from 2.6.19-rc1, it fails to compile

* Mon Oct 16 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2728.el5] 
- Update FC transport and Emulex lpfc Fibre Channel Driver (Tom Coughlan) [207551] 
- NFSv4 using memory after its freed fix (Steve Dickson) [206996] 
- GFS2 dirents are 'unkown' type (Steve Whitehouse) [210493] 
- Cachefs double unlock (Steve Dickson) [210701] 
- tty locking cleanup (Prarit Bhargava) [210249] 
- ibmveth fails in kdump boot (Janice Girouard - IBM on-site partner) [199129] 
- Kpobes backport from 2.6.19-rc1 (Anil S Keshavamurthy) [210555] 
- Ia64 - kprobe opcode must reside on 16 bytes alignment (Anil S Keshavamurthy) [210552] 
- GFS2 forgets to unmap pages (Steve Whitehouse) [207764] 
- DIO needs to avoid using page cache (Jeffrey Moyer) [207061] 
- megaraid_sas: update (Chip Coldwell) [209463] 
- NFS data corruption (Steve Dickson) [210071] 
- page align bss sections on x86_64 (Vivek Goyal) [210499] 
- blkbk/netbk modules don't load (Aron Griffis) [210070] 
- blktap does not build on ia64 (Aron Griffis) [208895] 
- blkbk/netbk modules don't load (Rik van Riel) [202971] 
- patches from xen-ia64-unstable (Rik van Riel) [210637] 
- Xen version strings need to reflect exact Red Hat build number (Stephen Tweedie) [211003] 
- updated to 2.6.18.1 stable series (Don Zickus) 
- updated execshield patch (Don Zickus) 
- revert CONFIG_PCI_CALGARY_IOMMU config (Don Zickus) 
- disable CONFIG_MAMBO (Don Zickus) 
 
* Thu Oct 12 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2727.el5] 
- I/O errors with dm-multipath when adding new path (Alasdair Kergon) [169302] 
- Kdump on i386 fails - Second kernel panics (Vivek Goyal) [207598] 
- patch to qla4xxx for supporting ioctl module (Mike Christie) [207356] 
- lockdep fixes (Peter Zijlstra) [208165 209135 204767] 
- printk cleanup (Dave Jones) 
- spec file cleanup (Dave Jones, Bill Nottingham) 
- gfs-dlm fix (Patrick Caulfield) 
- find-provides fix (Jon Masters) 
 
* Wed Oct 11 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2726.el5] 
- need to disable all cpu frequency scaling drivers in Xen kernel (Rik van Riel) [210336 208942] 
- radeon hangs DMA when CONFIG_CALGARY_IOMMU is build in kernel. (Konrad Rzeszutek) [210380] 
- Got Call Trace message when remove veth module (Janice Girouard) [208938] 
- cannot generate kABI deps unless kernel is installed (Jon Masters) [203926] 
- ctcmpc driver (Jan Glauber) [184608] 
- PTRACE_DETACH doesn't deliver signals under utrace. (Aristeu S. Rozanski F.) [207674] 
- SG_SCATTER_SZ causing Oops during scsi disk microcode update (Doug Ledford) [207146] 
- ia64 kprobe fixes (David Smith) 
 
* Tue Oct 10 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2725.el5] 
- Duplicate dput in sysfs_update_file can cause a panic. (Prarit Bhargava) [209454] 
- Lock issue with 2.6.18-1.2702.el5, NetworkManager and ipw3945 (John W. Linville) [208890] 
- cpqarray module fails to detect arrays (Chip Coldwell) [205653] 
- stex.c driver for Promise SuperTrak EX is missing (Jeff Garzik) [209179] 
- NetLabel does not audit configuration changes (Eric Paris) [208456] 
- NetLabel has a race problem in the cache (Eric Paris) [209324] 
- kernel/lockdep.c:1814/trace_hardirqs_on() (Not tainted) for APM (Peter Zijlstra) [209480] 
-  correct netlabel secid for packets without a known label (Eric Paris) [210032] 
- IPSec information leak with labeled networking (Eric Paris) [209171] 
- NetLabel hot-add memory confict pre-beta2 kenrel x86_64 (Konrad Rzeszutek) [208445] 
- NFS data corruption (Steve Dickson) [210071] 
- kernel dm multipath: ioctl support (Alasdair Kergon) [207575] 
- kernel dm: fix alloc_dev error path (Alasdair Kergon) [209660] 
- kernel dm snapshot: fix invalidation ENOMEM (Alasdair Kergon) [209661] 
- kernel dm snapshot: chunk_size parameter is not required after creation (Alasdair Kergon) [209840] 
- kernel dm snapshot: fix metadata error handling (Alasdair Kergon) [209842] 
- kernel dm snapshot: fix metadata writing when suspending (Alasdair Kergon) [209843] 
- kernel dm: full snapshot removal attempt causes a seg fault/kernel bug (Alasdair Kergon) [204796] 
- dm mirror: remove trailing space from table (Alasdair Kergon) [209848] 
- kernel dm: add uevent change event on resume (Alasdair Kergon) [209849] 
- kernel dm crypt: Provide a mechanism to clear key while device suspended (Milan Broz) [185471] 
- kernel dm: use private biosets to avoid deadlock under memory pressure (Alasdair Kergon) [209851] 
- kernel dm: add feature flags to structures for future kABI compatibility (Alasdair Kergon) [208543] 
- kernel dm: application visible I/O errors with dm-multipath and queue_if_no_path when adding new path (Alasdair Kergon) [169302] 
- refresh ia64-kexec-kdump patch (Don Zickus) 
- update exec-shield patch (Don Zickus) 
- revert x86 unwinder fixes (Don Zickus) 
 
 
* Mon Oct 09 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2722.el5]  
- update utrace patch to fix s390 build problems
- ia64 hotswap cpu patch fixes to compile under xen
- ia64 export fixes

* Mon Oct 09 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2718.el5]  
- Audit Filtering on PPID for = and != is inverted (Eric Paris) [206425] 
- Adding Hitachi SANRISE entries into SCSI white list (Chip Coldwell) [206532] 
- forward port of SCSI blacklist from RHEL4 (Chip Coldwell) [208256] 
- Need to add ALSA support for Broadwater platform (John W. Linville) [184855] 
- /proc/<pid>/smaps doesn't give any data (Alexander Viro) [208589] 
- ACPI based CPU hotplug causes kernel panic (Keiichiro Tokunaga) [208487] 
- New infiniband 12x power driver opensourced from IBM (Janice Girouard) [184791] 
- iscsi oops when connection creation fails (Mike Christie) [209006] 
- nommconf work-around still needed for AMD chipsets (Jim Baker) [207396] 
- ProPack XPMEM exported symbols (Greg Edwards) [206215] 
- PCI error recovery bug in e100 and e1000 cards (John W. Linville) [208187] 
- / on raid fails to boot post-install system (Jan Glauber) [196943] 
- auditctl fails to reject malformed ARCH filter (Eric Paris) [206427] 
- oom-killer updates (Larry Woodman) [208583] 
- NFS is revalidating directory entries too often (Steve Dickson) [205454] 
- kernel-xen cannot reboot (Stephen Tweedie) [209841] 
- Unsupported FS's in RHEL 5 Beta 1 (Don Zickus) [206486] 
 
* Thu Oct 05 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2717.el5] 
- patch fix for RDSCTP (Don Zickus)

* Thu Oct 05 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2715.el5] 
- RDTSCP Support (Bhavana Nagendra) [185057] 
- s390 kprobe on larl instruction crashes system (Jan Glauber) [205738] 
- single stepping is broken when kprobes is configured (Jan Glauber) [205739] 
- autofs kernel patches resulting from Connectathon testing (Ian Kent) [206952] 
- Include the qla3xxx networking driver (Konrad Rzeszutek) [208182] 
- overzealous sanity checking in sys_poll() (Chris Snook) [204705] 
- automounter cannot shutdown when timeout=0 (Ian Kent) [205836] 
- Rewrite of journaling data commit code (Eric Sandeen) [207739] 
- qla4xxx soft lockup when ethernet cable disconnected (Mike Christie) [206063] 
- hypfs_kill_super() check for initialized root inode (Jan Glauber) [207717] 
- The Matrox graphics driver is not built (Janice Girouard) [207200] 
 
* Mon Oct 02 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2714.el5] 
- Wrong SELinux context prevents hidd from working (David Woodhouse) [204655] 
- nfs connectathon component basic test 6 fails.... (Steve Dickson) [208637] 
- unstick STICKY bit to fix suspend/resume (Dave Jones) 
 
* Fri Sep 29 2006 Don Zickus <dzickus@redhat.com>
- fix up ipv6 multiple routing table patch

* Thu Sep 28 2006 Don Zickus <dzickus@redhat.com> 
- s390 ccs/ccw subsystem does not have proper uevent support (Pete Zaitcev) [199994] 
- 'Cannot allocate memory' when cat /proc/scsi/scsi (Chip Coldwell) [200299] 
- Add support for Kirkwood and Kirkwood LP NICs (John W. Linville) [207776] 
- remove userspace support from qla4xxx (Mike Christie) [206063] 
- NetLabel interface has changed in the upstream kernels (Eric Paris) [208119] 
- lockdep fixes (Peter Zijlstra) [208304 204795] 
 
* Thu Sep 28 2006 Steven Whitehouse <swhiteho@redhat.com>
- Updated GFS2/DLM patch

* Wed Sep 27 2006 Don Zickus <dzickus@redhat.com> 
-Multiple routing tables for IPv6 (Thomas Graf) [179612] 
-bunch of lockdep fixes (Peter Zijlstra) [200520 208294 208293 208292 208290] 
-rearrange the cachefs patches for easier future maintance (Steve Dickson) 
-enable some TCP congestion algorithms (David Miller) 
-add a test patch (Eric Paris) 
 
* Tue Sep 26 2006 Don Zickus <dzickus@redhat.com>
- Need to add the sata sas bits
 
* Tue Sep 26 2006 Don Zickus <dzickus@redhat.com> 
-Native SAS and SATA device support - SATA/IDE converter (Janice Girouard) [196336] 
-kernel unaligned access messages in rhel5a1 (Prarit Bhargava) [198572] 
-problems with LUNs mapped at LUN0 with iscsi and netapp filers (Mike Christie) [205802] 
-ext3 fails to mount a 16T filesystem due to overflows (Eric Sandeen) [206721] 
-possible recursive locking detected - swapper/1 (Peter Zijlstra) [203098] 
-FS-Cache: error from cache: -28 (David Howells) [204614] 
-aic94xx driver does not recognise SAS drives in x366 (Konrad Rzeszutek) [206526] 
-Support for 3945 driver (John W. Linville) [195534] 
-Memory Hotplug fails due to relocatable kernel patches (Vivek Goyal) [207596] 
-Potential overflow in jbd for filesystems > 8T (Eric Sandeen) [208024] 
-2,4-node x460 halts during bootup after installation (Konrad Rzeszutek) [203971] 
 
* Mon Sep 25 2006 Don Zickus <dzickus@redhat.com>
- fix x86 relocatable patch (again) to build properly

* Mon Sep 25 2006 Dave Jones <davej@redhat.com>
- Disable 31bit s390 kernel builds.

* Mon Sep 25 2006 Jarod Wilson <jwilson@redhat.com>
- Make kernel packages own initrd files

* Mon Sep 25 2006 John W. Linville <linville@redhat.com>
- Add periodic work fix for bcm43xx driver

* Sat Sep 23 2006 Dave Jones <davej@redhat.com>
- Disable dgrs driver.

* Fri Sep 22 2006 David Woodhouse <dwmw2@redhat.com>
- Fix PowerPC audit syscall success/failure check (#204927)
- Remove offsetof() from <linux/stddef.h> (#207569)
- One line per header in Kbuild files to reduce conflicts
- Fix visibility of ptrace operations on ppc32
- Fix ppc32 SECCOMP

* Thu Sep 21 2006 Dave Jones <davej@redhat.com>
- reiserfs: make sure all dentry refs are released before
  calling kill_block_super
- Fix up some compile warnings

* Thu Sep 21 2006 Mike Christie <mchristie@redhat.com>
- clean up spec file.

* Thu Sep 21 2006 Mike Christie <mchristie@redhat.com>
- drop 2.6.18-rc iscsi patch for rebase

* Wed Sep 20 2006 Juan Quintela <quintela@redhat.com>
- xen HV printf rate limit (rostedt).
- xen HV update to xen-unstable cset11540:9837ff37e354
- xen-update:
  * linux-2.6 changeset:   34294:dc1d277d06e0
  * linux-2.6-xen-fedora changeset:   36184:47c098fdce14
  * xen-unstable changeset:   11540:9837ff37e354

* Wed Sep 20 2006 Dave Jones <davej@redhat.com>
- 2.6.18
- i965 AGP suspend support.
- AGP x8 fixes.

* Tue Sep 19 2006 Juan Quintela <quintela@redhat.com>
- xen update to 2.6.18-rc7-git4.
  * linux-2.6 changeset: 34288:3fa5ab23fee7
  * linux-2.6-xen-fedora changeset: 36175:275f8c0b6342
  * xen-unstable changeset: 11486:d8bceca5f07d

* Tue Sep 19 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc7-git4
- Further lockdep fixes. (#207064)

* Tue Sep 19 2006 Don Zickus <dzickus@redhat.com>
- EXT3 overflows at 16TB (#206721)

* Tue Sep 19 2006 Don Zickus <dzickus@redhat.com>
- Increase nodes supported on ia64 (#203184)
- Powernow K8 Clock fix (#204354)
- NetLabel fixes

* Mon Sep 18 2006 Dave Jones <davej@redhat.com>
- Fix RTC lockdep bug. (Peter Zijlstra)

* Mon Sep 18 2006 Juan Quintela <quintela@redhat.com>
- xen HV update (cset 11470:2b8dc69744e3).

* Mon Sep 18 2006 David Woodhouse <dwmw2@redhat.com>
- Fix various Bluetooth compat ioctls

* Sun Sep 17 2006 Juan Quintela <quintela@redhat.com>
- xen update:
  * linux-2.6 changeset: 34228:ea3369ba1e2c
  * linux-2.6-xen-fedora changeset: 36107:47256dbb1583
  * linux-2.6-xen changeset: 22905:d8ae02f7df05
  * xen-unstable changeset: 11460:1ece34466781ec55f41fd29d53f6dafd208ba2fa

* Sun Sep 17 2006 Dave Jones <davej@redhat.com>
- Fix task->mm refcounting bug in execshield. (#191094)
- 2.6.18rc7-git2
- 586 SMP support.

* Sat Sep 16 2006 David Woodhouse <dwmw2@redhat.com>
- Implement futex primitives on IA64 and wire up [gs]et_robust_list again
  (patch from Jakub, #206613)

* Fri Sep 15 2006 Mike Christie <mchristie@redhat.com>
- fix slab corruption when starting qla4xxx with iscsid not started.

* Thu Sep 14 2006 Don Zickus <dzickus@redhat.com>
- add include/asm-x86_64/const.h to exported header file list
  used by the x86 relocatable patch (inside include/asm-x86_64/page.h)
  
* Thu Sep 14 2006 Dave Jones <davej@redhat.com>
- kprobe changes to make systemtap's life easier.

* Thu Sep 14 2006 Don Zickus <dzickus@redhat.com>
- sync up beta1 fixes and patches
   - includes infiniband driver
   - aic9400/adp94xx updates
   - squashfs s390 fix
- include x86 relocatable patch at end of list
- some /proc/kcore changes for x86 relocatable kernel
   
* Thu Sep 14 2006 David Woodhouse <dwmw2@redhat.com>
- 2.6.18rc7-git1
- header file fixups
- use correct arch for 'make headers_install' when cross-building

* Wed Sep 13 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc7

* Tue Sep 12 2006 David Woodhouse <dwmw2@redhat.com>
- Export <linux/netfilter/xt_{CONN,}SECMARK.h> (#205612)

* Tue Sep 12 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc6-git4
- Enable IFB driver. (#204552)
- Export copy_4K_page for ppc64

* Tue Sep 12 2006 David Woodhouse <dwmw2@redhat.com>
- GFS2 update

* Mon Sep 11 2006 Roland McGrath <roland@redhat.com>
- s390 single-step fix

* Mon Sep 11 2006 Dave Jones <davej@redhat.com>
- Add a PCI ID to sata_via
- Intel i965 DRM support.
- Fix NFS/Selinux oops. (#204848)

* Sat Sep  9 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc6-git3

* Fri Sep  8 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc6-git2

* Thu Sep  7 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc6-git1
- GFS2/DLM updates.

* Wed Sep  6 2006 Roland McGrath <roland@redhat.com>
- New utrace patch: fix 32-bit PTRACE_PEEKUSR for FP regs on ppc64. (#205179)

* Wed Sep  6 2006 Juan Quintela <quintela@redhat.com>
- Undo rhel5 xen patch for relocatable.

* Wed Sep  6 2006 Dave Jones <davej@redhat.com>
- AGP support for Intel I965

* Tue Sep  5 2006 Jeremy Katz <katzj@redhat.com>
- Update xenfb based on upstream review

* Tue Sep  5 2006 Dave Jones <davej@redhat.com>
- Numerous sparse fixes to Tux.

* Tue Sep  5 2006 Mike Christie <mchristi@redhat.com>
- update iscsi layer to what will be in 2.6.19-rc1

* Tue Sep  5 2006 Dave Jones <davej@redhat.com>
- NFS lockdep fixes.
- Make ia64 Altix IDE driver built-in instead of modular. (#205282)

* Mon Sep  4 2006 Juan Quintela <quintela@redhat.com>
- xenoprof upstream fix.
- update xen HV to cset 11394.
- xen update (3hypercall incompatibility included)
- linux-2.6 changeset: 34073:b1d36669f98d
- linux-2.6-xen-fedora changeset: 35901:b7112196674e
- xen-unstable changeset: 11204:5fc1fe79083517824d89309cc618f21302724e29
- fix ia64 (xen & net xen).

* Mon Sep  4 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc6
- Drop recent NFS changes completely.

* Sun Sep  3 2006 Dave Jones <davej@redhat.com>
- Fix bogus -EIO's over NFS (#204859)
- Enable ptrace in olpc kernels. (#204958)

* Sun Sep  3 2006 Marcelo Tosatti <mtosatti@redhat.com>
- Remove PAE, xen and kdump configs for olpc case

* Sun Sep  3 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc5-git7

* Sat Sep  2 2006 Dave Jones <davej@redhat.com>
- Fix up typo in tux.patch
- 2.6.18rc5-git6

* Wed Aug 30 2006 Juan Quintela <quintela@redhat.com>
- update xen-hv to cset 11256 (pre 3 hypercall breakage).
- remove debug=y from HV compilation.
- xen update (pre 3 hypercall breakage)
  * linux-2.6 changeset: 33957:421a6d428e95
  * linux-2.6-xen-fedora changeset: 35756:78332fcbe5b0
  * xen-unstable changeset: 11251:5fc1fe79083517824d89309cc618f21302724e29
  * get new irqflags code from linux-2.6.tip-xen.

* Wed Aug 30 2006 Jeremy Katz <katzj@redhat.com>
- Fix up DEFAULTKERNEL for kernel-xen[0U]->kernel-xen change

* Wed Aug 30 2006 Marcelo Tosatti <mtosatti@redhat.com>
- Fixes for DUB-E100 vB1 usb ethernet (backported from James M.)

* Tue Aug 29 2006 Jarod Wilson <jwilson@redhat.com>
- 2.6.18-rc5-git1

* Tue Aug 29 2006 Jeremy Katz <katzj@redhat.com>
- Fix serial console with xen dom0

* Tue Aug 29 2006 Don Zickus <dzickus@redhat.com>
- enabled EHEA driver
- x86 relocatable fixes
- audit code fixes for cachefs

* Mon Aug 28 2006 Jeremy Katz <katzj@redhat.com>
- Add updated pv framebuffer patch for Xen and re-enable the config options

* Mon Aug 28 2006 Juan Quintela <quintela@redhat.com>
- ia64 xen fixing.

* Sun Aug 27 2006 David Woodhouse <dwmw2@redhat.com>
- Fix V4L1 stuff in <linux/videodev.h> (#204225)

* Fri Aug 25 2006 Juan Quintela <quintela@redhat.com>
- update xen HV to xen-unstable cset 11251.
- fix ia64 xen HV compilation.
- linux xen kernel update:
  * linux-2.6 changeset: 33681:2695586981b9
  * linux-2.6-xen-fedora changeset: 35458:b1b8e00e7a17
  * linux-2.6-xen changeset: 22861:0b726fcb6780
  * xen-unstable changeset: 11204:5fc1fe79083517824d89309cc618f21302724e29

* Fri Aug 25 2006 Don Zickus <dzickus@redhat.com>
- build fix for ia64 kdump

* Fri Aug 25 2006 Don Zickus <dzickus@redhat.com>
- update utrace
- more gfs2-dlm fixes
- fix xen-devel build directory issue
- add x86, x86_64 relocatable kernel patch for rhel only (davej, forgive my sins)
  - applied xen relocatable cleanup on top of it
- add ia64 kexec/kdump pieces

* Fri Aug 25 2006 Jesse Keating <jkeating@redhat.com>
- Enable i386 for olpc so that kernel-headers is built

* Thu Aug 24 2006 David Woodhouse <dwmw2@redhat.com>
- Update GFS2 patch (from swhiteho)
- Enable kernel-headers build
- Enable i386 build _only_ for kernel-headers

* Tue Aug 22 2006 Don Zickus <dzickus@redhat.com>
- Another lockdep-fix
- NFS fix for the connectathon test
- Enable mmtimer for ia64
- Add support for iscsi qla4xxx

* Tue Aug 22 2006 Marcelo Tosatti <mtosatti@redhat.com>
- Add Libertas wireless driver

* Mon Aug 21 2006 Roland McGrath <roland@redhat.com>
- New utrace patch: experimental support for ia64, sparc64.

* Sun Aug 20 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc4-git1

* Sat Aug 19 2006 Dave Jones <davej@redhat.com>
- Update to latest upstream from GregKH's git tree.

* Sat Aug 19 2006 Juan Quintela <quintela@redhat.com>
- xen kernel update.
  * linux-2.6 changeset: 33525:dcc321d1340a
  * linux-2.6-xen-fedora changeset: 35247:400b0cf28ee4
  * linux-2.6-xen changeset: 22813:80c2ccf5c330
  * xen-unstable changeset: 11069:0340e579f06544431e915d17596ac144145a077e
- xen big config update.  Every config option is the same than normal kernel
  except MICROCODE, TCG_TPM & CONFIG_DEBUG_SLAB.
- disable XEN_FRAMEBUFFER & XEN_KEYBOARD.
- make sysrq c to "crash" all kernels.

* Thu Aug 17 2006 Don Zickus <dzickus@redhat.com>
- NFS 64-bit inode support
- QLogic firmware
- SELinux support for range transitions
- EHEA ethernet driver
- ppc irq mapping fix

* Wed Aug 16 2006 Roland McGrath <roland@redhat.com>
- New utrace patch:
  - Fix s390 single-step for real this time.
  - Revamp how arch code defines ptrace compatibility.

* Wed Aug 16 2006 Dave Jones <davej@redhat.com>
- Update to latest GregKH tree.
- Reenable debug.

* Tue Aug 15 2006 Don Zickus <dzickus@redhat.com>
- cleanup config-rhel-generic to compile again
- removed useless options in config-rhel-generic

* Tue Aug 15 2006 Don Zickus <dzickus@redhat.com>
- ppc64 spec cleanups

* Mon Aug 14 2006 Dave Jones <davej@redhat.com>
- Update to squashfs 3.1 which should fix stack overflows seen
  during installation.
- Merge framebuffer driver for OLPC.

* Sun Aug 13 2006 Juan Quintela <quintela@redhat.com>
- enable ia64 xen again.
- xen kernel-update linux-2.6-xen-fedora cset 35236:70890e6e4a72.
  * fix ia64 compilation problems.

* Sat Aug 12 2006 Juan Quintela <quintela@redhat.com>
- disable ia64 xen, it doesn't compile.
- xen HV update cset 11057:4ee64035c0a3
  (newer than that don't compile on ia64).
- update linux-2.6-xen patch to fix sort_regions on ia64.
- fix %%setup for xen HV to work at xen HV upgrades.

* Fri Aug 11 2006 Juan Quintela <quintela@redhat.com>
- xen HV update cset 11061:80f364a5662f.
- xen kernel update
  * linux-2.6-xen-fedora cset
  * linux-2.6-xen cset 22809:d4b3aba8876df169ffd9fac1d17bd88d87eb67c5.
  * xen-unstable 11060:323eb29083e6d596800875cafe6f843b5627d77b
  * Integrate xen virtual frame buffer patch.
  * Enable CONFIG_CRASH on xen.

* Fri Aug 11 2006 Dave Jones <davej@redhat.com>
- Yet more lockdep fixes.
- Update to GregKH's daily tree.
- GFS2/DLM locking bugfix

* Thu Aug 10 2006 Roland McGrath <roland@redhat.com>
- New utrace patch: fix ptrace synchronization issues.

* Thu Aug 10 2006 Dave Jones <davej@redhat.com>
- GFS2/DLM update.
- Daily GregKH updates
- More lockdep fixes.

* Wed Aug  9 2006 Roland McGrath <roland@redhat.com>
- Fix utrace_regset nits breaking s390.

* Wed Aug  9 2006 Dave Jones <davej@redhat.com>
- Another lockdep fix for networking.
- Change some hotplug PCI options.
- Daily update from GregKH's git tree.
- Unbreak SMP locking in oprofile.
- Fix hotplug CPU locking in workqueue creation.
- K8 EDAC support.
- IPsec labelling enhancements for MLS
- Netlabel: CIPSO labeled networking

* Tue Aug  8 2006 Roland McGrath <roland@redhat.com>
- Fix utrace/ptrace interactions with SELinux.

* Tue Aug  8 2006 Dave Jones <davej@redhat.com>
- Pull post-rc4 fixes from GregKH's git tree.

* Mon Aug  7 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc4

* Sun Aug  6 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc3-git7

* Fri Aug  4 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc3-git6
- Return of signed modules.

* Thu Aug  3 2006 Roland McGrath <roland@redhat.com>
- New utrace patch:
  - fix s390 single-step
  - first third of ia64 support, enable CONFIG_UTRACE (no ptrace yet)

* Fri Aug  3 2006 Juan Quintela <quintela@anano.mitica>
- Update linux-2.6-xen patch.
  * linux-2.6-xen-fedora cset 34931:a3fda906fb82
  * linux-2.6-xen cset 22777:158b51d317b76ebc94d61c25ad6a01d121dff750
  * xen-unstable cset  10866:4833dc75ce4d08e2adc4c5866b945c930a96f225

* Thu Aug  3 2006 Juan Quintela <quintela@redhat.com>
- xen hv compiled with -O2 through Config.mk
- Update xen HV cset 10294.

* Thu Aug  3 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc3-git3
- Fix PCI ID clash between ipr and dac960

* Thu Aug  3 2006 Jon Masters <jcm@redhat.com>
- Copy .config to include/config/auto.conf to avoid unnecessary "make prepare".
- This should finally fix #197220.
- Pulled in patch-2.6.18-rc3-git2.bz2.sign to fix SRPM build failure.

* Wed Aug  2 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc3-git2
- Readd patch to allow 460800 baud on 16C950 UARTs.
- Fix backtracing for interrupt stacks

* Wed Aug  2 2006 Jeremy Katz <katzj@redhat.com>
- add necessary ia64 hv fixes (#201040)

* Wed Aug  2 2006 Dave Jones <davej@redhat.com>
- More GFS2 bugfixing.

* Tue Aug  1 2006 Dave Jones <davej@redhat.com>
- s390 kprobes support.
- Fix oops in libata ata_device_add()
- Yet more fixes for lockdep triggered bugs.
- Merge numerous patches from -mm to improve software suspend.
- Fix incorrect section usage in MCE code that blew up on resume.

* Tue Aug  1 2006 Roland McGrath <roland@redhat.com>
- fix bogus BUG_ON in ptrace_do_wait

* Tue Aug  1 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc3-git1

* Tue Aug  1 2006 Juan Quintela <quintela@redhat.com>
- disable CONFIG_DEBUG_SLAB for xen (should fix #200127).

* Mon Jul 31 2006 Roland McGrath <roland@redhat.com>
- New utrace patch:
  - fix ptrace_do_wait deadlock (#200822, #200605)
  - arch cleanups

* Mon Jul 31 2006 Juan Quintela <quintela@redhat.com>
- disable blktap for xen-ia64 (don't compile).
- enable ia64-xen (it compiles, but still don't boot).

* Mon Jul 31 2006 Juan Quintela <quintela@redhat.com>
- Fix dlm s/u.generic_ip/i_private/.

* Mon Jul 31 2006 Don Zickus <dzickus@redhat.com>
- IA64 compile fixes

* Mon Jul 31 2006 Juan Quintela <quintela@redhat.com>
- Update xen patch to linux-2.6-xen-fedora cset 34801.
	* linux-2.6 cset 33175
	* no linux-2.6-xen updates.
- Remove xen x86_64 8 cpu limit.

* Mon Jul 31 2006 Dave Jones <davej@redhat.com>
- Numerous GFS2/DLM fixes.

* Mon Jul 31 2006 Jeremy Katz <katzj@redhat.com>
- new ahci suspend patch

* Mon Jul 31 2006 Dave Jones <davej@redhat.com>
- VFS: Destroy the dentries contributed by a superblock on unmounting [try #2]

* Sun Jul 30 2006 Jon Masters <jcm@redhat.com>
- Wasn't calling weak-modules properly.
- kabitool not being picked up (weird).

* Sun Jul 30 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc3

* Sat Jul 29 2006 Dave Jones <davej@redhat.com>
- lockdep fix: ipv6
- 2.6.18rc2-git7

* Fri Jul 28 2006 Don Zickus <dzickus@redhat.com>
- Refreshed NFS caching patches
- tweaked some ppc64 kdump config options

* Fri Jul 28 2006 Jon Masters <jcm@redhat.com>
- Remove make-symsets and built-in-where as now handled by kabitool

* Fri Jul 28 2006 Dave Jones <davej@redhat.com>
- Update futex-death patch.

* Thu Jul 27 2006 Roland McGrath <roland@redhat.com>
- s390 utrace fix

* Thu Jul 27 2006 Don Zickus <dzickus@redhat.com>
- Enable kdump on ppc64iseries.  yeah more rpms..

* Thu Jul 27 2006 Dave Jones <davej@redhat.com>
- Add missing export for ia64 (#200396)

* Thu Jul 27 2006 Juan Quintela <quintela@redhat.com>
- review all xen related patches.
- x86_64 dom0, x86_64 domU and i386 domU should work.
- fix xen i386 dom0 boot (#200382).

* Thu Jul 27 2006 Rik van Riel <riel@redhat.com>
- reduce hypervisor stack use with -O2, this really fixes bug (#198932)

* Wed Jul 26 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc2-git6

* Wed Jul 26 2006 Roland McGrath <roland@redhat.com>
- New utrace patch: unsafe_exec fix; s390 build enabled (but non-working).

* Wed Jul 26 2006 Juan Quintela <quintela@redhat.com>
- new xen patch based on linux-2.6-xen cset 22749.
  and linux-2.6 cset 33089.

* Wed Jul 26 2006 Dave Jones <davej@redhat.com>
- Enable sparsemem on ia64. (#108848)

* Wed Jul 26 2006 Juan Quintela <quintela@redhat.com>
- update xen-hv to 10730 cset, should really fix huge timeout problems.

* Wed Jul 26 2006 Juan Quintela <quintela@redhat.com>
- Workaround the huge timeouts problems on xen HV x86.
- xen update and cleanup/reorgatization of xen patches.

* Tue Jul 25 2006 Rik van Riel <riel@redhat.com>
- disable debug=y hypervisor build option because of stack overflow (#198932)

* Tue Jul 25 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc2-git4 & git5

* Tue Jul 25 2006 Jon Masters <jcm@redhat.com>
- Fix kabitool provided find-provides once again.

* Tue Jul 25 2006 Juan Quintela <quintela@redhat.com>
- Use cset number instead of date for xen hypervisor.
- Update xen hypervisor to cset 10712.

* Mon Jul 24 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc2-git2 & git3
- Fix PI Futex exit crash.
- Fix an inotify locking bug.
- Add device mapper mirroring patches.

* Mon Jul 24 2006 Jon Masters <jcm@redhat.com>
- Change kabideps location.

* Mon Jul 24 2006 Juan Quintela <quintela@redhat.com>
- New xen patch, fixes gso, xenoprof, vDSO.

* Sat Jul 22 2006 Dave Jones <davej@redhat.com>
- Enable connector proc events.
- Enable PPC64 memory hotplug.
- 2.6.18rc2-git1

* Sat Jul 22 2006 Juan Quintela <quintela@redhat.com>
- addia64-xen support, not enabled by default.
- add ia64-xen config

* Fri Jul 21 2006 Jeremy Katz <katzj@redhat.com>
- Patch from jakub to use sysv style hash for VDSO to fix booting
  on ia64 (#199634, #199595)
- Fix e1000 crc calculation for things to work with xen
- Update gfs2 patchset

* Thu Jul 20 2006 Roland McGrath <roland@redhat.com>
- Clean up spec changes for debuginfo generation to cover Xen case.
- New version of utrace patch, fixes /proc permissions. (#199014)

* Thu Jul 20 2006 Juan Quintela <quintela@anano.mitica>
- remove xenPAE option, as now the i686 xen kernel is PAE.

* Thu Jul 20 2006 Juan Quintela <quintela@redhat.com>
- Fix to get xen debug info files in the right position.

* Thu Jul 20 2006 Don Zickus <dzickus@redhat.com>
- apparently I was wrong and was fixed already

* Thu Jul 20 2006 Don Zickus <dzickus@redhat.com>
- fixed build_debuginfo to not collect a stripped kernel

* Wed Jul 19 2006 Don Zickus <dzickus@redhat.com>
- Add in support for nfs superblock sharing and cachefs
  patches from David Howells
- Disable 'make prepare' hack as it is breaking ppc symlinks
- Added tracking dirty pages patch from Peter Zijlstra
- Fix for Opteron timer scaling
- Fix for Calgary pci hang

* Wed Jul 19 2006 Juan Quintela <quintela@redhat>
- big xen patch.
- enable xen again.
- redo xen config.
- i686 kernel for xen uses PAE now.
- new xen Hypervisor cset 10711.

* Wed Jul 19 2006 Roland McGrath <roland@redhat.com>
- New version of utrace patch, might fix #198780.

* Wed Jul 19 2006 Jon Masters <jcm@redhat.com>
- Workaround upstream "make prepare" bug by adding an additional prepare stage.
- Fix kabideps

* Tue Jul 18 2006 Jon Masters <jcm@redhat.com>
- Check in new version of kabitool for kernel deps.
- Fix kabitool for correct location of symvers.
- Various other fixes when things broke.

* Sun Jul 16 2006 Dave Jones <davej@redhat.com>
- Support up to 4GB in the 586 kernel again.
- Drop the FPU optimisation, it may be the reason for
  strange SIGFPE warnings various apps have been getting.

* Sat Jul 15 2006 Dave Jones <davej@redhat.com>
- Cleaned up a bunch of bogons in the config files.
- 2.6.18-rc1-git9,git10 & 2.6.18-rc2
- improvements to linked list debugging.

* Fri Jul 14 2006 Don Zickus <dzickus@redhat.com>
- remove the ppc kdump patches

* Fri Jul 14 2006 Dave Jones <davej@redhat.com>
- 2.6.18-rc1-git8

* Thu Jul 13 2006 Dave Jones <davej@redhat.com>
- 2.6.18-rc1-git7
- More lockdep fixes.
- Fix slab corruption issue.

* Thu Jul 13 2006 Mike Christie <mchristi@redhat.com>
- Add iscsi update being sent upstream for 2.6.18-rc2

* Thu Jul 13 2006 Roland McGrath <roland@redhat.com>
- Fix spec typo that swallowed kdump subpackage.

* Thu Jul 13 2006 Dave Jones <davej@redhat.com>
- 2.6.18-rc1-git6

* Wed Jul 12 2006 Roland McGrath <roland@redhat.com>
- Build separate debuginfo subpackages instead of a single one.

* Wed Jul 12 2006 Dave Jones <davej@redhat.com>
- 2.6.18-rc1-git5
- Make serial console installs on ia64 work again.
- Shrink struct inode.

* Wed Jul 12 2006 David Woodhouse <dwmw2@redhat.com>
- Temporarily disable -headers subpackage until the problems which
  arise from brew not using older package are dealt with.

* Wed Jul 12 2006 David Woodhouse <dwmw2@redhat.com>
- No headers subpackage for noarch build
- Fix PI-futexes to be properly unlocked on unexpected exit

* Wed Jul 12 2006 Dave Jones <davej@redhat.com>
- Add sleazy fpu optimisation.   Apps that heavily
  use floating point in theory should get faster.

* Tue Jul 11 2006 Dave Jones <davej@redhat.com>
- Add utrace. (ptrace replacement).

* Tue Jul 11 2006 David Woodhouse <dwmw2@redhat.com>
- Build iSeries again
- Minor GFS2 update
- Enable kernel-headers subpackage

* Tue Jul 11 2006 Dave Jones <davej@redhat.com>
- 2.6.18-rc1-git4

* Mon Jul 10 2006 Dave Jones <davej@redhat.com>
- 2.6.18-rc1-git3
- Big bunch o' lockdep patches from Arjan.

* Sun Jul  9 2006 Dave Jones <davej@redhat.com>
- 2.6.18-rc1-git2

* Fri Jul  7 2006 Don Zickus <dzickus@redhat.com>
- Unified rhel and fedora srpm

* Fri Jul  7 2006 Dave Jones <davej@redhat.com>
- Add lockdep annotate for bdev warning.
- Enable autofs4 to return fail for revalidate during lookup

* Thu Jul  6 2006 Dave Jones <davej@redhat.com>
- 2.6.18-rc1
- Disable RT_MUTEX_TESTER

* Wed Jul  5 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git25

* Wed Jul  5 2006 Dave Jones <davej@redhat.com>
- Try out sparsemem experiment on x86-64.

* Wed Jul  5 2006 David Woodhouse <dwmw2@redhat.com>
- Fix asm-powerpc/cputime.h for new cputime64_t stuff
- Update GFS2

* Wed Jul  5 2006 Dave Jones <davej@redhat.com>
- Further lockdep improvements.

* Wed Jul  5 2006 David Woodhouse <dwmw2@redhat.com>
- 2.6.17-git24 (yay, headers_install)

* Tue Jul  4 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git21, git22 & git23

* Sun Jul  2 2006 David Woodhouse <dwmw2@redhat.com>
- Add ppoll() and pselect() on x86_64 again

* Sat Jul  1 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git19

* Fri Jun 30 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git16 & git17

* Fri Jun 30 2006 Jeremy Katz <katzj@redhat.com>
- really fix up squashfs

* Thu Jun 29 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git13, git14 & git15
- Hopefully fix up squashfs & gfs2

* Tue Jun 27 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git12
- Disable the signed module patches for now, they need love.

* Mon Jun 26 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git10 & git11
- Enable fake PCI hotplug driver. (#190437)
- Remove lots of 'modprobe loop's from specfile.

* Sun Jun 25 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git8 & git9

* Sat Jun 24 2006 Dave Jones <davej@redhat.com>
- Enable profiling for 586 kernels.
- 2.6.17-git6 & git7
  This required lots of rediffing. SATA suspend, Promise PATA-on-SATA,
  Xen, exec-shield, and more.  Tread carefully, harmful if swallowed etc.

* Fri Jun 23 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git5

* Fri Jun 23 2006 Jeremy Katz <katzj@redhat.com>
- update to squashfs 3.0

* Thu Jun 22 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git4
- Update sysconfig/kernel on x86 %%post - Robert Scheck (#196307)

* Thu Jun 22 2006 David Woodhouse <dwmw2@redhat.com>
- MTD update

* Thu Jun 22 2006 David Woodhouse <dwmw2@redhat.com>
- Update GFS2 patch
- Apply 'make headers_install' unconditionally now Linus has the cleanups

* Wed Jun 21 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git3

* Tue Jun 20 2006 David Woodhouse <dwmw2@redhat.com>
- Update MTD tree, Update and re-enable Geode tree
- Remove AC97 patch obsoleted by Geode tree

* Tue Jun 20 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git1

* Sun Jun 18 2006 Dave Jones <davej@redhat.com>
- 2.6.17

* Sat Jun 17 2006 David Woodhouse <dwmw2@redhat.com>
- Add Geode and MTD git trees (for OLPC)

* Thu Jun 15 2006 Don Zickus <dzickus@redhat.com>
- rhelbuild clean ups
- add back in support for iSeries and s390 (needed internally only)

* Thu Jun 15 2006 Jeremy Katz <katzj@redhat.com>
- fix installation of -xen kernel on baremetal to be dom0 grub config

* Wed Jun 14 2006 Dave Jones <davej@redhat.com>
- 2.6.17-rc6-git7
- Console fixes for suspend/resume
- Drop support for PPC iseries & 31bit s390.

* Wed Jun 14 2006 Juan Quintela <quintela@redhat.com>
- remove xen0/xenU/xen0-PAE/xenU-PAE packages
- disable xen PAE kernel for i386 for now
- create xen-PAE kernel
- remove %%requires xen from xen kernels

* Wed Jun 14 2006 Juan Quintela <quintela@redhat.com>
- rename xen0 & xenU to single xen kernels.

* Tue Jun 13 2006 Dave Jones <davej@redhat.com>
- 2.6.17-rc6-git5
- serial/tty resume fixing.

* Mon Jun 12 2006 Dave Jones <davej@redhat.com>
- 2.6.17-rc6-git3
- autofs4 - need to invalidate children on tree mount expire

* Sun Jun 11 2006 Dave Jones <davej@redhat.com>
- 2.6.17-rc6-git2
- Add MyMusix PD-205 to the unusual USB quirk list.
- Silence noisy unimplemented 32bit syscalls on x86-64.

* Sat Jun 10 2006 Juan Quintela <quintela@redhat.com>
- rebase xen to linux-2.6 cset 27412
- rebase xen to linux-2.6-xen cset 22608
- rebase HV cset 10314

* Fri Jun  9 2006 David Woodhouse <dwmw2@redhat.com>
- Update GFS2 patch, export GFS2 and DLM headers

* Fri Jun  9 2006 Dave Jones <davej@redhat.com>
- Disable KGDB again, it broke serial console :(
- 2.6.17-rc6-git1

* Wed Jun  7 2006 Dave Jones <davej@redhat.com>
- Experiment: Add KGDB.
- AC97 fix for OLPC.

* Tue Jun  6 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc6. Special 6/6/6 edition, what could go wrong?
- Add a kdump kernel for PPC64 (Don Zickus)
- Enable SCHED_STATS
