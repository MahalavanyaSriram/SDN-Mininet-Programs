from mininet.net  import Mininet
from mininet.node import Controller
from mininet.cli  import CLI
from mininet.link import TCLink
from mininet.log  import setLogLevel, info

def treeNetwork():
	"Creating tree network and adding Nodes to it"
	net = Mininet( controller=Controller )
	
	info( '*** Adding Controller\n' )
	net.addController( 'c0' )

	info( '*** Adding hosts\n' )
	h1  = net.addHost( 'h1', ip ='10.0.1.10/24' )
	h2  = net.addHost( 'h2', ip ='10.0.1.11/24' )
	h3  = net.addHost( 'h3', ip ='10.0.1.12/24' )
	h4  = net.addHost( 'h4', ip ='10.0.1.13/24' )
 	h5  = net.addHost( 'h5', ip ='10.0.2.10/24' )
	h6  = net.addHost( 'h6', ip ='10.0.2.11/24' )
	h7  = net.addHost( 'h7', ip ='10.0.2.12/24' )
	h8  = net.addHost( 'h8', ip ='10.0.2.13/24' )
	h9  = net.addHost( 'h9', ip ='10.0.1.1/24' )
	h10 = net.addHost( 'h10', ip ='10.0.2.1/24' )

	info( '*** Adding switch\n' )
	s9  = net.addSwitch( 's9' )
	s10 = net.addSwitch( 's10' )
	s11 = net.addSwitch( 's11' )
	s12 = net.addSwitch( 's12' )
	s13 = net.addSwitch( 's13' )
	s14 = net.addSwitch( 's14' )
	s15 = net.addSwitch( 's15' )
	
	info( '*** Creating Host Links\n' )
	net.addLink( h1,  s11 )
	net.addLink( h2,  s11 )
	net.addLink( h3,  s12 )
	net.addLink( h4,  s12 )
	net.addLink( h5,  s14 )
	net.addLink( h6,  s14 )
	net.addLink( h7,  s15 )
	net.addLink( h8,  s15 )
	net.addLink( h9,  s9  )
	net.addLink( h10, s9  )
	
	info( '*** Creating Switch Links\n' )
	net.addLink( s11, s10 )
	net.addLink( s12, s10, cls= TCLink, bw=15, delay='10ms')
	net.addLink( s14, s13 )
	net.addLink( s15, s13 )
	net.addLink( s9 , s10, cls= TCLink, bw=10)
	net.addLink( s9 , s13 )
	
	info( '*** Starting network\n' )
	net.start()
	
	info( '*** IP configs\n' )
	print 'Host', h1.name, 'has IP address', h1.IP()
	print 'Host', h2.name, 'has IP address', h2.IP()
	print 'Host', h3.name, 'has IP address', h3.IP()
	print 'Host', h4.name, 'has IP address', h4.IP()
	print 'Host', h5.name, 'has IP address', h5.IP()
	print 'Host', h6.name, 'has IP address', h6.IP()
	print 'Host', h7.name, 'has IP address', h7.IP()
	print 'Host', h8.name, 'has IP address', h8.IP()
	print 'Host', h9.name, 'has IP address', h9.IP()
	print 'Host', h10.name, 'has IP address', h10.IP()
	
	info( '*** Pinging All From all hosts\n' )
	net.pingAll()

	info( '\n*** Measuring bandwidth and delay on host h9\n\n' )
	net.iperf( (h1,h9) )
	net.iperf( (h2,h9) )
	net.iperf( (h3,h9) )
	net.iperf( (h4,h9) )
	
	info( '\n*** Measuring bandwidth and delay on host h10\n' )
        net.iperf( (h5,h10) )
        net.iperf( (h6,h10) )
        net.iperf( (h7,h10) )
        net.iperf( (h8,h10) )
	
	info( '*** Running CLI\n' )
	CLI( net )

	info( '*** Stopping network' )
	net.stop()

if __name__ == '__main__':
	setLogLevel( 'info' )
	treeNetwork()



