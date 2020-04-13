#Can you help Tom catch Jerry?

T&J hexionteam 12.04.2020

A pcapng file is given with nothing particularly interesting apart from the fact that every flag is a USB input to the PC and the last 4 bytes indicate that the device is most likely a mouse (the same way it is hinted in the name).

We write dissectors in lua that translate the hexadecimal values to the buffer code.

```usb_mouse_protocol = Proto("USB_mouse",  "USB mouse protocol")

local buttons   = ProtoField.uint8("usb_mouse.buttons",   "Buttons",   base.DEC)
local vendor1   = ProtoField.int8 ("usb_mouse.vendor1",   "Vendor 1",  base.DEC)
local vendor2   = ProtoField.int8 ("usb_mouse.vendor2",   "Vendor 2",  base.DEC)
local scrolling = ProtoField.int8 ("usb_mouse.scrolling", "Scrolling", base.DEC)
local x_offset  = ProtoField.int16("usb_mouse.x_offset",  "X offset",  base.DEC)
local y_offset  = ProtoField.int16("usb_mouse.y_offset",  "Y offset",  base.DEC)

usb_mouse_protocol.fields = {
  buttons, vendor1, vendor2,
  scrolling, x_offset, y_offset,
}

local scrolling_lookup = {
  [-1] = " (down)",
  [ 0] = " (not scrolling)",
  [ 1] = " (up)"
}

local function parse_buttons(buffer)
  -- byte & (1 << n) > 0
  local function is_bit_set(byte, n)
    return bit.band(byte, bit.lshift(1, n)) > 0
  end

  local LEFT_BUTTON_BIT    = 0
  local RIGHT_BUTTON_BIT   = 1
  local MIDDLE_BUTTON_BIT  = 2
  local BACK_BUTTON_BIT    = 3
  local FORWARD_BUTTON_BIT = 4
  local SWITCH_BUTTON_BIT  = 5

  local buttons_number = buffer(0,1):le_uint()
  local buttons_array = {}

  if is_bit_set(buttons_number, LEFT_BUTTON_BIT)    then table.insert(buttons_array, "left")    end
  if is_bit_set(buttons_number, RIGHT_BUTTON_BIT)   then table.insert(buttons_array, "right")   end
  if is_bit_set(buttons_number, MIDDLE_BUTTON_BIT)  then table.insert(buttons_array, "middle")  end
  if is_bit_set(buttons_number, BACK_BUTTON_BIT)    then table.insert(buttons_array, "back")    end
  if is_bit_set(buttons_number, FORWARD_BUTTON_BIT) then table.insert(buttons_array, "forward") end
  if is_bit_set(buttons_number, SWITCH_BUTTON_BIT)  then table.insert(buttons_array, "switch")  end

  local buttons_text = " (none)"
  
  if #buttons_array ~= 0 then
    buttons_text = " (" .. table.concat(buttons_array, ", ") .. ")"
  end

  return buttons_text
end

function usb_mouse_protocol.dissector(buffer, pinfo, tree)
  length = buffer:len()
  if length == 0 then return end

  pinfo.cols.protocol = usb_mouse_protocol.name

  local subtree = tree:add(usb_mouse_protocol, buffer(), "USB Mouse Data")
  
  local buttons_text   = parse_buttons(buffer)
  local scrolling_text = scrolling_lookup[buffer(3,1):le_int()]

  subtree:add_le(buttons,   buffer(0,1)):append_text(buttons_text)
  subtree:add_le(vendor1,   buffer(1,1))
  subtree:add_le(vendor2,   buffer(2,1))
  subtree:add_le(scrolling, buffer(3,1)):append_text(scrolling_text)
  subtree:add_le(x_offset,  buffer(4,2))
  subtree:add_le(y_offset,  buffer(6,2))
end

DissectorTable.get("usb.interrupt"):add(0xffff, usb_mouse_protocol)
```

Then we add the script to the plugins folder and address the .pcapng file again. We export it as JSON file for the later visualization of mouse pattern.

```import itertools
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

main()```

After we import JSON to Python and analyze it we get a matplotlib object which is too shrunk. We enlarge it and we can read the flag from there.
