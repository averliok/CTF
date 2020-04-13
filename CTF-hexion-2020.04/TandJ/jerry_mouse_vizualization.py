import itertools
import json
import matplotlib.pyplot as plt


def main():
  packets_export_file = open('/home/averliok/Downloads/jerry.json')
  packets = json.load(packets_export_file)

  x_offsets = [int(p["_source"]["layers"]["usb_mouse"]["usb_mouse.x_offset"])
    for p in packets]

  y_offsets = [-int(p["_source"]["layers"]["usb_mouse"]["usb_mouse.y_offset"])
    for p in packets]

  x_positions = list(itertools.accumulate(x_offsets))
  y_positions = list(itertools.accumulate(y_offsets))

  plt.figure(figsize=(120, 8))
  plt.plot(x_positions, y_positions)
  plt.title("Mouse position")
  plt.xlabel("X")
  plt.ylabel("Y")
  plt.savefig("hexctf.png")
  plt.show()

main()
