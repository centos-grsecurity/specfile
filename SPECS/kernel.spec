%global __spec_install_pre %{___build_pre}

Summary: The Linux kernel

# For a stable, released kernel, released_kernel should be 1. For rawhide
# and/or a kernel built from an rc or git snapshot, released_kernel should
# be 0.
%define released_kernel 1
%define dist .el6

# Versions of various parts

# Polite request for people who spin their own kernel rpms:
# please modify the "buildid" define in a way that identifies
# that the kernel isn't the stock distribution kernel, for example,
# by setting the define to ".local" or ".bz123456"
#
# % define buildid .local

%define rhel 1
%if %{rhel}
%define distro_build 71.29.1
%define signmodules 1
%else
# fedora_build defines which build revision of this kernel version we're
# building. Rather than incrementing forever, as with the prior versioning
# setup, we set fedora_cvs_origin to the current cvs revision s/1.// of the
# kernel spec when the kernel is rebased, so fedora_build automatically
# works out to the offset from the rebase, so it doesn't get too ginormous.
#
# If you're building on a branch, the RCS revision will be something like
# 1.1205.1.1.  In this case we drop the initial 1, subtract fedora_cvs_origin
# from the second number, and then append the rest of the RCS string as is.
# Don't stare at the awk too long, you'll go blind.
%define fedora_cvs_origin   1462
%define fedora_cvs_revision() %2
%global distro_build %(echo %{fedora_cvs_origin}.%{fedora_cvs_revision $Revision: 1.18.2.30 $} | awk -F . '{ OFS = "."; ORS = ""; print $3 - $1 ; i = 4 ; OFS = ""; while (i <= NF) { print ".", $i ; i++} }')
%define distro_build %{fedora_build}
%define signmodules 0
%endif

# if patch fuzzy patch applying will be forbidden
%define with_fuzzy_patches 0

# base_sublevel is the kernel version we're starting with and patching
# on top of -- for example, 2.6.22-rc7-git1 starts with a 2.6.21 base,
# which yields a base_sublevel of 21.
%define base_sublevel 32

## If this is a released kernel ##
%if 0%{?released_kernel}

# Do we have a -stable update to apply?
%define stable_update 0
# Is it a -stable RC?
%define stable_rc 0
# Set rpm version accordingly
%if 0%{?stable_update}
%define stablerev .%{stable_update}
%define stable_base %{stable_update}
%if 0%{?stable_rc}
# stable RCs are incremental patches, so we need the previous stable patch
%define stable_base %(echo $((%{stable_update} - 1)))
%endif
%endif
%define rpmversion 2.6.%{base_sublevel}%{?stablerev}

## The not-released-kernel case ##
%else
# The next upstream release sublevel (base_sublevel+1)
%define upstream_sublevel %(echo $((%{base_sublevel} + 1)))
# The rc snapshot level
%define rcrev 0
# The git snapshot level
%define gitrev 0
# Set rpm version accordingly
%define rpmversion 2.6.%{upstream_sublevel}
%endif
# Nb: The above rcrev and gitrev values automagically define Patch00 and Patch01 below.

# What parts do we want to build?  We must build at least one kernel.
# These are the kernels that are built IF the architecture allows it.
# All should default to 1 (enabled) and be flipped to 0 (disabled)
# by later arch-specific checks.

# The following build options are enabled by default.
# Use either --without <opt> in your rpmbuild command or force values
# to 0 in here to disable them.
#
# standard kernel
%define with_up        %{?_without_up:        0} %{?!_without_up:        1}
# kernel-smp (only valid for ppc 32-bit)
%define with_smp       %{?_without_smp:       0} %{?!_without_smp:       1}
# kernel-kdump
%define with_kdump     %{?_without_kdump:     0} %{?!_without_kdump:     1}
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     1}
# kernel-doc
%define with_doc       %{?_without_doc:       0} %{?!_without_doc:       1}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
# kernel-firmware
%define with_firmware  %{?_with_firmware:     1} %{?!_with_firmware:     0}
# tools/perf
%define with_perftool  %{?_without_perftool:  0} %{?!_without_perftool:  1}
# perf noarch subpkg
%define with_perf      %{?_without_perf:      0} %{?!_without_perf:      1}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}
# kernel-bootwrapper (for creating zImages from kernel + initrd)
%define with_bootwrapper %{?_without_bootwrapper: 0} %{?!_without_bootwrapper: 1}
# Want to build a the vsdo directories installed
%define with_vdso_install %{?_without_vdso_install: 0} %{?!_without_vdso_install: 1}
# Use dracut instead of mkinitrd for initrd image generation
%define with_dracut       %{?_without_dracut:       0} %{?!_without_dracut:       1}

# Build the kernel-doc package, but don't fail the build if it botches.
# Here "true" means "continue" and "false" means "fail the build".
%if 0%{?released_kernel}
%define doc_build_fail false
%else
%define doc_build_fail true
%endif

# Control whether we perform a compat. check against published ABI.
%define with_kabichk   %{?_without_kabichk:   0} %{?!_without_kabichk: 1}
# Control whether we perform a compat. check against published ABI.
%define with_fips      %{?_without_fips:      0} %{?!_without_fips:      1}

# Additional options for user-friendly one-off kernel building:
#
# Only build the base kernel (--with baseonly):
%define with_baseonly  %{?_with_baseonly:     1} %{?!_with_baseonly:     0}
# Only build the smp kernel (--with smponly):
%define with_smponly   %{?_with_smponly:      1} %{?!_with_smponly:      0}
# Only build the debug kernel (--with dbgonly):
%define with_dbgonly   %{?_with_dbgonly:      1} %{?!_with_dbgonly:      0}

# should we do C=1 builds with sparse
%define with_sparse	%{?_with_sparse:      1} %{?!_with_sparse:      0}

# Set debugbuildsenabled to 1 for production (build separate debug kernels)
#  and 0 for rawhide (all kernels are debug kernels).
# See also 'make debug' and 'make release'.
%define debugbuildsenabled 1

# pkg_release is what we'll fill in for the rpm Release: field
%if 0%{?released_kernel}

%if 0%{?stable_rc}
%define stable_rctag .rc%{stable_rc}
%endif
%define pkg_release %{distro_build}%{?stable_rctag}%{?dist}%{?buildid}

%else

# non-released_kernel
%if 0%{?rcrev}
%define rctag .rc%rcrev
%else
%define rctag .rc0
%endif
%if 0%{?gitrev}
%define gittag .git%gitrev
%else
%define gittag .git0
%endif
%define pkg_release 0.%{distro_build}%{?rctag}%{?gittag}%{?dist}%{?buildid}

%endif

# The kernel tarball/base version
%define kversion 2.6.32-71.29.1.el6

%define make_target bzImage

%define hdrarch %_target_cpu
%define asmarch %_target_cpu

%if 0%{!?nopatches:1}
%define nopatches 0
%endif

%if %{nopatches}
%define with_bootwrapper 0
%define variant -vanilla
%else
%define variant_fedora -fedora
%endif

%define using_upstream_branch 0
%if 0%{?upstream_branch:1}
%define stable_update 0
%define using_upstream_branch 1
%define variant -%{upstream_branch}%{?variant_fedora}
%define pkg_release 0.%{distro_build}%{upstream_branch_tag}%{?dist}%{?buildid}
%endif

%if %{rhel}
%define pkg_release %{distro_build}%{?dist}%{?buildid}
%endif
%define KVERREL %{rpmversion}-%{pkg_release}.%{_target_cpu}

%if !%{debugbuildsenabled}
%define with_debug 0
%endif

%if !%{with_debuginfo}
%define _enable_debug_packages 0
%endif
%define debuginfodir /usr/lib/debug

%define with_pae 0

# if requested, only build base kernel
%if %{with_baseonly}
%define with_smp 0
%define with_kdump 0
%define with_debug 0
%endif

# if requested, only build smp kernel
%if %{with_smponly}
%define with_up 0
%define with_kdump 0
%define with_debug 0
%endif

# if requested, only build debug kernel
%if %{with_dbgonly}
%if %{debugbuildsenabled}
%define with_up 0
%endif
%define with_smp 0
%define with_pae 0
%define with_xen 0
%define with_kdump 0
%define with_perftool 0
%endif

%define all_x86 i386 i686

%if %{with_vdso_install}
# These arches install vdso/ directories.
%define vdso_arches %{all_x86} x86_64 ppc ppc64 s390 s390x
%endif

# Overrides for generic default options

# only ppc and alphav56 need separate smp kernels
%ifnarch ppc alphaev56
%define with_smp 0
%endif

%ifarch s390x
%define with_kdump 1
%else
%define with_kdump 0
%endif

# don't do debug builds on anything but i686 and x86_64
%ifnarch i686 x86_64 s390x ppc64
%define with_debug 0
%endif

# only package docs noarch
%ifnarch noarch
%define with_doc 0
%define with_perf 0
%endif

# don't build noarch kernels or headers (duh)
%ifarch noarch
%define with_up 0
%define with_headers 0
%define all_arch_configs kernel-%{version}-*.config
%define with_firmware  %{?_without_firmware:  0} %{?!_without_firmware:  1}
%endif

# bootwrapper is only on ppc
%ifnarch ppc ppc64
%define with_bootwrapper 0
%endif

# sparse blows up on ppc64 alpha and sparc64
%ifarch ppc64 ppc alpha sparc64
%define with_sparse 0
%endif

# Per-arch tweaks

%ifarch %{all_x86}
%define asmarch x86
%define hdrarch i386
%define all_arch_configs kernel-%{version}-i?86*.config
%define image_install_path boot
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch x86_64
%define asmarch x86
%define all_arch_configs kernel-%{version}-x86_64*.config
%define image_install_path boot
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch ppc64
%define asmarch powerpc
%define hdrarch powerpc
%define all_arch_configs kernel-%{version}-ppc64*.config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%endif

%ifarch s390
%define all_arch_configs kernel-%{kversion}-s390*.config
%define image_install_path boot
%define make_target image
%define kernel_image arch/s390/boot/image
%endif

%ifarch s390x
%define asmarch s390
%define hdrarch s390
%define all_arch_configs kernel-%{version}-s390x*.config
%define image_install_path boot
%define make_target image
%define kernel_image arch/s390/boot/image
%endif

%ifarch sparc
# We only build sparc headers since we dont support sparc32 hardware
%endif

%ifarch sparc64
%define asmarch sparc
%define all_arch_configs kernel-%{version}-sparc64*.config
%define make_target image
%define kernel_image arch/sparc/boot/image
%define image_install_path boot
%define with_perftool 0
%endif

%ifarch ppc
%define asmarch powerpc
%define hdrarch powerpc
%define all_arch_configs kernel-%{version}-ppc{-,.}*config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%endif

%ifarch ia64
%define all_arch_configs kernel-%{version}-ia64*.config
%define image_install_path boot/efi/EFI/redhat
%define make_target compressed
%define kernel_image vmlinux.gz
%endif

%ifarch alpha alphaev56
%define all_arch_configs kernel-%{version}-alpha*.config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%endif

%ifarch %{arm}
%define all_arch_configs kernel-%{version}-arm*.config
%define image_install_path boot
%define hdrarch arm
%define make_target vmlinux
%define kernel_image vmlinux
%endif

%if %{nopatches}
# XXX temporary until last vdso patches are upstream
%define vdso_arches ppc ppc64
%endif

%if %{nopatches}%{using_upstream_branch}
# Ignore unknown options in our config-* files.
# Some options go with patches we're not applying.
%define oldconfig_target loose_nonint_oldconfig
%else
%define oldconfig_target nonint_oldconfig
%endif

# To temporarily exclude an architecture from being built, add it to
# %nobuildarches. Do _NOT_ use the ExclusiveArch: line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
# Which is a BadThing(tm).

# We don't build a kernel on i386; we only do kernel-headers there,
# and we no longer build for 31bit S390. Same for 32bit sparc and arm.
%define nobuildarches i386 i586 s390 sparc sparc64 ppc ia64 %{arm}

%ifarch %nobuildarches
%define with_up 0
%define with_smp 0
%define with_pae 0
%define with_kdump 0
%define with_debuginfo 0
%define with_perftool 0
%define _enable_debug_packages 0
%endif

%define with_pae_debug 0
%if %{with_pae}
%define with_pae_debug %{with_debug}
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
%define package_conflicts initscripts < 7.23, udev < 145-11, iptables < 1.3.2-1, ipw2200-firmware < 2.4, iwl4965-firmware < 228.57.2, selinux-policy-targeted < 1.25.3-14, squashfs-tools < 4.0, wireless-tools < 29-3

#
# The ld.so.conf.d file we install uses syntax older ldconfig's don't grok.
#
%define kernel_xen_conflicts glibc < 2.3.5-1, xen < 3.0.1

%define kernel_PAE_obsoletes kernel-smp < 2.6.17, kernel-xen <= 2.6.27-0.2.rc0.git6.fc10
%define kernel_PAE_provides kernel-xen = %{rpmversion}-%{pkg_release}

%ifarch x86_64
%define kernel_obsoletes kernel-xen <= 2.6.27-0.2.rc0.git6.fc10
%define kernel_provides kernel-xen = %{rpmversion}-%{pkg_release}
%endif

# We moved the drm include files into kernel-headers, make sure there's
# a recent enough libdrm-devel on the system that doesn't have those.
%define kernel_headers_conflicts libdrm-devel < 2.4.0-0.15

#
# Packages that need to be installed before the kernel is, because the %post
# scripts use them.
#
%define kernel_prereq  fileutils, module-init-tools, initscripts >= 8.11.1-1, kernel-firmware >= %{rpmversion}-%{pkg_release}, grubby >= 7.0.4-1
%if %{with_dracut}
%define initrd_prereq  dracut-kernel >= 002-18.git413bcf78
%else
%define initrd_prereq  mkinitrd >= 6.0.61-1
%endif

#
# This macro does requires, provides, conflicts, obsoletes for a kernel package.
#	%%kernel_reqprovconf <subpackage>
# It uses any kernel_<subpackage>_conflicts and kernel_<subpackage>_obsoletes
# macros defined above.
#
%define kernel_reqprovconf \
Provides: kernel = %{rpmversion}-%{pkg_release}\
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{pkg_release}%{?1:.%{1}}\
Provides: kernel-drm = 4.3.0\
Provides: kernel-drm-nouveau = 16\
Provides: kernel-modeset = 1\
Provides: kernel-uname-r = %{KVERREL}%{?1:.%{1}}\
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
Requires(post): /sbin/new-kernel-pkg\
Requires(preun): /sbin/new-kernel-pkg\
Conflicts: %{kernel_dot_org_conflicts}\
Conflicts: %{package_conflicts}\
%{expand:%%{?kernel%{?1:_%{1}}_conflicts:Conflicts: %%{kernel%{?1:_%{1}}_conflicts}}}\
%{expand:%%{?kernel%{?1:_%{1}}_obsoletes:Obsoletes: %%{kernel%{?1:_%{1}}_obsoletes}}}\
%{expand:%%{?kernel%{?1:_%{1}}_provides:Provides: %%{kernel%{?1:_%{1}}_provides}}}\
# We can't let RPM do the dependencies automatic because it'll then pick up\
# a correct but undesirable perl dependency from the module headers which\
# isn't required for the kernel proper to function\
AutoReq: no\
AutoProv: yes\
%{nil}

Name: kernel%{?variant}
Group: System Environment/Kernel
License: GPLv2
URL: http://www.kernel.org/
Version: %{rpmversion}
Release: %{pkg_release}
# DO NOT CHANGE THE 'ExclusiveArch' LINE TO TEMPORARILY EXCLUDE AN ARCHITECTURE BUILD.
# SET %%nobuildarches (ABOVE) INSTEAD
ExclusiveArch: noarch %{all_x86} x86_64 ppc ppc64 ia64 sparc sparc64 s390 s390x alpha alphaev56 %{arm}
ExclusiveOS: Linux

%kernel_reqprovconf
%ifarch x86_64 sparc64
Obsoletes: kernel-smp
%endif


#
# List the packages used during the kernel build
#
BuildRequires: module-init-tools, patch >= 2.5.4, bash >= 2.03, sh-utils, tar
BuildRequires: bzip2, findutils, gzip, m4, perl, make >= 3.78, diffutils, gawk
BuildRequires: gcc >= 3.4.2, binutils >= 2.12, redhat-rpm-config
BuildRequires: net-tools, patchutils, rpm-build >= 4.8.0-7
%if %{with_doc}
BuildRequires: xmlto
BuildRequires: asciidoc
%endif
%if %{with_sparse}
BuildRequires: sparse >= 0.4.1
%endif
%if %{with_perftool}
BuildRequires: elfutils-libelf-devel zlib-devel binutils-devel
%endif
%if %{signmodules}
BuildRequires: gnupg
%endif
BuildRequires: python
%if %{with_fips}
BuildRequires: hmaccalc
%endif
%ifarch s390x
# Ensure glibc{,-devel} is installed so zfcpdump can be built
BuildRequires: glibc-static
%endif

BuildConflicts: rhbuildsys(DiskFree) < 7Gb

%define fancy_debuginfo 1

%if %{fancy_debuginfo}
# Fancy new debuginfo generation introduced in Fedora 8.
%define debuginfo_args --strict-build-id
%endif

Source0: linux-2.6.32.27.tar.bz2

Source1: Makefile.common

%if 0%{?rcrev}
Source2: ftp://ftp.kernel.org/pub/linux/kernel/v2.6/testing/incr/patch-2.6.%{upstream_sublevel}-rc%{rcrev}.bz2
%if 0%{?gitrev}
Source3: ftp://ftp.kernel.org/pub/linux/kernel/v2.6/testing/incr/patch-2.6.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}.bz2
%endif
%endif

Source11: genkey
Source13: perf-archive
Source14: find-provides
Source15: merge.pl
Source16: perf
Source17: kabitool
Source18: check-kabi
Source19: extrakeys.pub

Source20: Makefile.config

Source30: Module.kabi_i686
Source31: Module.kabi_ppc64
Source32: Module.kabi_s390x
Source33: Module.kabi_x86_64

Source50: config-i686
Source51: config-s390x-kdump-rhel
Source52: config-generic
Source53: config-x86-generic-rhel
Source54: config-s390x-generic-rhel
Source55: config-x86-generic
Source56: config-x86_64-nodebug-rhel
Source57: config-s390x-rhel
Source58: config-powerpc64-kdump
Source59: config-i686-debug-rhel
Source60: config-nodebug
Source61: config-s390x
Source62: config-powerpc-generic-rhel
Source63: config-ia64-generic-rhel
Source64: config-s390x-kdump
Source65: config-nodebug-rhel
Source66: config-i686-nodebug
Source67: config-i686-debug
Source68: config-powerpc-generic
Source69: config-x86_64-debug
Source70: config-framepointer
Source71: config-i686-rhel
Source72: config-i686-nodebug-rhel
Source73: config-x86_64-nodebug
Source74: config-powerpc64-rhel
Source75: config-debug
Source76: config-x86_64-generic
Source77: config-x86_64-debug-rhel
Source78: config-x86_64-generic-rhel
Source79: config-debug-rhel
Source80: config-generic-rhel
Source81: config-powerpc64
Source82: config-s390x-debug
Source83: config-s390x-debug-rhel

# empty final patch file to facilitate testing of kernel patches
Patch999999: linux-kernel-test.patch

BuildRoot: %{_tmppath}/kernel-%{KVERREL}-root

# Override find_provides to use a script that provides "kernel(symbol) = hash".
# Pass path of the RPM temp dir containing kabideps to find-provides script.
%global _use_internal_dependency_generator 0
%define __find_provides %_sourcedir/find-provides %{_tmppath}
%define __find_requires /usr/lib/rpm/redhat/find-requires kernel

%description
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system: memory allocation, process allocation, device
input and output, etc.


%package doc
Summary: Various documentation bits found in the kernel source
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

%package firmware
Summary: Firmware files used by the Linux kernel
Group: Development/System
# This is... complicated.
# Look at the WHENCE file.
License: GPL+ and GPLv2+ and MIT and Redistributable, no modification permitted
%if "x%{?variant}" != "x"
Provides: kernel-firmware = %{rpmversion}-%{pkg_release}
%endif
%description firmware
Kernel-firmware includes firmware files required for some devices to
operate.

%package bootwrapper
Summary: Boot wrapper files for generating combined kernel + initrd images
Group: Development/System
Requires: gzip
%description bootwrapper
Kernel-bootwrapper contains the wrapper code which makes bootable "zImage"
files combining both kernel and initial ramdisk.

%package debuginfo-common-%{_target_cpu}
Summary: Kernel source files used by %{name}-debuginfo packages
Group: Development/Debug
%description debuginfo-common-%{_target_cpu}
This package is required by %{name}-debuginfo subpackages.
It provides the kernel source files common to all builds.

%package -n perf
Summary: Performance monitoring for the Linux kernel
Group: Development/System
License: GPLv2
%description -n perf
This package provides the supporting documentation for the perf tool
shipped in each kernel image subpackage.

#
# This macro creates a kernel-<subpackage>-debuginfo package.
#	%%kernel_debuginfo_package <subpackage>
#
%define kernel_debuginfo_package() \
%package %{?1:%{1}-}debuginfo\
Summary: Debug information for package %{name}%{?1:-%{1}}\
Group: Development/Debug\
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}\
Provides: %{name}%{?1:-%{1}}-debuginfo-%{_target_cpu} = %{version}-%{release}\
AutoReqProv: no\
%description -n %{name}%{?1:-%{1}}-debuginfo\
This package provides debug information for package %{name}%{?1:-%{1}}.\
This is required to use SystemTap with %{name}%{?1:-%{1}}-%{KVERREL}.\
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '/.*/%%{KVERREL}%{?1:\.%{1}}/.*|/.*%%{KVERREL}%{?1:\.%{1}}(\.debug)?' -o debuginfo%{?1}.list}\
%{nil}

#
# This macro creates a kernel-<subpackage>-devel package.
#	%%kernel_devel_package <subpackage> <pretty-name>
#
%define kernel_devel_package() \
%package %{?1:%{1}-}devel\
Summary: Development package for building kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: kernel%{?1:-%{1}}-devel-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}%{?1:.%{1}}\
Provides: kernel-devel = %{version}-%{release}%{?1:.%{1}}\
Provides: kernel-devel-uname-r = %{KVERREL}%{?1:.%{1}}\
AutoReqProv: no\
Requires(pre): /usr/bin/find\
%description -n kernel%{?variant}%{?1:-%{1}}-devel\
This package provides kernel headers and makefiles sufficient to build modules\
against the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-<subpackage> and its -devel and -debuginfo too.
#	%%define variant_summary The Linux kernel compiled for <configuration>
#	%%kernel_variant_package [-n <pretty-name>] <subpackage>
#
%define kernel_variant_package(n:) \
%package %1\
Summary: %{variant_summary}\
Group: System Environment/Kernel\
%kernel_reqprovconf\
%{expand:%%kernel_devel_package %1 %{!?-n:%1}%{?-n:%{-n*}}}\
%{expand:%%kernel_debuginfo_package %1}\
%{nil}


# First the auxiliary packages of the main kernel package.
%kernel_devel_package
%kernel_debuginfo_package


# Now, each variant package.

%define variant_summary The Linux kernel compiled for SMP machines
%kernel_variant_package -n SMP smp
%description smp
This package includes a SMP version of the Linux kernel. It is
required only on machines with two or more CPUs as well as machines with
hyperthreading technology.

Install the kernel-smp package if your machine uses two or more CPUs.


%define variant_summary The Linux kernel compiled for PAE capable machines
%kernel_variant_package PAE
%description PAE
This package includes a version of the Linux kernel with support for up to
64GB of high memory. It requires a CPU with Physical Address Extensions (PAE).
The non-PAE kernel can only address up to 4GB of memory.
Install the kernel-PAE package if your machine has more than 4GB of memory.


%define variant_summary The Linux kernel compiled with extra debugging enabled for PAE capable machines
%kernel_variant_package PAEdebug
Obsoletes: kernel-PAE-debug
%description PAEdebug
This package includes a version of the Linux kernel with support for up to
64GB of high memory. It requires a CPU with Physical Address Extensions (PAE).
The non-PAE kernel can only address up to 4GB of memory.
Install the kernel-PAE package if your machine has more than 4GB of memory.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.


%define variant_summary The Linux kernel compiled with extra debugging enabled
%kernel_variant_package debug
%description debug
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.


%define variant_summary A minimal Linux kernel compiled for crash dumps
%kernel_variant_package kdump
%description kdump
This package includes a kdump version of the Linux kernel. It is
required only on machines which will use the kexec-based kernel crash dump
mechanism.


%prep
# do a few sanity-checks for --with *only builds
%if %{with_baseonly}
%if !%{with_up}%{with_pae}
echo "Cannot build --with baseonly, up build is disabled"
exit 1
%endif
%endif

%if %{with_smponly}
%if !%{with_smp}
echo "Cannot build --with smponly, smp build is disabled"
exit 1
%endif
%endif

%if %{with_fuzzy_patches}
  patch_command='patch -p1 -s'
%else
  patch_command='patch -p1 -F1 -s'
%endif

ApplyPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  case "$patch" in
  *.bz2) bunzip2 < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.gz) gunzip < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *) $patch_command ${1+"$@"} < "$RPM_SOURCE_DIR/$patch" ;;
  esac
}

# don't apply patch if it's empty
ApplyOptionalPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  local C=$(wc -l $RPM_SOURCE_DIR/$patch | awk '{print $1}')
  if [ "$C" -gt 9 ]; then
    ApplyPatch $patch ${1+"$@"}
  fi
}

# we don't want a .config file when building firmware: it just confuses the build system
%define build_firmware \
   mv .config .config.firmware_save \
   make INSTALL_FW_PATH=$RPM_BUILD_ROOT/lib/firmware firmware_install \
   mv .config.firmware_save .config

if [ ! -d kernel-%{kversion}/vanilla-%{kversion}/ ]; then
	rm -f pax_global_header;
%setup -q -n kernel-%{kversion} -c
	mv linux-%{kversion} vanilla-%{kversion};
else
	cd kernel-%{kversion}/;
fi

if [ -d linux-%{kversion}.%{_target_cpu} ]; then
  # Just in case we ctrl-c'd a prep already
  rm -rf deleteme.%{_target_cpu}
  # Move away the stale away, and delete in background.
  mv linux-%{kversion}.%{_target_cpu} deleteme.%{_target_cpu}
  rm -rf deleteme.%{_target_cpu} &
fi

cp -rl vanilla-%{kversion} linux-%{kversion}.%{_target_cpu}

cd linux-%{kversion}.%{_target_cpu}

# Drop some necessary files from the source dir into the buildroot
cp $RPM_SOURCE_DIR/config-* .
cp %{SOURCE15} %{SOURCE1} %{SOURCE16} %{SOURCE17} %{SOURCE18} .

# Dynamically generate kernel .config files from config-* files
make -f %{SOURCE20} VERSION=%{version} configs

ApplyOptionalPatch linux-kernel-test.patch

# Any further pre-build tree manipulations happen here.

chmod +x scripts/checkpatch.pl

# only deal with configs if we are going to build for the arch
%ifnarch %nobuildarches

mkdir configs

# Remove configs not for the buildarch
for cfg in kernel-%{version}-*.config; do
  if [ `echo %{all_arch_configs} | grep -c $cfg` -eq 0 ]; then
    rm -f $cfg
  fi
done

%if !%{debugbuildsenabled}
rm -f kernel-%{version}-*debug.config
%endif

# now run oldconfig over all the config files
for i in *.config
do
  mv $i .config
  Arch=`head -1 .config | cut -b 3-`
  make ARCH=$Arch %{oldconfig_target} > /dev/null
  echo "# $Arch" > configs/$i
  cat .config >> configs/$i
  rm -f include/generated/kernel.arch
  rm -f include/generated/kernel.cross
done
# end of kernel config
%endif

# get rid of unwanted files resulting from patch fuzz
find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null

%if %{signmodules}
cp %{SOURCE19} .
cat <<EOF
###
### Now generating a PGP key pair to be used for signing modules.
###
### If this takes a long time, you might wish to run rngd in the background to
### keep the supply of entropy topped up.  It needs to be run as root, and
### should use a hardware random number generator if one is available, eg:
###
###     rngd -r /dev/hwrandom
###
### If one isn't available, the pseudo-random number generator can be used:
###
###     rngd -r /dev/urandom
###
EOF
gpg --homedir . --batch --gen-key %{SOURCE11}
cat <<EOF
###
### Key pair generated.
###
EOF
# if there're external keys to be included
if [ -s %{SOURCE19} ]; then
	gpg --homedir . --no-default-keyring --keyring kernel.pub --import %{SOURCE19}
fi
gpg --homedir . --export --keyring ./kernel.pub CentOS > extract.pub
gcc -o scripts/bin2c scripts/bin2c.c
scripts/bin2c ksign_def_public_key __initdata <extract.pub >crypto/signature/key.h
%endif

cd ..

###
### build
###
%build

%if %{with_sparse}
%define sparse_mflags	C=1
%endif

%if %{fancy_debuginfo}
# This override tweaks the kernel makefiles so that we run debugedit on an
# object before embedding it.  When we later run find-debuginfo.sh, it will
# run debugedit again.  The edits it does change the build ID bits embedded
# in the stripped object, but repeating debugedit is a no-op.  We do it
# beforehand to get the proper final build ID bits into the embedded image.
# This affects the vDSO images in vmlinux, and the vmlinux image in bzImage.
export AFTER_LINK=\
'sh -xc "/usr/lib/rpm/debugedit -b $$RPM_BUILD_DIR -d /usr/src/debug -i $@"'
%endif

cp_vmlinux()
{
  eu-strip --remove-comment -o "$2" "$1"
}

BuildKernel() {
    MakeTarget=$1
    KernelImage=$2
    Flavour=$3
    InstallName=${4:-vmlinuz}

    # Pick the right config file for the kernel we're building
    Config=kernel-%{version}-%{_target_cpu}${Flavour:+-${Flavour}}.config
    DevelDir=/usr/src/kernels/%{KVERREL}${Flavour:+.${Flavour}}

    # When the bootable image is just the ELF kernel, strip it.
    # We already copy the unstripped file into the debuginfo package.
    if [ "$KernelImage" = vmlinux ]; then
      CopyKernel=cp_vmlinux
    else
      CopyKernel=cp
    fi

    KernelVer=%{version}-%{release}.%{_target_cpu}${Flavour:+.${Flavour}}
    echo BUILDING A KERNEL FOR ${Flavour} %{_target_cpu}...

    # make sure EXTRAVERSION says what we want it to say
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = %{?stablerev}-%{release}.%{_target_cpu}${Flavour:+.${Flavour}}/" Makefile

    # if pre-rc1 devel kernel, must fix up SUBLEVEL for our versioning scheme
    %if !0%{?rcrev}
    %if 0%{?gitrev}
    perl -p -i -e 's/^SUBLEVEL.*/SUBLEVEL = %{upstream_sublevel}/' Makefile
    %endif
    %endif

    # and now to start the build process

    make -s mrproper
    cp configs/$Config .config

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

    if [ "$Arch" == "s390" -a "$Flavour" == "kdump" ]; then
        pushd arch/s390/boot
        gcc -static -o zfcpdump zfcpdump.c
        popd
    fi
    make -s ARCH=$Arch %{oldconfig_target} > /dev/null
    make -s ARCH=$Arch V=1 %{?_smp_mflags} $MakeTarget %{?sparse_mflags}
    if [ "$Arch" != "s390" -o "$Flavour" != "kdump" ]; then
        make -s ARCH=$Arch V=1 %{?_smp_mflags} modules %{?sparse_mflags} || exit 1
    fi

%if %{with_perftool}
    pushd tools/perf
# make sure the scripts are executable... won't be in tarball until 2.6.31 :/
    chmod +x util/generate-cmdlist.sh util/PERF-VERSION-GEN
    make -s V=1 %{?_smp_mflags} NO_DEMANGLE=1 perf
    mkdir -p $RPM_BUILD_ROOT/usr/libexec/
    install -m 755 perf $RPM_BUILD_ROOT/usr/libexec/perf.$KernelVer
    popd
%endif

    # Start installing the results
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/boot
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/%{image_install_path}
    install -m 644 System.map $RPM_BUILD_ROOT/%{debuginfodir}/boot/System.map-$KernelVer
%endif
    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}
    install -m 644 .config $RPM_BUILD_ROOT/boot/config-$KernelVer
    install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$KernelVer
%if %{with_dracut}
    # We estimate the size of the initramfs because rpm needs to take this size
    # into consideration when performing disk space calculations. (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-$KernelVer.img bs=1M count=20
%else
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initrd-$KernelVer.img bs=1M count=5
%endif
    if [ -f arch/$Arch/boot/zImage.stub ]; then
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/%{image_install_path}/zImage.stub-$KernelVer || :
    fi
    $CopyKernel $KernelImage \
    		$RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    chmod 755 $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer

%if %{with_fips}
    # hmac sign the kernel for FIPS
    echo "Creating hmac file: $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac"
    ls -l $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    sha512hmac $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer | sed -e "s,$RPM_BUILD_ROOT,," > $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac;
%endif

    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
    # Override $(mod-fw) because we don't want it to install any firmware
    # We'll do that ourselves with 'make firmware_install'
    if [ "$Arch" != "s390" -o "$Flavour" != "kdump" ]; then
      make -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=$KernelVer mod-fw=

      # check if the modules are being signed
%if %{signmodules}
      if [ -z "$(readelf -n $(find fs/ -name \*.ko | head -n 1) | grep module.sig)" ]; then
          echo "ERROR: modules are NOT signed" >&2;
          exit 1;
      fi
%endif
    else
      mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/{kernel,extra}
    fi

%ifarch %{vdso_arches}
    make -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=$KernelVer
    if grep '^CONFIG_XEN=y$' .config >/dev/null; then
      echo > ldconfig-kernel.conf "\
# This directive teaches ldconfig to search in nosegneg subdirectories
# and cache the DSOs there with extra bit 0 set in their hwcap match
# fields.  In Xen guest kernels, the vDSO tells the dynamic linker to
# search in nosegneg subdirectories and to match this extra hwcap bit
# in the ld.so.cache file.
hwcap 0 nosegneg"
    fi
    if [ ! -s ldconfig-kernel.conf ]; then
      echo > ldconfig-kernel.conf "\
# Placeholder file, no vDSO hwcap entries used in this kernel."
    fi
    %{__install} -D -m 444 ldconfig-kernel.conf \
        $RPM_BUILD_ROOT/etc/ld.so.conf.d/kernel-$KernelVer.conf
%endif

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
    cp System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -s Module.markers ]; then
      cp Module.markers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    fi

    # create the kABI metadata for use in packaging
    echo "**** GENERATING kernel ABI metadata ****"
    gzip -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-$KernelVer.gz
    chmod 0755 %_sourcedir/kabitool
    rm -f %{_tmppath}/kernel-$KernelVer-kabideps
    %_sourcedir/kabitool -s Module.symvers -o %{_tmppath}/kernel-$KernelVer-kabideps

%if %{with_kabichk}
    echo "**** kABI checking is enabled in kernel SPEC file. ****"
    chmod 0755 $RPM_SOURCE_DIR/check-kabi
    if [ -e $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Flavour ]; then
        cp $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Flavour $RPM_BUILD_ROOT/Module.kabi
        $RPM_SOURCE_DIR/check-kabi -k $RPM_BUILD_ROOT/Module.kabi -s Module.symvers || exit 1
        rm $RPM_BUILD_ROOT/Module.kabi # for now, don't keep it around.
    else
        echo "**** NOTE: Cannot find reference Module.kabi file. ****"
    fi
%endif
    # then drop all but the needed Makefiles/Kconfig files
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Documentation
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    cp .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -d arch/$Arch/scripts ]; then
      cp -a arch/$Arch/scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch} || :
    fi
    if [ -f arch/$Arch/*lds ]; then
      cp -a arch/$Arch/*lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch}/ || :
    fi
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*.o
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*/*.o
%ifarch ppc
    cp -a --parents arch/powerpc/lib/crtsavres.[So] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    if [ -d arch/%{asmarch}/include ]; then
      cp -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    cd include
    cp -a acpi config crypto keys linux math-emu media mtd net pcmcia rdma rxrpc scsi sound trace video drm asm-generic $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    asmdir=$(readlink asm)
    cp -a $asmdir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/
    pushd $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    ln -s $asmdir asm
    popd
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

    # mark modules executable so that strip-to-file can strip them
    xargs --no-run-if-empty chmod u+x < modnames

    # Generate a list of modules for block and networking.

    fgrep /drivers/ modnames | xargs --no-run-if-empty nm -upA |
    sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

    collect_modules_list()
    {
      sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef |
      LC_ALL=C sort -u > $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
    }

    collect_modules_list networking \
    			 'register_netdev|ieee80211_register_hw|usbnet_probe'
    collect_modules_list block \
    			 'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler'
    collect_modules_list drm \
    			 'drm_open|drm_init'
    collect_modules_list modesetting \
    			 'drm_crtc_init'

    # detect missing or incorrect license tags
    rm -f modinfo
    while read i
    do
      echo -n "${i#$RPM_BUILD_ROOT/lib/modules/$KernelVer/} " >> modinfo
      /sbin/modinfo -l $i >> modinfo
    done < modnames

    egrep -v \
    	  'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' \
	  modinfo && exit 1

    rm -f modinfo modnames

    # remove files that will be auto generated by depmod at rpm -i time
    for i in alias alias.bin ccwmap dep dep.bin ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols symbols.bin usbmap
    do
      rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$i
    done

    # Move the devel headers out of the root file system
    mkdir -p $RPM_BUILD_ROOT/usr/src/kernels
    mv $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/$DevelDir
    ln -sf ../../..$DevelDir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
}

###
# DO it...
###

# prepare directories
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/boot

cd linux-%{kversion}.%{_target_cpu}

%if %{with_debug}
BuildKernel %make_target %kernel_image debug
%endif

%if %{with_pae_debug}
BuildKernel %make_target %kernel_image PAEdebug
%endif

%if %{with_pae}
BuildKernel %make_target %kernel_image PAE
%endif

%if %{with_up}
BuildKernel %make_target %kernel_image
%endif

%if %{with_smp}
BuildKernel %make_target %kernel_image smp
%endif

%if %{with_kdump}
%ifarch s390x
BuildKernel %make_target %kernel_image kdump
%else
BuildKernel vmlinux vmlinux kdump vmlinux
%endif
%endif

%if %{with_doc}
# Make the HTML and man pages.
make -j1 htmldocs mandocs || %{doc_build_fail}

# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a=rX Documentation
find Documentation -type d | xargs chmod u+w
%endif

%if %{with_perf}
pushd tools/perf
make %{?_smp_mflags} man || %{doc_build_fail}
popd
%endif

###
### Special hacks for debuginfo subpackages.
###

# This macro is used by %%install, so we must redefine it before that.
%define debug_package %{nil}

%if %{fancy_debuginfo}
%define __debug_install_post \
  /usr/lib/rpm/find-debuginfo.sh %{debuginfo_args} %{_builddir}/%{?buildsubdir}\
%{nil}
%endif

%if %{with_debuginfo}
%ifnarch noarch
%global __debug_package 1
%files -f debugfiles.list debuginfo-common-%{_target_cpu}
%defattr(-,root,root)
%endif
%endif

###
### install
###

%install
# for some reason, on RHEL-5 RPM_BUILD_ROOT doesn't get set
if [ -z "$RPM_BUILD_ROOT" ]; then
	export RPM_BUILD_ROOT="%{buildroot}";
fi

cd linux-%{kversion}.%{_target_cpu}

%if %{with_doc}
docdir=$RPM_BUILD_ROOT%{_datadir}/doc/kernel-doc-%{rpmversion}
man9dir=$RPM_BUILD_ROOT%{_datadir}/man/man9

# copy the source over
mkdir -p $docdir
tar -f - --exclude=man --exclude='.*' -c Documentation | tar xf - -C $docdir

# Install man pages for the kernel API.
mkdir -p $man9dir
find Documentation/DocBook/man -name '*.9.gz' -print0 |
xargs -0 --no-run-if-empty %{__install} -m 444 -t $man9dir $m
ls $man9dir | grep -q '' || > $man9dir/BROKEN
%endif # with_doc

# perf docs
%if %{with_perf}
mandir=$RPM_BUILD_ROOT%{_datadir}/man
man1dir=$mandir/man1
pushd tools/perf/Documentation
make install-man mandir=$mandir
popd

pushd $man1dir
for d in *.1; do
 gzip $d;
done
popd
%endif # with_perf

# perf shell wrapper
%if %{with_perf}
mkdir -p $RPM_BUILD_ROOT/usr/sbin/
cp $RPM_SOURCE_DIR/perf $RPM_BUILD_ROOT/usr/sbin/perf
chmod 0755 $RPM_BUILD_ROOT/usr/sbin/perf
cp $RPM_SOURCE_DIR/perf-archive $RPM_BUILD_ROOT/usr/sbin/perf-archive
chmod 0755 $RPM_BUILD_ROOT/usr/sbin/perf-archive
mkdir -p $RPM_BUILD_ROOT%{_datadir}/doc/perf
%endif

%if %{with_headers}
# Install kernel headers
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

# Do headers_check but don't die if it fails.
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_check \
     > hdrwarnings.txt || :
if grep -q exist hdrwarnings.txt; then
   sed s:^$RPM_BUILD_ROOT/usr/include/:: hdrwarnings.txt
   # Temporarily cause a build failure if header inconsistencies.
   # exit 1
fi

find $RPM_BUILD_ROOT/usr/include \
     \( -name .install -o -name .check -o \
     	-name ..install.cmd -o -name ..check.cmd \) | xargs rm -f

# glibc provides scsi headers for itself, for now
rm -rf $RPM_BUILD_ROOT/usr/include/scsi
rm -f $RPM_BUILD_ROOT/usr/include/asm*/atomic.h
rm -f $RPM_BUILD_ROOT/usr/include/asm*/io.h
rm -f $RPM_BUILD_ROOT/usr/include/asm*/irq.h
%endif

%if %{with_firmware}
%{build_firmware}
%endif

%if %{with_bootwrapper}
make DESTDIR=$RPM_BUILD_ROOT bootwrapper_install WRAPPER_OBJDIR=%{_libdir}/kernel-wrapper WRAPPER_DTSDIR=%{_libdir}/kernel-wrapper/dts
%endif


###
### clean
###

%clean
rm -rf $RPM_BUILD_ROOT

###
### scripts
###

#
# This macro defines a %%post script for a kernel*-devel package.
#	%%kernel_devel_post [<subpackage>]
#
%define kernel_devel_post() \
%{expand:%%post %{?1:%{1}-}devel}\
if [ -f /etc/sysconfig/kernel ]\
then\
    . /etc/sysconfig/kernel || exit $?\
fi\
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]\
then\
    (cd /usr/src/kernels/%{KVERREL}%{?1:.%{1}} &&\
     /usr/bin/find . -type f | while read f; do\
       hardlink -c /usr/src/kernels/*.fc*.*/$f $f\
     done)\
fi\
%{nil}

# This macro defines a %%posttrans script for a kernel package.
#	%%kernel_variant_posttrans [<subpackage>]
# More text can follow to go at the end of this variant's %%post.
#
# grubby might be called during installation when a boot loader configuration
# file is not present, so just drop any error messages. See BZ#610813 for
# more details.
%define kernel_variant_posttrans() \
%{expand:%%posttrans %{?1}}\
%{expand:\
NEWKERNARGS=""\
(/sbin/grubby --info=`/sbin/grubby --default-kernel`) 2>/dev/null | grep -q crashkernel\
if [ $? -ne 0 ]\
then\
	NEWKERNARGS="--kernel-args=\"crashkernel=auto\""\
fi\
%if %{with_dracut}\
/sbin/new-kernel-pkg --package kernel%{?1:-%{1}} --mkinitrd --dracut --depmod --update %{KVERREL}%{?1:.%{1}} $NEWKERNARGS || exit $?\
%else\
/sbin/new-kernel-pkg --package kernel%{?1:-%{1}} --mkinitrd --depmod --update %{KVERREL}%{?1:.%{1}} $NEWKERNARGS || exit $?\
%endif}\
/sbin/new-kernel-pkg --package kernel%{?1:-%{1}} --rpmposttrans %{KVERREL}%{?1:.%{1}} || exit $?\
if [ -x /sbin/weak-modules ]\
then\
    /sbin/weak-modules --add-kernel %{KVERREL}%{?1:.%{1}} || exit $?\
fi\
%{nil}

#
# This macro defines a %%post script for a kernel package and its devel package.
#	%%kernel_variant_post [-v <subpackage>] [-r <replace>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_post(v:r:) \
%{expand:%%kernel_devel_post %{?-v*}}\
%{expand:%%kernel_variant_posttrans %{?-v*}}\
%{expand:%%post %{?-v*}}\
%{-r:\
if [ `uname -i` == "x86_64" -o `uname -i` == "i386" ] &&\
   [ -f /etc/sysconfig/kernel ]; then\
  /bin/sed -r -i -e 's/^DEFAULTKERNEL=%{-r*}$/DEFAULTKERNEL=kernel%{?-v:-%{-v*}}/' /etc/sysconfig/kernel || exit $?\
fi}\
%{expand:\
/sbin/new-kernel-pkg --package kernel%{?-v:-%{-v*}} --install %{KVERREL}%{?-v:.%{-v*}} || exit $?\
}\
%{nil}

#
# This macro defines a %%preun script for a kernel package.
#	%%kernel_variant_preun <subpackage>
#
%define kernel_variant_preun() \
%{expand:%%preun %{?1}}\
/sbin/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVERREL}%{?1:.%{1}} || exit $?\
if [ -x /sbin/weak-modules ]\
then\
    /sbin/weak-modules --remove-kernel %{KVERREL}%{?-v:.%{-v*}} || exit $?\
fi\
%{nil}

%kernel_variant_preun
%ifarch x86_64
%kernel_variant_post -r (kernel-smp|kernel-xen)
%else
%kernel_variant_post -r kernel-smp
%endif

%kernel_variant_preun smp
%kernel_variant_post -v smp

%kernel_variant_preun PAE
%kernel_variant_post -v PAE -r (kernel|kernel-smp|kernel-xen)

%kernel_variant_preun debug
%kernel_variant_post -v debug

%kernel_variant_post -v PAEdebug -r (kernel|kernel-smp|kernel-xen)
%kernel_variant_preun PAEdebug

%ifarch s390x
%postun kdump
    # Create softlink to latest remaining kdump kernel.
    # If no more kdump kernel is available, remove softlink.
    if [ "$(readlink /boot/zfcpdump)" == "/boot/vmlinuz-%{KVERREL}.kdump" ]
    then
        vmlinuz_next=$(ls /boot/vmlinuz-*.kdump 2> /dev/null | sort | tail -n1)
        if [ $vmlinuz_next ]
        then
            ln -sf $vmlinuz_next /boot/zfcpdump
        else
            rm -f /boot/zfcpdump
        fi
    fi

%post kdump
    ln -sf /boot/vmlinuz-%{KVERREL}.kdump /boot/zfcpdump
%endif

if [ -x /sbin/ldconfig ]
then
    /sbin/ldconfig -X || exit $?
fi

###
### file lists
###

%if %{with_headers}
%files headers
%defattr(-,root,root)
/usr/include/*
%endif

%if %{with_firmware}
%files firmware
%defattr(-,root,root)
/lib/firmware/*
%doc linux-%{kversion}.%{_target_cpu}/firmware/WHENCE
%endif

%if %{with_bootwrapper}
%files bootwrapper
%defattr(-,root,root)
/usr/sbin/*
%{_libdir}/kernel-wrapper
%endif

# only some architecture builds need kernel-doc
%if %{with_doc}
%files doc
%defattr(-,root,root)
%{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation/*
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}
%{_datadir}/man/man9/*
%endif

%if %{with_perf}
%files -n perf
%defattr(-,root,root)
%{_datadir}/doc/perf
/usr/sbin/perf
/usr/sbin/perf-archive
%{_datadir}/man/man1/*
%endif

# This is %{image_install_path} on an arch where that includes ELF files,
# or empty otherwise.
%define elf_image_install_path %{?kernel_image_elf:%{image_install_path}}

#
# This macro defines the %%files sections for a kernel package
# and its devel and debuginfo packages.
#	%%kernel_variant_files [-k vmlinux] <condition> <subpackage>
#
%define kernel_variant_files(k:) \
%if %{1}\
%{expand:%%files %{?2}}\
%defattr(-,root,root)\
/%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVERREL}%{?2:.%{2}}\
%if %{with_fips} \
/%{image_install_path}/.vmlinuz-%{KVERREL}%{?2:.%{2}}.hmac \
%endif \
/boot/System.map-%{KVERREL}%{?2:.%{2}}\
/boot/symvers-%{KVERREL}%{?2:.%{2}}.gz\
%if %{with_perftool}\
/usr/libexec/perf.%{KVERREL}%{?2:.%{2}}\
%endif\
#/boot/symvers-%{KVERREL}%{?2:.%{2}}.gz\
/boot/config-%{KVERREL}%{?2:.%{2}}\
%dir /lib/modules/%{KVERREL}%{?2:.%{2}}\
/lib/modules/%{KVERREL}%{?2:.%{2}}/kernel\
/lib/modules/%{KVERREL}%{?2:.%{2}}/extra\
/lib/modules/%{KVERREL}%{?2:.%{2}}/build\
/lib/modules/%{KVERREL}%{?2:.%{2}}/source\
/lib/modules/%{KVERREL}%{?2:.%{2}}/updates\
/lib/modules/%{KVERREL}%{?2:.%{2}}/weak-updates\
%ifarch %{vdso_arches}\
/lib/modules/%{KVERREL}%{?2:.%{2}}/vdso\
/etc/ld.so.conf.d/kernel-%{KVERREL}%{?2:.%{2}}.conf\
%endif\
/lib/modules/%{KVERREL}%{?2:.%{2}}/modules.*\
%if %{with_dracut}\
%ghost /boot/initramfs-%{KVERREL}%{?2:.%{2}}.img\
%else\
%ghost /boot/initrd-%{KVERREL}%{?2:.%{2}}.img\
%endif\
%{expand:%%files %{?2:%{2}-}devel}\
%defattr(-,root,root)\
%dir /usr/src/kernels\
/usr/src/kernels/%{KVERREL}%{?2:.%{2}}\
%if %{with_debuginfo}\
%ifnarch noarch\
%if %{fancy_debuginfo}\
%{expand:%%files -f debuginfo%{?2}.list %{?2:%{2}-}debuginfo}\
%{debuginfodir}/boot/System.map-%{KVERREL}%{?2:.%{2}}\
%else\
%{expand:%%files %{?2:%{2}-}debuginfo}\
%endif\
%defattr(-,root,root)\
%if !%{fancy_debuginfo}\
%if "%{elf_image_install_path}" != ""\
%{debuginfodir}/%{elf_image_install_path}/*-%{KVERREL}%{?2:.%{2}}.debug\
%endif\
%{debuginfodir}/lib/modules/%{KVERREL}%{?2:.%{2}}\
%{debuginfodir}/usr/src/kernels/%{KVERREL}%{?2:.%{2}}\
%{debuginfodir}/boot/System.map-%{KVERREL}%{?2:.%{2}}\
%endif\
%endif\
%endif\
%endif\
%{nil}


%kernel_variant_files %{with_up}
%kernel_variant_files %{with_smp} smp
%kernel_variant_files %{with_debug} debug
%kernel_variant_files %{with_pae} PAE
%kernel_variant_files %{with_pae_debug} PAEdebug
%ifarch s390x
%kernel_variant_files %{with_kdump} kdump
%else
%kernel_variant_files -k vmlinux %{with_kdump} kdump
%endif

%changelog
* Mon Jun 27 2011 Karanbir Singh <kbsingh@centos.org> [2.6.32-71.29.1.el6.centos]
- Roll in CentOS Branding

* Thu Apr 21 2011 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.29.1.el6]
- [mm] Revert "[mm] pdpte registers are not flushed when PGD entry is changed in x86 PAE mode" (Larry Woodman) [695256 691310]

* Wed Apr 20 2011 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.28.1.el6]
- [net] bonding: fix jiffy comparison issues (Andy Gospodarek) [698109 696337]
- [drm] radeon/kms: check AA resolve registers on r300 + regression fix (Dave Airlie) [680001 680002] {CVE-2011-1016}
- [infiniband] uverbs: Handle large number of entries in poll CQ (Eugene Teo) [688429 696137] {CVE-2011-1044 CVE-2010-4649}
- [net] sctp: fix the INIT/INIT-ACK chunk length calculation (Thomas Graf) [695386 690743] {CVE-2011-1573}
- [net] CAN: Use inode instead of kernel address for /proc file (Danny Feng) [664560 664561] {CVE-2010-4565}
- [fs] inotify: fix double free/corruption of stuct user (Eric Paris) [656831 656832] {CVE-2010-4250}
- [net] netfilter: ipt_CLUSTERIP: fix buffer overflow (Jiri Pirko) [689341 689342]
- [net] bonding: change test for presence of VLANs (Jiri Pirko) [696487 683496]
- [scsi] scsi_dh: fix reference counting in scsi_dh_activate error path (Mike Snitzer) [696889 680140]
- [net] enable VLAN NULL tagging (Neil Horman) [683810 633571]
- [scsi] scsi_dh: propagate SCSI device deletion (Mike Snitzer) [698114 669411]
- [fs] inotify: stop kernel memory leak on file creation failure (Eric Paris) [656831 656832] {CVE-2010-4250}

* Fri Apr 15 2011 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.27.1.el6]
- [scsi] megaraid: give FW more time to recover from reset (Tomas Henzl) [695322 692673]
- [netdrv] ixgbe: fix for 82599 erratum on Header Splitting (Andy Gospodarek) [683820 669231]
- [sound] ALSA: hda - nvhdmi: Add missing codec IDs, unify names (Jaroslav Kysela) [683817 636922]
- [mm] pdpte registers are not flushed when PGD entry is changed in x86 PAE mode (Larry Woodman) [695256 691310]
- [net] fix ebtables stack infoleak (Eugene Teo) [681322 681323] {CVE-2011-1080}
- [drm] fix unsigned vs signed comparison issue in modeset ctl ioctl (Don Howard) [679927 679928] {CVE-2011-1013}
- [pci] Enable ASPM state clearing regardless of policy (Alex Williamson) [694073 681017]
- [pci] Disable ASPM if BIOS asks us to (Alex Williamson) [694073 681017]
- [mm] do not keep kswapd awake for an unreclaimable zone (Johannes Weiner) [694186 633825]

* Mon Apr 11 2011 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.26.1.el6]
- [net] bnep: fix buffer overflow (Don Howard) [681315 681316] {CVE-2011-1079}
- [scsi] aic94xx: world-writable sysfs update_bios file (Don Howard) [679306 679307]
- [x86] tc1100-wmi: world-writable sysfs wireless and jogdial files (Don Howard) [679306 679307]
- [x86] acer-wmi: world-writable sysfs threeg file (Don Howard) [679306 679307]
- [mfd] ab3100: world-writable debugfs *_priv files (Don Howard) [679306 679307]
- [v4l] sn9c102: world-wirtable sysfs files (Don Howard) [679306 679307]
- [x86] Fix EFI pagetable to map whole memory (Takao Indoh) [670850 664364]
- [kernel] CAP_SYS_MODULE bypass via CAP_NET_ADMIN (Phillip Lougher) [681772 681773] {CVE-2011-1019}
- [kernel] failure to revert address limit override in OOPS error path (Dave Anderson) [659572 659573] {CVE-2010-4258}
- [fs] xfs: zero proper structure size for geometry calls (Phillip Lougher) [677267 677268] {CVE-2011-0711}
- [fs] xfs: prevent leaking uninitialized stack memory in FSGEOMETRY_V1 (Phillip Lougher) [677267 677268] {CVE-2011-0711}
- [tty] tty_audit: fix tty_audit_add_data live lock on audit disabled (Danny Feng) [684275 680126]
- [kernel] proc: protect mm start_code/end_code in /proc/pid/stat (Eugene Teo) [684572 684573] {CVE-2011-0726}
- [net] dccp oops (Eugene Teo) [682957 682958] {CVE-2011-1093}
- [firmware] dcdbas: force SMI to happen when expected (Shyam Iyer) [683440 664832]
- [security] ima: fix add LSM rule bug (Eric Paris) [667914 667915] {CVE-2011-0006}
- [sound] caiaq: Fix possible string buffer overflow (Jaroslav Kysela) [678475 678476] {CVE-2011-0712}
- [net] ixgbe: add option to control interrupt mode (Andy Gospodarek) [670114 670110 622640 637332]

* Sat Apr 2 2011 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.25.1.el6]
- [net] bridge: do not learn from exact matches (Jiri Pirko) [691777 623199]

* Sat Mar 26 2011 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.24.1.el6]
- [fs] Revert "[fs] inotify: stop kernel memory leak on file creation failure" (Eric Paris) [656831 656832] {CVE-2010-4250}

* Thu Mar 24 2011 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.23.1.el6]
- [x86] Revert "[x86] mtrr: Assume SYS_CFG[Tom2ForceMemTypeWB] exists on all future AMD CPUs" (Frank Arnold) [683813 652208]

* Wed Mar 23 2011 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.22.1.el6]
- rebuild

* Thu Mar 17 2011 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.21.1.el6]
- [netdrv] ixgbe: limit VF access to network traffic (Frantisek Hrbata) [684129 678717]
- [netdrv] ixgbe: work around for DDP last buffer size (Frantisek Hrbata) [684129 678717]
- [net] gro: reset dev and skb_iff on skb reuse (Andy Gospodarek) [688311 681970]
- [x86] mtrr: Assume SYS_CFG[Tom2ForceMemTypeWB] exists on all future AMD CPUs (Frank Arnold) [683813 652208]
- [virt] virtio_net: Add schedule check to napi_enable call (Michael S. Tsirkin) [684268 676579]
- [s390x] mm: add devmem_is_allowed() for STRICT_DEVMEM checking (Hendrik Brueckner) [684267 647365]
- [powerpc] Don't use kernel stack with translation off (Steve Best) [684266 628951]
- [powerpc] Initialise paca->kstack before early_setup_secondary (Steve Best) [684266 628951]

* Mon Mar 14 2011 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.20.1.el6]
- [dvb] kernel: av7110 negative array offset (Mauro Carvalho Chehab) [672403 672404] {CVE-2011-0521}
- [fs] sunrpc: Correct a misapplied patch (J. Bruce Fields) [678094 678146] {CVE-2011-0714}
- [netdrv] orinoco: fix TKIP countermeasure behaviour (Stanislaw Gruszka) [667908 667909] {CVE-2010-4648}
- [kernel] /proc/vmcore: speed up access to vmcore file (Neil Horman) [683442 672937]
- [netdrv] cnic: Fix big endian bug (Steve Best) [678484 676640]
- [scsi] fcoe: drop FCoE LOGO in FIP mode (Mike Christie) [683814 668114]
- [s390x] remove task_show_regs (Danny Feng) [677854 677855] {CVE-2011-0710}
- [ib] cm: Bump reference count on cm_id before invoking callback (Doug Ledford) [676190 676191] {CVE-2011-0695}
- [rdma] cm: Fix crash in request handlers (Doug Ledford) [676190 676191] {CVE-2011-0695}
- [net] bridge: Fix mglist corruption that leads to memory corruption (Herbert Xu) [678172 659421] {CVE-2011-0716}
- [netdrv] r8169: use RxFIFO overflow workaround and prevent RxFIFO induced infinite loops (Ivan Vecera) [680080 630810]
- [s390x] kernel: nohz vs cpu hotplug system hang (Hendrik Brueckner) [683815 668470]
- [netdrv] cxgb3/cxgb3_main.c: prevent reading uninitialized stack memory (Doug Ledford) [633156 633157] {CVE-2010-3296}
- [configs] redhat: added CONFIG_SECURITY_DMESG_RESTRICT option (Frantisek Hrbata) [683822 653245]
- [kernel] restrict unprivileged access to kernel syslog (Frantisek Hrbata) [683822 653245]
- [fs] cifs: allow matching of tcp sessions in CifsNew state (Jeff Layton) [683812 629085]
- [fs] cifs: fix potential double put of TCP session reference (Jeff Layton) [683812 629085]
- [fs] cifs: prevent possible memory corruption in cifs_demultiplex_thread (Jeff Layton) [683812 629085]
- [fs] cifs: eliminate some more premature cifsd exits (Jeff Layton) [683812 629085]
- [fs] cifs: prevent cifsd from exiting prematurely (Jeff Layton) [683812 629085]
- [fs] CIFS: Make cifs_convert_address() take a const src pointer and a length (Jeff Layton) [683812 629085]
- [kdump] kexec: accelerate vmcore copies by marking oldmem in /proc/vmcore as cached (Neil Horman) [683445 641315]
- [virt] KVM: VMX: Disallow NMI while blocked by STI (Avi Kivity) [683783 616296]
- [virt] kvm: write protect memory after slot swap (Michael S. Tsirkin) [683781 647367]

* Fri Feb 25 2011 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.19.1.el6]
- [crypto] sha-s390: Reset index after processing partial block (Herbert Xu) [678996 626515]
- [net] clear heap allocations for privileged ethtool actions (Jiri Pirko) [672434 672435] {CVE-2010-4655}
- [usb] iowarrior: don't trust report_size for buffer size (Don Zickus) [672421 672422] {CVE-2010-4656}
- [virt] virtio: console: Wake up outvq on host notifications (Amit Shah) [678558 643750]
- [fs] inotify: stop kernel memory leak on file creation failure (Eric Paris) [656831 656832] {CVE-2010-4250}
- [net] sctp: fix kernel panic resulting from mishandling of icmp dest unreachable msg (Neil Horman) [667028 667029] {CVE-2010-4526}
- [mm] install_special_mapping skips security_file_mmap check (Frantisek Hrbata) [662198 662199] {CVE-2010-4346}
- [kdump] vt-d: Handle previous faults after enabling fault handling (Takao Indoh) [678485 617137]
- [kdump] Enable the intr-remap fault handling after local apic setup (Takao Indoh) [678485 617137]
- [kdump] vt-d: Fix the vt-d fault handling irq migration in the x2apic mode (Takao Indoh) [678485 617137]
- [kdump] vt-d: Quirk for masking vtd spec errors to platform error handling logic (Takao Indoh) [678485 617137]
- [virt] virtio: console: Don't block entire guest if host doesn't read data (Amit Shah) [678562 643751]
- [virt] virtio: console: Prevent userspace from submitting NULL buffers (Amit Shah) [678559 635535]
- [virt] virtio: console: Fix poll blocking even though there is data to read (Amit Shah) [678561 634232]

* Wed Feb 2 2011 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.18.1.el6]
- [netdrv] ixgbe: make sure FCoE DDP user buffers are really released by the HW (Frantisek Hrbata) [674002 617193]
- [netdrv] ixgbe: invalidate FCoE DDP context when no error status is available (Frantisek Hrbata) [674002 617193]
- [netdrv] ixgbe: avoid doing FCoE DDP when adapter is DOWN or RESETTING (Frantisek Hrbata) [674002 617193]
- [fcoe] libfc: remove tgt_flags from fc_fcp_pkt struct (Mike Christie) [666797 633915]
- [fcoe] libfc: use rport timeout values for fcp recovery (Frantisek Hrbata) [666797 633915]
- [fcoe] libfc: incorrect scsi host byte codes returned to scsi-ml (Mike Christie) [666797 633915]
- [scsi] scsi_dh_alua: fix overflow in alua_rtpg port group id check (Mike Snitzer) [673978 670572]

* Fri Jan 28 2011 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.17.1.el6]
- [s390x] kdump: allow zfcpdump to mount and write to ext4 file systems (Amerigo Wang) [661667 628676]
- [scsi] qla2xxx: Properly set the return value in function qla2xxx_eh_abort (Chad Dupuis) [664398 635710]
- [scsi] qla2xxx: Drop srb reference before waiting for completion (Chad Dupuis) [664398 635710]
- [virt] KVM: VMX: Really clear cr0.ts when giving the guest ownership of the fpu (Avi Kivity) [658891 645898]
- [virt] KVM: SVM: Initialize fpu_active in init_vmcb() (Avi Kivity) [658891 645898]
- [virt] KVM: x86: Use unlazy_fpu() for host FPU (Avi Kivity) [658891 645898]
- [virt] KVM: Set cr0.et when the guest writes cr0 (Avi Kivity) [658891 645898]
- [virt] KVM: VMX: Give the guest ownership of cr0.ts when the fpu is active (Avi Kivity) [658891 645898]
- [virt] KVM: Lazify fpu activation and deactivation (Avi Kivity) [658891 645898]
- [virt] KVM: VMX: Allow the guest to own some cr0 bits (Avi Kivity) [658891 645898]
- [virt] KVM: Replace read accesses of vcpu->arch.cr0 by an accessor (Avi Kivity) [658891 645898]
- [virt] KVM: VMX: trace clts and lmsw instructions as cr accesses (Avi Kivity) [658891 645898]

* Mon Jan 24 2011 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.16.1.el6]
- [net] ipsec: fragment locally generated tunnel-mode IPSec6 packets as needed (Herbert Xu) [670421 661113]
- [net] tcp: Increase TCP_MAXSEG socket option minimum to TCP_MIN_MSS (Frantisek Hrbata) [652510 652511] {CVE-2010-4165}
- [perf] perf_events: Fix perf_counter_mmap() hook in mprotect() (Oleg Nesterov) [651672 651673] {CVE-2010-4169}
- [md] dm mpath: revert "dm: Call blk_abort_queue on failed paths" (Mike Snitzer) [658854 636771]
- [x86] UV: Address interrupt/IO port operation conflict (George Beshers) [662921 659480]
- [mm] guard page for stacks that grow upwards (Johannes Weiner) [666796 630562]
- [scsi] enable state transistions from OFFLINE to RUNNING (Mike Christie) [660590 643237]
- [scsi] set queue limits no_cluster for stacked devices (Mike Snitzer) [662050 658293]
- [mm] Out-of-memory under memory cgroup can call both of oom-killer-for-memcg and oom-killer-for-page-fault (Larry Woodman) [661732 592879]
- [scsi] libfc: possible race could panic system due to NULL fsp->cmd (Mike Christie) [662049 638297]
- [kernel] exec: copy-and-paste the fixes into compat_do_execve() paths (Oleg Nesterov) [627811 625695] {CVE-2010-4243}
- [kernel] exec: make argv/envp memory visible to oom-killer (Oleg Nesterov) [627811 625695] {CVE-2010-4243}
- [virt] virtio: console: Send SIGIO in case of port unplug (Amit Shah) [652720 624628]
- [virt] virtio: console: Send SIGIO on new data arrival on ports (Amit Shah) [652720 624628]
- [virt] virtio: console: Send SIGIO to processes that request it for host events (Amit Shah) [652720 624628]
- [virt] virtio: console: Reference counting portdev structs is not needed (Amit Shah) [662721 628805]
- [virt] virtio: console: Add reference counting for port struct (Amit Shah) [662721 628805]
- [virt] virtio: console: Use cdev_alloc() instead of cdev_init() (Amit Shah) [662721 628805]
- [virt] virtio: console: Add a find_port_by_devt() function (Amit Shah) [662721 628805]
- [virt] virtio: console: Add a list of portdevs that are active (Amit Shah) [662721 628805]
- [virt] virtio: console: open: Use a common path for error handling (Amit Shah) [662721 628805]
- [virt] virtio: console: remove_port() should return void (Amit Shah) [662721 628805]
- [virt] virtio: console: Make write() return -ENODEV on hot-unplug (Amit Shah) [662721 628805]
- [virt] virtio: console: Make read() return -ENODEV on hot-unplug (Amit Shah) [662721 628805]
- [virt] virtio: console: Unblock poll on port hot-unplug (Amit Shah) [662721 628805]
- [virt] virtio: console: Un-block reads on chardev close (Amit Shah) [662721 628805]
- [virt] virtio: console: Check if portdev is valid in send_control_msg() (Amit Shah) [662721 628805]
- [virt] virtio: console: Remove control vq data only if using multiport support (Amit Shah) [662721 628805]
- [virt] virtio: console: Reset vdev before removing device (Amit Shah) [662721 628805]
- [fs] Fix nfsv4 client lock reclaim behaviour (Sachin Prabhu) [661730 638269]
- [scsi] scsi_dh_alua: Handle all states correctly (Mike Snitzer) [659610 636994]
- [kernel] execve: improve interactivity and respond to SIGKILL with large arguments (Dave Anderson) [661731 629178]
- [virt] xen: handle events as edge-triggered (Andrew Jones) [661737 550724]
- [virt] xen: use percpu interrupts for IPIs and VIRQs (Andrew Jones) [661737 550724]

* Sun Jan 23 2011 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.15.1.el6]
- [net] bonding: prevent oopsing on calling pskb_may_pull on shared skb (Andy Gospodarek) [671342 665110]

* Wed Jan 5 2011 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.14.1.el6]
- [kvm] x86: zero kvm_vcpu_events->interrupt.pad (Marcelo Tosatti) [665471 665409] {CVE-2010-4525}

* Thu Dec 9 2010 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.13.1.el6]
- [scsi] lpfc: Fixed crashes for NULL pnode dereference (Rob Evers) [660589 635733]

* Wed Dec 8 2010 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.12.1.el6]
- [netdrv] igb: only use vlan_gro_receive if vlans are registered (Stefan Assmann) [652804 660192] {CVE-2010-4263}
- [net] core: neighbour update Oops (Jiri Pirko) [660591 658518]
- [scsi] lpfc: Set heartbeat timer off by default (Rob Evers) [660244 655935]
- [scsi] lpfc: Fixed crashes for BUG_ONs hit in the lpfc_abort_handler (Rob Evers) [659611 645882]

* Mon Dec 6 2010 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.11.1.el6]
- [kernel] posix-cpu-timers: workaround to suppress the problems with mt exec (Oleg Nesterov) [656267 656268] {CVE-2010-4248}
- [fs] bio: take care not overflow page count when mapping/copying user data (Danny Feng) [652530 652531] {CVE-2010-4162}
- [net] can-bcm: fix minor heap overflow (Danny Feng) [651846 651847] {CVE-2010-3874}
- [net] filter: make sure filters dont read uninitialized memory (Jiri Pirko) [651704 651705] {CVE-2010-4158}
- [net] inet_diag: Make sure we actually run the same bytecode we audited (Jiri Pirko) [651268 651269] {CVE-2010-3880}
- [v4l] ivtvfb: prevent reading uninitialized stack memory (Mauro Carvalho Chehab) [648832 648833] {CVE-2010-4079}
- [drm] via/ioctl.c: prevent reading uninitialized stack memory (Dave Airlie) [648718 648719] {CVE-2010-4082}
- [char] nozomi: clear data before returning to userspace on TIOCGICOUNT (Mauro Carvalho Chehab) [648705 648706] {CVE-2010-4077}
- [serial] clean data before filling it on TIOCGICOUNT (Mauro Carvalho Chehab) [648702 648703] {CVE-2010-4075}
- [net] af_unix: limit unix_tot_inflight (Neil Horman) [656761 656762] {CVE-2010-4249}
- [block] check for proper length of iov entries in blk_rq_map_user_iov() (Danny Feng) [652958 652959] {CVE-2010-4163}
- [net] Limit sendto()/recvfrom()/iovec total length to INT_MAX (Jiri Pirko) [651894 651895] {CVE-2010-4160}
- [netdrv] mlx4: Add OFED-1.5.2 patch to increase log_mtts_per_seg (Jay Fenlason) [643815 637284]
- [kernel] kbuild: fix external module compiling (Aristeu Rozanski) [658879 655231]
- [net] bluetooth: Fix missing NULL check (Jarod Wilson) [655667 655668] {CVE-2010-4242}
- [kernel] ipc: initialize structure memory to zero for compat functions (Danny Feng) [648694 648695] {CVE-2010-4073}
- [kernel] shm: fix information leak to userland (Danny Feng) [648688 648689] {CVE-2010-4072}
- [md] dm: remove extra locking when changing device size (Mike Snitzer) [653900 644380]
- [block] read i_size with i_size_read() (Mike Snitzer) [653900 644380]
- [kbuild] don't sign out-of-tree modules (Aristeu Rozanski) [655122 653507]

* Mon Nov 29 2010 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.10.1.el6]
- [fs] xfs: prevent reading uninitialized stack memory (Dave Chinner) [630808 630809] {CVE-2010-3078}
- [net] fix rds_iovec page count overflow (Jiri Pirko) [647423 647424] {CVE-2010-3865}
- [scsi] Fix megaraid_sas driver SLAB memory leak detected with CONFIG_DEBUG_SLAB (Shyam Iyer) [649436 633836]
- [usb] serial/mos*: prevent reading uninitialized stack memory (Don Zickus) [648697 648698] {CVE-2010-4074}
- [kernel] ecryptfs_uid_hash() buffer overflow (Jerome Marchand) [626320 611388] {CVE-2010-2492}
- [sound] seq/oss - Fix double-free at error path of snd_seq_oss_open() (Jaroslav Kysela) [630554 630555] {CVE-2010-3080}
- [virt] virtio-net: init link state correctly (Jason Wang) [653340 646369]
- [netdrv] prevent reading uninitialized memory in hso driver (Thomas Graf) [633143 633144] {CVE-2010-3298}

* Sun Nov 21 2010 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.9.1.el6]
- [fs] Do not mix FMODE_ and O_ flags with break_lease() and may_open() (Harshula Jayasuriya) [648408 642677]
- [fs] aio: check for multiplication overflow in do_io_submit (Jeff Moyer) [629450 629451] {CVE-2010-3067}
- [net] fix info leak from kernel in ethtool operation (Neil Horman) [646727 646728] {CVE-2010-3861}
- [net] packet: fix information leak to userland (Jiri Pirko) [649899 649900] {CVE-2010-3876}
- [net] clean up info leak in act_police (Neil Horman) [636393 636394] {CVE-2010-3477}
- [kernel] sys_semctl: fix kernel stack leakage (Danny Feng) [648723 648724] {CVE-2010-4083}
- [sound] sound/pci/rme9652: prevent reading uninitialized stack memory (Stanislaw Gruszka) [648710 648715 648711 648716] {CVE-2010-4080 CVE-2010-4081}
- [mm] Prevent Out Of Memory when changing cpuset's mems on NUMA (Larry Woodman) [651996 597127]

* Thu Oct 28 2010 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.8.1.el6]
- [mm] remove false positive THP pmd_present BUG_ON (Andrea Arcangeli) [647391 646384]

* Wed Oct 27 2010 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.7.1.el6]
- [drm] ttm: fix regression introduced in dfb4a4250168008c5ac61e90ab2b86f074a83a6c (Dave Airlie) [646994 644896]

* Wed Oct 20 2010 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.6.1.el6]
- [block] fix a potential oops for callers of elevator_change (Jeff Moyer) [644926 641408]

* Tue Oct 19 2010 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.5.1.el6]
- [security] IMA: require command line option to enabled (Eric Paris) [644636 643667]
- [net] Fix priv escalation in rds protocol (Neil Horman) [642899 642900] {CVE-2010-3904}
- [v4l] Remove compat code for VIDIOCSMICROCODE (Mauro Carvalho Chehab) [642472 642473] {CVE-2010-2963}
- [kernel] tracing: do not allow llseek to set_ftrace_filter (Jiri Olsa) [631625 631626] {CVE-2010-3079}
- [virt] xen: hold mm->page_table_lock in vmalloc_sync (Andrew Jones) [644038 643371]
- [fs] xfs: properly account for reclaimed inodes (Dave Chinner) [642680 641764]
- [drm] fix ioctls infoleak (Danny Feng) [626319 621437] {CVE-2010-2803}
- [netdrv] wireless extensions: fix kernel heap content leak (John Linville) [628437 628438] {CVE-2010-2955}
- [netdrv] niu: buffer overflow for ETHTOOL_GRXCLSRLALL (Danny Feng) [632071 632072] {CVE-2010-3084}
- [mm] add debug checks for mapcount related invariants (Andrea Arcangeli) [642679 622327 644037 642570]
- [mm] move VM_BUG_ON inside the page_table_lock of zap_huge_pmd (Andrea Arcangeli) [642679 622327 644037 642570]
- [mm] compaction: handle active and inactive fairly in too_many_isolated (Andrea Arcangeli) [642679 622327 644037 642570]
- [mm] start_khugepaged after setting transparent_hugepage_flags (Andrea Arcangeli) [642679 622327 644037 642570]
- [mm] fix hibernate memory corruption (Andrea Arcangeli) [644037 642570]
- [mm] ksmd wait_event_freezable (Andrea Arcangeli) [642679 622327 644037 642570]
- [mm] khugepaged wait_event_freezable (Andrea Arcangeli) [642679 622327 644037 642570]
- [mm] unlink_anon_vmas in __split_vma in case of error (Andrea Arcangeli) [642679 622327 644037 642570]
- [mm] fix memleak in copy_huge_pmd (Andrea Arcangeli) [642679 622327 644037 642570]
- [mm] fix hang on anon_vma->root->lock (Andrea Arcangeli) [642679 622327 644037 642570]
- [mm] avoid breaking huge pmd invariants in case of vma_adjust failures (Andrea Arcangeli) [642679 622327 644037 642570]

* Tue Oct 12 2010 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.4.1.el6]
- [scsi] fcoe: set default FIP mode as FIP_MODE_FABRIC (Mike Christie) [641457 636233]
- [virt] KVM: Fix fs/gs reload oops with invalid ldt (Avi Kivity) [639884 639885] {CVE-2010-3698}
- [drm] i915: prevent arbitrary kernel memory write (Jerome Marchand) [637690 637691] {CVE-2010-2962}
- [scsi] libfc: adds flogi retry in case DID is zero in RJT (Mike Christie) [641456 633907]
- [kernel] prevent heap corruption in snd_ctl_new() (Jerome Marchand) [638485 638486] {CVE-2010-3442}
- [scsi] lpfc: lpfc driver oops during rhel6 installation with snapshot 12/13 and emulex FC (Rob Evers) [641907 634703]
- [fs] ext4: Always journal quota file modifications (Eric Sandeen) [641454 624909]
- [mm] fix split_huge_page error like mapcount 3 page_mapcount 2 (Andrea Arcangeli) [641258 640611]
- [block] Fix pktcdvd ioctl dev_minor range check (Jerome Marchand) [638088 638089] {CVE-2010-3437}
- [drm] ttm: Fix two race conditions + fix busy codepaths (Dave Airlie) [642045 640871]
- [drm] Prune GEM vma entries (Dave Airlie) [642043 640870]
- [virt] ksm: fix bad user data when swapping (Andrea Arcangeli) [641459 640579]
- [virt] ksm: fix page_address_in_vma anon_vma oops (Andrea Arcangeli) [641460 640576]
- [net] sctp: Fix out-of-bounds reading in sctp_asoc_get_hmac() (Jiri Pirko) [640461 640462] {CVE-2010-3705}
- [mm] Move vma_stack_continue into mm.h (Mike Snitzer) [641483 638525]
- [net] sctp: Do not reset the packet during sctp_packet_config() (Jiri Pirko) [637681 637682] {CVE-2010-3432}
- [mm] vmstat incorrectly reports disk IO as swap in (Steve Best) [641458 636978]
- [scsi] fcoe: Fix NPIV (Neil Horman) [641455 631246]

* Sun Oct 3 2010 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.3.1.el6]
- [block] prevent merges of discard and write requests (Mike Snitzer) [639412 637805]
- [drm] nouveau: correct INIT_DP_CONDITION subcondition 5 (Ben Skeggs) [638973 636678]
- [drm] nouveau: enable enhanced framing only if DP display supports it (Ben Skeggs) [638973 636678]
- [drm] nouveau: fix required mode bandwidth calculation for DP (Ben Skeggs) [638973 636678]
- [drm] nouveau: disable hotplug detect around DP link training (Ben Skeggs) [638973 636678]
- [drm] nouveau: set DP display power state during DPMS (Ben Skeggs) [638973 636678]
- [mm] remove "madvise" from possible /sys/kernel/mm/redhat_transparent_hugepage/enabled options (Larry Woodman) [636116 634500]
- [netdrv] cxgb3: don't flush the workqueue if we are called from the workqueue (Doug Ledford) [634973 631547]
- [netdrv] cxgb3: deal with fatal parity error status in interrupt handler (Doug Ledford) [634973 631547]
- [netdrv] cxgb3: now that we define fatal parity errors, make sure they are cleared (Doug Ledford) [634973 631547]
- [netdrv] cxgb3: Add define for fatal parity error bit manipulation (Doug Ledford) [634973 631547]
- [virt] Emulate MSR_EBC_FREQUENCY_ID (Jes Sorensen) [633966 629836]
- [virt] Define MSR_EBC_FREQUENCY_ID (Jes Sorensen) [633966 629836]
- [kernel] initramfs: Fix initramfs size calculation (Hendrik Brueckner) [637087 626956]
- [kernel] initramfs: Generalize initramfs_data.xxx.S variants (Hendrik Brueckner) [637087 626956]
- [drm] radeon/kms: fix sideport detection on newer rs880 boards (Dave Airlie) [634984 626454]
- [block] switch s390 tape_block and mg_disk to elevator_change() (Mike Snitzer) [633864 632631]
- [block] add function call to switch the IO scheduler from a driver (Mike Snitzer) [633864 632631]

* Wed Sep 22 2010 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.2.1.el6]
- [misc] make compat_alloc_user_space() incorporate the access_ok() (Xiaotian Feng) [634465 634466] {CVE-2010-3081}
- [x86] kernel: fix IA32 System Call Entry Point Vulnerability (Xiaotian Feng) [634451 634452] {CVE-2010-3301}

* Thu Sep 16 2010 Frantisek Hrbata <fhrbata@redhat.com> [2.6.32-71.1.1.el6]
- [security] Make kernel panic in FIPS mode if modsign check fails (David Howells) [633865 625914]
- [virt] Guests on AMD with CPU type 6 and model >= 8 trigger errata read of MSR_K7_CLK_CTL (Jes Sorensen) [632292 629066]
- [x86] UV: use virtual efi on SGI systems (George Beshers) [633964 627653]

* Wed Sep 01 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-71.el6]
- [fs] nfsd: initialize nfsd versions before creating svc (J. Bruce Fields) [628084]
- [fs] nfsd: fix startup/shutdown order bug (J. Bruce Fields) [628084]
- [security] KEYS: Fix bug in keyctl_session_to_parent() if parent has no session keyring (David Howells) [627808] {CVE-2010-2960}
- [security] KEYS: Fix RCU no-lock warning in keyctl_session_to_parent() (David Howells) [627808] {CVE-2010-2960}

* Wed Aug 25 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-70.el6]
- [x86] Disable AMD IOMMU by default (Matthew Garrett) [593787]
- [netdrv] Revert "iwlwifi: disable hardware scanning by default" (Stanislaw Gruszka) [625981]
- [s390x] kernel: fix tlb flushing vs. concurrent /proc accesses (Hendrik Brueckner) [587587]
- [s390x] kernel: prepare mm_context_t for new tlb flush handling (Hendrik Brueckner) [587587]
- [fs] NFS: Fix an Oops in the NFSv4 atomic open code (Jeff Layton) [625718]
- [net] can: add limit for nframes and clean up signed/unsigned variables (Danny Feng) [625702] {CVE-2010-2959}
- [fs] aio: bump i_count instead of using igrab (Jeff Moyer) [626595]
- [fs] cifs: check for NULL session password (Jeff Layton) [625583]
- [fs] cifs: fix NULL pointer dereference in cifs_find_smb_ses (Jeff Layton) [625583]

* Tue Aug 24 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-69.el6]
- [mm] make stack guard page logic use vm_prev pointer (Mike Snitzer) [607859]
- [mm] make the mlock() stack guard page checks stricter (Mike Snitzer) [607859]
- [mm] make the vma list be doubly linked (Mike Snitzer) [607859]
- [drm] nv50: insert a delay before fb change to prevent display engine hang (Ben Skeggs) [618225]
- [mm] fix up some user-visible effects of the stack guard page (Mike Snitzer) [607859]
- [net] sched: fix some kernel memory leaks (Jiri Pirko) [624637] {CVE-2010-2942}

* Mon Aug 23 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-68.el6]
- [virt] xen pvhvm: don't start xenbus w/out pvhvm (Andrew Jones) [624665]
- [virt] xen pvhvm: don't unplug emulated devs w/out pvhvm (Andrew Jones) [625460]
- [virt] xen pvhvm: export xen_pv_hvm_enable (Andrew Jones) [625460]
- [fs] ext4: fix one more tracing oops (Eric Sandeen) [619013]
- [drm] Provide for HDMI output on NVIDIA GPUs (John Feeney) [619877]
- [netdrv] iwlwifi: disable aspm by default (John Linville) [611075]
- [x86] acpi: Update battery information on notification 0x81 (Matthew Garrett) [606388]

* Fri Aug 20 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-67.el6]
- [x86] acpi: Update battery information on notification 0x81 (Matthew Garrett) [606388]
- [mm] fix up some user-visible effects of the stack guard page (Mike Snitzer) [607859]
- [mm] fix page table unmap for stack guard page properly (Mike Snitzer) [607859]
- [x86] don't send SIGBUS for kernel page faults (Mike Snitzer) [607859]
- [mm] fix missing page table unmap for stack guard page failure case (Mike Snitzer) [607859]
- [mm] keep a guard page below a grow-down stack segment (Mike Snitzer) [607859]
- [fs] xfs: fix untrusted inode number lookup (Dave Chinner) [624860]
- [kernel] init, sched: Fix race between init and kthreadd (Gleb Natapov) [624329]
- [net] Fix IGMP3 report parsing (Aristeu Rozanski) [621431]

* Tue Aug 17 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-66.el6]
- [netdrv] be2net: maintain multicast packet count in driver (Ivan Vecera) [621287]
- [scsi] hpsa: don't use doorbel reset (Tomas Henzl) [612486]
- [x86] Fix the kdump kernel OOMs caused by passthrough mode setting (Bhavna Sarathy) [624059]
- [acpi] Force "pci=noacpi" on HP xw9300 (Prarit Bhargava) [615276]
- [mm] Revert mm-vmstat-Actively-update-vmstat-counters-in-low-memory-situations (Larry Woodman) [622328]
- [x86] Run EFI in physical mode to enable kdump on EFI-booted system (Takao Indoh) [593111]
- [fs] ext4: protect inode bitmap clearing w/ spinlock (Eric Sandeen) [623666]
- [scsi] libfc: call fc_remote_port_chkready under the host lock (Mike Christie) [623786]
- [x86] Ensure that we provide per-cpu ACPI support (Matthew Garrett) [623874]
- [fs] ext4: consolidate in_range() definitions (Eric Sandeen) [621829]
- [fs] ext4: fix NULL pointer dereference in tracing (Eric Sandeen) [619013]
- [block] O_DIRECT: fix the splitting up of contiguous I/O (Jeff Moyer) [622504]

* Mon Aug 16 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-65.el6]
- [fs] ext4: fix discard failure detection (Eric Sandeen) [608731]
- [x86] Avoid potential NULL dereference in pcc-cpufreq (Matthew Garrett) [623768]
- [scsi] bfa: vport create/delete fix (Rob Evers) [619226]
- [net] tcp: fix crash in tcp_xmit_retransmit_queue (Jerome Marchand) [618386]
- [build] Skip depmod when installing to non-standard INSTALL_MOD_PATH (Jon Masters) [609170]
- [sound] disable NVIDIA HDMI PCI device for Lenovo T410 (Jaroslav Kysela) [605742]
- [scsi] increase flush timeout (Mike Christie) [605322]
- [x86] local_irq_save/restore when issuing IPI in early bootup (Prarit Bhargava) [602823]

* Fri Aug 13 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-64.el6]
- [kernel] Revert "[kernel] sched: Fix a race between ttwu() and migrate_task()" (Matthew Garrett) [620883]
- [fs] btrfs: fix checks in BTRFS_IOC_CLONE_RANGE (Eugene Teo) [617003] {CVE-2010-2537 CVE-2010-2538}
- [kernel] Makefile.build: make KBUILD_SYMTYPES work again (Don Zickus) [617749]
- [netdrv] iwlwifi: disable hardware scanning by default (Stanislaw Gruszka) [593566]
- [scsi] Revert: qla2xxx: Propogate transport disrupted status for cable pull conditions for faster failover (Chad Dupuis) [622041]
- [drm] radeon: Don't limit vram size to aperture size (Matthew Garrett) [622039]
- [fs] xfs: don't walk AGs that can't hold inodes (Dave Chinner) [621044]
- [mmc] add Ricoh e822 support (Stanislaw Gruszka) [619900]
- [scsi] mvsas: fix hot plug handling and IO issues (David Milburn) [616178]
- [dm] mpath: enable discard support (Mike Snitzer) [619196]
- [block] update request stacking methods to support discards (Mike Snitzer) [619196]
- [dm] stripe: enable discard support (Mike Snitzer) [619196]
- [dm] stripe: optimize sector division (Mike Snitzer) [619196]
- [dm] stripe: move sector translation to a function (Mike Snitzer) [619196]
- [dm] error: return error for discards (Mike Snitzer) [619196]
- [dm] delay: enable discard support (Mike Snitzer) [619196]
- [dm] zero: silently drop discards (Mike Snitzer) [619196]
- [dm] split discard requests on target boundaries (Mike Snitzer) [619196]
- [dm] use dm_target_offset macro (Mike Snitzer) [619196]
- [dm] factor out max_io_len_target_boundary (Mike Snitzer) [619196]
- [dm] use common __issue_target_request for flush and discard support (Mike Snitzer) [619196]
- [dm] rename map_info flush_request to target_request_nr (Mike Snitzer) [619196]
- [dm] remove the DM_TARGET_SUPPORTS_DISCARDS feature flag (Mike Snitzer) [619196]
- [dm] introduce num_discard_requests in dm_target structure (Mike Snitzer) [619196]

* Tue Aug 10 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-63.el6]
- [fs] ext4: protect io completion lists with locking (Eric Sandeen) [621660]
- [trace] Packport new mm tracepoint Documentation to RHEL6 (Larry Woodman) [618305]
- [virt] KVM: Trace exception injection (Gleb Natapov) [616427]
- [s390x] qeth: Clear mac_bits field when switching between l2/l3 (Hendrik Brueckner) [621333]
- [net] ethtool: Fix potential kernel buffer overflow in ETHTOOL_GRXCLSRLALL (Jiri Pirko) [608953] {CVE-2010-2478}
- [infiniband] Update QLogic QIB InfiniBand driver to version OFED 1.5.2 (Jay Fenlason) [572401]
- [fs] update RWA_MASK, READA and SWRITE to match the corresponding BIO_RW_ bits (Jeff Moyer) [621693]

* Tue Aug 10 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-62.el6]
- [drm] Revert matroxfb support for G200EV chip (Peter Bogdanovic) [604830]
- [drm] i915: more DP/eDP backport fixes (Dave Airlie) [615058]
- [drm] correctly update connector DPMS status in drm_fb_helper (Dave Airlie) [615058]
- [x86] ACPI/PM: Move ACPI video resume to a PM notifier (Dave Airlie) [615058]
- [virt] x86: preset lpj values when on VMware (Zachary Amsden) [617390]
- [virt] Revert "vhost-net: utilize PUBLISH_USED_IDX feature" (Michael S. Tsirkin)
- [virt] Revert "virtio: put last seen used index into ring itself" (Michael S. Tsirkin) [616503]
- [virt] Revert "virtio: net: Remove net-specific advertising of PUBLISH_USED feature" (Michael S. Tsirkin) [616503]
- [virt] vhost: max s/g to match qemu (Michael S. Tsirkin) [619002]
- [kernel] sched: Fix set_cpu_active() in cpu_down() (Danny Feng) [620807]
- [dm] separate device deletion from dm_put (Mike Snitzer) [619199]
- [dm] prevent access to md being deleted (Mike Snitzer) [619199]
- [dm] ioctl: release _hash_lock between devices in remove_all (Mike Snitzer) [619199]

* Fri Aug 06 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-61.el6]
- [netdrv] r8169: disable PCIe ASPM (Michal Schmidt) [619880]
- [fusion] mptfusion: fix DMA boudary (Tomas Henzl) [618625]
- [fusion] mptfusion: Bump version to 3.04.16 (Tomas Henzl) [618625]
- [fusion] mptfusion: Added code for occationally SATA hotplug failure (Tomas Henzl) [618625]
- [fusion] mptfusion: schedule_target_reset from all Reset context (Tomas Henzl) [618625]
- [fusion] mptfusion: Added sanity to check B_T mapping for device before adding to OS (Tomas Henzl) [618625]
- [fusion] mptfusion: Corrected declaration of device_missing_delay (Tomas Henzl) [618625]
- [fusion] mptfusion: Set fw_events_off to 1 at driver load time (Tomas Henzl) [618625]
- [net] s2io: fixing DBG_PRINT() macro (Danny Feng) [619097]
- [trace] backport file writeback tracepoints from upstream to RHEL6 (Larry Woodman) [618305]
- [virt] vhost: thread per device attached to owner cgroups (Alex Williamson) [615118]
- [cgroups] fix API thinko (Alex Williamson) [615118]
- [cgroup] Revert: "workqueue: API to create a workqueue in cgroup" (Alex Williamson) [615118]
- [net] bonding: allow arp_ip_targets on separate vlans to use arp validation (Andy Gospodarek) [581657]
- [x86] Revert "[x86] kernel performance optimization with CONFIG_DEBUG_RODATA" (Aristeu Rozanski)

* Fri Aug 06 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-60.el6]
- [security] selinux: convert the policy type_attr_map to flex_array (Eric Paris) [617255]
- [net] bridge: Fix IGMPv3 report parsing (Herbert Xu) [621431]
- [kernel] CRED: Fix get_task_cred() and task_state() to not resurrect dead credentials (Jiri Olsa) [620380]
- [net] bonding: set device in RLB ARP packet handler (Andy Gospodarek) [619450]
- [x86] Remove warning in p4-clockmod driver (Prarit Bhargava) [618415]
- [trace] Back port upstream mm/vmscan.c tracepoints to RHEL6 (Larry Woodman) [618305]
- [net] bridge: Fix skb leak when multicast parsing fails on TX (Jiri Pirko) [617505]
- [x86] Retract nmi-stacktrace patch (George Beshers) [598586]
- [fs] cifs: account for new creduid parameter in spnego upcall string (Jeff Layton) [618608]
- [fs] cifs: add separate cred_uid field to sesInfo (Jeff Layton) [618608]
- [fs] cifs: check kmalloc() result (Jeff Layton) [618608]
- [fs] cifs: remove unused cifsUidInfo struct (Jeff Layton) [618608]
- [fs] cifs: clean up cifs_find_smb_ses (Jeff Layton) [618608]
- [fs] cifs: match secType when searching for existing tcp session (Jeff Layton) [618608]
- [fs] cifs: move address comparison into separate function (Jeff Layton) [618608]
- [fs] cifs: set the port in sockaddr in a more clearly defined fashion (Jeff Layton) [618608]
- [fs] cifs: remove an potentially confusing, obsolete comment (Jeff Layton) [618608]
- [fs] cifs: remove unused ip_address field in struct TCP_Server_Info (Jeff Layton) [618608]
- [fs] cifs: have decode_negTokenInit set flags in server struct (Jeff Layton) [618608]
- [fs] cifs: break negotiate protocol calls out of cifs_setup_session (Jeff Layton) [618608]
- [fs] cifs: eliminate "first_time" parm to CIFS_SessSetup (Jeff Layton) [618608]
- [fs] cifs: save the dialect chosen by server (Jeff Layton) [618608]
- [fs] cifs: change && to || (Jeff Layton) [618608]
- [fs] cifs: rename "extended_security" to "global_secflags" (Jeff Layton) [618608]
- [fs] cifs: move tcon find/create into separate function (Jeff Layton) [618608]
- [fs] cifs: move SMB session creation code into separate function (Jeff Layton) [618608]
- [fs] cifs: track local_nls in volume info (Jeff Layton) [618608]
- [drm] nouveau: support fetching LVDS EDID from ACPI (Ben Skeggs) [616860]
- [drm] ACPI: Export EDID blocks to the kernel (Ben Skeggs) [616860]
- [fs] Fix for stuck recovery issue in GFS2 (Steven Whitehouse) [590878]
- [powerpc] fix unsupported hardware to only be power5 (Steve Best) [619501]
- [scsi] megaraid: fix sas expander issue (Tomas Henzl) [607930]
- [virt] Default Xen PV-HVM to off (Don Dutile) [618172]
- [mm] Correctly assign the number of MIGRATE_RESERVE pageblocks (Andrea Arcangeli) [614427]
- [fs] return EINVAL when thawing unfrozen filesystems (Eric Sandeen) [601324]
- [fs] GFS2: Fix problem where try locks were trying too hard (Steven Whitehouse) [585299]
- [scsi] bnx2i: Fix iscsi connection cleanup (Mike Christie) [616939]
- [scsi] bfa: fix sysfs crash while reading error_frames stats (Rob Evers) [594882]
- [fusion] Block Error handling for deleting devices or Device in DMD (Tomas Henzl) [615866]
- [netdrv] tun: avoid BUG, dump packet on GSO errors (Herbert Xu) [616845]
- [netdr] rt2500usb: Fix WEP Enterprise (Stanislaw Gruszka) [609721]
- [kernel] cmdline disable real time scheduler (George Beshers) [607587]
- [fs] ext4: re-inline ext4_rec_len_(to|from)_disk functions (Eric Sandeen) [522808]
- [netdrv] be2net: include latest upstream fixes (Ivan Vecera) [617187]

* Wed Aug 04 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-59.el6]
- [virt] Revert "[virt] vhost: create a vhost thread per device" (Aristeu Rozanski) [615118]

* Tue Aug 03 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-58.el6]
- [scsi] Update lpfc version for 8.3.5.17 driver release (Rob Evers) [612235]
- [scsi] Fix endian conversion for BlockGuard in IOCB response (Rob Evers) [612235]
- [scsi] Fixed a driver discovery issue where driver was unable to discover a target after Eveready back link bounce test (Rob Evers) [612235]
- [scsi] Update lpfc version for 8.3.5.16 driver release (Rob Evers) [612235]
- [scsi] Fixed BlockGuard endian conversion problem for supporting PowerPC EEH (Rob Evers) [612235]
- [scsi] Fixed VLAN ID 0xFFF set to reg_fcfi mailbox command on FCF empty FCF VLAN bitmap (Rob Evers) [612235]
- [scsi] Update lpfc version for 8.3.5.15 driver release (Rob Evers) [612235]
- [scsi] Fixed a race condition causing FLOGI issued from dual processes (Rob Evers) [612235]
- [scsi] Fix bug with ct response data not being sent with sli4 (Rob Evers) [612235]
- [scsi] Fixed RoundRobin FCF failover due to mis-interpretation of kernel find_next_bit (Rob Evers) [612235]
- [scsi] Enhanced round-robin FCF failover algorithm to re-start on new FCF async event (Rob Evers) [612235]
- [scsi] Clear Ignore Reg Login Flag when purging mailbox queue (Rob Evers) [612235]
- [scsi] Fix for ELS commands stuck on txq (Rob Evers) [612235]
- [scsi] Fix bug with unsolicited CT event command not setting a flag (Rob Evers) [612235]
- [drm] radeon/kms: fix possible mis-detection of sideport on rs690/rs740 (Jerome Glisse) [614583]
- [scsi] fcoe: remove check for zero fabric name (Mike Christie) [614264]
- [scsi] libfc: Add retry logic to lport state machine when receiving LS_RJT (Mike Christie) [614264]
- [scsi] fcoe: fix offload feature flag change from netdev (Mike Christie) [614264]
- [scsi] fcoe: adds src and dest mac address checking for fcoe frames (Mike Christie) [614264]
- [scsi] fcoe: cleans up fcoe_disable and fcoe_enable (Mike Christie) [614264]
- [scsi] lpfc Update from 8.3.5.13 to 8.3.5.14 FC/FCoE (Rob Evers) [603808]
- [fusion] mptfusion: release resources in error return path (Tomas Henzl) [618560]
- [scsi] IO error on SuperTrak EX4650 (Muuhh IKEDA) [593969]
- [virt] vhost: create a vhost thread per device (Michael S. Tsirkin) [615118]
- [kernel] workqueue: API to create a workqueue in cgroup (Michael S. Tsirkin) [615118]
- [cgroup] Add an API to attach a task to current task's cgroup (Michael S. Tsirkin) [615118]

* Tue Aug 03 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-57.el6]
- [mm] avoid stalling allocations by introducing watermark_wait (Rik van Riel) [589604]
- [mm] scale nr_rotated to balance memory pressure (Rik van Riel) [619384]
- [mm] fix anon memory statistics with transparent hugepages (Rik van Riel) [619384]
- [pci] avoid compiler warning in quirks.c (Alex Williamson) [619525]
- [pci] Fix build if quirks are not enabled (Alex Williamson) [619525]
- [pci] add Intel 82599 Virtual Function specific reset method (Alex Williamson) [619525]
- [pci] add Intel USB specific reset method (Alex Williamson) [619525]
- [pci] support device-specific reset methods (Alex Williamson) [619525]
- [kernel] Documentation: Update memory-hotplug documentation (Steve Best) [612579]
- [powerpc] Define memory_block_size_bytes() for ppc/pseries (Steve Best) [612579]
- [kernel] Update the node sysfs code (Steve Best) [612579]
- [kernel] Allow memory_block to span multiple memory sections (Steve Best) [612579]
- [kernel] Add section count to memory_block (Steve Best) [612579]
- [kernel] Add new phys_index properties (Steve Best) [612579]
- [kernel] Move the find_memory_block() routine up (Steve Best) [612579]
- [usb] xhci: rename driver to xhci_hcd (Don Zickus) [617217]
- [usb] kabi placeholders for xhci (Don Zickus) [617217]
- [fs] nfsd: minor nfsd_svc() cleanup (Jeff Layton) [599675]
- [fs] nfsd: move more into nfsd_startup() (Jeff Layton) [599675]
- [fs] nfsd: just keep single lockd reference for nfsd (Jeff Layton) [599675]
- [fs] nfsd: clean up nfsd_create_serv error handling (Jeff Layton) [599675]
- [fs] nfsd: fix error handling in __write_ports_addxprt (Jeff Layton) [599675]
- [fs] nfsd: fix error handling when starting nfsd with rpcbind down (Jeff Layton) [599675]
- [fs] nfsd4: fix v4 state shutdown error paths (Jeff Layton) [599675]
- [mm] page allocator: Update free page counters after pages are placed on the free list (Andrea Arcangeli) [614427]
- [mm] page allocator: Drain per-cpu lists after direct reclaim allocation fails (Andrea Arcangeli) [614427]
- [mm] vmstat: Actively update vmstat counters in low memory situations (Andrea Arcangeli) [614427]
- [kernel] mem-hotplug: fix potential race while building zonelist for new populated zone (John Villalovos) [581557]
- [kernel] mem-hotplug: avoid multiple zones sharing same boot strapping boot_pageset (John Villalovos) [581557]
- [kernel] cpu/mem hotplug: enable CPUs online before local memory online (John Villalovos) [581557]
- [mm] remove khugepaged young bit check (Andrea Arcangeli) [615381]

* Fri Jul 30 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-56.el6]
- [fs] GFS2: Backup plan for "vmalloc is slow" (Steven Whitehouse) [619331]
- [s390x] zfcp: Do not try "forced close" when port is already closed (Hendrik Brueckner) [612594]
- [s390x] zfcp: Do not unblock rport from REOPEN_PORT_FORCED (Hendrik Brueckner) [612597]
- [s390x] zfcp: Fix retry after failed "open port" erp action (Hendrik Brueckner) [612601]
- [s390x] zfcp: Fail erp after timeout (Hendrik Brueckner) [612618]
- [s390x] zfcp: Use forced_reopen in terminate_rport_io callback (Hendrik Brueckner) [612621]
- [s390x] zfcp: Register SCSI devices after fc_remote_port_add (Hendrik Brueckner) [612586]
- [scsi] sg: fix bio leak with a detached device (Matthew Garrett) [619103]
- [powerpc] hash_huge_page: pte_insert failed (Steve Best) [618831]
- [block] md: fix lock ordering problem (Doug Ledford) [616103]
- [fs] sysfs: add attribute to indicate hw address assignment type (Stefan Assmann) [614786]
- [infiniband] ehca: init irq tasklet before irq can happen (Steve Best) [617741]
- [netdrv] iwlwifi: fix scan abort (Stanislaw Gruszka) [619686]
- [powerpc] ONLINE to OFFLINE CPU state transition during removal (Steve Best) [619212]
- [fs] ext4: fix potential NULL dereference while tracing (Eric Sandeen) [619013]
- [infiniband] ehca: Catch failing ioremap() (Steve Best) [617747]
- [netdrv] Add missing read memory barrier to Intel Ethernet device (Steve Best) [617279]
- [netdrv] igb: Fix Tx hangs seen when loading igb with max_vfs > 7 (Stefan Assmann) [617214]
- [pci] Revert "[pci] update bridge resources to get more big ranges in PCI assign unssigned" (Shyam Iyer) [617007]
- [netdrv] cnic: Fix context memory init on 5709 (Stanislaw Gruszka) [616952]
- [virt] vmxnet3: fix network connectivity issues (Andy Gospodarek) [616252]
- [drm] i915: eDP/DP fixes from upstream (Dave Airlie) [615058]
- [ata] ata_piix: fix locking around SIDPR access (David Milburn) [608542]
- [md] Fix md raid partition detection update (Doug Ledford) [607477]
- [netdrv] e1000e: 82577/82578 PHY register access issues (Andy Gospodarek) [592480]
- [s390x] Remove PSF order/suborder check for dasd ioctl (John Feeney) [566183]
- [x86] kernel performance optimization with CONFIG_DEBUG_RODATA (Danny Feng) [557364]
- [netdrv] Revert "[Fedora] [e1000] add quirk for ich9" (Andy Gospodarek) [613196]
- [block] cfq: always return false from should_idle if slice_idle is set to zero (Jeff Moyer) [616904]
- [block] cfq/jbd: Fix fsync performance for small files (Jeff Moyer) [578515]

* Thu Jul 29 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-55.el6]
- [kernel] Add -Werror and WAR for bogus array bounds warnings (Prarit Bhargava) [603733]
- [pci] Remove pci_bus_dump_resources() (Prarit Bhargava) [613972]
- [fs] CIFS: Compile fix for malicious redirect fix (David Howells) [612136] {CVE-2010-2524}

* Tue Jul 27 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-54.el6]
- [block] Disable async multicore raid xor function (Doug Ledford) [596490]
- [kernel] taint: Add mark_hardware_unsupported() (Prarit Bhargava) [600509]
- [kernel] panic: Allow warnings to set different taint flags (Prarit Bhargava) [600509]
- [kernel] taint: Add taint padding and TAINT_HARDWARE_UNSUPPORTED (Prarit Bhargava) [600509]
- [mm] disable transparent hugepages by default on small systems (Rik van Riel) [618444]
- [net] Kernel lockups with bonding and IPV6 (Shyam Iyer) [614240]
- [x86] ACPI: Improve C3 residency (Matthew Garrett) [583792]
- [x86] cpufreq: pcc driver should check for pcch method before calling _OSC (Matthew Garrett) [616908]
- [x86] Add PCC Cpufreq driver (Matthew Garrett) [465354]
- [x86] Disable IOMMU graphics on Cantiga chipset (John Villalovos) [602207]
- [fs] vfsmount: pad for future fanotify support (Eric Paris) [320631]
- [ipmi] Run a dummy command before submitting a new command (Matthew Garrett) [616089]
- [block] mmc: Avoid hangs with mounted SD cards (Matthew Garrett) [615318]
- [md] Fix md raid partition detection (Doug Ledford) [607477]
- [ipmi] Make sure drivers were registered before unregistering them (Matthew Garrett) [601376]
- [s390x] Enhanced qeth for new network device type support (Hendrik Brueckner) [599650]
- [fs] cifs: fix security issue with dns_resolver upcall (David Howells) [612136] {CVE-2010-2524}

* Mon Jul 26 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-53.el6]
- [fs] xfs: track AGs with reclaimable inodes in per-ag radix tree (Dave Chinner) [617035]
- [fs] xfs: convert inode shrinker to per-filesystem contexts (Dave Chinner) [617035]
- [mm] add context argument to shrinker callback (Dave Chinner) [617035]
- [netdrv] enic: bug fix: make the set/get netlink VF_PORT support symmetrical (Andy Gospodarek) [609635]
- [netdrv] enic: Use random mac addr when associating port-profile (Andy Gospodarek) [609635]
- [netdrv] enic: bug fix: sprintf UUID to string as u8 rather than u16 array (Andy Gospodarek) [609635]
- [net] netlink: bug fix: don't overrun skbs on vf_port dump (Andy Gospodarek) [609635]
- [netdrv] enic: Bug Fix: Handle surprise hardware removals (Andy Gospodarek) [609635]
- [netdrv] enic: Bug Fix: Change hardware ingress vlan rewrite mode (Andy Gospodarek) [609635]
- [drm] nouveau: cleanup connector/encoder creation (Ben Skeggs) [612402]
- [drm] nouveau: move LVDS detection back to connector detect() time (Ben Skeggs) [612402]
- [net] add missing header needed for sunrpc tracepoints (Steve Dickson) [567741]
- [drm] nouveau: fix race condition when under memory pressure (Ben Skeggs) [602663]
- [tty] fix tty->pgrp races (Jiri Olsa) [586022] {CVE-2009-4895}
- [scsi] Log msg when getting Unit Attention (Mike Christie) [585432]
- [scsi] be2iscsi: Fix for 64K data (Mike Christie) [608795]
- [cgroups] Fix device cgroup not allowing access to a partition (Vivek Goyal) [589662]
- [audit] fix for audit misreporting return code on amd64 if we had to reschedule (Alexander Viro) [604993]
- [x86] Fix ioremap() so will boot on IA-32 system with PAE (John Feeney) [607029]
- [netdrv] macvtap: Limit packet queue length (Herbert Xu) [614119]
- [virt] vhost: avoid pr_err on condition guest can trigger (Michael S. Tsirkin) [607177]
- [mm] ksmd and khugepaged freezing (Andrea Arcangeli) [617430]
- [pci] Allow read/write access to sysfs I/O port resources (Alex Williamson) [616174]
- [netdrv] improve ipv6 pkt throughput with TSO (John Feeney) [613770]
- [netdrv] ixgbe: use GFP_ATOMIC when allocating FCoE DDP context from the dma pool (Andy Gospodarek) [614243]
- [netdrv] ixgbe: properly toggling netdev feature flags when disabling FCoE (Andy Gospodarek) [614243]
- [scsi] fcoe: remove vlan ID from WWPN (Neil Horman) [611974]
- [fs] xfs: fix corruption case for block size < page size (Dave Chinner) [581432]
- [fs] xfs: unregister inode shrinker before freeing filesystem structures (Dave Chinner) [607750]
- [drm] i915: add 'reclaimable' to i915 self-reclaimable page allocations (Dave Airlie) [616614]
- [drm] i915: fix 945GM stability issues on Lenovo T60 laptops (Dave Airlie) [568780]
- [security] SELinux: check OPEN on truncate calls (Eric Paris) [578841]
- [fs] ext4: Fix buffer dirtying in data=journal mode (Eric Sandeen) [602251]
- [fs] ext3: Fix buffer dirtying in data=journal mode (Eric Sandeen) [602251]

* Tue Jul 20 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-52.el6]
- [virt] Call mask notifiers from pic (Gleb Natapov) [608613]
- [virt] Convert mask notifiers to use irqchip/pin instead of gsi (Gleb Natapov) [608613]
- [virt] Reenter guest after instruction emulation failure if emulation was due to access to non-mmio address (Gleb Natapov) [608595]
- [virt] Return EFAULT from kvm ioctl when guest access bad area (Gleb Natapov) [608595]
- [drm] nouveau: fix dual-link displays when plugged into single-link outputs (Ben Skeggs) [615154]
- [drm] nv50: obey dcb->duallink_possible (Ben Skeggs) [615154]
- [drm] nv50: fix duallink_possible calculation for DCB 4.0 cards (Ben Skeggs) [615154]
- [mm] Rename ramzswap to zram in documentation (Jerome Marchand) [578641]
- [mm] Rename ramzswap to zram in code (Jerome Marchand) [578641]
- [mm] Rename ramzswap files to zram (Jerome Marchand) [578641]
- [mm] ramzswap: Support generic I_O requests (Jerome Marchand) [578641]
- [mm] ramzswap: Handler for swap slot free callback (Jerome Marchand) [578641]
- [mm] swap: Add swap slot free callback to block_device_operations (Jerome Marchand) [578641]
- [mm] swapfile: Add flag to identify block swap devices (Jerome Marchand) [578641]
- [mm] ramzswap: Remove backing swap support (Jerome Marchand) [578641]
- [drm] i915: Output IRQ setup fixes (Adam Jackson) [591709]
- [drm] nouveau: fix oops on chipsets that only have a single crtc (Ben Skeggs) [602290]
- [drm] i915: fix oops on single crtc devices (Dave Airlie) [610002]
- [drm] radeon: check/restore sanity before doing anything else with GPU (Dave Airlie) [612767]
- [fs] jbd2: Fix I/O hang in jbd2_journal_release_jbd_inode (Steve Best) [607254]
- [fs] GFS2: rename causes kernel Oops (Robert S Peterson) [614642]
- [ipmi] Provide kipmid_max_busy_us parameter to cap CPU usage (Shyam Iyer) [609156]
- [kernel] kprobes: "repz ret" causes bad EIP value crash (Dave Anderson) [607215]
- [pci] panic on access to hot-removed device's proc fs (Don Zickus) [612024]
- [pci] don't reassign to ROM res if it is not going to be enabled (Peter Bogdanovic) [612950]
- [x86] i386: Update CPU & Memory Hot Add Not Supported messages (Prarit Bhargava) [600435]
- [x86] nmi: limit hrtimer to lapic or ioapic mode (Don Zickus) [581722]
- [virt] emulator: inc/dec can have lock prefix (Gleb Natapov) [615925]
- [virt] Implement xen_panic_block notifier for RHEL6 Xen guests (Don Dutile) [614476]
- [virt] KVM: MMU: fix conflict access permissions in direct sp (Avi Kivity) [607650]
- [virt] vhost-net: avoid flush under lock (Michael S. Tsirkin) [612421]
- [netdrv] bnx2x: Don't report link down if has been already down (Stanislaw Gruszka) [610311]
- [netdrv] mac80211: improve error checking if WEP fails to init (John Linville) [608704]
- [netdrv] ath9k: cleanup init error path (John Linville) [610224]
- [mm] memcontrol: never oom when charging huge pages (Andrea Arcangeli) [608996]
- [mm] memcontrol: prevent endless loop with huge pages and near-limit group (Andrea Arcangeli) [608996]
- [virt] Xen PV-on-HVM: prevent null chip data ref ptr on newer xen hv (Don Dutile) [523134]
- [virt] Xen PV-on-HVM: modularize platform-pci support (Don Dutile) [523134]
- [virt] HPET: Do not disable hpet if not initialized (Don Dutile) [523134]
- [virt] Xen PV-on-HVM: suspend-resume-support (Don Dutile) [523134]
- [virt] Xen PV-on-HVM: refactor platform-pci, grant-table, enlighten support (Don Dutile) [523134 600360]
- [virt] Xen PV-on-HVM: update evtchn delivery on HVM (Don Dutile) [523134]
- [virt] Xen PV-on-HVM: update hvm_op hypercall & related h files to upstream (Don Dutile) [523134]

* Tue Jul 20 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-51.el6]
- [block] cciss: bump version 3626RH (Tomas Henzl) [609522]
- [block] cciss: cleanup compiletime warnings (Tomas Henzl) [609522]
- [block] cciss: do not reset 640x boards (Tomas Henzl) [609522]
- [block] cciss: fix hard reset (Tomas Henzl) [609522]
- [block] cciss: factor out reset devices code (Tomas Henzl) [609522]
- [block] cciss: factor out cciss find cfg addrs (Tomas Henzl) [609522]
- [block] cciss: factor out cciss wait for mode change ack (Tomas Henzl) [609522]
- [block] cciss: factor out cciss disable dma prefetch on p600 (Tomas Henzl) [609522]
- [block] cciss: factor out cciss enable scsi prefetch (Tomas Henzl) [609522]
- [block] cciss: factor out CISS signature present (Tomas Henzl) [609522]
- [block] cciss: factor out cciss find board params (Tomas Henzl) [609522]
- [block] cciss: factor out cciss find cfgtables (Tomas Henzl) [609522]
- [block] cciss: factor out cciss wait for board ready (Tomas Henzl) [609522]
- [block] cciss: factor out cciss find memory BAR (Tomas Henzl) [609522]
- [block] cciss: remove board-id param from cciss interrupt mode (Tomas Henzl) [609522]
- [block] cciss: factor out cciss_board_disabled (Tomas Henzl) [609522]
- [block] cciss: factor out cciss lookup board id (Tomas Henzl) [609522]
- [block] cciss: save pdev early to avoid passing it around (Tomas Henzl) [609522]
- [audit] dynamically allocate audit_names when not enough space is in the names array (Eric Paris) [586108]
- [mm] mmu notifier index huge spte fix (Andrea Arcangeli) [606131]
- [x86] Update x86 MCE code part 2 (Prarit Bhargava) [580587]
- [kernel] execshield: respect disabled randomization (Roland McGrath) [605516]
- [scsi] mpt2sas: Fix to use sas device list instead of enclosure list (Tomas Henzl) [599049]
- [kernel] disable kmemleak by default for -debug kernels (Jason Baron) [612244]

* Thu Jul 15 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-50.el6]
- [net] CHECKSUM: header export and fixup (Michael S. Tsirkin) [605555]
- [pci] iommu/intel: Disable IOMMU for graphics if BIOS is broken (Adam Jackson) [593516]
- [fs] xfs: remove block number from inode lookup code (Jiri Pirko) [607031]
- [fs] xfs: rename XFS_IGET_BULKSTAT to XFS_IGET_UNTRUSTED (Jiri Pirko) [607031]
- [fs] xfs: validate untrusted inode numbers during lookup (Jiri Pirko) [607031]
- [fs] xfs: always use iget in bulkstat (Jiri Pirko) [607031]
- [igb] avoid platform reset and MCE with DCA (Stefan Assmann) [572732 606687]
- [drm] nouveau: downgrade severity of most init table parser errors (Ben Skeggs) [596679]
- [drm] nouveau: INIT_CONFIGURE_PREINIT/CLK/MEM on newer BIOSes is not an error (Ben Skeggs) [596679]
- [netdrv] enic: Replace LRO with GRO (Andy Gospodarek) [609635]
- [net] decreasing real_num_tx_queues needs to flush qdisc (Andy Gospodarek) [609260]
- [net] sched: qdisc_reset_all_tx is calling qdisc_reset without qdisc_lock (Andy Gospodarek) [609260]
- [fs] inotify: send IN_UNMOUNT events (Eric Paris) [580825]
- [fs] inotify: fix inotify oneshot support (Eric Paris) [614595]
- [s390x] zfcp: Zero memory for gpn_ft and adisc requests (Hendrik Brueckner) [609537]
- [s390x] zfcp: Do not escalate scsi eh after fast_io_fail_tmo fired (Hendrik Brueckner) [606365]
- [s390x] zfcp: Remove SCSI device during unit_remove (Hendrik Brueckner) [589278]
- [scsi] Allow FC LLD to fast-fail scsi eh by introducing new eh return (Hendrik Brueckner) [606365]
- [s390x] zfcp: Do not wait for SBALs on stopped queue (Hendrik Brueckner) [606359]
- [x86] efi: Fill all reserved memmap entries if add_efi_memmap specified (George Beshers) [607386]

* Wed Jul 14 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-49.el6]
- [edac] i7core_edac: Avoid doing multiple probes for the same card (Mauro Carvalho Chehab) [604564]
- [edac] i7core_edac: Properly discover the first QPI device (Mauro Carvalho Chehab) [604564]
- [usb] Disable XHCI (USB 3) HCD module autoloading (Matthew Garrett) [608343]
- [fs] xfs: prevent swapext from operating on write-only files (Jiri Pirko) [605162] {CVE-2010-2226}
- [powerpc] Add symbols to kernel to allow makedumpfile to filter on ppc64 (Neil Horman) [611710]
- [net] netfilter: add CHECKSUM target (Michael S. Tsirkin) [605555]
- [security] audit: dynamically allocate audit_names when not enough space is in the names array (Eric Paris) [586108]
- [pci] iommu/intel: Disable IOMMU for graphics if BIOS is broken (Adam Jackson) [593516]
- [virt] stop vpit before irq_routing freed (Gleb Natapov) [612648]
- [netdrv] Allow for BCM5709S to dump vmcore via NFS (John Feeney) [577809]
- [netdrv] igb: drop support for UDP hashing w/ RSS (Stefan Assmann) [613782]
- [netdrv] mac80211: remove wep dependency (John Linville) [608704]
- [mm] fix swapin race conditions (Andrea Arcangeli) [606131]
- [crypto] authenc: Add EINPROGRESS check (Stanislaw Gruszka) [604611]
- [fs] inotify: don't leak user struct on inotify release (Stanislaw Gruszka) [592399 604611]
- [x86] amd: Check X86_FEATURE_OSVW bit before accessing OSVW MSRs (Stanislaw Gruszka) [604611]
- [kernel] profile: fix stats and data leakage (Stanislaw Gruszka) [604611]
- [sound] ice1724: Fix ESI Maya44 capture source control (Stanislaw Gruszka) [604611]
- [mm] hugetlbfs: kill applications that use MAP_NORESERVE with SIGBUS instead of OOM-killer (Stanislaw Gruszka) [604611]
- [dma] dma-mapping: fix dma_sync_single_range_* (Stanislaw Gruszka) [604611]
- [hwmon] hp_accel: fix race in device removal (Stanislaw Gruszka) [604611]
- [net] ipv4: udp: fix short packet and bad checksum logging (Stanislaw Gruszka) [604611]

* Tue Jul 13 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-48.el6]
- [scsi] SCSI: Retry commands with UNIT_ATTENTION sense codes to fix ext3/ext4 I/O error (Stanislaw Gruszka) [604610]
- [scsi] Enable retries for SYNCRONIZE_CACHE commands to fix I/O error (Stanislaw Gruszka) [604610]
- [scsi] debug: virtual_gb ignores sector_size (Stanislaw Gruszka) [604610]
- [x86] acpi power_meter: acpi_device_class "power_meter_resource" too long (Stanislaw Gruszka) [604610]
- [v4l] budget: Oops: "BUG: unable to handle kernel NULL pointer dereference" (Stanislaw Gruszka) [604610]
- [virt] virtio: initialize earlier (Stanislaw Gruszka) [604610]
- [security] testing the wrong variable in create_by_name() (Stanislaw Gruszka) [604610]
- [netdrv] r8169: more broken register writes workaround (Stanislaw Gruszka) [604610]
- [netdrv] r8169: fix broken register writes (Stanislaw Gruszka) [604610]
- [netdrv] r8169: use correct barrier between cacheable and non-cacheable memory (Stanislaw Gruszka) [604610]
- [kernel] kgdb: don't needlessly skip PAGE_USER test for Fsl booke (Stanislaw Gruszka) [604610]
- [kernel] initramfs: handle unrecognised decompressor when unpacking (Stanislaw Gruszka) [604610]
- [sound] snd-meastro3: Ignore spurious HV interrupts during suspend / resume (Stanislaw Gruszka) [604610]
- [sound] snd-meastro3: Add amp_gpio quirk for Compaq EVO N600C (Stanislaw Gruszka) [604610]
- [x86] Disable large pages on CPUs with Atom erratum AAE44 (Stanislaw Gruszka) [604610]
- [x86] x86-64: Clear a 64-bit FS/GS base on fork if selector is nonzero (Stanislaw Gruszka) [604610]
- [edac] mce: Fix wrong mask and macro usage (Stanislaw Gruszka) [604610]
- [netdrv] p54pci: fix bugs in p54p_check_tx_ring (Stanislaw Gruszka) [604610]
- [netdrv] dm9601: fix phy/eeprom write routine (Stanislaw Gruszka) [604610]
- [block] ensure jiffies wrap is handled correctly in blk_rq_timed_out_timer (Stanislaw Gruszka) [604610]
- [serial] 8250_pnp: add Fujitsu Wacom device (Stanislaw Gruszka) [604610]
- [block] raid6: fix recovery performance regression (Stanislaw Gruszka) [604610]
- [fs] procfs: fix tid fdinfo (Stanislaw Gruszka) [604610]
- [usb] xhci: properly set endpoint context fields for periodic eps (Stanislaw Gruszka) [604610]
- [usb] xhci: properly set the "Mult" field of the endpoint context (Stanislaw Gruszka) [604610]
- [usb] OHCI: don't look at the root hub to get the number of ports (Stanislaw Gruszka) [604610]
- [usb] don't choose configs with no interfaces (Stanislaw Gruszka) [604610]
- [usb] fix testing the wrong variable in fs_create_by_name() (Stanislaw Gruszka) [604610]
- [usb] Add id for HP ev2210 a.k.a Sierra MC5725 miniPCI-e Cell Modem (Stanislaw Gruszka) [604610]
- [usb] fix remote wakeup settings during system sleep (Stanislaw Gruszka) [604610]
- [mm] hugetlb: fix infinite loop in get_futex_key() when backed by huge pages (Stanislaw Gruszka) [604610]
- [kernel] flex_array: fix the panic when calling flex_array_alloc() without __GFP_ZERO (Stanislaw Gruszka) [604610]
- [netdrv] mac80211: remove bogus TX agg state assignment (Stanislaw Gruszka) [604610]
- [ata] libata: fix locking around blk_abort_request() (Stanislaw Gruszka) [604610]
- [netdrv] p54usb: Add usbid for Corega CG-WLUSB2GT (Stanislaw Gruszka) [604610]
- [usb] EHCI: defer reclamation of siTDs (Stanislaw Gruszka) [604610]
- [drm] nouveau: initialise display before enabling interrupts (Ben Skeggs) [596703]
- [drm] nv50: fix DP->DVI if output has been programmed for native DP previously (Ben Skeggs) [596703]
- [block] dm ioctl: return uevent flag after rename (Mike Snitzer) [609591]
- [block] dm ioctl: make __dev_status return void (Mike Snitzer) [609591]
- [block] dm ioctl: remove __dev_status from geometry and target message (Mike Snitzer) [609591]
- [infiniband] mlx4: enable IBoE feature (Doug Ledford) [529397]
- [dm] dm-replicator: Fix replicator_ctr() error path (Heinz Mauelshagen) [612743]
- [virt] vmware: disable NMI watchdog in guest (Don Zickus) [612321]
- [virt] KVM: Expose MCE control MSRs to userspace (Avi Kivity) [558416]

* Mon Jul 12 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-47.el6]
- [x86] eeepc-laptop: disable cpu speed control on EeePC 701 (Stanislaw Gruszka) [604608]
- [x86] gart: Disable GART explicitly before initialization (Stanislaw Gruszka) [604608]
- [netdrv] r8169: clean up my printk uglyness (Stanislaw Gruszka) [604608]
- [input] wacom: switch mode upon system resume (Stanislaw Gruszka) [604608]
- [fs] eCryptfs: Decrypt symlink target for stat size (Stanislaw Gruszka) [604608]
- [usb] cdc-acm: Update to new autopm API (Stanislaw Gruszka) [604608]
- [netdrv] e1000e: stop cleaning when we reach tx_ring->next_to_use (Stanislaw Gruszka) [604608]
- [kernel] sched: Fix a race between ttwu() and migrate_task() (Stanislaw Gruszka) [604608]
- [fs] ecryptfs: fix error code for missing xattrs in lower fs (Stanislaw Gruszka) [604608]
- [pci] fix nested spinlock hang in aer_inject (Stanislaw Gruszka) [604608]
- [fs] ecryptfs: fix use with tmpfs by removing d_drop from ecryptfs_destroy_inode (Stanislaw Gruszka) [604608]
- [scsi] add scsi target reset support to scsi ioctl (Stanislaw Gruszka) [604608]
- [pci] PCIe AER: prevent AER injection if hardware masks error reporting (Stanislaw Gruszka) [604608]
- [fs] quota: Fix possible dq_flags corruption (Stanislaw Gruszka) [604608]
- [fs] fix NFS4 handling of mountpoint stat (Stanislaw Gruszka) [604608]
- [agp] intel-agp: Switch to wbinvd_on_all_cpus (Stanislaw Gruszka) [604608]
- [drm] radeon/kms: add FireMV 2400 PCI ID (Stanislaw Gruszka) [604608]
- [x86] amd-iommu: Use helper function to destroy domain (Stanislaw Gruszka) [604608]
- [hwmon] sht15: Fix sht15_calc_temp interpolation function (Stanislaw Gruszka) [604608]
- [hwmon] sht15: Properly handle the case CONFIG_REGULATOR=n (Stanislaw Gruszka) [604608]
- [ata] libata: disable NCQ on Crucial C300 SSD (Stanislaw Gruszka) [604608]
- [x86] thinkpad-acpi: lock down video output state access (Stanislaw Gruszka) [604608]
- [x86] thinkpad-acpi: convert to seq_file (Stanislaw Gruszka) [604608]
- [sound] usb: Fix Oops after usb-midi disconnection (Stanislaw Gruszka) [604608]
- [x86] thinkpad-acpi: log initial state of rfkill switches (Stanislaw Gruszka) [604608]
- [x86] thinkpad-acpi: use input_set_capability (Stanislaw Gruszka) [604608]
- [x86] thinkpad-acpi: expose module parameters (Stanislaw Gruszka) [604608]
- [fs] ext3: Don't update the superblock in ext3_statfs() (Stanislaw Gruszka) [604608]
- [x86] thinkpad-acpi: log temperatures on termal alarm (Stanislaw Gruszka) [604608]
- [x86] thinkpad-acpi: adopt input device (Stanislaw Gruszka) [604608]
- [x86] thinkpad-acpi: issue backlight class events (Stanislaw Gruszka) [604608]
- [x86] thinkpad-acpi: silence bogus complain during rmmod (Stanislaw Gruszka) [604608]
- [x86] thinkpad-acpi: fix some version quirks (Stanislaw Gruszka) [604608]
- [kernel] resource: move kernel function inside __KERNEL__ (Stanislaw Gruszka) [604608]
- [fs] ext3: journal all modifications in ext3_xattr_set_handle (Stanislaw Gruszka) [604608]
- [video] backlight: mbp_nvidia_bl - add five more MacBook variants (Stanislaw Gruszka) [604608]
- [sound] mixart: range checking proc file (Stanislaw Gruszka) [604608]
- [hid] fix oops in gyration_event() (Stanislaw Gruszka) [604608]
- [ata] pata_ali: Fix regression with old devices (Stanislaw Gruszka) [604608]
- [hwmon] lis3: fix show rate for 8 bits chips (Stanislaw Gruszka) [604608]
- [cgroup] freezer: Fix buggy resume test for tasks frozen with cgroup freezer (Stanislaw Gruszka) [604608]
- [kernel] genirq: Force MSI irq handlers to run with interrupts disabled (Stanislaw Gruszka) [604608]
- [fs] fat: fix buffer overflow in vfat_create_shortname() (Stanislaw Gruszka) [604608]
- [netdrv] mlx4: add dynamic LRO disable support (Amerigo Wang) [584359]
- [netdrv] s2io: add dynamic LRO disable support (Amerigo Wang) [584359]
- [drm] nv50: rewrite display irq handler (Ben Skeggs) [598842]
- [drm] nv50: send evo "update" command after each disconnect (Ben Skeggs) [598842]
- [drm] nv50: when debugging on, log which crtc we connect an encoder to (Ben Skeggs) [598842]
- [drm] nv50: supply encoder disable() hook (Ben Skeggs) [598842]
- [drm] disable encoder rather than dpms off in drm_crtc_prepare_encoders() (Ben Skeggs) [598842]
- [drm] nv50: DCB quirk for Dell M6300 (Ben Skeggs) [598842]
- [fs] writeback: limit write_cache_pages integrity scanning to current EOF (Dave Chinner) [602490]
- [fs] xfs: remove nr_to_write writeback windup. (Dave Chinner) [602490]
- [fs] writeback: pay attention to wbc->nr_to_write in write_cache_pages (Eric Sandeen) [602490]

* Mon Jul 12 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-46.el6]
- [fs] ext4: stop issuing discards if not supported by device (Eric Sandeen) [608731]
- [block] dm: only initialize full request_queue for request-based device (Mike Snitzer) [595393]
- [block] dm: prevent table type changes after initial table load (Mike Snitzer) [595393]
- [dm] skip second flush if request unsupported (Mike Snitzer) [612014]
- [dm] only ignore -EOPNOTSUPP for empty barrier requests (Mike Snitzer) [612014]
- [dm] snapshot: implement a merge method for snapshot origin (Mike Snitzer) [612375]
- [dm] snapshot: test chunk size against both origin and snapshot sector size (Mike Snitzer) [612375]
- [dm] snapshot: open origin before exception store initialization (Mike Snitzer) [612375]
- [dm] snapshot: iterate both the origin and snapshot devices (Mike Snitzer) [612375]
- [block] dm: support discard if at least one underlying device supports it (Mike Snitzer) [612014]
- [block] dm: support discard for multiple devices (Mike Snitzer) [612014]
- [block] dm: clear the discard flag if the device loses discard capability (Mike Snitzer) [612014]
- [block] dm: check that target supports discard just before submitting request (Mike Snitzer) [612014]
- [scsi] convert discard to REQ_TYPE_FS instead of REQ_TYPE_BLOCK_PC (Mike Snitzer) [610054]
- [scsi] fix leak in scsi_setup_discard_cmnd error path (Mike Snitzer) [610054]
- [scsi] remove unused free discard page in sd_done (Mike Snitzer) [610054]
- [scsi] add sd_unprep_fn to free discard page (Mike Snitzer) [610054]
- [block] implement an unprep function corresponding directly to prep (Mike Snitzer) [610054]
- [block] don't allocate a payload for discard request (Mike Snitzer) [610054]
- [fs] ext4: move aio completion after unwritten extent conversion (Christoph Hellwig) [589985]
- [fs] xfs: move aio completion after unwritten extent conversion (Christoph Hellwig) [589985]
- [fs] direct-io: move aio_complete into ->end_io (Christoph Hellwig) [589985]
- [drm] radeon/kms/igp: fix possible divide by 0 in bandwidth code (Dave Airlie) [609755]
- [drm] nouveau: disable acceleration on NVA3/NVA5/NVA8 by default (Ben Skeggs) [591062]
- [drm] vt/fbcon: try harder to print output when panicing (Dave Airlie) [579002]
- [fs] GFS2: fix BUG in gfs2_adjust_quota (Abhijith Das) [603827]
- [fs] nfsd: nfsd_setattr needs to call commit_metadata (Christoph Hellwig) [593652]
- [net] netfilter: remove config option NF_CT_ACCT completely (Jiri Pirko) [578476]
- [net] Revert "[net] bonding: make bonding support netpoll" (Andy Gospodarek) [604672]
- [scsi] stex: fix inconsistent usage of max_lun (David Milburn) [593255]
- [kernel] sched: Kill migration thread in CPU_POST_DEAD event in migration_call, instead of CPU_DEAD (Steve Best) [604846]
- [tracing] ftrace: fix function_graph livelock under kvm (Jason Baron) [596653]
- [block] dm: mpath fix NULL pointer dereference when path parameters missing (Mike Snitzer) [607242]
- [dm] dm-replicator: mandatory API change for replicator_resume(), replicator_dev_resume() and reference count fix calling dm_table_get_md() (Heinz Mauelshagen) [594922]
- [x86] AMD IOMMU: change default to passthrough mode (Bhavna Sarathy) [607631]
- [x86] dell-laptop: Add another Dell laptop family to the DMI whitelist (Matthew Garrett) [609268]
- [netdrv] cnic: fix bnx2x panics with multiple interfaces enabled (Stanislaw Gruszka) [609184]
- [mm] fix khugepaged startup race (Andrea Arcangeli) [612217]
- [mm] add robustness to pmd_same checks (Andrea Arcangeli) [607650]
- [mm] Fix vmalloc slow down (Steven Whitehouse) [583026]

* Mon Jul 12 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-45.el6]
- [drm] i915: fix display setup bugs + hibernate (Dave Airlie) [608515 609763]
- [fs] NFSv4: Fix an embarassing typo in encode_attrs() (Steve Dickson) [560786]
- [fs] NFSv4: Ensure that /proc/self/mountinfo displays the minor version number (Steve Dickson) [560786]
- [fs] NFSv4.1: Ensure that we initialise the session when following a referral (Steve Dickson) [560786]
- [fs] SUNRPC: Fix a re-entrancy bug in xs_tcp_read_calldir() (Steve Dickson) [560786]
- [fs] nfs4: use mandatory attribute file type in nfs4_get_root (Steve Dickson) [560786]
- [x86] UV: uv_irq.c: Fix all sparse warnings (George Beshers) [573095]
- [x86] uv: Remove recursion in uv_heartbeat_enable() (George Beshers) [573095]
- [x86] pat: Update the page flags for memtype atomically instead of using memtype_lock (George Beshers) [573095]
- [x86] UV: Improve BAU performance and error recovery (George Beshers) [573095]
- [mm] ksm.c: remove an unneeded _notify in write_protect_page (George Beshers) [573095]
- [x86] UV: Delete unneeded boot messages (George Beshers) [573095]
- [x86] UV: Fix target_cpus() in x2apic_uv_x.c (George Beshers) [573095]
- [x86] UV: Clean up UV headers for MMR definitions (George Beshers) [573095]
- [x86] Enable NMI on all cpus on UV (George Beshers) [573095]
- [x86] uv: Add serial number parameter to uv_bios_get_sn_info() (George Beshers) [573095]
- [virt] xen: sync upstream xen_init_cpuid_mask (Andrew Jones) [609028]
- [virt] xen: disable gbpages on pv guests (Andrew Jones) [609028]
- [virt] KVM: Fix mov cr3 #GP at wrong instruction (Marcelo Tosatti) [611889]
- [virt] KVM: Fix mov cr4 #GP at wrong instruction (Marcelo Tosatti) [611889]
- [virt] KVM: Fix mov cr0 #GP at wrong instruction (Marcelo Tosatti) [611889]
- [virt] KVM: Add missing srcu_read_lock() for kvm_mmu_notifier_release() (Marcelo Tosatti) [601320]
- [virt] KVM: limit the number of pages per memory slot (Marcelo Tosatti) [601318]
- [virt] KVM: MMU: Remove user access when allowing kernel access to gpte.w=0 page (Marcelo Tosatti) [601316]
- [virt] KVM: x86: Add missing locking to arch specific vcpu ioctls (Marcelo Tosatti) [601313]
- [virt] KVM: MMU: remove rmap before clear spte (Marcelo Tosatti) [601311]
- [virt] KVM: MMU: Segregate shadow pages with different cr0.wp (Marcelo Tosatti) [601308]
- [virt] KVM: x86: Check LMA bit before set_efer (Marcelo Tosatti) [601307]
- [virt] KVM: Dont allow lmsw to clear cr0.pe (Marcelo Tosatti) [601305]
- [virt] KVM: VMX: blocked-by-sti must not defer NMI injections (Marcelo Tosatti) [601304]
- [virt] KVM: x86: Call vcpu_load and vcpu_put in cpuid_update (Marcelo Tosatti) [601303]
- [virt] KVM: x86: Inject #GP with the right rip on efer writes (Marcelo Tosatti) [601301]
- [virt] KVM: MMU: Dont read pdptrs with mmu spinlock held in mmu_alloc_roots (Marcelo Tosatti) [601300]
- [virt] KVM: x86: properly update ready_for_interrupt_injection (Marcelo Tosatti) [601298]
- [virt] KVM: VMX: enable VMXON check with SMX enabled (Marcelo Tosatti) [601297]
- [virt] KVM: VMX: free vpid when fail to create vcpu (Marcelo Tosatti) [601292]
- [virt] vhost: add unlikely annotations to error path (Michael S. Tsirkin) [602607]
- [virt] vhost: break out of polling loop on error (Michael S. Tsirkin) [602607]

* Wed Jul 07 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-44.el6]
- [mm] Prevent soft lockup - CPU#0 stuck for 61s! in kswapd0 (Larry Woodman) [596971]

* Tue Jul 06 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-43.el6]
- [x86] properly account for IRQ injected only into BSP (Gleb Natapov) [609082]

* Wed Jun 30 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-42.el6]
- [block] writeback: simplify the write back thread queue (Christoph Hellwig) [602595]

* Tue Jun 29 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-41.el6]
- [mm] Fix slabcache corruption (Larry Woodman) [602595]

* Tue Jun 29 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-40.el6]
- [infiniband] Add IBoE support (Doug Ledford) [571959]
- [scsi] hpsa: don't pretend the reset works (Tomas Henzl) [598681]
- [fs] revert "procfs: provide stack information for threads" and its fixup commits (George Beshers) [573095]
- [x86] mce: Fix MSR_IA32_MCI_CTL2 CMCI threshold setup (John Villalovos) [593558]
- [s390x] cio: use exception-save stsch (Hendrik Brueckner) [596333]
- [s390x] cio: add hook to reenable mss after hibernation (Hendrik Brueckner) [596333]
- [s390x] cio: allow enable_facility from outside init functions (Hendrik Brueckner) [596333]
- [x86] wmi: Free the allocated acpi objects through wmi_get_event_data (Stanislaw Gruszka) [606736]
- [mtd] UBI: fix volume creation input checking (Stanislaw Gruszka) [606736]
- [mm] avoid THP expose VM bugs (Andrea Arcangeli) [606131]
- [dm] discard support for the linear target (Mike Snitzer) [608280]
- [block] fix DISCARD_BARRIER requests (Mike Snitzer) [608280]
- [block] Don't count_vm_events for discard bio in submit_bio (Mike Snitzer) [608280]

* Tue Jun 29 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-39.el6]
- [x86] disable PentiumPro memory ordering errata workaround (Gleb Natapov) [605745 606054]
- [net] Bluetooth: Keep a copy of each HID device's report descriptor (Mauro Carvalho Chehab) [565583]
- [hid] make Wacom modesetting failures non-fatal (Mauro Carvalho Chehab) [565583]
- [hid] Implement Wacom quirk in the kernel (Mauro Carvalho Chehab) [565583]
- [hid] make raw reports possible for both feature and output reports (Mauro Carvalho Chehab) [565583]
- [kernel] resources: fix call to alignf() in allocate_resource() (Peter Bogdanovic) [587729]
- [kernel] resources: when allocate_resource() fails, leave resource untouched (Peter Bogdanovic) [587729]
- [pci] introduce pci_assign_unassigned_bridge_resources (Peter Bogdanovic) [587729]
- [pci] update bridge resources to get more big ranges in PCI assign unssigned (Peter Bogdanovic) [587729]
- [pci] add failed_list to pci_bus_assign_resources (Peter Bogdanovic) [587729]
- [pci] add pci_bridge_release_resources and pci_bus_release_bridge_resources (Peter Bogdanovic) [587729]
- [kernel] resource: add release_child_resources (Peter Bogdanovic) [587729]
- [pci] separate pci_setup_bridge to small functions (Peter Bogdanovic) [587729]
- [scsi] aacraid: Disable ASPM by default (Matthew Garrett) [599735]
- [pci] Don't enable aspm before drivers have had a chance to veto it (Matthew Garrett) [599735]
- [netdrv] ehea: Fix kernel deadlock in DLPAR-mem processing (Steve Best) [605736]
- [netdrv] ehea: fix delayed packet processing (Steve Best) [605738]
- [netdrv] ehea: fix possible DLPAR/mem deadlock (Steve Best) [600516]
- [netdrv] ehea: error handling improvement (Steve Best) [600516]
- [x86] Fall back to GART if initialization fails (Bhavna Sarathy) [598974]
- [x86] AMD IOMMU memory region fail with buggy BIOS (Bhavna Sarathy) [598974]
- [virt] Search the LAPIC's for one that will accept a PIC interrupt (Christopher Lalancette) [596223]
- [virt] KVM: x86: Kick VCPU outside PIC lock again (Christopher Lalancette) [596223]
- [virt] KVM: x86: In DM_LOWEST, only deliver interrupts to vcpus with enabled LAPIC's (Christopher Lalancette) [596223]
- [virt] KVM: x86: Allow any LAPIC to accept PIC interrupts (Christopher Lalancette) [596223]
- [virt] KVM: x86: Introduce a workqueue to deliver PIT timer interrupts (Christopher Lalancette) [596223]
- [scsi] ibmvfc: Reduce error recovery timeout (Steve Best) [605729]
- [scsi] ibmvfc: Fix command completion handling (Steve Best) [605729]
- [powerpc] Enable asymmetric SMT scheduling on POWER7 (Steve Best) [596304]
- [kernel] sched: Add asymmetric group packing option for sibling domain (Steve Best) [596304]
- [kernel] sched: Fix capacity calculations for SMT4 (Steve Best) [596304]
- [fs] Btrfs: update to latest upstream code (Josef Bacik) [593834]
- [fs] direct-io: do not merge logically non-contiguous requests (Josef Bacik) [593834]
- [fs] direct-io: add a hook for the fs to provide its own submit_bio function (Josef Bacik) [593834]
- [fs] allow short direct-io reads to be completed via buffered IO (Josef Bacik) [593834]
- [fs] GFS2: O_TRUNC not working on stuffed files across cluster (Robert S Peterson) [606428]
- [nfs] nfsd4: shut down callback queue outside state lock (Jeff Layton) [599522]
- [security] IMA: policy handling and general cleanups (Eric Paris) [584901]
- [security] IMA: fix object lifetime to support non ext* FS (Eric Paris) [584901]
- [netdrv] be2net: Include latest fixes from upstream (Ivan Vecera) [604729]
- [netdrv] be2net: Add PCI SR-IOV support (Ivan Vecera) [602451]
- [scsi] hpsa: do not allow hard reset of 640x-boards (Tomas Henzl) [598681]
- [scsi] hpsa: fix hard reset (Tomas Henzl) [598681]
- [scsi] hpsa: reset devices code (Tomas Henzl) [598681]
- [scsi] hpsa: find cfg addrs (Tomas Henzl) [598681]
- [scsi] hpsa: finding the memory BAR (Tomas Henzl) [598681]
- [scsi] hpsa: look up the board id (Tomas Henzl) [598681]
- [x86] uv: uv_global_gru_mmr_address() macro fix (George Beshers) [607696]
- [crypto] vmac: make it work on big-endian (Jarod Wilson) [605688]
- [net] ipvs: One-Packet Scheduler (Thomas Graf) [584336]
- [drm] i915: Disable Sandybridge support for 6.0 (Adam Jackson) [604838 605302]
- [netdrv] vxge: fix memory leak in vxge_alloc_msix() error path (Michal Schmidt) [580392]
- [netdrv] vxge: fix SINGLE/MULTI_FUNCTION definitions (Michal Schmidt) [580392]
- [netdrv] vxge: update to 2.0.8.20182-k (Michal Schmidt) [580392]
- [sound] fix PCM ring buffer issues (Jaroslav Kysela) [574844 590159 600311]
- [netdrv] e1000/e1000e: implement a simple interrupt moderation (Andy Gospodarek) [607283]
- [netdrv] e1000e: add PCI device id to enable support for 82567V-4 (Andy Gospodarek) [607264]
- [netdrv] e1000e: update driver version number (Andy Gospodarek) [582803]
- [netdrv] e1000e: enable support for EEE on 82579 (Andy Gospodarek) [582803]
- [netdrv] e1000e: initial support for 82579 LOMs (Andy Gospodarek) [582803]
- [netdrv] e1000e: move settting of flow control refresh timer to link setup code (Andy Gospodarek) [582803]
- [netdrv] e1000e: Fix/cleanup PHY reset code for ICHx/PCHx (Andy Gospodarek) [582803]
- [netdrv] e1000e: fix check for manageability on ICHx/PCH (Andy Gospodarek) [582803]
- [netdrv] e1000e: separate out PHY statistics register updates (Andy Gospodarek) [582803]
- [netdrv] e1000e: more cleanup e1000_sw_lcd_config_ich8lan() (Andy Gospodarek) [582803]
- [netdrv] e1000e: cleanup e1000_sw_lcd_config_ich8lan() (Andy Gospodarek) [582803]
- [netdrv] e1000e: cleanup ethtool loopback setup code (Andy Gospodarek) [582803]
- [netdrv] e1000e: reset MAC-PHY interconnect on 82577/82578 (Andy Gospodarek) [582803]
- [netdrv] e1000e: Incorrect function pointer set for force_speed_duplex on 82577 (Andy Gospodarek) [598570]
- [netdrv] e1000e: Reset 82577/82578 PHY before first PHY register read (Andy Gospodarek) [598570]
- [fs] GFS2: Fix kernel NULL pointer dereference by dlm_astd (Robert S Peterson) [604244]
- [fs] GFS2: recovery stuck on transaction lock (Robert S Peterson) [590878]
- [netdrv] tg3: Include support for 5719 device (John Feeney) [595511]
- [mm] Do not attempt to allocate memory below mmap_min_addr (Eric Paris) [540333]
- [scsi] qla2xxx: Updated driver version to 8.03.01.05.06.0-k8 (Chad Dupuis) [595477]
- [scsi] qla2xxx: Add portid to async-request messages (Chad Dupuis) [595477]
- [scsi] qla2xxx: Propogate transport disrupted status for cable pull conditions for faster failover (Chad Dupuis) [595477]
- [scsi] qla2xxx: Do not restrict flash operations to specific regions for 4G adapters (Chad Dupuis) [595477]
- [scsi] qla2xxx: For ISP 23xx, select user specified login timeout value if greater than minuimum value(4 secs) (Chad Dupuis) [595477]
- [scsi] qla2xxx: Removed redundant check for ISP 84xx (Chad Dupuis) [595477]
- [scsi] qla2xxx: Do not enable VP in non fabric topology (Chad Dupuis) [595477]
- [scsi] qla2xxx: Make the FC port capability mutual exclusive (Chad Dupuis) [595477]
- [scsi] qla2xxx: Limit rport-flaps during link-disruptions (Chad Dupuis) [595477]
- [scsi] qla2xxx: Correct async-srb issues (Chad Dupuis) [595477]
- [scsi] qla2xxx: Correct use-after-free oops seen during EH-abort (Chad Dupuis) [595477]
- [scsi] qla2xxx: Fix cpu-affinity usage for non-capable ISPs (Chad Dupuis) [595477]
- [scsi] qla2xxx: Limit mailbox command contention for ADISC requests (Chad Dupuis) [595477]
- [scsi] qla2xxx: Further generalization of SRB CTX infrastructure (Chad Dupuis) [595477]
- [scsi] qla2xxx: ensure flash operation and host reset via sg_reset are mutually exclusive (Chad Dupuis) [595477]
- [scsi] qla2xxx: Prevent sending mbx commands from sysfs during isp reset (Chad Dupuis) [595477]
- [scsi] qla2xxx: Cleanup FCP-command-status processing debug statements (Chad Dupuis) [595477]
- [scsi] qla2xxx: Clear error status after uncorrectable non-fatal errors (Chad Dupuis) [595477]
- [scsi] qla2xxx: Add char device to incease driver use count (Chad Dupuis) [595477]
- [scsi] qla2xxx: Display proper link state for disconnected ports (Chad Dupuis) [595477]
- [scsi] qla2xxx: Check for ISP84xx before processing to get 84xx firmware version (Chad Dupuis) [595477]

* Fri Jun 25 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-38.el6]
- [ata] ahci: Fix failure to detect devices (Matthew Garrett) [608146]
- [ata] ahci: Fix device detection when stopping DMA engines (Matthew Garrett) [601195]
- [mm] Disable transparent hugepages when running under Xen (Andrea Arcangeli) [605566]
- [netdrv] tg3: Fix TX BD corruption on 5755+ devices (John Feeney) [603936]
- [netdrv] tg3: Fix memory leak on 5717/57765/5719 devices (John Feeney) [603933]
- [netdrv] bnx2: update firmware to 09-5.0.0.j15 to improve performance (John Feeney) [593797]
- [netdrv] iwlwifi: cancel scan watchdog in iwl_bg_abort_scan (John Linville) [604266]
- [netdrv] add bnx2_del_napi() to stop rmmod hangs (John Feeney) [599630]
- [virt] virtio: net: Remove net-specific advertising of PUBLISH_USED feature (Amit Shah) [605591]
- [virt] KVM: Increase NR_IOBUS_DEVS limit to 200 (Michael S. Tsirkin) [602262]
- [virt] account only for IRQ injected into BSP (Gleb Natapov) [601564]
- [virt] KVM: read apic->irr with ioapic lock held (Marcelo Tosatti) [579970]
- [x86] ACPI: Disable ASPM if the platform won't provide _OSC control for PCIe (Matthew Garrett) [584466]
- [x86] Move notify_cpu_starting() callback to a later stage (Prarit Bhargava) [600296]
- [x86] cpuidle: Fix incorrect optimization (John Villalovos) [593549]
- [block] cfq: Don't allow queue merges for queues that have no process references (Jeff Moyer) [605264]
- [infiniband] ehca: bitmask handling for lock_hcalls (Steve Best) [605739]
- [tpm] Fix tpm_readpubek_params_out struct (Peter Bogdanovic) [597235]
- [usb] Fix a hang of khubd if UHCI is removed (Pete Zaitcev) [579093]
- [oprofile] fix oprofile samples dropping under load on larger systems (John Villalovos) [561557]
- [kernel] check SEND_SIG_FORCED on TP_STORE_SIGINFO() (Oleg Nesterov) [591780]
- [kernel] pids: increase pid_max based on num_possible_cpus (Oleg Nesterov) [593164]
- [kernel] sys_personality: change sys_personality() to accept "unsigned int" instead of u_long (Oleg Nesterov) [593265]
- [kernel] fix cgroup's cpu controller to provide fair CPU usage to each group in some conditions (Larry Woodman) [544197]
- [gpu] vgaarb: fix incorrect dereference of userspace pointer (Danny Feng) [564247]
- [kernel] sched: avoid cache misses on large machines due to sibling preference (Jerome Marchand) [592302]
- [scsi] ipr: move setting of the allow_restart flag for vsets (Steve Best) [603090]
- [scsi] ibmvscsi: fix DMA API misuse (Steve Best) [595417]
- [netdrv] l2tp: Fix oops in pppol2tp_xmit (Danny Feng) [607055]
- [net] sysfs: ethtool_ops can be NULL (Danny Feng) [603662]
- [net] udp: Fix bogus UFO packet generation (Herbert Xu) [602878]
- [net] vlan: fix vlan_skb_recv() (Michael S. Tsirkin) [598920]
- [net] bonding: Fix fcoe mpio over inactive slave in a bond (Neil Horman) [603239]
- [net] bridge: Fix OOM crash in deliver_clone (Herbert Xu) [604494]
- [s390x] kernel: fix kernel panic caused by using kprobes (Hendrik Brueckner) [596876]
- [s390x] ccwgroup: add locking around drvdata access (Hendrik Brueckner) [598563]
- [s390x] cmm: fix module unload handling (Hendrik Brueckner) [598554]
- [powerpc] Rework VDSO gettimeofday to prevent time going backwards (Steve Best) [591495]
- [powerpc] Move kdump default base address to 64MB on 64bit (Steve Best) [603779]
- [fs] gfs2: Better error reporting when mounting a gfs fs without enough journals (Abhijith Das) [600408]
- [tty] Revert "[tty] fix race in tty_fasync" (Stanislaw Gruszka) [606747]
- [kdump] kexec: fix OOPS in crash_kernel_shrink (Steve Best) [592336]
- [fs] btrfs: prevent users from setting ACLs on files they do not own (Danny Feng) [603594] {CVE-2010-2071}
- [fs] cifs: remove bogus first_time check in NTLMv2 session setup code (Jeff Layton) [604785]
- [fs] cifs: don't attempt busy-file rename unless it's in same directory (Jeff Layton) [603707]
- [fs] ext4: Fix compat EXT4_IOC_ADD_GROUP (Eric Sandeen) [602428]
- [fs] ext4: Prevent creation of files larger than RLIMIT_FSIZE using fallocate (Eric Sandeen) [602427]
- [fs] ext4: Use our own write_cache_pages() (Eric Sandeen) [602384]
- [fs] xfs: Make fiemap work in query mode (Eric Sandeen) [602061]
- [fs] ext4: restart ext4_ext_remove_space() after transaction restart (Josef Bacik) [589645]
- [fs] ext4: Make sure the MOVE_EXT ioctl can't overwrite append-only files (Eric Sandeen) [601009] {CVE-2010-2066}
- [fs] btrfs: check for read permission on src file in the clone ioctl (Danny Feng) [593227] {CVE-2010-1636}
- [drm] radeon: fixes for radeon driver from upstream (Dave Airlie) [589098]
- [drm] radeon port 2.6.35 HDMI audio to RHEL6 (Jerome Glisse) [604435]
- [drm] nv50: fix iommu errors caused by device reading from address 0 (Ben Skeggs) [602498]
- [ata] libata: don't flush dcache on slab pages (Stanislaw Gruszka) [606719]
- [fs] cifs: don't call cifs_new_fileinfo unless cifs_open succeeds (Jeff Layton) [593422]
- [fs] cifs: don't ignore cifs_posix_open_inode_helper return value (Jeff Layton) [593422]
- [fs] cifs: clean up arguments to cifs_open_inode_helper (Jeff Layton) [593422]
- [fs] cifs: pass instantiated filp back after open call (Jeff Layton) [593422]
- [fs] cifs: move cifs_new_fileinfo call out of cifs_posix_open (Jeff Layton) [593422]
- [fs] cifs: implement drop_inode superblock op (Jeff Layton) [593422]
- [fs] cifs: checkpatch cleanup (Jeff Layton) [593422]
- [fs] nfsd: ensure sockets are closed on error (Jeff Layton) [603735]
- [fs] Revert "sunrpc: move the close processing after do recvfrom method" (Jeff Layton) [603735]
- [fs] Revert "sunrpc: fix peername failed on closed listener" (Jeff Layton) [603735]
- [virt] kvm: Prevent internal slots from being COWed (Glauber Costa) [601192]
- [virt] kvm: Keep slot ID in memory slot structure (Glauber Costa) [601192]
- [fs] writeback: split writeback_inodes_wb (Christoph Hellwig) [601202]
- [fs] writeback: remove writeback_inodes_wbc (Christoph Hellwig) [601202]
- [fs] writeback: fix pin_sb_for_writeback (Christoph Hellwig) [601202]
- [fs] writeback: add missing requeue_io in writeback_inodes_wb (Christoph Hellwig) [601202]
- [fs] writeback: simplify and split bdi_start_writeback (Christoph Hellwig) [601202]
- [fs] writeback: simplify wakeup_flusher_threads (Christoph Hellwig) [601202]
- [fs] writeback: fix writeback_inodes_wb from writeback_inodes_sb (Christoph Hellwig) [601202]
- [fs] writeback: enforce s_umount locking in writeback_inodes_sb (Christoph Hellwig) [601202]
- [fs] writeback: queue work on stack in writeback_inodes_sb (Christoph Hellwig) [601202]
- [fs] writeback: fix writeback completion notifications (Christoph Hellwig) [601202]
- [fs] vfs: improve writeback_inodes_wb() (Christoph Hellwig) [601202]
- [fs] writeback: remove unused nonblocking and congestion checks (Christoph Hellwig) [601202]
- [fs] writeback: remove the always false bdi_cap_writeback_dirty() test (Christoph Hellwig) [601202]
- [misc] hpilo: fix pointer warning in ilo_ccb_setup (Prarit Bhargava) [603733]
- [netdrv] libertas_tf: Fix warning in lbtf_rx for stats struct (Prarit Bhargava) [603733]
- [scsi] Fix userspace warning in /usr/include/scsi/scsi.h (Prarit Bhargava) [603733]
- [pci] Fix section mismatch warning in pcibios_scan_specific_bus() (Prarit Bhargava) [603733]
- [fs] Fix warning in fs/ecryptfs/messaging.c: ecryptfs_process_response() (Prarit Bhargava) [603733]
- [fs] Fix warning in fs/btrfs/ordered-data.c: btrfs_dec_test_ordered_pending() (Prarit Bhargava) [603733]
- [netdrv] Fix warnings in drivers/net/bnx2.c (Prarit Bhargava) [603733]
- [doc] Fix warning in Documentation/spi/spidev_fdx.c: do_msg() (Prarit Bhargava) [603733]
- [kernel] Fix stack warning in lib/decompress_bunzip2.c: get_next_block() (Prarit Bhargava) [603733]
- [netdrv] Fix warning in drivers/net/vxge/vxge-main.c: vxge_probe() (Prarit Bhargava) [603733]
- [v4l] Fix warnings in drivers/media/dvb/frontends (Prarit Bhargava) [603733]
- [trace] Fix warning in include/trace/events/kmem.h: mm_kswapd_ran() (Prarit Bhargava) [603733]
- [scsi] Fix warning in drivers/scsi/megaraid/megaraid_sas.c: process_fw_state_change_wq() (Prarit Bhargava) [603733]
- [pcmcia] Fix warnings in drivers/pcmcia/socket_sysfs.c (Prarit Bhargava) [603733]
- [netdrv] Fix warning in drivers/net/wireless/wl3501_cs.c: wl3501_esbq_exec() (Prarit Bhargava) [603733]
- [drm] Workaround broken check_headers.pl (Prarit Bhargava) [603733]
- [isdn] Fix warning in drivers/isdn/hardware/mISDN/hfcpci.c: hfcpci_softirq() (Prarit Bhargava) [603733]
- [virt] Fix warning in drivers/vhost/vhost.c: vhost_signal() (Prarit Bhargava) [603733]
- [md] Fix warning in drivers/md/dm-repl.c: _replicator_slink_message() (Prarit Bhargava) [603733]
- [virt] Fix warning in arch/x86/kvm/svm.c: svm_handle_mce() (Prarit Bhargava) [603733]
- [net] Fix stack warning in net/mac80211/debugfs_sta.c: sta_agg_status_read() (Prarit Bhargava) [603733]
- [kernel] Fix warnings in scripts/mod/mod-extract.c (Prarit Bhargava) [603733]
- [mm] Fix warning in mm/mprotect.c: mprotect_fixup() (Prarit Bhargava) [603733]
- [mm] Fix warning in mm/mmap.c: __split_vma() (Prarit Bhargava) [603733]
- [mca] Fix warning in include/linux/mca-legacy.h (Prarit Bhargava) [603733]
- [mm] Fix warning in include/linux/khugepaged.h (Andrea Arcangeli) [603733]
- [virt] Fix warnings in drivers/xen/events.c() (Prarit Bhargava) [603733]
- [x86] Fix warning in drivers/platform/x86/thinkpad_acpi.c (Prarit Bhargava) [603733]
- [netdrv] Fix warnings in drivers/net/wireless/b43/phy_lp.c (Prarit Bhargava) [603733]
- [block] Fix warning in drivers/block/cciss.c: fail_all_cmds() (Prarit Bhargava) [603733]
- [isdn] Fix warnings in drivers/isdn/hardware/mISDN/w6692.c (Prarit Bhargava) [603733]
- [kernel] Fix compiler warning in sched.c (Larry Woodman) [544197]
- [fs] fscache/object-list.c: fix warning on 32-bit (Prarit Bhargava) [603733]
- [sysfs] Fix warning in sysfs_open_file (Prarit Bhargava) [603733]
- [kdump] Fix warning in kexec_crash_size_show (Prarit Bhargava) [603733]
- [netdrv] libertas: fix uninitialized variable warning (Prarit Bhargava) [603733]
- [drm] Fixes linux-next & linux-2.6 checkstack warnings (Prarit Bhargava) [603733]
- [x86] acpi_pad: squish warning (Prarit Bhargava) [603733]
- [netdrv] iwlwifi: dynamically allocate buffer for sram debugfs file (Prarit Bhargava) [603733]
- [isdn] Fix warnings in eicon driver (Prarit Bhargava) [603733]
- [net] bridge: Make first arg to deliver_clone const (Prarit Bhargava) [603733]
- [kernel] linux/elfcore.h: hide kernel functions (Prarit Bhargava) [603733]
- [fs] quota: suppress warning: "quotatypes" defined but not used (Prarit Bhargava) [603733]
- [fs] fuse: fix large stack use (Prarit Bhargava) [603733]
- [uwb] wlp: refactor wlp_get_<attribute>() macros (Prarit Bhargava) [603733]
- [usb] Remove large struct from the stack in USB storage isd200 driver (Prarit Bhargava) [603733]
- [usb] isp1362: better 64bit printf warning fixes (Prarit Bhargava) [603733]
- [pci] PCI: kill off pci_register_set_vga_state() symbol export (Prarit Bhargava) [603733]
- [x86] intel-iommu: Fix section mismatch dmar_ir_support() uses dmar_tbl (Prarit Bhargava) [603733]
- [v4l] dvb-bt8xx: fix compile warning (Prarit Bhargava) [603733]
- [tty] tty_buffer: Fix distinct type warning (Prarit Bhargava) [603733]
- [virt] virtio: fix section mismatch warnings (Prarit Bhargava) [603733]
- [ata] Fix warning in libata-eh.c (Prarit Bhargava) [603733]
- [crypto] testmgr: Fix warning (Prarit Bhargava) [603733]
- [x86] Use __builtin_memset and __builtin_memcpy for memset/memcpy (Prarit Bhargava) [603733]
- [x86] apic: Fix prototype in hw_irq.h (Prarit Bhargava) [603733]
- [x86] nmi_watchdog: relax the nmi checks during bootup (Don Zickus) [596760]
- [x86] nmi_watchdog: disable correct cpu if it fails check (Don Zickus) [596760]
- [netdrv] iwlwifi: update supported PCI_ID list for 5xx0 series (John Linville) [599148]
- [netdrv] iwlwifi: recalculate average tpt if not current (John Linville) [595845]
- [netdrv] iwl3945: enable stuck queue detection on 3945 (John Linville) [595847]
- [netdrv] iwlwifi: fix internal scan race (John Linville) [595846]
- [netdrv] iwlwifi: fix scan races (John Linville) [595846]
- [virt] virtio: fix balloon without VIRTIO_BALLOON_F_STATS_VQ (Amit Shah) [601690]
- [virt] virtio: Fix scheduling while atomic in virtio_balloon stats (Amit Shah) [601690]
- [virt] virtio: Add memory statistics reporting to the balloon driver (Amit Shah) [601690]
- [block] make blk_init_free_list and elevator_init idempotent (Mike Snitzer) [594584]
- [block] avoid unconditionally freeing previously allocated request_queue (Mike Snitzer) [594584]
- [virt] vhost: fix the memory leak which will happen when memory_access_ok fails (Michael S. Tsirkin) [599299]
- [virt] vhost-net: fix to check the return value of copy_to/from_user() correctly (Michael S. Tsirkin) [599299]
- [virt] vhost: fix to check the return value of copy_to/from_user() correctly (Michael S. Tsirkin) [599299]
- [virt] vhost: Fix host panic if ioctl called with wrong index (Michael S. Tsirkin) [599299]
- [block] writeback: fixups for !dirty_writeback_centisecs (Mike Snitzer) [594570]
- [fs] writeback: disable periodic old data writeback for !dirty_writeback_centisecs (Mike Snitzer) [594570]
- [modsign] Include the GNU build ID note in the digest (David Howells) [581965]
- [modsign] Fix a number of module signing bugs (David Howells) [581965]
- [modsign] KEYS: Return more accurate error codes (David Howells) [591891]
- [netdrv] ixgbe: fix automatic LRO/RSC settings for low latency (Andy Gospodarek) [595555]
- [scsi] sync fcoe with upstream (Mike Christie) [603263]
- [trace] conflicting tracepoint power.h headers (Mark Wielaard) [599175]
- [netdrv] ixgbe: fix panic when shutting down system with WoL enabled (Andy Gospodarek) [601066]
- [netdrv] ixgbe: ixgbe_down needs to stop dev_watchdog (Andy Gospodarek) [604807]
- [scsi] sync fcoe (Mike Christie) [595558]
- [kernel] CRED: Fix a race in creds_are_invalid() in credentials debugging (James Leddy) [578268]
- [kernel] Remove timeout logic in mutex_spin_on_owner() to match upstream (Steve Best) [602805]

* Sun Jun 20 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-37.el6]
- [virt] Disable transparent hugepages when running under Xen (Dor Laor) [605566]
- [pci] fix compilation when CONFIG_PCI_MSI=n (Vivek Goyal) [589397]
- [block] virtio_blk: support barriers without FLUSH feature (Christoph Hellwig) [602595]
- [mm] make compound_lock irqsafe in put_page (Andrea Arcangeli) [605354]
- [mm] remove compound_lock from futex (Andrea Arcangeli) [605354]
- [mm] memcontrol compound_lock irqsafe (Andrea Arcangeli) [605354]
- [mm] add compound_lock_irqsave/irqrestore (Andrea Arcangeli) [605354]

* Wed Jun 16 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-36.el6]
- [virt] virtio-pci: Disable MSI at startup (Vivek Goyal) [589397]
- [mm] Reenable transparent hugepages (Aristeu Rozanski) [602436]

* Tue Jun 15 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-35.el6]
- [mm] Revert "[redhat] Enable transparent hugepages by default" (Aristeu Rozanski) [602436]

* Tue Jun 15 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-34.el6]
- [net] Revert "[net] bridge: make bridge support netpoll" (Herbert Xu) [602927]
- [virt] always invalidate and flush on spte page size change (Andrea Arcangeli) [578134]
- [mm] root anon vma bugchecks (Andrea Arcangeli) [578134]
- [mm] resurrect the check in page_address_in_vma (Andrea Arcangeli) [578134]
- [mm] root anon vma use root (Andrea Arcangeli) [578134]
- [mm] avoid ksm hang (Andrea Arcangeli) [578134]
- [mm] always add new vmas at the end (Andrea Arcangeli) [578134]
- [mm] remove unnecessary lock from __vma_link (Andrea Arcangeli) [578134]
- [mm] optimize hugepage tracking for memcgroup & handle splitting (Rik van Riel) [597108]
- [mm] properly move a transparent hugepage between cgroups (Rik van Riel) [597081]
- [mm] scale statistics if the page is a transparent hugepage (Rik van Riel) [597077]
- [mm] enhance mem_cgroup_charge_statistics with a page_size argument (Rik van Riel) [597058]
- [virt] add option to disable spinlock patching on hypervisor (Gleb Natapov) [599068]
- [virt] xen: don't touch xsave in cr4 (Andrew Jones) [599069]
- [drm] Update core to current drm-linus (Adam Jackson) [589547 589792 597022]
- [mm] fix refcount bug in anon_vma code (Rik van Riel) [602739]

* Thu Jun 03 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-33.el6]
- [netdrv] vlan: allow null VLAN ID to be used (Andy Gospodarek) [595555]
- [netdrv] ixgbe: Add boolean parameter to ixgbe_set_vmolr (Andy Gospodarek) [595555]
- [netdrv] ixgbe: fix bug when EITR=0 causing no writebacks (Andy Gospodarek) [595555]
- [netdrv] ixgbe: enable extremely low latency (Andy Gospodarek) [595555]
- [netdrv] ixgbe: added compat bits (Andy Gospodarek) [595555]
- [netdrv] ixgbe: dcb, do not tag tc_prio_control frames (Andy Gospodarek) [595555]
- [netdrv] ixgbe: fix ixgbe_tx_is_paused logic (Andy Gospodarek) [595555]
- [netdrv] ixgbe: always enable vlan strip/insert when DCB is enabled (Andy Gospodarek) [595555]
- [netdrv] ixgbe: remove some redundant code in setting FCoE FIP filter (Andy Gospodarek) [595555]
- [netdrv] ixgbe: fix wrong offset to fc_frame_header in ixgbe_fcoe_ddp (Andy Gospodarek) [595555]
- [netdrv] ixgbe: fix header len when unsplit packet overflows to data buffer (Andy Gospodarek) [595555]
- [netdrv] ixgbe: fix setting of promisc mode when using mac-vlans (Andy Gospodarek) [595555]
- [netdrv] ixgbe: Add support for VF MAC and VLAN configuration (Andy Gospodarek) [595555]
- [netdrv] ixgbe: fix bug with vlan strip in promsic mode (Andy Gospodarek) [595555]
- [virt] use unfair spinlock when running on hypervisor (Gleb Natapov) [599068]

* Wed Jun 02 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-32.el6]
- [kernel] sched: update normalized values on user updates via proc (Hendrik Brueckner) [590748]
- [kernel] sched: Make tunable scaling style configurable (Hendrik Brueckner) [590748]
- [s390x] nohz: Introduce arch_needs_cpu (Hendrik Brueckner) [590009]
- [ppc64] Use form 1 affinity to setup node distance (Steve Best) [594502]
- [ppc64] numa: Use ibm, architecture-vec-5 to detect form 1 affinity (Steve Best) [594502]
- [ppc64] Set a smaller value for RECLAIM_DISTANCE to enable zone reclaim (Steve Best) [594502]
- [block] Add padding to writeback_control (Mike Snitzer) [594570]
- [fs] cifs: fix page refcount leak (Jeff Layton) [595827]
- [scsi] megaraid_sas - Add three times Online controller reset (Tomas Henzl) [594821]
- [scsi] megaraid: update driver version to 4.28 (Tomas Henzl) [577010]
- [netdrv] tg3: Provide more support for 57765 with v3.108 (John Feeney) [581691]
- [scsi] skip sense logging for some ATA PASS-THROUGH cdbs (Jeff Moyer) [596997]
- [block] allow initialization of previously allocated request_queue (Mike Snitzer) [594584]
- [usb] Fix oops on switching USB controllers (Pete Zaitcev) [578979]
- [drm] nouveau: important fixes to vbios parser (Ben Skeggs) [596604]
- [virt] virtio: console: Fix crash when port is unplugged and blocked for write (Amit Shah) [596635]
- [virt] virtio: console: Fix crash when hot-unplugging a port and read is blocked (Amit Shah) [596635]
- [kernel] signals: check_kill_permission(): don't check creds if same_thread_group() (Oleg Nesterov) [595499]
- [drm] fix issue with wake up like upstream commit (Dave Airlie) [577959]
- [x86] Fix AMD IOMMU suspend/resume (Matthew Garrett) [593787]
- [mm] do_generic_file_read: clear page errors when issuing a fresh read of the page (Rik van Riel) [596334]
- [x86] Fix loud HPET warning on Intel Platforms (Prarit Bhargava) [592036]
- [x86] Intel Cougar Point PCH support for SATA, USB, HD Audio, I2C(SMBUS), and iTCO Watchdog (John Villalovos) [560077]
- [x86] dell-laptop: Update to match mainline (Matthew Garrett) [586495]
- [kernel] proc: backport afinity_hint code (Neil Horman) [591509]
- [scsi] bfa: powerpc compilation warning and endian fix (Rob Evers) [583154]
- [scsi] bfa: code review fixes (Rob Evers) [583154]
- [s390x] dasd: fix race between tasklet and dasd_sleep_on (Hendrik Brueckner) [591963]
- [s390x] vdso: add missing vdso_install target (Hendrik Brueckner) [587368]
- [mm] mempolicy: fix get_mempolicy() for relative and static nodes (Steve Best) [592327]
- [net] reserve ports for applications using fixed port numbers (Amerigo Wang) [580970]
- [kernel] sysctl: add proc_do_large_bitmap (Amerigo Wang) [580970]
- [kernel] sysctl: refactor integer handling proc code (Amerigo Wang) [580970]
- [virt] VMware Balloon: clamp number of collected non-balloonable pages (Amit Shah) [582826]
- [virt] x86, hypervisor: add missing <linux/module.h> (Amit Shah) [582826]
- [nfs] nfsd4: bug in read_buf (Steve Dickson) [597215]
- [nfs] svcrdma: RDMA support not yet compatible with RPC6 (Steve Dickson) [597215]
- [nfs] Revert "nfsd4: distinguish expired from stale stateids" (Steve Dickson) [597215]
- [nfs] nfsd: safer initialization order in find_file() (Steve Dickson) [597215]
- [nfs] nfs4: minor callback code simplification, comment (Steve Dickson) [597215]
- [nfs] NFSD: don't report compiled-out versions as present (Steve Dickson) [597215]
- [nfs] nfsd4: implement reclaim_complete (Steve Dickson) [597215]
- [nfs] nfsd4: nfsd4_destroy_session must set callback client under the state lock (Steve Dickson) [597215]
- [nfs] nfsd4: keep a reference count on client while in use (Steve Dickson) [597215]
- [nfs] nfsd4: mark_client_expired (Steve Dickson) [597215]
- [nfs] nfsd4: introduce nfs4_client.cl_refcount (Steve Dickson) [597215]
- [nfs] nfsd4: refactor expire_client (Steve Dickson) [597215]
- [nfs] nfsd4: extend the client_lock to cover cl_lru (Steve Dickson) [597215]
- [nfs] nfsd4: use list_move in move_to_confirmed (Steve Dickson) [597215]
- [nfs] nfsd4: fold release_session into expire_client (Steve Dickson) [597215]
- [nfs] nfsd4: rename sessionid_lock to client_lock (Steve Dickson) [597215]
- [nfs] nfsd4: fix bare destroy_session null dereference (Steve Dickson) [597215]
- [nfs] nfsd4: use local variable in nfs4svc_encode_compoundres (Steve Dickson) [597215]
- [nfs] nfsd: further comment typos (Steve Dickson) [597215]
- [nfs] sunrpc: centralise most calls to svc_xprt_received (Steve Dickson) [597215]
- [nfs] nfsd4: fix unlikely race in session replay case (Steve Dickson) [597215]
- [nfs] nfsd4: fix filehandle comment (Steve Dickson) [597215]
- [nfs] nfsd: potential ERR_PTR dereference on exp_export() error paths (Steve Dickson) [597215]
- [nfs] nfsd4: complete enforcement of 4.1 op ordering (Steve Dickson) [597215]
- [nfs] nfsd4: allow 4.0 clients to change callback path (Steve Dickson) [597215]
- [nfs] nfsd4: rearrange cb data structures (Steve Dickson) [597215]
- [nfs] NFSD: NFSv4 callback client should use RPC_TASK_SOFTCONN (Steve Dickson) [597215]
- [nfs] nfsd4: cl_count is unused (Steve Dickson) [597215]
- [nfs] nfsd4: don't sleep in lease-break callback (Steve Dickson) [597215]
- [nfs] nfsd4: indentation cleanup (Steve Dickson) [597215]
- [nfs] nfsd4: consistent session flag setting (Steve Dickson) [597215]
- [nfs] nfsd4: remove probe task's reference on client (Steve Dickson) [597215]
- [nfs] nfsd4: remove dprintk (Steve Dickson) [597215]
- [nfs] nfsd4: shutdown callbacks on expiry (Steve Dickson) [597215]
- [nfs] nfsd4: preallocate nfs4_rpc_args (Steve Dickson) [597215]
- [nfs] svcrpc: don't hold sv_lock over svc_xprt_put() (Steve Dickson) [597215]
- [nfs] nfsd: don't break lease while servicing a COMMIT (Steve Dickson) [597215]
- [nfs] nfsd: factor out hash functions for export caches (Steve Dickson) [597215]
- [nfs] sunrpc: never return expired entries in sunrpc_cache_lookup (Steve Dickson) [597215]
- [nfs] sunrpc/cache: factor out cache_is_expired (Steve Dickson) [597215]
- [nfs] sunrpc: don't keep expired entries in the auth caches (Steve Dickson) [597215]
- [nfs] nfsd4: document lease/grace-period limits (Steve Dickson) [597215]
- [nfs] nfsd4: allow setting grace period time (Steve Dickson) [597215]
- [nfs] nfsd4: reshuffle lease-setting code to allow reuse (Steve Dickson) [597215]
- [nfs] nfsd4: remove unnecessary lease-setting function (Steve Dickson) [597215]
- [nfs] nfsd4: simplify lease/grace interaction (Steve Dickson) [597215]
- [nfs] nfsd4: simplify references to nfsd4 lease time (Steve Dickson) [597215]
- [nfs] Fix another nfs_wb_page() deadlock (Steve Dickson) [595478]
- [nfs] Ensure that we mark the inode as dirty if we exit early from commit (Steve Dickson) [595478]
- [nfs] Fix a lock imbalance typo in nfs_access_cache_shrinker (Steve Dickson) [595478]
- [nfs] sunrpc: fix leak on error on socket xprt setup (Steve Dickson) [595478]
- [pci] Add padding to PCI structs for future enhancements (Prarit Bhargava) [590286]

* Wed May 26 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-31.el6]
- [mm] fix vma_adjust lock inversion (Andrea Arcangeli) [595808]
- [mm] eliminate compiler warning introduced by my "kernel pagefault tracepoint for x86 & x86_64 patch" (Larry Woodman) [526032]
- [netdrv] tg3: Fix INTx fallback when MSI fails (Steve Best) [594456]
- [virt] correctly trace irq injection on SVM (Gleb Natapov) [594020]
- [virt] KVM: remove CAP_SYS_RAWIO requirement from kvm_vm_ioctl_assign_irq (Alex Williamson) [594912]
- [virt] KVM: Fix wallclock version writing race (Glauber Costa) [592033]
- [x86] Fix double enable_IR_x2apic call on SMP kernel on !SMP boards (Luming Yu) [585122]
- [block] Adjust elv_iosched_show to return "none" for bio-based DM (Mike Snitzer) [595393]
- [dm] mpath: Add a feature flag attribute to the multipath structure (Mike Snitzer) [594503]
- [kernel] fix compat_sys_sched_getaffinity() (Oleg Nesterov) [582407]
- [usb] usbcore: Fix issue with disabled USB3 protocol ports (Bhavna Sarathy) [591916]
- [kernel] python: change scripts to use system python instead of env (Don Zickus) [575965]
- [scsi] mpt2sas: update to 05.100.00.02 (Tomas Henzl) [591971]
- [virt] Fix FV Xen guest when xen_pv_hvm not enabled (Don Dutile) [523134]
- [net] enhance network cgroup classifier to work in softirq context (Neil Horman) [595351]
- [net] gro: Fix bogus gso_size on the first fraglist entry (Herbert Xu) [594561]
- [nfs] sunrpc trace points (Steve Dickson) [567741]
- [nfs] don't try to decode GETATTR if DELEGRETURN returned error (Jeff Layton) [584391]
- [nfs] d_revalidate() is too trigger-happy with d_drop() (Jeff Layton) [587225]
- [ppc64] Fix zero length strncmp() on powerpc (Steve Best) [593129]
- [ppc64] pseries: Fix xics interrupt affinity (Steve Best) [592438]
- [ppc] Improve 64bit copy_tofrom_user (Steve Best) [591344]
- [fs] GFS2: Fix permissions checking for setflags ioctl() (Steven Whitehouse) [595395] {CVE-2010-1641}
- [gfs] GFS2: Add two useful messages (Steven Whitehouse) [589510]
- [serial] fix serial console hang after entering username (John Villalovos) [590851]
- [kdump] kexec can't load capturing kernel on some big RAM systems (Vitaly Mayatskikh) [580843]
- [fs] cleanup generic block based fiemap (Josef Bacik) [578560]
- [fs] vfs: add NOFOLLOW/UNUSED to umount flags (Josef Bacik) [562078]
- [fs] dlm: fix ast ordering for user locks (David Teigland) [592418]
- [fs] cifs: fix noserverino handling when unix extensions are enabled (Jeff Layton) [591483]
- [fs] cifs: don't update uniqueid in cifs_fattr_to_inode (Jeff Layton) [591483]
- [fs] cifs: always revalidate hardlinked inodes when using noserverino (Jeff Layton) [591483]
- [fs] cifs: Fix losing locks during fork() (Jeff Layton) [591483]
- [fs] cifs: propagate cifs_new_fileinfo() error back to the caller (Jeff Layton) [591483]
- [fs] cifs: add comments explaining cifs_new_fileinfo behavior (Jeff Layton) [591483]
- [fs] cifs: Allow null nd (as nfs server uses) on create (Jeff Layton) [591483]
- [fs] cifs: remove unused parameter from cifs_posix_open_inode_helper() (Jeff Layton) [591483]
- [fs] cifs: drop quota operation stubs (Jeff Layton) [591483]
- [fs] cifs: Remove unused cifs_oplock_cachep (Jeff Layton) [591483]
- [fs] cifs: Cleanup various minor breakage in previous cFYI cleanup (Jeff Layton) [591483]
- [fs] cifs: Neaten cERROR and cFYI macros, reduce text space (Jeff Layton) [591483]
- [fs] cifs: trivial white space (Jeff Layton) [591483]
- [fs] cifs: use add_to_page_cache_lru (Jeff Layton) [591483]
- [fs] cifs: not overwriting file_lock structure after GET_LK (Jeff Layton) [591483]
- [fs] cifs: Fix a kernel BUG with remote OS/2 server (Jeff Layton) [591483]
- [fs] cifs: initialize nbytes at the beginning of CIFSSMBWrite() (Jeff Layton) [591483]
- [fs] cifs: back out patches that didn't make it upstream (Jeff Layton) [591483]
- [fs] cifs: guard against hardlinking directories (Jeff Layton) [591229]
- [pci] check caps from sysfs file open to read device dependent config space (Don Dutile) [559709]
- [fs] sysfs: add struct file* to bin_attr callbacks (Don Dutile) [559709]
- [ata] pata_via: fixup detection issues (David Milburn) [591074]
- [security] keys: call_sbin_request_key() must write lock keyrings before modifying them (David Howells) [591891]
- [security] keys: Use RCU dereference wrappers in keyring key type code (David Howells) [591891]
- [security] keys: find_keyring_by_name() can gain access to a freed keyring (David Howells) [585101 591891] {CVE-2010-1437}
- [security] keys: Fix RCU handling in key_gc_keyring() (David Howells) [591891]
- [security] keys: the request_key() syscall should link an existing key to the dest keyring (David Howells) [591891]
- [security] keys: don't need to use RCU in keyring_read() as semaphore is held (David Howells) [591891]
- [security] keys: fix an RCU warning (David Howells) [591891]
- [security] keys: PTR_ERR return of wrong pointer in keyctl_get_security() (David Howells) [591891]
- [fs] CacheFiles: Fix error handling in cachefiles_determine_cache_security() (David Howells) [591894]
- [fs] CacheFiles: Fix occasional EIO on call to vfs_unlink() (David Howells) [591894]
- [fs] fs-cache: order the debugfs stats correctly (David Howells) [591894]
- [fs] SLOW_WORK: CONFIG_SLOW_WORK_PROC should be CONFIG_SLOW_WORK_DEBUG (David Howells) [591894]
- [fs] fscache: add missing unlock (David Howells) [591894]
- [fs] FS-Cache: Remove the EXPERIMENTAL flag (David Howells) [591894]
- [fs] CacheFiles: Fix a race in cachefiles_delete_object() vs rename (David Howells) [591894]
- [fs] switch cachefiles to kern_path() (David Howells) [591894]
- [fs] FS-Cache: Avoid maybe-used-uninitialised warning on variable (David Howells) [591894]
- [net] bonding: make bonding support netpoll (Amerigo Wang) [587751]
- [net] bridge: make bridge support netpoll (Amerigo Wang) [587751]
- [net] netpoll: add generic support for bridge and bonding devices (Amerigo Wang) [587751]
- [ppc64] Use lwarx/ldarx hint in bit locks (Steve Best) [594515]
- [ppc64] 85xx: Make sure lwarx hint isn't set on ppc32 (Steve Best) [594515]
- [ppc64] Use lwarx hint in spinlocks (Steve Best) [594515]
- [fs] tmpfs: Insert tmpfs cache pages to inactive list at first (Rik van Riel) [595210]
- [mm] vmscan: detect mapped file pages used only once (Rik van Riel) [595210]
- [mm] vmscan: drop page_mapping_inuse() (Rik van Riel) [595210]
- [mm] vmscan: factor out page reference checks (Rik van Riel) [595210]
- [nfs] SUNRPC: Don't spam gssd with upcall requests when the kerberos key expired (Steve Dickson) [595478]
- [nfs] SUNRPC: Reorder the struct rpc_task fields (Steve Dickson) [595478]
- [nfs] SUNRPC: Remove the 'tk_magic' debugging field (Steve Dickson) [595478]
- [nfs] SUNRPC: Move the task->tk_bytes_sent and tk_rtt to struct rpc_rqst (Steve Dickson) [595478]
- [nfs] Don't call iput() in nfs_access_cache_shrinker (Steve Dickson) [595478]
- [nfs] Clean up nfs_access_zap_cache() (Steve Dickson) [595478]
- [nfs] Don't run nfs_access_cache_shrinker() when the mask is GFP_NOFS (Steve Dickson) [595478]
- [nfs] SUNRPC: Ensure rpcauth_prune_expired() respects the nr_to_scan parameter (Steve Dickson) [595478]
- [nfs] SUNRPC: Ensure memory shrinker doesn't waste time in rpcauth_prune_expired() (Steve Dickson) [595478]
- [nfs] SUNRPC: Dont run rpcauth_cache_shrinker() when gfp_mask is GFP_NOFS (Steve Dickson) [595478]
- [nfs] Read requests can use GFP_KERNEL (Steve Dickson) [595478]
- [nfs] Clean up nfs_create_request() (Steve Dickson) [595478]
- [nfs] Don't use GFP_KERNEL in rpcsec_gss downcalls (Steve Dickson) [595478]
- [nfs] NFSv4: Don't use GFP_KERNEL allocations in state recovery (Steve Dickson) [595478]
- [nfs] SUNRPC: Fix xs_setup_bc_tcp() (Steve Dickson) [595478]
- [nfs] SUNRPC: Replace jiffies-based metrics with ktime-based metrics (Steve Dickson) [595478]
- [kernel] ktime: introduce ktime_to_ms() (Steve Dickson) [595478]
- [nfs] SUNRPC: RPC metrics and RTT estimator should use same RTT value (Steve Dickson) [595478]
- [nfs] Calldata for nfs4_renew_done() (Steve Dickson) [595478]
- [nfs] nfs4: renewd renew operations should take/put a client reference (Steve Dickson) [595478]
- [nfs] Squelch compiler warning in nfs_add_server_stats() (Steve Dickson) [595478]
- [nfs] Clean up fscache_uniq mount option (Steve Dickson) [595478]
- [nfs] Squelch compiler warning (Steve Dickson) [595478]
- [nfs] SUNRPC: Trivial cleanups in include/linux/sunrpc/xdr.h (Steve Dickson) [595478]
- [nfs] NFSv4: Clean up the NFSv4 setclientid operation (Steve Dickson) [595478]
- [nfs] NFSv4: Allow attribute caching with 'noac' mounts if client holds a delegation (Steve Dickson) [595478]
- [nfs] SUNRPC: Fail over more quickly on connect errors (Steve Dickson) [595478]
- [nfs] SUNRPC: Move the test for XPRT_CONNECTING into xprt_connect() (Steve Dickson) [595478]
- [nfs] SUNRPC: Cleanup - make rpc_new_task() call rpc_release_calldata on failure (Steve Dickson) [595478]
- [nfs] SUNRPC: Clean up xprt_release() (Steve Dickson) [595478]
- [nfs] NFSv4: Fix up the documentation for nfs_do_refmount (Steve Dickson) [595478]
- [nfs] Replace nfsroot on-stack filehandle (Steve Dickson) [595478]
- [nfs] Cleanup file handle allocations in fs/nfs/super.c (Steve Dickson) [595478]
- [nfs] Prevent the mount code from looping forever on broken exports (Steve Dickson) [595478]
- [nfs] Reduce stack footprint of nfs3_proc_getacl() and nfs3_proc_setacl() (Steve Dickson) [595478]
- [nfs] Reduce stack footprint of nfs_statfs() (Steve Dickson) [595478]
- [nfs] Reduce stack footprint of nfs_setattr() (Steve Dickson) [595478]
- [nfs] Reduce stack footprint of nfs4_proc_create() (Steve Dickson) [595478]
- [nfs] Reduce the stack footprint of nfs_proc_symlink() (Steve Dickson) [595478]
- [nfs] Reduce the stack footprint of nfs_proc_create (Steve Dickson) [595478]
- [nfs] Reduce the stack footprint of nfs_rmdir (Steve Dickson) [595478]
- [nfs] Reduce stack footprint of nfs_proc_remove() (Steve Dickson) [595478]
- [nfs] Reduce stack footprint of nfs3_proc_readlink() (Steve Dickson) [595478]
- [nfs] Reduce the stack footprint of nfs_link() (Steve Dickson) [595478]
- [nfs] Reduce stack footprint of nfs_readdir() (Steve Dickson) [595478]
- [nfs] Reduce stack footprint of nfs3_proc_rename() and nfs4_proc_rename() (Steve Dickson) [595478]
- [nfs] Reduce stack footprint of nfs_revalidate_inode() (Steve Dickson) [595478]
- [nfs] NFSv4: Reduce stack footprint of nfs4_proc_access() and nfs3_proc_access() (Steve Dickson) [595478]
- [nfs] NFSv4: Reduce the stack footprint of nfs4_remote_referral_get_sb (Steve Dickson) [595478]
- [nfs] NFSv4: Reduce stack footprint of nfs4_get_root() (Steve Dickson) [595478]
- [nfs] Reduce the stack footprint of nfs_follow_remote_path() (Steve Dickson) [595478]
- [nfs] Reduce the stack footprint of nfs_lookup (Steve Dickson) [595478]
- [nfs] NFSv4: Reduce the stack footprint of try_location() (Steve Dickson) [595478]
- [nfs] Reduce the stack footprint of nfs_create_server (Steve Dickson) [595478]
- [nfs] Reduce the stack footprint of nfs_follow_mountpoint() (Steve Dickson) [595478]
- [nfs] NFSv4: Eliminate nfs4_path_walk() (Steve Dickson) [595478]
- [nfs] Add helper functions for allocating filehandles and fattr structs (Steve Dickson) [595478]
- [nfs] NFSv4: Fix the locking in nfs_inode_reclaim_delegation() (Steve Dickson) [595478]
- [nfs] fix memory leak in nfs_get_sb with CONFIG_NFS_V4 (Steve Dickson) [595478]
- [nfs] fix some issues in nfs41_proc_reclaim_complete() (Steve Dickson) [595478]
- [nfs] Ensure that nfs_wb_page() waits for Pg_writeback to clear (Steve Dickson) [595478]
- [nfs] Fix an unstable write data integrity race (Steve Dickson) [595478]
- [nfs] testing for null instead of ERR_PTR() (Steve Dickson) [595478]
- [nfs] NFSv4: Don't attempt an atomic open if the file is a mountpoint (Steve Dickson) [595478]
- [nfs] SUNRPC: Fix a bug in rpcauth_prune_expired (Steve Dickson) [595478]
- [nfs] NFSv4: fix delegated locking (Steve Dickson) [595478]
- [nfs] Ensure that the WRITE and COMMIT RPC calls are always uninterruptible (Steve Dickson) [595478]
- [nfs] Fix a race with the new commit code (Steve Dickson) [595478]
- [nfs] Fix the mode calculation in nfs_find_open_context (Steve Dickson) [595478]
- [nfs] NFSv4: Fall back to ordinary lookup if nfs4_atomic_open() returns EISDIR (Steve Dickson) [595478]
- [nfs] SUNRPC: Fix the return value of rpc_run_bc_task() (Steve Dickson) [595478]
- [nfs] SUNRPC: Fix a use after free bug with the NFSv4.1 backchannel (Steve Dickson) [595478]
- [nfs] ensure bdi_unregister is called on mount failure (Steve Dickson) [595478]
- [nfs] fix unlikely memory leak (Steve Dickson) [595478]
- [nfs] nfs41: renewd sequence operations should take/put client reference (Steve Dickson) [595478]
- [nfs] prevent backlogging of renewd requests (Steve Dickson) [595478]
- [nfs] rpc client can not deal with ENOSOCK, so translate it into ENOCONN (Steve Dickson) [595478]

* Tue May 25 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-30.el6]
- [perf] sync tools/perf to 2.6.34 (Jason Baron) [578987]
- [drm] i915: Update to 2.6.34-rc7 (Adam Jackson) [592003]
- [perf] userspace and core update fix (Jason Baron) [567828 578987]
- [perf] rhel6 perf fixups (Jason Baron) [567828 578987]
- [perf] backport latest core perf support (Jason Baron) [567828 578987]
- [perf] pull back 'perf' userspace (Jason Baron) [567828 578987]
- [drm] radeon/kms: report lvds status as unknown with closed lid (Jerome Glisse) [585111 591628]
- [drm] fbdev: fix cloning on fbcon (Dave Airlie) [512023]
- [drm] fbcon disconnected + hotplug operation (Jerome Glisse) [580789]
- [kernel] slow-work: use get_ref wrapper instead of directly calling get_ref (Dave Airlie) [580789]
- [drm] radeon/kms: add special workaround for triple head servers (Dave Airlie) [512023]
- [infiniband] RDMA: Use rlimit helpers (Doug Ledford) [500229]
- [infiniband] ipoib: returned back addrlen check for mc addresses (Doug Ledford) [500229]
- [infiniband] RDMA/amso1100: Fix error paths in post_send and post_recv (Doug Ledford) [500229]
- [infiniband] IB/srp: Clean up error path in srp_create_target_ib() (Doug Ledford) [500229]
- [infiniband] IB/srp: Split send and recieve CQs to reduce number of interrupts (Doug Ledford) [500229]
- [infiniband] rdma: potential ERR_PTR dereference (Doug Ledford) [500229]
- [infiniband] RDMA/cm: Set num_paths when manually assigning path records (Doug Ledford) [500229]
- [infiniband] IB/cm: Fix device_create() return value check (Doug Ledford) [500229]
- [infiniband] IB/ucm: Clean whitespace errors (Doug Ledford) [500229]
- [infiniband] IB/ucm: Increase maximum devices supported (Doug Ledford) [500229]
- [infiniband] IB/ucm: Use stack variable 'base' in ib_ucm_add_one (Doug Ledford) [500229]
- [infiniband] IB/ucm: Use stack variable 'devnum' in ib_ucm_add_one (Doug Ledford) [500229]
- [infiniband] RDMA/cm: Remove unused definition of RDMA_PS_SCTP (Doug Ledford) [500229]
- [infiniband] RDMA/cm: Revert association of an RDMA device when binding to loopback (Doug Ledford) [500229]
- [infiniband] IB/addr: Correct CONFIG_IPv6 to CONFIG_IPV6 (Doug Ledford) [500229]
- [infiniband] IB/addr: Fix IPv6 routing lookup (Doug Ledford) [500229]
- [infiniband] IB/addr: Simplify resolving IPv4 addresses (Doug Ledford) [500229]
- [infiniband] RDMA/cm: fix loopback address support (Doug Ledford) [500229]
- [infiniband] IB/addr: Store net_device type instead of translating to RDMA transport (Doug Ledford) [500229]
- [infiniband] IB/addr: Verify source and destination address families match (Doug Ledford) [500229]
- [infiniband] RDMA/cma: Replace net_device pointer with index (Doug Ledford) [500229]
- [infiniband] RDMA/cma: Fix AF_INET6 support in multicast joining (Doug Ledford) [500229]
- [infiniband] RDMA/cma: Correct detection of SA Created MGID (Doug Ledford) [500229]
- [infiniband] RDMA/addr: Use appropriate locking with for_each_netdev() (Doug Ledford) [500229]
- [infiniband] RDMA/ucma: Add option to manually set IB path (Doug Ledford) [500229]
- [infiniband] IB/mad: Ignore iWARP devices on device removal (Doug Ledford) [500229]
- [infiniband] IB/umad: Clean whitespace (Doug Ledford) [500229]
- [infiniband] IB/umad: Increase maximum devices supported (Doug Ledford) [500229]
- [infiniband] IB/umad: Use stack variable 'base' in ib_umad_init_port (Doug Ledford) [500229]
- [infiniband] IB/umad: Use stack variable 'devnum' in ib_umad_init_port (Doug Ledford) [500229]
- [infiniband] IB/umad: Remove port_table[] (Doug Ledford) [500229]
- [infiniband] IB/umad: Convert *cdev to cdev in struct ib_umad_port (Doug Ledford) [500229]
- [infiniband] IB/uverbs: Use anon_inodes instead of private infinibandeventfs (Doug Ledford) [500229]
- [infiniband] IB/core: Fix and clean up ib_ud_header_init() (Doug Ledford) [500229]
- [infiniband] IB/core: Pack struct ib_device a little tighter (Doug Ledford) [500229]
- [infiniband] IB/uverbs: Whitespace cleanup (Doug Ledford) [500229]
- [infiniband] IB/uverbs: Pack struct ib_uverbs_event_file tighter (Doug Ledford) [500229]
- [infiniband] IB/uverbs: Increase maximum devices supported (Doug Ledford) [500229]
- [infiniband] IB/uverbs: use stack variable 'base' in ib_uverbs_add_one (Doug Ledford) [500229]
- [infiniband] IB/uverbs: Use stack variable 'devnum' in ib_uverbs_add_one (Doug Ledford) [500229]
- [infiniband] IB/uverbs: Remove dev_table (Doug Ledford) [500229]
- [infiniband] IB/uverbs: Convert *cdev to cdev in struct ib_uverbs_device (Doug Ledford) [500229]
- [infiniband] IB/uverbs: Fix return of PTR_ERR() of wrong pointer in ib_uverbs_get_context() (Doug Ledford) [500229]
- [infiniband] IB: Clarify the documentation of ib_post_send() (Doug Ledford) [500229]
- [infiniband] IB/ehca: Allow access for ib_query_qp() (Doug Ledford) [500229]
- [infiniband] IB/ehca: Do not turn off irqs in tasklet context (Doug Ledford) [500229]
- [infiniband] IB/ehca: Fix error paths in post_send and post_recv (Doug Ledford) [500229]
- [infiniband] IB/ehca: Rework destroy_eq() (Doug Ledford) [500229]
- [infiniband] IPoIB: Include return code in trace message for ib_post_send() failures (Doug Ledford) [500229]
- [infiniband] IPoIB: Fix TX queue lockup with mixed UD/CM traffic (Doug Ledford) [500229]
- [infiniband] IPoIB: Remove TX moderation settings from ethtool support (Doug Ledford) [500229]
- [infiniband] IB/ipath: Use bitmap_weight() (Doug Ledford) [500229]
- [infiniband] Remove BKL from ipath_open() (Doug Ledford) [500229]
- [rds] remove uses of NIPQUAD, use pI4 (Doug Ledford) [500229]
- [rds] RDS/IB+IW: Move recv processing to a tasklet (Doug Ledford) [500229]
- [rds] Do not send congestion updates to loopback connections (Doug Ledford) [500229]
- [rds] Fix panic on unload (Doug Ledford) [500229]
- [rds] Fix potential race around rds_i[bw]_allocation (Doug Ledford) [500229]
- [rds] Add GET_MR_FOR_DEST sockopt (Doug Ledford) [500229]
- [infiniband] IB/mlx4: Check correct variable for allocation failure (Doug Ledford) [500229]
- [infiniband] mlx4: replace the dma_sync_single_range_for_cpu/device API (Doug Ledford) [500229]
- [infiniband] IB/mlx4: Simplify retrieval of ib_device (Doug Ledford) [500229]
- [infiniband] mlx4_core: Fix cleanup in __mlx4_init_one() error path (Doug Ledford) [500229]
- [infiniband] IB/mlx4: Fix queue overflow check in post_recv (Doug Ledford) [500229]
- [infiniband] IB/mlx4: Initialize SRQ scatter entries when creating an SRQ (Doug Ledford) [500229]
- [infiniband] mlx4: use bitmap_find_next_zero_area (Doug Ledford) [500229]
- [infiniband] mlx4_core: return a negative error value (Doug Ledford) [500229]
- [infiniband] mlx4_core: Fix parsing of reserved EQ cap (Doug Ledford) [500229]
- [infiniband] IB/mlx4: Remove limitation on LSO header size (Doug Ledford) [500229]
- [infiniband] IB/mlx4: Remove unneeded code (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Correct cap.max_inline_data assignment in nes_query_qp() (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Fix CX4 link problem in back-to-back configuration (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Clear stall bit before destroying NIC QP (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Set assume_aligned_header bit (Doug Ledford) [500229]
- [infiniband] convert to use netdev_for_each_mc_addr (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Add support for KR device id 0x0110 (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Change WQ overflow return code (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Multiple disconnects cause crash during AE handling (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Fix crash when listener destroyed during loopback setup (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Use atomic counters for CM listener create and destroy (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Fix stale ARP issue (Doug Ledford) [500229]
- [infiniband] RDMA/nes: FIN during MPA startup causes timeout (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Free kmap() resources (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Check for zero STag (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Fix Xansation test crash on cm_node ref_count (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Abnormal listener exit causes loopback node crash (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Fix crash in nes_accept() (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Resource not freed for REJECTed connections (Doug Ledford) [500229]
- [infiniband] RDMA/nes: MPA request/response error checking (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Fix query of ORD values (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Fix MAX_CM_BUFFER define (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Pass correct size to ioremap_nocache() (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Update copyright and branding string (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Add max_cqe check to nes_create_cq() (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Clean up struct nes_qp (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Implement IB_SIGNAL_ALL_WR as an iWARP extension (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Add additional SFP+ PHY uC status check and PHY reset (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Correct fast memory registration implementation (Doug Ledford) [500229]
- [infiniband] RDMA/nes: Add support for IB_WR_*INV (Doug Ledford) [500229]
- [infiniband] RDMA/nes: In nes_post_recv() always set bad_wr on error (Doug Ledford) [500229]
- [infiniband] RDMA/nes: In nes_post_send() always set bad_wr on error (Doug Ledford) [500229]
- [netdrv] cxgb3: fix linkup issue (Doug Ledford) [500229]
- [netdrv] RDMA/cxgb3: Wait at least one schedule cycle during device removal (Doug Ledford) [500229]
- [netdrv] cxgb3: fix hot plug removal crash (Doug Ledford) [500229]
- [netdrv] RDMA/cxgb3: Mark RDMA device with CXIO_ERROR_FATAL when removing (Doug Ledford) [500229]
- [netdrv] RDMA/cxgb3: Don't allocate the SW queue for user mode CQs (Doug Ledford) [500229]
- [netdrv] RDMA/cxgb3: Increase the max CQ depth (Doug Ledford) [500229]
- [netdrv] RDMA/cxgb3: Doorbell overflow avoidance and recovery (Doug Ledford) [500229]
- [netdrv] cxgb3: convert to use netdev_for_each_addr (Doug Ledford) [500229]
- [netdrv] cxgb3: fix link flap (Doug Ledford) [500229]
- [netdrv] cxgb3: FIx VLAN over Jumbo frames (Doug Ledford) [500229]
- [netdrv] RDMA/cxgb3: Remove BUG_ON() on CQ rearm failure (Doug Ledford) [500229]
- [netdrv] cxgb3: fix GRO checksum check (Doug Ledford) [500229]
- [netdrv] cxgb3: add memory barriers (Doug Ledford) [500229]
- [netdrv] iwch_cm.c: use pM to show MAC address (Doug Ledford) [500229]
- [netdrv] cxgb3: Use kzalloc for allocating only one thing (Doug Ledford) [500229]
- [netdrv] RDMA/cxgb3: Fix error paths in post_send and post_recv (Doug Ledford) [500229]
- [netdrv] cxgb3: declare MODULE_FIRMWARE (Doug Ledford) [500229]
- [netdrv] cxgb3: Set the rxq (Doug Ledford) [500229]
- [netdrv] cxgb3: No need to wake queue in xmit handler (Doug Ledford) [500229]
- [netdrv] cxgb3: Added private MAC address and provisioning packet handler for iSCSI (Doug Ledford) [500229]
- [net] Hook up cxgb4 to Kconfig and Makefile (Doug Ledford) [500229]
- [netdrv] cxgb4: Add remaining driver headers and L2T management (Doug Ledford) [500229]
- [netdrv] cxgb4: Add main driver file and driver Makefile (Doug Ledford) [500229]
- [netdrv] cxgb4: Add HW and FW support code (Doug Ledford) [500229]
- [netdrv] cxgb4: Add packet queues and packet DMA code (Doug Ledford) [500229]
- [netdrv] cxgb4: Add register, message, and FW definitions (Doug Ledford) [500229]
- [net] use helpers to access mc list (Doug Ledford) [500229]
- [net] use helpers to access uc list (Doug Ledford) [500229]
- [kernel] strstrip incorrectly marked __must_check (Doug Ledford) [500229]
- [pci] introduce pci_pcie_cap() (Doug Ledford) [500229]
- [pci] cache PCIe capability offset (Doug Ledford) [500229]
- [kernel] bitmap: introduce bitmap_set, bitmap_clear, bitmap_find_next_zero_area (Doug Ledford) [500229]
- [md] Remove unnecessary casts of void * (Doug Ledford) [583050 586296 586299 588371]
- [md] expose max value of behind writes counter (Doug Ledford) [583050 586296 586299 588371]
- [md] remove some dead fields from mddev_s (Doug Ledford) [583050 586296 586299 588371]
- [md] allow integers to be passed to md/level (Doug Ledford) [583050 586296 586299 588371]
- [md] notify mdstat waiters of level change (Doug Ledford) [583050 586296 586299 588371]
- [md] don't unregister the thread in mddev_suspend (Doug Ledford) [583050 586296 586299 588371]
- [md] factor out init code for an mddev (Doug Ledford) [583050 586296 586299 588371]
- [md] pass mddev to make_request functions rather than request_queue (Doug Ledford) [583050 586296 586299 588371]
- [md] call md_stop_writes from md_stop (Doug Ledford) [583050 586296 586299 588371]
- [md] split md_set_readonly out of do_md_stop (Doug Ledford) [583050 586296 586299 588371]
- [md] factor md_stop_writes out of do_md_stop (Doug Ledford) [583050 586296 586299 588371]
- [md] start to refactor do_md_stop (Doug Ledford) [583050 586296 586299 588371]
- [md] factor do_md_run to separate accesses to ->gendisk (Doug Ledford) [583050 586296 586299 588371]
- [md] remove ->changed and related code (Doug Ledford) [583050 586296 586299 588371]
- [md] don't reference gendisk in getgeo (Doug Ledford) [583050 586296 586299 588371]
- [md] move io accounting out of personalities into md_make_request (Doug Ledford) [583050 586296 586299 588371]
- [md] notify level changes through sysfs (Doug Ledford) [583050 586296 586299 588371]
- [md] Relax checks on ->max_disks when external metadata handling is used (Doug Ledford) [583050 586296 586299 588371]
- [md] Correctly handle device removal via sysfs (Doug Ledford) [583050 586296 586299 588371]
- [md] Add support for Raid5->Raid0 and Raid10->Raid0 takeover (Doug Ledford) [583050 586296 586299 588371]
- [md] Add support for Raid0->Raid5 takeover (Doug Ledford) [583050 586296 586299 588371]
- [md] discard StateChanged device flag (Doug Ledford) [583050 586296 586299 588371]
- [md] manage redundancy group in sysfs when changing level (Doug Ledford) [583050 586296 586299 588371]
- [md] remove unneeded sysfs files more promptly (Doug Ledford) [583050 586296 586299 588371]
- [md] set mddev readonly flag on blkdev BLKROSET ioctl (Doug Ledford) [583050 586296 586299 588371]
- [md] don't insist on valid event count for spare devices (Doug Ledford) [583050 586296 586299 588371]
- [md] simplify updating of event count to sometimes avoid updating spares (Doug Ledford) [583050 586296 586299 588371]
- [md] restore ability of spare drives to spin down (Doug Ledford) [583050 586296 586299 588371]
- [md] raid6: Fix raid-6 read-error correction in degraded state (Doug Ledford) [583050 586296 586299 588371]
- [md] raid5: allow for more than 2^31 chunks (Doug Ledford) [583050 586296 586299 588371]
- [md] deal with merge_bvec_fn in component devices better (Doug Ledford) [583050 586296 586299 588371]
- [md] fix some lockdep issues between md and sysfs (Doug Ledford) [583050 586296 586299 588371]
- [md] fix 'degraded' calculation when starting a reshape (Doug Ledford) [583050 586296 586299 588371]
- [md] allow a resync that is waiting for other resync to complete, to be aborted (Doug Ledford) [583050 586296 586299 588371]
- [md] remove unnecessary code from do_md_run (Doug Ledford) [583050 586296 586299 588371]
- [md] make recovery started by do_md_run() visible via sync_action (Doug Ledford) [583050 586296 586299 588371]
- [md] use pU to print UUIDs (Doug Ledford) [583050 586296 586299 588371]
- [md] add 'recovery_start' per-device sysfs attribute (Doug Ledford) [583050 586296 586299 588371]
- [md] rcu_read_lock() walk of mddev->disks in md_do_sync() (Doug Ledford) [583050 586296 586299 588371]
- [md] integrate spares into array at earliest opportunity (Doug Ledford) [583050 586296 586299 588371]
- [md] move compat_ioctl handling into md.c (Doug Ledford) [583050 586296 586299 588371]
- [md] add MODULE_DESCRIPTION for all md related modules (Doug Ledford) [583050 586296 586299 588371]
- [md] raid: improve MD/raid10 handling of correctable read errors (Doug Ledford) [583050 586296 586299 588371]
- [md] raid10: print more useful messages on device failure (Doug Ledford) [583050 586296 586299 588371]
- [md] bitmap: update dirty flag when bitmap bits are explicitly set (Doug Ledford) [583050 586296 586299 588371]
- [md] Support write-intent bitmaps with externally managed metadata (Doug Ledford) [583050 586296 586299 588371]
- [md] bitmap: move setting of daemon_lastrun out of bitmap_read_sb (Doug Ledford) [583050 586296 586299 588371]
- [md] support updating bitmap parameters via sysfs (Doug Ledford) [583050 586296 586299 588371]
- [md] factor out parsing of fixed-point numbers (Doug Ledford) [583050 586296 586299 588371]
- [md] support bitmap offset appropriate for external-metadata arrays (Doug Ledford) [583050 586296 586299 588371]
- [md] remove needless setting of thread->timeout in raid10_quiesce (Doug Ledford) [583050 586296 586299 588371]
- [md] change daemon_sleep to be in 'jiffies' rather than 'seconds' (Doug Ledford) [583050 586296 586299 588371]
- [md] move offset, daemon_sleep and chunksize out of bitmap structure (Doug Ledford) [583050 586296 586299 588371]
- [md] collect bitmap-specific fields into one structure (Doug Ledford) [583050 586296 586299 588371]
- [md] add honouring of suspend_{lo,hi} to raid1 (Doug Ledford) [583050 586296 586299 588371]
- [md] raid5: don't complete make_request on barrier until writes are scheduled (Doug Ledford) [583050 586296 586299 588371]
- [md] support barrier requests on all personalities (Doug Ledford) [583050 586296 586299 588371]
- [md] don't reset curr_resync_completed after an interrupted resync (Doug Ledford) [583050 586296 586299 588371]
- [md] adjust resync_min usefully when resync aborts (Doug Ledford) [583050 586296 586299 588371]

* Mon May 24 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-29.el6]
- [mm] fix mm_take_all_locks regression in 3-7/49 (Andrea Arcangeli) [556572]
- [mm] avoid __cpuset_node_allowed_softwall to run when allocation is atomic (Andrea Arcangeli) [556572 591283]
- [mm] fix race between do_huge_pmd_anonymous_page and pte_alloc_map (Andrea Arcangeli) [556572]
- [mm] add missing update for root-anon-vma drop_anon_vma in memory compactation (Andrea Arcangeli) [556572]
- [mm] exec vs split_huge_page (Andrea Arcangeli) [556572]
- [mm] include anon hugepages into the anon stats (Andrea Arcangeli) [556572]
- [mm] split_huge_page anon_vma ordering dependency (Andrea Arcangeli) [556572]
- [mm] align page_add_new_anon_rmap (Andrea Arcangeli) [556572]
- [mm] do_pages_move cannot handle hugepages (Andrea Arcangeli) [556572]
- [mm] padding to decrease risk of kabi breakage (Andrea Arcangeli) [556572]
- [mm] transhuge isolate_migratepages() (Andrea Arcangeli) [556572]
- [mm] select CONFIG_COMPACTION if TRANSPARENT_HUGEPAGE enabled (Andrea Arcangeli) [556572]
- [mm] compaction: Do not schedule work on other CPUs for compaction (Andrea Arcangeli) [556572]
- [mm] Defer compaction using an exponential backoff when compaction fails (Andrea Arcangeli) [556572]
- [mm] Add a tunable that decides when memory should be compacted and when it should be reclaimed (Andrea Arcangeli) [556572]
- [mm] Direct compact when a high-order allocation fails (Andrea Arcangeli) [556572]
- [mm] Add /sys trigger for per-node memory compaction (Andrea Arcangeli) [556572]
- [mm] Add /proc trigger for memory compaction (Andrea Arcangeli) [556572]
- [mm] Memory compaction core (Andrea Arcangeli) [556572]
- [mm] Move definition for LRU isolation modes to a header (Andrea Arcangeli) [556572]
- [mm] Export fragmentation index via /proc/extfrag_index (Andrea Arcangeli) [556572]
- [mm] Export unusable free space index via /proc/unusable_index (Andrea Arcangeli) [556572]
- [mm] Allow CONFIG_MIGRATION to be set without CONFIG_NUMA or memory hot-remove (Andrea Arcangeli) [556572]
- [mm] Allow the migration of PageSwapCache pages (Andrea Arcangeli) [556572]
- [mm] Do not try to migrate unmapped anonymous pages (Andrea Arcangeli) [556572]
- [mm] Share the anon_vma ref counts between KSM and page migration (Andrea Arcangeli) [556572]
- [mm] Take a reference to the anon_vma before migrating (Andrea Arcangeli) [556572]
- [mm] add numa awareness to hugepage allocations (Andrea Arcangeli) [556572]
- [mm] enable direct defrag (Andrea Arcangeli) [556572]
- [mm] ksm: check for ERR_PTR from follow_page() (Andrea Arcangeli) [556572]
- [mm] err.h: add helper function to simplify pointer error checking (Andrea Arcangeli) [556572]
- [mm] don't leave orhpaned swap cache after ksm merging (Andrea Arcangeli) [556572]
- [mm] adapt to anon-vma root locking (Andrea Arcangeli) [556572]
- [mm] set default to never (Andrea Arcangeli) [556572]
- [mm] transparent hugepage bootparam (Andrea Arcangeli) [556572]
- [mm] remove lumpy reclaim (Andrea Arcangeli) [556572 583003]
- [mm] memcg fix prepare migration (Andrea Arcangeli) [556572]
- [mm] avoid false positive warning in mmio (Andrea Arcangeli) [556572]
- [virt] fix kvm swapping memory corruption (Andrea Arcangeli) [556572 583861]
- [mm] remove khugepaged/enabled (Andrea Arcangeli) [556572]
- [mm] use only khugepaged_wait (Andrea Arcangeli) [556572]
- [mm] khugepaged user stack (Andrea Arcangeli) [556572]
- [mm] define hugetlb_page (Andrea Arcangeli) [556572]
- [mm] migration: avoid race between shift_arg_pages() and rmap_walk() during migration by not migrating temporary stacks (Andrea Arcangeli) [556572]
- [mm] extend KSM refcounts to the anon_vma root (Andrea Arcangeli) [556572]
- [mm] always lock the root (oldest) anon_vma (Andrea Arcangeli) [556572]
- [mm] track the root (oldest) anon_vma (Andrea Arcangeli) [556572]
- [mm] change direct call of spin_lock(anon_vma->lock) to inline function (Andrea Arcangeli) [556572]
- [mm] rename anon_vma_lock to vma_lock_anon_vma (Andrea Arcangeli) [556572]
- [mm] rmap: remove anon_vma check in page_address_in_vma() (Andrea Arcangeli) [556572]
- [mm] mmap: check ->vm_ops before dereferencing (Andrea Arcangeli) [556572]
- [fs] xfs_export_operations.commit_metadata (Christoph Hellwig) [585442]
- [fs] xfs: fix inode pincount check in fsync (Christoph Hellwig) [585442]
- [fs] xfs: miscellaneous fixes from 2.6.34 (Dave Chinner) [585442]
- [fs] xfs: reserved block pool and ENOSPC fixes from 2.6.34 (Dave Chinner) [542712 585442]
- [fs] xfs: delayed write metadata from 2.6.34 (Dave Chinner) [585442]
- [lib] introduce list_sort (Dave Chinner) [585442]
- [fs] xfs: log fixes from 2.6.34 (Dave Chinner) [585442]
- [fs] xfs: quota changes from 2.6.34 (Dave Chinner) [585442]
- [fs] xfs: buffer API cleanups from 2.6.34 (Dave Chinner) [585442]
- [fs] xfs: AG indexing fixes from 2.6.34 (Dave Chinner) [585442]
- [fs] xfs: idle kernel thread fixes from 2.6.34 (Dave Chinner) [585442]
- [fs] online defrag fixes from 2.6.34 (Dave Chinner) [585442]
- [fs] jbd2: delay discarding buffers in journal_unmap_buffer (Eric Sandeen) [593082]
- [fs] ext4: Use slab allocator for sub-page sized allocations (Eric Sandeen) [593082]
- [fs] jbd2: don't use __GFP_NOFAIL in journal_init_common() (Eric Sandeen) [593082]
- [fs] jbd: jbd-debug and jbd2-debug should be writable (Eric Sandeen) [593082]
- [fs] ext4: Fixed inode allocator to correctly track a flex_bg's used_dirs (Eric Sandeen) [593082]
- [fs] ext4: Fix estimate of # of blocks needed to write indirect-mapped files (Eric Sandeen) [593082]
- [fs] ext4: fix up rb_root initializations to use RB_ROOT (Eric Sandeen) [593082]
- [fs] ext4: Release page references acquired in ext4_da_block_invalidatepages (Eric Sandeen) [593082]
- [fs] ext4: make "offset" consistent in ext4_check_dir_entry() (Eric Sandeen) [593082]
- [fs] ext4: Convert BUG_ON checks to use ext4_error() instead (Eric Sandeen) [593082]
- [fs] ext4: Handle non empty on-disk orphan link (Eric Sandeen) [593082]
- [fs] ext4: explicitly remove inode from orphan list after failed direct io (Eric Sandeen) [593082]
- [fs] ext4: Fix fencepost error in chosing choosing group vs file preallocation (Eric Sandeen) [593082]
- [fs] ext4: Fix BUG_ON at fs/buffer.c:652 in no journal mode (Eric Sandeen) [593082]
- [fs] ext4: correctly calculate number of blocks for fiemap (Eric Sandeen) [593082]
- [fs] ext4: add missing error checking to ext4_expand_extra_isize_ea() (Eric Sandeen) [593082]
- [fs] ext4: move __func__ into a macro for ext4_warning, ext4_error (Eric Sandeen) [593082]
- [fs] ext4: Use bitops to read/modify EXT4_I(inode)->i_state (Eric Sandeen) [593082]
- [fs] ext4: Drop EXT4_GET_BLOCKS_UPDATE_RESERVE_SPACE flag (Eric Sandeen) [593082]
- [fs] ext4: return correct wbc.nr_to_write in ext4_da_writepages (Eric Sandeen) [593082]
- [fs] ext4: replace BUG() with return -EIO in ext4_ext_get_blocks (Eric Sandeen) [593082]
- [virt] KVM SVM Implement workaround for Erratum 383 (Bhavna Sarathy) [592311]
- [virt] KVM SVM Handle MCEs early in the vmexit process (Bhavna Sarathy) [592311]
- [usb] serial: ftdi: add CONTEC vendor and product id (Stanislaw Gruszka) [584757]
- [usb] fix usbfs regression (Stanislaw Gruszka) [584757]
- [usb] add new ftdi_sio device ids (Stanislaw Gruszka) [580067]
- [usb] ftdi_sio: add device IDs (several ELV, one Mindstorms NXT) (Stanislaw Gruszka) [580067]
- [usb] ftdi_sio: new device id for papouch AD4USB (Stanislaw Gruszka) [580067]
- [v4l] gspca_mr973010a: Fix cif type 1 cameras not streaming on UHCI controllers (Stanislaw Gruszka) [580067]
- [v4l] DVB: Add support for Asus Europa Hybrid DVB-T card (Stanislaw Gruszka) [580063]
- [usb] mos7840: add device IDs for B&B electronics devices (Stanislaw Gruszka) [580063]
- [ppc64] fsl: Add PCI device ids for new QoirQ chips (Stanislaw Gruszka) [580063]
- [fs] vfs: Fix vmtruncate() regression (Stanislaw Gruszka) [579693]
- [kernel] sched: Fix task priority bug (Stanislaw Gruszka) [579693]
- [serial] 8250_pnp: add a new Fujitsu Wacom Tablet PC device (Stanislaw Gruszka) [579693]
- [i2c] pca: Don't use *_interruptible (Stanislaw Gruszka) [579693]
- [i2c] Do not use device name after device_unregister (Stanislaw Gruszka) [579693]
- [kernel] sched: Fix cpu_clock() in NMIs, on !CONFIG_HAVE_UNSTABLE_SCHED_CLOCK (Stanislaw Gruszka) [579693]
- [hid] add device IDs for new model of Apple Wireless Keyboard (Stanislaw Gruszka) [579693]
- [v4l] gspca: sn9c20x: Fix test of unsigned (Stanislaw Gruszka) [579693]
- [x86] SGI UV: Fix mapping of MMIO registers (Stanislaw Gruszka) [579693]
- [perf] timechart: Use tid not pid for COMM change (Stanislaw Gruszka) [580062]
- [usb] fix usbstorage for 2770:915d delivers no FAT (Stanislaw Gruszka) [580062]
- [x86] PCI/PAT: return EINVAL for pci mmap WC request for !pat_enabled (Stanislaw Gruszka) [580062]
- [acpi] EC: Add wait for irq storm (Stanislaw Gruszka) [580062]
- [acpi] EC: Accelerate query execution (Stanislaw Gruszka) [580062]
- [usb] add speed values for USB 3.0 and wireless controllers (Stanislaw Gruszka) [580062]
- [usb] add missing delay during remote wakeup (Stanislaw Gruszka) [580062]
- [usb] EHCI & UHCI: fix race between root-hub suspend and port resume (Stanislaw Gruszka) [580062]
- [usb] EHCI: fix handling of unusual interrupt intervals (Stanislaw Gruszka) [580062]
- [usb] Don't use GFP_KERNEL while we cannot reset a storage device (Stanislaw Gruszka) [580062]
- [usb] serial: fix memory leak in generic driver (Stanislaw Gruszka) [580062]
- [char] nozomi: quick fix for the close/close bug (Stanislaw Gruszka) [580062]
- [tty] fix race in tty_fasync (Stanislaw Gruszka) [580062]
- [netdrv] netiucv: displayed TX bytes value much too high (Stanislaw Gruszka) [580063]
- [block] md: fix small irregularity with start_ro module parameter (Stanislaw Gruszka) [580063]
- [input] i8042: add Dritek quirk for Acer Aspire 5610 (Stanislaw Gruszka) [580063]
- [hid] fixup quirk for NCR devices (Stanislaw Gruszka) [580063]
- [dmi] allow omitting ident strings in DMI tables (Stanislaw Gruszka) [580063]
- [scsi] scsi_dh: create sysfs file, dh_state for all SCSI disk devices (Stanislaw Gruszka) [580063]
- [nfs] Revert default r/wsize behavior (Stanislaw Gruszka) [580063]
- [usb] SIS USB2VGA DRIVER: support KAIREN's USB VGA adaptor USB20SVGA-MB-PLUS (Stanislaw Gruszka) [580067]
- [input] alps: add support for the touchpad on Toshiba Tecra A11-11L (Stanislaw Gruszka) [584757]
- [fs] gfs2: stuck in inode wait, no glocks stuck (Robert S Peterson) [583737]
- [netdrv] cnic: update to to 2.1.1 (Stanislaw Gruszka) [590019]
- [netdrv] bnx2x: fix system hung after netdev watchdog (Stanislaw Gruszka) [581907]
- [netdrv] bnx2: Fix most severe bugs in bnx2 2.0.8+ (John Feeney) [590879]
- [netdrv] Update bnx2 driver to 2.0.8 and fw to mips-06-5.0.0.j6 et al (John Feeney) [464728]
- [virt] VMware Balloon driver (Amit Shah) [582826]
- [x86] With Sandybridge graphics, kernel reboots unless 'agp=off' used on command line (John Villalovos) [591294]
- [kernel] unify string representation of NULL in vsprintf.c (Dave Anderson) [589613]
- [kernel] coredump: fix the page leak in dump_seek() (Oleg Nesterov) [580126]
- [edac] EDAC support for Nehalem Memory Controllers (Mauro Carvalho Chehab) [584507]
- [iscsi] Include support for next gen Dell iSCSI PowerVault controller MD36xxi into RDAC scsi device handler's device list (Shyam Iyer) [593814]
- [scsi] lpfc Update from 8.3.5.9 to 8.3.5.13 FC/FCoE (Rob Evers) [591648]
- [infiniband] iser: fix failover slowdown (Mike Christie) [589174]
- [net] TCP: avoid to send keepalive probes if receiving data (Flavio Leitner) [593052]
- [nfs] commit_metadata export operation replacing nfsd_sync_dir (Christoph Hellwig) [593652]
- [ppc64] numa: Add form 1 NUMA affinity (Steve Best) [593466]
- [ppc64] eeh: Fix a bug when pci structure is null (Steve Best) [593854]
- [ppc64] perf_event: Fix oops due to perf_event_do_pending call (Steve Best) [593464]
- [ppc] pseries: Quieten cede latency printk (Steve Best) [591739]
- [fs] GFS2: Don't "get" xattrs for ACLs when ACLs are turned off (Steven Whitehouse) [546294]
- [kexec] fix OOPS in crash_kernel_shrink (Steve Best) [592336]
- [fs] ext4: don't use quota reservation for speculative metadata blocks (Eric Sandeen) [587095]
- [fs] quota: add the option to not fail with EDQUOT in block allocation (Eric Sandeen) [587095]
- [fs] quota: use flags interface for dquot alloc/free space (Eric Sandeen) [587095]
- [fs] ext4: Fix quota accounting error with fallocate (Eric Sandeen) [587095]
- [fs] ext4: Ensure zeroout blocks have no dirty metadata (Eric Sandeen) [587095]
- [virt] vhost-net: utilize PUBLISH_USED_IDX feature (Michael S. Tsirkin) [593158]
- [virt] virtio: put last seen used index into ring itself (Michael S. Tsirkin) [593158]
- [virt] vhost: fix barrier pairing (Michael S. Tsirkin) [593158]
- [virt] virtio: use smp_XX barriers on SMP (Michael S. Tsirkin) [593158]
- [virt] virtio_ring: remove a level of indirection (Michael S. Tsirkin) [593158]
- [virt] trans_virtio: use virtqueue_xxx wrappers (Michael S. Tsirkin) [593158]
- [virt] virtio-rng: use virtqueue_xxx wrappers (Michael S. Tsirkin) [593158]
- [virt] virtio_net: use virtqueue_xxx wrappers (Michael S. Tsirkin) [593158]
- [virt] virtio_blk: use virtqueue_xxx wrappers (Michael S. Tsirkin) [593158]
- [virt] virtio_console: use virtqueue_xxx wrappers (Michael S. Tsirkin) [593158]
- [virt] virtio_balloon: use virtqueue_xxx wrappers (Michael S. Tsirkin) [593158]
- [virt] virtio: add virtqueue_ vq_ops wrappers (Michael S. Tsirkin) [593158]
- [virt] vhost-net: fix vq_memory_access_ok error checking (Michael S. Tsirkin) [593158]
- [virt] vhost: fix error handling in vring ioctls (Michael S. Tsirkin) [593158]
- [virt] vhost: fix interrupt mitigation with raw sockets (Michael S. Tsirkin) [593158]
- [virt] vhost: fix error path in vhost_net_set_backend (Michael S. Tsirkin) [593158]
- [netdrv] iwlwifi: iwl_good_ack_health() only apply to AGN device (John Linville) [573029]
- [netdrv] iwlwifi: code cleanup for connectivity recovery (John Linville) [573029]
- [netdrv] iwlwifi: Recover TX flow failure (John Linville) [573029]
- [netdrv] iwlwifi: move plcp check to separated function (John Linville) [573029]
- [netdrv] iwlwifi: Recover TX flow stall due to stuck queue (John Linville) [573029]
- [netdrv] iwlwifi: add internal short scan support for 3945 (John Linville) [573029]
- [netdrv] iwlwifi: separated time check for different type of force reset (John Linville) [573029]
- [netdrv] iwlwifi: Adjusting PLCP error threshold for 1000 NIC (John Linville) [573029]
- [netdrv] iwlwifi: multiple force reset mode (John Linville) [573029]
- [netdrv] iwlwifi: Tune radio to prevent unexpected behavior (John Linville) [573029]
- [netdrv] iwlwifi: Logic to control how frequent radio should be reset if needed (John Linville) [573029]
- [netdrv] iwlwifi: add function to reset/tune radio if needed (John Linville) [573029]
- [netdrv] iwlwifi: clear all the stop_queue flag after load firmware (John Linville) [573029]
- [netdrv] iwlwifi: check for aggregation frame and queue (John Linville) [573029]
- [ppc64] kdump: Fix race in kdump shutdown (Steve Best) [559709]
- [ppc64] kexec: Fix race in kexec shutdown (Steve Best) [593853]
- [net] Add ndo_{set|get}_vf_port support for enic dynamic vnics (Chris Wright) [581087]
- [net] Add netlink support for virtual port management (was iovnl) (Chris Wright) [581087]
- [net] core: add IFLA_STATS64 support (Chris Wright) [581087]
- [netdrv] igb: support for VF configuration tools (Chris Wright) [581087]
- [net] rtnetlink: Add SR-IOV VF configuration methods (Chris Wright) [581087]
- [pci] Add SR-IOV convenience functions and macros (Chris Wright) [581087]
- [scsi] sync iscsi layer (Mike Christie) [564148 570682]

* Thu May 20 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-28.el6]
- [mm] New round-robin rotor for SLAB allocations (Larry Woodman) [593154]
- [netdrv] ixgbe: FCoE fixes (Andy Gospodarek) [593474]
- [net] vlan: updates vlan real_num_tx_queues (Andy Gospodarek) [593474]
- [net] vlan: adds vlan_dev_select_queue (Andy Gospodarek) [593474]
- [net] vlan: Precise RX stats accounting (Andy Gospodarek) [593474]
- [net] add dev_txq_stats_fold() helper (Andy Gospodarek) [593474]
- [net] vlan: Add support to netdev_ops.ndo_fcoe_get_wwn for VLAN device (Andy Gospodarek) [593474]
- [netdrv] ixgbe: fixes for link problems, possible DMA errors, and VF/SR-IOV changes (Andy Gospodarek) [575188]
- [sound] ALSA HDA driver update 2010-05-11 (Jaroslav Kysela) [591083]
- [mm] show per-process swap usage via procfs (Larry Woodman) [546533]
- [netdrv] cxgb3 won't recover from EEH event twice (Steve Best) [591738]
- [virt] x86, cpu: Print AMD virtualization features in /proc/cpuinfo (Gleb Natapov) [592688]
- [x86] Intel ICH9 workaround for HPET timer issue on IbexPeak Platform (Luming Yu) [502629]
- [pci] Update pci_dev and pci_bus structs before kabi freeze (Prarit Bhargava) [593322]
- [pci] Output FW warning in pci_read/write_vpd (Prarit Bhargava) [586979]
- [infiniband] ehca: Require in_wc in process_mad() (Steve Best) [593095]
- [security] mmap_min_addr check CAP_SYS_RAWIO only for write (Eric Paris) [592417]
- [scsi] aacraid: Eliminate use after free (Tomas Henzl) [592926]
- [scsi] lpfc Update from 8.3.5.7 to 8.3.5.9 FC/FCoE (Rob Evers) [580677]
- [char] Eliminate use after free (Amit Shah) [593189]
- [ipmi] fix unlock balance (Tomas Henzl) [592925]
- [ppc64] only call start-cpu when a CPU is stopped (Steve Best) [592440]
- [ppc64] make query_cpu_stopped callable outside hotplug cpu (Steve Best) [592440]
- [kernel] cpufreq: make the iowait-is-busy-time a sysfs tunable (Rik van Riel) [585330]
- [kernel] ondemand: Solve the big performance issue with ondemand during disk IO (Rik van Riel) [585330]
- [kernel] sched: introduce get_cpu_iowait_time_us() (Rik van Riel) [585330]
- [kernel] sched: eliminate the ts->idle_lastupdate field (Rik van Riel) [585330]
- [kernel] sched: fold updating of the last update time into update_ts_time_stats() (Rik van Riel) [585330]
- [kernel] sched: update the idle statistics in get_cpu_idle_time_us (Rik van Riel) [585330]
- [kernel] sched: introduce a function to update the idle statistics (Rik van Riel) [585330]
- [kernel] sched: add a comment to get_cpu_idle_time_us (Rik van Riel) [585330]
- [kernel] nohz: Reuse ktime in sub-functions of tick_check_idle (Rik van Riel) [585330]
- [virt] Xen PV-on-HVM: Disable xen-blkfront for IDE & SCSI devices (Don Dutile) [523134]
- [virt] xen: PV-on-HVM: Disable xen-blkfront for PV-on-HVM for now (Don Dutile) [523134]
- [virt] xen: PV-on-HVM: Prevent pv drivers from crashing a FV guest if pv-on-hvm not configured (Don Dutile) [523134]
- [virt] xen: PV-on-HVM: Add kernel command line enablement control (Don Dutile) [523134]
- [virt] xen: backport PV-on-HVM (Don Dutile) [523134]
- [ppc] pseries: Pass more accurate number of supported cores to firmware (Steve Best) [591341]
- [ppc] Add static fields to ibm, client-architecture call (Steve Best) [591341]
- [kernel] mutex: Fix optimistic spinning vs. BKL (Steve Best) [591735]
- [kernel] mutex: Don't spin when the owner CPU is offline or other weird cases (Steve Best) [591735]
- [kernel] sched: Don't use possibly stale sched_class (Stanislaw Gruszka) [580067]
- [usb] unusual_devs: Add support for multiple Option 3G sticks (Stanislaw Gruszka) [580067]
- [usb] cp210x: Add 81E8 Zephyr Bioharness (Stanislaw Gruszka) [580067]
- [usb] serial: ftdi: add CONTEC vendor and product id (Stanislaw Gruszka) [580067]
- [usb] ftdi_sio: sort PID/VID entries in new ftdi_sio_ids.h header (Stanislaw Gruszka) [580067]
- [usb] ftdi_sio: isolate all device IDs to new ftdi_sio_ids.h header (Stanislaw Gruszka) [580067]
- [usb] Move hcd free_dev call into usb_disconnect to fix oops (Stanislaw Gruszka) [580067]
- [usb] remove debugging message for uevent constructions (Stanislaw Gruszka) [580067]
- [usb] fix crash in uhci_scan_schedule (Stanislaw Gruszka) [580067]
- [usb] fix the idProduct value for USB-3.0 root hubs (Stanislaw Gruszka) [580067]
- [usb] xhci: Fix finding extended capabilities registers (Stanislaw Gruszka) [580067]
- [x86] Fix SCI on IOAPIC != 0 (Stanislaw Gruszka) [580067]
- [x86] Avoid race condition in pci_enable_msix() (Stanislaw Gruszka) [580067]
- [x86] thinkpad-acpi: make driver events work in NVRAM poll mode (Stanislaw Gruszka) [580067]
- [x86] thinkpad-acpi: document HKEY event 3006 (Stanislaw Gruszka) [580067]
- [x86] thinkpad-acpi: R52 brightness_mode has been confirmed (Stanislaw Gruszka) [580067]
- [x86] thinkpad-acpi: fix poll thread auto-start (Stanislaw Gruszka) [580067]
- [net] scm: Only support SCM_RIGHTS on unix domain sockets. (Stanislaw Gruszka) [580067]
- [usb] serial: sierra driver indat_callback fix (Stanislaw Gruszka) [580067]
- [tty] Fix the ldisc hangup race (Stanislaw Gruszka) [580067]
- [kernel] devtmpfs: reset inode permissions before unlinking (Stanislaw Gruszka) [580067]
- [kernel] driver-core: fix race condition in get_device_parent() (Stanislaw Gruszka) [580067]
- [pm] hibernate: Fix preallocating of memory (Stanislaw Gruszka) [580067]
- [tpm] tpm_tis: TPM_STS_DATA_EXPECT workaround (Stanislaw Gruszka) [580067]
- [fs] Switch proc/self to nd_set_link() (Stanislaw Gruszka) [580067]
- [hid] usbhid: introduce timeout for stuck ctrl/out URBs (Stanislaw Gruszka) [580067]
- [hid] add multi-input quirk for NextWindow Touchscreen (Stanislaw Gruszka) [580067]
- [hid] remove TENX iBuddy from blacklist (Stanislaw Gruszka) [580067]
- [fs] vfs: take f_lock on modifying f_mode after open time (Stanislaw Gruszka) [580067]
- [acpi] thinkpad-acpi: wrong thermal attribute_group removed in thermal_exit() (Stanislaw Gruszka) [580067]
- [acpi] fix "acpi=ht" boot option (Stanislaw Gruszka) [580067]
- [acpi] remove Asus P2B-DS from acpi=ht blacklist (Stanislaw Gruszka) [580067]
- [pci] hotplug: check ioremap() return value in ibmphp_ebda.c (Stanislaw Gruszka) [580067]
- [pci] hotplug: ibmphp: read the length of ebda and map entire ebda region (Stanislaw Gruszka) [580067]
- [x86] msr/cpuid: Pass the number of minors when unregistering MSR and CPUID drivers (Stanislaw Gruszka) [580063]
- [fs] fnctl: f_modown should call write_lock_irqsave/restore (Stanislaw Gruszka) [580063]
- [sound] ASoC: fix a memory-leak in wm8903 (Stanislaw Gruszka) [580063]
- [mtd] UBI: initialise update marker (Stanislaw Gruszka) [580063]
- [mtd] UBI: fix memory leak in update path (Stanislaw Gruszka) [580063]
- [ipc] ns: fix memory leak (idr) (Stanislaw Gruszka) [580063]
- [input] i8042: remove identification strings from DMI tables (Stanislaw Gruszka) [580063]
- [netdrv] starfire: clean up properly if firmware loading fails (Stanislaw Gruszka) [580064]
- [kernel] random: drop weird m_time/a_time manipulation (Stanislaw Gruszka) [580064]
- [kernel] random: Remove unused inode variable (Stanislaw Gruszka) [580064]
- [mm] purge fragmented percpu vmap blocks (Stanislaw Gruszka) [580064]
- [mm] percpu-vmap fix RCU list walking (Stanislaw Gruszka) [580064]
- [x86] Add quirk for Intel DG45FC board to avoid low memory corruption (Stanislaw Gruszka) [580064]
- [regulator] Specify REGULATOR_CHANGE_STATUS for WM835x LED constraints (Stanislaw Gruszka) [580064]
- [x86] Add Dell OptiPlex 760 reboot quirk (Stanislaw Gruszka) [580064]
- [mm] fix migratetype bug which slowed swapping (Stanislaw Gruszka) [580064]
- [input] winbond-cir: remove dmesg spam (Stanislaw Gruszka) [580064]
- [acpi] Advertise to BIOS in _OSC: _OST on _PPC changes (Stanislaw Gruszka) [580064]
- [infiniband] Fix failure exit in ipathfs (Stanislaw Gruszka) [580064]
- [acpi] fix OSC regression that caused aer and pciehp not to load (Stanislaw Gruszka) [580064]
- [acpi] Add platform-wide _OSC support (Stanislaw Gruszka) [580064]
- [acpi] Add a generic API for _OSC (Stanislaw Gruszka) [580064]
- [s390x] fix single stepped svcs with TRACE_IRQFLAGS=y (Stanislaw Gruszka) [580064]
- [fs] sysfs: sysfs_sd_setattr set iattrs unconditionally (Stanislaw Gruszka) [580065]
- [acpi] fix High cpu temperature with 2.6.32 (Stanislaw Gruszka) [580065]
- [usb] usbfs: properly clean up the as structure on error paths (Stanislaw Gruszka) [580065]
- [kernel] class: Free the class private data in class_release (Stanislaw Gruszka) [580065]
- [serial] 8250: add serial transmitter fully empty test (Stanislaw Gruszka) [580065]
- [rtc] rtc-fm3130: add missing braces (Stanislaw Gruszka) [580065]
- [ata] Call flush_dcache_page after PIO data transfers in libata-sff.c (Stanislaw Gruszka) [580065]
- [net] dst: call cond_resched() in dst_gc_task() (Stanislaw Gruszka) [580065]
- [crypto] padlock-sha: Add import/export support (Stanislaw Gruszka) [580065]
- [x86] dell-wmi, hp-wmi: check wmi_get_event_data() return value (Stanislaw Gruszka) [580065]
- [tpm] tpm_infineon: fix suspend/resume handler for pnp_driver (Stanislaw Gruszka) [580065]
- [usb] ftdi_sio: add USB device ID's for B&B Electronics line (Stanislaw Gruszka) [580063]
- [fs] anon_inode: set S_IFREG on the anon_inode (Eric Paris) [591813]

* Tue May 18 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-27.el6]
- [ppc] pseries: Flush lazy kernel mappings after unplug operations (Steve Best) [591340]
- [fs] ext3: enable barriers by default (Eric Sandeen) [586062]
- [tracing] regset xstate extensions + generic PTRACE_{GET,SET}REGSET support (Oleg Nesterov) [587724]
- [scsi] hpsa: update to 2.0.2 (Tomas Henzl) [587418]
- [mm] Print more information about the task being OOM killed (Larry Woodman) [546533]
- [netdrv] igb/igbvf: use netdev_alloc_skb_ip_align() (Stefan Assmann) [589497]
- [acpi] Fix regression where _PPC is not read at boot even when ignore_ppc=0 (Matthew Garrett) [571893]
- [x86] i386: Do a global tlb flush on S4 resume (Matthew Garrett) [572818]
- [pci] Add ABI for PCI runtime power management (Matthew Garrett) [589781]
- [block] Fix regression in O_DIRECT|O_SYNC writes to block devices (Jeff Moyer) [582628]
- [kernel] add skip_spaces() implementation (Jaroslav Kysela) [591078]
- [kernel] sched: cpuacct: Use bigger percpu counter batch values for stats counters (Steve Best) [591343]
- [kernel] idr: fix a critical misallocation bug (Eric Paris) [582109]
- [net] tcp: Fix OOB POLLIN avoidance (Oleg Nesterov) [584786]
- [s390x] qeth: synchronize configuration interface (Hendrik Brueckner) [586962]
- [fs] inotify: race use after free/double free in inotify inode marks (Eric Paris) [582109]
- [fs] ext4: Add flag to files with blocks intentionally past EOF (Eric Sandeen) [578562]
- [drm] backport patches up to 2.6.34-rc7 (Adam Jackson) [589792]
- [kernel] elf coredump: add extended numbering support (Amerigo Wang) [578659]
- [kernel] binfmt_elf_fdpic: Fix build breakage introduced by coredump changes. (Amerigo Wang) [578659]
- [kernel] elf coredump: make offset calculation process and writing process explicit (Amerigo Wang) [578659]
- [kernel] elf coredump: replace ELF_CORE_EXTRA_* macros by functions (Amerigo Wang) [578659]
- [kernel] coredump: move dump_write() and dump_seek() into a header file (Amerigo Wang) [578659]
- [kernel] coredump: unify dump_seek() implementations for each binfmt_*.c (Amerigo Wang) [578659]
- [mm] introduce coredump parameter structure (Amerigo Wang) [578659]
- [powerpc] Reduce printk from pseries_mach_cpu_die() (Steve Best) [590754]
- [powerpc] Move checks in pseries_mach_cpu_die() (Steve Best) [590754]
- [powerpc] Reset kernel stack on cpu online from cede state (Steve Best) [590754]
- [virt] don't compute pvclock adjustments if we trust the tsc (Glauber Costa) [569603]
- [virt] Try using new kvm clock msrs (Glauber Costa) [569603]
- [virt] Add a global synchronization point for pvclock (Glauber Costa) [569603]
- [virt] Enable pvclock flags in vcpu_time_info structure (Glauber Costa) [569603]
- [virt] Tell the guest we'll warn it about tsc stability (Glauber Costa) [592296]
- [virt] export paravirtual cpuid flags in KVM_GET_SUPPORTED_CPUID (Glauber Costa) [592296]
- [virt] add new KVMCLOCK cpuid feature (Glauber Costa) [592296]
- [virt] change msr numbers for kvmclock (Glauber Costa) [592296]
- [scsi] enclosure: fix oops while iterating enclosure_status array (Stanislaw Gruszka) [580062]
- [usb] fix bitmask merge error (Stanislaw Gruszka) [580062]
- [acpi] enable C2 and Turbo-mode on Nehalem notebooks on A/C (Stanislaw Gruszka) [580063]
- [input] i8042: add Gigabyte M1022M to the noloop list (Stanislaw Gruszka) [580063]
- [kernel] nohz: Prevent clocksource wrapping during idle (Stanislaw Gruszka) [580063]
- [kernel] sched: Fix missing sched tunable recalculation on cpu add/remove (Stanislaw Gruszka) [580063]
- [netdrv] atl1c: use common_task instead of reset_task and link_chg_task (Stanislaw Gruszka) [580063]
- [netdrv] atl1e: disable NETIF_F_TSO6 for hardware limit (Stanislaw Gruszka) [580063]
- [kernel] driver-core: fix devtmpfs crash on s390 (Stanislaw Gruszka) [580063]
- [kernel] devtmpfs: set root directory mode to 0755 (Stanislaw Gruszka) [580063]
- [input] ALPS: add interleaved protocol support for Dell E6x00 series (Stanislaw Gruszka) [580063]
- [mm] flush dcache before writing into page to avoid alias (Stanislaw Gruszka) [580064]
- [block] pktcdvd: removing device does not remove its sysfs dir (Stanislaw Gruszka) [580064]
- [mm] add new 'read_cache_page_gfp()' helper function (Stanislaw Gruszka) [580064]
- [acpi] Add NULL pointer check in acpi_bus_start (Stanislaw Gruszka) [580065]
- [usb] usbfs: only copy the actual data received (Stanislaw Gruszka) [580065]
- [net] netfilter: xtables: compat out of scope fix (Stanislaw Gruszka) [580065]
- [net] pktgen: Fix freezing problem (Stanislaw Gruszka) [580065]

* Thu May 13 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-26.el6]
- [scsi] Sync fcoe to upsteam (Mike Christie) [590781]
- [netdrv] bnx2x: fix memory barrier (Stanislaw Gruszka) [580477]
- [x86] kprobes: fix removed int3 checking order (Dave Anderson) [585400]
- [net] fix oops at bootime in sysctl code (Stanislaw Gruszka) [580064]
- [net] af_packet: Don't use skb after dev_queue_xmit() (Stanislaw Gruszka) [580064]
- [net] restore ip source validation (Stanislaw Gruszka) [580064]
- [net] tcp: update the netstamp_needed counter when cloning sockets (Stanislaw Gruszka) [580064]
- [net] icmp: send fragment reassembly timeout w/ conntrack enabled (Neil Horman) [563175]
- [fs] GFS2: stuck in inode wait, no glocks stuck (Robert S Peterson) [583737]
- [mm] compcache: Backport compcache: ramzswap documentation (Jerome Marchand) [578641]
- [mm] compcache: xvmalloc memory allocator (Jerome Marchand) [578641]
- [mm] compcache: virtual block device driver (ramzswap) (Jerome Marchand) [578641]
- [mm] readahead: fix NULL filp dereference (Josef Bacik) [591055]
- [netdrv] tg3: 57780 and 5785 devices refuse to attach (Andy Gospodarek) [564117]
- [x86] Fetch valid frequencies for powernow_k8.o from ACPI _PST table (Bhavna Sarathy) [464630]
- [s390x] ptrace: fix return value of do_syscall_trace_enter() (Hendrik Brueckner) [588216]
- [fs] gfs2: fix oops while copying from ext3 to gfs2 (Abhijith Das) [586009] {CVE-2010-1436}
- [virt] virtio: console: Accept console size along with resize control message (Amit Shah) [589307]
- [virt] virtio: console: Store each console's size in the console structure (Amit Shah) [589307]
- [virt] virtio: console: Resize console port 0 on config intr only if multiport is off (Amit Shah) [589307]
- [sound] ac97: Add IBM ThinkPad R40e to Headphone/Line Jack Sense blacklist (Stanislaw Gruszka) [584757]
- [sound] ac97: Add Toshiba P500 to ac97 jack sense blacklist (Stanislaw Gruszka) [584757]
- [x86] amd: Restrict usage of c1e_idle() (Stanislaw Gruszka) [584757]
- [x86] Fix placement of FIX_OHCI1394_BASE (Stanislaw Gruszka) [584757]
- [net] netfilter: xt_recent: fix regression in rules using a zero hit_count (Stanislaw Gruszka) [584757]
- [kernel] softlockup: Stop spurious softlockup messages due to overflow (Stanislaw Gruszka) [584757]
- [kernel] cpuset: fix the problem that cpuset_mem_spread_node() returns an offline node (Stanislaw Gruszka) [584757]
- [pci] cleanup error return for pcix get and set mmrbc functions (Stanislaw Gruszka) [584757]
- [pci] fix access of PCI_X_CMD by pcix get and set mmrbc functions (Stanislaw Gruszka) [584757]
- [pci] fix return value from pcix_get_max_mmrbc() (Stanislaw Gruszka) [584757]
- [net] if_tunnel.h: add missing ams/byteorder.h include (Stanislaw Gruszka) [584757]
- [netdrv] jme: Protect vlgrp structure by pause RX actions (Stanislaw Gruszka) [584757]
- [netdrv] jme: Fix VLAN memory leak (Stanislaw Gruszka) [584757]
- [usb] option: add support for a new CMOTECH device to usb/serial/option (Stanislaw Gruszka) [584757]
- [usb] option: move hardcoded PID to a macro in usb/serial/option (Stanislaw Gruszka) [584757]
- [usb] option: fix incorrect manufacturer name in usb/serial/option: MAXON->CMOTECH (Stanislaw Gruszka) [584757]
- [usb] xHCI: re-initialize cmd_completion (Stanislaw Gruszka) [584757]
- [usb] EHCI: adjust ehci_iso_stream for changes in ehci_qh (Stanislaw Gruszka) [584757]
- [usb] EHCI: fix ITD list order (Stanislaw Gruszka) [584757]
- [tty] Take a 256 byte padding into account when buffering below sub-page units (Stanislaw Gruszka) [584757]
- [tty] Keep the default buffering to sub-page units (Stanislaw Gruszka) [584757]
- [mm] tmpfs: cleanup mpol_parse_str() (Stanislaw Gruszka) [584757]
- [perf] Make the install relative to DESTDIR if specified (Stanislaw Gruszka) [584757]
- [perf] perf_event: Fix oops triggered by cpu offline/online (Stanislaw Gruszka) [584757]
- [isdn] gigaset: prune use of tty_buffer_request_room (Stanislaw Gruszka) [584757]
- [isdn] gigaset: correct clearing of at_state strings on RING (Stanislaw Gruszka) [584757]
- [sound] hda: Disable MSI for Nvidia controller (Stanislaw Gruszka) [584757]
- [sound] hda: Fix 0 dB offset for HP laptops using CX20551 (Stanislaw Gruszka) [584757]
- [sound] hda: Fix secondary ADC of ALC260 basic model (Stanislaw Gruszka) [584757]
- [virt] virtio: fix out of range array access (Stanislaw Gruszka) [584757]
- [ipc] mqueue: fix mq_open() file descriptor leak on user-space processes (Stanislaw Gruszka) [584757]
- [security] sysctl: require CAP_SYS_RAWIO to set mmap_min_addr (Stanislaw Gruszka) [584757]
- [kernel] sched: Mark boot-cpu active before smp_init() (Stanislaw Gruszka) [584757]
- [pci] add support for 82576NS serdes to existing SR-IOV quirk (Stanislaw Gruszka) [584757]
- [v4l] DVB: em28xx-dvb: fix memleak in dvb_fini() (Stanislaw Gruszka) [584757]
- [pci] unconditionally clear AER uncorr status register during cleanup (Stanislaw Gruszka) [584757]
- [tracing] Do not record user stack trace from NMI context (Stanislaw Gruszka) [584757]
- [tracing] Disable buffer switching when starting or stopping trace (Stanislaw Gruszka) [584757]
- [tracing] Use same local variable when resetting the ring buffer (Stanislaw Gruszka) [584757]
- [tracing] function-graph: Init curr_ret_stack with ret_stack (Stanislaw Gruszka) [584757]
- [tracing] ring-buffer: Move disabled check into preempt disable section (Stanislaw Gruszka) [584757]
- [input] i8042: add ALDI/MEDION netbook E1222 to qurik reset table (Stanislaw Gruszka) [584757]
- [net] netfilter: xt_recent: fix false match (Stanislaw Gruszka) [580067]
- [net] netfilter: xt_recent: fix buffer overflow (Stanislaw Gruszka) [580067]
- [tracing] oprofile/x86: fix msr access to reserved counters (Stanislaw Gruszka) [580067]
- [tracing] oprofile/x86: use kzalloc() instead of kmalloc() (Stanislaw Gruszka) [580067]
- [tracing] oprofile/x86: remove node check in AMD IBS initialization (Stanislaw Gruszka) [580067]
- [tracing] oprofile: remove tracing build dependency (Stanislaw Gruszka) [580067]
- [x86] oprofile: fix perfctr nmi reservation for mulitplexing (Stanislaw Gruszka) [580067]
- [netdrv] via-rhine: Fix scheduling while atomic bugs (Stanislaw Gruszka) [580067]
- [net] ipv6: conntrack: Add member of user to nf_ct_frag6_queue structure (Stanislaw Gruszka) [580067]
- [net] Remove bogus IGMPv3 report handling (Stanislaw Gruszka) [580067]
- [net] sysfs: Use rtnl_trylock in wireless sysfs methods (Stanislaw Gruszka) [580067]
- [net] Fix sysctl restarts (Stanislaw Gruszka) [580067]
- [mm] slab: initialize unused alien cache entry as NULL at alloc_alien_cache() (Stanislaw Gruszka) [580067]
- [v4l] DVB: cxusb: Select all required frontend and tuner modules (Stanislaw Gruszka) [580067]
- [v4l] dvb: l64781.ko broken with gcc 4.5 (Stanislaw Gruszka) [580067]
- [v4l] DVB: uvcvideo: Fix controls blacklisting (Stanislaw Gruszka) [580063]
- [net] netfilter: nf_conntrack: fix hash resizing with namespaces (Stanislaw Gruszka) [580065]
- [net] netfilter: nf_conntrack: restrict runtime expect hashsize modifications (Stanislaw Gruszka) [580065]
- [net] netfilter: xtables: fix conntrack match v1 ipt-save output (Stanislaw Gruszka) [580063]
- [v4l] DVGB: DocBook/media: create links for included sources (Stanislaw Gruszka) [580063]
- [v4l] DVB: DocBook/media: copy images after building HTML (Stanislaw Gruszka) [580063]
- [v4l] DVB: dvb-core: fix initialization of feeds list in demux filter (Stanislaw Gruszka) [580065]
- [dma] ioat: fix infinite timeout checking in ioat2_quiesce (Stanislaw Gruszka) [580065]
- [v4l] DVB: smsusb: add autodetection support for five additional Hauppauge USB IDs (Stanislaw Gruszka) [580063]
- [x86] cpufreq: Fix use after free of struct powernow_k8_data (Stanislaw Gruszka) [580065]
- [regulator] Fix display of null constraints for regulators (Stanislaw Gruszka) [580065]

* Mon May 10 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-25.el6]
- [fs] exec: Fix 'flush_old_exec()/setup_new_exec()' split (Jiri Olsa) [586024] {CVE-2010-0307}
- [powerpc] TIF_ABI_PENDING bit removal (Jiri Olsa) [586024] {CVE-2010-0307}
- [x86] set_personality_ia32() misses force_personality32 (Jiri Olsa) [586024] {CVE-2010-0307}
- [x86] get rid of the TIF_ABI_PENDING bit (Jiri Olsa) [586024] {CVE-2010-0307}
- [kernel] split 'flush_old_exec' into two functions (Jiri Olsa) [586024] {CVE-2010-0307}
- [net] sctp: fix skb_over_panic from processing too many unknown params (Neil Horman) [584659] {CVE-2010-1173}
- [virt] kvm: fix vmx null pointer dereference (Eduardo Habkost) [570534] {CVE-2010-0435}
- [fs] gfs2: fix quota state reporting (Christoph Hellwig) [589945]
- [fs] gfs2: fix quota file size not a multiple of struct gfs2_quota (Abhijith Das) [589813]
- [x86] Use physical mode for IBM Summit platforms (John Villalovos) [558397]
- [mm] page allocator: update NR_FREE_PAGES only when necessary (Stanislaw Gruszka) [579693]
- [mm] memcg: ensure list is empty at rmdir (Stanislaw Gruszka) [579693]
- [video] revert "drivers/video/s3c-fb.c: fix clock setting for Samsung SoC Framebuffer" (Stanislaw Gruszka) [579693]
- [v4l] DVB: gspca - sunplus: Fix bridge exchanges (Stanislaw Gruszka) [580062]
- [hwmon] fschmd: Fix a memleak on multiple opens of /dev/watchdog (Stanislaw Gruszka) [580063]
- [sound] hda: Fix HP T5735 automute (Stanislaw Gruszka) [580063]
- [sound] hda: Fix quirk for Maxdata obook4-1 (Stanislaw Gruszka) [580063]
- [sound] ice1724: Patch for suspend/resume for ESI Juli@ (Stanislaw Gruszka) [580063]
- [sound] usb-audio: Avoid Oops after disconnect (Stanislaw Gruszka) [580065]
- [sound] ctxfi: fix PTP address initialization (Stanislaw Gruszka) [580065]
- [hwmon] lm78: Request I/O ports individually for probing (Stanislaw Gruszka) [580065]
- [hwmon] w83781d: Request I/O ports individually for probing (Stanislaw Gruszka) [580065]
- [hwmon] tmp421: Fix temperature conversions (Stanislaw Gruszka) [580067]
- [sound] via82xx: add quirk for D1289 motherboard (Stanislaw Gruszka) [580067]
- [hwmon] tmp421: Restore missing inputs (Stanislaw Gruszka) [580067]
- [sound] USB MIDI support for Access Music VirusTI (Stanislaw Gruszka) [580067]
- [sound] hda-intel: Add position_fix quirk for ASUS M2V-MX SE (Stanislaw Gruszka) [580067]
- [sound] pcm core: fix fifo_size channels interval check (Stanislaw Gruszka) [580067]
- [sound] hda: Use 3stack quirk for Toshiba Satellite L40-10Q (Stanislaw Gruszka) [580067]
- [bluetooth] Fix potential bad memory access with sysfs files (Stanislaw Gruszka) [584757]
- [hwmon] coretemp: Add missing newline to dev_warn() message (Stanislaw Gruszka) [584757]
- [bluetooth] Fix kernel crash on L2CAP stress tests (Stanislaw Gruszka) [584757]
- [input] wacom: ensure the device is initialized properly upon resume (Stanislaw Gruszka) [584757]
- [sound] hda: Fix input source elements of secondary ADCs on Realtek (Stanislaw Gruszka) [584757]
- [x86] nmi watchdog: use generic interrupt source to determine deadlocks (Don Zickus) [574570]
- [dm] eliminate some holes in data structures (Mike Snitzer) [586089]
- [dm] ioctl: introduce flag indicating uevent was generated (Mike Snitzer) [586089]
- [dm] free dm_io before bio_endio not after (Mike Snitzer) [586089]
- [dm] table: remove unused dm_get_device range parameters (Mike Snitzer) [586089]
- [dm] ioctl: only issue uevent on resume if state changed (Mike Snitzer) [586089]
- [dm] raid1: always return error if all legs fail (Mike Snitzer) [586089]
- [dm] mpath: refactor pg_init (Mike Snitzer) [586089]
- [dm] mpath: wait for pg_init completion when suspending (Mike Snitzer) [586089]
- [dm] mpath: hold io until all pg_inits completed (Mike Snitzer) [586089]
- [dm] mpath: avoid storing private suspended state (Mike Snitzer) [586089]
- [dm] document when snapshot has finished merging (Mike Snitzer) [586089]
- [dm] table: remove dm_get from dm_table_get_md (Mike Snitzer) [586089]
- [dm] mpath: skip activate_path for failed paths (Mike Snitzer) [586089]
- [dm] mpath: pass struct pgpath to pg init done (Mike Snitzer) [586089]
- [netdrv] mac80211: fix deferred hardware scan requests (John Linville) [561762]
- [x86] asus-laptop: add Lenovo SL hotkey support (Stanislaw Gruszka) [579693]
- [input] pmouse: move Sentelic probe down the list (Stanislaw Gruszka) [579693]
- [pci] cardbus: Add a fixup hook and fix powerpc (Stanislaw Gruszka) [579693]
- [mfd] Correct WM835x ISINK ramp time defines (Stanislaw Gruszka) [579693]
- [mfd] WM835x GPIO direction register is not locked (Stanislaw Gruszka) [579693]
- [edac] i5000_edac critical fix panic out of bounds (Stanislaw Gruszka) [579693]
- [i2c] i2c-tiny-usb: Fix on big-endian systems (Stanislaw Gruszka) [580065]
- [x86] thinkpad-acpi: fix bluetooth/wwan resume (Stanislaw Gruszka) [580067]
- [v4l] DVB: bttv: Move I2C IR initialization (Stanislaw Gruszka) [580067]
- [bluetooth] Fix sleeping function in RFCOMM within invalid context (Stanislaw Gruszka) [584757]
- [i2c] i2c-i801: Don't use the block buffer for I2C block writes (Stanislaw Gruszka) [584757]
- [s390x] vdso: use ntp adjusted clock multiplier (Hendrik Brueckner) [575728]
- [s390x] timekeeping: Fix clock_gettime vsyscall time warp (Hendrik Brueckner) [575728]
- [s390x] timekeeping: Fix accumulation bug triggered by long delay (Hendrik Brueckner) [575728]
- [netdrv] igb: fix warning in drivers/net/igb/igb_main.c (Stefan Assmann) [589272]
- [x86] Re-get cfg_new in case reuse/move irq_desc (Stanislaw Gruszka) [580065 583555]
- [hwmon] adt7462: fix wrong ADT7462_VOLT_COUNT (Stanislaw Gruszka) [580065]
- [fs] exec.c: fix initial stack reservation (Stanislaw Gruszka) [580067]
- [fs] exec.c: restrict initial stack space expansion to rlimit (Stanislaw Gruszka) [580065]
- [kernel] resource: add helpers for fetching rlimits (Stanislaw Gruszka) [580065]
- [tracing] ext4: Convert some events to DEFINE_EVENT (Mike Snitzer) [588108]
- [tracing] Convert some jbd2 events to DEFINE_EVENT (Mike Snitzer) [588108]
- [tracing] Convert some block events to DEFINE_EVENT (Mike Snitzer) [588108]
- [tracing] Convert some power events to DEFINE_EVENT (Mike Snitzer) [588108]
- [tracing] Convert some workqueue events to DEFINE_EVENT (Mike Snitzer) [588108]
- [tracing] Convert softirq events to DEFINE_EVENT (Mike Snitzer) [588108]
- [tracing] Convert some kmem events to DEFINE_EVENT (Mike Snitzer) [588108]
- [tracing] Convert module refcnt events to DEFINE_EVENT (Mike Snitzer) [588108]
- [tracing] xfs: use DECLARE_EVENT_CLASS (Mike Snitzer) [588108]
- [tracing] Harmonize event field names and print output names (Mike Snitzer) [588108]
- [tracing] Add DEFINE_EVENT(), DEFINE_SINGLE_EVENT() support to docbook (Mike Snitzer) [588108]
- [block] blk-cgroup: config options re-arrangement (Vivek Goyal) [586182]
- [block] blkio: Fix another BUG_ON() crash due to cfqq movement across groups (Vivek Goyal) [586182]
- [block] blkio: Fix blkio crash during rq stat update (Vivek Goyal) [586182]
- [block] blkio: Initialize blkg->stats_lock for the root cfqg too (Vivek Goyal) [586182]
- [block] blkio: Fix compile errors (Vivek Goyal) [586182]
- [block] Update to io-controller stats (Vivek Goyal) [586182]
- [block] io-controller: Add a new interface "weight_device" for IO-Controller (Vivek Goyal) [586182]
- [block] cfq-iosched: Fix the incorrect timeslice accounting with forced_dispatch (Vivek Goyal) [586182]
- [block] blkio: Add more debug-only per-cgroup stats (Vivek Goyal) [586182]
- [block] blkio: Add io_queued and avg_queue_size stats (Vivek Goyal) [586182]
- [block] blkio: Add io_merged stat (Vivek Goyal) [586182]
- [block] blkio: Changes to IO controller additional stats patches (Vivek Goyal) [586182]
- [block] expose the statistics in blkio.time and blkio.sectors for the root cgroup (Vivek Goyal) [586182]
- [block] blkio: Increment the blkio cgroup stats for real now (Vivek Goyal) [586182]
- [block] blkio: Add io controller stats like (Vivek Goyal) [586182]
- [block] blkio: Remove per-cfqq nr_sectors as we'll be passing (Vivek Goyal) [586182]
- [block] cfq-iosched: Add additional blktrace log messages in CFQ for easier debugging (Vivek Goyal) [586182]
- [block] cfq-iosched: requests "in flight" vs "in driver" clarification (Vivek Goyal) [586182]
- [ppc] cxgb3: Wait longer for control packets on initialization (Steve Best) [588848]
- [virt] KVM: convert ioapic lock to spinlock (Marcelo Tosatti) [588811]
- [virt] KVM: fix the handling of dirty bitmaps to avoid overflows (Marcelo Tosatti) [588811]
- [virt] KVM: MMU: fix kvm_mmu_zap_page() and its calling path (Marcelo Tosatti) [588811]
- [virt] KVM: VMX: Save/restore rflags.vm correctly in real mode (Marcelo Tosatti) [588811]
- [virt] KVM: Dont spam kernel log when injecting exceptions due to bad cr writes (Marcelo Tosatti) [588811]
- [virt] KVM: SVM: Fix memory leaks that happen when svm_create_vcpu() fails (Marcelo Tosatti) [588811]
- [virt] KVM: VMX: Update instruction length on intercepted BP (Marcelo Tosatti) [588811]
- [drm] nouveau: initial eDP support + additional fixes (Ben Skeggs) [588581]
- [s390x] zcore: Fix reipl device detection (Hendrik Brueckner) [587025]
- [connector] Delete buggy notification code (Stanislaw Gruszka) [580064 586025] {CVE-2010-0410}
- [netdrv] ath9k: fix beacon slot/buffer leak (Stanislaw Gruszka) [580064]
- [fusion] mptsas: Fix issue with chain pools allocation on katmai (Stanislaw Gruszka) [580064]
- [sunrpc] Fix a potential memory leak in auth_gss (Stanislaw Gruszka) [584757]
- [tracing] scsi: Enhance SCSI command tracing (Mike Snitzer) [588108]
- [tracing] scsi: Add missing verify command definitions (Mike Snitzer) [588108]
- [tracing] scsi: ftrace based SCSI command tracing (Mike Snitzer) [588108]
- [tracing] add __print_hex() (Mike Snitzer) [588108]
- [tracing] Add notrace to TRACE_EVENT implementation functions (Mike Snitzer) [588108]
- [tracing] Move a printk out of ftrace_raw_reg_event_foo() (Mike Snitzer) [588108]
- [tracing] Rename TRACE_EVENT_TEMPLATE() to DECLARE_EVENT_CLASS() (Mike Snitzer) [588108]
- [tracing] Convert some sched trace events to DEFINE_EVENT and _PRINT (Mike Snitzer) [588108]
- [tracing] Create new DEFINE_EVENT_PRINT (Mike Snitzer) [588108]
- [tracing] Create new TRACE_EVENT_TEMPLATE (Mike Snitzer) [588108]
- [tracing] additional interface changes and fixes (Mike Snitzer) [588108]
- [tracing] Ftrace dynamic ftrace_event_call support (Mike Snitzer) [588108]
- [fs] quota: fix WARN_ON when quota reservations get out of sync (Eric Sandeen) [581951]
- [scsi] fcoe: sync with upstream (Mike Christie) [577049 578328]

* Mon May 03 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-24.el6]
- [fs] ecryptfs: disallow ecryptfs as underlying filesystem (Eric Sandeen) [585185]
- [mm] Fix Section Mismatch warning in put_page_bootmem() (Prarit Bhargava) [587040]
- [mm] transparent hugepage support update (Andrea Arcangeli) [556572]
- [netdrv] ath9k: revert fb6635f6c114313f246cc34abc0b677264a765ed (Aristeu Rozanski) [584757]
- [virt] KVM: take srcu lock before call to complete_pio() (Gleb Natapov) [585887]
- [virt] virtio: Fix GFP flags passed from the virtio balloon driver (Amit Shah) [584680]
- [x86] Check chip_data value in irq_force_complete_move() (Prarit Bhargava) [564398]
- [x86] nmi_watchdog: use __cpuinit for 32-bit nmi_watchdog_default (Prarit Bhargava) [586967]
- [acpi] Fall back to manually changing SCI_EN (Matthew Garrett) [587008]
- [pci] Ensure that devices are resumed properly (Matthew Garrett) [586780]
- [serial] usb-serial: Rework and update qcserial (Matthew Garrett) [587009]
- [scsi] scsi_lib: Fix bug in completion of bidi commands (Stanislaw Gruszka) [580064]
- [net] phonet: add check for null pernet mem pointer in notifier (Jiri Pirko) [573122]
- [nfs] Ensure that writeback_single_inode() calls write_inode() when syncing (Jeff Layton) [584382]
- [serial] 8250_pnp: use wildcard for serial Wacom tablets (Stanislaw Gruszka) [580062]
- [fs] ext4: check s_log_groups_per_flex in online resize code (Eric Sandeen) [519461]
- [x86] Fix sched_clock_cpu for systems with unsynchronized TSC (Prarit Bhargava) [568344]
- [x86] Reenable TSC sync check at boot, even with NONSTOP_TSC (Prarit Bhargava) [568344]
- [mm] slab: add memory hotplug support (Prarit Bhargava) [562880]
- [x86] Set hotpluggable nodes in nodes_possible_map (Prarit Bhargava) [568344]
- [x86] acpi: Auto Online Hot-Added Memory (Prarit Bhargava) [568344]
- [mm] memory hotplug: fix a bug on /dev/mem for 64-bit kernels (Prarit Bhargava) [568344]
- [mm] update all PGDs for direct mapping changes on 64 bit (Prarit Bhargava) [568344]
- [x86] acpi: Map hotadded cpu to correct node (Prarit Bhargava) [568344]
- [ipmi] Change timeout and event poll to one second (Matthew Garrett) [584106]
- [ipmi] Attempt to register multiple SIs of the same type (Matthew Garrett) [584106]
- [ipmi] Reduce polling (Matthew Garrett) [584106]
- [ipmi] Reduce polling when interrupts are available (Matthew Garrett) [584106]
- [ipmi] Change device discovery order (Matthew Garrett) [584106]
- [ipmi] Only register one si per bmc (Matthew Garrett) [584106]
- [ipmi] Split device discovery and registration (Matthew Garrett) [584106]
- [ipmi] Change addr_source to an enum rather than strings (Matthew Garrett) [584106]
- [drm] radeon: rs780/rs880: MSI quirk fixes (Dave Airlie) [586168]
- [drm] radeon/kms: MC + watermark fixes + reset (Dave Airlie) [586168]
- [drm] radeon/kms/evergreen: add evergreen stage 2 - HPD irq (Dave Airlie) [580757]
- [drm] radeon: fixup radeon_asic struct c/h files (Dave Airlie) [586168]
- [drm] radeon/kms: misc + tv dac fixes (Dave Airlie) [586168]
- [drm] radeon/kms: squash upstream HDMI audio commits (Dave Airlie) [586168]
- [drm] kms/radeon: Integrated graphics fixes (Dave Airlie) [586168]
- [drm] radeon/kms: spread spectrum + pll fixes (Dave Airlie) [586168]
- [drm] radeon: add initial evergreen support + fixes (Dave Airlie) [580757]
- [kernel] tty: tty->pgrp races (Jiri Olsa) [586022]
- [netdrv] kernel: fix the r8169 frame length check error (Jiri Olsa) [586017] {CVE-2009-4537}

* Tue Apr 27 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-23.el6]
- [doc] add the documentation for mpol=local (Stanislaw Gruszka) [584757]
- [fs] tmpfs: handle MPOL_LOCAL mount option properly (Stanislaw Gruszka) [584757]
- [fs] tmpfs: mpol=bind:0 don't cause mount error (Stanislaw Gruszka) [584757]
- [netdrv] tun: orphan an skb on tx (Michael S. Tsirkin) [584428]
- [s390x] vmalloc: IPL failure with enabled memory cgroups (Hendrik Brueckner) [580918]
- [netdrv] b43: fall back gracefully to PIO mode after fatal DMA errors (John Linville) [583069]
- [netdrv] b43: Allow PIO mode to be selected at module load (John Linville) [583069]
- [netdrv] b43: Remove reset after fatal DMA error (John Linville) [583069]
- [netdrv] b43: Optimize PIO scratchbuffer usage (John Linville) [583069]
- [fs] vfs: get_sb_single() - do not pass options twice (Stanislaw Gruszka) [580063]
- [fs] tmpfs: fix oops on mounts with mpol=default (Stanislaw Gruszka) [584757]
- [kernel] cred.c: use kmem_cache_free (Stanislaw Gruszka) [580064]
- [fs] partition/msdos: fix unusable extended partition for > 512B sector (Stanislaw Gruszka) [584757]
- [fs] partitions/msdos: add support for large disks (Stanislaw Gruszka) [584757]
- [fs] eCryptfs: Add getattr function (Stanislaw Gruszka) [580065]
- [fs] ecryptfs: initialize private persistent file before dereferencing pointer (Stanislaw Gruszka) [580062]
- [fs] ecryptfs: use after free (Stanislaw Gruszka) [580062]
- [ppc] Track backing pages used allocated by vmemmap_populate() (Steve Best) [547854]
- [netdrv] be2net: recent bug fixes from upstream (Ivan Vecera) [583766]
- [sunrpc] handle allocation errors from __rpc_lookup_create() (Stanislaw Gruszka) [584757]
- [nfs] Prevent another deadlock in nfs_release_page() (Stanislaw Gruszka) [584757]
- [nfs] NFSv4: Don't ignore the NFS_INO_REVAL_FORCED flag in nfs_revalidate_inode() (Stanislaw Gruszka) [584757]
- [nfs] Fix an allocation-under-spinlock bug (Stanislaw Gruszka) [580067]
- [sunrpc] Handle EINVAL error returns from the TCP connect operation (Stanislaw Gruszka) [580067]
- [sunrpc] remove unnecessary svc_xprt_put (Stanislaw Gruszka) [580067]
- [x86] Add iMac9,1 to pci_reboot_dmi_table (Stanislaw Gruszka) [580067]
- [rtc] rtc-core: fix memory leak (Stanislaw Gruszka) [580067]
- [mm] readahead: introduce FMODE_RANDOM for POSIX_FADV_RANDOM (Stanislaw Gruszka) [580067]
- [fs] fix LOOKUP_FOLLOW on automount "symlinks" (Stanislaw Gruszka) [580067]
- [nfs] Too many GETATTR and ACCESS calls after direct I/O (Stanislaw Gruszka) [580065]
- [virt] kvmclock: count total_sleep_time when updating guest clock (Stanislaw Gruszka) [580065]
- [kernel] Export the symbol of getboottime and mmonotonic_to_bootbased (Stanislaw Gruszka) [580065]
- [nfs] NFS: Fix the mapping of the NFSERR_SERVERFAULT error (Stanislaw Gruszka) [580065]
- [nfs] NFS: Fix a umount race (Stanislaw Gruszka) [580065]
- [x86] amd-iommu: Fix possible integer overflow (Stanislaw Gruszka) [580064]
- [ata] libata: retry FS IOs even if it has failed with AC_ERR_INVALID (Stanislaw Gruszka) [580064]
- [firewire] firewire: ohci: fix crashes with TSB43AB23 on 64bit systems (Stanislaw Gruszka) [580064]
- [ata] pata_hpt3x2n: always stretch UltraDMA timing (Stanislaw Gruszka) [580067]
- [cgroup] memcg: fix oom killing a child process in an other cgroup (Stanislaw Gruszka) [580067]
- [ata] libata: retry link resume if necessary (Stanislaw Gruszka) [580064]
- [firewire] core: add_descriptor size check (Stanislaw Gruszka) [580064]
- [netdrv] iwlwifi: fix scan race (Stanislaw Gruszka) [584759]
- [netdrv] iwlwifi: clear all tx queues when firmware ready (Stanislaw Gruszka) [584759]
- [netdrv] iwlwifi: need check for valid qos packet before free (Stanislaw Gruszka) [584759]
- [netdrv] mac80211: tear down all agg queues when restart/reconfig hw (Stanislaw Gruszka) [584759]
- [netdrv] mac80211: move netdev queue enabling to correct spot (Stanislaw Gruszka) [584759]
- [netdrv] setup correct int pipe type in ar9170_usb_exec_cmd (Stanislaw Gruszka) [584759]
- [netdrv] iwlwifi: range checking issue (Stanislaw Gruszka) [584759]
- [netdrv] iwlwifi: fix nfreed-- (Stanislaw Gruszka) [584759]
- [netdrv] iwlwifi: counting number of tfds can be free for 4965 (Stanislaw Gruszka) [584759]
- [netdrv] b43: Workaround circular locking in hw-tkip key update callback (Stanislaw Gruszka) [584757]
- [ata] ahci: use BIOS date in broken_suspend list (Stanislaw Gruszka) [584757]
- [netdrv] mac80211: Reset dynamic ps timer in Rx path (Stanislaw Gruszka) [584757]
- [netdrv] ath9k: Enable IEEE80211_HW_REPORTS_TX_ACK_STATUS flag for ath9k (Stanislaw Gruszka) [584757]
- [netdrv] mac80211: Retry null data frame for power save (Stanislaw Gruszka) [584757]
- [netdrv] ath9k: Enable TIM timer interrupt only when needed. (Stanislaw Gruszka) [584757]
- [netdrv] ath9k: fix BUG_ON triggered by PAE frames (Stanislaw Gruszka) [584757]
- [netdrv] iwlwifi: Silence tfds_in_queue message (Stanislaw Gruszka) [584757]
- [netdrv] iwlwifi: use dma_alloc_coherent (Stanislaw Gruszka) [584757]
- [netdrv] wl1251: fix potential crash (Stanislaw Gruszka) [584757]
- [block] readahead: add blk_run_backing_dev (Stanislaw Gruszka) [584757]
- [netdrv] ath9k: fix lockdep warning when unloading module (Stanislaw Gruszka) [584757]
- [scsi] mvsas: add support for Adaptec ASC-1045/1405 SAS/SATA HBA (Stanislaw Gruszka) [584757]
- [netdrv] ath5k: fix setup for CAB queue (Stanislaw Gruszka) [584757]
- [netdrv] ath5k: dont use external sleep clock in AP mode (Stanislaw Gruszka) [584757]
- [netdrv] tg3: Fix tg3_poll_controller() passing wrong pointer to tg3_interrupt() (Stanislaw Gruszka) [584757]
- [netdrv] b43/b43legacy: Wake queues in wireless_core_start (Stanislaw Gruszka) [580067]
- [netdrv] ath5k: use correct packet type when transmitting (Stanislaw Gruszka) [580067]
- [netdrv] ath9k: disable RIFS search for AR91xx based chips (Stanislaw Gruszka) [580067]
- [netdrv] ath9k: fix rate control fallback rate selection (Stanislaw Gruszka) [580067]
- [netdrv] ath9k: fix beacon timer restart after a card reset (Stanislaw Gruszka) [580067]
- [netdrv] p54usb: Add the USB ID for Belkin (Accton) FD7050E ver 1010ec (Stanislaw Gruszka) [580067]
- [netdrv] rndis_wlan: disable stall workaround (Stanislaw Gruszka) [580067]
- [netdrv] rndis_wlan: fix buffer overflow in rndis_query_oid (Stanislaw Gruszka) [580067]
- [netdrv] rndis_wlan: handle NL80211_AUTHTYPE_AUTOMATIC (Stanislaw Gruszka) [580067]
- [netdrv] sky2: fix transmit DMA map leakage (Stanislaw Gruszka) [580067]
- [netdrv] airo: fix setting zero length WEP key (Stanislaw Gruszka) [580067]
- [netdrv] mac80211: quit addba_resp_timer if Tx BA session is torn down (Stanislaw Gruszka) [580067]
- [netdrv] iwlwifi: sanity check before counting number of tfds can be free (Stanislaw Gruszka) [580067]
- [netdrv] iwlwifi: set HT flags after channel in rxon (Stanislaw Gruszka) [580067]
- [netdrv] iwlwifi: error checking for number of tfds in queue (Stanislaw Gruszka) [580067]
- [netdrv] iwlwifi: Fix to set correct ht configuration (Stanislaw Gruszka) [580065]
- [netdrv] mac80211: Fix probe request filtering in IBSS mode (Stanislaw Gruszka) [580065]
- [netdrv] ath9k: Fix sequence numbers for PAE frames (Stanislaw Gruszka) [580065]
- [netdrv] b43: Fix throughput regression (Stanislaw Gruszka) [580065]
- [netdrv] rtl8187: Add new device ID (Stanislaw Gruszka) [580065]
- [ata] ahci: add Acer G725 to broken suspend list (Stanislaw Gruszka) [580065]
- [scsi] mptfusion: mptscsih_abort return value should be SUCCESS instead of value 0 (Stanislaw Gruszka) [580065]
- [nfs] Fix an Oops when truncating a file (Stanislaw Gruszka) [580065]
- [block] cciss: Make cciss_seq_show handle holes in the h->drv[] array (Stanislaw Gruszka) [580065]
- [netdrv] ath9k: fix eeprom INI values override for 2GHz-only cards (Stanislaw Gruszka) [580064]
- [netdrv] mac80211: fix NULL pointer dereference when ftrace is enabled (Stanislaw Gruszka) [580064]
- [block] fix bugs in bio-integrity mempool usage (Stanislaw Gruszka) [580064]
- [netdrv] sky2: Fix oops in sky2_xmit_frame() after TX timeout (Stanislaw Gruszka) [580064]
- [netdrv] iwlwifi: set default aggregation frame count limit to 31 (Stanislaw Gruszka) [580064]
- [netdrv] e1000/e1000e: don't use small hardware rx buffers (Stanislaw Gruszka) [580064]
- [netdrv] e1000: enhance frame fragment detection (Stanislaw Gruszka) [580064]
- [mm] rmap: anon_vma_prepare() can leak anon_vma_chain (Rik van Riel) [579936]
- [mm] rmap: add exclusively owned pages to the newest anon_vma (Rik van Riel) [579936]
- [mm] anonvma: when setting up page->mapping, we need to pick the _oldest_ anonvma (Rik van Riel) [579936]
- [mm] anon_vma: clone the anon_vma chain in the right order (Rik van Riel) [579936]
- [mm] vma_adjust: fix the copying of anon_vma chains (Rik van Riel) [579936]
- [mm] Simplify and comment on anon_vma re-use for anon_vma_prepare() (Rik van Riel) [579936]
- [mm] rmap: fix anon_vma_fork() memory leak (Rik van Riel) [579936]
- [s390x] nss: add missing .previous statement to asm function (Hendrik Brueckner) [581521]
- [ata] pata_mavell: correct check of AHCI config option (David Milburn) [584483]
- [fs] ext4: Issue the discard operation before releasing the blocks (Eric Sandeen) [575884]
- [scsi] 3w_sas: new driver (Tomas Henzl) [572781]
- [kernel] hrtimer: Tune hrtimer_interrupt hang logic (Marcelo Tosatti) [576355]

* Tue Apr 20 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-22.el6]
- [netdrv] b43: ssb: do not read SPROM if it does not exist (John Linville) [574895]
- [netdrv] igb: add support for Intel I350 Gigabit Network Connection (Stefan Assmann) [580727]
- [kernel] exec: refactor how usermodehelpers work and modify core_pipe recursion check (Neil Horman) [557387]
- [kernel] re-export page_is_ram() for crash module (Prarit Bhargava) [583032]
- [x86] amd_iommu: allow iommu to complete dma transactions during transition to kdump kernel (Neil Horman) [577788]
- [nfs] rsize and wsize settings ignored on v4 mounts (Steve Dickson) [582697]
- [net] igmp: fix ip_mc_sf_allow race (Flavio Leitner) [578932]
- [net] Remove skb_dma_map/unmap calls from drivers (Thomas Graf) [576690]
- [scsi] mpt2sas: IOs needs to be pause until handles are refreshed for all device after recovery (Tomas Henzl) [577909]
- [scsi] mpt2sas: Reworked scmd->result priority for _scsih_qcmd (Tomas Henzl) [577909]
- [x86] Suppress stack overrun message for init_task (Prarit Bhargava) [582625]
- [sunrpc] gss_krb5: Advertise rc4-hmac enctype support in the rpcsec_gss/krb5 upcall (Steve Dickson) [498317]
- [sunrpc] gss_krb5: Add support for rc4-hmac encryption (Steve Dickson) [498317]
- [sunrpc] gss_krb5: Use confounder length in wrap code (Steve Dickson) [498317]
- [sunrpc] gssd_krb5: More arcfour-hmac support (Steve Dickson) [498317]
- [sunrpc] gss_krb5: Save the raw session key in the context (Steve Dickson) [498317]
- [sunrpc] gssd_krb5: arcfour-hmac support (Steve Dickson) [498317]
- [sunrpc] gss_krb5: Advertise AES enctype support in the rpcsec_gss/krb5 upcall (Steve Dickson) [498317]
- [sunrpc] gss_krb5: add remaining pieces to enable AES encryption support (Steve Dickson) [498317]
- [sunrpc] gss_krb5: add support for new token formats in rfc4121 (Steve Dickson) [498317]
- [sunrpc] xdr: Add an export for the helper function write_bytes_to_xdr_buf() (Steve Dickson) [498317]
- [sunrpc] gss_krb5: Advertise triple-des enctype support in the rpcsec_gss/krb5 upcall (Steve Dickson) [498317]
- [sunrpc] gss_krb5: add support for triple-des encryption (Steve Dickson) [498317]
- [sunrpc] gss_krb5: Add upcall info indicating supported kerberos enctypes (Steve Dickson) [498317]
- [sunrpc] gss_krb5: handle new context format from gssd (Steve Dickson) [498317]
- [sunrpc] gss_krb5: import functionality to derive keys into the kernel (Steve Dickson) [498317]
- [sunrpc] gss_krb5: add ability to have a keyed checksum (hmac) (Steve Dickson) [498317]
- [sunrpc] gss_krb5: introduce encryption type framework (Steve Dickson) [498317]
- [sunrpc] gss_krb5: prepare for new context format (Steve Dickson) [498317]
- [sunrpc] gss_krb5: split up functions in preparation of adding new enctypes (Steve Dickson) [498317]
- [sunrpc] gss_krb5: Don't expect blocksize to always be 8 when calculating padding (Steve Dickson) [498317]
- [sunrpc] gss_krb5: Added and improved code comments (Steve Dickson) [498317]
- [sunrpc] gss_krb5: Introduce encryption type framework (Steve Dickson) [498317]
- [mm] Fix vfree race resulting in kernel bug (Steven Whitehouse) [582522]
- [ata] libata: fix accesses at LBA28 boundary (David Milburn) [582432]
- [netdrv] b43: Rewrite DMA Tx status handling sanity checks (John Linville) [574533]
- [char] tty: release_one_tty() forgets to put pids (Oleg Nesterov) [582077] {CVE-2010-1162}
- [mm] oom: fix the unsafe usage of badness() in proc_oom_score() (Oleg Nesterov) [582069]
- [netdrv] bonding: fix broken multicast with round-robin mode (Andy Gospodarek) [581644]
- [x86] Remove sysfs_attr_init, sysfs_bin_attr_init changes introduced in last MCE patch (Prarit Bhargava) [581659]
- [kernel] sched_getaffinity: allow less than NR_CPUS length (Oleg Nesterov) [578970]
- [scsi] bfa sync w/ upstream (Rob Evers) [576716]
- [gfs] GFS2: Fix ordering of ordered buffers (Steven Whitehouse) [581011]
- [gfs] GFS2: Don't withdraw on partial rindex entries (Robert S Peterson) [581009]
- [gfs] GFS2: livelock while reclaiming unlinked dinodes (Robert S Peterson) [570182]
- [scsi] mpt2sas: Do not reset handle before calling _scsih_remove_device in RESCAN task after HBA RESET (Tomas Henzl) [572646]
- [scsi] mpt2sas: Device removal algorithm in interrupt ctx (Tomas Henzl) [572646]
- [scsi] mpt2sas: fix the incorrect scsi_dma_map error checking (Tomas Henzl) [572646]
- [scsi] Upgrading version to 04.100.01.02 (Tomas Henzl) [572646]
- [scsi] mpt2sas: modified _scsih_sas_device_find_by_handle/sas_address (Tomas Henzl) [572646]
- [scsi] mpt2sas: RESCAN Barrier work is added in case of HBA reset (Tomas Henzl) [572646]
- [scsi] update the version to 04.100.01.00 (Tomas Henzl) [572646]
- [scsi] scsi_transport_sas: add support for transport layer retries (TLR) (Tomas Henzl) [572646]
- [scsi] mpt2sas: Added raid transport support (Tomas Henzl) [572646]
- [scsi] eliminate potential kmalloc failure in scsi_get_vpd_page() (Tomas Henzl) [572646]
- [ata] libata: fix ata_id_logical_per_physical_sectors (David Milburn) [582021]
- [netdrv] iwlwifi: Fix throughput stall issue in HT mode for 5000 (Stanislaw Gruszka) [580063]
- [infiniband] IPoIB: Clear ipoib_neigh.dgid in ipoib_neigh_alloc() (Stanislaw Gruszka) [580063]
- [net] cfg80211: fix channel setting for wext (Stanislaw Gruszka) [580063]
- [net] mac80211: check that ieee80211_set_power_mgmt only handles STA interfaces (Stanislaw Gruszka) [580063]
- [ata] ata_piix: fix MWDMA handling on PIIX3 (Stanislaw Gruszka) [580063]
- [ata] ahci: disable SNotification capability for ich8 (Stanislaw Gruszka) [580063]
- [netdrv] ar9170: Add support for D-Link DWA 160 A2 (Stanislaw Gruszka) [580063]
- [netdrv] sfc: Fix DMA mapping cleanup in case of an error in TSO (Stanislaw Gruszka) [580063]
- [fs] ext4: don't call write_inode under the journal (Josef Bacik) [576202]
- [fs] ext4: Calculate metadata requirements more accurately (Josef Bacik) [576202]
- [fs] ext4: Patch up how we claim metadata blocks for quota purposes (Josef Bacik) [576202]
- [fs] ext4: fix potential quota deadlock (Josef Bacik) [576202]
- [virt] virtio: console: Add support for nonblocking write()s (Amit Shah) [576241]
- [virt] virtio: console: Rename wait_is_over() to will_read_block() (Amit Shah) [576241]
- [virt] virtio: console: Don't always create a port 0 if using multiport (Amit Shah) [576241]
- [virt] virtio: console: Use a control message to add ports (Amit Shah) [576241]
- [virt] virtio: console: Move code around for future patches (Amit Shah) [576241]
- [virt] virtio: console: Remove config work handler (Amit Shah) [576241]
- [virt] virtio: console: Don't call hvc_remove() on unplugging console ports (Amit Shah) [576241]
- [virt] virtio: console: Return -EPIPE to hvc_console if we lost the connection (Amit Shah) [576241]
- [virt] virtio: console: Let host know of port or device add failures (Amit Shah) [576241]
- [virt] virtio: console: Add a __send_control_msg() that can send messages without a valid port (Amit Shah) [576241]
- [virt] hvc_console: Fix race between hvc_close and hvc_remove (Amit Shah) [577222]
- [virt] virtio: console makes incorrect assumption about virtio API (Amit Shah) [576241]
- [virt] MAINTAINERS: Put the virtio-console entry in correct alphabetical order (Amit Shah) [576241]
- [virt] virtio: console: Fix early_put_chars usage (Amit Shah) [576241]
- [virt] virtio: console: Check if port is valid in resize_console (Amit Shah) [576241]
- [virt] virtio: console: Generate a kobject CHANGE event on adding 'name' attribute (Amit Shah) [576241]
- [virt] virtio: console: Use better variable names for fill_queue operation (Amit Shah) [576241]
- [virt] virtio: console: Fix type of 'len' as unsigned int (Amit Shah) [576241]
- [vfs] rename block_fsync() to blkdev_fsync() (Jeff Moyer) [579781]
- [char] raw: add an fsync method (Jeff Moyer) [579781]
- [x86] Don't use logical-flat mode when more than 8 CPUs are possible (John Villalovos) [563798]
- [net] Backport the new socket API recvmmsg, receive multiple messages (Arnaldo Carvalho de Melo) [579850]
- [kernel] coredump: fix the page leak in dump_seek() (Oleg Nesterov) [580126]
- [s390x] callhome: fix broken proc interface and activate comp ID (Hendrik Brueckner) [579482]

* Mon Apr 12 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-21.el6]
- [x86] Update x86 MCE code (Prarit Bhargava) [580587]
- [scsi] 3w-xxxx: Force 60 second timeout default (Tomas Henzl) [572778]
- [netdrv] enic: update to upstream version 1.3.1.1 (Andy Gospodarek) [575950]
- [netdrv] igb: Add support for 82576 ET2 Quad Port Server Adapter (Stefan Assmann) [577421]
- [kernel] resource: Fix generic page_is_ram() for partial RAM pages (Prarit Bhargava) [578834]
- [x86] Use the generic page_is_ram() (Prarit Bhargava) [578834]
- [x86] Remove BIOS data range from e820 (Prarit Bhargava) [578834]
- [kernel] Move page_is_ram() declaration to mm.h (Prarit Bhargava) [578834]
- [kernel] Generic page_is_ram: use __weak (Prarit Bhargava) [578834]
- [kernel] resources: introduce generic page_is_ram() (Prarit Bhargava) [578834]
- [fs] GFS2: Clean up copying from stuffed files (Steven Whitehouse) [580857]
- [netdrv] igb: restrict WoL for 82576 ET2 Quad Port Server Adapter (Stefan Assmann) [578804]
- [drm] radeon/kms: move radeon KMS on/off switch out of staging (Dave Airlie) [580766]
- [netdrv] p54: fix deadlocks under tx load (Michal Schmidt) [580557]
- [gfs2] GFS2: Mandatory locking fix (Steven Whitehouse) [571606] {CVE-2010-0727}
- [x86] AMD: Fix NULL pointer dereference on 32-bit (Bhavna Sarathy) [571474]
- [x86] Add wbinvd SMP helper routines (Bhavna Sarathy) [571474]
- [x86] L3 cache: Remove NUMA dependency (Bhavna Sarathy) [571474]
- [x86] Calculate L3 indices (Bhavna Sarathy) [571474]
- [x86] Add cache index disable sys attributes (Bhavna Sarathy) [571474]
- [x86] Fix disabling of L3 cache indices (Bhavna Sarathy) [571474]
- [fs] NFS: Avoid a deadlock in nfs_release_page (Jeff Layton) [525963]
- [fs] NFS: Remove requirement for inode->i_mutex from nfs_invalidate_mapping (Jeff Layton) [525963]
- [fs] NFS: Clean up nfs_sync_mapping (Jeff Layton) [525963]
- [fs] NFS: Simplify nfs_wb_page() (Jeff Layton) [525963]
- [fs] NFS: Replace __nfs_write_mapping with sync_inode() (Jeff Layton) [525963]
- [fs] NFS: Simplify nfs_wb_page_cancel() (Jeff Layton) [525963]
- [fs] NFS: Ensure inode is always marked I_DIRTY_DATASYNC, if it has unstable pages (Jeff Layton) [525963]
- [fs] NFS: Run COMMIT as an asynchronous RPC call when wbc->for_background is set (Jeff Layton) [525963]
- [fs] NFS: Reduce the number of unnecessary COMMIT calls (Jeff Layton) [525963]
- [fs] NFS: Add a count of the number of unstable writes carried by an inode (Jeff Layton) [525963]
- [fs] NFS: Cleanup - move nfs_write_inode() into fs/nfs/write.c (Jeff Layton) [525963]
- [fs] writeback: pass writeback_control to ->write_inode (Jeff Layton) [525963]
- [fs] writeback: make sure data is on disk before calling ->write_inode (Jeff Layton) [525963]
- [fs] writeback: introduce wbc.for_background (Jeff Layton) [525963]
- [netdrv] macvlan: fix support for multiple driver backends (Anthony Liguori) [553337 566731]
- [netdrv] net/macvtap: add vhost support (Anthony Liguori) [553337 566731]
- [netdrv] macvtap: add GSO/csum offload support (Anthony Liguori) [553337 566731]
- [netdrv] macvtap: rework object lifetime rules (Anthony Liguori) [553337 566731]
- [netdrv] macvtap: fix reference counting (Anthony Liguori) [553337 566731]
- [netdrv] net: macvtap driver (Anthony Liguori) [553337 566731]
- [netdrv] macvlan: export macvlan mode through netlink (Anthony Liguori) [553337 566731]
- [netdrv] macvlan: implement bridge, VEPA and private mode (Anthony Liguori) [553337 566731]
- [netdrv] macvlan: cleanup rx statistics (Anthony Liguori) [553337 566731]
- [netdrv] macvlan: Precise RX stats accounting (Anthony Liguori) [553337 566731]
- [netdrv] macvlan: add private dev_txq_stats_fold function (Anthony Liguori) [553337 566731]
- [netdrv] veth: move loopback logic to common location (Anthony Liguori) [553337 566731]
- [s390x] zfcp: Remove lock dependency on unit remove (Hendrik Brueckner) [576860]
- [s390x] zfcp: Remove lock dependency on unit add (Hendrik Brueckner) [576860]
- [s390x] zfcp: Remove lock dependency on CCW remove (Hendrik Brueckner) [576860]
- [s390x] dasd: fix alignment of transport mode recovery TCW (Hendrik Brueckner) [575824]
- [s390x] cio: fix drvdata usage for the console subchannel (Hendrik Brueckner) [575826]
- [s390x] zcore: CPU registers are not saved under LPAR (Hendrik Brueckner) [575221]
- [s390x] zfcpdump: Use direct IO in order to increase dump speed (Hendrik Brueckner) [575189]
- [s390x] qeth: change checksumming default for HiperSockets (Hendrik Brueckner) [572227]
- [s390x] qeth: l3 send dhcp in non pass thru mode (Hendrik Brueckner) [572225]
- [s390x] zfcp: Remove attached ports and units correctly (Hendrik Brueckner) [571938]
- [drm] Bring in nouveau updates from upstream (Ben Skeggs) [558468]
- [vfs] pass struct file to do_truncate on O_TRUNC opens (Jeff Layton) [573995]
- [vfs] O_TRUNC open shouldn't fail after file truncation (Jeff Layton) [573995]
- [net] netfilter: ctnetlink: compute message size properly (Jiri Pirko) [578476]
- [block] cfq-iosched: Do not merge queues of BE and IDLE classes (Jeff Moyer) [577393]
- [block] remove 16 bytes of padding from struct request on 64bits (Jeff Moyer) [577393]
- [block] cfq: remove 8 bytes of padding from cfq_rb_root on 64 bit builds (Jeff Moyer) [577393]
- [block] cfq-iosched: quantum check tweak (Jeff Moyer) [577393]
- [block] remove padding from io_context on 64bit builds (Jeff Moyer) [577393]
- [block] cfq: reorder cfq_queue removing padding on 64bit (Jeff Moyer) [577393]
- [block] cfq-iosched: split seeky coop queues after one slice (Jeff Moyer) [577393]
- [x86] edac, mce: Filter out invalid values (Bhavna Sarathy) [574487]
- [x86] edac, mce, amd: silence GART TLB errors (Bhavna Sarathy) [574487]
- [x86] edac, mce: correct corenum reporting (Bhavna Sarathy) [574487]
- [x86] edac, mce: update AMD F10h revD check (Bhavna Sarathy) [574487]
- [x86] amd64_edac: Simplify ECC override handling (Bhavna Sarathy) [574487]
- [x86] amd64_edac: Do not falsely trigger kerneloops (Bhavna Sarathy) [574487]
- [x86] amd64_edac: Ensure index stays within bounds in amd64_get_scrub_rate (Bhavna Sarathy) [574487]
- [x86] amd64_edac: restrict PCI config space access (Bhavna Sarathy) [574487]
- [x86] amd64_edac: fix K8 chip select reporting (Bhavna Sarathy) [574487]
- [x86] amd64_edac: bump driver version (Bhavna Sarathy) [574487]
- [x86] amd64_edac: fix use-uninitialised bug (Bhavna Sarathy) [574487]
- [x86] amd64_edac: correct sys address to chip select mapping (Bhavna Sarathy) [574487]
- [x86] amd64_edac: add a leaner syndrome decoding algorithm (Bhavna Sarathy) [574487]
- [x86] amd64_edac: remove early hw support check (Bhavna Sarathy) [574487]
- [x86] amd64_edac: detect DDR3 memory type (Bhavna Sarathy) [574487]
- [x86] edac: add memory types strings for debugging (Bhavna Sarathy) [574487]
- [x86] amd64_edac: remove unneeded extract_error_address wrapper (Bhavna Sarathy) [574487]
- [x86] amd64_edac: rename StinkyIdentifier (Bhavna Sarathy) [574487]
- [x86] amd64_edac: remove superfluous dbg printk (Bhavna Sarathy) [574487]
- [x86] amd64_edac: enhance address to DRAM bank mapping (Bhavna Sarathy) [574487]
- [x86] amd64_edac: cleanup f10_early_channel_count (Bhavna Sarathy) [574487]
- [x86] amd64_edac: dump DIMM sizes on K8 too (Bhavna Sarathy) [574487]
- [x86] amd64_edac: cleanup rest of amd64_dump_misc_regs (Bhavna Sarathy) [574487]
- [x86] amd64_edac: cleanup DRAM cfg low debug output (Bhavna Sarathy) [574487]
- [x86] amd64_edac: wrap-up pci config read error handling (Bhavna Sarathy) [574487]
- [x86] amd64_edac: make DRAM regions output more human-readable (Bhavna Sarathy) [574487]
- [x86] amd64_edac: clarify DRAM CTL debug reporting (Bhavna Sarathy) [574487]

* Tue Apr 06 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-20.el6]
- [netdrv] iwlwifi: fix kdump hang (Stanislaw Gruszka) [575122]
- [kernel] clockevent: Don't remove broadcast device when cpu is dead (Danny Feng) [572438]
- [block] Export max number of segments and max segment size in sysfs (Jeff Moyer) [574132]
- [block] Finalize conversion of block limits functions (Jeff Moyer) [574132]
- [block] Fix overrun in lcm() and move it to lib (Jeff Moyer) [574132]
- [block] jiffies fixes (Jeff Moyer) [574132]
- [block] Consolidate phys_segment and hw_segment limits (Jeff Moyer) [574132]
- [block] Rename blk_queue_max_sectors to blk_queue_max_hw_sectors (Jeff Moyer) [574132]
- [block] Add BLK_ prefix to definitions (Jeff Moyer) [574132]
- [block] Remove unused accessor function (Jeff Moyer) [574132]
- [block] Update blk_queue_max_sectors and documentation (Jeff Moyer) [574132]
- [ata] ahci: Turn off DMA engines when there's no device attached (Matthew Garrett) [577967]
- [scsi] qla2xxx: minor updates and fixes from upstream (Rob Evers) [574526]
- [scsi] Additional BSG corrections from upstream (Rob Evers) [574590]
- [netdrv] be2net: Update be2net 10GB NIC driver to version 2.102.147u (Ivan Vecera) [576172]
- [scsi] update fibre channel layer (Mike Christie) [571824]
- [scsi] lpfc Update from 8.3.5.6 to 8.3.5.7 FC/FCoE (Rob Evers) [576174]
- [netdrv] e100: fix the 'size' argument passed to pci_pool_create() (Dean Nelson) [576887]
- [kernel] futex: remove rw parameter from get_futex_key() (Amerigo Wang) [555700]
- [drm] Add drm_gem_object_handle_unreference_unlocked and drm_gem_object_unreference_unlocked (Adam Jackson) [575910]
- [drm] i915: Update to 2.6.34-rc1 (pre-vga-switcheroo) (Adam Jackson) [575910]
- [scsi] libfcoe: Send port LKA every FIP_VN_KA_PERIOD secs (Rob Evers) [570693]
- [scsi] fnic: updating driver to 1.4.0.98 syncs w/ upstream (Rob Evers) [570693]
- [sound] snd-hda-intel: avoid divide by zero (Jaroslav Kysela) [567173] {CVE-2010-1085}
- [netdrv] bnx2x: use new firmware (Stanislaw Gruszka) [560993]
- [netdrv] bnx2: remove old firmware (Stanislaw Gruszka) [560993]
- [netdrv] bnx2x: 1.52.1-6 firmware (Stanislaw Gruszka) [560993]
- [netdrv] bnx2x: 1.52.1-6 bug fixes (Stanislaw Gruszka) [560993]
- [ata] ahci: support FIS-based switching (David Milburn) [463152]
- [drm] radeon: better GPU reset for lockup (Jerome Glisse) [576511]
- [block] cciss: add 30 second initial timeout wait on controller reset (Tomas Henzl) [574094]
- [serial] fix hang in serial console open (Neil Horman) [568418]
- [virt] vmw_pvscsi: adding vmware paravirtualized driver (Rob Evers) [553062]
- [scsi] 3w-9xxx: update 3w-9xxx to v2.26.02.014RH (Tomas Henzl) [572779]
- [netdrv] ixgbevf: initial support for 82599VF driver (Andy Gospodarek) [462790]
- [netdrv] ixgbe: update to version 2.0.62-k2 (Andy Gospodarek) [462790]
- [netdrv] netxen: More critical bug fixes and AER support (Tony Camuso) [516840]
- [netdrv] netxen: Sync with upstream kernel bug fixes (Tony Camuso) [516840]
- [fs] dlm: use bastmode in debugfs output (David Teigland) [568102]
- [fs] dlm: send reply before bast (David Teigland) [568102]
- [fs] dlm: fix ordering of bast and cast (David Teigland) [568102]
- [virt] virtio-net: remove send queue (Anthony Liguori) [555698]
- [virt] virtio-net: Defer skb allocation and remove recv queue (Anthony Liguori) [555698]
- [net] bridge: Allow enable/disable UFO on bridge device via ethtool (Anthony Liguori) [555537]
- [net] Make UFO on master device independent of attached devices (Anthony Liguori) [555537]
- [fs] xfs: fix locking for inode cache radix tree tag updates (Christoph Hellwig) [573836]
- [uv] fix microcode.ctl slow down in boot-time on large systems (George Beshers) [573018]
- [scsi] lpfc Update from 8.3.5.5 to 8.3.5.6 FC/FCoE (Rob Evers) [568889]
- [mm] transparent hugepage support update (Andrea Arcangeli) [556572]
- [netdrv] e1000e: fix data corruptor in NFS packet split filtering hw (Neil Horman) [572350]
- [security] selinux: dynamic class/perm discovery (Eric Paris) [570812]
- [security] selinux/ss: correct size computation (Eric Paris) [573000]
- [security] SELinux: reduce size of access vector hash table (Eric Paris) [570433]
- [security] SELinux: reset the security_ops before flushing the avc cache (Eric Paris) [572998]
- [sched] Fix sched_mc_power_savings for !SMT (Danny Feng) [571879]
- [security] selinux: Only audit permissions specified in policy (Eric Paris) [573002]
- [security] selinux: fix memory leak in sel_make_bools (Eric Paris) [573008]
- [security] SELinux: Make selinux_kernel_create_files_as() shouldn't just always return 0 (Eric Paris) [573011]
- [security] selinux: convert range transition list to a hashtab (Eric Paris) [572702]
- [virt] x86: remove kmap_atomic_pte paravirt op (Paolo Bonzini) [567203]
- [virt] vmi: disable highmem PTE allocation even when CONFIG_HIGHPTE=y (Paolo Bonzini) [567203]
- [virt] xen: disable highmem PTE allocation even when CONFIG_HIGHPTE=y (Paolo Bonzini) [567203]
- [virt] x86: allow allocation of highmem user page tables to be disabled when CONFIG_HIGHPTE=y (Paolo Bonzini) [567203]
- [netdrv] qlge: update to latest upstream (Andy Gospodarek) [562311]
- [netdrv] add netif_printk helpers (Andy Gospodarek) [562311]
- [net] bridge: Fix build error when IGMP_SNOOPING is not enabled (Herbert Xu) [574321]
- [net] bridge: Add multicast count/interval sysfs entries (Herbert Xu) [574321]
- [net] bridge: Add hash elasticity/max sysfs entries (Herbert Xu) [574321]
- [net] bridge: Add multicast_snooping sysfs toggle (Herbert Xu) [574321]
- [net] bridge: Add multicast_router sysfs entries (Herbert Xu) [574321]
- [net] bridge: Add multicast data-path hooks (Herbert Xu) [574321]
- [net] bridge: Add multicast start/stop hooks (Herbert Xu) [574321]
- [net] bridge: Add multicast forwarding functions (Herbert Xu) [574321]
- [net] bridge: Move NULL mdb check into br_mdb_ip_get (Herbert Xu) [574321]
- [net] bridge: ensure to unlock in error path in br_multicast_query() (Herbert Xu) [574321]
- [net] bridge: Fix RCU race in br_multicast_stop (Herbert Xu) [574321]
- [net] bridge: Use RCU list primitive in __br_mdb_ip_get (Herbert Xu) [574321]
- [net] bridge: cleanup: remove unneed check (Herbert Xu) [574321]
- [net] bridge: depends on INET (Herbert Xu) [574321]
- [net] bridge: Make IGMP snooping depend upon BRIDGE. (Herbert Xu) [574321]
- [net] bridge: Add core IGMP snooping support (Herbert Xu) [574321]
- [net] bridge: Fix br_forward crash in promiscuous mode (Herbert Xu) [574321]
- [net] bridge: Split may_deliver/deliver_clone out of br_flood (Herbert Xu) [574321]
- [net] bridge: Use BR_INPUT_SKB_CB on xmit path (Herbert Xu) [574321]
- [net] bridge: Avoid unnecessary clone on forward path (Herbert Xu) [574321]
- [net] bridge: Allow tail-call on br_pass_frame_up (Herbert Xu) [574321]
- [net] bridge: Do br_pass_frame_up after other ports (Herbert Xu) [574321]
- [net] Add netdev_alloc_skb_ip_align() helper (Herbert Xu) [574321]
- [kernel] futex_lock_pi() key refcnt fix (Danny Feng) [566347] {CVE-2010-0623}
- [pci] AER: fix aer inject result in kernel oops (Prarit Bhargava) [568515]
- [scsi] fix 32bit compatibility in BSG interface (Rob Evers) [554538]
- [x86] ACPI: don't cond_resched if irq is disabled (Danny Feng) [572441]
- [x86] Ensure dell-laptop buffers are below 4GB (Matthew Garrett) [570036]
- [hwmon] add hex '0x' indication to coretemp module output (Dean Nelson) [571865]
- [cifs] update cifs client code to latest upstream code (Jeff Layton) [562788]
- [block] fix merge_bvec_fn return value checks (Mike Snitzer) [571455]
- [fs] ext4: avoid uninit mem references on some mount options (Eric Sandeen) [562008]
- [s390x] dasd: Correct offline processing (Hendrik Brueckner) [568376]
- [s390x] dasd: Fix refcounting (Hendrik Brueckner) [568376]
- [x86] amd_iommu: remove dma-ops warning message (Bhavna Sarathy) [560002]
- [x86] amd_iommu: Fix IO page fault by adding device notifiers (Bhavna Sarathy) [560002]
- [x86] amd_iommu: Fix IOMMU API initialization for iommu=pt (Bhavna Sarathy) [560002]
- [x86] amd_iommu: Fix possible integer overflow (Bhavna Sarathy) [560002]
- [x86] amd_iommu: Fix deassignment of a device from the pt domain (Bhavna Sarathy) [560002]
- [gfs2] Allow the number of committed revokes to temporarily be negative (Benjamin Marzinski) [563907]
- [ppc64] powerpc: export data from new hcall H_EM_GET_PARMS (Steve Best) [570019]
- [x86] ACPI: Be in TS_POLLING state during mwait based C-state entry (Avi Kivity) [571440]
- [net] tcp: fix ICMP-RTO war (Jiri Olsa) [567532]
- [mm] Add padding to mm structures allow future patches during the RHEL6 life (Larry Woodman) [554511]

* Tue Mar 09 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-19.el6]
- [mm] Switch to SLAB (Aristeu Rozanski) [570614]

* Mon Mar 08 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-18.el6]
- [kernel/time] revert cc2f92ad1d0e03fe527e8ccfc1f918c368964dc8 (Aristeu Rozanski) [567551]
- [virt] hvc_console: Fix race between hvc_close and hvc_remove (Amit Shah) [568624]
- [scsi] Add netapp to scsi dh alua dev list (Mike Christie) [559586]
- [scsi] scsi_dh_emc: fix mode select setup (Mike Christie) [570685]
- [drm] Remove loop in IronLake graphics interrupt handler (John Villalovos) [557838]
- [x86] Intel Cougar Point chipset support (John Villalovos) [560077]
- [vhost] vhost-net: restart tx poll on sk_sndbuf full (Michael S. Tsirkin) [562837]
- [vhost] fix get_user_pages_fast error handling (Michael S. Tsirkin) [562837]
- [vhost] initialize log eventfd context pointer (Michael S. Tsirkin) [562837]
- [vhost] logging thinko fix (Michael S. Tsirkin) [562837]
- [vhost] vhost-net: switch to smp barriers (Michael S. Tsirkin) [562837]
- [net] bug fix for vlan + gro issue (Andy Gospodarek) [569922]
- [uv] Fix unmap_vma() bug related to mmu_notifiers (George Beshers) [253033]
- [uv] Have mmu_notifiers use SRCU so they may safely schedule (George Beshers) [253033]
- [drm] radeon/kms: bring all v2.6.33 fixes into EL6 kernel (Dave Airlie) [547422 554323 566618 569704]
- [dvb] Fix endless loop when decoding ULE at dvb-core (Mauro Carvalho Chehab) [569243]
- [kernel] sched: Fix SCHED_MC regression caused by change in sched cpu_power (Danny Feng) [568123]
- [s390x] vdso: glibc does not use vdso functions (Hendrik Brueckner) [567755]
- [drm] bring drm core/ttm/fb layer fixes in from upstream (Dave Airlie) [569701]
- [kernel] Fix SMT scheduler regression in find_busiest_queue() (Danny Feng) [568120]
- [s390x] qeth: avoid recovery during device online setting (Hendrik Brueckner) [568781]
- [mm] Fix potential crash with sys_move_pages (Danny Feng) [562591] {CVE-2010-0415}
- [scsi] pmcraid: bug fixes from upstream (Rob Evers) [567376]
- [scsi] lpfc Update from 8.3.5.4 to 8.3.5.5 FC/FCoE (Rob Evers) [564508]
- [ata] ahci: disable FPDMA auto-activate optimization on NVIDIA AHCI (David Milburn) [568815]
- [selinux] netlabel: fix corruption of SELinux MLS categories > 127 (Eric Paris) [568370]
- [gfs2] print glock numbers in hex (Robert S Peterson) [566755]
- [mm] Fix hugetlb.c clear_huge_page parameter (Andrea Arcangeli) [566604]
- [mm] fix anon_vma locking updates for transparent hugepage code (Andrea Arcangeli) [564515]
- [netdrv] cxgb3: add memory barriers (Steve Best) [568390]
- [dm] raid45 target: constructor error path oops fix (Heinz Mauelshagen) [567605]
- [scsi] mpt2sas: fix missing initialization (Tomas Henzl) [567965]
- [net] netfilter: nf_conntrack: per netns nf_conntrack_cachep (Jiri Pirko) [567181]
- [x86] nmi_watchdog: use __cpuinit for nmi_watchdog_default (Don Zickus) [567601]
- [netdrv] ixgbe: prevent speculative processing of descriptors (Steve Best) [568391]
- [kvm] Fix emulate_sys[call, enter, exit]()'s fault handling (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] Fix segment descriptor loading (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] Fix load_guest_segment_descriptor() to inject page fault (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] x86 emulator: Forbid modifying CS segment register by mov instruction (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] x86 emulator: Fix x86_emulate_insn() not to use the variable rc for non-X86EMUL values (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] x86 emulator: X86EMUL macro replacements: x86_emulate_insn() and its helpers (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] x86 emulator: X86EMUL macro replacements: from do_fetch_insn_byte() to x86_decode_insn() (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] inject #UD in 64bit mode from instruction that are not valid there (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] x86 emulator: Fix properties of instructions in group 1_82 (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] x86 emulator: code style cleanup (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] x86 emulator: Add LOCK prefix validity checking (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] x86 emulator: Check CPL level during privilege instruction emulation (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] x86 emulator: Fix popf emulation (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] x86 emulator: Check IOPL level during io instruction emulation (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] x86 emulator: fix memory access during x86 emulation (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] x86 emulator: Add Virtual-8086 mode of emulation (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] x86 emulator: Add group9 instruction decoding (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] x86 emulator: Add group8 instruction decoding (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] x86 emulator: Introduce No64 decode option (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [kvm] x86 emulator: Add 'push/pop sreg' instructions (Gleb Natapov) [560903 560904 563466] {CVE-2010-0298 CVE-2010-0306 CVE-2010-0419}
- [x86] AES/PCLMUL Instruction support: Various fixes for AES-NI and PCLMMUL (John Villalovos) [463496]
- [x86] AES/PCLMUL Instruction support: Use gas macro for AES-NI instructions (John Villalovos) [463496]
- [x86] AES/PCLMUL Instruction support: Various small fixes for AES/PCMLMUL and generate .byte code for some new instructions via gas macro (John Villalovos) [463496]
- [x86] AES/PCLMUL Instruction support: Add PCLMULQDQ accelerated implementation (John Villalovos) [463496]
- [scsi] megaraid_sas: fix for 32bit apps (Tomas Henzl) [559941]
- [kvm] fix large packet drops on kvm hosts with ipv6 (Neil Horman) [565525]
- [kvm] Add MAINTAINERS entry for virtio_console (Amit Shah) [566391]
- [kvm] virtio: console: Fill ports' entire in_vq with buffers (Amit Shah) [566391]
- [kvm] virtio: console: Error out if we can't allocate buffers for control queue (Amit Shah) [566391]
- [kvm] virtio: console: Add ability to remove module (Amit Shah) [566391]
- [kvm] virtio: console: Ensure no memleaks in case of unused buffers (Amit Shah) [566391]
- [kvm] virtio: console: update Red Hat copyright for 2010 (Amit Shah) [566391]
- [kvm] virtio: Initialize vq->data entries to NULL (Amit Shah) [566391]
- [kvm] virtio: console: outbufs are no longer needed (Amit Shah) [566391]
- [kvm] virtio: console: return -efault for fill_readbuf if copy_to_user fails (Amit Shah) [566391]
- [kvm] virtio: console: Allow sending variable-sized buffers to host, efault on copy_from_user err (Amit Shah) [566391]

* Thu Feb 18 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-17.el6]
- [s390] hvc_iucv: allocate IUCV send/receive buffers in DMA zone (Hendrik Brueckner) [566188]
- [s390] qdio: continue polling for buffer state ERROR (Hendrik Brueckner) [565528]
- [s390] qdio: prevent kernel bug message in interrupt handler (Hendrik Brueckner) [565542]
- [s390] zfcp: report BSG errors in correct field (Hendrik Brueckner) [564378]
- [s390] zfcp: cancel all pending work for a to be removed zfcp_port (Hendrik Brueckner) [564382]
- [nfs] mount.nfs: Unknown error 526 (Steve Dickson) [561975]
- [x86] x86-64, rwsem: Avoid store forwarding hazard in __downgrade_write (Avi Kivity) [563801]
- [x86] x86-64, rwsem: 64-bit xadd rwsem implementation (Avi Kivity) [563801]
- [x86] x86-64: support native xadd rwsem implementation (Avi Kivity) [563801]
- [x86] clean up rwsem type system (Avi Kivity) [563801]
- [x86] x86-32: clean up rwsem inline asm statements (Avi Kivity) [563801]
- [x86] nmi_watchdog: enable by default on RHEL-6 (Don Zickus) [523857]
- [block] freeze_bdev: don't deactivate successfully frozen MS_RDONLY sb (Mike Snitzer) [565890]
- [block] fix bio_add_page for non trivial merge_bvec_fn case (Mike Snitzer) [565890]
- [watchdog] Add support for iTCO watchdog on Ibex Peak chipset (John Villalovos) [536698]
- [kernel] time: Remove xtime_cache (Prarit Bhargava) [563135]
- [kernel] time: Implement logarithmic time accumalation (Prarit Bhargava) [563135]
- [dm] raid1: fail writes if errors are not handled and log fails (Mike Snitzer) [565890]
- [dm] mpath: fix stall when requeueing io (Mike Snitzer) [565890]
- [dm] log: userspace fix overhead_size calcuations (Mike Snitzer) [565890]
- [dm] stripe: avoid divide by zero with invalid stripe count (Mike Snitzer) [565890]
- [mm] anon_vma locking updates for transparent hugepage code (Rik van Riel) [564515]
- [mm] anon_vma linking changes to improve multi-process scalability (Rik van Riel) [564515]
- [virt] virtio_blk: add block topology support (Christoph Hellwig) [556477]
- [kvm] PIT: control word is write-only (Eduardo Habkost) [560905] {CVE-2010-0309}
- [kernel] Prevent futex user corruption to crash the kernel (Jerome Marchand) [563957]
- [selinux] print the module name when SELinux denies a userspace upcall (Eric Paris) [563731]
- [gfs] GFS2 problems on single node cluster (Steven Whitehouse) [564329]
- [ppc] Add kdump support to Collaborative Memory Manager (Steve Best) [563316]

* Fri Feb 12 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-16.el6]
- [nfs] Remove a redundant check for PageFsCache in nfs_migrate_page() (Steve Dickson) [563938]
- [nfs] Fix a bug in nfs_fscache_release_page() (Steve Dickson) [563938]
- [mm] fix BUG()s caused by the transparent hugepage patch (Larry Woodman) [556572]
- [fs] inotify: fix inotify WARN and compatibility issues (Eric Paris) [563363]
- [net] do not check CAP_NET_RAW for kernel created sockets (Eric Paris) [540560]
- [pci] Enablement of PCI ACS control when IOMMU enabled on system (Don Dutile) [523278]
- [pci] PCI ACS support functions (Don Dutile) [523278]
- [uv] x86: Fix RTC latency bug by reading replicated cachelines (George Beshers) [562189]
- [s390x] ctcm / lcs / claw: remove cu3088 layer (Hendrik Brueckner) [557522]
- [uv] vgaarb: add user selectability of the number of gpus in a system (George Beshers) [555879]
- [gpu] vgaarb: fix vga arbiter to accept PCI domains other than 0 (George Beshers) [555879]
- [uv] x86_64: update uv arch to target legacy VGA I/O correctly (George Beshers) [555879]
- [pci] update pci_set_vga_state to call arch functions (George Beshers) [555879]
- [uv] PCI: update pci_set_vga_state to call arch functions (George Beshers) [555879]
- [mm] remove madvise(MADV_HUGEPAGE) (Andrea Arcangeli) [556572]
- [mm] hugepage redhat customization (Andrea Arcangeli) [556572]
- [mm] introduce khugepaged (Andrea Arcangeli) [556572]
- [mm] transparent hugepage vmstat (Andrea Arcangeli) [556572]
- [mm] memcg huge memory (Andrea Arcangeli) [556572]
- [mm] memcg compound (Andrea Arcangeli) [556572]
- [mm] pmd_trans_huge migrate bugcheck (Andrea Arcangeli) [556572]
- [mm] madvise(MADV_HUGEPAGE) (Andrea Arcangeli) [556572]
- [mm] verify pmd_trans_huge isnt leaking (Andrea Arcangeli) [556572]
- [mm] transparent hugepage core (Andrea Arcangeli) [556572]
- [mm] dont alloc harder for gfp nomemalloc even if nowait (Andrea Arcangeli) [556572]
- [mm] introduce _GFP_NO_KSWAPD (Andrea Arcangeli) [556572]
- [mm] backport page_referenced microoptimization (Andrea Arcangeli) [556572]
- [mm] kvm mmu transparent hugepage support (Andrea Arcangeli) [556572]
- [mm] clear_copy_huge_page (Andrea Arcangeli) [556572]
- [mm] clear_huge_page fix (Andrea Arcangeli) [556572]
- [mm] split_huge_page paging (Andrea Arcangeli) [556572]
- [mm] split_huge_page_mm/vma (Andrea Arcangeli) [556572]
- [mm] add pmd_huge_pte to mm_struct (Andrea Arcangeli) [556572]
- [mm] clear page compound (Andrea Arcangeli) [556572]
- [mm] add pmd mmu_notifier helpers (Andrea Arcangeli) [556572]
- [mm] pte alloc trans splitting (Andrea Arcangeli) [556572]
- [mm] bail out gup_fast on splitting pmd (Andrea Arcangeli) [556572]
- [mm] add pmd mangling functions to x86 (Andrea Arcangeli) [556572]
- [mm] add pmd mangling generic functions (Andrea Arcangeli) [556572]
- [mm] special pmd_trans_* functions (Andrea Arcangeli) [556572]
- [mm] config_transparent_hugepage (Andrea Arcangeli) [556572]
- [mm] comment reminder in destroy_compound_page (Andrea Arcangeli) [556572]
- [mm] export maybe_mkwrite (Andrea Arcangeli) [556572]
- [mm] no paravirt version of pmd ops (Andrea Arcangeli) [556572]
- [mm] add pmd paravirt ops (Andrea Arcangeli) [556572]
- [mm] add native_set_pmd_at (Andrea Arcangeli) [556572]
- [mm] clear compound mapping (Andrea Arcangeli) [556572]
- [mm] update futex compound knowledge (Andrea Arcangeli) [556572]
- [mm] alter compound get_page/put_page (Andrea Arcangeli) [556572]
- [mm] add a compound_lock (Andrea Arcangeli) [556572]
- [mm] define MADV_HUGEPAGE (Andrea Arcangeli) [556572]
- [oprofile] Support Nehalem-EX CPU in Oprofile (John Villalovos) [528998]
- [nfs] nfs: handle NFSv3 -EKEYEXPIRED errors as we would -EJUKEBOX (Jeff Layton) [479359]
- [nfs] handle NFSv2 -EKEYEXPIRED returns from RPC layer appropriately (Jeff Layton) [479359]
- [nfs] sunrpc: parse and return errors reported by gssd (Jeff Layton) [479359]
- [nfs] nfs4: handle -EKEYEXPIRED errors from RPC layer (Jeff Layton) [479359]
- [net] nf_conntrack: fix memory corruption (Jon Masters) [559471]
- [kvm] emulate accessed bit for EPT (Rik van Riel) [555106]
- [vhost] fix TUN=m VHOST_NET=y (Michael S. Tsirkin) [562837]
- [vhost] vhost-net: defer f->private_data until setup succeeds (Chris Wright) [562837]
- [vhost] vhost-net: comment use of invalid fd when setting vhost backend (Chris Wright) [562837]
- [vhost] access check thinko fixes (Michael S. Tsirkin) [562837]
- [vhost] make default mapping empty by default (Michael S. Tsirkin) [562837]
- [vhost] add access_ok checks (Michael S. Tsirkin) [562837]
- [vhost] prevent modification of an active ring (Michael S. Tsirkin) [562837]
- [vhost] fix high 32 bit in FEATURES ioctls (Michael S. Tsirkin) [562837]
- [dm] dm-raid1: fix deadlock at suspending failed device (Takahiro Yasui) [557932]
- [dm] fix kernel panic at releasing bio on recovery failed region (Takahiro Yasui) [557934]
- [scsi] lpfc Update from 8.3.4 to 8.3.5.4 FC/FCoE (Rob Evers) [531028]
- [nfs] sunrpc/cache: fix module refcnt leak in a failure path (Steve Dickson) [562285]
- [nfs] Ensure that we handle NFS4ERR_STALE_STATEID correctly (Steve Dickson) [560784]
- [nfs] NFSv4.1: Don't call nfs4_schedule_state_recovery() unnecessarily (Steve Dickson) [560784]
- [nfs] NFSv4: Don't allow posix locking against servers that don't support it (Steve Dickson) [560784]
- [nfs] Ensure that the NFSv4 locking can recover from stateid errors (Steve Dickson) [560784]
- [nfs] Avoid warnings when CONFIG_NFS_V4=n (Steve Dickson) [560784]
- [nfs] Make nfs_commitdata_release static (Steve Dickson) [560784]
- [nfs] Try to commit unstable writes in nfs_release_page() (Steve Dickson) [560784]
- [nfs] Fix a reference leak in nfs_wb_cancel_page() (Steve Dickson) [560784]
- [nfs] nfs41: cleanup callback code to use __be32 type (Steve Dickson) [560785]
- [nfs] nfs41: clear NFS4CLNT_RECALL_SLOT bit on session reset (Steve Dickson) [560785]
- [nfs] nfs41: fix nfs4_callback_recallslot (Steve Dickson) [560785]
- [nfs] nfs41: resize slot table in reset (Steve Dickson) [560785]
- [nfs] nfs41: implement cb_recall_slot (Steve Dickson) [560785]
- [nfs] nfs41: back channel drc minimal implementation (Steve Dickson) [560785]
- [nfs] nfs41: prepare for back channel drc (Steve Dickson) [560785]
- [nfs] nfs41: remove uneeded checks in callback processing (Steve Dickson) [560785]
- [nfs] nfs41: directly encode back channel error (Steve Dickson) [560785]
- [nfs] nfs41: fix wrong error on callback header xdr overflow (Steve Dickson) [560785]
- [nfs] nfs41: Process callback's referring call list (Steve Dickson) [560785]
- [nfs] nfs41: Check slot table for referring calls (Steve Dickson) [560785]
- [nfs] nfs41: Adjust max cache response size value (Steve Dickson) [560785]
- [nfs] NFSD: Create PF_INET6 listener in write_ports (Steve Dickson) [560785]
- [nfs] SUNRPC: NFS kernel APIs shouldn't return ENOENT for "transport not found" (Steve Dickson) [560785]
- [nfs] SUNRPC: Bury "#ifdef IPV6" in svc_create_xprt() (Steve Dickson) [560785]
- [nfs] NFSD: Support AF_INET6 in svc_addsock() function (Steve Dickson) [560785]
- [nfs] SUNRPC: Use rpc_pton() in ip_map_parse() (Steve Dickson) [560785]
- [nfs] nfsd: 4.1 has an rfc number (Steve Dickson) [560785]
- [nfs] nfsd41: Create the recovery entry for the NFSv4.1 client (Steve Dickson) [560785]
- [nfs] nfsd: use vfs_fsync for non-directories (Steve Dickson) [560785]
- [nfs] nfsd4: Use FIRST_NFS4_OP in nfsd4_decode_compound() (Steve Dickson) [560785]
- [nfs] nfsd41: nfsd4_decode_compound() does not recognize all ops (Steve Dickson) [560785]

* Fri Feb 05 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-15.el6]
- [block] blk-cgroup: Fix lockdep warning of potential deadlock in blk-cgroup (Vivek Goyal) [561903]
- [block] cfq: Do not idle on async queues and drive deeper WRITE depths (Vivek Goyal) [561902]
- [quota] 64-bit quota format fixes (Jerome Marchand) [546311]
- [x86] fix Add AMD Node ID MSR support (Bhavna Sarathy) [557540]
- [fs] ext4: fix type of "offset" in ext4_io_end (Eric Sandeen) [560097]
- [x86] Disable HPET MSI on ATI SB700/SB800 (Prarit Bhargava) [557332]
- [x86] arch specific support for remapping HPET MSIs (Prarit Bhargava) [557332]
- [x86] intr-remap: generic support for remapping HPET MSIs (Prarit Bhargava) [557332]
- [gfs] GFS2: Extend umount wait coverage to full glock lifetime (Steven Whitehouse) [561287]
- [gfs] GFS2: Wait for unlock completion on umount (Steven Whitehouse) [561287]
- [gfs] GFS2: Use MAX_LFS_FILESIZE for meta inode size (Steven Whitehouse) [561307]
- [gfs] GFS2: Use GFP_NOFS for alloc structure (Steven Whitehouse) [561307]
- [gfs] GFS2: Fix refcnt leak on gfs2_follow_link() error path (Steven Whitehouse) [561307]

* Wed Feb 03 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-14.el6]
- [s390x] dasd: fix online/offline race (Hendrik Brueckner) [552840]
- [netdrv] update tg3 to version 3.106 and fix panic (John Feeney) [555101]
- [s390x] dasd: Fix null pointer in s390dbf and discipline checking (Hendrik Brueckner) [559615]
- [s390x] zcrypt: Do not remove coprocessor in case of error 8/72 (Hendrik Brueckner) [559613]
- [s390x] cio: channel path vary operation has no effect (Hendrik Brueckner) [559612]
- [uv] x86: Ensure hub revision set for all ACPI modes (George Beshers) [559752]
- [uv] x86: Add function retrieving node controller revision number (George Beshers) [559752]

* Fri Jan 29 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-13.el6]
- [virtio] console: show error message if hvc_alloc fails for console ports (Amit Shah) [543824]
- [virtio] console: Add debugfs files for each port to expose debug info (Amit Shah) [543824]
- [virtio] console: Add ability to hot-unplug ports (Amit Shah) [543824]
- [virtio] hvc_console: Export (GPL'ed) hvc_remove (Amit Shah) [543824]
- [virtio] Add ability to detach unused buffers from vrings (Amit Shah) [543824]
- [virtio] console: Handle port hot-plug (Amit Shah) [543824]
- [virtio] console: Remove cached data on port close (Amit Shah) [543824]
- [virtio] console: Register with sysfs and create a 'name' attribute for ports (Amit Shah) [543824]
- [virtio] console: Ensure only one process can have a port open at a time (Amit Shah) [543824]
- [virtio] console: Add file operations to ports for open/read/write/poll (Amit Shah) [543824]
- [virtio] console: Associate each port with a char device (Amit Shah) [543824]
- [virtio] console: Prepare for writing to / reading from userspace buffers (Amit Shah) [543824]
- [virtio] console: Add a new MULTIPORT feature, support for generic ports (Amit Shah) [543824]
- [virtio] console: Introduce a send_buf function for a common path for sending data to host (Amit Shah) [543824]
- [virtio] console: Introduce function to hand off data from host to readers (Amit Shah) [543824]
- [virtio] console: Separate out find_vqs operation into a different function (Amit Shah) [543824]
- [virtio] console: Separate out console init into a new function (Amit Shah) [543824]
- [virtio] console: Separate out console-specific data into a separate struct (Amit Shah) [543824]
- [virtio] console: ensure console size is updated on hvc open (Amit Shah) [543824]
- [virtio] console: struct ports for multiple ports per device. (Amit Shah) [543824]
- [virtio] console: remove global var (Amit Shah) [543824]
- [virtio] console: don't assume a single console port. (Amit Shah) [543824]
- [virtio] console: use vdev->priv to avoid accessing global var. (Amit Shah) [543824]
- [virtio] console: introduce a get_inbuf helper to fetch bufs from in_vq (Amit Shah) [543824]
- [virtio] console: ensure add_inbuf can work for multiple ports as well (Amit Shah) [543824]
- [virtio] console: encapsulate buffer information in a struct (Amit Shah) [543824]
- [virtio] console: port encapsulation (Amit Shah) [543824]
- [virtio] console: We support only one device at a time (Amit Shah) [543824]
- [virtio] hvc_console: Remove __devinit annotation from hvc_alloc (Amit Shah) [543824]
- [virtio] hvc_console: make the ops pointer const. (Amit Shah) [543824]
- [virtio] console: statically initialize virtio_cons (Amit Shah) [543824]
- [virtio] console: comment cleanup (Amit Shah) [543824]
- [x86] Fix crash when profiling more than 28 events (Bhavna Sarathy) [557570]
- [x86] Add AMD Node ID MSR support (Bhavna Sarathy) [557540]
- [kvm] fix spurious interrupt with irqfd (Marcelo Tosatti) [559343]
- [kvm] eventfd: allow atomic read and waitqueue remove (Marcelo Tosatti) [559343]
- [kvm] properly check max PIC pin in irq route setup (Marcelo Tosatti) [559343]
- [kvm] only allow one gsi per fd (Marcelo Tosatti) [559343]
- [kvm] x86: Fix leak of free lapic date in kvm_arch_vcpu_init() (Marcelo Tosatti) [559343]
- [kvm] x86: Fix probable memory leak of vcpu->arch.mce_banks (Marcelo Tosatti) [559343]
- [kvm] MMU: bail out pagewalk on kvm_read_guest error (Marcelo Tosatti) [559343]
- [kvm] x86: Fix host_mapping_level() (Marcelo Tosatti) [559343]
- [kvm] Fix race between APIC TMR and IRR (Marcelo Tosatti) [559343]
- [x86] acpi: Export acpi_pci_irq_{add|del}_prt() (James Paradis) [553781]
- [kdump] backport upstream ppc64 kcrctab fixes (Neil Horman) [558803]
- [mm] Memory tracking for Stratus (James Paradis) [512400]

* Thu Jan 28 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-12.el6]
- [drm] radeon possible security issue (Jerome Glisse) [556692]
- [mm] Memory tracking for Stratus (James Paradis) [512400]
- [pci] Always set prefetchable base/limit upper32 registers (Prarit Bhargava) [553471]
- [scsi] Sync be2iscsi with upstream (Mike Christie) [515256]
- [x86] msr/cpuid: Register enough minors for the MSR and CPUID drivers (George Beshers) [557554]
- [x86] Remove unnecessary mdelay() from cpu_disable_common() (Peter Bogdanovic) [463633]
- [x86] ioapic: Document another case when level irq is seen as an edge (Peter Bogdanovic) [463633]
- [x86] ioapic: Fix the EOI register detection mechanism (Peter Bogdanovic) [463633]
- [x86] io-apic: Move the effort of clearing remoteIRR explicitly before migrating the irq (Peter Bogdanovic) [463633]
- [x86] Remove local_irq_enable()/local_irq_disable() in fixup_irqs() (Peter Bogdanovic) [463633]
- [x86] Use EOI register in io-apic on intel platforms (Peter Bogdanovic) [463633]

* Tue Jan 26 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-11.el6]
- [kdump] Remove the 32MB limitation for crashkernel (Steve Best) [529270]
- [dm] dm-raid45: export missing dm_rh_inc (Heinz Mauelshagen) [552329]
- [block] dm-raid45: add raid45 target (Heinz Mauelshagen) [552329]
- [block] dm-replicator: blockdev site link handler (Heinz Mauelshagen) [552364]
- [block] dm-replicator: ringbuffer replication log handler (Heinz Mauelshagen) [552364]
- [block] dm-replicator: replication log and site link handler interfaces and main replicator module (Heinz Mauelshagen) [552364]
- [block] dm-replicator: documentation and module registry (Heinz Mauelshagen) [552364]
- [s390x] qeth: set default BLKT settings dependend on OSA hw level (Hendrik Brueckner) [557474]
- [drm] bring RHEL6 radeon drm up to 2.6.33-rc4/5 level (Jerome Glisse) [557539]
- [netdrv] e1000e: enhance frame fragment detection (Andy Gospodarek) [462780]
- [stable] ipv6: skb_dst() can be NULL in ipv6_hop_jumbo(). (David S. Miller) [555084]
- [stable] module: handle ppc64 relocating kcrctabs when CONFIG_RELOCATABLE=y (Rusty Russell) [555084]
- [stable] fix more leaks in audit_tree.c tag_chunk() (Al Viro) [555084]
- [stable] fix braindamage in audit_tree.c untag_chunk() (Al Viro) [555084]
- [stable] mac80211: fix skb buffering issue (and fixes to that) (Johannes Berg) [555084]
- [stable] kernel/sysctl.c: fix stable merge error in NOMMU mmap_min_addr (Mike Frysinger) [555084]
- [stable] libertas: Remove carrier signaling from the scan code (Samuel Ortiz) [555084]
- [stable] mac80211: add missing sanity checks for action frames (Felix Fietkau) [555084]
- [stable] iwl: off by one bug (Dan Carpenter) [555084]
- [stable] cfg80211: fix syntax error on user regulatory hints (Luis R. Rodriguez) [555084]
- [stable] ath5k: Fix eeprom checksum check for custom sized eeproms (Luis R. Rodriguez) [555084]
- [stable] iwlwifi: fix iwl_queue_used bug when read_ptr == write_ptr (Zhu Yi) [555084]
- [stable] xen: fix hang on suspend. (Ian Campbell) [555084]
- [stable] quota: Fix dquot_transfer for filesystems different from ext4 (Jan Kara) [555084]
- [stable] hwmon: (adt7462) Fix pin 28 monitoring (Roger Blofeld) [555084]
- [stable] hwmon: (coretemp) Fix TjMax for Atom N450/D410/D510 CPUs (Yong Wang) [555084]
- [stable] netfilter: nf_ct_ftp: fix out of bounds read in update_nl_seq() (Patrick McHardy) [555084]
- [stable] netfilter: ebtables: enforce CAP_NET_ADMIN (Florian Westphal) [555084]
- [stable] ASoC: Fix WM8350 DSP mode B configuration (Mark Brown) [555084]
- [stable] ALSA: atiixp: Specify codec for Foxconn RC4107MA-RS2 (Daniel T Chen) [555084]
- [stable] ALSA: ac97: Add Dell Dimension 2400 to Headphone/Line Jack Sense blacklist (Daniel T Chen) [555084]
- [stable] mmc_block: fix queue cleanup (Adrian Hunter) [555084]
- [stable] mmc_block: fix probe error cleanup bug (Jarkko Lavinen) [555084]
- [stable] mmc_block: add dev_t initialization check (Anna Lemehova) [555084]
- [stable] kernel/signal.c: fix kernel information leak with print-fatal-signals=1 (Andi Kleen) [555084]
- [stable] dma-debug: allow DMA_BIDIRECTIONAL mappings to be synced with DMA_FROM_DEVICE and (Krzysztof Halasa) [555084]
- [stable] lib/rational.c needs module.h (Sascha Hauer) [555084]
- [stable] drivers/cpuidle/governors/menu.c: fix undefined reference to `__udivdi3' (Stephen Hemminger) [555084]
- [stable] rtc_cmos: convert shutdown to new pnp_driver->shutdown (OGAWA Hirofumi) [555084]
- [stable] Revert "x86: Side-step lguest problem by only building cmpxchg8b_emu for pre-Pentium" (Rusty Russell) [555084]
- [stable] exofs: simple_write_end does not mark_inode_dirty (Boaz Harrosh) [555084]
- [stable] modules: Skip empty sections when exporting section notes (Ben Hutchings) [555084]
- [stable] ASoC: fix params_rate() macro use in several codecs (Guennadi Liakhovetski) [555084]
- [stable] fasync: split 'fasync_helper()' into separate add/remove functions (Linus Torvalds) [555084]
- [stable] untangle the do_mremap() mess (Al Viro)

* Fri Jan 22 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-10.el6]
- [mm] mmap: don't return ENOMEM when mapcount is temporarily exceeded in munmap() (Danny Feng) [557000]
- [netdrv] vxge: fix issues found in Neterion testing (Michal Schmidt) [493985]
- [x86] Force irq complete move during cpu offline (Prarit Bhargava) [541815]
- [sound] Fix SPDIF-In for AD1988 codecs + add Intel Cougar IDs (Jaroslav Kysela) [557473]
- [scsi] aic79xx: check for non-NULL scb in ahd_handle_nonpkt_busfree (Tomas Henzl) [557753]
- [s390x] fix loading of PER control registers for utrace. (CAI Qian) [556410]
- [s390x] ptrace: dont abuse PT_PTRACED (CAI Qian) [552102]
- [perf] Remove the "event" callback from perf events (Jason Baron) [525517]
- [perf] Use overflow handler instead of the event callback (Jason Baron) [525517]
- [perf] Fix locking for PERF_FORMAT_GROUP (Jason Baron) [525517]
- [perf] Fix event scaling for inherited counters (Jason Baron) [525517]
- [perf] Fix PERF_FORMAT_GROUP scale info (Jason Baron) [525517]
- [perf] Allow for custom overflow handlers (Jason Baron) [525517]
- [perf] Add a callback to perf events (Jason Baron) [525517]
- [perf] improve error reporting (Jason Baron) [525517]
- [perf] add kernel internal interface (Jason Baron) [525517]
- [utrace] fix utrace_maybe_reap() vs find_matching_engine() race (Oleg Nesterov) [557338]
- [x86] Disable Memory hot add on x86 32-bit (Prarit Bhargava) [557131]
- [netdrv] e1000e: update to the latest upstream (Andy Gospodarek) [462780]
- [gfs] Use dquot_send_warning() (Steven Whitehouse) [557057]
- [gfs] Add quota netlink support (Steven Whitehouse) [557057]
- [netdrv] qlge: update to upstream version v1.00.00.23.00.00-01 (Andy Gospodarek) [553357]
- [s390x] zfcp: set HW timeout requested by BSG request (Hendrik Brueckner) [556918]
- [s390x] zfcp: introduce BSG timeout callback (Hendrik Brueckner) [556918]
- [scsi] scsi_transport_fc: Allow LLD to reset FC BSG timeout (Hendrik Brueckner) [556918]

* Wed Jan 20 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-9.el6]
- [kvm] fix cleanup_srcu_struct on vm destruction (Marcelo Tosatti) [554762]
- [x86] core: make LIST_POISON less deadly (Avi Kivity) [554640]
- [x86] dell-wmi: Add support for new Dell systems (Matthew Garrett) [525548]
- [fs] xfs: 2.6.33 updates (Eric Sandeen) [554891]
- [x86] Add kernel pagefault tracepoint for x86 & x86_64. (Larry Woodman) [526032]
- [pci] PCIe AER: honor ACPI HEST FIRMWARE FIRST mode (Matthew Garrett) [537205]
- [block] direct-io: cleanup blockdev_direct_IO locking (Eric Sandeen) [556547]
- [tracing] tracepoint: Add signal tracepoints (Masami Hiramatsu) [526030]
- [cgroups] fix for "kernel BUG at kernel/cgroup.c:790" (Dave Anderson) [547815]
- [irq] Expose the irq_desc node as /proc/irq/*/node (George Beshers) [555866]
- [scsi] qla2xxx - Update support for FC/FCoE HBA/CNA (Rob Evers) [553854]
- [scsi] bfa update from 2.1.2.0 to 2.1.2.1 (Rob Evers) [475704]
- [nfs] sunrpc: fix build-time warning (Steve Dickson) [437715]
- [nfs] sunrpc: on successful gss error pipe write, don't return error (Steve Dickson) [437715]
- [nfs] SUNRPC: Fix the return value in gss_import_sec_context() (Steve Dickson) [437715]
- [nfs] SUNRPC: Fix up an error return value in gss_import_sec_context_kerberos() (Steve Dickson) [437715]
- [nfs] sunrpc: fix peername failed on closed listener (Steve Dickson) [437715]
- [nfs] nfsd: make sure data is on disk before calling ->fsync (Steve Dickson) [437715]
- [uv] React 2.6.32.y: isolcpus broken in 2.6.32.y kernel (George Beshers) [548842]
- [gru] GRU Rollup patch (George Beshers) [546680]
- [uv] XPC: pass nasid instead of nid to gru_create_message_queue (George Beshers) [546695]
- [uv] x86: XPC receive message reuse triggers invalid BUG_ON (George Beshers) [546695]
- [uv] x86: xpc_make_first_contact hang due to not accepting ACTIVE state (George Beshers) [546695]
- [uv] x86: xpc NULL deref when mesq becomes empty (George Beshers) [546695]
- [uv] x86: update XPC to handle updated BIOS interface (George Beshers) [546695]
- [uv] xpc needs to provide an abstraction for uv_gpa (George Beshers) [546695]
- [uv] x86, irq: Check move_in_progress before freeing the vector mapping (George Beshers) [546668]
- [uv] x86: Remove move_cleanup_count from irq_cfg (George Beshers) [546668]
- [uv] x86, irq: Allow 0xff for /proc/irq/[n]/smp_affinity on an 8-cpu system (George Beshers) [546668]
- [uv] x86, apic: Move SGI UV functionality out of generic IO-APIC code (George Beshers) [546668]
- [uv] x86 SGI: Fix irq affinity for hub based interrupts (George Beshers) [546668]
- [uv] x86 RTC: Always enable RTC clocksource (George Beshers) [546668]
- [uv] x86 RTC: Rename generic_interrupt to x86_platform_ipi (George Beshers) [546668]
- [uv] x86, mm: Correct the implementation of is_untracked_pat_range() (George Beshers) [548524]
- [uv] x86: Change is_ISA_range() into an inline function (George Beshers) [548524]
- [uv] x86, platform: Change is_untracked_pat_range() to bool (George Beshers) [548524]
- [uv] x86, mm: is_untracked_pat_range() takes a normal semiclosed range (George Beshers) [548524]
- [uv] x86, mm: Call is_untracked_pat_range() rather than is_ISA_range() (George Beshers) [548524]
- [uv] x86 SGI: Dont track GRU space in PAT (George Beshers) [548524]
- [scsi] megaraid: upgrade to 4.17 (Tomas Henzl) [520729]
- [scsi] mpt2sas: Bump version 03.100.03.00 (Tomas Henzl) [470848]
- [scsi] mpt2sas: don't update links nor unblock device at no link rate change (Tomas Henzl) [470848]
- [scsi] mpt2sas: add support for RAID Action System Shutdown Initiated at OS Shutdown (Tomas Henzl) [470848]
- [scsi] mpt2sas: freeze the sdev IO queue when firmware sends internal device reset (Tomas Henzl) [470848]
- [scsi] mpt2sas: fix PPC endian bug (Tomas Henzl) [470848]
- [scsi] mpt2sas: mpt2sas_base_get_sense_buffer_dma returns little endian (Tomas Henzl) [470848]
- [scsi] mpt2sas: return DID_TRANSPORT_DISRUPTED in nexus loss and SCSI_MLQUEUE_DEVICE_BUSY if device is busy (Tomas Henzl) [470848]
- [scsi] mpt2sas: retrieve the ioc facts prior to putting the controller into READY state (Tomas Henzl) [470848]
- [scsi] mpt2sas: add new info messages for IR and Expander events (Tomas Henzl) [470848]
- [scsi] mpt2sas: limit the max_depth to 32 for SATA devices (Tomas Henzl) [470848]
- [scsi] mpt2sas: add TimeStamp support when sending ioc_init (Tomas Henzl) [470848]
- [scsi] mpt2sas: add extended type for diagnostic buffer support (Tomas Henzl) [470848]
- [scsi] mpt2sas: add command line option diag_buffer_enable (Tomas Henzl) [470848]
- [scsi] mpt2sas: fix some comments (Tomas Henzl) [470848]
- [scsi] mpt2sas: stop driver when firmware encounters faults (Tomas Henzl) [470848]
- [scsi] mpt2sas: adding MPI Headers - revision L (Tomas Henzl) [470848]
- [scsi] mpt2sas: new device SAS2208 support (Tomas Henzl) [470848]
- [scsi] mpt2sas: check for valid response info (Tomas Henzl) [470848]
- [scsi] mpt2sas: fix expander remove fail (Tomas Henzl) [470848]
- [scsi] mpt2sas: use sas address instead of handle as a lookup (Tomas Henzl) [470848]
- [sound] ALSA HDA driver update 2009-12-15 (Jaroslav Kysela) [555812]
- [block] Honor the gfp_mask for alloc_page() in blkdev_issue_discard() (Mike Snitzer) [554719]
- [scsi] sync fcoe with upstream (Mike Christie) [549945]
- [net] dccp: modify how dccp creates slab caches to prevent bug halt in SLUB (Neil Horman) [553698]
- [s390x] tape: Add pr_fmt() macro to all tape source files (Hendrik Brueckner) [554380]
- [s390] qeth: fix packet loss if TSO is switched on (Hendrik Brueckner) [546632]
- [s390x] qeth: Support for HiperSockets Network Traffic Analyzer (Hendrik Brueckner) [463706]
- [serial] 8250: add support for DTR/DSR hardware flow control (Mauro Carvalho Chehab) [523848]

* Tue Jan 19 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-8.el6]
- [build] Revert "[redhat] disabling temporaly DEVTMPFS" (Aristeu Rozanski)

* Tue Jan 19 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-7.el6]
- [drm] minor printk fixes from upstream (Dave Airlie) [554601]
- [offb] add support for framebuffer handoff to offb. (Dave Airlie) [554948]
- [x86] allow fbdev primary video code on 64-bit. (Dave Airlie) [554930]
- [drm] nouveau: update to 2.6.33 level (Dave Airlie) [549930]
- [drm] ttm: validation API changes + ERESTART fixes. (Dave Airlie) [554918]
- [drm] radeon/kms: update to 2.6.33 (without TTM API changes) (Dave Airlie) [554918]
- [drm] i915: bring Intel DRM/KMS driver up to 2.6.33 (Dave Airlie) [554616]
- [drm] radeon/intel: realign displayport helper code with upstream. (Dave Airlie) [554601]
- [drm] kms: rollup KMS core and helper changes to 2.6.33 (Dave Airlie) [554601]
- [drm] remove address mask param for drm_pci_alloc() (Dave Airlie) [554601]
- [drm] add new userspace core drm interfaces from 2.6.33 (Dave Airlie) [554601]
- [drm] unlocked ioctl support for core + macro fixes (Dave Airlie) [554601]
- [drm] ttm: rollup upstream TTM fixes (Dave Airlie) [554601]
- [drm] mm: patch drm core memory range manager up to 2.6.33 (Dave Airlie) [554601]
- [drm] drm/edid: update to 2.6.33 EDID parser code (Dave Airlie) [554601]
- [net] dccp: fix module load dependency btw dccp_probe and dccp (Neil Horman) [554840]
- [powerpc] pseries: Correct pseries/dlpar.c build break without CONFIG_SMP (Steve Best) [539318]
- [powerpc] cpu-allocation/deallocation process (Steve Best) [539318]
- [powerpc] Add code to online/offline CPUs of a DLPAR node (Steve Best) [539318]
- [powerpc] CPU DLPAR handling (Steve Best) [539318]
- [powerpc] sysfs cpu probe/release files (Steve Best) [539318]
- [powerpc] Kernel handling of Dynamic Logical Partitioning (Steve Best) [539318]
- [powerpc] pseries: Add hooks to put the CPU into an appropriate offline state (Steve Best) [539318]
- [powerpc] pseries: Add extended_cede_processor() helper function. (Steve Best) [539318]
- [gfs] GFS2: Fix glock refcount issues (Steven Whitehouse) [546634]
- [gfs] GFS2: Ensure uptodate inode size when using O_APPEND (Steven Whitehouse) [547639]
- [gfs] GFS2: Fix locking bug in rename (Steven Whitehouse) [547640]
- [gfs] GFS2: Fix lock ordering in gfs2_check_blk_state() (Steven Whitehouse) [554673]
- [gfs2] only show nobarrier option on /proc/mounts when the option is active (Steven Whitehouse) [546665]
- [gfs2] add barrier/nobarrier mount options (Steven Whitehouse) [546665]
- [gfs2] remove division from new statfs code (Steven Whitehouse) [298561]
- [gfs2] Improve statfs and quota usability (Steven Whitehouse) [298561]
- [gfs2] Add set_xquota support (Steven Whitehouse) [298561]
- [gfs2] Add get_xquota support (Steven Whitehouse) [298561]
- [gfs2] Clean up gfs2_adjust_quota() and do_glock() (Steven Whitehouse) [298561]
- [gfs2] Remove constant argument from qd_get() (Steven Whitehouse) [298561]
- [gfs2] Remove constant argument from qdsb_get() (Steven Whitehouse) [298561]
- [gfs2] Add proper error reporting to quota sync via sysfs (Steven Whitehouse) [298561]
- [gfs2] Add get_xstate quota function (Steven Whitehouse) [298561]
- [gfs2] Remove obsolete code in quota.c (Steven Whitehouse) [298561]
- [gfs2] Hook gfs2_quota_sync into VFS via gfs2_quotactl_ops (Steven Whitehouse) [298561]
- [gfs2] Alter arguments of gfs2_quota/statfs_sync (Steven Whitehouse) [298561]
- [gfs2] Fix -o meta mounts for subsequent mounts (Steven Whitehouse) [546664]
- [gfs] GFS2: Fix gfs2_xattr_acl_chmod() (Steven Whitehouse) [546294]
- [gfs] VFS: Use GFP_NOFS in posix_acl_from_xattr() (Steven Whitehouse) [546294]
- [gfs] GFS2: Add cached ACLs support (Steven Whitehouse) [546294]
- [gfs] GFS2: Clean up ACLs (Steven Whitehouse) [546294]
- [gfs] GFS2: Use gfs2_set_mode() instead of munge_mode() (Steven Whitehouse) [546294]
- [gfs] GFS2: Use forget_all_cached_acls() (Steven Whitehouse) [546294]
- [gfs] VFS: Add forget_all_cached_acls() (Steven Whitehouse) [546294]
- [gfs] GFS2: Fix up system xattrs (Steven Whitehouse) [546294]
- [netdrv] igb: Update igb driver to support Barton Hills (Stefan Assmann) [462783]
- [dm] add feature flags to reduce future kABI impact (Mike Snitzer) [547756]
- [block] Stop using byte offsets (Mike Snitzer) [554718]
- [dm] Fix device mapper topology stacking (Mike Snitzer) [554718]
- [block] bdev_stack_limits wrapper (Mike Snitzer) [554718]
- [block] Fix discard alignment calculation and printing (Mike Snitzer) [554718]
- [block] Correct handling of bottom device misaligment (Mike Snitzer) [554718]
- [block] Fix incorrect alignment offset reporting and update documentation (Mike Snitzer) [554718]
- [kvm] Fix possible circular locking in kvm_vm_ioctl_assign_device() (Marcelo Tosatti) [554762]
- [kvm] only clear irq_source_id if irqchip is present (Marcelo Tosatti) [554762]
- [kvm] fix lock imbalance in kvm_*_irq_source_id() (Marcelo Tosatti) [554762]
- [kvm] VMX: Report unexpected simultaneous exceptions as internal errors (Marcelo Tosatti) [554762]
- [kvm] Allow internal errors reported to userspace to carry extra data (Marcelo Tosatti) [554762]
- [kvm] x86: disable paravirt mmu reporting (Marcelo Tosatti) [554762]
- [kvm] x86: disallow KVM_{SET, GET}_LAPIC without allocated in-kernel lapic (Marcelo Tosatti) [554762]
- [kvm] x86: disallow multiple KVM_CREATE_IRQCHIP (Marcelo Tosatti) [554762]
- [kvm] VMX: Disable unrestricted guest when EPT disabled (Marcelo Tosatti) [554762]
- [kvm] SVM: remove needless mmap_sem acquision from nested_svm_map (Marcelo Tosatti) [554762]
- [kvm] SVM: Notify nested hypervisor of lost event injections (Marcelo Tosatti) [554762]
- [kvm] SVM: Move INTR vmexit out of atomic code (Marcelo Tosatti) [554762]
- [kvm] remove pre_task_link setting in save_state_to_tss16 (Marcelo Tosatti) [554762]
- [kvm] x86: Extend KVM_SET_VCPU_EVENTS with selective updates (Marcelo Tosatti) [554500]
- [kvm] x86: Add KVM_GET/SET_VCPU_EVENTS (Marcelo Tosatti) [554500]
- [kvm] fix kvmclock-adjust-offset ioctl to match upstream (Marcelo Tosatti) [554524]
- [kvm] SVM: init_vmcb(): remove redundant save->cr0 initialization (Marcelo Tosatti) [554506]
- [kvm] SVM: Reset cr0 properly on vcpu reset (Marcelo Tosatti) [554506]
- [kvm] VMX: Use macros instead of hex value on cr0 initialization (Marcelo Tosatti) [554506]
- [kvm] avoid taking ioapic mutex for non-ioapic EOIs (Marcelo Tosatti) [550809]
- [kvm] Bump maximum vcpu count to 64 (Marcelo Tosatti) [550809]
- [kvm] convert slots_lock to a mutex (Marcelo Tosatti) [550809]
- [kvm] switch vcpu context to use SRCU (Marcelo Tosatti) [550809]
- [kvm] convert io_bus to SRCU (Marcelo Tosatti) [550809]
- [kvm] x86: switch kvm_set_memory_alias to SRCU update (Marcelo Tosatti) [550809]
- [kvm] use SRCU for dirty log (Marcelo Tosatti) [550809]
- [kvm] introduce kvm->srcu and convert kvm_set_memory_region to SRCU update (Marcelo Tosatti) [550809]
- [kvm] use gfn_to_pfn_memslot in kvm_iommu_map_pages (Marcelo Tosatti) [550809]
- [kvm] introduce gfn_to_pfn_memslot (Marcelo Tosatti) [550809]
- [kvm] split kvm_arch_set_memory_region into prepare and commit (Marcelo Tosatti) [550809]
- [kvm] modify alias layout in x86s struct kvm_arch (Marcelo Tosatti) [550809]
- [kvm] modify memslots layout in struct kvm (Marcelo Tosatti) [550809]
- [kvm] rcu: Enable synchronize_sched_expedited() fastpath (Marcelo Tosatti) [550809]
- [kvm] rcu: Add synchronize_srcu_expedited() to the documentation (Marcelo Tosatti) [550809]
- [kvm] rcu: Add synchronize_srcu_expedited() to the rcutorture test suite (Marcelo Tosatti) [550809]
- [kvm] Add synchronize_srcu_expedited() (Marcelo Tosatti) [550809]
- [kvm] Drop kvm->irq_lock lock from irq injection path (Marcelo Tosatti) [550809]
- [kvm] Move IO APIC to its own lock (Marcelo Tosatti) [550809]
- [kvm] Convert irq notifiers lists to RCU locking (Marcelo Tosatti) [550809]
- [kvm] Move irq ack notifier list to arch independent code (Marcelo Tosatti) [550809]
- [kvm] Move irq routing data structure to rcu locking (Marcelo Tosatti) [550809]
- [kvm] Maintain back mapping from irqchip/pin to gsi (Marcelo Tosatti) [550809]
- [kvm] Change irq routing table to use gsi indexed array (Marcelo Tosatti) [550809]
- [kvm] Move irq sharing information to irqchip level (Marcelo Tosatti) [550809]
- [kvm] Call pic_clear_isr() on pic reset to reuse logic there (Marcelo Tosatti) [550809]
- [kvm] Dont pass kvm_run arguments (Marcelo Tosatti) [550809]

* Thu Jan 14 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-6.el6]
- [modsign] Remove Makefile.modpost qualifying message for module sign failure (David Howells) [543529]
- [nfs] fix oops in nfs_rename() (Jeff Layton) [554337]
- [x86] AMD: Fix stale cpuid4_info shared_map data in shared_cpu_map cpumasks (Prarit Bhargava) [546610]
- [s390] kernel: improve code generated by atomic operations (Hendrik Brueckner) [547411]
- [s390x] tape: incomplete device removal (Hendrik Brueckner) [547415]
- [netdrv] be2net: update be2net driver to latest upstream (Ivan Vecera) [515262]
- [x86] mce: fix confusion between bank attributes and mce attributes (hiro muneda) [476606]
- [tpm] autoload tpm_tis driver (John Feeney) [531891]
- [stable] generic_permission: MAY_OPEN is not write access (Serge E. Hallyn) [555084]
- [stable] rt2x00: Disable powersaving for rt61pci and rt2800pci. (Gertjan van Wingerde) [555084]
- [stable] lguest: fix bug in setting guest GDT entry (Rusty Russell) [555084]
- [stable] ext4: Update documentation to correct the inode_readahead_blks option name (Fang Wenqi) [555084]
- [stable] sched: Sched_rt_periodic_timer vs cpu hotplug (Peter Zijlstra) [555084]
- [stable] amd64_edac: fix forcing module load/unload (Borislav Petkov) [555084]
- [stable] amd64_edac: make driver loading more robust (Borislav Petkov) [555084]
- [stable] amd64_edac: fix driver instance freeing (Borislav Petkov) [555084]
- [stable] x86, msr: msrs_alloc/free for CONFIG_SMP=n (Borislav Petkov) [555084]
- [stable] x86, msr: Add support for non-contiguous cpumasks (Borislav Petkov) [555084]
- [stable] amd64_edac: unify MCGCTL ECC switching (Borislav Petkov) [555084]
- [stable] cpumask: use modern cpumask style in drivers/edac/amd64_edac.c (Rusty Russell) [555084]
- [stable] x86, msr: Unify rdmsr_on_cpus/wrmsr_on_cpus (Borislav Petkov) [555084]
- [stable] ext4: fix sleep inside spinlock issue with quota and dealloc (#14739) (Dmitry Monakhov) [555084]
- [stable] ext4: Convert to generic reserved quota's space management. (Dmitry Monakhov) [555084]
- [stable] quota: decouple fs reserved space from quota reservation (Dmitry Monakhov) [555084]
- [stable] Add unlocked version of inode_add_bytes() function (Dmitry Monakhov) [555084]
- [stable] udf: Try harder when looking for VAT inode (Jan Kara) [555084]
- [stable] orinoco: fix GFP_KERNEL in orinoco_set_key with interrupts disabled (Andrey Borzenkov) [555084]
- [stable] drm: disable all the possible outputs/crtcs before entering KMS mode (Zhao Yakui) [555084]
- [stable] drm/radeon/kms: fix crtc vblank update for r600 (Dave Airlie) [555084]
- [stable] sched: Fix balance vs hotplug race (Peter Zijlstra) [555084]
- [stable] Keys: KEYCTL_SESSION_TO_PARENT needs TIF_NOTIFY_RESUME architecture support (Geert Uytterhoeven) [555084]
- [stable] b43: avoid PPC fault during resume (Larry Finger) [555084]
- [stable] hwmon: (sht15) Off-by-one error in array index + incorrect constants (Jonathan Cameron) [555084]
- [stable] netfilter: fix crashes in bridge netfilter caused by fragment jumps (Patrick McHardy) [555084]
- [stable] ipv6: reassembly: use seperate reassembly queues for conntrack and local delivery (Patrick McHardy) [555084]
- [stable] e100: Fix broken cbs accounting due to missing memset. (Roger Oksanen) [555084]
- [stable] memcg: avoid oom-killing innocent task in case of use_hierarchy (Daisuke Nishimura) [555084]
- [stable] x86/ptrace: make genregs[32]_get/set more robust (Linus Torvalds) [555084]
- [stable] V4L/DVB (13596): ov511.c typo: lock => unlock (Dan Carpenter) [555084]
- [stable] kernel/sysctl.c: fix the incomplete part of sysctl_max_map_count-should-be-non-negative.patch (WANG Cong) [555084]
- [stable] 'sysctl_max_map_count' should be non-negative (Amerigo Wang) [555084]
- [stable] NOMMU: Optimise away the {dac_,}mmap_min_addr tests (David Howells) [555084]
- [stable] mac80211: fix race with suspend and dynamic_ps_disable_work (Luis R. Rodriguez) [555084]
- [stable] iwlwifi: fix 40MHz operation setting on cards that do not allow it (Reinette Chatre) [555084]
- [stable] iwlwifi: fix more eeprom endian bugs (Johannes Berg) [555084]
- [stable] iwlwifi: fix EEPROM/OTP reading endian annotations and a bug (Johannes Berg) [555084]
- [stable] iwl3945: fix panic in iwl3945 driver (Zhu Yi) [555084]
- [stable] iwl3945: disable power save (Reinette Chatre) [555084]
- [stable] ath9k_hw: Fix AR_GPIO_INPUT_EN_VAL_BT_PRIORITY_BB and its shift value in 0x4054 (Vasanthakumar Thiagarajan) [555084]
- [stable] ath9k_hw: Fix possible OOB array indexing in gen_timer_index[] on 64-bit (Vasanthakumar Thiagarajan) [555084]
- [stable] ath9k: fix suspend by waking device prior to stop (Sujith) [555084]
- [stable] ath9k: wake hardware during AMPDU TX actions (Luis R. Rodriguez) [555084]
- [stable] ath9k: fix missed error codes in the tx status check (Felix Fietkau) [555084]
- [stable] ath9k: Fix TX queue draining (Sujith) [555084]
- [stable] ath9k: wake hardware for interface IBSS/AP/Mesh removal (Luis R. Rodriguez) [555084]
- [stable] ath5k: fix SWI calibration interrupt storm (Bob Copeland) [555084]
- [stable] cfg80211: fix race between deauth and assoc response (Johannes Berg) [555084]
- [stable] mac80211: Fix IBSS merge (Sujith) [555084]
- [stable] mac80211: fix WMM AP settings application (Johannes Berg) [555084]
- [stable] mac80211: fix propagation of failed hardware reconfigurations (Luis R. Rodriguez) [555084]
- [stable] iwmc3200wifi: fix array out-of-boundary access (Zhu Yi) [555084]
- [stable] Libertas: fix buffer overflow in lbs_get_essid() (Daniel Mack) [555084]
- [stable] KVM: LAPIC: make sure IRR bitmap is scanned after vm load (Marcelo Tosatti) [555084]
- [stable] KVM: MMU: remove prefault from invlpg handler (Marcelo Tosatti) [555084]
- [stable] ioat2,3: put channel hardware in known state at init (Dan Williams) [555084]
- [stable] ioat3: fix p-disabled q-continuation (Dan Williams) [555084]
- [stable] x86/amd-iommu: Fix initialization failure panic (Joerg Roedel) [555084]
- [stable] dma-debug: Fix bug causing build warning (Ingo Molnar) [555084]
- [stable] dma-debug: Do not add notifier when dma debugging is disabled. (Shaun Ruffell) [555084]
- [stable] dma: at_hdmac: correct incompatible type for argument 1 of 'spin_lock_bh' (Nicolas Ferre) [555084]
- [stable] md: Fix unfortunate interaction with evms (NeilBrown) [555084]
- [stable] x86: SGI UV: Fix writes to led registers on remote uv hubs (Mike Travis) [555084]
- [stable] drivers/net/usb: Correct code taking the size of a pointer (Julia Lawall) [555084]
- [stable] USB: fix bugs in usb_(de)authorize_device (Alan Stern) [555084]
- [stable] USB: rename usb_configure_device (Alan Stern) [555084]
- [stable] Bluetooth: Prevent ill-timed autosuspend in USB driver (Oliver Neukum) [555084]
- [stable] USB: musb: gadget_ep0: avoid SetupEnd interrupt (Sergei Shtylyov) [555084]
- [stable] USB: Fix a bug on appledisplay.c regarding signedness (pancho horrillo) [555084]
- [stable] USB: option: support hi speed for modem Haier CE100 (Donny Kurnia) [555084]
- [stable] USB: emi62: fix crash when trying to load EMI 6|2 firmware (Clemens Ladisch) [555084]
- [stable] drm/radeon: fix build on 64-bit with some compilers. (Dave Airlie) [555084]
- [stable] ASoC: Do not write to invalid registers on the wm9712. (Eric Millbrandt) [555084]
- [stable] powerpc: Handle VSX alignment faults correctly in little-endian mode (Neil Campbell) [555084]
- [stable] ACPI: Use the return result of ACPI lid notifier chain correctly (Zhao Yakui) [555084]
- [stable] ACPI: EC: Fix MSI DMI detection (Alexey Starikovskiy) [555084]
- [stable] acerhdf: limit modalias matching to supported (Stefan Bader) [555084]
- [stable] ALSA: hda - Fix missing capsrc_nids for ALC88x (Takashi Iwai) [555084]
- [stable] sound: sgio2audio/pdaudiocf/usb-audio: initialize PCM buffer (Clemens Ladisch) [555084]
- [stable] ASoC: wm8974: fix a wrong bit definition (Guennadi Liakhovetski) [555084]
- [stable] pata_cmd64x: fix overclocking of UDMA0-2 modes (Bartlomiej Zolnierkiewicz) [555084]
- [stable] pata_hpt3x2n: fix clock turnaround (Sergei Shtylyov) [555084]
- [stable] clockevents: Prevent clockevent_devices list corruption on cpu hotplug (Thomas Gleixner) [555084]
- [stable] sched: Select_task_rq_fair() must honour SD_LOAD_BALANCE (Peter Zijlstra) [555084]
- [stable] x86, cpuid: Add "volatile" to asm in native_cpuid() (Suresh Siddha) [555084]
- [stable] sched: Fix task_hot() test order (Peter Zijlstra) [555084]
- [stable] SCSI: fc class: fix fc_transport_init error handling (Mike Christie) [555084]
- [stable] SCSI: st: fix mdata->page_order handling (FUJITA Tomonori) [555084]
- [stable] SCSI: qla2xxx: dpc thread can execute before scsi host has been added (Michael Reed) [555084]
- [stable] SCSI: ipr: fix EEH recovery (Kleber Sacilotto de Souza) [555084]
- [stable] implement early_io{re,un}map for ia64 (Luck, Tony) [555084]
- [stable] perf_event: Fix incorrect range check on cpu number (Paul Mackerras) [555084]
- [stable] netfilter: xtables: document minimal required version (Jan Engelhardt) [555084]
- [stable] intel-iommu: ignore page table validation in pass through mode (Chris Wright) [555084]
- [stable] jffs2: Fix long-standing bug with symlink garbage collection. (David Woodhouse) [555084]
- [stable] ipvs: zero usvc and udest (Simon Horman) [555084]
- [stable] mm: sigbus instead of abusing oom (Hugh Dickins) [555084]
- [stable] drm/i915: Fix LVDS stability issue on Ironlake (Zhenyu Wang) [555084]
- [stable] drm/i915: PineView only has LVDS and CRT ports (Zhenyu Wang) [555084]
- [stable] drm/i915: Avoid NULL dereference with component_only tv_modes (Chris Wilson) [555084]
- [stable] x86: Under BIOS control, restore AP's APIC_LVTTHMR to the BSP value (Yong Wang) [555084]
- [stable] bcm63xx_enet: fix compilation failure after get_stats_count removal (Florian Fainelli) [555084]
- [stable] V4L/DVB (13116): gspca - ov519: Webcam 041e:4067 added. (Rafal Milecki) [555084]
- [stable] ext3: Fix data / filesystem corruption when write fails to copy data (Jan Kara) [555084]
- [stable] net: Fix userspace RTM_NEWLINK notifications. (Eric W. Biederman) [555084]
- [stable] ACPI: Use the ARB_DISABLE for the CPU which model id is less than 0x0f. (Zhao Yakui) [555084]
- [stable] vmalloc: conditionalize build of pcpu_get_vm_areas() (Tejun Heo) [555084]
- [stable] asus-laptop: change light sens default values. (Corentin Chary) [555084]
- [stable] acerhdf: add new BIOS versions (Peter Feuerer) [555084]
- [stable] matroxfb: fix problems with display stability (Alan Cox) [555084]
- [stable] ipw2100: fix rebooting hang with driver loaded (Zhu Yi) [555084]
- [stable] thinkpad-acpi: preserve rfkill state across suspend/resume (Henrique de Moraes Holschuh) [555084]
- [stable] thinkpad-acpi: fix default brightness_mode for R50e/R51 (Henrique de Moraes Holschuh) [555084]
- [stable] memcg: fix memory.memsw.usage_in_bytes for root cgroup (Kirill A. Shutemov) [555084]
- [stable] mac80211: Fix dynamic power save for scanning. (Vivek Natarajan) [555084]
- [stable] ath9k: fix tx status reporting (Felix Fietkau) [555084]
- [stable] tracing: Fix event format export (Johannes Berg) [555084]
- [stable] b43legacy: avoid PPC fault during resume (Larry Finger) [555084]
- [stable] sparc: Set UTS_MACHINE correctly. (David S. Miller) [555084]
- [stable] sparc64: Fix stack debugging IRQ stack regression. (David S. Miller) [555084]
- [stable] sparc64: Fix overly strict range type matching for PCI devices. (David S. Miller) [555084]
- [stable] sparc64: Don't specify IRQF_SHARED for LDC interrupts. (David S. Miller) [555084]
- [stable] b44 WOL setup: one-bit-off stack corruption kernel panic fix (Stanislav Brabec) [555084]
- [stable] ip_fragment: also adjust skb->truesize for packets not owned by a socket (Patrick McHardy) [555084]
- [stable] tcp: Stalling connections: Fix timeout calculation routine (Damian Lukowski) [555084]
- [stable] slc90e66: fix UDMA handling (Bartlomiej Zolnierkiewicz) [555084]
- [stable] xen: try harder to balloon up under memory pressure. (Ian Campbell) [555084]
- [stable] Xen balloon: fix totalram_pages counting. (Gianluca Guida) [555084]
- [stable] xen: explicitly create/destroy stop_machine workqueues outside suspend/resume region. (Ian Campbell) [555084]
- [stable] xen: use iret for return from 64b kernel to 32b usermode (Jeremy Fitzhardinge) [555084]
- [stable] xen: don't leak IRQs over suspend/resume. (Ian Campbell) [555084]
- [stable] xen: improve error handling in do_suspend. (Ian Campbell) [555084]
- [stable] xen: call clock resume notifier on all CPUs (Ian Campbell) [555084]
- [stable] xen: register runstate info for boot CPU early (Jeremy Fitzhardinge) [555084]
- [stable] xen: don't call dpm_resume_noirq() with interrupts disabled. (Jeremy Fitzhardinge) [555084]
- [stable] xen: register runstate on secondary CPUs (Ian Campbell) [555084]
- [stable] xen: register timer interrupt with IRQF_TIMER (Ian Campbell) [555084]
- [stable] xen: correctly restore pfn_to_mfn_list_list after resume (Ian Campbell) [555084]
- [stable] xen: restore runstate_info even if !have_vcpu_info_placement (Jeremy Fitzhardinge) [555084]
- [stable] xen: re-register runstate area earlier on resume. (Ian Campbell) [555084]
- [stable] xen/xenbus: make DEVICE_ATTR()s static (Jeremy Fitzhardinge) [555084]
- [stable] drm/i915: Add the missing clonemask for display port on Ironlake (Zhao Yakui) [555084]
- [stable] drm/i915: Set the error code after failing to insert new offset into mm ht. (Chris Wilson) [555084]
- [stable] drm/ttm: Fix build failure due to missing struct page (Martin Michlmayr) [555084]
- [stable] drm/radeon/kms: rs6xx/rs740: clamp vram to aperture size (Alex Deucher) [555084]
- [stable] drm/radeon/kms: fix vram setup on rs600 (Alex Deucher) [555084]
- [stable] drm/radeon/kms: fix legacy crtc2 dpms (Alex Deucher) [555084]
- [stable] drm/radeon/kms: handle vblanks properly with dpms on (Alex Deucher) [555084]
- [stable] drm/radeon/kms: Add quirk for HIS X1300 board (Alex Deucher) [555084]
- [stable] powerpc: Fix usage of 64-bit instruction in 32-bit altivec code (Benjamin Herrenschmidt) [555084]
- [stable] powerpc/therm_adt746x: Record pwm invert bit at module load time] (Darrick J. Wong) [555084]
- [stable] powerpc/windfarm: Add detection for second cpu pump (Bolko Maass) [555084]
- [stable] mm: hugetlb: fix hugepage memory leak in walk_page_range() (Naoya Horiguchi) [555084]
- [stable] mm: hugetlb: fix hugepage memory leak in mincore() (Naoya Horiguchi) [555084]
- [stable] x86: Fix bogus warning in apic_noop.apic_write() (Thomas Gleixner) [555084]
- [stable] rtl8187: Fix wrong rfkill switch mask for some models (Larry Finger) [555084]
- [stable] wireless: correctly report signal value for IEEE80211_HW_SIGNAL_UNSPEC (John W. Linville) [555084]
- [stable] mac80211: fix scan abort sanity checks (Johannes Berg) [555084]
- [stable] mac80211: Revert 'Use correct sign for mesh active path refresh' (Javier Cardona) [555084]
- [stable] mac80211: Fixed bug in mesh portal paths (Javier Cardona) [555084]
- [stable] mac80211: Fix bug in computing crc over dynamic IEs in beacon (Vasanthakumar Thiagarajan) [555084]
- [stable] Serial: Do not read IIR in serial8250_start_tx when UART_BUG_TXEN (Ian Jackson) [555084]
- [stable] Driver core: fix race in dev_driver_string (Alan Stern) [555084]
- [stable] debugfs: fix create mutex racy fops and private data (Mathieu Desnoyers) [555084]
- [stable] devpts_get_tty() should validate inode (Sukadev Bhattiprolu) [555084]
- [stable] futex: Take mmap_sem for get_user_pages in fault_in_user_writeable (Andi Kleen) [555084]
- [stable] md/bitmap: protect against bitmap removal while being updated. (NeilBrown) [555084]
- [stable] hfs: fix a potential buffer overflow (Amerigo Wang) [555084]
- [stable] pxa/em-x270: fix usb hub power up/reset sequence (Igor Grinberg) [555084]
- [stable] USB: Close usb_find_interface race v3 (Russ Dill) [555084]
- [stable] USB: usb-storage: add BAD_SENSE flag (Alan Stern) [555084]
- [stable] USB: usbtmc: repeat usb_bulk_msg until whole message is transfered (Andre Herms) [555084]
- [stable] USB: option.c: add support for D-Link DWM-162-U5 (Zhang Le) [555084]
- [stable] USB: musb_gadget_ep0: fix unhandled endpoint 0 IRQs, again (Sergei Shtylyov) [555084]
- [stable] USB: xhci: Add correct email and files to MAINTAINERS entry. (Sarah Sharp) [555084]
- [stable] jbd2: don't wipe the journal on a failed journal checksum (Theodore Ts'o) [555084]
- [stable] UBI: flush wl before clearing update marker (Sebastian Andrzej Siewior) [555084]
- [stable] bsdacct: fix uid/gid misreporting (Alexey Dobriyan) [555084]
- [stable] V4L/DVB: Fix test in copy_reg_bits() (Roel Kluin) [555084]
- [stable] pata_hpt{37x|3x2n}: fix timing register masks (take 2) (Sergei Shtylyov) [555084]
- [stable] x86: Fix typo in Intel CPU cache size descriptor (Dave Jones) [555084]
- [stable] x86: Add new Intel CPU cache size descriptors (Dave Jones) [555084]
- [stable] x86: Fix duplicated UV BAU interrupt vector (Cliff Wickman) [555084]
- [stable] x86/mce: Set up timer unconditionally (Jan Beulich) [555084]
- [stable] x86, mce: don't restart timer if disabled (Hidetoshi Seto) [555084]
- [stable] x86: Use -maccumulate-outgoing-args for sane mcount prologues (Thomas Gleixner) [555084]
- [stable] x86: Prevent GCC 4.4.x (pentium-mmx et al) function prologue wreckage (Thomas Gleixner) [555084]
- [stable] KVM: x86: include pvclock MSRs in msrs_to_save (Glauber Costa) [555084]
- [stable] KVM: fix irq_source_id size verification (Marcelo Tosatti) [555084]
- [stable] KVM: s390: Make psw available on all exits, not just a subset (Carsten Otte) [555084]
- [stable] KVM: s390: Fix prefix register checking in arch/s390/kvm/sigp.c (Carsten Otte) [555084]
- [stable] KVM: x86 emulator: limit instructions to 15 bytes (Avi Kivity) [555084]
- [stable] ALSA: hrtimer - Fix lock-up (Takashi Iwai) [555084]
- [stable] hrtimer: Fix /proc/timer_list regression (Feng Tang) [555084]
- [stable] ath5k: enable EEPROM checksum check (Luis R. Rodriguez) [555084]
- [stable] ath5k: allow setting txpower to 0 (Bob Copeland) [555084]
- [stable] ssb: Fix range check in sprom write (Michael Buesch) [555084]
- [stable] x86, apic: Enable lapic nmi watchdog on AMD Family 11h (Mikael Pettersson) [555084]
- [stable] x86: ASUS P4S800 reboot=bios quirk (Leann Ogasawara) [555084]
- [stable] x86: GART: pci-gart_64.c: Use correct length in strncmp (Joe Perches) [555084]
- [stable] x86: Fix iommu=nodac parameter handling (Tejun Heo) [555084]
- [stable] x86, Calgary IOMMU quirk: Find nearest matching Calgary while walking up the PCI tree (Darrick J. Wong) [555084]
- [stable] x86/amd-iommu: un__init iommu_setup_msi (Joerg Roedel) [555084]
- [stable] x86/amd-iommu: attach devices to pre-allocated domains early (Joerg Roedel) [555084]
- [stable] sched: Fix and clean up rate-limit newidle code (Mike Galbraith) [555084]
- [stable] sched: Rate-limit newidle (Mike Galbraith) [555084]
- [stable] sched: Fix affinity logic in select_task_rq_fair() (Mike Galbraith) [555084]
- [stable] sched: Check for an idle shared cache in select_task_rq_fair() (Mike Galbraith) [555084]
- [stable] PM / Runtime: Fix lockdep warning in __pm_runtime_set_status() (Rafael J. Wysocki) [555084]
- [stable] perf_event: Initialize data.period in perf_swevent_hrtimer() (Xiao Guangrong) [555084]
- [stable] perf_event: Fix invalid type in ioctl definition (Arjan van de Ven) [555084]
- [stable] rcu: Remove inline from forward-referenced functions (Paul E. McKenney) [555084]
- [stable] rcu: Fix note_new_gpnum() uses of ->gpnum (Paul E. McKenney) [555084]
- [stable] rcu: Fix synchronization for rcu_process_gp_end() uses of ->completed counter (Paul E. McKenney) [555084]
- [stable] rcu: Prepare for synchronization fixes: clean up for non-NO_HZ handling of ->completed counter (Paul E. McKenney) [555084]
- [stable] firewire: ohci: handle receive packets with a data length of zero (Jay Fenlason) [555084]
- [stable] USB: option: add pid for ZTE (zhao.ming9@zte.com.cn) [555084]
- [stable] USB: usb-storage: fix bug in fill_inquiry (Alan Stern) [555084]
- [stable] ext4: Fix potential fiemap deadlock (mmap_sem vs. i_data_sem) (Theodore Ts'o) [555084]
- [stable] ext4: Wait for proper transaction commit on fsync (Jan Kara) [555084]
- [stable] ext4: fix incorrect block reservation on quota transfer. (Dmitry Monakhov) [555084]
- [stable] ext4: quota macros cleanup (Dmitry Monakhov) [555084]
- [stable] ext4: ext4_get_reserved_space() must return bytes instead of blocks (Dmitry Monakhov) [555084]
- [stable] ext4: remove blocks from inode prealloc list on failure (Curt Wohlgemuth) [555084]
- [stable] ext4: Avoid data / filesystem corruption when write fails to copy data (Jan Kara) [555084]
- [stable] ext4: Return the PTR_ERR of the correct pointer in setup_new_group_blocks() (Roel Kluin) [555084]
- [stable] jbd2: Add ENOMEM checking in and for jbd2_journal_write_metadata_buffer() (Theodore Ts'o) [555084]
- [stable] ext4: move_extent_per_page() cleanup (Akira Fujita) [555084]
- [stable] ext4: initialize moved_len before calling ext4_move_extents() (Kazuya Mio) [555084]
- [stable] ext4: Fix double-free of blocks with EXT4_IOC_MOVE_EXT (Akira Fujita) [555084]
- [stable] ext4: make "norecovery" an alias for "noload" (Eric Sandeen) [555084]
- [stable] ext4: fix error handling in ext4_ind_get_blocks() (Jan Kara) [555084]
- [stable] ext4: avoid issuing unnecessary barriers (Theodore Ts'o) [555084]
- [stable] ext4: fix block validity checks so they work correctly with meta_bg (Theodore Ts'o) [555084]
- [stable] ext4: fix uninit block bitmap initialization when s_meta_first_bg is non-zero (Theodore Ts'o) [555084]
- [stable] ext4: don't update the superblock in ext4_statfs() (Theodore Ts'o) [555084]
- [stable] ext4: journal all modifications in ext4_xattr_set_handle (Eric Sandeen) [555084]
- [stable] ext4: fix i_flags access in ext4_da_writepages_trans_blocks() (Julia Lawall) [555084]
- [stable] ext4: make sure directory and symlink blocks are revoked (Theodore Ts'o) [555084]
- [stable] ext4: plug a buffer_head leak in an error path of ext4_iget() (Theodore Ts'o) [555084]
- [stable] ext4: fix possible recursive locking warning in EXT4_IOC_MOVE_EXT (Akira Fujita) [555084]
- [stable] ext4: fix lock order problem in ext4_move_extents() (Akira Fujita) [555084]
- [stable] ext4: fix the returned block count if EXT4_IOC_MOVE_EXT fails (Akira Fujita) [555084]
- [stable] ext4: avoid divide by zero when trying to mount a corrupted file system (Theodore Ts'o) [555084]
- [stable] ext4: fix potential buffer head leak when add_dirent_to_buf() returns ENOSPC (Theodore Ts'o) [555084]
- [stable] SCSI: megaraid_sas: fix 64 bit sense pointer truncation (Yang, Bo) [555084]
- [stable] SCSI: osd_protocol.h: Add missing #include (Martin Michlmayr) [555084]
- [stable] signal: Fix alternate signal stack check (Sebastian Andrzej Siewior) [555084]

* Sat Jan 09 2010 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-5.el6]
- [scsi] cciss: fix spinlock use (Tomas Henzl) [552910]
- [scsi] cciss,hpsa: reassign controllers (Tomas Henzl) [552192]
- [modsign] Don't attempt to sign a module if there are no key files (David Howells) [543529]
- [x86] Compile mce-inject module (Prarit Bhargava) [553323]
- [nfs] fix insecure export option (Steve Dickson) [437715]
- [nfs] NFS update to 2.6.33 part 3 (Steve Dickson) [437715]
- [nfs] NFS update to 2.6.33 part 2 (Steve Dickson) [437715]
- [nfs] NFS update to 2.6.33 part 1 (Steve Dickson) [437715]
- [s390] cio: deactivated devices can cause use after free panic (Hendrik Brueckner) [548490]
- [s390] cio: memory leaks when checking unusable devices (Hendrik Brueckner) [548490]
- [s390] cio: DASD steal lock task hangs (Hendrik Brueckner) [548490]
- [s390] cio: DASD cannot be set online (Hendrik Brueckner) [548490]
- [s390] cio: erratic DASD I/O behavior (Hendrik Brueckner) [548490]
- [s390] cio: not operational devices cannot be deactivated (Hendrik Brueckner) [548490]
- [s390] cio: initialization of I/O devices fails (Hendrik Brueckner) [548490]
- [s390] cio: kernel panic after unexpected interrupt (Hendrik Brueckner) [548490]
- [s390] cio: incorrect device state after device recognition and recovery (Hendrik Brueckner) [548490]
- [s390] cio: setting a device online or offline fails for unknown reasons (Hendrik Brueckner) [548490]
- [s390] cio: device recovery fails after concurrent hardware changes (Hendrik Brueckner) [548490]
- [s390] cio: device recovery stalls after multiple hardware events (Hendrik Brueckner) [548490]
- [s390] cio: double free under memory pressure (Hendrik Brueckner) [548490]
- [sunrpc] Don't display zero scope IDs (Jeff Layton) [463530]
- [sunrpc] Deprecate support for site-local addresses (Jeff Layton) [463530]
- [input] dell-laptop: Update rfkill state on switch change (Matthew Garrett) [547892]
- [input] Add support for adding i8042 filters (Matthew Garrett) [547892]
- [vfs] force reval of target when following LAST_BIND symlinks (Jeff Layton) [548153]
- [scsi] scsi_dh_rdac: add two IBM devices to rdac_dev_list (Rob Evers) [528576]
- [fs] ext4: flush delalloc blocks when space is low (Eric Sandeen) [526758]
- [fs] fs-writeback: Add helper function to start writeback if idle (Eric Sandeen) [526758]
- [fat] make discard a mount option (Jeff Moyer) [552355]
- [ext4] make trim/discard optional (and off by default) (Jeff Moyer) [552355]
- [fusion] bump version to 3.04.13 (Tomas Henzl) [548408]
- [fusion] fix for incorrect data underrun (Tomas Henzl) [548408]
- [fusion] remove unnecessary printk (Tomas Henzl) [548408]
- [cifs] NULL out tcon, pSesInfo, and srvTcp pointers when chasing DFS referrals (Jeff Layton) [545984]
- [fs] ext4: wait for log to commit when unmounting (Josef Bacik) [524267]
- [mm] hwpoison: backport the latest patches from linux-2.6.33 (Dean Nelson) [547705]
- [netdrv] bnx2i: update to 2.1.0 (Stanislaw Gruszka) [463268]
- [netdrv] cnic: fixes for RHEL6 (Stanislaw Gruszka) [463268]
- [gfs2] Fix potential race in glock code (Steven Whitehouse) [546279]
- [scsi] make driver PCI legacy I/O port free (Tomas Henzl) [549118]
- [scsi] eliminate double free (Tomas Henzl) [549351]
- [dlm] always use GFP_NOFS (David Teigland) [545904]
- [block] Fix topology stacking for data and discard alignment (Mike Snitzer) [549766]
- [scsi] scsi_dh: Make alua hardware handler s activate async (Rob Evers) [537257]
- [scsi] scsi_dh: Make hp hardware handler s activate async (Rob Evers) [537257]
- [scsi] scsi_dh: Make rdac hardware handler s activate async (Rob Evers) [537257]
- [scsi] scsi_dh: Change the scsidh_activate interface to be asynchronous (Rob Evers) [537257]
- [netdrv] update tg3 to version 3.105 (John Feeney) [465194]
- [netdrv] bnx2x: update to 1.52.1-5 (Stanislaw Gruszka) [464427]
- [netdrv] ixgbe: add support for 82599-KR and update to latest upstream (Andy Gospodarek) [462781]
- [block] cfq-iosched: Remove prio_change logic for workload selection (Jeff Moyer) [548796]
- [block] cfq-iosched: Get rid of nr_groups (Jeff Moyer) [548796]
- [block] cfq-iosched: Remove the check for same cfq group from allow_merge (Jeff Moyer) [548796]
- [block] cfq: set workload as expired if it doesn't have any slice left (Jeff Moyer) [548796]
- [block] Fix a CFQ crash in "for-2.6.33" branch of block tree (Jeff Moyer) [548796]
- [block] cfq: Remove wait_request flag when idle time is being deleted (Jeff Moyer) [548796]
- [block] cfq-iosched: commenting non-obvious initialization (Jeff Moyer) [548796]
- [block] cfq-iosched: Take care of corner cases of group losing share due to deletion (Jeff Moyer) [548796]
- [block] cfq-iosched: Get rid of cfqq wait_busy_done flag (Jeff Moyer) [548796]
- [block] cfq: Optimization for close cooperating queue searching (Jeff Moyer) [548796]
- [block] cfq-iosched: reduce write depth only if sync was delayed (Jeff Moyer) [548796]
- [x86] ucode-amd: Load ucode-patches once and not separately of each CPU (George Beshers) [548840]
- [x86] Remove enabling x2apic message for every CPU (George Beshers) [548840]
- [x86] Limit number of per cpu TSC sync messages (George Beshers) [548840]
- [sched] Limit the number of scheduler debug messages (George Beshers) [548840]
- [init] Limit the number of per cpu calibration bootup messages (George Beshers) [548840]
- [x86] Limit the number of processor bootup messages (George Beshers) [548840]
- [x86] cpu: mv display_cacheinfo -> cpu_detect_cache_sizes (George Beshers) [548840]
- [x86] Remove CPU cache size output for non-Intel too (George Beshers) [548840]
- [x86] Remove the CPU cache size printk's (George Beshers) [548840]

* Wed Dec 23 2009 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-4.el6]
- [kvm] VMX: Use shared msr infrastructure (Avi Kivity) [547777]
- [kvm] x86 shared msr infrastructure (Avi Kivity) [547777]
- [kvm] VMX: Move MSR_KERNEL_GS_BASE out of the vmx autoload msr area (Avi Kivity) [547777]
- [kvm] core, x86: Add user return notifiers (Avi Kivity) [547777]
- [quota] ext4: Support for 64-bit quota format (Jerome Marchand) [546311]
- [quota] ext3: Support for vfsv1 quota format (Jerome Marchand) [546311]
- [quota] Implement quota format with 64-bit space and inode limits (Jerome Marchand) [546311]
- [quota] Move definition of QFMT_OCFS2 to linux/quota.h (Jerome Marchand) [546311]
- [scsi] cciss: remove pci-ids (Tomas Henzl) [464649]
- [scsi] hpsa: new driver (Tomas Henzl) [464649]
- [mm] Add file page writeback mm tracepoints. (Larry Woodman) [523093]
- [mm] Add page reclaim mm tracepoints. (Larry Woodman) [523093]
- [mm] Add file page mm tracepoints. (Larry Woodman) [523093]
- [mm] Add anonynmous page mm tracepoints. (Larry Woodman) [523093]
- [mm] Add mm tracepoint definitions to kmem.h (Larry Woodman) [523093]
- [ksm] fix ksm.h breakage of nommu build (Izik Eidus) [548586]
- [ksm] remove unswappable max_kernel_pages (Izik Eidus) [548586]
- [ksm] memory hotremove migration only (Izik Eidus) [548586]
- [ksm] rmap_walk to remove_migation_ptes (Izik Eidus) [548586]
- [ksm] mem cgroup charge swapin copy (Izik Eidus) [548586]
- [ksm] share anon page without allocating (Izik Eidus) [548586]
- [ksm] take keyhole reference to page (Izik Eidus) [548586]
- [ksm] hold anon_vma in rmap_item (Izik Eidus) [548586]
- [ksm] let shared pages be swappable (Izik Eidus) [548586]
- [ksm] fix mlockfreed to munlocked (Izik Eidus) [548586]
- [ksm] stable_node point to page and back (Izik Eidus) [548586]
- [ksm] separate stable_node (Izik Eidus) [548586]
- [ksm] singly-linked rmap_list (Izik Eidus) [548586]
- [ksm] cleanup some function arguments (Izik Eidus) [548586]
- [ksm] remove redundancies when merging page (Izik Eidus) [548586]
- [ksm] three remove_rmap_item_from_tree cleanups (Izik Eidus) [548586]
- [mm] stop ptlock enlarging struct page (Izik Eidus) [548586]
- [mm] vmscan: do not evict inactive pages when skipping an active list scan (Rik van Riel) [548457]
- [mm] vmscan: make consistent of reclaim bale out between do_try_to_free_page and shrink_zone (Rik van Riel) [548457]
- [mm] vmscan: kill sc.swap_cluster_max (Rik van Riel) [548457]
- [mm] vmscan: zone_reclaim() dont use insane swap_cluster_max (Rik van Riel) [548457]
- [mm] vmscan: kill hibernation specific reclaim logic and unify it (Rik van Riel) [548457]
- [mm] vmscan: separate sc.swap_cluster_max and sc.nr_max_reclaim (Rik van Riel) [548457]
- [mm] vmscan: stop kswapd waiting on congestion when the min watermark is not being met (Rik van Riel) [548457]
- [mm] vmscan: have kswapd sleep for a short interval and double check it should be asleep (Rik van Riel) [548457]
- [mm] pass address down to rmap ones (Rik van Riel) [548457]
- [mm] CONFIG_MMU for PG_mlocked (Rik van Riel) [548457]
- [mm] mlocking in try_to_unmap_one (Rik van Riel) [548457]
- [mm] define PAGE_MAPPING_FLAGS (Rik van Riel) [548457]
- [mm] swap_info: note SWAP_MAP_SHMEM (Rik van Riel) [548457]
- [mm] swap_info: swap count continuations (Rik van Riel) [548457]
- [mm] swap_info: swap_map of chars not shorts (Rik van Riel) [548457]
- [mm] swap_info: SWAP_HAS_CACHE cleanups (Rik van Riel) [548457]
- [mm] swap_info: miscellaneous minor cleanups (Rik van Riel) [548457]
- [mm] swap_info: include first_swap_extent (Rik van Riel) [548457]
- [mm] swap_info: change to array of pointers (Rik van Riel) [548457]
- [mm] swap_info: private to swapfile.c (Rik van Riel) [548457]
- [mm] move inc_zone_page_state(NR_ISOLATED) to just isolated place (Rik van Riel) [548457]
- [xen] support MAXSMP (Andrew Jones) [547129]
- [xen] wait up to 5 minutes for device connetion and fix fallout (Paolo Bonzini) [523630]
- [uv] x86 SGI: Map low MMR ranges (George Beshers) [548181]
- [uv] gru: function to generate chipset IPI values (George Beshers) [548181]
- [uv] x86 RTC: Clean up error handling (George Beshers) [548181]
- [uv] x86: RTC: Add clocksource only boot option (George Beshers) [548181]
- [uv] x86: RTC: Fix early expiry handling (George Beshers) [548181]
- [uv] x86: introduce uv_gpa_is_mmr (George Beshers) [548181]
- [uv] x86: function to translate from gpa -> socket_paddr (George Beshers) [548181]
- [uv] x86: SGI UV: Fix BAU initialization (George Beshers) [548181]
- [s390] zfcp: Block SCSI EH thread for rport state BLOCKED (Hendrik Brueckner) [547413]
- [scsi] scsi_transport_fc: Introduce helper function for blocking scsi_eh (Hendrik Brueckner) [547413]
- [s390] zfcp: improve FSF error reporting (Hendrik Brueckner) [547386]
- [s390] zfcp: fix ELS ADISC handling to prevent QDIO errors (Hendrik Brueckner) [547385]
- [s390] zfcp: Assign scheduled work to driver queue (Hendrik Brueckner) [547377]
- [s390] zfcp: Don't fail SCSI commands when transitioning to blocked fc_rport (Hendrik Brueckner) [547379]
- [s390] ctcm: suspend has to wait for outstanding I/O (Hendrik Brueckner) [546633]
- [s390] cmm: free pages on hibernate (Hendrik Brueckner) [546407]
- [s390] iucv: add work_queue cleanup for suspend (Hendrik Brueckner) [546319]
- [s390] dasd: let device initialization wait for LCU setup (Hendrik Brueckner) [547735]
- [s390] dasd: remove strings from s390dbf (Hendrik Brueckner) [547735]
- [s390] dasd: enable prefix independent of pav support (Hendrik Brueckner) [547735]
- [sound] ALSA HDA driver update 2009-12-15 (Jaroslav Kysela) [525391]
- [utrace] utrace core (Roland McGrath) [549491]
- [utrace] implement utrace-ptrace (Roland McGrath) [549491]
- [ptrace] reorder the code in kernel/ptrace.c (Roland McGrath) [549491]
- [ptrace] export __ptrace_detach() and do_notify_parent_cldstop() (Roland McGrath) [549491]
- [ptrace_signal] check PT_PTRACED before reporting a signal (Roland McGrath) [549491]
- [tracehooks] check PT_PTRACED before reporting the single-step (Roland McGrath) [549491]
- [tracehooks] kill some PT_PTRACED checks (Roland McGrath) [549491]
- [signals] check ->group_stop_count after tracehook_get_signal() (Roland McGrath) [549491]
- [ptrace] x86: change syscall_trace_leave() to rely on tracehook when stepping (Roland McGrath) [549491]
- [ptrace] x86: implement user_single_step_siginfo() (Roland McGrath) [549491]
- [ptrace] change tracehook_report_syscall_exit() to handle stepping (Roland McGrath) [549491]
- [ptrace] powerpc: implement user_single_step_siginfo() (Roland McGrath) [549491]
- [ptrace] introduce user_single_step_siginfo() helper (Roland McGrath) [549491]
- [ptrace] copy_process() should disable stepping (Roland McGrath) [549491]
- [ptrace] cleanup ptrace_init_task()->ptrace_link() path (Roland McGrath) [549491]

* Thu Dec 17 2009 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-3.el6]
- [modsign] Don't check e_entry in ELF header (David Howells) [548027]
- [pci] pciehp: Provide an option to disable native PCIe hotplug (Matthew Garrett) [517050]
- [s390] OSA QDIO data connection isolation (Hendrik Brueckner) [537496]
- [s390] zcrypt: adjust speed rating of cex3 adapters (Hendrik Brueckner) [537495]
- [s390] zcrypt: adjust speed rating between cex2 and pcixcc (Hendrik Brueckner) [537495]
- [s390] zcrypt: use definitions for cex3 (Hendrik Brueckner) [537495]
- [s390] zcrypt: add support for cex3 device types (Hendrik Brueckner) [537495]
- [s390] zcrypt: special command support for cex3 exploitation (Hendrik Brueckner) [537495]
- [s390] zcrypt: initialize ap_messages for cex3 exploitation (Hendrik Brueckner) [537495]
- [s390] kernel: performance counter fix and page fault optimization (Hendrik Brueckner) [546396]
- [s390] kernel: fix dump indicator (Hendrik Brueckner) [546285]
- [s390] dasd: support DIAG access for read-only devices (Hendrik Brueckner) [546309]
- [s390] zcrypt: Do not simultaneously schedule hrtimer (Hendrik Brueckner) [546291]
- [s390] kernel: clear high-order bits after switching to 64-bit mode (Hendrik Brueckner) [546314]
- [virt] vhost: add missing architectures (Michael S. Tsirkin) [540389]
- [virt] vhost_net: a kernel-level virtio server (Michael S. Tsirkin) [540389]
- [virt] mm: export use_mm/unuse_mm to modules (Michael S. Tsirkin) [540389]
- [virt] tun: export underlying socket (Michael S. Tsirkin) [540389]
- [dm] snapshot-merge support from 2.6.33 (Mike Snitzer) [547563]
- [dm] snapshot changes from 2.6.33 (Mike Snitzer) [547563]
- [dm] crypt changes from 2.6.33 (Mike Snitzer) [547563]
- [dm] raid1 changes from 2.6.33 (Mike Snitzer) [547563]
- [dm] core and mpath changes from 2.6.33 (Mike Snitzer) [547563]
- [scsi] fix dma handling when using virtual hosts (Mike Christie) [525241]
- [nfs] convert proto= option to use netids rather than a protoname (Jeff Layton) [545973]

* Fri Dec 11 2009 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-2.el6]
- [block] config: enable CONFIG_BLK_DEV_INTEGRITY (Jeff Moyer) [490732]
- [block] config: enable CONFIG_BLK_CGROUP (Jeff Moyer) [425895]
- [libata] Clarify ata_set_lba_range_entries function (Jeff Moyer) [528046]
- [libata] Report zeroed read after Trim and max discard size (Jeff Moyer) [528046]
- [scsi] Correctly handle thin provisioning write error (Jeff Moyer) [528046]
- [scsi] sd: WRITE SAME(16) / UNMAP support (Jeff Moyer) [528046]
- [scsi] scsi_debug: Thin provisioning support (Jeff Moyer) [528046]
- [scsi] Add missing command definitions (Jeff Moyer) [528046]
- [block] Add support for the ATA TRIM command in libata. (Jeff Moyer) [528046]
- [block] dio: fix performance regression (Jeff Moyer) [545507]
- [block] cfq-iosched: Do not access cfqq after freeing it (Jeff Moyer) [425895]
- [block] include linux/err.h to use ERR_PTR (Jeff Moyer) [425895]
- [block] cfq-iosched: use call_rcu() instead of doing grace period stall on queue exit (Jeff Moyer) [425895]
- [block] blkio: Allow CFQ group IO scheduling even when CFQ is a module (Jeff Moyer) [425895]
- [block] blkio: Implement dynamic io controlling policy registration (Jeff Moyer) [425895]
- [block] blkio: Export some symbols from blkio as its user CFQ can be a module (Jeff Moyer) [425895]
- [block] cfq-iosched: make nonrot check logic consistent (Jeff Moyer) [545225]
- [block] io controller: quick fix for blk-cgroup and modular CFQ (Jeff Moyer) [425895]
- [block] cfq-iosched: move IO controller declerations to a header file (Jeff Moyer) [425895]
- [block] cfq-iosched: fix compile problem with !CONFIG_CGROUP (Jeff Moyer) [425895]
- [block] blkio: Documentation (Jeff Moyer) [425895]
- [block] blkio: Wait on sync-noidle queue even if rq_noidle = 1 (Jeff Moyer) [425895]
- [block] blkio: Implement group_isolation tunable (Jeff Moyer) [425895]
- [block] blkio: Determine async workload length based on total number of queues (Jeff Moyer) [425895]
- [block] blkio: Wait for cfq queue to get backlogged if group is empty (Jeff Moyer) [425895]
- [block] blkio: Propagate cgroup weight updation to cfq groups (Jeff Moyer) [425895]
- [block] blkio: Drop the reference to queue once the task changes cgroup (Jeff Moyer) [425895]
- [block] blkio: Provide some isolation between groups (Jeff Moyer) [425895]
- [block] blkio: Export disk time and sectors used by a group to user space (Jeff Moyer) [425895]
- [block] blkio: Some debugging aids for CFQ (Jeff Moyer) [425895]
- [block] blkio: Take care of cgroup deletion and cfq group reference counting (Jeff Moyer) [425895]
- [block] blkio: Dynamic cfq group creation based on cgroup tasks belongs to (Jeff Moyer) [425895]
- [block] blkio: Group time used accounting and workload context save restore (Jeff Moyer) [425895]
- [block] blkio: Implement per cfq group latency target and busy queue avg (Jeff Moyer) [425895]
- [block] blkio: Introduce per cfq group weights and vdisktime calculations (Jeff Moyer) [425895]
- [block] blkio: Introduce blkio controller cgroup interface (Jeff Moyer) [425895]
- [block] blkio: Introduce the root service tree for cfq groups (Jeff Moyer) [425895]
- [block] blkio: Keep queue on service tree until we expire it (Jeff Moyer) [425895]
- [block] blkio: Implement macro to traverse each service tree in group (Jeff Moyer) [425895]
- [block] blkio: Introduce the notion of cfq groups (Jeff Moyer) [425895]
- [block] blkio: Set must_dispatch only if we decided to not dispatch the request (Jeff Moyer) [425895]
- [block] cfq-iosched: no dispatch limit for single queue (Jeff Moyer) [425895]
- [block] Allow devices to indicate whether discarded blocks are zeroed (Jeff Moyer) [545203]
- [block] Revert "cfq: Make use of service count to estimate the rb_key offset" (Jeff Moyer) [425895]
- [block] cfq-iosched: fix corner cases in idling logic (Jeff Moyer) [425895]
- [block] cfq-iosched: idling on deep seeky sync queues (Jeff Moyer) [425895]
- [block] cfq-iosched: fix no-idle preemption logic (Jeff Moyer) [425895]
- [block] cfq-iosched: fix ncq detection code (Jeff Moyer) [425895]
- [block] cfq-iosched: cleanup unreachable code (Jeff Moyer) [425895]
- [block] cfq: Make use of service count to estimate the rb_key offset (Jeff Moyer) [425895]
- [block] partitions: read whole sector with EFI GPT header (Jeff Moyer) [463632]
- [block] partitions: use sector size for EFI GPT (Jeff Moyer) [463632]
- [block] Expose discard granularity (Jeff Moyer) [545203]
- [block] cfq-iosched: fix next_rq computation (Jeff Moyer) [425895]
- [block] cfq-iosched: simplify prio-unboost code (Jeff Moyer) [425895]
- [block] blkdev: flush disk cache on ->fsync (Jeff Moyer) [545199]
- [block] cfq-iosched: fix style issue in cfq_get_avg_queues() (Jeff Moyer) [425895]
- [block] cfq-iosched: fairness for sync no-idle queues (Jeff Moyer) [425895]
- [block] cfq-iosched: enable idling for last queue on priority class (Jeff Moyer) [425895]
- [block] cfq-iosched: reimplement priorities using different service trees (Jeff Moyer) [425895]
- [block] cfq-iosched: preparation to handle multiple service trees (Jeff Moyer) [425895]
- [block] cfq-iosched: adapt slice to number of processes doing I/O (Jeff Moyer) [425895]
- [block] cfq-iosched: improve hw_tag detection (Jeff Moyer) [425895]
- [block] cfq: break apart merged cfqqs if they stop cooperating (Jeff Moyer) [533932]
- [block] cfq: change the meaning of the cfqq_coop flag (Jeff Moyer) [533932]
- [block] cfq: merge cooperating cfq_queues (Jeff Moyer) [533932]
- [block] cfq: calculate the seek_mean per cfq_queue not per cfq_io_context (Jeff Moyer) [533932]
- [block] CFQ is more than a desktop scheduler (Jeff Moyer) [533932]
- [block] revert: cfq-iosched: limit coop preemption (Jeff Moyer) [533932]
- perf: Don't free perf_mmap_data until work has been done (Aristeu Rozanski) [547432]
- ext4: Fix insuficient checks in EXT4_IOC_MOVE_EXT (Aristeu Rozanski) [547432]
- agp: clear GTT on intel (Aristeu Rozanski) [547432]
- drm/i915: Fix sync to vblank when VGA output is turned off (Aristeu Rozanski) [547432]
- drm: nouveau fixes (Aristeu Rozanski) [547432]
- drm: radeon dp support (Aristeu Rozanski) [547432]
- drm: radeon fixes (Aristeu Rozanski) [547432]
- KVM: allow userspace to adjust kvmclock offset (Aristeu Rozanski) [547432]
- ath9k backports (Aristeu Rozanski) [547432]
- intel-iommu backport (Aristeu Rozanski) [547432]
- updating patch linux-2.6-nfsd4-proots.patch (2.6.32-8.fc13 reference) (Aristeu Rozanski) [547432]
- updating linux-2.6-execshield.patch (2.6.32-8.fc13 reference) (Aristeu Rozanski) [547432]

* Tue Dec 08 2009 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-1.el6]
- [rebase] Rebased to 2.6.32

* Mon Dec 07 2009 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-0.54.el6]
- [edac] amd64_edac: disabling temporarily (Aristeu Rozanski)
- [x86] Enable CONFIG_SPARSE_IRQ (Prarit Bhargava) [543174]
- [x86] panic if AMD cpu_khz is wrong (Prarit Bhargava) [523468]
- [infiniband] Rewrite SG handling for RDMA logic (Mike Christie) [540269]

* Wed Nov 25 2009 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-0.53.el6]
- [net] Add acession counts to all datagram protocols (Neil Horman) [445366]
- [modsign] Enable module signing in the RHEL RPM (David Howells) [517341]
- [modsign] Don't include .note.gnu.build-id in the digest (David Howells) [517341]
- [modsign] Apply signature checking to modules on module load (David Howells) [517341]
- [modsign] Module signature checker and key manager (David Howells) [517341]
- [modsign] Module ELF verifier (David Howells) [517341]
- [modsign] Add indications of module ELF types (David Howells) [517341]
- [modsign] Multiprecision maths library (David Howells) [517341]
- [procfs] add ability to modify proc file limits from outside a processes own context (Neil Horman) [461946]
- [s390x] fix build failure with CONFIG_FTRACE_SYSCALLS (Aristeu Rozanski) [538978]

* Wed Nov 25 2009 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-0.52.el6]
- [x86] AMD Northbridge: Verify NB's node is online (Prarit Bhargava) [536769]
- [scsi] devinfo update for Hitachi entries (Takahiro Yasui) [526763]
- [net] export device speed and duplex via sysfs (Andy Gospodarek) [453432]
- [ppc64] Fix kcrctab_ sections to undo undesireable relocations that break kdump (Neil Horman) [509012]
- [mm] Limit 32-bit x86 systems to 16GB and prevent panic on boot when system has more than ~30GB (Larry Woodman) [532039]

* Mon Nov 23 2009 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-0.51.el6]
- [kernel] Set panic_on_oops to 1 (Prarit Bhargava) [529963]
- [kdump] kexec: allow to shrink reserved memory (Amerigo Wang) [523091]
- [kdump] doc: update the kdump document (Amerigo Wang) [523091]
- [kdump] powerpc: implement crashkernel=auto (Amerigo Wang) [523091]
- [kdump] powerpc: add CONFIG_KEXEC_AUTO_RESERVE (Amerigo Wang) [523091]
- [kdump] ia64: implement crashkernel=auto (Amerigo Wang) [523091]
- [kdump] ia64: add CONFIG_KEXEC_AUTO_RESERVE (Amerigo Wang) [523091]
- [kdump] x86: implement crashkernel=auto (Amerigo Wang) [523091]
- [kdump] x86: add CONFIG_KEXEC_AUTO_RESERVE (Amerigo Wang) [523091]
- [block] aio: implement request batching (Jeff Moyer) [533931]
- [block] get rid of the WRITE_ODIRECT flag (Jeff Moyer) [533931]

* Sat Nov 21 2009 Aristeu Rozanski <arozansk@redhat.com> [2.6.32-0.50.el6]
- [crypto] padlock-aes: Use the correct mask when checking whether copying is required (Chuck Ebbert)
- [rfkill] add support to a key to control all radios (Aristeu Rozanski)
- [acpi] be less verbose about old BIOSes (Aristeu Rozanski)
- [drm] intel big hammer (Aristeu Rozanski)
- [e1000] add quirk for ich9 (Aristeu Rozanski)
- [pci] cacheline sizing (Dave Jones)
- [crash] add crash driver (Dave Anderson)
- [fb] disable fbcon logo with parameter (Aristeu Rozanski)
- [pci] silence some PCI resource allocation errors (Aristeu Rozanski)
- [serio] disable error messages when i8042 isn't found (Peter Jones)
- [serial] Enable higher baud rates for 16C95x (Aristeu Rozanski)
- [input] remove pcspkr modalias (Aristeu Rozanski)
- [floppy] remove the floppy pnp modalias (Aristeu Rozanski)
- [input] remove unwanted messages on spurious events (Aristeu Rozanski)
- [sound] hda intel prealloc 4mb dmabuffer (Aristeu Rozanski)
- [sound] disables hda beep by default (Aristeu Rozanski)
- [pci] sets PCIE ASPM default policy to POWERSAVE (Aristeu Rozanski)
- [pci] add config option to control the default state of PCI MSI interrupts (Aristeu Rozanski)
- [debug] always inline kzalloc (Aristeu Rozanski)
- [debug] add would_have_oomkilled procfs ctl (Aristeu Rozanski)
- [debug] add calls to print_tainted() on spinlock functions (Aristeu Rozanski)
- [debug] display tainted information on other places (Aristeu Rozanski)
- [x86] add option to control the NMI watchdog timeout (Aristeu Rozanski)
- [debug] print common struct sizes at boot time (Aristeu Rozanski)
- [acpi] Disable firmware video brightness change by default (Matthew Garrett)
- [acpi] Disable brightness switch by default (Aristeu Rozanski)
- [usb] enable autosuspend on UVC by default (Matthew Garrett)
- [usb] enable autosuspend by default on qcserial (Matthew Garrett)
- [usb] Allow drivers to enable USB autosuspend on a per-device basis (Matthew Garrett)
- [nfs] make nfs4 callback hidden (Steve Dickson)
- [nfsd4] proots (Aristeu Rozanski)
- [execshield] introduce execshield (Aristeu Rozanski)
- [powerpc] add modalias_show operation (Aristeu Rozanski)
- [hwmon] add VIA hwmon temperature sensor support (Aristeu Rozanski)
- [utrace] introduce utrace implementation (Aristeu Rozanski)
- [build] introduce AFTER_LINK variable (Aristeu Rozanski)


###
# The following Emacs magic makes C-c C-e use UTC dates.
# Local Variables:
# rpm-change-log-uses-utc: t
# End:
###
