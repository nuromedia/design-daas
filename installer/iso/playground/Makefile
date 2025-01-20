.PHONY: start stop reset
default: start

reset:
	rm -rf iso
	cp -r iso-ceph iso

start: reset
	./vm-run.bash -a start -n pve1 &
	./vm-run.bash -a start -n pve2 &
	./vm-run.bash -a start -n pve3 &
	sudo iptables -t nat -A POSTROUTING -o enp6s0 -j MASQUERADE
	sudo iptables -t nat -A POSTROUTING -o enp7s0 -j MASQUERADE

stop:
	./vm-run.bash -a stop -n pve1 &
	./vm-run.bash -a stop -n pve2 &
	./vm-run.bash -a stop -n pve3 &
	sudo iptables -t nat -D POSTROUTING -o enp6s0 -j MASQUERADE
	sudo iptables -t nat -D POSTROUTING -o enp7s0 -j MASQUERADE


