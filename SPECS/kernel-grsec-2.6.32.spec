# Define the version of the Linux Kernel Archive tarball.
%define LKAver 2.6.32.46

# Define the buildid, if required.
%define buildid .grsec

# The following build options are enabled by default.
# Use either --without <option> on your rpmbuild command line
# or force the values to 0, here, to disable them.

# standard kernel
%define with_std %{?_without_std:0} %{?!_without_std:1}
# kernel-PAE
%define with_pae %{?_without_pae:0} %{?!_without_pae:1}
# kernel-doc
%define with_doc %{?_without_doc:0} %{?!_without_doc:1}
# kernel-headers
%define with_hdr %{?_without_hdr:0} %{?!_without_hdr:1}

# Build only the kernel-doc package.
%ifarch noarch
%define with_std 0
%define with_pae 0
%define with_hdr 0
%endif

# Build only the 32-bit kernel-headers package.
%ifarch i386
%define with_std 0
%define with_pae 0
%define with_doc 0
%endif

# Build just the 32-bit kernel & kernel-PAE packages.
%ifarch i686
%define with_doc 0
%define with_hdr 0
%endif

# Build just the 64-bit kernel & kernel-headers packages.
%ifarch x86_64
%define with_pae 0
%define with_doc 0
%endif

# Define the correct buildarch.
%define buildarch x86_64
%ifarch i386 i686
%define buildarch i386
%endif

# Packages that need to be installed before the kernel because the %post scripts make use of them.
%define kernel_prereq fileutils, module-init-tools, initscripts >= 8.11.1-1, mkinitrd >= 4.2.21-1

# Determine the extraversion number.
%define everno %(echo %{LKAver} | %{__awk} -F\. '{ print $4 }')
%if "%{everno}" == ""
%define everno 0
%endif

Name: kernel
Summary: The Linux kernel. (The core of any Linux-based operating system.)
Group: System Environment/Kernel
License: GPLv2
URL: http://www.kernel.org/
Version: %(echo %{LKAver} | cut -c1-6)
Release: %{everno}%{?buildid}%{?dist}
ExclusiveArch: noarch i386 i686 x86_64
ExclusiveOS: Linux
Provides: kernel = %{version}
Provides: kernel-%{_target_cpu} = %{version}-%{release}
Prereq: %{kernel_prereq}
# We can't let RPM do the dependencies automatically because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function.
AutoReq: no
AutoProv: yes

# List the packages used during the kernel build.
BuildPreReq: module-init-tools, patch >= 2.5.4, bash >= 2.03, sh-utils, tar
BuildPreReq: bzip2, findutils, gzip, m4, perl, make >= 3.78, diffutils
BuildRequires: gcc >= 3.4.2, binutils >= 2.12, redhat-rpm-config, unifdef
BuildConflicts: rhbuildsys(DiskFree) < 500Mb

# Sources.
Source0: ftp://ftp.kernel.org/pub/linux/kernel/v2.6/linux-%{LKAver}.tar.bz2
Source1: config-%{version}-i686
Source2: config-%{version}-i686-PAE
Source3: config-%{version}-x86_64

# Grsecurity patch.
Patch1: grsecurity-2.2.2-2.6.32.46-201109150655.patch

%define KVERREL %{PACKAGE_VERSION}-%{PACKAGE_RELEASE}

BuildRoot: %{_tmppath}/%{name}-%{KVERREL}-root-%(%{__id_u} -n)

# Disable the building of the debug package.
%define	debug_package %{nil}

%description
This package provides the Linux kernel (vmlinuz), the core of any
Linux-based operating system. The kernel handles the basic functions
of the OS: memory allocation, process allocation, device I/O, etc.

%package devel
Summary: Development package for building kernel modules to match the kernel.
Group: System Environment/Kernel
Provides: kernel-devel = %{version}
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}
Prereq: /usr/bin/find
AutoReqProv: no

%description devel
This package provides the kernel header files and makefiles
sufficient to build modules against the kernel package.

%package PAE
Summary: The Linux kernel for PAE capable processors.
Group: System Environment/Kernel
Provides: kernel = %{version}
Provides: kernel-%{_target_cpu} = %{version}-%{release}PAE
Provides: kernel-PAE = %{version}
Provides: kernel-PAE-%{_target_cpu} = %{version}-%{release}PAE
Prereq: %{kernel_prereq}
# We can't let RPM do the dependencies automatically because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function.
AutoReq: no
AutoProv: yes

%description PAE
This package provides a version of the Linux kernel with support for up to 16GB of memory.
It requires processors with Physical Address Extension (PAE) ability.
The non-PAE kernel can only address up to 4GB of memory.

%package PAE-devel
Summary: Development package for building kernel modules to match the PAE kernel.
Group: System Environment/Kernel
Provides: kernel-PAE-devel = %{version}
Provides: kernel-PAE-devel-%{_target_cpu} = %{version}-%{release}PAE
Prereq: /usr/bin/find
AutoReqProv: no

%description PAE-devel
This package provides the kernel header files and makefiles
sufficient to build modules against the PAE kernel package.

%package doc
Summary: Various bits of documentation found in the kernel source.
Group: Documentation

%description doc
This package provides documentation files from the kernel source.
Various bits of information about the Linux kernel and the device
drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to the kernel modules at load time.

%package headers
Summary: Kernel C header files for use by glibc.
Group: Development/System
Conflicts: kernel-headers

%description headers
This package provides the C header files that specify the interface
between the Linux kernel and userspace libraries & programs. The
header files define structures and constants that are needed when
building most standard programs. They are also required when
rebuilding the glibc package.

%prep
%setup -q -n %{name}-%{version} -c
%{__mv} linux-%{LKAver} linux-%{version}.%{_target_cpu}
pushd linux-%{version}.%{_target_cpu} > /dev/null
%{__cp} %{SOURCE1} .
%{__cp} %{SOURCE2} .
%{__cp} %{SOURCE3} .
%patch1 -p1 -E
popd > /dev/null

%build
BuildKernel() {
    Flavour=$1

    # Select the correct flavour configuration file and set the development directory / symbolic link.
    if [ -n "$Flavour" ]; then
      Config=config-%{version}-%{_target_cpu}-$Flavour
      DevelDir=/usr/src/kernels/%{KVERREL}-$Flavour-%{_target_cpu}
      DevelLink=/usr/src/kernels/%{KVERREL}$Flavour-%{_target_cpu}
    else
      Config=config-%{version}-%{_target_cpu}
      DevelDir=/usr/src/kernels/%{KVERREL}-%{_target_cpu}
      DevelLink=
    fi

    KernelVer=%{version}-%{release}$Flavour

    # Correctly set the EXTRAVERSION string in the main Makefile.
    %{__perl} -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}$Flavour/" Makefile

    %{__make} -s mrproper
    %{__cp} $Config .config

    %{__make} -s CONFIG_DEBUG_SECTION_MISMATCH=y ARCH=%{buildarch} %{?_smp_mflags} bzImage
    %{__make} -s CONFIG_DEBUG_SECTION_MISMATCH=y ARCH=%{buildarch} %{?_smp_mflags} modules

    # Install the results into the RPM_BUILD_ROOT directory.
    %{__mkdir_p} $RPM_BUILD_ROOT/boot
    %{__install} -m 644 .config $RPM_BUILD_ROOT/boot/config-$KernelVer
    touch $RPM_BUILD_ROOT/boot/initrd-$KernelVer.img
    %{__gzip} -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-$KernelVer.gz
    %{__install} -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$KernelVer
    %{__cp} arch/%{buildarch}/boot/bzImage $RPM_BUILD_ROOT/boot/vmlinuz-$KernelVer
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/$KernelVer
    %{__make} -s INSTALL_MOD_PATH=$RPM_BUILD_ROOT KERNELRELEASE=$KernelVer ARCH=%{buildarch} modules_install

    # Set the modules to be executable, so that they will be stripped when packaged.
    find $RPM_BUILD_ROOT/lib/modules/$KernelVer -type f -name "*.ko" -exec %{__chmod} a+x "{}" ";"

    # Remove all the files that will be auto generated by depmod at the kernel install time.
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.*

    # Remove the two symbolic links.
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/source

    # Create the four directories and the one symbolic link.
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/$KernelVer/extra
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/$KernelVer/updates
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/$KernelVer/weak-updates
    pushd $RPM_BUILD_ROOT/lib/modules/$KernelVer > /dev/null
    %{__ln_s} build source
    popd > /dev/null

    # Collect the required development files.
    %{__cp} -a --parents `find -type f -name "Makefile*" -o -name "Kconfig*"` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    %{__cp} -a --parents kernel/bounds.[cs] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    %{__cp} -a --parents arch/x86/kernel/*.[cs] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    %{__cp} -a --parents `find security -type f -name "*.h"` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    %{__cp} -a Kbuild $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    %{__cp} -a .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    %{__cp} -a Module.* $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    %{__rm} -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Documentation
    %{__rm} -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    %{__rm} -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts

    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include

    %{__cp} -a --parents arch/x86/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    #%{__cp} -a --parents include/generated/*.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    pushd include > /dev/null
    %{__cp} -a acpi asm-generic config crypto drm keys linux math-emu media mtd net pcmcia rdma rxrpc scsi sound trace video xen $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    popd > /dev/null
    #%{__cp} -a include/generated/*.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/linux

    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts

    %{__cp} -a scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    find $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts -type f -name "*.o" -exec %{__rm} -f "{}" ";"

    # Ensure that the Makefile, Kbuild, .config, version.h, autoconf.h and auto.conf files
    # all have matching timestamps so that external modules can be built.
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Kbuild
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/linux/version.h
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/linux/autoconf.h
    #touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/autoconf.h
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf

    # Move the development files out of the /lib/modules/ file system.
    %{__mkdir_p} $RPM_BUILD_ROOT/usr/src/kernels
    %{__mv} $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT$DevelDir
    %{__ln_s} -f ../../..$DevelDir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    [ -z "$DevelLink" ] || %{__ln_s} -f `basename $DevelDir` $RPM_BUILD_ROOT$DevelLink
}

%{__rm} -rf $RPM_BUILD_ROOT
pushd linux-%{version}.%{_target_cpu} > /dev/null
%if %{with_std}
BuildKernel
%endif
%if %{with_pae}
BuildKernel PAE
%endif
popd > /dev/null

%install
pushd linux-%{version}.%{_target_cpu} > /dev/null
%if %{with_doc}
%{__mkdir_p} $RPM_BUILD_ROOT/usr/share/doc/%{name}-doc-%{version}/Documentation
# Sometimes non-world-readable files sneak into the kernel source tree.
%{__chmod} -R a+r *
# Copy the documentation over.
%{__tar} cf - Documentation | %{__tar} xf - -C $RPM_BUILD_ROOT/usr/share/doc/%{name}-doc-%{version}
# Remove the unrequired file.
%{__rm} -f $RPM_BUILD_ROOT/usr/share/doc/%{name}-doc-%{version}/Documentation/.gitignore
%endif

%if %{with_hdr}
# Install the kernel headers.
%{__make} -s INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr ARCH=%{buildarch} headers_install
find $RPM_BUILD_ROOT/usr/include -type f ! -name "*.h" -exec %{__rm} -f "{}" ";"
# For now, glibc provides the scsi headers.
%{__rm} -rf $RPM_BUILD_ROOT/usr/include/scsi
%endif
popd > /dev/null

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%post
/sbin/new-kernel-pkg --package kernel --mkinitrd --depmod --install %{KVERREL} || exit $?
if [ -x /sbin/weak-modules ]; then
    /sbin/weak-modules --add-kernel %{KVERREL} || exit $?
fi

%post devel
if [ -f /etc/sysconfig/kernel ]; then
    . /etc/sysconfig/kernel || exit $?
fi
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]; then
    pushd /usr/src/kernels/%{KVERREL}-%{_target_cpu} > /dev/null
    /usr/bin/find . -type f | while read f; do hardlink -c /usr/src/kernels/*FC*/$f $f; done
    popd > /dev/null
fi

%post PAE
/sbin/new-kernel-pkg --package kernel-PAE --mkinitrd --depmod --install %{KVERREL}PAE || exit $?
if [ -x /sbin/weak-modules ]; then
    /sbin/weak-modules --add-kernel %{KVERREL}PAE || exit $?
fi

%post PAE-devel
if [ -f /etc/sysconfig/kernel ]; then
    . /etc/sysconfig/kernel || exit $?
fi
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]; then
    pushd /usr/src/kernels/%{KVERREL}-PAE-%{_target_cpu} > /dev/null
    /usr/bin/find . -type f | while read f; do hardlink -c /usr/src/kernels/*FC*/$f $f; done
    popd > /dev/null
fi

%preun
/sbin/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVERREL} || exit $?
if [ -x /sbin/weak-modules ]; then
    /sbin/weak-modules --remove-kernel %{KVERREL} || exit $?
fi

%preun PAE
/sbin/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVERREL}PAE || exit $?
if [ -x /sbin/weak-modules ]; then
    /sbin/weak-modules --remove-kernel %{KVERREL}PAE || exit $?
fi

# Files section.
%if %{with_doc}
%files doc
%defattr(-,root,root)
%{_datadir}/doc/%{name}-doc-%{version}/Documentation/*
%dir %{_datadir}/doc/%{name}-doc-%{version}/Documentation
%dir %{_datadir}/doc/%{name}-doc-%{version}
%endif

%if %{with_hdr}
%files headers
%defattr(-,root,root)
/usr/include/*
%endif

%if %{with_std}
%files
%defattr(-,root,root)
/boot/vmlinuz-%{KVERREL}
/boot/System.map-%{KVERREL}
/boot/symvers-%{KVERREL}.gz
/boot/config-%{KVERREL}
/lib/firmware
%dir /lib/modules/%{KVERREL}
/lib/modules/%{KVERREL}/kernel
/lib/modules/%{KVERREL}/build
/lib/modules/%{KVERREL}/source
/lib/modules/%{KVERREL}/extra
/lib/modules/%{KVERREL}/updates
/lib/modules/%{KVERREL}/weak-updates
%ghost /boot/initrd-%{KVERREL}.img

%files devel
%defattr(-,root,root)
%dir /usr/src/kernels
%verify(not mtime) /usr/src/kernels/%{KVERREL}-%{_target_cpu}
%endif

%if %{with_pae}
%files PAE
%defattr(-,root,root)
/boot/vmlinuz-%{KVERREL}PAE
/boot/System.map-%{KVERREL}PAE
/boot/symvers-%{KVERREL}PAE.gz
/boot/config-%{KVERREL}PAE
/lib/firmware
%dir /lib/modules/%{KVERREL}PAE
/lib/modules/%{KVERREL}PAE/kernel
/lib/modules/%{KVERREL}PAE/build
/lib/modules/%{KVERREL}PAE/source
/lib/modules/%{KVERREL}PAE/extra
/lib/modules/%{KVERREL}PAE/updates
/lib/modules/%{KVERREL}PAE/weak-updates
%ghost /boot/initrd-%{KVERREL}PAE.img

%files PAE-devel
%defattr(-,root,root)
%dir /usr/src/kernels
%verify(not mtime) /usr/src/kernels/%{KVERREL}-PAE-%{_target_cpu}
/usr/src/kernels/%{KVERREL}PAE-%{_target_cpu}
%endif

%changelog
* Thu Sep 15 2011 Rudy Grigar <rudy@grigar.net> -2.6.32.46-0
- Reconfigure for 2.6.32.46 kernel.
- Add patch for grsecurity support.

* Thu Aug 04 2011 Alan Bartlett <ajb@elrepo.org> -2.6.35-14
- Updated to 2.6.35.14 tarball.
- Due to defective code, the Microsoft Hyper-V client
- drivers have not been configured for this build.

* Thu Apr 28 2011 Alan Bartlett <ajb@elrepo.org> -2.6.35-13
- Updated to 2.6.35.13 tarball.

* Sat Apr 02 2011 Alan Bartlett <ajb@elrepo.org> -2.6.35-12
- Updated to 2.6.35.12 tarball.

* Sat Mar 19 2011 Alan Bartlett <ajb@elrepo.org> - 2.6.35-11.1
- Set CONFIG_VETH=m [http://elrepo.org/bugs/view.php?id=119]
- Set CONFIG_STAGING=y
- Set CONFIG_STAGING_EXCLUDE_BUILD=n
- Set CONFIG_HYPERV=m [http://elrepo.org/bugs/view.php?id=122]
- Set CONFIG_HYPERV_STORAGE=m
- Set CONFIG_HYPERV_BLOCK=m
- Set CONFIG_HYPERV_NET=m

* Mon Feb 07 2011 Alan Bartlett <ajb@elrepo.org> - 2.6.35-11
- Updated to 2.6.35.11 tarball.
- Set CONFIG_CGROUPS=y
- Set CONFIG_CGROUP_FREEZER=y
- Set CONFIG_CGROUP_DEVICE=y
- Set CONFIG_CPUSETS=y
- Set CONFIG_PROC_PID_CPUSET=y
- Set CONFIG_CGROUP_CPUACCT=y
- Set CONFIG_RESOURCE_COUNTERS=y
- Set CONFIG_CGROUP_MEM_RES_CTLR=y
- Set CONFIG_CGROUP_MEM_RES_CTLR_SWAP=y
- Set CONFIG_CGROUP_SCHED=y
- Set CONFIG_NAMESPACES=y
- Set CONFIG_UTS_NS=y
- Set CONFIG_IPC_NS=y
- Set CONFIG_USER_NS=y
- Set CONFIG_PID_NS=y
- Set CONFIG_NET_NS=y

* Fri Feb 04 2011 Alan Bartlett <ajb@elrepo.org> - 2.6.35-10.2
- Set CONFIG_AMIGA_PARTITION=y
- Set CONFIG_EFI_PARTITION=y
- Set CONFIG_KARMA_PARTITION=y
- Set CONFIG_MAC_PARTITION=y
- Set CONFIG_MINIX_SUBPARTITION=y
- Set CONFIG_MSDOS_PARTITION=y
- Set CONFIG_OSF_PARTITION=y
- Set CONFIG_SGI_PARTITION=y
- Set CONFIG_SOLARIS_X86_PARTITION=y
- Set CONFIG_SUN_PARTITION=y
