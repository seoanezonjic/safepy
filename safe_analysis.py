#!/usr/bin/env python
# coding: utf-8

import argparse
import os

from safepy.safe import *

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Execute SAFE by commandline with input handling.')
	parser.add_argument('--path-to-config', metavar='path_to_config', type=str, default='', 
	                    help='Path to config file')
	parser.add_argument('--path-to-network', metavar='path_to_network', type=str, 
	                    help='Path to file containing network data')
	parser.add_argument('--path-to-attributes', metavar='path_to_attributes', type=str, 
	                    help='Path to file with the attributes asigned to each network node')
	parser.add_argument('--output-path', metavar='output_path', type=str, default='results',
	                    help='Path in which save SAFE folder results')
	parser.add_argument('--threads', metavar='threads', type=int, default=1,
	                    help='Number of threads to use in processing data')
	parser.add_argument('--build_network_only', action='store_true',
						help='Parse network data and build the netwok object with the similarity distances and layout. The network will be saved as gpickle')
	parser.add_argument('--show_significant_nodes', action='store_true',
						help='Show significant nodes in attribute plots')
	parser.add_argument('--show_raw_data', action='store_true',
						help='Show raw data in attribute plots')
	parser.add_argument('--not_domain_computation', action='store_true', default=False,
						help='Show raw data in attribute plots')
	parser.add_argument('--attribute_names', nargs='*', default=[],
	                    help='Attribute names space separated to be plotted')
	args = parser.parse_args()

	sf = SAFE(path_to_ini_file=args.path_to_config)
	sf.load_network(network_file=args.path_to_network)

	if args.build_network_only:
		sf.save_network(output_file=args.output_path)
		#sf.save_gpickle(args.output_path)
	else:
		if not os.path.exists(args.output_path):
			os.mkdir(args.output_path)
		
		sf.plot_network()
		sf.define_neighborhoods()
		sf.load_attributes(attribute_file=args.path_to_attributes)
		sf.compute_pvalues(num_permutations=500, processes=args.threads)

		# ########################################################################
		# ### Show unitary attributes (all neighborhoods for one attribute)
		# ########################################################################
		# sf.plot_sample_attributes(
		# 	attributes=args.attribute_names,
		# 	show_significant_nodes=args.show_significant_nodes,
		# 	show_raw_data=args.show_raw_data, 
		# 	save_fig=os.path.join(args.output_path,'attribute_plot.pdf')
		# )
		# ########################################################################
		# ### Combine the enrichment landscapes into a single composite map
		# ########################################################################
		if not args.not_domain_computation:
			sf.define_top_attributes()
			sf.define_domains(attribute_distance_threshold = 0.65)
			sf.trim_domains()
		# 	sf.plot_composite_network(
		# 		show_each_domain=True, 
		# 		show_domain_ids=True, 
		# 		save_fig=os.path.join(args.output_path,'plotComposite.pdf')
		# 	)

		# ########################################################################
		# ### Output text files
		# ########################################################################

		sf.print_output_files(output_dir=args.output_path)


		nodes = list(nx.get_node_attributes(sf.graph, 'key').values())
		nodes_len = len(nodes)
		attribute_names = sf.attributes['name'].values
		attr_thr = -np.log10(sf.enrichment_threshold)

		if sf.node2domain is not None:
			domains = sf.node2domain['primary_domain'].values
			ness = sf.node2domain['primary_nes'].values
			num_domains = sf.node2domain[sf.domains['id']].sum(axis=1).values

		row = 0
		f = open(os.path.join(args.output_path, 'neighborhoods.txt'), "w")
		for neighborhood in sf.neighborhoods:
			node_positions = [i for i in range(nodes_len) if neighborhood[i] > 0]
			if len(node_positions) > 1: # Neighborhood must contain more than one member
				nes = sf.nes[row]
				significative_nes = nes > attr_thr
				attr_names = attribute_names[significative_nes]
				if len(attr_names) > 0: # Neighborhood must enrich in at least one term
					names = [] #get gene ids
					for node_position in node_positions:
						names.append(nodes[node_position])
					nes_scores = nes[significative_nes]
					record = []
					record.append(','.join(attr_names))
					record.append(','.join([str(i) for i in nes_scores]))
					if sf.node2domain is not None:
						dom = domains[row]
						if  dom == 0: # There is not domain for this neighborhood
							dom = '-'
							score = '-'
							num ='-'
						else:
							dom = str(dom)
							score = str(ness[row])
							num = str(num_domains[row])
						record.append(dom)
						record.append(score)
						record.append(num)
					record.append(','.join(names))
					f.write('\t'.join(record) + '\n')
			row += 1
		f.close()
