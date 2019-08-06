# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|

  config.vm.box = "cedadev/centos7"
  config.vm.network "private_network", ip: "192.168.51.29"
  config.vm.network "forwarded_port", guest: 8091, host: 8091

  config.vm.synced_folder ".", "/Coding/cp4cds_metrics"

end
