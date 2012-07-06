import gevent

import mmm

from .base import Command

class ReplicateCommand(Command):
    'Run the mmm replicator based on the "replication" info in the config file'
    use_gevent = True
    remote_seer = True

    def run(self):
        'Run the mmm replicator based on the "replication" info in the config file'
        self.servers = {}
        topology = self.session.replicate['topology']
        replication = self.session.replicate['replication']
        assert sorted(topology.keys()) == ['cloud', 'local'], (
            'Need to have cloud and local defined in topology')

        # Load servers
        for name in topology:
            slave = mmm.ReplicationSlave(topology, name=name)
            slave.load_config()
            self.servers[name] = slave

        self._update_replication_config(replication)

        for s in self.servers.values():
            s.start()
        while True:
            gevent.sleep(5)
            self.log.info('=== mark ===')
        
    def _update_replication_config(self, replication):
        local = self.servers['local']
        cloud = self.servers['cloud']
        local_links = set()
        cloud_links = set()
        for cfg in replication:
            ns = '%s.%s' % (self.session.database, cfg['ns'])
            if cfg['dir'] == 'bidi':
                local.set_replication('cloud', ns, ns, cfg['ops'])
                cloud.set_replication('local', ns, ns, cfg['ops'])
                local_links.add((ns,ns))
                cloud_links.add((ns,ns))
            elif cfg['dir'] == 'down':
                local.set_replication('cloud', ns, ns, cfg['ops'])
                local_links.add((ns,ns))
            elif cfg['dir'] == 'up':
                cloud.set_replication('local', ns, ns, cfg['ops'])
                cloud_links.add((ns,ns))
            else:
                raise ValueError, 'Illegal config: %s' % cfg
            
        # Turn off replication not in local/cloud_links
        for repl in local.dump_config()['cloud']['replication']:
            if (repl['dst'], repl['src']) not in local_links:
                local.unset_replication('cloud', repl['dst'])
        for repl in cloud.dump_config()['local']['replication']:
            if (repl['dst'], repl['src']) not in cloud_links:
                cloud.unset_replication('local', repl['dst'])

        
