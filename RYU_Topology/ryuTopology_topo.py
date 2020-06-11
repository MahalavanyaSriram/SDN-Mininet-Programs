
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info

def treeNet():
    "Create an empty network and add nodes to it."

    net = Mininet(topo = None,controller=RemoteController )

    info( '*** Adding controller\n' )
    c0 = net.addController(name='c0',link=TCLink)

    info( '*** Adding hosts\n' )
    h1 = net.addHost( 'h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01' )
    h2 = net.addHost( 'h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02' )
    h3 = net.addHost( 'h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03' )
    h4 = net.addHost( 'h4', ip='10.0.0.4/24', mac='00:00:00:00:00:04' )
    h5 = net.addHost( 'h5', ip='10.0.0.5/24', mac='00:00:00:00:00:05' )
    h6 = net.addHost( 'h6', ip='10.0.0.6/24', mac='00:00:00:00:00:06' )
    
                                                                     

    info( '*** Adding switch\n' )
    s1 = net.addSwitch( 's1' )    
    s2 = net.addSwitch( 's2' ) 
    s3 = net.addSwitch( 's3' )    
    s4 = net.addSwitch( 's4' )    
    s5 = net.addSwitch( 's5' )    
    s6 = net.addSwitch( 's6' )    
    

    info( '*** Creating host links\n' )
    net.addLink( h1, s1 )
    net.addLink( h2, s2 )
    net.addLink( h3, s3 )
    net.addLink( h4, s4 )
    net.addLink( h5, s5 )
    net.addLink( h6, s6 )

    info( '*** Creating switch links\n' )
    net.addLink( s1, s2,cls= TCLink,bw=10)
    net.addLink( s1, s3,cls= TCLink,bw=10)
    net.addLink( s1, s5,cls= TCLink,bw=5)
    net.addLink( s5, s6,cls= TCLink,bw=5)
    net.addLink( s3, s4,cls= TCLink,bw=5)

    info( '*** Starting network\n')
    net.start()

    info( '*** Running CLI\n' )
    CLI( net )

    info( '*** Stopping network' )
    net.stop()
if __name__ == '__main__':
    setLogLevel( 'info' )
    treeNet()