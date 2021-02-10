#!/usr/bin/python
# -*- coding: utf-8 -*-

# Domain Joiner Program
# It runs well on Linux based operating systems.

import sys, os, subprocess

PATH_SAMBA = "/etc/samba/smb.conf"
PATH_SSSD = "/etc/sssd/sssd.conf"
PATH_PAMD_SESSIONS = "/etc/pam.d/common-session"
PATH_HOSTS = "/etc/hosts"
PATH_LIGHTDM = "/etc/lightdm/lightdm.conf"
PATH_KERBEROS = "/etc/krb5.conf"
PATH_REALM = "/etc/realmd.conf"
PATH_NSSWITCH = "/etc/nsswitch.conf"
PATH_SUDOADM = "/etc/sudoers.d/domainadmins"


def localeGen():
    with open("/etc/locale.gen", 'r+') as f:
        content = f.read()
        f.seek(0)
        f.truncate()
        f.write(content.replace("# en_US.UTF-8 UTF-8", "en_US.UTF-8 UTF-8"))

    with open("/etc/default/locale", "w") as localefile:
        localefile.write("""LANG=tr_TR.UTF-8
                            LANGUAGE=
                            LC_CTYPE="en_US.UTF-8"
                            LC_NUMERIC="tr_TR.UTF-8"
                            LC_TIME="tr_TR.UTF-8"
                            LC_COLLATE="tr_TR.UTF-8"
                            LC_MONETARY="en_US.UTF-8"
                            LC_MESSAGES="tr_TR.UTF-8"
                            LC_PAPER="en_US.UTF-8"
                            LC_NAME="tr_TR.UTF-8"
                            LC_ADDRESS="tr_TR.UTF-8"
                            LC_TELEPHONE="en_US.UTF-8"
                            LC_MEASUREMENT="en_US.UTF-8"
                            LC_IDENTIFICATION="en_US.UTF-8"
                            LC_ALL=""")
        cmd = subprocess.Popen("locale-gen", shell=True)
        cmd.communicate()
        cmd = subprocess.Popen("localedef -i en_US -f UTF-8 en_US-UTF-8", shell=True)
        cmd.communicate()
        cmd = subprocess.Popen("export LANGUAGE=en_US.UTF-8 && export LANG=en_US.UTF-8", shell=True)
        cmd.communicate()
        cmd = subprocess.Popen("export LC_ALL=en_US.UTF-8", shell=True)
        cmd.communicate()
        cmd = subprocess.Popen(
            "localectl set-locale LC_ADDRESS=en_US.UTF-8 && localectl set-locale LC_NAME=en_US.UTF-8 && localectl set-locale LC_MESSAGES=en_US.UTF-8 && localectl set-locale LC_COLLATE=en_US.UTF-8 && localectl set-locale LC_NUMERIC=en_US.UTF-8",
            shell=True)
        cmd.communicate()
        cmd = subprocess.Popen("localectl set-locale LANG=en_US.UTF-8", shell=True)
        cmd.communicate()


def controlLocale():
    with open("/etc/default/locale", "w") as localefile:
        localefile.write("""LANG=tr_TR.UTF-8
                            LANGUAGE=
                            LC_CTYPE="en_US.UTF-8"
                            LC_NUMERIC="tr_TR.UTF-8"
                            LC_TIME="tr_TR.UTF-8"
                            LC_COLLATE="tr_TR.UTF-8"
                            LC_MONETARY="en_US.UTF-8"
                            LC_MESSAGES="tr_TR.UTF-8"
                            LC_PAPER="en_US.UTF-8"
                            LC_NAME="tr_TR.UTF-8"
                            LC_ADDRESS="tr_TR.UTF-8"
                            LC_TELEPHONE="en_US.UTF-8"
                            LC_MEASUREMENT="en_US.UTF-8"
                            LC_IDENTIFICATION="en_US.UTF-8"
                            LC_ALL=""")


def checkWorkgroup():
    command = "net ads workgroup"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    ilk, workgroupname = out.split(": ")
    return (workgroupname)


def checkHostname(new, old):
    if (new == old):
        return False
    else:
        return True


def domainInfo(domainname):
    command = "samba-tool domain info " + domainname
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

    domain = "None"
    netbiosdomain = "None"
    dcname = "None"
    for line in out.decode("utf-8").splitlines():
        if "DC name" in line:
            ilk, dcname = line.split(": ")
        if "Netbios domain" in line:
            ilk, netbiosdomain = line.split(": ")
        if "Domain" in line:
            ilk, domain = line.split(": ")
    return (domain, netbiosdomain, dcname)


def gethostname():
    command = "hostname"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (hostname, err) = proc.communicate()
    return (hostname)


def realmnameUpper():
    command = "realm list | grep realm-name"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (realmname, err) = proc.communicate()
    print(realmname)
    return (realmname)


def haverealm():
    command = "which realm"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (realmname, err) = proc.communicate()
    if (realmname):
        command = "realm list | head -1"
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        (realmname, err) = proc.communicate()
        if (realmname):
            temprealm = "True"
        else:
            temprealm = "False"
    else:
        temprealm = "False"
    return (temprealm)


def getrealmname(realmname):
    command = "realm list | head -1"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (realmname, err) = proc.communicate()
    if (realmname):
        temprealm = realmname
    else:
        temprealm = "None"
    return (temprealm)


def LocalorDomain():
    command = "realm list"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = proc.communicate()
    if ("b''" in str(output)):
        return False
    return True


def checkUsernamePasswordDomain(hostname, username, domainname):
    command = "echo " + hostname + "| realm join -U " + username.lower() + " " + domainname.lower()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (realmname, err) = proc.communicate()
    if (("realm: Böyle bir erişim alanı bulunamadı" in err.decode("utf-8").splitlines())):
        return "Domain is not found!"
    elif (("realm: Erişim alanına katılamadı: Failed to join the domain" in err.decode("utf-8").splitlines())):
        return "Username or Password is wrong!"
    else:
        return "You joined to domain!"


def addDomainExt(newhostname, realm):
    command = "hostname"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (oldhostname, err) = proc.communicate()

    command = "hostnamectl set-hostname " + newhostname
    subprocess.check_output(command, shell=True)

    # TODO: Problem
    if (realm == "None"):
        oldhostname = oldhostname.decode("utf-8").strip()
        if (subprocess.call('grep -w "127.0.1.1" %s' % (PATH_HOSTS), shell=True) == 1):
            subprocess.Popen("echo '127.0.1.1   %s.%s   %s' >> %s" % (newhostname, realm, newhostname, PATH_HOSTS),
                             shell=True)
        else:
            subprocess.Popen(
                'sed -i "s/%s.*/%s.%s  %s/g" %s' % (oldhostname, newhostname, realm, newhostname, PATH_HOSTS),
                shell=True)
    else:
        oldhostname = oldhostname.decode("utf-8").strip()
        if (subprocess.call('grep -w "127.0.1.1" %s' % (PATH_HOSTS), shell=True) == 1):
            subprocess.Popen("echo '127.0.1.1   %s.%s   %s' >> %s" % (newhostname, realm, newhostname, PATH_HOSTS),
                             shell=True)
        else:
            subprocess.Popen(
                'sed -i "s/%s.*/%s.%s  %s/g" %s' % (oldhostname, newhostname, realm, newhostname, PATH_HOSTS),
                shell=True)


def leaveDomain():
    command1 = "realm leave"
    proc = subprocess.Popen(command1, stdout=subprocess.PIPE, shell=True)
    (output, err) = proc.communicate()
    return True


def addSAMBA(workgroup, realm):
    with open(PATH_SAMBA, "w") as sambafile:
        sambafile.write("""
    [global]
    unix charset=UTF-8
    workgroup = """ + workgroup + """
    client signing = yes
    client use spnego = yes
    security = ads
    dedicated keytab file = /etc/krb5.keytab
    kerberos method = secrets and keytab
    realm = """ + realm + """

    dns proxy = no
    map to guest = Bad User
    log file = /var/log/samba/log.%m
    max log size = 1000
    syslog = 0
    panic action = /usr/share/samba/panic-action %d """)


def addREALM(realm):
    proc = subprocess.Popen("lsb_release -r | cut -d':' -f2 | xargs", stdout=subprocess.PIPE, shell=True)
    (version, err) = proc.communicate()
    proc = subprocess.Popen("lsb_release -i | cut -d':' -f2 | xargs", stdout=subprocess.PIPE, shell=True)
    (distname, err) = proc.communicate()

    with open(PATH_REALM, "w") as realmfile:
        realmfile.write("""[users]
    default-home = /home/%D/%U
    default-shell = /bin/bash
    [active-directory]
    default-client = sssd
    os-name = """ + distname + """
    os-version = """ + version + """
    [service]
    automatic-install = no
    [""" + realm + """]
    fully-qualified-names = no
    automatic-id-mapping = yes
    user-principal = yes
    manage-system = no""")


def addSSSD(realm):
    with open(PATH_SSSD, "w") as sssdfile:
        sssdfile.write("""[sssd]
                        services = nss, pam
                        config_file_version = 2
                        domains = """ + realm + """
                        
                        [domain/""" + realm.upper() + """]
                        id_provider = ad
                        
                        override_homedir = /home/%d/%u""")
    command1 = "chown root:root " + PATH_SSSD
    command2 = "chmod 600 " + PATH_SSSD
    subprocess.Popen(command1, stdout=subprocess.PIPE, shell=True)
    subprocess.Popen(command2, stdout=subprocess.PIPE, shell=True)


def setTime(ntpserver):
    command1 = "ntpdate " + ntpserver
    command2 = "hwclock --systohc"
    cmd = subprocess.Popen(command1, stdout=subprocess.PIPE, shell=True)
    cmd.communicate()
    cmd = subprocess.Popen(command2, stdout=subprocess.PIPE, shell=True)
    cmd.communicate()


def restartService(servicename):
    command1 = "systemctl restart " + servicename
    subprocess.Popen(command1, stdout=subprocess.PIPE, shell=True)


def addMkHomedir():
    content = list()
    with open(PATH_PAMD_SESSIONS, "r") as pam:
        for line in pam:
            content.append(line)
    conf = "session required pam_mkhomedir.so skel=/etc/skel umask=0077\n"
    if not (content[len(content) - 1] == conf):
        content.append("session required pam_mkhomedir.so skel=/etc/skel umask=0077\n")
    with open(PATH_PAMD_SESSIONS, "w") as pam:
        for line in content:
            pam.write(line)


def krbDefaultRealm(realmname):
    with open(PATH_KERBEROS, 'r+') as f:
        content = f.read()
        f.seek(0)
        f.truncate()
        f.write(content.replace("default_realm = ATHENA.MIT.EDU", "default_realm = " + realmname.upper()))


def addSudoers(tm_domainname):
    with open(PATH_SUDOADM, "w") as sudofile:
        sudofile.write("""%domain\x20admins ALL=(ALL) ALL """)


def changeLightdmConf():
    with open(PATH_LIGHTDM, 'r+') as f:
        content = f.read()
        f.seek(0)
        f.truncate()
        f.write(content.replace("#greeter-show-manual-login=false", "greeter-show-manual-login=true"))

    with open(PATH_LIGHTDM, 'r+') as f:
        content = f.read()
        f.seek(0)
        f.truncate()
        f.write(content.replace("#greeter-hide-users=false", "greeter-hide-users=true"))


#######################################
## ana rutin
#######################################
def main():
    try:
        domainname = str(sys.argv[1])
        cmd = subprocess.Popen("DEBIAN_FRONTEND=noninteractive apt-get update", shell=True)
        cmd.communicate()

        cmd = subprocess.Popen(
            "DEBIAN_FRONTEND=noninteractive apt-get install krb5-user samba sssd libsss-sudo ntpdate realmd sssd-tools cifs-utils smbclient -y",
            shell=True)
        cmd.communicate()

        if (".local" in domainname.lower()):
            with open(PATH_NSSWITCH, 'r+') as f:
                content = f.read()
                f.seek(0)
                f.truncate()
                f.write(content.replace("files mdns4_minimal [NOTFOUND=return] dns",
                                        "dns files mdns4_minimal [NOTFOUND=return]"))

        if (os.path.isfile("/etc/samba/smb.conf") and os.path.isfile("/etc/krb5.conf")):
            print("Kurulum:OK")
        else:
            print("Paketler yüklenmemiş.")
            exit()

        domain, netbiosdomain, dcname = domainInfo(domainname)
        if (domain == "None"):
            print("Ulaşılamadı, DNS adresinizi kontrol ediniz")
            exit()

        localeGen()
        addDomainExt(sys.argv[2], domain)

        # domain
        addSAMBA(netbiosdomain, domain)
        addREALM(domain)

        setTime(dcname)
        restartService("smbd")
        restartService("nmbd")

        command = "echo " + sys.argv[4] + " | realm join --user=\"" + sys.argv[
            3] + "@" + domainname.upper() + "\" " + domainname.lower()
        cmd = subprocess.Popen(command, shell=True)
        cmd.communicate()

        krbDefaultRealm(domain)
        addMkHomedir()
        changeLightdmConf()
        controlLocale()
        addSudoers(domainname)
        # print("Tebrikler")
        command1 = "realm permit -a"
        cmd = subprocess.Popen(command1, shell=True)
        cmd.communicate()

        ## domaine alma
        print("OK")
    except IndexError as error:
        print("eksik parametre:", error)


if __name__ == "__main__":
    main()
