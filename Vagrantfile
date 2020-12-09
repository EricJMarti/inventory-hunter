Vagrant.configure("2") do |config|
  config.vm.define :hunter do |hunter|
    hunter.vm.box = "bento/ubuntu-18.04"
    hunter.vm.network "forwarded_port", guest: 80, host: 9091, host_ip: "127.0.0.1"

    hunter.ssh.forward_agent = true

    hunter.vm.network "private_network", type: "dhcp", virtualbox__intnet: true

    hunter.vm.synced_folder ".", "/home/vagrant/inventoryhunter"

    hunter.vm.provider "virtualbox" do |v|
      v.gui = false
      v.memory = "2048"
      v.cpus = 2
    end

    hunter.vm.provision "shell", path: "linux-ubuntu-setup.sh", args: "vagrant"
  end
end