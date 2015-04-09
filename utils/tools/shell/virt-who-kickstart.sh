#! /bin/sh
# Check RHEL build, when new compose arrives:
# make sure repo/distros exist, add repo/profiles/ and repo/kickstarts/libvirt/RHEL[5,6,7]/ 

source comment-line.sh

function check_builds(){

}

function check_distros(){
RHEL-7u0-Server-x64-20140507.0.distro
}

function create_profiles(){

}

function create_kickstarts(){

}


if [ check_builds ]; then
    star_line "check git repo"
    if ! [ -d repo ]; then
        star_line "git repo not exist, clone now"
        git clone git+ssh://git@qe-git.englab.nay.redhat.com/~/repo/virt-qe/repo
    fi

    star_line "run git pull"
    git pull

    star_line "run git status"
    git status

    while ! [ check_distros ]
    do
        if [ check_distros ]; then
            create_profiles
            create_kickstarts

            star_line "run git add"
            git add *** ***

            star_line "run git commit"
            git commit -m "sdfsadf"

            star_line "run git push"
            git push

            exit $?
        else
            star_line "distros file not exist yet, continue ..."
        fi
    done

else
    star_line "no new build available now, quite ... "
fi