#!/usr/bin/expect -f
set timeout -1
#set password red2015

set machine [lindex $argv 0]
puts "will return beaker machine: $machine"

proc return2beaker {target} {
    spawn ssh $target "return2beaker.sh"
    expect {
            "(yes/no)?"
            {
                send "yes\n"
                expect "*assword:" { send "red2015\n"}
            }
            "*assword:"
            {
                send "red2015\n"
            }
    }
    expect eof
    #expect -re "($|#)"
    #send "return2beaker.sh\r"
    #expect "Going on..."
    #send "exit 1\r"
}

if { $machine == "all" } {
    foreach  vm { ent-02-vm-01.lab.eng.nay.redhat.com ent-02-vm-02.lab.eng.nay.redhat.com ent-02-vm-03.lab.eng.nay.redhat.com ent-02-vm-04.lab.eng.nay.redhat.com ent-02-vm-05.lab.eng.nay.redhat.com } {
        return2beaker $vm
    }
} else {
    return2beaker $machine
}
