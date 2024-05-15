from ryven.NENV import *
# widgets = import_widgets(__file__)

import sys
import os

sys.path.append(os.path.dirname(__file__))

# from plot_nodes import nodes as plot_nodes
from Scope_node import nodes as plot_nodes

# from generator_signals import nodes as generator_signals
# from clock_node import nodes as clock_node
from read_nodes import nodes as read_nodes
# from spec_node import nodes as spec_node
from switch_node import nodes as switch_node
# from spectrum_node import nodes as spectrum_node
# from clock_node_new import nodes as clock_node_new
# from filter_node import nodes as filter_node
# from filter_node_new import nodes as filter_node_new
from zoh import nodes as zoh
from timer_node import nodes as timer_node
from Plus import nodes as Plus
# from readWAV import nodes as readWAV
from nodeint16 import nodes as ToInt16
from Gain import nodes as Gain
# from new_filter_node import nodes as new_filter
from Quantization import nodes as Quantization
from all_filter_node import nodes as AllFilter
from signal_generators import nodes as SIN
from Spectrum_analyzer import nodes as spectrum_analyzer_node
from up_down_sampling import nodes as up_down_sampling
from Delay import nodes as delay
from newPlus import nodes as newPlus
from Spectrum_and_Spectogram import nodes as spec_and_spect
# from MatplotlibSpectogram import nodes as matSpec
# from icon import nodes as icon
from A_law import nodes as a_law



export_nodes(
    *plot_nodes,
    # *generator_signals,
    # *clock_node,
    *read_nodes,
    # *spec_node,
    *switch_node,
    # *spectrum_node,
    # *clock_node_new,
    # *filter_node,
    # *filter_node_new,
    *zoh,
    *timer_node,
    # *Plus,
    # *readWAV,
    *ToInt16,
    *Gain,
    # *new_filter,
    *Quantization,
    *AllFilter,
    *SIN,
    *spectrum_analyzer_node,
    *up_down_sampling,
    *delay,
    *newPlus,
    *spec_and_spect,
    # *matSpec,
    *a_law,
)
