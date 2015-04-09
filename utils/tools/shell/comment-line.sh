#! /bin/sh
# display comment line, useage:
# --source comment-line.sh

function date_line() {
    echo `date +"%F %T"` $1
}

function star_line() {
    echo "********** ********** $1 ********** **********"
}

function triple_line() {
    echo "########## ########## ########## ##########"
    echo "********** $1 **********"
    echo "########## ########## ########## ##########"
}

# test
date_line "date_line"
star_line "star_line"
triple_line "triple_line"
