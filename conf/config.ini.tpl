[GLOBAL]
srv_inventory_file: /home/data/list-srv.txt

[PUPPET]
host: puppet.flox-arts.net
user: puppet
certdir: etc/puppet/ssl/ca/signed

[BACKUP]
host: puppet.flox-arts.net
user: puppet
confdir: etc/rsync-time-machine

[FLA_API]
api_ep_contract: http://localhost:8888/api/billing/contract/