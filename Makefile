ifneq ($(KERNELRELEASE),)
	obj-m := usb_key.o
else
	CURRENT = $(shell uname -r)
	KDIR = /lib/modules/$(CURRENT)/build
	PWD = $(shell pwd)

default:
	gcc -o crypto crypto.c
	cp crypto /usr/bin/
	$(MAKE) -C $(KDIR) M=$(PWD) modules
	mkdir -p /lib/modules/$(CURRENT)//usb_key
	cp usb_key.ko usb_key.mod.o Module.symvers /lib/modules/$(CURRENT)//usb_key
	echo "usb_key" >> /etc/modules-load.d/usb_key.conf

clean:
	rm -rf .tmp_versions
	rm *.ko
	rm *.o
	rm *.mod.c
	rm *.symvers
	rm *.order
	rm crypto

endif
