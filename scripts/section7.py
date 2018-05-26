#!/usr/bin/env python3

#
# arguments: <listFiles.xml> <out_modelblock.bin-input> <out_modelblock.bin-output> [model-name, [model-name]]
#
# If no model_name is given, then all models will be patched
#
#
# I personally ran this like this:
#
# [fox@x230 scripts]$ reset && ./section7.py /home/fox/Data/Projects/Sw_Racer/build/out_modelblock/listFiles.xml /home/fox/Data/Projects/Sw_Racer/build/out_modelblock.bin out_modelblock_test.bin model_130.bin
#

import sys
import os
import struct
from enum import IntEnum, auto
import xml.etree.ElementTree as ET

def get_value(s):
  if s[0:2] == '0x':
    return int(s[2:], 16)
  else:
    return int(s)

def readFile(path):
  with open(path, "rb") as f:
    return bytearray(f.read())

def writeFile(path, data):
  with open(path, "wb") as f:
    f.write(data)

def loadXML(path):
  print("Loading XML: '%s'" % path)
  xml = ET.parse(path)
  return xml.getroot()
  #xml = minidom.parse(path)
  #return xml.documentElement
  

in_xml_path = sys.argv[1]
in_path = sys.argv[2]
out_path = sys.argv[3]
model_names = sys.argv[4:]

# Load out_modelblock.bin
buf = readFile(in_path)

# Load listFiles.xml
xml = loadXML(in_xml_path)
all_model = xml.findall("File")
for model in all_model:

  # Check if we have to filter, and if this is a model we are interested in
  if (len(model_names) > 0) and not (model.attrib["name"] in model_names):
    continue

  # Get offset for section 2 in original out_modelblock.bin file
  offset_section2 = get_value(model.attrib["offset_section2"])

  # Load the respective XML
  #FIXME: Detect if this is absolute or relative path?
  model_xml = loadXML(os.path.join(os.path.dirname(in_xml_path), model.attrib["name"] + ".xml"))

  all_Models = model_xml.findall("Models")
  assert(len(all_Models) == 1)
  model_offset_section2 = get_value(all_Models[0].attrib["offset_section2"])

  all_section7 = model_xml.findall(".//Section7")
  for section7 in all_section7:
    model_section7_offset = get_value(section7.attrib["offset"])

    # Locate section7 in model
    section7_offset = offset_section2 + model_section7_offset - model_offset_section2

    _DATA_FMT = ">HBBBBHHHBBBBBBBBfffffLLHHLL"
    _DATA_SIZE = struct.calcsize(_DATA_FMT)
    i = 0

    class DATA(IntEnum):
      UNK_0 = 0

      FOG_FLAGS = auto()
      FOG_R = auto()
      FOG_G = auto()
      FOG_B = auto()
      FOG_START = auto()
      FOG_END = auto()

      LIGHTING_FLAGS = auto() # Is 7 when the folling 5 values are used
      AMBIENT_COLOR_R = auto()
      AMBIENT_COLOR_G = auto()
      AMBIENT_COLOR_B = auto()
      LIGHT_COLOR_R = auto()
      LIGHT_COLOR_G = auto()
      LIGHT_COLOR_B = auto()
      UNK_A = auto()
      UNK_B = auto()
      LIGHT_X = auto()
      LIGHT_Y = auto()
      LIGHT_Z = auto()

      UNKF_X = auto()
      UNKF_Y = auto()

      UNK_ZERO = auto()
      SURFACE_FLAGS = auto()

      UNK_6 = auto()
      UNK_7 = auto() # flags or count?

      UNK_8 = auto()
      UNK_9 = auto()

      LENGTH = auto()

    data = list(struct.unpack_from(_DATA_FMT, buf, section7_offset))
    assert(len(data) == DATA.LENGTH)

    print("Patch 0x%X: 0x%04X { 0x%02X #%02X%02X%02X %d %d } { 0x%02X #%02X%02X%02X #%02X%02X%02X 0x%02X 0x%02X { %.3f %.3f %.3f } } %.3f %.3f 0x%08X 0x%08X 0x%04X 0x%04X 0x%08X 0x%08X" % (section7_offset, *data))

    #FIXME: Testing..
    # 0x0000 = skydome
    # 0x0002 = background
    # 0x0012 = background
    # 0x0020 = skydome, and very very damped controls / can't point up banks [seems to work in reverse]
    # 0x0014 = skydome
    # 0x0024 = skydome, and very very damped controls / can't point up banks [seems to work in reverse]
    # not seen in game:
    # 0x0021 = skydome, and very very damped controls / can't point up banks [seems to work in reverse]
    # So probably: 0x02: background, else: skydome
    #              0x20: wall, else: ground
    assert(data[DATA.UNK_0] in [0x0000, 0x0002, 0x0004, 0x0010, 0x0012, 0x0014, 0x0020, 0x0024])
    data[DATA.UNK_0] = 0x0002

    # Controls fog
    # 0x00 = no fog
    # 0x01 = fog enabled
    assert(data[DATA.FOG_FLAGS] in [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x07, 0x0B, 0x0C])
    data[DATA.FOG_FLAGS] = 0x01

    # Patch section7 fog values
    data[DATA.FOG_R] = 0x0
    data[DATA.FOG_G] = 0x0
    data[DATA.FOG_B] = 0xFF

    data[DATA.FOG_START] = 1000
    data[DATA.FOG_START] = 3000

    # Turns on light position:
    # 0x00 = LIGHT_X,Y,Z is actually a light direction, no idea other than this
    # 0x01 = LIGHT_X,Y,Z is actually a light direction, no idea other than this
    # 0x03 = LIGHT_X,Y,Z is actually a light direction, no idea other than this
    # 0x06 = LIGHT_X,Y,Z is the light position, no idea other than this
    # 0x07 = LIGHT_X,Y,Z is the light position, no idea other than this
    # 0x0B = LIGHT_X,Y,Z is actually a light direction, no idea other than this
    # 0x0F = LIGHT_X,Y,Z is the light position, no idea other than this
    # 0x17 = LIGHT_X,Y,Z is the light position, no idea other than this
    assert(data[DATA.LIGHTING_FLAGS] in [0x00, 0x01, 0x03, 0x06, 0x07, 0x0B, 0x0F, 0x17])
    data[DATA.LIGHTING_FLAGS] = 0x07

    data[DATA.AMBIENT_COLOR_R] = 0xFF # Ambient color?
    data[DATA.AMBIENT_COLOR_G] = 0x00 # Ambient color?
    data[DATA.AMBIENT_COLOR_B] = 0x00 # Ambient color?

    data[DATA.LIGHT_COLOR_R] = 0x00
    data[DATA.LIGHT_COLOR_G] = 0x00
    data[DATA.LIGHT_COLOR_B] = 0xFF

    #FIXME: Testing..
    #       This seems to be the same for the entire track.
    #       Maybe it's just padding?
    #       In the second byte, note that the lower 3 bit are always 0!
    #       - except in 1 case
    unk_inferno = (0xFD, 0xE0)
    unk_beedos_wild_ride = (0x59, 0x00)
    more = []
    more += [(0x8B, 0x60)]
    more += [(0x5B, 0xB0)]
    more += [(0x33, 0x00)]
    more += [(0xC6, 0x50)]
    more += [(0x2F, 0x38)]
    more += [(0x0D, 0x30)]
    more += [(0xED, 0x10)]
    more += [(0xC0, 0x50)]
    more += [(0x32, 0x40)]
    more += [(0x0A, 0x58)]
    more += [(0x96, 0x98)]
    more += [(0x95, 0xF8)]
    more += [(0x9A, 0xA0)]
    more += [(0x54, 0x88)]
    more += [(0xFD, 0xD8)]
    more += [(0xBB, 0x00)]
    more += [(0x3D, 0x98)]
    more += [(0xA3, 0x28)]
    more += [(0x76, 0x60)]
    more += [(0x94, 0x00)]
    more += [(0x97, 0x50)]
    more += [(0x1F, 0x40)]
    more += [(0xBC, 0xF0)]

    # These seem to be from intro tracks (note how these use the lower 3 bits):
    more += [(0x00, 0x01)]
    more += [(0x00, 0x04)]
    more += [(0x00, 0x05)]
    assert((data[DATA.UNK_A], data[DATA.UNK_B]) in [unk_inferno,unk_beedos_wild_ride,*more])
    #data[DATA.UNK_A]=0x00
    #data[DATA.UNK_B]=0x00

    #FIXME: Testing..
    assert((data[DATA.UNKF_X], data[DATA.UNKF_Y]) in [(0.0, 1.0), (-1.0, 0.0), (0.0, -1.0), (-1.0, -1.0), (1.0, -1.0)])
    data[DATA.UNKF_X] = 0.0
    data[DATA.UNKF_Y] = 1.0

    assert(data[DATA.UNK_ZERO] == 0x00000000)

    more = 0
    more |= 0x20000000
    more |= 0x20000
    more |= 0x10000
    more |= 0x8000
    more |= 0x4000
    more |= 0x2000
    more |= 0x1000
    more |= 0x800
    more |= 0x400
    more |= 0x200
    more |= 0x100
    more |= 0x80
    more |= 0x40
    more |= 0x20
    more |= 0x10
    more |= 0x8
    more |= 0x4
    more |= 0x2
    more |= 0x1
    assert((data[DATA.SURFACE_FLAGS] & ~(more)) == 0)

    # Make AI always ride on side, also turn on ZOn for SWE1R flight simulator!
    #data[DATA.SURFACE_FLAGS] |= 0x20000000 | 0x1

    #FIXME: Testing..
    assert(data[DATA.UNK_6] in [0x0000, 0x0001, 0x0002, 0x100A])
    data[DATA.UNK_6] = 0x0001

    #FIXME: Testing..
    assert(data[DATA.UNK_7] in [0x0001, 0x0002, 0x594C, 0xA86C, 0xF280])
    data[DATA.UNK_7] = 0x594C

    #FIXME: Testing..
    #FIXME: assert(data[DATA.UNK_8] = ...)
    data[DATA.UNK_8] = 0x00000000

    #FIXME: Testing..
    #FIXME: assert(data[DATA.UNK_9] = ...)
    data[DATA.UNK_9] = 0x00000000

    # Writeback
    struct.pack_into(_DATA_FMT, buf, section7_offset, *data)

writeFile(out_path, buf)
