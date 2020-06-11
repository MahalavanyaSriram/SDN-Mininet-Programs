from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet, arp, ipv4
from ryu.lib.packet import ether_types
from ryu.lib import mac
from ryu.lib.mac import haddr_to_bin
from ryu.controller import mac_to_port
from ryu.ofproto import inet
import networkx as nx
from ryu.lib.packet import icmp
from ryu.ofproto import ether
from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link
from ryu.app.wsgi import ControllerBase
import array
from ryu.app.ofctl.api import get_datapath


class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    global dijkstra, receive_arp, dpid_hostLookup
    global path2
    path2 = [0]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.net = nx.DiGraph()
        self.g = nx.DiGraph()
        self.switch_map = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        self.switch_map.update({datapath.id: datapath})

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    def dijkstra(graph, src, dest, visited=[], distances={}, predecessors={}):
       
        # few checks
        if src not in graph:
            raise TypeError('The root of the shortest path tree cannot be found')

        if dest not in graph:
            raise TypeError('The target of the shortest path cannot be found')
            # ending condition
        if src == dest:
            # We build the shortest path and display it
            path = []
            pred = dest
            while pred != None:
                path.append(pred)
                pred = predecessors.get(pred, None)
		path_copy= path[:]
		path_copy.reverse()
            print('shortest path:  ' + str(path_copy) + " cost= " + str(distances[dest]))
            global path2
            path2 = path

        else:
            # if it is the initial  run, initializes the cost
            if not visited:
                distances[src] = 0
            # visit the neighbors
            for neighbor in graph[src]:
                if neighbor not in visited:
                    new_distance = distances[src] + graph[src][neighbor]
                    #print(new_distance)
                    if new_distance <= distances.get(neighbor, float('inf')):
                        distances[neighbor] = new_distance
                        predecessors[neighbor] = src
            # mark as visited
            visited.append(src)
          
            unvisited = {}
            for k in graph:
                if k not in visited:
                    unvisited[k] = distances.get(k, float('inf'))
            x = min(unvisited, key=unvisited.get)
            dijkstra(graph, x, dest, visited, distances, predecessors)

    def dpid_hostLookup(self, lmac):
        host_locate = {1: '00:00:00:00:00:01', 2: '00:00:00:00:00:02',
                       4: '00:00:00:00:00:04', 5: '00:00:00:00:00:05',
                       6: '00:00:00:00:00:06'}

        for dpid, mac in host_locate.iteritems():
            if lmac in mac:
                return dpid

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return

        src = eth.src
        dst = eth.dst
	if str(dst) in ("00:00:00:00:00:01","00:00:00:00:00:02","00:00:00:00:00:03","00:00:00:00:00:04",
"00:00:00:00:00:05","00:00:00:00:00:06"):
		msg = ev.msg

		dpid = datapath.id
		self.mac_to_port.setdefault(dpid, {})

		self.logger.info("---------finding the shortest path from source host with mac address %s to Destination with mac address %s", src, dst)
		
		if dst in self.mac_to_port[dpid]:
		    out_port = self.mac_to_port[dpid][dst]
		else:
		    out_port = ofproto.OFPP_FLOOD
		actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

		switch_list = get_switch(self, None)
		switches = [switch.dp.id for switch in switch_list]
		links_list = get_link(self, None)
		link_port = {(link.src.dpid, link.dst.dpid): link.src.port_no for link in links_list}
		self.g.add_nodes_from(switches)
		links = [(link.src.dpid, link.dst.dpid, {'port': link.src.port_no}) for link in links_list]
		self.g.add_edges_from(links)
		links = [(link.dst.dpid, link.src.dpid, {'port': link.dst.port_no}) for link in links_list]
		
		topo = {'1': {'3': 10, '2': 10, '5': 15},
		        '2': {'1': 10, '3': 15, '4': 15},
		        '3': {'1': 10, '2': 15, '4': 5},
		        '4': {'2': 15, '3': 5, '6': 10},
		        '5': {'1': 15, '6': 15},
		        '6': {'4': 10, '5': 15}}
		dst_dpid = dpid_hostLookup(self, dst)
		
		path3 = []
		src = str(src)
		dst = str(dst)
		
		dijkstra(topo, str(dpid), str(dst_dpid))
                print("Out of dijistra")
		global path2
		path3 = list(map(int, path2))
		path3.reverse()

		if not self.g.has_node(eth.src):
		    self.g.add_node(eth.src)
		    self.g.add_edge(eth.src, datapath.id)
		    self.g.add_edge(datapath.id, eth.src, port=in_port)

		if not self.g.has_node(eth.dst):
		    self.g.add_node(eth.dst)
		    self.g.add_edge(eth.dst, datapath.id)
		    self.g.add_edge(datapath.id, eth.dst, port=in_port)
		    

		if (path3 != []):
		    if self.g.has_node(eth.dst):
		        next_match = parser.OFPMatch(eth_dst=eth.dst)
		        back_match = parser.OFPMatch(eth_dst=eth.src)
		        #print(path3)
		        for on_path_switch in range(1, len(path3) - 1):
		            now_switch = path3[on_path_switch]
		            next_switch = path3[on_path_switch + 1]
		            back_switch = path3[on_path_switch - 1]
		            next_port = link_port[(now_switch, next_switch)]
		            back_port = link_port[(now_switch, back_switch)]
		            new_dp = get_datapath(self, next_switch)
		            action = parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
		                                                  [parser.OFPActionOutput(next_port)])
                            #actions = [parser.OFPActionOutput(next_port)]
		            inst = [action]
                            actions = [parser.OFPActionOutput(next_port)]
		            self.add_flow(datapath=new_dp,priority=1, actions=actions, match=next_match, buffer_id=0)
		            action = parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
		                                                  [parser.OFPActionOutput(back_port)])
		            inst = [action]
		            actions = [parser.OFPActionOutput(back_port)]
		            new_dp = get_datapath(self, back_switch)
		            self.add_flow(datapath=new_dp, match=back_match,priority=1, actions=actions, buffer_id=0)
		            out = datapath.ofproto_parser.OFPPacketOut(
		                datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions)
		            datapath.send_msg(out)

		    else:
		        return
		else:
		    if out_port != ofproto.OFPP_FLOOD:
		        self.add_flow(datapath, msg.in_port, dst, actions)

		    out = datapath.ofproto_parser.OFPPacketOut(
		        datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions)
		    datapath.send_msg(out)
